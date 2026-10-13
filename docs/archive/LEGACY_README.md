# Parallel ANN Research Baseline

For a concise Vietnamese guide covering WSL2 setup, building, and running PipeANN with the local SIFT1M dataset and index, see [HUONG_DAN_WSL2_VA_CHAY_BASELINE.md](../../HUONG_DAN_WSL2_VA_CHAY_BASELINE.md).

This repository is a clean research baseline for evaluating graph-based approximate nearest-neighbor (ANN) search on SSD. It contains PipeANN together with comparable search paths derived from DiskANN, Starling, and a coroutine-based implementation.

The repository contains source code and experiment utilities only. Datasets, generated indexes, build products, and local smoke-test artifacts are intentionally excluded from version control.

For the P0 local-artifact experiment runner, trace modes, optional local MLflow,
and SIFT1M validation, see [P0 experiments](../research/P0_EXPERIMENTS.md).

## Implemented search modes

The `search_disk_index` executable selects an implementation through the `search_mode` argument:

| Mode | Implementation | Main source file |
| ---: | --- | --- |
| `0` | DiskANN-style beam search | `src/v2/beam_search.cpp` |
| `1` | Starling-style page search | `src/v2/page_search.cpp` |
| `2` | PipeANN pipelined search | `src/v2/pipe_search.cpp` |
| `3` | Coroutine search | `src/v2/coro_search.cpp` |

Use identical datasets, indexes, thread counts, beam widths, and search-list sizes when comparing modes.

## Platform and dependencies

The actively used baseline targets x86-64 Linux. Ubuntu 22.04 or newer is recommended. An NVMe SSD is strongly recommended for meaningful disk-search measurements.

Install the build dependencies on Ubuntu:

```bash
sudo apt update
sudo apt install -y \
  build-essential \
  cmake \
  libaio-dev \
  libboost-all-dev \
  libgoogle-perftools-dev \
  libmkl-full-dev
```

The build enables CPU-specific optimizations through `-march=native`. A binary built on one machine may therefore not run on a machine with an older CPU instruction set.

## Build

Build the bundled `liburing` library first:

```bash
cd third_party/liburing
./configure
make library -j"$(nproc)"
cd ../..
```

Then configure and build the project:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j"$(nproc)"
```

The legacy helper is equivalent for a fresh checkout:

```bash
bash build.sh
```

`build.sh` expects the `build/` directory not to exist. Prefer the explicit CMake commands above for repeatable rebuilds.

Main executables are written to:

```text
build/tests/
build/tests/utils/
```

## Input formats

The supported vector element types are `float`, `int8`, and `uint8`.

The native vector format starts with two 32-bit integers followed by contiguous vector data:

```text
uint32 number_of_vectors
uint32 vector_dimension
element vectors[number_of_vectors][vector_dimension]
```

Utilities for converting `bvecs`, `fvecs`, `ivecs`, and TSV data are built in `build/tests/utils/`.

Example conversions:

```bash
build/tests/utils/bvecs_to_bin input.bvecs output.bin
build/tests/utils/fvecs_to_bin input.fvecs output.bin
build/tests/utils/ivecs_to_bin input.ivecs output.bin
```

Large datasets and generated indexes should be stored outside this repository. The `data/`, `indices/`, and `smoke_test/` paths are ignored by Git.

## Prepare an index

### Build an on-disk index

```bash
build/tests/build_disk_index \
  <data_type> \
  <data_file> \
  <index_prefix> \
  <R> <L> <B> <M> <threads> \
  <l2|cosine> \
  <single_file_index:0|1>
```

The main build parameters are:

- `R`: maximum graph out-degree.
- `L`: candidate-pool size used while building the graph.
- `B`: memory budget for PQ-compressed vectors, in GB.
- `M`: total build-memory budget, in GB.
- `threads`: number of build threads.

Example:

```bash
build/tests/build_disk_index \
  uint8 /data/base.bin /data/index/sample \
  96 128 3.3 256 32 l2 0
```

### Build PipeANN's in-memory entry index

Create a representative sample and its ID mapping:

```bash
build/tests/utils/gen_random_slice \
  uint8 /data/base.bin /data/index/sample_slice 0.01
```

Build the in-memory index:

```bash
build/tests/build_memory_index \
  uint8 \
  /data/index/sample_slice_data.bin \
  /data/index/sample_slice_ids.bin \
  /data/index/sample_mem.index \
  0 0 32 64 1.2 24 l2
```

Keep the in-memory index files next to the on-disk index and use a common prefix.

## Run a search

```bash
build/tests/search_disk_index \
  <data_type> \
  <index_prefix> \
  <threads> \
  <io_width> \
  <query_file> \
  <ground_truth_file> \
  <top_k> \
  <l2|cosine> \
  <search_mode> \
  <memory_L> \
  <search_L...>
```

Example using PipeANN (`search_mode=2`):

```bash
build/tests/search_disk_index \
  uint8 /data/index/sample \
  1 32 \
  /data/query.bin /data/truthset.bin \
  10 l2 2 10 \
  10 20 30 40
```

The executable reports throughput, average latency, tail latency, I/O statistics, and recall when a valid ground-truth file is available.

The existing `scripts/hello_world.sh` and figure scripts contain paths from the original evaluation environment. Update their dataset and index paths before using them on another machine.

## Reproducing experiments

Experiment entry points are located under `scripts/`:

- `scripts/tests/fig11.sh` through `fig18.sh`: individual experiment drivers.
- `scripts/run_all.sh`: runs the complete experiment sequence.
- `scripts/plotting.py` and `scripts/plotting.ipynb`: generate figures from experiment output.

These scripts are templates for the original experiment layout and reference absolute `/mnt/nvme...` paths. Review the paths, thread counts, and hardware assumptions before running them.

## Repository layout

```text
include/                  Public headers and vendored header-only dependencies
src/                      Core index construction and search implementation
src/v2/                   DiskANN, Starling, PipeANN, and coroutine search paths
tests/                    Command-line build and search programs
tests/utils/              Dataset, index, and evaluation utilities
scripts/                  Experiment and plotting scripts
third_party/liburing/     Vendored io_uring dependency
dependencies/windows/     Legacy Windows runtime dependencies
```

Generated directories such as `build/` and `smoke_test/` are local artifacts and can be deleted and recreated at any time.

## Cleaning generated files

Remove the project build and local smoke-test artifacts with:

```bash
rm -rf build smoke_test
```

Clean the bundled `liburing` build products with:

```bash
make -C third_party/liburing clean
```

Do not delete `third_party/liburing/` itself; its source and headers are required by this project.

## Datasets

Common evaluation datasets include:

- [BIGANN](http://corpus-texmex.irisa.fr/) for SIFT vectors.
- [deep1b_gt](https://github.com/matsui528/deep1b_gt) for DEEP vectors.
- [SPTAG SPACEV1B](https://github.com/microsoft/SPTAG/tree/main/datasets/SPACEV1B) for SPACEV vectors.

Dataset licensing and redistribution terms are controlled by their respective providers. No dataset is distributed in this repository.

## Origin and citation

This codebase is based on [DiskANN and FreshDiskANN](https://github.com/microsoft/DiskANN/tree/diskv2) and includes the PipeANN implementation associated with:

> Hao Guo and Youyou Lu. *Achieving Low-Latency Graph-Based Vector Search via Aligning Best-First Search Algorithm with SSD*. 19th USENIX Symposium on Operating Systems Design and Implementation (OSDI '25), 2025.

If you publish results obtained with this baseline, cite the original systems and clearly document any local changes, datasets, hardware, and parameters used in the comparison.

## License

See [LICENSE](LICENSE) and [NOTICE.txt](NOTICE.txt). Vendored dependencies retain their own licenses and documentation.
