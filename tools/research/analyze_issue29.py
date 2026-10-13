"""Independent read-only regeneration from finalized Issue29 local evidence."""
import argparse
import csv
import json
from pathlib import Path
import statistics
from artifact_bundle import verify
from paper_native_v3 import quality_against_canonical
from paper_rebaseline import digest, parse_output


def check_seal(root):
    for line in (root/'SHA256SUMS').read_text().splitlines():
        expected,relative=line.split('  ',1);p=Path(relative)
        if p.is_absolute() or '..' in p.parts or not (root/p).resolve().is_relative_to(root.resolve()):raise ValueError('Unsafe seal path')
        if digest(root/p)!=expected:raise ValueError('Checksum mismatch: '+relative)


def analyze(root):
    root=Path(root);check_seal(root)
    plan=json.loads((root/'PLAN.json').read_text());summary=json.loads((root/'SUMMARY.json').read_text())
    if digest(root/'PLAN.json')!=(root/'PLAN.sha256').read_text().split()[0]:raise ValueError('Plan checksum mismatch')
    c=plan['config'];commands=[]
    for name in ('QUALIFICATION_T16','QUALIFICATION_T8'):
        d=root/name
        if not d.exists():continue
        m=json.loads((d/'manifest.json').read_text());rows=[json.loads(x) for x in (d/'host.jsonl').read_text().splitlines()]
        if m['binary_sha256']!=plan['config']['quality_sha256']:raise ValueError('Quality identity mismatch')
        if digest(m['argv'][0])!=m['binary_sha256']:raise ValueError('Quality binary changed')
        if m['argv'][3:5]!=[name.rsplit('T',1)[1],'32']:raise ValueError('Quality config mismatch')
        temperatures=[max(v['value_C'] for v in s['sensors'].values() if v['name']=='coretemp' and (v['label'] or '').startswith('Package')) for s in rows]
        text=(d/'stdout.log').read_text()+'\n'+(d/'stderr.log').read_text()
        try:metrics=parse_output(text,'PAPER',100,32)
        except ValueError:metrics=None
        q=None
        if (root/(name+'.csv')).exists():
            # Even complete, correct rows from a terminated process NEVER undo its guard failure.
            b=Path(c['data_root']);q=quality_against_canonical(root/(name+'.csv'),b/'base_10m.bbin',b/'query.bbin',b/'gt_10m.bin')
        commands.append(dict(job=name,status='QUALIFIED' if m['exit_code']==0 and not m['guard_failure'] and q else 'PROVISIONAL',
            exit_code=m['exit_code'],guard_failure=m['guard_failure'],wall_time_s=m['wall_time_s'],
            metrics=metrics,independent_quality=q,temperature_samples_C=temperatures,max_temperature_C=max(temperatures),
            peak_sampled_rss_KiB=m['peak_rss_KiB'],host_samples=len(rows),
            collection_wall_max_s=max(s['collection_wall_s'] for s in rows),
            observer_cpu_total_s=sum(s['observer_cpu_s'] for s in rows),
            lateness_max_s=max(s['sample_lateness_s'] for s in rows),
            host_phase_scope='Process lifetime: load,2xL200 warmup,timedL100,export,teardown. No phase timestamps; thermal trip cannot be localized precisely.',
            temperature_vs_wall_caution='1Hz samples cannot exclude transient peaks; collection wall/CPU time are not measured overhead on ANN.',
            stdout_sha256=digest(d/'stdout.log'),manifest_sha256=digest(d/'manifest.json')))
    audit=verify(c['manifest'],c['data_root'],c['index_root'],True)
    return dict(status=summary['status'],plan_sha256=digest(root/'PLAN.json'),execution_summary=summary,
                commands=commands,full_reaudit_pass=audit['valid'],stock_runs=json.loads((root/'RUNS.json').read_text()),
                paired_T16_vs_T8=None,interpretation='No stock campaign or paired effect estimated. Quality executable timings are diagnostic only.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--campaign',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError('New derived output required')
    a.output.write_text(json.dumps(analyze(a.campaign),indent=2)+'\n')
