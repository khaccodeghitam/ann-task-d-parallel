# Parallel ANN Research

Research-first, evidence-driven exploration of new parallel ANN methods. PipeANN is a reference and baseline, not the research destination.

**Current primary subject:** OSDI'25 PipeANN 0.1.0 plus a minimal, explicit GCC13 portability patch (`PAPER_GCC13_PORTABLE`). A native SIFT10M disk+memory index is verified. An earlier single T8 result remains preliminary; the latest repeated results and independent offline studies are indexed below. Modern 2026 PipeANN is a separate preserved reference.

**Latest campaign:** Issue #32 completed and qualified 36/36 paper-stock runs under Custom Full-Fan 60/90 W. The six paired T16/T8 blocks show a median QPS change of −13.36% (90% block-bootstrap CI −14.35% to −11.49%); see the [campaign report](docs/research/CUSTOM_FULLFAN_SIFT10M_20261013.md). This result is specific to the paper-portable subject, native SIFT10M index and recorded host condition.

**Default environment for NEW ANN runs:** [Custom Full-Fan Experimental Environment v1](docs/EXPERIMENTAL_ENVIRONMENT_V1.md), observed `platform_profile=custom` and MMIO PL1/PL2 = 60/90 W; power limits and sensors must be verified before any host command. This is a prospective contract, not a retroactive relabeling or claim of peak QPS. The existing Performance 115/135 W results remain separate evidence.

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
