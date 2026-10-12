#!/usr/bin/env python3
"""Passive plan/analysis helpers for the pinned OSDI artifact. Never launches ANN.

The default artifact build rejects mem_L=0 and fails GCC13 AVX2 compilation.
This module does not repair either condition or authorize a different binary.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import random
import re
import statistics

PAPER = "d18dcd16fece1c9d1dea356d783ebba2ed649e54"
MODERN = "b9ec4ba86ff5d70bec277984777197f28dc2cf42"
INPUT = "47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3"
INDEX = "8955f8bca0c8ebb5afbd2a69e9760fc829d22ba76a4ef7b482339e88b2489595"
CELLS = ("PAPER_T1", "PAPER_T4", "PAPER_T8", "PAPER_T16", "MODERN_T8", "MODERN_T16")


def canonical_bytes(obj):
    return (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for data in iter(lambda: f.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def run_order():
    rows = []
    for block in range(6):
        for cell in CELLS[block:] + CELLS[:block]:
            version, t = cell.split("_T")
            rows.append(dict(stage="primary", block=block + 1, cell=cell,
                             version=version, threads=int(t), wcap=32, l_search=100))
    # Four non-L100 cells per version, alternating version order, rotated L.
    ls = (50, 75, 125, 150)
    for rep in range(3):
        for j, l in enumerate(ls[rep:] + ls[:rep]):
            for version in (("PAPER", "MODERN") if (rep + j) % 2 == 0
                            else ("MODERN", "PAPER")):
                rows.append(dict(stage="recall", block=rep + 1, cell=f"{version}_L{l}",
                                 version=version, threads=8, wcap=32, l_search=l))
    for rep in range(3):
        for w in ((16, 64) if rep % 2 == 0 else (64, 16)):
            rows.append(dict(stage="width", block=rep + 1, cell=f"PAPER_W{w}",
                             version="PAPER", threads=8, wcap=w, l_search=100))
    return [dict(sequence=i + 1, **r) for i, r in enumerate(rows)]


def search_argv(binary, prefix, query, truth, case, mem_l=0):
    if case["version"] not in ("PAPER", "MODERN"):
        raise ValueError("Unknown version")
    argv = [str(binary), "uint8", str(prefix), str(case["threads"]), str(case["wcap"]),
            str(query), str(truth), "10", "l2"]
    if case["version"] == "MODERN":
        argv.append("pq")
    return argv + ["2", str(mem_l), str(case["l_search"])]


def parse_output(text, version, l_search, wcap):
    """One printed measurement row; label alone never defines percentile."""
    if version not in ("PAPER", "MODERN"):
        raise ValueError("Unknown version")
    if re.search(r"(?:\bERROR\b|\bFailed\b|Mismatch|Unknown distance|Unknown search|"
                 r"mem_L = 0|No valid Lsearch|File size mismatch)", text, re.I):
        raise ValueError("Benchmark diagnostics indicate failure")
    rows = []
    for line in text.splitlines():
        fields = line.split()
        if len(fields) != 8 or not re.fullmatch(r"\d+", fields[0]):
            continue
        try:
            vals = [float(x) for x in fields]
        except ValueError:
            continue
        if int(vals[0]) == l_search and int(vals[1]) == wcap:
            rows.append(vals)
    if len(rows) != 1:
        raise ValueError("Exactly one expected measurement row required")
    _, _, qps, lat, tail, hops, ios, recall = rows[0]
    if not all(math.isfinite(v) for v in rows[0]) or min(qps, lat, tail) <= 0:
        raise ValueError("Nonfinite/nonpositive performance metric")
    if min(hops, ios) < 0 or not 0 <= recall <= 100:
        raise ValueError("Invalid work/recall metric")
    return dict(qps=qps, mean_latency_us=lat, p50_latency_us=None, p95_latency_us=None,
                p99_latency_us=tail if version == "MODERN" else None,
                p999_latency_us=tail if version == "PAPER" else None,
                mean_hops=hops, mean_ios=ios, recall=recall)


def quantile(values, p):
    if not values or not 0 <= p <= 1:
        raise ValueError("Invalid quantile")
    vals = sorted(values)
    x = p * (len(vals) - 1)
    a, b = math.floor(x), math.ceil(x)
    return vals[a] + (vals[b] - vals[a]) * (x - a)


def descriptive(values):
    if not values or not all(math.isfinite(v) for v in values):
        raise ValueError("Finite run values required")
    med = statistics.median(values)
    return dict(n=len(values), values=list(values), mean=statistics.mean(values), median=med,
                sample_sd=statistics.stdev(values) if len(values) > 1 else None,
                min=min(values), max=max(values), mad=statistics.median(abs(v-med) for v in values))


def paired(target, reference, samples=20000, seed=20261012):
    if len(target) != len(reference) or not target or any(v <= 0 for v in reference):
        raise ValueError("Complete positive-reference blocks required")
    deltas = [100 * (a / b - 1) for a, b in zip(target, reference)]
    result = descriptive(deltas)
    rng = random.Random(seed)
    boot = [statistics.median(rng.choices(deltas, k=len(deltas))) for _ in range(samples)]
    result.update(ci90=[quantile(boot, .05), quantile(boot, .95)],
                  bootstrap_samples=samples, bootstrap_seed=seed, statistical_unit="block")
    return result


def validate_records(plan, records, audits):
    """Strict complete-suite ledger validation, with no outcome-based retries."""
    if plan.get("execution_ready") is not True:
        raise ValueError("Source/build/semantic readiness gates have not passed")
    if len(records) != len(plan["order"]):
        raise ValueError("Incomplete suite; never backfill/reuse historical runs")
    seen = set()
    for case, record in zip(plan["order"], records):
        if record["run_id"] in seen:
            raise ValueError("Duplicate/reused run")
        seen.add(record["run_id"])
        for key in ("sequence", "stage", "block", "cell", "threads", "wcap", "l_search"):
            if record.get(key) != case[key]:
                raise ValueError(f"Order/configuration mismatch: {key}")
        version = case["version"]
        if record.get("subject_commit") != {"PAPER": PAPER, "MODERN": MODERN}[version]:
            raise ValueError("Subject mismatch")
        if record.get("binary_sha256") != plan["binaries"][version]:
            raise ValueError("Binary mismatch")
        if record.get("input_package_sha256") != INPUT:
            raise ValueError("Input mismatch")
        if record.get("index_package_sha256") != plan["indexes"][version]:
            raise ValueError("Index mismatch")
        for key in ("checksums_valid", "environment_valid", "telemetry_valid", "quality_valid"):
            if record.get(key) is not True:
                raise ValueError(f"Required evidence absent/invalid: {key}")
        if record.get("exit_code") != 0 or record.get("status") != "accepted":
            raise ValueError("Failed/aborted run")
    if audits.get("pre_audits_pass") is not True or audits.get("post_audits_pass") is not True:
        raise ValueError("Full pre/post audits required")
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--show-order", action="store_true")
    p.add_argument("--plan", type=Path)
    p.add_argument("--records", type=Path)
    p.add_argument("--audits", type=Path)
    p.add_argument("--plan-sha256")
    args = p.parse_args()
    if args.show_order:
        print(json.dumps(run_order(), indent=2))
    elif args.plan and args.records and args.audits and args.plan_sha256:
        if digest(args.plan) != args.plan_sha256:
            raise ValueError("Frozen plan digest mismatch")
        validate_records(json.loads(args.plan.read_text()), json.loads(args.records.read_text()),
                         json.loads(args.audits.read_text()))
        print('{"complete_suite_valid": true}')
    else:
        p.error("Use --show-order or --plan PLAN --plan-sha256 SHA --records LEDGER --audits AUDITS; no execution interface exists")


if __name__ == "__main__":
    main()
