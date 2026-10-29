# E0 — Queue starvation and dynamic worker roles (synthetic)

**Evidence status: MODEL_ONLY. This is not an ANN search, Recall measurement or hardware speedup.**

## Question
AverSearch §4 separates sub-queue maintenance and distance calculation; §5.3 identifies queue starvation and imperfect resource utilization. Does assigning an idle distance worker to queue maintenance reduce waiting enough to offset the cost of switching roles?

## Controlled comparison
- **Fixed:** 4 worker slots, 1 maintainer and 3 distance calculators.
- **Responsive:** 4 slots; 1 or 2 maintainers based on ready-queue occupancy and pending work. Reassignment is allowed only when idle, at a fixed decision epoch, and incurs a configurable cost.
- Identical frozen task IDs and identical maintenance/distance work. No ANN graph, query vectors, candidate selection, native concurrency, SSD, Recall or throughput. Timing units are simulated ticks, not milliseconds.

## Reproduce
```bash
python research/queue_role_e0.py --jobs 120 --cores 4 --maintain-ticks 6 --distance-ticks 1 --switch-ticks 1
python research/queue_role_e0.py --jobs 16 --cores 4 --maintain-ticks 1 --distance-ticks 5 --switch-ticks 40
python -m unittest discover -s tests/research -p 'test_queue_role_e0.py' -v
```

## Executed local synthetic examples

| Invented scenario | Fixed ticks | Responsive ticks | Fixed/responsive ratio |
| --- | ---: | ---: | ---: |
| Maintenance bottleneck, cheap switch | 721 | 362 | 1.992 |
| Distance bottleneck, expensive switch | 31 | 57 | 0.544 |

All jobs completed exactly once under both policies. Ratios are solely about this synthetic cost model. The second case is a counterexample against assuming adaptation is always better.

## Interpretation and next step
Model evidence supports a conditional scheduling intuition, not an end-to-end algorithmic improvement or novelty. Before a **real same-Recall** comparison, obtain pinned native iQAN/AverSearch implementations, instrument queue-empty time, overhead, expansions and useful/duplicate work; implement a toggleable policy in an isolated fork; run static vs dynamic at the same graph, data, CPU allocation, host state and **matched Recall@100**, measuring QPS/latency and uncertainty. Do not substitute this repository's frozen PipeANN SSD binary for iQAN/AverSearch or write to any stock subject. Real ANN benchmarking requires separate authorization and safe host conditions.

## Sources
- Speed-ANN (2022): https://arxiv.org/abs/2201.13007
- iQAN (2023): https://johnpzh.github.io/assets/papers/PPoPP-2023_iQAN_Zhen.CameraReady.pdf
- AverSearch (2025), §4, §5.3: https://arxiv.org/html/2504.20461
- Repository charter: [RESEARCH_PHILOSOPHY.md](../../RESEARCH_PHILOSOPHY.md)
