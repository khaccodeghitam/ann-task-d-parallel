# P0 reproducible experiments

Issue [#1](https://github.com/Irthn1311/Parallel_ANN_Research/issues/1) adds an
external-process harness around the existing `search_disk_index` executable.
Local JSON/CSV/JSONL files and captured stdout/stderr are the source of truth.
Local MLflow mirrors run metadata and available metrics for visualization and
comparison. An MLflow error does not change the ANN run's success status.

The harness leaves this repository's ANN core unchanged. Issue #4 adds observational
causal tracing in the separate canonical `PipeANN-p0` subject; see
[P0_CAUSAL_TRACING.md](P0_CAUSAL_TRACING.md). D1/D2/D3/D4/D6 algorithmic solutions
are not implemented.
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

## Explicit benchmark contracts and provenance

Every new invocation requires `--benchmark-profile`; there is no inference from
`P99 Lat`, the executable filename, or an ambient Git checkout. The contracts
were checked directly against both `tests/search_disk_index.cpp` sources:

| Stable profile | Profile version | Positional tail after metric | Printed `P99 Lat` |
| --- | --- | --- | --- |
| `legacy-research` | `legacy-research/v1` | search_mode, mem_L, L | percentile 0.999 -> `p999_latency_us`; p99 is null |
| `pipeann-b9ec4ba` | `pipeann-b9ec4ba/v1` | nbr_type, search_mode, mem_L, L | percentile 0.99 -> `p99_latency_us`; p999 is null |

Both use parser version `search-table/v1`. Their common argv prefix is binary,
data_type, index_prefix, threads, beam_width, query, truth, K, metric.
The canonical contract is bound to upstream commit
`b9ec4ba86ff5d70bec277984777197f28dc2cf42`. It requires `--neighbor-type` and
rejects missing/unknown values. Source-supported values are pq, rabitq,
rabitq3, rabitq4, rabitq5 and dummy. PQ and RaBitQ inputs are validated with
respectively their PQ and RaBitQ companion filenames; dummy has no compressed
neighbor files. In the legacy profile neighbor type is only a build annotation
and is never passed positionally. Choosing a profile asserts that the binary
implements that source contract; the harness cannot prove binary/source linkage.
For nonzero mem_L the legacy contract requires graph/data/tag companions;
upstream uses a disk-format `_mem.index` with optional `.tags` (identity mapping
when absent). These formats must not be interchanged.

Manifest and summary schema v2 record profile, profile version, parser version,
and printed percentile. Summaries also name the available latency metric.
Unreported p50/p95 and the other tail percentile remain null. Historical v1
schemas are retained as `manifest.v1.schema.json` and `summary.v1.schema.json`.

Use `--subject-repo <Git worktree>` to declare the repository that produced the
ANN executable. It must exist and be a Git worktree; it overrides optional
Git discovery from the resolved executable directory. Failed discovery leaves
all subject provenance fields null. The harness and subject may be different
repositories and different commits:

- `harness_repo_root`, `harness_repo_remote`, `harness_git_commit`,
  `harness_git_branch`, `harness_git_dirty` describe the tooling checkout.
- `subject_repo_root`, `subject_repo_remote`, `subject_git_commit`,
  `subject_git_branch`, `subject_git_dirty` describe the declared/discovered
  algorithm checkout. Use **subject commit** for scientific comparisons.

Git HEAD and dirty state describe the worktree at invocation; they do not prove
when an existing binary was compiled. `executable_sha256` and available CMake
metadata/flags are retained independently, including both legacy `diskann.dir`
and upstream `pipeann.dir` flags. A dirty subject requires inspection of its
changes before research comparison. Deprecated `git_commit`, `git_branch`,
`git_dirty`, and `repo_remote` remain compatibility aliases for **harness only**.
Do not interpret those old fields as external algorithm provenance.

The derived run index adds profile/version/parser and both provenance namespaces.
Its known v1 header migrates under the lock by appending columns, preserving
all historical values. New historical cells stay empty; source manifests and
summaries are never rewritten or retroactively assigned subject provenance.
Rebuilding accepts finalized v1 and v2 runs. MLflow records profile/version/parser
and both commits separately as params and tags; missing provenance is marked
`unknown` in the mirror, while authoritative JSON uses null.

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
Without `--causal-trace`, the query/event scaffold remains as described above.
Opt-in causal tracing exports real per-query counters and sampled numeric events
using the same runner and external evidence root.

Schema definitions are under `schemas/research/`. Query fields can be extended
with versioned optional fields only when actual measurements become available.
Telemetry is long form: sample time, CPU/PID/device, metric, numeric value, unit.
Native local sysstat timestamps are retained; unknown units are empty.
The raw output is available to audit normalization. A short run may finish
before the first telemetry sample; zero rows are valid and recorded explicitly.

## Legacy research SIFT1M infrastructure smoke

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
  --benchmark-profile legacy-research \
  --subject-repo "$HOME/ann-research/Parallel_ANN_Research" \
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
only its final measured row supplies QPS and run metrics. These warmups are
legacy-specific; upstream b9ec4ba has them commented out. This smoke uses all
10,000 queries in the existing small query file, not the 100,000-query copies.

## Canonical upstream SIFT1M invocation

The four original successful runs in `P0_SMOKE_REPORT.md` are **legacy-research
infrastructure smoke validation**, not the canonical upstream P0 baseline.
Their artifacts remain unchanged. The existing canonical executable was found
in `~/ann-research/PipeANN/build/tests/search_disk_index`; historical width-sweep
logs verify neighbor type pq, search mode 2 and mem_L=0 against the existing
original SIFT1M index. This canonical build does not need the legacy auxiliary
entry index. `PipeANN` and `PipeANN-p0` are clean at b9ec4ba; `PipeANN-p0` currently
has no built search executable. Do not claim it produced the existing `PipeANN`
binary.

To use the already built executable, set both binary and subject to `PipeANN`.
For an official run whose executable is produced from the canonical `PipeANN-p0`
worktree, use the following after verifying that executable/build is available:

```bash
.venv-research/bin/python tools/research/run_ann_experiment.py \
  --benchmark-profile pipeann-b9ec4ba \
  --subject-repo "$HOME/ann-research/PipeANN-p0" \
  --executable "$HOME/ann-research/PipeANN-p0/build/tests/search_disk_index" \
  --dataset-id sift1m --dataset-path "$HOME/ann-research/data/sift1m" \
  --query "$HOME/ann-research/data/sift1m/query.fbin" \
  --ground-truth "$HOME/ann-research/data/sift1m/gt.bin" \
  --index-id sift1m-original-pq --index-prefix "$HOME/ann-research/indexes/sift1m/sift1m" \
  --neighbor-type pq --data-type float --search-mode 2 --threads 8 --wcap 32 \
  --k 10 --l-search 75 --mem-l 0 --distance-metric l2 \
  --trace-mode OFF --repetition 1 --mlflow --dry-run
```

Remove `--dry-run` only for the intended run. This example does not request a
rebuild or download. Compare results only with matched profiles, subject source,
binary/build flags, inputs and search parameters. The new canonical smoke uses
L75/mem_L0 rather than the old legacy L20/mem_L10, so their QPS is not directly
comparable. No overhead conclusion follows from either infrastructure smoke.

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

Compare authoritative local summaries with identical profiles, subject commits,
input hashes, executable/build
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
updates upsert by run ID. Failed/interrupted runs also get rows. A known v1
CSV header migrates additively; an unknown incompatible header is preserved and reported in the manifest. To rebuild
a compatible derived index from canonical finalized runs, use:

```bash
python3 tools/research/rebuild_run_index.py --evidence-root "$HOME/ann-research/research-v3"
```

This updates the existing compatible index without deleting unrelated rows.

## Current limitations and generated-file policy

- p50/p95 and per-query measurements are unavailable. The explicit profile
  determines whether p99 or p999 is available; no output-label autodetection.
- Dataset-directory hashing is omitted. Query/truth and index files up to
  64 MiB are hashed; **index files larger than 64 MiB have `sha256=null`** with
  exact paths and sizes. A cached/full large-input provenance strategy is an
  explicit follow-up requirement **before official SIFT10M**. This patch does
  not hash multi-GB files on each smoke repetition or begin that redesign.
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
