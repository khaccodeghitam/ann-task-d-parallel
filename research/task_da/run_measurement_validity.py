"""Exactly three guarded OFF/aggregate-observer pairs, A3-R1 locked panel.

This one-study runner does not tune parameters or retry failed/slow processes.
Counters-ON and heavy-trace timing remain separately labelled sealed evidence.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
EVIDENCE = REPO.parent/'artifact-evidence'
sys.path.insert(0, str(EVIDENCE/'p2-pivot-b1-a1-resume-20261119'))
import resume


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def write(path, value):
    with path.open('x') as f:
        json.dump(value,f,indent=2,sort_keys=True);f.write('\n')


def rows(path):
    return [json.loads(s) for s in path.read_text().splitlines()]


def capture(root):
    assert __debug__
    assert Path('/proc/1/comm').read_text().strip()=='systemd', 'native host required'
    resume.verify_hardware()
    original_snapshot=resume.guard.host_snapshot
    def snapshot(output,pid=None):
        s=original_snapshot(output,pid)
        for path in Path('/proc').glob('[0-9]*/comm'):
            if resume.guard_name(path)=='task_da_phase_e':
                s['ann'].append(dict(pid=int(path.parent.name),comm='task_da_phase_eval'))
        return s
    resume.guard.host_snapshot=snapshot
    root=root.resolve();assert root.is_dir() and not (root/'preregistered.json').exists()
    lock=Path('/tmp/task-da-pivot-4650u.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    h3=EVIDENCE/'h3-overlap-screening-20261120'
    old=REPO/'build-task-da/task_da_p2_eval'
    observer=root/'observer/task_da_phase_eval'
    assert sha(old)==resume.REL_SHA
    assert (root/'observer_synthetic_tests.log').read_text().rstrip().endswith('OK')
    identity=json.loads((root/'observer/build_identity.json').read_text())
    assert sha(observer)==identity['binary_sha256']
    for name,h in identity['frozen_source_sha256'].items():
        assert sha(REPO/'research/task_da/search_common'/name)==h
    panel=root/'panel_64.ids';shutil.copyfile(h3/'panel_64.ids',panel)
    assert sha(panel)=='a19636b81c0b1197184cf1395f1decd50bd800993435d5e272c9805e5cb93545'
    ids=list(map(int,panel.read_text().split()));assert len(ids)==len(set(ids))==64
    warm=EVIDENCE/'p2-exploratory-0990-20261118/pilot_r1/warmup_val_100.ids'
    val=EVIDENCE/'p1-full-validation-20261117T225717+0700/split/val_10k.ids'
    assert set(ids)<=set(map(int,val.read_text().split()))
    manifest=json.loads((REPO/'docs/research/task-da/experiment_manifest_v3_reconciled.json').read_text())
    graphroot=REPO.parents[1]/'graph'
    graph=next(g for g in manifest['graphs'] if g['arm']=='A3' and g['replicate']==1)
    assert sha(graphroot/graph['path'])==graph['reported_sha256']
    for a in manifest['dataset']['artifacts'].values():
        assert sha(graphroot/a['path'])==a['reported_sha256']
    reference=rows(h3/'A3_r1/frozen_off/beam_970_p2_OFF.jsonl')
    reference_on=rows(h3/'A3_r1/new_on/beam_970_p2_ON.jsonl')
    trace=rows(h3/'A3_r1/trace_on/beam_970_p2_ON.jsonl')
    assert resume.payload(reference)==resume.payload(reference_on)==resume.payload(trace)
    resume.invariant(reference_on,trace)
    assert [r['query_id'] for r in reference]==ids
    # Independent exact distance and GT check, before using any new measurements.
    import numpy as np
    data=graphroot/'data/MSTuring_1M_v1'
    base=np.memmap(data/'base.1M.fbin',dtype='<f4',mode='r',offset=8,shape=(1000000,100))
    query=np.memmap(data/'query.public.100K.fbin',dtype='<f4',mode='r',offset=8,shape=(100000,100))
    gt=np.memmap(data/'groundtruth.public.100K.ibin',dtype='<u4',mode='r',offset=8,shape=(100000,100))
    recall=[];error=0.
    for r in reference:
        q=r['query_id'];recall.append(len(set(r['ids'])&set(map(int,gt[q,:10])))/10)
        for node,d in zip(r['ids'],r['squared_l2'],strict=True):
            delta=base[node].astype(np.float64)-query[q].astype(np.float64)
            error=max(error,abs(float(np.sum(delta*delta))-d))
    assert error<1e-12
    del base,query,gt
    pre=snapshot(root);assert not resume.RyzenGuard(pre).check(pre)
    injected={**pre,'sensors':{'inject':{'name':'k10temp','label':'Tctl','value_C':95.,'critical_mC':None}}}
    assert resume.RyzenGuard(pre).check(injected,os.getpid())
    assert resume.RyzenGuard(pre).check({**pre,'sensors':{}},os.getpid())
    schedule=[['frozen_off','phase_off'],['phase_off','frozen_off'],['frozen_off','phase_off']]
    write(root/'preregistered.json',dict(subject='A3-R1 p2 S16 beam970 flat+B1+A1 RR jobs1',
        panel_sha256=sha(panel),warmup_count=100,validation_queries=64,
        schedule=schedule,max_real_processes=6,no_retries=True,
        observer_drift_gate='95% paired log-ratio Student-t CI, df2, entirely within [-2%,+2%]',
        attribution_gate='no OFF phase transfer unless observer-drift gate passes; >=10% exclusive removable budget before mechanism work; novelty separate',
        sampling='perf probe denied at paranoid4; NOT_MEASURED; no further profiling',
        counters_and_heavy_trace='reuse sealed H3 raw only; descriptive, ordered and unreplicated, not contemporary causal overhead',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        git_diff_sha256=hashlib.sha256(subprocess.check_output(['git','diff','HEAD'])).hexdigest(),
        files_sha256={os.path.relpath(p,root):sha(p) for p in [old,observer,panel,warm,val,
            graphroot/graph['path'],Path(__file__),REPO/'research/task_da/build_phase_observer.py',
            Path(resume.__file__),Path(resume.guard.__file__)]},
        host=pre,correctness_precheck=dict(exact_distances=640,max_abs_error=error,recall64=sum(recall)/64,
            synthetic='PASS',archived_off_on_trace_payload='PASS')))
    checked=[]
    for i,pair in enumerate(schedule,1):
        for order,label in enumerate(pair,1):
            pre=snapshot(root);assert not resume.RyzenGuard(pre).check(pre), 'preflight stop; no retry'
            binary=old if label=='frozen_off' else observer
            out=root/'runs'/f'pair{i}_{order}_{label}'
            argv=[str(binary),'pipnn',str(graphroot/graph['path']),str(data/'base.1M.fbin'),
                str(data/'query.public.100K.fbin'),'--entry','0','--k','10','--beams','970',
                '--workers','2','--sync-interval','16','--merge-impl','flat',
                '--visited-policy','barrier_all_evaled','--frontier-mode','incremental','--jobs','1',
                '--cpu-list','0,2','--query-ids',str(panel),'--warmup-ids',str(warm),'--mode','OFF','--out-dir',str(out)]
            receipt=resume.guard.run(dict(argv=argv,binary_sha256=sha(binary),threads=1,timeout_s=90),out)
            assert receipt['exit_code']==0 and not receipt['guard_failure'] and receipt['host_samples']>0, receipt
            result=rows(out/'beam_970_p2_OFF.jsonl')
            summary=json.loads((out/'p2_eval_summary.json').read_text())
            assert summary['observed_cpus']==[0,2]
            assert [r['query_id'] for r in result]==ids and all(r['complete_top_k'] for r in result)
            assert resume.payload(result)==resume.payload(reference), 'STOP: output/ordering/distance parity'
            assert all('counters' not in r for r in result)
            if label=='phase_off':
                for r,old_on in zip(result,reference_on,strict=True):
                    p=r['phase_audit']
                    assert p['rounds']==old_on['counters']['sync_merge_count']
                    assert sum(p[k] for k in ('worker_phase_ns','gather_publish_ns','frontier_dispatch_ns'))<=r['latency_ns']
                    assert p['arrival_tail_ns']<=p['worker_phase_ns']
                    assert p['imbalance_ns']<=p['ideal_balance_ns']
            checked.append(dict(pair=i,order=order,label=label,output=str(out.relative_to(root)),
                                queries=64,payload_parity=True))
            write(root/f'checkpoint_{i}_{order}.json',dict(parity='PASS',result_sha256=sha(out/'beam_970_p2_OFF.jsonl')))
    assert len(checked)==6 and sha(old)==resume.REL_SHA
    write(root/'capture_checks.json',dict(status='PARITY_AND_CONSERVATION_PASS',processes=checked))
    print('All six processes passed correctness/parity; no statistical decision made by runner.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    capture(parser.parse_args().output)
