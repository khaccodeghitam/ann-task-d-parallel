# D1-O1 state model and prospective kill test

## Decision and scope

**D1_O1_DESIGN_ONLY.** Issue #20 permits this outcome when valid minimum
observability requires a broader redesign. The audited subject is
`35222026893ff7d1b45586fcdd8165a5ce592cd3`; its existing binary is
`f5795e43c3be1f2515bd37e21ad1fbab45b2849c859724629a8c6edea5e418dd`.
Research starting commit is `4c5e00eec1b9ce4acb8d18781a5b19d2129e4dad`.
Golden remains `b9ec4ba86ff5d70bec277984777197f28dc2cf42`.
Issue #20 and all comments (none at audit) were read before changes.
This design was written before any ANN edit; no ANN edit is proposed in this PR.

Safe point observations are possible. A valid continuous readiness observer is
not available by adding only selector-result counters: it needs coordinated
mutation-site accounting across pool merge/eviction, flags, publication and
execution phases. Implementing a partial observer would fail the requested
candidate conservation and continuous interval attribution gates. This is a
scope/safety decision, **not a claim that a future full observer is impossible**.
The implementation prerequisites below define that separate work precisely.

No D1 optimization or hypothesis experiment is executed. D1 remains UNTESTED;
D6 remains INCONCLUSIVE; D4 remains NOT TESTED. Existing D6 HOL is neither proof
of FIFO-caused throughput loss nor proof that graph dependency is the rival cause.

## Hypothesis and falsifier

Hypothesis: within the fixed sampled workload, a meaningful fraction of query
elapsed time contains a dependency-constrained issue/readiness opportunity gap,
rather than only physical I/O waiting, FIFO-hidden completion, lock/resource
waiting, scheduler delay or ready work not selected. Graph topology redesign is
worth prioritizing only if this **necessary opportunity** survives those rivals.

Null/falsifier: even an optimistic accounting of all possible opportunities is
too small, or observed low inflight intervals already have issue-ready/calc-ready
work or a non-dependency explanation. In that case deprioritize topology D1 for
the measured configuration. This does not disprove every future D1 mechanism.

Absence of currently eligible work is necessary evidence for a readiness deficit,
but not sufficient evidence for a causal graph bottleneck. Unknown neighbors
only become known after expansion. The observer cannot predict what a changed
graph would reveal, or whether extra work would help recall or the critical path.
In particular a structural opportunity deficit can **overlap I/O waiting**;
renaming all I/O wait as dependency starvation would make the hypothesis tautological.

## Exact source audit and hook requirements

Paths/line anchors refer to the exact subject above. All hooks in the last column
are **proposed**, not implemented. No extra selector call or measurement-only
pool scan is allowed.

| State / observation | Exact existing source | Existing semantics | Minimal future observation and limitation |
| --- | --- | --- | --- |
| Discovered vs duplicate encounter | `src/search/pipe_search_common.h:161`, `compute_and_push_nbrs`, visited-set insertion | Discovery dedup precedes distance/batch insertion; seen does not mean admitted | Observe existing insertion result; record batch input survivors and rejects in existing loops |
| Admitted / rejected / evicted | `include/candidate_pool.h:104`, `:145`, `:181`, `:197` | Single insertion and batch merge have different paths; batch trims old tail and new tail, then bulk memmoves | Observe actual decisions at trim/assignment; query+node+admission-generation identity, never rank or backing pointer |
| Seed / rescore | `include/candidate_pool.h:225`, `:233` | Seeds append; rescore sorts and resets markers, retaining flags/visited bits | Keep identity while ranks move; explicit seed-path control even though present package uses mem_L0 |
| Known-unissued / read eligible | `include/candidate_pool.h:254`, `:355`; `pipe_search_common.h:334` | Read walk advances mutable send marker; returns flagged candidate; caller clears flag | Existing result proves >=1 eligible or no eligible at that decision; does not count all ready candidates or persist over unobserved mutations |
| Selected before lock / send | `pipe_search_common.h:289-299`; `include/ssd_index.h:410`; `include/utils/lock_table.h:28-98` | Flag clears **before** existing lock call; current IO_SELECT is after lock/req preparation | Bracket actual call, without try-lock probe; lock-call elapsed time also includes host descheduling and lock-table maintenance |
| Physical submit | `src/utils/linux_aligned_file_reader.cpp:688-699` | SQE prepared, IO_SUBMIT immediately before io_uring_submit | Existing physical sequence; do not timestamp earlier selection as physical submit |
| Software cache | `linux_aligned_file_reader.cpp:1016-1038` | Cache hit marks finished; emits CACHE_READY, no submit/CQE | Distinct cache-ready/publish path; do not add a synthetic device request |
| Userspace CQE seen | `linux_aligned_file_reader.cpp:717-735` | Poll loop gets request pointer, records CQE, marks finished | Existing request correlation; not hardware completion timing |
| FIFO publication / map residency | `pipe_search_common.h:317-326` | Only queue-front finished requests publish into id_buf_map; evicted candidate can still publish | Observe actual map-insert result and FIFO correlation; published-map membership is separate from live candidate membership |
| Calc eligible / selected | `candidate_pool.h:262-270`; `pipe_search_common.h:351-361` | Non-empty map triggers one existing scan; ready predicate is map membership, unvisited candidate selected and marked visited before expansion | Existing return distinguishes SELECTED vs no eligible in scan; empty-map shortcut is a separate outcome; avoid a second scan |
| Frontier / termination | `candidate_pool.h:277-281`; `pipe_search_common.h:373-453` | frontier mutates both markers; termination and drain skip ordinary issue/expand decisions | Observe the **existing** returned marker and actual control branch; never call frontier again; exclude drain from search-opportunity time |
| Expansion | `pipe_search_common.h:353-361` | Selected node triggers exact compute and neighbor discovery; candidate pointer invalid after inserts | Preserve node-level expansion; current request table releases entry at publication, so no invented expansion/request edge |
| Query boundaries | `tests/search_disk_index.cpp:112-120`, `:165-167` | Dynamic OpenMP dispatch, per-query trace RAII; benchmark clocks surround parallel region | Existing v2 benchmark-relative query timestamps; no active-query occupancy or on/off-CPU interval coverage |

`next_read_nbr`, `next_calc_nbr` and `frontier` all mutate state. The main
publication map uses `reserve(128)`, which is a reservation, **not a bound**.
Published-but-evicted entries can remain until query destruction: the map erase
is only on actual calc selection. MAX_N_SECTOR_READS bounds reusable in-flight
request buffers, not all historically published nodes or candidate admissions.
The shared CandidatePool also serves other search modes and exposes mutable
element access; an observer must be explicitly scoped to the main pipe-search
pool, without accidentally including the secondary/filter pool or other modes.

The normal neighbor batch has a documented unique-ID precondition guaranteed by
the search visited set. Do not assume the generic single-insert API rejects every
duplicate without side effects: in a non-full pool its duplicate sentinel can
still increase size. A contract probe preserves and exposes this behavior; it is
not repaired here, and it is not asserted to occur in the frozen mem_L0 search.

## Populations, identities and conservation

Candidates: `(query_id, node_id, admission_generation)` with explicit live pool
membership; rejected discoveries are never live. A pool rank/backing pointer is
not an identity because insertion/rescore moves storage. Distinct same-distance
nodes are ordered by node ID. Duplicate encounters and re-admission, if a future
mode permits them, are separate recorded outcomes. A visited set suppresses
normal neighbor rediscovery even after pool eviction.

Requests: `(query_id, request_seq)` plus reusable IORequest address only while the
correlation is live. Selection copies candidate metadata into FIFO io_t. Eviction
does not cancel that request. Physical and software-cache lifecycles are separate:

```text
physical: selected -> submitted -> CQE observed -> FIFO published
cache:    selected -> cache ready -> FIFO published
candidate: discovered -> accepted/live -> selected for read and/or calc
                                 \-> evicted (request may still complete)
calc: selected/visited -> compute/neighbor discovery -> expansion completed
```

Calc selection can clear an unissued flag when the ready predicate is true;
selection and expansion completion are different times. Candidate membership,
request status and map residency are overlapping populations, not one partition.
Required future conservation equations at each mutation boundary:

- live candidates = seeds + admissions - evictions - explicit live removals;
  selected/visited candidates can remain in the live result pool;
- live = unvisited + visited; unvisited = issue-eligible + issued/non-calc-ready
  + calc-ready, **only after validating flag/map consistency for the scoped mode**;
  inconsistent combinations are UNKNOWN/invalid, never forced into a bucket;
- selected = physical submitted + cache ready + selected-before-send;
- physical submitted >= CQE seen >= physical published; cache ready >= cache published;
- FIFO order includes physical and cache selections; all requests drain at query end;
- ready map residents = live eligible + live ineligible + out-of-pool residents,
  not just calc-ready candidates;
- each mutation reconciles identity and counts, with no negative state, duplicate
  live identity, ghost readiness or unmatched request. Tables are fixed capacity;
  overflow/loss invalidates the entire sampled lifecycle, never silently evicts evidence.

The flag-based partition is a proposed scoped invariant, not a verified observer.
No bounded shadow/table capacity has been certified in this design-only outcome.

## Interval model and conservative attribution

Use per-query monotonic nanoseconds, half-open intervals `[t_i,t_{i+1})`.
`t_i` must be a real state-transition or phase boundary, with stable per-worker
sequence tie breaking; equal timestamps have zero duration. Driver QUERY_START
and QUERY_END bound elapsed time. Search termination/drain is tracked separately.
Event timestamps bracket observations; hook cost and unobserved transition windows
are UNKNOWN. Integrating a last-seen selector result until the next arbitrary event
is invalid unless **every** relevant mutation and phase boundary is accounted for.
Width headroom means the actual stock admission test on FIFO queue size versus
cur_beam_width, with selected-before-send tracked separately. It is not inferred
from physical submitted-minus-CQE count, which excludes hidden/cache requests.

Maintain simultaneous diagnostic flags, not a falsely disjoint causal label:

| Flag | Required evidence |
| --- | --- |
| ISSUE_OPPORTUNITY_DEFICIT | Search active, actual width has headroom, exact issue-eligible set empty |
| IO_WAIT | Physical submitted minus CQE observed > 0 (observation waiting, not pure device time) |
| FIFO_HIDDEN | Physical CQE observed minus physical published > 0; cache-ready unpublished separate |
| CALC_READY_UNSELECTED | Exact live eligible calc set non-empty outside currently selected calculation |
| PUBLISHED_INELIGIBLE | Resident map node not currently live/unvisited/in selector's eligible range |
| SELECTED_PRE_SEND | Existing selected candidate has not reached physical/cache path; lock interval annotated separately |
| HOST_OR_RESOURCE_DELAY | Independently observed off-CPU/resource interval; wall duration of lock call alone is insufficient |
| UNKNOWN | Missing state/mutation/phase/on-CPU coverage; inability to separate rival explanations |

For an exclusive descriptive time chart only, prioritize UNKNOWN, then known host/
resource wait, selected-before-send, ready-unselected, FIFO-hidden, IO_WAIT, then
remaining structural deficit. Also retain all overlapping flags. This priority is
an accounting convention, not causal proof. A deficit overlapping IO_WAIT is **not**
called proven dependency delay. With no issue-ready or calc-ready candidates, no
pending request and no hidden completion, examine termination/quiescence first.
The stock loop has no evidence of a hidden graph prerequisite resolving by itself.

Thus an exclusive causal D1 label needs an independent prerequisite/critical-path
argument or controlled later intervention. The current source/tracer cannot supply
it. We can prospectively bound an opportunity; we cannot identify achievable
topology speedup from these observations.

## Frozen prospective kill-test thresholds (no measurements in this issue)

Protocol ID `D1-KILL-DESIGN-v1`. These are **new prospective prioritization choices**,
not thresholds derived from G0-B/C2 and not a running campaign. A later independent
Issue must authorize/freeze its sample IDs, run order, repetitions and negative
controls before collecting any new readiness evidence. Revisions require a new
protocol ID before that evidence. Never retune this version to observed results.
The numerical snapshot is [plans/D1_KILL_DESIGN_V1.json](plans/D1_KILL_DESIGN_V1.json).
It explicitly records `executed=false`; it is not an accepted-measurement PLAN.

For each sampled query define lower/upper opportunity duration:

- lower: exact readiness deficit intervals whose measured rival states have been
  excluded; still a structural opportunity, not guaranteed useful work;
- upper: all width-headroom intervals that could be a readiness deficit, including
  uncovered/UNKNOWN intervals; no narrower upper bound without supporting evidence;
- denominator: full query elapsed time, including drain; exclude drain from the
  numerator. Zero elapsed time, negative state or loss makes analysis invalid.

Report per query, per run and per configuration; requests are not repetitions.
Use the usual sample median; p95 is linear interpolation at index `0.95*(n-1)`
of sorted query fractions. No request pooling or query-dependent weighting.
Eligibility for a positive prioritization decision requires >=95% state/phase
coverage in every sampled query, complete candidate/request conservation, zero
overflow/drops/unmatched events, and matched negative controls. UNKNOWN cannot be
discarded from the denominator or replaced with zero opportunity.

Proposed future design: five independent runs each T8/W32 and T16/W32, fixed common
distributed qid cohort and immutable packages/config; external CPU/SQPOLL telemetry
on both. Freeze this separately, not execute it here. Treat runs as repetitions;
report query clustering and all five values, no request-level p-values.

- **D1 TOPOLOGY NO-GO:** in >=4/5 runs of each regime, median per-query **upper**
  fraction <=2% and p95 upper fraction <=5%. Even optimistic opportunity is small.
  Or a verified complete state account shows all apparent deficits are explained
  by ready-unselected/host/resource/publication states. Report the specific rival.
- **PRIORITIZE FURTHER D1 TEST, not effectiveness:** in >=4/5 T16 runs median lower
  fraction >=10%, >=75% sampled queries lower fraction >=5%, and median lower
  fraction at T16 exceeds matched T8 by >=5 percentage points and >=2x. A zero T8
  denominator is reported explicitly; require the absolute difference, never infinity.
  The lower bound must survive the matched negative controls. This licenses only a
  separate controlled hypothesis test, not optimization or a D1 claim.
- Everything else: **INCONCLUSIVE**, retain rivals/UNKNOWN. Missing conservation
  or comparability is INVALID, not a negative scientific result.

Invalid evidence and inconsistent lower<=upper bounds take precedence over any
scientific label; never resolve an accounting contradiction as a positive result.
Evidence of substantial calc-ready or issue-ready work during low inflight is a
direct falsifier of labeling those particular intervals dependency-starved.
If readiness tracks physical wait rather than an independently unresolved graph
prerequisite, deprioritize topology attribution until that separation is tested.

An optimistic elapsed-time ceiling is `1/(1-f_upper)` for `0 <= f_upper < 1`,
under the unrealistic assumptions that all counted opportunity can disappear,
remaining query work is fixed, and no extra computation/I/O/resource contention
is introduced. At 2% this is approximately 1.0204. This is **not an achievable
speedup estimate**, throughput bound, graph-change prediction or system-wide result.
At f=1 the expression is unbounded/uninformative; never print a finite forecast.

## Required negative controls and future implementation gate

1. Actual header-level controls: eligible but unselected, selected flag cleared
   before submit, evicted candidate later published, published already visited,
   empty-map shortcut vs full selector no-ready, frontier rewind after admission,
   rescore identity, full-pool rejection, mixed cache/physical FIFO.
2. Synthetic event/control traces: lost admission/eviction, duplicate identities,
   CQE before submit, publish before readiness, opposite CQE order but FIFO publish,
   interleaved workers, equal timestamps, missing phase, table overflow, old protocols.
   Old PANTRC01/02 cannot be upgraded to readiness-valid by inference.
3. Ready-unselected low-inflight negative control must never classify starvation;
   I/O-wait and FIFO-hidden controls keep overlapping/UNKNOWN attribution.
4. Lock-call control separates pre-send from submit but leaves off-CPU attribution
   UNKNOWN without independent scheduling evidence. Sampling must not alter locks.
5. Host/kernel controls preserve native unbound environment, resource telemetry,
   sampling membership and benchmark-relative phases; short telemetry samples do
   not establish critical-path causality or one SQPOLL thread per worker by source.

The minimum full observer needs an explicitly opted-in pool mutation interface,
fixed identity tables for live candidates **and out-of-pool publication residents**,
true mutation ordering, selected-before-send spans, search/drain phase boundaries,
coalesced state intervals, and a versioned exporter/checker. Fixed event capacity
must cover worst-case all16 sampled queries on one worker; bounded inflight does
not bound spin iterations or historical admissions. Capacity estimates at T1/T8/
T16 need measured/proven operation bounds plus preallocated RAM and invalidation
on overflow. Per-iteration event logging or a readiness-only scan is rejected.

For scale only, the existing 34-uint64 event at capacity65536 consumes 17MiB per
worker: 17/136/272MiB at T1/T8/T16, before query rows, correlations and allocator
metadata. This is **not a capacity proof for a new observer**. There is no justified
bound yet on candidate transitions, residual map residents or uncoalesced spins;
do not multiply a mean per-query event count by 16 and call that a worst-case bound.

This coordinated design is larger than the minimal safe hook addition certified
here. No partial observer is shipped. If separately implemented, it needs all
Issue20 optimized/sanitizer tests, T1/T8/T16 correctness DETAIL smokes, new 12-block
native STOCK/OFF/LIGHT E0 and predeclared T16 consistency calibration, full package
audits and historical replay. The current binary's old E0 pass cannot certify a
future changed binary. No new binary means those conditional measurement gates
are **not applicable here**, rather than passed or inherited.
