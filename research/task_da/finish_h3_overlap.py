"""Validate native replay decisions and export descriptive cost/quality checks."""
import csv
import hashlib
import json
from pathlib import Path
import statistics
import sys
import numpy as np
from research.task_da.analyze_h3_overlap import boot,read_rows,dump
from research.task_da.h3_overlap import assign


def finish(root):
    out=root/'offline_analysis';a=json.loads((out/'analysis.json').read_text())
    qs=list(csv.DictReader((out/'query_metrics.csv').open()));rs=list(csv.DictReader((out/'round_metrics.csv').open()));results={}
    graphroot=Path('/home/thinhbui/Documents/ChatGPT/graph/data/MSTuring_1M_v1')
    base=np.memmap(graphroot/'base.1M.fbin',dtype='<f4',mode='r',offset=8,shape=(1000000,100))
    queries=np.memmap(graphroot/'query.public.100K.fbin',dtype='<f4',mode='r',offset=8,shape=(100000,100))
    truth=np.memmap(graphroot/'groundtruth.public.100K.ibin',dtype='<u4',mode='r',offset=8,shape=(100000,100))
    for rep,beam in [(1,970),(2,986),(3,966)]:
        g=f'A3_r{rep}';s=a['graphs'][g];q=[x for x in qs if x['graph']==g and x['panel']=='held']
        p={k:[x for x in q if x['policy']==k] for k in ['rr','signature','placebo','degree','eligible','exact_greedy']}
        rr=[x for x in rs if x['graph']==g and x['policy']=='rr'];sig=[x for x in rs if x['graph']==g and x['policy']=='signature']
        costs=list(csv.DictReader((root/'offline_cost'/g/'stdout.log').open()));byq={}
        for x,y,z in zip(rr,sig,costs,strict=True):
            v=byq.setdefault(int(x['query_index']),dict(saved=0,crit=0,ns=0,cost=0))
            v['saved']+=float(x['max_work'])-float(y['max_work']);v['crit']+=float(x['actual_max']);v['ns']+=float(x['max_worker_ns']);v['cost']+=float(z['signature_ns'])
        held=[v for k,v in byq.items() if k>=32]
        # Check native decision checksum against independently implemented Python policies.
        lines=iter((out/f'{g}_cost_input.txt').read_text().splitlines());count=int(next(lines));checksum=0
        for _ in range(count):
            n=int(next(lines));seeds=[];ss=[]
            for i in range(n):
                node,degree,lo,hi=map(int,next(lines).split());seeds.append(dict(id=node,degree=degree,eligible=[]));ss.append(lo+(hi<<64))
            degree=assign(seeds,'degree');sketch=assign(seeds,'signature',ss)
            checksum+=sum(i+1 if degree[i]==1 else 1 for i in range(0,n-1,2))
            checksum+=sum(i+1 if sketch[i+2]==1 else 1 for i in range(0,n-3,4))
        actual=int((root/'offline_cost'/g/'stderr.log').read_text().split()[0].split('=')[1]);assert actual==checksum*33,(g,actual,checksum*33)
        rows=read_rows(root/g/'trace_on'/f'beam_{beam}_p2_ON.jsonl');max_error=0;recall=[]
        for row in rows:
            qid=row['query_id'];recall.append(len(set(row['ids'])&set(map(int,truth[qid,:10])))/10)
            for node,d in zip(row['ids'],row['squared_l2']):
                diff=base[node].astype(np.float64)-queries[qid].astype(np.float64);expected=float(np.sum(diff*diff));max_error=max(max_error,abs(expected-d))
                assert abs(expected-d)<1e-12
        results[g]=dict(native_decision_checksum='PASS',distance_checks=len(rows)*10,max_distance_abs_error=max_error,
            recall64=statistics.mean(recall),recall64_se=statistics.stdev(recall)/8,
            signature_vs_placebo=boot([100*(1-float(x['max_seed_work'])/float(y['max_seed_work'])) for x,y in zip(p['signature'],p['placebo'])]),
            exact_vs_eligible=boot([100*(1-float(x['max_seed_work'])/float(y['max_seed_work'])) for x,y in zip(p['exact_greedy'],p['eligible'])]),
            native_ns_per_round={k:statistics.mean(float(x[k]) for x in costs) for k in ['degree_ns','signature_ns']},
            native_ns_per_query={k:sum(float(x[k]) for x in costs)/64 for k in ['degree_ns','signature_ns']},
            held_gross_time_equivalent_ns=statistics.mean(v['saved']*v['ns']/v['crit'] for v in held),
            held_native_cost_ns=statistics.mean(v['cost'] for v in held),
            held_net_time_equivalent_pct_OFF=boot([100*(v['saved']*v['ns']/v['crit']-v['cost'])/s['modes']['frozen_off']['mean_ns'] for v in held]),
            model_label='Sensitivity projection only: saved seed-union L2 * observed ns/critical L2. No counterfactual search timing.',
            observer_on_vs_counters_on_pct=100*(s['modes']['trace_on']['mean_ns']/s['modes']['new_on']['mean_ns']-1))
    dump(out/'cost_quality.json',results)
    print(json.dumps(results,indent=2))


if __name__=='__main__':finish(Path(sys.argv[1]))
