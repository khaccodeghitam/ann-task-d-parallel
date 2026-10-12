# Stock-like benchmark results: NOT_MEASURED

**DIRECT MEASUREMENT:**0 accepted searches,0 invalid searches,0 incomplete searches,66 NOT_RUN. Two interrupted constructions are separate evidence. No warmup, correctness search, primary block, curve or width case ran.

| Subject | T | Wcap | Completed repetitions | Recall@10 | Median QPS | Mean query latency | Tail |
|---|---:|---:|---:|---|---|---|---|
|Portable paper|1|32|0|NOT_MEASURED|NOT_MEASURED|NOT_MEASURED|P99.9 NOT_MEASURED|
|Portable paper|4|32|0|NOT_MEASURED|NOT_MEASURED|NOT_MEASURED|P99.9 NOT_MEASURED|
|Portable paper|8|32|0|NOT_MEASURED|NOT_MEASURED|NOT_MEASURED|P99.9 NOT_MEASURED|
|Portable paper|16|32|0|NOT_MEASURED|NOT_MEASURED|NOT_MEASURED|P99.9 NOT_MEASURED|
|Modern golden|8|32|0|NOT_MEASURED|NOT_MEASURED|NOT_MEASURED|P99 NOT_MEASURED|
|Modern golden|16|32|0|NOT_MEASURED|NOT_MEASURED|NOT_MEASURED|P99 NOT_MEASURED|

Paper T16/T8 effect and CI90 are null. No modern/paper speedup or recall-matched curve exists. [runs.csv](runs.csv) enumerates all66 unexecuted cases, with absent run IDs and blank metrics. [stats.csv](stats.csv) has n=0 and blank estimates for every planned regime. Zero completed repetitions is not zero QPS/recall/latency.

Stock QPS source timer surrounds the parallel query loop and its barrier, excluding loading/warmups/recall/teardown. Mean latency is mean QueryStats.total_us, a different per-query scope. Printed tail is not normalized; paper uses0.999 and modern0.99. Mean IO is application request/sector accounting, not device latency/IOPS. Printed mean_hops0 in the paper PipeSearch path is not a measured expansion count.

Build mpstat/pidstat/iostat and host/task snapshots are retained locally. They do not constitute search CPU/NVMe/SQPOLL evidence. No available metric is repurposed from a failed build or from the historical modern quiet campaign. All search resource statistics, actual-width trajectories and expansions remain NOT_MEASURED.
