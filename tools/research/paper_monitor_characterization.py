"""Four bounded stock runs: lite/rich/rich/lite; safety never disabled."""
import json
from pathlib import Path
import shutil
import time
import run_paper_fullfan_check as monitor
from paper_portable_v2 import read,utc,seal
from paper_rebaseline import canonical_bytes,digest,parse_output
from paper_paired_campaign import argv,resolved,environment_valid


def lite_snapshot(root,pid=None):
    start=time.monotonic();cpu=time.process_time()
    mem={k:int(v.split()[0])*1024 for line in Path('/proc/meminfo').read_text().splitlines() for k,v in [line.split(':',1)]}
    sensors={}
    for hw in Path('/sys/class/hwmon').glob('hwmon*'):
        for p in hw.glob('temp*_input'):
            v=read(p)
            if v and v.lstrip('-').isdigit():
                sensors[str(p)]=dict(value_C=int(v)/1000,name=read(hw/'name'),label=read(p.with_name(p.name.replace('_input','_label'))),critical_mC=read(p.with_name(p.name.replace('_input','_crit'))))
    ann=[]
    for p in Path('/proc').glob('[0-9]*'):
        comm=read(p/'comm')
        if comm in ('search_disk_ind','build_disk_inde','build_memory_in'):ann.append(dict(pid=int(p.name),comm=comm))
    return dict(timestamp=utc(),monotonic_s=start,mem_available=mem['MemAvailable'],swap_used=mem['SwapTotal']-mem['SwapFree'],
                free_disk=shutil.disk_usage(root).free,sensors=sensors,ann=ann,tasks=[],cpu={},sqpoll=[],
                power={str(p):read(p) for p in Path('/sys/class/power_supply').glob('*/online')},
                rapl={str(p):read(p) for p in Path('/sys/class/powercap').glob('intel-rapl*/**/constraint_*_power_limit_uw')},
                collection_wall_s=time.monotonic()-start,observer_cpu_s=time.process_time()-cpu)


def characterize(config,output):
    c=resolved(config);root=Path(output);root.mkdir(parents=True,exist_ok=False)
    plan=dict(protocol='PAPER_MONITOR_SCREEN_v1',order=['LITE','RICH','RICH','LITE'],T=8,W=32,L=100,
              pairs=[[0,1],[3,2]],pause_s=5,
              interpretation='Two paired effects only, descriptive; no precision/equivalence claim. 5% effect budget is half a prospective10% scaling effect, not inherited E0. Large/unstable effects => UNKNOWN. Main campaign remains uniformly rich and monitored.',
              lite='same1Hz thermal/AC/RAM/swap/disk/foreign-ANN safeguards and watchdog; omit per-thread/clocks/SQPOLL diagnostics',
              rich='unchanged full-fan snapshot collector',binary_sha256=digest(c['binary']),code_sha256=digest(__file__))
    (root/'PLAN.json').write_bytes(canonical_bytes(plan));(root/'PLAN.sha256').write_text(digest(root/'PLAN.json')+'  PLAN.json\n')
    records=[];original=monitor.host_snapshot
    try:
        for i,mode in enumerate(plan['order']):
            monitor.host_snapshot=lite_snapshot if mode=='LITE' else original
            d=root/f'{i+1}_{mode}';row=dict(T=8,W=32,L=100)
            m=monitor.run(dict(argv=argv(c,row),binary_sha256=plan['binary_sha256'],threads=8,timeout_s=240,monitor_mode=mode),d)
            if m['exit_code'] or m['guard_failure']:raise ValueError('Monitor screen process failed')
            environment_valid(d);metrics=parse_output((d/'stdout.log').read_text()+(d/'stderr.log').read_text(),'PAPER',100,32)
            records.append(dict(mode=mode,metrics=metrics))
            if i<3:time.sleep(5)
    finally:monitor.host_snapshot=original
    effects=[100*(records[b]['metrics']['qps']/records[a]['metrics']['qps']-1) for a,b in plan['pairs']]
    result=dict(records=records,rich_vs_lite_QPS_percent=effects,
                status='CHARACTERIZED_DESCRIPTIVE' if max(map(abs,effects))<=5 else 'UNKNOWN',
                limitation='n=2 paired effects; not proof of negligible observer effect')
    (root/'RESULT.json').write_bytes(canonical_bytes(result));seal(root);return result
