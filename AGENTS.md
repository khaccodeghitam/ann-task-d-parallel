# Research agent entrypoint

Read [RESEARCH_PHILOSOPHY.md](RESEARCH_PHILOSOPHY.md), then [docs/START_HERE.md](docs/START_HERE.md) and the relevant frozen evidence before work.

- PAPER_STOCK, PAPER_GCC13_PORTABLE and MODERN_GOLDEN are distinct subjects. The historical T16 regression proves no D mechanism or new algorithm benefit.
- Keep stock binaries, immutable inputs/indexes, historical raw evidence and frozen plans unchanged. Record source, binary, package and protocol identities.
- No sudo, fan/power/affinity/security changes, unrelated process termination, history rewrite or merge without explicit authorization. Current owner task authorization governs ordinary safe work.
- Run sequential benchmarks with functioning safety guard; never discard slow runs. Keep raw data external, publish compact relative-path summaries.
- Prefer one falsifiable small study over a generic instrumentation framework. Separate theory, feasibility, measured gain and novelty. Offline or simulated gains are not ANN throughput gains.
- D1 remains UNTESTED, D4 NOT TESTED, D6 INCONCLUSIVE on their historical subjects. H-V/H-G/H-C/H-F/H-QV are independent research lanes.
- Tests: `python -m unittest discover -s tests/research -v`; dataset-free checks must work without private artifacts. Linux integration is explicit opt-in.
