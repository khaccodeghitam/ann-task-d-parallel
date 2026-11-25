# A×D G2 v2 (`design-3.1`) · Complete Experimental Results

- **Status:** **`AUDIT_PASS`** · **`GO_A_FIXED_COHORT`** · **`GO_B_SYSTEM_FIXED_COHORT`** · **`EXPLORATORY_HOST_SPECIFIC`** · **`graph_population_ci = NOT_ESTIMABLE`**.
- **Protocol & Frozen Identity:** `AXD-G2-V2-3A-20261123` · revision **`design-3.1`** (`bc897419...`) · parent **`design-3`** (`425c7483...`) · ELF `task_da_p2_eval` (`7a2685e5...`) · `p = 2`, `S = 16`, `common beam = 432`, `CPU [0, 2]`, `jobs = 1`, `N = 10,000` (`v2_test_10000.ids`, `457abdc1...`), `warmup = 100`.
- **Audited Primary Evidence:** `../../../../artifact-evidence/axd-g2-v2-off-design3_1_run2/` (`1299/1299` `BUNDLE.sha256` OK, `NO_HOLD_JSON`), `../../../../artifact-evidence/axd-g2-v2-off-design3_1_run2-analysis.json` (`f0a35394...`), and reused upstream `../../../../artifact-evidence/axd-g2-v2-quality-design3/` (`166/166` OK).
- **Companion Documents:** [Final Audit](AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) · [Evidence Manifest](AXD_G2_V2_DESIGN3_1_EVIDENCE_MANIFEST.md) · [Closeout & G3 Decision](AXD_G2_CLOSEOUT_AND_G3_DECISION.md).

---

## 1. Executive Summary

On the frozen six-graph R90 P0A v1.3 MS-Turing-1M cohort (`3` Stock + `3` Fast, `C160/K1024/N2`, degree cap `64`) executed sequentially on `AMD Ryzen 5 PRO 4650U` (`p = 2`, `CPU [0, 2]`, `S = 16`, `beam = 432`, `12` balanced blocks = `144` OFF processes, `1,440,000` measured query executions):

1. **Quality Gate A & Gate B (`18/18` ON): BOTH `PASS`.** All 6 graphs exceed the `0.990` simultaneous Recall@10 lower bound (`LCB95 = 0.991188–0.991514`); `B1+A1` preserves **100% bit-exact ordered Top-10 IDs and `squared_l2` parity** across `60,000` validation ON pairs, `60,000` test ON pairs, and all `1,440,000` OFF test executions (`0` mismatches). Stock and Fast arms satisfy cross-arm Recall equivalence (`Fast − Stock = +0.000117`, `CI95 = [-0.000051, +0.000284] ⊂ (-0.0005, +0.0005)`).
2. **Primary Estimand A (`B1+A1` vs `baseline` within-graph): `GO_A_FIXED_COHORT`.** Geometric paired mean latency reduction is **`6.033%`** (`CI12 = [5.977%, 6.090%]`, `drift-CI6 = [5.991%, 6.075%]`, `joint bootstrap CI95 = [5.954%, 6.113%]`, `speedup = 1.0642×`), exceeding the pre-registered `3.0%` practical threshold by more than `2×`. Arithmetic mean latency drops from **`3619.71 µs` to `3401.33 µs`** (`-218.38 µs/query`, `-6.033%`).
3. **Zero Tail or RAM Regression:** Instead of regressing within the `+5% / +10%` envelope, **P50 (`-6.01%`), P95 (`-4.22%`), and P99 (`-4.09%`) all improve on every graph**. Peak RSS (`vm_hwm_kib`) is virtually unchanged (`871,696 → 871,705 KiB`, mean `+9.4 KiB`, `72/72` integer hard gate PASS).
4. **2×2 Factorial & Secondary Estimand B (`BUILD–SEARCH`): `GO_B_SYSTEM_FIXED_COHORT`.** Fast construction saves **`8.463 s/index` (`-20.03%`)** in historical Host A BUILD with **no measurable Search latency difference** (`+0.33 µs` base, `+0.37 µs` opt; CIs include `0`) and **zero BUILD × B1+A1 interaction** (`+0.037 µs`, `CI95 [-2.58, +2.66] µs`). Task A BUILD gains and Task D Search gains combine **additively**, saving **`30.336 s`** (`CI95 [30.071, 30.602] s`) at `Q = 100,000` and **`227.194 s`** (`CI95 [224.537, 229.850] s`) at `Q = 1,000,000` under the two-host model (excluding transfer/load).
5. **Mechanism Alignment & Nuance:** In ON diagnostics, `B1+A1` eliminates **`74.98%`** of duplicate L2 evaluations (**`-12.22%`** of total L2 evaluations, `~2,784 L2/query`), while keeping expansions, rounds, and frontier insertions bit-identical. Net OFF latency reduction (`-6.03%`) is roughly half the `-12.22%` total-L2 reduction, consistent with fixed non-L2 traversal work plus `+35.9 µs/query` higher ON `merge_time_ns` bookkeeping overhead.

---

## 2. Experimental Protocol Summary

- **Cohort & Engine:** Six original unmodified PiPNN graphs from Task A R90 P0A v1.3 (`MS-Turing-1M`, `1,000,000 × 100` FP32, `C160/K1024/N2`, degree cap `64`, H85 Highway `6bc2d477...`), evaluated with frozen Release ELF `task_da_p2_eval` (`7a2685e5...`, source `f2cd634`, GCC `13.3.0`, `-O3 -DNDEBUG -std=c++17`), entry `0`, `K = 10`, squared L2 in `double`, `flat` merge, `p = 2` pinned workers on physical cores `0, 1` (`CPU [0, 2]`, shared L3 CCX0 `[0..5]`), `S = 16`, `jobs = 1`, `common beam = 432` (locked validation-only from Stage 5 `val_10k` via assurance rule `r - 4.2279·SE >= 0.990`).
- **Policies:** `base` = `visited_policy=baseline, frontier_mode=full`; `opt` (`B1+A1`) = `visited_policy=barrier_all_evaled, frontier_mode=incremental`.
- **Query Panel Disclosure:** `v2_test_10000.ids` (`457abdc1...`, `10,000` unique IDs deterministically hash-ranked from the `81,000`-ID pool `test_90k \ (pilot3k ∪ disjoint3k ∪ narrow3k)`, `0` overlap with `val_10k` and all D small panels, but drawn from historical `public 100K` / `test_90k` previously evaluated by Task A and R86/P1). Every process runs `100` validation warmup queries (`warmup_val_100.ids`) prior to timing.
- **Balanced Execution & Environment Control:** `12` sequential blocks × `6` graphs × `2` policies = `144` OFF processes on clean `multi-user.target` TTY with temporary reversible pause of `2` user timers, `15` active system timers, companion services, `cups-browsed`, `avahi-daemon`, `cron`, and `snapd` (`scripts/prepare_quiet_tty_env.sh`). Topology-aware `design-3` contention guard enforced per-process (`workers [0..3] <= 0.01`, `CCX0 [0..5] <= 0.02`, `host [0..11] <= 0.025`, `single proc <= 0.10`, `preflight >= 15 s`). `design-3.1` amended only the OFF JSONL parser (`counters` strictly omitted in native P2 OFF) while keeping `100%` of statistical, quality, and guard contracts unchanged.

---

## 3. Quality ON Results (`18/18` Reused Upstream, Verified 100% by Replay)

| Graph (`arm`) | Validation `b432` Parity & Dup L2 Saved | Test `b432` Parity (`10k`) | Test Recall@10 (`SE`) | Simultaneous `LCB95` (`z=2.3940`, floor `0.990`) | Test Dup L2 Saved (`/query`) | Dup L2 Drop (`%` Total L2) |
|---|---|---|---:|---:|---:|---:|
| `stock_off_r1` | `100%` (`27,895,935`) | **`100%`** | `0.99209` (`0.000324`) | **`0.991315`** (`PASS`) | `27,828,990` (`2,782.9`) | `-74.96%` (`-12.22%`) |
| `stock_off_r2` | `100%` (`27,895,539`) | **`100%`** | `0.99197` (`0.000327`) | **`0.991188`** (`PASS`) | `27,839,745` (`2,784.0`) | `-75.00%` (`-12.22%`) |
| `stock_off_r3` | `100%` (`27,893,542`) | **`100%`** | `0.99209` (`0.000324`) | **`0.991314`** (`PASS`) | `27,843,458` (`2,784.3`) | `-75.01%` (`-12.22%`) |
| `fast_off_r1` | `100%` (`27,922,054`) | **`100%`** | `0.99229` (`0.000324`) | **`0.991514`** (`PASS`) | `27,853,430` (`2,785.3`) | `-75.01%` (`-12.23%`) |
| `fast_off_r2` | `100%` (`27,888,121`) | **`100%`** | `0.99197` (`0.000325`) | **`0.991193`** (`PASS`) | `27,840,614` (`2,784.1`) | `-74.97%` (`-12.22%`) |
| `fast_off_r3` | `100%` (`27,899,769`) | **`100%`** | `0.99224` (`0.000323`) | **`0.991467`** (`PASS`) | `27,835,869` (`2,783.6`) | `-74.95%` (`-12.22%`) |

- **Gate A (`A_pass = true`):** All `6/6` `LCB95 >= 0.991188 >= 0.990`; inter-graph point span = `0.000320`; `0 / 120,000` ON output mismatches.
- **Gate B (`B_pass = true`):** Stock arm mean = `0.992050`, Fast arm mean = `0.992167`, paired query-level `arm_difference = +0.00011667` (`SE = 0.00008544`), **`arm_ci95 = [-0.00005081, +0.00028414]`** strictly inside `(-0.0005, +0.0005)`.

---

## 4. Performance OFF Results (`144/144`, `run2`)

### 4.1 Primary Estimand A & Uncertainty Sensitivity

| Estimator / Sensitivity Scheme | Point Reduction (`%`) | 95% Confidence Interval (`%`) | Log-Ratio Point / CI95 | Speedup (`×`) | Exceeds `3.0%` (`θ=0.030459`)? |
|---|---:|---|---|---:|---|
| **Primary (`12` balanced blocks, `t`, `df=11`)** | **`6.0332%`** | **`[5.9766%, 6.0897%]`** | `0.062228` `[0.061626, 0.062830]` | **`1.06421×`** `[1.06356, 1.06485]` | **YES (`+2.977 pp` margin)** |
| Drift sensitivity (`6` adjacent pairs, `t`, `df=5`) | `6.0332%` | **`[5.9913%, 6.0750%]`** | `[0.061782, 0.062674]` | `1.06421×` | **YES (`+2.991 pp` margin)** |
| Query-only block bootstrap (`10,000`, block `100`, seed `20261123`) | `6.0332%` | **`[5.9703%, 6.0958%]`** | `[0.061559, 0.062895]` | `1.06421×` | **YES (`+2.970 pp` margin)** |
| **Joint query × process bootstrap (`10,000`, seed `20261123`)** | `6.0332%` | **`[5.9543%, 6.1130%]`** | `[0.061389, 0.063078]` | `1.06421×` | **YES (`+2.954 pp` margin)** |
| Alternate-seed joint bootstrap (`2,000`, seed `20261125`, audit check) | `6.0332%` | `[5.9589%, 6.1147%]` | `[0.061439, 0.063096]` | `1.06421×` | **YES (seed-invariant)** |
| Stock arm subgroup (`3` graphs, `df=11`) | **`6.0324%`** | `[5.9867%, 6.0780%]` | `[0.061734, 0.062706]` | `1.06420×` | **YES (`-218.36 µs`)** |
| Fast arm subgroup (`3` graphs, `df=11`) | **`6.0339%`** | `[5.9514%, 6.1163%]` | `[0.061359, 0.063114]` | `1.06421×` | **YES (`-218.40 µs`)** |
| Arithmetic cohort ratio-of-means (descriptive) | `6.0331%` | — | `3619.71 → 3401.33 µs` (`-218.38 µs`) | `1.06420×` | Consistent |

### 4.2 Per-Graph Latency, Tail, Throughput, RAM, CPU & Leave-One-Out Table (`12` Blocks per Graph)

| Graph | Base Mean (`µs`) | Opt Mean (`µs`) | Δ Mean (`µs`) | Geo Red. (`%`) `[CI95]` | LOO Red. (`%`) | P50 (`base→opt`, `Δ%`) | P95 (`base→opt`, `Δ%`, `UB18`) | P99 (`base→opt`, `Δ%`, `UB18`) | QPS_wall (`base→opt`) | ΔRSS KiB (`min/mean/max`) | Proc CPU-s (`base→opt`) |
|---|---:|---:|---:|---|---:|---|---|---|---|---|---:|
| `stock_off_r1` | `3619.56` | `3400.09` | `-219.46` | **`6.063%`** `[5.992, 6.135]` | `6.027%` | `3734.1→3508.9` (`-6.03%`) | `4100.4→3925.7` (`-4.26%`, `-4.14%`) | `4232.6→4064.0` (`-3.98%`, `-3.82%`) | `276.26→294.09` | `-76 / +45.7 / +212` | `76.13→70.66` |
| `stock_off_r2` | `3619.97` | `3402.83` | `-217.14` | **`5.999%`** `[5.896, 6.101]` | `6.040%` | `3736.3→3513.3` (`-5.97%`) | `4101.0→3929.1` (`-4.19%`, `-4.03%`) | `4225.1→4051.8` (`-4.10%`, `-3.91%`) | `276.23→293.86` | `-176 / -5.7 / +92` | `76.27→70.65` |
| `stock_off_r3` | `3620.10` | `3401.61` | `-218.49` | **`6.035%`** `[5.955, 6.116]` | `6.033%` | `3736.9→3512.2` (`-6.01%`) | `4099.3→3925.4` (`-4.24%`, `-4.07%`) | `4231.1→4058.0` (`-4.09%`, `-3.88%`) | `276.22→293.96` | `-296 / -67.7 / +140` | `75.82→70.67` |
| `fast_off_r1` | `3618.48` | `3401.06` | `-217.42` | **`6.009%`** `[5.860, 6.157]` | `6.038%` | `3735.2→3511.3` (`-5.99%`) | `4095.4→3924.5` (`-4.17%`, `-3.93%`) | `4229.9→4057.1` (`-4.09%`, `-3.78%`) | `276.34→294.01` | `-124 / -11.7 / +136` | `76.10→70.67` |
| `fast_off_r2` | `3620.83` | `3400.56` | `-220.27` | **`6.083%`** `[5.974, 6.193]` | `6.023%` | `3738.0→3511.4` (`-6.06%`) | `4100.7→3925.4` (`-4.28%`, `-4.09%`) | `4230.2→4055.5` (`-4.13%`, `-3.91%`) | `276.16→294.05` | `-144 / -22.3 / +112` | `76.42→70.78` |
| `fast_off_r3` | `3619.33` | `3401.81` | `-217.51` | **`6.010%`** `[5.870, 6.149]` | `6.038%` | `3736.7→3512.3` (`-6.01%`) | `4097.3→3926.9` (`-4.16%`, `-3.87%`) | `4220.7→4045.9` (`-4.14%`, `-3.80%`) | `276.28→293.94` | `-188 / +118.0 / +240` | `75.97→71.00` |
| **Cohort Overall** | **`3619.71`** | **`3401.33`** | **`-218.38`** | **`6.033%`** `[5.977, 6.090]` | `6.023–6.040%` | `3736.2→3511.6` (`-6.01%`) | `4099.0→3926.2` (`-4.22%`, `≤-3.87%`) | `4228.3→4055.4` (`-4.09%`, `≤-3.78%`) | **`276.25→293.99`** (`+6.42%`) | **`-296 / +9.4 / +240`** | **`76.12→70.74`** (`-7.07%`) |

*Notes:*
- `UB18` = simultaneous one-sided 95% upper bound (`t(1 - 0.05/18, 11)`) for tail regression (`+5%` p95 / `+10%` p99 budgets). Negative values prove **simultaneous tail improvement**, not merely absence of regression.
- **Process-window CPU time/query (`cpu_seconds / 10,000`):** `7,611.8 → 7,074.0 CPU-µs/query` (`-5.38 s/process`, `CI95 [-5.64, -5.11] s`, `-7.07%`; `cpu_percent = 191.43% → 190.91%`, `cpu_capacity_percent = 95.71% → 95.45%`). **Explicit caveat:** `cpu_seconds` covers the entire first-to-last alive `/proc/<pid>/stat` window (`proc_wall = 39.76 → 37.05 s`, `guard_wall = 40.13 → 37.93 s`, `batch_wall = 36.20 → 34.02 s`, non-batch load/warmup/serialize wall `~3.93 → 3.91 s`), and is **not** search-only CPU time.
- **Per-block stability (`b0..b11`):** Block geometric reductions are `6.047%, 6.102%, 6.043%, 5.914%, 5.970%, 6.010%, 6.216%, 5.918%, 6.016%, 6.078%, 5.957%, 6.127%` (`Spearman ρ(block, effect) = +0.035`).

### 4.3 Full 2×2 Factorial Cell Summary (`Arm × Policy`, `36` Processes per Cell)

| 2×2 Cell | Historical BUILD (`s`, Host A) | Search Mean (`µs`, SD across 12 blocks) | P50 / P95 / P99 (`µs`) | QPS_wall (`jobs=1`) | Peak RSS (`KiB`) | Proc CPU-s (`CPU-µs/q`*) | `cpu_percent` (`cap%`) |
|---|---:|---:|---|---:|---:|---:|---:|
| **`stock_base`** | `42.257` | `3619.87` (`2.36`) | `3735.8 / 4100.2 / 4229.6` | `276.24` | `871,687.8` | `76.07` (`7607.3`) | `191.44%` (`95.72%`) |
| **`stock_opt`** | `42.257` | `3401.51` (`1.45`) | `3511.5 / 3926.7 / 4057.9` | `293.97` | `871,678.6` | `70.66` (`7066.1`) | `190.91%` (`95.45%`) |
| **`fast_base`** | `33.793` | `3619.54` (`2.85`) | `3736.6 / 4097.8 / 4226.9` | `276.26` | `871,704.0` | `76.16` (`7616.4`) | `191.42%` (`95.71%`) |
| **`fast_opt`** | `33.793` | `3401.14` (`3.16`) | `3511.7 / 3925.6 / 4052.8` | `294.00` | `871,732.0` | `70.82` (`7081.8`) | `190.91%` (`95.45%`) |

*\*Process-alive window (`load + warmup + search + serialize`), not search-only CPU.*

### 4.4 Full 2×2 Contrasts & Modeled BUILD–SEARCH System Benefit (`GO_B_SYSTEM_FIXED_COHORT`)

Positive `ΔSearch` (`U − V`) and positive `ΔT(Q)` mean the target `V` is **faster** than reference `U`. All `ΔT(Q)` CIs are conditional on the 6 fixed historical Host A BUILD receipts and exclude cross-host transfer/load (`UNKNOWN`).

| Contrast (`Target V vs Ref U`) | Historical `ΔBUILD` (`s`) | Measured `ΔSearch` (`µs/q`) | Search Log-Ratio `CI95` (Joint Boot `Δµs`) | Modeled `ΔT(Q=1)` (`s`) `[CI95]` | Modeled `ΔT(Q=100k)` (`s`) `[t-CI95]` / `[Joint Boot]` | Modeled `ΔT(Q=1M)` (`s`) `[t-CI95]` | Break-Even `Q*` |
|---|---:|---:|---|---|---|---|---|
| `fast_base vs stock_base` *(BUILD arm effect on base)* | `+8.463` | `+0.330` | `[-0.000377, +0.000560]` (`[-1.24, +2.05] µs`) | `+8.463` `[8.463, 8.463]` | `+8.496` `[8.327, 8.666]` / `[8.339, 8.669]` | `+8.793` `[7.099, 10.487]` | `None` *(no loss)* |
| `fast_opt vs stock_opt` *(BUILD arm effect on opt)* | `+8.463` | `+0.367` | `[-0.000465, +0.000681]` (`[-1.49, +2.14] µs`) | `+8.463` `[8.463, 8.463]` | `+8.500` `[8.305, 8.695]` / `[8.314, 8.677]` | `+8.830` `[6.879, 10.780]` | `None` *(no loss)* |
| `stock_opt vs stock_base` *(B1+A1 on Stock, audit)* | `0.000` | `+218.364` | `[+0.061734, +0.062706]` (`t-CI [+216.64, +220.09] µs`) | `+0.000218` | `+21.836` `[21.664, 22.009]` | `+218.364` `[216.636, 220.092]` | `None` |
| `fast_opt vs fast_base` *(B1+A1 on Fast)* | `0.000` | `+218.401` | `[+0.061359, +0.063114]` (`[+214.95, +221.73] µs`) | `+0.000218` `[0.000215, 0.000221]` | **`+21.840`** `[21.533, 22.147]` / `[21.495, 22.173]` | **`+218.401`** `[215.331, 221.470]` | `None` |
| **`fast_opt vs stock_base`** *(Combined A×D system)* | **`+8.463`** | **`+218.730`** | **`[+0.061564, +0.063091]`** (`[+215.42, +222.04] µs`) | **`+8.464`** `[8.464, 8.464]` | **`+30.336`** `[30.071, 30.602]` / `[30.005, 30.667]` | **`+227.194`** `[224.537, 229.850]` | `None` *(strictly dominates)* |
| **2×2 Interaction** `(Fast_gain − Stock_gain)` | — | `+0.037` | `log +0.000016 [-0.000734, +0.000766]` (`[-2.58, +2.66] µs`) | — | — | — | **Zero interaction (additive)** |

### 4.5 Paired Foreign-Load Noise Balance (`noise_balance`, Diagnostic Only)

| Telemetry Tier | Base Mean | Opt Mean | Max Process Mean | Max Rolling Window (`run2`) | `design-3` Hard Cap | Paired `Δ (opt − base)` Mean `[CI95, df=11]` | Spearman `ρ(Δ, x_gb)` |
|---|---:|---:|---:|---:|---:|---|---:|
| Worker cores + SMT `[0..3]` | `0.001960` | `0.001839` | `0.003782` | `0.005495` (`10s`) | `<= 0.0100` | `-0.000122` `[-0.000296, +0.000052]` | `+0.0241` |
| CCX0 / Shared L3 `[0..5]` | `0.005004` | `0.005082` | `0.005789` | `0.007499` (`10s`) | `<= 0.0200` | `+0.000079` `[-0.000025, +0.000182]` | — |
| Whole host `[0..11]` | `0.005030` | `0.005106` | `0.005999` | `0.006997` (`15s`) | `<= 0.0250` | `+0.000077` `[-0.000028, +0.000182]` | `-0.1340` |

All three paired `Δ` CIs span zero (`imbalance_warning = false`), confirming no systematic noise bias favoring either policy.

---

## 5. Mechanism Evidence (All 17 Counters from `12` Test ON Runs)

*(Cohort mean per query across all 6 graphs × 10,000 test queries in `axd-g2-v2-quality-design3`; ON timing counters are diagnostic instrumentation only and do NOT constitute an exclusive OFF decomposition.)*

| Counter Group / Metric (Mean per Query) | `baseline/full` (`base`) | `B1+A1` (`opt`) | Exact Delta (`opt − base`) | Mechanistic Role |
|---|---:|---:|---:|---|
| `unique_distance_evaluations` | `19,063.5` | `19,063.5` | **`0.0` (exact invariant)** | Search trajectory & unique work unchanged |
| `expansions` (`unique` / `duplicate`) | `456.68` (`440.46` / `16.22`) | `456.68` (`440.46` / `16.22`) | **`0.0` (exact invariant)** | Exact parity of expanded vertices |
| `neighbor_attempts` / `frontier_insertions` | `26,069.5` / `2,548.5` | `26,069.5` / `2,548.5` | **`0.0` (exact invariant)** | Identical neighbor traversal & insertions |
| `sync_merge_count` | `14.866` | `14.866` | **`0.0` (exact invariant)** | Identical round count (`S = 16`) |
| `per_worker_expansions` (`w0` / `w1`) / `idle_rounds` (`w0` / `w1`) | `229.16` / `227.52` · `0` / `0.102` | `229.16` / `227.52` · `0` / `0.102` | **`0.0` (exact invariant)** | Identical load balance across workers |
| **`duplicate_distance_evaluations`** | **`3,712.97`** | **`928.77`** | **`-2,784.20` (`-74.98%`)** | **Direct B1 duplicate suppression** |
| **`distance_evaluations` (total L2)** | **`22,776.43`** | **`19,992.23`** | **`-2,784.20` (`-12.22%`)** | Exact 1:1 reduction from duplicate suppression |
| **`already_seen_attempts`** | **`3,293.07`** | **`6,077.27`** | **`+2,784.20` (`+84.55%`)** | Exact 1:1 shift from L2 compute to visited-bit hit |
| `per_worker_distance_evaluations` (`w0` / `w1`) | `11,436.6` / `11,339.9` | `10,042.1` / `9,950.1` | `-1,394.5` / `-1,389.7` | Symmetric `-12.2%` work savings on both workers |
| `merge_time_ns` (ON diagnostic, µs/query) | `348.51 µs` | `384.39 µs` | **`+35.88 µs` (`+10.3%`)** | Added B1 barrier publication + A1 bookkeeping cost |
| `barrier_wait_ns` (ON diagnostic, µs/query) | `219.70 µs` | `224.56 µs` | `+4.86 µs` (`+2.2%`) | Slight barrier wait increase in ON |
| `sync_wait_ns` (ON diagnostic, µs/query) | `568.09 µs` | `608.49 µs` | `+40.40 µs` (`+7.1%`) | Total ON sync window (`barrier + merge`) |
| `worker_idle_ns` (ON diagnostic, µs/query) | `1.93 µs` | `1.66 µs` | `-0.27 µs` (`-14.0%`) | Negligible worker idle |

**Mechanistic interpretation (strictly scoped):** `B1+A1` eliminates `2,784.2` duplicate L2 evaluations/query (`-12.22%` total L2) while keeping the entire search graph trajectory bit-identical. That the realized OFF latency savings is **`-6.03%`** (`-218.4 µs/query`) rather than `-12.22%` is directionally consistent with (a) non-L2 traversal/memory/sync fixed costs remaining on the critical path, and (b) additional coordinator/publication overhead visible in ON `merge_time_ns` (`+35.9 µs/query`). Because G2 v2 has neither solo-B1/solo-A1 ablations nor PMU hardware counters (`perf_event_paranoid=4`), exact cycle-level attribution and separation of B1 vs A1 remain outside G2 v2 scope.

---

## 6. Negative Findings & Complete Ledger of Historical HOLDs (Preserved Unmodified)

1. **Negative / Null Finding — Zero BUILD × B1+A1 Interaction & Zero Fast Search Speedup:** Contrary to any speculation that `Fast` construction degrades or amplifies `B1+A1`'s multi-worker traversal benefit, `Fast` and `Stock` have statistically indistinguishable OFF search latency (`Δ = +0.33/+0.37 µs`, CIs contain `0`) and statistically identical `B1+A1` gains (`6.034%` vs `6.032%`; interaction `+0.037 µs`, `CI95 [-2.58, +2.66] µs`).
2. **Historical Operational & Protocol HOLDs (All Preserved Intact, Never Merged into `run2`):**
   - **G2 v1 Stage 6 (`2026-11-23`, `QUALITY_HOLD`):** Failed cross-graph point span `<= 0.0001` on `narrow_test_3000.ids` (`observed span = 0.001033`), motivating the statistically powered G2 v2 protocol (`N = 10,000`, simultaneous LCB95, arm equivalence CI).
   - **G2 v2 `design-2` Stage 0 (`2026-11-24`, `BLOCKED_PREFLIGHT`):** `B3` resolved via durable venv; `B1` (`1%` whole-host 5s cap with `5×` quantization bias + double `/proc` scan) proved infeasible on GUI/default host, motivating controlled pre-data revision `design-3`.
   - **G2 v2 `design-3` Qualification #1 (`20261124T082344Z`, `QUALIFICATION_HOLD`):** Failed `93/850` 10s worker-core windows due to `avahi-daemon` (`50.6%` share) and autologin `gnome-shell` (`9.1%`); resolved without threshold edits via `multi-user.target` + stopping `cups-browsed`/`avahi-daemon` → Qualification #2 (`20261124T094602Z`) achieved **`QUALIFICATION_PASS` (`0` failures)**.
   - **G2 v2 `design-3` OFF #1 (`axd-g2-v2-off-design3`, `11/11`, `OFF_EXECUTION_HOLD` at #1/144):** Failed in `g2_v2_design3_analyzer.output_digest()` (`KeyError: 'counters'`) because native P2 OFF omits `"counters"` rather than emitting `null`; resolved by minimal controlled parser amendment `design-3.1`.
   - **G2 v2 `design-3.1` OFF `run1` (`axd-g2-v2-off-design3_1`, `1080/1080`, `OFF_EXECUTION_HOLD` at #120/144):** Completed `119/144` valid parity-verified receipts (`6652.5 s`) before user timer `snap.firmware-updater.firmware-notifier.timer` fired at `03:00:54 +07` and pushed 15s host foreign CPU to `0.0266 > 0.0250`; preserved intact as operational evidence (zero receipts recycled into `run2`), resolved via `scripts/prepare_quiet_tty_env.sh` → clean `144/144` `run2`.

---

## 7. Statistical Interpretation Boundaries

- **What `GO_A_FIXED_COHORT` and `GO_B_SYSTEM_FIXED_COHORT` mean:** Within the fixed 6-graph MS-Turing-1M R90 v1.3 cohort, the deterministic `v2_test_10000.ids` panel (and query-exchangeable draws under the block-bootstrap model), `p = 2 / S = 16 / beam = 432`, and `AMD Ryzen 5 PRO 4650U`, `B1+A1` produces a highly reproducible **`6.03%`** Search latency reduction (`> 2×` the `3%` practical threshold) with improved tail latencies and flat RAM, and combining `Fast` BUILD (Host A) with `B1+A1` Search (Host D) strictly outperforms every other cell in the 2×2 factorial at `Q = 100,000` (`+30.34 s` modeled savings).
- **What these verdicts do NOT mean:** `graph_population_ci = NOT_ESTIMABLE` — narrow block/query CIs (`±0.06 pp`) measure **execution-repeat and query-sampling precision on these 6 fixed graphs**, **NOT** uncertainty across new random graph constructions, new datasets, other CPU architectures, or single-host end-to-end deployment including transfer/load. The study remains **`EXPLORATORY_HOST_SPECIFIC`**.
