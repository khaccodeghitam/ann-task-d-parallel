#!/usr/bin/env python3
"""Bounded v2 execution helpers for the explicitly ported paper subject.

Reuses the existing harness collectors and version-specific passive parser.
No historical plan is edited; the CLI executes only an explicit command spec.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import time
from datetime import datetime, timezone
from paper_rebaseline import canonical_bytes, digest, parse_output
from run_ann_experiment import Telemetry, collector_availability, stop_process


def utc():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def host_snapshot(root, pid=None):
    start = time.monotonic()
    cpu_start = time.process_time()
    memory = {k: int(v.split()[0])*1024 for line in Path('/proc/meminfo').read_text().splitlines()
              for k, v in [line.split(':', 1)]}
    sensors = {}
    for h in Path('/sys/class/hwmon').glob('hwmon*'):
        for p in h.glob('temp*_input'):
            value = read(p)
            if value and value.lstrip('-').isdigit():
                sensors[str(p)] = dict(value_C=int(value)/1000, name=read(h/'name'),
                                      label=read(p.with_name(p.name.replace('_input','_label'))),
                                      critical_mC=read(p.with_name(p.name.replace('_input','_crit'))))
    power = {str(p): read(p) for p in Path('/sys/class/power_supply').glob('*/online')}
    rapl = {str(p): read(p) for p in Path('/sys/class/powercap').glob('intel-rapl*/**/constraint_*_power_limit_uw')}
    cpu = {str(p): read(p) for p in Path('/sys/devices/system/cpu').glob('cpu*/cpufreq/*')
           if p.name in ('scaling_cur_freq','scaling_max_freq','scaling_governor','energy_performance_preference')}
    tasks = []
    if pid:
        for t in Path(f'/proc/{pid}/task').glob('*'):
            status = read(t/'status')
            tasks.append(dict(tid=t.name, stat=read(t/'stat'), schedstat=read(t/'schedstat'),
                              status=status, comm=read(t/'comm')))
    # Narrow process identities; no command-line data or stacks of unrelated applications.
    ann = []; sqpoll = []
    for p in Path('/proc').glob('[0-9]*'):
        comm = read(p/'comm')
        if comm in ('search_disk_ind','build_disk_inde','build_memory_in'):
            ann.append(dict(pid=int(p.name), comm=comm, stat=read(p/'stat')))
        if comm and (comm.startswith('iou-sqp') or comm.startswith('iou-wrk')):
            sqpoll.append(dict(pid=int(p.name), comm=comm, stat=read(p/'stat'), status=read(p/'status')))
    return dict(timestamp=utc(), monotonic_s=start, mem_available=memory['MemAvailable'],
                swap_used=memory['SwapTotal']-memory['SwapFree'], free_disk=shutil.disk_usage(root).free,
                sensors=sensors, power=power, rapl=rapl, cpu=cpu, tasks=tasks, ann=ann,
                sqpoll=sqpoll, load=read('/proc/loadavg'),
                collection_wall_s=time.monotonic()-start, observer_cpu_s=time.process_time()-cpu_start)


class Guard:
    def __init__(self, baseline):
        self.baseline = baseline
        self.hot_since = None
        self.swap_since = None

    def check(self, s, owned_pid=None):
        reasons = []
        if s['mem_available'] <= 2**30: reasons.append('MemAvailable <=1GiB')
        if s['free_disk'] <= 20*2**30: reasons.append('disk free <=20GiB')
        if s['power'] != self.baseline['power']: reasons.append('AC online state changed')
        if s['rapl'] != self.baseline['rapl']: reasons.append('readable RAPL policy changed')
        if any(a['pid'] != owned_pid for a in s['ann']): reasons.append('foreign ANN process')
        hot = False
        for sensor in s['sensors'].values():
            v = sensor['value_C']; crit = sensor['critical_mC']
            if crit and v >= int(crit)/1000-2:
                reasons.append('sensor within 2C of readable critical trip')
            if sensor['name'] != 'coretemp': continue
            if sensor['label'] and 'Package' in sensor['label'] and v >= 98: hot = True
        now = s['monotonic_s']
        self.hot_since = (self.hot_since if self.hot_since is not None else now) if hot else None
        if self.hot_since is not None and now-self.hot_since >= 10: reasons.append('sustained thermal critical proximity')
        swap = s['swap_used'] > self.baseline['swap_used']+64*2**20
        self.swap_since = (self.swap_since if self.swap_since is not None else now) if swap else None
        if self.swap_since is not None and now-self.swap_since >= 10: reasons.append('sustained swap growth >64MiB')
        return reasons


def execute(spec, directory, baseline=None):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    baseline = baseline or host_snapshot(directory)
    guard = Guard(baseline)
    reasons = guard.check(baseline)
    if reasons: raise ValueError('Pre-command guard: '+', '.join(reasons))
    env = dict(os.environ)
    for k in ('OMP_PROC_BIND','OMP_PLACES','GOMP_CPU_AFFINITY'): env.pop(k, None)
    env.update(OMP_NUM_THREADS=str(spec.get('threads',8)), MKL_NUM_THREADS='8', OMP_DYNAMIC='FALSE', LC_ALL='C', S_TIME_FORMAT='ISO')
    env.update(spec.get('extra_environment', {}))
    manifest = dict(spec, timestamp_start=utc(), environment={k:env.get(k) for k in
                    ('OMP_NUM_THREADS','MKL_NUM_THREADS','OMP_DYNAMIC','OMP_PROC_BIND','OMP_PLACES','GOMP_CPU_AFFINITY')},
                    initial_host=baseline)
    (directory/'manifest.json').write_bytes(canonical_bytes(manifest))
    import shlex
    (directory/'command.sh').write_text(shlex.join(spec['argv'])+'\n')
    collectors = collector_availability('OFF', True)
    if any(x['status'] != 'available' for x in collectors.values()): raise ValueError('Required sysstat collector unavailable')
    tel = Telemetry(directory/'telemetry', collectors, 1)
    start = time.monotonic(); reason = None; maxrss = 0; samples = 0
    with (directory/'stdout.log').open('w') as out, (directory/'stderr.log').open('w') as err:
        process = subprocess.Popen(spec['argv'], stdout=out, stderr=err, env=env, start_new_session=True)
        manifest['pid'] = process.pid
        tel.start(process.pid)
        try:
            with (directory/'host.jsonl').open('w') as log:
                while process.poll() is None:
                    s = host_snapshot(directory, process.pid)
                    log.write(json.dumps(s)+'\n');log.flush();samples += 1
                    for t in s['tasks']:
                        if t['tid'] == str(process.pid) and t['status']:
                            for line in t['status'].splitlines():
                                if line.startswith('VmHWM:'): maxrss=max(maxrss,int(line.split()[1]))
                    reasons=guard.check(s,process.pid)
                    if reasons or time.monotonic()-start > spec.get('timeout_s',7200):
                        reason=', '.join(reasons) or 'command timeout';stop_process(process);break
                    # Interruptible polling avoids missing process termination for five seconds.
                    for _ in range(50):
                        if process.poll() is not None: break
                        time.sleep(.1)
                process.wait()
        except BaseException:
            stop_process(process);raise
        finally:
            tel.stop()
    manifest.update(timestamp_end=utc(), wall_time_s=time.monotonic()-start,
                    exit_code=process.returncode, guard_failure=reason,
                    peak_rss_KiB=maxrss, host_samples=samples, collectors=collectors)
    manifest['kernel_peak_direct_children_rss_KiB'] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    manifest['rss_note'] = 'VmHWM sampled; kernel direct-child peak includes collectors and earlier commands in this Python process'
    (directory/'manifest.json').write_bytes(canonical_bytes(manifest))
    failed_collectors=[k for k,v in collectors.items() if v['status']=='failed']
    if failed_collectors: reason = reason or 'collector failure: '+','.join(failed_collectors)
    if process.returncode or reason: raise ValueError('Command failed: '+str(reason or process.returncode))
    return manifest


def seal(directory):
    directory=Path(directory)
    paths=sorted(p for p in directory.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
    (directory/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(directory)}\n' for p in paths))


def validate_quality(path, query_count=10000, k=10, n=10000000):
    """Independently validate complete post-timer result export, not printed recall."""
    queries = {}
    with Path(path).open() as stream:
        for row in csv.DictReader(stream):
            q=int(row['query_id']); rank=int(row['rank']); node=int(row['node_id'])
            if not 0<=q<query_count or not 0<=rank<k or not 0<=node<n:
                raise ValueError('Result index out of range')
            if int(row['returned'])!=k:
                raise ValueError('Incomplete actual search return count')
            import math
            if any(not math.isfinite(float(row[x])) or float(row[x])<0
                   for x in ('distance','latency_us','io_count')):
                raise ValueError('Nonfinite/negative result or stats')
            ranks,nodes=queries.setdefault(q,(set(),set()))
            if rank in ranks or node in nodes: raise ValueError('Duplicate rank or result ID')
            ranks.add(rank);nodes.add(node)
    if len(queries)!=query_count or any(len(r)!=k for r,_ in queries.values()):
        raise ValueError('Missing query/rank rows')
    return dict(query_count=query_count,k=k,complete_returns=True,unique_valid_ids=True,
                finite_nonnegative_distances=True,rows=query_count*k)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();spec=json.loads(a.spec.read_text())
    try:
        result=execute(spec,a.output)
    finally:
        if a.output.exists(): seal(a.output)
    print(json.dumps({k:result[k] for k in ('exit_code','wall_time_s','peak_rss_KiB','guard_failure')}))


if __name__=='__main__': main()
