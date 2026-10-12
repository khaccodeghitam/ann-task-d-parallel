# PipeANN v0.1.0 rebaseline audit — 2026-10-12

**PAPER_REBASELINE_BLOCKED.** Official source/tag and existing package integrity
are verified. Default artifact compilation and mem_L0 compatibility failed
before any ANN benchmark. Zero new stock runs; no native index or diagnostic
binary. This directory must not be cited as a measured paper performance baseline.

| Report | Contents |
| --- | --- |
| [00 Executive summary](00_EXECUTIVE_SUMMARY.md) | Decision, actual outcomes and blockers |
| [01 Source/version audit](01_SOURCE_AND_VERSION_AUDIT.md) | Tag/tree, build proof and semantic incompatibility |
| [02 Upstream evolution](02_UPSTREAM_EVOLUTION_2025_2026.md) | 46+1 commits, active mechanisms and attribution limits |
| [03 Input/index compatibility](03_INDEX_AND_INPUT_COMPATIBILITY.md) | Full hashes, byte/source checks and native-builder mapping |
| [04 Protocol/host](04_BENCHMARK_PROTOCOL_AND_HOST.md) | Intended 66-run design, host observations and safety boundaries |
| [05 Results](05_BENCHMARK_RESULTS.md) | NOT_MEASURED table and correct metric/tail meanings |
| [06 Diagnostics](06_DIAGNOSTIC_LOGGING_AND_VALIDITY.md) | DESIGN_ONLY hooks, limitations and no trace-validity claim |
| [07 Research roadmap](07_HYPOTHESIS_RESEARCH_ROADMAP.md) | Independent H-V/H-G/H-C/H-F/H-QV1 hypotheses and falsifiers |
| [08 Reproduce/handoff](08_REPRODUCE_AND_HANDOFF.md) | Exact commands, paths, fingerprints and resumable blockers |

[PLAN.json](PLAN.json) is an immutable **blocked prospective design**, not an
execution-ready campaign: SHA256
`c79e74cb5e40fe59065c8de147ba582804f7557698b90f093d912f8d85ccf205`.
[SUMMARY.json](SUMMARY.json) records absent binary/index/result identities explicitly.

External authoritative audit evidence:
`/home/irthn/ann-research/research-v3/campaigns/PAPER_REBASELINE_SIFT10M_20261012T144741235340Z/`.
All raw source diffs, build failures, full audits, host snapshots, machine-readable
ledgers and test logs remain there. Small tooling:
[paper_rebaseline.py](../../../tools/research/paper_rebaseline.py);
tests: [test_paper_rebaseline.py](../../../tests/research/test_paper_rebaseline.py).
These helpers are passive and do not execute ANN.

No golden/instrumented source or binary modification; no data/index/historical
campaign rewrite; no algorithm, D1/D4/D6 solution, SIFT100M or novelty claim.
Main and existing Draft PRs #23/#24/#25 remain unchanged and unmerged.
