# Task D × Task A — P1 V4 Execution Plan (Post-Approval Blueprint)

- **Status:** **`PLANNED_NOT_EXECUTED`** *(Requires owner sign-off on [P1_V4_APPROVAL_CHECKLIST.md](P1_V4_APPROVAL_CHECKLIST.md) and [PROTOCOL_V4_APPROVAL_READY.md](PROTOCOL_V4_APPROVAL_READY.md) prior to execution.)*
- **Preserved Read-Only V3 Campaign:** `../artifact-evidence/p1-full-validation-20261117T225717+0700` (must never be modified or overwritten).
- **Planned V4 External Evidence Root:** `../artifact-evidence/p1-v4-validation-<YYYYMMDDTHHMMSS+0700>` (clean isolated campaign directory).

---

## 1. Pre-Execution Invariants & Prerequisites

Before running any command in V4:
1. Verify SHA-256 immutability of `base.1M.fbin` (`44e83e1d...`), `query.public.100K.fbin` (`48d087a1...`), `groundtruth.public.100K.ibin` (`fa5acf5a...`), all `9` formal `index.graph` files, `val_10k.ids` (`a3c948e9...`), `test_90k.ids` (`af871517...`), and `task_da::Index` (`engine.hpp` `2ca38624...`).
2. Confirm owner sign-off on: (a) calibration criterion (`LCB95_q` vs `eff-Wilson`), (b) holdout track (`Track A` independent queries vs `Track B` post-hoc `test_90k`), and (c) P2 gate scope (`Option B` full V4 P1 gate vs `Option A` `t0990`-only scope addendum).
3. If **Track A** is selected: complete acquisition, SHA pinning, brute-force spotcheck & `--gt-aux-min` audit, and structural validation of the new external query/GT files *before* Phase A calibration begins.
4. Confirm `task_da_p1_eval` binary SHA (`59dde1cc4bcee8ac66c360db298a8b088ad2da8c1a1bb273d75deeb6a1e0836b`, or rebuilt cleanly with Release + ASan CTest passing if any tooling update was authorized — no algorithmic change to `engine.hpp`).
5. Capture `host_metadata.json` (`Zen2`, SMT, governor, memory, disk) and verify sequential execution (`only one task_da_p1_eval process active at a time`).

---

## 2. Step-by-Step Execution Sequence

### Phase A — Fresh `val_10k` V4 Calibration Sweep (Validation Only, No Holdout Access)
- **Inputs:** Immutable `val_10k.ids`, `task_da_p1_eval` (`pipnn`, `--entry 0 --k 10 --mode OFF --jobs 6`), `evaluate_p1.py --gt-aux-min -1e-5 --query-ids val_10k.ids`.
- **Candidate Starting Brackets (to ensure full predecessor check `prev_grid < threshold <= b*`, expanding upward step `32` (`<=1024`) / `64` (`>1024`) capped at `4096`):**
  - `A0 / A1` (`t0990`): sweep from `384` upward (e.g. `384, 416, 448` -> already expects `416` clears `LCB95 >= 0.990` with `384` failing).
  - `A0 / A1` (`t0998`): sweep from `896` upward (`896, 928, 960, 992, 1024, ...` until `LCB95 >= 0.998` or `> 4096`).
  - `A3` (`t0990`): sweep from `896` upward (`896, 928, 960, 992, 1024, ...` until `LCB95 >= 0.990` or `> 4096`).
  - `A3` (`t0998`): sweep from `2176` upward (`2176, 2240, 2304, 2368, 2432, 2496, ...` until `LCB95 >= 0.998` or `> 4096`).
- **Note:** All V4 sweep outputs are generated and hashed inside the **new** V4 campaign directory `calibration_10k/` so V4 is independently reproducible from raw artifacts. If any cell fails to pass by `4096`, trigger immediate **STOP / HOLD**.

### Phase B — `val_10k` ON/OFF Parity & Freeze
- For all `18` selected `(graph, b_V4*)` points:
  1. Run `task_da_p1_eval --mode ON --jobs 6` on `val_10k.ids`.
  2. Verify `evaluate_p1.py --parity-off` yields `mismatches == 0`, `exact_ids_match == true`, `exact_squared_l2_match == true`, `counter_invariants_pass == true`, `incomplete_top_k_queries == 0`.
  3. Write and SHA-lock `frozen_calibration_manifest_v4.json` **strictly before** running Phase C holdout evaluation.

### Phase C — Frozen Holdout Evaluation (`OFF` + `ON` + Parity)
- **Track A (`<new_holdout_ids>`)** OR **Track B (`test_90k.ids`, explicitly tagged `POST_HOC_EXPLORATORY`)**:
  1. Run `OFF` mode sequentially per graph for both frozen targets `[b*_90, b*_98]` (checkpoint-safe per-graph runner; verify `complete_top_k`, negative GT acceptance, exact holdout ID coverage).
  2. Run `ON` mode sequentially per graph and verify `evaluate_p1.py --parity-off` (`mismatches == 0` across all `18` holdout pairs).
  3. Record raw `Recall@10`, query-level `SE`, 95% CI, replicate mean/SD per arm (`n=3`), and `PASS/FAIL` per `(graph, target)` strictly without retuning.

### Phase D — Phase 5 Verification & V4 Reporting
1. Re-verify `determinism_check` (`--jobs 1` twice vs `--jobs 6`), all `17+` immutable asset SHA-256s, and edge cases (`A3_r2` `840923`, negative GT queries).
2. Generate `EVIDENCE_CHECKSUMS.csv` inside `p1-v4-validation-.../`.
3. Publish new V4 deliverables in `docs/research/task-da/` (`P1_V4_CALIBRATION_MATRIX.{csv,json}`, `P1_V4_VALIDATION_REPORT.md`, `P1_V4_GATE_DECISION.md`, updating `P2_READINESS_CHECKLIST.md`) with exact Track A/Track B provenance labels (`P0 = HOLD`, `V3 = preserved`, `P3 = CLOSED`).
4. Run full Release CTest, ASan+UBSan CTest, and `unittest discover -s tests/research -v`.

---

## 3. Realistic Compute & Storage Budget (Grounded in Observed V3 Timings)

Observed wall times on `thinhbui-linux` (`Ryzen 5 PRO 4650U`, sequential `--jobs 6`):
- **`val_10k` sweeps (`OFF`):** `~21s / beam` (`A0/A1`) and `~46s / beam` (`A3`) -> ~`35–45` total beams across `9` graphs + `18` `val_10k` `ON` parity runs ≈ **`30–40 minutes`** (`~1.2 GB` JSONL storage).
- **Holdout (`test_90k` under Track B, `90K` queries × `2` beams × (`OFF` + `ON`)):**
  - `6` `A0/A1` graphs: ~`6.5 min/graph/mode` × `6` × `2` modes ≈ `78 minutes` (excluding `A0/A1` `416` if already matched, or full fresh isolated run ~`78 min`).
  - `3` `A3` graphs: ~`10.5 min/graph/mode` × `3` × `2` modes ≈ `63 minutes`.
  - Total sequential wall time for clean isolated Track B V4 campaign: **`~2.5–3.0 hours`** (`~8–9 GB` external evidence out of `~165 GB` free disk).
- Track A duration depends proportionally on the chosen unseen holdout query count $N_{\text{new}}$.
