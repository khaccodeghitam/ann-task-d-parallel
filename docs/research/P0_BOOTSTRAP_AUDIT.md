# P0 bootstrap audit — 2026-10-08

Issue #1 and all three comments read before implementation.

- Remote: `https://github.com/Irthn1311/Parallel_ANN_Research.git`.
- Target branch: `research/p0-observability-mlflow`.
- Starting remote commit verified through the GitHub API:
  `de55ccb092d45564a2153a7091ef65d23b0692e4`.
- Local clone initially absent. First HTTPS clone failed because terminal Git
  authentication was unavailable. At the user's request, obtained an exact
  shallow checkout through the authenticated GitHub connector: all 636 blobs,
  all tree objects, and the original commit object matched their GitHub SHA-1s.
  Shared blobs were read from the upstream Git object database; 14 different
  blobs were downloaded from this repository, never substituted from upstream.
  Terminal `git fetch --all --prune` still failed without credentials. Connector
  reads verified remote refs; publication will use the connector if necessary.
  Implementation drafts prepared under `/tmp`; existing worktrees preserved.
- `PipeANN` and `PipeANN-p0`: both clean at
  `b9ec4ba86ff5d70bec277984777197f28dc2cf42` (separate upstream provenance).
- Native Ubuntu 24.04.5 LTS, x86-64, kernel `7.0.0-38-generic`.
- CPU: Intel Core i7-12700H; 20 logical CPUs, 14 physical cores;
  RAM: 16,542,261,248 bytes.
- Git already installed: 2.43.0. Python 3.12.3, pip 24.0,
  codex-cli 0.160.1. No bootstrap packages installed.
- `mpstat`, `pidstat`, `iostat`: present under `/usr/bin`.
- MLflow initially absent from PATH and system Python.
  Installed MLflow 3.17.0 and jsonschema 4.26.0 only in `.venv-research`.
- Dataset: `~/ann-research/data/sift1m/{base.fbin,query.fbin,gt.bin}`.
  Existing larger query copies are not needed for this task.
- Index prefix: `~/ann-research/indexes/sift1m/sift1m`, with existing
  `_disk.index`, `_disk.index.tags`, `_pq_compressed.bin`, `_pq_pivots.bin`.
- Existing executable: `~/ann-research/PipeANN/build/tests/search_disk_index`;
  upstream build uses `USE_URING`, `BG_IO_THREAD`, `USE_AVX2`, `USE_TCMALLOC`.
  It is not assumed equivalent to the research repository executable.
- Research executable source: `tests/search_disk_index.cpp`; one invocation
  accepts several L values, but the harness uses one L per experiment.
  A fresh native research binary built without source changes using CMake
  defaults (OVERLAP_INIT, MKL_ILP64, USE_AVX2, io_uring; no DYN_PIPE_WIDTH).
  Required Boost headers were absent; the single Ubuntu libboost1.83-dev
  package was downloaded/extracted into ignored `.deps-research` without root.
  CPLUS_INCLUDE_PATH points there; optimization/search flags remain unchanged.
  CMake warned it could not find MKLConfig.cmake, but installed MKL headers and
  libraries were found by the existing build and linkage succeeded.
  PipeANN OVERLAP_INIT rejected mem_L=0. No memory entry index was found locally;
  built only this missing auxiliary index in an external unique setup directory,
  reusing the original disk/PQ files via symlinks. See P0_SMOKE_REPORT.md.
- Source computes the printed `P99 Lat` column at percentile 0.999.
  Harness records it as p99.9 and leaves p99 null.
- Generated evidence: external `~/ann-research/research-v3`; existing contents
  preserved. Research tooling environment: ignored `.venv-research` in clone.

The previous sandbox failure was resolved through session permissions only.
No host security policy was changed. Existing dataset/disk-index rebuilding was
not required; only the absent memory entry index was created separately.
