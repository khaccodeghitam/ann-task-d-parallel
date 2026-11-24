"""Read-only 900-second host qualification tool for G2 v2 design-3.

Never runs ANN binaries, never reads query/GT/graph artifacts, never modifies thresholds.
Saves full raw telemetry JSONL, schema-validated summary JSON, and BUNDLE.sha256.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time

import numpy as np

from .g2_v2_design3_contract import (
    CPUS, FREEZE, PROTOCOL, QUALIFICATION_DURATION_S, REVISION, ROOT, SCHEMA,
    load_freeze, require, require_default_loader, sha, validate_schema, write_new,
)
from .g2_v2_design3_guard import (
    PHASE_POLICIES, host_contract, host_snapshot_v3, make_guard, window_accounting,
)


def run_qualification(output_dir, *, duration_s=QUALIFICATION_DURATION_S,
                      snapshot_fn=host_snapshot_v3, sleep_fn=time.sleep,
                      host_fn=host_contract, freeze_check=True):
    """Execute read-only host qualification under frozen design-3 OFF noise/safety rules."""
    require(duration_s == QUALIFICATION_DURATION_S,
            f'official qualification must run exactly {QUALIFICATION_DURATION_S}s')
    if freeze_check:
        load_freeze(environment=True)
    require_default_loader(os.environ)
    host = host_fn()

    out = Path(output_dir).resolve()
    require(not out.exists(), f'qualification output already exists (never overwrite): {out}')
    out.mkdir(parents=True, exist_ok=False)

    tel_name = 'qualification_telemetry.jsonl'
    tel_path = out / tel_name
    pol = PHASE_POLICIES['qualification']

    started_utc = datetime.now(timezone.utc).isoformat()
    reason_counts = Counter()
    failure_events = []
    w10_pass = w10_fail = 0
    w15_pass = w15_fail = 0
    hard_guard_failures = 0

    tctls = []
    mem_avail_min = None
    free_disk_min = None
    swap_max = 0
    obs_cpu_list = []
    coll_wall_list = []
    w10_workers_vals = []
    w10_ccx0_vals = []
    w10_single_vals = []
    w15_all_vals = []

    with tel_path.open('x') as log:
        first = snapshot_fn(out)
        log.write(json.dumps(first) + '\n')
        log.flush()
        guard = make_guard(first, phase='qualification')
        init_reasons = guard.check(first)
        if init_reasons:
            hard_guard_failures += 1
            for r in init_reasons:
                reason_counts[r] += 1
            failure_events.append(dict(step=0, monotonic_s=first['monotonic_s'], reasons=init_reasons))

        start_mono = first['v3_cpu']['monotonic_s']
        last_snap = first
        step = 0
        while True:
            t_cur = last_snap['v3_cpu']['monotonic_s']
            if t_cur - start_mono >= duration_s:
                break
            sleep_fn(1.0)
            step += 1
            s = snapshot_fn(out)
            log.write(json.dumps(s) + '\n')
            log.flush()
            last_snap = s

            reasons = guard.check(s)
            ev = guard.noise.evaluations[-1]

            temps = [v['value_C'] for v in s['sensors'].values()
                     if v['name'] == 'k10temp' and v['label'] == 'Tctl']
            if len(temps) == 1:
                tctls.append(float(temps[0]))
            mem_avail_min = s['mem_available'] if mem_avail_min is None else min(mem_avail_min, s['mem_available'])
            free_disk_min = s['free_disk'] if free_disk_min is None else min(free_disk_min, s['free_disk'])
            swap_max = max(swap_max, int(s['swap_used']))
            if 'observer_cpu_s' in s:
                obs_cpu_list.append(float(s['observer_cpu_s']))
            if 'collection_wall_s' in s:
                coll_wall_list.append(float(s['collection_wall_s']))

            if 'window_10s' in ev:
                w10 = ev['window_10s']
                w10_workers_vals.append(w10['foreign_workers_fraction'])
                w10_ccx0_vals.append(w10['foreign_ccx0_fraction'])
                w10_single_vals.append(w10['max_single_foreign_rate'])
                bad10 = [r for r in reasons if any(k in r for k in ('worker-cores', 'CCX0', 'single foreign'))]
                if bad10:
                    w10_fail += 1
                else:
                    w10_pass += 1

            if 'window_15s' in ev:
                w15 = ev['window_15s']
                w15_all_vals.append(w15['foreign_all_fraction'])
                bad15 = [r for r in reasons if 'host [0..11]' in r]
                if bad15:
                    w15_fail += 1
                else:
                    w15_pass += 1

            if reasons:
                non_win = [r for r in reasons if not any(k in r for k in (
                    'worker-cores', 'CCX0', 'single foreign', 'host [0..11]'
                ))]
                if non_win:
                    hard_guard_failures += 1
                for r in reasons:
                    reason_counts[r] += 1
                if len(failure_events) < 200:
                    failure_events.append(dict(
                        step=step,
                        monotonic_s=s['v3_cpu']['monotonic_s'],
                        tctl_C=temps[0] if len(temps) == 1 else None,
                        reasons=reasons,
                        top_competing=ev.get('window_10s', ev.get('window_15s', {})).get('competing_processes', [])[:3],
                    ))

    total = window_accounting(first['v3_cpu'], last_snap['v3_cpu'])
    observed_wall_s = total['wall_s']
    monitor_cpu_s = total['monitor_cpu_s']
    monitor_p2_frac = monitor_cpu_s / (observed_wall_s * len(CPUS))
    monitor_1core_pct = 100.0 * monitor_cpu_s / observed_wall_s

    passed = bool(
        w10_pass > 0 and w15_pass > 0
        and w10_fail == 0 and w15_fail == 0
        and hard_guard_failures == 0
        and observed_wall_s >= duration_s - 1.0
    )

    def _stats(vals):
        if not vals:
            return dict(mean=0.0, p50=0.0, p95=0.0, max=0.0)
        arr = np.asarray(vals, dtype=float)
        return dict(
            mean=float(arr.mean()),
            p50=float(np.quantile(arr, 0.50, method='linear')),
            p95=float(np.quantile(arr, 0.95, method='linear')),
            max=float(arr.max()),
        )

    result = dict(
        schema=SCHEMA,
        protocol=PROTOCOL,
        revision=REVISION,
        verdict='QUALIFICATION_PASS' if passed else 'QUALIFICATION_HOLD',
        qualification_pass=passed,
        started_utc=started_utc,
        finished_utc=datetime.now(timezone.utc).isoformat(),
        freeze_sha256=sha(FREEZE) if FREEZE.exists() else '0' * 64,
        target_duration_s=duration_s,
        observed_wall_s=float(observed_wall_s),
        samples=step + 1,
        passed_windows_10s=w10_pass,
        failed_windows_10s=w10_fail,
        passed_windows_15s=w15_pass,
        failed_windows_15s=w15_fail,
        hard_guard_failures=hard_guard_failures,
        policy=pol,
        host=host,
        thermal_tctl_C=dict(
            min=float(min(tctls)) if tctls else None,
            max=float(max(tctls)) if tctls else None,
        ),
        resources=dict(
            min_mem_available_bytes=int(mem_avail_min) if mem_avail_min is not None else int(first['mem_available']),
            min_free_disk_bytes=int(free_disk_min) if free_disk_min is not None else int(first['free_disk']),
            max_swap_used_bytes=int(swap_max),
            ac_power=last_snap['power'],
        ),
        monitor_overhead=dict(
            total_monitor_cpu_s=float(monitor_cpu_s),
            monitor_1core_percent=float(monitor_1core_pct),
            monitor_p2_capacity_fraction=float(monitor_p2_frac),
            observer_cpu_s=_stats(obs_cpu_list),
            collection_wall_s=_stats(coll_wall_list),
        ),
        foreign_summary=dict(
            net_total_workers_fraction=float(total['foreign_workers_fraction']),
            net_total_ccx0_fraction=float(total['foreign_ccx0_fraction']),
            net_total_all_fraction=float(total['foreign_all_fraction']),
            rolling_10s_workers=_stats(w10_workers_vals),
            rolling_10s_ccx0=_stats(w10_ccx0_vals),
            rolling_10s_single_rate=_stats(w10_single_vals),
            rolling_15s_all=_stats(w15_all_vals),
        ),
        failure_reason_counts=dict(sorted(reason_counts.items())),
        failure_events_sample=failure_events[:50],
        telemetry_file=tel_name,
        telemetry_sha256=sha(tel_path),
        evidence_label='EXPLORATORY_HOST_SPECIFIC',
    )
    validate_schema(result, 'qualification')
    res_path = out / 'qualification_result.json'
    write_new(res_path, result)

    bundle_lines = [
        f'{sha(res_path)}  qualification_result.json\n',
        f'{sha(tel_path)}  {tel_name}\n',
    ]
    (out / 'BUNDLE.sha256').write_text(''.join(bundle_lines))
    return result, out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=None,
                        help='New output directory for qualification telemetry and receipts')
    args = parser.parse_args()
    if args.output is None:
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        output = ROOT.parent / 'artifact-evidence' / f'axd-g2-v2-design3-qualification-{stamp}'
    else:
        output = args.output
    result, out = run_qualification(output)
    summary = {
        'verdict': result['verdict'],
        'qualification_pass': result['qualification_pass'],
        'observed_wall_s': round(result['observed_wall_s'], 2),
        'windows_10s': f"{result['passed_windows_10s']} PASS / {result['failed_windows_10s']} FAIL",
        'windows_15s': f"{result['passed_windows_15s']} PASS / {result['failed_windows_15s']} FAIL",
        'hard_guard_failures': result['hard_guard_failures'],
        'monitor_1core_pct': round(result['monitor_overhead']['monitor_1core_percent'], 3),
        'monitor_p2_frac': round(result['monitor_overhead']['monitor_p2_capacity_fraction'], 5),
        'tctl_C': result['thermal_tctl_C'],
        'max_workers_10s': round(result['foreign_summary']['rolling_10s_workers']['max'], 5),
        'max_ccx0_10s': round(result['foreign_summary']['rolling_10s_ccx0']['max'], 5),
        'max_all_15s': round(result['foreign_summary']['rolling_15s_all']['max'], 5),
        'max_single_10s': round(result['foreign_summary']['rolling_10s_single_rate']['max'], 5),
        'failure_reason_counts': result['failure_reason_counts'],
        'output_dir': str(out),
        'qualification_result_sha256': sha(out / 'qualification_result.json'),
        'bundle_sha256': sha(out / 'BUNDLE.sha256'),
    }
    print(json.dumps(summary, indent=2))
    raise SystemExit(0 if result['qualification_pass'] else 2)


if __name__ == '__main__':
    main()
