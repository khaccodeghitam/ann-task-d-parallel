# G0 SIFT10M causal baseline — E0 stopped

**E0 INCONCLUSIVE; D6_INCONCLUSIVE; D1 observability NO.** Fifteen Stage A runs completed. Stage B LIGHT sentinels and Stage C DETAIL diagnostics were not executed because E0 did not permit proceeding. This is measurement infrastructure validation and an unresolved gate, not a research result or novelty claim.

## Bound state and frozen protocol

- Main/base and measurement harness: `8d6b20f6b1a544470bee5693a4ae9d4a34716feb` (merged Issue #6 / PR #7). The analysis commit is the commit containing this report; it was created after measurement.
- Golden subject: `b9ec4ba86ff5d70bec277984777197f28dc2cf42`, clean.
- Instrumented subject: `3bdcc064cb96aae4cd845bd2bb6adc5f5ba63e19`, clean.
- Golden binary SHA256: `a02ce69d1467727344c8620a254b4cba51d12616d3da171ef7c1a6668a9e8bc5`.
- Instrumented binary SHA256: `d51066cc5fe0cf2df71149e23910ce654dcc259ed271fea28ae7002c53a8bd18`.
- INPUT_PACKAGE SHA256: `47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3`.
- INDEX_PACKAGE SHA256: `8955f8bca0c8ebb5afbd2a69e9760fc829d22ba76a4ef7b482339e88b2489595`.
- Campaign: `G0_SIFT10M_20261008T143411326130Z`.
- Evidence directory: `/home/irthn/ann-research/research-v3/campaigns/G0_SIFT10M_20261008T143411326130Z/`.
- Exact frozen plan: [PLAN.json](plans/G0_SIFT10M_20261008T143411326130Z.json), [PLAN.md](plans/G0_SIFT10M_20261008T143411326130Z.md). Frozen 2026-10-08 14:38:04.565025 UTC; JSON SHA256 `88d4e9fadfa212a83220e231717ab55aa21b913cff0fe492e2203ea77a692b2e`.

Issue #8 was read completely before changes/measurement; it had no comments. Requested P0/SIFT10M documents and both subject trees were inspected. Neither ANN repository was modified. Search used the explicit `pipeann-b9ec4ba` profile: uint8, T8/W32, K10/L100/mem_L0, pq, l2, mode2, same 10K queries and package bindings. Every run requested local MLflow. STOCK used the golden binary without causal tracing; instrumented OFF/LIGHT required causal tracing.

The exact Stage A order was: R1 STOCK/OFF/LIGHT; R2 OFF/LIGHT/STOCK; R3 LIGHT/STOCK/OFF; R4 STOCK/LIGHT/OFF; R5 LIGHT/OFF/STOCK. Two seconds separated finalized harness invocations. No cache flush, affinity/governor/scheduler change or sudo tuning was performed. Shared environment: OMP_NUM_THREADS=8, MKL_NUM_THREADS=8, LC_ALL=C, S_TIME_FORMAT=ISO, OMP_PROC_BIND/OMP_PLACES unset.

Planned but gated: B = five cyclic repetitions of T1/W32, T8/W32, T8/W64, T16/W32, T16/W16; C = three repetitions of those configurations with DETAIL first-N=16. Capacity 65536 events/worker was decided before any measurement (about 272 MiB at T16). It remained fixed. No DETAIL capacity change or failed DETAIL run occurred because C never started.

## Immutable package audits and evidence integrity

Both pre- and post-campaign commands were executed with full components, not merely manifest digests:

```bash
.venv-research/bin/python tools/research/package_manifest.py verify ~/ann-research/data/bigann/sift10m/manifests/INPUT_PACKAGE.json --full-components
.venv-research/bin/python tools/research/package_manifest.py verify ~/ann-research/indexes/sift10m/INDEX_PACKAGE.json --full-components
```

Exact absolute argv, UTC start/end, duration, stdout/stderr, exit code and manifest digest are in `pre_*.audit.json` / `post_*.audit.json` and adjacent logs. All four audits returned 0 and matched the frozen digests. Post audits completed before final analysis.

| Audit | UTC start | UTC end | Seconds | Result |
| --- | --- | --- | ---: | --- |
| pre_input | 2026-10-08T14:35:13.082460+00:00 | 2026-10-08T14:35:14.048858+00:00 | 0.966449 | PASS |
| pre_index | 2026-10-08T14:35:14.049106+00:00 | 2026-10-08T14:35:17.664222+00:00 | 3.615198 | PASS |
| post_input | 2026-10-08T14:43:25.524447+00:00 | 2026-10-08T14:43:26.326406+00:00 | 0.801961 | PASS |
| post_index | 2026-10-08T14:43:26.326632+00:00 | 2026-10-08T14:43:28.886388+00:00 | 2.559763 | PASS |

`INTEGRITY.json` records 170 run artifact files checked against SHA256SUMS, 401 pre-existing artifact files unchanged, unchanged subject commits/binary hashes/size/mtime, and unchanged frozen plan. No dataset/index repair, chmod, rebuild or redownload occurred. Old SIFT1M/SIFT10M evidence was preserved. Each of the 15 MLflow mirrors was independently read back as FINISHED with matching package digests, subject/harness commits, T/W/L/K, trace mode, status and trace-validity tags (`MLFLOW_INTEGRITY.json`). MLflow was not used for scientific analysis. No events, raw trace or telemetry were uploaded by the mirror.

## Stage A measurements

All five values are in repetition order. Latencies are microseconds, recall is percent, mean I/O is benchmark I/O/query. SD is sample SD (n−1). Each run is an observation; no request-level independent-experiment inference, bootstrap or p-values are used.

| Case | Metric | Five values | Mean | Median | Min | Max | Sample SD |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| A/STOCK | qps | 4858.61, 4981.65, 4991.15, 4942.84, 4826.44 | 4920.1380 | 4942.8400 | 4826.4400 | 4991.1500 | 74.0048 |
| A/STOCK | mean_latency_us | 1637.58, 1594.02, 1591.93, 1606.41, 1646.4 | 1615.2680 | 1606.4100 | 1591.9300 | 1646.4000 | 25.2073 |
| A/STOCK | p99_latency_us | 4621, 2127, 2115, 2366, 4650 | 3175.8000 | 2366.0000 | 2115.0000 | 4650.0000 | 1336.3124 |
| A/STOCK | recall | 99.14, 99.14, 99.14, 99.14, 99.14 | 99.1400 | 99.1400 | 99.1400 | 99.1400 | 0.0000 |
| A/STOCK | mean_ios | 123.07, 123, 122.98, 123.03, 123.09 | 123.0340 | 123.0300 | 122.9800 | 123.0900 | 0.0462 |
| A/OFF | qps | 4999.61, 4979.56, 5003.31, 4992.68, 4985.43 | 4992.1180 | 4992.6800 | 4979.5600 | 5003.3100 | 9.7997 |
| A/OFF | mean_latency_us | 1589.27, 1594.19, 1589.13, 1592.56, 1592.7 | 1591.5700 | 1592.5600 | 1589.1300 | 1594.1900 | 2.2564 |
| A/OFF | p99_latency_us | 2089, 2138, 2093, 2182, 2114 | 2123.2000 | 2114.0000 | 2089.0000 | 2182.0000 | 38.2191 |
| A/OFF | recall | 99.14, 99.13, 99.15, 99.13, 99.13 | 99.1360 | 99.1300 | 99.1300 | 99.1500 | 0.0089 |
| A/OFF | mean_ios | 122.93, 123.03, 123, 123.01, 123.03 | 123.0000 | 123.0100 | 122.9300 | 123.0300 | 0.0412 |
| A/LIGHT | qps | 4817.92, 4988, 4979.19, 4962.03, 4978.04 | 4945.0360 | 4978.0400 | 4817.9200 | 4988.0000 | 71.6745 |
| A/LIGHT | mean_latency_us | 1648.53, 1590.55, 1593.03, 1598.11, 1593.07 | 1604.6580 | 1593.0700 | 1590.5500 | 1648.5300 | 24.6787 |
| A/LIGHT | p99_latency_us | 4621, 2102, 2128, 2382, 2126 | 2671.8000 | 2128.0000 | 2102.0000 | 4621.0000 | 1095.6337 |
| A/LIGHT | recall | 99.13, 99.12, 99.14, 99.12, 99.14 | 99.1300 | 99.1300 | 99.1200 | 99.1400 | 0.0100 |
| A/LIGHT | mean_ios | 123.07, 123, 123.01, 123.01, 123 | 123.0180 | 123.0100 | 123.0000 | 123.0700 | 0.0295 |

### Predeclared E0 decision

Absolute median QPS and mean-latency perturbation limits: OFF vs STOCK ≤3%; LIGHT vs OFF ≤5%. Natural spread uses 100×(max−min)/median and is inconclusive when at least the comparator margin. Required benchmark/trace validity is mandatory. The preflight also fixed a recall spread consistency guard of ≤0.02 percentage points; Issue #8 did not specify that numeric recall guard, so it is an additional conservative predeclared choice, not a post-result relaxation.

| Comparison | Median QPS delta | Median mean-latency delta | Margin |
| --- | ---: | ---: | ---: |
| OFF vs STOCK | +1.0083% | −0.8622% | 3% |
| LIGHT vs OFF | −0.2932% | +0.0320% | 5% |

| Group | QPS spread | Mean-latency spread |
| --- | ---: | ---: |
| STOCK | 3.3323% | 3.3908% |
| OFF | 0.4757% | 0.3177% |
| LIGHT | 3.4166% | 3.6395% |

**Derived decision: INCONCLUSIVE.** Median perturbations are within the performance margins, but STOCK spread exceeds the 3% comparator margin. Recall spans 99.12–99.15%, or 0.03 percentage points, exceeding the frozen recall guard. No recall/output-equivalence claim follows. All ten instrumented required traces are valid; all fifteen benchmark and overall statuses are success. OFF trace health validates the no-op protocol, not observed request histories.

The execution wrapper originally emitted `E0_GATE.json` = FAIL because its classification checked the recall guard before the frozen noise rule. That original derived file was preserved. `AMENDMENT_001_GATE_EVALUATOR.md` documents the evaluator-priority correction; `analysis_verified/E0_GATE_ANALYZED.json` applies the already frozen INCONCLUSIVE noise rule. Neither label allowed Stage B/C, so execution was unaffected. PLAN, measured data and every threshold remain unchanged. Development analysis outputs v1/v2/v3/final are retained; v1 rejected nested telemetry paths due an analyzer path-validation bug, corrected before final analysis. No finalized run failed that checksum check.

**Interpretation:** this campaign does not establish an overhead pass despite small median deltas. Large STOCK P99 variation is a measured fact; host/cache/thermal causes are unresolved. No quieter repetitions were selected or rerun.

## LIGHT counters and actual width limitations

Every LIGHT query began at actual width 4. Below are full-run counts and final-width observations, not time-weighted trajectories. LIGHT has no per-event timestamps; fractions of time at Wcap, above32 residency and width buckets require DETAIL and remain unavailable. No W64 run was executed.

| LIGHT rep | Submitted=CQE=published | Expanded | Published−expanded | Final width min/max | Queries ending at W32 | Max hidden | Max inflight |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | 1230743 | 1189740 | 41003 | 16/32 | 4628/10000 | 32 | 32 |
| 2 | 1230047 | 1189214 | 40833 | 14/32 | 4502/10000 | 32 | 32 |
| 3 | 1230104 | 1189438 | 40666 | 18/32 | 4448/10000 | 32 | 32 |
| 4 | 1230053 | 1189252 | 40801 | 18/32 | 4520/10000 | 32 | 32 |
| 5 | 1229977 | 1189123 | 40854 | 18/32 | 4575/10000 | 32 | 32 |

All LIGHT runs: events_written=0, sampled=0, events_dropped=0, ordering violations=0, unmatched submit/CQE/publish=0, negative hidden=0, outstanding_at_query_end=0, table_overflows=0. LIGHT contributes 50000 query counter rows; OFF contributes no query observations. Max hidden=32 is an aggregate observation of publication backlog, not a HOL duration or root-cause diagnosis. Request count and benchmark mean I/O/query are reported separately; inflight is not ANN logical work. Not every published node must be expanded.

## CPU, kernel and NVMe evidence

Native Linux kernel `7.0.0-38-generic`; root filesystem `/dev/nvme0n1p6`, ext4. Machine snapshots preserve readable per-policy governor/EPP/current/max frequency, thermal zones, NVMe queue attributes, free RAM/swap/storage. Policy0: powersave, balance_performance, current frequency 709621 kHz at snapshot, max 4600000 kHz; x86 package temperature 53°C. MemAvailable before: 9823036 KiB; swap total/free: 4194300/4027480 KiB. Free disk before/after: 129508433920 / 129481453568 bytes. These are snapshots, not measurements of frequency/temperature throughout each run. No settings were changed.

mpstat/pidstat/iostat were available. Raw logs remain under each LIGHT run’s `telemetry/`; normalized rows remain in `system_metrics.csv`. The following are arithmetic means of two approximately one-second samples/run, including startup/loading and partial search intervals. Short ~2.5 s processes limit resolution. STOCK/OFF have no host collectors, so there is no matched CPU/NVMe delta against them. Device-wide numbers include other workloads.

| LIGHT rep | CPU usr % | sys % | idle % | Process CPU % | Process usr % | Process sys % | Samples/series |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 36.020 | 31.180 | 32.650 | 1290.290 | 679.140 | 611.155 | 2 |
| 2 | 35.960 | 33.260 | 30.750 | 1359.500 | 699.500 | 660.000 | 2 |
| 3 | 36.475 | 33.745 | 29.730 | 1357.500 | 696.500 | 661.000 | 2 |
| 4 | 36.785 | 33.270 | 29.770 | 1352.500 | 696.500 | 656.000 | 2 |
| 5 | 37.915 | 33.665 | 28.425 | 1354.500 | 695.500 | 659.000 | 2 |

| LIGHT rep | NVMe read IOPS | Read KiB/s | r_await ms | aqu-sz | Util % |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 475528.275 | 1902158.930 | 0.070 | 34.790 | 63.055 |
| 2 | 497173.000 | 1988868.000 | 0.080 | 37.695 | 60.500 |
| 3 | 493807.855 | 1975289.030 | 0.080 | 38.100 | 64.260 |
| 4 | 493766.500 | 1975152.000 | 0.080 | 37.630 | 67.800 |
| 5 | 495074.000 | 1980344.000 | 0.080 | 37.405 | 61.700 |

Process CPU percentages use the sysstat multicore scale and can exceed 800%; they are not proof of one SQPOLL thread per worker. Source uses thread-local io_uring/SQPOLL, but **runtime SQPOLL/iou-wrk rows and fdinfo were not collected**: the representative T1/T8/T16 observer belonged to gated Stage B. Per-thread CPU and voluntary/involuntary context-switch counts are likewise unavailable in Stage A’s existing pidstat -u/-r/-d collector. This is missing measurement, not evidence that the kernel exposes no fdinfo or that SQPOLL threads do not exist. CPU sys and NVMe pressure are measured only at T8/W32; they cannot identify a T16 confound or SSD saturation.

## D6 and primary comparisons

**D6_INCONCLUSIVE: missing Stage C evidence.** No sampled request HOL p50/p95/p99/max, observed-I/O quantiles/ratios, time-weighted hidden/outstanding/unpublished state, hidden>0 or hidden≥2 fractions, or actual-width residency can be reported for G0. DETAIL checker execution and its zero-loss gate are not applicable because no G0 DETAIL run exists. Existing Issue #6 DETAIL smokes were not substituted.

Frozen D6_MATERIAL requires a ≥2× p95 HOL increase in ≥2/3 paired pathological repetitions, plus median p95 HOL ≥25% of median p95 observed I/O or hidden>0 for ≥25% query time. D6_LOW requires both pathological regimes below 10% HOL/observed and below 10% hidden time without a consistent increase. Missing evidence maps to INCONCLUSIVE, not LOW. Exact pairing/aggregation rules remain in PLAN.json.

| Required comparison | G0 result |
| --- | --- |
| T8/W32 → T8/W64 | Unmeasured; W64 actual width, HOL, hidden and performance unavailable |
| T8/W32 → T16/W32 | Unmeasured; host/kernel pressure and NVMe comparison unavailable |
| T16/W32 → T16/W16 | Unmeasured; lower-cap effect unavailable |
| T1/W32 → T8/W32 | Unmeasured; T1 baseline unavailable |

No frontier-redundancy, dependency-starvation, host-pressure causality or SSD-saturation conclusion is supported. Publication HOL is an application-level interval. **IO_SUBMIT remains after SQE preparation immediately before io_uring_submit; IO_CQE_SEEN remains when the userspace poll loop processes CQE/user_data. Their difference is userspace-observed I/O interval, never device hardware latency.** Timing hooks are unchanged.

## Analyzer, testing and next experiment

`tools/research/analyze_g0_causal.py` reads local manifests/summaries/counters/events/telemetry, validates checksums (including nested telemetry), package/provenance/search/sampling/order bindings and bracketing audits. It preserves run/query clusters and uses linear interpolated percentiles p×(n−1). Events are sorted within query by timestamp, frozen semantic rank, request/node/worker/TID, and stable payload. Tie groups contribute zero duration internally; maxima/residency use their post-group state. This convention cannot resolve sub-clock ordering. Width snapshots on non-width events are not used to invent a tied width chronology; actual WIDTH_INIT/CHANGE and QUERY_END govern it.

Reconstruction validates lifecycle, FIFO, nonnegative states, final drain and end/health counters; contradictions abort interpretation. Cache-ready paths are separate. NODE_EXPAND remains node-level; optional request expansion is not required or guessed. QUERY_START→WIDTH_INIT is unknown width; mean width is conditional on initialized duration and all residency fractions use full query duration. Per-query and run pooled request quantiles are descriptive; configuration statistics use one summary per run. No request-level pseudoreplication.

```bash
.venv-research/bin/python -m unittest discover -s tests/research -v
git diff --check
.venv-research/bin/python tools/research/analyze_g0_causal.py \
  --campaign ~/ann-research/research-v3/campaigns/G0_SIFT10M_20261008T143411326130Z \
  --output /path/to/a/new/analysis-directory
```

115 research Python tests pass (80 existing + 35 analyzer tests). Tests cover unsorted JSONL, equal timestamps, lifecycle/FIFO, negative/missing state, width residency, Wcap, optional expansion, worker/query/run clusters, HOL interpolation, cache paths, checksum containment, E0 noise priority and D6 LOW/MATERIAL/INCONCLUSIVE synthetic gates. No real SIFT data is needed for tests. Final analysis is in `analysis_verified/`; it is regenerated into a new directory, never over finalized evidence.

**D1 observability: NO.** See [D1_OBSERVABILITY_GAP.md](D1_OBSERVABILITY_GAP.md) for missing candidate eligibility/readiness/selector-null states and exact proposed source hooks. No hooks were implemented. Low inflight alone cannot distinguish dependency starvation from resource/publication/selection waits.

**Next recommended experiment (not executed):** a separate predeclared E0 revalidation after observing and documenting host-state stability and investigating recall reproducibility, retaining raw values and selecting no favorable repeats. The present 3%/5% thresholds and frozen recall guard stay intact for this campaign. Any future protocol choice must be explicit before data. Stage B/C and hypothesis tests require a valid new proceed decision.

No ANN source modification, FIFO modification, width-policy modification, D1/D4 implementation, graph/candidate/io_uring change, index rebuild, SIFT100M, or novelty claim. No large artifacts are committed; main remains untouched.

## Run / MLflow inventory

Each local directory is `~/ann-research/research-v3/runs/<run_id>/`; `executions/<stage>_R<rep>_<case>/command.sh` preserves the exact harness invocation. All below have benchmark_status=success, run_status=success, exit_code=0, mlflow_status=success. STOCK trace_valid=null; instrumented OFF/LIGHT trace_valid=true.

| Execution order | Case/rep | Run ID | MLflow ID |
| ---: | --- | --- | --- |
| 1 | STOCK/1 | `P0_sift10m_T8_W32_OFF_R001_20261008T143942269705Z_cccebcb53d5142678cc13ab5e01985c9` | `4337a6031ea940e995ec99c51f01f223` |
| 2 | OFF/1 | `P0_sift10m_T8_W32_OFF_R001_20261008T143948810825Z_d6168c6de47b4d99bdf3a85ee303e8ca` | `e13fafc2d9e44931ab9759a0e9a8611a` |
| 3 | LIGHT/1 | `P0_sift10m_T8_W32_LIGHT_R001_20261008T143955339746Z_d98bd1ba7c8349f8a3061fa9bc8ee247` | `0cb8f34ac4684b9ca21e60e153dbfd5b` |
| 4 | OFF/2 | `P0_sift10m_T8_W32_OFF_R002_20261008T144002020827Z_9a47e62c7734408288dac43baf382f42` | `89d2afb4c7914805b8b2a2def5b4a2fd` |
| 5 | LIGHT/2 | `P0_sift10m_T8_W32_LIGHT_R002_20261008T144008546862Z_7eea3a3e1f764d8dae7543c3b36571a3` | `07c121a356d0443fb6f31c8169a074af` |
| 6 | STOCK/2 | `P0_sift10m_T8_W32_OFF_R002_20261008T144015131968Z_4a1e50be55554c8ebbd634c91a0e1fbd` | `f730c431ec3d45ff97555be08dbd17cf` |
| 7 | LIGHT/3 | `P0_sift10m_T8_W32_LIGHT_R003_20261008T144021608643Z_026e5b5839af42ca91c69db25815b2f9` | `b8ed2ff6cc404553b3b7d3de89b66416` |
| 8 | STOCK/3 | `P0_sift10m_T8_W32_OFF_R003_20261008T144028186908Z_f0f8524923b947208fd46408f3f0a2f3` | `32269d2ebbfa47e1bb68eb19fb9932d4` |
| 9 | OFF/3 | `P0_sift10m_T8_W32_OFF_R003_20261008T144034680251Z_28bcfa65e27745ac9c09e881c3ce44a7` | `6b32bb89e8db4f75b4a39ff9be9a0b4c` |
| 10 | STOCK/4 | `P0_sift10m_T8_W32_OFF_R004_20261008T144041157669Z_94d5802218824277965beb5db5c47eeb` | `9e517e5266fc4fd795955575d13ea967` |
| 11 | LIGHT/4 | `P0_sift10m_T8_W32_LIGHT_R004_20261008T144047687650Z_1ea63031c8f149e6b25686310babd257` | `d3fc98c1d4b14e1ab89e137542d0a14b` |
| 12 | OFF/4 | `P0_sift10m_T8_W32_OFF_R004_20261008T144054316190Z_9c9428310bed47619701a2e1c507bdac` | `74b2726c9cd74612b12c6352c6c7f158` |
| 13 | LIGHT/5 | `P0_sift10m_T8_W32_LIGHT_R005_20261008T144100795377Z_1302f4f655d347aa8c436287ee3c0f29` | `8820277ffb7d4c04958d764453fc6bfc` |
| 14 | OFF/5 | `P0_sift10m_T8_W32_OFF_R005_20261008T144107440955Z_997698371f5d43f88f417e38e2ce5d91` | `a43230d1161f481a8c5482851e192681` |
| 15 | STOCK/5 | `P0_sift10m_T8_W32_OFF_R005_20261008T144113974333Z_ceab0a9fb12147a9be738acbce237998` | `42285a89d0c64a628c4ca9db1d414d64` |

Example exact LIGHT command (all other invocations preserved in campaign evidence):

```bash
#!/bin/sh
set -eu
export LC_ALL=C
export MKL_NUM_THREADS=8
export OMP_NUM_THREADS=8
unset OMP_PLACES
unset OMP_PROC_BIND
export S_TIME_FORMAT=ISO
exec /home/irthn/ann-research/Parallel_ANN_Research/.venv-research/bin/python /home/irthn/ann-research/Parallel_ANN_Research/tools/research/run_ann_experiment.py --subject-repo /home/irthn/ann-research/PipeANN-p0 --executable /home/irthn/ann-research/PipeANN-p0/build/tests/search_disk_index --benchmark-profile pipeann-b9ec4ba --dataset-id sift10m --data-type uint8 --dataset-path /home/irthn/ann-research/data/bigann/sift10m/canonical/base_10m.bbin --query /home/irthn/ann-research/data/bigann/sift10m/canonical/query.bbin --ground-truth /home/irthn/ann-research/data/bigann/sift10m/canonical/gt_10m.bin --index-id sift10m-R64-L100-PQ32 --index-prefix /home/irthn/ann-research/indexes/sift10m/sift10m --input-package-manifest /home/irthn/ann-research/data/bigann/sift10m/manifests/INPUT_PACKAGE.json --index-package-manifest /home/irthn/ann-research/indexes/sift10m/INDEX_PACKAGE.json --k 10 --l-search 100 --mem-l 0 --neighbor-type pq --distance-metric l2 --search-mode 2 --trace-detail-first-n 16 --trace-event-capacity 65536 --telemetry-interval 1 --mlflow --evidence-root /home/irthn/ann-research/research-v3 --timeout 300 --threads 8 --wcap 32 --trace-mode LIGHT --repetition 1 --causal-trace
```
