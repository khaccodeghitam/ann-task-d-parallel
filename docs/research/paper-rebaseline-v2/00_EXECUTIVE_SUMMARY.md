# Portable paper continuation — PARTIAL

**PAPER_REBASELINE_PARTIAL / BLOCKED_INDEX_BUILD_ENV.** This continuation resolved the GCC13 compiler blocker, built the explicitly named **PipeANN-0.1.0-GCC13-PORTABLE** binaries, passed math/sanitizer checks and built a native entry graph. It did not establish an executable SIFT10M disk baseline: the disk build was stopped by a directly observed power-policy change. No ANN search/benchmark was invoked, so no QPS/recall/scaling result exists.

Evidence: `/home/irthn/ann-research/research-v3/campaigns/PAPER_PORTABLE_V2_SIFT10M_20261012T153819219817Z`. New prospective v2 PLAN `4efa44b6e1b1eff5ac803f3977ff7c47a4e3264bbf6c3da81cb21de3abd620b8` is execution_ready=false. It must not be executed or filled in after the fact. Original PR26 reports and blocked PLAN remain unchanged.

| Deliverable | Result |
|---|---|
| Official source | d18dcd16fece1c9d1dea356d783ebba2ed649e54 preserved clean/detached |
| Portable source | c4cd32c6816c063f56ecc64f9d7b63c909202cab, tree 23fbb256528c67454cd4348bc58dfee700dffa06 |
| Portability diff | one file; +4/-1, no search/graph/I/O changes |
| GCC13 build | search, disk builder, memory builder, sampler successful |
| Correctness | 10,000 float +6,000 uint8 cases in optimized and ASan/UBSan each |
| Python tests | 365 PASS; synthetic/source/math tests, not ANN performance |
| Native disk index | interrupted after 131.284s; incomplete PQ codes, no disk graph |
| Native entry index | 100,004 sampled vectors, build 2.935s; structurally validated |
| Benchmark accepted/invalid/incomplete | 0/0/0; all 66 intended cases NOT_STARTED |
| Full input/modern index audits | pre/post PASS |

**DIRECT MEASUREMENT:** MMIO PL1 changed 115,000,000→105,000,000 µW at 2026-10-12T15:44:08.394278Z, while AC remained online. The wrapper stopped its owned builder, exit−15. Two sysfs aliases report the same policy, not two independent power observations. Later a passive read returned115W. That does not retroactively satisfy the unchanged-policy contract.

**UNKNOWN:** why firmware/owner/OS changed the policy; actual watts; valid paper QPS or T16/T8 effect. No causal thermal or power explanation is claimed. Minimum next action is establishing a policy-stable operating condition without this agent changing settings, then a fresh build destination and executable-ready plan. Do not restart or overwrite the partial build automatically.

English: portability and entry construction are validated; the performance rebaseline is genuinely blocked by an observed environment gate, not the old compiler error. No new paper performance claim is made.
