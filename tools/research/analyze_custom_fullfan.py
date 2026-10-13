"""Verify finalized Custom campaign and regenerate run/block statistics offline.

No performance decision thresholds beyond the frozen execution gates are added.
"""
import argparse
import csv
import json
import math
from pathlib import Path

from analyze_issue29 import check_seal
from artifact_bundle import verify
from paper_native_v3 import quality_against_canonical
from paper_paired_campaign import argv, validate_output, policy_state, paired_statistics
from paper_rebaseline import digest, descriptive


STOCK='5f5fa8d99cc83b523c71b7025e5f0b9aa61f45d42816804ed6d88755ebaa310b'
METRICS=('qps','mean_latency_us','p999_latency_us','recall','mean_ios')


def verify_environment(rows,initial):
    if not rows:raise ValueError('Missing host observations')
    if initial.get('platform_profile')!='custom':raise ValueError('Not Custom campaign')
    for s in rows:
        if policy_state(s)!=policy_state(initial):raise ValueError('Policy/profile mismatch')
        package=[x['value_C'] for x in s['sensors'].values() if x['name']=='coretemp' and (x['label'] or '').startswith('Package')]
        if not package or max(package)>=99:raise ValueError('Missing/unsafe temperature evidence')
        first_package=[v['value_C'] for v in rows[0]['sensors'].values() if v['name']=='coretemp' and (v['label'] or '').startswith('Package')]
        if not first_package or first_package[0]>=85:raise ValueError('Startup temperature gate failed')
        if not s.get('power') or any(v!='1' for v in s['power'].values()):raise ValueError('AC failed')
    # MMIO aliases must refer to exactly one positively observed register per limit.
    identities=initial.get('mmio_identity',{})
    for i,target in [(0,60),(1,90)]:
        keys=[k for k in initial['rapl'] if 'intel-rapl-mmio' in k and k.endswith(f'/constraint_{i}_power_limit_uw')]
        if not keys or any(not identities.get(k) for k in keys):raise ValueError('MMIO identity missing')
        if len({json.dumps(identities[k],sort_keys=True) for k in keys})!=1:raise ValueError('Ambiguous MMIO identities')
        if any(abs(int(initial['rapl'][k])/1e6-target)>1 for k in keys):raise ValueError('Wrong MMIO limit')


def command(root,name,row,binary,initial,c):
    d=root/name;m=json.loads((d/'manifest.json').read_text())
    if m['argv']!=argv(c,row,binary):raise ValueError('Command configuration mismatch: '+name)
    if digest(binary)!=m['binary_sha256']:raise ValueError('Executable changed')
    v,_=validate_output(d,row)
    rows=[json.loads(x) for x in (d/'host.jsonl').read_text().splitlines()]
    verify_environment(rows,initial)
    env=m['environment']
    if any(env[k] is not None for k in ('OMP_PROC_BIND','OMP_PLACES','GOMP_CPU_AFFINITY')):raise ValueError('Bound placement')
    if env['OMP_NUM_THREADS']!=str(row['T']) or env['MKL_NUM_THREADS']!='8' or env['OMP_DYNAMIC']!='FALSE':raise ValueError('Thread environment mismatch')
    temps=[max(v['value_C'] for v in s['sensors'].values() if v['name']=='coretemp' and (v['label'] or '').startswith('Package')) for s in rows]
    return v,dict(process_start=m['timestamp_start'],process_end=m['timestamp_end'],process_wall_s=m['wall_time_s'],
        host_samples=len(rows),temperature_max_C=max(temps),temperature_min_C=min(temps),
        mem_available_min_bytes=min(s['mem_available'] for s in rows),peak_sampled_rss_KiB=m['peak_rss_KiB'],
        observer_cpu_total_s=sum(s['observer_cpu_s'] for s in rows),collection_wall_max_s=max(s['collection_wall_s'] for s in rows),
        sample_lateness_max_s=max(s['sample_lateness_s'] for s in rows),sqpoll_task_counts=[len(s['sqpoll']) for s in rows],
        stdout_sha256=digest(d/'stdout.log'),manifest_sha256=digest(d/'manifest.json'))


def aggregate(records):
    groups={}
    for r in records:
        conf=r['configuration'];key=f"T{conf['T']}_W{conf['W']}_L{conf['L']}"
        groups.setdefault(key,[]).append(r)
    return {key:{metric:descriptive([r['metrics'][metric] for r in rs]) for metric in METRICS} for key,rs in groups.items()}


def pair_statistics(records,seed):
    deltas=[];logs=[];recalls=[];latency=[]
    for block in range(1,7):
        pair={r['configuration']['T']:r['metrics'] for r in records if r['configuration']['stage']=='core' and r['configuration']['block']==block}
        if set(pair)!={8,16}:raise ValueError('Missing paired block')
        a,b=pair[8],pair[16];deltas.append(100*(b['qps']/a['qps']-1));logs.append(math.log(b['qps']/a['qps']));recalls.append(b['recall']-a['recall']);latency.append(100*(b['mean_latency_us']/a['mean_latency_us']-1))
    def stats(values):return dict(**paired_statistics(values,seed),descriptive=descriptive(values))
    return dict(QPS_delta_percent=stats(deltas),log_QPS_ratio=stats(logs),
                recall_delta_pp=stats(recalls),mean_latency_delta_percent=stats(latency))


def analyze(root):
    root=Path(root);check_seal(root);plan=json.loads((root/'PLAN.json').read_text());execution=json.loads((root/'SUMMARY.json').read_text())
    if digest(root/'PLAN.json')!=(root/'PLAN.sha256').read_text().split()[0]:raise ValueError('Frozen plan checksum mismatch')
    if execution['status']!='QUALIFIED':raise ValueError('Campaign not qualified; preserve provisional evidence')
    c=plan['config'];records=json.loads((root/'RUNS.json').read_text());quality=json.loads((root/'QUALITY.json').read_text())
    if digest(c['input_package'])!='47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3':raise ValueError('Unexpected input package identity')
    if digest(c['index_package'])!='7140a47ac53b0480752059b5cb428b4d56dc627533974803b5ae4413827a7470':raise ValueError('Unexpected native index package identity')
    if len(quality)!=12 or len({q['run_id'] for q in quality})!=12:raise ValueError('Quality phase incomplete or duplicated')
    if len(records)!=len(plan['order']) or len(records)!=36:raise ValueError('Incomplete frozen campaign')
    if digest(c['binary'])!=STOCK:raise ValueError('Wrong stock binary')
    if plan['source_commit']!='c4cd32c6816c063f56ecc64f9d7b63c909202cab':raise ValueError('Wrong source subject')
    if not json.loads((root/'PRE_AUDIT.json').read_text())['valid'] or not json.loads((root/'POST_AUDIT.json').read_text())['valid']:raise ValueError('Audit failure')
    initial=plan['initial_environment'];checked=set();quality_results=[]
    for q in quality:
        row=q['configuration'];name=q['run_id'];metrics,host=command(root,name,row,c['quality_binary'],initial,c)
        if q['status']!='QUALIFIED' or metrics!=q['metrics']:raise ValueError('Quality record invalid')
        b=Path(c['data_root']);csv_path=root/(name+'.csv')
        if digest(csv_path)!=q['output_sha256']:raise ValueError('Quality output mismatch')
        exact=quality_against_canonical(csv_path,b/'base_10m.bbin',b/'query.bbin',b/'gt_10m.bin')
        if exact!=q['validation'] or exact['recall']<95 or abs(exact['recall']-metrics['recall'])>.011:raise ValueError('Independent correctness mismatch')
        checked.add((row['T'],row['W'],row['L']));quality_results.append(dict(job=name,configuration=row,validation=exact,host=host))
    if not {'QUALIFICATION_T16','QUALIFICATION_T8','POST_CORE_T16','POST_CORE_T8'}.issubset(q['run_id'] for q in quality):raise ValueError('Mandatory quality phase missing')
    enriched=[]
    for r,want in zip(records,plan['order']):
        if r['configuration']!=want or r['status']!='QUALIFIED':raise ValueError('Wrong order/configuration/status')
        if (want['T'],want['W'],want['L']) not in checked:raise ValueError('Unqualified configuration')
        v,host=command(root,r['run_id'],want,c['binary'],initial,c)
        if v!=r['metrics'] or host['stdout_sha256']!=r['stdout_sha256']:raise ValueError('Raw metric mismatch')
        enriched.append(dict(**r,host=host))
    audit=verify(c['manifest'],c['data_root'],c['index_root'],True)
    return dict(status='QUALIFIED',plan_sha256=digest(root/'PLAN.json'),protocol=plan['protocol'],
                input_package_sha256=digest(c['input_package']),index_package_sha256=digest(c['index_package']),
                full_reaudit_pass=audit['valid'],stock_runs=len(enriched),quality_runs=len(quality_results),
                groups=aggregate(enriched),paired=pair_statistics(enriched,plan['bootstrap']['seed']),
                records=enriched,quality_results=quality_results,
                limitations=['Stock IDs not directly exported; correctness corroborated by distinct same-library quality commands, not every stock output ID.',
                             'Whole-process host samples include loading,2xL200 warmup,search,teardown. No hardware IO latency or CPU phase attribution.',
                             'Six paired blocks give limited uncertainty resolution; no causal mechanism or modern head-to-head.'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--campaign',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('New derived output required')
    a.output.write_text(json.dumps(analyze(a.campaign),indent=2)+'\n')
