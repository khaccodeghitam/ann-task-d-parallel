# Task D × Task A Protocol v2 (GT Contract, Topology Boundary, and Smoke Safeguards)

**Effective date:** 2026-11-17  
**Supersedes for operational execution:** `PRE_REGISTRATION.md` (v1) and `experiment_manifest.yaml` (v1) remain **preserved unchanged** for historical preregistration integrity.  
**Resolved manifest:** [experiment_manifest_v2_resolved.json](experiment_manifest_v2_resolved.json)

---

## 1. Ground-Truth Contract (`groundtruth.public.100K.ibin`)

- **Immutable artifact:** `data/MSTuring_1M_v1/groundtruth.public.100K.ibin` (`80,000,008` bytes, SHA-256 `fa5acf5ab262b42355296e99f920e6aa863f48820ca6f70fa37ca7966634c344`) MUST remain byte-identical. Never clamp, shift, normalize, or reserialize GT.
- **Full-file scan & root-cause verification:**
  - Across all `100,000 × 100` entries (`10,000,000` IDs and distances), there are `0` out-of-range IDs, `0` duplicate IDs within a row, `0` NaN/Inf values, `0` non-monotonic pairs, `0` stored ties at `k=10`, and exactly `3` negative rank-0 auxiliary distances:
    - `q=45219, base=467759`: stored `-3.5762786865234375e-07`, exact float64 squared L2 `9.642754869869548e-14` (`max |q_i - b_i| = 8.94e-8`).
    - `q=48571, base=938845`: stored `-2.384185791015625e-07`, exact float64 squared L2 `0.0` (vectors bitwise identical).
    - `q=95033, base=905634`: stored `-2.384185791015625e-07`, exact float64 squared L2 `0.0` (vectors bitwise identical).
  - All MS-Turing-1M vectors are unit-normalized (`||x||^2 ≈ 1.0`), so float32 GEMM distance expansion `||q||^2 + ||b||^2 - 2(q·b)` produces `2–3` float32 ULPs of negative cancellation noise near zero.
  - Exact brute-force verification against `base.1M.fbin` (`44e83e1d...`) and `query.public.100K.fbin` (`48d087a1...`) confirms `35/35` exact top-10 ID/order and top-100 ID-set parity on queries `0..31` and `[45219, 48571, 95033]` (plus previously verified `50000`, `99999`), with max stored-vs-exact squared-L2 deviation `6.846e-07`. Full 100,000-row brute-force certification remains `NOT_CERTIFIED_FULL_100K_EXACT`.
- **Task A evaluator parity (`check_nn_recall.h`):**
  - Historical Task A C++ evaluator (`r86_v1_2_source/algorithms/utils/check_nn_recall.h` lines 86–112) comments out `GT.distances(...)` and never reads the stored auxiliary distance column.
- **Protocol v2 Recall & Validator Rules (`research/task_da/evaluate_smoke.py`):**
  1. `Recall@k` is defined strictly by **ground-truth ID membership (`truth[:k]`)**: `len(set(ids) & set(truth[:k])) / (k * len(rows))`.
  2. `evaluate_smoke.py` keeps default `--gt-aux-min 0.0` strictly fail-closed.
  3. For MS-Turing-1M `fa5acf5a...` validation under Protocol v2, callers explicitly pass `--gt-aux-min -1e-5` (hard-bounded to `[-1e-4, 0.0]`). Under this opt-in mode, the validator still rejects any `NaN`/`Inf`, any GT ID out of `[0, base_count)`, duplicate GT IDs, non-monotonic auxiliary distances, any auxiliary distance `< gt_aux_min`, and any negative engine `squared_l2` result distance; and explicitly reports `accepted_negative_gt_distances` and `accepted_negative_gt_queries`.

## 2. Historical Graph Topology Preservation

- All 9 formal graphs (`A0, A1, A3 × R1–R3`) match manifest SHA-256s and pass read-only structural format checks.
- **A3–R2 confound (`3d6113e7...`):** Node `840923` has `outdegree=29`, `incoming=0`, is unreachable from entry `0`, and appears in GT top-10 for queries `[23741, 47069, 66279, 89193]` (13 times in top-100). This is verified genuine historical build output linked to `A3/r2/build_result.json` and 12 search logs. Never add edges, relabel IDs, or alter entry `0`; report this reachability limit explicitly in all A3–R2 analyses.

## 3. P1 Bounded Common-Engine Correctness Smoke Contract

- Purpose: verify `task_da_smoke` (`research/task_da/search_common/smoke.cpp` + `engine.hpp`) end-to-end on real MS-Turing-1M inputs and `A0–R1` / `A3–R1` with `workers=1`, `entry=0`, `k=10`, `query_limit=32`, and identical `beam` across `ON` and `OFF` instrumentation modes.
- Required invariants:
  - Identical `ids` and `squared_l2` between `ON` and `OFF` on each graph.
  - Finite non-negative `squared_l2`, monotonic `(distance, id)`, non-null counters for `ON`, `null` counters for `OFF`.
  - No latency, QPS, or speedup measurement/claim; 32-query smoke Recall does **not** prove `0.990`/`0.998` campaign Recall floors.

## 4. P0 / P2 / P3 Gate Requirements Remaining

- **P0 remains HOLD** until:
  1. Missing historical Task A artifacts (`campaign_manifest.json`, 2 builder ELFs, 2 search ELFs, compile/link `flags.make`/`link.txt`/manifests, build-time `source_commit`/`source_diff_sha256`/dependency revisions, historical host receipt, acquisition manifest) are recovered from `/home/tai/ann-task-a` — **or** the owner explicitly authorizes a **separate** new build campaign with new `run_id`s.
  2. Current benchmark host (`thinhbui-linux` or another target machine) receives a qualified host profile (governor, SMT/CPU affinity, memory residency, thermal/frequency guard) approved by the Task D host owner.
- **P2 (multi-walker implementation) and P3 (benchmarking) remain CLOSED** until P0 and P1 are explicitly recorded `PASS`.
