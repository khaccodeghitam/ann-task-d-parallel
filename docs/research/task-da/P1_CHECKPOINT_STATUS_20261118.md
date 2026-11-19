# Task D × Task A — Full P1 Validation Checkpoint Status (2026-11-18T02:12+07:00)

> **[HISTORICAL CHECKPOINT SNAPSHOT — SUPERSEDED BY FINAL P1 DELIVERABLES]:** All remaining `15/18` `test_90k ON/OFF` parity runs and Phase 5 audits completed on `2026-11-18`. See [P1_FULL_VALIDATION_REPORT.md](P1_FULL_VALIDATION_REPORT.md), [P1_CALIBRATION_MATRIX.csv](P1_CALIBRATION_MATRIX.csv), [P1_ON_OFF_PARITY_REPORT.md](P1_ON_OFF_PARITY_REPORT.md), [P1_FULL_GATE_DECISION.md](P1_FULL_GATE_DECISION.md), and [P2_READINESS_CHECKLIST.md](P2_READINESS_CHECKLIST.md).

- **Status (at pause time):** `PAUSED_AT_CHECKPOINT` (later resumed and completed on `2026-11-18`)
- **Historical P0 Status:** Remains `HOLD` (unchanged; see [P0_P1_FINAL_RECONCILIATION_REPORT.md](P0_P1_FINAL_RECONCILIATION_REPORT.md))
- **Active Engine / Protocol:** `task_da::Index` (`entry_best_first_v1`, `workers=1`, `entry=0`, `k=10`), binary `build-task-da/task_da_p1_eval` (`sha256: 59dde1cc4bcee8ac66c360db298a8b088ad2da8c1a1bb273d75deeb6a1e0836b`), GT validator `--gt-aux-min -1e-5` (immutable `groundtruth.public.100K.ibin`), per [PROTOCOL_V3_P1_ADDENDUM.md](PROTOCOL_V3_P1_ADDENDUM.md)
- **External Evidence Root:** `../artifact-evidence/p1-full-validation-20261117T225717+0700`
  - Consolidated snapshot JSON: `checkpoint_20261118T0211.json`
  - Consolidated checkpoint CSV: `p1_checkpoint_matrix_20261118T0211.csv`
  - Idempotent resume runner: `run_test90k_on_parity.py`

---

## 1. Completed vs Remaining Scope

| Phase | Scope | Status | Verified Result |
|---|---|---|---|
| Phase 1 | Deterministic `val_10k` / `test_90k` split | **COMPLETE** | `10,000` (`a3c948e9aac4f40c1fb818a6f784c4fbb56473a0769affe3344493ed4eb87f57`) + `90,000` (`af871517d88aaad90549ba2fde0d4ed745f59400037a757f17bc93fa479bbfa3`), disjoint union `100,000` |
| Phase 2 | `task_da_p1_eval` + `dry_500` parity (`A0_R1`, `A3_R1`, `A3_R1_jobs6`, `A3_R2`) | **COMPLETE** | `8/8` configs `ON/OFF` parity **PASS** (`mismatches=0`, `incomplete_top_k=0`, `neg_acc=1`); `--jobs 6` bit-identical to `--jobs 1` |
| Phase 3 | `val_10k` calibration sweep & freeze + `val_10k` `ON/OFF` parity | **COMPLETE** | `18/18` cells selected & frozen in `frozen_calibration_manifest.json`; `18/18` `val_10k` `ON/OFF` parity (`10,000/10,000` queries each) **PASS** (`mismatches=0`, `incomplete_top_k=0`, `neg_acc=1`) |
| Phase 4 (OFF) | Held-out `test_90k` `OFF` at frozen beams (`9 graphs × 2 targets`) | **COMPLETE** | **`18/18` runs complete & audited** (`90,000/90,000` queries each, `incomplete_top_k=0`, `neg_acc=2`): **`t0990` = 9/9 PASS**, **`t0998` = 2/9 PASS / 7/9 FAIL** |
| Phase 4 (ON Parity) | Held-out `test_90k` `ON` & `ON/OFF` parity (`9 graphs × 2 targets`) | **PARTIAL (3/18)** | **PASS (3/18):** `A0_r1` (`beam=416`, `beam=896`), `A0_r2` (`beam=416`). Empty 0-byte `A0_r2/beam_896_ON.jsonl` removed cleanly. **PENDING (15/18):** `A0_r2 beam=896`, `A0_r3`, `A1_r1..r3`, `A3_r1..r3` |
| Phase 5 | Determinism repeat (`--jobs 1`), final SHA-256 audit, `EVIDENCE_CHECKSUMS.csv`, 6 final docs, test suite verification | **PENDING** | Run after remaining `15/18` `test_90k ON/OFF` parity finishes |

---

## 2. Verified Calibration (`val_10k`) & Held-Out (`test_90k OFF` + Completed `ON`) Matrix

> Note: Frozen calibration beams were locked strictly on `val_10k` before running `test_90k`. No retuning was performed after observing `test_90k` misses on `t0998`. All `test_90k` runs have `queries=90,000`, `total_slots=900,000`, `incomplete_top_k=0`, and `accepted_negative_gt_distances=2`.

| Arm-Rep | Target | Hist Task A Beam (100K Calib) | Frozen Beam (`prev_grid`: Recall) | `val_10k` Recall (`ON/OFF` Parity) | `val_10k` Mean DE / Exp | `test_90k OFF` Recall@10 (95% CI) | `test_90k` Floor Pass | `test_90k ON` Parity (Mean DE / Exp) |
|---|---|---|---|---|---|---|---|---|
| `A0_r1` | `t0990` | 384 (0.99106801) | **416** (`384`: 0.98996) | 0.991140 (**PASS**) | 18208.0 / 419.8 | **0.991206** (`[0.990976, 0.991435]`) | **PASS** | **PASS** (18196.1 / 419.8) |
| `A0_r1` | `t0998` | 896 (0.99817401) | **896** (`864`: 0.99790) | 0.998060 (**PASS**) | 36049.2 / 899.1 | **0.997950** (`[0.997847, 0.998053]`) | **FAIL** | **PASS** (36050.5 / 899.1) |
| `A0_r2` | `t0990` | 384 (0.99102002) | **416** (`384`: 0.98988) | 0.990970 (**PASS**) | 18209.1 / 419.8 | **0.991133** (`[0.990901, 0.991365]`) | **PASS** | **PASS** (18193.2 / 419.8) |
| `A0_r2` | `t0998` | 896 (0.99818301) | **896** (`864`: 0.99792) | 0.998050 (**PASS**) | 36042.0 / 899.1 | **0.997959** (`[0.997857, 0.998061]`) | **FAIL** | PENDING (`beam=896` only) |
| `A0_r3` | `t0990` | 384 (0.99103302) | **416** (`384`: 0.98990) | 0.991070 (**PASS**) | 18206.2 / 419.8 | **0.991196** (`[0.990965, 0.991426]`) | **PASS** | PENDING |
| `A0_r3` | `t0998` | 896 (0.99816400) | **896** (`864`: 0.99793) | 0.998090 (**PASS**) | 36037.1 / 899.1 | **0.997962** (`[0.997861, 0.998064]`) | **FAIL** | PENDING |
| `A1_r1` | `t0990` | 384 (0.99109501) | **416** (`384`: 0.98987) | 0.990990 (**PASS**) | 18212.4 / 419.9 | **0.991223** (`[0.990993, 0.991454]`) | **PASS** | PENDING |
| `A1_r1` | `t0998` | 896 (0.99816698) | **896** (`864`: 0.99784) | 0.998040 (**PASS**) | 36048.6 / 899.1 | **0.997957** (`[0.997855, 0.998058]`) | **FAIL** | PENDING |
| `A1_r2` | `t0990` | 384 (0.99101901) | **416** (`384`: 0.98985) | 0.991050 (**PASS**) | 18207.9 / 419.8 | **0.991138** (`[0.990908, 0.991367]`) | **PASS** | PENDING |
| `A1_r2` | `t0998` | 896 (0.99817097) | **928** (`896`: 0.99799) | 0.998200 (**PASS**) | 37167.2 / 931.1 | **0.998104** (`[0.998006, 0.998202]`) | **PASS** | PENDING |
| `A1_r3` | `t0990` | 384 (0.99102801) | **416** (`384`: 0.98981) | 0.990930 (**PASS**) | 18207.4 / 419.8 | **0.991146** (`[0.990914, 0.991377]`) | **PASS** | PENDING |
| `A1_r3` | `t0998` | 896 (0.99815500) | **896** (`864`: 0.99793) | 0.998100 (**PASS**) | 36040.3 / 899.1 | **0.997943** (`[0.997842, 0.998045]`) | **FAIL** | PENDING |
| `A3_r1` | `t0990` | 832 (0.99023801) | **896** (`864`: 0.98951) | 0.990190 (**PASS**) | 24005.5 / 899.7 | **0.990041** (`[0.989769, 0.990313]`) | **PASS** | PENDING |
| `A3_r1` | `t0998` | 2176 (0.99807101) | **2176** (`2112`: 0.99797) | 0.998090 (**PASS**) | 52028.5 / 2178.8 | **0.997879** (`[0.997775, 0.997982]`) | **FAIL** | PENDING |
| `A3_r2` | `t0990` | 832 (0.99028999) | **928** (`896`: 0.98979) | 0.990330 (**PASS**) | 24768.0 / 931.6 | **0.990730** (`[0.990469, 0.990991]`) | **PASS** | PENDING |
| `A3_r2` | `t0998` | 2176 (0.99805802) | **2304** (`2240`: 0.99796) | 0.998050 (**PASS**) | 54629.6 / 2306.8 | **0.998130** (`[0.998033, 0.998227]`) | **PASS** | PENDING |
| `A3_r3` | `t0990` | 832 (0.99033397) | **896** (`864`: 0.98945) | 0.990010 (**PASS**) | 24007.3 / 899.7 | **0.990129** (`[0.989859, 0.990399]`) | **PASS** | PENDING |
| `A3_r3` | `t0998` | 2176 (0.99806798) | **2112** (`2048`: 0.99780) | 0.998020 (**PASS**) | 50723.0 / 2114.9 | **0.997724** (`[0.997616, 0.997833]`) | **FAIL** | PENDING |

---

## 3. Verified Edge Cases & Structural Findings So Far

1. **`A3_r2` Unreachable Node `840923`:** On `val_10k` (`q=23741`) and `test_90k` (`q=47069, 66279, 89193`), node `840923` is structurally unreachable from entry `0` on `A3_r2` and never appears in returned top-10 IDs (`[False, False, False]` on `test_90k`), while `task_da::Index` still returns `10/10` valid nearest neighbors (`complete_top_k=True`, `incomplete_top_k=0`). Note: on `A3_r3` `beam=896`, `q=66279` also missed `840923` by search approximation before finding it at `beam=2112`.
2. **Negative Auxiliary GT Distances (`--gt-aux-min -1e-5`):**
   - `val_10k` (`q=48571`): `accepted_negative_gt_distances=1`, returned rank-0 exact base ID `938845` (`squared_l2=0.0`) across all 9 graphs.
   - `test_90k` (`q=45219, q=95033`): `accepted_negative_gt_distances=2`, returned rank-0 exact base IDs `467759` and `905634` across all 18 `OFF` runs (and completed `ON` runs).
3. **Why `task_da::Index` Diverges from Historical Task A Calibration:** Unlike Task A `filtered_beam_search` (`QP.cut=1.35`, offset batching `candidates.size() < beamSize/8`, lossy `hash_filter`, `float` L2), `task_da::Index` (`entry_best_first_v1`) uses exact `seen[]`, no prune cutoff, and `double` squared L2. At `t0998`, historical Task A also overflowed 32-bit `avg_cmps` (`~4.29e9`), whereas `task_da::Index` tracks 64-bit counters cleanly.
4. **Why `7/9` Frozen `t0998` Cells Missed `0.998` on `test_90k`:** Because `frozen_calibration_manifest.json` locked the smallest grid point clearing `0.998000` on `val_10k` with zero validation margin (`SE ≈ 0.00015` on `10K`), `val_10k` runs just above `0.998` (`0.99802–0.99810`) regressed slightly on the 9× larger `test_90k` (`0.997724–0.997962`), whereas the two runs pushed one grid step higher (`A1_r2 beam=928`, `A3_r2 beam=2304`) passed `0.998` on `test_90k` (`0.998104`, `0.998130`). Under P1 discipline (no `test_90k` retuning), this holds `P1 Quality Calibration` / `Full P1 Gate` until governed by a validation-margin or multi-fold rule.

---

## 4. Exact Command to Resume Tomorrow

Run from `/home/thinhbui/Documents/ChatGPT/Research ANN/task-d` (all completed `OFF` files and `A0_r1` / `A0_r2 beam=416` `ON` files are preserved automatically; `A0_r2` will run only `beam=896`, then `A0_r3`, `A1_r1..r3`, `A3_r1..r3` sequentially, ~55–60 min total):

```bash
python3 -u "/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/p1-full-validation-20261117T225717+0700/run_test90k_on_parity.py" \
  A0_r2 A0_r3 A1_r1 A1_r2 A1_r3 A3_r1 A3_r2 A3_r3
```

Then run Phase 5 checks (`--jobs 1` determinism repeat, immutable input/graph SHA-256 verification, `EVIDENCE_CHECKSUMS.csv`, the 6 final `task-da` report deliverables, and full CTest + ASan + `unittest`).
