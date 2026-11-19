"""Full P1 validator and ON/OFF parity checker (reuses evaluate_smoke contract)."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from .evaluate_smoke import _evaluate_rows, _normalize_argv


def _load_query_ids(path: Path) -> list[int]:
    ids = [int(tok) for tok in path.read_text(encoding='utf-8').split() if tok.strip()]
    if not ids or len(set(ids)) != len(ids) or any(q < 0 for q in ids):
        raise ValueError(f'invalid query_ids list: {path}')
    return ids


def _load_jsonl(path: Path) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    if not rows:
        raise ValueError(f'empty JSONL: {path}')
    return rows


def check_on_off_parity(on_rows: list[dict], off_rows: list[dict], base_count: int) -> dict:
    """Verify exact per-query ID/distance equality and ON counter invariants."""
    if len(on_rows) != len(off_rows):
        raise ValueError(f'ON/OFF row count mismatch: {len(on_rows)} vs {len(off_rows)}')
    on_by_q = {r['query_id']: r for r in on_rows}
    off_by_q = {r['query_id']: r for r in off_rows}
    if set(on_by_q) != set(off_by_q) or len(on_by_q) != len(on_rows):
        raise ValueError('ON/OFF query ID set mismatch')

    totals = dict(distance_evaluations=0, expansions=0, neighbor_attempts=0,
                  already_seen_attempts=0, frontier_insertions=0)
    mismatches = 0
    for qid, r_on in on_by_q.items():
        r_off = off_by_q[qid]
        if r_on.get('instrumentation') != 'ON' or r_off.get('instrumentation') != 'OFF':
            raise ValueError(f'wrong instrumentation label on q={qid}')
        if r_off.get('counters') is not None:
            raise ValueError(f'OFF row has non-null counters on q={qid}')
        c = r_on.get('counters')
        if not isinstance(c, dict):
            raise ValueError(f'ON row missing counters dict on q={qid}')
        if (
            r_on['ids'] != r_off['ids']
            or r_on['squared_l2'] != r_off['squared_l2']
            or r_on['complete_top_k'] != r_off['complete_top_k']
        ):
            mismatches += 1
        de = c['distance_evaluations']
        ex = c['expansions']
        na = c['neighbor_attempts']
        as_ = c['already_seen_attempts']
        fi = c['frontier_insertions']
        if de != 1 + na - as_:
            raise ValueError(f'counter balance invariant failed on q={qid}')
        if not (0 < ex <= fi <= de <= base_count):
            raise ValueError(f'counter monotonicity bound failed on q={qid}')
        for k_name in totals:
            totals[k_name] += c[k_name]

    if mismatches:
        raise ValueError(f'ON/OFF output mismatches: {mismatches}')
    n = len(on_rows)
    return dict(
        queries_checked=n,
        exact_ids_match=True,
        exact_squared_l2_match=True,
        exact_complete_top_k_match=True,
        counter_invariants_pass=True,
        off_counters_all_null=True,
        mismatches=0,
        mean_counters={k: v / n for k, v in totals.items()},
    )


def evaluate_p1(
    jsonl_path: Path,
    gt_path: Path,
    *,
    base_count: int,
    k: int,
    gt_aux_min: float = 0.0,
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
        expected_scope='P1_VALIDATION_NOT_BENCHMARK',
        max_rows=None,
        expected_query_ids=expected_qids,
        result_scope='P1_FULL_EVAL_NOT_P3_BENCHMARK',
    )
    result['jsonl_path'] = str(jsonl_path)
    result['jsonl_sha256'] = hashlib.sha256(jsonl_path.read_bytes()).hexdigest()
    result['beam'] = rows[0].get('beam')
    result['instrumentation'] = rows[0].get('instrumentation')
    if parity_off_path is not None:
        off_rows = _load_jsonl(parity_off_path)
        result['on_off_parity'] = check_on_off_parity(rows, off_rows, base_count)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rows', type=Path)
    parser.add_argument('ground_truth', type=Path)
    parser.add_argument('--base-count', type=int, required=True)
    parser.add_argument('--k', type=int, required=True)
    parser.add_argument('--gt-aux-min', type=float, default=0.0)
    parser.add_argument('--query-ids', type=Path, default=None)
    parser.add_argument('--parity-off', type=Path, default=None)
    args = parser.parse_args(_normalize_argv(list(sys.argv[1:] if argv is None else argv)))
    try:
        out = evaluate_p1(
            args.rows,
            args.ground_truth,
            base_count=args.base_count,
            k=args.k,
            gt_aux_min=args.gt_aux_min,
            query_ids_path=args.query_ids,
            parity_off_path=args.parity_off,
        )
    except ValueError as err:
        parser.error(str(err))
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
