#!/usr/bin/env python3
"""Regenerate local v3 stock summaries; no MLflow queries or performance exclusions."""
import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
from paper_rebaseline import canonical_bytes, descriptive, digest, paired
from paper_native_v3 import block_validity, check_diagnostics
from paper_rebaseline import parse_output


METRICS=('qps','recall','mean_latency_us','p99_latency_us','p999_latency_us','mean_ios','mean_hops')


def check_seal(directory):
    directory=Path(directory)
    for line in (directory/'SHA256SUMS').read_text().splitlines():
        sha,rel=line.split('  ',1)
        if digest(directory/rel)!=sha:raise ValueError('Corrupt finalized evidence: '+rel)


def analyze(root):
    root=Path(root);plan=json.loads((root/'PLAN.json').read_text())
    if (root/'PLAN.sha256').read_text().split()!=[digest(root/'PLAN.json'),'PLAN.json']:
        raise ValueError('Plan bytes changed')
    records=json.loads((root/'attempts.json').read_text()) if (root/'attempts.json').exists() else []
    by_config=defaultdict(lambda:defaultdict(list));flat=[];block_samples=defaultdict(list);primary={}
    for position,record in enumerate(records):
        case=plan['order'][position]
        for key in ('sequence','stage','block','cell','version','threads','wcap','l_search'):
            if record[key]!=case[key]:raise ValueError('Execution order/config mismatch: '+key)
        if record['status']=='completed_quality_valid':
            directory=Path(record['evidence']);check_seal(directory)
            manifest=json.loads((directory/'manifest.json').read_text())
            subject=plan['subjects'][case['version']]
            for key,expected in [('binary_sha256',subject['binary_sha256']),('subject_commit',subject['commit']),
                                 ('index_package_sha256',subject['index_sha256']),('input_package_sha256',plan['input_sha256'])]:
                if manifest[key]!=expected:raise ValueError('Run provenance mismatch: '+key)
            text=(directory/'stdout.log').read_text()+'\n'+(directory/'stderr.log').read_text();check_diagnostics(text)
            parsed=parse_output(text,case['version'],case['l_search'],case['wcap'])
            if parsed!=record['metrics']:raise ValueError('Independent raw-output parsing mismatch')
            key=f"{case['version']}_T{case['threads']}_W{case['wcap']}_L{case['l_search']}"
            for metric,value in parsed.items():
                if value is not None:by_config[key][metric].append(value)
            if case['stage']=='primary':
                primary[(case['block'],case['cell'])]=parsed
                block_samples[case['block']].append(manifest['initial_host'])
                block_samples[case['block']].extend(json.loads(line) for line in (directory/'host.jsonl').read_text().splitlines())
                boundary=json.loads((directory/'boundary_hosts.json').read_text())
                block_samples[case['block']].extend([boundary['before'],boundary['after']])
    # Reconstruct block policy from original logs, including recorded gaps.
    if (root/'gaps.jsonl').exists():
        index={r['run_id']:r for r in records}
        for line in (root/'gaps.jsonl').read_text().splitlines():
            gap=json.loads(line);r=index[gap['after']]
            if r['stage']=='primary' and r['sequence']%6:
                block_samples[r['block']].extend([gap['start'],gap['end']])
    block_verdicts={}
    for block,samples in block_samples.items():
        samples.sort(key=lambda x:x['monotonic_s'])
        complete=all((block,cell) in primary for cell in ('PAPER_T1','PAPER_T4','PAPER_T8','PAPER_T16','MODERN_T8','MODERN_T16'))
        block_verdicts[block]=block_validity(samples) if complete else {'status':'INCOMPLETE'}
    comparisons={}
    for target,reference in [('PAPER_T16','PAPER_T8'),('PAPER_T4','PAPER_T1'),('PAPER_T8','PAPER_T4'),
                             ('MODERN_T16','MODERN_T8'),('MODERN_T8','PAPER_T8'),('MODERN_T16','PAPER_T16')]:
        blocks=[b for b,v in sorted(block_verdicts.items()) if v['status']=='COMPARABLE']
        comparisons[target+'/'+reference]={}
        for metric in ('qps','mean_latency_us'):
            comparisons[target+'/'+reference][metric]=dict(blocks=blocks,result=paired([primary[(b,target)][metric] for b in blocks],
                        [primary[(b,reference)][metric] for b in blocks],samples=20000,seed=20261012) if blocks else None)
    stats={config:{metric:descriptive(values) for metric,values in metrics.items()} for config,metrics in sorted(by_config.items())}
    for position,case in enumerate(plan['order']):
        r=records[position] if position<len(records) else dict(case,status='NOT_RUN',reason='stage unavailable/stopped')
        row={k:r.get(k) for k in ('sequence','stage','block','cell','version','threads','wcap','l_search','run_id','status','reason')}
        row.update({m:r.get('metrics',{}).get(m) for m in METRICS});flat.append(row)
    with (root/'runs.csv').open('w') as stream:
        w=csv.DictWriter(stream,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
    with (root/'stats.csv').open('w') as stream:
        w=csv.DictWriter(stream,fieldnames=['config','metric','n','mean','median','sample_sd','min','max','mad','values']);w.writeheader()
        for config,metrics in stats.items():
            for metric,s in metrics.items():w.writerow(dict(config=config,metric=metric,**dict(s,values=json.dumps(s['values']))))
    summary=dict(statistics=stats,paired=comparisons,block_validity=block_verdicts,
                 completed_quality_valid=sum(r['status']=='completed_quality_valid' for r in records),
                 invalid_or_incomplete=sum(r['status']!='completed_quality_valid' for r in records),not_run=len(plan['order'])-len(records),
                 bootstrap=dict(samples=20000,seed=20261012,ci=.90,quantile='linear p*(n-1)',unit='block'),
                 interpretation='Run/block units only. Native-version comparisons differ in index bytes, mem_L and warmup. Tail percentiles are not comparable.')
    (root/'STOCK_ANALYSIS.json').write_bytes(canonical_bytes(summary))
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True)
    result=analyze(p.parse_args().evidence);print(json.dumps({k:result[k] for k in ('completed_quality_valid','invalid_or_incomplete','not_run')}))
