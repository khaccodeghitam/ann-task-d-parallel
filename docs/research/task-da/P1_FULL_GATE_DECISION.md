# Task D × Task A — Full P1 Gate Decision

- **Date:** 2026-11-18
- **Decision Authority Reference:** [PRE_REGISTRATION.md](PRE_REGISTRATION.md), [PROTOCOL_V2.md](PROTOCOL_V2.md), [PROTOCOL_V3_P1_ADDENDUM.md](PROTOCOL_V3_P1_ADDENDUM.md), [P0_P1_FINAL_RECONCILIATION_REPORT.md](P0_P1_FINAL_RECONCILIATION_REPORT.md)
- **Empirical Evidence:** [P1_FULL_VALIDATION_REPORT.md](P1_FULL_VALIDATION_REPORT.md), [P1_CALIBRATION_MATRIX.csv](P1_CALIBRATION_MATRIX.csv), [P1_ON_OFF_PARITY_REPORT.md](P1_ON_OFF_PARITY_REPORT.md)

---

## 1. Gate Status Matrix (Strict Separation of Scopes)

| Gate / Scope | Verdict | Rationale |
|---|---|---|
| **Historical P0 Overall (Preregistration v1)** | **`HOLD`** (Unchanged) | Runtime CLI seed absent in historical receipts (`SEED=555` + `PARLAY_NUM_THREADS=4` non-deterministic build variance), historical `tai-linux` governor/thermal logs unrecoverable, and `thinhbui-linux` (`Zen2 AVX2`) != `tai-linux` (`AVX-512`). |
| **P1 Engine Correctness & Determinism** | **`PASS`** | `18/18` `val_10k` + `18/18` `test_90k` + `8/8` `dry_500` runs complete with `0` incomplete top-10 queries, `0 / 1,804,000` ON/OFF parity mismatches, valid `uint64` counter invariants, exact determinism (`--jobs 1` repeat == `--jobs 6`), and `17/17` immutable asset SHA-256 verification. |
| **P1 Quality Calibration (Frozen Beams on `test_90k`)** | **`HOLD / PARTIAL_FAIL`** | **`t0990` passed `9/9`** (`0.990041–0.991223 >= 0.990`), whereas **`t0998` passed only `2/9`** (`A1_r2@928=0.998104`, `A3_r2@2304=0.998130`) and **failed `7/9`** (`A0_r1..r3`, `A1_r1`, `A1_r3` at `beam=896`: `0.997943–0.997962`; `A3_r1@2176`: `0.997879`; `A3_r3@2112`: `0.997724`). Strictly no post-hoc `test_90k` retuning was performed. |
| **Full P1 Gate** | **`HOLD`** | Requires BOTH P1 Correctness (`PASS`) AND Full P1 Quality Floor Generalization across all 18 cells (currently `11/18` pass on `test_90k`: `9/9` at `t0990`, `2/9` at `t0998`). |
| **P2 (Multi-Walker Common Engine)** | **`HOLD / CLOSED`** | Blocked by Full P1 Gate `HOLD`; no multi-walker implementation or runs authorized yet. |
| **P3 (Performance / QPS Benchmarking)** | **`HOLD / CLOSED`** | Blocked by P0 `HOLD`, Full P1 `HOLD`, P2 `CLOSED`, and hardware mismatch (`thinhbui-linux` NOT qualified vs `tai-linux`). |

---

## 2. Permitted Path to Resolve P1 Quality `HOLD` (Before Any P2 Work)

Per preregistration discipline, **never adjust beams by inspecting `test_90k` results**. Resolving the `t0998` generalization failure requires an explicit **Protocol V4 Addendum** approved by the research owner choosing one of the following blind/principled calibration rules before re-running calibration on `val_10k` alone (or a freshly separated internal validation fold):

1. **Option A — Statistical Validation Margin Rule (Recommended):**
   - Select the smallest grid beam whose **lower confidence bound** (e.g., Wilson / normal 95% lower bound or target `+ 2*SE`, where `SE ≈ 0.00015` on `n=10,000` implies a floor like `>= 0.9983` on `val_10k`) exceeds the formal floor `0.998` (and similarly `+margin` above `0.990` so borderline `A3_r1/r3` at `896` also hold safely).
2. **Option B — Resized Split (`val_30k` / `test_70k` via Deterministic Prefix):**
   - Because `10,000` queries allow only `~200` total top-10 slot misses at `0.998`, increasing the calibration split size (without using any prior `test_90k` outcomes to pick per-replicate exceptions) reduces selection variance (`SE ~ 1/sqrt(N)`). Note: since `test_90k` metrics have already been observed on `0..99999`, Option A (or gating P2 initially to `t0990`-validated single-worker baselines with Option A for `t0998`) is cleaner scientifically because threshold margin derives from validation sample binomial variance alone rather than peeking at `test_90k`.
3. **Option C — Algorithmic Parity Decision (Optional Separate Track):**
   - Keep `task_da::Index` (`entry_best_first_v1`) as the canonical Task D common engine (clean, exact `seen[]`, no `cut` heuristic), rather than mimicking `beamSearch.h` heuristics (`QP.cut=1.35`, `hash_filter`), because ON/OFF parity and exact determinism already `PASS` (`1,804,000` paired queries). Only change `entry_best_first_v1` if an explicit new common-engine protocol approves modifying the P1 baseline algorithm itself (which would invalidate P1 results and require full re-run).
