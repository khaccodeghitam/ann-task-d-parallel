#!/usr/bin/env python3
"""Offline E1 export checker; no search, timing, tuning or campaign certification.

JSON schema (one complete run):
 {"base_count": N, "search_wall_ns": positive_number,
  "queries": [{"query_id": int, "ids": [100 distinct ints], "latency_ns": number}]}
GT schema: {"base_count": N, "queries": [{"query_id": int, "ids": [100 distinct ints]}]}.
IDs define strict ID-based Recall@100, not distance-tie-expanded recall. GT is
read only by this offline tool. Exported timings must come from a qualified
native driver; this checker cannot establish their truth or hardware fairness.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path


def _positive(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")


def _rows(document, timed):
    n = document.get("base_count")
    if type(n) is not int or n < 100:
        raise ValueError("base_count must be an integer >= 100")
    rows = document.get("queries")
    if not isinstance(rows, list) or not rows:
        raise ValueError("queries must be a nonempty list")
    out = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("query rows must be objects")
        qid, ids = row.get("query_id"), row.get("ids")
        if type(qid) is not int or qid < 0 or qid in out:
            raise ValueError("query IDs must be unique nonnegative integers")
        if (not isinstance(ids, list) or len(ids) != 100
                or any(type(i) is not int or not 0 <= i < n for i in ids)
                or len(set(ids)) != 100):
            raise ValueError("each query must have exactly 100 unique in-range integer IDs")
        if timed:
            _positive(row.get("latency_ns"), "latency_ns")
        out[qid] = row
    return out


def _quantile(values, p):
    position = p * (len(values) - 1)
    lo = math.floor(position)
    hi = math.ceil(position)
    return values[lo] + (values[hi] - values[lo]) * (position - lo)


def summarize(run, truth):
    if not isinstance(run, dict) or not isinstance(truth, dict):
        raise ValueError("run and ground truth must be objects")
    actual, expected = _rows(run, True), _rows(truth, False)
    if run["base_count"] != truth["base_count"] or actual.keys() != expected.keys():
        raise ValueError("base sizes and complete query ID sets must match")
    _positive(run.get("search_wall_ns"), "search_wall_ns")
    if max(r["latency_ns"] for r in actual.values()) > run["search_wall_ns"]:
        raise ValueError("query latency exceeds the enclosing search wall interval")
    recalls = [len(set(row["ids"]) & set(expected[qid]["ids"])) / 100
               for qid, row in sorted(actual.items())]
    times = sorted(row["latency_ns"] for row in actual.values())
    return dict(evidence="IMPLEMENTED_NOT_BENCHMARKED", scope="OFFLINE_EXPORT_METRICS_ONLY",
                query_count=len(times), recall_at_100=sum(recalls) / len(recalls),
                recall_definition="mean |unique returned top100 IDs intersect GT top100 IDs| / 100",
                qps=len(times) * 1e9 / run["search_wall_ns"],
                latency_ns={f"p{percent}": _quantile(times, percent / 100)
                            for percent in (50, 95, 99)},
                quantile_method="linear p*(n-1)",
                caveat="Input metrics only; requires separate identity, correctness and safety evidence")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--ground-truth", type=Path, required=True)
    args = parser.parse_args()
    raw_run, raw_truth = args.run.read_bytes(), args.ground_truth.read_bytes()
    result = summarize(json.loads(raw_run), json.loads(raw_truth))
    result["input_sha256"] = dict(run=hashlib.sha256(raw_run).hexdigest(),
                                  ground_truth=hashlib.sha256(raw_truth).hexdigest())
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
