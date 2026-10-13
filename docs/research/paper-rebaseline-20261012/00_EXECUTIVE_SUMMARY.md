# PipeANN paper rebaseline — kết quả và quyết định

**PAPER_REBASELINE_BLOCKED.** Official tag verified; exact source cloned and audited;
existing input/index full hashes pass. No new ANN search or index build was run. The
requested 66-run suite, artifact T16/T8 effect, and version comparison are **NOT_MEASURED**.

Campaign/evidence: `/home/irthn/ann-research/research-v3/campaigns/PAPER_REBASELINE_SIFT10M_20261012T144741235340Z`. Frozen prospective PLAN: `c79e74cb5e40fe59065c8de147ba582804f7557698b90f093d912f8d85ccf205`. Research branch
`research/pipeann-paper-rebaseline-20261012`, verified main/base `32939fc4b5a952a588e7708e756a1eba8d673f0f`.
The final publication commit is recorded in external `PUBLICATION.json`; no measurement harness commit is claimed.

| Deliverable | Verified outcome |
| --- | --- |
| Official source | 0.1.0 → `d18dcd16fece1c9d1dea356d783ebba2ed649e54`, clean detached tree `8e6ee6b0dc71db7dfa9db742c2f7066929202bc2` |
| User-space build | liburing archive built; CMake configured; search/library build exit2 |
| Build blocker | GCC13 AVX2 cannot compile `_mm256_reduce_add_ps` in `src/distance.cpp:623` |
| Independent semantic blocker | default `OVERLAP_INIT` exits for mem_L0 (`src/v2/pipe_search.cpp:178–185`) |
| Native index | NOT_BUILT; no builder binary; no fabricated hash or performance cost |
| Existing canonical package | Full SHA256 pre/post audit result in INTEGRITY.json; source/index untouched |
| Accepted / invalid / incomplete new ANN runs | 0 / 0 / 0; 66 planned, NOT_RUN |
| Diagnostic logging | DESIGN_ONLY; no new binary or trace |
| Automated research tests | 339 PASS (318 existing +21 new); synthetic, not real ANN benchmarks |

**VERIFIED SOURCE FACT:** paper and modern CLI, initialization, warmup, percentile,
PQ builder, pool/locking and metadata differ. The complete47-commit ledger is in
[evolution report](02_UPSTREAM_EVOLUTION_2025_2026.md). Broad reconstruction, changed
PQ training, candidate-pool batch/marker work, and the latest contention fix are
important mechanisms, not47 proven performance improvements.

**UNKNOWN:** v0.1.0 QPS/recall on this laptop; true load compatibility; native-index
quality; T16 scaling; per-query tails; observer cost. No old numeric results are
inserted into a new paper-results table. The old−8.5096% quiet-stock result belongs
to b9ec4ba and its own host/protocol, and remains unchanged.

Immediate next decision: resolve both blockers **before another campaign**. A
verified compiler/portability path is needed, and the owner must explicitly choose
an artifact-supported mem_L>0 plus native entry index, or a separately identified
no-OVERLAP configuration. Neither silently becomes default paper stock/mem_L0.
Then create a new executable-ready plan with resolved binary/index identities.
Source research and independent new-algorithm lanes can proceed from this audit;
no D1/D4/D6 algorithm or new research result was implemented.

English: The pinned OSDI artifact is preserved. Local build portability and a
source-proven configuration incompatibility prevent a valid stock rebaseline.
The source/history, integrity, passive analysis tooling and resumable handoff are complete;
the performance baseline is not.
