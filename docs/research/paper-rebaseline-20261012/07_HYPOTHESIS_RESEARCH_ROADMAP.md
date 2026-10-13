# Independent hypothesis roadmap after source audit

These are **HYPOTHESES**, not D implementations, measured gains or novelty claims.
Primary baseline remains intended v0.1.0; its valid local performance foundation
is BLOCKED. Modern history is prior mechanism evidence, not the destination to
optimize. Preserve D1 UNTESTED / D4 NOT TESTED / D6 INCONCLUSIVE on old subjects.

## Cost model and decision discipline

Let per-query service C be useful distance/graph work, I useful physical I/O,
X speculative/duplicate work, S coordination/scheduling. Under bounded compute
and storage capacity, throughput cannot exceed min(P/C_eff, B/I_eff); query
latency also depends on the critical path, not only totals. Changing C can alter
I or recall. Amdahl's 1/((1−f)+f/s) is only an optimistic bound when f represents
the unhidden affected service, not every cycle inside an overlapping function.
No f/s values have been measured for this paper on this laptop.

## H-V: vector/PQ computation and locality

Mechanism: amortize query-table initialization or batch lookup/layout traffic
without changing distance/selection quality. Model benefit ΔC > packing/setup+
cache pollution and any added queue delay; a bandwidth limit can dominate SIMD.
**Counterexample:** exact/PQ work already hidden by I/O; faster kernels add no
end-to-end gain, or batching delays the first useful expansion.
Cheapest next test after supported build: isolated deterministic equivalent
PQ-distance kernels on actual32-byte codes, measure correctness and cycles/
bytes at bounded sizes, before ANN changes. Use scalar/stock and existing modern
prefetch/PQ layout as controls. A local faster kernel alone is not a recall-matched
system improvement. Modern69584994/504662ab/2ec84fe2 already cover contiguous
partitioning, faster training/encoding and prefetch abstractions; avoid presenting
the same representation as a new contribution.

## H-G: graph/index motifs and layout

Mechanism: neighborhood overlap/bridge structure may predict exploration gain
or permit page co-location, reducing physical pages per newly useful candidate.
Define J(u,v)=|N(u)∩N(v)|/|N(u)∪N(v)|; this is a structural signal, not query value.
Co-location helps only if queries actually co-access nodes and saved pages exceed
reordering/build/storage cost. **Counterexample:** high-overlap communities trap
search; low-overlap bridges are essential for hard queries, so redundancy pruning
can harm recall. Start with read-only sampled adjacency statistics on the existing
verified index and a toy graph/search simulator; no real index rewrite in this task.
Require query-held-out validation and build amortization C_build/N_queries against
query savings. Modern PiPNN/OOD/dense/filter bridges are documented graph changes;
Vamana/non-filtered motif ideas must explicitly distinguish their mechanism.

## H-C: CPU scheduling/resource organization

Mechanism: worker/ring service competition may decrease useful aggregate service
at larger T on a hybrid20-logical-CPU laptop. Distinguish on-CPU poll work, runnable
delay, device wait and frequency. Lifetime SQPOLL count is not search-phase occupancy.
The paper setup's56 contexts is a specific source fact worth checking after build,
not proof that56 active kernel pollers cause slowdown. **Counterexample:** storage
queue dominates, so relieving scheduler service changes little; moving work also
adds synchronization. Lowest-cost next evidence is existing `/proc`/sysstat phase
diagnostics with precise search markers if safely available; privileged profiler
access is outside this task. No affinity or SQPOLL-policy prototype is implemented.
Latestad9 locking fix concerns holder/waiter lifetime under contention; it does
not establish a scheduler cause in immutable static plain search.

## H-F: parallel frontier work organization

Mechanism: independent useful expansions can overlap computation while controlling
stale selection and speculative I/O. Model Δcritical_path saved against redundant
distance/pages, merge ordering and coordination cost. **Counterexample:** newly
revealed candidates invalidate stale work, or independent frontier entries have
high overlap; extra parallelism burns service without recall gain. Use a tiny
deterministic graph simulator comparing sequential information order with bounded
independent batches, reporting recall/work/critical-path under explicit service
assumptions. ModernCandidatePool/markers/batch merge already reduce bookkeeping;
parallel frontier is not merely reimplementing those helpers. No algorithm patch
is justified before usefulness and quality are demonstrated.

## H-QV1: query-conditioned marginal exploration value

Let state S contain currently known/discovered candidates and result set. Define
incremental information g_q(v|S), e.g. new promising candidates or reduction in
true top-K miss count, and physical/compute cost c_q(v|S). A policy would require
g/c to generalize to unseen queries at a lower total cost. PQ distance is only one
observable proxy; rank, novelty, graph overlap and query phase may matter.
**Counterexample:** apparent high novelty reveals distant dead ends; oracle value
depends on unseen descendants; logged trajectories omit alternatives and cannot
identify counterfactual benefit. First test on toy/small fully inspectable graph
states with held-out queries, an oracle upper bound and simple distance-only/novelty-
only controls. Label offline “new neighbor count” as descriptive, not a learned
causal utility target. Need bounded state replay and quality-preserving later
ablation; current DESIGN_ONLY trace does not supply it.

## Priority and dependency-aware next action

1. Resolve exact paper build +supported initialization contract. This changes
   whether the primary comparator exists; no amount of new tracing replaces it.
2. Validate source-stock loading/quality and native-index construction cost,
   then execute a newly frozen bounded stock suite. Preserve warmup/index caveats.
3. In parallel, cheap theoretical/toy H-QV1/H-G checks can falsify proxy assumptions
   without another campaign or general profiler. They are proposals, not work done.
4. Choose one later prototype by demonstrated information value: H-V if unhidden
   vector service is material; H-C if phase-aware service evidence supports it;
   H-F/H-QV1 if useful independent exploration survives overlap/quality controls.

GO means a necessary prediction survives a credible control with cost/quality
evidence. NO_GO is scoped to that mechanism/assumption; INCONCLUSIVE is retained
when service attribution, calibration or counterfactual value is missing.
Novelty requires a separate prior-art comparison after useful feasibility,
not inference from absence of a paper or a mechanism's new name. No new D program,
ANN optimization, SIFT100M run, graph alteration or claimed research contribution.
