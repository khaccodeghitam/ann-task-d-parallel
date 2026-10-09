# E0c SIFT10M native-placement validation — Issue #12

**E0C_PROCEED** under the frozen native/unbound paired protocol. Twelve blocks / 36 accepted runs, no exclusions or retries. This is an operational validation, not an instrumentation-overhead proof, equivalence to Issue #8, or novelty claim.

## Exact provenance and frozen protocol

- Campaign: `E0C_SIFT10M_20261009T055255739318Z`.
- External evidence: `/home/irthn/ann-research/research-v3/campaigns/E0C_SIFT10M_20261009T055255739318Z/`.
- PLAN SHA256: `247ce8b71296a89a7af8577cffe0bc777d22ac4e5f45002c232f71d5f9431303`.
- Main/base and clean measurement harness: `5884b5e32e7f1ea8afdbbec26e01310e71e4535a`.
- Analyzer/report commit is the commit containing this document, created after measurement.
- Golden subject: `b9ec4ba86ff5d70bec277984777197f28dc2cf42`; binary SHA256 `a02ce69d1467727344c8620a254b4cba51d12616d3da171ef7c1a6668a9e8bc5`.
- Instrumented subject: `3bdcc064cb96aae4cd845bd2bb6adc5f5ba63e19`; binary SHA256 `d51066cc5fe0cf2df71149e23910ce654dcc259ed271fea28ae7002c53a8bd18`.
- INPUT_PACKAGE SHA256: `47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3`.
- INDEX_PACKAGE SHA256: `8955f8bca0c8ebb5afbd2a69e9760fc829d22ba76a4ef7b482339e88b2489595`.
- Frozen tracked snapshots: [PLAN.json](plans/E0C_SIFT10M_20261009T055255739318Z/PLAN.json), [PLAN.md](plans/E0C_SIFT10M_20261009T055255739318Z/PLAN.md), [PLAN.sha256](plans/E0C_SIFT10M_20261009T055255739318Z/PLAN.sha256). Exact bytes match the external originals.

Issue #12 completely read before changes/measurement (no comments), together with E0b, G0, SIFT10M setup report and P0 causal tracing docs. Both ANN trees remained clean at their expected commits. No ANN/data/index build, download or source edit occurred.

All runs: canonical SIFT10M 10K query set, uint8/l2/pq/mode2/T8/W32/K10/L100/mem_L0, explicit pipeann-b9ec4ba profile. Printed P99 means percentile 0.99. STOCK uses golden binary, no causal trace, OFF mode. Instrumented OFF/LIGHT require causal tracing. All bind both package digests and local MLflow.

Native environment: OMP_NUM_THREADS=8, MKL_NUM_THREADS=8, OMP_DYNAMIC=FALSE; OMP_PROC_BIND, OMP_PLACES and GOMP_CPU_AFFINITY explicitly unset. Shared LC_ALL=C and S_TIME_FORMAT=ISO; OMP_DISPLAY_ENV/OMP_DISPLAY_AFFINITY unset. No taskset, numactl or manual affinity. Runtime CPU placement is diagnostic only. Governor/EPP/power/NVMe settings were observed without tuning.

Matched observers for all variants: --host-telemetry; mpstat/pidstat/iostat at 1 s; external pidstat -h -t -u -w -p PID 1; ps task rows and /proc task affinities/context switches/fdinfo at 0.35/1.2 s after process discovery. Readable process environment is captured with an explicit whitelist, excluding secrets. Missing kernel metadata is diagnostic, not an exclusion. Raw evidence is local; MLflow mirrors run-level data only.

Five seconds after harness finalization within each block, 15 seconds between blocks, no final pause. No performance-based exclusions, retries, warmup ANN workload or cache flush. Six specified permutations twice; all retained. Exact argv/environment/observer source and hashes remain in campaign executions/ and PLAN.

| Block | Frozen order |
| --- | --- |
| B01 | STOCK → OFF → LIGHT |
| B02 | STOCK → LIGHT → OFF |
| B03 | OFF → STOCK → LIGHT |
| B04 | OFF → LIGHT → STOCK |
| B05 | LIGHT → STOCK → OFF |
| B06 | LIGHT → OFF → STOCK |
| B07 | STOCK → OFF → LIGHT |
| B08 | STOCK → LIGHT → OFF |
| B09 | OFF → STOCK → LIGHT |
| B10 | OFF → LIGHT → STOCK |
| B11 | LIGHT → STOCK → OFF |
| B12 | LIGHT → OFF → STOCK |

## Full audits and integrity

Before and after all accepted measurements, full INPUT and INDEX component verification ran with package_manifest.py verify <manifest> --full-components. Exact argv, UTC boundaries, duration, stdout/stderr and manifest digest are preserved in pre/post audit files. All four pass; no repair or regeneration.

| Audit | Start UTC | End UTC | Seconds | Result |
| --- | --- | --- | ---: | --- |
| pre_input | 2026-10-09T05:52:56.597002+00:00 | 2026-10-09T05:52:57.799517+00:00 | 1.202572 | PASS |
| pre_index | 2026-10-09T05:52:57.799799+00:00 | 2026-10-09T05:53:01.691583+00:00 | 3.891853 | PASS |
| post_input | 2026-10-09T06:02:34.385588+00:00 | 2026-10-09T06:02:35.123554+00:00 | 0.737969 | PASS |
| post_index | 2026-10-09T06:02:35.123753+00:00 | 2026-10-09T06:02:37.501268+00:00 | 2.377522 | PASS |

504 finalized run files match SHA256SUMS; 1126 historical run files remain byte-identical. All historical campaign files, golden/instrumented source state and binary SHA/size/mtime, and frozen plan/source hashes verified unchanged. Historical E0b reanalysis reproduces the exact stored analysis object and E0B_PROCEED result; no historical output was rewritten.

## Paired block statistics and decision

BLOCK is the statistical unit. Performance delta = 100×(target/reference−1), recall delta = target−reference in percentage points. Decimal conversion of printed metrics before float representation preserves decimal boundaries. MAD is median deviation from the paired median; median absolute paired delta is median(|delta|).

Bootstrap remains 20,000 resamples of 12 blocks with replacement, random.Random seed 20261008; same index draws for every metric. CI90 is linear-interpolated 5th/95th percentile of bootstrap medians, p×(n−1). No query/request bootstrap, p-values or simultaneous-CI claim.

| Block | OFF/STOCK QPS % | LIGHT/OFF QPS % | OFF/STOCK mean latency % | LIGHT/OFF mean latency % | OFF−STOCK recall pp | LIGHT−OFF recall pp |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B01 | -0.341882 | 1.089038 | 0.317054 | -1.173672 | 0.020000 | -0.030000 |
| B02 | -0.145414 | -8.197143 | 0.158840 | 8.963533 | -0.020000 | 0.010000 |
| B03 | 1.541738 | -1.343649 | -1.549654 | 1.134062 | -0.010000 | 0.010000 |
| B04 | -1.468663 | 0.707042 | 1.361348 | -0.703335 | 0.000000 | 0.000000 |
| B05 | 1.231689 | 2.107818 | -1.223218 | -2.212093 | 0.000000 | 0.000000 |
| B06 | 0.724042 | -0.118693 | -0.711164 | 0.072454 | -0.010000 | 0.010000 |
| B07 | -1.175834 | 1.063463 | 1.331048 | -1.218775 | -0.010000 | 0.010000 |
| B08 | -0.020092 | 0.636070 | -0.017336 | -0.750126 | -0.010000 | -0.010000 |
| B09 | -1.226042 | 1.364956 | 1.231916 | -1.422544 | 0.000000 | 0.010000 |
| B10 | 3.187261 | 1.180656 | -3.175335 | -1.244163 | 0.010000 | -0.010000 |
| B11 | 0.005429 | -0.352537 | 0.037898 | 0.247283 | -0.010000 | 0.010000 |
| B12 | 0.112773 | -0.639730 | -0.066628 | 0.449623 | 0.030000 | -0.040000 |

| Comparison | Metric | Mean | Median | Median absolute paired delta | Sample SD | Min | Max | MAD | Median CI90 | Gate |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| OFF_vs_STOCK | qps | 0.202084 | -0.007332 | 0.949938 | 1.323932 | -1.468663 | 3.187261 | 0.949938 | [-0.597963, 0.724042] | PROCEED |
| OFF_vs_STOCK | mean_latency_us | -0.192103 | 0.010281 | 0.967191 | 1.325205 | -3.175335 | 1.361348 | 0.971540 | [-0.711164, 0.634907] | PROCEED |
| OFF_vs_STOCK | recall | -0.000833 | -0.005000 | 0.010000 | 0.014434 | -0.020000 | 0.030000 | 0.005000 | [-0.010000, 0.005000] | PROCEED |
| LIGHT_vs_OFF | qps | -0.208559 | 0.671556 | 1.076251 | 2.695883 | -8.197143 | 2.107818 | 0.741825 | [-0.352537, 1.089038] | PROCEED |
| LIGHT_vs_OFF | mean_latency_us | 0.178520 | -0.726731 | 1.153867 | 2.921742 | -2.212093 | 8.963533 | 0.747499 | [-1.218775, 0.247283] | PROCEED |
| LIGHT_vs_OFF | recall | -0.002500 | 0.005000 | 0.010000 | 0.017123 | -0.040000 | 0.010000 | 0.005000 | [-0.010000, 0.010000] | PROCEED |

Unchanged symmetric limits: ±3% OFF/STOCK, ±5% LIGHT/OFF, ±0.02 pp recall. Performance PROCEED requires |median| within the limit and CI90 entirely within it; FAIL requires CI fully outside on one side; otherwise INCONCLUSIVE. Recall uses the same CI rule. Invalid required traces or relative FAIL produce E0C_FAIL; otherwise relative INCONCLUSIVE or native sanity failure produces E0C_INCONCLUSIVE. No manual threshold/label promotion.

## Native-regime sanity and descriptive absolute comparison

Frozen factor-of-two sanity: STOCK median QPS≥2471.42 and median mean latency≤3212.82 us. This checks broad operating regime only, not equivalence.

| Campaign / STOCK | Median QPS | Median mean latency us |
| --- | ---: | ---: |
| Issue #8 native | 4942.84 | 1606.41 |
| E0b spread/threads | 107.13 | 74624.51 |
| E0c native/unbound | 3288.09 | 2420.98 |

**Native sanity: PASS. Relative classification: PROCEED. Final: E0C_PROCEED.** Cross-campaign absolute numbers are descriptive: placement, host state, time and observers differ. They do not isolate a causal placement effect or prove equivalence to Issue #8.

Passing the broad sanity interval does not restore Issue #8's exact throughput or latency: E0c STOCK is about 3.29k QPS / 2.42 ms, versus 4.94k QPS / 1.61 ms there. The origin of that remaining absolute difference is unresolved.

B02 LIGHT retains a −8.197143% paired QPS delta and +8.963533% mean-latency delta; B12 LIGHT−OFF recall retains −0.04 pp. These individual block values exceed the numerical effect margins, yet the predeclared gate applies to the median and its 12-block CI, which pass. No outlier exclusion, retry, per-block pass claim or bit-for-bit output-equivalence claim is made.

## Host, placement and SQPOLL diagnostics

Tables are per-run sample means/snapshots, including process startup/loading and partial search intervals. Short native searches limit sysstat resolution. Process CPU uses multicore scale; context-switch rates below are process/leader rows, not guessed sums across tasks. NVMe rows are device-wide. Telemetry samples are never independent block observations.

| Block/variant | CPU usr/sys/idle % | Process CPU % | Leader voluntary/involuntary /s | NVMe read IOPS | Read KiB/s | r_await ms | aqu-sz | util % |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| B01/STOCK | 41.167/36.073/22.727 | 1432.000 | 1.333/31.310 | 351099.333 | 1404885.333 | 0.110 | 38.590 | 70.367 |
| B01/OFF | 43.360/35.653/20.870 | 1401.000 | 1.667/5.000 | 341245.667 | 1364994.667 | 0.110 | 37.547 | 69.200 |
| B01/LIGHT | 39.293/35.887/24.803 | 1436.000 | 1.000/30.000 | 352522.483 | 1410097.913 | 0.110 | 38.577 | 72.393 |
| B02/STOCK | 39.310/36.103/24.570 | 1439.667 | 2.333/14.667 | 353808.443 | 1415249.703 | 0.110 | 38.843 | 71.200 |
| B02/LIGHT | 41.753/28.117/30.130 | 1273.667 | 1.333/1.333 | 317480.483 | 1269951.157 | 0.100 | 31.307 | 68.537 |
| B02/OFF | 41.523/36.030/22.413 | 1427.747 | 1.667/3.000 | 350740.260 | 1402981.030 | 0.110 | 38.380 | 68.770 |
| B03/OFF | 40.730/36.303/22.963 | 1431.667 | 1.333/4.647 | 352233.000 | 1408950.667 | 0.110 | 38.717 | 70.100 |
| B03/STOCK | 44.063/36.620/19.203 | 1414.667 | 1.667/74.333 | 346986.667 | 1388045.333 | 0.110 | 38.000 | 70.133 |
| B03/LIGHT | 45.190/36.130/18.577 | 1396.333 | 1.667/434.000 | 342120.667 | 1368498.667 | 0.110 | 37.050 | 71.467 |
| B04/OFF | 39.033/35.620/25.313 | 1400.000 | 2.000/12.333 | 344779.000 | 1379137.333 | 0.110 | 37.247 | 70.467 |
| B04/LIGHT | 41.223/36.153/22.607 | 1422.000 | 1.667/557.333 | 349506.000 | 1398062.667 | 0.110 | 38.293 | 71.700 |
| B04/STOCK | 39.703/35.163/25.117 | 1406.293 | 1.000/2.333 | 346755.287 | 1387041.097 | 0.110 | 37.877 | 68.310 |
| B05/LIGHT | 38.837/36.037/25.110 | 1431.717 | 1.333/4.333 | 352096.000 | 1408406.667 | 0.110 | 38.773 | 68.733 |
| B05/STOCK | 39.380/33.460/27.120 | 1360.000 | 1.667/6.000 | 339657.667 | 1358653.333 | 0.103 | 35.553 | 70.267 |
| B05/OFF | 38.930/33.530/27.527 | 1389.000 | 1.000/3.000 | 344649.667 | 1378620.000 | 0.103 | 36.750 | 67.767 |
| B06/LIGHT | 40.940/36.413/22.537 | 1418.050 | 2.000/2279.333 | 350001.333 | 1400022.667 | 0.110 | 38.260 | 70.300 |
| B06/OFF | 40.623/36.270/23.043 | 1423.383 | 1.333/7.333 | 351131.333 | 1404537.333 | 0.110 | 38.430 | 71.433 |
| B06/STOCK | 41.190/35.937/22.710 | 1411.000 | 1.667/4.667 | 347099.333 | 1388410.667 | 0.110 | 37.767 | 72.833 |
| B07/STOCK | 41.943/36.450/21.520 | 1419.333 | 1.667/552.000 | 348143.333 | 1392584.000 | 0.110 | 38.147 | 71.433 |
| B07/OFF | 39.413/35.473/25.067 | 1399.083 | 1.667/4.333 | 345011.590 | 1380060.963 | 0.107 | 37.287 | 71.923 |
| B07/LIGHT | 41.243/36.687/22.013 | 1429.333 | 1.333/7.000 | 351611.000 | 1406465.333 | 0.110 | 38.500 | 71.867 |
| B08/STOCK | 43.340/36.337/20.187 | 1414.790 | 2.000/452.667 | 348479.087 | 1393941.623 | 0.110 | 38.030 | 70.210 |
| B08/LIGHT | 40.083/36.410/23.443 | 1430.667 | 1.333/116.333 | 352770.667 | 1411090.667 | 0.110 | 38.523 | 71.000 |
| B08/OFF | 41.857/36.257/21.783 | 1413.000 | 1.667/1687.993 | 346315.333 | 1385318.667 | 0.110 | 37.827 | 70.967 |
| B09/OFF | 42.013/35.850/22.030 | 1397.667 | 2.333/17.333 | 345463.667 | 1381912.000 | 0.110 | 37.303 | 71.467 |
| B09/STOCK | 40.047/36.327/23.577 | 1427.333 | 2.000/82.000 | 350311.330 | 1401262.600 | 0.110 | 38.333 | 72.390 |
| B09/LIGHT | 42.603/36.410/20.803 | 1416.333 | 1.667/30.333 | 347000.667 | 1388118.667 | 0.110 | 38.140 | 71.800 |
| B10/OFF | 39.280/35.457/25.213 | 1395.000 | 1.333/6.333 | 345776.000 | 1383126.667 | 0.110 | 37.190 | 70.000 |
| B10/LIGHT | 37.573/35.747/26.680 | 1433.043 | 2.333/4.667 | 352413.500 | 1409665.953 | 0.110 | 38.700 | 63.620 |
| B10/STOCK | 35.473/33.533/30.977 | 1349.333 | 1.650/3.650 | 338758.667 | 1355076.000 | 0.100 | 35.173 | 66.267 |
| B11/LIGHT | 37.623/35.863/26.473 | 1440.333 | 1.333/3.667 | 354615.667 | 1418488.000 | 0.110 | 39.087 | 69.933 |
| B11/STOCK | 37.723/35.760/26.513 | 1435.030 | 1.333/2.000 | 355093.333 | 1420396.000 | 0.110 | 39.000 | 64.633 |
| B11/OFF | 37.340/35.630/27.030 | 1435.000 | 1.000/3.000 | 354598.000 | 1418418.667 | 0.110 | 39.050 | 66.867 |
| B12/LIGHT | 37.843/35.913/25.927 | 1438.333 | 1.667/5.000 | 353902.333 | 1424008.000 | 0.110 | 39.047 | 67.967 |
| B12/OFF | 37.597/35.643/26.753 | 1437.667 | 1.333/3.000 | 353920.943 | 1415717.017 | 0.110 | 38.957 | 65.613 |
| B12/STOCK | 37.520/35.717/26.727 | 1437.333 | 1.000/4.667 | 354747.667 | 1419017.333 | 0.110 | 39.063 | 68.333 |

| Block/variant | Load1 before/after | MemAvailable KiB before/after | Package °C before/after | CPU0 MHz runtime | Search-task masks / last CPUs | iou-sqp count / masks / last CPUs | iou-wrk count | io_uring fdinfo snapshots |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B01/STOCK | 2.75/3.89 | 11142580/11093084 | 64.0/74.0 | 2827.5,3300.0 | 0-19 / 0,1,2,3,4,5,6,11,12,16,17,19 | [8, 8] / 0-19 / 7,8,9,10,13,14,15,18 | [0, 0] | 2/2 |
| B01/OFF | 3.58/4.81 | 11034696/11071308 | 59.0/73.0 | 4100.0,3263.9 | 0-19 / 0,1,2,3,4,6,8,10,11,13,14,15,19 | [0, 8] / 0-19 / 5,7,9,12,16,17,18,19 | [0, 0] | 2/2 |
| B01/LIGHT | 4.59/4.28 | 11158044/11187156 | 58.0/65.0 | 4400.0,3400.0 | 0-19 / 4,10,11,12,13,14,15,16,17,18 | [8, 8] / 0-19 / 0,1,2,3,5,6,7,8,13,15,19 | [0, 0] | 2/2 |
| B02/STOCK | 3.49/3.45 | 11268056/11253484 | 58.0/67.0 | 3865.8,3300.0 | 0-19 / 0,2,4,6,10,12,16,17,18,19 | [8, 8] / 0-19 / 0,1,2,3,5,7,9,13,14,15 | [0, 0] | 2/2 |
| B02/LIGHT | 3.17/3.64 | 11253024/11255436 | 57.0/61.0 | 4069.1,3300.0 | 0-19 / 0,2,4,6,8,9,10,11,12,13 | [8, 8] / 0-19 / 14,15,16,17,18,19 | [0, 0] | 2/2 |
| B02/OFF | 3.43/4.84 | 11287040/11246532 | 58.0/66.0 | 1582.8,3300.0 | 0-19 / 0,2,4,7,10,12,13,14,16 | [8, 8] / 0-19 / 1,3,8,9,11,15,17,18,19 | [0, 0] | 2/2 |
| B03/OFF | 4.35/5.36 | 11327760/11222828 | 57.0/70.0 | 1593.0,3154.8 | 0-19 / 3,4,6,7,8,10,15,16,18 | [8, 8] / 0-19 / 0,1,9,11,12,13,14,17,19 | [0, 0] | 2/2 |
| B03/STOCK | 4.93/6.70 | 11214728/10867128 | 59.0/66.0 | 4267.5,3236.1 | 0-19 / 0,1,3,4,6,7,8,9,10,11,12,13 | [8, 8] / 0-19 / 5,9,13,14,15,16,17,18,19 | [0, 0] | 2/2 |
| B03/LIGHT | 6.24/7.34 | 10827376/10641504 | 59.0/67.0 | 3451.5,3248.1 | 0-19 / 0,1,2,7,8,10,13,14,15,16,17 | [8, 8] / 0-19 / 4,5,6,8,9,10,11,12,15,18,19 | [0, 0] | 2/2 |
| B04/OFF | 6.13/5.80 | 10557936/10546368 | 59.0/62.0 | 2539.7,3300.2 | 0-19 / 0,3,7,8,9,10,11,12,13,14,15 | [8, 8] / 0-19 / 1,2,4,5,16,17,18,19 | [0, 0] | 2/2 |
| B04/LIGHT | 5.33/5.14 | 10579980/10414020 | 58.0/69.0 | 2850.0,3300.0 | 0-19 / 0,1,2,5,6,7,8,9,10,11,13 | [8, 8] / 0-19 / 6,7,12,14,15,16,17,18,19 | [0, 0] | 2/2 |
| B04/STOCK | 4.97/6.10 | 10545816/10376968 | 64.0/69.0 | 1770.2,3300.0 | 0-19 / 2,3,4,6,7,8,9,10,11,12,14 | [8, 8] / 0-19 / 0,1,5,13,15,16,17,18,19 | [0, 0] | 2/2 |
| B05/LIGHT | 4.96/6.01 | 10583836/10557160 | 68.0/68.0 | 1209.0,3300.7 | 0-19 / 0,2,4,5,6,8,9,10,11,12,13 | [8, 8] / 0-19 / 1,3,14,15,16,17,18,19 | [0, 0] | 2/2 |
| B05/STOCK | 5.52/6.36 | 10565088/10400464 | 56.0/63.0 | 4100.4,3359.2 | 0-19 / 1,2,5,6,8,9,10,11,12,15 | [8, 8] / 0-19 / 12,13,14,15,16,17,18,19 | [0, 0] | 2/2 |
| B05/OFF | 6.09/6.97 | 10457836/10451284 | 57.0/62.0 | 4100.0,3300.3 | 0-19 / 0,1,2,4,5,6,8,10,11,12 | [8, 8] / 0-19 / 13,14,15,16,17,18,19 | [0, 0] | 2/2 |
| B06/LIGHT | 5.73/6.63 | 10485852/10149892 | 58.0/60.0 | 4273.7,3300.0 | 0-19 / 0,2,4,5,6,7,8,10,11,13,14 | [8, 8] / 0-19 / 1,3,12,15,16,17,18,19 | [0, 0] | 2/2 |
| B06/OFF | 6.18/5.39 | 10142892/10065228 | 63.0/58.0 | 4100.0,3239.3 | 0-19 / 0,2,4,5,6,8,9,10,12,13,14 | [8, 8] / 0-19 / 3,7,11,15,16,17,18,19 | [0, 0] | 2/2 |
| B06/STOCK | 5.03/4.71 | 10102640/10061948 | 60.0/67.0 | 4168.3,3173.4 | 0-19 / 1,2,3,4,5,7,10,13,14,15,18,19 | [8, 8] / 0-19 / 6,7,8,11,12,13,14,15,16,17 | [0, 0] | 2/2 |
| B07/STOCK | 4.25/4.14 | 9856116/9758264 | 57.0/60.0 | 4100.0,3302.5 | 0-19 / 0,4,7,12,14,15,16,17,18,19 | [8, 8] / 0-19 / 1,2,3,5,6,8,9,10,13 | [0, 0] | 2/2 |
| B07/OFF | 3.97/5.18 | 9897372/9893256 | 61.0/71.0 | 1113.9,3280.9 | 0-19 / 1,2,3,4,9,10,11,12,13,14,17 | [8, 8] / 0-19 / 0,5,6,7,12,14,15,16,18,19 | [0, 0] | 2/2 |
| B07/LIGHT | 4.84/5.82 | 9822324/9791680 | 58.0/64.0 | 4009.6,3300.2 | 0-19 / 0,2,4,8,10,11,12,13,15 | [8, 8] / 0-19 / 1,3,6,14,16,17,18,19 | [0, 0] | 2/2 |
| B08/STOCK | 5.16/6.11 | 9907808/9666028 | 59.0/77.0 | 4100.0,3303.8 | 0-19 / 0,1,2,3,4,5,6,10,11,12,13,14 | [8, 8] / 0-19 / 6,7,9,12,14,15,16,17,18,19 | [0, 0] | 2/2 |
| B08/LIGHT | 5.78/6.76 | 9865676/9853104 | 60.0/68.0 | 1397.5,3300.1 | 0-19 / 6,8,9,10,13,15,16,17,18 | [8, 8] / 0-19 / 1,2,3,5,7,11,12,14,19 | [0, 0] | 2/2 |
| B08/OFF | 6.30/6.15 | 9759984/9666916 | 77.0/63.0 | 4100.0,3300.0 | 0-19 / 0,5,6,7,8,9,11,13,14,15 | [8, 8] / 0-19 / 1,2,3,10,12,16,17,18,19 | [0, 0] | 2/2 |
| B09/OFF | 5.34/4.99 | 9639920/9765736 | 60.0/63.0 | 4241.2,3152.5 | 0-19 / 0,1,2,6,7,8,9,10,11,12,13 | [8, 8] / 0-19 / 1,5,14,15,16,17,18,19 | [0, 0] | 2/2 |
| B09/STOCK | 4.59/4.30 | 9799220/9855976 | 60.0/66.0 | 4339.1,3300.0 | 0-19 / 4,5,6,8,12,13,14,15,18 | [8, 8] / 0-19 / 1,3,7,9,11,16,17,19 | [0, 0] | 2/2 |
| B09/LIGHT | 4.36/5.37 | 9764396/9497244 | 67.0/63.0 | 2061.3,3202.7 | 0-19 / 1,3,5,7,8,11,12,13,17 | [8, 8] / 0-19 / 4,6,9,10,14,15,16,18,19 | [0, 0] | 2/2 |
| B10/OFF | 4.49/5.50 | 9537172/11849712 | 63.0/64.0 | 4398.4,3176.7 | 0-19 / 0,1,2,3,4,6,8,10,11,12,13 | [8, 8] / 0-19 / 5,9,14,15,16,17,18,19 | [0, 0] | 2/2 |
| B10/LIGHT | 5.06/6.09 | 11942152/11994336 | 58.0/61.0 | 3394.6,3300.0 | 0-19 / 0,2,4,6,7,10,12,14,15,18 | [8, 8] / 0-19 / 3,8,9,11,13,16,17,19 | [0, 0] | 2/2 |
| B10/STOCK | 5.68/6.59 | 12015464/12009688 | 58.0/62.0 | 4023.9,3400.0 | 0-19 / 0,1,2,6,8,10,11,12,13,14,16 | [8, 8] / 0-19 / 4,7,12,13,14,15,17,18,19 | [0, 0] | 2/2 |
| B11/LIGHT | 5.27/5.13 | 12016660/12012100 | 58.0/56.0 | 4100.0,3300.0 | 0-19 / 0,4,6,8,9,10,13,14,15 | [8, 8] / 0-19 / 3,7,11,12,16,17,18,19 | [0, 0] | 2/2 |
| B11/STOCK | 4.96/4.80 | 12035140/11991184 | 55.0/64.0 | 4056.2,3300.0 | 0-19 / 0,1,2,4,6,8,10,11,12,13,15,19 | [8, 8] / 0-19 / 3,5,7,9,14,16,17,18 | [0, 0] | 2/2 |
| B11/OFF | 4.42/4.14 | 12011460/11980008 | 55.0/57.0 | 4100.0,3248.6 | 0-19 / 0,1,2,6,7,8,10,11,12,13,15 | [8, 8] / 0-19 / 2,3,4,5,14,16,17,18,19 | [0, 0] | 2/2 |
| B12/LIGHT | 3.37/3.18 | 12025824/11938208 | 54.0/72.0 | 4100.0,3400.0 | 0-19 / 0,2,4,6,10,11,12,13,14,15,17 | [8, 8] / 0-19 / 2,3,7,8,9,12,16,18,19 | [0, 0] | 2/2 |
| B12/OFF | 3.09/4.20 | 11969068/11924344 | 55.0/58.0 | 4100.0,3300.0 | 0-19 / 0,1,2,4,6,8,9,10,12,13 | [8, 8] / 0-19 / 2,3,5,14,15,16,17,18,19 | [0, 0] | 2/2 |
| B12/STOCK | 3.86/5.00 | 11967432/11913284 | 54.0/56.0 | 399.5,3300.0 | 0-19 / 0,1,2,3,4,5,6,8,10,12,13,14 | [8, 8] / 0-19 / 7,9,11,15,16,17,18,19 | [0, 0] | 2/2 |

Observed governors ['powersave'], EPP ['balance_performance'], NVMe scheduler ['[none] mq-deadline']. Swap-used before/after range 0–320 KiB. All policies' current/max frequencies, queue attributes and readable power limits remain in raw snapshots. None was tuned.

Search-task rows include the benchmark background task; they are not automatically labeled OpenMP workers. LIGHT query counters retain worker/TID identity separately. SQPOLL counts/masks above are runtime observations, not an inference of one kernel thread per worker from source. A snapshot with no iou-wrk does not prove none existed. All exact task identities, last CPUs, context-switch counts, ps rows and fdinfo remain external.

**Measured facts** are the absolute/paired benchmark values, task snapshots and telemetry above. **Statistical summaries** are the frozen block medians/CIs and gates. **Interpretation** is limited to whether native operation and relative comparability satisfy Issue #12. **Unknown causes** include independent scheduler, thermal/frequency, background-load and completion-observation effects; cross-campaign differences cannot assign these causes. IO_SUBMIT/CQE timing is unchanged and remains userspace-observed I/O interval, not hardware latency.

## Tests, trace validity and run inventory

180 research Python tests pass (151 historical + 29 E0c), git diff --check passes. Synthetic coverage includes explicit native unset contract, accidental binding, sanity boundaries/failures, all paired gates/recall, invalid trace precedence, order/completeness/telemetry/package/subject validation and deterministic bootstrap. Historical E0b is replayed into new output only and compared for exact analysis equality.

All 24 required traces are valid with zero drops, ordering violations, negative hidden counts, unmatched submit/CQE/publish, outstanding correlations and table overflows. OFF validates the no-op protocol; LIGHT validates aggregates, not DETAIL event histories. STOCK trace_valid=null. No DETAIL run was requested. All 36 benchmark/overall statuses are success; all MLflow mirrors FINISHED with matching required metadata, checked separately from scientific analysis.

| Block/variant | QPS | Mean latency us | P99 us | Recall % | Mean IO/query | Run ID | MLflow ID |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| B01/STOCK | 3284.76 | 2422.3 | 4211.0 | 99.13 | 122.69 | `P0_sift10m_T8_W32_OFF_R001_20261009T055401274969Z_9d504b06dd66473e909428d475daec09` | `4da428934b9049268869c157c960bf10` |
| B01/OFF | 3273.53 | 2429.98 | 3475.0 | 99.15 | 122.66 | `P0_sift10m_T8_W32_OFF_R001_20261009T055412257770Z_ae2bc24a10d1450d9bb3ad086e6c95d6` | `636cdd77402749c99fc960c1e1c90e20` |
| B01/LIGHT | 3309.18 | 2401.46 | 3228.0 | 99.12 | 122.65 | `P0_sift10m_T8_W32_LIGHT_R001_20261009T055423060625Z_04984a25388f4a9ab435867e5c35363d` | `9a8fcf83fe354078a8173d03009e29e7` |
| B02/STOCK | 3307.79 | 2404.94 | 3242.0 | 99.14 | 122.69 | `P0_sift10m_T8_W32_OFF_R002_20261009T055443826725Z_c27b4631b1b74c95852896c25d53fc53` | `91ca92b84fa9443caed710841afd19e9` |
| B02/LIGHT | 3032.23 | 2624.67 | 6176.0 | 99.13 | 122.84 | `P0_sift10m_T8_W32_LIGHT_R002_20261009T055454436486Z_24a5fd7c52da451bb79d4996839b307f` | `d75dd83b8ff0451181d15184e295333d` |
| B02/OFF | 3302.98 | 2408.76 | 3269.0 | 99.12 | 122.62 | `P0_sift10m_T8_W32_OFF_R002_20261009T055505452700Z_6883aa1063664046a9e8509aad4f6b92` | `3ba5fbd7ae4340659651044e24814b7c` |
| B03/OFF | 3308.9 | 2404.63 | 3239.0 | 99.13 | 122.64 | `P0_sift10m_T8_W32_OFF_R003_20261009T055526186929Z_67956673f352448c8b4bb0215c35e5ff` | `8052b1bb600b42228e4f9f7db6427d85` |
| B03/STOCK | 3258.66 | 2442.48 | 4446.0 | 99.14 | 122.64 | `P0_sift10m_T8_W32_OFF_R003_20261009T055536920384Z_82bf4748281a4d3aaaaaaa0ab6aeb4cd` | `5c513498c8204bcc8297145d1ba9ff4e` |
| B03/LIGHT | 3264.44 | 2431.9 | 3985.0 | 99.14 | 122.67 | `P0_sift10m_T8_W32_LIGHT_R003_20261009T055547519027Z_dd6b1486d17c450d9d73421e540fdb01` | `1e6342b56f294ff2b1b04090d59547ef` |
| B04/OFF | 3243.09 | 2452.6 | 5267.0 | 99.13 | 122.71 | `P0_sift10m_T8_W32_OFF_R004_20261009T055608375886Z_92d8e3ac43004bcab98ed291e5ac7e9d` | `af2583ad05904c2fbc1a3c2a544b7465` |
| B04/LIGHT | 3266.02 | 2435.35 | 4659.0 | 99.13 | 122.63 | `P0_sift10m_T8_W32_LIGHT_R004_20261009T055619060366Z_aff6704de4a24f468df5a6cb9cc0abbe` | `ad0d7dec1f19485cb35655a5c7fac295` |
| B04/STOCK | 3291.43 | 2419.66 | 4987.0 | 99.13 | 122.67 | `P0_sift10m_T8_W32_OFF_R004_20261009T055629851234Z_3728e76edc784cd08bcdfe7a3ebae053` | `e4bcae110d4348d5962b2b532a0f395d` |
| B05/LIGHT | 3302.32 | 2409.23 | 3275.0 | 99.13 | 122.66 | `P0_sift10m_T8_W32_LIGHT_R005_20261009T055650403727Z_ef04c0c065224dae82532dc819ff8fd3` | `988441c517324818a34a27e6a2836edb` |
| B05/STOCK | 3194.8 | 2494.24 | 5582.0 | 99.13 | 122.67 | `P0_sift10m_T8_W32_OFF_R005_20261009T055701051245Z_93e5fd15aeeb457b8cf1270330e8cf87` | `0b06002cca9341ae8a791ea7caa33090` |
| B05/OFF | 3234.15 | 2463.73 | 5465.0 | 99.13 | 122.69 | `P0_sift10m_T8_W32_OFF_R005_20261009T055711689816Z_ea0d7cd832524e868abbe53ad326abf4` | `32f6ce3592d4411e8070cd3e9c2cc62b` |
| B06/LIGHT | 3290.3 | 2417.08 | 3411.0 | 99.14 | 122.65 | `P0_sift10m_T8_W32_LIGHT_R006_20261009T055732341101Z_fdae8a55ca32422d960f2fb033b3cc64` | `e1c74bcd6f7246c29f1ebaf1522da61c` |
| B06/OFF | 3294.21 | 2415.33 | 3380.0 | 99.13 | 122.68 | `P0_sift10m_T8_W32_OFF_R006_20261009T055743110523Z_58203bd12d0741a9aa4ca9195ceea0b1` | `080f48f37ef14b25bb3ad6c781935e15` |
| B06/STOCK | 3270.53 | 2432.63 | 4754.0 | 99.14 | 122.63 | `P0_sift10m_T8_W32_OFF_R006_20261009T055753778727Z_71535af591b04edab9a6f8804e8277c7` | `680c68b609ac4bff93ccbd9421efc7ac` |
| B07/STOCK | 3291.28 | 2415.39 | 3347.0 | 99.14 | 122.67 | `P0_sift10m_T8_W32_OFF_R007_20261009T055814429414Z_2506bfa97c5942f9bee10159ce97cb14` | `5de124f07ed842a4bcb8bf989cc08d28` |
| B07/OFF | 3252.58 | 2447.54 | 5328.0 | 99.13 | 122.7 | `P0_sift10m_T8_W32_OFF_R007_20261009T055825081476Z_ad4200db0655435498720325b7eca163` | `94b7f3912bd24889940a955133663eb4` |
| B07/LIGHT | 3287.17 | 2417.71 | 3309.0 | 99.14 | 122.64 | `P0_sift10m_T8_W32_LIGHT_R007_20261009T055835723164Z_70d2e450d8d44a928c5baddbde51cb79` | `2667106362af432584a86ecfadf7aac4` |
| B08/STOCK | 3284.89 | 2422.68 | 3525.0 | 99.14 | 122.61 | `P0_sift10m_T8_W32_OFF_R008_20261009T055856557513Z_bf6f52ae9cc14e4e9ac36a104aa1caf5` | `b58c35469892402e9393496543e61386` |
| B08/LIGHT | 3305.12 | 2404.09 | 3237.0 | 99.12 | 122.64 | `P0_sift10m_T8_W32_LIGHT_R008_20261009T055907119072Z_02501273b20240c8a03a576c6b69fc43` | `dec4887e5ee441fd9394b34290f1cff4` |
| B08/OFF | 3284.23 | 2422.26 | 3462.0 | 99.13 | 122.64 | `P0_sift10m_T8_W32_OFF_R008_20261009T055917909993Z_05f7ce5e9bba47b5ac40d22fa5d524d2` | `3d16b7cd2eb944fc869ba23ca06ae394` |
| B09/OFF | 3257.98 | 2441.4 | 5208.0 | 99.13 | 122.61 | `P0_sift10m_T8_W32_OFF_R009_20261009T055938645033Z_85695d4f6ad446b58333cbf2702fa13b` | `7124ed7c840144a6a8d6e1c1c7cb8ecd` |
| B09/STOCK | 3298.42 | 2411.69 | 3309.0 | 99.13 | 122.65 | `P0_sift10m_T8_W32_OFF_R009_20261009T055949451528Z_1894e13fb3c84ec48a7094462ab22652` | `3a9b77a2a07a4b8abfdb90f7abf2bbb7` |
| B09/LIGHT | 3302.45 | 2406.67 | 3299.0 | 99.14 | 122.68 | `P0_sift10m_T8_W32_LIGHT_R009_20261009T060000138268Z_5ef7b6ebf8904cb193b85f896af49750` | `eb0724633f5a4fc3bd4da48c5037b27d` |
| B10/OFF | 3265.98 | 2436.98 | 5388.0 | 99.14 | 122.67 | `P0_sift10m_T8_W32_OFF_R010_20261009T060020907662Z_2260d322047d458eabcc97bf99a5c85f` | `3e83a15970c14ebc8939fa15fc5a34df` |
| B10/LIGHT | 3304.54 | 2406.66 | 3242.0 | 99.13 | 122.66 | `P0_sift10m_T8_W32_LIGHT_R010_20261009T060031644634Z_a2f2d5c5e3014b3893bafe25e4abbb65` | `45551eb5fd2f4b95958f496e18089eb7` |
| B10/STOCK | 3165.1 | 2516.9 | 5628.0 | 99.13 | 122.77 | `P0_sift10m_T8_W32_OFF_R010_20261009T060042336742Z_9af64c5596f04a168a8a0dd7eb0bae76` | `0089e2c1d9494178a20833456ccd645d` |
| B11/LIGHT | 3304.27 | 2408.05 | 3257.0 | 99.14 | 122.66 | `P0_sift10m_T8_W32_LIGHT_R011_20261009T060102968087Z_2b14e39c05f0454383fa73ddcec7b5ef` | `1813239d23214189b7946353818f2130` |
| B11/STOCK | 3315.78 | 2401.2 | 3196.0 | 99.14 | 122.67 | `P0_sift10m_T8_W32_OFF_R011_20261009T060113602701Z_740648d5d73c414eb3cff78e1c2eac31` | `6fe027b2836e4129bcf0a2ae86e4f049` |
| B11/OFF | 3315.96 | 2402.11 | 3221.0 | 99.13 | 122.66 | `P0_sift10m_T8_W32_OFF_R011_20261009T060124102076Z_005fe36693914e4ba8346f82cfc7b7b6` | `bb08bc4433e74f25838efa6c931e6951` |
| B12/LIGHT | 3298.91 | 2410.58 | 3232.0 | 99.11 | 122.65 | `P0_sift10m_T8_W32_LIGHT_R012_20261009T060144658348Z_e5d26eb07f55417791eecabf5243c6b5` | `93fb85b997b44dcc85f120f3f4f11077` |
| B12/OFF | 3320.15 | 2399.79 | 3247.0 | 99.15 | 122.63 | `P0_sift10m_T8_W32_OFF_R012_20261009T060155353151Z_ad99e1d7bc764b0492fb4252817586dd` | `7da6cd0276fc4ff7b5c77b892810b4c7` |
| B12/STOCK | 3316.41 | 2401.39 | 3230.0 | 99.12 | 122.62 | `P0_sift10m_T8_W32_OFF_R012_20261009T060205911073Z_d582c4f45ff24fa09c5c13bee05e0451` | `f1d4230737134bd3b13f6d72c8d1f018` |

Run directories: ~/ann-research/research-v3/runs/<run_id>/. Exact command and observer evidence: campaign executions/Bxx_VARIANT/. Package audit, checksums, host snapshots, raw telemetry and analysis stay local; none are committed as bulky generated artifacts.

```bash
.venv-research/bin/python -m unittest discover -s tests/research -v
git diff --check
.venv-research/bin/python tools/research/analyze_e0c.py --campaign /home/irthn/ann-research/research-v3/campaigns/E0C_SIFT10M_20261009T055255739318Z --output /new/analysis-directory
```

E0C_PROCEED satisfies the measurement gate for proposing a later, separate G0-resume issue; execution requires that separate authorization.
G0 Stage B/C were not resumed. ANN source, FIFO, width policy and io_uring unchanged; no D1/D4 implementation; no data/index rebuild; SIFT100M untouched; main untouched; no large artifacts committed; no novelty claim. Stop after Draft PR.
