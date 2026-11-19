# Task D × Task A — Full P1 Correctness Validation & Calibration Report

- **Date:** 2026-11-18  
- **Study / Scope:** `task_d_x_task_a` — **Full P1 Single-Worker Common-Engine Validation (`workers=1`, `entry=0`, `k=10`)** across all 9 formal historical R86 graphs (`A0, A1, A3 × R1–R3`) on MS-Turing-1M (`1,000,000` vectors, `dim=100`, squared L2). No P2 multi-walker code or P3 timing/QPS benchmarks were executed.  
- **Protocol Anchor:** [PROTOCOL_V3_P1_ADDENDUM.md](PROTOCOL_V3_P1_ADDENDUM.md) (preserving [PRE_REGISTRATION.md](PRE_REGISTRATION.md) v1, [experiment_manifest.yaml](experiment_manifest.yaml) v1, [PROTOCOL_V2.md](PROTOCOL_V2.md), and [experiment_manifest_v3_reconciled.json](experiment_manifest_v3_reconciled.json) unchanged).  
- **Machine-Readable Outputs:** [P1_CALIBRATION_MATRIX.csv](P1_CALIBRATION_MATRIX.csv), [P1_CALIBRATION_MATRIX.json](P1_CALIBRATION_MATRIX.json), [P1_ON_OFF_PARITY_REPORT.md](P1_ON_OFF_PARITY_REPORT.md), [P1_FULL_GATE_DECISION.md](P1_FULL_GATE_DECISION.md), [P2_READINESS_CHECKLIST.md](P2_READINESS_CHECKLIST.md).  
- **External Raw Evidence Root:** `../artifact-evidence/p1-full-validation-20261117T225717+0700` (`261` hashed files listed in `EVIDENCE_CHECKSUMS.csv`).

---

## 1. Executive Verdict

1. **Common-Engine Correctness & Determinism (`PASS`):**
   - `task_da::Index` (`entry_best_first_v1`, `build-task-da/task_da_p1_eval`, `sha256: 59dde1cc4bcee8ac66c360db298a8b088ad2da8c1a1bb273d75deeb6a1e0836b`) executed cleanly across `18 × 10,000` validation sweeps (`val_10k`) and `18 × 90,000` held-out test sweeps (`test_90k`), plus `8 × 500` pre-flight `dry_500` runs (`3,608,000` query evaluations across `ON` and `OFF`).
   - **Zero incomplete top-10 queries (`0 / 3,608,000`)**, **zero invalid/duplicate IDs or NaN/Inf**, **`0 / 1,804,000` ON/OFF parity mismatches** (`exact_ids_match`, `exact_squared_l2_match`, `counter_invariants_pass`), and **100% byte-identical repeatability** across `--jobs 1` repeats and `--jobs 6` (`determinism_check/`).
2. **Quality Calibration Generalization (`HOLD / PARTIAL_FAIL`):**
   - Using strictly frozen `val_10k` minimum-grid beams (`frozen_calibration_manifest.json`) with **no test-set retuning**:
     - **`t0990` (target `>= 0.990`): `9 / 9` PASS** (`0.990041` to `0.991223`).
     - **`t0998` (target `>= 0.998`): `2 / 9` PASS (`A1_r2 @ 928 = 0.998104`, `A3_r2 @ 2304 = 0.998130`), `7 / 9` FAIL** (`A0_r1..r3`, `A1_r1`, `A1_r3` at `beam=896`: `0.997943–0.997962`; `A3_r1 @ 2176`: `0.997879`; `A3_r3 @ 2112`: `0.997724`).
   - Full Gate Decision in [P1_FULL_GATE_DECISION.md](P1_FULL_GATE_DECISION.md) is **HOLD**: do not advance to P2 multi-walker implementation until `t0998` calibration generalization is resolved under a governed protocol addendum (without peeking at `test_90k`). Historical **P0 overall** also remains **HOLD**.

---

## 2. Phase-by-Phase Execution & Evidence Summary

### Phase 1 — Deterministic Query Split & GT Integrity
- Sorted `0..99999` by `SHA256(UTF-8 "task-da-v1:20261115:<decimal-id>")` ascending:
  - `split/val_10k.ids`: `10,000` queries, `sha256: a3c948e9aac4f40c1fb818a6f784c4fbb56473a0769affe3344493ed4eb87f57` (contains GT negative `q=48571` and `A3-R2` unreachable-node query `q=23741`).
  - `split/test_90k.ids`: `90,000` queries, `sha256: af871517d88aaad90549ba2fde0d4ed745f59400037a757f17bc93fa479bbfa3` (contains GT negatives `q=45219, 95033` and `A3-R2` unreachable-node queries `q=47069, 66279, 89193`).
- Audited `groundtruth.public.100K.ibin` (`fa5acf5ab262b42355296e99f920e6aa863f48820ca6f70fa37ca7966634c344`) across all `100,000` rows: `disjoint=true`, `union=100,000`, `0` stored `float32` ties at rank 9 vs rank 10 (`split_manifest.json`). Note: `query.public.100K.fbin` was previously used by Task A, so `val_10k`/`test_90k` is an internal common-engine split rather than an unseen external dataset.

### Phase 2 — Engine Implementation & Validator Integration
- Left `research/task_da/search_common/engine.hpp` (`sha256: 2ca38624d2549534274743c144f901e8825bcbd607f53b87e91d1548173127bd`) and `smoke.cpp` (`ff4ce1ea83d6acfac5df1297fc692a367cdb16d69954aa483d2f4b7deb471049`) untouched.
- Added additive CLI `research/task_da/search_common/p1_eval.cpp` (`task_da_p1_eval`) and evaluator `research/task_da/evaluate_p1.py` sharing `_evaluate_rows` with `evaluate_smoke.py`. Default `--gt-aux-min 0.0` still rejects `q=48571` (`rc != 0`), while opt-in `--gt-aux-min -1e-5` accepts exact rank-0 matches on `q=48571` (`val_10k`, `accepted=1`) and `q=45219, 95033` (`test_90k`, `accepted=2`) without modifying `groundtruth.public.100K.ibin`.

### Phase 3 — `val_10k` Calibration & Freezing (`18/18` PASS)
- Selected minimum grid beam (`step=32 <= 1024`, `step=64 > 1024`, `MAX_BEAM=4096`) clearing `target` on `val_10k`, verifying every direct predecessor `prev_grid_beam` fell strictly below `target` (`calibration_10k/frozen_calibration_manifest.json`).
- Notice divergence vs Historical Task A calibrated beams (`384/896` on `A0/A1`; `832/2176` on `A3`): common engine stepped up to `416` on all `6/6` `A0/A1 t0990` cells (`384` scored `0.98981–0.98996` on `val_10k`), stepped up to `928` on `A1_r2 t0998`, `896/928/896` on `A3 t0990`, and `2176/2304/2112` on `A3 t0998`.

### Phase 4 — Frozen Held-Out `test_90k` Matrix (`18/18` Executed, `0` Retuning)

| Arm-Rep | Graph SHA-256 (prefix) | Target | Hist A Beam (100K Recall) | Frozen P1 Beam (`prev`: Val) | `val_10k` Recall | `test_90k` Hits / 900K | `test_90k` Recall@10 (95% CI) | Floor Pass | ON/OFF Parity |
|---|---|---|---:|---|---:|---:|---|---|---|
| `A0_r1` | `55df31ac9b77` | `t0990` | 384 (0.991068) | **416** (`384`: 0.98996) | 0.991140 | 892,085 | **0.991206** (`[0.990976, 0.991435]`) | **PASS** | PASS |
| `A0_r1` | `55df31ac9b77` | `t0998` | 896 (0.998174) | **896** (`864`: 0.99790) | 0.998060 | 898,155 | **0.997950** (`[0.997847, 0.998053]`) | **FAIL** | PASS |
| `A0_r2` | `e0e0be004e6b` | `t0990` | 384 (0.991020) | **416** (`384`: 0.98988) | 0.990970 | 892,020 | **0.991133** (`[0.990901, 0.991365]`) | **PASS** | PASS |
| `A0_r2` | `e0e0be004e6b` | `t0998` | 896 (0.998183) | **896** (`864`: 0.99792) | 0.998050 | 898,163 | **0.997959** (`[0.997857, 0.998061]`) | **FAIL** | PASS |
| `A0_r3` | `a4ad500421b9` | `t0990` | 384 (0.991033) | **416** (`384`: 0.98990) | 0.991070 | 892,076 | **0.991196** (`[0.990965, 0.991426]`) | **PASS** | PASS |
| `A0_r3` | `a4ad500421b9` | `t0998` | 896 (0.998164) | **896** (`864`: 0.99793) | 0.998090 | 898,166 | **0.997962** (`[0.997861, 0.998064]`) | **FAIL** | PASS |
| `A1_r1` | `7da34f1c3e0f` | `t0990` | 384 (0.991095) | **416** (`384`: 0.98987) | 0.990990 | 892,101 | **0.991223** (`[0.990993, 0.991454]`) | **PASS** | PASS |
| `A1_r1` | `7da34f1c3e0f` | `t0998` | 896 (0.998167) | **896** (`864`: 0.99784) | 0.998040 | 898,161 | **0.997957** (`[0.997855, 0.998058]`) | **FAIL** | PASS |
| `A1_r2` | `b08ef703f162` | `t0990` | 384 (0.991019) | **416** (`384`: 0.98985) | 0.991050 | 892,024 | **0.991138** (`[0.990908, 0.991367]`) | **PASS** | PASS |
| `A1_r2` | `b08ef703f162` | `t0998` | 896 (0.998171) | **928** (`896`: 0.99799) | 0.998200 | 898,294 | **0.998104** (`[0.998006, 0.998202]`) | **PASS** | PASS |
| `A1_r3` | `1b51bf711545` | `t0990` | 384 (0.991028) | **416** (`384`: 0.98981) | 0.990930 | 892,031 | **0.991146** (`[0.990914, 0.991377]`) | **PASS** | PASS |
| `A1_r3` | `1b51bf711545` | `t0998` | 896 (0.998155) | **896** (`864`: 0.99793) | 0.998100 | 898,149 | **0.997943** (`[0.997842, 0.998045]`) | **FAIL** | PASS |
| `A3_r1` | `0fff20ec4750` | `t0990` | 832 (0.990238) | **896** (`864`: 0.98951) | 0.990190 | 891,037 | **0.990041** (`[0.989769, 0.990313]`) | **PASS** | PASS |
| `A3_r1` | `0fff20ec4750` | `t0998` | 2176 (0.998071) | **2176** (`2112`: 0.99797) | 0.998090 | 898,091 | **0.997879** (`[0.997775, 0.997982]`) | **FAIL** | PASS |
| `A3_r2` | `3d6113e721fa` | `t0990` | 832 (0.990290) | **928** (`896`: 0.98979) | 0.990330 | 891,657 | **0.990730** (`[0.990469, 0.990991]`) | **PASS** | PASS |
| `A3_r2` | `3d6113e721fa` | `t0998` | 2176 (0.998058) | **2304** (`2240`: 0.99796) | 0.998050 | 898,317 | **0.998130** (`[0.998033, 0.998227]`) | **PASS** | PASS |
| `A3_r3` | `11f7a5059af3` | `t0990` | 832 (0.990334) | **896** (`864`: 0.98945) | 0.990010 | 891,116 | **0.990129** (`[0.989859, 0.990399]`) | **PASS** | PASS |
| `A3_r3` | `11f7a5059af3` | `t0998` | 2176 (0.998068) | **2112** (`2048`: 0.99780) | 0.998020 | 897,952 | **0.997724** (`[0.997616, 0.997833]`) | **FAIL** | PASS |

---

## 3. Root-Cause Analyses & Edge-Case Audits

1. **Why `entry_best_first_v1` Differs From Historical Task A (`beamSearch.h`):**
   - Historical Task A stops early via `QP.cut = 1.35`, batches offset candidates `< beamSize/8`, deduplicates with lossy `hash_filter`, and accumulates `float` squared L2. By contrast, `task_da::Index` uses exact `seen[]`, no prune cutoff (`expansions ≈ beam + 3`, higher than Task A's `avg_visited` `370`/`740`/`712`/`1449`), and `double` squared L2.
   - At `t0998`, Task A logs also overflowed 32-bit `avg_cmps` (`4294955360..4294959699`), whereas `task_da::Index` maintains exact 64-bit counters cleanly (`P1_ON_OFF_PARITY_REPORT.md`).
2. **Why `7/9` Frozen `t0998` Cells Missed `0.998` on `test_90k`:**
   - At `t0998`, the minimum-beam-on-`val_10k` rule (`zero` safety margin above `0.998000` on `10,000` queries, binomial `SE ≈ 0.00015`) suffered winner's-curse / finite-sample threshold variance: all five `A0/A1` cells locked at `beam=896` (`val_10k = 0.99804–0.99810`) settled between `0.997943–0.997962` on `test_90k`, and `A3_r1@2176` / `A3_r3@2112` settled at `0.997879` / `0.997724`. By contrast, both cells that landed one grid step higher on `val_10k` (`A1_r2@928 -> 0.998104`, `A3_r2@2304 -> 0.998130`) cleared `0.998` with comfortable CI95 lower bounds (`> 0.99800`). Even at `t0990`, `A3_r1/r3` at `896` landed very close to `0.990` (`0.990041`, `0.990129`).
3. **`A3_r2` Unreachable Node `840923`:**
   - Confirmed on `val_10k` (`q=23741`) and `test_90k` (`q=47069, 66279, 89193`): node `840923` never appears (`has_840923=false`) while `task_da::Index` returns `complete_top_k=true`, `hits_at_10=9/10` on all three `test_90k` queries at both `928` and `2304` (losing `3 / 900,000` slots, i.e., `~3.3e-6` recall, proving reachability defect did NOT cause the `t0998` generalization misses — in fact `A3_r2` passed `0.998`!).
4. **Negative Auxiliary GT Distances (`3 / 100,000` rank-0 entries):**
   - All 18 `val_10k` runs accepted `q=48571` (`neg_acc=1`, returned rank-0 exact `938845`, `10/10` hits). All 18 `test_90k` OFF and ON runs accepted `q=45219` (`rank-0=467759`, `10/10` hits) and `q=95033` (`rank-0=905634`, `10/10` hits) with `neg_acc=2`.
5. **Phase 5 Immutability Audit (`17 / 17` Exact Match After Final Run):**
   - Verified post-sweep SHA-256 of `base.1M.fbin`, `query.public.100K.fbin`, `groundtruth.public.100K.ibin`, all 9 formal `index.graph` files, `smoke.cpp`, `engine.hpp`, `PRE_REGISTRATION.md`, `experiment_manifest.yaml`, and `TASK_A_R86_CHECKSUMS.sha256` against baseline pins — zero mutation.
   - `EVIDENCE_CHECKSUMS.csv` hashes all `261` external files under `p1-full-validation-20261117T225717+0700`.
