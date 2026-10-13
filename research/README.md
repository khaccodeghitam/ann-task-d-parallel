# Bounded offline studies

One shared source [`studies.py`](studies.py) implements the three scoped studies. They never execute or modify stock PipeANN. Run after performance measurements, with appropriate thermal supervision and no concurrent campaign.

```sh
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python research/studies.py real \
  --index "$ANN_INDEX_ROOT/sift10m_disk.index" --query "$ANN_DATA_ROOT/query.bbin" \
  --limit-nodes 20000 --memory-budget-mib 1024 --output "$ANN_RESEARCH_ROOT/evidence/NEW_OFFLINE"
python research/studies.py frontier --output "$ANN_RESEARCH_ROOT/evidence/NEW_SIM"
```

For the executed real-graph run, these arguments were passed through the existing thermal/AC/RAM guard and watchdog (`run_paper_fullfan_check.py --spec SPEC --output NEW_GUARD_DIRECTORY`, threads1/MKL1/OpenBLAS1). Raw spec/protocol hashes remain in the local archive. The standalone reader enforces its RSS/adjacency/distance budgets but does not replace thermal supervision.

`MOTIF_SIGNAL_STUDY_01`:2,000 uniform anchors; sampled directed wedge/cycle closure and edge overlap, plus held-out overlap feature test. Jaccard is not a motif count; all degrees64 makes the degree permutation stratum constant. Exact overlap needs paid adjacency or metadata.

`CANDIDATE_VALUE_ORACLE_01`:48 actual queries; independent exact-distance surrogate states after8/24 expansions;12 candidate forks/state, no mutation of Seen/topK during label calculation. Train28/validation10/test10 queries. Labels use normalized top10 distance-sum improvement. Raw `G1` atK10 denotes threshold opportunity, not a realK1 claim. A k1 invocation of the same threshold formula is well-defined; empty/partial topK is explicitly excluded. Not a faithful PQ/asynchronous counterfactual.

`PARALLEL_FRONTIER_SIM_01`: five synthetic directed families, equal24-expansion budgets, sharedIO2 and p4. Simulated time is not wall time. Ideal work/span bounds are not measured speedups. Random and decoy controls expose quality/work tradeoffs; oracle-adjacency exploration is not a ready online policy.

[Observed results and limitations](../results/paper_20261013/REPORT.md). No H-V/H-C implementation, D optimization or novelty claim is included.
