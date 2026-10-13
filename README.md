# Parallel ANN Research

Research-first, evidence-driven exploration of new parallel ANN methods. PipeANN is a reference and baseline, not the research destination.

**Current primary subject:** OSDI'25 PipeANN 0.1.0 plus a minimal, explicit GCC13 portability patch (`PAPER_GCC13_PORTABLE`). A native SIFT10M disk+memory index is verified. The first T8 result was preliminary; repeated results and independent offline studies are indexed below. Modern 2026 PipeANN is a separate preserved reference.

**Repeated-campaign status: UNCERTIFIED.**18 stock processes completed; mandatory T16 quality validation hit the thermal guard. Extension was not run. Published statistics are explicitly provisional; real-graph and synthetic studies did execute.

**Issue29 follow-up:** [T16-first qualification and offline decision memo](docs/research/ISSUE29_DECISION_MEMO.md). T16 correctness passed, subsequent T8 quality hit100°C; no new stock campaign ran. Oracle-disagreement and branching controls executed; tested cheap features did not improve held-out selection utility.

- [Start here](docs/START_HERE.md): clone, prerequisites, configurable paths and smoke.
- [Subjects and versions](docs/BASELINES_AND_VERSIONS.md) · [datasets/artifacts](docs/DATASETS_AND_ARTIFACTS.md)
- [Build and reproduce](docs/BUILD_AND_REPRODUCE.md) · [benchmark method](docs/BENCHMARK_METHOD.md)
- [Results](docs/RESULTS_INDEX.md) · [research roadmap](docs/RESEARCH_ROADMAP.md)
- [Research philosophy](RESEARCH_PHILOSOPHY.md) · [history](docs/archive/HISTORY.md)

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-lite.txt
cp .env.example .env                 # edit external source/data/index paths
set -a; . ./.env; set +a
.venv/bin/python scripts/ann.py preflight
.venv/bin/python scripts/ann.py campaign --dry-run
```

No command silently downloads data, rebuilds an index, tunes hardware or invokes sudo. Raw evidence/data/indexes remain outside Git; small manifests/results are versioned. The bundled historical C++ tree is retained for traceability and **is not the active paper baseline**; build the pinned sibling subject instead.

D1 remains UNTESTED, D4 NOT TESTED, D6 INCONCLUSIVE on historical modern subjects. H-V/H-G/H-C/H-F/H-QV are separate research lanes. No offline signal or simulator output is an end-to-end ANN speedup or novelty claim.
