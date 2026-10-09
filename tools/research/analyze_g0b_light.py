#!/usr/bin/env python3
"""Issue #14 LIGHT sentinels: local evidence, run-level descriptive statistics only."""
import argparse
from collections import Counter
import csv
from datetime import datetime
import json
import math
from pathlib import Path
import statistics
import sys

from analyze_e0b import COLLECTORS, ZERO_HEALTH, digest, load_run, read_json, verify_sums

ORDERS = [list('ABCDE'), list('BCDEA'), list('CDEAB'), list('DEABC'), list('EABCD')]
SENTINELS = dict(zip('ABCDE', ({'threads': t, 'wcap': w} for t, w in
                             ((1, 32), (8, 32), (8, 64), (16, 32), (16, 16)))))
EXPECTED_PACKAGES = {'input': '47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3',
                     'index': '8955f8bca0c8ebb5afbd2a69e9760fc829d22ba76a4ef7b482339e88b2489595'}
SUBJECT_COMMIT = '3bdcc064cb96aae4cd845bd2bb6adc5f5ba63e19'
HARNESS_COMMIT = 'b7ba71e6fc7b20630ca2a7efe6d95cd36a75f2cf'
METRICS = ('qps', 'mean_latency_us', 'p99_latency_us', 'recall', 'mean_ios')
COUNTS = ('selected', 'submitted', 'cqe_seen', 'published', 'expanded', 'cache_ready', 'cache_published')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def descriptive(values):
    values = list(values)
    require(values and all(type(v) in (int, float) and math.isfinite(v) for v in values),
            'Missing/nonfinite descriptive metric')
    return dict(values=values, n=len(values), mean=statistics.mean(values), median=statistics.median(values),
                min=min(values), max=max(values), sample_sd=statistics.stdev(values) if len(values) > 1 else None)


def query_aggregates(rows, count, wcap, threads, run_id):
    require(len(rows) == count and {r['query_id'] for r in rows} == set(range(count)), 'Missing/duplicate query rows')
    for r in rows:
        require(r['run_id'] == run_id and r['trace_mode'] == 'LIGHT', 'Query identity/mode mismatch')
        require(0 <= r['worker_id'] < threads and r['linux_tid'] > 0, 'Worker identity invalid')
        require(r['initial_width'] == min(4, wcap) and r['initial_width'] <= r['final_width'] <= wcap,
                'Invalid actual width')
        require(r['width_change_count'] == r['final_width'] - r['initial_width'], 'Stock +1 width count mismatch')
        require(all(r[k] == 0 for k in (*ZERO_HEALTH, 'events_written', 'is_sampled')), 'Invalid LIGHT query health')
        require(r['selected'] == r['submitted'] + r['cache_ready'] and
                r['submitted'] == r['cqe_seen'] == r['published'] == r['cqe_count'] and
                r['cache_ready'] == r['cache_published'], 'Cache/physical lifecycle mismatch')
        require(r['expanded'] <= r['published'] + r['cache_published'], 'Expansion exceeds search-visible nodes')
        require(0 <= r['max_inflight'] <= wcap and 0 <= r['max_completed_hidden'] <= r['max_inflight'],
                'Inflight/hidden bounds violated')
        require(all(r[k] >= 0 for k in COUNTS), 'Negative logical counter')
    worker_tids = {}
    for r in rows:
        require(worker_tids.setdefault(r['worker_id'], r['linux_tid']) == r['linux_tid'], 'Worker/TID changed within run')
    require(len(set(worker_tids.values())) == len(worker_tids), 'Duplicate worker TID')
    totals = {k: sum(r[k] for r in rows) for k in COUNTS}
    return {'query_count': count, 'worker_tids': worker_tids, 'totals': totals, 'per_query': {k: v / count for k, v in totals.items()},
            'initial_width_distribution': dict(sorted(Counter(r['initial_width'] for r in rows).items())),
            'final_width_distribution': dict(sorted(Counter(r['final_width'] for r in rows).items())),
            'query_width_statistics': {k: descriptive(r[k] for r in rows) for k in ('initial_width', 'final_width', 'width_change_count')},
            'mean_initial_width': statistics.mean(r['initial_width'] for r in rows),
            'mean_final_width': statistics.mean(r['final_width'] for r in rows),
            'mean_width_increases': statistics.mean(r['width_change_count'] for r in rows),
            'width_increase_total': sum(r['width_change_count'] for r in rows),
            'ending_at_wcap_fraction': sum(r['final_width'] == wcap for r in rows) / count,
            'max_inflight': max(r['max_inflight'] for r in rows),
            'max_completed_hidden': max(r['max_completed_hidden'] for r in rows),
            'published_not_expanded': totals['published'] + totals['cache_published'] - totals['expanded'],
            'time_weighted_width': None, 'publication_hol_us': None}


def validate_plan(plan):
    require(plan['schema_version'] == 1 and plan['issue'] == 14, 'Unsupported protocol')
    require(all(plan[f'{kind}_package_sha256'] == sha for kind, sha in EXPECTED_PACKAGES.items()), 'Frozen package mismatch')
    require(plan['harness_commit'] == HARNESS_COMMIT and plan['subjects']['instrumented']['commit'] == SUBJECT_COMMIT,
            'Frozen provenance mismatch')
    require(plan['orders'] == ORDERS and plan['sentinels'] == SENTINELS, 'Frozen order/configuration mismatch')
    require(plan['accepted_run_count'] == 25 and plan['repetitions'] == 5, 'Repetition mismatch')
    require(plan['search'] == {'benchmark_profile': 'pipeann-b9ec4ba', 'dataset_id': 'sift10m', 'data_type': 'uint8',
                             'distance_metric': 'l2', 'k': 10, 'l_search': 100, 'mem_l': 0, 'neighbor_type': 'pq',
                             'query_count': 10000, 'search_mode': 2}, 'Frozen search mismatch')
    require(plan['environment']['OMP_NUM_THREADS'] == 'REQUESTED_T', 'Requested-T policy mismatch')
    for k, v in {'MKL_NUM_THREADS': '8', 'OMP_DYNAMIC': 'FALSE', 'OMP_PROC_BIND': None,
                 'OMP_PLACES': None, 'GOMP_CPU_AFFINITY': None}.items():
        require(plan['environment'].get(k) == v, 'Native environment mismatch')
    require(plan['pause']['after_finalized_run_s'] == 5 and plan['telemetry']['interval_s'] == 1 and
            plan['telemetry']['collectors'] == list(COLLECTORS), 'Observer/pause policy mismatch')
    require(plan['trace']['mode'] == 'LIGHT' and plan['trace']['causal_trace_enabled'] is True,
            'LIGHT-only protocol mismatch')


def validate_records(records, plan):
    validate_plan(plan)
    require(len(records) == 25, 'Missing run: expected 25')
    require([(r['round'], r['config']) for r in records] ==
            [(i, c) for i, order in enumerate(ORDERS, 1) for c in order], 'Run order mismatch')
    require(len({r['run_id'] for r in records}) == 25, 'Duplicate run ID')
    subject = plan['subjects']['instrumented']
    for r in records:
        m, s, h = r['manifest'], r['summary'], r['trace_health']
        require(r['runner_return_code'] == 0 and m['run_id'] == s['run_id'] == r['run_id'], 'Run identity/exit mismatch')
        require(m['repetition'] == r['round'], 'Repetition identity mismatch')
        for kind in ('input', 'index'):
            require(m[f'{kind}_package_manifest_sha256'] == plan[f'{kind}_package_sha256'], 'Package mismatch')
        require(m['subject_git_commit'] == subject['commit'] and m['subject_repo_root'] == subject['root'] and
                m['subject_git_dirty'] is False and m['executable_sha256'] == subject['binary_sha256'] and
                m['executable'] == str(Path(subject['root']) / 'build/tests/search_disk_index'), 'Subject/binary mismatch')
        require(m['harness_git_branch'] == 'research/g0b-sift10m-light-sentinels' and
                m['subject_git_branch'] == 'research/p0-causal-instrumentation' and
                m['harness_repo_root'] == str(Path(subject['root']).parent / 'Parallel_ANN_Research'), 'Repository namespace mismatch')
        require(m['harness_git_commit'] == plan['harness_commit'] and m['harness_git_dirty'] is False,
                'Harness provenance mismatch')
        require(all(m.get(k) == v for k, v in {**plan['search'], **SENTINELS[r['config']]}.items()),
                'Execution configuration mismatch')
        require(m['environment']['OMP_NUM_THREADS'] == str(SENTINELS[r['config']]['threads']) and
                m['environment']['MKL_NUM_THREADS'] == '8', 'Native placement mismatch')
        require(all(m['environment'].get(k) is None for k in ('OMP_PLACES', 'OMP_PROC_BIND')), 'Native affinity mismatch')
        require(m['trace_mode'] == 'LIGHT' and m['causal_trace_enabled'] is True and
                all(m['trace_config'][k] == plan['trace'][k] for k in ('detail_first_n', 'event_capacity')),
                'Trace configuration mismatch')
        require(m['host_telemetry_requested'] is True and m['host_telemetry_option'] is True and
                m['telemetry_interval_s'] == 1, 'Host telemetry policy mismatch')
        require(all(m['host_telemetry_collectors'].get(k, {}).get('status') == 'stopped' and
                    m['host_telemetry_collectors'][k].get('metric_rows', 0) > 0 and
                    r['telemetry_presence'].get(k) for k in COLLECTORS), 'Host telemetry unavailable')
        require(m['mlflow_enabled'] is True and m['mlflow_status'] == 'success' and
                m['mlflow_run_id'] == r['mlflow_run_id'], 'MLflow mirror policy failure')
        require(m['benchmark_status'] == s['benchmark_status'] == 'success' and
                m['status'] == s['run_status'] == 'success' and m['trace_valid'] is s['trace_valid'] is True,
                'Experiment failed')
        require(h['trace_valid'] is True and h['trace_mode'] == 'LIGHT' and h['query_rows'] == plan['search']['query_count']
                and all(h.get(k) == 0 for k in (*ZERO_HEALTH, 'events_written', 'sample_observed', 'sample_requested')),
                'Trace health failed')
        q = r['queries']
        require(q['query_count'] == plan['search']['query_count'], 'Query count mismatch')
        require(all(q['totals'][k] == h[k] for k in COUNTS) and
                q['width_increase_total'] == h['width_change_count'] and
                q['max_inflight'] == h['max_inflight'] and q['max_completed_hidden'] == h['max_completed_hidden'],
                'Query/health aggregate mismatch')
        # Commands retain explicit unset keys; runtime process environment independently checks them when readable.
        for snap in r.get('runtime_snapshots', []):
            env = snap.get('benchmark_environment', {})
            if env is not None and env:
                for key in ('OMP_PROC_BIND', 'OMP_PLACES', 'GOMP_CPU_AFFINITY'):
                    require(env.get(key) is None, 'Runtime affinity unexpectedly set')
                for key, expected in (('OMP_NUM_THREADS', str(m['threads'])), ('MKL_NUM_THREADS', '8'), ('OMP_DYNAMIC', 'FALSE')):
                    require(env.get(key) == expected, 'Runtime native environment mismatch')


def analyze_records(records, plan):
    validate_records(records, plan)
    groups = {}
    for config in SENTINELS:
        runs = [r for r in records if r['config'] == config]
        metrics = {k: descriptive(r['summary'][k] for r in runs) for k in METRICS}
        for k in ('mean_initial_width', 'mean_final_width', 'mean_width_increases', 'ending_at_wcap_fraction', 'max_inflight', 'max_completed_hidden'):
            metrics[k] = descriptive(r['queries'][k] for r in runs)
        for k in COUNTS:
            metrics[k + '_total'] = descriptive(r['queries']['totals'][k] for r in runs)
            metrics[k + '_per_query'] = descriptive(r['queries']['per_query'][k] for r in runs)
        groups[config] = {'configuration': SENTINELS[config], 'run_ids': [r['run_id'] for r in runs],
                          'metrics': metrics, 'width_distributions_per_run': [r['queries']['final_width_distribution'] for r in runs]}
    comparisons = {}
    for reference, target in (('B', 'C'), ('B', 'D'), ('D', 'E'), ('A', 'B')):
        comparisons[target + '_vs_' + reference] = {
            k: (groups[target]['metrics'][k]['median'] - groups[reference]['metrics'][k]['median']) if k == 'recall'
            else 100 * (groups[target]['metrics'][k]['median'] / groups[reference]['metrics'][k]['median'] - 1)
            for k in METRICS}
    return {'campaign_valid': True, 'classification': 'G0B_COMPLETE', 'D6': 'D6_INCONCLUSIVE',
            'D1_observability': 'NO', 'D4_selector_gate': 'NOT TESTED', 'accepted_runs': 25,
            'statistical_unit': 'RUN; query distributions nested per run', 'groups': groups, 'comparisons': comparisons}


def telemetry_coverage(directory, interval):
    series = {}
    with (directory / 'system_metrics.csv').open() as stream:
        for row in csv.DictReader(stream):
            key = '|'.join((row['collector'], row['entity'], row['metric']))
            series.setdefault(key, []).append(row['sample_time_local'])
    result = {}
    for key, times in series.items():
        parsed = [datetime.fromisoformat(t) if 'T' in t else datetime.strptime(t, '%H:%M:%S') for t in times]
        # One run cannot span a day; modular subtraction also handles midnight.
        span = (parsed[-1] - parsed[0]).total_seconds() % 86400
        result[key] = {'sample_count': len(times), 'timestamps_local': times, 'first_to_last_span_s': span,
                       'nominal_interval_coverage_s': len(times) * interval,
                       'limitation': 'Includes loading/startup/partial intervals; not steady-state search coverage'}
    return result


def load_light(record, plan):
    local_plan = {**plan, 'environment': {**plan['environment'], 'OMP_NUM_THREADS': str(SENTINELS[record['config']]['threads'])}}
    directory = Path(record['run_directory'])
    names = [line.split('  ', 1)[1] for line in (directory / 'SHA256SUMS').read_text().splitlines()]
    required = {'manifest.json', 'summary.json', 'command.sh', 'stdout.log', 'query_metrics.csv', 'system_metrics.csv',
                'trace_health.json', 'ann_trace.bin', 'trace_check.json', 'events.jsonl', *('telemetry/' + c + '.log' for c in COLLECTORS)}
    require(len(names) == len(set(names)) and required.issubset(names), 'Required checksum coverage missing')
    r = load_run(record, local_plan)
    m = r['manifest']; paths = plan['paths']
    expected_argv = [m['executable'], 'uint8', paths['index_prefix'], str(m['threads']), str(m['wcap']),
                     paths['query'], paths['ground_truth'], '10', 'l2', 'pq', '2', '0', '100']
    require(m['argv'] == expected_argv, 'Canonical benchmark argv mismatch')
    folder = Path(record['execution_directory']); verify_sums(folder)
    require((folder / 'pidstat_threads.log').is_file() and (folder / 'pidstat_threads.log').stat().st_size > 0,
            'External pidstat observer missing')
    require((directory / 'events.jsonl').stat().st_size == 0 and read_json(directory / 'trace_check.json')['trace_valid'],
            'Unexpected LIGHT events or checker failure')
    with (Path(record['run_directory']) / 'query_metrics.csv').open() as stream:
        rows = []
        for row in csv.DictReader(stream):
            rows.append({k: v if k in ('schema_version', 'run_id', 'trace_mode') else
                         float(v) if k == 'latency_us' else int(v) for k, v in row.items()})
    r['queries'] = query_aggregates(rows, plan['search']['query_count'], SENTINELS[record['config']]['wcap'],
                                  SENTINELS[record['config']]['threads'], record['run_id'])
    r['telemetry_coverage'] = telemetry_coverage(Path(record['run_directory']), plan['telemetry']['interval_s'])
    return r


def analyze_campaign(campaign):
    require(digest(campaign / 'PLAN.json') == (campaign / 'PLAN.sha256').read_text().split()[0], 'Frozen plan SHA mismatch')
    plan = read_json(campaign / 'PLAN.json'); validate_plan(plan)
    records = [load_light(r, plan) for r in read_json(campaign / 'results.json')]
    result = analyze_records(records, plan)
    first = datetime.fromisoformat(records[0]['manifest']['timestamp_start'])
    last = datetime.fromisoformat(records[-1]['manifest']['timestamp_end'])
    require(datetime.fromisoformat(plan['frozen_at']) < first, 'Plan frozen late')
    audits = {}
    for period in ('pre', 'post'):
        for kind in ('input', 'index'):
            a = read_json(campaign / f'{period}_{kind}.audit.json')
            require(a['exit_code'] == 0 and a['manifest_sha256'] == plan[f'{kind}_package_sha256'] and
                    '--full-components' in a['argv'] and plan['paths'][kind + '_manifest'] in a['argv'],
                    'Full-content package audit failed')
            require(datetime.fromisoformat(a['timestamp_end']) < first if period == 'pre' else
                    datetime.fromisoformat(a['timestamp_start']) > last, 'Audits do not bracket campaign')
            audits[period + '_' + kind] = a
    pauses = read_json(campaign / 'pauses.json')
    require(len(pauses) == 24, 'Pause completeness failure')
    for pause, r, following in zip(pauses, records, records[1:]):
        require((pause['after_round'], pause['after_config']) == (r['round'], r['config']) and
                pause['requested_s'] == 5 and pause['elapsed_s'] >= 5, 'Frozen pause policy violation')
        require(datetime.fromisoformat(pause['start']) >= datetime.fromisoformat(r['manifest']['timestamp_end']) and
                datetime.fromisoformat(pause['end']) <= datetime.fromisoformat(following['manifest']['timestamp_start']),
                'Pause/measurement chronology violated')
    for name, sha in plan['code_sha256'].items():
        require(digest(campaign / name) == sha, 'Campaign execution code changed')
    integrity = read_json(campaign / 'INTEGRITY.json')
    require(integrity['full_package_audits_pass'] and integrity['subjects_and_binaries_unchanged'] and
            integrity['frozen_plan_unchanged'], 'Post-campaign integrity invalid')
    return {**result, 'campaign_id': plan['campaign_id'], 'plan_sha256': digest(campaign / 'PLAN.json'),
            'package_audits': audits, 'integrity': integrity, 'runs': records,
            'source': 'Local authoritative artifacts only; no MLflow queries', 'exclusions': []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    try:
        result = analyze_campaign(args.campaign)
    except (ValueError, KeyError, TypeError, OSError, statistics.StatisticsError) as error:
        result = {'campaign_valid': False, 'classification': 'G0B_INVALID', 'error': str(error)}
    (args.output / 'analysis.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({k: result.get(k) for k in ('campaign_valid', 'classification', 'campaign_id', 'error')}, indent=2))
    return 0 if result['campaign_valid'] else 2


if __name__ == '__main__':
    sys.exit(main())
