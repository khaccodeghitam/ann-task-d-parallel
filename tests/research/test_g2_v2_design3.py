"""Dataset-free scientific and implementation audit suite for G2 v2 design-3.

Never invokes ANN binaries, profilers, test panels, or live host mutations.
Verifies all 6 design-3 amendments and exact estimand identity with design-2.
"""
import copy
import json
import math
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from research.task_da import g2_v2_analyzer as a_d2
from research.task_da import g2_v2_design3_analyzer as a3
from research.task_da import g2_v2_design3_contract as c3
from research.task_da import g2_v2_design3_guard as g3
from research.task_da import g2_v2_design3_qualify as q3
from research.task_da import g2_v2_design3_runner as r3


def make_cap(t, *, own=0, monitor=0, watchdog=0, watchdog_pid=None, owned_pid=100,
             per_cpu=None, extra_procs=None, named_jobs=None,
             own_start=4, mon_start=7, wd_start=9, own_cpu=0, mon_cpu=8, wd_cpu=10):
    """Build a synthetic v3_cpu capture with exact per-CPU conservation."""
    if per_cpu is None:
        pc = {str(i): 0 for i in range(12)}
        pc[str(own_cpu)] += own
        pc[str(mon_cpu)] += monitor
        if watchdog_pid is not None:
            pc[str(wd_cpu)] += watchdog
    else:
        pc = {str(i): int(per_cpu.get(str(i), per_cpu.get(i, 0))) for i in range(12)}
    host_busy = sum(pc.values())
    procs = {
        '200': ['python', monitor, mon_start, mon_cpu],
    }
    if owned_pid is not None:
        procs[str(owned_pid)] = ['task_da_p2_eval', own, own_start, own_cpu]
    if watchdog_pid is not None:
        procs[str(watchdog_pid)] = ['python', watchdog, wd_start, wd_cpu]
    if extra_procs:
        for pid, entry in extra_procs.items():
            procs[str(pid)] = list(entry)
    return dict(
        monotonic_s=float(t),
        hz=100,
        host_busy_ticks=host_busy,
        per_cpu_busy_ticks=pc,
        owned=dict(comm='task_da_p2_eval' if owned_pid is not None else '',
                   ticks=own, start=own_start if owned_pid is not None else 0,
                   processor=own_cpu if owned_pid is not None else -1),
        monitor=dict(comm='python', ticks=monitor, start=mon_start, processor=mon_cpu),
        watchdog=dict(comm='python' if watchdog_pid is not None else '',
                      ticks=watchdog if watchdog_pid is not None else 0,
                      start=wd_start if watchdog_pid is not None else 0,
                      processor=wd_cpu if watchdog_pid is not None else -1),
        owned_pid=owned_pid,
        monitor_pid=200,
        watchdog_pid=watchdog_pid,
        named_jobs=list(named_jobs or []),
        processes=procs,
    )


def make_snap(cap, *, temp=60.0, mem=8 * 2**30, disk=40 * 2**30, swap=0, ac='1', ann=None):
    return dict(
        timestamp='2026-11-24T00:00:00+00:00',
        monotonic_s=cap['monotonic_s'],
        mem_available=mem,
        swap_used=swap,
        free_disk=disk,
        sensors={'t': dict(name='k10temp', label='Tctl', value_C=temp, critical_mC='95000')},
        power={'AC': ac},
        rapl={},
        cpu={},
        tasks=[],
        ann=list(ann or []),
        sqpoll=[],
        load='0.10 0.10 0.10 1/200 1',
        collection_wall_s=0.015,
        observer_cpu_s=0.010,
        v3_cpu=cap,
    )


def fixture_d3(*, foreign_fn=None):
    rows = []
    latency = np.empty((12, 6, 2, c3.N))
    for b in range(12):
        for j, graph in enumerate(c3.GRAPHS):
            for k, p in enumerate(('base', 'opt')):
                value = (3000 + 10 * b + 5 * j) * (1.0 if p == 'base' else 0.94)
                latency[b, j, k] = value
                fw, fc, fa = (0.001, 0.002, 0.005) if foreign_fn is None else foreign_fn(b, j, p)
                rows.append(dict(
                    block=b, graph=graph, policy=p, mode='OFF', valid=True, beam=432,
                    observed_cpus=[0, 2], query_count=c3.N, mean_us=value, p50_us=value,
                    p95_us=value, p99_us=value, qps_wall=1e6 / value, rss_kib=850000,
                    cpu_seconds=10.0, wall_seconds=10.0, cpu_percent=100.0, cpu_capacity_percent=50.0,
                    monitor_cpu_seconds=0.1, watchdog_cpu_seconds=0.01,
                    foreign_workers_fraction=fw, foreign_ccx0_fraction=fc, foreign_all_fraction=fa,
                    max_rolling_foreign_workers_fraction=fw,
                    max_rolling_foreign_ccx0_fraction=fc,
                    max_rolling_foreign_all_fraction=fa,
                ))
    quality = dict(A_pass=True, B_pass=True, B_authorized=True, parity=True, duplicate_reduction=True)
    return rows, latency, quality


class Design3GuardAndAccountingTests(unittest.TestCase):
    def test_parse_stat_extracts_ticks_start_and_processor_with_spaces_parens(self):
        fields = ['S'] + ['0'] * 40
        fields[11] = '101'
        fields[12] = '23'
        fields[19] = '4455'
        fields[36] = '9'
        parsed = g3.parse_stat('999 (kworker/u50:1 (odd)) ' + ' '.join(fields))
        self.assertEqual(parsed, dict(comm='kworker/u50:1 (odd)', ticks=124, start=4455, processor=9))
        with self.assertRaises(ValueError):
            g3.parse_stat('999 (short) S 0 0 0')

    def test_parse_proc_stat_conservation_and_malformed_rejection(self):
        lines = []
        total = [0] * 8
        for c in range(12):
            row = [100 + c, 1, 20 + c, 5000, 10, 2, 3, 0]
            for i in range(8):
                total[i] += row[i]
            lines.append(f'cpu{c} ' + ' '.join(map(str, row)))
        good = 'cpu  ' + ' '.join(map(str, total)) + '\n' + '\n'.join(lines) + '\n'
        agg, per_cpu = g3.parse_proc_stat(good)
        self.assertEqual(agg, sum(per_cpu.values()))
        # Valid Linux nsec_to_clock_t floor-truncation slack (e.g. +22 <= 6*12=72) MUST PASS
        total_slack = list(total)
        total_slack[0] += 22
        good_slack = 'cpu  ' + ' '.join(map(str, total_slack)) + '\n' + '\n'.join(lines) + '\n'
        agg_s, per_s = g3.parse_proc_stat(good_slack)
        self.assertEqual(agg_s - sum(per_s.values()), 22)
        # Violate upper conservation (> 6*12=72) MUST FAIL
        total_hi = list(total)
        total_hi[0] += 73
        bad_hi = 'cpu  ' + ' '.join(map(str, total_hi)) + '\n' + '\n'.join(lines) + '\n'
        with self.assertRaises(ValueError):
            g3.parse_proc_stat(bad_hi)
        # Violate lower conservation (agg < sum) MUST FAIL
        total_lo = list(total)
        total_lo[0] -= 1
        bad_lo = 'cpu  ' + ' '.join(map(str, total_lo)) + '\n' + '\n'.join(lines) + '\n'
        with self.assertRaises(ValueError):
            g3.parse_proc_stat(bad_lo)
        # Missing cpu11
        missing = 'cpu  ' + ' '.join(map(str, total)) + '\n' + '\n'.join(lines[:-1]) + '\n'
        with self.assertRaises(ValueError):
            g3.parse_proc_stat(missing)

    def test_watchdog_and_monitor_excluded_zero_false_abort(self):
        # Monitor uses 4 ticks/s (2% p2) on CPU 8, watchdog uses 2 ticks/s (1% p2) on CPU 10,
        # owned uses 190 ticks/s on CPU 0; true foreign = 0 -> MUST PASS all windows!
        c = g3.ContentionV3(phase='off')
        for t in range(20):
            cap = make_cap(t, own=190 * t, monitor=4 * t, watchdog=2 * t, watchdog_pid=201)
            reasons = c.observe(cap)
            self.assertEqual(reasons, [])
        self.assertTrue(c.ready)
        ev = c.evaluations[-1]
        self.assertEqual(ev['window_10s']['foreign_workers_fraction'], 0.0)
        self.assertEqual(ev['window_15s']['foreign_all_fraction'], 0.0)
        self.assertAlmostEqual(ev['window_15s']['watchdog_cpu_s'], 0.30, places=6)
        self.assertAlmostEqual(ev['window_15s']['monitor_cpu_s'], 0.60, places=6)

    def test_net_window_subtraction_eliminates_quantization_rectification_false_abort(self):
        # Simulate +/-2 tick phase jitter every second between /proc/stat and owned/monitor ticks
        # with ZERO true foreign CPU over 20s: design-2 per-1s clamp would inflate +0.01/step!
        # Design-3 net subtraction over 10s/15s windows MUST have zero false aborts!
        jitter = [0, 2, -2, 2, -2, 2, -2, 2, -2, 2, -2, 2, -2, 2, -2, 2, -2, 2, -2, 0]
        c = g3.ContentionV3(phase='off')
        for t, j in enumerate(jitter):
            pc = {str(i): 0 for i in range(12)}
            pc['0'] = max(0, 190 * t + j)
            pc['8'] = 4 * t
            cap = make_cap(t, own=190 * t, monitor=4 * t, per_cpu=pc)
            reasons = c.observe(cap)
            self.assertEqual(reasons, [], f'unexpected false abort at t={t}: {reasons}')
        # Endpoint net difference at t=19 minus t=4 is at most 2 ticks / 30s = 0.00067 << 0.025
        self.assertLessEqual(c.evaluations[-1]['window_15s']['foreign_all_fraction'], 0.001)

    def test_topology_ccx1_os_pulse_allowed_while_worker_cores_and_ccx0_strictly_guarded(self):
        # Case A: 0.30s OS pulse on CPU 9 (CCX1) during 15s -> 0.30 / 30 = 0.010 <= 0.025 (PASS!)
        # and workers [0..3] = 0.0, ccx0 [0..5] = 0.0, single rate = 0.30/10 = 0.03 <= 0.10 (PASS!)
        c_ok = g3.ContentionV3(phase='off')
        for t in range(18):
            pulse = 30 if t >= 6 else 0  # 300ms burst at t=6 on CPU 9 (CCX1)
            pc = {str(i): 0 for i in range(12)}
            pc['0'] = 190 * t
            pc['8'] = 3 * t
            pc['9'] = pulse
            extra = {'500': ['sa1', pulse, 100, 9]} if pulse else {}
            reasons = c_ok.observe(make_cap(t, own=190 * t, monitor=3 * t, per_cpu=pc, extra_procs=extra))
            self.assertEqual(reasons, [], f'CCX1 OS pulse falsely rejected at t={t}: {reasons}')

        # Case B: 0.25s foreign load on CPU 1 (SMT sibling of worker CPU 0!) over 10s
        # -> 0.25 / 20 = 0.0125 > 0.010 worker-cores limit -> MUST FAIL!
        c_smt = g3.ContentionV3(phase='off')
        saw_worker_fail = False
        for t in range(12):
            f_ticks = int(2.5 * t)  # 0.025 CPU-s/s on CPU 1
            pc = {str(i): 0 for i in range(12)}
            pc['0'] = 190 * t
            pc['1'] = f_ticks
            pc['8'] = 3 * t
            extra = {'501': ['sneaky', f_ticks, 100, 1]}
            reasons = c_smt.observe(make_cap(t, own=190 * t, monitor=3 * t, per_cpu=pc, extra_procs=extra))
            if any('worker-cores [0..3]' in r for r in reasons):
                saw_worker_fail = True
        self.assertTrue(saw_worker_fail)

        # Case C: 0.45s foreign load on CPU 4 (CCX0 shared L3) over 10s
        # -> 0.45 / 20 = 0.0225 > 0.020 CCX0 limit -> MUST FAIL!
        c_ccx0 = g3.ContentionV3(phase='off')
        saw_ccx0_fail = False
        for t in range(12):
            f_ticks = int(4.5 * t)  # 0.045 CPU-s/s on CPU 4
            pc = {str(i): 0 for i in range(12)}
            pc['0'] = 190 * t
            pc['4'] = f_ticks
            pc['8'] = 3 * t
            extra = {'502': ['l3hog', f_ticks, 100, 4]}
            reasons = c_ccx0.observe(make_cap(t, own=190 * t, monitor=3 * t, per_cpu=pc, extra_procs=extra))
            if any('CCX0 [0..5]' in r for r in reasons):
                saw_ccx0_fail = True
        self.assertTrue(saw_ccx0_fail)

        # Case D: Untracked kernel IRQ storm on CPU 0 (no foreign PID) -> caught by conservation lb!
        c_irq = g3.ContentionV3(phase='off')
        saw_irq_fail = False
        for t in range(12):
            irq_ticks = 6 * t  # 0.06 CPU-s/s hard IRQ on CPU 0 (exceeds monitor 0.02 + 0.02 threshold)
            pc = {str(i): 0 for i in range(12)}
            pc['0'] = 190 * t + irq_ticks
            pc['8'] = 2 * t
            reasons = c_irq.observe(make_cap(t, own=190 * t, monitor=2 * t, per_cpu=pc))
            if any('worker-cores [0..3]' in r for r in reasons):
                saw_irq_fail = True
        self.assertTrue(saw_irq_fail)

    def test_single_process_cap_and_known_cpu_jobs_instant_rejection(self):
        # Instant KNOWN_CPU_JOBS rejection at t=0 without waiting 10s
        cap = make_cap(0, extra_procs={'900': ['stress-ng', 1, 10, 9]},
                       named_jobs=[{'pid': 900, 'comm': 'stress-ng', 'processor': 9}])
        self.assertTrue(any('named CPU/ANN job' in r for r in g3.ContentionV3(phase='off').observe(cap)))
        self.assertTrue(any('named CPU/ANN job' in r for r in g3.ContentionV3(phase='quality').observe(cap)))

        # Unknown sustained single process at 12% of 1 core on CCX1 -> caught by Tier 3 (>10%) in OFF
        c_off = g3.ContentionV3(phase='off')
        saw_single = False
        for t in range(12):
            f_ticks = 12 * t
            pc = {str(i): 0 for i in range(12)}
            pc['0'] = 190 * t
            pc['9'] = f_ticks
            extra = {'901': ['mystery_job', f_ticks, 10, 9]}
            reasons = c_off.observe(make_cap(t, own=190 * t, per_cpu=pc, extra_procs=extra))
            if any('single foreign process mystery_job' in r for r in reasons):
                saw_single = True
        self.assertTrue(saw_single)

    def test_quality_phase_allows_small_ccx1_os_load_but_blocks_overload_and_thermal(self):
        # 4% p2 capacity (0.08 CPU-s/s) on CCX1: FAILS OFF (>2.5%) but PASSES QUALITY (<=10%)
        c_off = g3.ContentionV3(phase='off')
        c_qual = g3.ContentionV3(phase='quality')
        off_failed = False
        for t in range(18):
            f_ticks = 8 * t
            pc = {str(i): 0 for i in range(12)}
            pc['0'] = 190 * t
            pc['9'] = f_ticks
            extra = {'600': ['apt-check', f_ticks, 10, 9]}
            cap = make_cap(t, own=190 * t, per_cpu=pc, extra_procs=extra)
            if c_off.observe(cap):
                off_failed = True
            self.assertEqual(c_qual.observe(cap), [])
        self.assertTrue(off_failed)

        # Heavy overload (15% p2 = 0.30 CPU-s/s) MUST STILL FAIL QUALITY!
        c_qual_bad = g3.ContentionV3(phase='quality')
        qual_failed = False
        for t in range(18):
            f_ticks = 30 * t
            pc = {str(i): 0 for i in range(12)}
            pc['0'] = 190 * t
            pc['9'] = f_ticks
            extra = {'601': ['heavy_compile', f_ticks, 10, 9]}
            if c_qual_bad.observe(make_cap(t, own=190 * t, per_cpu=pc, extra_procs=extra)):
                qual_failed = True
        self.assertTrue(qual_failed)

        # Hardware thermal/RAM/disk/AC/swap limits survive unchanged in both phases
        base_s = make_snap(make_cap(0))
        for phase in ('quality', 'off'):
            for field, val, needle in [
                ('mem_available', 2**30, 'MemAvailable'),
                ('free_disk', 20 * 2**30, 'Disk free'),
                ('power', {'AC': '0'}, 'AC'),
            ]:
                gd = g3.make_guard(copy.deepcopy(base_s), phase=phase)
                bad = copy.deepcopy(base_s)
                bad[field] = val
                self.assertTrue(any(needle in r for r in gd.check(bad)))
            gd_t = g3.make_guard(copy.deepcopy(base_s), phase=phase)
            hot = make_snap(make_cap(1), temp=95.0)
            self.assertTrue(any('Tctl' in r for r in gd_t.check(hot, owned_pid=100)))

    def test_pid_reuse_gap_and_counter_regression_fail_closed(self):
        c0 = make_cap(0, own=10, monitor=5, watchdog=2, watchdog_pid=201)
        # Gap > 2s
        with self.assertRaises(ValueError):
            g3.validate_step(c0, make_cap(2.5, own=20, monitor=6, watchdog=3, watchdog_pid=201))
        # Owned PID start_ticks changed (PID reuse)
        with self.assertRaises(ValueError):
            g3.validate_step(c0, make_cap(1.0, own=20, monitor=6, watchdog=3, watchdog_pid=201, own_start=999))
        # Watchdog PID start_ticks changed
        with self.assertRaises(ValueError):
            g3.validate_step(c0, make_cap(1.0, own=20, monitor=6, watchdog=3, watchdog_pid=201, wd_start=999))
        # Counter regression on per-CPU
        pc_bad = {str(i): 0 for i in range(12)}
        pc_bad['0'] = 5
        with self.assertRaises(ValueError):
            g3.validate_step(c0, make_cap(1.0, own=10, monitor=5, watchdog=2, watchdog_pid=201, per_cpu=pc_bad))

    def test_topology_hierarchy_conservation_always_holds(self):
        rng = random.Random(20261124)
        for _ in range(50):
            pc0 = {str(i): 1000 for i in range(12)}
            pc1 = {str(i): 1000 + rng.randint(0, 50) for i in range(12)}
            own = rng.randint(0, 180)
            mon = rng.randint(0, 20)
            wd = rng.randint(0, 5)
            # Ensure aggregate >= own+mon+wd on valid samples
            pc1['0'] += own
            pc1['8'] += mon
            pc1['10'] += wd
            extra = {
                '700': ['bg1', rng.randint(0, 25), 1, rng.choice([0, 1, 2, 3])],
                '701': ['bg2', rng.randint(0, 25), 1, rng.choice([4, 5])],
                '702': ['bg3', rng.randint(0, 25), 1, rng.choice([6, 7, 8, 9, 10, 11])],
            }
            c0 = make_cap(0, own=0, monitor=0, watchdog=0, watchdog_pid=201, per_cpu=pc0)
            c1 = make_cap(10, own=own, monitor=mon, watchdog=wd, watchdog_pid=201, per_cpu=pc1, extra_procs=extra)
            acc = g3.window_accounting(c0, c1)
            self.assertGreaterEqual(acc['foreign_workers_fraction'], 0.0)
            self.assertLessEqual(acc['foreign_workers_fraction'], acc['foreign_ccx0_fraction'] + 1e-12)
            self.assertLessEqual(acc['foreign_ccx0_fraction'], acc['foreign_all_fraction'] + 1e-12)


class Design3AuthorizationAndQualificationTests(unittest.TestCase):
    def test_design2_approval_receipt_is_strictly_rejected(self):
        # Exact structure of design-2 approval receipt (both UNAPPROVED template and signed design-2 format)
        d2_signed = dict(
            schema='axd_g2_v2.2',
            protocol=c3.PROTOCOL,
            revision='design-2',
            owner='<thinhbui>',
            approved_at='2026-11-24T07:28:46+07:00',
            freeze_sha256='f' * 64,
            artifacts_sha256='a' * 64,
            output_directory='/future/quality',
            scope='QUALITY_ONLY',
            quota_s=3600,
            quiet_host_confirmed=True,
        )
        with self.assertRaisesRegex(ValueError, 'design-2|design-3'):
            c3.authorize(d2_signed, 'f' * 64, 'a' * 64, 'quality', '/future/quality',
                         qualification_digest='b' * 64)

        d2_tmpl = json.loads((c3.ROOT / 'configs/axd_g2_v2_approval.UNAPPROVED.json').read_text())
        with self.assertRaises(ValueError):
            c3.authorize(d2_tmpl, 'f' * 64, 'a' * 64, 'quality', '/future/quality',
                         qualification_digest='b' * 64)

        d3_tmpl = json.loads((c3.ROOT / 'configs/axd_g2_v2_design3_approval.UNAPPROVED.json').read_text())
        with self.assertRaises(ValueError):
            c3.authorize(d3_tmpl, 'f' * 64, 'a' * 64, 'quality', '/future/quality',
                         qualification_digest='b' * 64)

    def test_design3_approval_requires_matching_qualification_and_scope(self):
        ap = dict(
            schema=c3.SCHEMA,
            protocol=c3.PROTOCOL,
            revision=c3.REVISION,
            owner='FIXTURE_OWNER',
            approved_at='2026-11-24T09:00:00+07:00',
            freeze_sha256='f' * 64,
            artifacts_sha256='a' * 64,
            qualification_sha256='b' * 64,
            output_directory='/future/quality',
            scope='QUALITY_ONLY',
            quota_s=3600,
            quiet_host_confirmed=True,
        )
        self.assertEqual(
            c3.authorize(ap, 'f' * 64, 'a' * 64, 'quality', '/future/quality', qualification_digest='b' * 64),
            'QUALITY_ONLY',
        )
        # Missing or mismatched qualification digest MUST fail
        with self.assertRaises(ValueError):
            c3.authorize(ap, 'f' * 64, 'a' * 64, 'quality', '/future/quality', qualification_digest=None)
        with self.assertRaises(ValueError):
            c3.authorize(ap, 'f' * 64, 'a' * 64, 'quality', '/future/quality', qualification_digest='9' * 64)
        # QUALITY_ONLY cannot authorize OFF
        with self.assertRaises(ValueError):
            c3.authorize(ap, 'f' * 64, 'a' * 64, 'off', '/future/quality',
                         qualification_digest='b' * 64, quality_digest='c' * 64)
        # OFF_AB authorized only with matching quality_sha256 & quota_s=10800
        ap_off = dict(ap, scope='OFF_AB', quota_s=10800, quality_sha256='c' * 64)
        self.assertEqual(
            c3.authorize(ap_off, 'f' * 64, 'a' * 64, 'off', '/future/quality',
                         qualification_digest='b' * 64, quality_digest='c' * 64),
            'OFF_AB',
        )

    def test_process_result_fixture_checks_watchdog_topology_and_ram(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            item = dict(c3.schedule()[0])
            item.update(name=r3.name(item), argv=['FIXTURE_NOT_EXECUTED'])
            visited, frontier = c3.POLICIES[item['policy']]
            row = dict(
                mode='OFF', instrumentation=False, workers=2, sync_interval=16, beam=432, jobs=1,
                merge_impl='flat', visited_policy=visited, frontier_mode=frontier, query_id=0,
                ids=list(range(10)), squared_l2=list(map(float, range(10))), complete_top_k=True,
                counters=None, latency_ns=3000000,
            )
            with (out / 'beam_432_p2_OFF.jsonl').open('w') as stream:
                for i in range(c3.N):
                    row['query_id'] = i
                    stream.write(json.dumps(row) + '\n')
            artifacts = {'graphs': {item['graph']: '/fixture/graph'},
                         'base': '/fixture/base', 'queries': '/fixture/queries', 'test': '/fixture/ids'}
            summary = dict(
                requested_cpus=[0, 2], observed_cpus=[0, 2], workers=2, sync_interval=16, jobs=1, k=10,
                entry=0, warmup_count=100, query_count=c3.N, mode='OFF', merge_impl='flat',
                graph_format='pipnn', visited_policy=visited, frontier_mode=frontier,
                graph_path='/fixture/graph', base_path='/fixture/base', query_path='/fixture/queries',
                vm_hwm_kib=850000,
                runs=[dict(beam=432, batch_wall_ns=30000000000, qps_wall=c3.N / 30.0,
                           latency_us=dict(mean=3000, p50=3000, p95=3000, p99=3000))],
            )
            (out / 'p2_eval_summary.json').write_text(json.dumps(summary))
            guard = dict(exit_code=0, guard_failure=None, host_samples=16,
                         pid=100, process_start_ticks='4', watchdog_pid=201)
            (out / 'manifest.json').write_text(json.dumps(guard))
            snaps = [make_snap(make_cap(t, own=180 * t, monitor=2 * t, watchdog=1 * t, watchdog_pid=201))
                     for t in range(16)]
            (out / 'host.jsonl').write_text(''.join(json.dumps(s) + '\n' for s in snaps))
            with patch.object(r3, 'ids', return_value=list(range(c3.N))):
                rec = r3.process_result(item, out, artifacts, guard, phase='off')
                self.assertEqual(rec['cpu_percent'], 180.0)
                self.assertEqual(rec['foreign_all_fraction'], 0.0)
                self.assertAlmostEqual(rec['watchdog_cpu_seconds'], 0.15, places=6)
                # Mismatched watchdog PID must fail
                bad_guard = dict(guard, watchdog_pid=999)
                with self.assertRaises(ValueError):
                    r3.process_result(item, out, artifacts, bad_guard, phase='off')
                # Invalid negative vm_hwm_kib must fail
                summary['vm_hwm_kib'] = -1
                (out / 'p2_eval_summary.json').write_text(json.dumps(summary))
                with self.assertRaises(ValueError):
                    r3.process_result(item, out, artifacts, guard, phase='off')

    def test_ram_hard_gate_and_freeze_tamper_fail_closed(self):
        self.assertTrue(a3.ram_pair(100000, 165536)['hard_pass'])
        self.assertFalse(a3.ram_pair(100000, 165537)['hard_pass'])
        self.assertTrue(a3.ram_pair(1000000, 1100000)['hard_pass'])
        self.assertFalse(a3.ram_pair(1000000, 1100001)['hard_pass'])
        for bad in (None, 0, -1, 0.5, float('nan'), float('inf'), True, '850000'):
            with self.assertRaises(ValueError):
                a3.ram_pair(bad, 100000)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'comp.py').write_text('v1\n')
            f = dict(protocol=c3.PROTOCOL, revision=c3.REVISION, schema=c3.SCHEMA,
                     beam=432, cpus=[0, 2], workers=2, components={'comp.py': c3.sha(root / 'comp.py')})
            fp = root / 'freeze.json'
            fp.write_text(json.dumps(f))
            with patch.object(c3, 'ROOT', root):
                c3.load_freeze(fp, environment=False)
                (root / 'comp.py').write_text('tampered\n')
                with self.assertRaises(ValueError):
                    c3.load_freeze(fp, environment=False)

    def test_qualification_900s_pass_and_hold_on_synthetic_clock(self):
        fake_host = dict(cpu_model='AMD Ryzen 5 PRO 4650U', cpus=[0, 2],
                         worker_cores_cpus=[0, 1, 2, 3], ccx0_cpus=[0, 1, 2, 3, 4, 5],
                         cores=['0', '1'], siblings=['0-1', '2-3'], l3_shared_lists=['0-5', '0-5'],
                         ccx1_l3_shared_list='6-11', allowed_cpus=list(range(12)),
                         kernel='7.0.0-43-generic', clk_tck=100)
        # 1. Clean 900s run with periodic 200ms CCX1 timer pulses at t=300 and t=600 -> MUST PASS!
        t_box = [0.0]
        cum_pulse = [0]

        def snap_pass(_root):
            t = t_box[0]
            if int(t) in (300, 600):
                cum_pulse[0] += 20
            pc = {str(i): 0 for i in range(12)}
            pc['8'] = int(2 * t)
            pc['9'] = cum_pulse[0]
            extra = {'500': ['sa1', cum_pulse[0], 10, 9]} if cum_pulse[0] else {}
            return make_snap(make_cap(t, owned_pid=None, own=0, monitor=int(2 * t), per_cpu=pc, extra_procs=extra))

        def step_sleep(sec):
            t_box[0] += sec

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'qual_pass'
            res, _ = q3.run_qualification(out, snapshot_fn=snap_pass, sleep_fn=step_sleep,
                                          host_fn=lambda: fake_host, freeze_check=False)
            self.assertEqual(res['verdict'], 'QUALIFICATION_PASS')
            self.assertTrue(res['qualification_pass'])
            self.assertEqual(res['failed_windows_10s'], 0)
            self.assertEqual(res['failed_windows_15s'], 0)
            self.assertGreaterEqual(res['passed_windows_15s'], 885)
            self.assertTrue((out / 'BUNDLE.sha256').exists())

        # 2. Contaminated 900s run with worker-core contention at t=400..415 -> MUST HOLD!
        t_box2 = [0.0]
        bad_ticks = [0]

        def snap_fail(_root):
            t = t_box2[0]
            if 400 <= t <= 415:
                bad_ticks[0] += 5
            pc = {str(i): 0 for i in range(12)}
            pc['1'] = bad_ticks[0]
            pc['8'] = int(2 * t)
            extra = {'555': ['worker_hog', bad_ticks[0], 10, 1]} if bad_ticks[0] else {}
            return make_snap(make_cap(t, owned_pid=None, own=0, monitor=int(2 * t), per_cpu=pc, extra_procs=extra))

        def step_sleep2(sec):
            t_box2[0] += sec

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'qual_hold'
            res, _ = q3.run_qualification(out, snapshot_fn=snap_fail, sleep_fn=step_sleep2,
                                          host_fn=lambda: fake_host, freeze_check=False)
            self.assertEqual(res['verdict'], 'QUALIFICATION_HOLD')
            self.assertFalse(res['qualification_pass'])
            self.assertGreater(res['failed_windows_10s'], 0)
            self.assertTrue(any('worker-cores [0..3]' in k for k in res['failure_reason_counts']))


class Design3AnalyzerParityAndNoiseBalanceTests(unittest.TestCase):
    def test_estimands_are_mathematically_identical_to_design2(self):
        rows3, latency, quality = fixture_d3()
        # Strip design-3 noise fields for design-2 analyzer comparison
        extra_keys = {
            'monitor_cpu_seconds', 'watchdog_cpu_seconds',
            'foreign_workers_fraction', 'foreign_ccx0_fraction', 'foreign_all_fraction',
            'max_rolling_foreign_workers_fraction', 'max_rolling_foreign_ccx0_fraction',
            'max_rolling_foreign_all_fraction',
        }
        rows2 = [{k: v for k, v in r.items() if k not in extra_keys} for r in rows3]
        build = {g: dict(wall_s=42.0 if g.startswith('stock') else 34.0, graph_bytes=200000000) for g in c3.GRAPHS}

        real_b2, real_b3 = a_d2.bootstrap, a3.bootstrap
        with patch.object(a_d2, 'bootstrap', side_effect=lambda x, **kw: real_b2(x, resamples=64, **kw)), \
             patch.object(a3, 'bootstrap', side_effect=lambda x, **kw: real_b3(x, resamples=64, **kw)):
            out2 = a_d2.analyze(rows2, latency, quality, build=build)
            out3 = a3.analyze(rows3, latency, quality, build=build)

        c3.validate_schema(out3, 'analysis')
        for field in (
            'verdict', 'primary_estimand', 'primary_reduction', 'speedup',
            'primary_log_ci95', 'primary_reduction_ci95', 'drift_log_ci95',
            'arithmetic_base_us', 'arithmetic_opt_us', 'arithmetic_reduction',
            'graph_log_effects', 'ram_hard_pass', 'stability_pass', 'safety_pass',
            'B_quality_pass', 'build_search', 'query_bootstrap', 'joint_bootstrap',
            'graph_population_ci', 'evidence_label',
        ):
            self.assertEqual(out2[field], out3[field], f'estimand drift in field: {field}')

    def test_paired_noise_balance_detects_systematic_imbalance_without_altering_verdict(self):
        # Balanced noise -> imbalance_warning = False
        rows_bal, lat, qual = fixture_d3(foreign_fn=lambda b, j, p: (0.002, 0.004, 0.008))
        real_b3 = a3.bootstrap
        with patch.object(a3, 'bootstrap', side_effect=lambda x, **kw: real_b3(x, resamples=64, **kw)):
            res_bal = a3.analyze(rows_bal, lat, qual)
        self.assertFalse(res_bal['noise_balance']['imbalance_warning'])
        self.assertIsNone(res_bal['noise_balance']['spearman_delta_all_vs_log_effect'])

        # Systematic opt > base noise -> imbalance_warning = True, CI > 0, Spearman finite
        def imbalanced(b, j, p):
            if p == 'base':
                return (0.001, 0.002, 0.004 + 0.0001 * b)
            return (0.006, 0.009, 0.014 + 0.0003 * b)

        rows_imb, lat2, qual2 = fixture_d3(foreign_fn=imbalanced)
        # Add tiny variation in x_gb across blocks so Spearman is non-degenerate
        for b in range(12):
            for j in range(6):
                lat2[b, j, 1] *= (1.0 - 0.0005 * b)
                idx = next(i for i, r in enumerate(rows_imb)
                           if r['block'] == b and r['graph'] == c3.GRAPHS[j] and r['policy'] == 'opt')
                v = float(lat2[b, j, 1, 0])
                rows_imb[idx].update(mean_us=v, p50_us=v, p95_us=v, p99_us=v, qps_wall=1e6 / v)
        with patch.object(a3, 'bootstrap', side_effect=lambda x, **kw: real_b3(x, resamples=64, **kw)):
            res_imb = a3.analyze(rows_imb, lat2, qual2)
        c3.validate_schema(res_imb, 'analysis')
        nb = res_imb['noise_balance']
        self.assertTrue(nb['imbalance_warning'])
        self.assertGreater(nb['paired_delta_all_ci95'][0], 0.0)
        self.assertGreater(nb['paired_delta_workers_ci95'][0], 0.0)
        self.assertIsNotNone(nb['spearman_delta_all_vs_log_effect'])
        # Confirm hierarchy check rejects corrupted process receipt
        bad_rows = copy.deepcopy(rows_bal)
        bad_rows[0]['foreign_workers_fraction'] = 0.02
        bad_rows[0]['foreign_all_fraction'] = 0.005
        with self.assertRaises(ValueError):
            a3.analyze(bad_rows, lat, qual)

    def test_plan_never_opens_ann_inputs_and_produces_exact_18_and_144_counts(self):
        artifacts = {k: '/missing/' + k for k in ['binary', 'base', 'queries', 'val', 'test', 'warmup']}
        artifacts['graphs'] = {g: '/missing/' + g for g in c3.GRAPHS}
        with patch.object(Path, 'open', side_effect=AssertionError('plan opened a file')):
            p_off = r3.plan(artifacts, 'off', '/future/off')
            p_qual = r3.plan(artifacts, 'quality', '/future/quality')
        self.assertEqual(len(p_qual), 18)
        self.assertEqual(len(p_off), 144)
        self.assertEqual(p_off[0]['argv'][p_off[0]['argv'].index('--beams') + 1], '432')
        self.assertEqual(p_off[0]['argv'][p_off[0]['argv'].index('--cpu-list') + 1], '0,2')


if __name__ == '__main__':
    unittest.main()
