# Task D × Task A — P2 Multi-Walker Readiness Checklist

- **Current P2 Status:** **`HOLD / CLOSED`** (Blocked by [P1_FULL_GATE_DECISION.md](P1_FULL_GATE_DECISION.md))
- **Purpose:** Enumerate exact prerequisites required before writing or benchmarking any P2 multi-walker (`workers > 1`) common-engine code.

---

## Checklist

| # | Prerequisite | Current State | Evidence / Blocker |
|---|---|---|---|
| 1 | P0 Provenance & Historical Artifact Reconciliation | **RECONCILED WITH `HOLD` DISCLOSURE** | 12/12 graph/data SHAs, 261 raw receipts, 4/4 ELFs verified (`experiment_manifest_v3_reconciled.json`); historical runtime seed & R86 host telemetry remain unrecoverable (`P0 = HOLD`). |
| 2 | Deterministic Query Split & GT Opt-In Policy | **`PASS`** | Deterministic `val_10k` (`a3c948e9...`) / `test_90k` (`af871517...`); `--gt-aux-min -1e-5` verified against immutable GT without altering data. |
| 3 | Common Engine (`workers=1`) Correctness & ON/OFF Parity | **`PASS`** | `0 / 1,804,000` mismatches across `dry_500`, `val_10k`, `test_90k`; `0` incomplete top-k; deterministic `--jobs 1` == `--jobs 6`. |
| 4 | Edge-Case Handling (`A3-R2` unreachable `840923` & negative rank-0 GT) | **`PASS`** | Structurally sound (`A3_r2` loses only `840923` slots while completing `10/10` results; negative aux rank-0 matches return exact IDs). |
| 5 | Quality Calibration Floor Generalization on `test_90k` | **`HOLD / BLOCKING`** | `t0990` passes `9/9`, **`t0998` fails `7/9`** at frozen zero-margin `val_10k` beams (`A0/A1@896`, `A3_r1@2176`, `A3_r3@2112`). Must freeze an owner-approved Protocol V4 Addendum (e.g., validation LCB margin rule) and pass held-out calibration before P2. |
| 6 | P2 Multi-Walker Protocol & Shared-State Contract | **NOT WRITTEN (PENDING GATE)** | Must define `p`-worker synchronization/work-stealing or frontier sharing semantics, counter aggregation invariants (`ON/OFF`), determinism rule, and non-regression vs frozen `workers=1` beams prior to code. |
| 7 | P3 Performance Host Qualification (`benchmark` gate) | **`CLOSED` (`thinhbui-linux` NOT QUALIFIED)** | Current Ubuntu host (`Ryzen 5 PRO 4650U`, `Zen2 AVX2`) cannot produce direct QPS claims vs historical `tai-linux` (`AVX-512`); P2 initial campaign must be scoped to correctness / work-efficiency (`distance_evaluations`, `expansions`, `ON/OFF` parity) unless run on qualified hardware under P3 protocol. |
