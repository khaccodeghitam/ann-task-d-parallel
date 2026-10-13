# Issue29: thermal qualification and oracle-disagreement decision

## Outcome

**Host campaign: SKIPPED_THERMAL. Offline research: OFFLINE_EXECUTED.**

Started from verified merged main `5ec0841fcd04e9c06824ef3e10b59f4b08d58ed7` (PR28). No index rebuild or historical campaign continuation. Execution code was committed locally as `5816889` before freezing either prospective plan. Terminal Git HTTPS lacked credentials; the authenticated GitHub connector verified main/merge and supplied the signed merge object, whose exact Git SHA and tree were independently reconstructed locally. No credentials were written to files.

External archive ID: `ISSUE29_20261013T110233068975Z`, under the workspace's `research-v3/campaigns/`. [Machine-readable summary](../../results/issue29_20261013/SUMMARY.json), [offline results](../../results/issue29_20261013/OFFLINE_SUMMARY.json), [all36 planned stock cells](../../results/issue29_20261013/runs.csv). All36 are NOT_TESTED. No paired stock estimate or extension curve exists.

Frozen host PLAN SHA256: `29c200f19fdd3a3e497125a8a0ba450a6e9bfe267eebc9c8f14e3a0270a9ff91`.
Frozen offline PLAN SHA256: `6210ebddb50f4b616dc11a4ebe4570ae4f832aae446730e88946be8b6d5ec4b5`.
The committed [public plan](../../results/issue29_20261013/PLAN.public.json) is an explicitly sanitized derivative, **not** a replacement execution plan. Original plans/configs/raw logs remain local and sealed.

## Direct measurements: T16 qualified, subsequent T8 thermal stop

Operating condition: Performance profile, AC online, MMIO PL1/PL2 **115/135W**, unchanged in sampled command observations. Governor `powersave` with EPP `performance`; these were observed, never set. Fan mode/RPM was not measured. This is not the earlier Custom60/90W build condition. Idle temperature alone did not predict sustained safety.

|Independent quality executable|T16|T8|
|---|---:|---:|
|Startup package,°C|46|50|
|Maximum sampled package,°C|98|100|
|Process wall time,s|14.4761|13.0511|
|Native exit|0|−15(SIGTERM)|
|Full result rows observed offline|100,000|100,000|
|Independent recall@10,%|99.210|99.209|
|Status|QUALIFIED correctness|PROVISIONAL; thermal failure|

T16: all10,000 queries returned10 unique in-range IDs and finite nonnegative distances;100,000 exact uint8 squared-L2 values independently matched canonical vectors. Tie-aware recall matched printed99.21%. No user-visible failed-read/CQE error was found. CQE loss/completion counters are not exposed by this binary, so zero unobserved kernel errors is **not** established.

T8: the guard observed100°C and critical-trip readings, terminated the owned process group, and stopped progression. Offline revalidation found a complete correct CSV, but **does not undo the safety failure or qualify that command**. Metrics and CSV can finish before teardown; there are no phase timestamps to locate the thermal trip precisely relative to timing/export/teardown. No retries, replacement or stock launch occurred.

The quality executable printed diagnostic T16 QPS3217.90,mean4847.57µs,trueP99.9=115124µs,meanIO106.92; T8 printed3607.65,2160.41µs,P99.9=3320µs,meanIO106.89. These are **not headline stock measurements or a valid paired comparison**. The quality executable has post-timer export and a distinct hash. Do not project these timings onto the preserved stock executable or infer a bottleneck.

Minimum sampled available RAM12.40GiB, disk110.69GiB; swap626,688bytes, no growth. Sensor/watchdog remained functional. Package99°C once/97°C for10s cutoffs, critical-trip guard, native unbound environment and all RAM/disk/AC guards were preserved. A single T16 success provided no guarantee that T8 or later commands would be safe.

Observer:15 T16/14 T8 samples. Maximum collection wall0.14186/0.03109s, summed collector selfCPU0.49193/0.33958s, maximum scheduled-sample lateness0.000851/0.001217s. These cover process lifetime including load, twoL200 warmups, L100 search, export and teardown. Collection duration is **not measured ANN overhead**. One-hertz sampling can miss peaks; precise search-phase CPU utilization, NVMe IOPS/await and a new overhead equivalence result remain NOT_MEASURED. Prior monitor characterization remains scoped to its original archive.

## Integrity and source contract

- PAPER_STOCK: `d18dcd16fece1c9d1dea356d783ebba2ed649e54`, untouched.
- PAPER_GCC13_PORTABLE: `c4cd32c6816c063f56ecc64f9d7b63c909202cab`, tree `23fbb256528c67454cd4348bc58dfee700dffa06`; existing AVX2 reduction patch only, no new C++ changes.
- Stock binary SHA256 `5f5fa8d99cc83b523c71b7025e5f0b9aa61f45d42816804ed6d88755ebaa310b`.
- Quality binary SHA256 `0beb63e0536a3ea3198c710345f27be9970a482edcf532ed70f53f399a19c497`; same preserved library, separate post-timer export driver.
- Native INDEX_PACKAGE `7140a47ac53b0480752059b5cb428b4d56dc627533974803b5ae4413827a7470`; INPUT_PACKAGE `47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3`.

Nine-component full pre/post audits and independent re-audit passed; modern index full audit passed. All subject worktrees remained clean. Previously sealed210-file PR28 archive and57-file full-fan archive reverified without modification. PR28 fact remains18 stock native exits0, **0/18 certified**, not replaced by this campaign.

Verified paper source at the portable commit: `tests/search_disk_index.cpp:140` dynamic OpenMP query loop; `:186` search wall timer end; `:196`0.999 percentile; `:226` two fullL200 warmups. `src/v2/pipe_search.cpp:127` visited suppression, `:139` PQ admission distance, `:171` initial dynamic width4, `:178` memory initialization, `:210` FIFO push, `:228` FIFO pop, `:263` exact distance/expansion. ConfiguredW32 is not measured actual/time-weightedW. Printed hops0 is not a validated expansion count.

## Derived statistics: oracle disagreement

Reused sealed real-graph surrogate rows:48 queries,96 states,1,152 candidates, original28/10/10 whole-query partitions. No fabricated rows or new graph construction. Target is saved normalized reduction of the sum of current top10 exact squared-L2 distances after fixed-state one-step neighbor revelation. No GT enters features/policy. This is **not PipeANN/PQ replay**.

Beneficial disagreement means oracle-bestGk exceeds nearest-choiceGk by more than numerical1e−12; ties prefer nearest distance then lowest node ID. The epsilon is numerical tie handling, not an effect threshold. Statistics average within query, then bootstrap whole queries20,000times using NumPy PCG64 seed20261029, linear percentileCI90. This measures sampled-state uncertainty, not all10M workload generalization.

|Partition|Queries|Disagreement fraction(CI90)|Mean oracle gap(CI90)|Top query share of gap|Top5 share|
|---|---:|---|---|---:|---:|
|All|48|0.500[0.4271,0.5729]|0.008209[0.006370,0.010168]|8.28%|30.33%|
|Validation|10|0.700[0.600,0.850]|0.010275[0.006889,0.013586]|20.39%|75.72%|
|Reused test|10|0.400[0.200,0.600]|0.004185[0.001444,0.007337]|40.20%|98.05%|

38/48 queries have some positive gap;6/10 test queries do. Test gap is strongly concentrated. Original test results were already inspected in PR28: this is **reused held-out validation, not an untouched prospective test**. No post-observation feature/regularization tuning was performed.

Post-execution descriptive [strata](../../results/issue29_20261013/STRATA.json): step8 disagreement75%,step24 25%; step8 contributes93.08% of total gap. These are surrogate expansion steps, not measured ANN startup/steady-state phases. Beneficial oracle ranks span2–12; median normalized-distance penalty0.08581. No duration or QPS saving follows from a utility gap.

## Fixed feature test: predictions changed, utility did not improve

Models/regularization/features/controls were frozen before fitting this audit: train-only standardization, ridge1e−3, no validation/test selection. Distance-only; distance+degree/rank/history; fixed cheap nonlinear margin interactions; negative control permuting training labels within each state. All candidate decisions are evaluated, not only correlation or regression error.

|Model|Validation query-mean gain|Test choices changed/20|Test query-mean gain(CI90)|Test RMSE|
|---|---:|---:|---|---:|
|Distance only|0|0|0[0,0]|0.032409|
|Degree/rank/history|−0.004543|4|0[0,0]|0.032579|
|Cheap margin interactions|−0.0000273|7|−0.0001224[−0.0003672,0]|0.031369|
|Permuted training labels|−0.007423|18|−0.014774[−0.029764,−0.001995]|0.033067|

Margin model improves test RMSE but worsens selected utility: a concrete falsifier of “better regression error implies better exploration policy.” Changed candidates with equal zeroGk are not useful gains. No model meets the predeclared requirement of changed choices **and positive lower query-cluster gain CI in both validation and reused test**. Even a pass would justify fresh-query replication, not online integration. Prior exact Jaccard placement remains NO-GO; it was not re-tuned here.

## Feature timing and cost contract

These are analytical operation/byte counts, **not measured CPU nanoseconds or measured SSD latency**. “Available in surrogate” does not establish identical native information.

|Feature|Before expansion?|CPU / SSD / memory cost|Native caveat|
|---|---|---|---|
|Distance, rank|Yes in saved exact-distance frontier|Stored scalar; rank already sorted; O(1) read|Native admission is generallyPQ; initial memory entries use another path. Exact unread-candidate distance and normalization threshold are not free/native-equivalent|
|Nearest/second margin, squared/rank/phase interactions|Yes from maintained surrogate frontier|Two scalar reads, O(1) arithmetic/candidate; no additional SSD under that contract|Native eligible frontier and PQ normalization must first be proved; no logging-only scan or extra selector call authorized|
|Degree|Constant64 in these sampled rows|Constant adds no signal; optional4bytes/node=40MB at10M|Actual unread degree requires disk row unless metadata is stored; globalR bound alone is not actual per-node degree|
|Seen count, step/history|Yes when maintained at existing mutations|O(1) counters/query, a few numeric words; no extra SSD|Surrogate and native admission/expansion transitions differ; values not interchangeable|
|Prior useful discoveries per candidate|UNKNOWN before reading it|Requires legitimate history, missing from these saved fields|Saved `novel/useful/Gk/batch_marginal` are post-expansion labels, explicitly excluded from all feature matrices|
|Exact adjacency overlap|No for an unread candidate without paying|Read candidate/anchor adjacency, O(64) set work; random sector4KiB;4byte/640M directed edges=2.56GB precomputed feature alone|Not a free motif signal; zero tested selection gain|

No inference that structural graph dependency, D1 or a proposed topology improvement explains any throughput observation.

## H-F: useful branching isolated within its limits

Real surrogate: second nearest candidate has positive *incremental* top10 utility in34/96 states. Mean within-query incrementalGk0.006187,CI90[0.004449,0.008099]. Fixed two-expansion union uses saved first/second marginal labels, no extra graph reads. No adaptive second-step state or latency exists; cannot claim a fixed-budget win over adaptive sequential search or independent useful parallel tasks.

New controlled synthetic run:30 cases, chain/branching each31nodes, same distance scores, budget24expansions,p4, fixed sharedIO/service costs, sequential/distance-batch/random, five seeds. All realized24expansions. Branching distance batch finishes budget in66.275 simulated units vs sequential121.26, both recall1; **first useful goal arrives later**,30.605 vs20.22. Random also finishes in66.275 with recall1 in these constructed cases, with seed-dependent arrival. Chain both121.26, both recall0: equal failure is not useful positive-quality evidence. Cross-family qualities are not matched. This separates budget completion from useful discovery and refuses to turn simulated units into ANN speedups.

## Decision and bounded next step

**Improved understanding:** oracle gap is common but early-step and test-query concentrated; changing predictions/choices is insufficient; branching can complete work faster yet delay useful progress.

**Failed:** no tested cheap-feature policy gives held-out utility improvement. Thermal qualification did not support starting the stock matrix. No ANN throughput gain, complete baseline or novelty claim.

**Decision:** do not integrate raw overlap or this margin model into stock. Do not automatically build a broad observer/PQ replay. A small source-faithful replay becomes plausible only when an explicit pre-expansion feature survives fresh-query, query-cluster validation with positive utility at paid cost, or a separately scoped check shows the exact-distance oracle gap persists under nativePQ admission.

A future minimal replay contract would need immutable query/visited/retset/full_retset states, PQ table/codes, native memory-entry initialization, legitimate actual selector outcomes and deterministic publication/tie policy. Native async order cannot be reproduced from this CSV. Start with32–64 new queries,2 states and12 candidate counterfactuals, bounded1GiB process RSS;49k–98k uint8 distance labels imply roughly6–12MiB logical vector bytes but potentially192–384MiB4KiB random read traffic before overlap/cache effects. The320MBPQ payload and snapshot/adjacency overhead must be budgeted. This is a cost estimate, not measured implementation time/overhead; actual source fidelity is the main engineering risk. Require independent state-reset/lifecycle tests and disclose any deterministic-order surrogate. No implementation automatically follows this memo.

D1 UNTESTED; D4 NOT TESTED; D6 INCONCLUSIVE remain scoped to historical subjects. No FIFO/width/io_uring change, perf framework, host tuning, SIFT100M or algorithm optimization.

## Reproduce without benchmarks

See [Issue29 workflow](../ISSUE29_WORKFLOW.md). Both existing and newly created dependency-only virtualenvs passed451 tests at delivery. Tests include the first/second qualification failure, hot preflight with no invocation, full fake36-stock orchestration, late quality failure preserving12 provisional stock records, deterministic clustered bootstrap, query split rejection, label-free features and matched-quality flags. Initial fake-fixture missing CSV failures were retained and corrected in tests; they were not real ANN attempts. Delivery also makes the command-line wrapper return nonzero on a stopped campaign; this post-execution CLI-only correction does not alter the sealed execution code, its recorded commit, or evidence.
