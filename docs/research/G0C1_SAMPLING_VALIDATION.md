# G0-C1 distributed sampling validation

**G0C1_PASS**: deterministic explicit-qid sampling is complete and valid; new-subject native paired E0 is **E0C_PROCEED**. No official G0-C2 experiment or D6 timing interpretation was performed.

## Exact identities

- Issue: #16; research/main base `36cc84b98418e9051c4d7c798ffaae20b06f8a3e`.
- Clean measurement harness `a31228e4d73a06bb588e8f23d668d20c2bda4f1b`; final report commit is the commit containing this document.
- Golden subject `b9ec4ba86ff5d70bec277984777197f28dc2cf42`, pristine throughout; binary SHA256 `a02ce69d1467727344c8620a254b4cba51d12616d3da171ef7c1a6668a9e8bc5`.
- Prior instrumented subject `3bdcc064cb96aae4cd845bd2bb6adc5f5ba63e19`; its prior binary was retained externally without overwrite.
- New local subject `35222026893ff7d1b45586fcdd8165a5ce592cd3`, tree `a0f730206dd5d5e7e2c06bdf5894c583a79613ca`.
- New binary SHA256 `f5795e43c3be1f2515bd37e21ad1fbab45b2849c859724629a8c6edea5e418dd` (34698648 bytes).
- Incremental patch SHA256 `3b6fea09d8a5b38d05f137a1bc55f9bd564634a5f50870c6dfcf855775b30f0d`.
- INPUT_PACKAGE `47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3`.
- INDEX_PACKAGE `8955f8bca0c8ebb5afbd2a69e9760fc829d22ba76a4ef7b482339e88b2489595`.
- Campaign `G0C1_SIFT10M_20261009T073827804239Z`; local evidence `/home/irthn/ann-research/research-v3/campaigns/G0C1_SIFT10M_20261009T073827804239Z`.
- Frozen PLAN SHA256 `94e411000d230d8250a1907bff95594d05894363728ed0ede1df80a58ef2b208`; exact copies in [plans/G0C1_PLAN.json](plans/G0C1_PLAN.json), [PLAN.md](plans/G0C1_PLAN.md), [PLAN.sha256](plans/G0C1_PLAN.sha256). Plan/source/config were not edited after measurement began.

## Implementation and source semantics

Config is parsed once before search: `--trace-sample-policy explicit_qids --trace-sample-qids <strict ascending CSV>`. Duplicate/unsorted/out-of-range/noncanonical/empty/oversized IDs are rejected. Read-only uint8 bitmap membership is chosen once at query begin; the complete query and physical/cache request lifecycle is retained. No per-event allocation, locks, string/JSON/file I/O or new candidate-selector invocation.

Default first-N remains unchanged and emits PANTRC01/v1. Explicit DETAIL emits PANTRC02/v2 with exact IDs, canonical digest and benchmark origin/end metadata; event/counter numeric layouts remain unchanged. New derived events/health use schema-v3. The manifest and run index gain additive sampling fields; old index cells remain unchanged, missing new fields stay blank. MLflow receives policy/digest/count only, alongside existing run metadata; no raw traces/events/telemetry are uploaded.

Only sampler/tracer implementation, tracer tests and two observational benchmark driver calls changed in the subject. Reader submission/CQE hooks, FIFO, width heuristic, CandidatePool, graph/search/distance and io_uring code are byte-identical to the old subject. OFF/LIGHT do not gain phase clocks, bitmap lookups or active-query atomics. Full implementation rationale: [sampler design](G0C1_SAMPLER_DESIGN.md).

## Build and reproducible subject provenance

The authorized incremental build reused existing canonical CMake configuration; golden binary/source and SIFT10M/index were not rebuilt. Exact compiler definitions/flags, CMake/compile-command digests and binary identity are in [subject metadata](subject/G0C1_SUBJECT.json). Compiler: g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0.

```sh
CPLUS_INCLUDE_PATH=/home/irthn/ann-research/Parallel_ANN_Research/.deps-research/usr/include cmake --build build --target search_disk_index -j4
```

Local subject branch: `research/g0c1-distributed-detail-sampling`; no upstream subject push. [Incremental patch](subject/G0C1_SAMPLER.patch) applies to `3bdcc064...`; the original P0 patch reconstructs that base from golden. An isolated temporary Git index verified that applying this patch produces tree `a0f730206dd5d5e7e2c06bdf5894c583a79613ca` exactly. [Raw commit object](subject/G0C1_SUBJECT_COMMIT.txt) hashes to the new subject commit. Reproduction instructions are in [subject README](subject/G0C1_REPRODUCE.md).

## Tests and historical replay

**250 research Python tests PASS** (213 historical plus 37 new), optimized C++ tracer suite PASS, ASan/UBSan C++ suite PASS, `git diff --check` PASS. Tests cover strict sampling configuration, SHA256 vectors, OFF/LIGHT no-op paths, legacy first-N, full physical/cache lifecycle, FIFO, reuse, width, event/table overflow, old/new raw formats, missing/extra/wrong/duplicate query identity, sampling/phase digest corruption, schema/index migration, fake benchmark integration, MLflow small-only mirroring and malformed causal traces.

```sh
.venv-research/bin/python -m unittest discover -s tests/research -v
git diff --check
g++ -std=c++17 -O2 -Wall -Wextra -I include tests/test_causal_trace.cpp src/utils/causal_trace.cpp -o <external-setup>/test_causal_trace
<external-setup>/test_causal_trace <new-external-path>/synthetic_v2.bin
g++ -std=c++17 -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -I include tests/test_causal_trace.cpp src/utils/causal_trace.cpp -o <external-setup>/test_causal_trace_sanitized
<external-setup>/test_causal_trace_sanitized
```

C++ commands run in PipeANN-p0. Test/build logs live under `research-v3/notes/G0C1_SETUP_20261009T072328930400Z`. C++-generated v2 synthetic trace was independently exported/checked by Python with matching SHA256 and full lifecycle.

All **103 historical raw traces** remain readable (36 OFF,60 LIGHT,7 DETAIL). Frozen E0b, E0c and G0-B serialized analysis JSON replays match exactly in new external output directories, including classifications E0B_PROCEED/E0C_PROCEED/G0B_COMPLETE. No historical run or campaign output was rewritten. The derived run index is migrated additively, not a canonical artifact.

## Non-headline distributed DETAIL correctness

Frozen illustrative correctness IDs (not an official G0-C2 sample): `1000,1533,2066,2600,3133,3666,4200,4733,5266,5800,6333,6866,7400,7933,8466,9000`.

Sampling digest: `bb12f3bd4c1a370786765e1ebe6f5ef9883b6deab2d4437392090e3c3556deda` (ASCII canonical CSV plus newline). Exactly16 requested/observed distinct IDs at T1/T8/T16, W32/K10/L100/memL0/pq/l2/mode2, native OMP T/MKL8/dynamicFALSE, fixed packages, matched telemetry and local MLflow.

| T | Events | Max events on one worker | Start phase fraction range | Query rows | Invariant checker |
|---|---:|---:|---|---:|---|
| 1 | 10128 | 10128 | 0.1015–0.8996 | 10000 | PASS |
| 8 | 10124 | 2570 | 0.1040–0.9003 | 10000 | PASS |
| 16 | 10090 | 1855 | 0.1012–0.8968 | 10000 | PASS |

All smoke failure counters are zero: drops/table overflows/ordering violations/negative hidden/unmatched submit-CQE-publish/outstanding correlations. Every sampled QUERY_START/WIDTH_INIT/QUERY_END/TRACE_HEALTH is present; all sampled physical requests select/submit/CQE/publish correctly in FIFO order. Published requests need not expand; no expansion-to-request mapping is invented.

The allocated event capacity65536/worker is cumulative across the run. Memory is17MiB(T1),136MiB(T8),272MiB(T16), plus query rows/request tables/10KiB bitmap. Historical maximum full-event estimate1077/query ×16 all on one worker =17232, 3.803× headroom. Observed largest worker10128 events. This is empirical headroom, not a universal bound; overflow is explicit invalidity.

Example exact T8 smoke runner command (other two replace T and OMP_NUM_THREADS with1/16):

```sh
#!/bin/sh
set -eu
unset GOMP_CPU_AFFINITY
export LC_ALL=C
export MKL_NUM_THREADS=8
unset OMP_DISPLAY_AFFINITY
unset OMP_DISPLAY_ENV
export OMP_DYNAMIC=FALSE
export OMP_NUM_THREADS=8
unset OMP_PLACES
unset OMP_PROC_BIND
export S_TIME_FORMAT=ISO
exec /home/irthn/ann-research/Parallel_ANN_Research/.venv-research/bin/python /home/irthn/ann-research/Parallel_ANN_Research/tools/research/run_ann_experiment.py --subject-repo /home/irthn/ann-research/PipeANN-p0 --executable /home/irthn/ann-research/PipeANN-p0/build/tests/search_disk_index --benchmark-profile pipeann-b9ec4ba --dataset-id sift10m --data-type uint8 --dataset-path /home/irthn/ann-research/data/bigann/sift10m/canonical/base_10m.bbin --query /home/irthn/ann-research/data/bigann/sift10m/canonical/query.bbin --ground-truth /home/irthn/ann-research/data/bigann/sift10m/canonical/gt_10m.bin --index-id sift10m-R64-L100-PQ32 --index-prefix /home/irthn/ann-research/indexes/sift10m/sift10m --input-package-manifest /home/irthn/ann-research/data/bigann/sift10m/manifests/INPUT_PACKAGE.json --index-package-manifest /home/irthn/ann-research/indexes/sift10m/INDEX_PACKAGE.json --threads 8 --wcap 32 --k 10 --l-search 100 --mem-l 0 --neighbor-type pq --distance-metric l2 --search-mode 2 --trace-detail-first-n 16 --trace-event-capacity 65536 --host-telemetry --telemetry-interval 1 --mlflow --evidence-root /home/irthn/ann-research/research-v3 --timeout 300 --threads 8 --trace-sample-policy explicit_qids --trace-sample-qids 1000,1533,2066,2600,3133,3666,4200,4733,5266,5800,6333,6866,7400,7933,8466,9000 --trace-mode DETAIL --repetition 1 --causal-trace
```

Each smoke also runs `check_causal_trace.py <events.jsonl> --health <trace_health.json>` independently; exact argv/results in execution evidence.

## Phase observability and limits

**MEASURED FACT:** benchmark-relative sampled starts span about10%–90% of benchmark duration; existing worker/TID and full lifecycle boundaries are retained. Two new steady-clock observations bracket the query loop only in explicit DETAIL.

**DERIVED METRIC:** phase fractions are timestamp differences divided by benchmark origin-to-end duration. A 1M-call optimized clock diagnostic measured14.916ns/call (~30ns for two additional observations); ASan/UBSan17.019ns/call. This is not an ANN overhead estimate.

**LIMITATION:** total active-query occupancy and query dispatch progress are not recorded. Late/distributed qids or phase fractions do not establish steady-state concurrency. Future G0-C2 must predeclare phase-scoped interpretation and may remain inconclusive. No global boundary atomic or hot-loop lock was added.

`IO_SUBMIT` remains after SQE preparation/immediately before io_uring_submit; `IO_CQE_SEEN` remains userspace CQE/user_data processing. Their difference is a **userspace-observed I/O interval**, not hardware/device latency. Publication delay is application-level; no D6 timing classification is computed here.

## New subject native paired E0

12 complete paired blocks,36 accepted runs, exactly six orders repeated twice: STOCK/OFF/LIGHT; STOCK/LIGHT/OFF; OFF/STOCK/LIGHT; OFF/LIGHT/STOCK; LIGHT/STOCK/OFF; LIGHT/OFF/STOCK. Fixed5s within/15s between blocks after finalization, no performance exclusions/retries. Search: SIFT10M uint8/l2/pq/mode2 T8/W32/K10/L100/memL0, same canonical10K queries, both package bindings and local MLflow.

Native environment: OMP_NUM_THREADS=8, MKL_NUM_THREADS=8, OMP_DYNAMIC=FALSE; OMP_PROC_BIND, OMP_PLACES and GOMP_CPU_AFFINITY explicitly unset. No taskset/numactl/pinning or governor/EPP/scheduler/power tuning. All three variants use mpstat/pidstat/iostat at1s plus matched external thread pidstat/runtime/task/fdinfo observers.

Statistical unit = **BLOCK**; performance delta100×(target/reference−1), recall target−reference in percentage points. Fixed20,000 block resamples, seed20261008,90% percentile CI. OFF/STOCK margins±3%, LIGHT/OFF±5%, recall±0.02pp; decision logic identical to E0c. No request/query pseudoreplication.

| Comparison | Metric | Median delta | CI90 | Margin | Gate |
|---|---|---:|---|---:|---|
| OFF_vs_STOCK | qps (percent) | -0.005687 | [-0.908583, 0.114776] | ±3 | PROCEED |
| OFF_vs_STOCK | mean_latency_us (percent) | 0.049291 | [-0.232071, 1.013819] | ±3 | PROCEED |
| OFF_vs_STOCK | recall (percentage_points) | 0.005000 | [-0.005000, 0.010000] | ±0.02 | PROCEED |
| LIGHT_vs_OFF | qps (percent) | -0.092196 | [-0.774912, 0.918835] | ±5 | PROCEED |
| LIGHT_vs_OFF | mean_latency_us (percent) | -0.099916 | [-1.051510, 0.612877] | ±5 | PROCEED |
| LIGHT_vs_OFF | recall (percentage_points) | 0.010000 | [0.000000, 0.010000] | ±0.02 | PROCEED |

All12 paired values in block order:

| Comparison/metric | Values |
|---|---|
| OFF_vs_STOCK/qps | -0.094785, -2.265011, -1.749557, 0.056411, -2.293939, 0.056234, 0.311022, -0.067609, -0.187532, 0.224868, 0.114776, 0.781656 |
| OFF_vs_STOCK/mean_latency_us | 0.127279, 2.303356, 1.933628, -0.142429, 2.339050, 0.004570, -0.264091, 0.094011, 0.189190, -0.255232, -0.232071, -0.709264 |
| OFF_vs_STOCK/recall | 0.000000, -0.010000, 0.000000, -0.010000, -0.010000, 0.010000, 0.010000, 0.000000, 0.020000, 0.010000, 0.010000, 0.010000 |
| LIGHT_vs_OFF/qps | -0.043042, 5.009709, 2.903416, 0.120033, 1.880713, 0.046231, -0.606214, -0.141349, -4.650508, -0.789349, -0.774912, -0.880110 |
| LIGHT_vs_OFF/mean_latency_us | -0.130430, -4.921296, -3.044202, -0.131438, -1.972589, -0.155390, 0.463486, -0.069403, 4.800916, 0.612877, 0.673785, 0.658901 |
| LIGHT_vs_OFF/recall | 0.010000, 0.020000, 0.010000, -0.010000, 0.000000, 0.010000, 0.000000, 0.020000, 0.010000, 0.000000, 0.010000, 0.000000 |

| Comparison/metric | Mean | Median absolute delta | Sample SD | Min | Max | MAD |
|---|---:|---:|---:|---:|---:|---:|
| OFF_vs_STOCK/qps | -0.426122 | 0.206200 | 1.048850 | -2.293939 | 0.781656 | 0.206200 |
| OFF_vs_STOCK/mean_latency_us | 0.449000 | 0.243652 | 1.081634 | -0.709264 | 2.339050 | 0.292942 |
| OFF_vs_STOCK/recall | 0.003333 | 0.010000 | 0.009847 | -0.010000 | 0.020000 | 0.005000 |
| LIGHT_vs_OFF/qps | 0.172885 | 0.782130 | 2.349791 | -4.650508 | 5.009709 | 0.689934 |
| LIGHT_vs_OFF/mean_latency_us | -0.267899 | 0.635889 | 2.356940 | -4.921296 | 4.800916 | 0.735805 |
| LIGHT_vs_OFF/recall | 0.006667 | 0.010000 | 0.008876 | -0.010000 | 0.020000 | 0.010000 |

Native sanity **PASS**: STOCK median QPS=3300.500≥2471.42; mean latency=2412.035µs≤3212.82. This is a broad operating-regime check, not equivalence with a prior absolute performance level.

**DERIVED STATISTICAL RESULT:** E0C_PROCEED; all four relative performance and both paired recall gates PROCEED. Comparability is supported for the frozen T8/W32 host/protocol/package configuration. It is not a universal instrumentation-overhead proof. T16/W64 and DETAIL overhead beyond that scope remain **unvalidated**.

### All measurements and mirror IDs

| Block/case | QPS | Mean latency µs | P99 µs | Recall@10 % | Mean I/O | Run ID | MLflow ID |
|---|---:|---:|---:|---:|---:|---|---|
| B01/STOCK | 3302.2 | 2412.02 | 3263.0 | 99.13 | 122.64 | `P0_sift10m_T8_W32_OFF_R001_20261009T073952954543Z_78fb3cee893044c6a14abed9a6ba5afc` | `b4a1b9152ec447199082233cacd35d90` |
| B01/OFF | 3299.07 | 2415.09 | 3291.0 | 99.13 | 122.71 | `P0_sift10m_T8_W32_OFF_R001_20261009T074003454966Z_7efec885cf074a38ac3aab7ae4ad7dc0` | `fc61760a29ed47a1be5d940ca41c4bc1` |
| B01/LIGHT | 3297.65 | 2411.94 | 3286.0 | 99.14 | 122.66 | `P0_sift10m_T8_W32_LIGHT_R001_20261009T074014091542Z_cf0f52e1e36b4a879caca954527c9057` | `9a5da63ca1714380b5d077cbce9844ca` |
| B02/STOCK | 3219.41 | 2474.65 | 5537.0 | 99.14 | 122.74 | `P0_sift10m_T8_W32_OFF_R002_20261009T074034798943Z_b40c425518164de7a6c0669d72af46aa` | `f1056db6fa4f45d3bd26dc4ad720643a` |
| B02/LIGHT | 3304.12 | 2407.06 | 3247.0 | 99.15 | 122.66 | `P0_sift10m_T8_W32_LIGHT_R002_20261009T074045404734Z_baf563197c16444da1d42336c9b10484` | `ef185e3dc3d346c0b460ea31026e044f` |
| B02/OFF | 3146.49 | 2531.65 | 5798.0 | 99.13 | 122.78 | `P0_sift10m_T8_W32_OFF_R002_20261009T074056123633Z_84599a37679f48d4ab312bf4ac9059d2` | `4d3fa0c6fd8f4ac09f6ca69bccfa46b3` |
| B03/OFF | 3202.09 | 2487.68 | 5538.0 | 99.13 | 122.75 | `P0_sift10m_T8_W32_OFF_R003_20261009T074116894335Z_940d65a1d2f141829533ba9d46302889` | `466f5d03bc87493e8f1fc14cc978b191` |
| B03/STOCK | 3259.11 | 2440.49 | 5271.0 | 99.13 | 122.67 | `P0_sift10m_T8_W32_OFF_R003_20261009T074127681717Z_6d9829d8443d45cf84c02fec36ae55c0` | `c3ad49da7dcf42d5ada5376801797329` |
| B03/LIGHT | 3295.06 | 2411.95 | 3325.0 | 99.14 | 122.62 | `P0_sift10m_T8_W32_LIGHT_R003_20261009T074138303594Z_da36d0111e8d49dd9ee6bc8f706f0a36` | `dfb2bbdc208a462d8109e50f581cc206` |
| B04/OFF | 3299.09 | 2411.79 | 3245.0 | 99.14 | 122.67 | `P0_sift10m_T8_W32_OFF_R004_20261009T074159020140Z_762a7b458cb548dcb118d18fc35d756b` | `44038664c7784346b8f16c412fe0b676` |
| B04/LIGHT | 3303.05 | 2408.62 | 3240.0 | 99.13 | 122.67 | `P0_sift10m_T8_W32_LIGHT_R004_20261009T074209671764Z_84f6247082bf4608a82377587958db00` | `1e4f6a4d9f0e4235a57bc0c50af894c7` |
| B04/STOCK | 3297.23 | 2415.23 | 3376.0 | 99.15 | 122.69 | `P0_sift10m_T8_W32_OFF_R004_20261009T074220317642Z_a6fa991944e44121b5dd8cfda2894d85` | `80d3ebe50f6344e0b0cf1b8623de9a78` |
| B05/LIGHT | 3291.45 | 2414.67 | 3293.0 | 99.13 | 122.63 | `P0_sift10m_T8_W32_LIGHT_R005_20261009T074241013763Z_b8e6f7f0cc59426988603ad21df7a39a` | `305643b6134d457c836de626fec37ae8` |
| B05/STOCK | 3306.54 | 2406.96 | 3257.0 | 99.14 | 122.66 | `P0_sift10m_T8_W32_OFF_R005_20261009T074251786997Z_49a61dc6030b47a88e9465eb97cdc789` | `75c9a715f23444629e9479fef0eb6978` |
| B05/OFF | 3230.69 | 2463.26 | 5499.0 | 99.13 | 122.67 | `P0_sift10m_T8_W32_OFF_R005_20261009T074302295031Z_884353e65465461f907cf73cabe36b0c` | `970c7afc96134017a663a42030b2593f` |
| B06/LIGHT | 3311.02 | 2403.11 | 3258.0 | 99.14 | 122.65 | `P0_sift10m_T8_W32_LIGHT_R006_20261009T074323084833Z_835173bca550431d86d14ace75548c28` | `74d6944460f349cd993c6dbc5fc51010` |
| B06/OFF | 3309.49 | 2406.85 | 3239.0 | 99.13 | 122.65 | `P0_sift10m_T8_W32_OFF_R006_20261009T074333739282Z_1fc2f95ca36346df811c8398093bff4c` | `9ebd109593a445f5aef45db2f4b48d6c` |
| B06/STOCK | 3307.63 | 2406.74 | 3305.0 | 99.12 | 122.62 | `P0_sift10m_T8_W32_OFF_R006_20261009T074344408854Z_db65471ef25f4033b20a678120000921` | `d57e7660ea7c4d19978f425aae9847ab` |
| B07/STOCK | 3298.8 | 2412.05 | 3306.0 | 99.13 | 122.66 | `P0_sift10m_T8_W32_OFF_R007_20261009T074404975196Z_eab82e904bf6451aaf9cbdcfa7c5b79d` | `73cfbbb971bc4ebcad69d208b4bdbf96` |
| B07/OFF | 3309.06 | 2405.68 | 3251.0 | 99.14 | 122.6 | `P0_sift10m_T8_W32_OFF_R007_20261009T074415504436Z_efb2f980ae2947df906aa9952ca60ef8` | `78f42f65b039459382abdb7b1d1643ea` |
| B07/LIGHT | 3289.0 | 2416.83 | 3335.0 | 99.14 | 122.64 | `P0_sift10m_T8_W32_LIGHT_R007_20261009T074426224320Z_559af7d4ad084f869d0d4b7c0d010027` | `f6fdf66427744473a3896cc820d9d9a3` |
| B08/STOCK | 3313.19 | 2403.98 | 3246.0 | 99.13 | 122.62 | `P0_sift10m_T8_W32_OFF_R008_20261009T074446929521Z_6178b926f88343479ccb42a2024836e1` | `7bc9e8292c0d4a5da3d7b348985a2848` |
| B08/LIGHT | 3306.27 | 2404.57 | 3263.0 | 99.15 | 122.66 | `P0_sift10m_T8_W32_LIGHT_R008_20261009T074457419386Z_856d14f0f61142d693001dcd08cc2194` | `be146d88d1674a63b7789fad4fd33e5d` |
| B08/OFF | 3310.95 | 2406.24 | 3208.0 | 99.13 | 122.65 | `P0_sift10m_T8_W32_OFF_R008_20261009T074508060139Z_8e93603db5db451eb8addadd98353ab4` | `914b78912c064430bbf4974302381104` |
| B09/OFF | 3305.23 | 2409.54 | 3255.0 | 99.14 | 122.65 | `P0_sift10m_T8_W32_OFF_R009_20261009T074528639653Z_9b7a4e3774794917906265ee12f5d63f` | `57657e09910e4231a78b7f7ce9e98953` |
| B09/STOCK | 3311.44 | 2404.99 | 3225.0 | 99.12 | 122.67 | `P0_sift10m_T8_W32_OFF_R009_20261009T074539218258Z_fbf47bf8585648edbf67a00c31f28cd2` | `4bf7adec500d4996aefad409b07cefd6` |
| B09/LIGHT | 3151.52 | 2525.22 | 5756.0 | 99.15 | 122.79 | `P0_sift10m_T8_W32_LIGHT_R009_20261009T074549721561Z_bca49b63c89b4b0c9a2fba1e9e60954c` | `5118e3af5862421a8b37dfb6a34bd9f4` |
| B10/OFF | 3311.59 | 2403.42 | 3251.0 | 99.14 | 122.62 | `P0_sift10m_T8_W32_OFF_R010_20261009T074610499008Z_6980f5c3b8e34889b9074867423e00ed` | `0caa0bacff3f41ceaa63b9978b0ba872` |
| B10/LIGHT | 3285.45 | 2418.15 | 3347.0 | 99.14 | 122.66 | `P0_sift10m_T8_W32_LIGHT_R010_20261009T074621076685Z_d68f5146ad2c45b8b9050dc71a7ab7f0` | `806c732bce9b48c3bb04e24cc70a29df` |
| B10/STOCK | 3304.16 | 2409.57 | 3267.0 | 99.13 | 122.65 | `P0_sift10m_T8_W32_OFF_R010_20261009T074631827015Z_648038329d7e4d38a5cd8766fc2a65c5` | `93054fe67bc841109c7d0bbf7f58dfd6` |
| B11/LIGHT | 3271.6 | 2428.0 | 3757.0 | 99.14 | 122.68 | `P0_sift10m_T8_W32_LIGHT_R011_20261009T074652310690Z_fada63800f1b417fafa67b8a92927a2f` | `8dadd1356b73474889cf42007dd8a92b` |
| B11/STOCK | 3293.37 | 2417.36 | 3317.0 | 99.12 | 122.68 | `P0_sift10m_T8_W32_OFF_R011_20261009T074703188706Z_8de0b1618d3f493cbed29221bb8b461e` | `b523f21f426145c292bc93b669c7b19f` |
| B11/OFF | 3297.15 | 2411.75 | 3350.0 | 99.13 | 122.68 | `P0_sift10m_T8_W32_OFF_R011_20261009T074713892636Z_e1654710873e4240aef439d458323dfd` | `5ce72341168c40aca67fbd18a3952775` |
| B12/LIGHT | 3290.82 | 2415.26 | 3391.0 | 99.14 | 122.69 | `P0_sift10m_T8_W32_LIGHT_R012_20261009T074734663483Z_84de1278666b42c0893b37897120e5c7` | `1e67f8940c2a4c6f978b5228f691aab8` |
| B12/OFF | 3320.04 | 2399.45 | 3246.0 | 99.14 | 122.65 | `P0_sift10m_T8_W32_OFF_R012_20261009T074745458763Z_38bc0f6399fc48bb9e4e9c9d7eeffef7` | `2a4da0d0b1754b008d0f5762590eb08f` |
| B12/STOCK | 3294.29 | 2416.59 | 3382.0 | 99.13 | 122.7 | `P0_sift10m_T8_W32_OFF_R012_20261009T074755987070Z_2d18697b51db490da5d3be45f62cc4dc` | `d4f498224296450f9a01761ab10bc380` |

| Correctness smoke | Run ID | MLflow ID |
|---|---|---|
| T1/W32 DETAIL | `P0_sift10m_T1_W32_DETAIL_R001_20261009T073850058528Z_ec4a450f96ea47d69a036eeb76086245` | `0808b3c7aeef4037ab322624da275016` |
| T8/W32 DETAIL | `P0_sift10m_T8_W32_DETAIL_R001_20261009T073909699872Z_12191d3ea53b4fbfb9a791bda3e62745` | `000a478d848843229c4d2737ade701f7` |
| T16/W32 DETAIL | `P0_sift10m_T16_W32_DETAIL_R001_20261009T073920801025Z_b05c273269f147ada2114c00b6744c78` | `eab2b861c2234e72a08e8ad0d69b813b` |

All39 ANN benchmark/overall statuses success; required trace validity true. STOCK trace_valid=null. All39 MLflow mirrors read back FINISHED with correct subject/harness/package/search/status metadata; explicit-sampler policy/digest/count also match. MLflow readback is a transport validation, never the scientific source.

## Package, artifact and source integrity

| Audit | UTC start | UTC end | Duration s | Exit |
|---|---|---|---:|---:|
| pre/input | 2026-10-09T07:38:28.677287+00:00 | 2026-10-09T07:38:29.553449+00:00 | 0.876 | 0 |
| pre/index | 2026-10-09T07:38:29.553715+00:00 | 2026-10-09T07:38:33.638827+00:00 | 4.085 | 0 |
| post/input | 2026-10-09T07:48:11.048415+00:00 | 2026-10-09T07:48:12.163556+00:00 | 1.115 | 0 |
| post/index | 2026-10-09T07:48:12.163773+00:00 | 2026-10-09T07:48:15.861645+00:00 | 3.698 | 0 |

Exact full-component audit command for each package (both before/after all39 runs):

```sh
.venv-research/bin/python tools/research/package_manifest.py verify ~/ann-research/data/bigann/sift10m/manifests/INPUT_PACKAGE.json --full-components
.venv-research/bin/python tools/research/package_manifest.py verify ~/ann-research/indexes/sift10m/INDEX_PACKAGE.json --full-components
```

Both immutable package digests/full component bytes match before and after. 552 new run files match SHA256SUMS; 2091 old run files and all historical campaign files are unchanged. Frozen plan/code/harness files and golden/new subject commit/clean state/binary hash/size/mtime verified. Per-execution observer checksums also verified; golden prior binary and preserved old instrumented binary match pre-change hashes.

## Diagnostics and interpretation

Local raw mpstat/pidstat/iostat, thread observer, task/allowed-mask/last-CPU/SQPOLL/fdinfo snapshots, host load/MemAvailable/swap/governor/EPP/frequency/thermal/NVMe metadata are retained uniformly. Short T8 runs supply only a few1s telemetry records and snapshots; these are not precise steady-state means or proof of a causal host mechanism. This issue analyzes sampler correctness and new-subject comparability only; no official publication-HOL distribution or D6 regime comparison was performed.

**INTERPRETATION:** explicit sampling removes the first-N-only restriction and records coarse phase context. The E0 gate supports proceeding to separately authorized preparation of G0-C2; it does not authorize that campaign within this issue.

**UNRESOLVED:** steady-state occupancy, unsampled lifecycle timing, readiness/dependency starvation and phase representativeness. D1 observability remains **NO**; D4 selector gate **NOT TESTED**; D6 **INCONCLUSIVE**.

## Reanalysis and stop

```sh
.venv-research/bin/python tools/research/analyze_g0c1.py --campaign /home/irthn/ann-research/research-v3/campaigns/G0C1_SIFT10M_20261009T073827804239Z --output /new/analysis-directory
```

No scientific protocol deviations or performance-based exclusions. Git publication uses the authenticated GitHub connector with expected-parent, non-force fast-forward updates because terminal Git lacks credentials. The subject commit remains local and is reproduced by its tracked patch/commit/tree mapping. Research/main and golden untouched; ANN FIFO/width/io_uring/search semantics unchanged. No D1/D4, G0-C2, SIFT100M, dataset/index rebuild or novelty claim. No datasets, indexes, binaries, raw traces/runs/telemetry, MLflow DB/artifacts or virtualenvs are committed. Stop after Draft PR.
