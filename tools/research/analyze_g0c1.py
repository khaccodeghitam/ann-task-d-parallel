#!/usr/bin/env python3
"""Issue #16 sampler correctness plus unchanged native paired E0 protocol."""
import argparse
import json
from pathlib import Path
import sys
import analyze_e0b as paired
import analyze_e0c as native
from check_causal_trace import check_events
from trace_sampling import explicit_policy


def validate_smoke(directory, plan, threads):
    manifest=paired.read_json(directory/'manifest.json');summary=paired.read_json(directory/'summary.json')
    health=paired.read_json(directory/'trace_health.json')
    paired.verify_sums(directory)
    policy=explicit_policy(plan['detail_smoke']['qids'],plan['search']['query_count'])
    expected={**plan['search'],'threads':threads,'trace_mode':'DETAIL','causal_trace_enabled':True,
              'harness_git_commit':plan['harness_commit'],'harness_git_dirty':False,
              'subject_git_commit':plan['subjects']['instrumented']['commit'],'subject_git_dirty':False,
              'executable_sha256':plan['subjects']['instrumented']['binary_sha256'],
              'input_package_manifest_sha256':plan['input_package_sha256'],
              'index_package_manifest_sha256':plan['index_package_sha256']}
    for key,value in expected.items():
        if manifest.get(key)!=value:raise ValueError(f'Smoke configuration/provenance mismatch: {key}')
    for key,value in native.NATIVE_ENVIRONMENT.items():
        if key in manifest['environment'] and manifest['environment'][key]!=(str(threads) if key=='OMP_NUM_THREADS' else value):
            raise ValueError('Smoke native environment mismatch')
    if any(summary.get(k)!=v for k,v in [('benchmark_status','success'),('run_status','success'),('trace_valid',True)]):
        raise ValueError('Invalid smoke execution/trace status')
    if manifest['trace_config']['sample_policy']!=policy or health['sample_policy']!=policy:
        raise ValueError('Smoke sample policy mismatch')
    if health['requested_sample_qids']!=policy['qids'] or health['observed_sample_qids']!=policy['qids']:
        raise ValueError('Smoke exact membership mismatch')
    if not health['trace_valid'] or any(health.get(k,0) for k in plan['trace_health_zero_fields']):
        raise ValueError('Smoke trace health failure')
    if health['query_rows']!=plan['search']['query_count']:raise ValueError('Missing query counters')
    events=[json.loads(line) for line in (directory/'events.jsonl').read_text().splitlines()]
    checked=check_events(events,expected_qids=policy['qids'])
    if not checked['trace_valid']:raise ValueError('Smoke causal invariants failed')
    return {'run_id':manifest['run_id'],'mlflow_run_id':manifest['mlflow_run_id'],'threads':threads,
            'sample_qids':policy['qids'],'sampling_sha256':policy['sha256'],'events_written':health['events_written'],
            'trace_valid':True,'query_rows':health['query_rows'],'phase':health['sampled_query_phase']}


def analyze_campaign(campaign):
    result=paired.analyze_campaign(campaign,issue=16,record_analyzer=native.analyze_records)
    plan=paired.read_json(campaign/'PLAN.json');smokes=paired.read_json(campaign/'smoke_results.json')
    if [r['threads'] for r in smokes]!=[1,8,16]:raise ValueError('Sampler smoke completeness/order mismatch')
    validated=[validate_smoke(Path(r['run_directory']),plan,r['threads']) for r in smokes]
    for row in validated:
        manifest=paired.read_json(Path(next(r['run_directory'] for r in smokes if r['run_id']==row['run_id']))/'manifest.json')
        for kind in ('input','index'):
            audit=result['package_audits']
            if audit[f'pre_{kind}']['timestamp_end']>manifest['timestamp_start'] or audit[f'post_{kind}']['timestamp_start']<manifest['timestamp_end']:
                raise ValueError('Audits do not bracket DETAIL smoke')
    return {**result,'protocol':'g0c1-sampler-native-e0-v1','sampler_smokes':validated,
            'd6':'D6_INCONCLUSIVE','d1_observability':'NO','d4_selector_gate':'NOT TESTED','g0c2_executed':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--campaign',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    try:result=analyze_campaign(args.campaign)
    except (ValueError,KeyError,TypeError,OSError) as error:result={'campaign_valid':False,'classification':None,'error':str(error)}
    (args.output/'analysis.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result.get(k) for k in ('campaign_valid','classification','campaign_id','error')},indent=2))
    sys.exit(2 if not result['campaign_valid'] else 1 if result['classification']=='E0C_FAIL' else 0)
