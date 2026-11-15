# Pre-registration v1 — prospective D×A study, not executed

The reviewed proposal defines the gates. This file freezes the first study's
comparison rules, while unavailable artifact/host/seed identities stay OPEN.
Before any real measurement, write a new immutable resolved protocol with hashes
and host identity; do not edit this version to fit results. No P3 run is authorized
by a successful structural preflight alone.

## Hypotheses and smallest study

H1/H2: at matched Recall, A0 and A3 differ in parallel scaling, work inflation or
synchronization cost beyond differences in their single-worker work. H3 (a
topology/progress-aware scheduler) is unopened until P3–P4 support a mechanism.
Primary dataset MS-Turing-1M, n=1M, d=100, float32 L2, public query/GT hashes in
manifest. Pilot: A0/A3 × p=1/4. Add A1 control before attributing an effect to H17;
add p=2 after pilot stability. A2/A4/D0 and another dataset are later extensions.
Keep one engine, metric, ID mapping, initialization/termination policy and data
layout across graphs. Vary search beam per graph/worker only during validation.

## Quality and query split

Recall@10 floors .990 and .998. A floor pass alone is never exact Recall matching.
For prospective Task D tuning, sort query IDs by SHA256 of UTF-8
`task-da-v1:20261115:<decimal-id>`; first 10,000 are validation, remaining 90,000
test. Record SHA256 of both ordered ID lists before running. Public queries have
already been used by Task A; this is a Task D tuning holdout, not a previously
unseen dataset. Start beams from a broad validation sweep, not assumed Task A
values; save all settings and failed-quality runs. Freeze settings before test.

Report native operating points and exact measured Recall. A direct matched-point
comparison requires both configurations above the target with absolute Recall
difference <=0.0001 (prospective tolerance, not proof of statistical equality).
Also show the full Recall–latency curve and target interpolation as a sensitivity
analysis using only observed bracketing points, no extrapolation. If matching
fails, report HOLD/quality tradeoff rather than unconditional speedup. ON counts
must be measured at the same operating points; BUILD counters are excluded.

## Replication and execution

Aim for 3 independent OFF builds per arm; those reported in the sheet may be
reused only after file hashes, source/diff/binary, dataset, build flags, seed or
actual randomness mechanism and raw receipts are verified. Unknown seeds cannot
be invented. If recovery requires rebuilds, assign new run IDs and a separate
campaign; do not impersonate historical graph hashes. At least 5 process-level
timing repeats per graph/setting. Graph replicate is the independence unit;
5 processes on one graph are not 5 graph replicates.

Run one benchmark process at a time. Paired/interleaved arm-worker order uses
the same recorded query blocks (1,000 queries) and a frozen shuffle seed 20261115.
Use separate OFF timing and ON instrumentation processes. Warm up a fixed 100
validation queries before timing each process; test queries and graph remain
memory resident. Include per-query scheduler/reset costs; exclude loading,
validation and output serialization from search interval, record each separately.
No thermal/frequency/power/affinity changes in this PR. Qualified measurement
requires an explicitly named host profile, verified guard and stable pilot;
thresholds depend on that profile and are not invented from fixture timings.
Keep stopped and slow runs with reason/status. Do not rerun only slow cells.

## Outcomes, uncertainty and decision

Primary: absolute per-query latency distribution at matched Recall, p50/p95;
QPS separately at concurrency=1 (intra-query p does not mean p concurrent queries).
Report work D, expansions, duplicate attempts/expansions with explicit meanings,
per-worker attribution, synchronization/merge/idle costs and peak RSS/index bytes.
Missing metrics = NOT_MEASURED. Report p99 only with enough observations and
uncertainty; no serving-tail claims from this offline workload.

S(G,p)=T(G,1)/T(G,p); E=S/p; I_D=D(G,p)/D(G,1)-1.
Interaction Δ=log(S(A0,p))-log(S(A3,p)); show absolute T as well as S.
Hierarchical paired analysis: graph replicates outer, process repeats and paired
query blocks inner, 95% uncertainty intervals. Three graphs limit precision;
publish estimates and dispersion, do not overstate narrow query-only intervals.

Prospective continuation target: a stable graph×worker difference in latency
scaling of at least 5% (|Δ|>=log(1.05)), or >=10% work/sync difference explaining
an actionable bottleneck, surviving quality matching and A1/degree controls.
An interval spanning zero is INCONCLUSIVE/HOLD, not positive evidence. These
thresholds guide whether to invest, not establish novelty or guarantee a gain.
For a later scheduler, preregister its objective/ablations before test tuning;
no scheduler has been designed or benchmarked here.

NO-GO/PIVOT if controlled evidence shows no graph×worker effect beyond sequential
cost/degree, or representation/quality confounds cannot be removed. P4 must find
a Task D execution bottleneck with a cheap observable signal before opening P5.
Comparisons against best-tuned fixed/staged baselines, controller overhead and
negative results remain mandatory. Paper novelty review is deferred with P5,
and no novelty claim is made in P0/P1.
