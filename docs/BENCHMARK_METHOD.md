# Paper-native paired benchmark protocol

This page retains the PR28 historical18-core design. The new prospective T16-first contract and actual thermal-stop outcome are in [Issue29 workflow](ISSUE29_WORKFLOW.md) and [decision memo](research/ISSUE29_DECISION_MEMO.md). Do not rerun or relabel the failed historical campaign. New stock measurements were NOT_TESTED after Issue29's qualification-stage stop.

One config-driven command, no rebuild:

```sh
python scripts/ann.py campaign --dry-run
python scripts/ann.py campaign --output "$ANN_RESEARCH_ROOT/evidence/NEW_CAMPAIGN"
python scripts/ann.py summarize --output "$ANN_RESEARCH_ROOT/evidence/NEW_CAMPAIGN" > summary.json
```

Core18: six alternating balanced AB/BA T8/T16 pairs; fixed seed20261013 chooses the first order. After each pair one reference alternates T1/T4, giving three each. Main settings: uint8,L2,mode2,K10,L100,W32,mem_L10, exact10K queries. Native unbound environment OMP_NUM_THREADS=T,MKL_NUM_THREADS=8,OMP_DYNAMIC=FALSE; unset binding/places/GOMP affinity. No concurrent compilation/tests/studies during timing.

Before any case freeze hashed PLAN with ordered rows, package/source/binary/tool hashes, host state and config. Between same-stage/same-block cases pause5s; a block/stage transition pauses15s. No outcome-based retries. Required correctness arm runs after core before extension, and after extension; all10K returns/distances are independently validated per distinct configuration using the separate same-library probe. Stock has no ID export; this prevalidated equivalent implementation is the explicit scope of its ID sanity evidence, not directly observed per-stock IDs.

Extension only after core validation: L50/75/125/150, three each atT8/W32, then W16/W64, three each atT8/L100. All orders frozen before first case. Configured Wcap is not measured time-weighted actual W.

Every run uses the same rich1Hz collector and independent heartbeat watchdog. Package99°C once or97°C for10s; missing credible sensor, AC change, RAM≤1GiB, disk≤20GiB, sustained swap>64MiB, foreign ANN or240s per-run cap stops. Policy/profile changes within run or paired block stop scientific progression and preserve evidence. Unavailable required observations fail closed; no tuning/automatic process kills. Five-second/whole-process snapshots of prior campaigns are not substituted. Current1Hz samples still do not prove continuous thermal/policy stability or phase-specific CPU utilization.

Monitor screen is separately frozen LITE/RICH/RICH/LITE, same stock T8, same1Hz safety/watchdog and5s gaps. LITE omits thread/frequency/SQPOLL diagnostic reads; it does not turn thermal safeguards off. Two paired effects characterize only descriptively. A5% observer budget was chosen as half a prospective10% scaling effect, not inherited D/E0 thresholds. It is not an equivalence proof. Main campaign remains uniformly rich.

Statistics: six **blocks** are units, not60K individual query repeats. Delta=100*(QPS16/QPS8−1); also paired log ratio and recall percentage-point differences. Median/mean/sampleSD/MAD/min/max and all raw values. Deterministic20,000 block-bootstrap draws, seed20261013, percentileCI90 with linear p*(n−1) interpolation; show leave-one-block-out medians. Six blocks provide limited uncertainty resolution and no causal mechanism identification.

Paper printed P99 is actually0.999 → P99.9. Modern uses0.99 → P99. Absent stock P50/P95/P99 remain null. QPS timer excludes loading, two L200 warmups, recall and teardown; per-query mean latency has a different scope. Application mean I/O is not device IOPS/latency; paper hops0 is not expansions. Compare recall–throughput curves within measured overlap only, never extrapolate or equate unequal recall to pure speedup.

Full content audits pre/post; cheap size/mtime checks between cases. Parse raw stdout/stderr independently, reject exit0 with read/CQE/error diagnostics, missing10K header, nonfinite metrics or zero recall. Preserve all failures. Local raw evidence is authoritative; no MLflow dependency or raw uploads.

The executed v1 campaign stopped during post-core qualityT16 at100°C; no extension ran. Reviewed v2 adds a fixed5s gap and startup<85°C requirement before each quality command and attributes failures to the actual job. These corrections are synthetic-tested only; the v1 PLAN/results are not rewritten or rerun.
