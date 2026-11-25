#!/usr/bin/env python3
"""Export verified underlying CSV/JSON data tables for Task D Final Handoff.

Reads directly from immutable audited G2 v2 design-3.1 JSON artifacts and
verified repository/survey records. Produces zero synthetic experimental data.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

TABLES = Path(__file__).resolve().parent
REPO = TABLES.parents[4]


def verified_json(path: Path, expected_sha: str) -> dict:
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_sha:
        raise ValueError(f"SHA-256 mismatch for {path.name}")
    return json.loads(data)


def write_csv(directory: Path, filename: str, fieldnames: list[str], rows: list[dict]) -> None:
    with (directory / filename).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=REPO.parent / "artifact-evidence")
    parser.add_argument("--output", type=Path, default=TABLES)
    args = parser.parse_args()
    out = args.output
    analysis = verified_json(
        args.evidence / "axd-g2-v2-off-design3_1_run2-analysis.json",
        "f0a35394f028550a1f14f4928467a62e5d09363a2ef26cffa160d0c7e200615c",
    )
    audit = verified_json(
        args.evidence / "axd-g2-v2-final-audit-design3_1/audit_results.json",
        "c79e45a3482a702b8ca0aa48c68089c86875db025e002e8523109abb656e9c66",
    )
    quality = verified_json(
        args.evidence / "axd-g2-v2-quality-design3/quality.json",
        "360e1d29fc3c8f3c03e381ce57dea2e826459f7534577d6d24ec6ac81a54c59f",
    )
    build_ref = verified_json(
        REPO / "configs/axd_g2_v2_build_reference.json",
        "c9ad18b0062fea39609089b26817d43adc2cb4f495cd72c3a3ef7261abbc87b3",
    )
    out.mkdir(parents=True, exist_ok=True)

    # 1. Research Timeline
    timeline_rows = [
        {"idx": 1, "era": "Kỷ nguyên 1: Nền tảng & PipeANN", "date": "2026-10-01–13", "milestone": "Gate 0 & Issue #32 PipeANN SIFT10M", "detail": "36/36 Custom Full-Fan 60/90W; T16 vs T8 = -13.36% QPS; D1/D4/D6 bảo lưu", "status": "PASS", "category": "Baseline"},
        {"idx": 2, "era": "Kỷ nguyên 1: Nền tảng & PipeANN", "date": "2026-10-13", "milestone": "Sàng lọc Offline H-Lanes", "detail": "H-G: 2.56 GB, lợi ích 0; H-QV1: utility −0.000122; H-F: mô phỏng", "status": "NO-GO", "category": "Negative"},
        {"idx": 3, "era": "Kỷ nguyên 2: Khảo sát 3 Cụm & E0–E3", "date": "2026-10-15–22", "milestone": "Góp ý GV & Taxonomy D01–D10", "detail": "Đảo quy trình prior-art trước; chuẩn hóa 3 cụm khảo sát", "status": "COMPLETE", "category": "Survey"},
        {"idx": 4, "era": "Kỷ nguyên 2: Khảo sát 3 Cụm & E0–E3", "date": "2026-10-29", "milestone": "AverSearch E0 Queue-Role (108 ô)", "detail": "Responsive vs min(F1,F2): 3 thắng / 15 hòa / 90 thua (MODEL_ONLY)", "status": "REFUTED", "category": "Negative"},
        {"idx": 5, "era": "Kỷ nguyên 2: Khảo sát 3 Cụm & E0–E3", "date": "2026-11-05", "milestone": "E2 SIFT1M NSG & Cụm 1–3 Closeout", "detail": "Single-mutex F1=19.21 > Ad3=15.09 > F2=10.72 QPS; dừng 90.25°C; khảo sát 3 cụm hoàn tất 12–14/11", "status": "NO-GO", "category": "Negative"},
        {"idx": 6, "era": "Kỷ nguyên 3: R86 A×D (P0–P4, H1–H3)", "date": "2026-11-15–18", "milestone": "Đề xuất A×D & Full P1 V3", "detail": "1.804M ON/OFF parity PASS; t0998 trượt 7/9 (winner's curse)", "status": "HOLD", "category": "Gate"},
        {"idx": 7, "era": "Kỷ nguyên 3: R86 A×D (P0–P4, H1–H3)", "date": "2026-11-19", "milestone": "Stage D (378 lượt) & Stage E", "detail": "H1 có điều kiện; std::set→flat thu hẹp khoảng cách; TP-CG PIVOT", "status": "PIVOT", "category": "Pivot"},
        {"idx": 8, "era": "Kỷ nguyên 3: R86 A×D (P0–P4, H1–H3)", "date": "2026-11-19", "milestone": "B1+A1 Pilot & Narrow A3 (R2/R3)", "detail": "R2 -12.29%, R3 -10.08%, nhưng outer df=1 CI [-2.84%, +25.21%]", "status": "HOLD", "category": "Gate"},
        {"idx": 9, "era": "Kỷ nguyên 3: R86 A×D (P0–P4, H1–H3)", "date": "2026-11-20", "milestone": "H3 Overlap (6,095 rd) & Meas. Audit", "detail": "79–80% dup là emergent; sig-128 thua degree; CI observer vượt biên dưới −2%", "status": "NO-GO", "category": "Negative"},
        {"idx": 10, "era": "Kỷ nguyên 4: G1/G2 R90 design-3.1", "date": "2026-11-22–24", "milestone": "G1 PASS → v1 HOLD → design-3 Qual", "detail": "G1 30/30 PASS; v1 span HOLD → v2 b432; Qual #2 853/853 PASS", "status": "PASS", "category": "Gate"},
        {"idx": 11, "era": "Kỷ nguyên 4: G1/G2 R90 design-3.1", "date": "2026-11-24–25", "milestone": "Quality ON 18/18 & 2 OFF HOLDs", "detail": "Gate A&B PASS; design-3 #1 KeyError & run1 #120 firmware-notifier HOLD (cô lập)", "status": "HOLD", "category": "Gate"},
        {"idx": 12, "era": "Kỷ nguyên 4: G1/G2 R90 design-3.1", "date": "2026-11-25", "milestone": "G2 design-3.1 run2 & Final Audit", "detail": "144/144 OFF (-6.033%), GO_A + GO_B, AUDIT_PASS 0 discrepancies, 9/9 Remote SHA", "status": "GO / PASS", "category": "Success"},
    ]
    write_csv(out, "table01_research_timeline.csv", list(timeline_rows[0].keys()), timeline_rows)

    # 2. Taxonomy D01–D10
    tax_rows = [
        {"code": "D01", "cluster": "Cụm 1: CPU Multi-core", "mechanism": "Parallel graph construction", "phase": "BUILD", "resource": "CPU / RAM", "representative": "ParlayANN (PPoPP '24)", "status": "SURVEY_COMPLETE (Task A tham chiếu)"},
        {"code": "D02", "cluster": "Cụm 1: CPU Multi-core", "mechanism": "Edge-wise parallel expansion", "phase": "SEARCH (intra)", "resource": "CPU / RAM", "representative": "Speed-ANN §3 (đối chứng)", "status": "SURVEY_COMPLETE"},
        {"code": "D03", "cluster": "Cụm 1: CPU Multi-core", "mechanism": "Path-wise / multi-walker & async tasks", "phase": "SEARCH (intra)", "resource": "CPU / RAM", "representative": "Speed-ANN, iQAN, AverSearch, Task D B1+A1", "status": "EXPERIMENTAL (G2 GO_A_FIXED_COHORT)"},
        {"code": "D04", "cluster": "Cụm 2: CPU–SSD Pipeline", "mechanism": "Batched SSD beam search", "phase": "SEARCH (intra)", "resource": "CPU + SSD", "representative": "DiskANN / Vamana (NeurIPS '19)", "status": "SURVEY_COMPLETE"},
        {"code": "D05", "cluster": "Cụm 2: CPU–SSD Pipeline", "mechanism": "Continuous async CPU–SSD pipeline", "phase": "SEARCH (intra)", "resource": "CPU + SSD", "representative": "PipeANN / PipeSearch (OSDI '25)", "status": "BASELINE (Issue #32 SIFT10M) / SURVEY"},
        {"code": "D06", "cluster": "Cụm 2: CPU–SSD Pipeline", "mechanism": "Adaptive per-query I/O width W", "phase": "SEARCH (intra)", "resource": "SSD", "representative": "PipeANN §4.2", "status": "SURVEY_COMPLETE"},
        {"code": "D07", "cluster": "Cụm 2: CPU–SSD Pipeline", "mechanism": "Completion-aware I/O issuance", "phase": "SEARCH (intra)", "resource": "CPU + SSD", "representative": "PipeANN §4.3 Fig.10", "status": "SURVEY_COMPLETE"},
        {"code": "D08", "cluster": "Cụm 2: CPU–SSD Pipeline", "mechanism": "Memory-first look-ahead + P1/P2/P3", "phase": "SEARCH (intra)", "resource": "RAM + CPU + SSD", "representative": "LAANN (arXiv '26)", "status": "SURVEY_COMPLETE (NOT_RUN)"},
        {"code": "D09", "cluster": "Cụm 3: GPU Data Parallelism", "mechanism": "GPU distance + WarpSelect / graph GPU", "phase": "SEARCH / BUILD", "resource": "GPU VRAM/Regs", "representative": "FAISS GPU ('17), CAGRA ('24), FusionANNS ('25)", "status": "SURVEY_COMPLETE (0 GPU benchmark)"},
        {"code": "D10", "cluster": "Trục xuyên suốt (Orthogonal)", "mechanism": "Inter-query concurrency & resource control", "phase": "SERVING (inter)", "resource": "CPU / SSD / GPU", "representative": "ANN Serving, Hitcher, PipeANN multi-T", "status": "OPEN (Issue #32 T16=-13.36%; G2 jobs=1)"},
    ]
    write_csv(out, "table02_taxonomy_d01_d10.csv", list(tax_rows[0].keys()), tax_rows)

    # 3. Prior Art Comparison
    pa_rows = [
        {"system": "ParlayANN ('24)", "cluster": "C1 / D01", "phase": "BUILD (+Search)", "parallelism": "Batch snapshot + semisort", "sync_mech": "Batch boundary", "key_tradeoff": "Chi phí gom batch & RAM tạm", "scope_note": "PAPER (không đổi thành search latency)"},
        {"system": "Speed-ANN ('22)", "cluster": "C1 / D03", "phase": "SEARCH intra", "parallelism": "Multi-walker, staged M", "sync_mech": "Update-pos AUP", "key_tradeoff": "Work inflation, băng thông RAM", "scope_note": "PAPER (kết quả trên CPU của tác giả)"},
        {"system": "iQAN ('23)", "cluster": "C1 / D03", "phase": "SEARCH intra", "parallelism": "Path-wise + locality", "sync_mech": "Lazy AUP merge", "key_tradeoff": "Cùng dòng Speed-ANN (không tính đôi)", "scope_note": "PAPER (PPoPP '23)"},
        {"system": "AverSearch ('25)", "cluster": "C1 / D03", "phase": "SEARCH async", "parallelism": "Balancer/Maint./Calc.", "sync_mech": "Async shared array", "key_tradeoff": "Phân vai cố định khi hàng đợi mất cân bằng", "scope_note": "PAPER (E1/E3 chỉ là prototype độc lập)"},
        {"system": "DiskANN ('19)", "cluster": "C2 / D04", "phase": "SEARCH SSD", "parallelism": "Batched beam W", "sync_mech": "Batch I/O barrier", "key_tradeoff": "Chờ request chậm nhất (tail I/O)", "scope_note": "PAPER (baseline SSD)"},
        {"system": "PipeANN ('25)", "cluster": "C2 / D05–07", "phase": "SEARCH SSD", "parallelism": "Async I/O + adaptive W", "sync_mech": "Interleaved issue/exp", "key_tradeoff": "I/O suy đoán có thể lãng phí", "scope_note": "PAPER + OBS (#32 T16 -13.36% SIFT10M)"},
        {"system": "LAANN ('26)", "cluster": "C2 / D08", "phase": "SEARCH SSD", "parallelism": "Look-ahead + P1/P2/P3", "sync_mech": "Persistence + io_uring", "key_tradeoff": "CPU thêm + phụ thuộc PageANN layout", "scope_note": "PAPER (NOT_RUN)"},
        {"system": "FAISS GPU ('17)", "cluster": "C3 / D09", "phase": "SEARCH GPU", "parallelism": "GEMM/IVF + WarpSelect", "sync_mech": "Warp ballot/shuffle", "key_tradeoff": "VRAM, register pressure, batch nhỏ", "scope_note": "PAPER (Maxwell 2017; NOT_RUN)"},
        {"system": "CAGRA ('24)", "cluster": "C3 / D09", "phase": "BUILD+SEARCH", "parallelism": "GPU CTA graph search", "sync_mech": "Visited hash + CTA", "key_tradeoff": "Giới hạn VRAM ở quy mô rất lớn", "scope_note": "PAPER (prior art GPU graph)"},
        {"system": "Task D B1+A1", "cluster": "C1 / D03", "phase": "SEARCH intra", "parallelism": "BSP p=2 S=16 hygiene", "sync_mech": "Barrier mark + inc.", "key_tradeoff": "Baseline hygiene (không novelty); p=4 chưa ổn", "scope_note": "D-OBS (-6.03%, -74.98% dup, bit-exact)"},
    ]
    write_csv(out, "table03_prior_art_comparison.csv", list(pa_rows[0].keys()), pa_rows)

    # 4. Research Gap -> Hypothesis -> Experiment -> Decision
    wf_rows = [
        {"stage": "1. PipeANN CPU–SSD", "gap": "Nghẽn T16 & chọn ứng viên SSD", "hypothesis": "D1/D4/D6, H-G, H-QV1, H-V, H-F", "experiment": "Issue #32 (36/36) + Surrogate SIFT10M", "decision": "Issue #32 PASS; H-G/H-QV1 NO-GO; D1/D4/D6 bảo lưu"},
        {"stage": "2. AverSearch Roles", "gap": "Queue starvation ở phân vai tĩnh", "hypothesis": "Dynamic role reallocation vượt static", "experiment": "E0 (108 ô) + E2 SIFT1M NSG (1 mutex)", "decision": "E0 REFUTED (3/15/90); E2 FORMAL NO-GO"},
        {"stage": "3. R86 Graph × Worker", "gap": "Tương tác BUILD R86 × multi-walker", "hypothesis": "H1/H2 tương tác; H3 TP-CG động", "experiment": "Stage D (378 lượt) + Prior-art Audit", "decision": "H1 EXPLORATORY; std::set→flat; TP-CG PIVOT"},
        {"stage": "4. H3 Overlap & Meas.", "gap": "Duplicate L2 còn lại sau B1+A1", "hypothesis": "Overlap-aware seed assignment (sig-128)", "experiment": "6,095 rounds trace + Phase Observer", "decision": "Overlap NO-GO (79–80% emergent); Obs NOT_VALIDATED"},
        {"stage": "5. B1+A1 & G2 v2 R90", "gap": "Lãng phí nền BSP & tích hợp A×D", "hypothesis": "B1+A1 giảm ≥3% OFF, bit-exact, +Fast BUILD", "experiment": "G2 design-3.1 run2 (144 OFF + 18 ON)", "decision": "GO_A_FIXED_COHORT (-6.03%) + GO_B_SYSTEM_FIXED_COHORT (model +30.34s@100k)"},
    ]
    write_csv(out, "table04_workflow_decisions.csv", list(wf_rows[0].keys()), wf_rows)

    # 5. G2 2x2 Arms & Overall Summary (exact from audit_results.json + analysis.json)
    ss = audit["summary_stats"]
    arms = ss["arms"]
    cells = ss["cells_2x2"]
    overall = ss["overall_secondary"]
    qm = audit["quality_mechanism"]["test"]

    def arm_on_avg(prefix: str, pol: str, field: str) -> float:
        gs = [g for g in qm if g.startswith(prefix)]
        return sum(qm[g][f"{pol}_counters"][field]["mean_per_query"] for g in gs) / len(gs)

    def all_on_avg(pol: str, field: str) -> float:
        gs = list(qm.keys())
        return sum(qm[g][f"{pol}_counters"][field]["mean_per_query"] for g in gs) / len(gs)

    arm_rows = [
        {
            "arm_id": "stock_base", "label": "Stock + Baseline", "build_arm": "Stock", "search_policy": "baseline",
            "recall_mean": sum(qm[g]["recall_mean"] for g in qm if g.startswith("stock_")) / 3.0,
            "mean_us": cells["stock_base"]["mean_us"], "p50_us": cells["stock_base"]["p50_us"],
            "p95_us": cells["stock_base"]["p95_us"], "p99_us": cells["stock_base"]["p99_us"],
            "qps_wall_jobs1": cells["stock_base"]["qps_wall"],
            "dup_l2_per_q": arm_on_avg("stock_", "base", "duplicate_distance_evaluations"),
            "total_l2_per_q": arm_on_avg("stock_", "base", "distance_evaluations"),
            "unique_l2_per_q": arm_on_avg("stock_", "base", "unique_distance_evaluations"),
            "proc_cpu_s": cells["stock_base"]["cpu_seconds_proc"], "peak_rss_kib": cells["stock_base"]["rss_kib"],
            "geo_reduction_pct": 0.0, "geo_ci95_low_pct": "", "geo_ci95_high_pct": "",
        },
        {
            "arm_id": "stock_opt", "label": "Stock + B1+A1", "build_arm": "Stock", "search_policy": "B1+A1",
            "recall_mean": sum(qm[g]["recall_mean"] for g in qm if g.startswith("stock_")) / 3.0,
            "mean_us": cells["stock_opt"]["mean_us"], "p50_us": cells["stock_opt"]["p50_us"],
            "p95_us": cells["stock_opt"]["p95_us"], "p99_us": cells["stock_opt"]["p99_us"],
            "qps_wall_jobs1": cells["stock_opt"]["qps_wall"],
            "dup_l2_per_q": arm_on_avg("stock_", "opt", "duplicate_distance_evaluations"),
            "total_l2_per_q": arm_on_avg("stock_", "opt", "distance_evaluations"),
            "unique_l2_per_q": arm_on_avg("stock_", "opt", "unique_distance_evaluations"),
            "proc_cpu_s": cells["stock_opt"]["cpu_seconds_proc"], "peak_rss_kib": cells["stock_opt"]["rss_kib"],
            "geo_reduction_pct": arms["stock_reduction_pct"],
            "geo_ci95_low_pct": arms["stock_reduction_ci95_pct"][0],
            "geo_ci95_high_pct": arms["stock_reduction_ci95_pct"][1],
        },
        {
            "arm_id": "fast_base", "label": "Fast v2 + Baseline", "build_arm": "Fast v2", "search_policy": "baseline",
            "recall_mean": sum(qm[g]["recall_mean"] for g in qm if g.startswith("fast_")) / 3.0,
            "mean_us": cells["fast_base"]["mean_us"], "p50_us": cells["fast_base"]["p50_us"],
            "p95_us": cells["fast_base"]["p95_us"], "p99_us": cells["fast_base"]["p99_us"],
            "qps_wall_jobs1": cells["fast_base"]["qps_wall"],
            "dup_l2_per_q": arm_on_avg("fast_", "base", "duplicate_distance_evaluations"),
            "total_l2_per_q": arm_on_avg("fast_", "base", "distance_evaluations"),
            "unique_l2_per_q": arm_on_avg("fast_", "base", "unique_distance_evaluations"),
            "proc_cpu_s": cells["fast_base"]["cpu_seconds_proc"], "peak_rss_kib": cells["fast_base"]["rss_kib"],
            "geo_reduction_pct": 0.0, "geo_ci95_low_pct": "", "geo_ci95_high_pct": "",
        },
        {
            "arm_id": "fast_opt", "label": "Fast v2 + B1+A1", "build_arm": "Fast v2", "search_policy": "B1+A1",
            "recall_mean": sum(qm[g]["recall_mean"] for g in qm if g.startswith("fast_")) / 3.0,
            "mean_us": cells["fast_opt"]["mean_us"], "p50_us": cells["fast_opt"]["p50_us"],
            "p95_us": cells["fast_opt"]["p95_us"], "p99_us": cells["fast_opt"]["p99_us"],
            "qps_wall_jobs1": cells["fast_opt"]["qps_wall"],
            "dup_l2_per_q": arm_on_avg("fast_", "opt", "duplicate_distance_evaluations"),
            "total_l2_per_q": arm_on_avg("fast_", "opt", "distance_evaluations"),
            "unique_l2_per_q": arm_on_avg("fast_", "opt", "unique_distance_evaluations"),
            "proc_cpu_s": cells["fast_opt"]["cpu_seconds_proc"], "peak_rss_kib": cells["fast_opt"]["rss_kib"],
            "geo_reduction_pct": arms["fast_reduction_pct"],
            "geo_ci95_low_pct": arms["fast_reduction_ci95_pct"][0],
            "geo_ci95_high_pct": arms["fast_reduction_ci95_pct"][1],
        },
        {
            "arm_id": "overall_base", "label": "Gộp 6 Graph (Base)", "build_arm": "Pooled", "search_policy": "baseline",
            "recall_mean": sum(qm[g]["recall_mean"] for g in qm) / 6.0,
            "mean_us": analysis["arithmetic_base_us"], "p50_us": overall["p50_base_mean_us"],
            "p95_us": overall["p95_base_mean_us"], "p99_us": overall["p99_base_mean_us"],
            "qps_wall_jobs1": overall["qps_base_mean"],
            "dup_l2_per_q": all_on_avg("base", "duplicate_distance_evaluations"),
            "total_l2_per_q": all_on_avg("base", "distance_evaluations"),
            "unique_l2_per_q": all_on_avg("base", "unique_distance_evaluations"),
            "proc_cpu_s": overall["cpu_s_base_mean"], "peak_rss_kib": overall["rss_base_mean_kib"],
            "geo_reduction_pct": 0.0, "geo_ci95_low_pct": "", "geo_ci95_high_pct": "",
        },
        {
            "arm_id": "overall_opt", "label": "Gộp 6 Graph (B1+A1)", "build_arm": "Pooled", "search_policy": "B1+A1",
            "recall_mean": sum(qm[g]["recall_mean"] for g in qm) / 6.0,
            "mean_us": analysis["arithmetic_opt_us"], "p50_us": overall["p50_opt_mean_us"],
            "p95_us": overall["p95_opt_mean_us"], "p99_us": overall["p99_opt_mean_us"],
            "qps_wall_jobs1": overall["qps_opt_mean"],
            "dup_l2_per_q": all_on_avg("opt", "duplicate_distance_evaluations"),
            "total_l2_per_q": all_on_avg("opt", "distance_evaluations"),
            "unique_l2_per_q": all_on_avg("opt", "unique_distance_evaluations"),
            "proc_cpu_s": overall["cpu_s_opt_mean"], "peak_rss_kib": overall["rss_opt_mean_kib"],
            "geo_reduction_pct": analysis["primary_reduction"] * 100.0,
            "geo_ci95_low_pct": analysis["primary_reduction_ci95"][0] * 100.0,
            "geo_ci95_high_pct": analysis["primary_reduction_ci95"][1] * 100.0,
        },
    ]
    write_csv(out, "table05_g2_2x2_arms_summary.csv", list(arm_rows[0].keys()), arm_rows)

    # 6. Four CI Families (+ Drift)
    drift_pct = [(1.0 - math.exp(-x)) * 100.0 for x in analysis["drift_log_ci95"]]
    qboot_pct = [(1.0 - math.exp(-x)) * 100.0 for x in analysis["query_bootstrap"]["primary_log_ci95"]]
    jboot_pct = [(1.0 - math.exp(-x)) * 100.0 for x in analysis["joint_bootstrap"]["primary_log_ci95"]]
    point_pct = analysis["primary_reduction"] * 100.0
    ci_rows = [
        {"ci_family": "Primary block-t (df=11)", "point_pct": point_pct, "low_pct": analysis["primary_reduction_ci95"][0] * 100.0, "high_pct": analysis["primary_reduction_ci95"][1] * 100.0, "status": "ESTIMATED", "scope": "Độ lặp 12 block cân bằng (6 graph cố định, 10k query cố định)"},
        {"ci_family": "Drift-paired block-t (df=5)", "point_pct": point_pct, "low_pct": drift_pct[0], "high_pct": drift_pct[1], "status": "ESTIMATED", "scope": "6 cặp block liền kề (phân tích độ nhạy theo thời gian)"},
        {"ci_family": "Query-only bootstrap (10k)", "point_pct": point_pct, "low_pct": qboot_pct[0], "high_pct": qboot_pct[1], "status": "ESTIMATED", "scope": "Lấy mẫu khối 100 query (seed 20261123; điều kiện hóa run)"},
        {"ci_family": "Joint bootstrap (10k)", "point_pct": point_pct, "low_pct": jboot_pct[0], "high_pct": jboot_pct[1], "status": "ESTIMATED", "scope": "Kết hợp lặp tiến trình + lấy mẫu query (6 graph cố định)"},
        {"ci_family": "Graph population CI", "point_pct": "", "low_pct": "", "high_pct": "", "status": "NOT_ESTIMABLE", "scope": "6 đồ thị dùng chung SEED=555; không suy rộng quần thể RNG mới"},
    ]
    write_csv(out, "table06_ci_families.csv", list(ci_rows[0].keys()), ci_rows)

    # 7. Latency Quantiles (Mean, P50, P95, P99)
    q_rows = [
        {"metric": "Mean", "base_us": analysis["arithmetic_base_us"], "opt_us": analysis["arithmetic_opt_us"], "delta_us": analysis["arithmetic_opt_us"] - analysis["arithmetic_base_us"], "change_pct": -analysis["arithmetic_reduction"] * 100.0, "pre_reg_bound": "Thay đổi số học; ngưỡng GO áp dụng cho log-ratio"},
        {"metric": "P50 (Median)", "base_us": overall["p50_base_mean_us"], "opt_us": overall["p50_opt_mean_us"], "delta_us": overall["p50_opt_mean_us"] - overall["p50_base_mean_us"], "change_pct": -overall["p50_geo_reduction_pct"], "pre_reg_bound": "Secondary (cải thiện)"},
        {"metric": "P95", "base_us": overall["p95_base_mean_us"], "opt_us": overall["p95_opt_mean_us"], "delta_us": overall["p95_opt_mean_us"] - overall["p95_base_mean_us"], "change_pct": -overall["p95_geo_reduction_pct"], "pre_reg_bound": "Upper <= +5.0% (PASS: -3.87%)"},
        {"metric": "P99", "base_us": overall["p99_base_mean_us"], "opt_us": overall["p99_opt_mean_us"], "delta_us": overall["p99_opt_mean_us"] - overall["p99_base_mean_us"], "change_pct": -overall["p99_geo_reduction_pct"], "pre_reg_bound": "Upper <= +10.0% (PASS: -3.78%)"},
    ]
    write_csv(out, "table07_latency_quantiles.csv", list(q_rows[0].keys()), q_rows)

    # 8. QPS by Arm (jobs=1)
    qps_rows = [
        {"arm": "Stock (3 graphs)", "base_qps": cells["stock_base"]["qps_wall"], "opt_qps": cells["stock_opt"]["qps_wall"], "gain_pct": (cells["stock_opt"]["qps_wall"] / cells["stock_base"]["qps_wall"] - 1.0) * 100.0},
        {"arm": "Fast v2 (3 graphs)", "base_qps": cells["fast_base"]["qps_wall"], "opt_qps": cells["fast_opt"]["qps_wall"], "gain_pct": (cells["fast_opt"]["qps_wall"] / cells["fast_base"]["qps_wall"] - 1.0) * 100.0},
        {"arm": "Gộp 6 Graphs", "base_qps": overall["qps_base_mean"], "opt_qps": overall["qps_opt_mean"], "gain_pct": overall["qps_gain_pct"]},
    ]
    write_csv(out, "table08_qps_by_arm.csv", list(qps_rows[0].keys()), qps_rows)

    # 9. ON L2 & Bookkeeping Counters (exact from audit_results.json)
    on_fields = [
        ("unique_distance_evaluations", "Unique L2 / query", "count/q"),
        ("duplicate_distance_evaluations", "Duplicate L2 / query", "count/q"),
        ("distance_evaluations", "Total L2 / query", "count/q"),
        ("already_seen_attempts", "Already-seen attempts / query", "count/q"),
        ("neighbor_attempts", "Neighbor attempts / query", "count/q"),
        ("expansions", "Total expansions / query", "count/q"),
        ("unique_expansions", "Unique expansions / query", "count/q"),
        ("duplicate_expansions", "Duplicate expansions / query", "count/q"),
        ("frontier_insertions", "Frontier insertions / query", "count/q"),
        ("sync_merge_count", "Sync rounds / query", "rounds/q"),
        ("merge_time_ns", "ON merge_time (µs/q)", "µs/q"),
        ("barrier_wait_ns", "ON barrier_wait (µs/q)", "µs/q"),
        ("sync_wait_ns", "ON sync_wait (µs/q)", "µs/q"),
    ]
    on_rows = []
    for key, label, unit in on_fields:
        scale = 1e-3 if key.endswith("_ns") else 1.0
        b = all_on_avg("base", key) * scale
        o = all_on_avg("opt", key) * scale
        delta = o - b
        pct = (delta / b * 100.0) if b else 0.0
        on_rows.append({"counter": key, "label": label, "unit": unit, "base_mean": b, "opt_mean": o, "delta": delta, "change_pct": pct})
    write_csv(out, "table09_on_l2_counters.csv", list(on_rows[0].keys()), on_rows)

    # 10. Per-Graph R90 Results (6 graphs)
    pg_order = ["stock_off_r1", "stock_off_r2", "stock_off_r3", "fast_off_r1", "fast_off_r2", "fast_off_r3"]
    pg_rows = []
    for g in pg_order:
        p = ss["per_graph"][g]
        qmg = qm[g]
        pg_rows.append({
            "graph": g,
            "arm": "Stock" if g.startswith("stock_") else "Fast v2",
            "recall_mean": qmg["recall_mean"],
            "recall_lcb95": qmg["recall_lcb95"],
            "mean_base_us": p["base_mean_us"],
            "mean_opt_us": p["opt_mean_us"],
            "geo_reduction_pct": p["reduction_pct"],
            "geo_ci95_low_pct": p["reduction_ci95_pct"][0],
            "geo_ci95_high_pct": p["reduction_ci95_pct"][1],
            "loo_reduction_pct": p["loo_reduction_pct"],
            "qps_base": p["qps_base"],
            "qps_opt": p["qps_opt"],
            "dup_l2_reduction_pct": qmg["dup_l2_reduction_pct"],
            "total_l2_reduction_pct": qmg["total_l2_reduction_pct"],
        })
    write_csv(out, "table10_per_graph_r90.csv", list(pg_rows[0].keys()), pg_rows)

    # 11. Measured BUILD Comparison (Host A historical receipts)
    build_rows = []
    for g in pg_order:
        br = build_ref[g]
        build_rows.append({
            "graph": g,
            "arm": "Stock" if g.startswith("stock_") else "Fast v2",
            "wall_s": br["wall_s"],
            "graph_bytes": br["graph_bytes"],
            "graph_mib": br["graph_bytes"] / (1024.0 * 1024.0),
            "build_threads": br["build_threads"],
            "graph_sha256": br["graph_sha256"],
            "builder_elf_sha256": br["builder_elf_sha256"],
            "receipt_sha256": br["receipt_sha256"],
        })
    write_csv(out, "table11_measured_build_host_a.csv", list(build_rows[0].keys()), build_rows)

    # 12. Modeled Two-Host BUILD-SEARCH (exact from analysis["build_search"])
    bs = analysis["build_search"]
    b_stock = sum(build_ref[f"stock_off_r{i}"]["wall_s"] for i in (1, 2, 3)) / 3.0
    b_fast = sum(build_ref[f"fast_off_r{i}"]["wall_s"] for i in (1, 2, 3)) / 3.0
    s_sb = cells["stock_base"]["mean_us"] * 1e-6
    s_so = cells["stock_opt"]["mean_us"] * 1e-6
    s_fb = cells["fast_base"]["mean_us"] * 1e-6
    s_fo = cells["fast_opt"]["mean_us"] * 1e-6

    bs_rows = []
    for Q, tag in [(1, "JSON"), (10_000, "DERIVED"), (100_000, "JSON"), (1_000_000, "JSON")]:
        t_sb = b_stock + Q * s_sb
        t_so = b_stock + Q * s_so
        t_fb = b_fast + Q * s_fb
        t_fo = b_fast + Q * s_fo
        saved_fo_vs_sb = t_sb - t_fo
        build_part = b_stock - b_fast
        search_part = Q * (s_sb - s_fo)
        ci_lo = ci_hi = j_lo = j_hi = ""
        if str(Q) in bs["contrasts"]["fast_opt_vs_stock_base"]["workloads"]:
            w = bs["contrasts"]["fast_opt_vs_stock_base"]["workloads"][str(Q)]
            ci_lo, ci_hi = w["ci95_s"]
            j_lo, j_hi = w["joint_ci95_s"]
        bs_rows.append({
            "Q": Q, "source_tag": tag,
            "stock_base_s": t_sb, "fast_base_s": t_fb, "stock_opt_s": t_so, "fast_opt_s": t_fo,
            "saved_fast_opt_vs_stock_base_s": saved_fo_vs_sb,
            "saved_build_component_s": build_part,
            "saved_search_component_s": search_part,
            "saved_pct": (saved_fo_vs_sb / t_sb) * 100.0,
            "ci95_low_s": ci_lo, "ci95_high_s": ci_hi,
            "joint_ci95_low_s": j_lo, "joint_ci95_high_s": j_hi,
        })
    write_csv(out, "table12_modeled_two_host_build_search.csv", list(bs_rows[0].keys()), bs_rows)

    # 13. Objective Closure Matrix Summary (exact alignment with TASK_D_OBJECTIVE_CLOSURE_MATRIX.md)
    oc_rows = [
        {"group": "A. Phân công gốc (14/10 & Tuần 1)", "req_id": "REQ-A1", "short_title": "Tuần 1 Gate 0: Paper/Dataset/Protocol", "status": "COMPLETE_WITH_SCOPE"},
        {"group": "A. Phân công gốc (14/10 & Tuần 1)", "req_id": "REQ-A2", "short_title": "Đọc 5 nguồn nền & 6 khái niệm cốt lõi", "status": "COMPLETE"},
        {"group": "A. Phân công gốc (14/10 & Tuần 1)", "req_id": "REQ-A3", "short_title": "Execution DAG & cơ chế nghẽn scaling", "status": "COMPLETE_WITH_SCOPE"},
        {"group": "A. Phân công gốc (14/10 & Tuần 1)", "req_id": "REQ-A4", "short_title": "Đề xuất ≥2 giả thuyết có điều kiện bác bỏ", "status": "COMPLETE"},
        {"group": "B. Điều chỉnh sau góp ý GV (16/10)", "req_id": "REQ-B1", "short_title": "Prior art trước & Taxonomy D01–D10", "status": "COMPLETE"},
        {"group": "B. Điều chỉnh sau góp ý GV (16/10)", "req_id": "REQ-B2", "short_title": "Kiểm nguồn gốc & tách nhãn bằng chứng", "status": "COMPLETE"},
        {"group": "B. Điều chỉnh sau góp ý GV (16/10)", "req_id": "REQ-B3", "short_title": "Khảo sát Cụm 1 (CPU Multi-core Q1–Q4)", "status": "SURVEY_COMPLETE"},
        {"group": "B. Điều chỉnh sau góp ý GV (16/10)", "req_id": "REQ-B4", "short_title": "Khảo sát Cụm 2 (CPU–SSD Q1–Q8)", "status": "SURVEY_COMPLETE"},
        {"group": "B. Điều chỉnh sau góp ý GV (16/10)", "req_id": "REQ-B5", "short_title": "Khảo sát Cụm 3 (GPU FAISS Q1–Q8)", "status": "SURVEY_COMPLETE"},
        {"group": "C. Ba Mục tiêu cốt lõi Chuyên đề", "req_id": "REQ-C1", "short_title": "Mục tiêu 1: Trình bày ANN & cải tiến", "status": "COMPLETE"},
        {"group": "C. Ba Mục tiêu cốt lõi Chuyên đề", "req_id": "REQ-C2", "short_title": "Mục tiêu 2: Đề xuất song song kiểm chứng", "status": "COMPLETE_WITH_SCOPE"},
        {"group": "C. Ba Mục tiêu cốt lõi Chuyên đề", "req_id": "REQ-C3", "short_title": "Mục tiêu 3: Cài đặt & thực nghiệm công bằng", "status": "COMPLETE_WITH_SCOPE"},
        {"group": "D. Đề xuất A×D 15/11 (P0–P6, H1–H3)", "req_id": "REQ-D1", "short_title": "P0/P1 Tương thích .pipnn & Parity", "status": "COMPLETE_WITH_SCOPE"},
        {"group": "D. Đề xuất A×D 15/11 (P0–P6, H1–H3)", "req_id": "REQ-D2", "short_title": "P2 Common multi-walker & ON/OFF split", "status": "COMPLETE"},
        {"group": "D. Đề xuất A×D 15/11 (P0–P6, H1–H3)", "req_id": "REQ-D3", "short_title": "P3/P4 Kiểm định H1–H2 (Stage D 378 lượt)", "status": "COMPLETE_WITH_SCOPE"},
        {"group": "D. Đề xuất A×D 15/11 (P0–P6, H1–H3)", "req_id": "REQ-D4", "short_title": "H3 / TP-CG lập lịch động (P5 gốc)", "status": "NO_GO"},
        {"group": "D. Đề xuất A×D 15/11 (P0–P6, H1–H3)", "req_id": "REQ-D5", "short_title": "H3 Overlap-Aware Seed Assignment", "status": "REFUTED_WITH_SCOPE"},
        {"group": "D. Đề xuất A×D 15/11 (P0–P6, H1–H3)", "req_id": "REQ-D6", "short_title": "AverSearch-inspired E0–E3 queue roles", "status": "REFUTED_WITH_SCOPE"},
        {"group": "D. Đề xuất A×D 15/11 (P0–P6, H1–H3)", "req_id": "REQ-D7", "short_title": "P6 Cross-host i5 / Dataset 2 / R4–R5 / G3", "status": "NOT_RUN"},
        {"group": "D. Đề xuất A×D 15/11 (P0–P6, H1–H3)", "req_id": "REQ-D8", "short_title": "Lịch sử R86 Narrow A3 & PipeANN D1/D4/D6", "status": "HOLD"},
        {"group": "D. Đề xuất A×D 15/11 (P0–P6, H1–H3)", "req_id": "REQ-D9", "short_title": "Benchmark native GPU & scheduler SSD mới", "status": "OUT_OF_SCOPE"},
        {"group": "E. G2 v2 design-3.1 & Closeout", "req_id": "REQ-E1", "short_title": "G2 v2 design-3.1 OFF 144/144 & Quality 18/18", "status": "COMPLETE_WITH_SCOPE"},
        {"group": "E. G2 v2 design-3.1 & Closeout", "req_id": "REQ-E2", "short_title": "Tích hợp A×D 2×2 & Mô hình BUILD–SEARCH", "status": "COMPLETE_WITH_SCOPE"},
        {"group": "E. G2 v2 design-3.1 & Closeout", "req_id": "REQ-E3", "short_title": "Audit độc lập (0 diff) & Archive 9/9 SHA", "status": "COMPLETE"},
        {"group": "E. G2 v2 design-3.1 & Closeout", "req_id": "REQ-E4", "short_title": "Xác nhận phạm vi EXPLORATORY & đóng gói", "status": "ADVISOR_DECISION_REQUIRED"},
        {"group": "E. G2 v2 design-3.1 & Closeout", "req_id": "REQ-E5", "short_title": "Quyết định chốt G2 hay mở G3 mới", "status": "ADVISOR_DECISION_REQUIRED"},
    ]
    write_csv(out, "table13_objective_closure_summary.csv", list(oc_rows[0].keys()), oc_rows)

    # 14. Canonical A×D Integration JSON
    canonical = {
        "schema": "task_a_d_canonical_handoff_v1",
        "cohort": "MS-Turing-1M, R90 P0A v1.3, C160 K1024 N2, SEED=555, three four-thread builds per arm",
        "sources_relative_to_repository": [
            "configs/axd_g2_v2_build_reference.json",
            "../artifact-evidence/axd-g2-v2-off-design3_1_run2-analysis.json",
            "../artifact-evidence/axd-g2-v2-quality-design3/quality.json",
            "../artifact-evidence/axd-g2-v2-final-audit-design3_1/audit_results.json",
        ],
        "build_graph_receipts": build_rows,
        "four_cells": [
            {**row, "build_mean_s": b_stock if row["build_arm"] == "Stock" else b_fast}
            for row in arm_rows[:4]
        ],
        "test_quality_by_graph": [
            {key: row[key] for key in ("graph", "recall_mean", "recall_lcb95")}
            for row in pg_rows
        ],
        "protocol": analysis["protocol"],
        "revision": analysis["revision"],
        "evidence_label": analysis["evidence_label"],
        "graph_population_ci": analysis["graph_population_ci"],
        "verdict_primary": analysis["verdict"],
        "verdict_build_search": bs["status"],
        "audit_verdict": "AUDIT_PASS",
        "audit_discrepancies": len(audit["discrepancies"]),
        "commits": {
            "search_source_f2cd634": "f2cd634b837a70735c3e31e5956f0524bfc26675",
            "g2_closeout_4bc70ff": "4bc70ff867c3945f39514be7df86cadb9849671d",
            "final_status_d0f4816": "d0f4816",
            "synthesis_a0916db": "a0916db45563ae90bbe8d4e73ad202b6a2991d3e",
        },
        "measured_build_host_a": {
            "host": "Host A (tai-linux, 4 build threads, historical R90 P0A v1.3 receipts)",
            "stock_mean_s": b_stock,
            "fast_mean_s": b_fast,
            "delta_s": b_stock - b_fast,
            "reduction_pct": (1.0 - b_fast / b_stock) * 100.0,
            "total_6_graphs_bytes": sum(build_ref[g]["graph_bytes"] for g in pg_order),
        },
        "measured_search_host_d": {
            "host": "Host D (AMD Ryzen 5 PRO 4650U, multi-user.target, p=2, S=16, beam=432, jobs=1)",
            "primary_reduction_pct": point_pct,
            "speedup": analysis["speedup"],
            "primary_ci95_pct": [x * 100.0 for x in analysis["primary_reduction_ci95"]],
            "drift_ci95_pct": drift_pct,
            "query_bootstrap_ci95_pct": qboot_pct,
            "joint_bootstrap_ci95_pct": jboot_pct,
            "interaction_fast_minus_stock_us": arms["interaction_fast_minus_stock_us"],
            "interaction_ci95_us": arms["interaction_fast_minus_stock_us_ci95"],
            "interaction_log": arms["interaction_fast_minus_stock_log"],
            "interaction_log_ci95": arms["interaction_fast_minus_stock_log_ci95"],
            "quality_gate_a_pass": quality["A_pass"],
            "quality_gate_b_pass": quality["B_pass"],
            "gate_b_fast_minus_stock_recall": quality["arm_difference"],
            "gate_b_ci95": quality["arm_ci95"],
        },
        "modeled_two_host_build_search": {
            "warning": "MODELED TWO-HOST ADDITIVE COMBINATION ONLY — NOT NATIVE SINGLE-HOST END-TO-END; TRANSFER/LOAD EXCLUDED AND UNKNOWN",
            "workloads": bs_rows,
        },
    }
    (out / "table14_axd_canonical_integration.json").write_text(
        json.dumps(canonical, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Exported 14 verified tables into {out}")


if __name__ == "__main__":
    main()
