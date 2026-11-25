# A×D G2 v2 (`design-3.1`) · Final Independent Audit Report

- **Final Audit Verdict:** **`AUDIT_PASS`** *(0 discrepancies across 100% independent replay of raw evidence, freeze manifests, approvals, 144 OFF processes, 18 Quality ON processes, 6 R90 v1.3 graphs, statistical inference, and BUILD–SEARCH model).*
- **Confirmed Frozen Analyzer Verdicts (Unmodified):**
  - Primary Estimand A: **`GO_A_FIXED_COHORT`** (`primary_reduction = 6.033151%`, `CI95 = [5.976580%, 6.089687%]`, `speedup = 1.064205×`).
  - Secondary Estimand B (BUILD–SEARCH): **`GO_B_SYSTEM_FIXED_COHORT`** (`saved_s(Q=100,000) = 30.336 s`, `CI95 = [30.071, 30.602] s`).
  - Scope & Uncertainty Labels: **`EXPLORATORY_HOST_SPECIFIC`** · **`graph_population_ci = NOT_ESTIMABLE`** · **`noise_balance.imbalance_warning = false`**.
- **Protocol & Revision:** `AXD-G2-V2-3A-20261123` · revision **`design-3.1`** · schema **`axd_g2_v2.3.1`** · `p = 2`, `S = 16`, `common beam = 432`, `CPU [0, 2]`, `AMD Ryzen 5 PRO 4650U`, Linux kernel `7.0.0-43-generic`.
- **Audit Date:** 2026-11-25.
- **Audit Constraints Verified:** Zero new native ANN benchmarks, zero re-runs of 144 OFF or 18 ON, zero modifications to frozen protocols/thresholds/analyzer/B1+A1, zero edits to raw evidence or historical HOLD bundles, zero `design-3.2` or G3 work, zero git commit/push/merge/PR actions.
- **Companion Closeout Documents:**
  - [AXD_G2_V2_DESIGN3_1_RESULTS.md](AXD_G2_V2_DESIGN3_1_RESULTS.md)
  - [AXD_G2_V2_DESIGN3_1_EVIDENCE_MANIFEST.md](AXD_G2_V2_DESIGN3_1_EVIDENCE_MANIFEST.md)
  - [AXD_G2_CLOSEOUT_AND_G3_DECISION.md](AXD_G2_CLOSEOUT_AND_G3_DECISION.md)

---

## 1. Executive Audit Scorecard (All Checks `PASS`, `0` Discrepancies)

All values below were verified directly from immutable disk artifacts, frozen C++/Python sources, raw JSONL streams (`1,440,000` OFF rows + `180,000` ON rows), and independent numerical recomputation — without relying on owner-reported summaries.

| # | Audit Domain | Verification Scope | Observed Outcome | Status |
|---:|---|---|---|---|
| 1 | Frozen protocol & packages | `design-3.1` (`29/29`), `design-3` (`26/26`), `design-2` (`24/24`) checksums; `load_freeze(environment=True, check_parent=True)` | `29/29`, `26/26`, `24/24` OK; parent invariants exact; Python `3.12.3` + `7/7` pinned packages OK | **`PASS`** |
| 2 | Source, ELF, compiler & native libs | `git show f2cd634:...` (`3` C++ files), Release ELF `task_da_p2_eval`, `/usr/bin/c++`, `5` `.so` libs, `base/queries/gt/val/warmup/test`, `6` Stage 5 baselines | 100% SHA-256 byte-exact match against `AXD_G2_V2_DESIGN3_1_FREEZE_MANIFEST.json` | **`PASS`** |
| 3 | Six R90 v1.3 graph SHA-256s | Direct disk rehash of `MS-Turing1M_{stock,fast}_off_r{1,2,3}.graph` vs freeze, `TRANSFER_MANIFEST.json`, and BUILD receipts | `6/6` SHA-256 and exact byte lengths match (`1,292,447,108 B` total) | **`PASS`** |
| 4 | Approval & campaign identity | `design3_1_off_approval_run2.json`, `start.json`, `complete.json`, console log, `BUNDLE.sha256`, `POST_REBOOT_RESTORATION` | Approval SHA `edbe6e98...` (`scope=OFF_AB`, `quota_s=10800`, `owner=thinhbui`, `2026-11-25T04:55:17+07:00`) matches `start.json`; `authorize()` PASS; `1299/1299` `BUNDLE.sha256` OK; `NO_HOLD_JSON`; `elapsed_s=7987.18 s`; `POST_REBOOT_RESTORATION=OK` | **`PASS`** |
| 5 | Strict HOLD isolation | Compare `run2` against `axd-g2-v2-off-design3` (`11/11` HOLD) and `axd-g2-v2-off-design3_1` (`1080/1080` HOLD) | Both HOLD bundles intact (`11/11`, `1080/1080`); `0/144` overlapping receipt SHAs; `0` leaked HOLD paths in `run2` or `analysis.json` | **`PASS`** |
| 6 | Upstream Qualification & Quality ON | Reused `QUALIFICATION_PASS` (`2/2` OK) and `axd-g2-v2-quality-design3` (`166/166` OK); independent replay of all `18/18` ON runs + Recall@10 + Gates A & B | `Gate A = PASS` (all 6 `LCB95 >= 0.991188 >= 0.990`), `Gate B = PASS` (`arm_ci95 = [-0.000051, +0.000284] ⊂ (-0.0005, +0.0005)`), `120,000/120,000` ON parity PASS, `max_diff vs quality.json = 0.0` | **`PASS`** |
| 7 | 144 OFF execution, parity & guards | `144` processes, `144` preflights, `72` pairs, `12` balanced blocks, `1,440,000` raw OFF rows, `host.jsonl` replay | `12×6×2` balance exact (`2×` per graph/pos, `6 AB / 6 BA`); `1,440,000/1,440,000` OFF rows omit `counters`; `144/144` bit-exact ON/OFF parity; `0` guard replay failures; `0` non-empty `stderr.log`; monotonic non-overlapping | **`PASS`** |
| 8 | Statistical & bootstrap recomputation | Independent recomputation of primary estimand, `CI12`, `drift CI6`, `query_bootstrap` (`10k`), `joint_bootstrap` (`10k`), graph CIs, LOO, 18 tail/RAM bounds, `noise_balance` | **`max_stat_diff_vs_frozen = 0.0`**; `max_noise_balance_diff = 0.0`; alternate-seed (`20261125`) bootstrap confirms `[5.959%, 6.115%]`; `AB` (`6.025%`) ≈ `BA` (`6.041%`); all pre-registered GO criteria satisfied with zero threshold edits | **`PASS`** |
| 9 | BUILD receipts & BUILD–SEARCH model | Re-verify 6 historical BUILD receipts (`configs/axd_g2_v2_build_reference.json`), 4 contrasts, `T(Q)` at `Q = 1, 100k, 1M`, and `GO_B_SYSTEM_FIXED_COHORT` gates | **`max_build_search_diff_vs_frozen = 2.84e-14`**; `GO_B_SYSTEM_FIXED_COHORT` confirmed strictly conditional on historical Host A BUILD receipts, excluding transfer/load | **`PASS`** |
| 10 | Missing metrics, confounders & limits | Telemetry inspection (`rapl`, `cpufreq`, `k10temp`, `proc_wall`, `cpu_seconds`), protocol disclosures, claim boundaries | All gaps, confounders, and non-generalizability boundaries documented transparently (§7) | **`PASS`** |

---

## 2. Provenance, Freeze Integrity & Graph SHA-256 Verification

### 2.1 Frozen Packages, Source & Runtime Pins

| Asset | Expected / Frozen Pin | Audited State |
|---|---|---|
| `design-3.1` Freeze Manifest | `bc8974193970b1663a53e08bc7de16b91013f11866965f872a78d775b7b28f5e` (`29/29` entries) | **EXACT MATCH** (`29/29 OK`) |
| `design-3` Freeze Manifest (parent) | `425c748329292ffe15db2c52bdf53f5d219b47d1ecf95ac3c76a5429814159ae` (`26/26` entries) | **EXACT MATCH** (`26/26 OK`) |
| `design-2` Freeze Manifest (ancestor) | `91186d57e5992e1df70f86a55ba928ad4d6613bb0b67ccbee0f485cc380d1749` (`24/24` entries) | **EXACT MATCH** (`24/24 OK`) |
| Frozen Search Source (`f2cd634b837a70735c3e31e5956f0524bfc26675`) | `p2_eval.cpp` (`b356ba8d...`), `p2_engine.hpp` (`c4b1bdc2...`), `engine.hpp` (`2ca38624...`) | **EXACT MATCH** (`3/3` via `git show`) |
| Release ELF `task_da_p2_eval` | `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1` | **EXACT MATCH** |
| Compiler `/usr/bin/c++` (GCC 13.3.0) | `1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769` | **EXACT MATCH** |
| Pinned Python 3.12.3 Executable | `e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f` | **EXACT MATCH** (`7/7` pkgs exact) |
| Native Runtime `.so` Libraries (`5/5`) | `libstdc++.so.6` (`1fd75fe7...`), `libgcc_s.so.1` (`d93224d2...`), `libc.so.6` (`755a371e...`), `libm.so.6` (`5dcc4d25...`), `ld-linux-x86-64.so.2` (`5fc09408...`) | **EXACT MATCH** (`5/5`) |
| Dataset & Splits (`base`, `queries`, `gt`, `val`, `warmup`, `test`) | `base` `44e83e1d...`, `queries` `48d087a1...`, `gt` `fa5acf5a...`, `val` `a3c948e9...`, `warmup` `199ca606...`, `v2_test_10000.ids` `457abdc1...` | **EXACT MATCH** (`6/6`; `val ∩ test = ∅`) |
| Stage 5 Validation Baselines (`b432`, `6/6`) | `axd-g2-validation-20261122-G81SkWjO` (`6/6` ON JSONLs) | **EXACT MATCH** (`6/6`) |

*Repository commit note:* `HEAD` is `5bc7de698f38f1e0257e0b1cce2f39196de71ff0` (`main` / `research/task-da-pivot-b1-a1-20261119`), which tracks `design-2` and `design-3`; all `design-3.1` components remain pinned as an uncommitted content-SHA overlay (verified `29/29 OK`), matching the `wrapper_source_identity` policy of the freeze manifest.

### 2.2 Direct Rehash Audit of All Six R90 v1.3 Graphs

| Graph Key | File Name | Disk Bytes | Rehashed Disk SHA-256 (`= Freeze = TRANSFER_MANIFEST = BUILD Receipt`) | Builder ELF SHA-256 | Historical BUILD Wall (s) |
|---|---|---:|---|---|---:|
| `stock_off_r1` | `MS-Turing1M_stock_off_r1.graph` | `215,313,724` | `db4f5257f06d7ca6df0a040d19590d201bc3e9b1eab7bf0f36265732969716cc` | `13bef65c...` | `42.57` |
| `stock_off_r2` | `MS-Turing1M_stock_off_r2.graph` | `215,413,516` | `5de325e9bbb0b46208c4878b3af77ae79c7c1821096eb11064efab5c15d0ae84` | `13bef65c...` | `41.99` |
| `stock_off_r3` | `MS-Turing1M_stock_off_r3.graph` | `215,432,108` | `a7eb1ad15ff31130ce8411169f19b41d9bde75577ad5b5416e1b53a90ecbd010` | `13bef65c...` | `42.21` |
| `fast_off_r1` | `MS-Turing1M_fast_off_r1.graph` | `215,398,220` | `104a1bc69711e494dbf562772b867752dd915e53ff7ed4142763cdc98fb354e9` | `fcfb16d0...` | `33.84` |
| `fast_off_r2` | `MS-Turing1M_fast_off_r2.graph` | `215,429,104` | `4b69a53c548cdb47714902c2201fe732daf668683056aae9efa724982e11731a` | `fcfb16d0...` | `33.74` |
| `fast_off_r3` | `MS-Turing1M_fast_off_r3.graph` | `215,460,436` | `7c80157e8165e2792151e4934078fd7bd2fa2deebad2ad9864ba6aaf24da0462` | `fcfb16d0...` | `33.80` |
| **Total (6 graphs)** | — | **`1,292,447,108`** | **`6/6 MATCH`** | `f5e48bb6...` | Stock `42.257` / Fast `33.793` |

---

## 3. Approval Identity, Campaign Completeness & HOLD Isolation Audit

- **Approval receipt (`design3_1_off_approval_run2.json`):**
  - SHA-256: `edbe6e98005b358ade094747d33bab3edfc509dcf5b7d9327708a0041d44deba` (matches `axd-g2-v2-off-design3_1_run2.console.log` line 4 and exact JSON equality with `start.json["approval"]`).
  - Owner & timestamp: `owner = "thinhbui"`, `approved_at = "2026-11-25T04:55:17+07:00"` (explicit timezone verified).
  - Scope & quota: `scope = "OFF_AB"`, `quota_s = 10800`, `quiet_host_confirmed = true`, targeting `/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-off-design3_1_run2`.
- **Execution window & seal (`axd-g2-v2-off-design3_1_run2`):**
  - Started UTC: `2026-11-24T22:06:37Z` · Finished UTC: `2026-11-25T00:19:44Z` · `complete.json["elapsed_s"] = 7987.182369 s` (`133.12 min` = `2.219 h`, leaving `2,812.82 s` / `26.0%` headroom under `quota_s = 10800 s`).
  - `BUNDLE.sha256` (`c2b4d8f1c6e0cc004a3c2db100abce6ed48c85657c90fd9a4c38d81882925a84`): **`1,299 / 1,299` OK** (`3` top-level JSONs + `144` `*_preflight.jsonl` + `144 × 8` per-process files). **`NO_HOLD_JSON`**.
  - Post-reboot host restoration (`./scripts/prepare_quiet_tty_env.sh --verify-restored`): **`POST_REBOOT_RESTORATION=OK`** (all checked desktop/system/user units active on standard Ubuntu Desktop).
- **Zero contamination from the two historical HOLD campaigns:**
  - `axd-g2-v2-off-design3` (design-3 parser `KeyError: 'counters'` HOLD at process #1): preserved untouched (`BUNDLE.sha256` **`11/11 OK`**, `HOLD.json` SHA `8187bb38...`).
  - `axd-g2-v2-off-design3_1` (design-3.1 run1 `firmware-notifier` HOLD at process #120/144): preserved untouched (`BUNDLE.sha256` **`1080/1080 OK`**, `HOLD.json` SHA `4e078fc1...`).
  - Independent set intersection between `run2/complete.json["receipts"]` (`144` SHAs) and `run1/HOLD.json["receipts"]` (`119` SHAs) = **`0` overlapping SHAs**. Zero path references to either HOLD directory appear in `run2/start.json` or `run2-analysis.json`.

---

## 4. Audit of 144 OFF Processes, 144 Preflights, Schedule Balance & Telemetry

| Operational & Raw-Data Check | Audited Result across `run2` | Verdict |
|---|---|---|
| Schedule completeness & factorial balance | `12` blocks × `6` graphs × `2` policies = `144` processes (`72` consecutive pairs). Every graph appears exactly `2×` at each block position `0..5`, with `6` `base→opt` (`AB`) and `6` `opt→base` (`BA`) pairs. `start.json["plan"] == plan(artifacts, "off", RUN2)` exact. | **`PASS`** |
| Monotonic non-overlapping timeline | Every preflight and process start `monotonic_s` is strictly greater than previous process end `monotonic_s` across all `144` runs. | **`PASS`** |
| Preflight quiet windows (`>= 15 s` required) | `144/144` preflight JSONLs verified against `complete.json["preflight_sha256"]`; duration `15.552–15.792 s` (zero thermal cooldown delays). | **`PASS`** |
| Native OFF row schema & bit-exact parity | `1,440,000 / 1,440,000` JSONL rows strictly omit `"counters"` (`design-3.1` producer contract); exact `v2_test_10000.ids` order; **`144/144`** processes match Quality ON ordered Top-10 IDs + `squared_l2` SHA-256 digests (`0 / 1,440,000` mismatches). | **`PASS`** |
| Recomputed `process_result()` vs `metrics.json` | **`144/144`** exact equality; `144/144` `exit_code == 0`, `guard_failure is None`, `stderr.log == 0 B`, `requested_cpus == observed_cpus == [0, 2]`. | **`PASS`** |
| Independent `make_guard(phase="off")` replay | **`0` failures** across all `144` `host.jsonl` files (`38–41` 1 Hz samples/process, total `~5,600` samples). | **`PASS`** |
| Peak rolling foreign CPU vs `design-3` caps | Workers `[0..3]` max `0.005495 <= 0.010` (`45.1%` margin); CCX0 `[0..5]` max `0.007499 <= 0.020` (`62.5%` margin); Host `[0..11]` max `0.006997 <= 0.025` (`72.0%` margin). | **`PASS`** |
| Hardware, thermal & resource envelopes | `AC = 1` continuously; `Tctl` start `41.00–55.125°C` (`< 85°C`), exec max `78.50°C` (`< 95°C`); `min MemAvailable = 13.16 GiB` (`> 1 GiB`); `min free disk = 136.14 GiB` (`> 20 GiB`); `max swap = 0 B`; governor `schedutil`, `platform_profile = balanced`. | **`PASS`** |

---

## 5. Independent Statistical, Bootstrap, Stability & GO/PIVOT Criteria Audit

### 5.1 Numerical Cross-Check vs Frozen Analyzer (`axd-g2-v2-off-design3_1_run2-analysis.json`)

Independent Python recomputation directly from the `(12, 6, 2, 10000)` raw `beam_432_p2_OFF.jsonl` latency tensor reproduced **every frozen analyzer output identically**:

| Quantity Audited | Frozen Analyzer Value | Independent Recomputation | Max Abs Diff |
|---|---|---|---:|
| `primary_reduction` (`1 - exp(-xbar)`) | `0.06033150997154797` (`6.033151%`) | `0.06033150997154797` | **`0.0`** |
| `primary_log_ci95` (`df = 11`) | `[0.06162629072101192, 0.06282998148566661]` | Exact match | **`0.0`** |
| `primary_reduction_ci95` | `[5.976580461%, 6.089687496%]` | Exact match | **`0.0`** |
| `speedup` (`exp(xbar)`) | `1.0642051006411009×` | Exact match | **`0.0`** |
| `drift_log_ci95` (`6` block pairs, `df = 5`) | `[0.06178245492352153, 0.06267381728315698]` (`[5.991%, 6.075%]`) | Exact match | **`0.0`** |
| `query_bootstrap.primary_log_ci95` (`10k`, seed `20261123`) | `[0.0615589879442858, 0.06289464911949924]` (`[5.970%, 6.096%]`) | Exact match | **`0.0`** |
| `joint_bootstrap.primary_log_ci95` (`10k`, seed `20261123`) | `[0.06138917199941519, 0.06307841239441755]` (`[5.954%, 6.113%]`) | Exact match | **`0.0`** |
| `graph_log_effects` (`6` graphs) | `[0.062549, 0.061860, 0.062251, 0.061967, 0.062763, 0.061978]` | Exact match | **`0.0`** |
| `leave_one_out_log_effects` (`6` LOO) | `[0.062164 .. 0.062302]` (`[6.023%, 6.040%]`) | Exact match | **`0.0`** |
| `tail_log_upper` (`p95`, `p99`) & `ram_mean_upper` (`18` bounds) | `max p95 upper = -3.868%`, `max p99 upper = -3.782%`, `max RAM upper = 0.00262` | Exact match | **`0.0`** |
| `noise_balance` (`paired_delta_all/workers/ccx0`, Spearman) | `imbalance_warning = false`, `ρ_all = -0.1340`, `ρ_wrk = +0.0241` | Exact match | **`0.0`** |
| `build_search` (`4` contrasts × `3` workloads) | `GO_B_SYSTEM_FIXED_COHORT`; `saved_s(100k) = 30.33637 s` | Exact match | **`2.84e-14`** |

### 5.2 Audit of Pre-Registered GO / HOLD / PIVOT Criteria (Unmodified Thresholds)

| Pre-Registered Criterion (`AXD_G2_V2_GO_NO_GO_CRITERIA.md`) | Frozen Threshold | Audited Value (`run2`) | Gate Result |
|---|---|---|---|
| Quality Gate A (6 simultaneous `LCB95`, parity, invariants) | All 6 `LCB95 >= 0.990`; 100% parity; `dup_L2_saved > 0` | `min LCB95 = 0.991188`; `120k/120k` ON + `1.44M/1.44M` OFF parity; `-74.98%` dup L2 | **`PASS`** |
| Quality Gate B (cross-arm Recall equivalence) | `arm_ci95 ⊂ (-0.0005 + 1e-12, +0.0005 - 1e-12)` | `[-0.000051, +0.000284]` (margin `> 0.000215` both sides) | **`PASS`** |
| Primary gain lower CI12, drift CI6, joint bootstrap CI95 | `min(lowers) > θ + 1e-12` (`θ = 0.030459`, `3.0%`) | `min = 0.061389` (`5.954%`), margin **`+0.030930` log (`> 2×` threshold)** | **`PASS`** |
| Stability: 6 graphs `> 0`, Stock & Fast `>= 3%`, 6 LOO `>= 3%` | All 6 `> 0`; arms & LOO `>= 0.030459` | Graphs `[5.999%, 6.083%]`; Stock `6.032%`, Fast `6.034%`; LOO `[6.023%, 6.040%]` | **`PASS`** |
| RAM integer hard gate (all 72 pairs) | `10(C - B) <= max(655360, B)` (`<= 10% B`) | **`72/72 PASS`** (`ΔRSS ∈ [-296, +240] KiB`, max normalized `0.00275 <= 1.0`) | **`PASS`** |
| 18 simultaneous upper bounds + joint bootstrap tail upper95 | `p95 <= +5%`, `p99 <= +10%`, `RAM <= 1.0` | `p95 <= -3.868%`, `p99 <= -3.782%` (**improvement**), `RAM <= 0.00262` | **`PASS`** |
| PIVOT_TO_TASK_A trigger rules | Primary & Fast upper CI `< θ`, or any tail/RAM lower bound `> budget` | None triggered | **`NOT TRIGGERED`** |
| `GO_B_SYSTEM_FIXED_COHORT` (`Q₀ = 100,000`) | `B_pass & B_authorized & safe`; `fast_opt vs stock_base` lower CI12 & joint CI `> 0`; beats `fast_base` and `stock_opt` | `min lower = +30.005 s > 0`; vs `fast_base = +21.840 s`; vs `stock_opt = +8.500 s` | **`PASS`** |

### 5.3 Supplementary Audit Sensitivity & Confounder Checks (Diagnostic Only)

- **Bootstrap seed stability:** Independent `2,000`-resample joint bootstrap with alternate seed `20261125` gives `[5.959%, 6.115%]`, matching frozen seed `20261123` (`[5.954%, 6.113%]`).
- **Execution order balance (`AB` vs `BA`):** `36` `base→opt` pairs average **`6.025%`** (`CI95 [5.966%, 6.084%]`); `36` `opt→base` pairs average **`6.041%`** (`CI95 [5.983%, 6.100%]`). Difference `0.016 pp` is negligible with fully overlapping CIs — zero order confounding.
- **Temporal drift across 12 blocks (`2.22 h`):** Spearman correlation of block index `0..11` with paired effect `x_b` is **`ρ = +0.035`** (essentially flat; all 12 blocks within `[5.914%, 6.216%]`). Mild shared upward latency drift (`ρ = +0.364` base, `+0.357` opt; `~2–4 µs` over 2.2 h) canceled cleanly by consecutive pairing.
- **Thermal & CPU-frequency balance (`opt − base` across 12 blocks):**
  - Start `Tctl`: `Δ = -0.281°C` (`CI95 [-1.372, +0.810]°C`, includes `0` — balanced at process launch).
  - Mean execution `Tctl`: `67.50°C` (`opt`) vs `68.08°C` (`base`), `Δ = -0.574°C` (`CI95 [-0.797, -0.351]°C`) — expected physical consequence of `opt` running `~2.2 s` shorter and using `~7.1%` less CPU work per process.
  - Mean worker `[0, 2]` clock (`scaling_cur_freq`): `3745.8 MHz` (`opt`) vs `3740.6 MHz` (`base`), `Δ = +5.20 MHz` (`CI95 [-5.54, +15.93] MHz`, includes `0` — `~0.14%` difference, cannot explain a `6.03%` latency reduction).

---

## 6. Audit of BUILD Receipts & BUILD–SEARCH Model Separation

The audit verifies strict separation between three distinct evidence layers inside `build_search`:

1. **Historical BUILD (Host A, NOT re-run in G2):** Six immutable R90 P0A v1.3 receipts (`source_commit = f5e48bb6...`, `build_threads = 4`, H85 Highway `6bc2d477...`), pinned in `configs/axd_g2_v2_build_reference.json` (`c9ad18b0...`). Stock mean = **`42.257 s`** (`41.99–42.57 s`); Fast mean = **`33.793 s`** (`33.74–33.84 s`); `ΔBUILD = +8.463 s` (`-20.03%`). Graph size is virtually unchanged (`+0.020%`, total `1,292,447,108 B`).
2. **Measured SEARCH (Host D, Ryzen 5 PRO 4650U, `run2` 144 OFF):** Contemporaneous paired execution at `p = 2`, `S = 16`, `beam = 432`, `jobs = 1`, `N = 10,000`. Fast vs Stock search difference is near zero (`+0.330 µs` base, `+0.367 µs` opt; CIs include `0`); B1+A1 reduces search latency by **`218.36 µs`** (Stock) and **`218.40 µs`** (Fast).
3. **Modeled Two-Host System Benefit (`T(Q) = BUILD + Q × mean_OFF`):** Combines Host A BUILD constants with Host D SEARCH distributions. All CIs (`ci95_s`, `joint_ci95_s`) are **strictly conditional on the 6 fixed historical BUILD observations** (zero BUILD variance across new random roots), and explicitly **exclude index transfer, disk/network serialization, and graph-load time** (`deployment = "two hosts; transfer/load excluded and UNKNOWN"`).

---

## 7. Missing Metrics, Confounders & Scientific Limitations Audited

| Category | Audited Gap / Confounder | Evidence & Scientific Impact |
|---|---|---|
| **Missing metrics** | **Search-only CPU time** | `metrics.json["cpu_seconds"]` (`76.12 → 70.74 s`, `-7.07%`) measures `/proc/<pid>/stat` across the process-alive window (including ~`3.9 s` of graph/base load, 100-query warmup, and JSONL serialization). `p2_eval_summary.json` does not emit search-only `rusage`. |
| **Missing metrics** | **Energy / Power (Watts, Joules/query)** | `rapl` dictionary is empty (`{}`) in `100%` of `host.jsonl` samples on this host; energy efficiency is **`NOT_MEASURED`**. |
| **Missing metrics** | **Hardware PMU / Microarchitectural counters** | `perf_event_paranoid = 4`; IPC, L2/L3 cache misses, TLB misses, and branch mispredictions are **`NOT_MEASURED`**. Exclusive OFF cycle-level attribution remains **`UNKNOWN`**. |
| **Missing metrics** | **Solo B1 vs Solo A1 ablation** | G2 v2 evaluates only the combined `B1+A1` policy vs `baseline`; individual contributions of `B1` (`barrier_all_evaled`) and `A1` (`incremental` frontier) are **not separable** from G2 v2 data. |
| **Missing metrics** | **Multi-worker scaling (`p=1, 4`) & concurrent serving (`jobs > 1`)** | Strictly `p = 2`, `S = 16`, `jobs = 1` (`p1/p4 = NOT_SUPPORTED`). `QPS_wall` (`276.25 → 293.99`) is single-stream batch rate, **not** multi-query serving throughput. |
| **Missing metrics** | **End-to-end single-host BUILD + transfer + load + SEARCH** | BUILD ran on Host A (`4` threads); SEARCH ran on Host D (`2` pinned cores). Transfer time is excluded; local non-batch wall (`~3.91–3.93 s`, including load+warmup+serialize) is measured only on Host D and excluded from `T(Q)`. |
| **Confounders & limits** | **Fixed cohort & unverified root independence (`n = 6` graphs)** | `graph_population_ci = NOT_ESTIMABLE`. `Stock-r1..r3` and `Fast-r1..r3` are 3 build invocations/arm with `root independence NOT_VERIFIED`; inference does not generalize to fresh random seeds/builds. |
| **Confounders & limits** | **Historical public query pool & post-v1 redesign** | `v2_test_10000.ids` is disjoint from `val_10k` and D's 3 small 3k panels, but is drawn from `test_90k` / `public 100K` previously exposed to Task A and R86/P1; v2 was designed after seeing v1 Stage 6. Label remains **`EXPLORATORY_HOST_SPECIFIC`**, never fresh confirmatory holdout. |
| **Confounders & limits** | **Single host (`AMD Ryzen 5 PRO 4650U`, `schedutil`), single dataset (`MS-Turing-1M`)** | Dynamic frequency scaling (`schedutil`, `balanced` profile) remained active by protocol (not fixed-clock); though worker clocks were balanced (`+5.2 MHz`, CI includes 0), generalization to other CPUs (e.g., Intel `i5-14600KF`), datasets, or graph families is **`NOT_TESTED`**. |
