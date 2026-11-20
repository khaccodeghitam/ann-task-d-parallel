# H3 overlap signal screening — kết quả nghiên cứu nhỏ

Ngày: **2026-11-20**. **Quyết định: NO-GO cho prototype seed-neighborhood-overlap scheduling đang xét, đặc biệt signature-128/quartet.** Có signal topology để giải thích công thực, nhưng cách xấp xỉ rẻ không vượt degree/load-aware hoặc placebo; phần cải thiện riêng của exact overlap sau eligible-load rất nhỏ. Chưa có cơ sở xây H3 online từ thiết kế này. Quyết định có phạm vi A3, p=2, S=16, baseline B1+A1 và panel dưới đây; không bác bỏ mọi phương pháp topology hay scheduling nhiều bước.

**Không có assignment mới nào được thực thi trong search.** ANN luôn dùng flat merge + fixed S16 + B1+A1 + round-robin. Các assignment khác chỉ chạy trên snapshot offline. Không dùng test để chọn policy; không dùng i5-14600KF; không dựng R4/R5; không thay search semantics hoặc protocol gate; H3 không được nâng PASS.

## 1. Preflight, freeze và danh tính

Đã đọc đầy đủ [novelty audit](H3_NOVELTY_AND_PRIOR_ART_AUDIT.md), [screening plan](H3_OVERLAP_SIGNAL_SCREENING_PLAN.md), [R4/R5 review](TASK_A_R4_R5_FEASIBILITY_REVIEW.md), Research Philosophy và Start Here. Git đầu lượt có năm tài liệu untracked, không có tracked modification. Ba tài liệu H3 được bảo toàn nguyên byte bằng commit riêng **`1d383897669b9b2445bcb9d6409c34ddffb9709f`**. Hai tài liệu post-replication/preregistration B1+A1 có sẵn vẫn giữ nguyên, không nhập vào commit đó.

Freeze Stage D/E `87d4a814...`, freeze B1+A1 `f2cd634b...`, narrow report `40bb7c54...` và các tag vẫn nguyên. Kiểm lại **23/23** file pins của narrow freeze và SHA cả ba A3 graph; không sửa evaluator lịch sử, input, index, raw hay preregistration cũ. Baseline khoa học vẫn là flat + fixed S + B1+A1 trong phạm vi đã biết; narrow replication giữ HOLD.

| Subject | Danh tính |
| --- | --- |
| Host duy nhất | `thinhbui-linux`, AMD Ryzen 5 PRO 4650U; ANN workers CPU 0/2, jobs=1 |
| Graph A3-R1, beam 970 | `0fff20ec47502c675c4905787d319390e49fa5bee856ac16c814c74697c5fbb2` |
| Graph A3-R2, beam 986 | `3d6113e721fa26c8a82f77d2e5bcbc60b6e55352532814694afb146c9c5f9c6c` |
| Graph A3-R3, beam 966 | `11f7a5059af309db0a08c4a9e0484d194c8ea5c6f17d8c8f9f67ceb299d85829` |
| Frozen Release evaluator | `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1` |
| New trace evaluator | `4903d4262876eb928b4a61c5461d306bdfd94337b830505d4a9f75c8c094887c` |
| Offline native cost executable | `dba81a04d66eb151738dd42c05285fa6c59fa4ffcebd2c533e6b9139f0d46687` |
| Package manifest V3 | `9094fb348269918077b37e901b887eae7ac1662c74a45aa43a237cd227e57d16` |
| Panel 64 IDs | `a19636b81c0b1197184cf1395f1decd50bd800993435d5e272c9805e5cb93545` |

Source, binary, input/graph/panel, guard and protocol identities are in [capture freeze](../../../../artifact-evidence/h3-overlap-screening-20261120/frozen_capture.json) and [final identities](../../../../artifact-evidence/h3-overlap-screening-20261120/final_identities.json). New builds use the common CMake Release recipe (GCC, C++17, `-O3 -DNDEBUG`, no added `-march=native`/fast-math). New build directories are separate from both frozen Release and sanitizer builds.

Raw bundle: **144 files, 155.248.611 byte including manifest**, outside Git. [BUNDLE.sha256](../../../../artifact-evidence/h3-overlap-screening-20261120/BUNDLE.sha256) has SHA-256 **`fb6b1c81dee38ed78eb5de23f589668638097faf60e4d395f6e6cc5f67ac8f15`**. No slow/failed observation was removed. Source and new executables are archived there; capture-time CMake bytes match their frozen hash. Final CMake adds the offline cost target after capture; engine/evaluator bytes used for capture are unchanged.

## 2. Design and correctness gate

Panel selection followed the plan: sort `val_10k` IDs by SHA-256 bytes of ASCII `task-d-h3-overlap-screen-v1/<decimal-ID>`, tie by ID, take first **64**. First 32 development, last 32 screening; same IDs/order on all graphs, locked before capture. R1 development data train the small predictive check; R2/R3 held-panel results test transfer. This is exploratory validation, not unseen test.

Each graph ran one frozen OFF process, one new trace-binary OFF, one counters ON without capture, and one trace ON: **12 processes total**, each with the same 100 validation warmups and 64 measured queries. The fixed order supports parity/observer characterization; it is not a balanced replicated latency experiment. No repeats were added after looking at timing.

Trace is compile-time isolated by `TASK_DA_ROUND_TRACE` in a separate target. The default target has no round-record code. Runtime capture is accepted only for p2/S16/flat/B1+A1, degree≤64 and ON counters. It reads seeds/settled before release, appends `(parent, neighbor)` L2 events and expanded IDs into reserved worker-private buffers, and copies records only after all workers finish. It does not change queues, visited publication, ties, seed selection, assignment or S. Maximum 128 rounds/query; degree/S bounds keep stored trace below the conservative 8 MiB/query budget. Overflow stops recording while search finishes, tested on a synthetic long chain.

For simplicity the implemented snapshot stores eligible neighbor IDs, not the planned packed visited mask; raw adjacency is read from the immutable graph offline. This is a bounded observer cost, not a proposed online estimator. All **192 trace queries and 6.095 rounds** completed; maximum 33 rounds/query, no overflow or censored query. Offline reconstruction from entry fanout plus prior rounds' evaluated/expanded IDs reproduced every eligible list exactly.

Correctness results:

- All four modes match ordered top-10 IDs and squared L2 on every query, for each graph. Counters ON/trace match every non-time counter, including per-worker work, expansions and rounds. Actual online dispatch is always `rank % 2`.
- Reconstructed L2 events plus serial entry work equal total evaluations; per-round cross-worker intersections equal all query duplicate counters. No L2 ID repeats inside one worker/round.
- Independent float64 distance checks pass **1.920/1.920** returned distances, max absolute error `7,78e-16`. Descriptive Recall@10 on 64 queries is R1/R2 0,990625, R3 0,993750. Sample SE is about 0,0043/0,0043/0,0030: this small panel does not certify a new recall floor. Historical beams remain unchanged.
- Release CTest and native ASan+UBSan+LSan suites pass the common contracts and four new overlap/trace tests. Dataset-free suite: **520 tests, 507 pass, 13 skip**; native integrations remain opt-in. Initial sanitizer attempts under the sandbox failed because LeakSanitizer cannot operate under ptrace; native rerun passed without disabling leak checks. Those logs are retained.

Capture used the sealed Ryzen thermal/AC/RAM/disk guard plus heartbeat watchdog and the existing sequential lock, in the native PID namespace. All **12/12** evaluator exits were 0, guard failures 0, **60 host samples**, Tctl **64,625–84,5°C**. Three later offline replay processes were also sequential and guarded. No fan/power/security/system-affinity change was made. [Capture checks](../../../../artifact-evidence/h3-overlap-screening-20261120/capture_checks.json), [guarded commands and raw](../../../../artifact-evidence/h3-overlap-screening-20261120/A3_r1/trace_on/manifest.json).

## 3. Observed mechanism: phần duplicate nào nằm ở seed?

All 64 queries/graph, observed RR trace; means per query. “Seed” means a parent belongs to that round's originally dispatched seed set; this is a local parent classification, not an ancestral causal proof.

| Graph | Rounds | Total L2/query | Duplicate L2/query (% total) | Seed–seed | Seed–emergent | Emergent–emergent |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A3-R1 | 2.024 | 26.753,0 | 712,11 (2,662%) | 88,59 | 53,27 | 570,25 |
| A3-R2 | 2.053 | 27.114,6 | 662,25 (2,442%) | 88,72 | 53,06 | 520,47 |
| A3-R3 | 2.018 | 26.671,8 | 691,09 (2,591%) | 87,72 | 50,53 | 552,84 |

About **79–80%** of residual duplicates are emergent–emergent; **12,4–13,4%** are seed–seed. The latter correspond to only **0,327–0,331% of all L2** on these paths. Removing them alone cannot justify a large total-work claim. This is not a hard bound for a policy that changes future paths, because new paths/rounds/Recall can also change.

Only **75,3–75,7%** of dispatched seeds are actually popped in their round: newly discovered candidates consume part of S. Consequently, evaluating all original seeds' one-hop union is an imperfect counterfactual. It cannot be labeled the new algorithm's actual work.

An ownership oracle on **all observed duplicate events**, allowing each repeated distance to be assigned freely while preserving observed paths, could save about **469–483 critical-worker L2/query**, around 3,3–3,4% of `sum_round max_worker_L2`. This is an optimistic work bound with no claim of realizable ownership or latency savings. The seed-only policy cannot simply claim this whole budget.

## 4. Offline assignment comparison

Every policy receives exactly the same ordered seed set and beginning-of-round eligible sets `E(s) = N_out(s) \ settled`. Rank-pair constraints keep one seed per pair per worker; tails use RR. Objective metrics are whole-round unions:

```text
U_w = union of E(s) assigned to w
D_seed = |U_0 intersection U_1|
M_seed = max(|U_0|, |U_1|)
query proxy gain = 100 * (1 - sum_round M_policy / sum_round M_RR)
```

Degree balances cumulative raw degree. Eligible-load balances `|E(s)|` without overlap. Exact quartet replaces the planned bit count by exact local union cardinality; exact accumulated is greedy marginal union over all seeds already assigned in that round. **Neither heuristic is called an exact global oracle.** Signature uses the preregistered 128-bit raw-adjacency occupancy sketch, first SHA digest byte's low 7 bits, with fixed salt. Placebo rotates signatures among observed seed IDs of identical raw degree, ordered by fixed hash; it controls degree and sketch cost within this observed seed pool, not an independently drawn graph-wide permutation.

Held **32 queries/graph**, paired query bootstrap CI95, 4.000 resamples with fixed RNG. These are uncertainty intervals for an offline proxy conditional on each graph/panel; they are not ANN speedup intervals or independent graph-seed inference.

| Assignment | R1 proxy gain % [CI95] | R2 | R3 |
| --- | --- | --- | --- |
| RR | 0 | 0 | 0 |
| Degree/load | 1,78 [1,42; 2,14] | 1,63 [1,30; 2,00] | 1,72 [1,39; 2,06] |
| Eligible-load | 3,85 [3,42; 4,29] | 3,70 [3,31; 4,14] | 3,76 [3,37; 4,14] |
| Exact quartet | 1,89 [1,61; 2,17] | 1,86 [1,60; 2,16] | 2,03 [1,76; 2,30] |
| Exact accumulated greedy | 3,95 [3,52; 4,39] | 3,81 [3,42; 4,26] | 3,87 [3,48; 4,26] |
| Signature-128 quartet | 0,83 [0,55; 1,10] | 0,62 [0,37; 0,89] | 0,62 [0,36; 0,89] |
| Degree-stratified placebo | 0,75 [0,42; 1,07] | 0,68 [0,40; 0,98] | 0,80 [0,52; 1,10] |

Exact accumulated improves only **0,106 / 0,120 / 0,114%** over eligible-load, with CI95 approximately [0,085;0,127], [0,096;0,145], [0,098;0,130]. Most of its apparent advantage over raw-degree balancing comes from knowing which neighbors are already visited, not from overlap itself.

Signature versus degree is **−0,97 / −1,03 / −1,12%**. Signature versus placebo is **+0,073 [−0,120;0,279] / −0,064 [−0,264;0,150] / −0,184 [−0,382;−0,006]%**. The cheap sketch does not demonstrate the topology-specific advantage required by the plan.

Negative rounds were retained. Signature makes M worse than RR in **824/2.024**, **859/2.053**, **844/2.018** rounds. Exact quartet also worsens **615/649/610** rounds, despite optimizing its local quartet objective. This exposes cross-quartet interactions; minimizing local overlap is not equivalent to minimizing whole-round critical work.

For a genuine oracle check, exhaustively enumerated all rank-pair orientations on **eight predetermined round-position quantiles per graph** (≤32 seeds, worker symmetry only when valid). Average sampled-round maximum possible M reduction is **4,09 / 5,92 / 4,75%**; individual rounds range from 0 to 14,98%. These are upper bounds on this one-hop objective **for those 24 snapshots only**, not a whole-query or whole-study upper bound. Python enumeration costs about 0,14–0,16 s at 32 seeds; it is an offline ceiling check, not an online design.

Full positive/negative records: [round metrics](../../../../artifact-evidence/h3-overlap-screening-20261120/offline_analysis/round_metrics.csv), [query metrics](../../../../artifact-evidence/h3-overlap-screening-20261120/offline_analysis/query_metrics.csv), [oracle records](../../../../artifact-evidence/h3-overlap-screening-20261120/offline_analysis/oracle.csv).

## 5. Overlap dự báo được gì?

Held-panel Spearman associations on RR snapshots:

| Predictor → outcome | R1 | R2 | R3 |
| --- | ---: | ---: | ---: |
| D_seed → actual duplicate L2 | 0,806 | 0,797 | 0,801 |
| D_seed → max worker processing time ON | 0,455 | 0,428 | 0,449 |
| D_seed → summed barrier wait ON | 0,102 | 0,097 | 0,106 |
| M_seed → actual maximum worker L2 | 0,935 | 0,942 | 0,928 |

A small OLS diagnostic trained only on R1 development uses raw degree, eligible degree, seed count, round index and visited fraction. Adding exact D_seed/M_seed reduces held MAE for duplicate work from **27,30→24,08 / 25,66→22,59 / 24,53→21,22 L2/round**. Maximum-worker-L2 MAE falls **29,52→26,79 / 29,43→26,69 / 29,31→27,36**. ON max-worker-time MAE falls about 18–19 µs to 16–17 µs; barrier/round-time errors also fall, but substantial residual remains.

This is a useful positive diagnostic signal. It is not causal identification: graph region, phase, visited coverage and emergent paths co-vary. Exact overlap is expensive information; the result does not establish that signature-128 captures it. Round rows are dependent within queries, and no round-level p-value is offered as graph replication. Full model errors are in [analysis.json](../../../../artifact-evidence/h3-overlap-screening-20261120/offline_analysis/analysis.json).

## 6. Runtime cost and sensitivity analysis

Actual query latency measured only for **RR**, mean µs/query; one process/mode, descriptive:

| Mode | R1 | R2 | R3 |
| --- | ---: | ---: | ---: |
| Frozen OFF | 5.224,96 | 5.299,82 | 5.228,03 |
| Trace binary OFF, capture disabled | 5.016,15 | 5.237,74 | 5.116,30 |
| Counters ON, capture disabled | 5.579,87 | 5.720,93 | 5.462,76 |
| Trace ON | 6.294,18 | 6.375,20 | 6.217,37 |

The ordered unreplicated modes cannot establish a code speedup. Trace adds **11,44–13,81%** relative to counters ON in these processes. Direct timestamp windows show eligible-snapshot preparation about **793–819 µs/query** and post-arrival record copying **191–196 µs/query**. These windows include allocation/copy/read costs; append overhead and cache perturbation also exist. Their sum need not equal the process-level difference. Do not subtract these numbers from ON timing to invent OFF round latency. Summed worker barrier-wait is not wall time and is not added again to round wall.

The separate native replay has **no graph search**. It checks decisions against the Python implementation, then replays the observed seed IDs with a 16.000.000-byte signature table. Signature generation, input parsing and table construction are outside kernel timing; table entries used by the observed panel are populated. It measures a mostly warm steady replay, not full cold-sidecar behavior or deployment cost. The executable uses generic Release flags; native POPCNT specialization was not added. Replay is unpinned within the Ryzen's allowed CPUs, unlike the ANN worker mapping; absolute costs remain descriptive.

| Native offline kernel | R1 | R2 | R3 |
| --- | ---: | ---: | ---: |
| Degree, ns/round | 159,7 | 152,3 | 158,2 |
| Signature, ns/round | 939,9 | 896,2 | 902,7 |
| Degree, µs/query | 5,05 | 4,89 | 4,99 |
| Signature, µs/query | 29,72 | 28,75 | 28,46 |

Signature footprint is 15,26 MiB payload/graph, plus headers/scratch; a deployable sidecar requires one graph-edge pass and its own hash/build/amortization accounting. No full sidecar was built. RR's seed payload is at most 512 signature bytes/round, potentially 32 separate cache-line loads. Exact eligible lists require up to 2.048 arc/visited checks before dispatch; current capture shows that collecting this information naively is far from the 1%-of-OFF budget (~52–53 µs/query). The observer is not asserted to be the fastest possible exact estimator.

For sensitivity only, convert saved seed M into time using each query's observed `sum max(worker_ns) / sum max(worker_L2)` and subtract native signature replay cost. This assumes one-hop saved work transfers to the critical path at the observed average cost. It is **not an empirically validated counterfactual latency model**; it mixes instrumented cost with a proxy, and its CI excludes model uncertainty.

| Held panel | R1 | R2 | R3 |
| --- | ---: | ---: | ---: |
| Gross time-equivalent saving, µs/query | 35,37 | 27,96 | 27,08 |
| Native signature cost, µs/query | 30,16 | 29,26 | 29,21 |
| Net time-equivalent, % frozen OFF [query CI95] | +0,100 [−0,118;0,305] | −0,025 [−0,234;0,202] | −0,041 [−0,252;0,173] |

Even this favorable transfer assumption is nowhere near the preregistered 5% useful-signal threshold. Signature cost is below 1% of OFF, but consumes roughly all projected gross benefit and fails the **≤20% of gross savings** budget. A faster popcount could change kernel cost; it would not repair the failed comparison with degree/placebo or establish novelty. [Cost/quality checks](../../../../artifact-evidence/h3-overlap-screening-20261120/offline_analysis/cost_quality.json), [native replay raw](../../../../artifact-evidence/h3-overlap-screening-20261120/offline_cost/A3_r2/stdout.log).

## 7. Novelty recheck

Primary sources below were accessible in this turn; conclusions are paper-level, not author-binary replications:

| Prior art | Mechanism already present | Boundary for this study |
| --- | --- | --- |
| [Speed-ANN §§4.3–4.4](https://johnpzh.github.io/assets/papers/arXiv-2022_Speed-ANN_Zhen.pdf) | Even unchecked-candidate split, local best-first paths, adaptive merge; neighbor grouping for memory locality | Its round-robin checker is not proof of a particular seed mapping. Seed-overlap dispatch not established by the sections read. |
| [iQAN §5](https://johnpzh.github.io/assets/papers/PPoPP-2023_iQAN_Zhen.CameraReady.pdf) | Staged path-wise expansion, update-position-driven synchronization, loose shared visited | Dynamic S/width and redundancy-aware sync are prior art; “redundancy” includes unpromising paths. |
| [AverSearch §§4.2–4.4](https://arxiv.org/html/2504.20461v2#S4) | Work stealing through global buffer, asynchronous roles, distance-array reuse of shared destination evaluations | Shared-distance reuse and load balancing cannot be claimed as new here. |
| [Çatalyürek–Aykanat §3, 1996 precursor](https://faculty.cc.gatech.edu/~umit/assets/pdf/Catalyurek96.pdf) | Balanced task partitioning with shared-data hyperedges; connectivity-minus-one objective | D_seed is the same connectivity objective after mapping seed→task, neighbor→hyperedge. |

The only possible distinct question remains whether a very cheap, rank-constrained, query/round-specific predictor can guide assignment under multi-step ANN budgets. This study demonstrates some exact diagnostic signal but **not** the required cheap predictor or an algorithmic contribution beyond constrained partitioning. Combining sketches, load balance and swaps is insufficient novelty. Exact author artifact equivalence and exhaustive absence of related online overlap schedulers remain **UNVERIFIED**; no novelty claim is made.

## 8. Decision and limits

**NO-GO for implementing the current overlap-aware H3 candidate.** This follows the plan's scoped negative criteria: signature does not beat placebo/degree on held R2/R3, the topology-specific exact increment over eligible-load is ~0,1%, and estimated useful savings do not clear the cost/5% requirements. A positive diagnostic correlation is preserved as a finding; it does not rescue the scheduling proposal.

Important limits: 64 validation queries/graph, 32 held; one RR process per mode; only p2/S16/A3; same historical RNG root 555 across R1–R3; query and host conditions shared; trace perturbs runtime/cache; oracle covers 24 snapshots only; no changed-path Recall/latency measured. These prevent universal claims about graph ANN scheduling or real speedup. More data on the same proxy alone would not address the missing cheap topology-specific mechanism. A substantially different multi-step mechanism would need a new design review before implementation.

Original TP-CG remains **PIVOT**. H3 remains **NOT_OPENED**, not PASS. Historical P0 / Full P1 / t0998 **HOLD**; Protocol V4 D1–D5 **UNAPPROVED**; P3 Official **CLOSED**. D1 **UNTESTED**, D4 **NOT TESTED**, D6 **INCONCLUSIVE** on their historical subjects; PAPER_STOCK / PAPER_GCC13_PORTABLE / MODERN_GOLDEN and H-V/H-G/H-C/H-F/H-QV retain separate scopes. R4/R5 remains **OWNER DECISION REQUIRED**, not created.

Code for review: [trace records](../../../research/task_da/search_common/p2_round_trace.hpp), [common engine hooks](../../../research/task_da/search_common/p2_engine.hpp), [capture runner](../../../research/task_da/run_h3_overlap_screen.py), [offline policies](../../../research/task_da/h3_overlap.py), [analyzer](../../../research/task_da/analyze_h3_overlap.py), [cost kernel](../../../research/task_da/h3_assignment_cost.cpp), [validation](../../../research/task_da/finish_h3_overlap.py), [synthetic tests](../../../tests/research/test_h3_overlap.py). The source-only changes and this report remain reviewable in the working tree; the three prior reports were committed separately as requested.
