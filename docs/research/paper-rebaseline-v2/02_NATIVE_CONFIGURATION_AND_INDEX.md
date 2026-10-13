# Native configuration and new index provenance

**VERIFIED SOURCE FACT:** tag CMake unconditionally enables OVERLAP_INIT; build.sh adds DYN_PIPE_WIDTH. [pipe_search.cpp:178](https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/src/v2/pipe_search.cpp#L178) requires positive mem_L. Native target is10 with a R32/L64/alpha1.2 entry graph, matching artifact README mechanism. No mem0 backport or NO_OVERLAP variant was built.

Paper disk builder B is PQ RAM GiB, not bytes/vector. B=0.298023223876953125 produces exactly32 chunks in retained stdout. Planned R64/L100/M8GiB/T8/single_file0. Native command is captured in BUILD_PLAN and failed attempt command.sh. Budget reserved5GiB final+20GiB temporary+1GiB evidence+20GiB retained space, with ≥9GiB available at admission. No storage or memory failure triggered.

**DIRECT MEASUREMENT:** build aborted on MMIO PL1 change after131.284s, exit−15, sampled VmHWM2,625,444KiB (lower bound; initial helper did not capture kernel high-water mark). Min sampled MemAvailable11,397,173,248 bytes; no swap; observed core temperatures≤85°C. Temperature measurements do not prove causality or thermal safety between samples. No disk graph/tags exist; no valid INDEX_PACKAGE was created. Partial hashes are retained for preservation, never usable as a finalized index:

| Partial component | Bytes | SHA256 | Status |
|---|---:|---|---|
| sift10m_pq_compressed.bin | 224000008 | `dd3d1c00c66d990d3ebc2d49a3ac3c450fc337a2783a4b8f0c651cbaf3006d51` | incomplete codes; expected 320000008 |
| sift10m_pq_pivots.bin | 136356 | `315e241272be627497ad32588a364a3d65e3827389de99a4b64bc29e2384d6f0` | pivots produced; no completed disk index |

Independent non-performance entry preparation proceeded without resuming the stopped disk build. Stock gen_random_slice0.01 uses random_device and does not expose seed; retained100,004 unique/in-range IDs and exact sample bytes provide reproducible inputs, not deterministic resampling. Every selected vector was checked against canonical base at its ID. Memory graph builder used T8 instead of README's server example T24 as a documented laptop resource setting.

Memory build command:
```sh
/home/irthn/ann-research/PipeANN-paper-portable/build/tests/build_memory_index uint8 /home/irthn/ann-research/indexes/sift10m-paper/entry_sample_0.01_data.bin /home/irthn/ann-research/indexes/sift10m-paper/entry_sample_0.01_ids.bin /home/irthn/ann-research/indexes/sift10m-paper/sift10m_mem.index 0 0 32 64 1.2 8 l2
```

Entry build2.93457s. Sampled VmHWM33,644KiB; kernel peak across direct child benchmark+collector processes54,356KiB, not a claimed separately measured benchmark-only peak. Graph header/byte length,100,004 adjacency rows, unique/in-range local edges, max degree32, entry local64971, exact data/tag equality to sample all validated. Search-time memory-index load NOT_MEASURED.

| Entry file | Bytes | SHA256 |
|---|---:|---|
| entry_sample_0.01_data.bin | 12800520 | `ec2a2797ee84442855bb7096688c8ac7c3e9446e6840fbed7c649264b45de127` |
| entry_sample_0.01_ids.bin | 400024 | `b46a63118d21dc5fd21b0d45a4a65bce4637784edbd8b8ad65fcf8d5b6bef9bb` |
| sift10m_mem.index | 12036740 | `8081156e56476bcd163032d6ba00dd056a781ae21ff19ee9fb627a4ff522b466` |
| sift10m_mem.index.data | 12800520 | `ec2a2797ee84442855bb7096688c8ac7c3e9446e6840fbed7c649264b45de127` |
| sift10m_mem.index.tags | 400024 | `b46a63118d21dc5fd21b0d45a4a65bce4637784edbd8b8ad65fcf8d5b6bef9bb` |

External ENTRY_PACKAGE SHA256 `65241ce227d29672df2468f36a403cf99d1dbf7822819a9e62c747b7917bb0a1` is a **separate entry-only manifest**, not the required disk INDEX_PACKAGE. Original input and modern index full pre/post SHA audits pass. No shared-index loading claim; modern mem10 entry was not built. Source-based format audit remains [PR26 report03](../paper-rebaseline-20261012/03_INDEX_AND_INPUT_COMPATIBILITY.md).
