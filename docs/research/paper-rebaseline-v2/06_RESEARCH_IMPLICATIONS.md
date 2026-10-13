# Research implications and independent next decisions

**VERIFIED SOURCE FACT:** the47-commit evolution audit remains intact in PR26 report02:82936410 reconstructs runtime/index ownership and adds mem0 fallback;69584994 changes PQ training/partitioning; c3ef9f19/c13236d5 introduce candidate markers/batch merge/prefetch; latestad9 fixes sparse-lock holder/waiter ownership/contention. None is newly measured here; no per-commit gain or attribution is asserted.

**HYPOTHESIS:** H-V SIMD/locality changes matter only when unhidden vector service exceeds packing/cache cost; faster distance computation can yield no ANN gain under I/O critical paths. Math portability checks establish a usable kernel, not acceleration evidence. Cheapest later test is deterministic PQ-kernel equivalence/cost at actual32-byte layout after baseline exists.

**HYPOTHESIS:** H-G adjacency overlap can reduce co-access pages but can also remove useful bridges and damage recall. Read-only toy/sampled adjacency analysis with held-out query relevance precedes any graph alteration. Current entry graph structural validity supplies no query-level motif value.

**HYPOTHESIS:** H-C scheduler/ring competition may reduce aggregate useful service; paper's fixed56 context setup differs from modern resource ownership. It is not proof of56 simultaneous SQPOLL pollers or of the old T16 regression. Stock phase-aware passive diagnostics should establish actual service before a scheduling experiment; no privilege/affinity change here.

**HYPOTHESIS:** H-F useful independent frontier work can shorten critical paths only if stale/redundant speculation and coordination costs are smaller. Existing modern batch/marker optimizations are prior mechanism evidence, not a novel parallel frontier proof. Tiny deterministic graph simulations offer cheaper falsifiers than broad tracing.

**HYPOTHESIS:** H-QV1 query-conditioned incremental information per cost needs explicit state and counterfactual controls. New-neighbor counts may predict novelty without predicting true top-K value; omitted alternative expansions and descendants can confound any logged label. Start with fully inspectable toy states, distance-only/novelty-only controls and held-out queries.

Recommended immediate decision: resolve the **measured mutable power-policy condition**, then finish a native disk index in a fresh path and freeze a fully bound protocol. This is not an invitation to tune RAPL or assume Performance Mode guarantees stability. Do not optimize PipeANN or revive D1/D4/D6 to repair the baseline. Source history and first-principles roadmaps remain useful despite missing performance evidence; neither absence of a matching paper nor a similar implementation determines usefulness/novelty alone.
