# PR #52 independent review and Step 3 outcome — 2026-10-29

Review subject: [PR #52](https://github.com/Irthn1311/Parallel_ANN_Research/pull/52),
`c59e36651d1cdde22c8a1faa3039c96bb05fc2cf`; fetched main
`1613b53cca2e3853f8d6f06b89772a3587dea1ab`. Both matched local refs and GitHub.
The working tree was initially clean. All three changed files and all three E0
commits were inspected against main. PR was already Draft, with no comments.
Continue on its existing research branch; preserve the reviewed commits, update
this Draft, do not merge. No stock source, binary, index, frozen plan or historical
result is edited.

**E0 completed, MODEL_ONLY. Real same-Recall/same-hardware Step 3 is incomplete;
ANN hypothesis INCONCLUSIVE.** See [E0 specification/results](AVERSEARCH_QUEUE_ROLE_E0.md),
[E1 design and source audit](AVERSEARCH_QUEUE_ROLE_E1.md) and
[compact verified summary](../../results/queue_role_review_20261029/SUMMARY.json).

## Findings against the original commit (line numbers refer to c59e366)

No Critical defect found within the explicitly synthetic scope. Major means a
measurement/experimental defect capable of changing this study's interpretation;
Minor means a contract/reproducibility issue. None implies a native ANN defect.

| Severity | Location at reviewed commit | Finding and evidence | Resolution |
|---|---|---|---|
| Major | `research/queue_role_e0.py:79–84` | Starvation requires `pending`, ignoring maintenance in flight. One job, maintenance=6, distance=1, four workers: total 7 ticks, reported distance idle=0 despite three calculators waiting for six ticks (18 worker-ticks). The metric also depends on earlier workers popping `pending` within the same tick. | Snapshot upstream liveness before dispatch; separately count starvation and terminal drain idle; partition every worker-tick. |
| Major | `research/queue_role_e0.py:50–69` | Monitoring/controller decisions are free. `switch_ticks` pays migration only. Occupancy reads, role scans and repeated reassignment attempts have no time cost; therefore the proposed break-even hypothesis is not tested. | Explicit paid monitoring on the helper; observation-only control; sensitivity over monitoring and switching costs. Costs remain invented, not calibrated CPU costs. |
| Major | `research/queue_role_e0.py:44,106–114`; `tests/research/test_queue_role_e0.py:23–31` | Only a fixed 1:3 split is tested. With homogeneous maintenance-heavy jobs a static 2:2 split can explain the apparent gain without adaptation. The old tests cannot distinguish resource allocation from controller value. | Add fixed 2:2 and monitoring-only controls. Revised favorable example: fixed1=721, fixed2=361, adaptive=364 ticks. |
| Major (external validity) | `research/queue_role_e0.py:41–44,79–92`; `docs/research/AVERSEARCH_QUEUE_ROLE_E0.md:6–11,30` | All maintenance jobs exist initially and each produces one mandatory distance job. No graph-dependent feedback, queue ownership, global pruning/balancing, speculative work, cache or bandwidth limit exists. Extra maintenance capacity is assumed freely parallelizable. This is not Baseline A (original AverSearch). Completing equal IDs validates work conservation only. The old document correctly disclaims ANN results; those caveats must be retained. | Relabel as an open pipeline feasibility model; no purported native baseline. Specify source-dependent ownership requirements in E1. |
| Minor | `research/queue_role_e0.py:50–69`; old memo `:10` | Only desired role count is epoch-gated; actual reassignment runs every tick. Counterexample n=4, maintenance=5, distance=1, epoch=4, switch=2 changes roles at ticks 0 and 10. Documentation implies switches only at epochs. Not intrinsically an invalid scheduler, but the execution contract is inaccurate. | Sample only at idle epochs; explicitly apply the sampled decision after paid monitoring, then switching. Tests check both times and prohibit preemption. |
| Minor | `research/queue_role_e0.py:33–39,96–102`; tests `:33–37` | Python booleans pass integer validation, fractional thresholds are accepted, and thresholds are absent from output configuration. Empty input, delayed publication, exact cost accounting and adaptive determinism lack tests. | Strict non-boolean integers, empty input contract, complete config, independent static oracle and adversarial tests. |

Original switch delays do consume the specified number of model ticks, and
end-of-tick publication prevents later workers seeing new results instantaneously.
Those parts are sound; they are not counted as defects. Sorted completed IDs
check exactly-once completion but say nothing about useful ANN discoveries,
query termination, Recall, redundant graph exploration or memory traffic.

## Independent execution

Original focused tests: **4/4 passed** using Python 3.12.3. Reproduced original
examples exactly: 721/362 (ratio 1.991713), 31/57 (0.543860). Original edge
counterexamples are retained externally, including the 0-vs-18 starvation bug
and off-epoch switches. Do not replace these historical numbers with v2 outputs.

First full-suite attempt: 413 discovered tests, three import errors because
system Python lacked NumPy. This was an environment failure, not hidden or
classified as a model defect. A private dependency-only environment then used
NumPy 2.5.4 and jsonschema 4.26.0 from `requirements-lite.txt`:
**491/491 dataset-free tests passed**, including **21 focused tests** (15 model,
6 offline export checker). Linux native integration was not opted into. No ANN
benchmark, index build or compiler workload was run.

The static model is independently checked against a finish-time recurrence on
486 small cases. Another 192 parameter combinations check deterministic results,
work conservation and total worker-time accounting. Model sensitivity includes
all 108 predeclared combinations, four policies each; no slow cases removed.
These deterministic cases are not statistical replicates and have no ANN CI.

## Decision

The original evidence was reproducible but insufficient to establish a dynamic
controller's advantage over an adequate static split. Revised E0 retains wins,
ties and losses: adaptive versus the better of both static allocations wins 3,
ties 15, loses 90. All three wins assume zero switching cost. The better-static
comparison is a descriptive per-case lower envelope, not an online oracle policy.

The universal claim that adaptation always helps is **REFUTED_WITH_SCOPE** by
explicit model counterexamples. The conditional theoretical mechanism remains
coherent; its usefulness on AverSearch is **INCONCLUSIVE**. No novelty conclusion.
The metric reader is **IMPLEMENTED_NOT_BENCHMARKED**; no native adaptive ANN
implementation or **EXPERIMENT_SUPPORTED** result is delivered.

Raw evidence archive ID: `QUEUE_ROLE_REVIEW_20261029`. Public summaries use
relative filenames and SHA256s; raw logs, original source copy, matrix and
source audit stay outside Git. Record the archive root separately on the owner's
machine. Historical PAPER_STOCK, PAPER_GCC13_PORTABLE, MODERN_GOLDEN and their
D1/D4/D6 statuses remain distinct and unchanged.
