# Task D × Task A — P1 Instrumentation ON/OFF Parity & Determinism Report

**Status:** **PASS (100% Exact Parity)**  
**Engine Policy:** `task_da::Index` (`entry_best_first_v1`, `workers=1`, `entry=0`, `k=10`)  
**Binary:** `build-task-da/task_da_p1_eval` (`sha256: 59dde1cc4bcee8ac66c360db298a8b088ad2da8c1a1bb273d75deeb6a1e0836b`)  
**Matrix Source:** [P1_CALIBRATION_MATRIX.csv](P1_CALIBRATION_MATRIX.csv) / [P1_CALIBRATION_MATRIX.json](P1_CALIBRATION_MATRIX.json)  
**External Parity Summary:** `../artifact-evidence/p1-full-validation-20261117T225717+0700/parity/parity_summary.json`

---

## 1. Executive Summary

Across **44** distinct `(split, graph, beam)` ON/OFF run pairs totaling **1,804,000** paired per-query comparisons (`3,608,000` query executions counting both `ON` and `OFF`), enabling Task D 64-bit instrumentation (`--mode ON`) produced **zero mismatches (`0 / 1,804,000`)** relative to `--mode OFF`:

| Cohort | Run Pairs | Queries / Pair | Total Paired Queries | Exact IDs | Exact Squared L2 | Complete Top-k | Counter Invariants | `OFF` Counters Null | Mismatches |
|---|---:|---:|---:|---|---|---|---|---|---|
| `dry_500` (`A0_R1`, `A3_R1`, `A3_R1_jobs6`, `A3_R2`) | 8 | 500 | 4,000 | **TRUE (8/8)** | **TRUE (8/8)** | **TRUE (8/8)** | **TRUE (8/8)** | **TRUE (8/8)** | **0** |
| `val_10k` (`9 graphs × 2 targets`) | 18 | 10,000 | 180,000 | **TRUE (18/18)** | **TRUE (18/18)** | **TRUE (18/18)** | **TRUE (18/18)** | **TRUE (18/18)** | **0** |
| `test_90k` (`9 graphs × 2 targets`) | 18 | 90,000 | 1,620,000 | **TRUE (18/18)** | **TRUE (18/18)** | **TRUE (18/18)** | **TRUE (18/18)** | **TRUE (18/18)** | **0** |
| **Total** | **44** | — | **1,804,000** | **PASS (44/44)** | **PASS (44/44)** | **PASS (44/44)** | **PASS (44/44)** | **PASS (44/44)** | **0** |

---

## 2. Counter Invariants & Arithmetic Conservation

Evaluated via `research/task_da/evaluate_p1.py` (`--parity-off`):
1. Top-10 `ids` (`len == 10`, strictly valid `[0, 1000000)`, zero duplicates) identical slot-by-slot between `ON` and `OFF`.
2. `squared_l2` identical IEEE-754 float values slot-by-slot (`exact_squared_l2_match=true`) and monotonically non-decreasing in `(squared_l2, id)`.
3. `complete_top_k == true` across every query (`incomplete_top_k_queries == 0` in all 44 cohorts).
4. `OFF` rows strictly emit `counters: null` (`off_counters_all_null=true`).
5. `ON` rows emit all 5 non-negative 64-bit counters (`distance_evaluations`, `expansions`, `neighbor_attempts`, `already_seen_attempts`, `frontier_insertions`), satisfying `distance_evaluations == 1 + (neighbor_attempts - already_seen_attempts)` (verified on every query and visible in the mean columns below, while avoiding Historical Task A's 32-bit `avg_cmps` overflow observed at `t0998` around `~4.29e9`).

---

## 3. `dry_500` Pre-Flight Parity & Single- vs Multi-Query Thread Repeatability

| Config | Beam | Queries | Recall@10 | Mean DE | Mean Exp | Mean Neighbor Att | Mean Already Seen | Mean Frontier Ins | Mismatches |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `A0_R1` | 384 | 500 | 0.989600 | 16886.53 | 388.00 | 22040.86 | 5155.33 | 1485.34 | 0 |
| `A0_R1` | 896 | 500 | 0.998600 | 36001.91 | 899.10 | 51512.04 | 15511.13 | 3023.61 | 0 |
| `A3_R1` (`--jobs 1`) | 832 | 500 | 0.987600 | 22546.41 | 835.82 | 31575.53 | 9030.12 | 2627.16 | 0 |
| `A3_R1` (`--jobs 1`) | 2176 | 500 | 0.997200 | 52218.19 | 2178.83 | 81909.53 | 29692.33 | 6227.28 | 0 |
| `A3_R1_jobs6` (`--jobs 6`) | 832 | 500 | 0.987600 | 22546.41 | 835.82 | 31575.53 | 9030.12 | 2627.16 | 0 |
| `A3_R1_jobs6` (`--jobs 6`) | 2176 | 500 | 0.997200 | 52218.19 | 2178.83 | 81909.53 | 29692.33 | 6227.28 | 0 |
| `A3_R2` | 832 | 500 | 0.986600 | 22554.25 | 835.97 | 31578.15 | 9024.90 | 2638.62 | 0 |
| `A3_R2` | 2176 | 500 | 0.996800 | 52222.75 | 2178.84 | 81894.93 | 29673.18 | 6241.92 | 0 |

**Phase 5 Explicit Determinism Repeat Check (`determinism_check/`, `A3_r1`, `dry_500.ids`):** Running `--jobs 1` twice sequentially (`jobs1_run1`, `jobs1_run2`) and `--jobs 6` (`jobs6`) yielded **100% byte-identical SHA-256 JSONLs**:
- `beam_896_OFF.jsonl`: `c8749812797a80cd2c813aa1acc64fd018a786f73b3960bc73c647e111ab6691`
- `beam_896_ON.jsonl`: `7344630e6352f9f78cdf7726670a109c007f900be44fdf6e2b16fd6cb7bcc7b0`
- `beam_2176_OFF.jsonl`: `21979d3330b4caad0af4b07f5e3783873305a6f5623692f0e3a0fee63524bcaa`
- `beam_2176_ON.jsonl`: `43c76e914e6cddec4128067b3c2f60bef212f43f86ad2914098e0957b99a7a1e`

---

## 4. Full `val_10k` & `test_90k` Counter Summary Across All 18 Configurations

All `18/18` `val_10k` (`10,000` queries each) and `18/18` `test_90k` (`90,000` queries each) pairs achieved `exact_ids_match=true`, `exact_squared_l2_match=true`, `exact_complete_top_k_match=true`, `counter_invariants_pass=true`, `off_counters_all_null=true`, and `mismatches=0`.

| Graph | Target | Frozen Beam | `val_10k` Mean DE / Exp | `test_90k` Mean DE | `test_90k` Mean Exp | `test_90k` Neighbor Att | `test_90k` Already Seen | `test_90k` Frontier Ins | Seen / Neighbor Ratio |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `A0_r1` | `t0990` | 416 | 18208.0 / 419.8 | 18196.1 | 419.8 | 23948.2 | 5753.2 | 1579.7 | 0.240 |
| `A0_r1` | `t0998` | 896 | 36049.2 / 899.1 | 36050.5 | 899.1 | 51681.3 | 15631.9 | 3012.9 | 0.302 |
| `A0_r2` | `t0990` | 416 | 18209.1 / 419.8 | 18193.2 | 419.8 | 23951.0 | 5758.8 | 1579.9 | 0.240 |
| `A0_r2` | `t0998` | 896 | 36042.0 / 899.1 | 36042.8 | 899.1 | 51689.2 | 15647.4 | 3012.6 | 0.303 |
| `A0_r3` | `t0990` | 416 | 18206.2 / 419.8 | 18190.5 | 419.8 | 23944.5 | 5754.9 | 1580.0 | 0.240 |
| `A0_r3` | `t0998` | 896 | 36037.1 / 899.1 | 36038.1 | 899.1 | 51674.4 | 15637.3 | 3012.8 | 0.303 |
| `A1_r1` | `t0990` | 416 | 18212.4 / 419.9 | 18196.8 | 419.8 | 23955.3 | 5759.5 | 1580.0 | 0.240 |
| `A1_r1` | `t0998` | 896 | 36048.6 / 899.1 | 36050.0 | 899.1 | 51698.3 | 15649.3 | 3012.8 | 0.303 |
| `A1_r2` | `t0990` | 416 | 18207.9 / 419.8 | 18194.6 | 419.8 | 23946.3 | 5752.7 | 1579.7 | 0.240 |
| `A1_r2` | `t0998` | 928 | 37167.2 / 931.1 | 37169.9 | 931.1 | 53533.3 | 16364.4 | 3106.4 | 0.306 |
| `A1_r3` | `t0990` | 416 | 18207.4 / 419.8 | 18191.8 | 419.8 | 23947.0 | 5756.3 | 1579.7 | 0.240 |
| `A1_r3` | `t0998` | 896 | 36040.3 / 899.1 | 36040.8 | 899.1 | 51680.4 | 15640.5 | 3012.6 | 0.303 |
| `A3_r1` | `t0990` | 896 | 24005.5 / 899.7 | 24026.3 | 899.7 | 33918.8 | 9893.5 | 2796.5 | 0.292 |
| `A3_r1` | `t0998` | 2176 | 52028.5 / 2178.8 | 52084.2 | 2178.8 | 81794.9 | 29711.7 | 6220.7 | 0.363 |
| `A3_r2` | `t0990` | 928 | 24768.0 / 931.6 | 24788.1 | 931.6 | 35111.0 | 10323.9 | 2887.0 | 0.294 |
| `A3_r2` | `t0998` | 2304 | 54629.6 / 2306.8 | 54686.0 | 2306.8 | 86562.4 | 31877.3 | 6555.4 | 0.368 |
| `A3_r3` | `t0990` | 896 | 24007.3 / 899.7 | 24027.1 | 899.7 | 33922.8 | 9896.7 | 2795.6 | 0.292 |
| `A3_r3` | `t0998` | 2112 | 50723.0 / 2114.9 | 50775.7 | 2114.8 | 79412.4 | 28637.7 | 6052.9 | 0.361 |

**Key Structural Observation:** Because `entry_best_first_v1` lacks Task A's `QP.cut=1.35` pruning cutoff and offset batching, `mean_expansions` closely tracks `beam + ~3` (e.g., `419.8` at `beam=416`, `899.1–899.7` at `beam=896`, `2114.8–2306.8` at `beam=2112–2304`), whereas Task A historical `avg_visited` stopped early (`370` at `384`, `740–741` at `896`, `712` at `832`, `1448–1449` at `2176`). `val_10k` and `test_90k` mean work counters align closely (`<0.2%` relative difference), confirming homogeneous query-workload complexity across splits.
