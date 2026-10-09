# P0 causal PipeANN measurement

Issue #4 instruments only the canonical subject in `~/ann-research/PipeANN-p0`.
The research repository contains the exporter/checker/runner support and a small
exact subject patch. Golden `~/ann-research/PipeANN` stays clean. This is measurement,
not a D1/D2/D3/D4/D6 solution, algorithm change, or research result.

## Runtime contract

Use the existing `pipeann-b9ec4ba` profile, mode 2, and explicit `--subject-repo`.
Causal tracing adds no positional arguments. `--causal-trace` passes and records:

| Environment key | Meaning |
| --- | --- |
| PIPEANN_TRACE_MODE | OFF, LIGHT or DETAIL |
| PIPEANN_TRACE_OUTPUT | Exclusive owned run path for ann_trace.bin |
| PIPEANN_TRACE_DETAIL_FIRST_N | Deterministic sampled qids less than N (default 8) |
| PIPEANN_TRACE_EVENT_CAPACITY | Fixed event capacity per OpenMP worker (default 16384) |

The harness clears ambient trace settings when opt-in is absent. A stock binary
cannot silently satisfy opt-in: missing/truncated raw output makes `trace_valid=false`
and the runner returns nonzero. Finalized evidence separates three fields:

- `benchmark_status`: ANN process execution plus benchmark parsing result;
  success, failed, interrupted or timed_out.
- `trace_valid`: true/false for required causal evidence, null when tracing is
  not enabled. Pending validation also starts as null.
- `run_status`: overall experiment validity. It is success **iff** benchmark_status
  is success and (tracing is not required or trace_valid is true). Manifest `status`
  is a finalized alias of run_status; it remains running during execution.

A successful benchmark with a missing/corrupt/dropped/invariant-invalid required
trace has benchmark_status=success, trace_valid=false and run_status=failed; the
runner returns 1. Metrics, stdout and trace diagnostics are retained. `exit_code`
in summary and finalized manifest is the native ANN process returncode (negative
for signal termination, null if no process started), not the runner's return code.
Interrupted/timed_out benchmark states remain the overall state.

MLflow transport remains independent: mlflow_status=success means the mirror
completed. Its run terminal state is FINISHED only for overall run_status=success,
otherwise FAILED. Tags expose benchmark_status, trace_valid and run_status.

This is an additive schema-v2 forward correction. Presence of benchmark_status
identifies the new contract; older v2 records without it retain their recorded
pre-fix status semantics and are not rewritten or assigned an inferred benchmark
status. See [migration details](P0_EXPERIMENTS.md) and the
[historical campaign note](P0_CAUSAL_VALIDATION.md).

OFF initializes the runtime and dumps only protocol metadata, with no event clocks,
arrays, query rows or correlation operations. Its trace health zeros mean **zero
recorded observations**, not zero actual ANN I/O/expansions. OFF trace-valid indicates
valid protocol/configuration, not per-request verification. Benchmark metrics remain
available in summary.json. LIGHT captures real aggregates for all queries, without
per-event clocks or events. DETAIL adds full events for qid<first_N and retains LIGHT
aggregates for all queries. DETAIL is unsuitable for headline QPS.

Each worker has a preallocated numeric event array and fixed 512-entry request table,
four times the stock 128 inflight limit. TLS is installed by driver RAII immediately
before the existing pipe_search call and cleared after its return/drain. Query id,
worker number, Linux TID, request sequence, numeric request key and ring identity are
observational metadata. No IORequest/public API/CandidatePool layout is changed.
No strings, JSON, file writes, mutexes, malloc/new or MLflow occur per event.

## Semantics and timing

Required events: QUERY_START/END, WIDTH_INIT/CHANGE, IO_SELECT/SUBMIT/CQE_SEEN/PUBLISH,
NODE_EXPAND and TRACE_HEALTH. Width change snapshots include old/new W, Wcap, exact
stock cur_n_in/cur_tot/n_in/n_out/max_marker and inflight count. No heuristic change,
shrink path, candidate selection, extra mutating selector call or queue scan is added.

Physical requests follow SELECTED -> SUBMITTED -> CQE_SEEN -> PUBLISHED. NODE_EXPAND
observes only the actual existing selector result. Some published requests never
expand. Expansion remains node-level with request_seq=null; no guessed source-request
mapping is asserted. Worker buffers are exported in worker order; JSONL is not claimed
to be globally timestamp-sorted. Timestamps are monotonic nanoseconds, not UTC.

- IO_SUBMIT timestamps after SQE preparation and immediately before the existing
  io_uring_submit() call. IO_CQE_SEEN timestamps when CQE/user_data is processed by
  the userspace poll loop, not necessarily the exact batch-peek instant.
- L_observed_io = t_cqe_seen - t_submit: **userspace-observed I/O interval**,
  including observation/poll scheduling delay; **not device hardware latency**.
- L_HOL = t_publish - t_cqe_seen: application publication delay.
- L_ready = t_expand - t_publish when a source-request mapping is independently
  established. This first patch deliberately leaves expansion request_seq unknown.

Stock send_read can hit the software cache without an SQ submission or CQE. That
path emits IO_CACHE_READY, not a fabricated CQE. Physical submitted/cqe_seen/published
counters exclude cache-only requests; cache_ready/cache_published are separate.
Thus physical completed_hidden=cqe_seen-published is nonnegative. Publication FIFO
checking includes both paths, in selection order; physical requests still preserve
submit order. No cache behavior or FIFO is changed. CQE errors invalidate trace health
while stock CQ handling/error logging stays unchanged.

Width initialization is min(4,Wcap). Actual changes preserve the stock +1/cap condition.
LIGHT exposes initial/final width, change count, max inflight and max completed_hidden;
time-weighted mean width is deferred to avoid extra LIGHT clocks. Query latency comes
from existing QueryStats total_us and is exported as latency_ns/latency_us; it does not
include driver cleanup after the search call. QPS includes that driver work.

## Build and exact subject reproduction

[subject/P0_CAUSAL_SUBJECT.json](subject/P0_CAUSAL_SUBJECT.json) records the exact base,
subject commit/tree, binary hashes, patch hash and build commands. Only the subject
local instrumentation branch is committed; nothing is pushed to thustorage upstream.
[subject/P0_CAUSAL_PIPEANN.patch](subject/P0_CAUSAL_PIPEANN.patch) contains the entire
small source delta, including its standalone tracer test. The exact Git commit object
is preserved in [subject/P0_CAUSAL_SUBJECT_COMMIT.txt](subject/P0_CAUSAL_SUBJECT_COMMIT.txt).

To reproduce in a **clean instrumentation worktree at b9ec4ba**, first verify HEAD,
status and destination branch. Do not apply to golden stock or an existing dirty tree.
With RESEARCH_REPO set to the harness checkout and SUBJECT_COMMIT read from mapping:

```bash
git apply --check "$RESEARCH_REPO/docs/research/subject/P0_CAUSAL_PIPEANN.patch"
git apply --index "$RESEARCH_REPO/docs/research/subject/P0_CAUSAL_PIPEANN.patch"
git write-tree  # must equal subject_tree in the mapping
git hash-object -w -t commit "$RESEARCH_REPO/docs/research/subject/P0_CAUSAL_SUBJECT_COMMIT.txt"
# Verify emitted SHA equals subject_commit, then fast-forward only the intended local branch:
git update-ref refs/heads/research/p0-causal-instrumentation "$SUBJECT_COMMIT" b9ec4ba86ff5d70bec277984777197f28dc2cf42
```

Build commands used, preserving the golden empty CMAKE_BUILD_TYPE and flags:

```bash
cd ~/ann-research/PipeANN-p0/third_party/liburing
./configure
make library -j4
cd ~/ann-research/PipeANN-p0
CPLUS_INCLUDE_PATH="$HOME/ann-research/Parallel_ANN_Research/.deps-research/usr/include" \
  cmake -S . -B build -DIO_ENGINE=uring -DUSE_TCMALLOC=ON -DBUILD_PYTHON_INTERFACE=OFF
CPLUS_INCLUDE_PATH="$HOME/ann-research/Parallel_ANN_Research/.deps-research/usr/include" \
  cmake --build build --target search_disk_index -j4
```

Local Boost headers were already present; no package/data/index download was needed.
Golden and instrumented definitions/flags match exactly after source-root normalization:
BG_IO_THREAD, NDEBUG, USE_AVX2, USE_TCMALLOC, USE_URING, GNU 13.3.0/native O3.
CMake/build scripts are unchanged. This trace contract is validated for USE_URING,
not SPDK/AIO or arbitrary multi-L standalone benchmark invocations.

## Run, inspect and check

From the research repository, reuse existing SIFT1M inputs:

```bash
.venv-research/bin/python tools/research/run_ann_experiment.py \
  --benchmark-profile pipeann-b9ec4ba --subject-repo "$HOME/ann-research/PipeANN-p0" \
  --executable "$HOME/ann-research/PipeANN-p0/build/tests/search_disk_index" \
  --dataset-path "$HOME/ann-research/data/sift1m" \
  --query "$HOME/ann-research/data/sift1m/query.fbin" \
  --ground-truth "$HOME/ann-research/data/sift1m/gt.bin" \
  --index-prefix "$HOME/ann-research/indexes/sift1m/sift1m" \
  --neighbor-type pq --threads 8 --wcap 32 --k 10 --l-search 75 --mem-l 0 \
  --trace-mode DETAIL --causal-trace --trace-detail-first-n 8 \
  --trace-event-capacity 16384 --mlflow --dry-run
```

Remove --dry-run to execute; use OFF/LIGHT for those modes. Golden runs use the golden
binary/worktree and omit --causal-trace. No SIFT10M or grid is part of this workflow.

ANN writes ann_trace.bin only after measured search ends. PANTRC01/v1 is an 8-byte magic
plus ten little-endian uint64 header values, 34-field numeric events, then 28-field query
counter rows. UINT64_MAX represents unavailable numeric values, except signed CQE
result decoding. The Python exporter produces events.jsonl, query_metrics.csv,
trace_health.json and trace_check.json. Raw/readable traces and all metadata are
checksummed by the same runner. No per-event data is mirrored to MLflow; only run-level
configuration/trace validity and normal benchmark summary metrics are logged.

```bash
.venv-research/bin/python tools/research/check_causal_trace.py \
  "$RUN_DIR/events.jsonl" --health "$RUN_DIR/trace_health.json"
(cd "$RUN_DIR" && sha256sum -c SHA256SUMS)
```

Checker verifies query boundaries, unique sequence/correlation, submit before CQE,
CQE/cache readiness before publication, FIFO, nonnegative hidden count, drained
correlations, actual node publication before expansion, width initialization/bounds/
nondecreasing +1 behavior, cumulative counters, sample completeness and trace loss.
Sampled event histories must agree with separate query summaries. Missing/truncated
raw output, overflow, unmatched events and errors are explicit invalidity. Interruptions
preserve diagnostics and fail tracing when no complete raw dump exists.

## Limits and interpretation

[The design](P0_CAUSAL_TRACE_DESIGN.md) froze five rotating E0 repetitions per case and
five sentinels before measurements; no post-hoc overhead threshold was selected.
[The validation report](P0_CAUSAL_VALIDATION.md) records actual metrics/run IDs. Existing
benchmark outputs do not expose exact top-K result arrays, so recall consistency is
reported without claiming bit-for-bit query-output equivalence. Host frequency/load
are observed, not controlled by topology placement or governor changes.

Large completed_hidden measures application-level publication HOL; it does not
establish a root cause. Low inflight does not prove algorithm dependency starvation.
Algorithm prerequisites, resource serialization, candidate availability and CPU pressure
remain distinct future questions. No novelty/hypothesis conclusion is made here.

Generated runs/raw traces/MLflow/builds/data/indexes remain external or ignored. No large
artifacts are committed. Large index files >64 MiB still have sha256=null; cached/full
hashing remains a follow-up before official SIFT10M. The original Issue #1 smoke artifacts
remain immutable and retain their legacy infrastructure classification.

## G0-C1 explicit DETAIL sampling

Opt in with `--causal-trace --trace-mode DETAIL --trace-sample-policy explicit_qids --trace-sample-qids 1000,3000,5000,7000,9000`. IDs must be canonical, strictly increasing, unique and in range. Configuration is parsed once; full query/request lifecycles are retained. Default first-N and PANTRC01 remain supported. Explicit sampling uses PANTRC02/v2 and derived schema-v3 events/health, with exact IDs and canonical SHA256. The run index gains additive sampling identity columns; historical cells stay blank. MLflow mirrors only policy/digest/count. See [sampler design](G0C1_SAMPLER_DESIGN.md). Query-relative timestamps provide coarse phase context, not active-query occupancy or proof of steady state. IO_SUBMIT to IO_CQE_SEEN remains a userspace-observed I/O interval.
