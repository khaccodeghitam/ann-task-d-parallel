# P0 causal instrumentation validation — Issue #4

Completed on 2026-10-08 using existing SIFT1M data/indexes. This validates the measurement infrastructure and characterizes instrumentation overhead; it is not an algorithmic or novelty result. No D1/D2/D3/D4/D6 instrumentation solution, adaptive width, admission control, or SIFT10M work is included.

## Reproducible sources and build

- Research branch: `research/p0-causal-instrumentation`; parent `b379a9260cb310e1ed1f7bdd3325c41a3a86e649` (merged Issue #1 harness). The containing research commit versions the tested harness patch.
- Golden stock subject: `b9ec4ba86ff5d70bec277984777197f28dc2cf42` in `~/ann-research/PipeANN`; clean and unchanged.
- Instrumented subject: `3bdcc064cb96aae4cd845bd2bb6adc5f5ba63e19` in `~/ann-research/PipeANN-p0`, local branch `research/p0-causal-instrumentation`; clean. Not pushed to upstream.
- Golden search binary SHA256: `a02ce69d1467727344c8620a254b4cba51d12616d3da171ef7c1a6668a9e8bc5`.
- Instrumented search binary SHA256: `d51066cc5fe0cf2df71149e23910ce654dcc259ed271fea28ae7002c53a8bd18`.
- [Exact subject mapping, build commands, flags and patch hashes](subject/P0_CAUSAL_SUBJECT.json); [small patch](subject/P0_CAUSAL_PIPEANN.patch); [exact commit object](subject/P0_CAUSAL_SUBJECT_COMMIT.txt). Temporary-index patch application reproduces tree `68cb192a2a931676a95e5f63ac17a91ea505b193`; hashing the saved commit object reproduces the exact subject commit.
- GNU C++ 13.3.0; empty CMAKE_BUILD_TYPE matching golden; native O3. Source/test compile flags match after root normalization: `-DBG_IO_THREAD -DNDEBUG -DUSE_AVX2 -DUSE_TCMALLOC -DUSE_URING`. Golden binary, CMake cache, compile_commands and both flags.make retain their hashes, sizes and mtimes.

[Runtime/build instructions](P0_CAUSAL_TRACING.md) contain the exact build commands. Existing local Boost headers were reused; no package, dataset or index download/rebuild was needed. Only the instrumented subject search binary was built.

ANN source changes insert observational hooks in the driver, pipe_search_common.h and Linux reader, plus the separate tracer/test. CandidatePool and IORequest/QueryBuffer layouts, public API, CMakeLists.txt and build.sh are byte-identical to the canonical base. Candidate selection, FIFO publication, width conditions/clamps/counters, termination and io_uring scheduling are unchanged. The research repository src/, include/, tests/search_disk_index.cpp, CMakeLists.txt and build.sh are untouched.

## Machine, inputs and evidence

Host CPU: 12th Gen Intel(R) Core(TM) i7-12700H; 20 logical CPUs / 14 physical cores; RAM 16542253056 bytes; kernel 7.0.0-38-generic. No governor, affinity or cache-drop changes were made for the campaign. Shared host load/frequency remain limits on interpretation.

- Dataset: `~/ann-research/data/sift1m`; queries `query.fbin`: 10000 × 128 float.
- Query SHA256: `9b0082b67d0ac55b4c7d42216560344567ad87ce3e75a9d5214a0762f1c15d65`.
- Truth: `gt.bin`, SHA256 `4c06dd3d1539b1de50f1b7e98a116833ed5c2f1571d0ef81f383a04541e797e7`.
- Existing index prefix: `~/ann-research/indexes/sift1m/sift1m`.
- Canonical `pipeann-b9ec4ba/v1` profile, `search-table/v1` parser; printed P99 is percentile 0.99. P50/P95/P999 remain null.
- All E0 runs: T8/W32/K10/L75/mem_L0/pq/l2/search_mode2, identical query/truth hashes, index metadata, benchmark profile, search parameters and recorded OpenMP/MKL environment.
- `mpstat`, `pidstat`, `iostat` and isolated local MLflow are available. OFF telemetry is disabled; LIGHT/DETAIL use non-root collectors.

Local evidence root: `~/ann-research/research-v3`. Each table run below lives in `runs/<run_id>`. Persistent campaign directory: `notes/P0_CAUSAL_20261008T123459Z_3d6610fc`, containing exact command argv JSON, stdout/stderr, frozen plan, golden metadata, E0 characterization and final integrity audit. MLflow SQLite/artifacts live in `mlflow/`; all 23 mirrors are FINISHED and metrics/profile/subject/harness commits match local evidence. MLflow remains a comparison mirror.

Run manifests correctly record the harness parent b379a926 with harness_git_dirty=true (the implementation was being validated before committing), independently of the clean subject commit 3bdcc064 or b9ec4ba. They are not rewritten to pretend the harness was already committed. The containing research commit publishes that harness implementation. Large index files >64 MiB retain sha256=null; cached/full hashing is a required follow-up before official SIFT10M.

## Tests and integrity

```bash
cd ~/ann-research/Parallel_ANN_Research
.venv-research/bin/python -m unittest discover -s tests/research -v
git diff --check
cd ~/ann-research/PipeANN-p0
g++ -std=c++17 -O2 -Wall -Wextra -I include tests/test_causal_trace.cpp src/utils/causal_trace.cpp -o /tmp/p4-test-causal-trace
/tmp/p4-test-causal-trace
```

51 Python tests pass (38 prior harness tests plus 13 causal tests). The standalone C++ tracer test passes OFF no-op, deterministic sampling, LIGHT counters, request reuse/correlation/FIFO, cache readiness, width snapshots, event overflow/table overflow and config validation. Synthetic CQE-before-submit, publish-before-CQE, duplicate sequence, negative hidden, width decrease/jump and unfinished requests all fail the checker as required. Raw protocol/truncation/mode/sample mismatch, query-counter contradiction, exporter/health schemas and missing output are covered.

Final integrity audit: 23 successful local runs, 23 MLflow mirrors, 294 checksummed files, all schemas and strengthened exporter/checker pass. 40 pre-existing artifact files retain their original SHA256 values. The four legacy infrastructure smoke runs remain intact and are not relabeled as a canonical baseline. Finalized run directories were never rewritten; strengthened exporter rechecks used detached temporary directories.

## First smoke commands and results

Run from the research repository. These are the exact harness argv used (defaults: first_n=8, event capacity=16384, external evidence root). Each owned run command.sh records the exact benchmark argv and trace environment.

```bash
/home/irthn/ann-research/Parallel_ANN_Research/.venv-research/bin/python /home/irthn/ann-research/Parallel_ANN_Research/tools/research/run_ann_experiment.py --benchmark-profile pipeann-b9ec4ba --subject-repo /home/irthn/ann-research/PipeANN-p0 --executable /home/irthn/ann-research/PipeANN-p0/build/tests/search_disk_index --dataset-path /home/irthn/ann-research/data/sift1m --query /home/irthn/ann-research/data/sift1m/query.fbin --ground-truth /home/irthn/ann-research/data/sift1m/gt.bin --index-prefix /home/irthn/ann-research/indexes/sift1m/sift1m --neighbor-type pq --threads 8 --wcap 32 --k 10 --l-search 75 --mem-l 0 --trace-mode OFF --causal-trace --mlflow
```

```bash
/home/irthn/ann-research/Parallel_ANN_Research/.venv-research/bin/python /home/irthn/ann-research/Parallel_ANN_Research/tools/research/run_ann_experiment.py --benchmark-profile pipeann-b9ec4ba --subject-repo /home/irthn/ann-research/PipeANN-p0 --executable /home/irthn/ann-research/PipeANN-p0/build/tests/search_disk_index --dataset-path /home/irthn/ann-research/data/sift1m --query /home/irthn/ann-research/data/sift1m/query.fbin --ground-truth /home/irthn/ann-research/data/sift1m/gt.bin --index-prefix /home/irthn/ann-research/indexes/sift1m/sift1m --neighbor-type pq --threads 8 --wcap 32 --k 10 --l-search 75 --mem-l 0 --trace-mode LIGHT --causal-trace --mlflow
```

```bash
/home/irthn/ann-research/Parallel_ANN_Research/.venv-research/bin/python /home/irthn/ann-research/Parallel_ANN_Research/tools/research/run_ann_experiment.py --benchmark-profile pipeann-b9ec4ba --subject-repo /home/irthn/ann-research/PipeANN-p0 --executable /home/irthn/ann-research/PipeANN-p0/build/tests/search_disk_index --dataset-path /home/irthn/ann-research/data/sift1m --query /home/irthn/ann-research/data/sift1m/query.fbin --ground-truth /home/irthn/ann-research/data/sift1m/gt.bin --index-prefix /home/irthn/ann-research/indexes/sift1m/sift1m --neighbor-type pq --threads 8 --wcap 32 --k 10 --l-search 75 --mem-l 0 --trace-mode DETAIL --causal-trace --mlflow
```

| Smoke mode | QPS | Mean latency µs | P99 µs | Recall % | Events | Trace valid |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| OFF | 3822.34 | 2082.50 | 2832 | 99.32 | 0 | true |
| LIGHT | 3821.11 | 2081.30 | 2807 | 99.32 | 0 | true |
| DETAIL | 3730.34 | 2131.80 | 5065 | 99.32 | 3885 | true |

DETAIL samples qids 0–7 deterministically. OFF health zeros describe zero recorded observations, not zero actual ANN I/O. LIGHT/DETAIL have 10000 real query aggregate rows. No exact top-K output equivalence is claimed: the existing driver prints aggregate recall and does not persist those arrays.

## E0 overhead characterization

Five repetitions per case, rotating order before measurements: stock/OFF/LIGHT, OFF/LIGHT/stock, LIGHT/stock/OFF, stock/OFF/LIGHT, OFF/LIGHT/stock. No pass/fail overhead threshold was invented. Summary below uses arithmetic run means and sample standard deviation (n=5).

| Case | QPS mean | QPS median | QPS min–max | QPS sample SD | Mean latency µs | P99 µs | Recall % | Mean IO |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| stock_OFF | 3835.632 | 3839.75 | 3818.24–3846.46 | 11.119 | 2075.586 | 2798.6 | 99.318 | 91.836 |
| instrumented_OFF | 3829.352 | 3836.56 | 3806.52–3844.79 | 16.747 | 2078.688 | 2793.8 | 99.318 | 91.840 |
| instrumented_LIGHT | 3830.864 | 3831.92 | 3819.22–3841.33 | 7.934 | 2075.434 | 2759.8 | 99.318 | 91.846 |

| Instrumented relative to stock mean | QPS delta % | Mean latency delta % | P99 delta % | Mean IO delta % |
| --- | ---: | ---: | ---: | ---: |
| instrumented_OFF | -0.1637 | +0.1495 | -0.1715 | +0.0044 |
| instrumented_LIGHT | -0.1243 | -0.0073 | -1.3864 | +0.0109 |

Delta = 100 × (case mean / stock mean − 1). These small QPS differences coexist with overlapping observed run ranges and host variance; they neither isolate exact instrumentation cost nor establish a speedup. Recall averages agree, without bitwise output equivalence. The single DETAIL smoke QPS is 2.7451% below the stock E0 mean, but it is not a repeated matched overhead comparison or headline performance measurement.

| E0 case | QPS by repetition | Mean latency µs by repetition | P99 µs by repetition |
| --- | --- | --- | --- |
| stock_OFF | 3818.24, 3831.62, 3846.46, 3839.75, 3842.09 | 2085.51, 2078.31, 2069.05, 2073.65, 2071.41 | 2882, 2756, 2778, 2800, 2777 |
| instrumented_OFF | 3806.52, 3816.99, 3844.79, 3841.90, 3836.56 | 2090.75, 2085.33, 2071.34, 2071.75, 2074.27 | 2854, 2806, 2755, 2759, 2795 |
| instrumented_LIGHT | 3819.22, 3831.92, 3832.59, 3841.33, 3829.26 | 2081.60, 2075.97, 2074.82, 2069.57, 2075.21 | 2767, 2754, 2752, 2761, 2765 |

LIGHT host telemetry, pooled arithmetic means over 10 one-second samples:

| Collector / entity / metric | Mean | Min–max | Unit |
| --- | ---: | --- | --- |
| mpstat / all / %idle | 19.649 | 15.860–22.370 | percent |
| pidstat / benchmark_process / %CPU | 1559.800 | 1508.000–1609.000 | percent |
| iostat / nvme0n1 / r/s | 340003.139 | 326793.000–352909.000 | 1/s |
| iostat / nvme0n1 / rkB/s | 1360018.935 | 1307176.000–1411640.000 | KiB/s |
| iostat / nvme0n1 / r_await | 0.110 | 0.110–0.110 | ms |
| iostat / nvme0n1 / %util | 77.731 | 73.600–83.700 | percent |

Host busy derived from all-CPU idle is 80.351%, including other processes. pidstat CPU is multicore accounting (1559.8% is not normalized to one core); SQPOLL CPU/process attribution requires care. NVMe statistics are host/device observations, not per-request hardware latency. Collectors cover process startup/drain/post-search dumping as well as search. Stock/OFF have no telemetry, so no CPU/NVMe delta against stock is invented.

## Trace health and sentinel coverage

Six DETAIL runs have 23229 verified events across 48 sampled queries. All traced runs report zero drops, table overflows, unmatched submits/CQEs/publications, ordering violations, negative hidden count and outstanding correlations at query end. DETAIL first8/capacity16384 passes query/request ordering, FIFO publication, width bounds/init/nondecreasing +1 and drained-request invariants. Full-query aggregate totals agree with stored counters; sampled histories agree with their query summaries.

| Event | Total DETAIL count |
| --- | ---: |
| QUERY_START | 48 |
| WIDTH_INIT | 48 |
| IO_SELECT | 4469 |
| IO_SUBMIT | 4469 |
| IO_CQE_SEEN | 4469 |
| IO_PUBLISH | 4469 |
| NODE_EXPAND | 4181 |
| WIDTH_CHANGE | 980 |
| QUERY_END | 48 |
| TRACE_HEALTH | 48 |
| IO_CACHE_READY | 0 |

Cache readiness is tested synthetically, but these existing mem_L0 runs observed no cache-only path. Expansion request_seq remains null because no safe direct source-request mapping was added; not every published request must expand. L_observed_io and L_HOL can be derived from sampled events, but L_ready needs an independently established node/source mapping. No HOL/dependency-root-cause interpretation is made.

| Sentinel (DETAIL first8) | QPS (diagnostic only) | Events | Drops | Valid |
| --- | ---: | ---: | ---: | --- |
| T1/W32 | 1017.09 | 3962 | 0 | true |
| T8/W32 | 3798.00 | 3869 | 0 | true |
| T8/W64 | 3815.26 | 3851 | 0 | true |
| T16/W32 | 3371.07 | 3885 | 0 | true |
| T16/W16 | 3304.46 | 3777 | 0 | true |

Only the five requested sentinels were executed after smoke and E0; no T×W sweep.

## Run registry

All run directories: `~/ann-research/research-v3/runs/<run_id>`. Stage/order comes from the campaign record; each manifest is canonical.

| Stage / case | Run ID | MLflow run ID |
| --- | --- | --- |
| smoke / instrumented OFF | `P0_sift1m_T8_W32_OFF_R001_20261008T123621273453Z_77216b05da244e11b3b50139cb549ff3` | `9b8b02ed51204219b33dc0cad8bc0c24` |
| smoke / instrumented LIGHT | `P0_sift1m_T8_W32_LIGHT_R001_20261008T123657742566Z_659ff2f02aaa4d8c979b90edba38c759` | `f73f883095ef4a7da87182e04d183ca5` |
| smoke / instrumented DETAIL | `P0_sift1m_T8_W32_DETAIL_R001_20261008T123702541545Z_3e166604103d4ef6bd2c41fa3920200e` | `ae2fc02f6b464f448fb67c5d5b207009` |
| e0 / stock OFF | `P0_sift1m_T8_W32_OFF_R001_20261008T123837327593Z_bdb84d2e5dfa492c93214372fc98699a` | `73fc20c44472477f8e386cf7221dd022` |
| e0 / instrumented OFF | `P0_sift1m_T8_W32_OFF_R001_20261008T123841996091Z_02cc0c330bf64d6fa8d0f548aeb06557` | `1152ffd6e6c0430dbaba633db90297c5` |
| e0 / instrumented LIGHT | `P0_sift1m_T8_W32_LIGHT_R001_20261008T123846685813Z_fbbbcb3a9a6c4a9bba02806db6a42665` | `a8085a3880d94155b04448355a38532e` |
| e0 / instrumented OFF | `P0_sift1m_T8_W32_OFF_R002_20261008T123851481436Z_6206b1ec71374ddebc97bb9e915b42d8` | `8f649d95e2f84afa806af9737af9c6ea` |
| e0 / instrumented LIGHT | `P0_sift1m_T8_W32_LIGHT_R002_20261008T123856219343Z_66d80658eef44d50899fb132bec7fa7f` | `77dc652cb75c43e48b47c3af075a498c` |
| e0 / stock OFF | `P0_sift1m_T8_W32_OFF_R002_20261008T123900991076Z_5077163eb86e4a2692220b34f7053e02` | `c6320bcfc5384ed7865f9902229980e7` |
| e0 / instrumented LIGHT | `P0_sift1m_T8_W32_LIGHT_R003_20261008T123905652625Z_4f3d8fbf9ab040878417c0f709de6694` | `3a1ac712cc5c436f9ba7181cfb44b5fb` |
| e0 / stock OFF | `P0_sift1m_T8_W32_OFF_R003_20261008T123910463645Z_921e5de5a2e144809c6db6aaea0d9bd1` | `ee2abdf5bae940bb8aae10fdd5a6c0e2` |
| e0 / instrumented OFF | `P0_sift1m_T8_W32_OFF_R003_20261008T123915115021Z_6a395e6123574ca9bf45b64fc91c7926` | `5f29999ba497493b8788e5892d265495` |
| e0 / stock OFF | `P0_sift1m_T8_W32_OFF_R004_20261008T123919831940Z_f857096c893447c48c6502c3ff1507f2` | `b5df8198674b46209609cba7e1a7490f` |
| e0 / instrumented OFF | `P0_sift1m_T8_W32_OFF_R004_20261008T123924498522Z_99334254afcb41a08bc7535d28a11f87` | `488dec1d1c0947d39dfed9d9ade7e297` |
| e0 / instrumented LIGHT | `P0_sift1m_T8_W32_LIGHT_R004_20261008T123929225324Z_dcc961d5499844af8db0789b36d45c79` | `64e7e49e002e4289bacc877386c2182b` |
| e0 / instrumented OFF | `P0_sift1m_T8_W32_OFF_R005_20261008T123933989329Z_f5b83a4ac83a4eb6bce78907039ad7bc` | `737efb36a5c44c88ad692e27034cb811` |
| e0 / instrumented LIGHT | `P0_sift1m_T8_W32_LIGHT_R005_20261008T123938738305Z_b1f60b167d484c30ab268c7bd4368028` | `b03f979741c84a55a24b81aed5b0bf51` |
| e0 / stock OFF | `P0_sift1m_T8_W32_OFF_R005_20261008T123943540796Z_6726b541957540759edffcdf1d9e2f72` | `ae3f50da5c4e41e29739fe840e15b461` |
| sentinel / instrumented DETAIL | `P0_sift1m_T1_W32_DETAIL_R001_20261008T124504231507Z_5c90d6e2ef004355bf77e9fca16268a5` | `0fcdb126eac44c858f6252ecffc95a82` |
| sentinel / instrumented DETAIL | `P0_sift1m_T8_W32_DETAIL_R001_20261008T124516291847Z_ab71e1d98d7348748f75a626e98dc384` | `7af3fc947e7d4ef2b988dd81197c4361` |
| sentinel / instrumented DETAIL | `P0_sift1m_T8_W64_DETAIL_R001_20261008T124521260612Z_52771a386e44411c9a6300e2ef58063a` | `8acd2dd680054f12bc702f29db2cc93f` |
| sentinel / instrumented DETAIL | `P0_sift1m_T16_W32_DETAIL_R001_20261008T124526120229Z_7efef527f4304083be351583c58151f8` | `2eb4fdeac39147539f45e844ea720363` |
| sentinel / instrumented DETAIL | `P0_sift1m_T16_W16_DETAIL_R001_20261008T124531391463Z_493fab4137d84cebbac26fbc851cee99` | `ee857ffe0cf54636accfad8f617cd9dc` |

To inspect a DETAIL run, set RUN_DIR to its directory and execute:

```bash
.venv-research/bin/python tools/research/check_causal_trace.py "$RUN_DIR/events.jsonl" --health "$RUN_DIR/trace_health.json"
(cd "$RUN_DIR" && sha256sum -c SHA256SUMS)
.venv-research/bin/mlflow ui --backend-store-uri "sqlite:///$HOME/ann-research/research-v3/mlflow/mlflow.db" --default-artifact-root "$HOME/ann-research/research-v3/mlflow/artifacts" --host 127.0.0.1 --port 5000
```

Generated datasets/indexes/builds/virtualenvs/raw traces/events/CSV/MLflow remain external or ignored. Only tooling, schemas, docs, synthetic tests and the small subject patch/provenance are committed. Golden stock and main are unchanged; FIFO and stock width heuristic are unchanged; SIFT10M is untouched; D1/D4 are not implemented; no novelty claim.
