# Exact source, build and version audit

## Identity and reading provenance

**VERIFIED SOURCE FACT:** [release0.1.0](https://github.com/thustorage/PipeANN/releases/tag/0.1.0)
is the authors' OSDI'25 artifact, released2025-06-19. Local `git describe --tags --exact-match`
returns0.1.0; HEAD `d18dcd16fece1c9d1dea356d783ebba2ed649e54`; tree `8e6ee6b0dc71db7dfa9db742c2f7066929202bc2`.
`/home/irthn/ann-research/PipeANN-paper` is clean/detached. No source patch, submodule
substitution or checkout of latest main was made. Generated build files are ignored.
Golden b9ec4ba and old instrumented34a485ba remain at their original commits, trees
and binary hashes; `source/*_identity.json` records actual initial state.

Remote upstream HEAD observed `ad9d7be9f836fa49f5a8b678af1e3398ccec846a`, dated2026-10-09:46 commits d18→b9 and one
further commit. Main research verified `32939fc4b5a952a588e7708e756a1eba8d673f0f` using the connected GitHub read API;
terminal private-repo fetch fails for absent HTTPS credentials. That failure is
not treated as a successful fetch. New branch is based on the verified local object.

[Charter PR25](https://github.com/Irthn1311/Parallel_ANN_Research/pull/25), HEAD
`638e58d9983b981e347f26428f1f95bc47eb3d91`, is **Draft/open/unmerged**. Its actual
RESEARCH_PHILOSOPHY.md and AGENTS.md were read before substantive work, without
pretending they are on main. Their preserved contents are in `source/charter/`.
PR23/24 are also Draft/open/unmerged; their full bodies and identities are saved.
Merged setup/E0c/G0C2/D1-O1 documents, PR23 D1-O2a validation and quiet-stock local
analysis were read as historical context. No campaign was rerun or relabeled.

## Host and actual build

**DIRECT MEASUREMENT:** Ubuntu24.04.5, Linux7.0.0-38-generic, i7-12700H,20 logical/
14 physical cores,16,542,265,344 bytes RAM; GCC13.3.0/CMake3.28/Python3.12. Existing
MKL headers/libs, libaio, tcmalloc and isolated Boost headers were available.
No system dependency install or elevated command occurred. Alternative compilers
icpx/icpc/clang++/g++11/g++12 were not found on PATH; no promise that installing one
would resolve all build issues is made.

Exact build sequence used existing dependencies (stock source unchanged):

```sh
cd /home/irthn/ann-research/PipeANN-paper/third_party/liburing
./configure
make library -j4
cd /home/irthn/ann-research/PipeANN-paper
export CPLUS_INCLUDE_PATH=/usr/include/mkl:/home/irthn/ann-research/Parallel_ANN_Research/.deps-research/usr/include
export ADDITIONAL_DEFINITIONS=-DDYN_PIPE_WIDTH
cmake -S . -B build
cmake --build build --target search_disk_index build_disk_index -j4
```

CMake exit0; build exit2. Initial failure was reproduced once with exact argv,
UTC boundaries and stdout/stderr in `build/build_failure_reproduction.*`.
The reproduced attempt took7.17657s; initial attempt was observed in tool output
but lacks a full saved timing log. No build peak RSS or total duration is invented.
`source/build_identities.json` hashes liburing, source and captured flags;
flags SHA256 `0feb63f2e803a8a8e74a9566c652c5de07449707ae7324f0300ba31a3c4555e0`. Search/builder binary SHA256s are **null**, not placeholders.

**VERIFIED SOURCE FACT:** [CMake](https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/CMakeLists.txt#L47-L85) detects this
host as AVX2 and enables OVERLAP_INIT; [build.sh](https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/build.sh) adds DYN_PIPE_WIDTH.
Actual flags include O3/Ofast/march=native/OpenMP/NDEBUG/MKL_ILP64/USE_AVX2.
The float distance implementation uses an undeclared AVX2 reduction intrinsic
([distance.cpp:623](https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/src/distance.cpp#L623)); all instantiations compile
even though the requested dataset is uint8. No -U flags, forged CPU detection or
modern distance code were introduced to bypass this.

## Scientific configuration audit

**VERIFIED SOURCE FACT:** [pipe_search.cpp:178–190](https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/src/v2/pipe_search.cpp#L178-L190)
rejects mem_L0 in the default overlapping initialization path. The CLI help saying
“0 means not using mem index” does not override this compiled branch. A later
commit82936410 adds a fallback; it is outside the official artifact. The default
paper scripts use mem_L10 and an entry index. Thus the specified mem_L0 default
artifact experiment is blocked independently of compiler choice.

The AVX2 non-temporal PQ path **does** call the ordinary population fallback
([pq_table.h:157–182](https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/include/pq_table.h#L157-L182)); its TODO is not
evidence of an uninitialized table. The failing intrinsic is a separate issue.

| Contract | Paper | Modern b9ec4ba | Consequence |
| --- | --- | --- | --- |
| Search CLI | no positional nbr_type | positional pq before mode | explicit profile required |
| Printed P99 label | percentile0.999 | percentile0.99 | p999 vs p99; cannot merge tails |
| Warmup | two full10K L200 loops | driver warmups commented | process/window phase differs |
| Context setup | fixed56 setup iterations | requested buffer/ring lifecycle | audit runtime; no guessed SQPOLL count |
| mem_L0 | default path rejects | fallback supported | no apples-to-apples default mem0 stock |
| PQ builder argument | RAM budget converted to chunks | direct PQ bytes | B32 is not PQ32 for paper |
| Pool | sorted Neighbor array, read/calc scans | dedicated CandidatePool/batch markers | algorithm/plumbing differs |

Actual binary invocation/help, index loading and numeric correctness remain
NOT_RUN_NO_BINARY. Source-based argv is available; an executable usage test was not
substituted with a fabricated binary output. Readiness means all build/config/
index/quality gates passed, not merely successful CMake configuration.
