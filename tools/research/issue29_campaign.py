"""Issue29 prospective T16-first qualification and conditional paper-only runs.

Reuses the preserved owned-process thermal guard; never resumes old campaigns.
"""
import argparse
import json
from pathlib import Path
import random
import subprocess
import time

from artifact_bundle import verify, unchanged
from paper_native_v3 import quality_against_canonical
from paper_paired_campaign import argv, validate_output, environment_valid, policy_state, resolved
from paper_portable_v2 import host_snapshot, utc, seal
from paper_rebaseline import canonical_bytes, digest, descriptive
from run_paper_fullfan_check import run, CoolingGuard


def schedule(seed=20261029):
    first=random.Random(seed).choice([8,16]); rows=[]
    for block in range(1,7):
        for t in ([first,24-first] if block%2 else [24-first,first]):
            rows.append(dict(stage='core',block=block,T=t,W=32,L=100))
    for block in range(1,4):
        for t in ([1,4] if block%2 else [4,1]):
            rows.append(dict(stage='reference',block=block,T=t,W=32,L=100))
    rng=random.Random(seed)
    for rep in range(1,4):
        ls=[50,75,125,150]; rng.shuffle(ls)
        rows.extend(dict(stage='extension_L',block=rep,T=8,W=32,L=l) for l in ls)
    for rep in range(1,4):
        ws=[16,64]; rng.shuffle(ws)
        rows.extend(dict(stage='extension_W',block=rep,T=8,W=w,L=100) for w in ws)
    return [dict(sequence=i+1,**row) for i,row in enumerate(rows)]


def snapshot(root):
    s=host_snapshot(root)
    p=Path('/sys/firmware/acpi/platform_profile')
    s['platform_profile']=p.read_text().strip() if p.exists() else None
    return s


def expected_host_violations(s, contract):
    """Reject an unverified operating profile; never write to sysfs."""
    if not contract:
        return []
    errors = []
    target = str(contract.get('platform_profile', '')).strip().lower()
    actual = str(s.get('platform_profile') or '').strip().lower()
    if target != 'custom':
        errors.append('EXPECTED_ENVIRONMENT: only the prospective custom profile is supported')
    elif actual != target:
        errors.append(f'EXPECTED_ENVIRONMENT: profile {actual!r}, required {target!r}')
    try:
        tol = float(contract.get('tolerance_W', 1))
        if not 0 <= tol <= 1:
            raise ValueError('tolerance must be within [0,1] W')
        targets = [float(contract['mmio_PL1_W']), float(contract['mmio_PL2_W'])]
        if targets != [60.0, 90.0]:
            raise ValueError('fixed Custom v1 requires MMIO 60/90W')
    except (TypeError, ValueError, KeyError) as e:
        errors.append(f'EXPECTED_ENVIRONMENT: invalid frozen config ({e})')
        return errors
    entries = (s.get('rapl') or {})
    for i, label in enumerate(('PL1', 'PL2')):
        suffix = f'/constraint_{i}_power_limit_uw'
        matches = [value for key, value in entries.items()
                   if 'intel-rapl-mmio' in str(key).lower() and str(key).lower().endswith(suffix)]
        if len(matches) != 1:
            errors.append(f'EXPECTED_ENVIRONMENT: {label} MMIO sensor missing or ambiguous ({len(matches)})')
            continue
        try:
            watts = int(matches[0]) / 1_000_000
        except (TypeError, ValueError):
            errors.append(f'EXPECTED_ENVIRONMENT: {label} unreadable MMIO limit')
            continue
        if abs(watts-targets[i]) > tol:
            errors.append(f'EXPECTED_ENVIRONMENT: {label} MMIO {watts:.3f}W, required {targets[i]:.0f}±{tol:g}W')
    return errors


def qualify_start(s, baseline, expected=None):
    reasons=CoolingGuard(baseline).check(s)
    package=[x['value_C'] for x in s['sensors'].values() if x['name']=='coretemp' and (x['label'] or '').startswith('Package')]
    if not package or max(package)>=85: reasons.append('Startup package >=85C or unavailable')
    if not s.get('rapl') or s.get('platform_profile') is None: reasons.append('Policy/profile unavailable')
    if policy_state(s)!=policy_state(baseline): reasons.append('Fixed operating condition changed')
    reasons.extend(expected_host_violations(s, expected))
    if reasons: raise ValueError('; '.join(reasons))


def execute(config, output):
    c=resolved(config); root=Path(output);root.mkdir(parents=True,exist_ok=False)
    initial=snapshot(root);rows=schedule()
    source=Path(c['subject_repo'])
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
    tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=source,text=True).strip()
    if commit!='c4cd32c6816c063f56ecc64f9d7b63c909202cab' or tree!='23fbb256528c67454cd4348bc58dfee700dffa06': raise ValueError('Portable subject mismatch')
    if subprocess.check_output(['git','status','--porcelain'],cwd=source): raise ValueError('Dirty subject')
    if digest(c['binary'])!='5f5fa8d99cc83b523c71b7025e5f0b9aa61f45d42816804ed6d88755ebaa310b': raise ValueError('Stock binary mismatch')
    if digest(c['quality_binary'])!=c['quality_sha256']: raise ValueError('Quality binary mismatch')
    plan=dict(protocol='ISSUE29_T16_FIRST_v1',created=utc(),config=c,source_commit=commit,source_tree=tree,
              harness_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
              code_sha256=digest(__file__),guard_sha256=digest(Path(__file__).with_name('run_paper_fullfan_check.py')),
              initial_environment=initial,expected_operating_condition=c.get('expected_operating_condition'),order=rows,seed=20261029,
              bootstrap=dict(samples=20000,seed=20261029,CI=.90,unit='paired block',quantile='linear p*(n-1)'),
              phases=['Full pre-audit','5s gap; T16 full quality FIRST','5s gap; T8 full quality','12 paired stock','5s gap; T16 and T8 post-core quality','6 optional references','18 optional L/W'],
              pause_s=5,between_block_s=15,timeout_s=240,total_wall_cap_s=3600,
              guards='Same 1Hz rich guard/watchdog. Package >=99C once or >=97C for10s; startup >=85C rejects every command. AC,1GiB RAM,20GiB disk,swap,foreign ANN guards unchanged.',
              acceptance='No retries. All commands fixed policy/profile; quality every configuration before first use plus core postchecks; IDs/cardinality/all exact distances and tie-aware recall independently checked; recall>=95%, printed quality discrepancy<=0.011pp. Full post hash audit. Any failure leaves ALL completed stock outputs PROVISIONAL.',
              quality_floor_rationale='95% is a gross correctness floor below prior native99.206%, not a recall-equivalence or speedup threshold. All measured recall differences must still be reported.',
              inference='Stock IDs not exported; separate same-library quality probe establishes correctness per config, not identity of every nondeterministic stock result. Mixed-phase host telemetry; P99.9 only.',
              extension_condition='Only after all prior gates, same fixed policy, startup<85C and total wall budget; no automatic cooling retries.')
    (root/'PLAN.json').write_bytes(canonical_bytes(plan));(root/'PLAN.sha256').write_text(digest(root/'PLAN.json')+'  PLAN.json\n')
    records=[];quality=[];stop=None;active=None;fingerprint=None;started=time.monotonic()
    def persist():
        (root/'RUNS.json').write_bytes(canonical_bytes(records));(root/'QUALITY.json').write_bytes(canonical_bytes(quality))
    def checked_run(row,name,quality_mode=False):
        nonlocal active
        active=name
        if time.monotonic()-started>3600: raise ValueError('Prospective total wall budget exhausted')
        time.sleep(5); s=snapshot(root)
        with (root/'startup.jsonl').open('a') as f:f.write(json.dumps(dict(job=name,host=s))+'\n')
        qualify_start(s,initial,c.get('expected_operating_condition'));unchanged(fingerprint)
        binary=c['quality_binary'] if quality_mode else c['binary']
        spec=dict(argv=argv(c,row,binary),threads=row['T'],binary_sha256=digest(binary),timeout_s=240,run_id=name)
        result=root/(name+'.csv')
        if quality_mode:spec['extra_environment']={'PAPER_QUALITY_OUTPUT':str(result)}
        m=run(spec,root/name);v,_=validate_output(root/name,row);env=environment_valid(root/name)
        if any(policy_state(s)!=policy_state(initial) for s in env):raise ValueError('Fixed operating condition changed during command')
        if v['recall']<95:raise ValueError('Recall below prospective gross quality floor')
        entry=dict(run_id=name,configuration=row,metrics=v,manifest_sha256=digest(root/name/'manifest.json'),stdout_sha256=digest(root/name/'stdout.log'))
        if quality_mode:
            data=Path(c['data_root']);q=quality_against_canonical(result,data/'base_10m.bbin',data/'query.bbin',data/'gt_10m.bin')
            if q['recall']<95 or abs(q['recall']-v['recall'])>.011:raise ValueError('Independent quality mismatch')
            entry.update(status='QUALIFIED',validation=q,output_sha256=digest(result));quality.append(entry)
        else:entry.update(status='PROVISIONAL');records.append(entry)
        active=None;persist();print(json.dumps(dict(job=name,status=entry['status'],**v)),flush=True)
        return entry
    try:
        qualify_start(initial,initial,c.get('expected_operating_condition'))
        if digest(c['input_package'])!='47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3':raise ValueError('Input package identity mismatch')
        if digest(c['index_package'])!='7140a47ac53b0480752059b5cb428b4d56dc627533974803b5ae4413827a7470':raise ValueError('Native index package identity mismatch')
        fingerprint=verify(c['manifest'],c['data_root'],c['index_root'],True)
        (root/'PRE_AUDIT.json').write_bytes(canonical_bytes(fingerprint))
        checked_run(dict(T=16,W=32,L=100),'QUALIFICATION_T16',True)
        checked_run(dict(T=8,W=32,L=100),'QUALIFICATION_T8',True)
        validated={(16,32,100),(8,32,100)}
        for i,row in enumerate(rows):
            key=(row['T'],row['W'],row['L'])
            if key not in validated:
                checked_run(row,f'QUALITY_T{key[0]}_W{key[1]}_L{key[2]}',True);validated.add(key)
            checked_run(row,f"R{row['sequence']:02d}_T{row['T']}_W{row['W']}_L{row['L']}")
            if i==11:
                checked_run(dict(T=16,W=32,L=100),'POST_CORE_T16',True)
                checked_run(dict(T=8,W=32,L=100),'POST_CORE_T8',True)
            if i<len(rows)-1 and (rows[i+1]['stage'],rows[i+1]['block'])!=(row['stage'],row['block']):time.sleep(10)
    except BaseException as e:
        stop=f'{type(e).__name__}: {e}';print(json.dumps(dict(stop=stop,failed_job=active)),flush=True)
    finally:
        try:post=verify(c['manifest'],c['data_root'],c['index_root'],True)
        except Exception as e:post=dict(valid=False,error=str(e));stop=stop or 'Post-audit failure'
        (root/'POST_AUDIT.json').write_bytes(canonical_bytes(post))
        if not stop and len(records)==len(rows):
            for r in records:r['status']='QUALIFIED'
        persist()
        outcome=dict(status='QUALIFIED' if not stop else 'SKIPPED_THERMAL' if not records and ('guard' in str(stop).lower() or '85C' in str(stop)) else 'BLOCKED_ENVIRONMENT' if not records and 'EXPECTED_ENVIRONMENT' in str(stop) else 'PROVISIONAL',stop_reason=stop,failed_job=active,
                     stock_completed=len(records),stock_qualified=sum(r['status']=='QUALIFIED' for r in records),quality_completed=len(quality),post_audit_valid=post['valid'])
        (root/'SUMMARY.json').write_bytes(canonical_bytes(outcome));seal(root)
    return outcome


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    if a.dry_run:print(json.dumps(schedule(),indent=2))
    else:
        result=execute(json.loads(a.config.read_text()),a.output)
        print(json.dumps(result,indent=2))
        if result['status']!='QUALIFIED':raise SystemExit(2)
