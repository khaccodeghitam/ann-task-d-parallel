# Task D × Task A — P1.5 Statistical Calibration Review & Options Analysis

- **Date:** 2026-11-18
- **Scope:** Statistical evaluation of validation-only calibration rules using already-saved `val_10k` sweeps (`../artifact-evidence/p1-full-validation-20261117T225717+0700/calibration_10k/`) and [P1_5_VAL_TEST_GAP_MATRIX.csv](P1_5_VAL_TEST_GAP_MATRIX.csv). **No `test_90k` feedback was used to tune per-graph settings; no new searches were executed.**

---

## 1. Metric Uncertainty Structure: Queries vs Slots vs Graph Replicates

1. **Query-level vs Slot-level Binomial Variance (`Design Effect > 1`):**
   - In `research/task_da/evaluate_smoke.py` (`_evaluate_rows`, reused by `evaluate_p1.py`), each query $i \in \{1,\dots,N_q\}$ contributes $r_i = \text{hits}_i / 10 \in \{0.0, 0.1, \dots, 1.0\}$, yielding empirical query-level variance:
     $$\widehat{\text{SE}}_q = \sqrt{\frac{\sum_{i=1}^{N_q}(r_i - \hat{R})^2}{N_q(N_q - 1)}}$$
   - Naive slot-level binomial / slot-level Wilson (`n_slots = 10 * N_q = 100,000`) assumes all `10` slots within a query are independent Bernoulli trials. Empirical per-query hit histograms prove intra-query clustering (`deff = (SE_q / SE_slot)^2 > 1`):
     - At `t0990` on `A0/A1` (`beam=416`): `val_deff = 1.41–1.45` (`SE_q = 0.000352–0.000361` vs naive `0.000296–0.000300`).
     - At `t0990` on `A3` (`beam=896/928`): `val_deff = 1.80–1.95` (`SE_q = 0.000416–0.000439` vs naive `0.000310–0.000315`; ~`1.34×–1.40×` wider than slot-binomial).
     - At `t0998` across all arms: `val_deff = 1.14–1.20` (`SE_q = 0.000143–0.000154` vs naive `0.000134–0.000141`).
   - **Statistical Rule:** Never apply unadjusted slot-level Wilson intervals at `n = 100,000` slots; either use **query-level normal/t LCB** ($\hat{R} - z \cdot \widehat{\text{SE}}_q$) or **effective-sample Wilson LCB** using $N_{\text{eff}} = 10 N_q / \text{deff}$ (which closely agrees: on `A3_r3 @ 896`, query LCB95 is `0.989149` and `eff-Wilson` is `0.989112`, whereas naive `100K`-slot Wilson gives an artificially tight `0.989375`).
2. **Graph Replicate Correlation on Shared Queries:**
   - Because all `9` graphs share the identical `val_10k` and `test_90k` query sets, cross-graph outcomes are positively correlated (`Pearson r = 0.71–0.91` per-query on `test_90k` `A0/A1`). Therefore, cross-replicate standard errors must **not** treat `90,000` queries × `3` graphs as `270,000` independent queries. Consistent with [PRE_REGISTRATION.md](PRE_REGISTRATION.md), **graph replicate (`R1..R3`) is the outer unit** (`n = 3` replicates/arm), while query-level uncertainty accounts for within-graph finite query sampling.
3. **Sequential Grid Stopping Bias:**
   - Searching sequentially over candidate beams $b_1 < b_2 < \dots$ introduces an upward threshold-crossing selection bias (`winner's curse`) whenever step size yields $\Delta\text{Recall} \lesssim 2\cdot\widehat{\text{SE}}_q$ (`+0.00009..+0.00022` near `0.998` vs `2 * SE_q ≈ 0.00030`), even though grid evaluations share common random numbers (same queries).

---

## 2. Comparison of Four Candidate Calibration Strategies

| Option | Rule Definition (on `val_10k` alone) | Observed Behavior on Already-Saved `val_10k` Points (`no new runs`) | Validation Work / Beam Cost Shift | Strengths & Weaknesses |
|---|---|---|---|---|
| **1. Current Baseline** (V3 Addendum) | Smallest grid beam with `val_10k_recall >= target` | Picked `A0/A1: 416 / 896` (`A1_r2: 928`); `A3: 896,928,896 / 2176,2304,2112` | Baseline (`36.0k` DE at `A0/A1@896`, `50.7k–54.6k` DE at `A3@2112–2304`) | **Fails generalizability at `0.998` (`2/9` pass `test_90k`)** and leaves `A3 t0990` razor-thin (`+4.1e-5` on `A3_r1`). |
| **2a. One-sided 95% Query LCB** | Smallest grid beam with $\hat{R}_{\text{val}} - 1.645\,\widehat{\text{SE}}_q \ge \text{target}$ | At `t0998`: `A0_r1 -> 928` (`0.99824`, LCB `0.998007`); `A1_r1 -> 960` (`0.99830`); `A3_r1 -> 2304` (`0.99828`). Remaining cells stopped before clearing (`UNOBSERVED_ABOVE_928/2240/2304`). | `+1` to `+2` grid steps on `t0998` (`~+3.1%` DE per `+32b` on `A0/A1`; `~+2.5%` DE per `+64b` on `A3`) | Removes worst misses (`896`, `2112`, `2176`), yet `A0_r2, A0_r3, A1_r2, A1_r3 @ 928` only miss `1.645` LCB by `3e-6..68e-6` (`~0.99793–0.997997`); slight stopping-bias residual (`α=0.05` vs multiple grid checks). |
| **2b. Two-sided 95% Query LCB / Effective-N Wilson (`α=0.025` one-sided)** *(Recommended)* | Smallest grid beam with $\hat{R}_{\text{val}} - 1.96\,\widehat{\text{SE}}_q \ge \text{target}$ (or `eff-Wilson >= target`, `N_eff = 100k/deff`) | Requires `~target + 0.00028` at `t0998` (`SE_q ≈ 0.00014`) & `~target + 0.00083` at `t0990 A3`. Saved passes: `A0/A1 t0990 = 416` (all `6/6`); `A0_r1 t0998 = 960`; `A1_r1 t0998 = 960`; `A3_r1 t0990 = 960`; `A3_r1 t0998 = 2304`. Other `t0998` cells stopped prior to `LCB95 >= 0.998` (`>= 960` / `>= 2304–2368`). | `A0/A1 t0990`: `+0` beam (`416`); `A0/A1 t0998`: `+2` steps (`896->960`, `~+6.2%` DE); `A3 t0990`: `~+2` steps (`896->960`, `~+6.3%` DE); `A3 t0998`: `~+2..3` steps (`2112/2176->2304/2368`, `~+5–8%` DE) | **Principled, zero test-leakage:** derives solely from validation query variance & clustering (`deff`), rejects both borderline `896` (`t0998`) AND razor-thin `A3@896` (`t0990`), and buffers against sequential stopping bias without requiring external tuning constants. |
| **3. Fixed Pre-Registered Margin** (`target + δ`) | e.g., `δ = +0.0005` (`0.990`), `δ = +0.0002` or `+0.0003` (`0.998`) | At `δ_98=+0.0002`: picks `928` on `A0_r1..r3, A1_r2..r3` (`0.99820–0.99824`), `960` on `A1_r1`, `2240` on `A3_r1, A3_r3`. At `δ_98=+0.0003` (`>=0.99830`): closely mirrors Option `2b` (`960`, `2368`). | At `+2e-4`: `+1` step (`~+3.1%` DE). At `+3e-4`: `+2` steps (`~+6%` DE). | Simpler rule, **weakness:** if chosen right now *after* viewing `test_90k` gaps (`-0.00006..-0.00028`), fixed `δ` risks post-hoc overfitting critique unless explicitly tied to `k*SE_val` (`2.0 * SE_query`). |
| **4. Per-Graph × Target Calibration w/ Explicit Cap** | Apply Option `2b` per `(arm, rep, target)` with `step=32<=1024`, `step=64>1024`, hard `MAX_BEAM=4096` (or tighter cap if registered) | Keeps per-graph heterogeneity (`A3_r2 != A3_r1/r3`), guarantees bounded sweep well inside `MAX_BEAM=4096` (`~960` for `A0/A1`, `~2304–2432` for `A3`) | Well within compute budget (`~50%` headroom below `MAX_BEAM=4096`) | Preserves Protocol V1/V3 principle ("Vary search beam per graph/worker only during validation") rather than forcing one brittle beam across non-identical replicates (`A3`). |

---

## 3. Work Cost Estimate (Purely from Observed Validation / Saved Counter Rates)

Measured exact validation `ON` counter growth across observed frozen beams:
- **`A0/A1` near `0.998` (`A1_r1 @ 896` vs `A1_r2 @ 928`):** `+32` beam increases `val_10k` `mean_expansions` from `899.1` to `931.1` (`+32.0`) and `mean_de` from `36,048.6` to `37,167.2` (`+1,118.6 DE`, **`+3.10%` per step**; `+64` beam from `896 -> 960` projects `~+6.2%` DE).
- **`A3` near `0.990` (`A3_r1 @ 896` vs `A3_r2 @ 928`):** `+32` beam increases `mean_expansions` from `899.7` to `931.6` (`+31.9`) and `mean_de` from `24,005.5` to `24,768.0` (`+762.5 DE`, **`+3.18%` per `+32` step**).
- **`A3` near `0.998` (`A3_r3 @ 2112` -> `A3_r1 @ 2176` -> `A3_r2 @ 2304`):** `+192` beam (`+3` grid steps of `64`) increases `mean_de` from `50,723.0` to `54,629.6` (`+3,906.6 DE`, **`~+1,302 DE / +2.5%` per `+64` step**).
- Raising `A0/A1 t0998` (`896 -> 960`) and `A3 t0998` (`2112/2176 -> 2304–2432`) remains well under `MAX_BEAM = 4096` and preserves a clean `~2.4–2.5×` beam/expansion ratio (`~1.4–1.5×` `distance_evaluations` ratio) between `A3` (`~55k–57k DE`) and `A0/A1` (`~38k DE`) at `t0998` (vs `t0990`: `A0/A1@416` `~18.2k DE` and `A3@960` `~25.5k DE`).
