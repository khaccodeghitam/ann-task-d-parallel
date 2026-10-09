#!/usr/bin/env python3
"""Issue #18: analyze local replicated distributed DETAIL evidence, preserving run/query clusters; never read MLflow.

Intervals are userspace-observed, not hardware/device latency. Equal timestamps
use the frozen semantic order; residency integrates the state after each tie group.
No statistical inference treats individual requests as independent experiments.
"""
import argparse
from collections import Counter, defaultdict, deque
import csv
from datetime import datetime
import hashlib
import itertools
import json
from pathlib import Path
import statistics
import sys

RANK = {name: i for i, name in enumerate(("QUERY_START", "WIDTH_INIT", "WIDTH_CHANGE",
    "IO_SELECT", "IO_SUBMIT", "IO_CQE_SEEN", "IO_CACHE_READY", "IO_PUBLISH",
    "NODE_EXPAND", "QUERY_END", "TRACE_HEALTH"))}
FAILURES = ("events_dropped", "ordering_violations", "negative_hidden_count",
            "unmatched_submit", "unmatched_cqe", "unmatched_publish", "outstanding_at_query_end", "table_overflows")
METRICS = ("qps", "mean_latency_us", "p99_latency_us", "recall", "mean_ios")


def read_json(path):
    return json.loads(Path(path).read_text())


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def distribution(values):
    values = list(values)
    if not values:
        return {"values": [], "n": 0, **dict.fromkeys(("mean", "median", "min", "max", "sample_sd"))}
    return {"values": values, "n": len(values), "mean": statistics.mean(values),
            "median": statistics.median(values), "min": min(values), "max": max(values),
            "sample_sd": statistics.stdev(values) if len(values) > 1 else None}


def percentile(values, p):
    values = sorted(values)
    if not values:
        return None
    index = p * (len(values) - 1)
    lo = int(index)
    hi = min(lo + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (index - lo)


def quantiles(values):
    values = list(values)
    return {"n": len(values), **{k: percentile(values, p) for k, p in
            (("p50", .5), ("p95", .95), ("p99", .99), ("max", 1))}}


def event_key(event):
    def numeric(name):
        value = event.get(name)
        return -1 if value is None else value
    return (event["timestamp_ns"], RANK[event["event"]], numeric("old_width") if event["event"] == "WIDTH_CHANGE" else -1, numeric("request_seq"),
            numeric("node_id"), numeric("worker_id"), numeric("linux_tid"),
            json.dumps(event, sort_keys=True, separators=(",", ":")))


def analyze_query(events):
    events = sorted(events, key=event_key)
    kinds = Counter(e["event"] for e in events)
    if any(kinds[k] != 1 for k in ("QUERY_START", "QUERY_END", "WIDTH_INIT", "TRACE_HEALTH")):
        raise ValueError("Missing/duplicate query boundary, width init or health")
    start = next(e for e in events if e["event"] == "QUERY_START")
    end = next(e for e in events if e["event"] == "QUERY_END")
    begin, finish = start["timestamp_ns"], end["timestamp_ns"]
    if finish <= begin:
        raise ValueError("Nonpositive query duration")
    if any((e["query_id"], e.get("worker_id"), e.get("linux_tid")) !=
           (start["query_id"], start.get("worker_id"), start.get("linux_tid")) for e in events):
        raise ValueError("Query/worker identity changed")
    requests, queue, published_nodes = {}, deque(), set()
    counts = Counter()
    state = {"hidden": 0, "device_outstanding": 0, "total_unpublished": 0}
    area = Counter()
    maxima = Counter()
    fractions = Counter()
    buckets = Counter()
    width = wcap = initial = None
    width_area = initialized_ns = cap_ns = above32_ns = unknown_ns = 0
    previous = begin
    changes = 0
    for timestamp, tied in itertools.groupby(events, key=lambda e: e["timestamp_ns"]):
        tied = list(tied)
        if timestamp < begin or (timestamp > finish and any(e["event"] != "TRACE_HEALTH" for e in tied)):
            raise ValueError("Event outside query boundary")
        dt = max(0, min(timestamp, finish) - previous)
        for key, value in state.items():
            area[key] += value * dt
        fractions["hidden_gt0"] += dt * (state["hidden"] > 0)
        fractions["hidden_ge2"] += dt * (state["hidden"] >= 2)
        if width is None:
            unknown_ns += dt
        else:
            width_area += width * dt
            initialized_ns += dt
            cap_ns += dt * (width == wcap)
            above32_ns += dt * (width > 32)
            bucket = next(label for lo, hi, label in ((1, 4, "1-4"), (5, 8, "5-8"),
                (9, 16, "9-16"), (17, 32, "17-32"), (33, 64, "33-64"), (65, sys.maxsize, "65+"))
                if lo <= width <= hi)
            buckets[bucket] += dt
        previous = min(timestamp, finish)
        for e in tied:
            kind, seq = e["event"], e.get("request_seq")
            if any(e.get(k) is not None and e[k] < 0 for k in ("submitted", "cqe_seen", "published", "expanded", "cache_ready", "cache_published", "outstanding_correlations")):
                raise ValueError("Negative causal counter")
            if kind not in RANK:
                raise ValueError("Unknown event")
            if e.get("events_dropped", 0) or e.get("ordering_violations", 0):
                raise ValueError("Runtime loss/order violation")
            if kind == "WIDTH_INIT":
                wcap, width = e["wcap"], e["width"]
                if wcap < 1 or width != min(4, wcap):
                    raise ValueError("Wrong initial width")
                initial = width
            elif kind == "WIDTH_CHANGE":
                if width is None or e["old_width"] != width or not width <= e["width"] <= min(width + 1, wcap):
                    raise ValueError("Width decrease/jump/inconsistent old width")
                width = e["width"]
                changes += 1
            if kind in ("WIDTH_INIT", "WIDTH_CHANGE", "QUERY_END") and e.get("width") is not None and (width is None or e["width"] != width or e.get("wcap") != wcap):
                raise ValueError("Width snapshot mismatch")
            if kind == "IO_SELECT":
                if not isinstance(seq, int) or seq != len(requests) + 1:
                    raise ValueError("Duplicate/nonmonotonic request_seq")
                requests[seq] = {"state": "selected", "node_id": e.get("node_id"),
                                 "request_key": e.get("request_key")}
                queue.append(seq)
                counts["selected"] += 1
            elif kind in ("IO_SUBMIT", "IO_CQE_SEEN", "IO_CACHE_READY", "IO_PUBLISH"):
                request = requests.get(seq)
                if request is None:
                    raise ValueError("Causal event without selected request/submit")
                for key in ("node_id", "request_key"):
                    if request[key] != e.get(key):
                        raise ValueError("Request identity mismatch")
                expected = {"IO_SUBMIT": ("selected",), "IO_CQE_SEEN": ("submitted",),
                            "IO_CACHE_READY": ("selected",), "IO_PUBLISH": ("cqe", "cache")}[kind]
                if request["state"] not in expected:
                    raise ValueError("Submit/CQE/publication order violation")
                if kind == "IO_SUBMIT":
                    request.update(state="submitted", submit=timestamp)
                    counts["submitted"] += 1
                elif kind == "IO_CQE_SEEN":
                    if e.get("cqe_result", 0) is not None and e.get("cqe_result", 0) < 0:
                        raise ValueError("CQE error")
                    request.update(state="cqe", cqe=timestamp)
                    counts["cqe_seen"] += 1
                elif kind == "IO_CACHE_READY":
                    request.update(state="cache")
                    counts["cache_ready"] += 1
                else:
                    if not queue or queue.popleft() != seq:
                        raise ValueError("Non-FIFO publication")
                    counts["cache_published" if request["state"] == "cache" else "published"] += 1
                    request.update(state="published", publish=timestamp)
                    published_nodes.add(request["node_id"])
            elif kind == "NODE_EXPAND":
                if e.get("node_id") not in published_nodes:
                    raise ValueError("Expansion without publication")
                counts["expanded"] += 1
            elif kind in ("QUERY_END", "TRACE_HEALTH"):
                if queue or e.get("outstanding_correlations", 0):
                    raise ValueError("Unfinished request at query end")
                for key in ("submitted", "cqe_seen", "published", "expanded", "cache_ready", "cache_published"):
                    if e.get(key) is not None and e[key] != counts[key]:
                        raise ValueError("Reconstruction contradicts end/health counter")
            # Snapshot fields cannot determine tie ordering, but negative snapshots
            # are always invalid. End counters provide order-independent cross-checks.
            if e.get("completed_hidden") is not None and e["completed_hidden"] < 0:
                raise ValueError("Negative hidden snapshot")
            state = {"hidden": counts["cqe_seen"] - counts["published"],
                     "device_outstanding": counts["submitted"] - counts["cqe_seen"],
                     "total_unpublished": counts["submitted"] - counts["published"]}
            if any(value < 0 for value in state.values()):
                raise ValueError("Negative reconstructed state")
        for key, value in state.items():
            maxima[key] = max(maxima[key], value)
    if queue or any(state.values()):
        raise ValueError("Final outstanding state is nonzero")
    duration = finish - begin
    timings = []
    for seq, request in requests.items():
        if "submit" not in request:
            continue  # cache-ready paths have no physical submission
        observed = (request["cqe"] - request["submit"]) / 1000
        hol = (request["publish"] - request["cqe"]) / 1000
        if min(observed, hol) < 0:
            raise ValueError("Negative request interval")
        timings.append({"request_seq": seq, "node_id": request["node_id"],
                        "submit_ns": request["submit"], "cqe_ns": request["cqe"], "publish_ns": request["publish"],
                        "observed_io_us": observed, "publication_hol_us": hol,
                        "hol_to_observed_io_ratio": hol / observed if observed > 0 else None})
    return {"query_id": start["query_id"], "worker_id": start.get("worker_id"),
        "linux_tid": start.get("linux_tid"), "start_ns": begin, "end_ns": finish,
        "duration_ns": duration, "request_metrics": timings,
        "publication_hol_us": quantiles(r["publication_hol_us"] for r in timings),
        "observed_io_us": quantiles(r["observed_io_us"] for r in timings),
        "hol_to_observed_io_ratio": quantiles(r["hol_to_observed_io_ratio"] for r in timings
                                              if r["hol_to_observed_io_ratio"] is not None),
        "time_weighted": {**{f"mean_{k}": area[k] / duration for k in state},
            **{f"max_{k}": maxima[k] for k in state},
            **{f"fraction_{k}": fractions[k] / duration for k in ("hidden_gt0", "hidden_ge2")}},
        "width": {"initial": initial, "final": width, "maximum": width, "changes": changes,
            "time_weighted_mean": width_area / initialized_ns if initialized_ns else None,
            "unknown_fraction": unknown_ns / duration, "fraction_at_wcap": cap_ns / duration,
            "fraction_above32": above32_ns / duration,
            "bucket_fractions": {k: buckets[k] / duration for k in ("1-4", "5-8", "9-16", "17-32", "33-64", "65+")}},
        "logical_work": {**{k: counts[k] for k in ("selected", "submitted", "cqe_seen", "published", "expanded", "cache_ready", "cache_published")},
            "published_not_expanded": counts["published"] + counts["cache_published"] - counts["expanded"]}}


def analyze_events(events):
    grouped = defaultdict(list)
    for event in events:
        if event.get("event") not in RANK or not isinstance(event.get("timestamp_ns"), int) or event["timestamp_ns"] < 0:
            raise ValueError("Unknown event/invalid timestamp")
        qid = event.get("query_id")
        if not isinstance(qid, int) or qid < 0:
            raise ValueError("Invalid query_id")
        grouped[qid].append(event)
    queries = [analyze_query(grouped[qid]) for qid in sorted(grouped)]
    requests = [r for q in queries for r in q["request_metrics"]]
    duration = sum(q["duration_ns"] for q in queries)
    run_time_weighted = {key: sum(q["duration_ns"] * q["time_weighted"][key] for q in queries) / duration
                         for key in ("mean_hidden", "mean_device_outstanding", "mean_total_unpublished",
                                     "fraction_hidden_gt0", "fraction_hidden_ge2")} if duration else {}
    return {"analysis_valid": True, "queries": queries, "time_weighted": run_time_weighted,
        "publication_hol_us": quantiles(r["publication_hol_us"] for r in requests),
        "observed_io_us": quantiles(r["observed_io_us"] for r in requests),
        "hol_to_observed_io_ratio": quantiles(r["hol_to_observed_io_ratio"] for r in requests
                                               if r["hol_to_observed_io_ratio"] is not None),
        "hidden_gt0_fraction": sum(q["duration_ns"] * q["time_weighted"]["fraction_hidden_gt0"]
                                    for q in queries) / duration if duration else None,
        "grouping": "Requests nested in queries nested in runs; pooled request quantiles descriptive only"}


# Historical analyzers are unchanged. C2 freezes a new estimand/gate below.
from analyze_e0b import COLLECTORS, ZERO_HEALTH, load_run, verify_sums
from analyze_g0b_light import SENTINELS, EXPECTED_PACKAGES, telemetry_coverage, require
from causal_trace import read_raw, COUNTER_FIELDS, FAILURE_COUNTERS
from check_causal_trace import check_events
from trace_sampling import explicit_policy

ORDERS = [list('ABCDE'), list('BCDEA'), list('CDEAB')]
QIDS = [1000,1533,2066,2600,3133,3666,4200,4733,5266,5800,6333,6866,7400,7933,8466,9000]
SAMPLE_SHA = 'bb12f3bd4c1a370786765e1ebe6f5ef9883b6deab2d4437392090e3c3556deda'
BASE = 'f2f07fb32c2b5f31bf33e457162721de4e645f45'
SUBJECT = '35222026893ff7d1b45586fcdd8165a5ce592cd3'
BINARY = 'f5795e43c3be1f2515bd37e21ad1fbab45b2849c859724629a8c6edea5e418dd'
SEARCH = dict(benchmark_profile='pipeann-b9ec4ba',dataset_id='sift10m',data_type='uint8',distance_metric='l2',k=10,l_search=100,mem_l=0,neighbor_type='pq',query_count=10000,search_mode=2)
THRESHOLDS = dict(hol_relative_factor=2,majority=2,material_scale_ratio=.25,material_hidden_fraction=.25,low_ratio=.10,low_hidden_fraction=.10,phase_min_bins=4,phase_bin_count=5)


def phase_coverage(queries, origin, end, expected_qids=QIDS):
    require(end > origin > 0, 'Invalid benchmark phase boundaries')
    require(len(queries) == len(expected_qids) and sorted(q['query_id'] for q in queries) == list(expected_qids), 'Incorrect sampling membership')
    bins = [0]*5
    fractions = []
    for q in queries:
        require(origin <= q['start_ns'] < q['end_ns'] <= end, 'Query outside benchmark phase bounds')
        q['benchmark_relative_start_ns'] = q['start_ns']-origin
        q['benchmark_relative_end_ns'] = q['end_ns']-origin
        q['start_fraction'] = (q['start_ns']-origin)/(end-origin)
        q['end_fraction'] = (q['end_ns']-origin)/(end-origin)
        fractions.append(q['start_fraction']); bins[min(4,int(q['start_fraction']*5))] += 1
    return dict(start_fraction=quantiles(fractions), min_start_fraction=min(fractions),median_start_fraction=statistics.median(fractions),max_start_fraction=max(fractions),start_bins=bins,occupied_bins=sum(bool(n) for n in bins),phase_coverage_insufficient=sum(bool(n) for n in bins)<4,active_query_occupancy='UNMEASURED')


def histogram(values):
    bounds = [0,.5,1,2,5,10,25,50,100,250,1000]
    counts = [0]*len(bounds)
    for value in values:
        require(value >= 0,'Negative histogram interval')
        bucket=max(i for i,low in enumerate(bounds) if low<=value);counts[bucket]+=1
    return dict(lower_bounds_us=bounds,counts=counts,label='Within-run request descriptions; requests are nonindependent')


def describe_detail(events, origin, end, expected_qids=QIDS):
    result=analyze_events(events)
    result['phase']=phase_coverage(result['queries'],origin,end,expected_qids)
    queries=result['queries'];requests=[r for q in queries for r in q['request_metrics']]
    result['median_query_hidden_gt0_fraction']=statistics.median(q['time_weighted']['fraction_hidden_gt0'] for q in queries)
    io=result['observed_io_us']['p95'];hol=result['publication_hol_us']['p95']
    result['p95_hol_to_p95_observed_io_ratio']=hol/io if io is not None and io>0 else None
    result['zero_observed_io_request_count']=sum(r['observed_io_us']==0 for r in requests)
    result['query_distributions']={k:quantiles(q['time_weighted'][k] for q in queries) for k in ('mean_hidden','mean_device_outstanding','mean_total_unpublished','fraction_hidden_gt0','fraction_hidden_ge2')}
    result['query_width_distributions']={k:quantiles(q['width'][k] for q in queries) for k in ('initial','final','maximum','changes','time_weighted_mean','fraction_at_wcap','fraction_above32','unknown_fraction')}
    result['query_timing_distributions']={k:quantiles(q[k]['p95'] for q in queries if q[k]['p95'] is not None) for k in ('publication_hol_us','observed_io_us')}
    result['request_histograms']={k:histogram(r[k] for r in requests) for k in ('publication_hol_us','observed_io_us')}
    return result


def d6_gate(groups):
    base=dict(classification='D6_INCONCLUSIVE',system_wide_D6='INCONCLUSIVE',thresholds=THRESHOLDS)
    if any(len(groups.get(c,[]))!=3 or {r['round'] for r in groups[c]}!={1,2,3} for c in SENTINELS):
        return {**base,'reason':'Missing/duplicate repeated regimes'}
    ordered={c:sorted(groups[c],key=lambda r:r['round']) for c in SENTINELS}
    phase_failed=[f"{c}/R{r['round']}" for c,rows in ordered.items() for r in rows if r['detail']['phase']['phase_coverage_insufficient']]
    measurements={}
    for c in ('C','D'):
        hol=[r['detail']['publication_hol_us']['p95'] for r in ordered[c]]
        observed=[r['detail']['observed_io_us']['p95'] for r in ordered[c]]
        baseline=[r['detail']['publication_hol_us']['p95'] for r in ordered['B']]
        hidden=[r['detail']['median_query_hidden_gt0_fraction'] for r in ordered[c]]
        require(all(v is None or v>=0 for v in hol+observed+baseline+hidden),'Negative D6 metric')
        ratios=[h/o if h is not None and o is not None and o>0 else None for h,o in zip(hol,observed)]
        relative=[h/b if h is not None and b is not None and b>0 else None for h,b in zip(hol,baseline)]
        confirmations=[v is not None and v>=2 for v in relative]
        defined=[v for v in ratios if v is not None]
        # Zero reference pairs never count as 2x confirmations. LOW also guards
        # any >reference elevation in >=2 pairs, a conservative frozen definition.
        consistent=sum(h is not None and b is not None and h>b for h,b in zip(hol,baseline))>=2
        median_ratio=statistics.median(defined) if defined else None
        material=sum(confirmations)>=2 and ((median_ratio is not None and median_ratio>=.25) or statistics.median(hidden)>=.25)
        low=all(v is not None and v<.10 for v in ratios) and all(v<.10 for v in hidden) and not consistent
        measurements[c]=dict(p95_hol_us=hol,p95_observed_io_us=observed,baseline_p95_hol_us=baseline,ratios=ratios,relative_ratios=relative,confirmations=confirmations,defined_ratio_count=len(defined),zero_reference_pairs=sum(b==0 for b in baseline),median_ratio=median_ratio,median_query_hidden_fractions=hidden,median_hidden_fraction=statistics.median(hidden),consistent_elevation=consistent,material=material,low=low)
    verdict='D6_INCONCLUSIVE' if phase_failed else 'D6_MATERIAL' if any(m['material'] for m in measurements.values()) else 'D6_LOW' if all(m['low'] for m in measurements.values()) else 'D6_INCONCLUSIVE'
    return {**base,'classification':verdict,'phase_failed_runs':phase_failed,'measurements':measurements,'reason':'Fixed sampled cohort only; no active-query occupancy or causal intervention'}


def validate_plan(plan):
    require(plan['issue']==18 and plan['schema_version']==1 and plan['main_base_commit']==BASE,'Protocol/base mismatch')
    require(plan['orders']==ORDERS and plan['sentinels']==SENTINELS and plan['accepted_run_count']==15 and plan['repetitions']==3,'Frozen run order/config mismatch')
    require(plan['search']==SEARCH and plan['thresholds']==THRESHOLDS,'Frozen search/threshold mismatch')
    for kind,sha in EXPECTED_PACKAGES.items():require(plan[kind+'_package_sha256']==sha,'Frozen package mismatch')
    require(plan['subjects']['instrumented']['commit']==SUBJECT and plan['subjects']['instrumented']['binary_sha256']==BINARY,'Subject/binary mismatch')
    require(plan['subjects']['STOCK']['commit']=='b9ec4ba86ff5d70bec277984777197f28dc2cf42','Golden mismatch')
    require(plan['trace']==dict(mode='DETAIL',causal_trace_enabled=True,detail_first_n=16,event_capacity=65536,sample_policy=explicit_policy(QIDS,10000)),'Sampling/config mismatch')
    require(plan['trace']['sample_policy']['sha256']==SAMPLE_SHA,'Sampling digest mismatch')
    require(plan['environment']['OMP_NUM_THREADS']=='REQUESTED_T','Thread environment policy mismatch')
    for k,v in dict(MKL_NUM_THREADS='8',OMP_DYNAMIC='FALSE',OMP_PROC_BIND=None,OMP_PLACES=None,GOMP_CPU_AFFINITY=None).items():require(k in plan['environment'] and plan['environment'][k]==v,'Native environment mismatch')
    require(plan['pause']['after_finalized_run_s']==5 and plan['telemetry']['collectors']==list(COLLECTORS) and plan['telemetry']['interval_s']==1 and plan['telemetry']['host_telemetry_requested'] is True,'Observer/pause mismatch')


def validate_record(r,plan):
    m,s,h=r['manifest'],r['summary'],r['trace_health'];subject=plan['subjects']['instrumented']
    require(r['runner_return_code']==0 and r['run_id']==m['run_id']==s['run_id'] and m['repetition']==r['round'],'Execution identity mismatch')
    require(m['harness_git_commit']==plan['harness_commit'] and m['harness_git_dirty'] is False and m['harness_git_branch']=='research/g0c2-sift10m-detail-d6','Harness provenance mismatch')
    require(m['subject_git_commit']==subject['commit'] and m['subject_git_dirty'] is False and m['subject_repo_root']==subject['root'] and m['executable_sha256']==subject['binary_sha256'] and m['executable']==str(Path(subject['root'])/'build/tests/search_disk_index'),'Subject provenance mismatch')
    require(m['subject_git_branch']==plan['subject_branch'],'Subject branch mismatch')
    for kind in EXPECTED_PACKAGES:require(m[kind+'_package_manifest_sha256']==plan[kind+'_package_sha256'],'Package mismatch')
    require(all(m.get(k)==v for k,v in {**SEARCH,**SENTINELS[r['config']]}.items()),'Search configuration mismatch')
    env={**plan['environment'],'OMP_NUM_THREADS':str(m['threads'])}
    for snapenv in [m['environment'],*(x.get('benchmark_environment') for x in r['runtime_snapshots'] if x.get('benchmark_environment'))]:
        for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OMP_DYNAMIC','OMP_PROC_BIND','OMP_PLACES','GOMP_CPU_AFFINITY'):
            require(snapenv.get(k)==env[k],'Native runtime environment mismatch')
    require(m['trace_mode']=='DETAIL' and m['causal_trace_enabled'] is True and all(m['trace_config'][k]==plan['trace'][k] for k in ('detail_first_n','event_capacity','sample_policy')),'Trace config mismatch')
    require(m['status']==s['run_status']=='success' and m['benchmark_status']==s['benchmark_status']=='success' and m['trace_valid'] is s['trace_valid'] is True,'Benchmark/trace failure')
    require(h['trace_valid'] is True and h['schema_version']==3 and h['trace_mode']=='DETAIL' and h['sample_requested']==h['sample_observed']==16 and h['requested_sample_qids']==h['observed_sample_qids']==QIDS and h['sample_policy']==plan['trace']['sample_policy'],'Trace sample health mismatch')
    require(h['query_rows']==10000 and h['buffer_capacity']==65536 and all(h[k]==0 for k in FAILURE_COUNTERS),'Trace health failure')
    require(m['host_telemetry_requested'] is m['host_telemetry_option'] is True and m['telemetry_interval_s']==1,'Host telemetry mismatch')
    require(all(m['host_telemetry_collectors'][k]['status']=='stopped' and m['host_telemetry_collectors'][k]['metric_rows']>0 and r['telemetry_presence'][k] for k in COLLECTORS),'Missing telemetry')
    require(m['mlflow_enabled'] is True and m['mlflow_status']=='success' and m['mlflow_run_id']==r['mlflow_run_id'],'MLflow transport mismatch')


def load_detail(record,plan):
    directory=Path(record['run_directory']);folder=Path(record['execution_directory'])
    names=[line.split('  ',1)[1] for line in (directory/'SHA256SUMS').read_text().splitlines()]
    required={'manifest.json','summary.json','command.sh','stdout.log','query_metrics.csv','system_metrics.csv','trace_health.json','ann_trace.bin','trace_check.json','events.jsonl',*('telemetry/'+k+'.log' for k in COLLECTORS)}
    require(len(names)==len(set(names)) and required.issubset(names),'Required checksum coverage missing')
    local_plan={**plan,'environment':{**plan['environment'],'OMP_NUM_THREADS':str(SENTINELS[record['config']]['threads'])}}
    r=load_run(record,local_plan);validate_record(r,plan);verify_sums(folder)
    require(read_json(folder/'offline_checker.stdout.json')['trace_valid'] is True,'Independent checker failed')
    require((folder/'pidstat_threads.log').stat().st_size>0,'External thread observer missing')
    m,h=r['manifest'],r['trace_health'];paths=plan['paths']
    require(m['argv']==[m['executable'],'uint8',paths['index_prefix'],str(m['threads']),str(m['wcap']),paths['query'],paths['ground_truth'],'10','l2','pq','2','0','100'],'Canonical argv mismatch')
    config,raw_events,rows=read_raw(directory/'ann_trace.bin')
    require(config['protocol_version']==2 and config['sample_policy']==plan['trace']['sample_policy'] and config['trace_mode']=='DETAIL' and config['workers']==m['threads'] and config['buffer_capacity']==65536 and config['queries']==10000,'PANTRC02 configuration mismatch')
    events=[json.loads(line) for line in (directory/'events.jsonl').read_text().splitlines()]
    require(events==[{**e,'run_id':record['run_id']} for e in raw_events],'Raw/event export disagreement')
    require(read_json(directory/'trace_check.json')['trace_valid'] is True and check_events(events,expected_qids=QIDS)['trace_valid'],'Causal/FIFO checker failed')
    with (directory/'query_metrics.csv').open() as stream:csv_rows=list(csv.DictReader(stream))
    require(len(rows)==len(csv_rows)==10000 and {q['query_id'] for q in rows}==set(range(10000)),'Missing/duplicate query counters')
    require(sorted(q['query_id'] for q in rows if q['is_sampled'])==QIDS,'Incorrect counter sampling')
    for row,export in zip(rows,csv_rows):
        require(export['run_id']==record['run_id'] and export['trace_mode']=='DETAIL' and int(export['schema_version'])==3 and all(int(export[k])==row[k] for k in COUNTER_FIELDS) and float(export['latency_us'])==row['latency_ns']/1000,'Raw/query export disagreement')
        require(all(row[k]==0 for k in FAILURE_COUNTERS) and row['submitted']==row['cqe_seen']==row['published']==row['cqe_count'] and row['selected']==row['submitted']+row['cache_ready'] and row['cache_ready']==row['cache_published'],'Query counter lifecycle failure')
        require(row['initial_width']==min(4,m['wcap']) and row['width_change_count']==row['final_width']-row['initial_width'] and row['initial_width']<=row['final_width']<=m['wcap'],'Width counter failure')
        require(0<=row['worker_id']<m['threads'] and row['linux_tid']>0 and row['expanded']<=row['published']+row['cache_published'] and 0<=row['max_completed_hidden']<=row['max_inflight']<=m['wcap'],'Query worker/expansion/bounds failure')
        require(row['is_sampled'] in (0,1) and (row['events_written']>0)==bool(row['is_sampled']),'Unsampled events/missing sample')
    for k in ('selected','submitted','cqe_seen','published','expanded','cache_ready','cache_published','events_written','width_change_count'):
        require(sum(q[k] for q in rows)==h[k],'Raw/health total disagreement')
    require(sum(q['events_written'] for q in rows)==len(events),'Event count disagreement')
    require(all(config[k]==h[k] for k in ('benchmark_origin_ns','benchmark_end_ns')),'Benchmark phase metadata disagreement')
    r['detail']=describe_detail(events,config['benchmark_origin_ns'],config['benchmark_end_ns'])
    for q in r['detail']['queries']:
        raw=next(row for row in rows if row['query_id']==q['query_id'])
        require(all(raw[k]==v for k,v in q['logical_work'].items() if k!='published_not_expanded'),'Query/event count disagreement')
        require(raw['worker_id']==q['worker_id'] and raw['linux_tid']==q['linux_tid'],'Query/event identity mismatch')
    r['telemetry_coverage']=telemetry_coverage(directory,1)
    r['whole_workload_counters']={k:sum(q[k] for q in rows) for k in ('selected','submitted','cqe_seen','published','expanded','cache_ready','cache_published')}
    return r


def validate_order(records):
    require(len(records)==15,'Missing run: expected 15')
    require([(r['round'],r['config']) for r in records]==[(i,c) for i,order in enumerate(ORDERS,1) for c in order],'Wrong run order')
    require(len({r['run_id'] for r in records})==15,'Duplicate run ID')


def analyze_campaign(campaign):
    require(digest(campaign/'PLAN.json')==(campaign/'PLAN.sha256').read_text().split()[0],'Plan SHA mismatch')
    plan=read_json(campaign/'PLAN.json');validate_plan(plan)
    raw=read_json(campaign/'results.json');validate_order(raw)
    records=[load_detail(r,plan) for r in raw]
    groups={c:[r for r in records if r['config']==c] for c in SENTINELS};gate=d6_gate(groups)
    audits={}
    first=records[0]['manifest']['timestamp_start'];last=records[-1]['manifest']['timestamp_end']
    require(plan['frozen_at']<first,'Plan frozen after measurement')
    for period in ('pre','post'):
        for kind in ('input','index'):
            a=read_json(campaign/f'{period}_{kind}.audit.json')
            require(a['exit_code']==0 and a['manifest_sha256']==plan[kind+'_package_sha256'] and '--full-components' in a['argv'] and plan['paths'][kind+'_manifest'] in a['argv'],'Package audit failure')
            require(a['timestamp_end']<first if period=='pre' else a['timestamp_start']>last,'Audits do not bracket runs')
            audits[period+'_'+kind]=a
    pauses=read_json(campaign/'pauses.json');require(len(pauses)==14,'Missing pauses')
    for p,r,next_run in zip(pauses,records,records[1:]):
        require((p['after_round'],p['after_config'])==(r['round'],r['config']) and p['requested_s']==5 and p['elapsed_s']>=5 and p['start']>=r['manifest']['timestamp_end'] and p['end']<=next_run['manifest']['timestamp_start'],'Pause policy violation')
    for name,sha in plan['code_sha256'].items():require(digest(campaign/name)==sha,'Frozen execution code changed')
    integrity=read_json(campaign/'INTEGRITY.json');require(all(integrity[k] for k in ('full_package_audits_pass','subjects_and_binaries_unchanged','frozen_plan_unchanged')),'Campaign integrity failed')
    mirror=read_json(campaign/'mlflow_readback.json');require(mirror['all_finished_and_bound'] is True and mirror['checked_runs']==15,'MLflow readback failure')
    summaries={c:{k:distribution(r['detail'][k]['p95'] for r in rows) for k in ('publication_hol_us','observed_io_us')} for c,rows in groups.items()}
    comparisons={}
    for reference,target in (('B','C'),('B','D'),('D','E'),('A','B')):
        paired=[]
        for a,b in zip(groups[reference],groups[target]):
            row=dict(round=a['round'],reference_run_id=a['run_id'],target_run_id=b['run_id'])
            for k in ('publication_hol_us','observed_io_us'):
                ref=a['detail'][k]['p95'];tar=b['detail'][k]['p95'];row[k+'_p95_delta_us']=tar-ref;row[k+'_p95_ratio']=tar/ref if ref>0 else None
            row['hidden_fraction_delta']=b['detail']['median_query_hidden_gt0_fraction']-a['detail']['median_query_hidden_gt0_fraction'];paired.append(row)
        comparisons[target+'_vs_'+reference]=paired
    return dict(campaign_valid=True,classification='G0C2_COMPLETE',campaign_id=plan['campaign_id'],plan_sha256=digest(campaign/'PLAN.json'),sampled_D6=gate,system_wide_D6='INCONCLUSIVE',D1_observability='NO',D4_selector_gate='NOT TESTED',runs=records,groups=summaries,comparisons=comparisons,package_audits=audits,integrity=integrity,source='Local finalized evidence; requests nested in query/run/configuration',exclusions=[])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--campaign',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    try:result=analyze_campaign(args.campaign)
    except (ValueError,KeyError,TypeError,OSError,statistics.StatisticsError) as error:result=dict(campaign_valid=False,classification='G0C2_INVALID',error=str(error))
    (args.output/'analysis.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({k:result.get(k) for k in ('campaign_valid','classification','campaign_id','error')}));return 0 if result['campaign_valid'] else 2


if __name__=='__main__':sys.exit(main())
