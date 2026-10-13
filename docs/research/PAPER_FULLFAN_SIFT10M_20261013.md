# Paper-native SIFT10M: one full-fan construction and stock validation

**Outcome: SIFT10M_BUILD = PASS; SIFT10M_PAPER_SEARCH = PASS.** SIFT1M fallback was not needed and was not run. Exactly one renewed SIFT10M construction and three search invocations ran:32-query quality smoke,10K-query quality validation and one10K-query portable-stock check. No retry, T16, sweep, E0, DETAIL or modern performance comparison was executed.

Run ID: `PAPER_FULLFAN_SIFT10M_20261013T081513543576Z`. Local authoritative evidence: [PAPER_FULLFAN_SIFT10M_20261013T081513543576Z](${ANN_RESEARCH_ROOT}/research-v3/campaigns/PAPER_FULLFAN_SIFT10M_20261013T081513543576Z/SUMMARY.json), [INTEGRITY.json](${ANN_RESEARCH_ROOT}/research-v3/campaigns/PAPER_FULLFAN_SIFT10M_20261013T081513543576Z/INTEGRITY.json), [runs.csv](${ANN_RESEARCH_ROOT}/research-v3/campaigns/PAPER_FULLFAN_SIFT10M_20261013T081513543576Z/runs.csv). Prior v1/v2/v3 reports, failed prefixes and frozen plans remain historical evidence and were not rewritten or resumed.

## Subject and operating condition

**VERIFIED SOURCE FACT:** Official0.1.0 is `d18dcd16fece1c9d1dea356d783ebba2ed649e54`, tree`8e6ee6b0dc71db7dfa9db742c2f7066929202bc2`. Actual executable subject is the existing GCC13-portable commit `c4cd32c6816c063f56ecc64f9d7b63c909202cab`, tree`23fbb256528c67454cd4348bc58dfee700dffa06`. Its sole upstream difference is the documented AVX2 horizontal-reduction +4/−1 patch. Floating reassociation is acknowledged; this is not a byte-exact unmodified upstream executable. No C++ source or binary was changed or rebuilt in this round. Existing optimized and ASan/UBSan distance evidence (10,000float+6,000uint8 cases each) remains applicable to this unchanged subject; it was not rerun.

- Builder SHA256: `f9f0124e737caa56aafe4441d3c42051c4f264a9412eff6e232f8baff1037e8a`.
- Portable stock search SHA256: `5f5fa8d99cc83b523c71b7025e5f0b9aa61f45d42816804ed6d88755ebaa310b`.
- Flags retain OVERLAP_INIT,DYN_PIPE_WIDTH,AVX2,OpenMP,O3/Ofast,march=native.
- Research HEAD at execution: `abc7915b12cd2a4716c73e3c99415b0111f04849`. The new wrapper was an isolated uncommitted file, bound by SHA256`232ed904b54359af17161c2f785b81c77097aad4d99f68325e08faf88cfefcbb` before construction and unchanged throughout all runs; do not claim that HEAD already contained it.

**DIRECT MEASUREMENT:** Native Ubuntu/kernel7.0.0-38-generic, Intel i7-12700H, approximately16GiB RAM and NVMe/ext4. Firmware `platform_profile=custom`; AC online in every recorded build/search snapshot. User-selected full-fan cooling is recorded from the task/start authorization; RPM is not independently established. No program changed fans, governor, power limits, affinity, scheduler or security controls. Observed MMIO PL1/PL2 stayed60/90W in samples, with no captured policy transition. These are policy limits, not consumed watts. They differ from preceding115/105W construction conditions, so lower temperatures cannot be attributed uniquely to fan speed.

## Construction and safety

New, initially absent prefix: `${ANN_RESEARCH_ROOT}/indexes/sift10m-paper-fullfan-20261013T081513543576Z/sift10m`. Canonical SIFT10M is10,000,000×128,uint8,L2; INPUT_PACKAGE SHA256`47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3`. Preflight checked manifest identity, component size/mtime/header against existing full-hash evidence, rehashed query/GT and all five retained entry files, and independently verified100,004 unique in-range entry IDs and exact sample-vector membership in the canonical base. A fresh full input audit passed before search; full post-search input/modern/native audits also passed.

Exact executed command:

```sh
${ANN_RESEARCH_ROOT}/PipeANN-paper-portable/build/tests/build_disk_index uint8 ${ANN_RESEARCH_ROOT}/data/bigann/sift10m/canonical/base_10m.bbin ${ANN_RESEARCH_ROOT}/indexes/sift10m-paper-fullfan-20261013T081513543576Z/sift10m 64 100 0.298023223876953125 8 8 l2 0
```

R64/Lbuild100/M8GiB/T8/split-index0. B=`0.298023223876953125` is **PQ RAM GiB**, not a chunk argument. Log and binary header both confirm **32 PQ chunks**. Environment: OMP_NUM_THREADS=8,MKL_NUM_THREADS=8,OMP_DYNAMIC=FALSE; OMP_PROC_BIND/OMP_PLACES/GOMP_CPU_AFFINITY unset.

[BUILD_PLAN.json](${ANN_RESEARCH_ROOT}/research-v3/campaigns/PAPER_FULLFAN_SIFT10M_20261013T081513543576Z/BUILD_PLAN.json) SHA256`494f211eebdfb39a9d9b1e2410597ff55c3fb050d2dfff63874c416bc39e0dbd` was frozen before this one attempt. One-second coretemp package sampling: terminate at99°C once or97°C for10seconds; stop on missing credible sensor, readable critical trip, AC loss/change, memory≤1GiB, disk≤20GiB, swap growth>64MiB for10seconds, foreign ANN or7200second duration cap. PL1 policy changes alone are logged rather than construction aborts. Monitor exceptions terminate the owned process group; independent six-second heartbeat watchdog covers monitor loss/stall, with SIGTERM then bounded SIGKILL escalation. Child parent-death protection covers launch-to-watchdog handoff. No unrelated process is terminated.

| Build measurement | Actual |
|---|---:|
| Wall time | 1526.117880s (25m26.118s) |
| Exit / guard failure |0 / none|
| Package maximum, sampled |69°C|
| Sampled time ≥97°C |0s|
| Package samples |1527|
| Sampled VmHWM |5,648,260KiB (~5.39GiB)|
| Minimum MemAvailable |7020597248bytes (~6.54GiB)|
| Minimum filesystem free |116467228672bytes (~108.47GiB)|
| Maximum swap used |303,104bytes; no sustained growth guard|
| Captured MMIO/policy changes |0|

The supplied entry graph was reused by **byte-for-byte independent copies**, with hash checks, after successful builder completion; no hardlinks, sample regeneration or changes to retained files. Entry package SHA256`65241ce227d29672df2468f36a403cf99d1dbf7822819a9e62c747b7917bb0a1`; memory graph100,004 nodes and2,909,175 loaded out-edges.

## Finished index integrity

Full native structural validation passed:10M node coordinates equal canonical base bytes;640M graph edges unique per row and in range; degree64; metadataN10M/D128/node record388bytes/10 nodes per4096byte sector. Disk size4,096,004,096bytes. PQ header10M×32, codes320,000,008bytes; pivots loaded with256×128 centroids. Untagged disk index uses source-defined implicit identity tags; no artificial disk `.tags` file was created. Missing optional `.del`/partition/tag files are documented native paths, not silently ignored read errors.

[INDEX_PACKAGE.json](${ANN_RESEARCH_ROOT}/indexes/sift10m-paper-fullfan-20261013T081513543576Z/INDEX_PACKAGE.json) SHA256: **`7140a47ac53b0480752059b5cb428b4d56dc627533974803b5ae4413827a7470`**. Six search components total4,441,377,744bytes. Builder warmup sample files are retained too (1,001,008 rows, not used by this driver). All eight output files total4,573,510,816bytes; [BUILD_OUTPUTS.json](${ANN_RESEARCH_ROOT}/indexes/sift10m-paper-fullfan-20261013T081513543576Z/BUILD_OUTPUTS.json) SHA256`7a5698318265b4b04968502c1038ae0446284f035a7e3db98f72a39d477db58f` records them. All eight hashes were rechecked after searches.

| Output component | Bytes | SHA256 |
|---|---:|---|
| `sift10m_disk.index` | 4096004096 | `f840be795911ac819a8bca9220be508d1e4256c6722def1e9deb48f9961bbde1` |
| `sift10m_mem.index` | 12036740 | `8081156e56476bcd163032d6ba00dd056a781ae21ff19ee9fb627a4ff522b466` |
| `sift10m_mem.index.data` | 12800520 | `ec2a2797ee84442855bb7096688c8ac7c3e9446e6840fbed7c649264b45de127` |
| `sift10m_mem.index.tags` | 400024 | `b46a63118d21dc5fd21b0d45a4a65bce4637784edbd8b8ad65fcf8d5b6bef9bb` |
| `sift10m_pq_compressed.bin` | 320000008 | `6bffe39d451647ee79aec95f4774bf0a53efa2e4f2eb64f5eb5fb1fa14dee735` |
| `sift10m_pq_pivots.bin` | 136356 | `668e35124f9871748c837f971b728298cdb7eb9a228460657593e41b2fe349c2` |
| `sift10m_sample_data.bin` | 128129032 | `7b4d315b13dc643445a22ace09e1e7da2676673fecd2926761b7d52a23082dc1` |
| `sift10m_sample_ids.bin` | 4004040 | `abb46b9a63873a08e354376534076c8e0be1e4a02611404a53997a2b958b6fe1` |

## Actual search correctness and stock result

[SEARCH_CHECK_PLAN.json](${ANN_RESEARCH_ROOT}/research-v3/campaigns/PAPER_FULLFAN_SIFT10M_20261013T081513543576Z/SEARCH_CHECK_PLAN.json) SHA256`e08d5e14bb8eb68ff577c70edca95db2844251ddbcb1163ab4ee1921a7b24019` was frozen before any ANN search. Order: quality32 →5s gap→ quality10K →5s gap→ stock10K. All three returned0 with no guard failure or ERROR/Failed/EBADF/CQE-read diagnostics. The fixed90% recall sanity floor is a gross correctness gate, not an OSDI quality target or competitive-performance proof; L was not tuned.

**DIRECT MEASUREMENT:** The separate existing same-library exporter validated all320 tiny-smoke and100,000 full-corpus result rows: complete K10 returns, unique/in-range IDs, finite distances and exact independently recomputed uint8 squared-L2. Tiny recall98.125%; full-corpus tie-aware recall **99.206%**, matching printed99.21%. This exporter adds a query-local return-count store and post-timer CSV export; its QPS is not stock evidence. Stock itself prints recall and does not export IDs; stock uniqueness is not misrepresented as directly exported evidence.

Actual portable-stock command:

```sh
${ANN_RESEARCH_ROOT}/PipeANN-paper-portable/build/tests/search_disk_index uint8 ${ANN_RESEARCH_ROOT}/indexes/sift10m-paper-fullfan-20261013T081513543576Z/sift10m 8 32 ${ANN_RESEARCH_ROOT}/data/bigann/sift10m/canonical/query.bbin ${ANN_RESEARCH_ROOT}/data/bigann/sift10m/canonical/gt_10m.bin 10 l2 2 10 100
```

| T/Wcap | K/L/mem_L | Timed queries | QPS | Mean latency,µs | P99.9,µs | Recall@10 | Mean application I/O/query |
|---|---|---:|---:|---:|---:|---:|---:|
|8/32|10/100/10|10,000|5,863.23|1,301.62|1,916.00|99.21%|107.02|

**VERIFIED SOURCE FACT:** [Artifact driver](https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/tests/search_disk_index.cpp) runs two complete L200 query warmups before the timed L100 pass. OVERLAP_INIT requires positive mem_L and the native memory entry; no mem_L0 fallback was patched in. QPS surrounds the parallel query loop/barrier, excluding index load/warmups/recall/export. Full stock process duration8.135724s; search window approximately1.705545s derived from rounded QPS, not a separately recorded exact timestamp. Printed “P99 Lat” uses0.999f, thus **P99.9**, whereas modern usesP99. P50/P95/P99 stock metrics are NOT_MEASURED. Printed hops0 is not a measured expansion count. Application I/O counters are not NVMe IOPS or hardware latency.

Stock maximum sampled package62°C; nine whole-process snapshots, no sampled policy/profile change. No phase-specific CPU/NVMe utilization conclusion is supported. Collector median/max wall cost was31.455/32.273ms, own snapshot CPU0.245s across the process; build snapshot median/max41.805/94.831ms and ownCPU40.284s. Wall collection time is not benchmark slowdown. No observer OFF/ON calibration exists; short search sampling is sparse. No continuous thermal guarantee, causal fan claim, scaling/CI or modern speedup claim follows from this single run.

## Tests, preservation and next action

**397 research Python tests PASS**, including seven new package99°C/sustained97°C/sensor loss/resource/AC/swap and watchdog positive/negative tests. Test-only disposable Python processes were used for watchdog verification. No real extra ANN experiment ran during tests. Existing original paper, portable, golden and PipeANN-p0 worktrees are clean and their commits unchanged. Canonical inputs, modern index, retained entry and all previous failed attempts remain untouched. No privileged action, D1/D4/D6 implementation, new optimization, SIFT100M or PR merge/update.

The only research-workspace additions are this report, `tools/research/run_paper_fullfan_check.py` and `tests/research/test_paper_fullfan_check.py`; prior research files remain unchanged. Preparation initially used the system interpreter without NumPy and failed before any ANN launch; it was corrected to the existing `.venv-research` interpreter. This did not consume or retry a builder attempt.

Next action: preserve this native package and use the exact mem_L10 command as the correctness substrate for algorithm research. If T8/T16 scaling or a modern comparison is later authorized, freeze a new balanced protocol under the recorded power/cooling condition; do not reuse the historical modern−8.51% as artifact evidence or mix native-index/mem_L/warmup differences into a claimed isolated speedup. This bounded task is complete; no fallback or additional benchmark is needed now.
