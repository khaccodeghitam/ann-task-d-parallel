# G0-B SIFT10M LIGHT sentinels — Issue #14

**G0B_COMPLETE.** Exactly 25 accepted LIGHT runs, five per sentinel, under native/unbound placement. Pre/post full-component package audits PASS; all 250,000 query counter records are present, all 25 benchmarks/required traces/overall experiment statuses are successful. **D6_INCONCLUSIVE; D1 observability NO; D4 selector gate NOT TESTED.** G0-C was not executed. This is system characterization, not a research result, novelty claim or instrumentation-overhead proof.

## Frozen provenance and execution

- Campaign: `G0B_SIFT10M_20261009T063743710720Z`.
- Evidence: `/home/irthn/ann-research/research-v3/campaigns/G0B_SIFT10M_20261009T063743710720Z`.
- PLAN SHA256: `4bf2c75d63a2865d66bcde9e6e4eed464a1fd6d831a80568086febec57116a9d`; exact tracked copies [PLAN.json](plans/G0B_SIFT10M_20261009T063743710720Z.json), [PLAN.md](plans/G0B_SIFT10M_20261009T063743710720Z.md). The external PLAN.sha256 verifies its JSON bytes. Frozen `2026-10-09T06:38:26.716966+00:00` and unchanged throughout measurements.
- Main/base and clean measurement harness commit: `b7ba71e6fc7b20630ca2a7efe6d95cd36a75f2cf`. The analyzer/report commit is the commit containing this document, created after measurement. No harness/source edits during any accepted run.
- Golden subject `b9ec4ba86ff5d70bec277984777197f28dc2cf42`, branch main, clean; binary SHA256 `a02ce69d1467727344c8620a254b4cba51d12616d3da171ef7c1a6668a9e8bc5`. Golden was verified but not run by G0-B.
- Instrumented subject `3bdcc064cb96aae4cd845bd2bb6adc5f5ba63e19`, branch research/p0-causal-instrumentation, clean; binary SHA256 `d51066cc5fe0cf2df71149e23910ce654dcc259ed271fea28ae7002c53a8bd18`.
- INPUT_PACKAGE SHA256 `47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3`.
- INDEX_PACKAGE SHA256 `8955f8bca0c8ebb5afbd2a69e9760fc829d22ba76a4ef7b482339e88b2489595`.

Issue #14 was read fully before actions and had no comments. All six requested documents were read; exact driver/tracer sampling source was inspected read-only. Terminal fetch cannot authenticate; GitHub connected app supplied exact branch/base metadata. The local signed base object was verified byte-for-byte by its Git SHA. Publication uses a normal fast-forward through that connection, never a force update or main modification.

Canonical BigANN first 10M uint8/D128, 10K queries, existing Vamana R64/Lbuild100/PQ32 index; canonical profile pipeann-b9ec4ba, l2/pq/mode2, K10/Lsearch100/mem_L0. A=T1/W32; B=T8/W32; C=T8/W64; D=T16/W32; E=T16/W16. Exact order: R1 ABCDE, R2 BCDEA, R3 CDEAB, R4 DEABC, R5 EABCD. Five seconds after every finalized harness/MLflow invocation except final (24 recorded pauses); no warmup, cache flush, tuning, performance exclusions or retries. Full hashes necessarily read components before the campaign.

Every run: --causal-trace --trace-mode LIGHT --host-telemetry --mlflow and both package manifests. Nominal telemetry interval 1s; same external pidstat thread observer and runtime snapshots at 0.35/1.2s after benchmark discovery for all sentinels. Capacity 65536/worker, detail_first_n 16 recorded but no queries sampled and no DETAIL arrays/events in LIGHT. Source uses omp_set_num_threads(requested T); no explicit mkl_set override was found. MKL_NUM_THREADS remains8 under the contract.

```sh
OMP_NUM_THREADS=<requested T>
MKL_NUM_THREADS=8
OMP_DYNAMIC=FALSE
LC_ALL=C
S_TIME_FORMAT=ISO
unset OMP_PROC_BIND OMP_PLACES GOMP_CPU_AFFINITY OMP_DISPLAY_ENV OMP_DISPLAY_AFFINITY
```

No taskset/numactl/manual affinity, governor/EPP/scheduler/power changes. E0c established comparability at **T8/W32** for this binary; it supplies no overhead guarantee at the other T/W sentinels.

Exact executable wrapper and its SHA256 are frozen in PLAN; all commands/argv, host snapshots and observer logs live under executions/B<round>_<config>/. Example actual first command (environment shown above):

```sh
/home/irthn/ann-research/Parallel_ANN_Research/.venv-research/bin/python /home/irthn/ann-research/Parallel_ANN_Research/tools/research/run_ann_experiment.py --subject-repo /home/irthn/ann-research/PipeANN-p0 --executable /home/irthn/ann-research/PipeANN-p0/build/tests/search_disk_index --benchmark-profile pipeann-b9ec4ba --dataset-id sift10m --data-type uint8 --dataset-path /home/irthn/ann-research/data/bigann/sift10m/canonical/base_10m.bbin --query /home/irthn/ann-research/data/bigann/sift10m/canonical/query.bbin --ground-truth /home/irthn/ann-research/data/bigann/sift10m/canonical/gt_10m.bin --index-id sift10m-R64-L100-PQ32 --index-prefix /home/irthn/ann-research/indexes/sift10m/sift10m --input-package-manifest /home/irthn/ann-research/data/bigann/sift10m/manifests/INPUT_PACKAGE.json --index-package-manifest /home/irthn/ann-research/indexes/sift10m/INDEX_PACKAGE.json --k 10 --l-search 100 --mem-l 0 --neighbor-type pq --distance-metric l2 --search-mode 2 --trace-detail-first-n 16 --trace-event-capacity 65536 --host-telemetry --telemetry-interval 1 --mlflow --evidence-root /home/irthn/ann-research/research-v3 --timeout 300 --threads 1 --wcap 32 --trace-mode LIGHT --repetition 1 --causal-trace
```

## Integrity and trace health

MEASURED FACT: both full-component audits before/after passed, before interpretation. Exact argv/UTC timing/stdout/stderr/digest/exit are in pre_*.audit.json/post_*.audit.json and adjacent logs; commands used package_manifest.py verify <manifest> --full-components. No repair, permission change, rebuild or rewrite occurred.

| Audit | UTC start | UTC end | Seconds | Result |
| --- | --- | --- | --- | --- |
| pre_input | 2026-10-09T06:37:48.675558+00:00 | 2026-10-09T06:37:49.473738+00:00 | 0.7982 | PASS |
| pre_index | 2026-10-09T06:37:49.474000+00:00 | 2026-10-09T06:37:51.958095+00:00 | 2.4842 | PASS |
| post_input | 2026-10-09T06:44:14.614469+00:00 | 2026-10-09T06:44:15.491960+00:00 | 0.8775 | PASS |
| post_index | 2026-10-09T06:44:15.492215+00:00 | 2026-10-09T06:44:17.895804+00:00 | 2.4036 | PASS |

INTEGRITY.json verified 400 run artifact files, 1666 historical run files unchanged, all old campaign-file hashes unchanged, exact subject commits/clean states/binary hashes/sizes/mtimes unchanged and frozen plan/execution source unchanged. Per-run SHA256SUMS cover raw/exported traces, query CSV, metadata and raw telemetry. Execution observer files also have separate SHA256SUMS, verified by the analyzer. No historical evidence was rewritten.

Each LIGHT run: query_rows 10000, events_written 0, sample_requested/observed 0, events_dropped 0, ordering_violations 0, negative_hidden_count 0, unmatched_submit/CQE/publish 0, outstanding_at_query_end 0, table_overflows 0. Query IDs cover 0..9999 exactly; worker/TID identities, stock width initialization and +1 counts, physical/cache lifecycle conservation and aggregate agreement are checked. Zero LIGHT events does not mean zero I/O. See per-run trace_health.json/trace_check.json.

MLFLOW_INTEGRITY.json independently read back all 25 mirrors as FINISHED with package digests, harness/subject commits, T/W/L/K, telemetry, benchmark_status, trace_valid and run_status matching local metadata. No raw events/traces/telemetry were uploaded. **MLflow is a mirror; analysis reads local artifacts only.**

## Performance and logical work

MEASURED FACT: all five values below are in repetition order, not sorted by performance. Latencies are microseconds, recall is percent, mean_ios is benchmark sector-equivalent read-request I/O/query. SD is sample SD(n−1). Statistical unit is the run; query distributions remain nested per run; no request-level pseudoreplication, p-values or post-hoc performance gate.

| Sentinel | Metric | R1, R2, R3, R4, R5 | Mean | Median | Min | Max | Sample SD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | qps | 924.58, 925.63, 925.03, 921.64, 925.36 | 924.448 | 925.03 | 921.64 | 925.63 | 1.6179 |
| A | mean_latency_us | 1070.78, 1069.7, 1069.82, 1073.47, 1069.53 | 1070.66 | 1069.82 | 1069.53 | 1073.47 | 1.6443 |
| A | p99_latency_us | 1343, 1326, 1330, 1361, 1325 | 1337 | 1330 | 1325 | 1361 | 15.2151 |
| A | recall | 99.15, 99.15, 99.16, 99.15, 99.16 | 99.154 | 99.15 | 99.15 | 99.16 | 0.0055 |
| A | mean_ios | 124.89, 124.9, 124.9, 124.89, 124.91 | 124.898 | 124.9 | 124.89 | 124.91 | 0.0084 |
| B | qps | 3317.29, 3252.28, 3282.08, 3306.66, 3205.2 | 3272.702 | 3282.08 | 3205.2 | 3317.29 | 45.2845 |
| B | mean_latency_us | 2396.35, 2444.77, 2420.98, 2404.84, 2481.56 | 2429.7 | 2420.98 | 2396.35 | 2481.56 | 34.3615 |
| B | p99_latency_us | 3218, 5279, 3324, 3220, 5767 | 4161.6 | 3324 | 3218 | 5767 | 1255.4339 |
| B | recall | 99.12, 99.13, 99.14, 99.13, 99.13 | 99.13 | 99.13 | 99.12 | 99.14 | 0.0071 |
| B | mean_ios | 122.63, 122.67, 122.68, 122.71, 122.71 | 122.68 | 122.68 | 122.63 | 122.71 | 0.0332 |
| C | qps | 3303.54, 3303.74, 3299.91, 3278.03, 3311.35 | 3299.314 | 3303.54 | 3278.03 | 3311.35 | 12.6063 |
| C | mean_latency_us | 2406.57, 2406.89, 2409.77, 2424.52, 2401.99 | 2409.948 | 2406.89 | 2401.99 | 2424.52 | 8.6091 |
| C | p99_latency_us | 3228, 3264, 3245, 4867, 3231 | 3567 | 3245 | 3228 | 4867 | 726.8614 |
| C | recall | 99.13, 99.14, 99.14, 99.14, 99.14 | 99.138 | 99.14 | 99.13 | 99.14 | 0.0045 |
| C | mean_ios | 122.63, 122.67, 122.64, 122.69, 122.64 | 122.654 | 122.64 | 122.63 | 122.69 | 0.0251 |
| D | qps | 2847.09, 2849.57, 2801.52, 2794.58, 2854.98 | 2829.548 | 2847.09 | 2794.58 | 2854.98 | 28.9988 |
| D | mean_latency_us | 5583.53, 5578.42, 5676.62, 5681.82, 5562.75 | 5616.628 | 5583.53 | 5562.75 | 5681.82 | 57.6784 |
| D | p99_latency_us | 29481, 30924, 35970, 29215, 28050 | 30728 | 29481 | 28050 | 35970 | 3103.7414 |
| D | recall | 99.14, 99.13, 99.14, 99.13, 99.13 | 99.134 | 99.13 | 99.13 | 99.14 | 0.0055 |
| D | mean_ios | 122.77, 122.82, 122.84, 122.75, 122.67 | 122.77 | 122.77 | 122.67 | 122.84 | 0.0667 |
| E | qps | 2769.94, 2850.07, 2798.8, 2908.1, 2770.55 | 2819.492 | 2798.8 | 2769.94 | 2908.1 | 59.2985 |
| E | mean_latency_us | 5715.5, 5582.57, 5659.1, 5469.11, 5738.96 | 5633.048 | 5659.1 | 5469.11 | 5738.96 | 109.6792 |
| E | p99_latency_us | 30872, 28111, 30260, 24984, 31985 | 29242.4 | 30260 | 24984 | 31985 | 2767.0832 |
| E | recall | 99.12, 99.12, 99.11, 99.12, 99.11 | 99.116 | 99.12 | 99.11 | 99.12 | 0.0055 |
| E | mean_ios | 121.47, 121.55, 121.52, 121.38, 121.5 | 121.484 | 121.5 | 121.38 | 121.55 | 0.065 |


DERIVED METRIC: all queries initialize actual width 4. Means below summarize final width and increases across the 10K queries within each run, then describe the five run summaries. Fractions are0..1. Final W is **not time-weighted W**; LIGHT lacks width residency/time-at-Wcap. Wcap64 does not imply actual W64.

| Sentinel | Metric | R1, R2, R3, R4, R5 | Mean | Median | Min | Max | Sample SD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | mean_initial_width | 4, 4, 4, 4, 4 | 4 | 4 | 4 | 4 | 0 |
| A | mean_final_width | 31.717, 31.708, 31.7133, 31.7271, 31.7133 | 31.7157 | 31.7133 | 31.708 | 31.7271 | 0.0071 |
| A | mean_width_increases | 27.717, 27.708, 27.7133, 27.7271, 27.7133 | 27.7157 | 27.7133 | 27.708 | 27.7271 | 0.0071 |
| A | ending_at_wcap_fraction | 0.8659, 0.8582, 0.8628, 0.8666, 0.866 | 0.8639 | 0.8659 | 0.8582 | 0.8666 | 0.0035 |
| A | max_inflight | 32, 32, 32, 32, 32 | 32 | 32 | 32 | 32 | 0 |
| A | max_completed_hidden | 32, 32, 31, 32, 32 | 31.8 | 32 | 31 | 32 | 0.4472 |
| B | mean_initial_width | 4, 4, 4, 4, 4 | 4 | 4 | 4 | 4 | 0 |
| B | mean_final_width | 29.4149, 29.4502, 29.415, 29.4097, 29.5171 | 29.4414 | 29.415 | 29.4097 | 29.5171 | 0.0453 |
| B | mean_width_increases | 25.4149, 25.4502, 25.415, 25.4097, 25.5171 | 25.4414 | 25.415 | 25.4097 | 25.5171 | 0.0453 |
| B | ending_at_wcap_fraction | 0.3269, 0.328, 0.3225, 0.3255, 0.3369 | 0.328 | 0.3269 | 0.3225 | 0.3369 | 0.0054 |
| B | max_inflight | 32, 32, 32, 32, 32 | 32 | 32 | 32 | 32 | 0 |
| B | max_completed_hidden | 31, 32, 32, 32, 32 | 31.8 | 32 | 31 | 32 | 0.4472 |
| C | mean_initial_width | 4, 4, 4, 4, 4 | 4 | 4 | 4 | 4 | 0 |
| C | mean_final_width | 30.3038, 30.3256, 30.2178, 30.3377, 30.2266 | 30.2823 | 30.3038 | 30.2178 | 30.3377 | 0.0563 |
| C | mean_width_increases | 26.3038, 26.3256, 26.2178, 26.3377, 26.2266 | 26.2823 | 26.3038 | 26.2178 | 26.3377 | 0.0563 |
| C | ending_at_wcap_fraction | 0, 0, 0, 0, 0 | 0 | 0 | 0 | 0 | 0 |
| C | max_inflight | 36, 39, 37, 38, 39 | 37.8 | 38 | 36 | 39 | 1.3038 |
| C | max_completed_hidden | 33, 34, 32, 34, 36 | 33.8 | 34 | 32 | 36 | 1.4832 |
| D | mean_initial_width | 4, 4, 4, 4, 4 | 4 | 4 | 4 | 4 | 0 |
| D | mean_final_width | 29.5566, 29.524, 29.6204, 29.5182, 29.3533 | 29.5145 | 29.524 | 29.3533 | 29.6204 | 0.0988 |
| D | mean_width_increases | 25.5566, 25.524, 25.6204, 25.5182, 25.3533 | 25.5145 | 25.524 | 25.3533 | 25.6204 | 0.0988 |
| D | ending_at_wcap_fraction | 0.3723, 0.3645, 0.3767, 0.3615, 0.3556 | 0.3661 | 0.3645 | 0.3556 | 0.3767 | 0.0084 |
| D | max_inflight | 32, 32, 32, 32, 32 | 32 | 32 | 32 | 32 | 0 |
| D | max_completed_hidden | 32, 32, 32, 32, 32 | 32 | 32 | 32 | 32 | 0 |
| E | mean_initial_width | 4, 4, 4, 4, 4 | 4 | 4 | 4 | 4 | 0 |
| E | mean_final_width | 15.9992, 15.9996, 15.9994, 15.9995, 15.997 | 15.9989 | 15.9994 | 15.997 | 15.9996 | 0.0011 |
| E | mean_width_increases | 11.9992, 11.9996, 11.9994, 11.9995, 11.997 | 11.9989 | 11.9994 | 11.997 | 11.9996 | 0.0011 |
| E | ending_at_wcap_fraction | 0.9992, 0.9996, 0.9994, 0.9995, 0.997 | 0.9989 | 0.9994 | 0.997 | 0.9996 | 0.0011 |
| E | max_inflight | 16, 16, 16, 16, 16 | 16 | 16 | 16 | 16 | 0 |
| E | max_completed_hidden | 16, 16, 16, 16, 16 | 16 | 16 | 16 | 16 | 0 |


DERIVED METRIC: per-query logical actions below come from full-query counters. Physical submitted/CQE observed/published are separate from software-cache ready/published. Expanded is node-level, not request-mapped; published minus expanded is a count difference, not identification of particular unexpanded requests. Stock stats->n_ios increments read_io_size/SECTOR_LEN after send_read, even if the software cache serves it; it is not universally a physical-device-request count. Here cache_ready/cache_published are zero in all runs, and one-sector requests agree with traced physical counts up to printed rounding. Totals are exactly per-query averages×10000; corresponding total means/SD scale by 10000. More inflight requests need not be more useful ANN work.

| Sentinel | Metric | R1, R2, R3, R4, R5 | Mean | Median | Min | Max | Sample SD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | selected_per_query | 124.8942, 124.8953, 124.8965, 124.8949, 124.9128 | 124.8987 | 124.8953 | 124.8942 | 124.9128 | 0.0079 |
| A | submitted_per_query | 124.8942, 124.8953, 124.8965, 124.8949, 124.9128 | 124.8987 | 124.8953 | 124.8942 | 124.9128 | 0.0079 |
| A | cqe_seen_per_query | 124.8942, 124.8953, 124.8965, 124.8949, 124.9128 | 124.8987 | 124.8953 | 124.8942 | 124.9128 | 0.0079 |
| A | published_per_query | 124.8942, 124.8953, 124.8965, 124.8949, 124.9128 | 124.8987 | 124.8953 | 124.8942 | 124.9128 | 0.0079 |
| A | expanded_per_query | 120.5911, 120.5821, 120.5793, 120.5972, 120.5845 | 120.5868 | 120.5845 | 120.5793 | 120.5972 | 0.0073 |
| A | cache_ready_per_query | 0, 0, 0, 0, 0 | 0 | 0 | 0 | 0 | 0 |
| A | cache_published_per_query | 0, 0, 0, 0, 0 | 0 | 0 | 0 | 0 | 0 |
| B | selected_per_query | 122.63, 122.674, 122.6836, 122.7095, 122.7122 | 122.6819 | 122.6836 | 122.63 | 122.7122 | 0.0333 |
| B | submitted_per_query | 122.63, 122.674, 122.6836, 122.7095, 122.7122 | 122.6819 | 122.6836 | 122.63 | 122.7122 | 0.0333 |
| B | cqe_seen_per_query | 122.63, 122.674, 122.6836, 122.7095, 122.7122 | 122.6819 | 122.6836 | 122.63 | 122.7122 | 0.0333 |
| B | published_per_query | 122.63, 122.674, 122.6836, 122.7095, 122.7122 | 122.6819 | 122.6836 | 122.63 | 122.7122 | 0.0333 |
| B | expanded_per_query | 118.6249, 118.663, 118.6482, 118.6742, 118.6789 | 118.6578 | 118.663 | 118.6249 | 118.6789 | 0.0219 |
| B | cache_ready_per_query | 0, 0, 0, 0, 0 | 0 | 0 | 0 | 0 | 0 |
| B | cache_published_per_query | 0, 0, 0, 0, 0 | 0 | 0 | 0 | 0 | 0 |
| C | selected_per_query | 122.6325, 122.6666, 122.6389, 122.6884, 122.6387 | 122.653 | 122.6389 | 122.6325 | 122.6884 | 0.0238 |
| C | submitted_per_query | 122.6325, 122.6666, 122.6389, 122.6884, 122.6387 | 122.653 | 122.6389 | 122.6325 | 122.6884 | 0.0238 |
| C | cqe_seen_per_query | 122.6325, 122.6666, 122.6389, 122.6884, 122.6387 | 122.653 | 122.6389 | 122.6325 | 122.6884 | 0.0238 |
| C | published_per_query | 122.6325, 122.6666, 122.6389, 122.6884, 122.6387 | 122.653 | 122.6389 | 122.6325 | 122.6884 | 0.0238 |
| C | expanded_per_query | 118.6037, 118.6201, 118.6247, 118.6536, 118.6222 | 118.6249 | 118.6222 | 118.6037 | 118.6536 | 0.0181 |
| C | cache_ready_per_query | 0, 0, 0, 0, 0 | 0 | 0 | 0 | 0 | 0 |
| C | cache_published_per_query | 0, 0, 0, 0, 0 | 0 | 0 | 0 | 0 | 0 |
| D | selected_per_query | 122.7718, 122.8212, 122.8377, 122.7543, 122.671 | 122.7712 | 122.7718 | 122.671 | 122.8377 | 0.0657 |
| D | submitted_per_query | 122.7718, 122.8212, 122.8377, 122.7543, 122.671 | 122.7712 | 122.7718 | 122.671 | 122.8377 | 0.0657 |
| D | cqe_seen_per_query | 122.7718, 122.8212, 122.8377, 122.7543, 122.671 | 122.7712 | 122.7718 | 122.671 | 122.8377 | 0.0657 |
| D | published_per_query | 122.7718, 122.8212, 122.8377, 122.7543, 122.671 | 122.7712 | 122.7718 | 122.671 | 122.8377 | 0.0657 |
| D | expanded_per_query | 118.7118, 118.7569, 118.7456, 118.6885, 118.6114 | 118.7028 | 118.7118 | 118.6114 | 118.7569 | 0.0579 |
| D | cache_ready_per_query | 0, 0, 0, 0, 0 | 0 | 0 | 0 | 0 | 0 |
| D | cache_published_per_query | 0, 0, 0, 0, 0 | 0 | 0 | 0 | 0 | 0 |
| E | selected_per_query | 121.4657, 121.5481, 121.5204, 121.3759, 121.5035 | 121.4827 | 121.5035 | 121.3759 | 121.5481 | 0.0668 |
| E | submitted_per_query | 121.4657, 121.5481, 121.5204, 121.3759, 121.5035 | 121.4827 | 121.5035 | 121.3759 | 121.5481 | 0.0668 |
| E | cqe_seen_per_query | 121.4657, 121.5481, 121.5204, 121.3759, 121.5035 | 121.4827 | 121.5035 | 121.3759 | 121.5481 | 0.0668 |
| E | published_per_query | 121.4657, 121.5481, 121.5204, 121.3759, 121.5035 | 121.4827 | 121.5035 | 121.3759 | 121.5481 | 0.0668 |
| E | expanded_per_query | 118.3812, 118.5178, 118.4677, 118.296, 118.4481 | 118.4222 | 118.4481 | 118.296 | 118.5178 | 0.0859 |
| E | cache_ready_per_query | 0, 0, 0, 0, 0 | 0 | 0 | 0 | 0 | 0 |
| E | cache_published_per_query | 0, 0, 0, 0, 0 | 0 | 0 | 0 | 0 | 0 |


| Sentinel/rep | Submitted = CQE = physical published | Expanded | Selected | Cache ready/published | Width increases | Max inflight/hidden |
| --- | --- | --- | --- | --- | --- | --- |
| A/1 | 1248942 | 1205911 | 1248942 | 0/0 | 277170 | 32/32 |
| A/2 | 1248953 | 1205821 | 1248953 | 0/0 | 277080 | 32/32 |
| A/3 | 1248965 | 1205793 | 1248965 | 0/0 | 277133 | 32/31 |
| A/4 | 1248949 | 1205972 | 1248949 | 0/0 | 277271 | 32/32 |
| A/5 | 1249128 | 1205845 | 1249128 | 0/0 | 277133 | 32/32 |
| B/1 | 1226300 | 1186249 | 1226300 | 0/0 | 254149 | 32/31 |
| B/2 | 1226740 | 1186630 | 1226740 | 0/0 | 254502 | 32/32 |
| B/3 | 1226836 | 1186482 | 1226836 | 0/0 | 254150 | 32/32 |
| B/4 | 1227095 | 1186742 | 1227095 | 0/0 | 254097 | 32/32 |
| B/5 | 1227122 | 1186789 | 1227122 | 0/0 | 255171 | 32/32 |
| C/1 | 1226325 | 1186037 | 1226325 | 0/0 | 263038 | 36/33 |
| C/2 | 1226666 | 1186201 | 1226666 | 0/0 | 263256 | 39/34 |
| C/3 | 1226389 | 1186247 | 1226389 | 0/0 | 262178 | 37/32 |
| C/4 | 1226884 | 1186536 | 1226884 | 0/0 | 263377 | 38/34 |
| C/5 | 1226387 | 1186222 | 1226387 | 0/0 | 262266 | 39/36 |
| D/1 | 1227718 | 1187118 | 1227718 | 0/0 | 255566 | 32/32 |
| D/2 | 1228212 | 1187569 | 1228212 | 0/0 | 255240 | 32/32 |
| D/3 | 1228377 | 1187456 | 1228377 | 0/0 | 256204 | 32/32 |
| D/4 | 1227543 | 1186885 | 1227543 | 0/0 | 255182 | 32/32 |
| D/5 | 1226710 | 1186114 | 1226710 | 0/0 | 253533 | 32/32 |
| E/1 | 1214657 | 1183812 | 1214657 | 0/0 | 119992 | 16/16 |
| E/2 | 1215481 | 1185178 | 1215481 | 0/0 | 119996 | 16/16 |
| E/3 | 1215204 | 1184677 | 1215204 | 0/0 | 119994 | 16/16 |
| E/4 | 1213759 | 1182960 | 1213759 | 0/0 | 119995 | 16/16 |
| E/5 | 1215035 | 1184481 | 1215035 | 0/0 | 119970 | 16/16 |


### Exact final-width distributions

Each entry is final W:query count within one 10K-query run. Counts are kept per run; pooling them would not add experimental repetitions.

| Sentinel/rep | Final W:count | Queries ending above 32 |
| --- | --- | --- |
| A/1 | 12:1, 15:1, 17:1, 18:3, 19:1, 20:2, 21:2, 22:1, 23:4, 24:10, 25:4, 26:13, 27:35, 28:91, 29:178, 30:378, 31:616, 32:8659 | 0 |
| A/2 | 11:1, 14:1, 17:2, 18:1, 19:3, 21:2, 22:3, 23:5, 24:3, 25:3, 26:18, 27:33, 28:86, 29:190, 30:402, 31:665, 32:8582 | 0 |
| A/3 | 14:1, 16:2, 17:2, 18:2, 19:3, 21:3, 22:2, 23:3, 24:4, 25:4, 26:7, 27:33, 28:97, 29:203, 30:370, 31:636, 32:8628 | 0 |
| A/4 | 11:1, 16:1, 17:2, 18:1, 20:4, 21:1, 22:2, 23:2, 24:3, 25:7, 26:11, 27:37, 28:67, 29:187, 30:390, 31:618, 32:8666 | 0 |
| A/5 | 12:1, 15:2, 17:2, 18:2, 19:2, 20:1, 21:2, 22:2, 23:2, 24:7, 25:8, 26:9, 27:33, 28:93, 29:189, 30:402, 31:583, 32:8660 | 0 |
| B/1 | 20:1, 21:12, 22:35, 23:81, 24:234, 25:393, 26:703, 27:930, 28:1087, 29:1210, 30:1114, 31:931, 32:3269 | 0 |
| B/2 | 16:1, 18:1, 20:1, 21:5, 22:27, 23:85, 24:194, 25:446, 26:691, 27:886, 28:1103, 29:1155, 30:1114, 31:1011, 32:3280 | 0 |
| B/3 | 16:1, 19:1, 20:3, 21:8, 22:35, 23:90, 24:222, 25:444, 26:626, 27:881, 28:1177, 29:1195, 30:1107, 31:985, 32:3225 | 0 |
| B/4 | 19:1, 20:3, 21:11, 22:26, 23:88, 24:212, 25:390, 26:713, 27:988, 28:1102, 29:1166, 30:1086, 31:959, 32:3255 | 0 |
| B/5 | 18:1, 21:8, 22:22, 23:91, 24:231, 25:391, 26:605, 27:880, 28:1048, 29:1212, 30:1103, 31:1039, 32:3369 | 0 |
| C/1 | 20:3, 21:10, 22:35, 23:92, 24:222, 25:432, 26:683, 27:873, 28:1096, 29:1121, 30:1131, 31:1018, 32:837, 33:641, 34:472, 35:386, 36:287, 37:199, 38:134, 39:95, 40:71, 41:56, 42:37, 43:26, 44:23, 45:8, 46:3, 47:3, 48:4, 51:2 | 2447 |
| C/2 | 18:1, 20:2, 21:6, 22:27, 23:90, 24:214, 25:401, 26:690, 27:909, 28:1122, 29:1173, 30:1116, 31:968, 32:818, 33:657, 34:459, 35:367, 36:280, 37:176, 38:165, 39:109, 40:94, 41:52, 42:41, 43:25, 44:10, 45:12, 46:7, 47:5, 48:2, 49:1, 51:1 | 2463 |
| C/3 | 13:1, 17:1, 19:1, 20:2, 21:8, 22:31, 23:89, 24:226, 25:482, 26:686, 27:912, 28:1098, 29:1151, 30:1115, 31:1010, 32:815, 33:607, 34:467, 35:383, 36:258, 37:222, 38:117, 39:108, 40:64, 41:44, 42:31, 43:28, 44:15, 45:15, 46:4, 47:4, 48:3, 49:1, 51:1 | 2372 |
| C/4 | 20:1, 21:6, 22:27, 23:96, 24:219, 25:400, 26:682, 27:935, 28:1125, 29:1103, 30:1103, 31:1010, 32:803, 33:659, 34:493, 35:359, 36:249, 37:211, 38:182, 39:100, 40:73, 41:55, 42:42, 43:19, 44:16, 45:13, 46:5, 47:6, 48:2, 49:3, 50:2, 52:1 | 2490 |
| C/5 | 21:8, 22:41, 23:85, 24:222, 25:419, 26:692, 27:922, 28:1167, 29:1173, 30:1150, 31:1003, 32:767, 33:565, 34:462, 35:339, 36:296, 37:232, 38:145, 39:95, 40:75, 41:60, 42:28, 43:16, 44:16, 45:11, 46:1, 47:5, 48:3, 50:1, 51:1 | 2351 |
| D/1 | 15:12, 16:9, 17:7, 18:5, 19:7, 20:7, 21:25, 22:51, 23:115, 24:205, 25:361, 26:567, 27:799, 28:992, 29:1106, 30:1057, 31:952, 32:3723 | 0 |
| D/2 | 15:14, 16:11, 17:4, 18:8, 19:7, 20:5, 21:16, 22:50, 23:107, 24:174, 25:387, 26:628, 27:789, 28:1052, 29:1099, 30:1061, 31:943, 32:3645 | 0 |
| D/3 | 15:28, 16:20, 17:16, 18:5, 19:5, 20:7, 21:11, 22:33, 23:74, 24:171, 25:328, 26:556, 27:796, 28:983, 29:1106, 30:1100, 31:994, 32:3767 | 0 |
| D/4 | 15:17, 16:9, 17:13, 18:10, 19:3, 20:10, 21:20, 22:42, 23:127, 24:225, 25:354, 26:585, 27:792, 28:1005, 29:1053, 30:1061, 31:1059, 32:3615 | 0 |
| D/5 | 13:1, 15:14, 16:8, 17:16, 18:12, 19:18, 20:20, 21:34, 22:76, 23:150, 24:261, 25:410, 26:620, 27:783, 28:970, 29:1069, 30:1054, 31:928, 32:3556 | 0 |
| E/1 | 15:8, 16:9992 | 0 |
| E/2 | 15:4, 16:9996 | 0 |
| E/3 | 15:6, 16:9994 | 0 |
| E/4 | 15:5, 16:9995 | 0 |
| E/5 | 15:30, 16:9970 | 0 |


MEASURED FACT: W64 final maximum is 51–52 across repetitions, no query ends at 64, and 23.51–24.90% end above 32. Its maximum observed inflight is 36–39, below the CLI cap and below the largest final width. T16/W16 final W is 15–16, with essentially all queries ending at16. These are endpoint/extreme observations, not time residency or evidence of frontier redundancy.

## Host / kernel / NVMe diagnostics

MEASURED FACT: mpstat/pidstat/iostat were available for every run; raw logs retained. The following are arithmetic means of available one-second samples **within each run**, including loading/startup/partial search intervals. Device metrics cover the whole NVMe device and other workloads. CPU/process percentages follow multicore sysstat conventions; process CPU can exceed100%. No precise steady-state average or causality is inferred from these short windows.

| Sentinel/rep | CPU usr% | sys% | idle% | Process CPU% | NVMe read IOPS | Read KiB/s | r_await ms | aqu-sz | util% | Samples CPU/process/NVMe | Span CPU/NVMe s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A/1 | 7.1109 | 5.16 | 87.6682 | 195.1818 | 105778.2727 | 423118.1818 | 0.0627 | 6.8718 | 75.5091 | 11/11/11 | 10.0/10.0 |
| A/2 | 6.2164 | 5.0682 | 88.6236 | 195.1818 | 106124.3636 | 424502.1818 | 0.0609 | 6.9 | 75.7818 | 11/11/11 | 10.0/10.0 |
| A/3 | 7.8145 | 5.1891 | 86.9382 | 195.7273 | 105999.6364 | 424001.8182 | 0.0609 | 6.8718 | 75.4182 | 11/11/11 | 10.0/10.0 |
| A/4 | 7.8145 | 5.25 | 86.8373 | 195.18 | 105554.8745 | 422223.4964 | 0.0627 | 6.89 | 75.6264 | 11/11/11 | 10.0/10.0 |
| A/5 | 7.3573 | 5.1518 | 87.3427 | 195.4545 | 105971.1818 | 423936.3636 | 0.0618 | 6.8745 | 76.3273 | 11/11/11 | 10.0/10.0 |
| B/1 | 38 | 35.9733 | 25.99 | 1443.3333 | 355868.6667 | 1423502.6667 | 0.11 | 39.07 | 67.9333 | 3/3/3 | 2.0/2.0 |
| B/2 | 41.6633 | 35.0733 | 23.1767 | 1404.5267 | 347045.06 | 1388204.17 | 0.1067 | 37.4533 | 71.7967 | 3/3/3 | 2.0/2.0 |
| B/3 | 44.6667 | 35.75 | 19.5267 | 1414.1733 | 345359.4867 | 1381455.2067 | 0.11 | 37.8667 | 70.2633 | 3/3/3 | 2.0/2.0 |
| B/4 | 38.15 | 35.9667 | 25.8133 | 1441.6667 | 355099.3333 | 1420410.6667 | 0.11 | 38.96 | 70.8 | 3/3/3 | 2.0/2.0 |
| B/5 | 41.2767 | 32.8833 | 25.8367 | 1378.6667 | 342605 | 1370442.6667 | 0.1033 | 36.1133 | 68.8667 | 3/3/3 | 2.0/2.0 |
| C/1 | 40.7733 | 35.5567 | 23.6667 | 1424 | 349511.3333 | 1398066.6667 | 0.11 | 38.37 | 67.9 | 3/3/3 | 2.0/2.0 |
| C/2 | 39.8467 | 35.8267 | 24.2767 | 1432.6667 | 352055 | 1408244 | 0.11 | 38.7 | 72.1333 | 3/3/3 | 2.0/2.0 |
| C/3 | 39.6333 | 36.1367 | 24.1967 | 1439.71 | 353699.8933 | 1414818.2033 | 0.11 | 38.8567 | 70.0267 | 3/3/3 | 2.0/2.0 |
| C/4 | 41.7433 | 36.0833 | 22.14 | 1426.6667 | 351010 | 1404057.3333 | 0.11 | 38.3667 | 70.1667 | 3/3/3 | 2.0/2.0 |
| C/5 | 39.7567 | 35.82 | 24.4233 | 1437.3333 | 354530 | 1418156 | 0.11 | 38.9033 | 68.5667 | 3/3/3 | 2.0/2.0 |
| D/1 | 52.0367 | 40.09 | 7.84 | 1749.3333 | 310928 | 1243733.3333 | 0.0967 | 30.1667 | 67.8 | 3/3/3 | 2.0/2.0 |
| D/2 | 45.5667 | 45.9333 | 8.5 | 1780 | 312568.38 | 1250309.3867 | 0.0967 | 30.51 | 73.0267 | 3/3/3 | 2.0/2.0 |
| D/3 | 45.9267 | 45.4967 | 8.5433 | 1753 | 303757.3333 | 1215050.6667 | 0.0967 | 29.1367 | 69.1667 | 3/3/3 | 2.0/2.0 |
| D/4 | 46.5075 | 46.2075 | 7.27 | 1768 | 306877.75 | 1227545 | 0.095 | 29.2475 | 69.35 | 4/4/4 | 3.0/3.0 |
| D/5 | 46.1033 | 45.8067 | 8.0767 | 1738.6667 | 307283.3333 | 1229194.6667 | 0.0967 | 29.4333 | 70.0333 | 3/3/3 | 2.0/2.0 |
| E/1 | 46.0275 | 47.08 | 6.8275 | 1743.34 | 303086.55 | 1212367.1875 | 0.09 | 27.905 | 74.3575 | 4/4/4 | 3.0/3.0 |
| E/2 | 49.4 | 42.22 | 8.2633 | 1759.0367 | 307666.7133 | 1230678.8133 | 0.0967 | 29.0167 | 73.14 | 3/3/3 | 2.0/2.0 |
| E/3 | 45.4267 | 46.31 | 8.2633 | 1733.6467 | 305012.6667 | 1220065.3333 | 0.09 | 28.71 | 69.1333 | 3/3/3 | 2.0/2.0 |
| E/4 | 43.35 | 48.1033 | 8.5467 | 1781.58 | 310434.38 | 1241753.4667 | 0.0933 | 29.4767 | 69.01 | 3/3/3 | 2.0/2.0 |
| E/5 | 49.2875 | 44.0425 | 6.645 | 1781.25 | 303210.4925 | 1212853.96 | 0.09 | 28.01 | 70.8225 | 4/4/4 | 3.0/3.0 |


Coverage: A has 11 samples/series and 10s first-to-last span (nominal 11 one-second intervals); B/C have 3 samples and 2s span; D/E have 3–4 samples and 2–3s span. Exact local timestamps per series, nominal interval coverage, collector UTC start/end and raw log paths are in analysis_verified/analysis.json and local manifest. Nominal coverage is not fraction of the search-only phase: collector boundaries include other process phases, and partial intervals are not resolved. No estimates are upgraded to steady-state precision. External thread pidstat similarly provides only a few records, not complete worker residency.

| Sentinel/rep | Process voluntary cs/s | Process involuntary cs/s | Thread entities observed | Process cs samples |
| --- | --- | --- | --- | --- |
| A/1 | 0.0909 | 2.6282 | 3 | 11 |
| A/2 | 0 | 8.4545 | 3 | 11 |
| A/3 | 0 | 3.4545 | 3 | 11 |
| A/4 | 0 | 5.2727 | 3 | 11 |
| A/5 | 0 | 5.9091 | 3 | 11 |
| B/1 | 1 | 3.3333 | 17 | 3 |
| B/2 | 2 | 3.6667 | 17 | 3 |
| B/3 | 1.3333 | 15.3333 | 17 | 3 |
| B/4 | 1.3333 | 6.3233 | 17 | 3 |
| B/5 | 1.6667 | 3.3333 | 17 | 3 |
| C/1 | 1 | 1.9933 | 17 | 3 |
| C/2 | 1 | 3.6567 | 17 | 3 |
| C/3 | 1 | 5.6667 | 17 | 3 |
| C/4 | 1 | 8.3333 | 17 | 3 |
| C/5 | 1.3333 | 3 | 17 | 3 |
| D/1 | 1 | 125.3333 | 33 | 3 |
| D/2 | 1.6667 | 132 | 33 | 3 |
| D/3 | 1.3333 | 111.3333 | 33 | 3 |
| D/4 | 2.6667 | 4116.6667 | 33 | 3 |
| D/5 | 1.65 | 176.5 | 33 | 3 |
| E/1 | 2.31 | 205.8333 | 33 | 3 |
| E/2 | 1.6667 | 115.3333 | 33 | 3 |
| E/3 | 1.3333 | 147.8367 | 33 | 3 |
| E/4 | 2 | 1793.5633 | 33 | 3 |
| E/5 | 1.6667 | 3041 | 33 | 3 |


Context-switch rates above are process rows from the external observer; per-thread rates/CPU remain in raw pidstat_threads.log and analysis thread_telemetry. They are separate from cumulative task-status counters in snapshots. A process row cannot summarize all worker/kernel switching.

| Sentinel/rep | Snapshots | iou-sqp counts | iou-wrk counts | Matched worker allowed CPUs | Matched worker last CPUs | Captured SQPOLL allowed CPUs | Snapshots with io_uring fdinfo |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A/1 | 2 | 0,1 | 0,0 | 0-19 | 4,5 | 0-19 | 2 |
| A/2 | 2 | 0,1 | 0,0 | 0-19 | 4 | 0-19 | 2 |
| A/3 | 2 | 0,1 | 0,0 | 0-19 | 8 | 0-19 | 2 |
| A/4 | 2 | 0,1 | 0,0 | 0-19 | 4 | 0-19 | 2 |
| A/5 | 2 | 0,1 | 0,0 | 0-19 | 4 | 0-19 | 2 |
| B/1 | 2 | 8,8 | 0,0 | 0-19 | 4,6,8,12,13,16,17,19 | 0-19 | 2 |
| B/2 | 2 | 8,8 | 0,0 | 0-19 | 0,4,6,8,10,12,13,15,17 | 0-19 | 2 |
| B/3 | 2 | 8,8 | 0,0 | 0-19 | 0,1,2,5,7,9,10,12,13,14,15 | 0-19 | 2 |
| B/4 | 2 | 8,8 | 0,0 | 0-19 | 0,2,4,6,8,12,13,14,18 | 0-19 | 2 |
| B/5 | 2 | 8,8 | 0,0 | 0-19 | 0,2,4,6,8,9,10,13 | 0-19 | 2 |
| C/1 | 2 | 8,8 | 0,0 | 0-19 | 2,4,6,9,12,13,14,16 | 0-19 | 2 |
| C/2 | 2 | 8,8 | 0,0 | 0-19 | 0,1,4,6,9,11,12,14,15,17 | 0-19 | 2 |
| C/3 | 2 | 8,8 | 0,0 | 0-19 | 0,2,3,4,8,10,12,13,18 | 0-19 | 2 |
| C/4 | 2 | 8,8 | 0,0 | 0-19 | 0,1,3,4,8,10,13,14,16 | 0-19 | 2 |
| C/5 | 2 | 8,8 | 0,0 | 0-19 | 2,4,6,8,9,10,12,13,19 | 0-19 | 2 |
| D/1 | 2 | 16,16 | 0,0 | 0-19 | 0,2,3,4,5,6,7,9,12,13,14,15,16,17,18,19 | 0-19 | 2 |
| D/2 | 2 | 16,16 | 0,0 | 0-19 | 0,1,3,6,7,8,10,11,12,14,16,17,18,19 | 0-19 | 2 |
| D/3 | 2 | 16,16 | 0,0 | 0-19 | 0,1,2,3,4,5,6,7,9,11,12,13,14,17,18,19 | 0-19 | 2 |
| D/4 | 2 | 16,16 | 0,0 | 0-19 | 0,1,3,4,5,6,7,8,9,10,11,14,15,16,17,18,19 | 0-19 | 2 |
| D/5 | 2 | 16,16 | 0,0 | 0-19 | 1,2,3,4,5,7,8,9,10,12,14,15,16,18,19 | 0-19 | 2 |
| E/1 | 2 | 16,16 | 0,0 | 0-19 | 0,1,2,3,4,6,8,9,10,11,12,13,14,16,17,18 | 0-19 | 2 |
| E/2 | 2 | 16,16 | 0,0 | 0-19 | 0,1,2,4,6,7,8,9,10,11,12,13,14,15,16,17,18,19 | 0-19 | 2 |
| E/3 | 2 | 16,16 | 0,0 | 0-19 | 0,1,2,3,4,5,6,7,8,9,11,13,14,16,17,18,19 | 0-19 | 2 |
| E/4 | 2 | 16,16 | 0,0 | 0-19 | 2,3,4,5,6,7,8,11,12,13,14,16,17,18,19 | 0-19 | 2 |
| E/5 | 2 | 16,16 | 0,0 | 0-19 | 0,1,2,3,4,5,6,7,8,9,10,15,16,17,18,19 | 0-19 | 2 |


Workers are matched by Linux TIDs from query counter records, not guessed from non-iou task names. RequestedT has corresponding observed query worker identities. SQPOLL task counts are direct ps observations: T8 snapshots show 8, T16 show 16; T1 shows 0 at the first/loading snapshot and 1 at the second. This is not a universal one-kernel-thread-per-worker inference. No iou-wrk row appeared in these snapshots; absence between snapshots is unknown. All worker masks observed are 0-19, consistent with unbound eligibility, not proof of equal CPU residency. Captured iou-sqp masks are also0-19. Last-CPU snapshots show movement across the eligible set but cannot measure migration rates. io_uring fdinfo was readable in 50/50 snapshots; its full text is preserved, not treated as device timing.

| Sentinel/rep | Pre-run load1 | Pre-run MemAvailable | Package temperature snapshot range °C | Policy0 frequency snapshot range MHz |
| --- | --- | --- | --- | --- |
| A/1 | 1.67 | 10044520 kB | 68–86 | 448.99–4219.975 |
| A/2 | 9.03 | 10168504 kB | 58–90 | 892.63–4587.912 |
| A/3 | 9.33 | 10117964 kB | 69–92 | 400.06–3452.653 |
| A/4 | 9.80 | 10243912 kB | 58–96 | 400.153–4394.594 |
| A/5 | 9.05 | 10220728 kB | 71–92 | 400–4277.39 |
| B/1 | 1.52 | 10130008 kB | 56–94 | 400–4099.958 |
| B/2 | 4.53 | 10121332 kB | 63–89 | 399.348–4100 |
| B/3 | 7.29 | 10052852 kB | 61–90 | 726.45–3284.984 |
| B/4 | 7.50 | 10251472 kB | 60–92 | 858.468–4070.454 |
| B/5 | 7.33 | 10211996 kB | 58–91 | 667.543–4055.655 |
| C/1 | 2.46 | 10148032 kB | 58–83 | 400–4403.846 |
| C/2 | 4.06 | 10249416 kB | 58–84 | 400–3200 |
| C/3 | 6.97 | 10268356 kB | 57–100 | 522.2–4100.041 |
| C/4 | 7.61 | 10245400 kB | 57–98 | 675.472–4099.958 |
| C/5 | 6.94 | 10222292 kB | 58–86 | 400–4099.958 |
| D/1 | 3.42 | 10101380 kB | 55–87 | 847.844–3200.032 |
| D/2 | 4.85 | 10244312 kB | 58–87 | 434.601–3299.966 |
| D/3 | 7.38 | 10227636 kB | 58–87 | 1312.142–4350.129 |
| D/4 | 6.64 | 10226312 kB | 65–90 | 486.615–3200 |
| D/5 | 6.02 | 10178292 kB | 73–88 | 441.317–3291.199 |
| E/1 | 5.55 | 10056924 kB | 58–87 | 1271.408–3477.971 |
| E/2 | 7.43 | 10122296 kB | 64–88 | 885.288–3200 |
| E/3 | 8.56 | 10185276 kB | 60–87 | 691.086–3200 |
| E/4 | 8.27 | 10203708 kB | 59–88 | 529.094–3200 |
| E/5 | 8.14 | 10186436 kB | 60–88 | 413.317–3200.032 |


Governor powersave, EPP balance_performance, policy0 maximum 4600MHz; NVMe scheduler [none] mq-deadline (active none). RAM/swap, all-policy current/max frequencies, thermal-zone types, NVMe queue attributes and readable power-limit settings are retained before/after every run and in runtime snapshots. Temperature/frequency ranges above cover only four snapshots/run, not a continuous thermal/frequency trajectory; policy0 is not all hybrid cores. Load is a one-minute host average. Settings were recorded, not changed.

## Primary comparisons

DERIVED METRIC: target-vs-reference percent change of configuration **medians**; recall difference is percentage points. These descriptive comparisons retain five-run variability shown above; they are neither paired-E0 equivalence gates nor independent-request inference.

| Target vs reference | QPS Δ% | Mean latency Δ% | P99 Δ% | Recall Δpp | Mean I/O Δ% |
| --- | --- | --- | --- | --- | --- |
| C_vs_B | 0.6539 | -0.582 | -2.3767 | 0.01 | -0.0326 |
| D_vs_B | -13.2535 | 130.631 | 786.9134 | 0 | 0.0734 |
| E_vs_D | -1.6961 | 1.3534 | 2.6424 | -0.01 | -1.0345 |
| B_vs_A | 254.808 | 126.2979 | 149.9248 | -0.02 | -1.7774 |


- **T8/W32 → T8/W64:** QPS+0.65%, mean latency−0.58%, P99−2.38%, mean I/O−0.03%. These differences are small relative to some five-run variation; no performance gain is established. About24% of queries end above 32, none reach64; actual width residence is unknown. CPU sys is about35–36%, NVMe sampled IOPS/await/queue are similar. No frontier-redundancy or D6 timing claim follows.
- **T8/W32 → T16/W32:** QPS−13.25%, mean latency+130.63%, median P99+786.91%, mean I/O+0.07%. Final-width means remain around29.4–29.5 while sys rises to roughly40–46% and idle falls to roughly7–9%;16 SQPOLL tasks are observed instead of8. NVMe sampled read IOPS/queue decrease, with r_await around0.095–0.097ms versus0.103–0.110ms. **INTERPRETATION:** consistent with greater host/kernel pressure, not proof of its cause and not evidence that the SSD is saturated. Scheduler/load/frequency/power/cache contributions remain unresolved.
- **T16/W32 → T16/W16:** median QPS−1.70%, mean latency+1.35%, P99+2.64%, mean I/O−1.03%. Actual final width becomes essentially16, and inflight/hidden extrema halve to 16. Sampled host sys/idle remains pressured; broad performance improvement is not demonstrated. A cap change is a diagnostic configuration, not a new algorithm.
- **T1/W32 → T8/W32:** median QPS+254.81% (3.55×), mean latency+126.30%, P99+149.92%, mean I/O−1.78%. End-at-Wcap fraction falls from about86.6% to32.7%. Host idle declines markedly and NVMe read IOPS rises. Scaling is descriptive; no linear-scaling assumption or dependency-starvation conclusion is justified.

## D6, D1 and next measurement

**D6_INCONCLUSIVE** by the LIGHT-only contract. Max completed_hidden is 32 at capped W32, 32–36 for W64 and 16 at W16; it shows completion/publication backlog extrema, not per-request CQE-to-publication HOL latency or duration. No D6_MATERIAL/LOW label is assigned. IO_SUBMIT timing remains after SQE preparation immediately before io_uring_submit, and IO_CQE_SEEN remains userspace poll processing; their interval is **userspace-observed I/O**, not hardware device latency. No timing hook changed.

**D1 observability NO:** current signals cannot distinguish dependency starvation from I/O waiting, FIFO-hidden completion, published-but-not-calc-ready state and ready-unselected work; low inflight alone is insufficient. [Existing gap](D1_OBSERVABILITY_GAP.md) remains unchanged. **D4 selector gate NOT TESTED.**

**UNRESOLVED HYPOTHESIS:** precise causes of T16 tail/throughput behavior and publication HOL duration. No frontier-level selection evidence or steady-state width timeline exists in LIGHT. Recommended next task is a separately reviewed G0-C sampling/protocol issue, using deterministic later/distributed qids with complete lifecycle/zero-loss checks and a new binary comparability check if sampling code changes. [G0-C sampling design](G0C_DETAIL_SAMPLING_REQUIREMENTS.md) proposes the minimum hooks and validation; it is not implemented or executed.

## Reproduction, tests and scope

```sh
.venv-research/bin/python -m unittest discover -s tests/research -v
git diff --check
.venv-research/bin/python tools/research/analyze_g0b_light.py \
  --campaign ~/ann-research/research-v3/campaigns/G0B_SIFT10M_20261009T063743710720Z \
  --output /path/to/new/analysis-directory
```

**213 Python tests PASS** (180 existing +33 new), including frozen order/missing run/configuration/package/provenance/trace failures, full-query checks, actual-width/count aggregation, physical-vs-cache conservation, matched host telemetry, run-level SD, invalid campaign, worker/TID consistency, midnight/time-only and ISO telemetry timestamps. Historical E0b/E0c code/results are unchanged. Full-content audits and checksum validations are independent acceptance evidence; no real dataset is needed for unit tests.

analysis_v1/ preserved a derived analyzer rejection because iostat uses ISO timestamps while mpstat uses time-only timestamps. The parser was corrected with a synthetic ISO regression; analysis_v2 and final succeeded. This was an analysis-only bug, not a measurement/protocol amendment; frozen plan, order, thresholds, local runs and all observed bytes stayed unchanged.

Only analyzer, synthetic tests, small frozen plan/report and design document are tracked. No ANN source, FIFO, width heuristic, candidate/search order, graph or io_uring modification; no D1/D4, no G0-C execution, no SIFT100M, no data/index rebuild, no large artifacts committed, main untouched. Stop after Draft PR.

## Run / MLflow inventory

Every run has benchmark_status=success, trace_valid=true, run_status=success, native exit0, runner exit0 and mlflow_status=success. Local authoritative directory is ~/ann-research/research-v3/runs/<run_id>/.

| Execution | Round/config | Run ID | MLflow ID |
| --- | --- | --- | --- |
| 1 | 1/A | `P0_sift10m_T1_W32_LIGHT_R001_20261009T063826886345Z_bcd31635d95944f99e86111ea17651e1` | `04418edad5be470f93cb43c2cd8e8c3d` |
| 2 | 1/B | `P0_sift10m_T8_W32_LIGHT_R001_20261009T063845860988Z_cedcad2e49154493972307363f86a068` | `957b2c458f21481dac4b0e91df335345` |
| 3 | 1/C | `P0_sift10m_T8_W64_LIGHT_R001_20261009T063856505584Z_78adaa564a404b11aebdaba94e7b0e15` | `3a638e6a72834d8fb156db9173a0b794` |
| 4 | 1/D | `P0_sift10m_T16_W32_LIGHT_R001_20261009T063907240166Z_9bdfdc5309854ffc856e137a25745a70` | `d4a3ede0fddf4d8eb3af705fcc6974f0` |
| 5 | 1/E | `P0_sift10m_T16_W16_LIGHT_R001_20261009T063918474319Z_c8569c189a124690b4de5669582af1b9` | `17b4a6d063224f5ca75627bc7d1f8438` |
| 6 | 2/B | `P0_sift10m_T8_W32_LIGHT_R002_20261009T063929642750Z_9e87708f2bca47cea4b6358da8f69a8d` | `96ae276cf79c44468cfbd1bec39a53f8` |
| 7 | 2/C | `P0_sift10m_T8_W64_LIGHT_R002_20261009T063940354311Z_035e15e113844b889a873dc0f21e559a` | `75a82c9327f348f58d0715b634ef1d46` |
| 8 | 2/D | `P0_sift10m_T16_W32_LIGHT_R002_20261009T063951104523Z_25c38090dfb1470a9d40041989e1eef6` | `8d5cfd735dc045e39410a37211a3b64f` |
| 9 | 2/E | `P0_sift10m_T16_W16_LIGHT_R002_20261009T064002290816Z_4f607fc7ca49430da1bee3625057cde3` | `237050eee821479d87880880b064793f` |
| 10 | 2/A | `P0_sift10m_T1_W32_LIGHT_R002_20261009T064013430999Z_de373827c5704db8823bf76de8d50b64` | `445485b801f649d68757f369cb3fb2aa` |
| 11 | 3/C | `P0_sift10m_T8_W64_LIGHT_R003_20261009T064032383296Z_378f8c18919a4706907a105ec840c68e` | `4996eff77b1c45b7af2725d94b184a99` |
| 12 | 3/D | `P0_sift10m_T16_W32_LIGHT_R003_20261009T064043071492Z_d21fd0ccdc5149848727d18c4947acb1` | `49387766839b4e24a65a905ace2185c6` |
| 13 | 3/E | `P0_sift10m_T16_W16_LIGHT_R003_20261009T064054326075Z_afd64390c71944df95b7718ee6fd6ccf` | `520bc54113c94229832768e9dbf37a06` |
| 14 | 3/A | `P0_sift10m_T1_W32_LIGHT_R003_20261009T064105565169Z_429e864c6ebd498087bc149c7e29223f` | `23f8efd9c9454fe4a22803c924d27105` |
| 15 | 3/B | `P0_sift10m_T8_W32_LIGHT_R003_20261009T064124511891Z_8f6ed90c2a974b3b8fd3e628ec0301aa` | `365072807cb745a1ac1bd8d614eb4b62` |
| 16 | 4/D | `P0_sift10m_T16_W32_LIGHT_R004_20261009T064135248941Z_6553d42cff4f493cabc6063781e921b2` | `8259bca3ac4e4597a12c2e093e67ddb8` |
| 17 | 4/E | `P0_sift10m_T16_W16_LIGHT_R004_20261009T064146497543Z_96d11d445f1948b696b56e50bfe173fa` | `9ad0049c6bae4f429899d9b957e0b6ad` |
| 18 | 4/A | `P0_sift10m_T1_W32_LIGHT_R004_20261009T064157625907Z_5650d13568d94e5e9248b1bc0ec35385` | `382e1d4a29a4404aa945c1e3f91ba006` |
| 19 | 4/B | `P0_sift10m_T8_W32_LIGHT_R004_20261009T064216669474Z_b9a7b8cda1114ff8897acbcf886e2af8` | `f1b7dbe8810f4e558bc6c2bbf6716656` |
| 20 | 4/C | `P0_sift10m_T8_W64_LIGHT_R004_20261009T064227310734Z_bd3a2d83af014c148399efdb29312c8f` | `444ef4f5a89d4fed98e59b52bf082ce0` |
| 21 | 5/E | `P0_sift10m_T16_W16_LIGHT_R005_20261009T064238070119Z_12e3317b6a1a4b8a8fb405eb60be2911` | `9b28aa6abca3420f9bf2d1bb148662a9` |
| 22 | 5/A | `P0_sift10m_T1_W32_LIGHT_R005_20261009T064249300285Z_707b580975684244ad30ecf823c37c11` | `0c3561a7e17d4a2ab8737f4e969e4e50` |
| 23 | 5/B | `P0_sift10m_T8_W32_LIGHT_R005_20261009T064308358961Z_08a5c4aeb44d445fa6a68e96b8f619b5` | `a2224d37bdd846ac963b97c56d12deb5` |
| 24 | 5/C | `P0_sift10m_T8_W64_LIGHT_R005_20261009T064319116722Z_f07ebcde1f6349618c97416258877718` | `50a8f63ea6a34340ac13ce7d9a79331a` |
| 25 | 5/D | `P0_sift10m_T16_W32_LIGHT_R005_20261009T064329745071Z_1d8c1955e00349f892bfc4bbca5e4791` | `9aeb70d69cc04e7aa9e1fb1f591c2120` |
