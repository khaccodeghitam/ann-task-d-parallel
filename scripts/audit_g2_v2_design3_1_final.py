#!/usr/bin/env python3
"""Independent end-to-end final audit for A×D G2 v2 design-3.1 OFF_AB run2.

Strictly read-only with respect to frozen packages and raw evidence directories.
Re-verifies freezes, all 6 R90 v1.3 graphs, approval & HOLD isolation, 18/18
Quality ON (Gates A & B + all 17 mechanism counters), 144/144 OFF processes
(1,440,000 query rows, strict counters-absent schema, bit-exact ON/OFF parity,
guard telemetry replay, balanced 12x6x2 schedule), independent statistical &
bootstrap inference, and the BUILD-SEARCH model against frozen analyzer output.

Usage:
  env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT \\
    /home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python \\
    scripts/audit_g2_v2_design3_1_final.py --output /tmp/audit_results.json

Pass --skip-bootstrap for a fast (~15s) full raw-data/parity/guard/analytic audit
that skips only the 20,000-replicate weighted-tail bootstrap recomputation.
"""
import argparse
import hashlib
import json
import math
import random
import struct
import sys
from pathlib import Path

import numpy as np

GRAPHS = [
    "stock_off_r1", "stock_off_r2", "stock_off_r3",
    "fast_off_r1", "fast_off_r2", "fast_off_r3",
]
POLICIES = ["base", "opt"]
N = 10000
THETA = -math.log(0.97)
TIE_EPS = 1e-12
Z_FLOOR = 2.3939797998185884  # norm.ppf(1 - 0.05/6)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def spearman(x, y):
    ax, ay = np.asarray(x, dtype=float), np.asarray(y, dtype=float)

    def avg_ranks(a):
        order = np.argsort(a, kind="mergesort")
        ranks = np.empty(len(a), dtype=float)
        sa = a[order]
        i = 0
        while i < len(a):
            j = i + 1
            while j < len(a) and sa[j] == sa[i]:
                j += 1
            ranks[order[i:j]] = 0.5 * (i + j - 1) + 1.0
            i = j
        return ranks

    rx, ry = avg_ranks(ax), avg_ranks(ay)
    denom = float(np.std(rx) * np.std(ry))
    if denom == 0.0:
        return None
    return float(np.mean((rx - rx.mean()) * (ry - ry.mean())) / denom)


def parse_args():
    default_repo = Path(__file__).resolve().parent.parent
    default_ev = default_repo.parent / "artifact-evidence"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=default_repo,
                        help="Path to task-d repository root (default: parent of scripts/).")
    parser.add_argument("--evidence-root", type=Path, default=default_ev,
                        help="Path to external artifact-evidence root.")
    parser.add_argument("--output", type=Path, default=None,
                        help="Optional path to write full JSON audit report.")
    parser.add_argument("--skip-bootstrap", action="store_true",
                        help="Skip 10k+10k+2k bootstrap recomputation (fast raw+analytic check).")
    parser.add_argument("--skip-env-check", action="store_true",
                        help="Pass environment=False to load_freeze (for cross-host inspection).")
    return parser.parse_args()


def main():
    args = parse_args()
    repo = args.repo.resolve()
    ev = args.evidence_root.resolve()
    run2 = ev / "axd-g2-v2-off-design3_1_run2"
    analysis_path = ev / "axd-g2-v2-off-design3_1_run2-analysis.json"
    approval_run2 = ev / "axd-g2-v2-approvals/design3_1_off_approval_run2.json"
    qual_pass = ev / "axd-g2-v2-design3-qualification-20261124T094602Z/qualification_result.json"
    quality_dir = ev / "axd-g2-v2-quality-design3"
    hold_d31 = ev / "axd-g2-v2-off-design3_1"

    sys.path.insert(0, str(repo))
    from research.task_da import g2_v2_design3_1_analyzer as d31_analyzer
    from research.task_da import g2_v2_design3_1_contract as d31_contract
    from research.task_da import g2_v2_design3_1_runner as d31_runner
    from research.task_da import g2_v2_design3_guard as d3_guard

    def t_ci95(arr):
        a = np.asarray(arr, dtype=float)
        df = len(a) - 1
        k = d31_analyzer.tcrit(0.975, df)
        m = float(a.mean())
        se = float(a.std(ddof=1) / math.sqrt(len(a)))
        return m, se, [m - k * se, m + k * se]

    report = {"checks": {}, "discrepancies": []}

    def record_check(name, passed, detail):
        report["checks"][name] = {"pass": bool(passed), "detail": detail}
        if not passed:
            report["discrepancies"].append({"check": name, "detail": detail})

    # 1. Freeze, Environment, Artifacts (incl. all 6 R90 graphs, binary, .so, inputs, Stage 5 baselines)
    freeze = d31_contract.load_freeze(environment=not args.skip_env_check, check_parent=True)
    artifacts = json.loads((run2 / "artifacts.json").read_text())
    d31_runner.verify_artifacts(freeze, artifacts)
    graph_audit = {}
    for g in GRAPHS:
        gp = Path(artifacts["graphs"][g])
        gsha = sha256_file(gp)
        gbytes = gp.stat().st_size
        bref = freeze["build_reference"][g]
        ok = (gsha == freeze["graph_sha256"][g] == bref["graph_sha256"] and gbytes == bref["graph_bytes"])
        graph_audit[g] = {"sha256": gsha, "bytes": gbytes, "match_freeze_and_build": ok}
    record_check("freeze_and_artifacts_all_6_graphs", all(v["match_freeze_and_build"] for v in graph_audit.values()), {
        "freeze_sha256": sha256_file(d31_contract.FREEZE),
        "parent_design3_freeze_sha256": sha256_file(d31_contract.PARENT_DESIGN3_FREEZE),
        "artifacts_sha256": sha256_file(run2 / "artifacts.json"),
        "graphs": graph_audit,
        "total_graph_bytes": sum(v["bytes"] for v in graph_audit.values()),
    })

    # 2. Approval, Start, Complete, Qualification, Quality Context, HOLD isolation
    start = json.loads((run2 / "start.json").read_text())
    complete = json.loads((run2 / "complete.json").read_text())
    approval_disk = json.loads(approval_run2.read_text())
    approval_sha = sha256_file(approval_run2)
    d31_runner.verify_qualification(qual_pass, freeze=freeze)
    quality = d31_runner.quality_context(
        quality_dir / "quality.json",
        expected_artifacts_sha256=sha256_file(run2 / "artifacts.json"),
        expected_qualification_sha256=sha256_file(qual_pass),
    )
    scope = d31_contract.authorize(
        approval_disk,
        sha256_file(d31_contract.FREEZE),
        sha256_file(run2 / "artifacts.json"),
        "off",
        run2,
        qualification_digest=sha256_file(qual_pass),
        quality_digest=sha256_file(quality_dir / "quality.json"),
    )
    approval_matches_start = (start["approval"] == approval_disk)
    no_hold_json = not (run2 / "HOLD.json").exists()

    overlap_shas = set()
    if (hold_d31 / "HOLD.json").exists():
        hold_d31_json = json.loads((hold_d31 / "HOLD.json").read_text())
        overlap_shas = set(complete["receipts"].values()) & set(hold_d31_json["receipts"].values())
    start_text = (run2 / "start.json").read_text()
    analysis_text = analysis_path.read_text()
    hold_path_leak = (
        ('axd-g2-v2-off-design3"' in start_text)
        or ("axd-g2-v2-off-design3/" in start_text)
        or ("axd-g2-v2-off-design3_1/" in start_text)
        or ('axd-g2-v2-off-design3_1"' in start_text)
        or ("axd-g2-v2-off-design3/" in analysis_text)
        or ("axd-g2-v2-off-design3_1/" in analysis_text)
    )
    record_check(
        "approval_identity_and_hold_isolation",
        approval_matches_start and no_hold_json and scope == "OFF_AB" and len(overlap_shas) == 0 and not hold_path_leak,
        {
            "approval_sha256": approval_sha,
            "owner": approval_disk["owner"],
            "approved_at": approval_disk["approved_at"],
            "scope": scope,
            "quota_s": approval_disk["quota_s"],
            "elapsed_s": complete["elapsed_s"],
            "no_hold_json": no_hold_json,
            "approval_matches_start": approval_matches_start,
            "receipt_sha_overlap_with_run1_hold": len(overlap_shas),
            "hold_path_leak": hold_path_leak,
        },
    )

    # 3. Full Quality ON 18/18 independent replay & ALL 17 mechanism counters
    val_ids = d31_runner.ids(artifacts["val"])
    test_ids = d31_runner.ids(artifacts["test"])
    assert set(val_ids).isdisjoint(set(test_ids))
    with Path(artifacts["gt"]).open("rb") as stream:
        gt_hdr = struct.unpack("<II", stream.read(8))
        assert gt_hdr == (100000, 100)
    gt = np.memmap(artifacts["gt"], dtype="<u4", offset=8, shape=(100000, 100), mode="r")

    quality_replay = {"test": {}, "validation": {}}
    recall_mat = np.empty((6, N), dtype=float)
    counter_keys_scalar = sorted(d31_analyzer.SCALAR_COUNTER_KEYS)
    counter_keys_array = sorted(d31_analyzer.ARRAY_COUNTER_KEYS)

    for j, g in enumerate(GRAPHS):
        b_path = Path(quality["graphs"][g]["references"]["base"]["path"])
        o_path = Path(quality["graphs"][g]["references"]["opt"]["path"])
        b_rows = d31_analyzer.output_rows(b_path)
        o_rows = d31_analyzer.output_rows(o_path)
        pair_chk = d31_analyzer.pair_on(b_rows, o_rows)
        assert pair_chk["output_digest"] == quality["graphs"][g]["output_digest"]
        assert pair_chk["duplicate_l2_saved"] == quality["graphs"][g]["duplicate_l2_saved"]

        for qi, row in enumerate(b_rows):
            gt_top10 = set(map(int, gt[row["query_id"], :10]))
            recall_mat[j, qi] = len(set(row["ids"]) & gt_top10) / 10.0

        def agg_counters(rows):
            out = {}
            for k in counter_keys_scalar:
                vals = [r["counters"][k] for r in rows]
                out[k] = {"sum": int(sum(vals)), "mean_per_query": float(np.mean(vals))}
            for k in counter_keys_array:
                w0 = [r["counters"][k][0] for r in rows]
                w1 = [r["counters"][k][1] for r in rows]
                out[k] = {
                    "w0_sum": int(sum(w0)),
                    "w1_sum": int(sum(w1)),
                    "w0_mean": float(np.mean(w0)),
                    "w1_mean": float(np.mean(w1)),
                }
            return out

        cb = agg_counters(b_rows)
        co = agg_counters(o_rows)
        quality_replay["test"][g] = {
            "output_digest": pair_chk["output_digest"],
            "recall_mean": float(recall_mat[j].mean()),
            "recall_se": float(recall_mat[j].std(ddof=1) / math.sqrt(N)),
            "recall_lcb95": float(recall_mat[j].mean() - Z_FLOOR * recall_mat[j].std(ddof=1) / math.sqrt(N)),
            "duplicate_l2_saved": pair_chk["duplicate_l2_saved"],
            "dup_l2_reduction_pct": 100.0 * pair_chk["duplicate_l2_saved"] / cb["duplicate_distance_evaluations"]["sum"],
            "total_l2_reduction_pct": 100.0 * pair_chk["duplicate_l2_saved"] / cb["distance_evaluations"]["sum"],
            "base_counters": cb,
            "opt_counters": co,
        }

        vb_path = Path(artifacts["validation_root"]) / freeze["validation_baseline"][g]["path"]
        vo_path = quality_dir / f"b-1_{g}_opt_validation/beam_432_p2_ON.jsonl"
        vchk = d31_analyzer.pair_on(d31_analyzer.output_rows(vb_path), d31_analyzer.output_rows(vo_path))
        assert vchk["output_digest"] == quality["validation"][g]["output_digest"]
        assert vchk["duplicate_l2_saved"] == quality["validation"][g]["duplicate_l2_saved"]
        quality_replay["validation"][g] = vchk

    d_q = recall_mat[3:].mean(axis=0) - recall_mat[:3].mean(axis=0)
    d_mean, d_se, d_ci95 = t_ci95(d_q)
    gate_a_pass = bool(all(quality_replay["test"][g]["recall_lcb95"] >= 0.990 for g in GRAPHS))
    gate_b_pass = bool(d_ci95[0] > -0.0005 + TIE_EPS and d_ci95[1] < 0.0005 - TIE_EPS)
    q_max_diff = max(
        max(abs(quality_replay["test"][g]["recall_mean"] - quality["recall"][j]) for j, g in enumerate(GRAPHS)),
        max(abs(quality_replay["test"][g]["recall_lcb95"] - quality["lcb95"][j]) for j, g in enumerate(GRAPHS)),
        abs(d_mean - quality["arm_difference"]),
        abs(d_ci95[0] - quality["arm_ci95"][0]),
        abs(d_ci95[1] - quality["arm_ci95"][1]),
    )
    record_check("quality_on_18_of_18_and_gates_AB", gate_a_pass and gate_b_pass and q_max_diff < 1e-12, {
        "gate_A_pass": gate_a_pass,
        "gate_B_pass": gate_b_pass,
        "arm_difference": d_mean,
        "arm_se": d_se,
        "arm_ci95": d_ci95,
        "max_diff_vs_quality_json": q_max_diff,
        "stock_arm_mean_recall": float(recall_mat[:3].mean()),
        "fast_arm_mean_recall": float(recall_mat[3:].mean()),
        "inter_graph_span": float(recall_mat.mean(axis=1).max() - recall_mat.mean(axis=1).min()),
    })
    report["quality_mechanism"] = quality_replay

    # 4. Full independent audit of 144 OFF processes, 144 preflights, schedule balance, guard replay, raw JSONL
    sched = d31_runner.plan(artifacts, "off", run2)
    assert len(sched) == 144
    assert start["plan"] == sched, "start.json plan mismatch"

    pos_counts = {g: [0] * 6 for g in GRAPHS}
    order_counts = {g: {"base_first": 0, "opt_first": 0} for g in GRAPHS}
    pair_order_map = {}
    for b in range(12):
        blk = sched[b * 12:(b + 1) * 12]
        assert all(x["block"] == b for x in blk)
        seen_graphs = []
        for pos in range(6):
            p0, p1 = blk[2 * pos], blk[2 * pos + 1]
            assert p0["graph"] == p1["graph"]
            assert {p0["policy"], p1["policy"]} == {"base", "opt"}
            g = p0["graph"]
            seen_graphs.append(g)
            pos_counts[g][pos] += 1
            if p0["policy"] == "base":
                order_counts[g]["base_first"] += 1
                pair_order_map[(b, g)] = "AB"
            else:
                order_counts[g]["opt_first"] += 1
                pair_order_map[(b, g)] = "BA"
        assert set(seen_graphs) == set(GRAPHS)
    sched_balanced = (
        all(all(c == 2 for c in pos_counts[g]) for g in GRAPHS)
        and all(order_counts[g]["base_first"] == 6 and order_counts[g]["opt_first"] == 6 for g in GRAPHS)
    )

    latency = np.empty((12, 6, 2, N), dtype=float)
    means = np.empty((12, 6, 2), dtype=float)
    p50s = np.empty((12, 6, 2), dtype=float)
    p95s = np.empty((12, 6, 2), dtype=float)
    p99s = np.empty((12, 6, 2), dtype=float)
    qps_wall = np.empty((12, 6, 2), dtype=float)
    batch_wall_s = np.empty((12, 6, 2), dtype=float)
    proc_wall_s = np.empty((12, 6, 2), dtype=float)
    guard_wall_s = np.empty((12, 6, 2), dtype=float)
    cpu_s = np.empty((12, 6, 2), dtype=float)
    cpu_pct = np.empty((12, 6, 2), dtype=float)
    cpu_cap_pct = np.empty((12, 6, 2), dtype=float)
    rss_kib = np.empty((12, 6, 2), dtype=np.int64)
    f_wrk = np.empty((12, 6, 2), dtype=float)
    f_ccx = np.empty((12, 6, 2), dtype=float)
    f_all = np.empty((12, 6, 2), dtype=float)
    max_roll_wrk = np.empty((12, 6, 2), dtype=float)
    max_roll_ccx = np.empty((12, 6, 2), dtype=float)
    max_roll_all = np.empty((12, 6, 2), dtype=float)
    tctl_start = np.empty((12, 6, 2), dtype=float)
    tctl_max = np.empty((12, 6, 2), dtype=float)
    tctl_mean = np.empty((12, 6, 2), dtype=float)
    freq_worker_mean_mhz = np.empty((12, 6, 2), dtype=float)
    preflight_dur_s = []
    preflight_samples = []
    host_samples_list = []
    min_mem_avail = float("inf")
    min_free_disk = float("inf")
    max_swap_used = 0
    ac_values = set()
    rapl_nonempty = 0
    governors = set()
    platform_profiles = set()
    stderr_nonempty = 0
    counters_absent_rows = 0
    total_off_rows = 0
    parity_matches = 0
    guard_replay_failures = 0
    monotonic_order_ok = True
    prev_end_mono = -1.0
    recomputed_metrics_matches = 0
    file_count_per_dir = set()

    for item in sched:
        b = item["block"]
        j = GRAPHS.index(item["graph"])
        p = POLICIES.index(item["policy"])
        tname = item["name"]
        pdir = run2 / tname
        pf_path = run2 / f"{tname}_preflight.jsonl"

        file_count_per_dir.add(len(list(pdir.iterdir())))
        assert sha256_file(pf_path) == complete["preflight_sha256"][tname]
        assert sha256_file(pdir / "metrics.json") == complete["receipts"][tname]

        pf_rows = d31_analyzer.output_rows(pf_path)
        preflight_samples.append(len(pf_rows))
        preflight_dur_s.append(pf_rows[-1]["monotonic_s"] - pf_rows[0]["monotonic_s"])
        if pf_rows[0]["monotonic_s"] <= prev_end_mono:
            monotonic_order_ok = False

        manifest = json.loads((pdir / "manifest.json").read_text())
        metrics = json.loads((pdir / "metrics.json").read_text())
        summary = json.loads((pdir / "p2_eval_summary.json").read_text())
        host_rows = d31_analyzer.output_rows(pdir / "host.jsonl")
        host_samples_list.append(len(host_rows))

        if (pdir / "stderr.log").stat().st_size != 0:
            stderr_nonempty += 1

        if manifest["initial_host"]["monotonic_s"] <= prev_end_mono:
            monotonic_order_ok = False
        prev_end_mono = host_rows[-1]["monotonic_s"]

        replay = d3_guard.make_guard(manifest["initial_host"], phase="off")
        for s in host_rows:
            if replay.check(s, manifest["pid"]):
                guard_replay_failures += 1

        recomp = d31_runner.process_result(item, pdir, artifacts, manifest, phase="off")
        if recomp == metrics:
            recomputed_metrics_matches += 1

        raw_rows = d31_analyzer.output_rows(pdir / "beam_432_p2_OFF.jsonl")
        assert len(raw_rows) == N
        total_off_rows += len(raw_rows)
        counters_absent_rows += sum(1 for r in raw_rows if "counters" not in r)
        dig, qids = d31_analyzer.output_digest(raw_rows, mode="OFF", policy=item["policy"])
        assert qids == test_ids
        if dig == quality["graphs"][item["graph"]]["output_digest"] == metrics["output_digest"]:
            parity_matches += 1

        lats = np.array([r["latency_ns"] / 1000.0 for r in raw_rows], dtype=float)
        latency[b, j, p] = lats
        means[b, j, p] = float(lats.mean())
        p50s[b, j, p] = float(np.quantile(lats, 0.5, method="linear"))
        p95s[b, j, p] = float(np.quantile(lats, 0.95, method="linear"))
        p99s[b, j, p] = float(np.quantile(lats, 0.99, method="linear"))
        batch_wall_s[b, j, p] = summary["runs"][0]["batch_wall_ns"] / 1e9
        qps_wall[b, j, p] = N / batch_wall_s[b, j, p]
        proc_wall_s[b, j, p] = metrics["wall_seconds"]
        guard_wall_s[b, j, p] = manifest["wall_time_s"]
        cpu_s[b, j, p] = metrics["cpu_seconds"]
        cpu_pct[b, j, p] = metrics["cpu_percent"]
        cpu_cap_pct[b, j, p] = metrics["cpu_capacity_percent"]
        rss_kib[b, j, p] = int(summary["vm_hwm_kib"])
        f_wrk[b, j, p] = metrics["foreign_workers_fraction"]
        f_ccx[b, j, p] = metrics["foreign_ccx0_fraction"]
        f_all[b, j, p] = metrics["foreign_all_fraction"]
        max_roll_wrk[b, j, p] = metrics["max_rolling_foreign_workers_fraction"]
        max_roll_ccx[b, j, p] = metrics["max_rolling_foreign_ccx0_fraction"]
        max_roll_all[b, j, p] = metrics["max_rolling_foreign_all_fraction"]

        def get_tctl(sample):
            for v in sample["sensors"].values():
                if v.get("name") == "k10temp" and v.get("label") == "Tctl":
                    return float(v["value_C"])
            return None

        tctl_start[b, j, p] = get_tctl(manifest["initial_host"])
        tctls = [get_tctl(s) for s in host_rows if get_tctl(s) is not None]
        tctl_max[b, j, p] = max(tctls)
        tctl_mean[b, j, p] = float(np.mean(tctls))

        freqs = []
        for s in host_rows:
            min_mem_avail = min(min_mem_avail, s["mem_available"])
            min_free_disk = min(min_free_disk, s["free_disk"])
            max_swap_used = max(max_swap_used, s["swap_used"])
            ac_values.update(s["power"].values())
            if s.get("rapl"):
                rapl_nonempty += 1
            if "platform_profile" in s:
                platform_profiles.add(s["platform_profile"])
            for cid in (0, 2):
                ckey = f"/sys/devices/system/cpu/cpu{cid}/cpufreq/scaling_cur_freq"
                gkey = f"/sys/devices/system/cpu/cpu{cid}/cpufreq/scaling_governor"
                if ckey in s["cpu"]:
                    freqs.append(int(s["cpu"][ckey]) / 1000.0)
                if gkey in s["cpu"]:
                    governors.add(s["cpu"][gkey])
        freq_worker_mean_mhz[b, j, p] = float(np.mean(freqs))

    record_check(
        "144_off_execution_parity_guard_and_schedule",
        sched_balanced and total_off_rows == 1440000 and counters_absent_rows == 1440000
        and parity_matches == 144 and guard_replay_failures == 0
        and monotonic_order_ok and recomputed_metrics_matches == 144
        and stderr_nonempty == 0 and file_count_per_dir == {8},
        {
            "schedule_balanced_12x6x2": sched_balanced,
            "total_off_query_rows": total_off_rows,
            "counters_absent_rows": counters_absent_rows,
            "bit_exact_parity_processes": parity_matches,
            "guard_replay_failures": guard_replay_failures,
            "monotonic_non_overlapping": monotonic_order_ok,
            "recomputed_metrics_exact_matches": recomputed_metrics_matches,
            "stderr_nonempty_count": stderr_nonempty,
            "file_count_per_process_dir": sorted(file_count_per_dir),
            "preflight_dur_s_min_max": [float(min(preflight_dur_s)), float(max(preflight_dur_s))],
            "host_samples_min_max": [int(min(host_samples_list)), int(max(host_samples_list))],
            "min_mem_available_gib": min_mem_avail / (2**30),
            "min_free_disk_gib": min_free_disk / (2**30),
            "max_swap_used_bytes": int(max_swap_used),
            "ac_power_values": sorted(ac_values),
            "governors": sorted(governors),
            "platform_profiles": sorted(platform_profiles),
            "rapl_nonempty_samples": rapl_nonempty,
            "tctl_start_min_max_C": [float(tctl_start.min()), float(tctl_start.max())],
            "tctl_exec_max_C": float(tctl_max.max()),
            "tctl_exec_mean_base_vs_opt_C": [float(tctl_mean[:, :, 0].mean()), float(tctl_mean[:, :, 1].mean())],
            "freq_worker_mean_base_vs_opt_mhz": [float(freq_worker_mean_mhz[:, :, 0].mean()), float(freq_worker_mean_mhz[:, :, 1].mean())],
        },
    )

    # 5. Independent statistical audit & exact comparison against frozen analysis.json
    frozen_out = json.loads(analysis_path.read_text())

    x = np.log(means[:, :, 0] / means[:, :, 1])
    xb = x.mean(axis=1)
    xbar, xbar_se, primary_log_ci95 = t_ci95(xb)
    primary_red = float(-math.expm1(-xbar))
    primary_red_ci95 = [float(-math.expm1(-v)) for v in primary_log_ci95]
    speedup = float(math.exp(xbar))

    xb_pairs = xb.reshape(6, 2).mean(axis=1)
    _, _, drift_log_ci95 = t_ci95(xb_pairs)

    if args.skip_bootstrap:
        q_boot = frozen_out["query_bootstrap"]
        j_boot = frozen_out["joint_bootstrap"]
        alt_boot = {"skipped": True}
    else:
        q_boot = d31_analyzer.bootstrap(latency, joint=False)
        j_boot = d31_analyzer.bootstrap(latency, joint=True)
        rng = random.Random(20261125)
        resamples, k_blk = 2000, N // 100
        counts = np.zeros((resamples, k_blk), dtype=np.int32)
        proc = np.empty((resamples, 12), dtype=np.int32)
        for r in range(resamples):
            proc[r] = [rng.randrange(12) for _ in range(12)]
            for _ in range(k_blk):
                counts[r, rng.randrange(k_blk)] += 1
        bsums = latency.reshape(12, 6, 2, k_blk, 100).sum(axis=-1)
        bm = np.einsum("rk,mgpk->rmgp", counts, bsums, optimize=True) / N
        bm = bm[np.arange(resamples)[:, None], proc]
        bx = np.log(bm[:, :, :, 0] / bm[:, :, :, 1]).mean(axis=(1, 2))
        lo, hi = np.quantile(bx, [0.025, 0.975], method="linear").tolist()
        alt_boot = {"log_ci95": [lo, hi], "reduction_ci95": [-math.expm1(-lo), -math.expm1(-hi)]}

    graph_log = x.mean(axis=0)
    stock_arm_log = x[:, :3].mean(axis=1)
    fast_arm_log = x[:, 3:].mean(axis=1)
    _, _, stock_arm_ci = t_ci95(stock_arm_log)
    _, _, fast_arm_ci = t_ci95(fast_arm_log)
    loo_log = [float(np.delete(x, j, axis=1).mean()) for j in range(6)]

    crit18 = d31_analyzer.tcrit(1.0 - 0.05 / 18.0, 11)
    u95 = np.log(p95s[:, :, 1] / p95s[:, :, 0])
    u99 = np.log(p99s[:, :, 1] / p99s[:, :, 0])
    ram_norm = np.empty((12, 6), dtype=float)
    ram_hard_passes = []
    for b in range(12):
        for j in range(6):
            B = int(rss_kib[b, j, 0])
            C = int(rss_kib[b, j, 1])
            ram_norm[b, j] = (C - B) / max(65536.0, 0.10 * B)
            ram_hard_passes.append(10 * (C - B) <= max(655360, B))

    upper_u95 = u95.mean(axis=0) + crit18 * u95.std(axis=0, ddof=1) / math.sqrt(12)
    upper_u99 = u99.mean(axis=0) + crit18 * u99.std(axis=0, ddof=1) / math.sqrt(12)
    lower_u95 = u95.mean(axis=0) - crit18 * u95.std(axis=0, ddof=1) / math.sqrt(12)
    lower_u99 = u99.mean(axis=0) - crit18 * u99.std(axis=0, ddof=1) / math.sqrt(12)
    upper_ram = ram_norm.mean(axis=0) + crit18 * ram_norm.std(axis=0, ddof=1) / math.sqrt(12)
    lower_ram = ram_norm.mean(axis=0) - crit18 * ram_norm.std(axis=0, ddof=1) / math.sqrt(12)

    gain_pass = min(primary_log_ci95[0], drift_log_ci95[0], j_boot["primary_log_ci95"][0]) > THETA + TIE_EPS
    stability_pass = (
        bool(np.all(graph_log > 0))
        and float(stock_arm_log.mean()) >= THETA
        and float(fast_arm_log.mean()) >= THETA
        and all(v >= THETA for v in loo_log)
    )
    hard_ram_pass = all(ram_hard_passes) and bool(np.all(ram_norm <= 1.0))
    safety_pass = (
        hard_ram_pass
        and bool(np.all(upper_ram <= 1.0))
        and bool(np.all(upper_u95 <= math.log(1.05)))
        and bool(np.all(upper_u99 <= math.log(1.10)))
        and bool(np.all(np.array(j_boot["tail_log_upper95"])[:, 0] <= math.log(1.05)))
        and bool(np.all(np.array(j_boot["tail_log_upper95"])[:, 1] <= math.log(1.10)))
    )
    verdict_indep = "GO_A_FIXED_COHORT" if (gain_pass and stability_pass and safety_pass and quality["duplicate_reduction"]) else "HOLD"
    pivot_triggered = (
        (primary_log_ci95[1] < THETA - TIE_EPS and fast_arm_ci[1] < THETA - TIE_EPS)
        or bool(np.any(lower_u95 > math.log(1.05)))
        or bool(np.any(lower_u99 > math.log(1.10)))
        or bool(np.any(lower_ram > 1.0))
    )

    diffs = {
        "primary_reduction": abs(primary_red - frozen_out["primary_reduction"]),
        "primary_log_ci95": max(abs(a - b) for a, b in zip(primary_log_ci95, frozen_out["primary_log_ci95"])),
        "primary_reduction_ci95": max(abs(a - b) for a, b in zip(primary_red_ci95, frozen_out["primary_reduction_ci95"])),
        "speedup": abs(speedup - frozen_out["speedup"]),
        "drift_log_ci95": max(abs(a - b) for a, b in zip(drift_log_ci95, frozen_out["drift_log_ci95"])),
        "query_boot_primary": max(abs(a - b) for a, b in zip(q_boot["primary_log_ci95"], frozen_out["query_bootstrap"]["primary_log_ci95"])),
        "joint_boot_primary": max(abs(a - b) for a, b in zip(j_boot["primary_log_ci95"], frozen_out["joint_bootstrap"]["primary_log_ci95"])),
        "graph_log_effects": max(abs(a - b) for a, b in zip(graph_log.tolist(), frozen_out["graph_log_effects"])),
        "loo_log_effects": max(abs(a - b) for a, b in zip(loo_log, frozen_out["leave_one_out_log_effects"])),
        "upper_u95": float(np.max(np.abs(upper_u95 - np.array(frozen_out["tail_log_upper"])[:, 0]))),
        "upper_u99": float(np.max(np.abs(upper_u99 - np.array(frozen_out["tail_log_upper"])[:, 1]))),
        "upper_ram": float(np.max(np.abs(upper_ram - np.array(frozen_out["ram_mean_upper"])))),
    }
    max_stat_diff = max(diffs.values())

    arms_mean_us = means.reshape(12, 2, 3, 2).mean(axis=2)
    bref = freeze["build_reference"]
    b_stock = float(np.mean([bref[g]["wall_s"] for g in GRAPHS[:3]]))
    b_fast = float(np.mean([bref[g]["wall_s"] for g in GRAPHS[3:]]))
    bs_out = frozen_out["build_search"]
    bs_diff = max(abs(b_stock - bs_out["mean_build_stock_s"]), abs(b_fast - bs_out["mean_build_fast_s"]))
    for label, (ref, tgt) in d31_analyzer.CONTRASTS.items():
        u = arms_mean_us[:, ref[0], ref[1]]
        v = arms_mean_us[:, tgt[0], tgt[1]]
        d = u - v
        db = (b_stock if ref[0] == 0 else b_fast) - (b_stock if tgt[0] == 0 else b_fast)
        c_frozen = bs_out["contrasts"][label]
        bs_diff = max(bs_diff, abs(float(d.mean()) - c_frozen["mean_search_delta_us"]))
        for q in (1, 100000, 1000000):
            tm, _, tci = t_ci95(db + q * d / 1e6)
            wf = c_frozen["workloads"][str(q)]
            bs_diff = max(bs_diff, abs(tm - wf["saved_s"]), abs(tci[0] - wf["ci95_s"][0]), abs(tci[1] - wf["ci95_s"][1]))

    bs_main_100k = bs_out["contrasts"]["fast_opt_vs_stock_base"]["workloads"]["100000"]
    bs_go_indep = (
        min(bs_main_100k["ci95_s"][0], bs_main_100k["joint_ci95_s"][0]) > TIE_EPS
        and bs_out["contrasts"]["fast_opt_vs_fast_base"]["workloads"]["100000"]["saved_s"] > 0
        and bs_out["contrasts"]["fast_opt_vs_stock_opt"]["workloads"]["100000"]["saved_s"] > 0
        and safety_pass and gate_b_pass
    )

    nb_recomp = d31_analyzer.noise_balance_diagnostics(f_all, f_wrk, f_ccx, x)
    nb_diff = max(
        abs(nb_recomp["paired_delta_all_mean"] - frozen_out["noise_balance"]["paired_delta_all_mean"]),
        abs(nb_recomp["paired_delta_workers_mean"] - frozen_out["noise_balance"]["paired_delta_workers_mean"]),
        abs(nb_recomp["spearman_delta_all_vs_log_effect"] - frozen_out["noise_balance"]["spearman_delta_all_vs_log_effect"]),
        abs(nb_recomp["spearman_delta_workers_vs_log_effect"] - frozen_out["noise_balance"]["spearman_delta_workers_vs_log_effect"]),
    )

    record_check(
        "independent_statistical_and_build_search_audit",
        verdict_indep == frozen_out["verdict"] == "GO_A_FIXED_COHORT"
        and not pivot_triggered
        and bs_go_indep and bs_out["status"] == "GO_B_SYSTEM_FIXED_COHORT"
        and max_stat_diff < 1e-13 and bs_diff < 1e-12 and nb_diff < 1e-14
        and frozen_out["evidence_label"] == "EXPLORATORY_HOST_SPECIFIC"
        and frozen_out["graph_population_ci"] == "NOT_ESTIMABLE"
        and frozen_out["noise_balance"]["imbalance_warning"] is False,
        {
            "verdict_indep": verdict_indep,
            "verdict_frozen": frozen_out["verdict"],
            "build_search_status": bs_out["status"],
            "bootstrap_recomputed": not args.skip_bootstrap,
            "alt_seed_20261125_joint_boot": alt_boot,
            "max_stat_diff_vs_frozen": max_stat_diff,
            "max_build_search_diff_vs_frozen": bs_diff,
            "max_noise_balance_diff_vs_frozen": nb_diff,
            "per_check_diffs": diffs,
        },
    )

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2))

    print("=== INDEPENDENT FINAL AUDIT SUMMARY ===")
    for k, v in report["checks"].items():
        print(f"CHECK {k}: {'PASS' if v['pass'] else 'FAIL'}")
    print(f"DISCREPANCIES_COUNT={len(report['discrepancies'])}")
    if report["discrepancies"]:
        print(json.dumps(report["discrepancies"], indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
