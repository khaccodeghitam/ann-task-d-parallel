# Upstream evolution:46 intervening commits +one later commit

**VERIFIED SOURCE FACT:** `git rev-list d18dcd16..b9ec4ba` contains46 commits;
ad9 adds one. Full diffs and exact dates/paths are saved in `source/commits/`,
`source/EVOLUTION_LEDGER.json`, pinned source snapshots and aggregate.diff.
Merge commits are included in the count; first-parent diffs were separately
inspected for merged changes, not counted as independent optimizations.
No newer README was used as the v0.1.0 configuration contract.

## Most consequential mechanisms

### Reconstruction and resource ownership

[82936410](https://github.com/thustorage/PipeANN/commit/82936410ed2fc8e0982009fb347a88e8681db9dc)
replaces PQFlashIndex/v2 search organization with SSDIndex/QueryBuffer/update
architecture. Mem_L0 fallback is added aftertag; newer dynamic write/read locks,
loc mappings and buffering are not automatically paper mechanisms. Artifact
setup allocates56 contexts regardless of requested T; modern gets per-thread
context during query search and uses buffer pooling. This potentially changes
memory/runtime service, but no live SQPOLL/thread count was measured here.
Arrays replacing id/loc hashes in21a61b93 affect metadata cost; update/delete fixes
must be separated from unfiltered static mode2. H-C should distinguish query
CPU service from update synchronization and startup contexts.

### Graph construction and compressed representation

[69584994](https://github.com/thustorage/PipeANN/commit/6958499400fd6cb985b11438c2db478c698a3115)
changes dimension partitioning/training (contiguous chunks, identity permutation,
kmeans++/Elkan, parallel chunk work), not merely a timer or compiler switch.
See `src/utils/partition_and_pq.cpp`, `src/neighbor/pq.cpp` and changed paths in
the saved commit.504662ab further changes PQ encoding/training scheduling and
adds multi-bit RaBitQ. c4a4eb30 adds1-bit RaBitQ/neighbor abstraction. With pq
selected, alternate RaBitQ kernels are inactive; PQ model/construction changes
are still relevant to quality/build/storage. Same32-byte size does not imply
same distance estimator, graph bytes or recall. Native-index comparison must
report that confounding, build effort and index size.

[PiPNN0ccf3881](https://github.com/thustorage/PipeANN/commit/0ccf38818b16289af5217699dd7cb4fb8464dc3b)
introduces partition-based graph indexing; chosen existing index is Vamana,
so PiPNN is not retroactively its builder.43528b71 introduces OOD/dense-neighbor/
filter-specific construction/plumbing. H-G motif/bridge ideas must examine these
representations before claiming equivalence or novelty, while no-filter SIFT10M
does not activate every branch.052ae7eb changes merge dedup bookkeeping, not
evidence that query frontier redundancy was solved.

### Frontier/candidate pool and prefetch

[a0b6ed04](https://github.com/thustorage/PipeANN/commit/a0b6ed041c0874fcc894382eb02fb5de0b035d51)
is titled Milvus but its `src/search/pipe_search_common.h` diff also adds send/
first-unvisited markers, reorders initialization bookkeeping and changes
termination/rerank/drain. It cannot be dismissed as serving code only.
[c3ef9f19](https://github.com/thustorage/PipeANN/commit/c3ef9f19670c9a06a268efa62fc99b79d0adec9b)
introduces a dedicated `include/candidate_pool.h`: sorted storage with separate
read/calc markers, batch survival rules, filtered bridge promotion and frontier
rewinding on insertion. These selectors mutate state; repeated observation
calls would change search. Old retset scan flags and new markers are not
interchangeable continuous-readiness observations.

[c13236d5](https://github.com/thustorage/PipeANN/commit/c13236d5beab2c8a6f77d6af585ce96fd384c6f7)
uses batched insertion/backward merge/pruning rather than repeated one-element
insertion/memmove, plus PQ-coordinate/visited-set prefetch and cheaper calc/
termination guards. Active plain search can benefit or change service mix;
quality/order behavior must still be tested, not assumed byte-identical.
9e7a193d prefetches approximate membership and pins selector resources, primarily
relevant to filter paths; no-filter callbacks are not the same cost.2ec84fe2
unifies codec prefetch APIs. H-V cache ideas and H-F bookkeeping ideas need
controls against this prior evolution. Prefetch is not additional graph knowledge,
and efficient sorting is not proof of useful parallel expansion or H-QV1 value.

### I/O, publication and locking

FIFO queue-front publication is visible in artifact and modern source, but
query drain/buffer/cache/update semantics differ. Mode2 uses SQPOLL;8a79f2db
repairs optional libaio support, while43528b71 adds optional SPDK with different
device/poller organization. Neither optional backend is the existing golden
USE_URING path. C13b593a EINTR/CQE/error checks and6d430ff5 coroutine/request
reset changes are correctness/runtime work, not quantitative optimizations.

Latest [ad9d7be9](https://github.com/thustorage/PipeANN/commit/ad9d7be9f836fa49f5a8b678af1e3398ccec846a),
[include/utils/lock_table.h](https://github.com/thustorage/PipeANN/blob/ad9d7be9f836fa49f5a8b678af1e3398ccec846a/include/utils/lock_table.h), replaces
sparse-entry pthread ownership with an ownerless atomic RWSpinLock. It pins
holders/waiters while outside the cuckoo-map bucket and waits there, so a waiter
does not block the bucket needed by unlock. Unlock may occur in background I/O
rather than the acquiring thread; lifetime/ownership matter. This removes a
source-level contention hazard, but retains spin waiting/no fairness guarantee.
No claim that it explains the old static T16 regression or improves QPS by a
specific amount is justified. b9ec4ba secondary binary does not include it.

### Scope not activated or performance not established

Deletion/tag-reuse/merge fixes, filtered selectors, range/IP search, OOD paths,
Python/RPC/Milvus clients, ARM fallback, MkDocs/plots/README and CI are substantial
project evolution but not all active in plain uint8/L2/PQ static mode2. Some
commits touch common source as well; actual paths, not titles, determine scope.
7840ce96 enlarges PQ scratch capacity;0512/6a040 free lock arrays; b9 widens cached
ifstream offsets/restores deletion. These are correctness/resource changes.
Author commit-message speedup statements are not measurements on this laptop.

## Complete source-reviewed timeline

The linked commit provides the full changed paths/diff; external JSON retains
first-parent path lists. Dates below are author dates; raw ledger also retains
committer dates. “Active” above refers to source path applicability, not proof
that a hardware feature or contention condition occurred in a benchmark.

| Date / commit | Group | Actual change and applicability |
| --- | --- | --- |
| 2025-06-19 / [82936410](https://github.com/thustorage/PipeANN/commit/82936410ed2fc8e0982009fb347a88e8681db9dc) | core/runtime | OdinANN update-capable reconstruction; new SSDIndex/QueryBuffer, per-call SQPOLL and mem_L0 fallback. Baseline source and initialization contract change. |
| 2025-06-19 / [4cdcd057](https://github.com/thustorage/PipeANN/commit/4cdcd057ca66628ecceb2567e44f6f550bb9c159) | build | Correct relocated liburing include/source linkage; build correctness. |
| 2025-06-21 / [7d31215c](https://github.com/thustorage/PipeANN/commit/7d31215c40085984d25e77774969a3c40898f6fd) | updates | Deletion race repair, per-worker state for update path; not a plain-query optimization claim. |
| 2025-06-24 / [c13b593a](https://github.com/thustorage/PipeANN/commit/c13b593a2b6c4fdc0ddff8bdae2577f4062fddb4) | correctness/runtime | retset capacity includes mem_L and grows; CQE/EINTR/error paths revised; deletion fixes. |
| 2025-06-25 / [ab06f3c8](https://github.com/thustorage/PipeANN/commit/ab06f3c81682bef6278c0cbd8724f47784684d3b) | plotting | Plotting output revision; no measured search speedup. |
| 2025-06-25 / [411bf2dd](https://github.com/thustorage/PipeANN/commit/411bf2ddfb50b5df59fb9682da8add9dfab24d30) | plotting | Plotting revision; no search-mechanism change attributed. |
| 2025-06-28 / [3166cdd8](https://github.com/thustorage/PipeANN/commit/3166cdd8aef478a5b9a7b3fc14445ba1b0b7e79d) | runtime/build | Old-kernel/AIO conditional paths and file-open compatibility; configuration dependent. |
| 2025-06-30 / [f4d9dc15](https://github.com/thustorage/PipeANN/commit/f4d9dc15a81b4f5c184698c26678c55990767b2e) | scripts | Plot/script cleanup, including result cleanup commands; inspected, never executed. |
| 2025-07-01 / [06ee17ac](https://github.com/thustorage/PipeANN/commit/06ee17acaabc3be3b5af83558a1440f35c2a3006) | docs | README update; not algorithm evidence. |
| 2025-07-15 / [8a79f2db](https://github.com/thustorage/PipeANN/commit/8a79f2db9c638fe3c3e58129c0fd7b7d39507085) | runtime | Libaio option implemented consistently through completion paths; not selected in golden USE_URING. |
| 2025-07-15 / [3d6d169c](https://github.com/thustorage/PipeANN/commit/3d6d169ca684a8441455b58d8f86cc65117f8dff) | docs/plots | Artifact-evaluation figures; no new local measurement. |
| 2025-07-16 / [7840ce96](https://github.com/thustorage/PipeANN/commit/7840ce96ac74a461b8efe2739b6aed5b14c15b9a) | correctness | PQ scratch grows from25600 floats to256×MAX_PQ_CHUNKS; capacity correction, not proven leak/performance result. |
| 2025-07-25 / [0a7ddf22](https://github.com/thustorage/PipeANN/commit/0a7ddf22063771f3a6bb77e6b77aedb7b693c51e) | docs | Post-AE README update. |
| 2025-07-30 / [f0eb56cb](https://github.com/thustorage/PipeANN/commit/f0eb56cbeda360da4fe6ccf1b71fed5a554b61c0) | docs | README update. |
| 2025-08-11 / [7de4151a](https://github.com/thustorage/PipeANN/commit/7de4151a480dfbfd2997b09c029080ad92417308) | docs | README update. |
| 2025-08-26 / [655b3841](https://github.com/thustorage/PipeANN/commit/655b3841cd740f5d34a0ddf6207b3452a587f96a) | GT utilities | Update-workload ground-truth timing/interval utility changes; not static GT bytes used here. |
| 2025-09-29 / [7ca3c077](https://github.com/thustorage/PipeANN/commit/7ca3c077a5be2c66437ad6c47aebdc1ce94bbb2c) | API/search | Python integration/reconstruction, neighbor abstraction and mapping changes; width init min(4,Wcap), buffers revised. |
| 2025-09-30 / [ecae81f3](https://github.com/thustorage/PipeANN/commit/ecae81f320c9dc30e8fd0e45d7d3156350bacb05) | updates/locks | Deletion correctness/PQ synchronization revisions; update paths must be separated from static search. |
| 2025-10-09 / [21a61b93](https://github.com/thustorage/PipeANN/commit/21a61b936990b1f97eff7bc2682f40dbda84d5ee) | metadata/memory | id2loc/loc2id arrays replace hash tables; alters mapping memory/access, not graph coordinates. |
| 2025-10-14 / [6d430ff5](https://github.com/thustorage/PipeANN/commit/6d430ff58895f3dcf2dd3217d319047293978c42) | coro/runtime | Coro stack/request reset and AIO correlation fixes; CoroSearch distinct from mode2. |
| 2025-10-14 / [c4a4eb30](https://github.com/thustorage/PipeANN/commit/c4a4eb304e4c5232aeafde82b9484bfc765b8606) | vector/CLI | 1-bit RaBitQ +neighbor codec CLI; alternative codec not enabled in PQ baseline. |
| 2025-10-30 / [f2031d91](https://github.com/thustorage/PipeANN/commit/f2031d91ef9dcfecc5c07ef9d4e01347259f8f11) | vector/buffers | Unified query-context size across neighbor codecs; changes resource abstraction. |
| 2025-11-12 / [69584994](https://github.com/thustorage/PipeANN/commit/6958499400fd6cb985b11438c2db478c698a3115) | PQ/build | Contiguous chunk grouping, identity permutation, parallel chunk training, kmeans++/Elkan; model/PQ bytes and graph-build costs can differ. |
| 2025-12-05 / [2ec0658c](https://github.com/thustorage/PipeANN/commit/2ec0658c1bf01f6ab4a26aaf1a5d8a6547fe9528) | filter/search/API | Filtered ANNS/IP and source reconstruction; plain common plumbing can change even when filter/IP unused. |
| 2025-12-12 / [504662ab](https://github.com/thustorage/PipeANN/commit/504662ab583b0eae079e82ea6c3f14db176aaca5) | PQ/vector | PQ training/encoding scheduling/layout revision; multi-bit RaBitQ optional. Commit title is not quantified speedup. |
| 2026-01-03 / [4566a20e](https://github.com/thustorage/PipeANN/commit/4566a20e9d99cd9a4b79cbfbcdeb67d0528e7582) | updates | Concurrent search/delete/merge filter correction. |
| 2026-01-04 / [45b44e6c](https://github.com/thustorage/PipeANN/commit/45b44e6c82c0f33f02cacc7f4f45c9f80f9982e1) | updates | Old deletion-set clearing/tag reuse. |
| 2026-01-04 / [e6acdec6](https://github.com/thustorage/PipeANN/commit/e6acdec6bee6f20e325d9b3e2385f7eb01c37484) | merge | Merge incorporates deletion fixes; not an additional independent mechanism. |
| 2026-01-29 / [0512c5ad](https://github.com/thustorage/PipeANN/commit/0512c5ad420fcf2ddd9e074a3c23bb263fd367bc) | locks | Destroy/free allocated pthread lock array; lifetime leak fix. |
| 2026-02-04 / [6a0403c9](https://github.com/thustorage/PipeANN/commit/6a0403c94c14e4eada5a7c0849dc8a10662fefef) | merge/locks | Merge of lock-table destructor fix; first-parent diff checked, not double-counted gain. |
| 2026-03-26 / [56528912](https://github.com/thustorage/PipeANN/commit/56528912cd56598082bf9af3160e5bb927f4ca5f) | portability/build | AVX512VPOPCNTDQ fallback and optional Python build; feature-dependent. |
| 2026-03-28 / [0ccf3881](https://github.com/thustorage/PipeANN/commit/0ccf38818b16289af5217699dd7cb4fb8464dc3b) | graph/build | PiPNN partition-based graph construction option; Vamana baseline does not select it. |
| 2026-05-18 / [43528b71](https://github.com/thustorage/PipeANN/commit/43528b71e04292cc34d44befcd61fa703217cdd8) | filter/graph/runtime | Speculative filtering, OOD/dense-neighbor/refinement, range paths, applications and optional SPDK; common pipeline also revised. |
| 2026-05-18 / [2fb8b83f](https://github.com/thustorage/PipeANN/commit/2fb8b83f7f6ff6a259e545d7935e4afff77ea219) | docs/CI | MkDocs/GitHub Pages deployment. |
| 2026-05-20 / [99a14f45](https://github.com/thustorage/PipeANN/commit/99a14f450e646c3415d64eef56768baceb305c7e) | docs | Filtered PipeANN bibliography; not a benchmark. |
| 2026-05-27 / [4ba39b1e](https://github.com/thustorage/PipeANN/commit/4ba39b1e790722785b89602e617b5dadd4795a39) | filter/updates | RangeSelector membership correction and entry-point insertion locking change; static no-filter paths mostly bypass specifics. |
| 2026-06-22 / [a0b6ed04](https://github.com/thustorage/PipeANN/commit/a0b6ed041c0874fcc894382eb02fb5de0b035d51) | server/search | Milvus gRPC plus core send/calc markers, termination/rerank/drain and optional node payload; plain path changes cannot be dismissed as server-only. |
| 2026-06-22 / [6c7d9dae](https://github.com/thustorage/PipeANN/commit/6c7d9dae21bc0590aa570c8d2998f34abf37f61c) | CI | libunwind CI dependency; no search gain attributed. |
| 2026-06-23 / [602d2c65](https://github.com/thustorage/PipeANN/commit/602d2c65206859d1ab23c9f731ec72c3060c05bc) | portability | ARM architecture compatibility; different platform, not our x86 mode. |
| 2026-06-24 / [bbdf6f09](https://github.com/thustorage/PipeANN/commit/bbdf6f09f0e45ce62d6aad5c897c195b84d10313) | server | Milvus flush-state RPC compatibility; no plain CLI activation. |
| 2026-06-25 / [052ae7eb](https://github.com/thustorage/PipeANN/commit/052ae7eb72bcee3b32a2fdd43af12117e8949214) | graph/merge | Per-neighborhood set replaces large bitmap clearing during merge; merge service, not per-query useful work. |
| 2026-07-06 / [c3ef9f19](https://github.com/thustorage/PipeANN/commit/c3ef9f19670c9a06a268efa62fc99b79d0adec9b) | candidate/search | Dedicated CandidatePool, shared ordered state/markers, filtered bridge retention, actual residual I/O drain. |
| 2026-07-10 / [9e7a193d](https://github.com/thustorage/PipeANN/commit/9e7a193dc3f38ad12063bfe50aa5885efb4e8d3b) | prefetch/filter | Approximate membership prefetch/pinning and related search hints; no-filter callback differs from filtered path. |
| 2026-07-17 / [c13236d5](https://github.com/thustorage/PipeANN/commit/c13236d5beab2c8a6f77d6af585ce96fd384c6f7) | candidate/prefetch | Batch insertion/pruning/backward merge, PQ/visited prefetch and empty-calc/frontier bookkeeping shortcuts. |
| 2026-07-19 / [2ec84fe2](https://github.com/thustorage/PipeANN/commit/2ec84fe20c37dc3cc236b66f7eba31c0cc80bf1e) | vector/prefetch | Codec prefetch interface across PQ/RaBitQ; common representation contract. |
| 2026-09-08 / [b9ec4ba8](https://github.com/thustorage/PipeANN/commit/b9ec4ba86ff5d70bec277984777197f28dc2cf42) | correctness | cached_ifstream offsets widen to size_t and cache buffer deletion restored; version frozen as secondary. |
| 2026-10-09 / [ad9d7be9](https://github.com/thustorage/PipeANN/commit/ad9d7be9f836fa49f5a8b678af1e3398ccec846a) | locking | Ownerless RWSpinLock, holder/waiter pinning and wait outside sparse-map bucket; no fairness guarantee or measured QPS delta. |

## Comparison attribution boundary

1. **VERIFIED SOURCE FACT:** functional/algorithm/build/layout differences listed
   here exist in exact pinned sources.
2. **DIRECT MEASUREMENT:** end-to-end common-workload version performance is
   NOT_MEASURED; this task has zero new ANN runs.
3. **HYPOTHESIS / UNKNOWN:** contributions of each mechanism to quality/QPS/tails
   require ablations or supported controlled comparisons. Source similarity,
   a commit title or a faster native-index system alone does not isolate causality.

The [official OSDI paper](https://www.usenix.org/system/files/osdi25-guo.pdf)
describes compute/I/O pipelining, dynamic width and entry-point initialization;
its server-scale evaluation is not this laptop workload. The artifact's own
README/scripts and exact source establish executable settings. No paper
performance figure is asserted reproduced, and no prior-art novelty claim is made.
