# Task D × Task A — P0/P1 v2 Evidence Verification, GT Policy & Bounded Smoke Report

**Date:** 2026-11-17  
**Branch:** `research/task-d-a-p0-p1-20261115` (uncommitted new files; `main` untouched; PR #57 closed/unmerged)  
**Machine-readable companions:** [P0_P1_V2_SUMMARY.json](P0_P1_V2_SUMMARY.json), [P0_P1_V2_SUMMARY.csv](P0_P1_V2_SUMMARY.csv), [experiment_manifest_v2_resolved.json](experiment_manifest_v2_resolved.json), [PROTOCOL_V2.md](PROTOCOL_V2.md)  
**Preserved v1 baseline files (unchanged):** [experiment_manifest.yaml](experiment_manifest.yaml), [PRE_REGISTRATION.md](PRE_REGISTRATION.md)  
**External evidence roots:**
- Recovery archive audit: `artifact-evidence/p0-p1-recovery-20261117T161322+0700`
- V2 verification & P1 smoke logs: `artifact-evidence/p0-p1-v2-smoke-20261117T170810+0700`

---

## 1. Evidence Validation (PASS on Checksums & Cross-Links; Open Historical Provenance Gaps)

- **Checksum recomputation:** `279 / 279` entries in `p0-p1-recovery-20261117T161322+0700/EVIDENCE_CHECKSUMS.csv` recomputed on disk with `0` failures.
- **Data & Graph assets (`12 / 12`):** `base.1M.fbin` (`44e83e1d...`), `query.public.100K.fbin` (`48d087a1...`), `groundtruth.public.100K.ibin` (`fa5acf5a...`), and all 9 OFF formal `index.graph` files (`A0, A1, A3 × r1..r3`) recomputed on disk and verified identical across v1 manifest, `TaskD_R86_MST1M_Handoff_v1/sha256sums.txt`, and `/home/thinhbui/Documents/ChatGPT/graph`.
- **261 raw receipts/logs (`27` BUILD + `234` SEARCH):** Every `build_command.json`, `build_result.json`, `native.build.log`, `calibrated_t0990.json`, `calibrated_t0998.json`, `calib_*`, and `measure_*_s{1..5}` across all 9 graphs cross-verifies against its corresponding `index.graph` SHA-256, `base.1M.fbin` SHA-256, `build_log_sha256`, `log_sha256`, and runner `r86_mst1m_fasttrack_formal_v1.py` (`3f6cde145120298411c0be94fd4d983b52aa7eabe1fe77dc410dd255f6ec797e`).
- **Resolved manifest v2 preflight:** `python3 -m research.task_da.preflight docs/research/task-da/experiment_manifest_v2_resolved.json --artifact-root ...` exited `1` (`HOLD`, `12/12` `AVAILABLE`, `28` remaining blockers: `9 × 3` for `build_source_commit` / `build_source_diff_sha256` / `seed`, plus host/provenance review; `raw_receipt_path` resolved on all 9 graphs).
- **Cryptographically verified checksums vs reported-only metadata:**
  - **Verified on disk:** 12 dataset/graph files, 261 raw receipt/log files, runner script `r86_mst1m_fasttrack_formal_v1.py` (`3f6cde14...`), common-engine binary `build-task-da/task_da_smoke` (`0d462c09...`).
  - **Reported-only pins (local ELF or build-time tree missing):** builder `stock_off` (`aa2d174e...`), builder `h17_off` (`5f673586...`), search `v3` (`ea6c757b...`), search `v4` (`bb6576ad...`).
  - **Unverified / not recorded:** `campaign_manifest.json`, `build_source_commit`, `build_source_diff_sha256`, compiler `flags.make`/`link.txt`/dependency commits at build time, `seed` (`NOT_RECORDED`), `historical_host_receipt`, and current host qualification.

---

## 2. GT Protocol v2 & Validator Tests (`evaluate_smoke.py`)

- **Empirical root cause of the 3 negative auxiliary distances (`fa5acf5a...`):**
  - Full 100,000-row scan confirms `0` non-finite values, `0` non-monotonic rows, `0` ties at `k=10` in stored distances, and `3` rank-0 negative entries: `q=45219/b=467759` (`-3.5762786865234375e-07`, exact float64 sq-L2 `9.642754869869548e-14`), `q=48571/b=938845` (`-2.384185791015625e-07`, exact `0.0`), and `q=95033/b=905634` (`-2.384185791015625e-07`, exact `0.0`).
  - All 3 pairs involve unit-norm vectors (`||q||^2 ≈ 1.0`), producing 2–3 float32 ULPs of negative cancellation noise from `||q||^2 + ||b||^2 - 2(q·b)`.
  - Brute-force exact float64 verification on 35 queries (`0..31` and `45219, 48571, 95033`) confirms `35/35` exact top-10 ID/order match and `35/35` exact top-100 ID-set match (max stored distance deviation `6.846e-07`). Full 100K exactness remains `NOT_CERTIFIED_FULL_100K_EXACT`.
- **Task A evaluator reconciliation:** `check_nn_recall.h` comments out `GT.distances(...)` (lines 96, 98) and never reads the auxiliary distance column.
- **Validator implementation (`research/task_da/evaluate_smoke.py`, SHA-256 `c73830a5...`):**
  - Preserves strict default `--gt-aux-min 0.0` (CLI and API fail closed on negative GT distances).
  - Adds opt-in `--gt-aux-min -1e-5` (bounded to `[-1e-4, 0.0]`), computing ID-only `Recall@k` on `truth[:k]` while still rejecting `NaN`/`Inf`, non-monotonicity, invalid/duplicate IDs, GT values `< gt_aux_min`, and any negative engine `squared_l2` result, and explicitly reporting `accepted_negative_gt_distances` and `accepted_negative_gt_queries`.
  - **Real GT negative-row probe (`q=45219, 48571, 95033` against `groundtruth.public.100K.ibin`):** default `--gt-aux-min 0.0` exited `2` (`invalid GT distances`); `--gt-aux-min -1e-5` exited `0` with `accepted_negative_gt_distances=3`, `accepted_negative_gt_queries=3`.
- **Verification after final edit:**
  - `ctest --test-dir build-task-da --output-on-failure`: **PASS** (`1/1` CTest target, `19/19` unittest cases including 7 native subprocess cases).
  - `ASAN_OPTIONS=detect_leaks=0 ctest --test-dir build-task-da-asan --output-on-failure`: **PASS** (`1/1` CTest target).
  - Full `tests/research` suite (`PYTHONPATH=.deps-research TASK_DA_SMOKE=./build-task-da/task_da_smoke`): **510 / 510 PASS** (`0` failures, `0` skipped).

---

## 3. P1 Bounded Common-Engine Smoke (`A0–R1` & `A3–R1`, `p=1`, 32 Queries)

Executed sequentially using `build-task-da/task_da_smoke` (`0d462c097f815af75de05f427c89b6a78a3ca35f6b925322bea1e67f1d6c17ed`), `entry=0`, `k=10`, `query_ids=[0..31]`, format `pipnn`, matching `base` (`44e83e1d...`), `queries` (`48d087a1...`), and `ground_truth` (`fa5acf5a...`). **No latency, QPS, or speedup measured or claimed.**

| Graph (`run_id`) | Graph SHA-256 | Beam | Mode | ON/OFF IDs & `squared_l2` Match | Complete Top-10 | `Recall@10` (`0..31`) | Max `squared_l2` Diff vs f64 | Output JSONL SHA-256 |
|---|---|---:|---|---|---|---|---:|---|
| `R86_MST1M_A0_OFF_FORMAL_R1` | `55df31ac...72522` | 384 | ON | Exact (`true`) | 32/32 | `0.987500` | `7.77e-16` | `584e4f0f5dd78395699a4f081df4fe51ab353b34926c10f3ad7e56d487b13e10` |
| `R86_MST1M_A0_OFF_FORMAL_R1` | `55df31ac...72522` | 384 | OFF | Exact (`true`) | 32/32 | `0.987500` | `7.77e-16` | `b4caa153b1c33c3a36a5b2ba56af4cb965ba8bbb9f356030ff8256139f0b2bb6` |
| `R86_MST1M_A3_OFF_FORMAL_R1` | `0fff20ec...5fbb2` | 832 | ON | Exact (`true`) | 32/32 | `0.968750` | `7.77e-16` | `9235cd8439228c7832431ce9d3255e98626667994574a04731605b43ba601dfa` |
| `R86_MST1M_A3_OFF_FORMAL_R1` | `0fff20ec...5fbb2` | 832 | OFF | Exact (`true`) | 32/32 | `0.968750` | `7.77e-16` | `f9a40d45fb7a77d388c63122396dad6f7d26f5cb6c4303691442adc4d99369fc` |

- **Representative sample (`q=0`, identical across ON/OFF):**
  - `A0-R1` (`beam=384`): `ids=[84139, 98069, 733955, 126930, 241689, 639103, 530233, 54250, 248827, 738038]`, `d0=0.48739319736953196`, ON counters `distance_evaluations=11876, expansions=390, neighbor_attempts=17592, already_seen_attempts=5717, frontier_insertions=1314`.
  - `A3-R1` (`beam=832`): same top-10 `ids` and `d0=0.48739319736953196` on `q=0`, ON counters `distance_evaluations=18117, expansions=837, neighbor_attempts=29155, already_seen_attempts=11039, frontier_insertions=2175`.
- **Full 32-query IDs, distances, and ON counters:** stored in `artifact-evidence/p0-p1-v2-smoke-20261117T170810+0700/smoke_per_query_parity.csv` and the 4 `.jsonl` files above (`evaluate_smoke.py` run with both default `0.0` and `--gt-aux-min -1e-5`, returning identical `Recall@10` with `accepted_negative_gt_distances=0` on `0..31`).
- **Important scope note:** These 32-query smoke runs do **not** prove `0.990`/`0.998` campaign Recall floors (in fact, under `entry_best_first_v1` without Task A's `cut=1.35`, `A0-R1` got `0.9875` and `A3-R1` got `0.96875` on `q0..q31`). Prospective common-engine beam calibration on the 10K validation split remains required before P3.
- **Topology preservation:** No graph edges, IDs, or entry points were altered (`A3–R2` node `840923` preserved unchanged).

---

## 4. Scoped Gate Status & Remaining Blockers

| Gate / Scope | Verdict | Basis / Remaining Blockers |
|---|---|---|
| Byte identity (`12` assets + `261` raw receipts) | **PASS** | All checksums verified on disk; build/search receipt chains cross-verified. |
| **P0 (Historical provenance & Host)** | **HOLD** | Missing on this machine: `campaign_manifest.json`, 2 builder ELFs (`aa2d174e...`, `5f673586...`), 2 search ELFs (`ea6c757b...`, `bb6576ad...`), `flags.make`/`link.txt`/compile manifests, `build_source_commit`, `build_source_diff_sha256`, dependency revisions at build time, `seed` (`NOT_RECORDED`), `MS_TURING_1M_REPRO_MANIFEST.json`, `historical_host_receipt`, and current host P3 qualification (`thinhbui-linux` runs `schedutil`). |
| **P1 (GT v2 & Common-Engine Smoke)** | **PASS (SCOPED CORRECTNESS)** / **HOLD (FULL CAMPAIGN)** | GT Protocol v2 + `--gt-aux-min -1e-5` validator + 510 tests + `A0-R1`/`A3-R1` 32-query ON/OFF parity all PASS. Full P1 remains **HOLD** until P0 provenance/host decision is resolved and optional multi-rep/NSG checks & full-100K GT decision are settled. |
| **P2 (Multi-walker) / P3 (Benchmark)** | **CLOSED** | Not implemented or executed. |

### Concrete Next Steps
1. **Owner / Task A host (`/home/tai/ann-task-a`) decision:** Either export the remaining missing ELFs, `campaign_manifest.json`, `flags.make`/`link.txt`, build-time source commit/diff, and historical host receipt — **or** formally decide whether P0 proceeds as a *new* Task D common-engine campaign on the 9 verified graph bytes (documenting historical `seed=NOT_RECORDED` & missing builder ELFs as permanent scope bounds, or running a separate newly-IDed build campaign).
2. **Task D Host Owner:** Qualify the benchmark machine (governor, SMT/core affinity, memory residency, thermal/frequency guard) in a host profile before opening P2/P3.
3. **Separate P2 Multi-Walker Prompt (only after P0/P1 full PASS):** Design `p=1/2/4` traversal engine separately without expanding this task's scope.
