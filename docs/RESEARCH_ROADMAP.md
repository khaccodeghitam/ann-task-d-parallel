# Research roadmap: independent H lanes

[Issue29 actual follow-up](research/ISSUE29_DECISION_MEMO.md): saved-state oracle audit executed; test gap is concentrated and fixed cheap-feature models give no utility improvement. No automatic online integration or broad replay is justified. Native T16 quality passed once; subsequent T8 thermal failure prevented all new stock runs. Earlier results below keep their original scope.

Read [philosophy](../RESEARCH_PHILOSOPHY.md) first. PipeANN is a reference, not the target to optimize indefinitely. D1 UNTESTED, D4 NOT TESTED, D6 INCONCLUSIVE remain historical statuses; none is reclassified here.

## Executed small studies

[Actual compact results](../results/paper_20261013/OFFLINE_STUDIES.json), [simulator cases](../results/paper_20261013/FRONTIER_SIM.json), [source](../research/studies.py), [report](../results/paper_20261013/REPORT.md).

Real-graph study uses48 whole queries split28/10/10,96 independently constructed surrogate states,1,152 candidate rows,2,000 uniform topology anchors,7,852 adjacency reads and95,242 exact distance evaluations. It is **not a PipeANN/PQ/asynchronous state replay**. Directed transitive/cycle closure opportunities are sampled wedges, not full motif counts. Jaccard is overlap, not a motif count. Random vertex-induced subgraphs were avoided; full outgoing rows are fetched from a uniform anchor sample and a separate query-conditioned surrogate traversal. Neither sampling scheme establishes global motif prevalence or real PipeANN access distribution.

For stateS with at leastK discovered exact distances, deterministic distance/ID topK utility is negative sum of topK distances. `Gk` is normalized improvement after revealing unseen outgoing neighbors. Empty/partial topK is excluded. For k1, the tested threshold formula is max(0,tau−best novel distance). The executed raw CSV field `G1` at k10 is a **k10-threshold opportunity**, not a claimed measured k1 nearest-neighbor gain; models useGk only. Fixed-state batch marginal gain uses set union and deterministic ties. It does not emulate policy continuation, prefetch, latency or multihop search, and establishes no general submodularity theorem.

Features include candidate exact distance, frontier rank, constant degree64 and history. Adding overlap slightly worsened held-out RMSE and changed no selected candidate relative to baseline. Degree-stratified permutation control was included (all sampled degrees64). Validation/test queries are disjoint; uncertainty clusters by query.40.19% candidates had positiveGk; mean49.97 novel neighbors but only1.28 below the current threshold. Novel discovery is not automatically useful progress.

## Decision matrix

| Lane | Theory | Engineering/cost | Measured empirical result | Novelty | Next decision |
|---|---|---|---|---|---|
| H-G motif/overlap | Coherent local redundancy proxy; not query utility | Exact overlap needs unread adjacency or paid metadata;4bytes×640M edges=2.56GB | Tested overlap gives no selection gain; RMSE slightly worse | UNKNOWN; evolution audit is not exhaustive prior-art proof | Deprioritize this raw overlap feature; no online integration |
| H-QV1 candidate value | Fixed-state one-step utility well-defined | Bounded offline oracle feasible; faithful PQ/runtime state remains missing | Oracle meanGk0.041455 vs nearest choice0.037270; simple models do not exploit gap | UNKNOWN | Conditional cheap feature screening on existing rows; no ANN speedup claim |
| H-F parallel frontier | Chain span prevents parallelism; branching can expose work | Synthetic model includes shared IO and scheduling costs; adjacency-based diversity is oracle metadata |125 synthetic cases; no chain benefit; decoy exploration changes recall, random can lose recall | UNKNOWN | Keep as model-supported mechanism, require paid-feature and equal-recall real-state controls |
| H-V vector/PQ | Batch reuse may amortize code/lookup traffic | Extra buffering/cache cost and delayed dependencies can dominate | NOT_MEASURED | UNKNOWN | Bound table/code bandwidth vs saved evaluations before microbenchmark |
| H-C resource concurrency | More query workers also add SQPOLL/CPU demand | Hybrid cores, busy polling and thermal policy confound |18 stock outputs show provisional T16 loss; campaign uncertified | UNKNOWN | Stable-condition qualification precedes mechanism attribution; no affinity tuning |

[Upstream evolution](research/paper-rebaseline-20261012/02_UPSTREAM_EVOLUTION_2025_2026.md) includes candidate/prefetch/runtime changes; source similarity is neither a measured gain nor novelty clearance. No reviewed-source fact proves our motif/frontier mechanisms are new.

The next cheapest justified research action is **offline analysis of oracle-best vs distance-choice states and feature acquisition costs**, using saved candidate rows. Do not buy2.56GB metadata for a feature that selected no better candidate. A future end-to-end prototype needs a separately authorized, source-faithful state contract and recall-matched baseline; do not rebuild this index or revive D instrumentation automatically.
