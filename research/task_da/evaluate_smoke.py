"""Recall@k for explicit smoke rows against MS-Turing split IDs/distances GT.

This is neither an exact-oracle validator nor a performance evaluator.
"""
import argparse
import json
import math
import mmap
from pathlib import Path
import struct


def evaluate(rows, gt_path, base_count, k):
    if type(base_count) is not int or not 0 < k <= base_count or not rows or len(rows) > 32:
        raise ValueError("invalid smoke shape")
    with Path(gt_path).open('rb') as stream:
        size = Path(gt_path).stat().st_size
        if size < 8:
            raise ValueError("truncated GT")
        with mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            nq, width = struct.unpack_from('<II', data)
            if not nq or not width or k > width or size != 8 + 8 * nq * width:
                raise ValueError("GT must contain header, all IDs, then all float distances")
            seen, intersection = set(), 0
            for row in rows:
                q = row['query_id']
                if type(q) is not int or q in seen or not 0 <= q < nq:
                    raise ValueError("invalid/duplicate query ID")
                seen.add(q)
                if row.get('scope') != 'CORRECTNESS_SMOKE_NOT_BENCHMARK':
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
                if any(not math.isfinite(x) or x < 0 for x in td) or list(td) != sorted(td):
                    raise ValueError("invalid GT distances")
                intersection += len(set(ids) & set(truth[:k]))
            return dict(scope='SMOKE_RECALL_ONLY_NOT_P1_GATE_PASS', queries=len(rows), k=k,
                        recall_at_k=intersection / (k * len(rows)),
                        incomplete_top_k_queries=sum(len(row['ids']) < k for row in rows),
                        gt_distance_semantics='NOT_USED_FOR_RECALL', benchmark_executed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rows', type=Path)
    parser.add_argument('ground_truth', type=Path)
    parser.add_argument('--base-count', type=int, required=True)
    parser.add_argument('--k', type=int, required=True)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.rows.read_text().splitlines() if line.strip()]
    print(json.dumps(evaluate(rows, args.ground_truth, args.base_count, args.k), indent=2))


if __name__ == '__main__':
    main()
