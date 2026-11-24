"""Frozen p2 G2 analysis; no subprocess, ANN execution, or split generation."""
import argparse
import fcntl
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import time

import numpy as np

from .g2_v2_contract import (BLOCKS, BOOTSTRAPS, CPUS, GRAPHS, N, POLICIES, QUERY_BLOCK,
                             PROTOCOL, REVISION, SCHEMA, SEED, THETA, TIE_EPS, Z_FLOOR, load_freeze, number,
                             require, sha, validate_schema, write_new)
from .evaluate_p2 import validate_p2_counters_row

CONTRASTS = {'fast_base_vs_stock_base':((0,0),(1,0)),
             'fast_opt_vs_stock_opt':((0,1),(1,1)),
             'fast_opt_vs_stock_base':((0,0),(1,1)),
             'fast_opt_vs_fast_base':((1,0),(1,1))}


def _betacf(a, b, x):
    c, d = 1., 1 - (a+b)*x/(a+1)
    d = 1 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 401):
        for aa in (m*(b-m)*x/((a-1+2*m)*(a+2*m)),
                   -(a+m)*(a+b+m)*x/((a+2*m)*(a+1+2*m))):
            d, c = 1+aa*d, 1+aa/c
            d = 1 / (d if abs(d) > 1e-300 else 1e-300)
            c = c if abs(c) > 1e-300 else 1e-300
            delta = d*c
            h *= delta
        if abs(delta-1) < 1e-14:
            return h
    raise ValueError('incomplete beta did not converge')


def _beta(a, b, x):
    if x <= 0: return 0.
    if x >= 1: return 1.
    bt = math.exp(math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)+a*math.log(x)+b*math.log1p(-x))
    return bt*_betacf(a,b,x)/a if x < (a+1)/(a+b+2) else 1-bt*_betacf(b,a,1-x)/b


def tcrit(p, df):
    require(0 < p < 1 and df > 0, 'invalid t quantile')
    lo, hi = -100., 100.
    for _ in range(90):
        mid = (lo+hi)/2
        v = .5*_beta(df/2, .5, df/(df+mid*mid))
        cdf = 1-v if mid >= 0 else v
        if cdf < p: lo = mid
        else: hi = mid
    return (lo+hi)/2


def ci(values, *, critical=None):
    a = np.asarray(values, dtype=float)
    require(a.ndim == 1 and len(a) > 1 and np.isfinite(a).all(), 'invalid CI observations')
    k = tcrit(.975, len(a)-1) if critical is None else critical
    mean, margin = float(a.mean()), float(k*a.std(ddof=1)/math.sqrt(len(a)))
    return [mean-margin, mean+margin]


def reduction(x):
    return float(-math.expm1(-x))


def ram_pair(base_kib, opt_kib):
    b, c = number(base_kib, positive=True), number(opt_kib, positive=True)
    require(b.is_integer() and c.is_integer(),'RSS must be positive integer KiB')
    budget = max(65536., .10*b)
    return dict(delta_kib=c-b, budget_kib=budget, normalized=(c-b)/budget,
                hard_pass=(10*(int(c)-int(b)) <= max(655360,int(b))))


def output_rows(path):
    with Path(path).open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def output_digest(rows, *, mode, policy):
    digest, qids = hashlib.sha256(), []
    for row in rows:
        require(row['mode'] == mode and row['instrumentation'] is (mode == 'ON'), 'mode/instrumentation mismatch')
        require(row['workers'] == 2 and row['sync_interval'] == 16 and row['beam'] == 432
                and row['jobs'] == 1 and row['merge_impl'] == 'flat', 'search configuration mismatch')
        visited, frontier = POLICIES[policy]
        require(row['visited_policy'] == visited and row['frontier_mode'] == frontier, 'policy mismatch')
        ids, distances, q = row['ids'], row['squared_l2'], row['query_id']
        require(type(q) is int and 0 <= q < 100000, 'invalid query ID')
        require(len(ids) == len(distances) == 10 and len(set(ids)) == 10 and row['complete_top_k'] is True,
                'incomplete/nonunique Top10')
        require(all(type(i) is int and 0 <= i < 1000000 for i in ids), 'invalid returned ID')
        digest.update(struct.pack('<I', q))
        for i, d in zip(ids, distances):
            number(d)
            digest.update(struct.pack('<Id', i, d))
        if mode == 'ON': validate_p2_counters_row(row, 1000000)
        else: require(row['counters'] is None, 'OFF counters must be null')
        qids.append(q)
    require(len(qids) == len(set(qids)) and bool(qids), 'empty/duplicate query output')
    return digest.hexdigest(), qids


def pair_on(base, opt):
    bd, bq = output_digest(base, mode='ON', policy='base')
    od, oq = output_digest(opt, mode='ON', policy='opt')
    require(bd == od and bq == oq, 'base/opt exact parity failed')
    ignored = {'distance_evaluations', 'duplicate_distance_evaluations', 'already_seen_attempts',
               'per_worker_distance_evaluations', 'sync_wait_ns', 'barrier_wait_ns', 'merge_time_ns', 'worker_idle_ns'}
    saved = 0
    for b, c in zip(base, opt):
        u, v = b['counters'], c['counters']
        require({k:x for k,x in u.items() if k not in ignored} == {k:x for k,x in v.items() if k not in ignored},
                'B1/A1 invariant failed')
        delta = u['duplicate_distance_evaluations']-v['duplicate_distance_evaluations']
        require(delta >= 0 and u['distance_evaluations']-v['distance_evaluations'] == delta
                and v['already_seen_attempts']-u['already_seen_attempts'] == delta, 'saved-L2 accounting failed')
        saved += delta
    return dict(parity=True, output_digest=bd, queries=len(bq), duplicate_l2_saved=saved)


def quality_gate(recalls):
    a = np.asarray(recalls, dtype=float)
    require(a.shape == (6, N) and np.isfinite(a).all() and ((a >= 0) & (a <= 1)).all(), 'invalid Recall matrix')
    require(np.allclose(a*10,np.rint(a*10),rtol=0,atol=1e-12),'Recall must be integer hits /10')
    means = a.mean(axis=1)
    lower = means-Z_FLOOR*a.std(axis=1,ddof=1)/math.sqrt(N)
    d = a[3:].mean(axis=0)-a[:3].mean(axis=0)
    interval = ci(d)
    return dict(A_pass=bool(np.all(lower >= .990)), B_pass=bool(interval[0] > -.0005+TIE_EPS and interval[1] < .0005-TIE_EPS),
                recall=means.tolist(), lcb95=lower.tolist(), arm_difference=float(d.mean()), arm_ci95=interval)


def weighted_tails(values, cluster, counts):
    """Exact type-7 p95/p99 of integer-weighted samples, in bounded batches."""
    require(np.isfinite(values).all() and np.all(values > 0), 'invalid latency sample')
    require(np.all(counts >= 0) and np.all(counts.sum(axis=1) == counts.shape[1]), 'invalid bootstrap counts')
    n = len(values)
    result = np.empty((len(counts), 2))
    if np.all(values == values[0]):
        result[:] = values[0]
        return result
    ordered = np.argsort(values, kind='stable')
    sorted_values, sorted_cluster = values[ordered], cluster[ordered]
    for start in range(0, len(counts), 16):
        weights = counts[start:start+16, sorted_cluster]
        cumulative = np.cumsum(weights, axis=1, dtype=np.int64)
        for k, q in enumerate((.95, .99)):
            pos = q*(n-1); lo = int(pos); hi = math.ceil(pos)
            l = np.argmax(cumulative > lo, axis=1); h = np.argmax(cumulative > hi, axis=1)
            result[start:start+16,k] = sorted_values[l]*(1-(pos-lo))+sorted_values[h]*(pos-lo)
    return result


def bootstrap(latency, *, joint, resamples=BOOTSTRAPS, block_length=QUERY_BLOCK):
    """Generic dimensions only for synthetic fixtures; production locks 12x6x2x10000."""
    a = np.asarray(latency, dtype=float)
    require(a.ndim == 4 and a.shape[2] == 2 and a.shape[3] % block_length == 0
            and np.isfinite(a).all() and (a > 0).all(), 'invalid paired latency tensor')
    m, g, _, n = a.shape; k = n//block_length
    rng = random.Random(SEED)
    counts = np.zeros((resamples,k), dtype=np.int32)
    proc = np.empty((resamples,m), dtype=np.int32)
    for b in range(resamples):
        proc[b] = [rng.randrange(m) for _ in range(m)] if joint else np.arange(m)
        for _ in range(k): counts[b,rng.randrange(k)] += 1
    block_sums = a.reshape(m,g,2,k,block_length).sum(axis=-1)
    means = np.einsum('rk,mgpk->rmgp', counts, block_sums, optimize=True)/n
    tail = np.empty((resamples,m,g,2,2))
    cluster = np.arange(n)//block_length
    for b in range(m):
        for j in range(g):
            for p in range(2):
                tail[:,b,j,p,:] = weighted_tails(a[b,j,p], cluster, counts)
    idx = np.arange(resamples)[:,None]
    means = means[idx,proc]; tail = tail[idx,proc]
    x = np.log(means[:,:,:,0]/means[:,:,:,1]).mean(axis=(1,2))
    u = np.log(tail[:,:,:,1,:]/tail[:,:,:,0,:]).mean(axis=1)
    delta = {}
    if g == 6:
        arms = means.reshape(resamples,m,2,3,2).mean(axis=(1,3))
        for label,(ref,target) in CONTRASTS.items():
            values = arms[:,ref[0],ref[1]]-arms[:,target[0],target[1]]
            delta[label] = np.quantile(values,[.025,.975],method='linear').tolist()
    return dict(resamples=resamples,query_block_length=block_length,scheme='joint' if joint else 'query_only',
                primary_log_ci95=np.quantile(x,[.025,.975],method='linear').tolist(),
                latency_contrast_delta_ci95_us=delta,
                tail_log_upper95=np.quantile(u,.95,axis=0,method='linear').tolist())


def build_search(means, quality, build, joint):
    if build is None: return dict(status='BUILD_REFERENCE_NOT_SUPPLIED')
    require(set(build)==set(GRAPHS),'incomplete frozen BUILD reference')
    for row in build.values():
        number(row['wall_s'],positive=True);number(row['graph_bytes'],positive=True)
    b = [float(np.mean([build[g]['wall_s'] for g in GRAPHS[i:i+3]])) for i in (0,3)]
    result = dict(status='HOLD_QUALITY_B',build_graphs=build,mean_build_stock_s=b[0],mean_build_fast_s=b[1],
                  uncertainty='conditional on fixed historical BUILD receipts; population CI NOT_ESTIMABLE',
                  deployment='two hosts; transfer/load excluded and UNKNOWN')
    if quality.get('B_pass') is not True: return result
    if quality.get('B_authorized') is not True:
        result['status']='NOT_AUTHORIZED_B'
        return result
    arms = means.reshape(12,2,3,2).mean(axis=2)
    result['contrasts'] = {}
    for label,(ref,target) in CONTRASTS.items():
        u,v = arms[:,ref[0],ref[1]],arms[:,target[0],target[1]]
        delta = u-v; delta_b = b[ref[0]]-b[target[0]]
        slope = float(delta.mean())/1e6
        root = -delta_b/slope if slope else None
        values = dict(log_latency_ratio_ci95=ci(np.log(u/v)),mean_search_delta_us=float(delta.mean()),
                      positive_break_even_queries=root if root is not None and root>0 else None,workloads={})
        for q in (1,100000,1000000):
            t = delta_b+q*delta/1e6
            boot = [delta_b+q*d/1e6 for d in joint['latency_contrast_delta_ci95_us'][label]]
            values['workloads'][str(q)] = dict(saved_s=float(t.mean()),ci95_s=ci(t),joint_ci95_s=boot)
        result['contrasts'][label]=values
    comparisons=result['contrasts']
    main=comparisons['fast_opt_vs_stock_base']['workloads']['100000']
    result['status'] = ('GO_B_SYSTEM_FIXED_COHORT' if min(main['ci95_s'][0],main['joint_ci95_s'][0])>TIE_EPS
                        and all(comparisons[k]['workloads']['100000']['saved_s']>0
                                for k in ('fast_opt_vs_fast_base','fast_opt_vs_stock_opt')) else 'HOLD_B_SYSTEM_UNCERTAINTY')
    return result


def analyze(rows, latency, quality, *, build=None):
    require(quality.get('A_pass') is True and quality.get('parity') is True, 'quality A receipt required')
    keys = [(r['block'],r['graph'],r['policy']) for r in rows]
    wanted = {(b,g,p) for b in range(BLOCKS) for g in GRAPHS for p in POLICIES}
    require(len(keys) == len(set(keys)) == 144 and set(keys) == wanted, 'missing/duplicate process pair')
    by = dict(zip(keys, rows)); means = np.empty((12,6,2)); tails = np.empty((12,6,2,2)); ram = np.empty((12,6))
    for b in range(12):
        for j,g in enumerate(GRAPHS):
            for p,policy in enumerate(POLICIES):
                r = by[b,g,policy]
                require(r['valid'] is True and r['mode'] == 'OFF' and r['observed_cpus'] == CPUS
                        and r['beam'] == 432 and r['query_count'] == N, 'invalid process receipt')
                means[b,j,p] = number(r['mean_us'],positive=True)
                for k,q in enumerate(('p95_us','p99_us')): tails[b,j,p,k] = number(r[q],positive=True)
                for name in ('p50_us','qps_wall','cpu_seconds','wall_seconds'): number(r[name],positive=True)
                require(r['p50_us'] <= r['p95_us'] <= r['p99_us'], 'nonmonotonic percentiles')
                require(abs(r['cpu_percent']-100*r['cpu_seconds']/r['wall_seconds']) < 1e-7, 'CPU utilization inconsistent')
                require(abs(r['cpu_capacity_percent']-r['cpu_percent']/2) < 1e-7, 'CPU capacity normalization inconsistent')
            ram[b,j] = ram_pair(by[b,g,'base']['rss_kib'],by[b,g,'opt']['rss_kib'])['normalized']
    a = np.asarray(latency, dtype=float)
    require(a.shape == (12,6,2,N) and np.isfinite(a).all() and (a>0).all(), 'full paired query tensor required')
    require(np.allclose(a.mean(axis=-1), means, rtol=1e-8,atol=1e-8), 'mean/raw mismatch')
    quant = np.quantile(a,[.95,.99],axis=-1,method='linear').transpose(1,2,3,0)
    require(np.allclose(quant,tails,rtol=1e-8,atol=1e-8), 'tail/raw mismatch')
    x = np.log(means[:,:,0]/means[:,:,1]); xb = x.mean(axis=1)
    primary, drift = ci(xb), ci(xb.reshape(6,2).mean(axis=1))
    query, joint = bootstrap(a,joint=False), bootstrap(a,joint=True)
    critical = tcrit(1-.05/18,11)
    u = np.log(tails[:,:,1,:]/tails[:,:,0,:])
    upper_tail = u.mean(axis=0)+critical*u.std(axis=0,ddof=1)/math.sqrt(12)
    upper_ram = ram.mean(axis=0)+critical*ram.std(axis=0,ddof=1)/math.sqrt(12)
    stable = bool(np.all(x.mean(axis=0)>0) and np.all(x.reshape(12,2,3).mean(axis=(0,2))>=THETA)
                  and all(np.delete(x,j,axis=1).mean()>=THETA for j in range(6)))
    hard_ram = bool(np.all(ram<=1))
    safe = bool(hard_ram and np.all(upper_ram<=1) and np.all(upper_tail<=np.log([1.05,1.10]))
                and np.all(np.array(joint['tail_log_upper95'])<=np.log([1.05,1.10])))
    gain = min(primary[0],drift[0],joint['primary_log_ci95'][0]) > THETA+TIE_EPS
    verdict = 'GO_A_FIXED_COHORT' if gain and stable and safe and quality.get('duplicate_reduction') is True else 'HOLD'
    if primary[1] < THETA-TIE_EPS and ci(x[:,3:].mean(axis=1))[1] < THETA-TIE_EPS:
        verdict = 'PIVOT_TO_TASK_A'
    lower_tail = u.mean(axis=0)-critical*u.std(axis=0,ddof=1)/math.sqrt(12)
    lower_ram = ram.mean(axis=0)-critical*ram.std(axis=0,ddof=1)/math.sqrt(12)
    if np.any(lower_tail>np.log([1.05,1.10])) or np.any(lower_ram>1):
        verdict = 'PIVOT_TO_TASK_A'
    metrics = {}
    for graph in GRAPHS:
        metrics[graph] = {}
        for policy in POLICIES:
            metrics[graph][policy] = {}
            for field in ('mean_us','p50_us','p95_us','p99_us','qps_wall','rss_kib','cpu_percent','cpu_capacity_percent'):
                values = [by[b,graph,policy][field] for b in range(12)]
                metrics[graph][policy][field] = dict(mean=float(np.mean(values)),min=float(min(values)),max=float(max(values)))
    secondary = build_search(means,quality,build,joint)
    if not safe and secondary['status']=='GO_B_SYSTEM_FIXED_COHORT':secondary['status']='HOLD_B_RESOURCES'
    return dict(schema=SCHEMA, protocol=PROTOCOL, revision=REVISION, verdict=verdict,
                primary_estimand='geometric_paired_mean_latency_ratio', primary_log_ci95=primary,
                primary_reduction=reduction(float(xb.mean())), primary_reduction_ci95=list(map(reduction,primary)),
                speedup=float(np.exp(xb.mean())), drift_log_ci95=drift, query_bootstrap=query, joint_bootstrap=joint,
                arithmetic_base_us=float(means[:,:,0].mean()), arithmetic_opt_us=float(means[:,:,1].mean()),
                arithmetic_reduction=float(1-means[:,:,1].mean()/means[:,:,0].mean()),
                graph_log_effects=x.mean(axis=0).tolist(), ram_hard_pass=hard_ram,
                primary_block_log_effects=xb.tolist(),graph_log_ci95=[ci(x[:,j]) for j in range(6)],
                arm_log_ci95={'stock':ci(x[:,:3].mean(axis=1)),'fast':ci(x[:,3:].mean(axis=1))},
                leave_one_out_log_effects=[float(np.delete(x,j,axis=1).mean()) for j in range(6)],
                metrics_by_graph_policy=metrics,
                ram_max_by_graph=ram.max(axis=0).tolist(), ram_mean_upper=upper_ram.tolist(),
                tail_log_upper=upper_tail.tolist(),tail_log_lower=lower_tail.tolist(),ram_mean_lower=lower_ram.tolist(),
                stability_pass=stable, safety_pass=safe,
                B_quality_pass=quality.get('B_pass') is True,
                build_search=secondary,
                graph_population_ci='NOT_ESTIMABLE', evidence_label='EXPLORATORY_HOST_SPECIFIC')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    with Path('/tmp/task-da-pivot-4650u.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        started=time.monotonic()
        freeze = load_freeze()
        from .g2_v2_runner import load_campaign
        rows, latency, quality = load_campaign(args.campaign)
        result = analyze(rows,latency,quality,build=freeze['build_reference'])
        require(time.monotonic()-started<=10800,'analysis quota exhausted; no GO output')
        validate_schema(result,'analysis')
        write_new(args.output, result)


if __name__ == '__main__': main()
