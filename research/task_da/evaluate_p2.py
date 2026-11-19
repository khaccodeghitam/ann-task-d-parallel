"""P2 multi-walker validator, counter-invariant checker, and exploratory quality/H2 summary."""
import argparse
import json
from pathlib import Path
import sys

from .evaluate_p1 import _load_jsonl, _load_query_ids
from .evaluate_smoke import _evaluate_rows, _normalize_argv


def validate_p2_counters_row(row: dict, base_count: int) -> dict:
    """Validate Mode ON P2 multi-walker counters and algebraic invariants on a single row."""
    qid = row.get('query_id')
    workers = row.get('workers')
    if workers not in (1, 2, 4):
        raise ValueError(f'invalid workers count on q={qid}: {workers}')
    c = row.get('counters')
    if not isinstance(c, dict):
        raise ValueError(f'ON row missing counters dict on q={qid}')

    de = c['distance_evaluations']
    u_de = c['unique_distance_evaluations']
    d_de = c['duplicate_distance_evaluations']
    ex = c['expansions']
    u_ex = c['unique_expansions']
    d_ex = c['duplicate_expansions']
    na = c['neighbor_attempts']
    as_ = c['already_seen_attempts']
    fi = c['frontier_insertions']
    sm = c['sync_merge_count']
    sw = c['sync_wait_ns']
    bw = c['barrier_wait_ns']
    mt = c['merge_time_ns']
    wi = c['worker_idle_ns']
    pw_exp = c['per_worker_expansions']
    pw_dist = c['per_worker_distance_evaluations']
    pw_idle = c['per_worker_idle_rounds']

    if de < 1 or de != 1 + na - as_:
        raise ValueError(f'P2 distance evaluation balance failed on q={qid}: de={de}, na={na}, as={as_}')
    if de != u_de + d_de or d_de < 0 or u_de < 1:
        raise ValueError(f'P2 unique/dup distance split failed on q={qid}')
    if ex < 1 or ex != u_ex + d_ex or d_ex < 0 or u_ex < 1:
        raise ValueError(f'P2 unique/dup expansion split failed on q={qid}')
    if not (u_ex <= u_de <= base_count) or fi < 1 or fi > de:
        raise ValueError(f'P2 counter monotonic bounds failed on q={qid}')
    if len(pw_exp) != workers or len(pw_dist) != workers or len(pw_idle) != workers:
        raise ValueError(f'P2 per-worker array length mismatch on q={qid}')
    if sum(pw_exp) != ex or sum(pw_dist) != de:
        raise ValueError(f'P2 per-worker sum mismatch on q={qid}')
    if any(v < 0 for v in pw_exp + pw_dist + pw_idle) or min(sm, sw, bw, mt, wi) < 0:
        raise ValueError(f'P2 negative counter on q={qid}')
    if workers == 1 and (d_ex != 0 or d_de != 0 or sm != 0 or sw != 0 or bw != 0 or mt != 0 or wi != 0 or pw_idle != [0]):
        raise ValueError(f'P2 workers=1 multi-worker overhead must be zero on q={qid}')
    return c


def check_p2_on_off_parity(on_rows: list[dict], off_rows: list[dict], base_count: int) -> dict:
    """Verify P2 ON/OFF structural parity, exact deterministic match, and multi-walker invariants."""
    if len(on_rows) != len(off_rows):
        raise ValueError(f'ON/OFF row count mismatch: {len(on_rows)} vs {len(off_rows)}')
    on_by_q = {r['query_id']: r for r in on_rows}
    off_by_q = {r['query_id']: r for r in off_rows}
    if set(on_by_q) != set(off_by_q) or len(on_by_q) != len(on_rows):
        raise ValueError('ON/OFF query ID set mismatch')

    workers = on_rows[0]['workers']
    scalar_keys = [
        'distance_evaluations', 'unique_distance_evaluations', 'duplicate_distance_evaluations',
        'expansions', 'unique_expansions', 'duplicate_expansions',
        'neighbor_attempts', 'already_seen_attempts', 'frontier_insertions',
        'sync_merge_count', 'sync_wait_ns', 'barrier_wait_ns', 'merge_time_ns', 'worker_idle_ns',
    ]
    totals = {k: 0 for k in scalar_keys}
    pw_exp_tot = [0] * workers
    pw_dist_tot = [0] * workers
    pw_idle_tot = [0] * workers
    mismatches = 0

    for qid, r_on in on_by_q.items():
        r_off = off_by_q[qid]
        if r_on.get('workers') != workers or r_off.get('workers') != workers:
            raise ValueError(f'workers mismatch across rows on q={qid}')
        if r_on.get('mode') != 'ON' or r_on.get('instrumentation') is not True:
            raise ValueError(f'wrong ON metadata on q={qid}')
        if r_off.get('mode') != 'OFF' or r_off.get('instrumentation') is not False or r_off.get('counters') is not None:
            raise ValueError(f'wrong OFF metadata or non-null counters on q={qid}')
        if r_on.get('jobs') != 1 or r_off.get('jobs') != 1:
            raise ValueError(f'inter-query jobs must be 1 on q={qid}')
        if (
            r_on['ids'] != r_off['ids']
            or r_on['squared_l2'] != r_off['squared_l2']
            or r_on['complete_top_k'] != r_off['complete_top_k']
        ):
            mismatches += 1

        c = validate_p2_counters_row(r_on, base_count)
        for key in scalar_keys:
            totals[key] += c[key]
        for w in range(workers):
            pw_exp_tot[w] += c['per_worker_expansions'][w]
            pw_dist_tot[w] += c['per_worker_distance_evaluations'][w]
            pw_idle_tot[w] += c['per_worker_idle_rounds'][w]

    if mismatches:
        raise ValueError(f'P2 ON/OFF output mismatches: {mismatches}')

    n = len(on_rows)
    mean_pw_exp = [v / n for v in pw_exp_tot]
    avg_worker_exp = (totals['expansions'] / n) / workers
    max_over_mean_imbalance = (max(mean_pw_exp) / avg_worker_exp) if avg_worker_exp > 0 else 1.0

    return dict(
        queries_checked=n,
        workers=workers,
        exact_ids_match=True,
        exact_squared_l2_match=True,
        exact_complete_top_k_match=True,
        counter_invariants_pass=True,
        off_counters_all_null=True,
        mismatches=0,
        mean_counters={k: totals[k] / n for k in scalar_keys},
        mean_per_worker_expansions=mean_pw_exp,
        mean_per_worker_distance_evaluations=[v / n for v in pw_dist_tot],
        mean_per_worker_idle_rounds=[v / n for v in pw_idle_tot],
        duplicate_expansion_rate=(totals['duplicate_expansions'] / totals['expansions']),
        duplicate_distance_eval_rate=(totals['duplicate_distance_evaluations'] / totals['distance_evaluations']),
        workload_imbalance_max_over_mean=max_over_mean_imbalance,
    )


def evaluate_p2(
    jsonl_path: Path,
    gt_path: Path,
    *,
    base_count: int,
    k: int,
    gt_aux_min: float = -1e-5,
    query_ids_path: Path | None = None,
    parity_off_path: Path | None = None,
) -> dict:
    rows = _load_jsonl(jsonl_path)
    expected_qids = _load_query_ids(query_ids_path) if query_ids_path else None
    result = _evaluate_rows(
        rows,
        gt_path,
        base_count,
        k,
        gt_aux_min=gt_aux_min,
        expected_scope='task_d_a_common_p2_exploratory',
        max_rows=None,
        expected_query_ids=expected_qids,
        result_scope='P2_EXPLORATORY_0990_EVAL',
    )
    result['workers'] = rows[0]['workers']
    result['beam'] = rows[0]['beam']
    result['mode'] = rows[0]['mode']
    if rows[0]['mode'] == 'ON':
        for row in rows:
            validate_p2_counters_row(row, base_count)
        result['counter_invariants_pass'] = True
    if parity_off_path is not None:
        off_rows = _load_jsonl(parity_off_path)
        result['on_off_parity'] = check_p2_on_off_parity(rows, off_rows, base_count)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Validate P2 multi-walker JSONL and compute Recall/H2 stats.')
    parser.add_argument('jsonl', type=Path)
    parser.add_argument('gt', type=Path)
    parser.add_argument('base_count', type=int)
    parser.add_argument('--k', type=int, default=10)
    parser.add_argument('--gt-aux-min', type=float, default=-1e-5)
    parser.add_argument('--query-ids', type=Path, default=None)
    parser.add_argument('--parity-off', type=Path, default=None)
    parser.add_argument('--out-json', type=Path, default=None)
    args = parser.parse_args(_normalize_argv(argv))
    res = evaluate_p2(
        args.jsonl,
        args.gt,
        base_count=args.base_count,
        k=args.k,
        gt_aux_min=args.gt_aux_min,
        query_ids_path=args.query_ids,
        parity_off_path=args.parity_off,
    )
    text = json.dumps(res, indent=2) + '\n'
    if args.out_json is not None:
        args.out_json.write_text(text, encoding='utf-8')
    sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
