# Task D × Task A — PROTOCOL V4 ADDENDUM DRAFT (Validation LCB Calibration & Leakage Disclosure)

- **Status:** **`DRAFT_FOR_OWNER_APPROVAL`** (Not yet active; no V4 runs have been executed)
- **Immutable Ancestors Preserved Unchanged:**
  - [PRE_REGISTRATION.md](PRE_REGISTRATION.md) (v1)
  - [experiment_manifest.yaml](experiment_manifest.yaml) (v1)
  - [PROTOCOL_V2.md](PROTOCOL_V2.md)
  - [PROTOCOL_V3_P1_ADDENDUM.md](PROTOCOL_V3_P1_ADDENDUM.md)
  - External frozen V3 evidence (`../artifact-evidence/p1-full-validation-20261117T225717+0700/calibration_10k/frozen_calibration_manifest.json` and all `18/18` V3 `test_90k` PASS/FAIL records including the `7/9` `t0998` misses) remain **strictly preserved and unedited**.

---

## 1. Problem Requiring Protocol Revision

Under [PROTOCOL_V3_P1_ADDENDUM.md](PROTOCOL_V3_P1_ADDENDUM.md), beam selection chose the minimum grid beam on `val_10k` (`n = 10,000`) satisfying point estimate `val_10k_recall >= target` (`0.990` or `0.998`) with zero statistical uncertainty margin. On `test_90k` (`n = 90,000`):
- **`t0990` (`0.990`):** Passed `9/9`, though `A3_r1@896` (`0.990041`) and `A3_r3@896` (`0.990129`) stayed within `+4.1e-5..+1.29e-4` of the floor (`100K`: `0.990056`, `0.990117`).
- **`t0998` (`0.998`):** Failed **`7/9`** (`A0_r1..r3`, `A1_r1`, `A1_r3` at `beam=896`: `0.997943–0.997962`; `A3_r1@2176 = 0.997879`; `A3_r3@2112 = 0.997724`), because beam-response slopes flatten to `0.00009–0.00022` per step (`< 1.4 × SE_val`), causing threshold-crossing selection bias ("winner's curse") and correlated cross-graph misses (`Pearson r = 0.71–0.91`).

---

## 2. Historical Results Explicitly Retained

- **Historical P0 Overall:** Remains **`HOLD`** (missing historical runtime seed, unrecoverable `tai-linux` thermal/governor telemetry, Zen2 vs AVX-512 host mismatch).
- **V3 P1 Engine Correctness & Parity:** Remains **`PASS`** (`0 / 1,804,000` ON/OFF mismatches, `0` incomplete top-10, exact determinism, immutable `17/17` SHA matches).
- **V3 Quality Gate (`frozen_calibration_manifest.json`):** Permanently recorded as **`HOLD / PARTIAL_FAIL (t0990: 9/9 PASS; t0998: 2/9 PASS, 7/9 FAIL)`** and must never be overwritten, hidden, or renamed to claim retroactive V3 PASS. Changing calibration rules does **not** alter the quality capability of a fixed graph/beam; it only defines a statistically safer operating point.

---

## 3. Revised Validation Calibration Rule (Per Graph × Target)

For each `(graph, target)` among `A0, A1, A3 × R1–R3 × {0.990, 0.998}`, evaluate strictly on `val_10k` (`split/val_10k.ids`, SHA-256 `a3c948e9aac4f40c1fb818a6f784c4fbb56473a0769affe3344493ed4eb87f57`):

1. **Metric & Per-Query Uncertainty Estimator (Accounting for Intra-Query Clustering):**
   - Compute per-query recall $r_i = |\text{pred}_i \cap \text{GT}_{i,1:10}| / 10$ across $N_q = 10,000$ validation queries using opt-in GT validator `--gt-aux-min -1e-5` (default `0.0` preserved).
   - Compute query-level sample mean $\hat{R}_{\text{val}}$ and query-level empirical standard error:
     $$\widehat{\text{SE}}_q = \sqrt{\frac{\sum_{i=1}^{N_q} (r_i - \hat{R}_{\text{val}})^2}{N_q (N_q - 1)}}$$
   - **Prohibition on narrow slot-level CI:** Do **not** apply unadjusted binomial/Wilson intervals assuming $10 \times N_q = 100,000$ independent slots, which empirically underestimates variance by `deff = 1.14–1.95` across targets.
2. **Primary Confidence Selection Criterion (`Query-Level Two-Sided 95% LCB >= target`, equivalently `97.5%` one-sided confidence):**
   $$\text{LCB}_{95,q}(b) = \hat{R}_{\text{val}}(b) - 1.96 \cdot \widehat{\text{SE}}_q(b) \ge \text{target}$$
   *(Alternatively, effective-sample Wilson LCB using $N_{\text{eff}} = 10 N_q / \widehat{\text{deff}}$ yields nearly identical selection boundaries within `< 3e-5` while staying bounded in `[0, 1]`.)*
   - Choose the **minimum grid beam $b^*$** satisfying $\text{LCB}_{95,q}(b^*) \ge \text{target}$ and verify its immediate lower lattice neighbor $b_{\text{prev}}$ failed $\text{LCB}_{95,q}(b_{\text{prev}}) < \text{target}$.
   - **No Per-Graph Ad-Hoc Margin Tuning:** The `1.96 * SE_q` buffer derives completely from validation-sample dispersion rather than any constant back-fitted from `test_90k` errors. If an additional fixed floor margin is ever added later, it must be fixed *a priori* globally before seeing the target dataset.
3. **Search Lattice & Bounds:**
   - Lattice step: `32` for `beam <= 1024`, `64` for `1024 < beam <= 4096`.
   - Hard cap: `MAX_BEAM = 4096` (non-negotiable stopping boundary; do not raise dynamically if a replicate exceeds `4096`).
   - Run full `ON/OFF` parity (`evaluate_p1 --parity-off`) on every newly frozen `(graph, target, b_V4*)` on `val_10k` and store in a **new** V4 campaign directory (`p1-v4-calibration-...`) without touching V3 evidence.

---

## 4. Query Split, Leakage Prevention, and Confirmation Classification

1. **Strict Prohibition on Using `test_90k` to Retune Beams:**
   - `test_90k` (`af871517d88aaad90549ba2fde0d4ed745f59400037a757f17bc93fa479bbfa3`) must **never** be inspected inside calibration selection, stopping conditions, or margin adjustments, nor re-split/shuffled after seeing `7/9` V3 misses to manufacture an "unseen" fold from the same `100K` pool.
2. **Two Mutually Exclusive Evaluation Tracks (Must Pick One Before Running):**
   - **Track A — True Independent Confirmation (`RECOMMENDED FOR CONFIRMATORY CLAIM`):**
     - Acquire or designate a **genuinely new independent query + exact GT holdout** (never used by historical Task A or by Task D V3 `val_10k`/`test_90k`), verify SHA-256 and GT sanity/exactness before search, and evaluate frozen V4 beams `b_V4*` once.
   - **Track B — Exploratory / Post-Hoc Verification on Existing `test_90k` (`IF NO NEW QUERIES EXIST`):**
     - If no independent unseen dataset is available, evaluating the new `val_10k`-frozen `b_V4*` on existing `test_90k` MUST be explicitly labeled **`EXPLORATORY / POST-HOC GATE VERIFICATION`** in all reports and papers, because `test_90k` outcomes at neighboring beams were already observed during V3. It cannot be reported as zero-leakage independent confirmation.

---

## 5. PASS / HOLD Gate Criteria & Stopping Rules

| Criterion | PASS Condition | HOLD / STOP Condition |
|---|---|---|
| Beam Calibration Bound | All `18/18` `(graph, target)` clear `LCB95_q >= target` at `b_V4* <= 4096` | Any cell fails to reach `LCB95_q >= target` by `beam = 4096` -> **STOP & HOLD** |
| Engine Parity & Integrity | `0` incomplete top-k, `0` ID/distance/counter invariant errors, `0` ON/OFF parity mismatches | Any single parity mismatch, counter violation, or incomplete top-k -> **IMMEDIATE STOP & HOLD** |
| Holdout Quality Verification | Under Track A: `18/18` cells clear `test >= target` on unseen holdout. Under Track B: `18/18` clear `test_90k >= target` (classified `POST_HOC_EXPLORATORY`). *(Note: `3`-graph arm evaluation also reports replicate mean/SD without pooling dependent query slots.)* | Any single `(graph, target)` scores `< target` (`0.990` or `0.998`) on holdout -> **HOLD (do not retune again on holdout!)** |
| P3 / P0 Boundaries | Explicit preservation: `P0 = HOLD` and `P3 = CLOSED` remain untouched unless separately resolved by qualified benchmark host + provenance. | Any timing/QPS/speedup claim from V4 validation runs violates protocol and auto-holds gate. |
