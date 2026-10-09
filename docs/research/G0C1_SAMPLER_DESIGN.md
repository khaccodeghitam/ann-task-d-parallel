# G0-C1 sampler design — frozen before C++ changes

Issue #16 was read completely (no comments). Research base is `36cc84b98418e9051c4d7c798ffaae20b06f8a3e`; golden `b9ec4ba86ff5d70bec277984777197f28dc2cf42` and old instrumented subject `3bdcc064cb96aae4cd845bd2bb6adc5f5ba63e19` were verified clean. Golden remains immutable. This prepares sampling; no G0-C2/D6 classification or D1/D4 implementation.

## Source audit and minimum surface

Old `include/causal_trace.h:107` chooses DETAIL `qid < config.first_n` at begin. Driver `tests/search_disk_index.cpp:118` RAII surrounds exactly one existing pipe_search; dynamic OpenMP chunk 1 is unchanged. `prepare` parses before the timed loop and allocates cumulative per-worker arrays. `emit` writes 34 numeric uint64 fields, with timestamps only for sampled DETAIL; counter rows have 28 fields. Correlation table is 512 entries, stock maximum inflight128. CQE and submission hooks in the reader, FIFO/width/expansion hooks in pipe_search_common.h remain byte-identical.

Only tracer header/implementation, standalone tracer test, and two observational driver calls change. Public ANN API/request layouts, candidate pool, search/reader/CMake/build code do not change. Research changes reuse runner/exporter/checker/schemas/index/MLflow. Exact incremental subject patch, raw commit object, tree, base, flags and new binary hash will be saved under docs/research/subject. The prior binary is retained externally before rebuilding.

## Sampling contract

Default `--trace-sample-policy first_n` preserves the existing `--trace-detail-first-n` meaning and v1 output. Opt-in `--trace-sample-policy explicit_qids --trace-sample-qids 1000,1533,...,9000` requires causal DETAIL. Environment: PIPEANN_TRACE_SAMPLE_POLICY and PIPEANN_TRACE_SAMPLE_QIDS. Harness clears ambient keys for stock/first-N; no positional benchmark arguments change.

Both implementations independently require canonical decimal integers (no signs/whitespace/leading zeros), strictly increasing/unique, nonempty, each less than query_count; max1024 IDs, max16384 input characters, max1000000 query-count bitmap entries. Bad/irrelevant sampler configuration is rejected before search. Parsing and SHA256 happen once in prepare; explicit DETAIL creates a uint8 membership bitmap, read-only throughout execution. Begin selects one bitmap byte once for the entire query, preserving QUERY_START through drained QUERY_END/TRACE_HEALTH. OFF/LIGHT never allocate/read the bitmap or gain phase clocks. No strings, allocations, file/JSON writes, mutexes or extra selectors occur per event.

Canonical sample identity: lowercase SHA256 of the ASCII comma-separated canonical IDs plus one newline. Raw trace, manifest and health contain the exact IDs and digest; raw digest is computed independently in C++, and checked independently by Python. First-N is never overloaded. Explicit IDs in this issue are correctness samples only, not a frozen official G0-C2 sample.

## Protocol compatibility

| Mode/policy | Raw protocol | Events/rows | Compatibility |
| --- | --- | --- | --- |
| OFF/LIGHT/default first-N DETAIL | PANTRC01/v1 | Existing 34-field events and 28-field rows | Byte layout and first-N semantics unchanged |
| Explicit-qid DETAIL | PANTRC02/v2 | Same numeric event/row layouts | New metadata extension; v1 remains readable |

v2 begins with the existing `<8s10Q` header (version2), then `<4Q`: policy1, ID count, monotonic benchmark origin ns, benchmark end ns; ascending uint64 IDs, then 32 raw SHA256 bytes. Events and query rows follow. Dimensions, exact size, bounds, IDs/digest, metadata times and sample membership are validated. Manifest schema-v2 gains optional versioned sample fields; v2-derived event/health records use schema_version3. Historical records/run-index cells remain untouched and missing new fields stay blank. No old artifacts are rewritten.

## Phase observations and effects

For explicit DETAIL only, take two steady-clock readings just before the existing timed loop and after its barrier. Existing QUERY_START/END timestamps derive benchmark-relative times and relative phase fractions in Python. No extra per-event or per-query clocks, locks, global atomic dispatch/active counters, or new request/expansion correlation is added. Clock-call microbenchmark will quantify the two added clock observations; DETAIL smoke timing is diagnostic, not an overhead result. New OFF/LIGHT binary effects require the separately frozen paired E0 gate.

Sampled query boundaries identify time and coarse phase but cannot reconstruct total active-query occupancy, dispatch completion count, ready work, or certify steady-state concurrency. Those remain explicitly unavailable. Later qids do not prove steady state; G0-C2 must predeclare phase interpretation and may remain inconclusive.

## Capacity and validation plan

Freeze 65536 events/worker for correctness smoke. Event272 bytes gives 17MiB at T1,136MiB at T8,272MiB at T16, plus fixed request tables/2.14MiB query counters and10KiB bitmap for10K queries. Capacity is cumulative per worker: assume all16 sampled queries can fall on one worker, never N/T. The maximum complete-event estimate over all G0-B query rows is1077; all16 on one worker is17232, giving3.803× headroom. This is historical observed work, not a mathematical bound; any drops/overflow invalidate rather than overwrite/retry for prettier results.

Tests cover known SHA vectors, strict ID configuration, legacy first-N, OFF/LIGHT allocation-free sampling paths, full lifecycle/reuse/FIFO/cache, capacity/table drops, old/new raw formats, exact requested/observed IDs, missing/extra/duplicate/wrong-qid, digest/time corruption and schema/index/MLflow compatibility. Python malformed causal traces remain rejected. Historical E0b/E0c/G0-B analyzers replay into new external directories and must reproduce original summaries.

Correctness: frozen distributed16 qids from1000+floor(8000*j/15), one tiny non-headline DETAIL run each T1/W32,T8/W32,T16/W32, exact membership/full lifecycles/zero-loss. Independent offline checker on every smoke. Package full-content audits bracket all new runs.

New E0: separate immutable plan before accepted measurements, 12 paired blocks of STOCK/new OFF/new LIGHT at native T8/W32/K10/L100/memL0/pq/l2/mode2 and fixed packages. Use E0c order, 5s within/15s between blocks, matched collectors/external observers, bootstrap20000 block resamples/seed20261008/CI90, ±3% OFF/STOCK, ±5% LIGHT/OFF, recall ±0.02pp, native sanity stockQPS≥2471.42 and mean latency≤3212.82us. No exclusions, threshold edits or hidden retries. Failures remain preserved and reported; no automatic G0-C2 authorization. T1/T16/W64 overhead beyond T8/W32 is unvalidated.

C++ optimized and ASan/UBSan tests passed. A 1M-call steady clock microbenchmark measured14.916ns/call (sanitized17.019ns/call); two added explicit-DETAIL phase observations are roughly30ns nominal, not a benchmark overhead claim. No active/dispatch atomics were added.
