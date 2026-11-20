#!/usr/bin/env python3
"""Bounded offline snapshot screening; no ANN search or policy replay paths."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import statistics
import time
import numpy as np
from research.task_da.h3_overlap import assign,exact_oracle,metrics


def read_rows(p):return [json.loads(x) for x in p.read_text().splitlines()]
def dump(p,a):
    with p.open('x') as f:json.dump(a,f,indent=2,allow_nan=False);f.write('\n')
def ranks(a):
    order=np.argsort(a,kind='stable');out=np.empty(len(a),float);i=0
    while i<len(a):
        j=i+1
        while j<len(a) and a[order[j]]==a[order[i]]:j+=1
        out[order[i:j]]=(i+j-1)/2;i=j
    return out
def corr(a,b):
    x,y=ranks(np.array(a)),ranks(np.array(b))
    return float(np.corrcoef(x,y)[0,1]) if np.std(x)>0 and np.std(y)>0 else None
def boot(values):
    a=np.array(values);rng=np.random.default_rng(20261120)
    b=a[rng.integers(0,len(a),(4000,len(a)))].mean(axis=1)
    return dict(mean=float(a.mean()),ci95=list(map(float,np.quantile(b,[.025,.975]))))


def analyze(root,out):
    out.mkdir(exist_ok=False);checks=json.loads((root/'capture_checks.json').read_text());assert checks['status']=='CAPTURE_PARITY_PASS'
    manifest=json.loads(Path('docs/research/task-da/experiment_manifest_v3_reconciled.json').read_text())
    graphroot=Path('/home/thinhbui/Documents/ChatGPT/graph');policies=['rr','degree','eligible','exact_quartet','exact_greedy','signature','placebo']
    all_records=[];summary={};cost_fixture=[];oracle_rows=[];query_summary=[]
    for rep,beam in [(1,970),(2,986),(3,966)]:
        g=f'A3_r{rep}';folder=root/g
        bymode={name:read_rows(folder/name/f'beam_{beam}_p2_{mode}.jsonl') for name,mode in
                [('frozen_off','OFF'),('new_off','OFF'),('new_on','ON'),('trace_on','ON')]}
        rows=bymode['trace_on'];gp=next(x for x in manifest['graphs'] if x['arm']=='A3' and x['replicate']==rep)
        mm=np.memmap(graphroot/gp['path'],dtype='<u4',mode='r');n=int(mm[0]);degree=mm[2:2+n]
        offsets=np.concatenate(([0],np.cumsum(degree,dtype=np.int64)));edges=mm[2+n:]
        def neighbors(v):return list(map(int,edges[offsets[v]:offsets[v+1]]))
        sig_cache={}
        def sig(v):
            if v not in sig_cache:
                mask=0
                for nbr in neighbors(v):
                    bit=int.from_bytes(hashlib.sha256(f'task-d-h3-adj128-v1/{nbr}'.encode()).digest(),'little')&127
                    mask |= 1<<bit
                sig_cache[v]=mask
            return sig_cache[v]
        pools=collections.defaultdict(set)
        for q in rows:
            for r in q['rounds']:
                for s in r['seeds']:pools[s['degree']].add(s['id'])
        placebo={};singleton=0
        for pool in pools.values():
            order=sorted(pool,key=lambda v:hashlib.sha256(f'task-d-h3-placebo-v1/{v}'.encode()).digest())
            for i,v in enumerate(order):placebo[v]=order[(i+1)%len(order)]
            singleton+=len(order)==1
        graph_records=[];qt=[]
        for qi,q in enumerate(rows):
            # Independent reconstruction of the monotone B1 settled set.
            entry=0;visited={entry,*neighbors(entry)};initial=len(visited)
            query_events=0;query_dup=0;query_exp=1
            agg={p:collections.Counter() for p in policies};obs=collections.Counter()
            for ri,r in enumerate(q['rounds']):
                seeds=sorted(r['seeds'],key=lambda x:x['rank']);sets=[set(s['eligible']) for s in seeds]
                assert [s['rank'] for s in seeds]==list(range(len(seeds)))
                assert [s['worker'] for s in seeds]==assign(seeds,'rr')
                for s in seeds:
                    assert s['degree']==int(degree[s['id']])
                    assert s['eligible']==[v for v in neighbors(s['id']) if v not in visited]
                ew=[{v:parent for parent,v in w['evaluated']} for w in r['workers']]
                for w,e in zip(r['workers'],ew):
                    assert len(e)==len(w['evaluated'])
                    assert all(v not in visited and v in neighbors(parent) for parent,v in w['evaluated'])
                    assert w['start_ns']<=w['done_ns']<=r['arrived_ns']
                dup=set(ew[0])&set(ew[1]);seed_ids={s['id'] for s in seeds};classes=collections.Counter()
                for v in dup:classes[sum(ew[w][v] in seed_ids for w in range(2))]+=1
                actual=[len(x) for x in ew];wc=[w['done_ns']-w['start_ns'] for w in r['workers']]
                exp=[v for w in r['workers'] for v in w['expanded']]
                query_events+=sum(actual);query_dup+=len(dup);query_exp+=len(exp)
                observed=dict(actual_l2=sum(actual),actual_max=max(actual),actual_dup=len(dup),
                    seed_seed_dup=classes[2],seed_emergent_dup=classes[1],emergent_dup=classes[0],
                    max_worker_ns=max(wc),worker0_ns=wc[0],worker1_ns=wc[1],
                    barrier_wait_ns=sum(r['arrived_ns']-w['done_ns'] for w in r['workers'] if w['expanded']),
                    round_ns=r['end_ns']-r['prepare_ns'],snapshot_ns=r['snapshot_ns'],copy_ns=r['copy_ns'],
                    seeds=len(seeds),seed_popped=len(set(exp)&seed_ids),expansions=len(exp),
                    raw_degree=sum(s['degree'] for s in seeds),eligible_degree=sum(map(len,sets)),
                    visited_fraction=1-sum(map(len,sets))/max(1,sum(s['degree'] for s in seeds)))
                # Duplicate ownership oracle over the observed paths: work bound, not latency.
                d=len(dup);best_max=max(actual[0]-d,actual[1]-d,(sum(actual)-d+1)//2)
                observed['ownership_oracle_saved_l2']=max(actual)-best_max
                for k,v in observed.items():obs[k]+=v
                ss=[sig(s['id']) for s in seeds];ps=[sig(placebo[s['id']]) for s in seeds]
                cost_fixture.append((g,qi,ri,seeds,ss))
                for p in policies:
                    start=time.perf_counter_ns();a=assign(seeds,p,ps if p=='placebo' else ss);dt=time.perf_counter_ns()-start
                    m=metrics(sets,a);record=dict(graph=g,query_index=qi,query_id=q['query_id'],round=ri,
                        panel='dev' if qi<32 else 'held',policy=p,python_scheduler_ns=dt,**m,**observed)
                    graph_records.append(record);all_records.append(record)
                    for k,v in m.items():agg[p][k]+=v
                visited.update(ew[0]);visited.update(ew[1]);visited.update(exp)
            assert query_events+initial==q['counters']['distance_evaluations']
            assert query_dup==q['counters']['duplicate_distance_evaluations']
            assert query_exp==q['counters']['expansions']
            for p in policies:
                qt.append(dict(graph=g,query_index=qi,query_id=q['query_id'],panel='dev' if qi<32 else 'held',policy=p,
                    max_seed_work=agg[p]['max_work'],duplicate_seed_work=agg[p]['duplicate'],
                    proxy_gain_pct=100*(1-agg[p]['max_work']/max(1,agg['rr']['max_work'])),
                    actual_dup=q['counters']['duplicate_distance_evaluations'],actual_l2=q['counters']['distance_evaluations'],
                    actual_critical_l2=obs['actual_max'],ownership_oracle_saved_l2=obs['ownership_oracle_saved_l2'],
                    seed_seed_dup=obs['seed_seed_dup'],seed_emergent_dup=obs['seed_emergent_dup'],emergent_dup=obs['emergent_dup'],
                    seed_popped=obs['seed_popped'],seeds=obs['seeds'],snapshot_ns=obs['snapshot_ns'],copy_ns=obs['copy_ns'],
                    actual_max_worker_ns=obs['max_worker_ns'],trace_latency_ns=q['latency_ns']))
        # Exact eight rounds: deterministic global round-position quantiles, no work-based selection.
        rr=[r for r in graph_records if r['policy']=='rr'];targets=sorted({int(i*(len(rr)-1)/7) for i in range(8)})
        for index in targets:
            r=rr[index];seeds=sorted(rows[r['query_index']]['rounds'][r['round']]['seeds'],key=lambda s:s['rank'])
            t=time.perf_counter_ns();a=exact_oracle(seeds);elapsed=time.perf_counter_ns()-t;m=metrics([set(s['eligible']) for s in seeds],a)
            oracle_rows.append(dict(graph=g,query_index=r['query_index'],round=r['round'],elapsed_ns=elapsed,
                                    rr_max=r['max_work'],rr_duplicate=r['duplicate'],**m))
        query_summary.extend(qt)
        held=[r for r in rr if r['query_index']>=32]
        associations={name:corr([r['duplicate'] for r in held],[r[name] for r in held]) for name in
            ['actual_dup','actual_max','max_worker_ns','barrier_wait_ns','round_ns']}
        # Train on R1 development only below; preserve exact feature rows here.
        summary[g]=dict(queries=64,rounds=len(rr),max_rounds=max(len(q['rounds']) for q in rows),
            placebo_singleton_degree_strata=singleton,
            modes={k:dict(mean_ns=statistics.mean(x['latency_ns'] for x in a),p95_ns=float(np.quantile([x['latency_ns'] for x in a],.95))) for k,a in bymode.items()},
            actual={k:statistics.mean(x[k] for x in qt if x['policy']=='rr') for k in
                ['actual_l2','actual_dup','actual_critical_l2','seed_seed_dup','seed_emergent_dup','emergent_dup','seed_popped','seeds','snapshot_ns','copy_ns','ownership_oracle_saved_l2']},
            held_spearman_seed_duplicate=associations,
            held_spearman_max_seed_actual_max=corr([r['max_work'] for r in held],[r['actual_max'] for r in held]),
            policies={p:boot([x['proxy_gain_pct'] for x in qt if x['policy']==p and x['panel']=='held']) for p in policies},
            policy_round_outcomes={p:dict(zip(['better','equal','worse'],
                [sum(op(a['max_work'],b['max_work']) for a,b in zip([x for x in graph_records if x['policy']==p],rr))
                for op in [lambda a,b:a<b,lambda a,b:a==b,lambda a,b:a>b]])) for p in policies})
    # Small predictive check: degree/phase versus degree+exact overlap.
    rr=[r for r in all_records if r['policy']=='rr'];train=[r for r in rr if r['graph']=='A3_r1' and r['panel']=='dev']
    def features(r,overlap):
        f=[1,r['raw_degree'],r['eligible_degree'],r['seeds'],r['round'],r['visited_fraction']]
        return f+[r['duplicate'],r['max_work']] if overlap else f
    predictive={}
    for target in ['actual_dup','actual_max','max_worker_ns','barrier_wait_ns','round_ns']:
        predictive[target]={}
        for overlap in [False,True]:
            x=np.array([features(r,overlap) for r in train],float);scale=np.maximum(np.std(x,axis=0),1);beta=np.linalg.lstsq(x/scale,np.array([r[target] for r in train]),rcond=None)[0]
            for g in summary:
                held=[r for r in rr if r['graph']==g and r['panel']=='held'];y=np.array([r[target] for r in held]);pred=np.array([features(r,overlap) for r in held])/scale@beta
                predictive[target].setdefault(g,{})['overlap' if overlap else 'degree']=dict(mae=float(np.mean(abs(pred-y))),rmse=float(np.mean((pred-y)**2)**.5))
    # Paired whole-query gain versus the stronger cheap degree baseline.
    for g in summary:
        q=[x for x in query_summary if x['graph']==g and x['panel']=='held'];degree=[x for x in q if x['policy']=='degree']
        summary[g]['gain_vs_degree']={p:boot([100*(1-a['max_seed_work']/max(1,b['max_seed_work'])) for a,b in
            zip([x for x in q if x['policy']==p],degree)]) for p in policies}
    for name,records in [('round_metrics.csv',all_records),('query_metrics.csv',query_summary),('oracle.csv',oracle_rows)]:
        with (out/name).open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    # Native replay input has precomputed raw-adjacency signatures; all preparation outside kernel timing.
    for g in summary:
        subset=[x for x in cost_fixture if x[0]==g]
        with (out/f'{g}_cost_input.txt').open('x') as f:
            f.write(f'{len(subset)}\n')
            for _,qi,ri,seeds,sigs in subset:
                f.write(f'{len(seeds)}\n')
                for s,mask in zip(seeds,sigs):f.write(f"{s['id']} {s['degree']} {mask&((1<<64)-1)} {mask>>64}\n")
    dump(out/'analysis.json',dict(graphs=summary,predictive=predictive,oracle=oracle_rows,
        labels={'policies':'ONE-HOP OFFLINE COUNTERFACTUAL; no latency/recall replay','oracle':'optimal rank-pair union objective on 8 rounds/graph only','timing':'ANN timing is RR only; one process/mode, descriptive, no speedup test'}))
    print(json.dumps({'graphs':summary,'predictive':predictive},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('output',type=Path);a=p.parse_args();analyze(a.root,a.output)
