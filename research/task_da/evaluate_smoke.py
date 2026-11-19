"""Recall@k for explicit smoke rows against MS-Turing split IDs/distances GT.

This is neither an exact-oracle validator nor a performance evaluator.
"""
import argparse
import json
import math
import mmap
from pathlib import Path
import struct
import sys


def _evaluate_rows(
    rows,
    gt_path,
    base_count,
    k,
    *,
    gt_aux_min=0.0,
    expected_scope='CORRECTNESS_SMOKE_NOT_BENCHMARK',
    max_rows=32,
    expected_query_ids=None,
    result_scope='SMOKE_RECALL_ONLY_NOT_P1_GATE_PASS',
):
    if (
        type(base_count) is not int
        or not 0 < k <= base_count
        or not rows
        or (max_rows is not None and len(rows) > max_rows)
    ):
        raise ValueError("invalid smoke shape")
    if (
        isinstance(gt_aux_min, bool)
        or not isinstance(gt_aux_min, (int, float))
        or not math.isfinite(gt_aux_min)
        or not -1e-4 <= gt_aux_min <= 0.0
    ):
        raise ValueError("invalid gt_aux_min")
    with Path(gt_path).open('rb') as stream:
        size = Path(gt_path).stat().st_size
        if size < 8:
            raise ValueError("truncated GT")
        with mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            nq, width = struct.unpack_from('<II', data)
            if not nq or not width or k > width or size != 8 + 8 * nq * width:
                raise ValueError("GT must contain header, all IDs, then all float distances")
            seen, intersection, query_hits = set(), 0, []
            neg_aux_count, neg_aux_queries = 0, 0
            for row in rows:
                q = row['query_id']
                if type(q) is not int or q in seen or not 0 <= q < nq:
                    raise ValueError("invalid/duplicate query ID")
                seen.add(q)
                if row.get('scope') != expected_scope:
                    raise ValueError("wrong result scope")
                ids, distances = row['ids'], row['squared_l2']
                if len(ids) > k or len(ids) != len(distances) or len(set(ids)) != len(ids):
                    raise ValueError("invalid result length/duplicates")
                if any(type(i) is not int or not 0 <= i < base_count for i in ids):
                    raise ValueError("invalid result ID")
                if any(type(d) not in (float, int) or not math.isfinite(d) or d < 0 for d in distances):
                    raise ValueError("invalid result distance")
                if list(zip(distances, ids)) != sorted(zip(distances, ids)):
                    raise ValueError("results not ordered by distance/ID")
                truth = struct.unpack_from('<'+'I'*width, data, 8 + q * width * 4)
                td = struct.unpack_from('<'+'f'*width, data, 8 + nq * width * 4 + q * width * 4)
                if len(set(truth)) != width or any(i >= base_count for i in truth):
                    raise ValueError("invalid GT IDs")
                if any(not math.isfinite(x) or x < gt_aux_min for x in td) or list(td) != sorted(td):
                    raise ValueError("invalid GT distances")
                row_neg = sum(1 for x in td if x < 0.0)
                if row_neg:
                    neg_aux_count += row_neg
                    neg_aux_queries += 1
                hits = len(set(ids) & set(truth[:k]))
                intersection += hits
                query_hits.append(hits / k)
            if expected_query_ids is not None:
                expected_set = set(expected_query_ids)
                if len(expected_set) != len(expected_query_ids) or seen != expected_set:
                    raise ValueError("evaluated query IDs do not match expected split")
            n_rows = len(rows)
            mean_recall = intersection / (k * n_rows)
            if n_rows > 1:
                var = sum((x - mean_recall) ** 2 for x in query_hits) / (n_rows - 1)
                se = math.sqrt(var / n_rows)
                ci95_half = 1.96 * se
            else:
                se, ci95_half = 0.0, 0.0
            return dict(scope=result_scope, queries=n_rows, k=k,
                        hits=intersection, total_slots=k * n_rows,
                        recall_at_k=mean_recall,
                        recall_std_err=se,
                        recall_ci95_low=max(0.0, mean_recall - ci95_half),
                        recall_ci95_high=min(1.0, mean_recall + ci95_half),
                        incomplete_top_k_queries=sum(len(row['ids']) < k for row in rows),
                        gt_distance_semantics=('ID_ONLY_WITH_OPT_IN_BOUNDED_AUX_NEGATIVE_TOLERANCE'
                                               if gt_aux_min < 0.0 else 'NOT_USED_FOR_RECALL'),
                        gt_aux_min=float(gt_aux_min),
                        accepted_negative_gt_distances=neg_aux_count,
                        accepted_negative_gt_queries=neg_aux_queries,
                        benchmark_executed=False)


def evaluate(rows, gt_path, base_count, k, *, gt_aux_min=0.0):
    summary = _evaluate_rows(rows, gt_path, base_count, k, gt_aux_min=gt_aux_min)
    for drop_key in ('hits', 'total_slots', 'recall_std_err', 'recall_ci95_low', 'recall_ci95_high'):
        summary.pop(drop_key, None)
    return summary


def _normalize_argv(argv):
    """Allow negative scientific-notation values like '--gt-aux-min -1e-5'."""
    out = []
    i = 0
    while i < len(argv):
        if argv[i] == '--gt-aux-min' and i + 1 < len(argv):
            try:
                float(argv[i + 1])
                out.append(f'--gt-aux-min={argv[i + 1]}')
                i += 2
                continue
            except ValueError:
                pass
        out.append(argv[i])
        i += 1
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rows', type=Path)
    parser.add_argument('ground_truth', type=Path)
    parser.add_argument('--base-count', type=int, required=True)
    parser.add_argument('--k', type=int, required=True)
    parser.add_argument('--gt-aux-min', type=float, default=0.0,
                        help='Opt-in lower bound in [-1e-4, 0.0] for finite monotonic GT auxiliary distances')
    args = parser.parse_args(_normalize_argv(sys.argv[1:] if argv is None else list(argv)))
    rows = [json.loads(line) for line in args.rows.read_text().splitlines() if line.strip()]
    try:
        result = evaluate(rows, args.ground_truth, args.base_count, args.k, gt_aux_min=args.gt_aux_min)
    except ValueError as err:
        parser.error(str(err))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
