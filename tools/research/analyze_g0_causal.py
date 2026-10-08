#!/usr/bin/env python3
"""Analyze local G0 evidence, preserving run/query clusters; never read MLflow.

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
    return (event["timestamp_ns"], RANK[event["event"]], numeric("request_seq"),
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
                        "observed_io_us": observed, "publication_hol_us": hol,
                        "hol_to_observed_io_ratio": hol / observed if observed > 0 else None})
    return {"query_id": start["query_id"], "worker_id": start.get("worker_id"),
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


def e0_gate(records, thresholds):
    groups = {case: [r for r in records if r["case"] == case] for case in ("STOCK", "OFF", "LIGHT")}
    if any(len(rows) != 5 or {r["repetition"] for r in rows} != set(range(1, 6)) for rows in groups.values()):
        return {"status": "INCONCLUSIVE", "reason": "Missing five-repetition groups"}
    if any(r["summary"]["run_status"] != "success" or
           (r["case"] != "STOCK" and r["summary"].get("trace_valid") is not True) for r in records):
        return {"status": "FAIL", "reason": "Invalid benchmark/required trace"}
    spreads, deltas = {}, {}
    for case, rows in groups.items():
        spreads[case] = {metric: 100 * (max(v) - min(v)) / statistics.median(v)
                        for metric in thresholds["metrics"]
                        for v in [[r["summary"][metric] for r in rows]]}
    noisy = exceeded = False
    for target, base, margin in (("OFF", "STOCK", thresholds["OFF_vs_STOCK_percent"]),
                                ("LIGHT", "OFF", thresholds["LIGHT_vs_OFF_percent"])):
        label = f"{target}_vs_{base}"
        deltas[label] = {}
        for metric in thresholds["metrics"]:
            a = statistics.median(r["summary"][metric] for r in groups[target])
            b = statistics.median(r["summary"][metric] for r in groups[base])
            delta = 100 * (a / b - 1)
            deltas[label][metric] = delta
            exceeded |= abs(delta) > margin
            noisy |= max(spreads[target][metric], spreads[base][metric]) >= margin
    recalls = [r["summary"]["recall"] for r in records]
    recall_range = max(recalls) - min(recalls)
    recall_ok = recall_range <= thresholds["recall_max_range_percentage_points"] + 1e-10
    # The frozen noise rule has precedence over a derived failed-consistency label.
    status = "INCONCLUSIVE" if noisy else "FAIL" if exceeded or not recall_ok else "PROCEED"
    return {"status": status, "median_deltas_percent": deltas, "spread_percent": spreads,
            "noise_comparable_to_margin": noisy, "performance_margins_pass": not exceeded,
            "recall_range_percentage_points": recall_range, "recall_guard_pass": recall_ok,
            "thresholds": thresholds}


def d6_gate(config_runs, thresholds):
    if any(len(config_runs.get(c, [])) != 3 for c in ("B", "C", "D")):
        return {"classification": "D6_INCONCLUSIVE", "reason": "Missing three DETAIL repetitions for B/C/D"}
    groups = {c: sorted(config_runs[c], key=lambda r: r["repetition"]) for c in ("B", "C", "D")}
    if any({r["repetition"] for r in rows} != {1, 2, 3} or
           any(not r["detail"]["analysis_valid"] for r in rows) for rows in groups.values()):
        return {"classification": "D6_INCONCLUSIVE", "reason": "Invalid DETAIL grouping/evidence"}
    measurements = {}
    for c in ("C", "D"):
        hol = [r["detail"]["publication_hol_us"]["p95"] for r in groups[c]]
        obs = [r["detail"]["observed_io_us"]["p95"] for r in groups[c]]
        hidden = [r["detail"]["hidden_gt0_fraction"] for r in groups[c]]
        baseline = [r["detail"]["publication_hol_us"]["p95"] for r in groups["B"]]
        if any(v is None for v in hol + obs + hidden + baseline) or any(v <= 0 for v in obs):
            return {"classification": "D6_INCONCLUSIVE", "reason": "Insufficient physical I/O intervals"}
        majority = sum(h >= thresholds["hol_relative_factor"] * b and h > b for h, b in zip(hol, baseline)) >= thresholds["majority"]
        scale = (statistics.median(hol) >= thresholds["material_scale_ratio"] * statistics.median(obs)
                 or statistics.median(hidden) >= thresholds["material_hidden_fraction"])
        low = (all(h < thresholds["low_ratio"] * o for h, o in zip(hol, obs))
               and all(f < thresholds["low_hidden_fraction"] for f in hidden)
               and sum(h > b for h, b in zip(hol, baseline)) < thresholds["majority"])
        measurements[c] = {"p95_hol_us": hol, "p95_observed_io_us": obs, "hidden_gt0_fraction": hidden,
                           "baseline_p95_hol_us": baseline, "relative_majority": majority,
                           "material_scale": scale, "low": low}
    result = "D6_MATERIAL" if any(v["relative_majority"] and v["material_scale"] for v in measurements.values()) else (
             "D6_LOW" if all(v["low"] for v in measurements.values()) else "D6_INCONCLUSIVE")
    return {"classification": result, "measurements": measurements}


def telemetry(directory):
    path = directory / "system_metrics.csv"
    if not path.exists():
        return {"available": False, "series": {}}
    groups = defaultdict(list)
    with path.open() as stream:
        for row in csv.DictReader(stream):
            groups[(row["collector"], row["entity"], row["metric"])].append(float(row["value"]))
    return {"available": True, "series": {"|".join(key): distribution(values) for key, values in sorted(groups.items())},
            "aggregation": "Arithmetic sample summaries; not time-integrated or cross-device sums",
            "runtime_sqpoll": "Not collected in Stage A; Stage B observer is gated",
            "thread_cpu_context_switches": "Unavailable in Stage A collector configuration"}


def verify_sums(directory):
    for line in (directory / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split("  ", 1)
        path = directory / name
        if not path.resolve().is_relative_to(directory.resolve()) or digest(path) != expected:
            raise ValueError(f"Run checksum mismatch: {path}")


def load_run(record, plan):
    directory = Path(record["run_directory"])
    verify_sums(directory)
    manifest, summary = read_json(directory / "manifest.json"), read_json(directory / "summary.json")
    for key in ("input_package_manifest_sha256", "index_package_manifest_sha256"):
        if manifest.get(key) != plan[key.replace("manifest_", "")]:
            raise ValueError("Run package digest differs from frozen plan")
    expected_subject = plan["subjects"]["STOCK" if record["case"] == "STOCK" else "instrumented"]["commit"]
    if (manifest["harness_git_commit"] != plan["harness_commit"] or
        manifest["subject_git_commit"] != expected_subject or
        manifest["harness_git_dirty"] or manifest["subject_git_dirty"]):
        raise ValueError("Run provenance differs from frozen plan")
    if record["stage"] == "A":
        config = plan["stage_A"]
        expected_trace = plan["stage_A"]["cases"][record["case"]]
    else:
        config = plan["configurations"][record["case"]]
        expected_trace = plan[f"stage_{record['stage']}"]
    expected = {"threads": config["threads"], "wcap": config["wcap"],
        "benchmark_profile": plan["search"]["benchmark_profile"], "k": plan["search"]["K"],
        "l_search": plan["search"]["Lsearch"], "mem_l": plan["search"]["mem_L"],
        "distance_metric": plan["search"]["metric"], "neighbor_type": plan["search"]["neighbor_type"],
        "search_mode": plan["search"]["search_mode"], "query_count": plan["search"]["query_count"],
        "trace_mode": expected_trace["trace_mode"], "causal_trace_enabled": expected_trace["causal_trace"]}
    if any(manifest.get(k) != v for k, v in expected.items()):
        raise ValueError("Search/trace configuration differs from frozen plan")
    for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OMP_PLACES", "OMP_PROC_BIND"):
        if manifest["environment"].get(key) != plan["environment"][key]:
            raise ValueError("Run environment differs from frozen plan")
    if expected_trace["causal_trace"]:
        if any(manifest["trace_config"][k] != plan["trace"][k] for k in ("detail_first_n", "event_capacity")):
            raise ValueError("Sampling/capacity differs from frozen plan")
    if summary["run_status"] != "success" or summary["run_id"] != record["run_id"]:
        raise ValueError("Unaccepted run")
    result = {**record, "summary": summary, "timestamp_start": manifest["timestamp_start"],
              "timestamp_end": manifest["timestamp_end"], "telemetry": telemetry(directory)}
    if summary.get("causal_trace_enabled"):
        health = read_json(directory / "trace_health.json")
        if health["trace_valid"] is not True or any(health.get(k, 0) for k in FAILURES):
            raise ValueError("Invalid trace health")
        result["trace_health"] = health
        with (directory / "query_metrics.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        expected_rows = 0 if record["trace_mode"] == "OFF" else plan["search"]["query_count"]
        if len(rows) != expected_rows or len({r["query_id"] for r in rows}) != len(rows):
            raise ValueError("Missing/duplicate query counter rows")
        result["query_aggregates"] = {"rows": len(rows),
            "initial_width": dict(Counter(r["initial_width"] for r in rows)),
            "final_width": dict(Counter(r["final_width"] for r in rows)),
            "width_changes": distribution(int(r["width_change_count"]) for r in rows),
            "logical_work": {k: sum(int(r[k]) for r in rows) for k in
                             ("selected", "submitted", "cqe_seen", "published", "expanded", "cache_ready", "cache_published")}}
        if record["trace_mode"] == "DETAIL":
            events = [json.loads(line) for line in (directory / "events.jsonl").read_text().splitlines() if line.strip()]
            detail = analyze_events(events)
            sampled = {int(r["query_id"]): r for r in rows if r["is_sampled"] == "1"}
            if set(sampled) != {q["query_id"] for q in detail["queries"]} or len(sampled) != health["sample_requested"]:
                raise ValueError("Sample grouping contradicts trace health")
            for query in detail["queries"]:
                row = sampled[query["query_id"]]
                for key, value in query["logical_work"].items():
                    if key != "published_not_expanded" and int(row[key]) != value:
                        raise ValueError("Query reconstruction contradicts counters")
            result["detail"] = detail
    return result


def group_runs(records):
    groups = defaultdict(list)
    for record in records:
        groups[(record["stage"], record["case"])].append(record)
    return {f"{stage}/{case}": {metric: distribution(r["summary"][metric] for r in sorted(rows, key=lambda r: r["repetition"]))
                                for metric in METRICS} for (stage, case), rows in groups.items()}


def detail_distributions(records):
    """One observation per run for config statistics, with full query clusters retained."""
    grouped = defaultdict(list)
    for record in records:
        if "detail" in record:
            grouped[record["case"]].append(record)
    return {case: {
        "run_ids": [r["run_id"] for r in rows],
        "p95_publication_hol_us": distribution(r["detail"]["publication_hol_us"]["p95"] for r in rows),
        "p95_observed_io_us": distribution(r["detail"]["observed_io_us"]["p95"] for r in rows),
        "hidden_gt0_fraction": distribution(r["detail"]["hidden_gt0_fraction"] for r in rows),
        "query_counts": [len(r["detail"]["queries"]) for r in rows],
        "inference": "Run-level descriptive distribution only; query/request clusters in runs"}
        for case, rows in grouped.items()}


def analyze_campaign(campaign):
    plan_path = campaign / "PLAN.json"
    if digest(plan_path) != (campaign / "PLAN.sha256").read_text().split()[0]:
        raise ValueError("Frozen plan digest mismatch")
    plan = read_json(plan_path)
    audits = {}
    for when in ("pre", "post"):
        for kind in ("input", "index"):
            audit = read_json(campaign / f"{when}_{kind}.audit.json")
            if (audit["exit_code"] != 0 or audit["manifest_sha256"] != plan[f"{kind}_package_sha256"]
                or "--full-components" not in audit["argv"]):
                raise ValueError("Full package audit failed")
            audits[f"{when}_{kind}"] = audit
    records = []
    for stage in ("A", "B", "C"):
        path = campaign / f"stage_{stage}_results.json"
        if path.exists():
            records.extend(load_run(r, plan) for r in read_json(path))
    if records:
        machine = read_json(campaign / "machine_before.json")
        for run in records:
            binary_case = "PipeANN" if run["case"] == "STOCK" else "PipeANN-p0"
            manifest = read_json(Path(run["run_directory"]) / "manifest.json")
            if manifest["executable_sha256"] != machine["binaries"][binary_case]["sha256"]:
                raise ValueError("Executable hash differs from preflight")
        if any(datetime.fromisoformat(left["timestamp_end"]) > datetime.fromisoformat(right["timestamp_start"])
               for left, right in zip(records, records[1:])):
            raise ValueError("Measurements overlap or chronological order differs")
        first = min(datetime.fromisoformat(r["timestamp_start"]) for r in records)
        last = max(datetime.fromisoformat(r["timestamp_end"]) for r in records)
        if any(datetime.fromisoformat(audits[f"pre_{k}"]["timestamp_end"]) > first or
               datetime.fromisoformat(audits[f"post_{k}"]["timestamp_start"]) < last for k in ("input", "index")):
            raise ValueError("Full audits do not bracket measurements")
    for stage in ("B", "C"):
        stage_records = [r for r in records if r["stage"] == stage]
        expected = [(i, case) for i, order in enumerate(plan[f"stage_{stage}"]["orders"], 1) for case in order]
        if stage_records and [(r["repetition"], r["case"]) for r in stage_records] != expected:
            raise ValueError(f"Stage {stage} incomplete/order differs from frozen plan")
    a = [r for r in records if r["stage"] == "A"]
    expected_order = [(rep, case) for rep, order in enumerate(plan["stage_A"]["orders"], 1) for case in order]
    if [(r["repetition"], r["case"]) for r in a] != expected_order:
        raise ValueError("Stage A run order differs from frozen plan")
    gate = e0_gate(a, plan["e0_thresholds"])
    if gate["status"] != "PROCEED" and any(r["stage"] != "A" for r in records):
        raise ValueError("Later stages executed without E0 PROCEED")
    detail_groups = defaultdict(list)
    for record in records:
        if record["stage"] == "C":
            detail_groups[record["case"]].append(record)
    return {"schema_version": 1, "analysis_valid": True, "campaign_id": plan["campaign_id"],
            "plan_sha256": digest(plan_path), "package_audits": audits, "runs": records,
            "run_distributions": group_runs(records), "detail_distributions": detail_distributions(records), "E0": gate,
            "D6": d6_gate(detail_groups, plan["d6_thresholds"]),
            "headline_source": "Local finalized manifest/summary/query_metrics/telemetry/events; MLflow never queried",
            "stages_B_C": "not executed: E0 gate" if gate["status"] != "PROCEED" else "see runs"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New directory, never overwritten")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    try:
        result = analyze_campaign(args.campaign)
    except (ValueError, KeyError, TypeError, OSError) as error:
        result = {"analysis_valid": False, "error": str(error), "interpretation": "STOP"}
    (args.output / "analysis.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    if result["analysis_valid"]:
        (args.output / "E0_GATE_ANALYZED.json").write_text(json.dumps(result["E0"], indent=2) + "\n")
        with (args.output / "run_metrics.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, ("stage", "case", "repetition", "run_id", "mlflow_run_id", *METRICS))
            writer.writeheader()
            for run in result["runs"]:
                writer.writerow({**{k: run[k] for k in ("stage", "case", "repetition", "run_id", "mlflow_run_id")},
                                 **{k: run["summary"][k] for k in METRICS}})
    print(json.dumps({k: result.get(k) for k in ("analysis_valid", "campaign_id", "E0", "D6", "error")}, indent=2))
    return 0 if result["analysis_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
