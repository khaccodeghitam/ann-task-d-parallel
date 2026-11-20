#!/usr/bin/env python3
"""Authorized 64-validation-query RR-only trace capture, native Ryzen guard.

No online scheduling changes. Output directory must contain a prelocked panel
and no prior run folders. Never overwrite or silently resume a failed study.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
EVIDENCE = REPO.parent/'artifact-evidence'
sys.path.insert(0,str(EVIDENCE/'p2-pivot-b1-a1-resume-20261119'))
sys.dont_write_bytecode = True
import resume


def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def write(p,obj):
    with p.open('x') as f:json.dump(obj,f,indent=2,sort_keys=True);f.write('\n')


def capture(root):
    assert Path('/proc/1/comm').read_text().strip() == 'systemd','native host required'
    resume.verify_hardware()
    original_snapshot = resume.guard.host_snapshot
    def snapshot(out,pid=None):
        s=original_snapshot(out,pid)
        for p in Path('/proc').glob('[0-9]*/comm'):
            if resume.guard_name(p) == 'task_da_p2_trac':
                s['ann'].append({'pid':int(p.parent.name),'comm':'task_da_p2_trace_eval'})
        return s
    resume.guard.host_snapshot=snapshot
    root=root.resolve()
    assert root.is_dir() and not (root/'frozen_capture.json').exists()
    lock=Path('/tmp/task-da-pivot-4650u.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    spec=json.loads((root/'preregistered.json').read_text())
    panel=root/'panel_64.ids'
    assert sha(panel)==spec['panel_sha256']
    ids=list(map(int,panel.read_text().split()));assert len(ids)==len(set(ids))==64
    val=EVIDENCE/'p1-full-validation-20261117T225717+0700/split/val_10k.ids'
    assert set(ids)<=set(map(int,val.read_text().split()))
    warm=EVIDENCE/'p2-exploratory-0990-20261118/pilot_r1/warmup_val_100.ids'
    manifest=json.loads((REPO/'docs/research/task-da/experiment_manifest_v3_reconciled.json').read_text())
    graphroot=REPO.parents[1]/'graph'
    old=REPO/'build-task-da/task_da_p2_eval'
    trace=REPO/'build-h3-screen/task_da_p2_trace_eval'
    plain=REPO/'build-h3-screen/task_da_p2_eval'
    assert sha(old)==resume.REL_SHA
    paths=[panel,warm,val,old,trace,plain,Path(__file__),REPO/'research/task_da/h3_overlap.py',
           REPO/'research/task_da/CMakeLists.txt',Path(resume.__file__),Path(resume.guard.__file__),
           *sorted((REPO/'research/task_da/search_common').glob('*.*'))]
    graphs=[g for g in manifest['graphs'] if g['arm']=='A3']
    for g in graphs:assert sha(graphroot/g['path'])==g['reported_sha256'];paths.append(graphroot/g['path'])
    for a in manifest['dataset']['artifacts'].values():
        assert sha(graphroot/a['path'])==a['reported_sha256'];paths.append(graphroot/a['path'])
    baseline=snapshot(root); reasons=resume.RyzenGuard(baseline).check(baseline)
    assert not reasons,reasons
    injected={**baseline,'sensors':{'inject':{'name':'k10temp','label':'Tctl','value_C':95.,'critical_mC':None}}}
    assert resume.RyzenGuard(baseline).check(injected,os.getpid())
    assert resume.RyzenGuard(baseline).check({**baseline,'sensors':{}},os.getpid())
    write(root/'frozen_capture.json',dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        diff_sha256=hashlib.sha256(subprocess.check_output(['git','diff','HEAD'])).hexdigest(),
        files_sha256={os.path.relpath(p,root):sha(p) for p in paths},host=baseline,
        compiler=subprocess.check_output(['c++','--version'],text=True),protocol=spec))
    # All four non-timing modes are frozen in advance. No adaptive repeats.
    quality=[]
    for rep,beam in [(1,970),(2,986),(3,966)]:
        g=next(x for x in graphs if x['replicate']==rep)
        rows=[]
        for label,binary,mode,enabled in [('frozen_off',old,'OFF',False),('new_off',trace,'OFF',False),
                                        ('new_on',trace,'ON',False),('trace_on',trace,'ON',True)]:
            s=snapshot(root);assert not resume.RyzenGuard(s).check(s)
            out=root/f'A3_r{rep}'/label
            argv=[str(binary),'pipnn',str(graphroot/g['path']),str(graphroot/'data/MSTuring_1M_v1/base.1M.fbin'),
                  str(graphroot/'data/MSTuring_1M_v1/query.public.100K.fbin'),'--entry','0','--k','10',
                  '--beams',str(beam),'--workers','2','--sync-interval','16','--merge-impl','flat',
                  '--visited-policy','barrier_all_evaled','--frontier-mode','incremental','--jobs','1',
                  '--cpu-list','0,2','--query-ids',str(panel),'--warmup-ids',str(warm),
                  '--mode',mode,'--out-dir',str(out)]+(['--round-trace'] if enabled else [])
            receipt=resume.guard.run(dict(argv=argv,binary_sha256=sha(binary),threads=1,timeout_s=90),out)
            assert receipt['exit_code']==0 and not receipt['guard_failure'] and receipt['host_samples']>0,receipt
            a=[json.loads(x) for x in (out/f'beam_{beam}_p2_{mode}.jsonl').read_text().splitlines()]
            assert [x['query_id'] for x in a]==ids and all(x['complete_top_k'] for x in a)
            summary=json.loads((out/'p2_eval_summary.json').read_text());assert summary['observed_cpus']==[0,2]
            rows.append(a)
            if len(rows)>1:assert resume.payload(a)==resume.payload(rows[0]),'ON/OFF output mismatch'
            if enabled:
                resume.invariant(a,rows[2])
                for q in a:
                    assert not q['trace_overflow']
                    assert len(q['rounds'])==q['counters']['sync_merge_count']
                    assert all(len(r['seeds'])<=32 for r in q['rounds'])
            assert sum(p.stat().st_size for p in out.parent.rglob('*') if p.is_file())<512*2**20
        quality.append(dict(graph=f'A3_r{rep}',queries=64,parity=True,counters_parity=True))
    write(root/'capture_checks.json',dict(graphs=quality,status='CAPTURE_PARITY_PASS'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path)
    a=p.parse_args();capture(a.output)
