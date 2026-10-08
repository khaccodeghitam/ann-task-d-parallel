# P0 reproducible experiments

Issue [#1](https://github.com/Irthn1311/Parallel_ANN_Research/issues/1) adds an
external-process harness around the existing `search_disk_index` executable.
Local JSON/CSV/JSONL files and captured stdout/stderr are the source of truth.
Local MLflow mirrors run metadata and available metrics for visualization and
comparison. An MLflow error does not change the ANN run's success status.

No ANN core code is changed. D1/D2/D3/D4/D6 instrumentation is not implemented.
Search order, candidate pools, beam-width behavior, io_uring, completion handling,
frontiers, and termination remain those of the selected executable/build.
SIFT10M is outside this issue.

## Setup

Use Python 3.10+ on Linux. Local-only execution uses the standard library.
Install optional MLflow and schema-test dependencies in an isolated environment:

```bash
python3 -m venv .venv-research
.venv-research/bin/python -m pip install -r requirements-research.txt
.venv-research/bin/python -m unittest discover -s tests/research -v
```

Direct dependencies are pinned. Record `pip freeze` in local evidence when exact
transitive environment reproduction is needed. No system Python packages need
to be changed. `mpstat`, `pidstat`, and `iostat` are optional (`sysstat` on Ubuntu);
their absence and collector failures are recorded and do not block searching.
Collectors run without root.

Build the research repository itself as described in the root README, reusing
existing data/indexes. Do not assume the upstream `PipeANN` binary implements
this repository's baseline. For this validation, the only missing build
dependency was Boost headers. Without sudo, the minimal package was extracted
locally rather than changing ANN source:

```bash
mkdir -p .deps-research/downloads
(cd .deps-research/downloads && apt-get download libboost1.83-dev)
dpkg-deb -x .deps-research/downloads/libboost1.83-dev_*.deb .deps-research
(cd third_party/liburing && ./configure && make library -j4)
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
CPLUS_INCLUDE_PATH="$PWD/.deps-research/usr/include" \
  cmake --build build --target search_disk_index build_memory_index -j4
```

The existing CMake defaults are preserved: `OVERLAP_INIT`, AVX2 detected on this
host, native Release optimizations, and io_uring. `DYN_PIPE_WIDTH` is not enabled
by this CMake invocation. The legacy `build.sh` enables it, so it is a distinct
build configuration, not an equivalent command. Record build flags before
comparing results. The harness records binary hashes and available CMake build
metadata, including flags and their hashes.

## External evidence and modes

Default evidence root: `Path.home() / "ann-research/research-v3"`, expanded by
the runner. Override with `ANN_EVIDENCE_ROOT` or `--evidence-root`. Existing
contents are preserved. Run IDs include parameters, UTC microseconds, and a
UUID; run directories are created exclusively and never reused or overwritten.

```text
~/ann-research/research-v3/
  manifests/                   auxiliary input provenance/setup when needed
  runs/<run_id>/
    manifest.json              inputs, host, Git/build provenance, status
    command.sh                 exact argv, cwd, allowlisted thread environment
    stdout.log                 combined benchmark stdout/stderr
    summary.json               available run-level benchmark measurements
    SHA256SUMS                 all finalized evidence files in this run
    query_metrics.csv          LIGHT/DETAIL; currently header only
    system_metrics.csv         LIGHT/DETAIL; normalized numeric sysstat samples
    telemetry/*.log            LIGHT/DETAIL; original collector output
    trace_health.json          LIGHT/DETAIL; availability and row counts
    events.jsonl               DETAIL; harness lifecycle scaffold only
    mlflow.log                 MLflow-enabled runs; mirror diagnostics
    mlflow_result.json         MLflow worker result when available
  summaries/run_index.csv      derived convenience index, not canonical
  traces/
  scripts/
  notes/
  mlflow/mlflow.db
  mlflow/artifacts/
```

| Mode | Current behavior |
| --- | --- |
| OFF | Manifest, exact command, stdout, summary and checksums; no telemetry or ANN instrumentation. Optional MLflow logging occurs afterward. |
| LIGHT | OFF plus optional Linux telemetry and a query schema. Current executable exports no per-query rows. Intended for eventual headline runs after overhead checks. |
| DETAIL | LIGHT plus harness start/end events. Sampled ANN event infrastructure is scaffolded only; unsuitable for headline QPS. |

No `width_timeseries.csv` is produced because widths are not exported.
Schema definitions are under `schemas/research/`. Query fields can be extended
with versioned optional fields only when actual measurements become available.
Telemetry is long form: sample time, CPU/PID/device, metric, numeric value, unit.
Native local sysstat timestamps are retained; unknown units are empty.
The raw output is available to audit normalization. A short run may finish
before the first telemetry sample; zero rows are valid and recorded explicitly.

## SIFT1M dry run and smoke run

The discovered original files are under `~/ann-research/data/sift1m` and
`~/ann-research/indexes/sift1m`. This research build's PipeANN mode with
`OVERLAP_INIT` requires `mem_L > 0` and a memory entry index. The historical
disk index was valid, but this auxiliary memory index was absent.

For validation, a fresh directory under external `manifests/` contains symlinks
to the original four disk/PQ files and only the missing auxiliary index. Its
sample contains every 100th base vector (10,000 rows) and original vector IDs.
The existing repository's `build_memory_index` built it with `R=32, L=64,
alpha=1.2, threads=8, metric=l2`. The setup directory contains the sampling
script, exact build command, log, manifest, and hashes. The disk index was
neither rebuilt nor copied. Reuse this setup; never overwrite it.

Use the prefix recorded in `P0_SMOKE_REPORT.md`, or another validated compatible
prefix with `_mem.index`, `_mem.index.data`, and `_mem.index.tags` companions:

```bash
export ANN_INDEX_PREFIX="$HOME/ann-research/research-v3/manifests/<setup_id>/sift1m"
.venv-research/bin/python tools/research/run_ann_experiment.py \
  --executable build/tests/search_disk_index \
  --dataset-id sift1m --dataset-path "$HOME/ann-research/data/sift1m" \
  --query "$HOME/ann-research/data/sift1m/query.fbin" \
  --ground-truth "$HOME/ann-research/data/sift1m/gt.bin" \
  --index-id sift1m-existing-disk-entry10k --index-prefix "$ANN_INDEX_PREFIX" \
  --data-type float --search-mode 2 --threads 8 --wcap 32 \
  --k 10 --l-search 20 --mem-l 10 --distance-metric l2 \
  --trace-mode OFF --repetition 1 --no-mlflow --dry-run
```

Remove `--dry-run` to execute. Use `--mlflow` instead of `--no-mlflow` to mirror
the run. Change the trace mode explicitly to collect telemetry. Dry run resolves
and validates inputs and prints the command, prospective directory, mode,
MLflow state and collector availability. It creates no files/directories and
starts no benchmark, collector or MLflow process.

One L is supported per experiment to keep summaries unambiguous. The binary's
two built-in L=200 warmups remain unchanged and are included in wall time;
only its final measured row supplies QPS and run metrics. This smoke uses all
10,000 queries in the existing small query file, not the 100,000-query copies.

## Local MLflow UI

The runner uses an explicit local SQLite URI and local artifact location,
ignoring ambient cloud tracking/registry URIs. It creates one run under
`Parallel_ANN_P0`, mirrors parameters, tags and non-null metrics, and uploads
only small stable summary/command files. The local run directory is linked by
tag. Final manifest records mirror success/failure, error and MLflow run ID.

The post-benchmark worker has a separate timeout (`--mlflow-timeout`, default
60s). Missing packages, store errors, and timeouts preserve local evidence.
The run's benchmark status remains independent of its mirror status. Failed
mirrors may have an ID if MLflow created a partial run before logging failed.
Do not treat a partial MLflow run as the authoritative record.

```bash
EVIDENCE_ROOT="${ANN_EVIDENCE_ROOT:-$HOME/ann-research/research-v3}"
.venv-research/bin/mlflow ui \
  --backend-store-uri "sqlite:///$EVIDENCE_ROOT/mlflow/mlflow.db" \
  --default-artifact-root "$EVIDENCE_ROOT/mlflow/artifacts" \
  --host 127.0.0.1 --port 5000
```

Open `http://127.0.0.1:5000`, select `Parallel_ANN_P0`, then select runs to compare.
The SQLite/client approach follows the official
[local database guide](https://mlflow.org/docs/latest/ml/tracking/tutorials/local-database/)
and [MlflowClient API](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html).

## Inspect, compare and recover

```bash
RUN_DIR="$HOME/ann-research/research-v3/runs/<run_id>"
python3 -m json.tool "$RUN_DIR/manifest.json"
python3 -m json.tool "$RUN_DIR/summary.json"
cat "$RUN_DIR/command.sh" "$RUN_DIR/stdout.log"
(cd "$RUN_DIR" && sha256sum -c SHA256SUMS)
```

Compare canonical summaries with identical input hashes, executable/build
flags, search mode, threads, width, K/L/mem_L, and host settings. MLflow provides
convenient comparisons; `summaries/run_index.csv` provides CSV filtering.
Recall is a percentage, not a fraction. Do not infer an overhead result from
these smoke runs: proper controlled repetitions and equivalence checks remain
future work.

SIGINT/SIGTERM and benchmark timeouts stop the benchmark process group and
collectors before finalizing diagnostics. A nonzero exit or missing/ambiguous
benchmark result row produces a failed run. The benchmark's `main` discards
some inner return codes, so zero exit alone is not evidence of success.
Default benchmark timeout is 300s (`--timeout`). SIGKILL/power loss cannot be
caught: an unfinished manifest remains recognizable as `status=running`.

The index uses an exclusive `flock` and atomic file replacement. Repeated
updates upsert by run ID. Failed/interrupted runs also get rows. An incompatible
pre-existing CSV header is preserved and reported in the manifest. To rebuild
a compatible derived index from canonical finalized runs, use:

```bash
python3 tools/research/rebuild_run_index.py --evidence-root "$HOME/ann-research/research-v3"
```

This updates the existing compatible index without deleting unrelated rows.

## Current limitations and generated-file policy

- p50/p95/p99 and per-query measurements are unavailable and remain null or
  absent rows. Source uses 0.999 for its misleading `P99 Lat` header; the runner
  stores `p999_latency_us` and leaves `p99_latency_us` null.
- Neighbor type is not a runtime benchmark flag. It remains null unless the
  user supplies a known build annotation; it never changes search behavior.
- Dataset-directory hashing and full large disk-index hashing are omitted by
  default. Query/truth and small index files are hashed; large index files retain
  exact paths and sizes. Smoke validation additionally checks original hashes.
- The frozen shell command captures argv/cwd and an allowlist of threading
  variables; it does not dump secrets or the entire machine environment.
- Collector output formats depend on sysstat versions. Unknown/unparsed output
  remains in raw logs; zero usable samples are visible in trace health.
- Generated runs are never overwritten. Final checksums cover every run file
  except `SHA256SUMS` itself. Files are final after checksums; no guarantee of
  immutability against an external editor is claimed.

Git tracks only harness code, schemas, dependencies, tests, docs and small
textual reports. `.gitignore` extends existing rules for data/indexes, builds,
raw traces, MLflow stores, caches, virtualenvs and local headers. Keep bulky
evidence external. Before staging, inspect `git status --short`,
`git diff --stat`, and `git diff --cached --name-only`.
