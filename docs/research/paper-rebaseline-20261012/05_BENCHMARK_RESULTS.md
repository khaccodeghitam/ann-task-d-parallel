# Benchmark results — absence recorded explicitly

**DIRECT MEASUREMENT:** zero new ANN runs invoked. Accepted0, invalid0,
incomplete0, planned-not-run66. Build failure exit2 is not a failed benchmark.
No correctness smoke, common-index loading run, native-index build, L sweep,
width sweep or diagnostic ANN smoke completed. No MLflow run was created.

| Cell / W32 L100 | n | QPS median | Recall@10 | Mean latency µs | Correct tail name | Tail µs |
| --- | --- | --- | --- | --- | --- | --- |
| PAPER_T1 | 0 | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | P99.9 | NOT_MEASURED |
| PAPER_T4 | 0 | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | P99.9 | NOT_MEASURED |
| PAPER_T8 | 0 | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | P99.9 | NOT_MEASURED |
| PAPER_T16 | 0 | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | P99.9 | NOT_MEASURED |
| MODERN_T8 | 0 | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | P99 | NOT_MEASURED |
| MODERN_T16 | 0 | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | P99 | NOT_MEASURED |

Every mean/median/SD/MAD/CI/paired effect, curve and width sensitivity for this
task is NOT_MEASURED. Machine-readable numeric fields are null/empty, never0
to represent an absent metric. RUN_INDEX.csv contains66 **planned** cells with
status NOT_RUN and empty run_id; RUN_METRICS.csv has a header and zero records.
PAIRED_RESULTS/SCALING_SUMMARY/RECALL_QPS_CURVES retain explicit availability/n0.
The helper never calculates bootstrap statistics from this empty campaign.

**UNKNOWN:** actual artifact T16/T8 behavior. The old golden quiet campaign
`QUIET_STOCK_SIFT10M_20261010T063747348821Z` reports12 accepted runs,
median−8.50956284%, CI90[−10.58633478,−6.33176694] under its own Performance Mode/
quiet protocol. Its stored classification is MATERIAL_REGRESSION_OBSERVED.
This context was read, not rerun or independently requalified for the paper.
It is not paired evidence in this new suite and does not predict paper scaling.

## Metric semantics established from source

**VERIFIED SOURCE FACT:** paper [driver](https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/tests/search_disk_index.cpp#L136-L207)
starts the timer immediately before the selected search parallel loop, ends
after its implicit barrier, QPS=Nq/duration. It excludes loading, warmups,
post-timer result conversion/recall/printing. Per-query total_us measures a
different interval in pipe_search; process wall-time is not QPS denominator.
Mean latency is from QueryStats, not10000/QPS. Driver ignores returned search
count; therefore successful exit/row alone cannot prove all K outputs valid.

Paper printed“P99 Lat” is **P99.9** (0.999f), modern is **P99** (0.99f).
[percentile_stats.h](https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/include/percentile_stats.h#L40-L53) sorts values
and indexes the integer truncation of p×N; it is not the bootstrap interpolation
convention. P50/P95 and the other version's tail are NOT_MEASURED. No raw latency
sample exporter was implemented, so normalized tails cannot be compared.

[calculate_recall](https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/src/aux_utils.cpp#L107-L136) constructs sets,
extends GT equal-distance ties at the Kth boundary, and divides summed hits by
Nq×K, reporting percent. This verified definition is required on both paths.
Mean I/O is request count in artifact; modern counts sectors from read_io_size.
Cache and physical I/O must remain distinguishable. Artifact n_hops is not
incremented in the audited pipe path: a printed0 does not prove zero expansions.
Neither CQE interval nor device-wide r_await is interchangeable with hardware
service time or query-critical latency.

CPU/NVMe/SQPOLL/runtime thermal metrics **during this benchmark suite** are
NOT_MEASURED. Host observations only cover passive preparation. No observer
overhead, warmup equivalence, recall quality or native-index speedup is claimed.
No paper100M/1B throughput number was reproduced on this SIFT10M laptop.
