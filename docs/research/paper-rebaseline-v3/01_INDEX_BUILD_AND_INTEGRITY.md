# Native construction and integrity

**VERIFIED SOURCE FACT:** Official source commit d18dcd16fece1c9d1dea356d783ebba2ed649e54, tree8e6ee6b0dc71db7dfa9db742c2f7066929202bc2 remains clean/detached in PipeANN-paper. Portable subject c4cd32c6816c063f56ecc64f9d7b63c909202cab/tree23fbb256528c67454cd4348bc58dfee700dffa06 remains clean. The sole +4/−1 AVX2 float reduction patch is retained in [v2](../paper-rebaseline-v2/gcc13-portability.patch); real-number equivalence does not imply bit-identical floating summation or identical near-tie ordering. There is no new ANN source commit.

Verified portable search SHA256 `5f5fa8d99cc83b523c71b7025e5f0b9aa61f45d42816804ed6d88755ebaa310b`; disk builder `f9f0124e737caa56aafe4441d3c42051c4f264a9412eff6e232f8baff1037e8a`. Existing build flags include OVERLAP_INIT,DYN_PIPE_WIDTH,USE_AVX2,OpenMP,Ofast/O3,march=native. Exact flags/ldd are local preparation records; no compiler or system package was installed. The old optimized and ASan/UBSan tests each passed10,000 float and6,000 exact uint8 cases, with acknowledged reassociation tolerance; full ANN sanitizer coverage is not claimed.

**VERIFIED SOURCE FACT:** [builder](<https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/tests/build_disk_index.cpp>) takes B as PQ RAM GiB; [aux_utils](<https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/src/aux_utils.cpp#L795>) computes chunks from budget/N. Both actual logs confirm32 chunks for B=0.298023223876953125. Parameters R64/L100/M8GiB are unchanged. The second build's thread count is4, not a claimed T8 construction.

| Owned construction | T8 | Separately frozen T4 |
|---|---:|---:|
| Start UTC | 2026-10-12T16:29:43.411866+00:00 | 2026-10-12T16:43:02.883676+00:00 |
| End UTC | 2026-10-12T16:34:41.345800+00:00 | 2026-10-12T17:15:57.243446+00:00 |
| Attempt wall seconds | 297.933598 | 1974.359424 |
| Exit |−15|−15|
| Sampled VmHWM KiB | 5629968 | 5641308 |
| Kernel direct-child peak KiB | 5627688 | 5639776 |
| Minimum sampled MemAvailable bytes | 8426651648 | 8359944192 |
| Maximum swap-used bytes | 1245184 | 1245184 |
| Maximum reported core/package temperature |100°C|100°C|
| Host snapshots |60|393|
| Snapshot-level policy changes |1|29|

Kernel child peak includes collectors; VmHWM is sampled. These are partial-attempt resources, not full-build peak or controlled build-speed comparisons. Total owned build wall time2272.293s. Initial free storage exceeded116GiB and available RAM13GiB; retained ≥20GiB disk and≥1GiB RAM guards never triggered. No sustained>64MiB swap-growth gate triggered. AC was online in every recorded snapshot. Firmware platform_profile was readable as performance at the recorded inspection, not continuously sampled. Kernel severe-log access was denied without privilege; absence of kernel warnings is not asserted.

The failed T8 prefix `/home/irthn/ann-research/indexes/sift10m-paper-v3/sift10m` and T4 prefix `/home/irthn/ann-research/indexes/sift10m-paper-v3-t4/sift10m` each contain PQ pivots136356bytes and PQ codes320000008bytes (header10M×32). Neither has `_disk.index`. **No complete INDEX_PACKAGE exists, and no partial output may be reused/repaired as a completed index.** All four exact hashes are [PARTIAL_OUTPUTS.json](PARTIAL_OUTPUTS.json). T4 completed pass0 but stopped during pass1; source stdout is authoritative for progress.

The retained entry-only package SHA256 `65241ce227d29672df2468f36a403cf99d1dbf7822819a9e62c747b7917bb0a1`, graph SHA256 `8081156e56476bcd163032d6ba00dd056a781ae21ff19ee9fb627a4ff522b466`, all100,004 unique tagged sample vectors/edges were previously structurally checked and their five files rehashed before/final-after v3. Sampling seed is not exposed; exact bytes are preserved. No fresh sample was drawn and no entry component copied to incomplete prefixes.

Canonical INPUT_PACKAGE `47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3` and modern INDEX_PACKAGE `8955f8bca0c8ebb5afbd2a69e9760fc829d22ba76a4ef7b482339e88b2489595` full pre/final-post audits PASS. No old permissions, graph, data or source files changed.
