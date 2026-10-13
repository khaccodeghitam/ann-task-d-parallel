"""One paper-only paired protocol. Local evidence is authoritative; no index build."""
import csv
import json
import math
import os
from pathlib import Path
import random
import statistics
import time
from artifact_bundle import verify, unchanged
from paper_rebaseline import canonical_bytes, digest, parse_output, descriptive
from paper_portable_v2 import host_snapshot, seal, utc
from run_paper_fullfan_check import run


def schedule(seed=20261013, extension=True):
    rng=random.Random(seed);first=rng.choice([8,16]);rows=[]
    for b in range(1,7):
        pair=[first,24-first] if b%2 else [24-first,first]
        for t in pair:rows.append(dict(stage='core',block=b,T=t,W=32,L=100))
        rows.append(dict(stage='core_reference',block=b,T=1 if b%2 else 4,W=32,L=100))
    if extension:
        for rep in range(1,4):
            ls=[50,75,125,150];rng.shuffle(ls)
            rows.extend(dict(stage='extension_L',block=rep,T=8,W=32,L=l) for l in ls)
        for rep in range(1,4):
            ws=[16,64];rng.shuffle(ws)
            rows.extend(dict(stage='extension_W',block=rep,T=8,W=w,L=100) for w in ws)
    return [dict(sequence=i+1,**r) for i,r in enumerate(rows)]


def resolved(config):
    def expand(v):
        if isinstance(v,str):
            s=os.path.expandvars(v)
            if '${' in s:raise ValueError('Unset environment variable: '+v)
            return s
        return v
    return {k:expand(v) for k,v in config.items()}


def argv(c,row,binary=None,query=None,truth=None):
    return [str(binary or c['binary']),'uint8',str(Path(c['index_root'])/c.get('prefix','sift10m')),
            str(row['T']),str(row['W']),str(query or Path(c['data_root'])/'query.bbin'),
            str(truth or Path(c['data_root'])/'gt_10m.bin'),'10','l2','2','10',str(row['L'])]


def validate_output(directory,row):
    directory=Path(directory);m=json.loads((directory/'manifest.json').read_text())
    if m['exit_code'] or m['guard_failure']:raise ValueError('Owned process/guard failed')
    text=(directory/'stdout.log').read_text()+'\n'+(directory/'stderr.log').read_text()
    if 'Metadata: #pts = 10000, #dims = 128' not in text:
        raise ValueError('10K query completion contract not established')
    v=parse_output(text,'PAPER',row['L'],row['W'])
    if v['recall']<=0:raise ValueError('Zero recall')
    return v,m


def policy_state(s):return {k:s.get(k) for k in ('power','rapl','platform_profile')}


def environment_valid(directory):
    rows=[json.loads(x) for x in (Path(directory)/'host.jsonl').read_text().splitlines()]
    if not rows or any(not s.get('power') or not s.get('rapl') or s.get('platform_profile') is None for s in rows):
        raise ValueError('Environmental evidence incomplete')
    if any(policy_state(x)!=policy_state(rows[0]) for x in rows[1:]):
        raise ValueError('ENV_CONFOUNDED: policy/profile transition')
    return rows


def run_campaign(config,output):
    c=resolved(config);root=Path(output)
    if root.exists():raise FileExistsError('New campaign directory required; no resume/replacement')
    root.mkdir(parents=True)
    fingerprint=verify(c['manifest'],c['data_root'],c['index_root'],True)
    binary_sha=digest(c['binary'])
    if c.get('binary_sha256') and binary_sha!=c['binary_sha256']:raise ValueError('Binary digest mismatch')
    subject=Path(c['subject_repo']);import subprocess
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=subject,text=True).strip()
    tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=subject,text=True).strip()
    if subprocess.check_output(['git','status','--porcelain'],cwd=subject,text=True).strip():raise ValueError('Dirty subject')
    if tree!='23fbb256528c67454cd4348bc58dfee700dffa06':raise ValueError('Wrong portable source tree')
    if not Path(c['quality_binary']).is_file():raise ValueError('Separate quality probe required; use quality-build first')
    guard=host_snapshot(root)
    if any(v!='1' for v in guard['power'].values()) or not guard['power']:raise ValueError('Stable AC required')
    if max(v['value_C'] for v in guard['sensors'].values() if v['name']=='coretemp' and (v['label'] or '').startswith('Package'))>=85:
        raise ValueError('Startup package >=85C; no automatic retry')
    rows=schedule(c.get('seed',20261013),c.get('extension',True))
    plan=dict(protocol='PAPER_PAIRED_NATIVE_v1',created=utc(),config=c,source_commit=source,source_tree=tree,
              harness_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=Path(__file__).resolve().parents[2],text=True).strip(),binary_sha256=binary_sha,quality_binary_sha256=digest(c['quality_binary']),bundle=fingerprint,
              order=rows,pause_s=c.get('pause_s',5),between_block_s=c.get('between_block_s',15),
              bootstrap=dict(samples=20000,seed=20261013,CI=.90,unit='paired block',quantile='linear p*(n-1)'),
              monitor='rich 1Hz; same safety guard and watchdog in every stock run',
              acceptance='No outcome exclusions or retries. Process/error/header/recall/policy failures stop. Full post hash audit required. Independent same-library full-query quality arm per configuration; stock IDs are not directly exported.',
              optional_extension='Only after 18 core processes and six complete policy-stable pairs; L then W priority',
              initial_environment=guard,wrapper_sha256=digest(Path(__file__).with_name('run_paper_fullfan_check.py')),
              paired_code_sha256=digest(__file__))
    (root/'PLAN.json').write_bytes(canonical_bytes(plan));(root/'PLAN.sha256').write_text(digest(root/'PLAN.json')+'  PLAN.json\n')
    records=[];stop=None;checked={}
    def quality_check(row):
        from paper_native_v3 import quality_against_canonical
        key=(row['T'],row['W'],row['L'])
        if key in checked:return
        name=f"QUALITY_T{key[0]}_W{key[1]}_L{key[2]}";result=root/(name+'.csv')
        spec=dict(argv=argv(c,row,c['quality_binary']),threads=row['T'],binary_sha256=digest(c['quality_binary']),timeout_s=240,
                  extra_environment={'PAPER_QUALITY_OUTPUT':str(result)},purpose='correctness_only')
        run(spec,root/name);v,_=validate_output(root/name,row);environment_valid(root/name)
        b=Path(c['data_root']);quality=quality_against_canonical(result,b/'base_10m.bbin',b/'query.bbin',b/'gt_10m.bin')
        if quality['recall']<=0 or abs(quality['recall']-v['recall'])>.011:raise ValueError('Independent recall mismatch')
        checked[key]=quality
        (root/(name+'_validation.json')).write_bytes(canonical_bytes(quality))
    try:
        for row in rows:
            unchanged(fingerprint);runid=f"R{row['sequence']:02d}_T{row['T']}_W{row['W']}_L{row['L']}"
            record=dict(row,run_id=runid,status='INCOMPLETE');records.append(record)
            spec=dict(argv=argv(c,row),threads=row['T'],binary_sha256=binary_sha,timeout_s=c.get('timeout_s',240),
                      run_id=runid,source_commit=source,source_tree=tree,bundle_sha256=fingerprint['manifest_sha256'])
            m=run(spec,root/runid);metrics,m=validate_output(root/runid,row);env=environment_valid(root/runid)
            record.update(status='BENCHMARK_SUCCESS_PENDING_QUALITY',metrics=metrics,start=m['timestamp_start'],end=m['timestamp_end'],exit_code=m['exit_code'],process_wall_s=m['wall_time_s'],environment=policy_state(env[0]),stdout_sha256=digest(root/runid/'stdout.log'))
            # Paired comparisons never mix policies even when each run is internally stable.
            if row['stage']=='core':
                peers=[x for x in records if x['stage']=='core' and x['block']==row['block'] and 'environment'in x]
                if any(x['environment']!=record['environment'] for x in peers):raise ValueError('Paired block environment mismatch')
            if row['sequence']==18:
                for previous in records:quality_check(previous)
                for previous in records:
                    previous['status']='VALID';previous['quality_validation']=checked[(previous['T'],previous['W'],previous['L'])]
            (root/'progress.json').write_bytes(canonical_bytes(records))
            print(json.dumps(dict(progress=len(records),target=len(rows),run_id=runid,**metrics)),flush=True)
            if row!=rows[-1]:
                nextrow=rows[row['sequence']]
                time.sleep(c.get('between_block_s',15) if nextrow['block']!=row['block'] or nextrow['stage']!=row['stage'] else c.get('pause_s',5))
        # Extension-only correctness arm follows all extension timings.
        for row in rows:quality_check(row)
        for r in records:r['status']='VALID';r['quality_validation']=checked[(r['T'],r['W'],r['L'])]
    except BaseException as e:
        stop=f'{type(e).__name__}: {e}'
        if records and records[-1]['status']!='VALID':
            records[-1]['status']='INVALID';records[-1]['failure_reason']=stop
    finally:
        try:post=verify(c['manifest'],c['data_root'],c['index_root'],True)
        except Exception as e:post={'valid':False,'error':str(e)};stop=stop or 'Post-package audit failed'
        (root/'POST_AUDIT.json').write_bytes(canonical_bytes(post))
        (root/'RUNS.json').write_bytes(canonical_bytes(records))
        (root/'EXECUTION.json').write_bytes(canonical_bytes(dict(stop_reason=stop,post_audit_valid=post['valid'],valid_runs=sum(r['status']=='VALID' for r in records),attempted=len(records),planned=len(rows))))
        seal(root)
    if stop:raise ValueError(stop)
    return records


def percentile(values,p):
    values=sorted(values);x=p*(len(values)-1);i=int(x);return values[i]+(values[min(i+1,len(values)-1)]-values[i])*(x-i)


def paired_statistics(values,seed=20261013,samples=20000):
    if len(values)!=6:raise ValueError('Six complete pairs required')
    rng=random.Random(seed);medians=[statistics.median(rng.choices(values,k=6)) for _ in range(samples)]
    return dict(values=values,median=statistics.median(values),mean=statistics.mean(values),sample_SD=statistics.stdev(values),
                CI90=[percentile(medians,.05),percentile(medians,.95)],
                leave_one_block_out_medians=[statistics.median(values[:i]+values[i+1:]) for i in range(6)])


def summarize(root):
    root=Path(root);plan=json.loads((root/'PLAN.json').read_text());records=json.loads((root/'RUNS.json').read_text())
    if digest(root/'PLAN.json')!=(root/'PLAN.sha256').read_text().split()[0]:raise ValueError('Frozen plan changed')
    for line in (root/'SHA256SUMS').read_text().splitlines():
        h,p=line.split('  ',1)
        if digest(root/p)!=h:raise ValueError('Evidence checksum mismatch: '+p)
    if len(records)!=len(plan['order']):raise ValueError('Incomplete campaign; preserve partial evidence')
    for r,want in zip(records,plan['order']):
        if any(r[k]!=v for k,v in want.items()) or r['status']!='VALID':raise ValueError('Invalid order/status')
        metrics,_=validate_output(root/r['run_id'],r)
        if metrics!=r['metrics']:raise ValueError('Raw metrics disagree')
    groups={}
    for r in records:
        key=f"T{r['T']}_W{r['W']}_L{r['L']}";groups.setdefault(key,[]).append(r)
    agg={k:{metric:descriptive([r['metrics'][metric] for r in rs]) for metric in ['qps','mean_latency_us','p999_latency_us','recall','mean_ios']} for k,rs in groups.items()}
    deltas=[];logs=[];recall=[]
    for block in range(1,7):
        pair={r['T']:r for r in records if r['stage']=='core' and r['block']==block}
        if set(pair)!={8,16}:raise ValueError('Missing paired cell')
        a,b=pair[8]['metrics'],pair[16]['metrics'];deltas.append(100*(b['qps']/a['qps']-1));logs.append(math.log(b['qps']/a['qps']));recall.append(b['recall']-a['recall'])
    return dict(valid=True,groups=agg,paired_T16_vs_T8=paired_statistics(deltas),paired_log_ratio=paired_statistics(logs),paired_recall_pp=paired_statistics(recall),runs=records,protocol_sha256=digest(root/'PLAN.json'))
