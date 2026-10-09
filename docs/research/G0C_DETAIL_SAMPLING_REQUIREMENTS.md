# G0-C DETAIL sampling requirements — design only

**No sampling change or DETAIL execution is implemented by Issue #14.** Current D6 remains INCONCLUSIVE, D1 observability NO, D4 selector NOT TESTED. A separate reviewed G0-C protocol is required.

## Existing rule and startup bias

The exact instrumented subject is `3bdcc064cb96aae4cd845bd2bb6adc5f5ba63e19`, based on `b9ec4ba86ff5d70bec277984777197f28dc2cf42`. In `tests/search_disk_index.cpp:111–122`, OpenMP uses dynamic scheduling with chunk 1. `QueryScope(i, omp_get_thread_num(), &stats[i].total_us)` surrounds the existing synchronous pipe_search call. `include/causal_trace.h:102–111` chooses `config.mode == DETAIL && qid < config.first_n` once at query begin. Thus first-N=16 observes early query IDs; at T16 these can largely be the first dispatch wave, at T8 the first few waves. Worker/ring initialization, cache warming and concurrency ramp-up may differ from later search. At T1 it is still an early prefix. Determinism does not make a prefix representative.

Query ID is an ordering coordinate, not elapsed time or measured steady-state concurrency. A later-ID sample reduces prefix bias but cannot alone prove steady state. Current LIGHT captures all-query counters without clocks: final W is not width residency, and max hidden is not a CQE-to-publication latency distribution. Do not classify D6_LOW/MATERIAL from this campaign.

## Minimal proposed method

Prefer a small **explicit sorted query-ID set**, parsed once before the measured loop and bound by a digest. For a future 10K-query run, an illustrative distributed 16-ID set is `1000 + floor(j*8000/15)`, j=0..15, spanning qid1000..9000. This is a proposal, not an already frozen scientific sample. Choose and freeze the exact IDs before future results, identically across T/W/repetitions. Retain query/run grouping; request counts cannot act as independent repetitions.

A single later contiguous range is simpler but can overrepresent one period. A modulo/stride rule is compact but requires explicit start/end/stride and exact count, and may correlate with ordering. An explicit set makes membership/count/digest unambiguous. Sampling must operate on qid, never worker number, completion order, latency, QPS or observed backlog. Reject duplicates, out-of-range IDs and inconsistent N. A fixed membership bitmap for 10K queries (~10 KiB) can be prepared once; no per-event allocation/string parsing or lock is required.

## Exact proposed hooks and ownership

| Component | Existing exact hook | Minimal future change |
| --- | --- | --- |
| Configuration / fixed allocation | subject `src/utils/causal_trace.cpp:25–44` prepare, currently first_n parsing at33 and event allocation at43 | Parse/validate policy and IDs before measurement; prepare immutable membership structure; record policy identity. OFF keeps its early allocation-free return at39. |
| Whole-query sampling | subject `include/causal_trace.h:107` in begin | Replace only the sampling predicate; choose once before QUERY_START. Keep all existing query counters, request correlation and event hooks. Never enable/disable midway through a query. |
| Driver lifecycle | subject `tests/search_disk_index.cpp:118–122`, QueryScope; header `:123–126` | Preserve RAII start and end after existing search/drain; no public API or scheduling change. |
| Event capacity / loss | header `emit :74–100`; subject prepare `:40–44` | Fixed numeric event array per worker; capacity counts all sampled queries handled by that worker cumulatively. Overflow invalidates the trace. |
| Protocol dump | subject `src/utils/causal_trace.cpp:46–61`, header fields at53–54 | Version the raw protocol if adding sample metadata; preserve exact policy/ID-set digest. Do not overload first_n to mean a different policy. |
| Harness configuration / manifest | research `tools/research/run_ann_experiment.py`: TRACE_ENV_KEYS, trace validation around193–195, environment construction276, manifest trace_config321 | New explicit optional policy configuration; ambient values sanitized, resolved policy recorded. Keep historical first-N default/replay compatibility. |
| Export and health | research `tools/research/causal_trace.py`: read_raw, export_trace sample membership checks | Version-aware membership validation; requested/observed IDs exactly match. No qid<first_n assumption for the new protocol. |
| Checker / analysis | research `tools/research/check_causal_trace.py`, `analyze_g0_causal.py` query grouping | Require complete per-query/request lifecycles; sort within query with stable tie rules; validate sampled set and retain clustering. |

No FIFO scan, extra next_calc_nbr invocation, candidate admission/order, width update, io_uring or public SSDIndex change is necessary for this design.

## Capacity and lifecycle validation

Event capacity is **per worker across the entire run**, not per query and not per sample batch. Do not divide N by T to assume a maximum per worker under dynamic scheduling. Freeze a conservative capacity using the maximum total events if all selected queries happen to land on one worker, observed logical-work bounds plus width/query boundary events and a stated safety margin. LIGHT counters can estimate event needs but cannot prove an upper bound on future DETAIL demand. Validate with a non-headline correctness preflight, then freeze capacity for all accepted DETAIL configurations. Do not increase it after selectively observing failed sampled traces without a documented new protocol/amendment.

The existing event is 34 uint64 fields =272 bytes. Capacity65536 consumes 17 MiB/worker, 272 MiB at T16, before tables/query counters and the ANN working set. The correlation table remains512 entries/worker versus stock inflight maximum128. Preserve RAM headroom, exact binary/build hashes and all buffer/drop counts. All selected queries require QUERY_START, WIDTH_INIT, QUERY_END and TRACE_HEALTH, with physical SELECT→SUBMIT→CQE_SEEN→PUBLISH and separate cache-ready paths. Expansion need not exist for every published request. Submitted/CQE/published counts must drain; zero unmatched, ordering, negative hidden, overflow/drops and outstanding correlations; raw/export checksum agreement mandatory.

IO_SUBMIT remains after SQE preparation immediately before io_uring_submit; IO_CQE_SEEN remains userspace poll processing. Their difference is a **userspace-observed I/O interval**, not device hardware latency.

## Comparability and avoiding startup-only conclusions

A sampling predicate/protocol patch creates a new subject/binary identity. Revalidate OFF/LIGHT comparability with a separately frozen E0 protocol before official use, even if those modes are intended to remain unaffected. Existing E0c validates T8/W32 of the old binary only; it is not an overhead guarantee at T1/T16/W64. Validate new DETAIL membership/lifecycle/capacity separately; DETAIL QPS is never a headline metric.

The future G0-C plan should freeze distributed/later IDs and, if desired, a separately labeled startup sample. Record query start/end timestamps relative to benchmark start, observed worker concurrency and run phase; collect global origin through a pre-loop hook if the current protocol cannot supply it. Do not infer steady state merely from qid. Compare phases without treating the same run's requests as independent experiments. D6 requires valid per-request observed-I/O and publication-HOL distributions, query-time hidden occupancy and replicated run/query grouping under its separately frozen thresholds. This document neither implements those hooks nor authorizes G0-C execution.
