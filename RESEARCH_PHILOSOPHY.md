# Research Philosophy — Parallel ANN Research

> **PRIMARY RESEARCH CHARTER. Read before planning, evaluating, implementing, or reporting ANN research.**
> This defines research reasoning priorities, not a replacement for explicit owner authorization, integrity rules, or evidence.
> **Research-first · First-principles · Critical thinking · Exploratory development · Falsifiable evidence.**

## 1. Central principle

**Không mặc định ý tưởng đúng chỉ vì người nghiên cứu đề xuất. Không mặc định ý tưởng sai vì nó chưa từng xuất hiện trong tài liệu. Phân tích bản chất bằng lý thuyết, toán học, thuật toán, kiến trúc hệ thống và thực nghiệm; đồng thời chủ động phát triển những hướng mới có cơ sở.**

An unconventional or not-yet-published idea requires **serious mechanism analysis**, not reflexive agreement or dismissal. Lack of matching literature is neither evidence of impossibility nor proof of novelty.

The purpose of this research is to create, test, and evaluate genuinely useful approaches to **parallel approximate nearest-neighbor (ANN) search**, potentially involving new algorithms or architectures. The objective is **not** to patch PipeANN simply because a hotspot or inefficiency is visible.

## 2. Mandatory independent questions

Never substitute the answer to one question for another.

| Question | Means | Evidence |
|---|---|---|
| Theoretical coherence | Is the proposed mechanism internally consistent and compatible with applicable principles? | Explicit assumptions, mathematics, algorithms, proofs or counterexamples |
| Practical feasibility | Can the idea be implemented and function with realistic cost/resource limits? | Cost model, small prototype, controlled experiments |
| Improvement value | Does it improve the relevant objective against fair alternatives? | Recall-matched QPS/latency, scaling, resource cost, ablations, replication |
| Novelty | What is meaningfully different from prior work? | Careful literature positioning, distinguishable algorithmic contribution |

**Novel ≠ feasible ≠ useful ≠ proven.** A first failed experiment may invalidate a narrow implementation or assumption, not the entire open-ended idea.

## 3. Collaborative behavior: no yes-man, no shallow veto

When an owner proposes a raw intuition, the assistant/research agent must:

1. **Steelman the mechanism**: identify what structure, relationship, computation, dependency, or resource could yield a benefit; formulate the strongest coherent hypothesis before judging it.
2. **Search the design space**: consider alternative algorithmic locations and representations beyond the initial example. If A is weak at traversal, investigate A′ at indexing, construction, batching, or scheduling. Consider principled combinations of independent ideas.
3. **Quantify**: state costs, expected savings, asymptotic bounds where possible, overlap/critical paths in a parallel system, capacity/memory effects, and realistic operating assumptions. Do not invent expected gain percentages.
4. **Challenge**: seek counterexamples, failure conditions, correctness/recall tradeoffs, negative controls and stronger simpler baselines. Do not equate novelty with worth.
5. **Make falsifiable**: define predictions, success/failure/unknown observations and the cheapest credible experiment. Distinguish evidence from speculation.
6. **Use literature constructively**: consult papers to learn techniques, proofs, limits, controls and prior art, not to prohibit unstudied ideas. A similar paper does not automatically close an avenue; a genuinely equivalent prior method must be acknowledged.

If a relevant theorem rules an idea out under applicable assumptions, say so and show the contradiction. If evidence is insufficient, say **UNKNOWN** instead of forcing a yes/no verdict.

## 4. Research ideas are not fixed locations

The owner’s examples are **starting points, not an exhaustive list or mandatory architecture**:

- **Vector computation**: distance/PQ operations, batching, SIMD, layout, memory locality or reduced redundant computation.
- **Graph structure and motifs**: motif statistics or local structure that may help construction, indexing, graph layout, routing, candidate selection, workload grouping, or parallel traversal.
- **CPU core/thread resource organization**: worker scheduling, P/E/SMT placement, task decomposition, I/O cooperation, latency hiding, coordination and contention.

Explore new directions and combinations when justified. Do **not** force any of these ideas to become a PipeANN-specific patch. Distinguish generic ANN methods from platform-specific systems improvements.

## 5. PipeANN: reference and baseline, not the research destination

**Role A — Research reference:** inspect and use PipeANN to explore and test suitable hypotheses, not to assume its bottlenecks dictate every research direction.

**Role B — Performance baseline:** compare the new method against unmodified golden PipeANN under defensibly matched hardware, input/query workload and evaluation conditions.

A proposed method may use an independent implementation or a deliberately modified prototype, but must not overwrite the golden subject or silently reclassify its measurements.

For fair comparisons:
- Match dataset, query set, distance metric, K, evaluation methodology, hardware and operating conditions.
- Match recall or evaluate the **recall–throughput/latency tradeoff**; QPS wins with degraded recall are not unconditional wins.
- If index construction differs, report build time, memory, disk/index size and amortization instead of requiring identical index bytes.
- Use prospectively selected configurations, paired runs and report uncertainty; compare baselines contemporaneously when host state changes.
- Preserve input/index/protocol identities, raw evidence and scientific provenance. Never cherry-pick favorable runs.
- Separate measurement-observer correctness from the algorithmic hypothesis.

**Existing evidence:** a quiet SIFT10M W32 golden screening observed T16/T8 QPS median delta approximately −8.51% in its specified conditions. This validates a scaling phenomenon, **not** any specific D-mechanism, causal resource bottleneck, nor a proposed solution.

## 6. D-hypothesis boundaries: learn without becoming trapped

D1 dependency starvation is **UNTESTED**; restricted D1-O2a observation is **INCONCLUSIVE**, D1-O2b design is **NO-GO for that observer**, not a falsification of all topology approaches. D6 FIFO publication HOL is **INCONCLUSIVE** under its prespecified test. D4 frontier/selector is **NOT TESTED**. Keep exact versioned evidence and avoid converting an observer failure into a scientific negative result.

Do not require solving all D-hypotheses before designing new approaches. Only add instrumentation if a particular unresolved variable would materially change the next research decision. Time-box tools and avoid endless readiness gates.

## 7. Minimal hypothesis-development protocol (flexible, not bureaucracy)

For each idea, record only what meaningfully changes the decision:

| Field | Required content |
|---|---|
| Research problem | What measurable limitation or opportunity is targeted? |
| Mechanism and variant(s) | How is benefit obtained; where else could it apply? |
| Assumptions and cost model | What must hold, what is saved, what new cost is incurred? |
| Necessary prediction | What should change if the explanation is right? |
| Counterexample / falsifier | What plausible observation would disfavor or reject it? |
| Cheapest next test | Toy proof/simulation/microbenchmark/prototype before full campaign when sufficient |
| Comparison contract | Workload, recall, cost, variance and reference algorithm |
| Evidence label | PROPOSED / MODEL_SUPPORTED / EXPERIMENT_SUPPORTED / REFUTED_WITH_SCOPE / UNKNOWN |

Stop or pivot when a validated theoretical contradiction or repeated controlled counterevidence defeats the **specified** mechanism; do not persist indefinitely. Conversely, never reject a whole family because its first placement fails.

## 8. Efficiency and authorization

**Do not confuse infrastructure completion with scientific progress.** Prefer the smallest experiment that can change a decision. Avoid building a generic profiler, trace platform, scheduling framework or broad PR without a clear hypothesis-specific information need.

No new real ANN benchmark, host tuning, sudo access, changes to golden PipeANN, historical evidence, frozen plans, or GitHub merges without the owner's explicit task-specific authorization. Preparation and synthetic tests are not benchmark authorization.

Agent responses should distinguish **observed facts**, **deductions under assumptions**, **plausible explanations**, **unknowns**, and **the next discriminating experiment**. Never flatter, overclaim novelty, or veto based only on absence of similar papers.

## 9. Reading priority for humans and coding agents

1. **Read this charter first** for research planning and scientific interpretation.
2. Read the latest research status and the relevant immutable experiment/PR evidence.
3. Read source and related literature as needed to explain the mechanism.
4. Propose minimal tests or implementation only after identifying what question they answer.
5. Respect owner decisions and the distinction between idea exploration and authorized measurements.

This file is intended to stay stable; amend it through an explicit, reviewed documentation change if the research philosophy changes. It is an **internal project charter**, not a guarantee that outside sessions or tools automatically ingest every repository file.
