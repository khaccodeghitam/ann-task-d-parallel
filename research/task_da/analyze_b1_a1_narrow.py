#!/usr/bin/env python3
"""Verify the narrow replication bundle and export paired latency and quality estimates."""
import argparse
import csv
import json
import math
import os
import statistics as stats
from collections import defaultdict
from pathlib import Path

from run_b1_a1_narrow import ARMS, BEAMS, GEMINI, ORDERS, RESUME, STAGE_D, STAGE_D_BEAMS, require, sha, write_json

T95 = {1: 12.7062047364, 2: 4.30265272975, 4: 2.77644510520}
LATENCIES = ('mean', 'p50', 'p95')
ON_COUNTERS = ('duplicate_distance_evaluations', 'merge_time_ns', 'barrier_wait_ns',
               'frontier_insertions', 'sync_merge_count')


def read(path):
    return json.loads(path.read_text())


def verify_bundle(root):
    seal = root / 'BUNDLE.sha256'
    seen = set()
    for line in seal.read_text().splitlines():
        digest, name = line.split('  ', 1)
        path = root / name
        require(path.resolve().is_relative_to(root.resolve()) and path not in seen, name)
        require(sha(path) == digest, f'Checksum mismatch: {path}')
        seen.add(path)
    require(seen == {path for path in root.rglob('*') if path.is_file() and path != seal},
            f'Unexpected files in bundle {root}')
    return len(seen)


def interval(values):
    values = list(values)
    n = len(values)
    if n == 0:
        return None
    mean = stats.mean(values)
    sd = stats.stdev(values) if n > 1 else None
    radius = T95[n - 1] * sd / math.sqrt(n) if sd is not None else None
    return dict(n=n, mean=mean, sd=sd, ci95=[mean - radius, mean + radius] if radius is not None else None)


def latency(rows):
    raw = sorted(row['latency_ns'] for row in rows)
    require(raw and raw[0] > 0, 'Missing or invalid query latency')

    def percentile(fraction):
        low, frac = divmod(fraction * (len(raw) - 1), 1)
        return ((1 - frac) * raw[int(low)] + frac * raw[math.ceil(low + frac)]) / 1000

    return dict(mean=stats.mean(raw) / 1000, p50=percentile(.50), p95=percentile(.95))


def measurement(path, graph, block, arm, baseline_block, root, raw_csv=None):
    summary = read(path / 'p2_eval_summary.json')
    result, = summary['runs']
    source = path / Path(result['result_file']).name
    rows = [json.loads(line) for line in source.read_text().splitlines()]
    require(len(rows) == result['queries'] == result['complete_top_k_count'], source)
    require(result['sum_latency_ns'] == sum(row['latency_ns'] for row in rows), source)
    measured = latency(rows)
    require(all(math.isclose(measured[key], result['latency_us'][key], rel_tol=1e-8) for key in LATENCIES), source)
    if raw_csv:
        raw_csv.writerows((graph, block, arm, summary['mode'], row['query_id'], row['latency_ns'],
                           json.dumps(row['ids'], separators=(',', ':')),
                           json.dumps(row['squared_l2'], separators=(',', ':')),
                           *(row.get('counters', {}).get(key) for key in ON_COUNTERS)) for row in rows)
    return dict(graph=graph, block=block, arm=arm, baseline_block=baseline_block,
                raw_jsonl=os.path.relpath(source, root), **{f'{k}_us': v for k, v in measured.items()})


def pilot_metrics(root):
    observed = []
    designs = ((GEMINI / 'pilot1_b1_isolated/off', 'pilot_b1', {'base': 'flat_base', 'b1': 'B1_only'}),
               (RESUME / 'evidence/pilot2_a1_isolated/off', 'pilot_a1',
                {'base': 'flat_base', 'a1': 'A1_only', 'combo': 'B1_A1_combo'}))
    for directory, label, names in designs:
        for block in range(1, 6):
            for arm, name in names.items():
                path = directory / f'A3_r1_p2_S16_{name}_rep{block - 1}'
                observed.append(measurement(path, 'A3_r1', block, arm, label, root))
    return observed


def pilot_quality():
    val = read(STAGE_D_BEAMS)['selected_45_cells']['A3_r1']['S16']['2']
    directory = RESUME / 'evidence/pilot2_a1_isolated'
    arm = read(directory / 'pilot2_a1_isolated_summary.json')['arms']['A3_r1_p2_S16_flat_base']
    point, se = arm['test3k_recall'], arm['test3k_se']
    return dict(val_point=val['recall_at_10'], val_lcb95=val['lcb95_q'],
                test_point=point, test_lcb95=point - 1.96 * se, delta_from_baseline=0)


def frozen_validation_parity(root):
    calibration = STAGE_D_BEAMS.parent
    with (STAGE_D / 'EVIDENCE_CHECKSUMS.csv').open() as file:
        sealed = {row['relative_path']: row['sha256'] for row in csv.DictReader(file)}
    verdicts = {}
    for graph, folder in (('A3_r2', 'A3_r2_p2_S16_ref1'), ('A3_r3', 'A3_r3_p2_S16')):
        beam = BEAMS[graph]
        current = root / 'validation' / f'{graph}_base' / f'beam_{beam}_p2_ON.jsonl'
        if not current.with_name('checkpoint.json').is_file():
            continue
        original = calibration / folder / f'beam_{beam}_p2_OFF.jsonl'
        require(sha(original) == sealed[str(original.relative_to(STAGE_D))], original)
        with original.open() as a, current.open() as b:
            keys = ('query_id', 'ids', 'squared_l2')
            verdicts[graph] = all(all(old[k] == new[k] for k in keys)
                                  for old, new in zip(map(json.loads, a), map(json.loads, b), strict=True))
    return verdicts


def pair_effect(reference, variant):
    require(len(reference) == len(variant) == 5, 'Expected five paired process runs')
    results = {}
    for metric in LATENCIES:
        key = f'{metric}_us'
        base = [row[key] for row in reference]
        arm = [row[key] for row in variant]
        differences = [a - b for a, b in zip(base, arm, strict=True)]
        delta = interval(differences)
        results[metric] = dict(baseline_us=interval(base), variant_us=interval(arm), delta_us=delta,
            paired_improvement_pct=interval(100 * (a - b) / a for a, b in zip(base, arm, strict=True)),
            paired_speedup=interval(a / b for a, b in zip(base, arm, strict=True)),
            aggregate_improvement_pct=100 * (1 - stats.mean(arm) / stats.mean(base)),
            aggregate_speedup=stats.mean(base) / stats.mean(arm),
            paired_cohen_dz=delta['mean'] / delta['sd'] if delta['sd'] else None)
    return results


def estimates(records):
    by_graph = defaultdict(lambda: defaultdict(list))
    for row in records:
        by_graph[row['graph']][(row['baseline_block'], row['arm'])].append(row)
    graph_stats = {}
    for graph, arms in by_graph.items():
        expected = {('pilot_b1', 'base'), ('pilot_b1', 'b1'), ('pilot_a1', 'base'),
                    ('pilot_a1', 'a1'), ('pilot_a1', 'combo')} if graph == 'A3_r1' else {('narrow', arm) for arm in ARMS}
        if set(arms) != expected or any(len(rows) != 5 for rows in arms.values()):
            continue
        for values in arms.values():
            values.sort(key=lambda row: row['block'])
            require([v['block'] for v in values] == list(range(1, 6)), graph)
        report = {arm: pair_effect(arms[(scope, 'base')], rows)
                  for (scope, arm), rows in arms.items() if arm != 'base'}
        scope = 'pilot_a1' if graph == 'A3_r1' else 'narrow'
        report['combo_vs_a1'] = pair_effect(arms[(scope, 'a1')], arms[(scope, 'combo')])
        if graph != 'A3_r1':
            report['combo_vs_b1'] = pair_effect(arms[(scope, 'b1')], arms[(scope, 'combo')])
            samples = zip(*(arms[(scope, arm)] for arm in ('base', 'b1', 'a1', 'combo')), strict=True)
            report['interaction_us'] = interval(combo['mean_us'] - a1['mean_us'] - b1['mean_us'] + base['mean_us']
                                                 for base, b1, a1, combo in samples)
        graph_stats[graph] = report
    return graph_stats


def outer(graphs, effects):
    if not all(graph in effects for graph in graphs):
        return None
    return {arm: {metric: {key: interval(effects[g][arm][metric][key]['mean'] for g in graphs)
                          for key in ('paired_improvement_pct', 'paired_speedup', 'delta_us')}
                  for metric in LATENCIES} for arm in ('b1', 'a1', 'combo')}


def host_stats(root):
    phase_totals = defaultdict(lambda: dict(samples=0, min_tctl=None, max_tctl=None,
                                           min_available=None, all_ac_online=True))
    process_peak = {}
    swap_pages = {'pswpin': 0, 'pswpout': 0}
    freq = {0: [], 2: []}
    for path in sorted(root.rglob('host.jsonl')):
        prev = None
        phase = path.relative_to(root).parts[0]
        for line in path.read_text().splitlines():
            sample = json.loads(line)
            values = [s['value_C'] for s in sample['sensors'].values() if s['name'] == 'k10temp' and s['label'] == 'Tctl']
            aggregate = phase_totals[phase]
            aggregate['samples'] += 1
            if len(values) == 1:
                tctl = values[0]
                aggregate['min_tctl'] = min(tctl, aggregate['min_tctl'] or tctl)
                aggregate['max_tctl'] = max(tctl, aggregate['max_tctl'] or tctl)
            memory = sample['mem_available']
            aggregate['min_available'] = min(memory, aggregate['min_available'] or memory)
            aggregate['all_ac_online'] &= bool(sample['power']) and set(sample['power'].values()) == {'1'}
            for cpu, values in freq.items():
                key = f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_cur_freq'
                value = sample['cpu'].get(key)
                if value is not None:
                    values.append(int(value))
            if prev:
                for key in swap_pages:
                    swap_pages[key] += max(0, sample['swap_pages'][key] - prev['swap_pages'][key])
                elapsed = sample['monotonic_s'] - prev['monotonic_s']
                old = {(p['pid'], p['start_ticks']): p['user_ticks'] + p['system_ticks'] for p in prev['competing_processes']}
                if elapsed >= .5:
                    for proc in sample['competing_processes']:
                        identity = (proc['pid'], proc['start_ticks'])
                        if identity in old:
                            cpu_pct = 100 * (proc['user_ticks'] + proc['system_ticks'] - old[identity]) / (
                                elapsed * os.sysconf('SC_CLK_TCK'))
                            name = proc['name']
                            process_peak[name] = max(process_peak.get(name, 0), cpu_pct)
            prev = sample
    return dict(samples=sum(row['samples'] for row in phase_totals.values()), by_phase=dict(phase_totals),
                cpufreq_sample_min_max_khz={cpu: [min(vals), max(vals)] if vals else None for cpu, vals in freq.items()},
                swap_pages_in_within_run_intervals=swap_pages,
                competing_processes_peak_cpu_pct=sorted(process_peak.items(), key=lambda pair: -pair[1])[:12])


def main(root, out):
    require(not out.resolve().is_relative_to(root.resolve()), 'Export outside the sealed raw bundle')
    count = verify_bundle(root)
    checkpoint = read(root / 'checkpoint.json')
    measurements = pilot_metrics(out)
    out.mkdir()
    with (out / 'raw_query_latency.csv').open('x') as file:
        raw = csv.writer(file)
        raw.writerow(('graph', 'block', 'arm', 'mode', 'query_id', 'latency_ns', 'ids', 'squared_l2', *ON_COUNTERS))
        for graph in BEAMS:
            for arm in ARMS:
                path = root / 'test_on' / f'{graph}_{arm}'
                if (path / 'checkpoint.json').exists():
                    measurement(path, graph, 'test_on', arm, 'narrow', out, raw)
            for block, order in enumerate(ORDERS, 1):
                schedule = order.split() if graph == 'A3_r2' else order.split()[::-1]
                for position, arm in enumerate(schedule, 1):
                    path = root / 'off' / f'block{block}_{graph}' / f'{position}_{arm}'
                    if (path / 'checkpoint.json').exists():
                        measurements.append(measurement(path, graph, block, arm, 'narrow', out, raw))
    if checkpoint['status'] == 'COMPLETE':
        require(sum(m['graph'] in BEAMS for m in measurements) == 40, 'Missing replication OFF process results')
    with (out / 'process_latency.csv').open('x') as file:
        writer = csv.DictWriter(file, fieldnames=measurements[0].keys())
        writer.writeheader()
        writer.writerows(measurements)
    quality = {phase: read(root / f'{phase}_quality.json') for phase in ('validation', 'test_on')
               if (root / f'{phase}_quality.json').exists()}
    if quality:
        with (out / 'quality.csv').open('x') as file:
            columns = ('phase', 'graph', 'arm', 'beam', 'point', 'se', 'lcb95', 'delta_from_baseline', 'matched_span', 'pass')
            writer = csv.DictWriter(file, fieldnames=columns, extrasaction='ignore')
            writer.writeheader()
            for phase, receipt in quality.items():
                writer.writerows({'phase': phase, **row} for row in receipt['rows'])
    by_graph = estimates(measurements)
    primary = outer(tuple(BEAMS), by_graph)
    decision = 'HOLD'
    if primary and checkpoint['status'] == 'COMPLETE':
        estimates_pct = [by_graph[g]['combo']['mean']['paired_improvement_pct'] for g in BEAMS]
        bounds = primary['combo']['mean']['paired_improvement_pct']['ci95']
        if all(x['mean'] >= 5 and x['ci95'][0] > 0 for x in estimates_pct) and bounds[0] > 0:
            decision = 'GO_BASELINE_OPTIMIZATION'
        elif all(x['ci95'][1] < 5 for x in estimates_pct):
            decision = 'PIVOT'
    write_json(out / 'analysis.json', dict(decision=decision, checkpoint=checkpoint, verified_raw_files=count,
        raw_bundle_sha256=sha(root / 'BUNDLE.sha256'), frozen=read(root / 'frozen.json'), quality=quality,
        pilot_quality=pilot_quality(), frozen_validation_exact_top10=frozen_validation_parity(root),
        by_graph=by_graph, outer_r2_r3=primary, outer_r1_r2_r3_exploratory=outer(('A3_r1', *BEAMS), by_graph),
        host=host_stats(root)))
    with (out / 'CHECKSUMS.sha256').open('x') as manifest:
        for path in sorted(out.iterdir()):
            if path.name != 'CHECKSUMS.sha256':
                manifest.write(f'{sha(path)}  {path.name}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw', type=Path)
    parser.add_argument('export', type=Path)
    args = parser.parse_args()
    main(args.raw.resolve(), args.export.resolve())
