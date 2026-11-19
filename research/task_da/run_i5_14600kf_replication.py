#!/usr/bin/env python3
"""Reproducible Stage D replication runner prepared for Intel Core i5-14600KF.

Enforces:
- Strict Intel hybrid P-core detection via /sys/devices/cpu_core/cpus and
  /sys/devices/system/cpu/cpu*/topology/thread_siblings_list (physical sibling-0
  P-cores only; E-cores and HT siblings are strictly excluded).
- Fail-closed host check: refuses benchmark execution on non-i5-14600KF hosts
  unless --dry-run / --preflight-only is requested.
- Full SHA-256 verification of all 9 graphs (A0/A1/A3 x r1..r3), MSTuring_1M_v1
  base/query/groundtruth, val_10k/test_90k splits, warmup/pilot query IDs, and
  the frozen 45-cell val_10k manifest before launching any search.
- Read-only thermal and CPU frequency telemetry before and after every repeat
  (no sudo, no governor/power/affinity/ASLR changes).
- Sequential execution of all 63 frozen cells x (5 interleaved OFF repeats +
  1 separate ON diagnostic), exact ON/OFF parity checks, outer n=3 graph-seed
  Student-t (df=2) CI95 reporting, and EVIDENCE_CHECKSUMS.csv generation.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
import platform
import socket
import statistics
import struct
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

T_CRIT_95_DF2 = 4.302652729911275
T_CRIT_95_DF4 = 2.7764451051977987

EXPECTED_GRAPH_SHA256: Dict[str, str] = {
    "A0_r1": "55df31ac9b7716f779dca332ce9360c9e21a065f9298ec1c92c8ccdd37d72522",
    "A0_r2": "e0e0be004e6b3bd9cf55c4f620863e2d002aa5798a9e258f5330ee2f1d1ee6b9",
    "A0_r3": "a4ad500421b95700f34d1d2e267640decffbf3f54a88fdb2b3708cf33448405b",
    "A1_r1": "7da34f1c3e0ff8a67092a2c9f96bc35122b88fdbe36c59347d1f213b55c46979",
    "A1_r2": "b08ef703f162b75f6c2512d29d58113212c185030dc5b230a7488c8244c82ede",
    "A1_r3": "1b51bf7115450c208bc209d9419fd42425c8393e75f712ec1fabdd7fb69787b1",
    "A3_r1": "0fff20ec47502c675c4905787d319390e49fa5bee856ac16c814c74697c5fbb2",
    "A3_r2": "3d6113e721fa26c8a82f77d2e5bcbc60b6e55352532814694afb146c9c5f9c6c",
    "A3_r3": "11f7a5059af309db0a08c4a9e0484d194c8ea5c6f17d8c8f9f67ceb299d85829",
}

EXPECTED_DATASET_SHA256: Dict[str, str] = {
    "base.1M.fbin": "44e83e1dd4c65999b75873101adc5ac06ca900d259a2befd05c2c3aa28ff4042",
    "query.public.100K.fbin": "48d087a17bec15a5ec9ea526fe9bd14ac31bbbb5cd200817b341adbb77695644",
    "groundtruth.public.100K.ibin": "fa5acf5ab262b42355296e99f920e6aa863f48820ca6f70fa37ca7966634c344",
    "val_10k.ids": "a3c948e9aac4f40c1fb818a6f784c4fbb56473a0769affe3344493ed4eb87f57",
    "test_90k.ids": "af871517d88aaad90549ba2fde0d4ed745f59400037a757f17bc93fa479bbfa3",
    "val10k_manifest": "f98c0454f065e8debf10e7849f2ebcd1061d294980c8ddad5f836269175b4bc5",
    "pilot_ids": "18d8b901e925d71c0ddb2d043bf2cba12edab4061859da833bd1ccc37790c1b0",
    "warmup_ids": "199ca6066269641347280d6ef4eaab39efee3397b87c23cd74d38ee85bcd4783",
}

CONFIG_SPECS: List[Tuple[str, int, int, str]] = [
    ("p1_base", 1, 8, "flat"),
    ("p2_S8_set", 2, 8, "set"),
    ("p2_S8_flat", 2, 8, "flat"),
    ("p2_S16_flat", 2, 16, "flat"),
    ("p4_S8_set", 4, 8, "set"),
    ("p4_S8_flat", 4, 8, "flat"),
    ("p4_S16_flat", 4, 16, "flat"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def parse_cpu_list_spec(spec: str) -> List[int]:
    cpus: List[int] = []
    for part in spec.strip().split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo_s, hi_s = part.split("-", 1)
            cpus.extend(range(int(lo_s), int(hi_s) + 1))
        else:
            cpus.append(int(part))
    return sorted(set(cpus))


def read_cpu_model(proc_cpuinfo: Path = Path("/proc/cpuinfo")) -> str:
    if not proc_cpuinfo.exists():
        return "UNKNOWN"
    for line in proc_cpuinfo.read_text(errors="replace").splitlines():
        if line.lower().startswith("model name"):
            return line.split(":", 1)[1].strip()
    return "UNKNOWN"


def detect_intel_pcore_physical_cpus(sys_root: Path = Path("/sys")) -> Dict[str, object]:
    """Identify distinct physical P-cores (sibling-0 only) on Intel hybrid CPUs."""
    pcore_file = sys_root / "devices/cpu_core/cpus"
    ecore_file = sys_root / "devices/cpu_atom/cpus"
    hybrid = pcore_file.exists()
    pcore_logical = parse_cpu_list_spec(pcore_file.read_text()) if hybrid else []
    ecore_logical = parse_cpu_list_spec(ecore_file.read_text()) if ecore_file.exists() else []
    pcore_set = set(pcore_logical)

    # Group by physical core using thread_siblings_list (pick lowest logical ID per core).
    seen_groups = set()
    physical_pcores: List[int] = []
    sibling_groups: List[List[int]] = []
    for cpu in pcore_logical:
        sib_path = sys_root / f"devices/system/cpu/cpu{cpu}/topology/thread_siblings_list"
        if sib_path.exists():
            sibs = parse_cpu_list_spec(sib_path.read_text())
        else:
            sibs = [cpu]
        key = tuple(sibs)
        if key in seen_groups:
            continue
        seen_groups.add(key)
        # Ensure sibling group lies wholly inside P-core set.
        if all(s in pcore_set for s in sibs):
            sibling_groups.append(sibs)
            physical_pcores.append(sibs[0])

    return {
        "hybrid_sysfs_present": hybrid,
        "pcore_logical": pcore_logical,
        "ecore_logical": ecore_logical,
        "pcore_sibling_groups": sibling_groups,
        "physical_pcores_sibling0": physical_pcores,
        "recommended_cpu_lists": {
            "1": physical_pcores[:1],
            "2": physical_pcores[:2],
            "4": physical_pcores[:4],
        }
        if len(physical_pcores) >= 4
        else None,
    }


def read_telemetry_snapshot(cpus: Sequence[int], sys_root: Path = Path("/sys")) -> Dict[str, object]:
    """Read-only temperature, frequency, and governor snapshot (no sudo)."""
    temps_c: Dict[str, float] = {}
    hwmon_root = sys_root / "class/hwmon"
    if hwmon_root.exists():
        for hm in sorted(hwmon_root.iterdir()):
            name_p = hm / "name"
            name = name_p.read_text(errors="replace").strip() if name_p.exists() else hm.name
            if name not in ("coretemp", "k10temp", "zenpower", "acpitz"):
                continue
            for tf in sorted(hm.glob("temp*_input")):
                lbl_p = hm / tf.name.replace("_input", "_label")
                lbl = lbl_p.read_text(errors="replace").strip() if lbl_p.exists() else tf.stem
                try:
                    temps_c[f"{name}:{lbl}"] = round(int(tf.read_text().strip()) / 1000.0, 2)
                except (OSError, ValueError):
                    pass

    freqs_khz: Dict[str, int] = {}
    governors: Dict[str, str] = {}
    for c in cpus:
        fp = sys_root / f"devices/system/cpu/cpu{c}/cpufreq/scaling_cur_freq"
        gp = sys_root / f"devices/system/cpu/cpu{c}/cpufreq/scaling_governor"
        if fp.exists():
            try:
                freqs_khz[f"cpu{c}"] = int(fp.read_text().strip())
            except (OSError, ValueError):
                pass
        if gp.exists():
            try:
                governors[f"cpu{c}"] = gp.read_text().strip()
            except OSError:
                pass

    return {
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "temps_c": temps_c,
        "freqs_khz": freqs_khz,
        "governors": governors,
        "loadavg_1m": os.getloadavg()[0] if hasattr(os, "getloadavg") else None,
    }


def verify_inputs(
    graph_root: Path,
    v3_split_dir: Path,
    val10k_manifest: Path,
    pilot_ids: Path,
    warmup_ids: Path,
    allow_custom_test_ids: bool,
) -> Dict[str, str]:
    verified: Dict[str, str] = {}

    def check(label: str, path: Path, expected: Optional[str]) -> None:
        if not path.exists():
            raise FileNotFoundError(f"Missing required artifact ({label}): {path}")
        got = sha256_file(path)
        if expected is not None and got != expected:
            raise ValueError(f"SHA-256 mismatch for {label} ({path}): expected {expected}, got {got}")
        verified[label] = got

    data_dir = graph_root / "data/MSTuring_1M_v1"
    check("base.1M.fbin", data_dir / "base.1M.fbin", EXPECTED_DATASET_SHA256["base.1M.fbin"])
    check("query.public.100K.fbin", data_dir / "query.public.100K.fbin", EXPECTED_DATASET_SHA256["query.public.100K.fbin"])
    check("groundtruth.public.100K.ibin", data_dir / "groundtruth.public.100K.ibin", EXPECTED_DATASET_SHA256["groundtruth.public.100K.ibin"])
    check("val_10k.ids", v3_split_dir / "val_10k.ids", EXPECTED_DATASET_SHA256["val_10k.ids"])
    check("test_90k.ids", v3_split_dir / "test_90k.ids", EXPECTED_DATASET_SHA256["test_90k.ids"])
    check("val10k_manifest", val10k_manifest, EXPECTED_DATASET_SHA256["val10k_manifest"])
    check("warmup_ids", warmup_ids, EXPECTED_DATASET_SHA256["warmup_ids"])
    check(
        "pilot_ids",
        pilot_ids,
        None if allow_custom_test_ids else EXPECTED_DATASET_SHA256["pilot_ids"],
    )

    for arm in ("A0", "A1", "A3"):
        for seed in ("r1", "r2", "r3"):
            key = f"{arm}_{seed}"
            gp = graph_root / f"experiments/R86/msturing_1m_sixarm/formal_mst1m_v1/{arm}/{seed}/index.graph"
            check(key, gp, EXPECTED_GRAPH_SHA256[key])

    # Verify warmup_ids and pilot_ids are strictly disjoint and pilot_ids subset of test_90k.
    w_set = {int(x) for x in warmup_ids.read_text().split() if x.strip()}
    p_set = {int(x) for x in pilot_ids.read_text().split() if x.strip()}
    t_set = {int(x) for x in (v3_split_dir / "test_90k.ids").read_text().split() if x.strip()}
    if w_set & p_set:
        raise ValueError("warmup_ids and test/pilot_ids overlap!")
    if not p_set.issubset(t_set):
        raise ValueError("test/pilot_ids is not a strict subset of test_90k.ids!")
    return verified


def recall_from_jsonl(jsonl_path: Path, gt_buf: bytes, k_gt: int) -> Tuple[float, float, int]:
    vals: List[float] = []
    with jsonl_path.open() as f:
        for line in f:
            row = json.loads(line)
            qid = row["query_id"]
            ids = row["ids"][:10]
            off = qid * k_gt * 4
            gt10 = set(struct.unpack("<10I", gt_buf[off : off + 40]))
            vals.append(len(gt10.intersection(ids)) / 10.0)
    n = len(vals)
    mu = sum(vals) / n
    var = sum((x - mu) ** 2 for x in vals) / (n - 1)
    se = math.sqrt(var / n)
    return mu, se, n


def check_on_off_exact_parity(on_jsonl: Path, off_jsonl: Path) -> Tuple[bool, bool]:
    """Verify exact bit-identical IDs/distances between ON and OFF + counter invariants."""
    with on_jsonl.open() as f_on, off_jsonl.open() as f_off:
        for l_on, l_off in zip(f_on, f_off):
            r_on = json.loads(l_on)
            r_off = json.loads(l_off)
            if r_on["query_id"] != r_off["query_id"] or r_on["ids"] != r_off["ids"] or r_on["squared_l2"] != r_off["squared_l2"]:
                return False, False
            c = r_on["counters"]
            if c["expansions"] != c["unique_expansions"] + c["duplicate_expansions"]:
                return True, False
            if c["distance_evaluations"] != c["unique_distance_evaluations"] + c["duplicate_distance_evaluations"]:
                return True, False
    return True, True


def summary_stats(vals: Sequence[float], t_crit: float) -> Dict[str, float]:
    n = len(vals)
    mu = statistics.mean(vals)
    sd = statistics.stdev(vals) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n > 1 else 0.0
    return {
        "n": n,
        "mean": mu,
        "median": statistics.median(vals),
        "stdev": sd,
        "se": se,
        "min": min(vals),
        "max": max(vals),
        "ci95_low": mu - t_crit * se,
        "ci95_high": mu + t_crit * se,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Stage D P2 Replication Runner for Intel Core i5-14600KF.")
    ap.add_argument("--binary", type=Path, required=True, help="Path to Release task_da_p2_eval binary built on this host.")
    ap.add_argument("--graph-root", type=Path, required=True, help="Root containing data/MSTuring_1M_v1 and experiments/R86/...")
    ap.add_argument("--v3-split-dir", type=Path, required=True, help="Directory containing val_10k.ids and test_90k.ids.")
    ap.add_argument("--val10k-manifest", type=Path, required=True, help="Frozen stage_d_val10k_45cells_manifest.json.")
    ap.add_argument("--pilot-ids", type=Path, required=True, help="Query IDs file (frozen pilot_test_3000.ids or disjoint test subset).")
    ap.add_argument("--warmup-ids", type=Path, required=True, help="Frozen warmup_val_100.ids.")
    ap.add_argument("--out-dir", type=Path, required=True, help="Dedicated host-specific external evidence output directory.")
    ap.add_argument("--repeats", type=int, default=5, help="Number of interleaved OFF process repeats (default: 5, minimum: 5).")
    ap.add_argument("--pcores", type=str, default="", help="Optional explicit 4 physical sibling-0 P-core IDs (e.g. '0,2,4,6'), validated against cpu_core.")
    ap.add_argument("--disjoint-test-ids", action="store_true", help="Allow custom test IDs subset of test_90k.ids (still disjoint from warmup_ids).")
    ap.add_argument("--resume", action="store_true", help="Skip already completed verified repeats inside --out-dir.")
    ap.add_argument("--dry-run", action="store_true", help="Validate host topology, P-core affinity, and all SHA-256 inputs without running benchmarks.")
    args = ap.parse_args(argv)

    if args.repeats < 5:
        raise SystemExit("ERROR: --repeats must be >= 5 per Stage D protocol.")

    cpu_model = read_cpu_model()
    topo = detect_intel_pcore_physical_cpus()
    is_i5_14600kf = "14600KF" in cpu_model.upper()

    if args.pcores:
        chosen_pcores = parse_cpu_list_spec(args.pcores)
        if len(chosen_pcores) != 4:
            raise SystemExit("ERROR: --pcores must specify exactly 4 physical P-cores.")
        if topo["hybrid_sysfs_present"]:
            if not set(chosen_pcores).issubset(set(topo["physical_pcores_sibling0"])):
                raise SystemExit(
                    f"ERROR: --pcores {chosen_pcores} contains non-P-core or HT-sibling CPUs. "
                    f"Valid physical sibling-0 P-cores: {topo['physical_pcores_sibling0']}"
                )
    else:
        chosen_pcores = topo["physical_pcores_sibling0"][:4] if len(topo["physical_pcores_sibling0"]) >= 4 else []

    preflight = {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "cpu_model": cpu_model,
        "is_i5_14600kf": is_i5_14600kf,
        "topology": topo,
        "selected_4_physical_pcores": chosen_pcores,
        "dry_run": args.dry_run,
    }

    if not args.binary.exists():
        raise SystemExit(f"ERROR: Binary not found: {args.binary}")
    preflight["binary_sha256"] = sha256_file(args.binary)

    verified_hashes = verify_inputs(
        args.graph_root,
        args.v3_split_dir,
        args.val10k_manifest,
        args.pilot_ids,
        args.warmup_ids,
        args.disjoint_test_ids,
    )
    preflight["verified_inputs_count"] = len(verified_hashes)

    if args.dry_run:
        print(json.dumps(preflight, indent=2))
        if not is_i5_14600kf:
            print("PREFLIGHT_NOTE: Host is NOT i5-14600KF (benchmark execution would fail closed). Status: NOT_RUN.")
        elif len(chosen_pcores) < 4:
            print("PREFLIGHT_ERROR: Fewer than 4 physical P-cores detected.")
            return 2
        else:
            print("PREFLIGHT_OK: Ready to execute Stage D replication on i5-14600KF.")
        return 0

    if not is_i5_14600kf:
        raise SystemExit(
            f"REFUSED (fail-closed): Detected CPU '{cpu_model}' is not Intel Core i5-14600KF. "
            "Never mix hosts; pass --dry-run to validate preflight only."
        )
    if len(chosen_pcores) < 4 or not topo["hybrid_sysfs_present"]:
        raise SystemExit(
            "REFUSED (fail-closed): Could not verify >= 4 physical sibling-0 P-cores from /sys/devices/cpu_core/cpus."
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    h1_dir = args.out_dir / "h1_off"
    h2_dir = args.out_dir / "h2_on"
    h1_dir.mkdir(exist_ok=True)
    h2_dir.mkdir(exist_ok=True)

    manifest = json.loads(args.val10k_manifest.read_text())["selected_45_cells"]
    cpu_map = {
        1: chosen_pcores[:1],
        2: chosen_pcores[:2],
        4: chosen_pcores[:4],
    }

    base_path = args.graph_root / "data/MSTuring_1M_v1/base.1M.fbin"
    query_path = args.graph_root / "data/MSTuring_1M_v1/query.public.100K.fbin"
    gt_path = args.graph_root / "data/MSTuring_1M_v1/groundtruth.public.100K.ibin"

    cells: List[Dict[str, object]] = []
    for arm in ("A0", "A1", "A3"):
        for seed in ("r1", "r2", "r3"):
            gk = f"{arm}_{seed}"
            gp = args.graph_root / f"experiments/R86/msturing_1m_sixarm/formal_mst1m_v1/{arm}/{seed}/index.graph"
            for cfg_name, w, S, merge_impl in CONFIG_SPECS:
                s_key = f"S{S}"
                b_info = manifest[gk][s_key][str(w)]
                cells.append(
                    {
                        "cell_id": f"{gk}_{cfg_name}",
                        "arm": arm,
                        "seed": seed,
                        "graph_key": gk,
                        "graph_path": str(gp),
                        "config": cfg_name,
                        "workers": w,
                        "sync_interval": S,
                        "merge_impl": merge_impl,
                        "beam": int(b_info["beam"]),
                        "val10k_recall": float(b_info["recall_at_10"]),
                        "val10k_lcb95": float(b_info["lcb95_q"]),
                    }
                )

    def run_single(cell: Dict[str, object], mode: str, out_sub: Path) -> Path:
        summary_file = out_sub / "p2_eval_summary.json"
        if summary_file.exists():
            if args.resume:
                return summary_file
            raise FileExistsError(f"Refusing to overwrite existing output without --resume: {summary_file}")
        out_sub.mkdir(parents=True, exist_ok=True)
        w = int(cell["workers"])
        cpus = cpu_map[w]
        pre_tel = read_telemetry_snapshot(cpus)
        cmd = [
            str(args.binary),
            "pipnn",
            str(cell["graph_path"]),
            str(base_path),
            str(query_path),
            "--entry",
            "0",
            "--query-ids",
            str(args.pilot_ids),
            "--warmup-ids",
            str(args.warmup_ids),
            "--k",
            "10",
            "--beams",
            str(cell["beam"]),
            "--workers",
            str(w),
            "--sync-interval",
            str(cell["sync_interval"]),
            "--merge-impl",
            str(cell["merge_impl"]),
            "--jobs",
            "1",
            "--cpu-list",
            ",".join(str(c) for c in cpus),
            "--mode",
            mode,
            "--out-dir",
            str(out_sub),
        ]
        subprocess.run(cmd, check=True)
        post_tel = read_telemetry_snapshot(cpus)
        (out_sub / "host_telemetry.json").write_text(
            json.dumps({"pre": pre_tel, "post": post_tel, "requested_cpus": cpus}, indent=2) + "\n"
        )
        # Verify observed_cpus match requested P-cores strictly.
        sj = json.loads(summary_file.read_text())
        if sj.get("observed_cpus") != cpus:
            raise RuntimeError(
                f"Affinity verification failed for {out_sub}: requested {cpus}, observed {sj.get('observed_cpus')}"
            )
        return summary_file

    # Interleaved OFF repeats across all 63 cells (rotated per repeat).
    for rep in range(args.repeats):
        order = cells[rep % len(cells) :] + cells[: rep % len(cells)]
        if rep % 2 == 1:
            order = list(reversed(order))
        for cell in order:
            run_single(cell, "OFF", h1_dir / f"{cell['cell_id']}_rep{rep}")

    # Separate ON diagnostic pass.
    for cell in cells:
        run_single(cell, "ON", h2_dir / f"{cell['cell_id']}_on")

    # Aggregate results, verify exact ON/OFF parity, and compute outer n=3 CI95s.
    with gt_path.open("rb") as f:
        _, k_gt = struct.unpack("<II", f.read(8))
        gt_buf = f.read()

    cell_summaries: Dict[str, Dict[str, object]] = {}
    for cell in cells:
        cid = str(cell["cell_id"])
        off_means: List[float] = []
        off_p50s: List[float] = []
        off_p95s: List[float] = []
        off_qps: List[float] = []
        for rep in range(args.repeats):
            sj = json.loads((h1_dir / f"{cid}_rep{rep}" / "p2_eval_summary.json").read_text())
            r0 = sj["runs"][0]
            off_means.append(r0["latency_us"]["mean"])
            off_p50s.append(r0["latency_us"]["p50"])
            off_p95s.append(r0["latency_us"]["p95"])
            off_qps.append(r0["qps_wall"])
        on_sj = json.loads((h2_dir / f"{cid}_on" / "p2_eval_summary.json").read_text())
        on_r0 = on_sj["runs"][0]
        off0_sj = json.loads((h1_dir / f"{cid}_rep0" / "p2_eval_summary.json").read_text())
        exact_par, inv_ok = check_on_off_exact_parity(
            Path(on_r0["result_file"]), Path(off0_sj["runs"][0]["result_file"])
        )
        rec, se, nq = recall_from_jsonl(Path(on_r0["result_file"]), gt_buf, k_gt)
        cell_summaries[cid] = {
            **cell,
            "test_recall": rec,
            "test_recall_se": se,
            "test_queries": nq,
            "on_off_exact_match": exact_par,
            "counter_invariants_pass": inv_ok,
            "latency_mean_us": summary_stats(off_means, T_CRIT_95_DF4),
            "latency_p50_us": summary_stats(off_p50s, T_CRIT_95_DF4),
            "latency_p95_us": summary_stats(off_p95s, T_CRIT_95_DF4),
            "qps_wall": summary_stats(off_qps, T_CRIT_95_DF4),
            "counters_mean": on_r0.get("counters_mean", {}),
            "vm_hwm_kib": off0_sj.get("vm_hwm_kib"),
        }

    for arm in ("A0", "A1", "A3"):
        for seed in ("r1", "r2", "r3"):
            p1_m = float(cell_summaries[f"{arm}_{seed}_p1_base"]["latency_mean_us"]["mean"])
            for cfg_name, w, _, _ in CONFIG_SPECS:
                cid = f"{arm}_{seed}_{cfg_name}"
                m = float(cell_summaries[cid]["latency_mean_us"]["mean"])
                cell_summaries[cid]["ratio_of_agg_means"] = p1_m / m
                cell_summaries[cid]["efficiency_agg"] = (p1_m / m) / w

    outer_n3: Dict[str, Dict[str, object]] = {}
    for arm in ("A0", "A1", "A3"):
        outer_n3[arm] = {}
        for cfg_name, _, _, _ in CONFIG_SPECS:
            spds = [float(cell_summaries[f"{arm}_{s}_{cfg_name}"]["ratio_of_agg_means"]) for s in ("r1", "r2", "r3")]
            lats = [float(cell_summaries[f"{arm}_{s}_{cfg_name}"]["latency_mean_us"]["mean"]) for s in ("r1", "r2", "r3")]
            recs = [float(cell_summaries[f"{arm}_{s}_{cfg_name}"]["test_recall"]) for s in ("r1", "r2", "r3")]
            outer_n3[arm][cfg_name] = {
                "replicates_speedup_agg": spds,
                "speedup_agg_outer_n3": summary_stats(spds, T_CRIT_95_DF2),
                "latency_mean_us_outer_n3": summary_stats(lats, T_CRIT_95_DF2),
                "test_recall_outer_n3": summary_stats(recs, T_CRIT_95_DF2),
            }

    final_summary = {
        "protocol": "PROTOCOL_V4_1_P2_EXPLORATORY_0990_STAGE_D_I5_14600KF_REPLICATION",
        "preflight": preflight,
        "verified_hashes": verified_hashes,
        "cells": cell_summaries,
        "outer_replicate_summary_n3": outer_n3,
    }
    (args.out_dir / "i5_14600kf_replication_summary.json").write_text(json.dumps(final_summary, indent=2) + "\n")

    # Export compact CSV.
    with (args.out_dir / "I5_14600KF_REPLICATION_SUMMARY.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "cell_id",
                "arm",
                "seed",
                "workers",
                "sync_interval",
                "merge_impl",
                "beam",
                "val10k_recall",
                "test_recall",
                "mean_lat_us",
                "sd_lat_us",
                "ratio_agg_speedup",
                "efficiency_agg",
                "on_off_exact_match",
                "counter_invariants_pass",
            ]
        )
        for cid, c in cell_summaries.items():
            w.writerow(
                [
                    cid,
                    c["arm"],
                    c["seed"],
                    c["workers"],
                    c["sync_interval"],
                    c["merge_impl"],
                    c["beam"],
                    f"{c['val10k_recall']:.6f}",
                    f"{c['test_recall']:.6f}",
                    f"{c['latency_mean_us']['mean']:.2f}",
                    f"{c['latency_mean_us']['stdev']:.2f}",
                    f"{c['ratio_of_agg_means']:.4f}",
                    f"{c['efficiency_agg']:.4f}",
                    c["on_off_exact_match"],
                    c["counter_invariants_pass"],
                ]
            )

    # Export EVIDENCE_CHECKSUMS.csv.
    rows = []
    for fp in sorted(args.out_dir.rglob("*")):
        if fp.is_file() and fp.name != "EVIDENCE_CHECKSUMS.csv":
            rows.append((str(fp.relative_to(args.out_dir)), fp.stat().st_size, sha256_file(fp)))
    with (args.out_dir / "EVIDENCE_CHECKSUMS.csv").open("w", newline="") as f:
        cw = csv.writer(f)
        cw.writerow(["relative_path", "bytes", "sha256"])
        cw.writerows(rows)

    print("I5_14600KF_REPLICATION_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
