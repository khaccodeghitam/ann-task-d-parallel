#!/usr/bin/env python3
"""One owned command, 1-second thermal guard and independent heartbeat watchdog.

No fan/power/affinity writes. This does not edit earlier frozen protocols.
"""
import argparse
import ctypes
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import time

from paper_portable_v2 import host_snapshot, utc
from paper_rebaseline import canonical_bytes, digest


class CoolingGuard:
    def __init__(self, baseline):
        self.baseline = baseline
        self.hot_since = self.swap_since = None

    def check(self, s, owned_pid=None):
        reasons = []
        packages = [v['value_C'] for v in s['sensors'].values()
                    if v['name'] == 'coretemp' and (v['label'] or '').startswith('Package')]
        if not packages or any(not -10 <= v <= 120 for v in packages):
            reasons.append('Reliable package temperature unavailable')
        now = s['monotonic_s']
        if packages and max(packages) >= 99:
            reasons.append('Package temperature >=99C')
        hot = bool(packages) and max(packages) >= 97
        self.hot_since = (now if self.hot_since is None else self.hot_since) if hot else None
        if self.hot_since is not None and now - self.hot_since >= 10:
            reasons.append('Package temperature >=97C for >=10 seconds')
        for v in s['sensors'].values():
            if v['critical_mC'] and v['value_C'] >= int(v['critical_mC']) / 1000:
                reasons.append('Readable sensor reached critical trip')
        if not s['power'] or any(v != '1' for v in s['power'].values()):
            reasons.append('AC unavailable/offline')
        if s['power'] != self.baseline['power']:
            reasons.append('AC state changed')
        if s['mem_available'] <= 2**30: reasons.append('MemAvailable <=1GiB')
        if s['free_disk'] <= 20*2**30: reasons.append('Disk free <=20GiB')
        if any(a['pid'] != owned_pid for a in s['ann']): reasons.append('Foreign ANN process')
        swap = s['swap_used'] > self.baseline['swap_used'] + 64*2**20
        self.swap_since = (now if self.swap_since is None else self.swap_since) if swap else None
        if self.swap_since is not None and now-self.swap_since >= 10:
            reasons.append('Swap growth >64MiB for >=10 seconds')
        # RAPL policy transitions are evidence, never standalone construction stops.
        return reasons


def start_ticks(pid):
    try: return Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19]
    except (OSError, IndexError): return None


def terminate_group(pid, ticks, grace=10):
    if start_ticks(pid) != ticks: return
    try: os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError: return
    until = time.monotonic() + grace
    while time.monotonic() < until:
        try:
            stat = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
            if stat[0] == 'Z' or stat[19] != ticks: return
        except OSError: return
        time.sleep(.1)
    if start_ticks(pid) == ticks:
        try: os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError: pass


def watchdog(read_fd, write_fd, pid, ticks, log):
    os.close(write_fd)
    try:
        while True:
            ready, _, _ = select.select([read_fd], [], [], 6)
            data = os.read(read_fd, 1024) if ready else b''
            if b'DONE' in data: return
            if not data:
                Path(log).write_text(json.dumps({'timestamp': utc(), 'reason': 'monitor heartbeat lost',
                                                 'owned_pid': pid, 'start_ticks': ticks})+'\n')
                terminate_group(pid, ticks)
                return
    finally: os.close(read_fd)


def run(spec, output):
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    baseline = host_snapshot(output)
    guard = CoolingGuard(baseline)
    reasons = guard.check(baseline)
    if reasons: raise ValueError('Pre-command guard: '+', '.join(reasons))
    if digest(spec['argv'][0]) != spec['binary_sha256']:
        raise ValueError('Executable digest mismatch')
    env = dict(os.environ)
    for k in ('OMP_PROC_BIND', 'OMP_PLACES', 'GOMP_CPU_AFFINITY'): env.pop(k, None)
    env.update(OMP_NUM_THREADS=str(spec.get('threads', 8)), MKL_NUM_THREADS='8',
               OMP_DYNAMIC='FALSE', LC_ALL='C')
    env.update(spec.get('extra_environment', {}))
    manifest = dict(spec, initial_host=baseline, timestamp_start=utc(),
                    wrapper_sha256=digest(__file__), environment={k:env.get(k) for k in
                    ('OMP_NUM_THREADS','MKL_NUM_THREADS','OMP_DYNAMIC','OMP_PROC_BIND','OMP_PLACES','GOMP_CPU_AFFINITY')})
    (output/'manifest.json').write_bytes(canonical_bytes(manifest))
    import shlex
    (output/'command.sh').write_text(shlex.join(spec['argv'])+'\n')
    start = time.monotonic(); maxrss = samples = 0; reason = None; wd = None; write_fd = None
    # Bootstrap catches monitor death even in the launch-to-watchdog interval.
    bootstrap = ('import ctypes,os,signal,sys; '
                 'p=int(sys.argv[1]); '
                 'r=ctypes.CDLL(None,use_errno=True).prctl(1,signal.SIGKILL,0,0,0); '
                 'sys.exit(125) if r != 0 or os.getppid()!=p else None; '
                 'os.execv(sys.argv[2],sys.argv[2:])')
    with (output/'stdout.log').open('w') as out, (output/'stderr.log').open('w') as err:
        process = subprocess.Popen([sys.executable,'-c',bootstrap,str(os.getpid()),*spec['argv']],
                                   stdout=out,stderr=err,env=env,start_new_session=True)
        ticks = start_ticks(process.pid)
        manifest.update(pid=process.pid, process_start_ticks=ticks)
        (output/'manifest.json').write_bytes(canonical_bytes(manifest))
        try:
            if ticks is None: raise ValueError('Owned process identity unavailable')
            read_fd, write_fd = os.pipe()
            wd = os.fork()
            if wd == 0:
                try: watchdog(read_fd, write_fd, process.pid, ticks, output/'watchdog_failure.json')
                finally: os._exit(0)
            os.close(read_fd)
            with (output/'host.jsonl').open('w') as log:
                deadline = time.monotonic()
                while process.poll() is None:
                    s = host_snapshot(output, process.pid)
                    s['sample_lateness_s'] = max(0, s['monotonic_s']-deadline)
                    s['platform_profile'] = Path('/sys/firmware/acpi/platform_profile').read_text().strip() if Path('/sys/firmware/acpi/platform_profile').exists() else None
                    log.write(json.dumps(s)+'\n'); log.flush(); samples += 1
                    for task in s['tasks']:
                        if task['tid'] == str(process.pid) and task['status']:
                            for line in task['status'].splitlines():
                                if line.startswith('VmHWM:'): maxrss=max(maxrss,int(line.split()[1]))
                    os.write(write_fd,b'.')
                    if os.waitpid(wd, os.WNOHANG)[0]:
                        wd = None; raise ValueError('Independent watchdog exited unexpectedly')
                    reasons = guard.check(s, process.pid)
                    if time.monotonic()-start >= spec.get('timeout_s',7200): reasons.append('Owned command timeout')
                    if reasons:
                        reason = ', '.join(reasons); terminate_group(process.pid,ticks); break
                    deadline += 1
                    while process.poll() is None and time.monotonic() < deadline:
                        time.sleep(min(.1,max(0,deadline-time.monotonic())))
                process.wait()
        except BaseException as exc:
            reason = f'Monitor/interruption failure: {type(exc).__name__}: {exc}'
            terminate_group(process.pid,ticks); process.wait()
        finally:
            if write_fd is not None:
                try: os.write(write_fd,b'DONE')
                except BrokenPipeError: pass
                os.close(write_fd)
            if wd: os.waitpid(wd,0)
            manifest.update(timestamp_end=utc(),wall_time_s=time.monotonic()-start,
                            exit_code=process.returncode,guard_failure=reason,
                            peak_rss_KiB=maxrss,host_samples=samples)
            (output/'manifest.json').write_bytes(canonical_bytes(manifest))
    print(json.dumps({k:manifest[k] for k in ['exit_code','guard_failure','wall_time_s','peak_rss_KiB','host_samples']}))
    return manifest


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); result=run(json.loads(a.spec.read_text()),a.output)
    sys.exit(0 if result['exit_code']==0 and not result['guard_failure'] else 1)
