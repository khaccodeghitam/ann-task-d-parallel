#!/usr/bin/env python3
"""Execute exactly one explicitly frozen v3 stock suite; no retries or resume."""
import argparse
import json
from pathlib import Path
import time
import traceback
import subprocess
from paper_rebaseline import canonical_bytes, digest, parse_output, search_argv
from paper_portable_v2 import host_snapshot, seal, utc
from paper_native_v3 import execute, block_validity, check_diagnostics, verify_native_package
from package_manifest import load_verified
from run_ann_experiment import telemetry_rows


def telemetry(directory, identity):
    normalized=[];coverage={}
    for name in ('mpstat','pidstat','iostat'):
        path=directory/'telemetry'/f'{name}.log'
        if not path.exists():raise ValueError('Required collector log missing')
        rows=list(telemetry_rows(path.read_text(errors='replace'),name,identity))
        if not rows:raise ValueError('Required telemetry has no parsed samples: '+name)
        normalized.extend(rows)
        coverage[name]=dict(metric_rows=len(rows),sample_labels=len({r['sample_time_local'] for r in rows}),
                            scope='whole process; load/warmup/search/teardown mixed')
    (directory/'system_metrics.json').write_bytes(canonical_bytes(normalized))
    return coverage


def validate_plan(plan):
    if plan.get('protocol')!='PAPER_NATIVE_V3_STOCK_v1' or plan.get('execution_ready') is not True:
        raise ValueError('Not an execution-ready v3 protocol')
    from paper_rebaseline import run_order
    if plan['order']!=run_order():raise ValueError('Exact predeclared 66-case order mismatch')
    commits={'PAPER':'c4cd32c6816c063f56ecc64f9d7b63c909202cab','MODERN':'b9ec4ba86ff5d70bec277984777197f28dc2cf42'}
    for version,subject in plan['subjects'].items():
        if subject['commit']!=commits[version]:raise ValueError('Pinned subject mismatch')
        if digest(subject['binary'])!=subject['binary_sha256']:raise ValueError('Binary mismatch')
        repo=subject['source_repo']
        actual=subprocess.check_output(['git','-C',repo,'rev-parse','HEAD','HEAD^{tree}'],text=True).splitlines()
        if actual!=[subject['commit'],subject['tree']] or subprocess.check_output(['git','-C',repo,'status','--porcelain'],text=True):
            raise ValueError('Source identity/cleanliness mismatch')
    inp,sha=load_verified(plan['input_manifest'],'input')
    if sha!=plan['input_sha256']:raise ValueError('Input package mismatch')
    modern,sha=load_verified(plan['subjects']['MODERN']['index_manifest'],'index')
    if sha!=plan['subjects']['MODERN']['index_sha256']:raise ValueError('Modern index mismatch')
    native=verify_native_package(plan['subjects']['PAPER']['index_manifest'])
    if digest(plan['subjects']['PAPER']['index_manifest'])!=plan['subjects']['PAPER']['index_sha256']:
        raise ValueError('Paper index mismatch')
    for file,sha in plan['wrapper_fingerprints'].items():
        if digest(file)!=sha:raise ValueError('Execution helper changed after plan freeze')
    expected={'input':plan['input_sha256'],'paper':plan['subjects']['PAPER']['index_sha256'],'modern':plan['subjects']['MODERN']['index_sha256']}
    for name,sha in expected.items():
        audit=json.loads(Path(plan['pre_audits'][name]).read_text())
        if audit['exit_code']!=0 or audit['manifest_sha256']!=sha or '--full-components' not in audit['argv']:
            raise ValueError('Required full pre-audit failed/missing: '+name)
    for version,validation in plan['quality_validation'].items():
        if version not in commits:raise ValueError('Unknown quality subject')
        value=json.loads(Path(validation['path']).read_text())
        if digest(validation['path'])!=validation['sha256'] or value.get('query_count')!=10000 or value.get('exact_squared_L2_checked')!=100000 or value.get('validation_pass') is not True:
            raise ValueError('Full-corpus quality validation not established')
    if set(plan['quality_validation'])!=set(commits):raise ValueError('Both subjects require quality validation')
    return True


def run(root):
    root=Path(root);plan_path=root/'PLAN.json';plan=json.loads(plan_path.read_text())
    if (root/'PLAN.sha256').read_text().split()!=[digest(plan_path),'PLAN.json']:
        raise ValueError('Frozen plan digest mismatch')
    if (root/'attempts.json').exists():raise FileExistsError('No automatic campaign resume/retry')
    validate_plan(plan)
    records=[];blocks={};start=time.monotonic();stop=None
    (root/'runs').mkdir()
    for case in plan['order']:
        if time.monotonic()-start>plan['suite_timeout_s']:
            stop='Prospective suite wall-time cap';break
        if case['stage']!='primary':
            good=sum(v['status']=='COMPARABLE' for v in blocks.values())
            if len([r for r in records if r['stage']=='primary'])!=36 or good<plan['secondary_min_comparable_blocks']:
                stop='Secondary gate: primary completeness/comparable-block minimum not met';break
        subject=plan['subjects'][case['version']]
        run_id=f"{case['sequence']:02d}_{case['stage']}_B{case['block']:02d}_{case['cell']}"
        directory=root/'runs'/run_id
        spec=dict(case,run_id=run_id,argv=search_argv(subject['binary'],subject['prefix'],plan['query'],plan['truth'],case,subject['mem_L']),
                  threads=case['threads'],timeout_s=plan['per_run_timeout_s'],label='stock_headline',
                  subject_commit=subject['commit'],subject_tree=subject['tree'],binary_sha256=subject['binary_sha256'],
                  index_package_sha256=subject['index_sha256'],input_package_sha256=plan['input_sha256'],
                  benchmark_profile=subject['profile'],plan_sha256=digest(plan_path))
        record=dict(case,run_id=run_id,status='incomplete',evidence=str(directory),**{k:spec[k] for k in
                    ('subject_commit','subject_tree','binary_sha256','index_package_sha256','input_package_sha256','benchmark_profile')})
        records.append(record);(root/'attempts.json').write_bytes(canonical_bytes(records))
        try:
            validate_plan(plan)
            before=host_snapshot(root)
            with (root/'progress.jsonl').open('a') as stream:stream.write(json.dumps(dict(event='RUN_START',timestamp=utc(),run_id=run_id))+'\n')
            manifest=execute(spec,directory)
            output=(directory/'stdout.log').read_text(errors='replace')+'\n'+(directory/'stderr.log').read_text(errors='replace')
            check_diagnostics(output)
            metrics=parse_output(output,case['version'],case['l_search'],case['wcap'])
            if metrics['recall']<plan['minimum_primary_recall_percent'] and case['stage']=='primary':
                raise ValueError('Predeclared primary recall floor failed')
            if metrics['recall']==0:raise ValueError('Zero recall invalidates every search')
            coverage=telemetry(directory,run_id)
            after=host_snapshot(root)
            (directory/'boundary_hosts.json').write_bytes(canonical_bytes(dict(before=before,after=after)))
            samples=[before,manifest['initial_host']]+[json.loads(line) for line in (directory/'host.jsonl').read_text().splitlines()]+[after]
            record.update(status='completed_quality_valid',metrics=metrics,exit_code=manifest['exit_code'],wall_time_s=manifest['wall_time_s'],
                          telemetry_coverage=coverage,host_samples=len(samples),environment=block_validity(samples))
            (directory/'summary.json').write_bytes(canonical_bytes(record))
            # Seal after adding independently parsed results and telemetry.
            seal(directory)
            record['checksum_manifest_sha256']=digest(directory/'SHA256SUMS')
            if case['stage']=='primary':
                key=str(case['block']);block=blocks.setdefault(key,dict(samples=[],runs=[]))
                block['samples'].extend(samples);block['runs'].append(run_id)
                if len(block['runs'])==6:
                    verdict=block_validity(block['samples']);blocks[key]=dict(**verdict,runs=block['runs'])
                    (root/'blocks.json').write_bytes(canonical_bytes({k:{x:y for x,y in b.items() if x!='samples'} for k,b in blocks.items()}))
            with (root/'progress.jsonl').open('a') as stream:stream.write(json.dumps(dict(event='RUN_END',timestamp=utc(),run_id=run_id,metrics=metrics))+'\n')
            print(json.dumps(dict(run_id=run_id,**metrics)),flush=True)
        except BaseException as error:
            record.update(status='invalid_or_interrupted',reason=str(error))
            (root/'failure.txt').write_text(traceback.format_exc())
            if directory.exists():seal(directory)
            stop=str(error)
            print(json.dumps(dict(stopped=stop,run_id=run_id)),flush=True)
        finally:
            (root/'attempts.json').write_bytes(canonical_bytes(records))
        if stop:break
        if case['sequence']!=len(plan['order']):
            next_case=plan['order'][case['sequence']]
            pause=plan['between_block_pause_s'] if (case['stage'],case['block'])!=(next_case['stage'],next_case['block']) else plan['within_block_pause_s']
            # Gap observations belong to the ending block unless the block is complete.
            gap_start=host_snapshot(root);time.sleep(pause);gap_end=host_snapshot(root)
            with (root/'gaps.jsonl').open('a') as stream:
                stream.write(json.dumps(dict(after=run_id,pause_s=pause,start=gap_start,end=gap_end))+'\n')
            if case['stage']=='primary' and case['sequence']%6:
                blocks[str(case['block'])]['samples'].extend([gap_start,gap_end])
    (root/'EXECUTION.json').write_bytes(canonical_bytes(dict(stop_reason=stop,completed=len([r for r in records if r['status']=='completed_quality_valid']),
                                              attempted=len(records),not_run=len(plan['order'])-len(records),wall_time_s=time.monotonic()-start)))
    return records


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True)
    run(p.parse_args().evidence)
