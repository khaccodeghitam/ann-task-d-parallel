# Minimal diagnostic logging: DESIGN_ONLY

The required stock baseline did not pass build/config readiness. No diagnostic
clone, C++ patch, binary, exported event, T8/T16 diagnostic smoke or overhead
calibration was created. PANTRC01/02/PANOP historical traces were not migrated;
their schema contracts belong to the modern subject. Lost events/overflow/
sample coverage for paper are **NOT_MEASURED**, not zero or trace_valid=true.

Source-grounded future question: conditional on an actual sampled expansion,
how much **new discovered and admitted neighborhood information** does it reveal,
and what selection/read/publication decisions follow? This is a descriptive
state-transition question, not a causal marginal-value result.

| Proposed event | Exact artifact hook | Observable relationship / restraint |
| --- | --- | --- |
| QUERY_BEGIN/END | tests/search_disk_index.cpp:140–146 existing pipe_search call | qid/worker/TID and benchmark-origin offset; isolate warmup iterations |
| DISCOVER / DUPLICATE | src/v2/pipe_search.cpp:117–127 existing visited insertion loop | known source expanded node +neighbor; no extra scan |
| ADMIT / REJECT | :129–148 existing PQ comparison/InsertIntoPool return | PQ squared-L2 type/rank; displaced candidate must be captured before mutation, not guessed |
| SELECT_READ | :232–248 existing flagged retset selection | observe returned item only; no second selector |
| SUBMIT | :199–214 plus src/linux_aligned_file_reader.cpp send_io | stable query/request ordinal; request pointer is reusable, not permanent ID |
| CQE_SEEN | reader poll existing CQE user_data processing | userspace-observed completion, not hardware completion |
| PUBLISH | pipe_search.cpp:221–228 FIFO front finished insertion | no queue scan/reorder; insertion outcome distinct from candidate readiness |
| EXPAND / EXACT_DISTANCE | :255–266 actual calc selection +existing distance computation | node/source-neighbor counts; no fabricated physical-request mapping |
| WIDTH | :171 and :344–346 actual assignments | Wcap differs from effective W; clocks not required on unsampled queries |

The artifact's selectors are lambdas over a sorted array, not the modern public
CandidatePool interface. Admissions can move storage; selection clears flags;
published nodes can be outside live candidates. `id_buf_map` is not erased on
expansion in this version. Source inspection found no explicit remaining-I/O
drain in this pipe_search exit; request-buffer ownership and lifecycle must be
proved before correlating query-end with final CQE. Do not graft modern “every
submit publishes before query end” assertions onto this source without proof.

Proposed separate diagnostic format would contain numeric query/worker/TID,
event/ordinal/monotonic_ns/node/source, distance_kind, distance, actual insertion
outcome and neighborhood counts. UNKNOWN uses a schema sentinel, not a guessed
parent or causal edge. A fixed distributed16-qid set can reuse documented IDs
1000…9000 only as a **new explicitly versioned sampling configuration**, with
all warmups excluded, exact membership checked. A capacity65536×64-byte record
would reserve4MiB/worker (64MiB atT16), but sufficiency is **not proven**: admissions
can scale with R×expansions, and all sampled queries may land on one worker.
Preallocated drop/overflow accounting must fail closed; no event allocation,
file/JSON I/O, shared event mutex, pool scan or selector duplication.

Stock headlines stay separate from any post-timer query exporter or diagnostic
build. If implemented later, correctness fixtures must cover ties, eviction,
request-pointer reuse, partial return and warmup/query identities. Two tiny
T8/T16 smokes would certify only mechanics; observer timing remains uncalibrated
without a separately defined effect test. No perf/tracefs pilot is needed here.

For motifs, offline index adjacency +unique-neighbor discovery could support
overlap statistics. For H-QV1, a logged expansion trajectory provides a factual
prefix but **not** the counterfactual value of an unselected expansion; search
path censoring and descendants make attribution nonidentifiable from logging
alone. Need a frozen replay/state simulator or carefully controlled later
prototype before calling novelty, recall improvement or marginal causal value.
