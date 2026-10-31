# E0 v2 — bounded open-pipeline scheduling test

**MODEL_ONLY. Synthetic completion ticks are not ANN latency, QPS, Recall or
hardware speedup.** This model is not an implementation/replay of AverSearch.
[Original PR review](AVERSEARCH_QUEUE_ROLE_REVIEW.md) preserves the v1 evidence;
[E1](AVERSEARCH_QUEUE_ROLE_E1.md) states what a real comparison requires.

## Falsifiable question and limits

Can an online helper policy complete an identical two-stage workload sooner
than fixed roles after paying observation and migration costs? A positive result
would establish feasibility in these assumptions only. All N identical jobs
exist at t=0 and require m maintenance ticks followed by d distance ticks.
No work is created by distance results. No pruning, speculative duplication,
memory contention, shared queue ownership or graph dependencies are modeled.
In particular, permitting two maintainers assumes separable maintenance work.

With P workers and r maintainers, steady-state service capacity is bounded by
`min(r/m, (P-r)/d)` jobs/tick. The balance point is `r*=P*m/(m+d)` before integer
rounding, pipeline startup/drain or controller costs. More maintenance capacity
can alleviate producer starvation while simultaneously removing distance
capacity. A bottleneck, serial ownership or saturated bandwidth may prevent any
saving. This is an analytical model, not a throughput prediction for ANN.

## Exact execution contract

- Four controls: fixed1 (1 maintainer/3 calculators), fixed2 (2/2), observe
  (fixed1 roles with paid monitoring), responsive (one permanent maintainer,
  two permanent calculators, one helper initially a calculator). P defaults to
  4, may be >=3. Policy never reads job costs or future completions.
- At `t % epoch == 0`, only an idle, non-switching helper with no pending
  decision samples pending/ready queue counts. `pending>0 && ready<=low` selects
  maintenance; `pending==0 || ready>=high` selects distance; otherwise retain
  the current role. Defaults: epoch=4, low=1, high=5. No fitted thresholds.
- Monitoring occupies the helper for o ticks. Its sampled decision applies
  afterwards; a role change then occupies it for s ticks. Busy tasks are never
  preempted. Zero cost applies immediately. A stale sample is not retrospectively
  corrected. At most this one helper can migrate; no always-free manager exists.
  Worker-local epoch detection and ordinary FIFO dispatch have no separate cost:
  o is the assumed aggregate *eligible decision* cost, not measured overhead.
- Each tick then dispatches existing FIFO work in worker-index order. One tick
  of service is performed. Completion publishes at the end of the tick; results
  are available only next tick, regardless of worker order. No same-tick cascade.
- Every worker-tick belongs to exactly one of maintenance service, distance
  service, monitoring, switching, maintenance idle, distance starvation, or
  terminal distance drain idle. Starvation means empty ready queue while queued
  OR in-flight upstream maintenance remains, sampled before dispatch. Drain idle
  is separately counted when no more maintenance can publish. Counters include
  startup/drain and measure worker-time, not wall-time.
- Stop when all jobs complete. Irrelevant outstanding helper overhead is not
  drained afterwards; actual consumed overhead and remaining paid interval are
  reported (remaining current phase only, excluding any switch not yet started).
  This horizon excludes scheduler teardown. Empty input completes in
  zero ticks with null ratios. All durations/counts reject bools/nonintegers.

Reduced starvation alone is insufficient: removing calculators or replacing
idle time with monitoring can lower this counter with no useful work gain.
Always inspect makespan, full worker-time partition and both static controls.
An observation-only example below demonstrates this directly.

## Reproduce (standard library only)

```sh
python3 research/queue_role_e0.py --jobs 120 --cores 4 --maintain-ticks 6 --distance-ticks 1 --switch-ticks 1 --monitor-ticks 1
python3 research/queue_role_e0.py --jobs 16 --cores 4 --maintain-ticks 1 --distance-ticks 5 --switch-ticks 40 --monitor-ticks 1
python3 research/queue_role_e0.py --suite > /path/to/new/external/model-v2-matrix.json
python3 -m unittest discover -s tests/research -p 'test_queue_role_e*.py' -v
```

`--suite` uses its own fixed grid, ignoring individual-case flags. Grid:
N={16,120}, m={1,2,6}, d={1,5}, s={0,1,40}, o={0,1,4}; P=4, epoch=4,
low=1, high=5. All 108 combinations and four policies are reported. The grid
and source hash were written to external MODEL_PLAN.json before executing it.
Historical examples were already known; this is a sensitivity study, not blind
validation. No seeds, warmups or error bars are appropriate for simulated ticks.

## Verified v2 results

| Constructed case | Fixed1 ticks | Fixed2 ticks | Observe ticks | Responsive ticks |
|---|---:|---:|---:|---:|
| N120,m6,d1,s1,o1 | 721 | 361 | 721 | 364 |
| N16,m1,d5,s40,o1 | 31 | 41 | 32 | 42 |

In row 1, fixed1 distance-starvation is 2041 worker-ticks. Observe lowers it to
1861 but consumes 181 monitoring ticks and still finishes at 721. Responsive
uses 2 monitoring and 1 switching tick; it finishes later than fixed2. A cost
counter need not sum to `decisions*cost` when the completion horizon truncates
an irrelevant final monitoring/transition interval.

| Adaptive comparison over all 108 cases | Win | Tie | Loss |
|---|---:|---:|---:|
| versus fixed1 | 69 | 13 | 26 |
| versus fixed2 | 30 | 8 | 70 |
| versus better static split, per case | 3 | 15 | 90 |

All three best-static wins have m=2,d=5,s=0: (N16,o0) ticks 32 versus best
static 37; (N120,o0) 217 versus 245; (N120,o4) 231 versus 245. Nonzero monitoring
can alter sampling phase; neither cost nor outcomes are assumed monotonic.
These counts describe this grid, not a distribution of real ANN workloads.
No general superiority or calibrated break-even point follows.

Tests cover independent analytical static schedules, in-flight starvation,
publication delay, exact monitoring/switch timing, no preemption, hysteresis,
large epochs, incomplete terminal overhead, empty input, strict inputs,
work/time conservation, deterministic adaptation and negative controls.
See [summary and source identities](../../results/queue_role_review_20261029/SUMMARY.json).
