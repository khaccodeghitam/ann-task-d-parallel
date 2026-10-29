# E1 — source audit, narrow hypothesis and prospective comparison

**Native adaptive ANN: NOT IMPLEMENTED. ANN outcome: INCONCLUSIVE.**
Only the offline export checker is **IMPLEMENTED_NOT_BENCHMARKED**. No native
measurement has been launched. This is a proposed protocol, not a frozen
execution plan or a certification that the current host is safe.

## Prior mechanism and the narrower question

[AverSearch v2, §§4.2–4.4 and §5.3](https://arxiv.org/html/2504.20461v2)
describes global threshold pruning, candidate redistribution through a global
buffer, speculative distance work, and maintainer fallback distance computation.
Its §5.3 attributes some starvation to static roles. Thus it already balances
work dynamically; “adding balancing” alone is not a distinct contribution.
The E0 feed-forward pipeline omits this feedback and shared ownership. A change
in which threads do work differs conceptually from candidate redistribution,
but implementation equivalence and novelty remain unverified.

Hypothesis H: for a fixed query/index/search contract, lending one otherwise
idle calculator to **separable maintenance work** can shorten useful search
completion enough to exceed observation, handoff, publication and lost-distance
capacity costs. It must preserve the original pruning, visited rules, distance
kernel, termination and number/ownership of sub-queues. The test is of a bounded
helper, not arbitrary migration of all threads.

This is plausible when available maintenance work limits the production of
useful frontier candidates, distance capacity is temporarily excessive and
maintenance can be split safely. It can lose when maintenance has a serial
owner, vectors saturate memory bandwidth, helper work perturbs caches, tasks are
too short, snapshots become stale, roles oscillate, the frontier really has no
useful work, or additional candidates cause speculative/redundant exploration.
Lower idle counters can simply mean fewer calculators; the necessary prediction
is earlier useful completion at matched Recall after **all** costs, accompanied
by the expected service/idle redistribution. There is no assumed gain percent.

Proposed cheap signals: an owner-published unchecked-candidate count, a count
of completed distance-result batches awaiting maintenance, and per-worker
empty-poll counters accumulated locally. Sample at coarse safe task boundaries,
with hysteresis and a minimum dwell interval. Do not scan all queues, read GT,
use uncomputed distances or make a controller see future job times. Atomic
loads, cache-line traffic and snapshot publication are costs to measure.

Narrow implementation candidate, contingent on source audit: calculators help
prepare immutable completed-result batches (e.g. sorting a scratch batch) while
the existing owner alone commits queue changes. One helper lease per subgroup;
publish results with the existing synchronization rules. The controller admits
help only with an observed pending batch and calculator starvation. A low
unchecked count by itself is insufficient. If native maintenance has no
independent batch, this candidate is infeasible; do not silently add multiple
writers or change the number of queues to obtain a favorable model result.
Exact thresholds/dwell intervals must be fixed before timing from source and
calibration observations; E0 values are not native tuning evidence.

## Source and build audit (2026-10-29)

Repository search found no iQAN/AverSearch implementation in this research
checkout; E0 is Python and the native baseline is PipeANN. Bounded public search
used `AverSearch github`, `AverSearch code Luo`, exact-name GitHub repository
search, and paper links. No author-verifiable AverSearch code repository was
located. **NOT LOCATED is not proof no release exists.** Its source commit,
license, dependency lock and buildability remain UNKNOWN. No guessed GitHub
project is substituted and no author was contacted.

The [iQAN paper artifact appendix](https://johnpzh.github.io/assets/papers/PPoPP-2023_iQAN_Zhen.CameraReady.pdf)
points to [johnpzh/iQAN_AE](https://github.com/johnpzh/iQAN_AE) and
[Zenodo artifact](https://doi.org/10.5281/zenodo.7322631). A separate clean shallow
clone was inspected without changing it:

| Field | Verified value |
|---|---|
| Source commit | `da7359439ffa94909f243dd3df6be71b76ce1e35` |
| Tree | `d6c936e7f36c4da28f1a484c913d084bd6f2d4d6` |
| Root LICENSE | GNU GPL version 3 text, SHA256 `3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986` |
| Build definition | CMake >=3.9, C++14, Boost, OpenMP, `-march=native` |
| Small-data native entry | `app/PSS_v5_distance_threshold_profiling.cpp`; `core/Searching.202102022027.PSS_v5.dist_thresh.profiling.cpp` |
| Expected inputs | float fvecs base/query, NSG graph, top-100 GT; not the preserved PipeANN disk/PQ package |
| Build availability in this execution environment | `cmake`, `gcc`, `g++` absent from PATH; `/usr/include/boost` absent |
| Actual build / binary hash | NOT BUILT / absent; no successful build asserted |

Sources: pinned [CMakeLists](https://github.com/johnpzh/iQAN_AE/blob/da7359439ffa94909f243dd3df6be71b76ce1e35/CMakeLists.txt),
[LICENSE](https://github.com/johnpzh/iQAN_AE/blob/da7359439ffa94909f243dd3df6be71b76ce1e35/LICENSE),
[README](https://github.com/johnpzh/iQAN_AE/blob/da7359439ffa94909f243dd3df6be71b76ce1e35/README.md).
The audit records the root license text; no third-party code is vendored here.
Do not copy its implementation into the PipeANN baseline. Keep any future
modified source in a separate repository with its notices and pinned identity.

Once a toolchain exists, an isolated source/build check could use:

```sh
# External checkout pinned to the exact audited commit; no data or search here.
cmake -S "$IQAN_SOURCE" -B "$NEW_IQAN_BUILD" -DCMAKE_BUILD_TYPE=Release
cmake --build "$NEW_IQAN_BUILD" --target PSS_v5_distance_threshold_profiling -j1
```

These commands were NOT run. Successful iQAN compilation would still not supply
Baseline A: iQAN lacks the AverSearch role architecture under test. Reimplementing
paper pseudocode would create a new subject requiring independent validation,
not an original AverSearch baseline. The task authorizes conditional ANN work,
but source and native safety/data prerequisites are unsatisfied; no additional
permission is inferred to tune the host or alter preserved artifacts.

## Prospective experiment contract

Independent variable: scheduling mode. Start with a single small in-memory
SIFT1M workload if supported by the verified AverSearch source; do not download
or rebuild anything until source, format and artifact provenance are established.

- A: original AverSearch, original fixed role allocation and existing balancing.
  A0: pristine original binary for functional parity and observer characterization.
- B: same source and search settings, optional helper enabled via runtime flag;
  all new buffers allocated for both A/B, same total memory budget. Disabling the
  flag bypasses helper and monitoring; an observation-only flag samples/charges
  monitoring without changing roles. A/B use the same compiler/flags/library.
- C: best legal fixed role allocation selected on calibration queries only.
  Include its actual queue configuration in the identity; if it requires different
  subgroup count, disclose that difference. It is a stronger alternative, not a
  claim to isolate scheduling alone. E0's hindsight static envelope is not C.

Same immutable base, ordered query bytes, L2 distance implementation, K=100,
graph bytes, entry points, visited/pruning/tie/termination rules, total thread
count, allocated memory and machine. Proposed total budget T=8, inter-query=1;
include balancer and helper in T, no hidden service threads. Audit whether the
native source supports this configuration before freezing it. Record actual
hardware topology, CPU model/microcode, compiler and shared libraries. Inherit
unchanged affinity; do not tune power, fans, security or CPU placement.

For the standard 10,000-query SIFT1M set, use query IDs 0–1999 for calibration
and 2000–9999 for final paired measurements. Freeze the split before tuning;
if a different dataset/query count is necessary, issue a new named protocol.
Target Recall@100 >=0.99; A/B/C must additionally differ by <=0.001 absolute
recall (0.1 percentage point) in every accepted paired block. This is the declared
matching tolerance, not “identical recall”. Select search breadth and legal
static splits on calibration only, freeze a finite grid before calibration, and
publish all attempts. First test identical search parameters; if recall differs,
compare separately tuned measured points within tolerance. No test-set retuning,
extrapolation or headline QPS comparison outside the overlap.

Pre/post content hashes bind dataset/query/GT/index, original and patched source
commit/tree/patch, executable, dependencies, protocol and exporter. Original
immutable manifests are read-only. New AverSearch manifests are separate from
PAPER_STOCK, PAPER_GCC13_PORTABLE and MODERN_GOLDEN. Existing K10 PipeANN results
cannot fill a missing Recall@100 AverSearch cell.

Correctness first: tiny deterministic graphs, duplicate suppression, complete
output IDs, finite distances, queue-owner/race/termination tests, sanitizer runs,
and disabled-mode parity against A0. Use a separate correctness run to verify
exported distances against canonical vectors and independently audited GT.
Deterministic ID tie policy is part of GT identity; do not mix strict ID recall
with historical distance-tie-expanded recall.

For timing, two full warmup passes at each frozen configuration, then timed
query loop using a monotonic clock; exclude loading, warmup, GT evaluation,
exports and teardown. Preserve query IDs, per-query elapsed ns and the enclosing
wall interval. Inter-query=1 fixes concurrency while testing intra-query workers.
QPS=N_queries / timed wall seconds, not reciprocal median latency. Adaptive
execution order may change returned IDs; equal code/settings never establishes
equal Recall by itself.

Use six blocks, one run each of A/B/C, in order ABC, ACB, BAC, BCA, CAB, CBA;
all runs sequential, no concurrent builds/tests. Independent guard/watchdog,
Custom 60/90W contract and startup/sensor/AC/RAM/disk/swap gates from
[environment v1](../EXPERIMENTAL_ENVIRONMENT_V1.md) remain mandatory on the owner
host. A foreign/unsupported host needs its own measured profile. Preserve minimum
5s within-block/15s between-block gaps and >=85C startup rejection; >=99C once or
>=97C for 10s stops. Validate guard/process-group cleanup with synthetic processes
before any actual command; bind per-command timeout (initial cap 240s). Retain
all slow/failed/stopped observations, no outcome-dependent retries. Post-check
source and input hashes and quality; an invalid campaign yields no accepted gain.

Report all six block ratios and median/mean/SD/min/max; reuse
`tools/research/paper_paired_campaign.py:paired_statistics` for deterministic
20,000-resample, seed20261013, CI90 of paired QPS percentage deltas. Blocks, not
individual queries, are independent repeat units. Include leave-one-block-out
results; six blocks give limited uncertainty. Summarize within-run p50/p95/p99
from actual query samples using linear p*(n-1); show all run summaries and avoid
pooling queries as independent benchmark replicates.

## Minimal measurements and decision rule

| Metric | Definition / minimal acquisition |
|---|---|
| Recall@100 | Mean intersection of 100 unique returned IDs and the canonical top100 GT, divided by 100; offline only |
| Query p50/p95/p99; QPS | Per-query monotonic elapsed ns and total timed-query wall ns; no substituted P99.9 |
| Distances | Count actual distance-kernel evaluations, including speculative and maintainer fallback; local counters reduced after timing |
| Expansions | Count adjacency expansion starts; keep unique vertex IDs separately in diagnostic runs |
| Duplicate ratio | `(distance calls - unique (query,vertex) evaluated)/distance calls`, null if zero; unique sets are diagnostic only |
| Speculative excess | Optional separate ratio versus a defined serial search at identical parameters; not the same as duplicate ratio or automatically “useless” work |
| Queue starvation / idle | Local calculator no-eligible-work intervals excluding quiescence, separately startup and drain; sum worker-ns and normalize by calculator-active worker-ns and total worker budget |
| Scheduling/synchronization | Local time/counts for sampling, leases, publication and blocked waits; retain lost distance capacity and scratch memory; pair observation-only against disabled mode |
| Memory bandwidth | Only validated, accessible counters with documented event/byte conversion and observer cost; otherwise NOT_MEASURED, no sudo/security changes |

The new [offline checker](../../research/queue_role_e1_metrics.py) validates
complete query sets, exactly 100 unique in-range IDs, finite positive times,
strict Recall and percentiles. It hashes its run/GT input files and never invokes
search. It neither validates vector distances nor certifies a timing protocol.
A native exporter is intentionally not fabricated before the source is known.

```sh
python3 research/queue_role_e1_metrics.py --run /external/run.json --ground-truth /external/gt.json
python3 -m unittest discover -s tests/research -p 'test_queue_role_e*.py' -v
# Repository regression checks, after installing requirements-lite in a venv:
python -m unittest discover -s tests/research -v
```

Instrumented diagnostic runs are distinct from headline timing runs. Qualify
observer overhead with balanced disabled/observed pairs before interpreting
fine-grained intervals. A measured perturbation >2% requires reducing diagnostic
sampling and keeping only timing/output collection in headline runs; do not
subtract observer time from measured ANN latency. No bandwidth or mechanism
claim is made from unvalidated counters.

Predeclared practical support criterion: all identity/safety/correctness/recall
gates pass; B median QPS improves >=5% over BOTH A and calibrated C, and lower
CI90 of paired delta is >0; p95/p99 do not regress >5% in the per-run median
comparison. The 5% is a prospective practical threshold, not a predicted gain.
The diagnostic arm must show the expected work/idle redistribution at measured
cost. A QPS gain without this pattern supports a performance observation, not
this mechanism. If valid costs erase the gain or the upper CI90 is <=0, reject
this implementation in this workload (**REFUTED_WITH_SCOPE**). If CI spans zero,
recall cannot be matched, data/source/guard are unavailable or the effect misses
the practical threshold, report **INCONCLUSIVE** rather than tuning on outcomes.
No result here establishes novelty or all-dataset benefit.

Current blockers: author-verifiable AverSearch source/license; native compiler
and dependencies in this execution environment; a validated compatible graph/
vector/GT package and native exporter; implemented safe helper/disabled parity;
measured host profile with functioning native guard. Resolving these is the next
step toward actual Recall-matched evidence, not rerunning the Python model.
