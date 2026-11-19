# Task D × Task A — P1.5 Gate & P2 Scope Recommendation

- **Date:** 2026-11-18
- **Decision Status Today:** **`P2 REMAINS HOLD / CLOSED`** until the research owner explicitly signs off on Protocol V4 calibration & P2 scope rules below. **No P2 implementation or runs were started.**
- **Supporting Documents:** [P1_5_QUALITY_FAILURE_ANALYSIS.md](P1_5_QUALITY_FAILURE_ANALYSIS.md), [P1_5_VAL_TEST_GAP_MATRIX.csv](P1_5_VAL_TEST_GAP_MATRIX.csv), [P1_5_CALIBRATION_OPTIONS.md](P1_5_CALIBRATION_OPTIONS.md), [PROTOCOL_V4_ADDENDUM_DRAFT.md](PROTOCOL_V4_ADDENDUM_DRAFT.md), [P2_READINESS_CHECKLIST.md](P2_READINESS_CHECKLIST.md).

---

## 1. Comparison of P2 Scope Options

### Option A — Scope-Restricted P2 Only at `t0990` (`0.990`, Where V3 Passed `9/9`)
- **Precondition:** Requires an owner-approved scope addendum amending P1->P2 entry strictly to `t0990` **correctness & work-efficiency only** (`no P3 timing/QPS claims`), plus a written P2 shared-state/counter contract before coding.
- **Benefits:**
  - Unblocks early multi-walker (`workers = p > 1`) correctness testing, ON/OFF parity invariants, synchronization/frontier-merge auditing, and `I_D = D(G,p)/D(G,1) - 1` analysis at `0.990` without waiting for `t0998` re-calibration or an unseen dataset.
  - All `6/6` `A0/A1` graphs at `beam=416` already have strong `test_90k` margins (`0.991133–0.991223`, `+0.00113..+0.00122` above `0.990`).
- **Risks & Protocol Limits:**
  1. **Razor-thin `A3 t0990` baseline (`+4.1e-5` on `A3_r1@896`, `+1.29e-4` on `A3_r3@896`):** At `beam=896`, `A3_r1` scored `0.990041` on `test_90k` (`100K=0.990056`). Multi-walker `p > 1` traversal order can change frontier expansion slightly; even a tiny negative quality fluctuation could push `A3` under `0.990` at matched beam unless V4 `LCB95` calibration is applied to `A3 t0990` too (`896 -> ~960`).
  2. **Non-generalizability to `0.998`:** `t0990` operates at `beam=416` (`A0/A1`) / `896–928` (`A3`) with `already_seen / neighbor_attempts = 0.240–0.294`, whereas `t0998` operates at `~960` / `~2304–2432` with `0.302–0.368` seen ratio and heavier frontier contention; scaling/work-inflation conclusions at `0.990` **cannot** be generalized to `0.998`.
  3. **Permitted claims strictly bounded:** Can report multi-walker functional correctness, determinism invariants, and single-regime `t0990` work inflation (`I_D`); **cannot** claim Full P1 completion, `t0998` matching, P3 QPS speedup, or paper novelty (`P0 = HOLD`, `Zen2` host not qualified for `tai-linux` QPS).

### Option B — Hold All P2 Until Both `0.990` and `0.998` Satisfy Protocol V4 Full P1 Gate *(Recommended Default)*
- **Precondition:** Approve [PROTOCOL_V4_ADDENDUM_DRAFT.md](PROTOCOL_V4_ADDENDUM_DRAFT.md) (`Option 2b`: two-sided 95% query-level LCB `val_recall - 1.96 * SE_q >= target` across all `18` cells), decide holdout track (`Track A` unseen query set vs `Track B` post-hoc check on `test_90k`), and execute V4 P1 validation cleanly first.
- **Benefits:**
  - Fixes **both** the `7/9` `t0998` misses AND the borderline `A3_r1/r3` `t0990` margins in one uniform, non-tuned validation rule (`~960` on `A0/A1 t0998`, `~960` on `A3 t0990`, `~2304–2368` on `A3 t0998`, estimate grounded in observed `A0_r1, A1_r1, A3_r1` sweeps).
  - Establishes a single clean, immutable P1 baseline table across both floors (`0.990` and `0.998`) before any P2 code is written, avoiding split multi-version baselines and re-work.
  - Under Track B (existing `test_90k` exploratory verification), the remaining V4 validation runs (`val_10k` upper grid steps + `test_90k` ON/OFF) represent a bounded ~`2`-hour single-phase campaign; under Track A (unseen holdout), it establishes full zero-leakage confirmation before opening P2.
- **Risks & Protocol Limits:**
  - Adds one clean P1 validation step before opening P2 (~2h compute under Track B, or longer only if an external unseen query dataset must first be sourced/verified under Track A).
  - Under Track B, V4 `test_90k` verification must still be transparently labeled `exploratory / post-hoc gate verification` (never independent confirmation) while `P0 = HOLD` remains disclosed.

---

## 2. Recommendation & Owner Decisions Required Before Resuming Execution

**Recommendation:** **Keep P2 `HOLD / CLOSED` right now (`Option B`)** and resolve P1 cleanly via [PROTOCOL_V4_ADDENDUM_DRAFT.md](PROTOCOL_V4_ADDENDUM_DRAFT.md) (`Query-level LCB95 >= target`, accounting for clustering `deff = 1.14–1.95` and keeping `MAX_BEAM = 4096`) before opening P2. If the owner still elects Option A (`t0990`-only P2), we strongly recommend still applying the V4 `LCB95` bump to `A3 t0990` first so `A3_r1/r3` do not straddle `0.99004` during multi-walker testing.

### Decisions Requiring Explicit Owner Approval Before Next Step
1. **Approve Calibration Criterion for Protocol V4:** Adopt two-sided query-level `LCB95` ($\hat{R}_{\text{val}} - 1.96\,\widehat{\text{SE}}_q \ge \text{target}$) vs effective-$N$ Wilson vs fixed validation margin?
2. **Select Holdout Integrity Track (`Track A` vs `Track B`):** Will a new unseen independent query/GT holdout be supplied (`Track A` — true confirmatory gate), or should V4 validate frozen `val_10k` beams against existing `test_90k` strictly disclosed as `post-hoc / exploratory gate verification` (`Track B`)?
3. **Approve P2 Scope Option (`Option B` Full Gate vs `Option A` Restricted `t0990` Pilot):** Keep P2 closed until `t0990 + t0998` both pass V4 (`Option B`), or explicitly amend scope to `t0990`-only non-benchmark P2 engineering (`Option A`)?
4. **Target Scope of Next P2 Campaign:** Confirm P2 initially measures functional correctness, ON/OFF counter invariants, determinism, and work inflation $I_D$ (`no QPS/benchmarking claims` on `thinhbui-linux` while `P0 = HOLD`).
