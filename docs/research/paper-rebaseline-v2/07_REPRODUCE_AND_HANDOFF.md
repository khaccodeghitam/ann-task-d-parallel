# Reproduce and resume safely

Research continuation parent d06d3d9549d942c8c65786f7667cc8ee00ba47b9; verified main32939fc4b5a952a588e7708e756a1eba8d673f0f. New branch research/pipeann-paper-portable-v2-20261012. Final publication SHA is in separate external PUBLICATION.json. PR23/24/25/26 stay Draft/unmerged and unchanged. Raw evidence `/home/irthn/ann-research/research-v3/campaigns/PAPER_PORTABLE_V2_SIFT10M_20261012T153819219817Z`; small SUMMARY/PLAN and reports here; full logs/index files remain external.

Reproduce source in a **new absent destination**, never resetting existing trees:
```sh
git clone --no-hardlinks ~/ann-research/PipeANN-paper NEW_PORTABLE_CHECKOUT
cd NEW_PORTABLE_CHECKOUT
git checkout d18dcd16fece1c9d1dea356d783ebba2ed649e54
git apply --unidiff-zero /home/irthn/ann-research/Parallel_ANN_Research/docs/research/paper-rebaseline-v2/gcc13-portability.patch
git add src/distance.cpp
git write-tree # must equal 23fbb256528c67454cd4348bc58dfee700dffa06
cd third_party/liburing
./configure
make library -j4
cd ../..
CPLUS_INCLUDE_PATH=/usr/include/mkl:/home/irthn/ann-research/Parallel_ANN_Research/.deps-research/usr/include ADDITIONAL_DEFINITIONS=-DDYN_PIPE_WIDTH cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
CPLUS_INCLUDE_PATH=/usr/include/mkl:/home/irthn/ann-research/Parallel_ANN_Research/.deps-research/usr/include cmake --build build --target search_disk_index build_disk_index build_memory_index gen_random_slice -j4
```
Different absolute paths/toolchain/linker timestamps can change binary hashes even with the same source tree. Capture new provenance rather than pretend bit identity. Exact original compile/build logs are in external build/.

Tests:
```sh
cd /home/irthn/ann-research/Parallel_ANN_Research
.venv-research/bin/python -B -m unittest discover -s tests/research -v
g++ -std=c++17 -march=native -DUSE_AVX2 -fopenmp -Ofast -I../PipeANN-paper-portable/include tests/research/paper_distance_check.cpp ../PipeANN-paper-portable/src/distance.cpp -o NEW_OPT_TEST
./NEW_OPT_TEST
# Replace -Ofast with -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer for sanitizer test.
git diff --check
```

Do not execute current PLAN: no complete disk graph. Preserve partial `/home/irthn/ann-research/indexes/sift10m-paper`. After establishing unchanged AC/RAPL conditions, **a separate fresh build destination and new frozen plan** are needed. The paper-native disk builder mapping remains:
```sh
# Template ONLY; NEW_PREFIX must be in a new verified safe destination.
~/ann-research/PipeANN-paper-portable/build/tests/build_disk_index uint8 ~/ann-research/data/bigann/sift10m/canonical/base_10m.bbin NEW_PREFIX 64 100 0.298023223876953125 8 8 l2 0
```
Preserved entry sample/index can be independently reverified; they do not substitute for the disk graph. Exact sample seed is unavailable; use retained hashed sample IDs/bytes to reproduce input. Do not reclassify entry-only ENTRY_PACKAGE as disk INDEX_PACKAGE.

Unexecuted native search template after all index/quality gates:
```sh
env -u OMP_PROC_BIND -u OMP_PLACES -u GOMP_CPU_AFFINITY OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OMP_DYNAMIC=FALSE ~/ann-research/PipeANN-paper-portable/build/tests/search_disk_index uint8 NEW_PREFIX 8 32 ~/ann-research/data/bigann/sift10m/canonical/query.bbin ~/ann-research/data/bigann/sift10m/canonical/gt_10m.bin 10 l2 2 10 100
```
Use separate quality exporter for full K/ID/distance validation, never as stock headline. Exporter env PAPER_QUALITY_OUTPUT is only honored by that separate driver; portable stock ignores it. Modern CLI additionally passes pq before mode, with separately recorded memL/warmups/index. Full input+index audits, minimum recall, errors even exit0, phase semantics and all host gates are still mandatory.

No source/data/index permissions or host settings changed. No modern index rebuild, historical evidence write, ANN search, diagnostic observer, MLflow run, algorithm change, SIFT100M or claimed novelty occurred. This is a reproducible compiler/entry resolution with truthful remaining environment/index blockers, not completed paper-performance reproduction.
