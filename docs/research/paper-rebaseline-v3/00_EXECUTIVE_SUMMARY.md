# V3 outcome: PAPER_REBASELINE_BLOCKED

**DIRECT MEASUREMENT:** Neither native disk-index construction finished safely. The original T8 attempt reached reported Package100°C/Core12 98°C after297.934s. A separately frozen, resource-only T4 construction reached reported Package100°C/Core20 100°C after1974.359s. Both owned processes were terminated (exit−15) by the unchanged critical-proximity guard. No third attempt or ANN search was launched.

**VERIFIED IMPLEMENTATION FACT:** V3 correctly separates construction safety from benchmark comparability. MMIO PL1-only changes are logged and do not kill construction. T4 continued through29 snapshot-level policy changes; the actual stop was thermal. Power policy is neither measured watts nor proof of graph corruption.

| Deliverable | Actual result |
|---|---|
| Official source | 0.1.0 tag → d18dcd16fece1c9d1dea356d783ebba2ed649e54; pristine original |
| Portable executable | Existing c4cd32c6816c063f56ecc64f9d7b63c909202cab verified; no C++ change/rebuild |
| Native memory entry | Existing100,004-node graph and all five retained files fully hash-verified; not copied because disk construction failed |
| Complete native disk index | **NONE**; both prefixes are failed partial evidence |
| Stock benchmark suite | **0 accepted / 0 invalid / 0 incomplete searches;66 NOT_RUN** |
| Tests |390 Python tests PASS, including25 v3 synthetic tests; retained optimized/sanitizer distance tests apply to unchanged subject |
| Input/modern integrity | Full-content pre/final-post audits PASS |

**UNKNOWN:** Paper T16/T8 QPS behavior, recall, latency, normalized tails and modern/paper performance. The historical modern−8.51% is not artifact evidence. No performance conclusion, paper throughput reproduction or novelty claim is made.

Evidence: `/home/irthn/ann-research/research-v3/campaigns/PAPER_NATIVE_V3_SIFT10M_20261012T162845717948Z`. Versioned wrapper code snapshot commit `6a420b88341fe630df415ee752095fabfb12214e`. Blocked ledger PLAN SHA256 `2436c7c579fe3af3feecac5ade0b87bf1fae910e85f8cf3758b3c388c6c20a08`; execution_ready=false. The pre-construction plans and pre-search design have their own immutable digests in [03](03_BENCHMARK_PROTOCOL.md). [SUMMARY.json](SUMMARY.json) and [INTEGRITY.json](INTEGRITY.json) distinguish builds from searches.

Immediate next requirement: a construction environment that can finish without triggering the existing thermal guard. Further unattended attempts on this unchanged setup are not justified by the two observed stops. Use a suitable build host or address physical cooling first; retain the same source/input/parameters and produce a new index identity. No privileged power change or guard bypass is recommended.
