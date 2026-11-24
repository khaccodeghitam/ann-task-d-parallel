"""Read-only 1 Hz /proc telemetry plus the unchanged guarded-command watchdog."""
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import time

from .g2_v2_contract import CPUS, ROOT, load_freeze, require

BACKGROUND_CAPACITY = .01  # one third of the 3% minimum effect; not an empirical noise bound
WINDOW_S = 5.
MAX_GAP_S = 2.
KNOWN_CPU_JOBS = {'stress-ng', 'sysbench', 'task_da_p2_eval', 'task_da_p1_eval',
                  'search_disk_ind', 'build_disk_inde', 'build_memory_in'}


def parse_stat(text):
    left, rest = text.rsplit(')', 1)
    fields = rest.split()
    return dict(comm=left.split('(',1)[1], ticks=int(fields[11])+int(fields[12]), start=int(fields[19]))


def cpu_capture(pid=None):
    ticks = list(map(int, Path('/proc/stat').read_text().splitlines()[0].split()[1:9]))
    require(len(ticks) == 8, 'host CPU counters unavailable')
    own = parse_stat(Path(f'/proc/{pid}/stat').read_text()) if pid else dict(ticks=0,start=0)
    monitor = parse_stat(Path(f'/proc/{os.getpid()}/stat').read_text())
    processes = {}
    for path in Path('/proc').glob('[0-9]*/stat'):
        try: processes[path.parent.name] = parse_stat(path.read_text())
        except (OSError, ValueError, IndexError): continue  # exited/unreadable PID; host aggregate still covers CPU
    return dict(monotonic_s=time.monotonic(), hz=os.sysconf('SC_CLK_TCK'),
                host_busy_ticks=sum(ticks)-ticks[3]-ticks[4], owned=own, monitor=monitor,
                owned_pid=pid, monitor_pid=os.getpid(), processes=processes)


def interval(before, after):
    dt = after['monotonic_s']-before['monotonic_s']
    require(.5 <= dt <= MAX_GAP_S and before['hz'] == after['hz'] > 0, 'CPU cadence/gap invalid')
    hz = after['hz']
    if before['owned_pid'] and after['owned_pid']:
        require(before['owned_pid']==after['owned_pid'] and before['owned']['start'] == after['owned']['start'],
                'owned PID identity changed')
    deltas = [after['host_busy_ticks']-before['host_busy_ticks'],
              after['owned']['ticks']-before['owned']['ticks'],
              after['monitor']['ticks']-before['monitor']['ticks']]
    require(all(x >= 0 for x in deltas), 'CPU counter regressed')
    busy, owned, monitor = [v/hz for v in deltas]
    foreign = max(0.,busy-owned-monitor)
    top = []
    for pid, p in after['processes'].items():
        prev = before['processes'].get(pid)
        if pid in (str(after['owned_pid']),str(after['monitor_pid'])) or not prev or prev['start'] != p['start']:
            continue
        delta = p['ticks']-prev['ticks']
        if delta > 0: top.append(dict(pid=int(pid),comm=p['comm'],cpu_seconds=delta/hz))
    return dict(wall_s=dt, owned_cpu_s=owned, monitor_cpu_s=monitor, foreign_busy_s=foreign,
                competing_processes=sorted(top,key=lambda p:p['cpu_seconds'],reverse=True)[:10])


class Contention:
    def __init__(self):
        self.last = None
        self.intervals = []

    def observe(self, value):
        reasons = []
        for pid, p in value['processes'].items():
            if int(pid) != value['owned_pid'] and p['comm'] in KNOWN_CPU_JOBS:
                reasons.append('foreign named CPU/ANN job')
        if self.last is not None:
            tick = interval(self.last,value)
            self.intervals.append(tick)
            # Latest >=5-second window; no outcome-dependent baseline adjustment.
            window, wall = [], 0.
            for item in reversed(self.intervals):
                window.append(item); wall += item['wall_s']
                if wall >= WINDOW_S: break
            if wall >= WINDOW_S:
                fraction = sum(x['foreign_busy_s'] for x in window)/(wall*len(CPUS))
                tick['foreign_capacity_fraction'] = fraction
                if fraction > BACKGROUND_CAPACITY:
                    reasons.append('foreign CPU >1% of p2 capacity over >=5 seconds')
        self.last = value
        return reasons

    @property
    def ready(self):
        return sum(x['wall_s'] for x in self.intervals) >= WINDOW_S


def cpu_metrics(captures):
    require(len(captures) >= 2, 'CPU samples missing')
    total_cpu = total_wall = 0.
    for before, after in zip(captures,captures[1:]):
        d = interval(before,after)
        total_cpu += d['owned_cpu_s']; total_wall += d['wall_s']
    require(total_wall >= WINDOW_S and total_cpu > 0, 'CPU observation window too short/empty')
    return dict(cpu_seconds=total_cpu, wall_seconds=total_wall,
                cpu_percent=100*total_cpu/total_wall, cpu_capacity_percent=100*total_cpu/(2*total_wall),
                cpu_window='first_to_last_alive_proc_stat_sample_including_load_warmup_output')


def amd_reasons(snapshot, owned_pid=None):
    temps = [v['value_C'] for v in snapshot['sensors'].values() if v['name']=='k10temp' and v['label']=='Tctl']
    if len(temps)!=1 or type(temps[0]) not in (float,int) or not math.isfinite(temps[0]) or not 0<temps[0]<=120:
        return ['valid unique Tctl missing']
    return ['Tctl threshold'] if temps[0] >= (95 if owned_pid is not None else 85) else []


def host_contract():
    require('AMD Ryzen 5 PRO 4650U' in Path('/proc/cpuinfo').read_text(), 'only Ryzen 4650U is authorized')
    require(set(CPUS) <= os.sched_getaffinity(0), 'worker CPUs unavailable')
    cores, siblings, caches = [], [], []
    for cpu in CPUS:
        root = Path(f'/sys/devices/system/cpu/cpu{cpu}')
        cores.append((root/'topology/core_id').read_text().strip())
        siblings.append((root/'topology/thread_siblings_list').read_text().strip())
        caches.append((root/'cache/index3/shared_cpu_list').read_text().strip())
    require(len(set(cores))==2 and len(set(caches))==1, 'p2 topology changed')
    result = dict(cpu_model='AMD Ryzen 5 PRO 4650U', cpus=CPUS, cores=cores, siblings=siblings,
                l3_shared_lists=caches, allowed_cpus=sorted(os.sched_getaffinity(0)),
                kernel=os.uname().release, clk_tck=os.sysconf('SC_CLK_TCK'))
    for field,value in load_freeze(environment=False)['host_profile'].items():
        require(result[field]==value,f'host profile mismatch: {field}; no affinity/power tuning permitted')
    return result


def guard_module():
    """Load frozen base guard; extend its checks in this process, never edit its source."""
    sys.path.insert(0,str(ROOT/'tools/research'))
    spec = importlib.util.spec_from_file_location('_g2_v2_frozen_guard',ROOT/'tools/research/run_paper_fullfan_check.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    parent, capture = module.CoolingGuard, module.host_snapshot

    def snapshot(root,pid=None):
        result = capture(root,pid)
        result['v2_cpu'] = cpu_capture(pid)
        return result

    class G2Guard(parent):
        def __init__(self,baseline):
            super().__init__(baseline)
            self.noise = Contention()
            self.noise.observe(baseline['v2_cpu'])

        def check(self,s,owned_pid=None):
            reasons = [v for v in super().check(s,owned_pid) if v!='Reliable package temperature unavailable']
            reasons += amd_reasons(s,owned_pid)
            try:
                # run() checks the same baseline once after construction.
                if (self.noise.last is not s['v2_cpu'] and
                        s['v2_cpu']['monotonic_s']-self.noise.last['monotonic_s'] >= .5):
                    reasons += self.noise.observe(s['v2_cpu'])
            except (ValueError,KeyError,TypeError): reasons.append('CPU telemetry invalid')
            return reasons

    module.CoolingGuard, module.host_snapshot = G2Guard, snapshot
    return module


def quiet_preflight(module,root,*,log_path,timeout_s=180):
    deadline = time.monotonic()+min(180,timeout_s)
    with Path(log_path).open('x') as log:
        first = module.host_snapshot(root)
        log.write(json.dumps(first)+'\n');log.flush()
        # Resource baseline stays fixed through cooldown/quiet observation.
        check = module.CoolingGuard(first)
        while True:
            s = module.host_snapshot(root)
            log.write(json.dumps(s)+'\n');log.flush()
            reasons = check.check(s)
            if reasons:
                # Only thermal start cooldown may wait; contention/invalidity does not auto-retry.
                require(reasons == ['Tctl threshold'] and not amd_reasons(s,1), ', '.join(reasons))
                check.noise = Contention()
                check.noise.observe(s['v2_cpu'])
            elif check.noise.ready:
                return s
            require(time.monotonic()<deadline,'preflight quiet/cooling timeout')
            time.sleep(1)
