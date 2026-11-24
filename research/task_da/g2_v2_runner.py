"""G2 p2-only planner and separately owner-authorized sequential runner.

The plan command never opens ANN inputs. Nothing executes at import time.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import struct
import time

import numpy as np

from .g2_v2_contract import (BEAM, CPUS, FREEZE, GRAPHS, N, POLICIES, PROTOCOL, REVISION, ROOT, SCHEMA,
                             argv_for, authorize, load_freeze, number, quality_schedule,
                             require, require_default_loader, schedule, sha, validate_schema, write_new)
from . import g2_v2_analyzer as analysis


def emit(path, value, kind):
    validate_schema(value,kind)
    write_new(path,value)


def name(item):
    return f"b{item['block']}_{item['graph']}_{item['policy']}_{item['panel']}"


def plan(artifacts, phase, output):
    items = quality_schedule() if phase == 'quality' else schedule()
    return [dict(item, name=name(item), argv=argv_for(item,artifacts,Path(output)/name(item))) for item in items]


def verify_artifacts(freeze, artifacts):
    # Called only after explicit authorization; never by plan or preparation audit.
    require(bool(freeze['native_runtime_sha256']),'native runtime identity is required')
    for path,digest in freeze['native_runtime_sha256'].items():
        require(sha(path)==digest,f'native runtime changed: {path}')
    for key, digest in freeze['artifact_sha256'].items():
        require(sha(artifacts[key]) == digest, f'artifact mismatch: {key}')
    require(set(artifacts['graphs'])==set(GRAPHS),'graph cohort mismatch')
    for g,digest in freeze['graph_sha256'].items():
        require(sha(artifacts['graphs'][g])==digest,f'graph mismatch: {g}')
    for g, item in freeze['validation_baseline'].items():
        require(sha(Path(artifacts['validation_root'])/item['path'])==item['sha256'],f'validation baseline mismatch: {g}')


def ids(path):
    result = [int(v) for v in Path(path).read_text().split()]
    require(len(result)==N and len(set(result))==N and all(0<=v<100000 for v in result),'invalid pinned query list')
    return result


def process_result(item, output, artifacts, raw_guard):
    require(raw_guard['exit_code']==0 and raw_guard['guard_failure'] is None and raw_guard['host_samples']>=6,
            'failed/under-observed guarded process')
    summary_path = output/'p2_eval_summary.json'
    summary = json.loads(summary_path.read_text())
    require(summary['requested_cpus']==summary['observed_cpus']==CPUS and summary['workers']==2
            and summary['sync_interval']==16 and summary['jobs']==1 and summary['k']==10
            and summary['entry']==0 and summary['warmup_count']==100 and summary['query_count']==N
            and summary['mode']==item['mode'] and summary['merge_impl']=='flat','summary protocol mismatch')
    for field,key in [('graph_path',None),('base_path','base'),('query_path','queries')]:
        target=artifacts['graphs'][item['graph']] if key is None else artifacts[key]
        require(Path(summary[field]).resolve()==Path(target).resolve(),'summary input path mismatch')
    require(summary['graph_format']=='pipnn' and
            (summary['visited_policy'],summary['frontier_mode'])==POLICIES[item['policy']],
            'summary policy/format mismatch')
    require(len(summary['runs'])==1 and summary['runs'][0]['beam']==BEAM,'beam sweep forbidden')
    run = summary['runs'][0]
    result_path = output/f"beam_{BEAM}_p2_{item['mode']}.jsonl"
    rows = analysis.output_rows(result_path)
    digest,qids = analysis.output_digest(rows,mode=item['mode'],policy=item['policy'])
    require(qids==ids(artifacts['val' if item['panel']=='validation' else 'test']),'output query order mismatch')
    number(summary['vm_hwm_kib'],positive=True)
    latency = np.array([number(r['latency_ns'],positive=True)/1000 for r in rows])
    batch = number(run['batch_wall_ns'],positive=True)/1e9
    require(abs(run['qps_wall']-N/batch)<=1e-5*max(1,N/batch),'batch QPS mismatch')
    require(abs(run['latency_us']['mean']-float(latency.mean()))<=1e-5*max(1,float(latency.mean())), 'mean latency mismatch')
    for q in (.5,.95,.99):
        key=f'p{int(q*100)}'
        require(abs(run['latency_us'][key]-float(np.quantile(latency,q,method='linear')))<=1e-5*max(1,run['latency_us'][key]),
                'percentile definition mismatch')
    host = analysis.output_rows(output/'host.jsonl')
    require(len(host)==raw_guard['host_samples'],'host sample count mismatch')
    require(all(s['v2_cpu']['owned_pid']==raw_guard['pid'] and
                s['v2_cpu']['owned']['start']==int(raw_guard['process_start_ticks']) for s in host),
            'CPU samples belong to a different process')
    from .g2_v2_guard import cpu_metrics
    metrics = cpu_metrics([s['v2_cpu'] for s in host])
    record = dict(item,schema=SCHEMA,revision=REVISION,valid=True,observed_cpus=CPUS,beam=BEAM,query_count=N,
                mean_us=float(latency.mean()),p50_us=float(np.quantile(latency,.5,method='linear')),
                p95_us=float(np.quantile(latency,.95,method='linear')),p99_us=float(np.quantile(latency,.99,method='linear')),
                qps_wall=N/batch,rss_kib=summary['vm_hwm_kib'],rss_source='p2_eval_summary.vm_hwm_kib',
                output_digest=digest,raw_sha256={p.name:sha(p) for p in (result_path,summary_path,output/'manifest.json',output/'host.jsonl')},
                **metrics)
    validate_schema(record,'process')
    return record


def finish_quality(output, artifacts, freeze):
    validation, pairs, recall = {}, {}, []
    require(set(ids(artifacts['val'])).isdisjoint(ids(artifacts['test'])),'validation/test overlap')
    with Path(artifacts['gt']).open('rb') as stream:
        require(struct.unpack('<II',stream.read(8))==(100000,100),'GT header mismatch')
    gt = np.memmap(artifacts['gt'],dtype='<u4',offset=8,shape=(100000,100),mode='r')
    for g in GRAPHS:
        vi = dict(block=-1,graph=g,policy='opt',panel='validation',mode='ON')
        base = analysis.output_rows(Path(artifacts['validation_root'])/freeze['validation_baseline'][g]['path'])
        opt = analysis.output_rows(output/name(vi)/'beam_432_p2_ON.jsonl')
        validation[g] = analysis.pair_on(base,opt)
        items = [dict(block=-1,graph=g,policy=p,panel='test',mode='ON') for p in ('base','opt')]
        paths = [output/name(i)/'beam_432_p2_ON.jsonl' for i in items]
        b,c = [analysis.output_rows(path) for path in paths]
        check = analysis.pair_on(b,c)
        check['references'] = {p:dict(path=str(path.resolve()),sha256=sha(path)) for p,path in zip(('base','opt'),paths)}
        pairs[g]=check
        recall.append([len(set(row['ids'])&set(map(int,gt[row['query_id'],:10])))/10 for row in b])
    result = analysis.quality_gate(recall)
    result.update(schema=SCHEMA,protocol=PROTOCOL,revision=REVISION,parity=True,
                  duplicate_reduction=all(p['duplicate_l2_saved']>0 for p in pairs.values()),
                  graphs=pairs,validation=validation,freeze_sha256=sha(FREEZE))
    validate_schema(result,'quality')
    emit(output/'quality.json',result,'quality')
    return result


def check_reference(record, quality, output):
    g,p = record['graph'],record['policy']
    ref = quality['graphs'][g]['references'][p]
    require(sha(ref['path'])==ref['sha256'],'quality output changed')
    rows=analysis.output_rows(ref['path'])
    digest,qids=analysis.output_digest(rows,mode='ON',policy=p)
    require(digest==record['output_digest'] and digest==quality['graphs'][g]['output_digest'],'OFF/ON parity failed')
    require(len(qids)==N,'quality reference length mismatch')


def quality_context(path):
    path=Path(path);root=path.parent
    require(path.name=='quality.json' and not (root/'HOLD.json').exists(),'partial/HOLD quality phase')
    complete=json.loads((root/'complete.json').read_text())
    validate_schema(complete,'complete')
    require(complete['phase']=='quality' and complete['freeze_sha256']==sha(FREEZE)
            and complete['quality_sha256']==sha(path),'quality completion identity mismatch')
    wanted={name(item) for item in quality_schedule()}
    require(set(complete['receipts'])==set(complete['preflight_sha256'])==wanted,'quality phase incomplete')
    for item in wanted:
        require(sha(root/item/'metrics.json')==complete['receipts'][item],'quality process receipt changed')
        require(sha(root/(item+'_preflight.jsonl'))==complete['preflight_sha256'][item],'quality preflight changed')


def execute(phase, artifacts_path, approval_path, output, quality_path=None):
    started=time.monotonic()
    freeze = load_freeze()
    artifacts = json.loads(Path(artifacts_path).read_text())
    validate_schema(artifacts,'artifacts')
    approval = json.loads(Path(approval_path).read_text())
    scope = authorize(approval,sha(FREEZE),sha(artifacts_path),phase,output,
                      quality_digest=sha(quality_path) if quality_path else None)
    quality = None
    if phase=='off':
        require(quality_path is not None,'OFF requires approved quality report')
        quality_context(quality_path)
        quality=json.loads(Path(quality_path).read_text())
        validate_schema(quality,'quality')
        require(quality.get('freeze_sha256')==sha(FREEZE) and quality.get('A_pass') is True
                and quality.get('parity') is True,'quality A not PASS')
        require(scope!='OFF_AB' or quality.get('B_pass') is True,'quality B not PASS')
    from .g2_v2_guard import guard_module, host_contract, quiet_preflight
    host=host_contract()
    require_default_loader(os.environ)
    verify_artifacts(freeze,artifacts)
    output=Path(output).resolve()
    require(not output.exists(),'never overwrite/resume output')
    module=guard_module()
    tasks=plan(artifacts,phase,output)
    # Shared lock is held through all preflights, runs and postchecks.
    with Path('/tmp/task-da-pivot-4650u.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        output.mkdir(parents=True,exist_ok=False)
        if module.host_snapshot(output)['free_disk']<=25*2**30:
            emit(output/'HOLD.json',dict(schema=SCHEMA,reason='initial disk <=25GiB',receipts={}), 'hold')
            raise ValueError('initial disk must exceed 20GiB floor +5GiB output reserve')
        with (output/'artifacts.json').open('xb') as saved:
            saved.write(Path(artifacts_path).read_bytes())
        emit(output/'start.json',dict(schema=SCHEMA,protocol=PROTOCOL,revision=REVISION,phase=phase,
                  freeze_sha256=sha(FREEZE),artifacts=artifacts,artifacts_sha256=sha(artifacts_path),approval=approval,host=host,
                  environment={'OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','OMP_DYNAMIC':'FALSE'},
                  quality_path=str(Path(quality_path).resolve()) if quality_path else None,
                  quality_sha256=sha(quality_path) if quality_path else None,plan=tasks), 'start')
        receipts={}; preflights={};pairs={}; active=None
        try:
            for item in tasks:
                active=item['name']
                require(time.monotonic()-started<approval['quota_s'],'phase quota exhausted')
                load_freeze()
                preflight_path=output/(item['name']+'_preflight.jsonl')
                quiet_preflight(module,output,log_path=preflight_path,
                                timeout_s=approval['quota_s']-(time.monotonic()-started))
                preflights[item['name']]=sha(preflight_path)
                require(time.monotonic()-started<approval['quota_s'],'quota expired during preflight')
                directory=output/item['name']
                guard=module.run(dict(argv=item['argv'],binary_sha256=freeze['artifact_sha256']['binary'],threads=1,
                               timeout_s=min(180,approval['quota_s']-(time.monotonic()-started)),
                               extra_environment={'MKL_NUM_THREADS':'1'}),directory)
                require(time.monotonic()-started<=approval['quota_s'],'phase quota exhausted')
                record=process_result(item,directory,artifacts,guard)
                if phase=='off':
                    check_reference(record,quality,directory)
                emit(directory/'metrics.json',record,'process')
                receipts[item['name']]=sha(directory/'metrics.json')
                if phase=='off':
                    key=item['block'],item['graph']
                    pairs.setdefault(key,{})[item['policy']]=record
                    if set(pairs[key])=={'base','opt'}:
                        pair=pairs[key]
                        require(analysis.ram_pair(pair['base']['rss_kib'],pair['opt']['rss_kib'])['hard_pass'],
                                'RAM_HARD_HOLD: one paired process exceeded budget')
            verify_artifacts(freeze,artifacts)
            if phase=='quality':
                quality=finish_quality(output,artifacts,freeze)
            require(time.monotonic()-started<=approval['quota_s'],'phase quota exhausted during postchecks')
            emit(output/'complete.json',dict(schema=SCHEMA,phase=phase,freeze_sha256=sha(FREEZE),
                      receipts=receipts,preflight_sha256=preflights,quality_sha256=sha(output/'quality.json') if phase=='quality' else sha(quality_path),
                      elapsed_s=time.monotonic()-started),'complete')
        except BaseException as exc:
            emit(output/'HOLD.json',dict(schema=SCHEMA,reason=f'{type(exc).__name__}: {exc}',
                      receipts=receipts,elapsed_s=time.monotonic()-started,stopped_at=active),'hold')
            raise


def load_campaign(output):
    output=Path(output)
    require(not (output/'HOLD.json').exists(),'HOLD/partial campaign cannot produce GO')
    start=json.loads((output/'start.json').read_text());complete=json.loads((output/'complete.json').read_text())
    validate_schema(start,'start');validate_schema(complete,'complete')
    require(start['phase']==complete['phase']=='off' and complete['freeze_sha256']==sha(FREEZE),'wrong campaign/freeze')
    require(sha(start['quality_path'])==start['quality_sha256']==complete['quality_sha256'],'quality receipt changed')
    quality_context(start['quality_path'])
    quality=json.loads(Path(start['quality_path']).read_text())
    validate_schema(quality,'quality')
    require(quality['freeze_sha256']==sha(FREEZE),'quality freeze changed')
    require(sha(output/'artifacts.json')==start['artifacts_sha256'] and
            json.loads((output/'artifacts.json').read_text())==start['artifacts'],'artifact map changed')
    authorize(start['approval'],sha(FREEZE),start['artifacts_sha256'],'off',output,quality_digest=start['quality_sha256'])
    require(start['plan']==plan(start['artifacts'],'off',output),'execution order/plan changed')
    quality['B_authorized']=start['approval']['scope']=='OFF_AB'
    rows=[];latency=np.empty((12,6,2,N))
    wanted={name(i) for i in schedule()}
    require(set(complete['receipts'])==wanted,'missing/extra campaign receipt')
    require(set(complete['preflight_sha256'])==wanted,'missing preflight receipt')
    require({p.name for p in output.iterdir() if p.is_dir()}==wanted,'unexpected/retry process directory')
    previous_end=-1.
    for item in schedule():
        directory=output/name(item);path=directory/'metrics.json'
        require(sha(output/(name(item)+'_preflight.jsonl'))==complete['preflight_sha256'][name(item)],'preflight raw changed')
        require(sha(path)==complete['receipts'][name(item)],'process metrics changed')
        record=json.loads(path.read_text())
        validate_schema(record,'process')
        require(all(record[k]==item[k] for k in ('block','graph','policy','mode','panel')),'process label mismatch')
        for raw,digest in record['raw_sha256'].items(): require(sha(directory/raw)==digest,'raw receipt changed')
        guard=json.loads((directory/'manifest.json').read_text())
        host=analysis.output_rows(directory/'host.jsonl')
        from .g2_v2_guard import guard_module
        replay=guard_module().CoolingGuard(guard['initial_host'])
        require(all(not replay.check(sample,guard['pid']) for sample in host),'replayed safety/contention failed')
        require(guard['initial_host']['monotonic_s']>previous_end,'process ordering/overlap invalid')
        previous_end=host[-1]['monotonic_s']
        require(guard['argv']==argv_for(item,start['artifacts'],directory)
                and guard['binary_sha256']==load_freeze(environment=False)['artifact_sha256']['binary'],
                'guard command/binary mismatch')
        recomputed=process_result(record,directory,start['artifacts'],guard)
        require(recomputed==record,'process metrics inconsistent with raw')
        check_reference(record,quality,directory)
        raw=analysis.output_rows(directory/'beam_432_p2_OFF.jsonl')
        latency[item['block'],GRAPHS.index(item['graph']),('base','opt').index(item['policy'])]=[r['latency_ns']/1000 for r in raw]
        rows.append(record)
    return rows,latency,quality


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('plan','execute'))
    parser.add_argument('--phase',choices=('quality','off'),required=True)
    parser.add_argument('--artifacts',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--approval',type=Path)
    parser.add_argument('--quality',type=Path)
    parser.add_argument('--run-output',type=Path,help='exact proposed campaign directory for plan, never created by plan')
    args=parser.parse_args()
    if args.action=='plan':
        load_freeze(environment=False)
        require(args.run_output is not None,'plan requires exact proposed --run-output')
        artifacts = json.loads(args.artifacts.read_text())
        validate_schema(artifacts,'artifacts')
        emit(args.output,dict(schema=SCHEMA,protocol=PROTOCOL,revision=REVISION,phase=args.phase,freeze_sha256=sha(FREEZE),
                  artifacts_sha256=sha(args.artifacts),commands=plan(artifacts,args.phase,args.run_output.resolve())),'plan')
    else:
        require(args.approval is not None,'execution requires separate dated owner approval')
        execute(args.phase,args.artifacts,args.approval,args.output,args.quality)


if __name__ == '__main__': main()
