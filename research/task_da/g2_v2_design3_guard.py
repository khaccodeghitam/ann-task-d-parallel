"""Design-3 single-pass 1 Hz /proc telemetry, watchdog accounting, and topology-aware guard.

Amendments over design-2 (zero changes to design-2 or frozen base guard source):
1. Single /proc/[0-9]*/stat pass per sample (eliminates duplicate /proc scanning).
2. Explicit watchdog_pid accounting alongside owned_pid and monitor_pid.
3. Net window subtraction across window endpoints (eliminates per-1s max(0,.) rectification bias).
4. Topology-aware CPU noise tiers: worker cores+SMT [0..3], CCX0/L3 [0..5], whole host [0..11],
   plus sustained single-process cap and instant KNOWN_CPU_JOBS rejection.
5. Phase-aware contention guard: strict 3-tier noise limits for OFF / qualification;
   coarse anti-overload limits + full hardware/thermal safety for deterministic QUALITY_ONLY ON.
"""
from datetime import datetime, timezone
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from .g2_v2_design3_contract import (
    ALL_HOST_CPUS, CCX0_CPUS, CPUS, ROOT, WORKER_CORES_CPUS, load_freeze, require,
)

MAX_GAP_S = 2.0
MIN_GAP_S = 0.5
MIN_RUN_WINDOW_S = 5.0

# Phase-specific frozen design-3 contention policies (normalized by wall_s * len(CPUS) = wall_s * 2;
# single_process_max_rate is CPU-s/s = fraction of 1 core).
PHASE_POLICIES = {
    'off': {
        'worker_cores_window_s': 10.0,
        'worker_cores_max_fraction': 0.01,   # <= 1.0% of p2 capacity on CPUs {0,1,2,3}
        'ccx0_window_s': 10.0,
        'ccx0_max_fraction': 0.02,           # <= 2.0% of p2 capacity on L3 CCX0 {0..5}
        'host_window_s': 15.0,
        'host_max_fraction': 0.025,          # <= 2.5% of p2 capacity on {0..11} (0.42% of 12 threads)
        'single_proc_window_s': 10.0,
        'single_proc_max_rate': 0.10,        # <= 10% of 1 core for any single foreign process
        'preflight_window_s': 15.0,
    },
    'quality': {
        'worker_cores_window_s': 10.0,
        'worker_cores_max_fraction': None,   # recorded diagnostically; deterministic quality unaffected
        'ccx0_window_s': 10.0,
        'ccx0_max_fraction': None,           # recorded diagnostically
        'host_window_s': 15.0,
        'host_max_fraction': 0.10,           # <= 10% of p2 capacity (anti-overload)
        'single_proc_window_s': 10.0,
        'single_proc_max_rate': 0.25,        # <= 25% of 1 core sustained
        'preflight_window_s': 10.0,
    },
}
PHASE_POLICIES['qualification'] = dict(PHASE_POLICIES['off'])

KNOWN_CPU_JOBS = frozenset({
    'stress-ng', 'sysbench', 'task_da_p2_eval', 'task_da_p1_eval',
    'search_disk_ind', 'build_disk_inde', 'build_memory_in',
})
LEGACY_ANN_COMMS = frozenset({'search_disk_ind', 'build_disk_inde', 'build_memory_in'})


def _utc():
    return datetime.now(timezone.utc).isoformat()


def _read_text(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def parse_stat(text):
    """Parse /proc/<pid>/stat -> comm, utime+stime ticks, starttime, last CPU processor."""
    left, rest = text.rsplit(')', 1)
    fields = rest.split()
    require(len(fields) >= 37, 'truncated /proc/<pid>/stat')
    return dict(
        comm=left.split('(', 1)[1],
        ticks=int(fields[11]) + int(fields[12]),
        start=int(fields[19]),
        processor=int(fields[36]),
    )


def parse_proc_stat(text):
    """Parse aggregate and per-CPU busy ticks (user+nice+system+irq+softirq+steal) from /proc/stat."""
    agg = None
    per_cpu = {}
    for line in text.splitlines():
        if not line.startswith('cpu'):
            continue
        parts = line.split()
        label = parts[0]
        vals = [int(v) for v in parts[1:9]]
        require(len(vals) == 8 and all(v >= 0 for v in vals), f'invalid /proc/stat line: {label}')
        busy = sum(vals) - vals[3] - vals[4]  # exclude idle(3) and iowait(4); no guest double-count
        if label == 'cpu':
            agg = busy
        elif label[3:].isdigit():
            per_cpu[label[3:]] = busy
    require(agg is not None and len(per_cpu) >= len(ALL_HOST_CPUS), 'incomplete /proc/stat CPU rows')
    for c in ALL_HOST_CPUS:
        require(str(c) in per_cpu, f'missing cpu{c} in /proc/stat')
    # In Linux fs/proc/stat.c, aggregate cpu sums 6 busy fields in ns before nsec_to_clock_t floor
    # division, whereas each cpuN floors individually: 0 <= agg - sum(per_cpu) <= 6 * len(per_cpu).
    cpu_sum = sum(per_cpu.values())
    max_trunc_slack = 6 * len(per_cpu)
    require(0 <= agg - cpu_sum <= max_trunc_slack,
            f'/proc/stat conservation violated: agg={agg} sum={cpu_sum} slack_max={max_trunc_slack}')
    return agg, per_cpu


def _zero_proc():
    return dict(comm='', ticks=0, start=0, processor=-1)


def _read_small(path):
    try:
        fd = os.open(path, os.O_RDONLY)
        try:
            return os.read(fd, 4096).decode('utf-8', 'replace').strip()
        finally:
            os.close(fd)
    except OSError:
        return None


_SYSFS_CACHE = None


def _sysfs_paths():
    """Discover static hwmon/power/cpufreq sysfs file paths once; read live values each tick."""
    global _SYSFS_CACHE
    if _SYSFS_CACHE is not None:
        return _SYSFS_CACHE
    sensor_entries = []
    for h in sorted(Path('/sys/class/hwmon').glob('hwmon*')):
        h_name = _read_small(str(h / 'name'))
        for p in sorted(h.glob('temp*_input')):
            lbl = _read_small(str(p.with_name(p.name.replace('_input', '_label'))))
            crit = _read_small(str(p.with_name(p.name.replace('_input', '_crit'))))
            sensor_entries.append((str(p), h_name, lbl, crit))
    power_paths = [str(p) for p in sorted(Path('/sys/class/power_supply').glob('*/online'))]
    cpufreq_paths = [
        str(p) for p in sorted(Path('/sys/devices/system/cpu').glob('cpu*/cpufreq/*'))
        if p.name in ('scaling_cur_freq', 'scaling_max_freq', 'scaling_governor')
    ]
    _SYSFS_CACHE = (sensor_entries, power_paths, cpufreq_paths)
    return _SYSFS_CACHE


def _parse_stat_bytes(data):
    """Fast bytes parser for /proc/<pid>/stat matching parse_stat() identically."""
    rpar = data.rfind(b')')
    require(rpar > 0, 'malformed /proc/<pid>/stat')
    lpar = data.find(b'(')
    fields = data[rpar + 1:].split()
    require(len(fields) >= 37, 'truncated /proc/<pid>/stat')
    return (
        data[lpar + 1:rpar].decode('utf-8', 'replace'),
        int(fields[11]) + int(fields[12]),
        int(fields[19]),
        int(fields[36]),
    )


def host_snapshot_v3(root, pid=None, *, watchdog_pid=None):
    """Single-pass low-overhead host + per-CPU + process telemetry snapshot."""
    start_wall = time.monotonic()
    cpu_start = time.process_time()

    meminfo_raw = _read_small('/proc/meminfo') or ''
    memory = {}
    for line in meminfo_raw.splitlines():
        if line.startswith(('MemAvailable:', 'SwapTotal:', 'SwapFree:')):
            k, v = line.split(':', 1)
            memory[k] = int(v.split()[0]) * 1024

    sensor_entries, power_paths, cpufreq_paths = _sysfs_paths()
    sensors = {}
    for spath, h_name, lbl, crit in sensor_entries:
        value = _read_small(spath)
        if value and value.lstrip('-').isdigit():
            sensors[spath] = dict(
                value_C=int(value) / 1000.0,
                name=h_name,
                label=lbl,
                critical_mC=crit,
            )

    power = {p: _read_small(p) for p in power_paths}
    cpu_freq = {p: _read_small(p) for p in cpufreq_paths}

    tasks = []
    if pid is not None:
        task_dir = f'/proc/{pid}/task'
        try:
            with os.scandir(task_dir) as it:
                for e in it:
                    tasks.append(dict(tid=e.name, status=_read_small(f'{task_dir}/{e.name}/status')))
        except OSError:
            pass

    # Read /proc/stat + owned/monitor/watchdog + single os.scandir pass over /proc/[0-9]*/stat
    agg_busy, per_cpu_busy = parse_proc_stat(Path('/proc/stat').read_text())
    mon_pid = os.getpid()
    own = parse_stat(Path(f'/proc/{pid}/stat').read_text()) if pid is not None else _zero_proc()
    monitor = parse_stat(Path(f'/proc/{mon_pid}/stat').read_text())
    wd = _zero_proc()
    if watchdog_pid is not None:
        wd_text = _read_small(f'/proc/{watchdog_pid}/stat')
        if wd_text:
            wd = parse_stat(wd_text)

    excluded = {mon_pid}
    if pid is not None:
        excluded.add(pid)
    if watchdog_pid is not None:
        excluded.add(watchdog_pid)

    ann = []
    named_jobs = []
    processes = {}
    with os.scandir('/proc') as it:
        for entry in it:
            pid_str = entry.name
            if not pid_str.isdigit():
                continue
            try:
                fd = os.open(f'/proc/{pid_str}/stat', os.O_RDONLY)
                try:
                    raw = os.read(fd, 512)
                finally:
                    os.close(fd)
                comm, ticks, start_tk, proc_cpu = _parse_stat_bytes(raw)
            except (OSError, ValueError, IndexError):
                continue  # exited or unreadable PID; /proc/stat aggregate still covers its ticks
            pid_int = int(pid_str)
            if pid_int not in excluded:
                if comm in LEGACY_ANN_COMMS:
                    ann.append(dict(pid=pid_int, comm=comm))
                if comm in KNOWN_CPU_JOBS:
                    named_jobs.append(dict(pid=pid_int, comm=comm, processor=proc_cpu))
            # Compact lossless serialization: omit zero-tick processes (delta from absent -> ticks > 0 is exact)
            if ticks > 0 or pid_int in excluded:
                processes[pid_str] = [comm, ticks, start_tk, proc_cpu]

    v3_cpu = dict(
        monotonic_s=time.monotonic(),
        hz=os.sysconf('SC_CLK_TCK'),
        host_busy_ticks=agg_busy,
        per_cpu_busy_ticks=per_cpu_busy,
        owned=own,
        monitor=monitor,
        watchdog=wd,
        owned_pid=pid,
        monitor_pid=mon_pid,
        watchdog_pid=watchdog_pid,
        named_jobs=named_jobs,
        processes=processes,
    )
    return dict(
        timestamp=_utc(),
        monotonic_s=start_wall,
        mem_available=memory['MemAvailable'],
        swap_used=memory['SwapTotal'] - memory['SwapFree'],
        free_disk=shutil.disk_usage(root).free,
        sensors=sensors,
        power=power,
        rapl={},
        cpu=cpu_freq,
        tasks=tasks,
        ann=ann,
        sqpoll=[],
        load=_read_small('/proc/loadavg'),
        collection_wall_s=time.monotonic() - start_wall,
        observer_cpu_s=time.process_time() - cpu_start,
        v3_cpu=v3_cpu,
    )


def _unpack_proc_entry(entry):
    if isinstance(entry, list):
        require(len(entry) == 4, 'invalid compact process entry')
        return entry[0], int(entry[1]), int(entry[2]), int(entry[3])
    require(isinstance(entry, dict), 'invalid dict process entry')
    return entry['comm'], int(entry['ticks']), int(entry['start']), int(entry.get('processor', -1))


def validate_step(before, after):
    """Validate two consecutive captures for cadence, PID identity, and counter monotonicity."""
    dt = after['monotonic_s'] - before['monotonic_s']
    require(MIN_GAP_S <= dt <= MAX_GAP_S and before['hz'] == after['hz'] > 0,
            f'CPU cadence/gap invalid: dt={dt:.3f}s')
    if before['owned_pid'] is not None and after['owned_pid'] is not None:
        require(before['owned_pid'] == after['owned_pid']
                and before['owned']['start'] == after['owned']['start'],
                'owned PID identity changed')
    require(before['monitor_pid'] == after['monitor_pid']
            and before['monitor']['start'] == after['monitor']['start'],
            'monitor PID identity changed')
    if before.get('watchdog_pid') is not None and after.get('watchdog_pid') is not None:
        require(before['watchdog_pid'] == after['watchdog_pid']
                and before['watchdog']['start'] == after['watchdog']['start'],
                'watchdog PID identity changed')

    require(after['host_busy_ticks'] >= before['host_busy_ticks'], 'host CPU counter regressed')
    require(after['owned']['ticks'] >= before['owned']['ticks'], 'owned CPU counter regressed')
    require(after['monitor']['ticks'] >= before['monitor']['ticks'], 'monitor CPU counter regressed')
    wd_b = before.get('watchdog', _zero_proc())['ticks']
    wd_a = after.get('watchdog', _zero_proc())['ticks']
    if before.get('watchdog_pid') is not None and after.get('watchdog_pid') is not None:
        require(wd_a >= wd_b, 'watchdog CPU counter regressed')

    for c in ALL_HOST_CPUS:
        k = str(c)
        require(k in before['per_cpu_busy_ticks'] and k in after['per_cpu_busy_ticks'],
                f'missing per-CPU counter cpu{k}')
        require(after['per_cpu_busy_ticks'][k] >= before['per_cpu_busy_ticks'][k],
                f'per-CPU counter regressed: cpu{k}')
    return dt


def window_accounting(start_cap, end_cap):
    """Exact net window accounting between start_cap and end_cap (NO per-1s rectification bias)."""
    wall_s = end_cap['monotonic_s'] - start_cap['monotonic_s']
    require(wall_s > 0 and start_cap['hz'] == end_cap['hz'] > 0, 'invalid window span/hz')
    hz = end_cap['hz']

    host_busy_s = (end_cap['host_busy_ticks'] - start_cap['host_busy_ticks']) / hz
    owned_s = (end_cap['owned']['ticks'] - start_cap['owned']['ticks']) / hz
    monitor_s = (end_cap['monitor']['ticks'] - start_cap['monitor']['ticks']) / hz
    wd_s = 0.0
    if start_cap.get('watchdog_pid') is not None and end_cap.get('watchdog_pid') is not None:
        wd_s = (end_cap['watchdog']['ticks'] - start_cap['watchdog']['ticks']) / hz
    elif end_cap.get('watchdog_pid') is not None:
        wd_s = end_cap['watchdog']['ticks'] / hz

    require(host_busy_s >= 0 and owned_s >= 0 and monitor_s >= 0 and wd_s >= 0,
            'negative counter delta over window')

    self_total_s = owned_s + monitor_s + wd_s
    # Single net subtraction across the full window eliminates per-second max(0,.) rectification bias!
    foreign_all_s = max(0.0, host_busy_s - self_total_s)

    per_cpu_s = {
        c: (end_cap['per_cpu_busy_ticks'][str(c)] - start_cap['per_cpu_busy_ticks'][str(c)]) / hz
        for c in ALL_HOST_CPUS
    }
    require(all(v >= 0 for v in per_cpu_s.values()), 'negative per-CPU delta over window')
    busy_workers_s = sum(per_cpu_s[c] for c in WORKER_CORES_CPUS)
    busy_ccx0_s = sum(per_cpu_s[c] for c in CCX0_CPUS)

    excluded = {str(end_cap['monitor_pid'])}
    if end_cap['owned_pid'] is not None:
        excluded.add(str(end_cap['owned_pid']))
    if end_cap.get('watchdog_pid') is not None:
        excluded.add(str(end_cap['watchdog_pid']))

    # Per-process net deltas over the full window
    competing = []
    procs_workers_s = 0.0
    procs_ccx0_s = 0.0
    start_procs = start_cap.get('processes', {})
    for pid_str, entry in end_cap.get('processes', {}).items():
        if pid_str in excluded:
            continue
        comm, ticks_end, st_end, proc_cpu = _unpack_proc_entry(entry)
        prev = start_procs.get(pid_str)
        if prev is not None:
            _, ticks_start, st_start, _ = _unpack_proc_entry(prev)
            if st_start == st_end:
                dticks = ticks_end - ticks_start
            else:
                dticks = ticks_end  # PID reused during window; new process started at 0
        else:
            # Absent at window start (had 0 ticks or spawned during window)
            dticks = ticks_end
        if dticks > 0:
            cpu_s = dticks / hz
            competing.append(dict(
                pid=int(pid_str),
                comm=comm,
                cpu_seconds=cpu_s,
                cpu_rate=cpu_s / wall_s,
                processor=proc_cpu,
            ))
            if proc_cpu in WORKER_CORES_CPUS:
                procs_workers_s += cpu_s
            if proc_cpu in CCX0_CPUS:
                procs_ccx0_s += cpu_s

    competing.sort(key=lambda item: item['cpu_seconds'], reverse=True)
    max_single = competing[0] if competing else None
    max_single_rate = max_single['cpu_rate'] if max_single else 0.0

    # Conservation-bounded topology foreign estimates:
    #   foreign_lb(S) = max(0, busy(S) - self_total_s) catches untracked hard-IRQs/short-lived bursts
    #   procs(S)      = tracked foreign PIDs on S (zero dilution from monitor running on CCX1)
    #   capped above by foreign_all_s so 0 <= foreign_workers <= foreign_ccx0 <= foreign_all ALWAYS!
    foreign_workers_lb = max(0.0, busy_workers_s - self_total_s)
    foreign_ccx0_lb = max(0.0, busy_ccx0_s - self_total_s)
    foreign_workers_s = min(foreign_all_s, max(foreign_workers_lb, procs_workers_s))
    foreign_ccx0_s = min(foreign_all_s, max(foreign_ccx0_lb, procs_ccx0_s, foreign_workers_s))

    denom = wall_s * len(CPUS)
    return dict(
        wall_s=wall_s,
        host_busy_s=host_busy_s,
        owned_cpu_s=owned_s,
        monitor_cpu_s=monitor_s,
        watchdog_cpu_s=wd_s,
        foreign_all_s=foreign_all_s,
        foreign_workers_s=foreign_workers_s,
        foreign_ccx0_s=foreign_ccx0_s,
        foreign_all_fraction=foreign_all_s / denom,
        foreign_workers_fraction=foreign_workers_s / denom,
        foreign_ccx0_fraction=foreign_ccx0_s / denom,
        max_single_foreign_rate=max_single_rate,
        max_single_foreign_comm=max_single['comm'] if max_single else None,
        competing_processes=competing[:10],
    )


class ContentionV3:
    """Topology-aware, phase-aware rolling window contention monitor with net subtraction."""

    def __init__(self, phase='off'):
        require(phase in PHASE_POLICIES, f'unknown contention phase: {phase}')
        self.phase = phase
        self.policy = PHASE_POLICIES[phase]
        self.captures = []
        self.evaluations = []

    def _window_start(self, min_window_s):
        """Return the most recent capture index i such that captures[-1] - captures[i] >= min_window_s."""
        end_t = self.captures[-1]['monotonic_s']
        for idx in range(len(self.captures) - 2, -1, -1):
            if end_t - self.captures[idx]['monotonic_s'] >= min_window_s:
                return self.captures[idx]
        return None

    def observe(self, cap):
        reasons = []
        # Instantaneous rejection of named CPU/ANN benchmark jobs (no waiting window)
        excluded = {cap['monitor_pid']}
        if cap['owned_pid'] is not None:
            excluded.add(cap['owned_pid'])
        if cap.get('watchdog_pid') is not None:
            excluded.add(cap['watchdog_pid'])

        for nj in cap.get('named_jobs', []):
            if nj['pid'] not in excluded and nj['comm'] in KNOWN_CPU_JOBS:
                reasons.append(f"foreign named CPU/ANN job: {nj['comm']}")
                break
        if not reasons:
            for pid_str, entry in cap.get('processes', {}).items():
                comm, _, _, _ = _unpack_proc_entry(entry)
                if int(pid_str) not in excluded and comm in KNOWN_CPU_JOBS:
                    reasons.append(f'foreign named CPU/ANN job: {comm}')
                    break

        if self.captures:
            validate_step(self.captures[-1], cap)
        self.captures.append(cap)

        ev = dict(monotonic_s=cap['monotonic_s'], phase=self.phase)
        pol = self.policy

        # 10s window checks (worker cores [0..3], CCX0 [0..5], single foreign process)
        w10_start = self._window_start(pol['worker_cores_window_s'])
        if w10_start is not None:
            acc10 = window_accounting(w10_start, cap)
            ev['window_10s'] = acc10
            if (pol['worker_cores_max_fraction'] is not None
                    and acc10['foreign_workers_fraction'] > pol['worker_cores_max_fraction']):
                reasons.append(
                    f"worker-cores [0..3] foreign CPU {acc10['foreign_workers_fraction']:.4f} "
                    f"> {pol['worker_cores_max_fraction']:.4f} over >={pol['worker_cores_window_s']:.0f}s"
                )
            if (pol['ccx0_max_fraction'] is not None
                    and acc10['foreign_ccx0_fraction'] > pol['ccx0_max_fraction']):
                reasons.append(
                    f"CCX0 [0..5] foreign CPU {acc10['foreign_ccx0_fraction']:.4f} "
                    f"> {pol['ccx0_max_fraction']:.4f} over >={pol['ccx0_window_s']:.0f}s"
                )
            if (pol['single_proc_max_rate'] is not None
                    and acc10['max_single_foreign_rate'] > pol['single_proc_max_rate']):
                reasons.append(
                    f"single foreign process {acc10['max_single_foreign_comm']} "
                    f"{acc10['max_single_foreign_rate']:.4f} > {pol['single_proc_max_rate']:.4f} "
                    f"over >={pol['single_proc_window_s']:.0f}s"
                )

        # 15s window check (whole host [0..11])
        w15_start = self._window_start(pol['host_window_s'])
        if w15_start is not None:
            acc15 = window_accounting(w15_start, cap)
            ev['window_15s'] = acc15
            if (pol['host_max_fraction'] is not None
                    and acc15['foreign_all_fraction'] > pol['host_max_fraction']):
                reasons.append(
                    f"host [0..11] foreign CPU {acc15['foreign_all_fraction']:.4f} "
                    f"> {pol['host_max_fraction']:.4f} over >={pol['host_window_s']:.0f}s"
                )

        ev['reasons'] = list(reasons)
        self.evaluations.append(ev)
        return reasons

    @property
    def ready(self):
        if len(self.captures) < 2:
            return False
        elapsed = self.captures[-1]['monotonic_s'] - self.captures[0]['monotonic_s']
        return elapsed >= self.policy['preflight_window_s']


def cpu_and_noise_metrics(captures, *, phase='off'):
    """Compute validated run-level CPU utilization and topology-aware foreign noise summaries."""
    require(len(captures) >= 2, 'CPU samples missing')
    for before, after in zip(captures, captures[1:]):
        validate_step(before, after)

    total = window_accounting(captures[0], captures[-1])
    require(total['wall_s'] >= MIN_RUN_WINDOW_S and total['owned_cpu_s'] > 0,
            'CPU observation window too short/empty')

    # Replay rolling windows to capture peak rolling foreign fractions
    replay = ContentionV3(phase=phase)
    max_w_workers = total['foreign_workers_fraction']
    max_w_ccx0 = total['foreign_ccx0_fraction']
    max_w_all = total['foreign_all_fraction']
    for cap in captures:
        replay.observe(cap)
        ev = replay.evaluations[-1]
        if 'window_10s' in ev:
            max_w_workers = max(max_w_workers, ev['window_10s']['foreign_workers_fraction'])
            max_w_ccx0 = max(max_w_ccx0, ev['window_10s']['foreign_ccx0_fraction'])
        if 'window_15s' in ev:
            max_w_all = max(max_w_all, ev['window_15s']['foreign_all_fraction'])

    return dict(
        cpu_seconds=total['owned_cpu_s'],
        wall_seconds=total['wall_s'],
        cpu_percent=100.0 * total['owned_cpu_s'] / total['wall_s'],
        cpu_capacity_percent=100.0 * total['owned_cpu_s'] / (len(CPUS) * total['wall_s']),
        cpu_window='first_to_last_alive_proc_stat_sample_including_load_warmup_output',
        monitor_cpu_seconds=total['monitor_cpu_s'],
        watchdog_cpu_seconds=total['watchdog_cpu_s'],
        foreign_workers_fraction=total['foreign_workers_fraction'],
        foreign_ccx0_fraction=total['foreign_ccx0_fraction'],
        foreign_all_fraction=total['foreign_all_fraction'],
        max_rolling_foreign_workers_fraction=max_w_workers,
        max_rolling_foreign_ccx0_fraction=max_w_ccx0,
        max_rolling_foreign_all_fraction=max_w_all,
    )


def amd_reasons(snapshot, owned_pid=None):
    temps = [v['value_C'] for v in snapshot['sensors'].values()
             if v['name'] == 'k10temp' and v['label'] == 'Tctl']
    if (len(temps) != 1 or type(temps[0]) not in (float, int)
            or not math.isfinite(temps[0]) or not 0 < temps[0] <= 120):
        return ['valid unique Tctl missing']
    return ['Tctl threshold'] if temps[0] >= (95 if owned_pid is not None else 85) else []


def host_contract():
    """Verify full 12-CPU topology, worker cores [0,2], CCX0 [0-5], CCX1 [6-11], kernel, CLK_TCK."""
    require('AMD Ryzen 5 PRO 4650U' in Path('/proc/cpuinfo').read_text(),
            'only Ryzen 4650U is authorized')
    require(set(CPUS) <= os.sched_getaffinity(0), 'worker CPUs unavailable')
    cores, siblings, caches = [], [], []
    for cpu in CPUS:
        root = Path(f'/sys/devices/system/cpu/cpu{cpu}')
        cores.append((root / 'topology/core_id').read_text().strip())
        siblings.append((root / 'topology/thread_siblings_list').read_text().strip())
        caches.append((root / 'cache/index3/shared_cpu_list').read_text().strip())
    require(len(set(cores)) == 2 and len(set(caches)) == 1, 'p2 topology changed')
    ccx0_l3 = sorted({
        (Path(f'/sys/devices/system/cpu/cpu{c}/cache/index3/shared_cpu_list')).read_text().strip()
        for c in CCX0_CPUS
    })
    ccx1_l3 = sorted({
        (Path(f'/sys/devices/system/cpu/cpu{c}/cache/index3/shared_cpu_list')).read_text().strip()
        for c in ALL_HOST_CPUS if c not in CCX0_CPUS
    })
    require(ccx0_l3 == ['0-5'] and ccx1_l3 == ['6-11'],
            f'unexpected CCX/L3 topology: ccx0={ccx0_l3} ccx1={ccx1_l3}')
    result = dict(
        cpu_model='AMD Ryzen 5 PRO 4650U',
        cpus=CPUS,
        worker_cores_cpus=list(WORKER_CORES_CPUS),
        ccx0_cpus=list(CCX0_CPUS),
        cores=cores,
        siblings=siblings,
        l3_shared_lists=caches,
        ccx1_l3_shared_list=ccx1_l3[0],
        allowed_cpus=sorted(os.sched_getaffinity(0)),
        kernel=os.uname().release,
        clk_tck=os.sysconf('SC_CLK_TCK'),
    )
    for field, value in load_freeze(environment=False)['host_profile'].items():
        require(result[field] == value,
                f'host profile mismatch: {field}; no affinity/power tuning permitted')
    return result


def _load_frozen_base_guard():
    sys.path.insert(0, str(ROOT / 'tools/research'))
    spec = importlib.util.spec_from_file_location(
        '_g2_v2_d3_frozen_base_guard', ROOT / 'tools/research/run_paper_fullfan_check.py'
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_guard(baseline, *, phase='off'):
    """Construct a design-3 guard extending frozen CoolingGuard without modifying base source."""
    base_mod = _load_frozen_base_guard()
    parent = base_mod.CoolingGuard

    class G2Design3Guard(parent):
        def __init__(self, base_snap):
            super().__init__(base_snap)
            self.phase = phase
            self.noise = ContentionV3(phase=phase)
            self.noise.observe(base_snap['v3_cpu'])

        def check(self, s, owned_pid=None):
            reasons = [v for v in super().check(s, owned_pid)
                       if v != 'Reliable package temperature unavailable']
            reasons += amd_reasons(s, owned_pid)
            try:
                last_cap = self.noise.captures[-1]
                cur_cap = s['v3_cpu']
                if last_cap is not cur_cap and cur_cap['monotonic_s'] - last_cap['monotonic_s'] >= MIN_GAP_S:
                    reasons += self.noise.observe(cur_cap)
            except (ValueError, KeyError, TypeError) as exc:
                reasons.append(f'CPU telemetry invalid: {exc}')
            return reasons

    return G2Design3Guard(baseline)


def quiet_preflight(root, *, log_path, phase='off', timeout_s=180, snapshot_fn=host_snapshot_v3):
    deadline = time.monotonic() + min(180.0, timeout_s)
    with Path(log_path).open('x') as log:
        first = snapshot_fn(root)
        log.write(json.dumps(first) + '\n')
        log.flush()
        guard = make_guard(first, phase=phase)
        while True:
            s = snapshot_fn(root)
            log.write(json.dumps(s) + '\n')
            log.flush()
            reasons = guard.check(s)
            if reasons:
                # Only thermal start cooldown may wait; contention/invalidity never auto-retries.
                require(reasons == ['Tctl threshold'] and not amd_reasons(s, 1), ', '.join(reasons))
                guard.noise = ContentionV3(phase=phase)
                guard.noise.observe(s['v3_cpu'])
            elif guard.noise.ready:
                return s
            require(time.monotonic() < deadline, 'preflight quiet/cooling timeout')
            time.sleep(1.0)


def run_guarded_v3(spec, output, *, phase='off', snapshot_fn=host_snapshot_v3):
    """Run one owned command with frozen watchdog semantics + design-3 watchdog-aware telemetry."""
    base_mod = _load_frozen_base_guard()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    baseline = snapshot_fn(output)
    guard = make_guard(baseline, phase=phase)
    reasons = guard.check(baseline)
    if reasons:
        raise ValueError('Pre-command guard: ' + ', '.join(reasons))
    if base_mod.digest(spec['argv'][0]) != spec['binary_sha256']:
        raise ValueError('Executable digest mismatch')

    env = dict(os.environ)
    for k in ('OMP_PROC_BIND', 'OMP_PLACES', 'GOMP_CPU_AFFINITY'):
        env.pop(k, None)
    env.update(OMP_NUM_THREADS=str(spec.get('threads', 1)), MKL_NUM_THREADS='1',
               OMP_DYNAMIC='FALSE', LC_ALL='C')
    env.update(spec.get('extra_environment', {}))
    manifest = dict(
        spec,
        initial_host=baseline,
        timestamp_start=_utc(),
        wrapper_sha256=base_mod.digest(__file__),
        base_guard_sha256=base_mod.digest(base_mod.__file__),
        phase=phase,
        environment={k: env.get(k) for k in
                     ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_DYNAMIC',
                      'OMP_PROC_BIND', 'OMP_PLACES', 'GOMP_CPU_AFFINITY')},
    )
    (output / 'manifest.json').write_bytes(base_mod.canonical_bytes(manifest))
    import shlex
    (output / 'command.sh').write_text(shlex.join(spec['argv']) + '\n')

    start = time.monotonic()
    maxrss = 0
    samples = 0
    reason = None
    wd = None
    write_fd = None
    bootstrap = (
        'import ctypes,os,signal,sys; '
        'p=int(sys.argv[1]); '
        'r=ctypes.CDLL(None,use_errno=True).prctl(1,signal.SIGKILL,0,0,0); '
        'sys.exit(125) if r != 0 or os.getppid()!=p else None; '
        'os.execv(sys.argv[2],sys.argv[2:])'
    )
    with (output / 'stdout.log').open('w') as out, (output / 'stderr.log').open('w') as err:
        process = subprocess.Popen(
            [sys.executable, '-c', bootstrap, str(os.getpid()), *spec['argv']],
            stdout=out, stderr=err, env=env, start_new_session=True,
        )
        ticks = base_mod.start_ticks(process.pid)
        manifest.update(pid=process.pid, process_start_ticks=ticks)
        (output / 'manifest.json').write_bytes(base_mod.canonical_bytes(manifest))
        try:
            if ticks is None:
                raise ValueError('Owned process identity unavailable')
            read_fd, write_fd = os.pipe()
            wd = os.fork()
            if wd == 0:
                try:
                    base_mod.watchdog(read_fd, write_fd, process.pid, ticks, output / 'watchdog_failure.json')
                finally:
                    os._exit(0)
            os.close(read_fd)
            manifest['watchdog_pid'] = wd
            manifest['watchdog_start_ticks'] = base_mod.start_ticks(wd)
            (output / 'manifest.json').write_bytes(base_mod.canonical_bytes(manifest))
            with (output / 'host.jsonl').open('w') as log:
                deadline = time.monotonic()
                while process.poll() is None:
                    s = snapshot_fn(output, process.pid, watchdog_pid=wd)
                    s['sample_lateness_s'] = max(0.0, s['monotonic_s'] - deadline)
                    pp = Path('/sys/firmware/acpi/platform_profile')
                    s['platform_profile'] = pp.read_text().strip() if pp.exists() else None
                    log.write(json.dumps(s) + '\n')
                    log.flush()
                    samples += 1
                    for task in s['tasks']:
                        if task['tid'] == str(process.pid) and task['status']:
                            for line in task['status'].splitlines():
                                if line.startswith('VmHWM:'):
                                    maxrss = max(maxrss, int(line.split()[1]))
                    os.write(write_fd, b'.')
                    if os.waitpid(wd, os.WNOHANG)[0]:
                        wd = None
                        raise ValueError('Independent watchdog exited unexpectedly')
                    reasons = guard.check(s, process.pid)
                    if time.monotonic() - start >= spec.get('timeout_s', 180):
                        reasons.append('Owned command timeout')
                    if reasons:
                        reason = ', '.join(reasons)
                        base_mod.terminate_group(process.pid, ticks)
                        break
                    deadline += 1.0
                    while process.poll() is None and time.monotonic() < deadline:
                        time.sleep(min(0.1, max(0.0, deadline - time.monotonic())))
                process.wait()
        except BaseException as exc:
            reason = f'Monitor/interruption failure: {type(exc).__name__}: {exc}'
            base_mod.terminate_group(process.pid, ticks)
            process.wait()
        finally:
            if write_fd is not None:
                try:
                    os.write(write_fd, b'DONE')
                except BrokenPipeError:
                    pass
                os.close(write_fd)
            if wd:
                os.waitpid(wd, 0)
            manifest.update(
                timestamp_end=_utc(),
                wall_time_s=time.monotonic() - start,
                exit_code=process.returncode,
                guard_failure=reason,
                peak_rss_KiB=maxrss,
                host_samples=samples,
            )
            (output / 'manifest.json').write_bytes(base_mod.canonical_bytes(manifest))
    return manifest
