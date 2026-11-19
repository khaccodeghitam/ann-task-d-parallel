# Task D × Task A — P1.5 Quality Failure Root-Cause Analysis (`7/9` Fails at `Recall@10 >= 0.998`)

- **Date:** 2026-11-18
- **Status:** Methodological & Root-Cause Investigation (Zero New Experiments; Zero Modifications to Frozen Evidence)
- **Inputs Analyzed:** [PRE_REGISTRATION.md](PRE_REGISTRATION.md), [PROTOCOL_V2.md](PROTOCOL_V2.md), [PROTOCOL_V3_P1_ADDENDUM.md](PROTOCOL_V3_P1_ADDENDUM.md), [P1_FULL_VALIDATION_REPORT.md](P1_FULL_VALIDATION_REPORT.md), [P1_CALIBRATION_MATRIX.csv](P1_CALIBRATION_MATRIX.csv), [P1_FULL_GATE_DECISION.md](P1_FULL_GATE_DECISION.md), [P1_5_VAL_TEST_GAP_MATRIX.csv](P1_5_VAL_TEST_GAP_MATRIX.csv), and external raw files under `../artifact-evidence/p1-full-validation-20261117T225717+0700`.

---

## 1. Executive Conclusion

The `7/9` quality floor misses on held-out `test_90k` at `t0998` (`0.998`) are **not** caused by a common-engine correctness bug, instrumentation drift, dataset shift, or `A3_r2`'s unreachable node `840923`. Instead, direct audit of all `18` configurations across `val_10k` (`10,000` queries), `test_90k` (`90,000` queries), and their disjoint union (`100,000` full public queries) establishes **three compounding statistical & structural mechanisms**:

1. **Zero-margin threshold calibration on a finite `10K` sample under flattened beam sensitivity (`slope ≈ +0.00013..+0.00021` per grid step near `0.998`):**
   - At `t0998`, a single grid step (`+32` beam on `A0/A1`, `+64` on `A3`) improves Recall@10 by less than `1.4 × SE(val_10k)` (`SE_query ≈ 0.00015`). Selecting the earliest grid beam whose `val_10k` mean clears `0.998000` with `0` statistical margin produces **threshold-crossing upward selection bias ("winner's curse")**.
   - Pooling `val_10k + test_90k` (`1,000,000` top-10 slots) proves that for **all 5** failing `A0/A1 @ 896` configurations (`A0_r1..r3`, `A1_r1`, `A1_r3`), the full `100K` population Recall@10 is strictly **`0.997959–0.997975 < 0.998000`**, and for `A3_r1 @ 2176` / `A3_r3 @ 2112` is **`0.997900` / `0.997754 < 0.998000`**. Thus `beam=896` (`A0/A1`) and `2176/2112` (`A3_r1/r3`) never truly cleared `0.998` on the 100K query pool; `val_10k` happened to cross `0.99800` slightly early by `+0.3σ..+0.9σ` (`+4e-5..+1e-4`), then regressed toward the true sub-`0.998` mean on `test_90k`.
2. **Strong positive cross-replicate dependence on the shared query split (`Pearson r = 0.71–0.91`):**
   - Because all graphs run on the exact same `val_10k` and `test_90k` MS-Turing-1M queries, per-query hit counts are strongly correlated across replicates (`A0_r1 vs A0_r2: r=0.7140`; `A0_r2 vs A0_r3: r=0.8967`; `A1_r1 vs A1_r3: r=0.9068` at `beam=896`). When `beam=896` crossed `0.998` on `val_10k` for one `A0/A1` graph, `5/6` crossed together (`0.99804–0.99810`) and then **all 5** failed together on `test_90k` (`0.997943–0.997962`), whereas `A1_r2` barely missed `0.998` at `896` (`0.99799`), stepped to `928`, and passed `test_90k` (`0.998104`).
3. **Why `t0990` passed `9/9` cleanly on `A0/A1` while `A3 t0990` remained tight:**
   - Around `0.990`, `A0/A1` beam sensitivity is `~7×` steeper (`+0.00109..+0.00120` per `+32` step), so stepping from `384` (`~0.9899`) to `416` (`~0.9911`) automatically builds a `+3 × SE_val` safety buffer (`~+0.00105`), giving `6/6` `test_90k` passes (`0.991133–0.991223`). On `A3`, the `0.990` slope is half as steep (`+0.00054..+0.00068 / +32b`) and per-query clustering is higher (`deff = 1.80–1.95`), leaving `A3_r1@896` (`0.990041`) and `A3_r3@896` (`0.990129`) only `+4.1e-5` and `+1.29e-4` above `0.990`.

---

## 2. Full 18-Configuration Gap & Floor-Distance Audit

Full machine-readable table in [P1_5_VAL_TEST_GAP_MATRIX.csv](P1_5_VAL_TEST_GAP_MATRIX.csv). Every `Z`-score below uses query-level standard errors `Z = (test - val) / sqrt(SE_val^2 + SE_test^2)`.

| Graph | Target | Beam (`prev`) | `val_10k` (Margin) | `test_90k` (Margin) | Full `100K` Recall | `test - val` (`Z`) | `SE_val` (`deff`) | Slope / Step | `test_90k` |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `A0_r1` | `t0990` | 416 (384) | 0.99114 (`+1.14e-3`) | 0.991206 (`+1.21e-3`) | 0.991199 | `+6.6e-5` (`+0.18`) | 0.000352 (`1.41`) | `+0.00118 / 32b` | **PASS** |
| `A0_r2` | `t0990` | 416 (384) | 0.99097 (`+9.70e-4`) | 0.991133 (`+1.13e-3`) | 0.991117 | `+1.6e-4` (`+0.43`) | 0.000360 (`1.45`) | `+0.00109 / 32b` | **PASS** |
| `A0_r3` | `t0990` | 416 (384) | 0.99107 (`+1.07e-3`) | 0.991196 (`+1.20e-3`) | 0.991183 | `+1.3e-4` (`+0.33`) | 0.000358 (`1.45`) | `+0.00117 / 32b` | **PASS** |
| `A1_r1` | `t0990` | 416 (384) | 0.99099 (`+9.90e-4`) | 0.991223 (`+1.22e-3`) | 0.991200 | `+2.3e-4` (`+0.62`) | 0.000357 (`1.43`) | `+0.00112 / 32b` | **PASS** |
| `A1_r2` | `t0990` | 416 (384) | 0.99105 (`+1.05e-3`) | 0.991138 (`+1.14e-3`) | 0.991129 | `+8.8e-5` (`+0.23`) | 0.000356 (`1.43`) | `+0.00120 / 32b` | **PASS** |
| `A1_r3` | `t0990` | 416 (384) | 0.99093 (`+9.30e-4`) | 0.991146 (`+1.15e-3`) | 0.991124 | `+2.2e-4` (`+0.57`) | 0.000361 (`1.45`) | `+0.00112 / 32b` | **PASS** |
| `A3_r1` | `t0990` | 896 (864) | 0.99019 (`+1.90e-4`) | 0.990041 (`+4.10e-5`) | 0.990056 | `-1.5e-4` (`-0.33`) | 0.000428 (`1.88`) | `+0.00068 / 32b` | **PASS** |
| `A3_r2` | `t0990` | 928 (896) | 0.99033 (`+3.30e-4`) | 0.990730 (`+7.30e-4`) | 0.990690 | `+4.0e-4` (`+0.92`) | 0.000416 (`1.80`) | `+0.00054 / 32b` | **PASS** |
| `A3_r3` | `t0990` | 896 (864) | 0.99001 (`+1.00e-5`) | 0.990129 (`+1.29e-4`) | 0.990117 | `+1.2e-4` (`+0.26`) | 0.000439 (`1.95`) | `+0.00056 / 32b` | **PASS** |
| **`A0_r1`** | `t0998` | 896 (864) | 0.99806 (`+6.0e-5`) | **0.997950 (`-5.0e-5`)** | **0.997961** | `-1.1e-4` (`-0.69`) | 0.000150 (`1.16`) | `+0.00016 / 32b` | **FAIL** |
| **`A0_r2`** | `t0998` | 896 (864) | 0.99805 (`+5.0e-5`) | **0.997959 (`-4.1e-5`)** | **0.997968** | `-9.1e-5` (`-0.58`) | 0.000149 (`1.15`) | `+0.00013 / 32b` | **FAIL** |
| **`A0_r3`** | `t0998` | 896 (864) | 0.99809 (`+9.0e-5`) | **0.997962 (`-3.8e-5`)** | **0.997975** | `-1.3e-4` (`-0.81`) | 0.000149 (`1.17`) | `+0.00016 / 32b` | **FAIL** |
| **`A1_r1`** | `t0998` | 896 (864) | 0.99804 (`+4.0e-5`) | **0.997957 (`-4.3e-5`)** | **0.997965** | `-8.3e-5` (`-0.52`) | 0.000152 (`1.19`) | `+0.00020 / 32b` | **FAIL** |
| `A1_r2` | `t0998` | **928** (896) | 0.99820 (`+2.0e-4`) | **0.998104 (`+1.04e-4`)** | **0.998114** | `-9.6e-5` (`-0.63`) | 0.000143 (`1.14`) | `+0.00021 / 32b` | **PASS** |
| **`A1_r3`** | `t0998` | 896 (864) | 0.99810 (`+1.0e-4`) | **0.997943 (`-5.7e-5`)** | **0.997959** | `-1.6e-4` (`-1.00`) | 0.000148 (`1.16`) | `+0.00017 / 32b` | **FAIL** |
| **`A3_r1`** | `t0998` | 2176 (2112) | 0.99809 (`+9.0e-5`) | **0.997879 (`-1.21e-4`)** | **0.997900** | `-2.1e-4` (`-1.33`) | 0.000149 (`1.17`) | `+0.00012 / 64b` | **FAIL** |
| `A3_r2` | `t0998` | **2304** (2240) | 0.99805 (`+5.0e-5`) | **0.998130 (`+1.30e-4`)** | **0.998122** | `+8.0e-5` (`+0.51`) | 0.000149 (`1.15`) | `+0.00009 / 64b` | **PASS** |
| **`A3_r3`** | `t0998` | 2112 (2048) | 0.99802 (`+2.0e-5`) | **0.997724 (`-2.76e-4`)** | **0.997754** | `-3.0e-4` (`-1.81`) | 0.000154 (`1.20`) | `+0.00022 / 64b` | **FAIL** |

---

## 3. Hypotheses Explicitly Evaluated and Separated

### Confirmed Primary Cause
1. **Unprotected Threshold-Crossing Selection Bias Near a Flat Recall Curve (`t0998`):**
   - On all `7` failed `t0998` runs, `val_margin_vs_floor` was only `+0.00002` to `+0.00010` (`+0.13 SE` to `+0.67 SE`), smaller than a single grid increment (`0.00009–0.00022`) and much smaller than `1.96 × SE_val ≈ 0.00029`.
   - Meanwhile, on the exact same frozen configurations, `test - val` `Z`-scores lie cleanly inside `[-1.81, +0.92]` across all `18` cells — fully consistent with normal sampling fluctuation (`|Z| <= 1.96`), concentrated in the negative direction at `t0998` (`8/9` negative `test - val`) specifically because stopping on the *first* validation crossing conditions on `val_10k >= 0.99800`.
2. **A0/A1 Uniformity vs A3 Replicate Structural Variance (`PARLAY_NUM_THREADS=4`):**
   - Across `A0_r1..r3` at `beam=896`, `test_90k` recalls are virtually identical (`0.997950, 0.997959, 0.997962`; cross-replicate `SD = 0.000006`); at `beam=416`, `A0` and `A1` also cluster within `0.000090` (`0.991133–0.991223`, `SD = 0.000040–0.000047`). Note also `A0` and `A1` have nearly identical total graph edge counts (`52.85M–52.88M`) and identical work counters (`mean_de ≈ 36,038–36,050` at `beam=896`).
   - By contrast, `A3` (`~38.35M` edges) exhibits genuine graph-replicate structural variance (`test_90k` `t0998` `SD = 0.000205`; `t0990` `SD = 0.000375`): at `val_10k beam=2176`, `A3_r1=0.99809`, `A3_r2=0.99783`, `A3_r3=0.99816` (`range = 0.00033`). Because `A3_r3` happened to cross slightly early at `2112` (`val=0.99802`), it fell `-0.000276` below `0.998` on `test_90k`; because `A3_r2` ran lower on `val_10k` at `2112..2240` (`0.99770, 0.99783, 0.99796`), it stepped to `2304` and passed (`0.998130`).

### Explicitly Ruled Out as Primary Causes
1. **Engine / ON-OFF / Counter Bugs (`RULED OUT`):** Parity is **PASS** on `1,804,000 / 1,804,000` paired queries (`0` mismatches); `incomplete_top_k = 0`; `--jobs 1` repeats and `--jobs 6` are byte-identical (`SHA-256`). Parity proves deterministic faithful implementation of `entry_best_first_v1`, which is orthogonal to whether a selected `beam` meets a quality floor.
2. **Systematic `val_10k` vs `test_90k` Workload Drift (`RULED OUT`):** On `A0/A1 beam=416`, `val_10k` actually scored **lower** than `test_90k` on `6/6` graphs (`val = 0.99093–0.99114` vs `test = 0.991133–0.991223`), and mean work counters (`DE`, `expansions`) differ by `< 0.2%` between splits.
3. **`A3_r2` Unreachable Node `840923` (`RULED OUT`):** `A3_r2` lost `1 / 100,000` (`q=23741`) on `val_10k` and `3 / 900,000` (`3.3e-6`) on `test_90k`, yet `A3_r2` **passed** both `0.990` and `0.998`, whereas `A3_r1` and `A3_r3` (where `840923` is reachable) failed `0.998`. (Even at `beam=2176`, `A3_r2`'s `val_10k` gap vs `A3_r1/r3` was `26–33` misses, far larger than the `1` missing `840923` slot.)

### What Remains Unproven Without Further Evidence
- Exact `test_90k` Recall at `beam=928` or `960` for `A0_r1..r3`, `A1_r1`, `A1_r3`, or at `beam=2240..2432` for `A3_r1..r3`, because those configurations have not been executed on `test_90k` (and `A0_r2, A0_r3, A1_r2, A1_r3, A3_r2` sweeps on `val_10k` stopped upon first floor pass).
- Confirmatory performance on an **independent external query distribution**: all `100,000` MS-Turing-1M public queries were already inspected by historical Task A and now by Task D P1 (`val_10k` and `test_90k`).
