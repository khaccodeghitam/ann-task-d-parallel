# Task D × Task A — Protocol V4 Approval-Ready Addendum (`task_d_x_task_a`)

- **Document Status:** **`APPROVAL_READY_PENDING_OWNER_SIGNOFF`** *(Do **not** execute V4 runs or treat as approved until the research owner explicitly signs off in [P1_V4_APPROVAL_CHECKLIST.md](P1_V4_APPROVAL_CHECKLIST.md).)*
- **Date:** 2026-11-18
- **Supersedes / Extends Draft:** Consolidates [PROTOCOL_V4_ADDENDUM_DRAFT.md](PROTOCOL_V4_ADDENDUM_DRAFT.md) after statistical and operational finalization of P1.5 ([P1_5_QUALITY_FAILURE_ANALYSIS.md](P1_5_QUALITY_FAILURE_ANALYSIS.md), [P1_5_VAL_TEST_GAP_MATRIX.csv](P1_5_VAL_TEST_GAP_MATRIX.csv), [P1_5_CALIBRATION_OPTIONS.md](P1_5_CALIBRATION_OPTIONS.md), [P1_5_GATE_RECOMMENDATION.md](P1_5_GATE_RECOMMENDATION.md)).
- **Immutable Ancestor Documents Preserved Byte-Identical:**
  - [PRE_REGISTRATION.md](PRE_REGISTRATION.md) (v1)
  - [experiment_manifest.yaml](experiment_manifest.yaml) (v1)
  - [PROTOCOL_V2.md](PROTOCOL_V2.md)
  - [PROTOCOL_V3_P1_ADDENDUM.md](PROTOCOL_V3_P1_ADDENDUM.md)
  - [experiment_manifest_v3_reconciled.json](experiment_manifest_v3_reconciled.json)
  - Frozen V3 evidence directory `../artifact-evidence/p1-full-validation-20261117T225717+0700` (including `calibration_10k/frozen_calibration_manifest.json` and all V3 `test_90k` PASS/FAIL records) remains **strictly read-only and unmodified**.

---

## 1. Preserved Historical & V3 Baseline State

Protocol V4 does **not** overwrite, amend, or re-interpret prior campaign verdicts:

| Scope / Baseline | Preserved Verdict | Exact Empirical Basis |
|---|---|---|
| **Historical P0 Overall (Preregistration v1)** | **`HOLD`** | Runtime CLI seed absent in Task A receipts (`SEED=555` + `PARLAY_NUM_THREADS=4` non-determinism), unrecoverable historical `tai-linux` governor/thermal telemetry, and `thinhbui-linux` (`Zen2 AVX2`) != `tai-linux` (`AVX-512`). |
| **P1 Engine Correctness & Determinism (`workers=1`)** | **`PASS`** | `1,804,000 / 1,804,000` paired ON/OFF queries exact (`0` mismatches across `dry_500`, `val_10k`, `test_90k`), `0` incomplete top-10 queries, `--jobs 1` repeats == `--jobs 6` SHA-256 bit-identical, `17/17` immutable asset SHAs verified. |
| **V3 Calibration Quality (`t0990 = 0.990`)** | **`9 / 9 PASS`** | Frozen V3 `test_90k`: `A0` (`416`: `0.991133–0.991206`), `A1` (`416`: `0.991138–0.991223`), `A3` (`896, 928, 896`: `0.990041, 0.990730, 0.990129`). |
| **V3 Calibration Quality (`t0998 = 0.998`)** | **`2 / 9 PASS, 7 / 9 FAIL`** | PASS: `A1_r2@928=0.998104`, `A3_r2@2304=0.998130`. FAIL: `A0_r1..r3, A1_r1, A1_r3@896` (`0.997943–0.997962`), `A3_r1@2176` (`0.997879`), `A3_r3@2112` (`0.997724`). Full `100K` pool confirmed all 7 failing beams had population `Recall@10 (100K) < 0.998` (`0.997754–0.997975`). |
| **Full P1 Gate (under V3)** | **`HOLD`** | Correctness passed; quality generalization at `0.998` failed (`7/9`). |
| **P2 Multi-Walker & P3 Benchmark** | **`HOLD / CLOSED`** | Both remain closed pending owner decision under Protocol V4. |

---

## 2. Statistical Methodology & Validity Audit

### 2.1 Metric Definition and Intra-Query Clustering (`deff > 1`)
- Let query $i \in \{1,\dots,N_q\}$ contribute per-query Recall@10 $r_i = |\text{pred}_i \cap \text{GT}_{i,1:10}| / 10 \in \{0.0, 0.1, \dots, 1.0\}$, evaluated under Protocol v2 GT contract (`--gt-aux-min -1e-5`, ID-membership only, immutable `groundtruth.public.100K.ibin`).
- Sample mean and empirical query-level standard error (`evaluate_smoke.py:_evaluate_rows`, reused by `evaluate_p1.py`):
  $$\hat{R} = \frac{1}{N_q} \sum_{i=1}^{N_q} r_i, \qquad \widehat{\text{SE}}_q = \sqrt{\frac{\sum_{i=1}^{N_q} (r_i - \hat{R})^2}{N_q(N_q - 1)}}$$
- **Why Naive Slot-Binomial / Slot-Wilson Is Rejected:** Treating the `10` top-k slots of each query as independent Bernoulli trials ($N = 10 N_q = 100,000$) ignores intra-query correlation (`deff = (SE_q / SE_slot)^2`). Empirically measured on `val_10k`:
  - `t0990`: `deff = 1.41–1.45` (`A0/A1`, `SE_q ≈ 0.000356`) and `deff = 1.80–1.95` (`A3`, `SE_q ≈ 0.000428`). On `A3_r3@896`, naive `100K`-slot Wilson yields `0.989375` vs true query-level `0.989149` (underestimating uncertainty).
  - `t0998`: `deff = 1.14–1.20` (`SE_q ≈ 0.000143–0.000154`).

### 2.2 Adequacy of `LCB95 = mean - 1.96 × SE_q` (Checked Against Non-Parametric Bootstrap)
- Although `r_i` is left-skewed (`skew_q = -6.64 to -9.47` across `val_10k` operating points), at $N_q = 10,000$ ($|\text{skew}|/\sqrt{N_q} < 0.095$), 2,000-resample empirical query bootstrap confirms tight normal alignment:
  - Example saved `val_10k` points: `A0_r1@960` (`mean - 1.96*SE_q = 0.998038` vs `boot_p025 = 0.998040`); `A1_r1@960` (`0.998026` vs `0.998010`); `A3_r1@960` (`0.990209` vs `0.990200`); `A3_r1@2304` (`0.998003` vs `0.998000`); `A3_r1@2368` (`0.998112` vs `0.998110`). Maximum observed discrepancy across audited points is `<= 0.000059` (`A3_r3@896`).
- Furthermore, $\hat{R}_{\text{val}} - 1.96 \cdot \widehat{\text{SE}}_q$ is **exact to `recall_ci95_low`** already emitted by `research/task_da/evaluate_p1.py` (`evaluate_smoke.py`), eliminating discrepancy between tool output and protocol gate rule.
- *(Note on secondary conservative alternative)*: Wilson score on effective slot sample $N_{\text{eff}} = 10 N_q / \widehat{\text{deff}}$ (`eff-Wilson`) sits `~2.2–2.3e-5` lower than `mean - 1.96*SE_q` near `0.998` (e.g., `0.997980` vs `0.998003` on `A3_r1@2304`), so if the owner selects `LCB95_q` vs `eff-Wilson`, the exact choice must be locked in [P1_V4_APPROVAL_CHECKLIST.md](P1_V4_APPROVAL_CHECKLIST.md) prior to execution.

### 2.3 Cross-Graph Dependence & Sequential Selection Bias Disclosure (Mandatory Limitations)
1. **Sequential Multi-Beam Stopping Risk:** Sweeping multiple beams on `val_10k` and stopping at the first pass creates an optional-stopping effect across candidate points. Setting `z = 1.96` (one-sided $\alpha = 0.025$ vs V3's $\alpha = 0.50$) sharply shrinks premature crossings on flat `0.998` plateaus (`+0.00028` implied buffer vs `+0.00009..+0.00021` step gains), **but does not reduce family-wise error strictly to zero** across `18` decisions.
2. **Cross-Replicate Shared-Query Dependence:** Because all `9` graphs evaluate on identical queries (`Pearson r = 0.71–0.91` per query across `A0/A1`), replicate errors are correlated rather than independent. Consistent with [PRE_REGISTRATION.md](PRE_REGISTRATION.md), arm-level summaries must treat **graph replicate (`R1..R3`) as the outer unit** and never pool `3 × N_q` queries into a narrow combined CI.

---

## 3. Normative V4 Beam Calibration Specification

1. **Data Scope:** Validation split `split/val_10k.ids` ONLY ($N_q = 10,000$, SHA-256 `a3c948e9aac4f40c1fb818a6f784c4fbb56473a0769affe3344493ed4eb87f57`), engine `task_da::Index` (`entry_best_first_v1`, `workers=1`, `entry=0`, `k=10`). **Zero access to `test_90k` or any holdout metrics during beam selection.**
2. **Targets & Lattice Bounds:**
   - Quality floors: `target in {0.990, 0.998}`.
   - Grid lattice: step **`32`** for `beam <= 1024`; step **`64`** for `1024 < beam <= 4096`.
   - Hard upper bound: **`MAX_BEAM = 4096`** (non-negotiable).
3. **Selection Rule (Per Graph × Target):**
   - For each `(arm, rep, target)`, evaluate candidate beams along the valid lattice in increasing order and select the **smallest grid beam $b^* \le 4096$** meeting the owner-approved criterion (default recommended: `recall_ci95_low(val_10k, b*) >= target`, i.e., $\hat{R}_{\text{val}}(b^*) - 1.96\,\widehat{\text{SE}}_q(b^*) \ge \text{target}$), while verifying its immediate lower lattice neighbor $b_{\text{prev}}$ failed the same criterion (`< target`).
   - Run full `ON/OFF` parity (`evaluate_p1 --parity-off`) for all `18` selected `(graph, b*)` pairs on `val_10k` and freeze into a new `frozen_calibration_manifest_v4.json` **before any holdout run starts**.
4. **Failure / Infeasibility Rule (`No Passing Beam <= 4096`):**
   - If for any `(graph, target)` no lattice point $b \le 4096$ clears the V4 criterion on `val_10k`:
     - Record that cell as **`CALIBRATION_INFEASIBLE_AT_MAX_BEAM`**.
     - **Do NOT** raise `MAX_BEAM > 4096`, drop `target`, tweak `--gt-aux-min` beyond `-1e-5`, or borrow beams from `test_90k`.
     - **STOP** progression for Full P1 Gate and record **`HOLD`** (escalate to owner for topology/algorithm diagnosis).

---

## 4. Two Holdout Verification Tracks (Anti-Leakage Governance)

**Rule:** Never use `test_90k` (`af871517...`) to adjust beams, re-partition the existing `100K` query pool, or rescue failing replicates. One track below must be designated **before** running V4:

| Aspect | Track A — Independent Fresh Holdout *(Confirmatory)* | Track B — Existing `test_90k` Check *(Exploratory / Post-Hoc)* |
|---|---|---|
| **Query Source** | New external unseen query + exact GT dataset (never evaluated by Task A or Task D V3), with verified SHA-256 and exact brute-force / `--gt-aux-min` audit beforehand. | Existing `split/test_90k.ids` (`90,000` queries, SHA-256 `af871517...`), frozen and unchanged. |
| **Permitted Scientific Claim** | **Confirmatory out-of-sample generalization verification** of the V4 single-worker quality gate (still under disclosed `P0 = HOLD` graph build provenance). | Strictly classified **`EXPLORATORY / POST-HOC GATE VERIFICATION`**. Demonstrates only that applying a validation-variance rule *a priori* without per-graph `test_90k` tuning eliminates V3's premature crossing misses; **cannot be claimed as zero-leakage independent confirmation**. |
| **Pass / Fail Rule** | All `18/18` `(graph, target)` achieve `Recall@10 >= target`, `0` parity mismatches, `0` incomplete top-10. | All `18/18` `(graph, target)` achieve `Recall@10 >= target` on `test_90k`, `0` parity mismatches, `0` incomplete top-10. |
| **If Any Cell Misses** | Immediate **`HOLD`**; no third retune on the same holdout. | Immediate **`HOLD`**; no further tuning on `test_90k`. |

---

## 5. Gate Boundaries & Stopping Conditions

- **Strict Preservation:** `P0 = HOLD`, `V3 Quality = HOLD (t0990: 9/9 PASS; t0998: 2/9 PASS, 7/9 FAIL)`, and `P3 = CLOSED` remain unaltered regardless of V4 outcomes. Changing calibration criterion does **not** constitute an algorithmic quality improvement on fixed graphs.
- **Immediate Hard Stops During Any V4 Run:**
  1. Any dataset, graph, or frozen V3 manifest SHA-256 mismatch.
  2. Any single `ON/OFF` parity mismatch (`ids`, `squared_l2`, `complete_top_k`, or counter conservation invariant).
  3. Any `incomplete_top_k_queries > 0` or validator error (`--gt-aux-min -1e-5` boundary violation).
  4. Any calibration infeasibility (`> 4096`) or any holdout miss (`< target`).
- **Benchmark Prohibition:** No latency, QPS, or hardware-scaling claim is permitted under Protocol V4; `task_da_p1_eval --jobs N` remains purely a correctness throughput helper across independent queries.
