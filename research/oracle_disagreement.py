#!/usr/bin/env python3
"""Fixed offline audit of saved exact-distance surrogate states, not ANN replay."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import random
import statistics
import numpy as np
from studies import simulate


SEED=20261029
MODELS=('distance_only','degree_history','cheap_margin','permuted_training_labels')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_rows(path):
    rows=[];split_by_query={}
    with Path(path).open() as stream: raw_rows=list(csv.DictReader(stream))
    for raw in raw_rows:
        r={k:v if k=='split' else float(v) for k,v in raw.items()}
        for k in ('query_id','step','node','degree','seen','novel','useful'):r[k]=int(r[k])
        q=r['query_id'];old=split_by_query.setdefault(q,r['split'])
        if old!=r['split'] or r['split'] not in ('train','validation','test'):raise ValueError('Query split leakage')
        if any(not np.isfinite(v) for k,v in r.items() if k!='split'):raise ValueError('Nonfinite candidate data')
        if r['Gk']<0 or r['batch_marginal_Gk']< -1e-12:raise ValueError('Negative utility')
        rows.append(r)
    states=group_states(rows)
    for rs in states.values():
        if len({r['node'] for r in rs})!=len(rs) or len({r['frontier_rank'] for r in rs})!=len(rs):raise ValueError('Duplicate candidate/rank')
        if len({r['split'] for r in rs})!=1:raise ValueError('State split leakage')
        rs.sort(key=lambda r:r['frontier_rank'])
        if rs[0]['frontier_rank']!=0:raise ValueError('Missing nearest candidate')
        if any(rs[i]['distance_norm']>rs[i+1]['distance_norm'] for i in range(len(rs)-1)):raise ValueError('Distance/rank mismatch')
    return rows


def group_states(rows):
    groups={}
    for r in rows:groups.setdefault((r['query_id'],r['step']),[]).append(r)
    return groups


def cluster_ci(values,samples=20000):
    if not values:return None
    rng=np.random.default_rng(SEED)
    v=np.asarray(values,dtype=float);means=v[rng.integers(len(v),size=(samples,len(v)))].mean(axis=1)
    return [float(x) for x in np.quantile(means,[.05,.95],method='linear')]


def disagreement(rows):
    per={};details=[]
    for (q,step),rs in sorted(group_states(rows).items()):
        nearest=min(rs,key=lambda r:(r['distance_norm'],r['node']))
        best=min(rs,key=lambda r:(-r['Gk'],r['distance_norm'],r['node']))
        gap=best['Gk']-nearest['Gk'];positive=gap>1e-12
        d=dict(query_id=q,split=nearest['split'],step=step,nearest_node=nearest['node'],oracle_node=best['node'],
               nearest_Gk=nearest['Gk'],oracle_Gk=best['Gk'],gap=gap,beneficial_disagreement=positive)
        details.append(d);per.setdefault(q,[]).append(d)
    queries=[dict(query_id=q,split=ds[0]['split'],states=len(ds),disagreement_fraction=statistics.mean(d['beneficial_disagreement'] for d in ds),mean_gap=statistics.mean(d['gap'] for d in ds),total_gap=sum(d['gap'] for d in ds)) for q,ds in sorted(per.items())]
    total=sum(q['total_gap'] for q in queries);ranked=sorted(queries,key=lambda q:(-q['total_gap'],q['query_id']))
    return dict(states=details,queries=queries,query_cluster_disagreement_mean=statistics.mean(q['disagreement_fraction'] for q in queries),
                disagreement_CI90=cluster_ci([q['disagreement_fraction'] for q in queries]),
                mean_query_gap=statistics.mean(q['mean_gap'] for q in queries),gap_CI90=cluster_ci([q['mean_gap'] for q in queries]),
                total_gap=total,top1_gap_share=ranked[0]['total_gap']/total if total else 0,
                top5_gap_share=sum(q['total_gap'] for q in ranked[:5])/total if total else 0,
                positive_gap_queries=sum(q['total_gap']>1e-12 for q in queries))


def design(rows,model):
    states=group_states(rows); margins={}
    for key,rs in states.items():
        d=sorted(r['distance_norm'] for r in rs);margins[key]=d[1]-d[0] if len(d)>1 else 0
    result=[]
    for r in rows:
        d=r['distance_norm'];rank=r['frontier_rank'];margin=margins[r['query_id'],r['step']]
        f=[d]
        if model!='distance_only':f += [rank,r['degree']/64,r['seen']/2000,r['step']/24]
        if model in ('cheap_margin','permuted_training_labels'):f += [d*d,rank*rank,d*margin,rank*margin,rank*r['step']/24]
        result.append(f)
    return np.asarray(result)


def fit_models(rows):
    train=[r for r in rows if r['split']=='train'];results={}
    if not train or any(not any(r['split']==s for r in rows) for s in ('validation','test')):raise ValueError('All query partitions required')
    for model in MODELS:
        X=design(train,model);mean=X.mean(axis=0);scale=X.std(axis=0);scale[scale<1e-12]=1
        X=np.column_stack([np.ones(len(X)),(X-mean)/scale]);y=np.asarray([r['Gk'] for r in train])
        if model=='permuted_training_labels':
            rng=random.Random(SEED)
            for rs in group_states(train).values():
                ix=[i for i,r in enumerate(train) if r['query_id']==rs[0]['query_id'] and r['step']==rs[0]['step']]
                perm=list(y[ix]);rng.shuffle(perm);y[ix]=perm
        penalty=np.eye(X.shape[1])*1e-3;penalty[0,0]=0
        coef=np.linalg.solve(X.T@X+penalty,X.T@y);evaluations={}
        for split in ('validation','test'):
            sub=[r for r in rows if r['split']==split];Z=np.column_stack([np.ones(len(sub)),(design(sub,model)-mean)/scale]);pred=Z@coef
            per_query={};changes=0;state_count=0;selected_values=[]
            for key,rs in group_states(sub).items():
                ix=[i for i,r in enumerate(sub) if (r['query_id'],r['step'])==key]
                pick=max(ix,key=lambda i:(pred[i],-sub[i]['distance_norm'],-sub[i]['node']))
                near=min(ix,key=lambda i:(sub[i]['distance_norm'],sub[i]['node']))
                changes+=pick!=near;state_count+=1;selected_values.append(sub[pick]['Gk'])
                per_query.setdefault(key[0],[]).append(sub[pick]['Gk']-sub[near]['Gk'])
            gains=[statistics.mean(v) for v in per_query.values()];ci=cluster_ci(gains)
            evaluations[split]=dict(queries=len(gains),states=state_count,changed_choices=changes,
                mean_selected_Gk=statistics.mean(selected_values),mean_query_gain=statistics.mean(gains),query_cluster_gain_CI90=ci,
                per_query_gain={str(k):statistics.mean(v) for k,v in per_query.items()},
                RMSE=float(np.sqrt(np.mean((pred-np.asarray([r['Gk'] for r in sub]))**2))),
                useful_signal=changes>0 and ci[0]>0)
        results[model]=dict(coefficients=coef.tolist(),train_mean=mean.tolist(),train_scale=scale.tolist(),**evaluations)
    return results


def branching(rows):
    pairs=[]
    for key,rs in sorted(group_states(rows).items()):
        rs=sorted(rs,key=lambda r:r['frontier_rank'])
        if len(rs)<2:continue
        gain=rs[1]['batch_marginal_Gk']
        pairs.append(dict(query_id=key[0],step=key[1],split=rs[0]['split'],first_Gk=rs[0]['Gk'],second_increment_Gk=gain,
                          fixed_two_expansion_union_Gk=rs[0]['Gk']+gain,second_has_useful_progress=gain>1e-12))
    per={}
    for r in pairs:per.setdefault(r['query_id'],[]).append(r['second_increment_Gk'])
    controls=[]
    # Equal nodes, scoring, expansion budget and p; adjacency is the controlled synthetic variable.
    families={'chain':{i:[i+1] if i<30 else [] for i in range(31)},
              'branching':{i:[v for v in (2*i+1,2*i+2) if v<31] for i in range(31)}}
    for family,g in families.items():
        for policy in ('sequential','distance_batch','random'):
            for seed in range(5):controls.append(dict(family=family,seed=seed,**simulate(g,policy,p=4,budget=24,seed=seed)))
    comparisons=[]
    for family in families:
        for seed in range(5):
            a=next(r for r in controls if r['family']==family and r['seed']==seed and r['policy']=='sequential')
            for b in [r for r in controls if r['family']==family and r['seed']==seed and r['policy']!='sequential']:
                comparisons.append(dict(family=family,seed=seed,policy=b['policy'],equal_quality=a['recall_at1']==b['recall_at1'],
                    recall_reference=a['recall_at1'],recall_target=b['recall_at1'],time_ratio=b['simulated_time']/a['simulated_time'],
                    equal_realized_expansion_count=a['expansions']==b['expansions']))
    return dict(real_graph_surrogate_pairs=pairs,mean_query_second_increment=statistics.mean(statistics.mean(v) for v in per.values()),
                increment_CI90=cluster_ci([statistics.mean(v) for v in per.values()]),
                synthetic_rows=controls,quality_controlled_comparisons=comparisons,
                scope='Real static union has fixed2 expansions but no adaptive second-step counterfactual/latency. Synthetic equal-budget comparisons are interpretable as quality-matched ONLY where equal_quality=true. Not ANN speedups.')


def execute(path,output):
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    plan=dict(protocol='ISSUE29_ORACLE_DISAGREEMENT_v1',source_rows_sha256=sha(path),code_sha256=sha(__file__),seed=SEED,
              models=MODELS,ridge=1e-3,bootstrap_samples=20000,unit='whole query',CI=.90,
              selection_ties='prediction then nearest distance then lowest node ID',
              target='Saved Gk fixed-state normalized exact-distance top10 sum improvement; no ground truth features',
              validation='Original28/10/10 query split preserved; test was previously inspected, so this is reused-held-out audit, not untouched prospective validation. No model tuning on validation/test.',
              decision='Require changed choices plus positive lower query-cluster gain CI on validation AND reused test to justify FRESH query replication. Never claim online benefit.',
              controls='Distance-only; degree/history; within-training-state permuted labels. Prior overlap feature remains NO-GO in tested placement.')
    (out/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');(out/'PLAN.sha256').write_text(sha(out/'PLAN.json')+'  PLAN.json\n')
    rows=load_rows(path);result=dict(status='OFFLINE_EXECUTED',candidate_rows=len(rows),queries=len({r['query_id'] for r in rows}),
                                   disagreement={split:disagreement([r for r in rows if split=='all' or r['split']==split]) for split in ('all','train','validation','test')},
                                   models=fit_models(rows),frontier=branching(rows))
    (out/'SUMMARY.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    for name,data in [('states',result['disagreement']['all']['states']),('queries',result['disagreement']['all']['queries'])]:
        with (out/(name+'.csv')).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rows',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=execute(a.rows,a.output)
    print(json.dumps(dict(status=r['status'],candidate_rows=r['candidate_rows'],queries=r['queries'],models={k:v['test'] for k,v in r['models'].items()}),indent=2))
