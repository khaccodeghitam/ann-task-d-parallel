"""Descriptive phase budgets and the preregistered three-pair validity gate."""
import argparse
import csv
import json
import math
from pathlib import Path
import statistics as st

REPO=Path(__file__).resolve().parents[2]


def read_rows(path):
    return [json.loads(s) for s in path.read_text().splitlines()]


def analyze(root):
    checks=json.loads((root/'capture_checks.json').read_text())
    assert checks['status']=='PARITY_AND_CONSERVATION_PASS'
    process=[];flat=[];log_ratios=[]
    for item in checks['processes']:
        rows=read_rows(root/item['output']/'beam_970_p2_OFF.jsonl')
        mean=st.mean(r['latency_ns'] for r in rows)
        record={**item,'mean_ns':mean}
        for r in rows:
            flat.append(dict(pair=item['pair'],order=item['order'],label=item['label'],
                query_id=r['query_id'],latency_ns=r['latency_ns'],**r.get('phase_audit',{})))
        if item['label']=='phase_off':
            p={k:st.mean(r['phase_audit'][k] for r in rows) for k in rows[0]['phase_audit'] if k!='kind'}
            p['coordinator_ns']=p['gather_publish_ns']+p['frontier_dispatch_ns']
            p['residual_ns']=mean-p['worker_phase_ns']-p['coordinator_ns']
            assert p['residual_ns']>=0
            record['phase_mean']=p
            record['phase_share_pct']={k:100*v/mean for k,v in p.items() if k.endswith('_ns')}
        process.append(record)
    assert len(process)==6
    for i in (1,2,3):
        pair={x['label']:x['mean_ns'] for x in process if x['pair']==i}
        log_ratios.append(math.log(pair['phase_off']/pair['frozen_off']))
    # df=2; do not substitute 192 query observations for three process pairs.
    center=st.mean(log_ratios)
    half=4.302652729911275*st.stdev(log_ratios)/math.sqrt(3)
    ci=[100*math.expm1(center-half),100*math.expm1(center+half)]
    gate=ci[0]>=-2 and ci[1]<=2
    off=[x['mean_ns'] for x in process if x['label']=='frozen_off']
    obs=[x for x in process if x['label']=='phase_off']
    phase={k:st.mean(x['phase_mean'][k] for x in obs) for k in obs[0]['phase_mean']}
    offmean=st.mean(off);obsmean=st.mean(x['mean_ns'] for x in obs)
    phase_shares={k:100*v/obsmean for k,v in phase.items() if k.endswith('_ns')}
    h3=REPO.parent/'artifact-evidence/h3-overlap-screening-20261120'
    old_modes={}
    for label,mode in [('frozen_off','OFF'),('new_off','OFF'),('new_on','ON'),('trace_on','ON')]:
        rows=read_rows(h3/'A3_r1'/label/f'beam_970_p2_{mode}.jsonl')
        old_modes[label]=dict(mean_ns=st.mean(r['latency_ns'] for r in rows),queries=len(rows))
    old_modes['comparisons_pct']=dict(
        trace_build_off_vs_frozen=100*(old_modes['new_off']['mean_ns']/old_modes['frozen_off']['mean_ns']-1),
        counters_on_vs_same_build_off=100*(old_modes['new_on']['mean_ns']/old_modes['new_off']['mean_ns']-1),
        trace_on_vs_counters_on=100*(old_modes['trace_on']['mean_ns']/old_modes['new_on']['mean_ns']-1),
        trace_on_vs_frozen_off=100*(old_modes['trace_on']['mean_ns']/old_modes['frozen_off']['mean_ns']-1))
    # Host samples include load/initialization as well as search; no phase attribution.
    host=[]
    for x in process:
        for s in read_rows(root/x['output']/'host.jsonl'):
            host.extend(v['value_C'] for v in s['sensors'].values() if v['name']=='k10temp' and v['label']=='Tctl')
    output=dict(processes=process,paired_log_ratios=log_ratios,
        paired_percent=[100*math.expm1(x) for x in log_ratios],
        observer_change_pct=100*math.expm1(center),observer_CI95_pct=ci,
        observer_gate='PASS' if gate else 'NOT_VALIDATED_OUTSIDE_EQUIVALENCE_BUDGET',
        observed_off_mean_ns=offmean,observed_off_process_sd_ns=st.stdev(off),observer_mean_ns=obsmean,
        phase_mean=phase,phase_share_pct=phase_shares,
        phase_transfer_to_OFF='conditional on validity and phase-specific transfer; NOT_ESTABLISHED',
        temperature_samples_C=dict(n=len(host),min=min(host),max=max(host)),
        h3_sealed_modes=old_modes,
        opportunity_sensitivity=dict(target_5pct_OFF_ns=.05*offmean,
            hypothetical_1pct_OFF_controller_ns=.01*offmean,
            hypothetical_1pct_OFF_controller_ns_per_round=.01*offmean/phase['rounds'],
            ideal_balance_minus_hypothetical_controller_pct_observer=100*(phase['ideal_balance_ns']-.01*offmean)/obsmean,
            fraction_of_observed_coordinator_to_remove_for_5pct_OFF_plus_1pct_controller=.06*offmean/phase['coordinator_ns']),
        labels=dict(raw='observed',bounds='zero-cost fixed-work counterfactual, not algorithm speedup',
                    old_mode_comparisons='ordered unreplicated descriptive process comparisons, not causal overhead',
                    PMU='NOT_MEASURED: existing perf permissions denied'))
    (root/'analysis.json').write_text(json.dumps(output,indent=2)+'\n')
    with (root/'query_summary.csv').open('w',newline='') as f:
        fields=list(dict.fromkeys(k for r in flat for k in r))
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(flat)
    print(json.dumps({k:v for k,v in output.items() if k not in ('processes','paired_log_ratios')},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    analyze(parser.parse_args().output.resolve())
