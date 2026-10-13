#!/usr/bin/env python3
"""Bounded offline graph/state studies. NOT PipeANN replay or online optimization."""
import argparse
import csv
import heapq
import json
import math
import mmap
import os
from pathlib import Path
import random
import resource
import struct
import sys
import numpy as np


class GraphReader:
    def __init__(self,path,limit_nodes=20000,memory_budget_mib=512):
        self.file=Path(path).open('rb');self.mm=mmap.mmap(self.file.fileno(),0,access=mmap.ACCESS_READ)
        if struct.unpack_from('<II',self.mm)!=(9,1):raise ValueError('Paper split metadata required')
        self.meta=struct.unpack_from('<9Q',self.mm,8);self.n,self.d=self.meta[:2];self.width,self.slots=self.meta[3:5]
        if self.d!=128 or self.width!=388 or self.slots!=10 or len(self.mm)!=self.meta[7]:raise ValueError('Wrong paper geometry')
        self.cache={};self.limit=limit_nodes;self.memory_budget=memory_budget_mib*2**20
    def offset(self,node):
        if not 0<=node<self.n:raise ValueError('Node out of range')
        return 4096+(node//self.slots)*4096+(node%self.slots)*self.width
    def vector(self,node):
        # Sparse random vector reads must not fault-around an entire multi-GB mmap.
        raw=os.pread(self.file.fileno(),128,self.offset(node))
        if len(raw)!=128:raise ValueError('Truncated vector')
        return np.frombuffer(raw,dtype='u1').astype(np.int32)
    def neighbors(self,node):
        if node not in self.cache:
            if len(self.cache)>=self.limit:raise ValueError('Adjacency sample capacity exhausted')
            off=self.offset(node);degree=struct.unpack_from('<I',self.mm,off+128)[0]
            if not 0<degree<=64:raise ValueError('Invalid degree')
            ns=struct.unpack_from('<'+str(degree)+'I',self.mm,off+132)
            if len(set(ns))!=len(ns) or any(x>=self.n for x in ns):raise ValueError('Invalid edges')
            self.cache[node]=ns
            if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024>self.memory_budget:raise MemoryError('RSS exceeds declared budget')
        return self.cache[node]
    def close(self):self.mm.close();self.file.close()


def jaccard(a,b):
    a,b=set(a),set(b);return len(a&b)/len(a|b) if a or b else 0.


def motif_counts(graph,u):
    ns=set(graph[u]);transitive=cycles=0
    for v in ns:
        transitive+=len(ns&set(graph.get(v,())))
        for w in graph.get(v,()):cycles+=int(u in graph.get(w,()))
    return dict(transitive_ordered_wedges=transitive,three_cycles_rooted=cycles)


def utility(top,k):
    if len(top)<k:raise ValueError('Partial top-k has no finite threshold utility here')
    return sum(sorted(top)[:k])


def one_step(current,novel,k=10):
    # Entries are (distance,node_id); deterministic distance/id ties.
    if len(current)<k:raise ValueError('Partial top-k excluded')
    old=sorted(current)[:k];eligible={n:d for d,n in novel if n not in {n for _,n in current}}
    after=sorted(old+[(d,n) for n,d in eligible.items()])[:k];tau=old[-1][0]
    return dict(G1=max(0,tau-min(eligible.values())) if eligible else 0,
                Gk=(sum(d for d,_ in old)-sum(d for d,_ in after))/max(1,sum(d for d,_ in old)),
                useful=sum(d<tau for d in eligible.values()),novel=len(eligible),after=after)


def rankdata(values):
    result=np.zeros(len(values));order=sorted(range(len(values)),key=lambda i:(values[i],i));i=0
    while i<len(order):
        j=i+1
        while j<len(order) and values[order[j]]==values[order[i]]:j+=1
        for v in order[i:j]:result[v]=(i+j-1)/2
        i=j
    return result


def spearman(a,b):
    x,y=rankdata(a),rankdata(b)
    return float(np.corrcoef(x,y)[0,1]) if np.std(x)>0 and np.std(y)>0 else None


def real_study(index,query,out,seed=20261013,n_queries=48,limit_nodes=20000,memory_budget_mib=1024):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);g=GraphReader(index,limit_nodes,memory_budget_mib);rng=random.Random(seed)
    qdata=np.memmap(query,mode='r',dtype='u1',offset=8,shape=(10000,128));qids=rng.sample(range(10000),n_queries)
    rows=[];topology=[];distance_evals=0
    # Uniform anchors; one sampled directed wedge/cycle opportunity each, not all-edge enumeration.
    for u in rng.sample(range(g.n),2000):
        nu=g.neighbors(u);v=rng.choice(nu);w=rng.choice(g.neighbors(v));other=rng.choice(nu)
        topology.append(dict(u=u,degree=len(nu),sampled_transitive_closure=int(other in g.neighbors(v)),sampled_cycle_closure=int(u in g.neighbors(w)),edge_jaccard=jaccard(nu,g.neighbors(v))))
    for qi,qid in enumerate(qids):
        q=qdata[qid].astype(np.int32);dist={};front=[];seen=set();expanded=set();last=g.meta[2]
        def d(node):
            nonlocal distance_evals
            if node not in dist:
                delta=g.vector(node)-q;dist[node]=int(np.dot(delta,delta));distance_evals+=1
                if distance_evals>300000:raise ValueError('Distance budget exhausted')
            return dist[node]
        seen.add(last);heapq.heappush(front,(d(last),last))
        for step in range(25):
            if step in (8,24):
                candidates=heapq.nsmallest(12,front);current=[(dist[x],x) for x in seen];tau=sorted(current)[9][0]
                batch=set()
                for rank,(dv,v) in enumerate(candidates):
                    ns=g.neighbors(v);novel=[(d(u),u) for u in ns if u not in seen];value=one_step(current,novel)
                    overlap=jaccard(ns,g.neighbors(last));without=one_step(current,[(d(u),u) for u in batch])['Gk']
                    plus=one_step(current,[(d(u),u) for u in batch|set(ns) if u not in seen])['Gk']
                    rows.append(dict(query_id=qid,split='train' if qi<28 else 'validation' if qi<38 else 'test',step=step,node=v,
                                     distance_norm=dv/max(1,tau),frontier_rank=rank/12,degree=len(ns),seen=len(seen),
                                     overlap=overlap,G1=value['G1'],Gk=value['Gk'],novel=value['novel'],useful=value['useful'],batch_marginal_Gk=plus-without))
                    if rank<2:batch.update(ns)
            if step==24:break
            while front and front[0][1] in expanded:heapq.heappop(front)
            if not front:break
            _,v=heapq.heappop(front);expanded.add(v);last=v
            for u in g.neighbors(v):
                if u not in seen:seen.add(u);heapq.heappush(front,(d(u),u))
    def feature(r,motif=False):
        f=[1,r['distance_norm'],r['frontier_rank'],r['degree']/64,r['seen']/2000,r['step']/24]
        return f+[r['overlap']] if motif else f
    train=[r for r in rows if r['split']=='train'];val=[r for r in rows if r['split']=='validation'];test=[r for r in rows if r['split']=='test']
    def fit_eval(motif,permuted=False):
        tr=[dict(r) for r in train];te=[dict(r) for r in test];va=[dict(r) for r in val]
        if permuted:
            # Degree-stratified permutation; this graph has constant degree64. Query splits preserved.
            for subset in [tr,te,va]:
                values=[r['overlap'] for r in subset];random.Random(seed+77).shuffle(values)
                for r,v in zip(subset,values):r['overlap']=v
        X=np.array([feature(r,motif) for r in tr]);y=np.array([r['Gk'] for r in tr]);coef=np.linalg.solve(X.T@X+np.eye(X.shape[1])*1e-6,X.T@y)
        pred=np.array([feature(r,motif) for r in te])@coef;actual=np.array([r['Gk'] for r in te]);selected=[];baseline=[];best=[];correlations=[]
        query_gain={}
        for key in sorted({(r['query_id'],r['step']) for r in te}):
            ix=[i for i,r in enumerate(te) if (r['query_id'],r['step'])==key];p=max(ix,key=lambda i:(pred[i],-te[i]['frontier_rank']));a=min(ix,key=lambda i:te[i]['distance_norm'])
            selected.append(te[p]['Gk']);baseline.append(te[a]['Gk']);best.append(max(te[i]['Gk'] for i in ix));rho=spearman([pred[i] for i in ix],[actual[i] for i in ix])
            if rho is not None:correlations.append(rho)
            query_gain.setdefault(str(key[0]),[]).append(te[p]['Gk']-te[a]['Gk'])
        gains=[float(np.mean(v)) for v in query_gain.values()];bootrng=random.Random(seed);boot=[float(np.mean(bootrng.choices(gains,k=len(gains)))) for _ in range(2000)]
        vp=np.array([feature(r,motif) for r in va])@coef
        return dict(test_RMSE=float(np.sqrt(np.mean((pred-actual)**2))),validation_RMSE=float(np.sqrt(np.mean((vp-np.array([r['Gk'] for r in va]))**2))),
                    mean_state_spearman=float(np.mean(correlations)) if correlations else None,mean_selected_Gk=float(np.mean(selected)),distance_only_choice_Gk=float(np.mean(baseline)),oracle_best_Gk=float(np.mean(best)),
                    query_cluster_gain_CI90=[float(np.quantile(boot,.05)),float(np.quantile(boot,.95))],per_query_gain=query_gain)
    models={name:fit_eval(*args) for name,args in [('distance_degree_history',(False,False)),('plus_overlap',(True,False)),('permuted_overlap',(True,True))]}
    result=dict(study=['MOTIF_SIGNAL_STUDY_01','CANDIDATE_VALUE_ORACLE_01'],status='EXECUTED_REAL_GRAPH',seed=seed,queries=qids,query_split=[28,10,10],states=2*n_queries,candidate_rows=len(rows),adjacency_nodes_read=len(g.cache),distance_evaluations=distance_evals,
                uniform_topology_anchors=len(topology),sampled_transitive_closure_rate=float(np.mean([r['sampled_transitive_closure'] for r in topology])),sampled_cycle_closure_rate=float(np.mean([r['sampled_cycle_closure'] for r in topology])),mean_edge_jaccard=float(np.mean([r['edge_jaccard'] for r in topology])),
                positive_Gk_fraction=float(np.mean([r['Gk']>0 for r in rows])),mean_novel_neighbors=float(np.mean([r['novel'] for r in rows])),mean_useful_novel_neighbors=float(np.mean([r['useful'] for r in rows])),models=models,peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Independent bounded exact-distance traversal states, not paper/PQ runtime replay. Labels fork fixed Seen/topK; union expansion uses deterministic distance/id ties. No ground truth enters online features. Static one-step batch utility only; no multi-hop counterfactual or submodularity claim.',
                feature_cost='Exact overlap requires unread candidate adjacency or precomputed metadata; it is not a free online feature. One4-byte value per640M directed edges would cost2.56GB before indexing overhead.',
                limitations=['Uniform-node wedge samples are not full motif counts or query-access samples','Induced subgraph not used; full outgoing adjacency queried read-only','Two states/query are clustered; train/validation/test split by whole query','Exact-distance surrogate differs from PQ admission and asynchronous search','Motif feature has unavailable-at-runtime information unless paid metadata/I/O cost','No end-to-end speedup or novelty conclusion'])
    with (out/'candidate_rows.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    (out/'SUMMARY.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');g.close();return result


def synthetic_graphs():
    chain={i:[i+1] if i<23 else [] for i in range(24)}
    tree={i:[x for x in [2*i+1,2*i+2] if x<63] for i in range(63)}
    cluster={i:list(dict.fromkeys([(i//8)*8+j for j in range(8) if (i//8)*8+j!=i]+([i+8] if i+8<32 else []))) for i in range(32)}
    decoy={0:list(range(1,9))+[33]}
    for i in range(1,33):decoy[i]=[1+(i-1+j)%32 for j in range(1,17)]
    decoy[33]=[34];decoy[34]=[]
    bridge={i:[i+1] if i<15 else [] for i in range(16)};bridge[0]+=[16,17,18];bridge.update({16:[17,18],17:[16,18],18:[16,17]})
    return dict(chain=chain,branching_tree=tree,clustered_triangles=cluster,bridge=bridge,decoy_dense_cluster=decoy)


def simulate(graph,policy,p=4,budget=24,seed=0):
    rng=random.Random(seed);goal=max(graph);scores={u:abs(goal-u) for u in graph}
    if 'x' in graph:raise ValueError('Numeric graph IDs required')
    if len(graph)==35:scores.update({u:u for u in range(1,33)});scores[33]=100;scores[34]=0
    frontier={0};seen={0};done=set();clock=0.;first_goal=None;distance_evals=1;duplicates=0;depth={0:1};batch_records=[]
    while frontier and len(done)<budget:
        ranked=sorted(frontier,key=lambda u:(scores[u],u));width=1 if policy=='sequential' else p
        if policy in ('sequential','same_budget_best_first','distance_batch'):batch=ranked[:width]
        elif policy=='random':batch=rng.sample(ranked,min(width,len(ranked)))
        else:
            batch=ranked[:1]
            while len(batch)<min(width,len(ranked)):
                candidates=[u for u in ranked if u not in batch]
                pick=min(candidates,key=lambda u:(max(jaccard(graph[u],graph[v]) for v in batch),scores[u],u));batch.append(pick)
        batch=batch[:budget-len(done)];new=set();local_dup=0
        for u in batch:
            for v in graph[u]:
                if v in seen or v in new:local_dup+=1
                else:new.add(v);depth[v]=depth[u]+1
        evaluations=len(new);distance_evals+=evaluations;duplicates+=local_dup
        # Fixed5 service units, shared2-request service capacity,0.01/distance,p compute lanes, scheduling cost.
        duration=max(5.,5*len(batch)/2)+.01*evaluations/p+.05*len(batch);clock+=duration
        for u in batch:frontier.remove(u);done.add(u)
        frontier.update(new);seen.update(new)
        if goal in new and first_goal is None:first_goal=clock
        batch_records.append(dict(batch=batch,new=len(new),duplicates=local_dup,finish=clock))
    work=5*len(done)+.01*distance_evals;span=5*max((depth[u] for u in done),default=0)
    return dict(policy=policy,p=p,budget=budget,expansions=len(done),distance_evaluations=distance_evals,duplicate_discoveries=duplicates,work_units=work,dependency_span_service_units=span,ideal_lower_bound=max(work/p,span),simulated_time=clock,recall_at1=int(goal in seen),first_goal_time=first_goal)


def frontier_study(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);rows=[]
    for name,g in synthetic_graphs().items():
        for policy in ['sequential','same_budget_best_first','distance_batch','random','anchor_explore']:
            for seed in range(5):rows.append(dict(graph=name,seed=seed,**simulate(g,policy,seed=seed)))
    result=dict(status='EXECUTED',study='PARALLEL_FRONTIER_SIM_01',rows=rows,scope='Synthetic directed graphs only; synchronous discrete-event batches, shared IO capacity2, p4, equal24-expansion budget. Simulated service units are not real CPU/SSD time. Same-budget best-first and distance-batch intentionally coincide; they are not distinct wins. Anchor exploration pays oracle adjacency-feature assumption; no recall guarantee.')
    (out/'SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('study',choices=['real','frontier']);p.add_argument('--index',type=Path);p.add_argument('--query',type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--limit-nodes',type=int,default=20000);p.add_argument('--memory-budget-mib',type=int,default=1024)
    a=p.parse_args()
    if a.study=='real':
        if not a.index or not a.query:p.error('--index and --query required')
        v=real_study(a.index,a.query,a.output,limit_nodes=a.limit_nodes,memory_budget_mib=a.memory_budget_mib)
    else:v=frontier_study(a.output)
    print(json.dumps({k:v[k] for k in v if k not in ('rows','queries','models')},indent=2))
