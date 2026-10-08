# P0 causal trace design — Issue #4

Design recorded before editing ANN source. Harness base b379a9260cb310e1ed1f7bdd3325c41a3a86e649;
subject base b9ec4ba86ff5d70bec277984777197f28dc2cf42. Golden PipeANN is clean and read-only;
ANN changes belong in PipeANN-p0, tooling changes in Parallel_ANN_Research.

## Source re-audit

All requested files were inspected at the clean subject commit. PipeSearch common obtains
get_ctx(IORING_SETUP_SQPOLL); USE_URING Linux reader ioctx::ring is static thread_local,
initialized on first get_ctx and destroyed by deregister_thread. Single send_io sets
sqe user_data to &req and submits unchanged. poll() peeks CQEs, reads that IORequest*,
marks finished, and acknowledges CQEs. QueryBuffer owns reqs[128] and sector scratch;
sector_idx cycles modulo MAX_N_SECTOR_READS=128 and QueryBuffer reset starts it at zero.
Buffers are acquired/returned by pop_query_buf/push_query_buf. No layout changes.

on_flight_ios is std::queue<io_t>; poll_all publishes only finished queue fronts into
id_buf_map and pops FIFO. Width starts min(4,Wcap); the exact waste condition grows by
+1, max(4), min(Wcap), with no shrink. next_calc_nbr mutates visited/flag; observe only
its existing returned node. QueryStats total_us is existing microsecond latency.
OpenMP benchmark dispatch is schedule(dynamic,1), with known qid and worker number.

One source mismatch with the simplified lifecycle: send_read can return a cache hit,
setting finished without SQ submission or CQE (READ_ONLY_TESTS is absent in the golden
flags). Add IO_CACHE_READY for this path, rather than fabricate a CQE. Physical
submitted/cqe_seen/published counters exclude cache-only requests; cache_ready and
cache_published are separate. Therefore completed_hidden=cqe_seen-published remains
nonnegative for physical I/O. FIFO checker includes all selected reads, including
cache hits; physical requests still follow submit order. A cache-ready request follows
SELECTED -> CACHE_READY -> PUBLISHED, and may subsequently be expanded. CQE error
status is recorded and invalidates the trace without changing stock error handling.

## Event hooks

| Event | Semantic meaning / exact source hook | Numeric fields | OFF / LIGHT / DETAIL | Hot-path strategy | Invariant |
| --- | --- | --- | --- | --- | --- |
| QUERY_START | benchmark driver RAII immediately before the existing pipe_search | qid, worker, Linux tid, sample | no-op / counters / sampled event | TLS install, no API changes | one begin/end per traced query |
| WIDTH_INIT | pipe_search_common after min(4,beam_width) | W, Wcap, ctx identity | no-op / aggregates / sampled event | numeric TLS | W=min(4,Wcap) |
| WIDTH_CHANGE | immediately after unchanged stock condition and clamps, only if W changed | old/new W, Wcap, cur_n_in,cur_tot,n_in,n_out,max_marker,inflight | no-op / aggregates / sampled event | never mutate heuristic state | nondecreasing, <=+1 |
| IO_SELECT | send_read_req after constructing its existing IORequest, before send_read | req key/seq,node,page,loc,offset,len,W,inflight | no-op / correlation / sampled event | fixed table | monotonic unique sequence |
| IO_SUBMIT | scalar USE_URING send_io after SQE prepared, immediately before existing submit | request correlation, timestamps only sampled | no-op / count / sampled event | same-thread registration before poll | selected before submitted |
| IO_CQE_SEEN | poll and poll_alloc on retrieving user_data, before finished assignment | req key/seq, CQE res, poll batch size, cumulative counters | no-op / aggregate poll/count / sampled event | unchanged CQE acknowledgment | submit precedes seen |
| IO_CACHE_READY | send_read successful existing cache branch | req key/seq, cache readiness | no-op / count / sampled event | observes existing branch result | no invented CQE |
| IO_PUBLISH | FIFO loop immediately after existing id_buf_map insertion | req key/seq, physical/cache counters, hidden,inflight | no-op / count / sampled event | no scan/reorder | prior CQE/cache readiness, FIFO |
| NODE_EXPAND | calc_best_node after the existing mutating next_calc_nbr returns non-null | actual node id, time, width | no-op / count / sampled event | no extra selector call | actual expansion only |
| QUERY_END | RAII immediately after pipe_search return/drain | aggregate counters, outstanding, drops,violations, existing query latency | no-op / per-query row / sampled event | writes preallocated summary row | outstanding zero |
| TRACE_HEALTH | after QUERY_END state collected, before TLS clear | drops,unmatched,ordering,outstanding | post-run header / aggregate row / sampled event | fixed event buffer | loss never silent |

NODE_EXPAND remains node-level, with request_seq=null: no extra source-request map is
added to ANN state. Offline node-id matching can be inspected, but no guessed causal
mapping is asserted and published requests need not be expanded.

## Storage, configuration and exports

One context per worker allocated before the measured parallel loop. TLS points to that
context only during a query. Numeric fixed-size event arrays have explicit per-worker
capacity (default 16384); no mutex, allocation, strings, serialization or file I/O per
event. Fixed 512-entry open-addressed request table is four times the stock maximum
128 inflight requests. Slots are released on publication, allowing request-address reuse;
query boundaries validate outstanding entries. Overflow/unmatched/ordering counters
invalidate evidence; search decisions and request buffers remain untouched.

OFF performs guarded no-ops, no event clocks/writes/table operations. LIGHT aggregates
all queries without per-event clocks. DETAIL adds events for deterministic qid<first_N,
while all queries retain LIGHT counters. Default first_N=8; record configured count and
observed sample. Width time-weighted mean is deferred in LIGHT to avoid extra clocks;
initial/final/change/max-inflight/max-hidden counters are available.

Environment: PIPEANN_TRACE_MODE, PIPEANN_TRACE_OUTPUT, PIPEANN_TRACE_DETAIL_FIRST_N,
PIPEANN_TRACE_EVENT_CAPACITY. The existing canonical positional argv stays unchanged.
The runner opts in with --causal-trace and freezes all trace env values in command and
manifest. Missing raw output is an explicit invalid trace, never a successful scaffold.

The driver writes versioned little-endian numeric binary header/events/query rows only
after measured search ends. Raw output is created exclusively and retained; Python exports
events.jsonl and real query_metrics.csv, computes trace_health.json and machine-readable
invariant results, and checksums all files. MLflow receives run-level configuration/status
only, never events. Interrupted/missing/truncated traces fail health without discarding ANN
diagnostics. All generated evidence stays in ~/ann-research/research-v3.

## Validation plan frozen before measurements

Build with golden compiler, empty CMAKE_BUILD_TYPE, uring, tcmalloc, AVX2/native O3 flags;
capture golden binary SHA256/cache/flags before build. Reuse installed dependencies/local
Boost headers; no golden modifications, data/index rebuild or download. Test fixed tracer
structures and synthetic invalid lifecycles as well as all harness tests.

Smoke sequence: instrumented OFF, LIGHT, DETAIL first 8, T8/W32/K10/L75/mem_L0/pq/l2,
existing 10K SIFT1M query and index; each mirrored locally to MLflow. DETAIL validity is a
correctness gate: zero drops, unmatched events, ordering violations and outstanding.

After smoke validity, E0 has five repetitions each of golden stock, instrumented OFF,
instrumented LIGHT. Order rotates across repetitions, identical search/input/thread
settings; host telemetry only in LIGHT. Report distributions and deltas, no performance
pass/fail threshold and no threshold selected after results. One sampled DETAIL smoke
can describe its overhead relative to stock distribution but is not headline evidence.

After E0 characterization and correctness, run only five DETAIL first-8 sentinels:
T1/W32,T8/W32,T8/W64,T16/W32,T16/W16. No full grid. Short telemetry is descriptive only.
Large hidden completions indicate application publication HOL, not an automatic root-cause
claim; low inflight does not establish dependency starvation. No D1/D2/D3/D4 solution,
adaptive global W, admission control, SIFT10M, novelty or hypothesis claims.

## Subject versioning

Commit tracer separately on PipeANN-p0 local research/p0-causal-instrumentation. Do not
push thustorage upstream. Research repository stores a small full patch from b9ec4ba and
commit/hash/build mapping sufficient to reproduce it; do not copy the subject tree.
