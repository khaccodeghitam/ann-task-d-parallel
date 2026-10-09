#!/usr/bin/env python3
"""E0b paired-block analysis of immutable local artifacts; MLflow is not a source."""
import argparse
import csv
from datetime import datetime
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import random
import shlex
import statistics
import sys

ORDERS = [("STOCK", "OFF", "LIGHT"), ("STOCK", "LIGHT", "OFF"),
          ("OFF", "STOCK", "LIGHT"), ("OFF", "LIGHT", "STOCK"),
          ("LIGHT", "STOCK", "OFF"), ("LIGHT", "OFF", "STOCK")] * 2
COLLECTORS = ("mpstat", "pidstat", "iostat")
COMPARISONS = (("OFF", "STOCK", 3), ("LIGHT", "OFF", 5))
ZERO_HEALTH = ("events_dropped", "ordering_violations", "negative_hidden_count",
              "unmatched_submit", "unmatched_cqe", "unmatched_publish",
              "outstanding_at_query_end", "table_overflows")


def read_json(path):
    return json.loads(Path(path).read_text())


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def verify_sums(directory):
    for line in (directory / 'SHA256SUMS').read_text().splitlines():
        expected, name = line.split('  ', 1)
        path = directory / name
        if not path.resolve().is_relative_to(directory.resolve()) or digest(path) != expected:
            raise ValueError(f'Checksum mismatch: {path}')


def percentile(values, p):
    values = sorted(values)
    index = p * (len(values) - 1)
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * (index - lower)


def paired_delta(target, reference, recall=False):
    if not all(type(v) in (float, int) and math.isfinite(v) for v in (target, reference)):
        raise ValueError('Missing/nonfinite paired metric')
    t, r = Decimal(str(target)), Decimal(str(reference))
    if recall:
        return float(t - r)
    if r <= 0 or t <= 0:
        raise ValueError('Nonpositive paired performance metric')
    return float(100 * (t / r - 1))


def descriptive(values):
    values = list(values)
    median = statistics.median(values)
    return {'values': values, 'n': len(values), 'mean': statistics.mean(values),
            'median': median, 'median_absolute_paired_delta': statistics.median(abs(v) for v in values),
            'sample_sd': statistics.stdev(values) if len(values) > 1 else None,
            'min': min(values), 'max': max(values),
            'MAD': statistics.median(abs(v - median) for v in values)}


def bootstrap_median(values, samples=20000, seed=20261008):
    if len(values) != 12:
        raise ValueError('Bootstrap unit requires exactly 12 block observations')
    rng = random.Random(seed)
    medians = [statistics.median(values[rng.randrange(12)] for _ in range(12)) for _ in range(samples)]
    return [percentile(medians, .05), percentile(medians, .95)]


def comparison_gate(median, ci, margin, recall=False):
    lo, hi = ci
    if lo > hi or not all(math.isfinite(v) for v in (median, lo, hi)):
        raise ValueError('Invalid CI')
    if lo > margin or hi < -margin:
        return 'FAIL'
    if lo >= -margin and hi <= margin and (recall or abs(median) <= margin):
        return 'PROCEED'
    return 'INCONCLUSIVE'


def validate_records(records, plan):
    expected = [(i, case) for i, order in enumerate(ORDERS, 1) for case in order]
    if [tuple(order) for order in plan['orders']] != ORDERS:
        raise ValueError('Frozen plan does not match Issue #10 order')
    if any(type(r['block']) is not int or not 1 <= r['block'] <= 12 for r in records):
        raise ValueError('Invalid block identity')
    if len(records) != 36:
        raise ValueError('Missing/incomplete 12-block campaign: STOP')
    if [(r['block'], r['case']) for r in records] != expected:
        raise ValueError('Block order violation: STOP')
    if len({r['run_id'] for r in records}) != 36:
        raise ValueError('Duplicate/reused run ID')
    for r in records:
        m, s = r['manifest'], r['summary']
        if m['repetition'] != r['block']:
            raise ValueError('Block/repetition mismatch')
        if m['run_id'] != r['run_id'] or s['run_id'] != r['run_id']:
            raise ValueError('Run identity mismatch')
        for k in ('input', 'index'):
            if m.get(f'{k}_package_manifest_sha256') != plan[f'{k}_package_sha256']:
                raise ValueError('Package mismatch')
        subject = plan['subjects']['STOCK' if r['case'] == 'STOCK' else 'instrumented']
        if (m['subject_git_commit'] != subject['commit'] or m['subject_repo_root'] != subject['root']
            or m['subject_git_dirty'] or m['executable_sha256'] != subject['binary_sha256']):
            raise ValueError('Subject/binary provenance mismatch')
        if m['harness_git_commit'] != plan['harness_commit'] or m['harness_git_dirty']:
            raise ValueError('Harness provenance mismatch')
        if any(m.get(k) != v for k, v in plan['search'].items()):
            raise ValueError('Search configuration mismatch')
        for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_PROC_BIND', 'OMP_PLACES'):
            if m['environment'].get(key) != plan['environment'][key]:
                raise ValueError('Placement/environment mismatch')
        if any(m.get(k) != v for k, v in plan['variants'][r['case']].items()):
            raise ValueError('Variant contract mismatch')
        if m['causal_trace_enabled'] and any(m['trace_config'][k] != plan['trace'][k]
                for k in ('detail_first_n', 'event_capacity')):
            raise ValueError('Trace configuration mismatch')
        if not m.get('host_telemetry_requested') or m.get('host_telemetry_option') is not True:
            raise ValueError('Matched host telemetry request missing')
        if m['telemetry_interval_s'] != plan['telemetry']['interval_s']:
            raise ValueError('Telemetry interval mismatch')
        if any(m['host_telemetry_collectors'].get(k, {}).get('status') != 'stopped' or
               not m['host_telemetry_collectors'][k].get('metric_rows') or
               not r.get('telemetry_presence', {}).get(k) for k in COLLECTORS):
            raise ValueError('Matched telemetry presence/status missing')
        if not m['mlflow_enabled']:
            raise ValueError('MLflow policy mismatch')
        if s['benchmark_status'] != 'success':
            raise ValueError('Benchmark execution failure: campaign STOP')


def analyze_records(records, plan):
    validate_records(records, plan)
    if plan['bootstrap'] != {**plan['bootstrap'], 'samples': 20000, 'seed': 20261008, 'block_count': 12,
                             'ci_percent': 90, 'unit': 'block'}:
        raise ValueError('Bootstrap protocol mismatch')
    if plan['effect_margins_percent'] != {'OFF_vs_STOCK': 3, 'LIGHT_vs_OFF': 5} or plan['recall_tolerance_percentage_points'] != .02:
        raise ValueError('Frozen effect tolerance mismatch')
    blocks = {i: {r['case']: r for r in records if r['block'] == i} for i in range(1, 13)}
    comparisons, gates = {}, []
    for target, reference, margin in COMPARISONS:
        name = f'{target}_vs_{reference}'; comparisons[name] = {}
        for metric in ('qps', 'mean_latency_us', 'recall'):
            values = [paired_delta(blocks[i][target]['summary'][metric], blocks[i][reference]['summary'][metric],
                                   recall=metric == 'recall') for i in range(1, 13)]
            stats = descriptive(values)
            ci = bootstrap_median(values)
            limit = .02 if metric == 'recall' else margin
            status = comparison_gate(stats['median'], ci, limit, recall=metric == 'recall')
            comparisons[name][metric] = {**stats, 'ci90_median': ci, 'margin': limit, 'decision': status,
                                       'unit': 'percentage_points' if metric == 'recall' else 'percent'}
            gates.append(status)
    invalid_traces = [r['run_id'] for r in records if r['manifest']['causal_trace_enabled'] and
                     (r['summary'].get('trace_valid') is not True or not r.get('trace_health', {}).get('trace_valid') or
                      any(r.get('trace_health', {}).get(k, 0) for k in ZERO_HEALTH))]
    status = 'E0B_FAIL' if invalid_traces or 'FAIL' in gates else (
             'E0B_INCONCLUSIVE' if 'INCONCLUSIVE' in gates else 'E0B_PROCEED')
    return {'campaign_valid': True, 'classification': status, 'comparisons': comparisons,
            'invalid_required_traces': invalid_traces, 'statistical_unit': 'BLOCK',
            'block_count': 12, 'accepted_runs': len(records), 'bootstrap': plan['bootstrap']}


def metric_summary(values):
    result = descriptive(values)
    result.pop('median_absolute_paired_delta')
    result['role'] = 'diagnostic samples, never independent block observations'
    return result


def thread_telemetry(path):
    if not path.exists():
        return {}
    header = None
    series = {}
    for line in path.read_text().splitlines():
        fields = line.lstrip('# ').split()
        if 'TGID' in fields and 'TID' in fields:
            header = fields
            continue
        if header is None or len(fields) != len(header):
            continue
        row = dict(zip(header, fields))
        tgid, tid = row['TGID'], row['TID']
        if not (tgid.isdigit() or tid.isdigit()):
            continue
        entity = 'process:' + tgid if tid == '-' else 'thread:' + tid
        for metric, raw in row.items():
            if metric in ('Time', 'UID', 'TGID', 'TID', 'CPU', 'Command'):
                continue
            try:
                value = float(raw)
            except ValueError:
                continue
            if math.isfinite(value):
                series.setdefault(entity + '|' + metric, []).append(value)
    return {k: metric_summary(v) for k,v in series.items()}


def load_run(record, plan):
    directory = Path(record['run_directory']); verify_sums(directory)
    manifest = read_json(directory / 'manifest.json'); summary = read_json(directory / 'summary.json')
    for key, source in (('dataset_path', 'dataset'), ('query_path', 'query'), ('ground_truth_path', 'ground_truth'),
                        ('index_path', 'index_prefix'), ('input_package_manifest_path', 'input_manifest'),
                        ('index_package_manifest_path', 'index_manifest')):
        if manifest[key] != plan['paths'][source]:
            raise ValueError('Input/index path-role mismatch')
    series, presence = {}, {}
    with (directory / 'system_metrics.csv').open() as stream:
        for row in csv.DictReader(stream):
            if row['run_id'] != record['run_id']:
                raise ValueError('Telemetry run identity mismatch')
            key = '|'.join((row['collector'], row['entity'], row['metric']))
            series.setdefault(key, []).append(float(row['value']))
    for name in COLLECTORS:
        path = directory / 'telemetry' / f'{name}.log'
        presence[name] = path.is_file() and path.stat().st_size > 0 and any(k.startswith(name+'|') for k in series)
    result = {**record, 'manifest': manifest, 'summary': summary, 'telemetry_presence': presence,
              'telemetry': {k: metric_summary(v) for k, v in series.items()}}
    if manifest['causal_trace_enabled']:
        result['trace_health'] = read_json(directory / 'trace_health.json')
    folder = Path(record['execution_directory'])
    command = (folder / 'command.sh').read_text().splitlines()
    for key, value in plan['environment'].items():
        required = f'export {key}={shlex.quote(value)}' if value is not None else f'unset {key}'
        if required not in command:
            raise ValueError('Recorded full environment mismatch')
    result['host_before'] = read_json(folder / 'host_before.json')
    result['host_after'] = read_json(folder / 'host_after.json')
    result['runtime_snapshots'] = [read_json(p) for p in sorted(folder.glob('runtime_[0-9].json'))]
    thread_log = folder / 'pidstat_threads.log'
    result['pidstat_threads_raw'] = str(thread_log) if thread_log.is_file() else None
    result['thread_telemetry'] = thread_telemetry(thread_log)
    # Do not assume a kernel snapshot can always be captured or identify every
    # non-iou task as an OpenMP worker. Raw task/affinity data remain diagnostic.
    return result


def analyze_campaign(campaign, *, issue=10, record_analyzer=analyze_records):
    if digest(campaign / 'PLAN.json') != (campaign / 'PLAN.sha256').read_text().split()[0]:
        raise ValueError('Frozen plan SHA mismatch')
    plan = read_json(campaign / 'PLAN.json')
    if plan['schema_version'] != 1 or plan['issue'] != issue:
        raise ValueError('Unsupported campaign protocol version')
    records = [load_run(r, plan) for r in read_json(campaign / 'results.json')]
    audits = {}
    for period in ('pre', 'post'):
        for kind in ('input', 'index'):
            a = read_json(campaign / f'{period}_{kind}.audit.json')
            if a['exit_code'] != 0 or a['manifest_sha256'] != plan[f'{kind}_package_sha256'] or '--full-components' not in a['argv']:
                raise ValueError('Full-content package audit failure: STOP')
            audits[f'{period}_{kind}'] = a
    if records:
        first = min(datetime.fromisoformat(r['manifest']['timestamp_start']) for r in records)
        last = max(datetime.fromisoformat(r['manifest']['timestamp_end']) for r in records)
        for kind in ('input', 'index'):
            if datetime.fromisoformat(audits[f'pre_{kind}']['timestamp_end']) > first or datetime.fromisoformat(audits[f'post_{kind}']['timestamp_start']) < last:
                raise ValueError('Package audits do not bracket accepted measurements')
        if datetime.fromisoformat(plan['frozen_at']) > first:
            raise ValueError('Plan frozen after measurement')
        if any(datetime.fromisoformat(a['manifest']['timestamp_end']) > datetime.fromisoformat(b['manifest']['timestamp_start']) for a,b in zip(records, records[1:])):
            raise ValueError('Chronological order overlap')
    pauses = read_json(campaign / 'pauses.json')
    expected_pauses = [(i, case, 5 if pos < 2 else 15) for i, order in enumerate(ORDERS, 1)
                       for pos, case in enumerate(order) if i < 12 or pos < 2]
    if [(p['after_block'], p['after_case'], p['requested_s']) for p in pauses] != expected_pauses or any(p['elapsed_s'] < p['requested_s'] for p in pauses):
        raise ValueError('Frozen pause policy violated')
    result = record_analyzer(records, plan)
    return {**result, 'campaign_id': plan['campaign_id'], 'plan_sha256': digest(campaign / 'PLAN.json'),
            'package_audits': audits, 'runs': records, 'exclusions': [],
            'source': 'Local authoritative finalized files only; no MLflow reads'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='New output directory, never overwritten')
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    try:
        result = analyze_campaign(args.campaign)
    except (ValueError, KeyError, TypeError, OSError, statistics.StatisticsError) as error:
        result = {'campaign_valid': False, 'classification': None, 'protocol_status': 'INVALID/STOP', 'error': str(error)}
    (args.output / 'analysis.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k:result.get(k) for k in ('campaign_valid','classification','campaign_id','error')},indent=2))
    return 2 if not result['campaign_valid'] else 1 if result['classification'] == 'E0B_FAIL' else 0


if __name__ == '__main__':
    sys.exit(main())
