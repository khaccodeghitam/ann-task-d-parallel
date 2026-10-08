# P0 SIFT1M infrastructure smoke report — 2026-10-08

Implemented Issue #1 on `research/p0-observability-mlflow` from
`de55ccb092d45564a2153a7091ef65d23b0692e4`.
Validation ran before publication, with the harness changes correctly recorded
as `git_dirty=true`. ANN source, headers, benchmark source, and CMake defaults
remained byte-identical to that starting commit. Final commit SHA is reported
in the final implementation response and PR.

The following four historical runs are **legacy-research infrastructure smoke
validation**, not the canonical upstream P0 baseline. Their original v1
artifacts and original commands are preserved. The profile label is a source
audit classification; no historical artifacts have been rewritten. New runs
require an explicit profile and separate subject/harness provenance.

## Original legacy validation command (before profile CLI)

From `~/ann-research/Parallel_ANN_Research`:

```bash
.venv-research/bin/python tools/research/run_ann_experiment.py \
  --executable build/tests/search_disk_index \
  --dataset-id sift1m --dataset-path ~/ann-research/data/sift1m \
  --query ~/ann-research/data/sift1m/query.fbin \
  --ground-truth ~/ann-research/data/sift1m/gt.bin \
  --index-id sift1m-existing-disk-entry10k \
  --index-prefix /home/irthn/ann-research/research-v3/manifests/P0_S1M_ENTRY_20261008T083427Z_45b2b5b8b763/sift1m \
  --data-type float --search-mode 2 --threads 8 --wcap 32 \
  --k 10 --l-search 20 --mem-l 10 --distance-metric l2 \
  --trace-mode OFF --repetition 2 --mlflow
```

The same resolved command was dry-run with `--dry-run`, OFF repetition 1 used
`--no-mlflow`, OFF repetition 3 used system `python3` and `--no-mlflow`
(MLflow is absent from that interpreter), and LIGHT repetition 4 used the
virtualenv interpreter with `--trace-mode LIGHT --no-mlflow`. No sweep was run.

Exact benchmark argv (identical across successful runs):

```bash
/home/irthn/ann-research/Parallel_ANN_Research/build/tests/search_disk_index float /home/irthn/ann-research/research-v3/manifests/P0_S1M_ENTRY_20261008T083427Z_45b2b5b8b763/sift1m 8 32 /home/irthn/ann-research/data/sift1m/query.fbin /home/irthn/ann-research/data/sift1m/gt.bin 10 l2 2 10 20
```

## Legacy infrastructure measurements

| Run | QPS | Recall (%) | Mean latency (us) | p99.9 (us) | Hops | I/Os | Wall (s) | Exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| off | 6837.33 | 91.14 | 1133.05 | 2240.00 | 26.86 | 59.44 | 11.170 | 0 |
| mlflow | 6827.37 | 91.19 | 1136.15 | 2236.00 | 26.85 | 59.47 | 11.240 | 0 |
| local-only | 6796.68 | 91.19 | 1140.06 | 2323.00 | 26.85 | 59.52 | 11.417 | 0 |
| light | 6812.78 | 91.18 | 1135.44 | 2263.00 | 26.86 | 59.47 | 11.276 | 0 |

p50/p95/p99 are null. The source computes 0.999 for its `P99 Lat` column;
it is correctly stored as p99.9. Wall time includes the unmodified built-in
L=200 warmups and startup. These are smoke checks, not research results.
No instrumentation-overhead or equivalence conclusion is justified.

## Run identities and artifacts

Evidence root: `/home/irthn/ann-research/research-v3`. All four legacy infrastructure runs succeeded.

- off: `P0_sift1m_T8_W32_OFF_R001_20261008T083531270564Z_b97c0c24851f404fa4fd50c9b994c7b5`
  Directory: `/home/irthn/ann-research/research-v3/runs/P0_sift1m_T8_W32_OFF_R001_20261008T083531270564Z_b97c0c24851f404fa4fd50c9b994c7b5`
- mlflow: `P0_sift1m_T8_W32_OFF_R002_20261008T083749161512Z_bc3b15a588904b638b55afcb4707d53f`
  Directory: `/home/irthn/ann-research/research-v3/runs/P0_sift1m_T8_W32_OFF_R002_20261008T083749161512Z_bc3b15a588904b638b55afcb4707d53f`
- local-only: `P0_sift1m_T8_W32_OFF_R003_20261008T083851792083Z_1bd423cae7814171bcde6700e880bbf7`
  Directory: `/home/irthn/ann-research/research-v3/runs/P0_sift1m_T8_W32_OFF_R003_20261008T083851792083Z_1bd423cae7814171bcde6700e880bbf7`
- light: `P0_sift1m_T8_W32_LIGHT_R004_20261008T084012366131Z_e29161e26f884319be380698f8ee94d8`
  Directory: `/home/irthn/ann-research/research-v3/runs/P0_sift1m_T8_W32_LIGHT_R004_20261008T084012366131Z_e29161e26f884319be380698f8ee94d8`

MLflow run ID: `44cb8291ca904179b625c669bde1c36d`.
Experiment: `Parallel_ANN_P0`. Local SQLite store and artifacts under external
`mlflow/`. Verified FINISHED status, parameters/tags, metric equality with local
summary, and command/summary artifacts. The documented UI command returned
HTTP 200 and served this run through the API. The temporary server was stopped.

```bash
EVIDENCE_ROOT="${ANN_EVIDENCE_ROOT:-$HOME/ann-research/research-v3}"
.venv-research/bin/mlflow ui \
  --backend-store-uri "sqlite:///$EVIDENCE_ROOT/mlflow/mlflow.db" \
  --default-artifact-root "$EVIDENCE_ROOT/mlflow/artifacts" \
  --host 127.0.0.1 --port 5000
```

OFF/local-only contents: manifest, command, stdout, summary, SHA256SUMS.
MLflow-enabled OFF also has mirror diagnostics/result. LIGHT also has empty
query schema, system CSV, raw collector logs and trace health. LIGHT collected
5,852 numeric rows: mpstat 2,310; pidstat 154; iostat 3,388. All collectors
were stopped/reaped. No per-query/width/causal measurements were invented.

## Tests and integrity

```bash
.venv-research/bin/python -m unittest discover -s tests/research -v
python3 tools/research/rebuild_run_index.py --evidence-root ~/ann-research/research-v3
git diff --check
git diff -- src include tests/search_disk_index.cpp CMakeLists.txt build.sh third_party
git status --short
```

22 tests cover IDs, manifest/summary/CSV schemas, conservative parsing, null
percentiles, dry-run side effects, local-only execution, MLflow failure/worker
timeout/cancellation, failed processes, SIGTERM cleanup, missing collectors,
DETAIL scaffold, input validation, checksums, exclusive run directories, and
concurrent/compatible/incompatible/rebuilt run indexes. No SIFT is needed.

Every successful run passed JSON schema validation and `sha256sum -c SHA256SUMS`.
Each has exactly one finalized index row. Original disk/PQ/index-tag/query/truth
file hashes, sizes and mtimes were identical before and after validation.
Both upstream worktrees remained clean. Git ignore checks cover datasets,
indexes, builds, traces, evidence, MLflow, virtualenv and extracted headers.

## Deviations and dependency findings

- Terminal clone/fetch/push credentials were unavailable. At the user's request,
  the authenticated GitHub connector supplied a SHA-verified shallow checkout
  (636 blobs, all trees, exact original commit). Publication uses a non-force
  connector ref update with an expected branch-head SHA; no reset/rewrite.
- Research PipeANN OVERLAP_INIT requires mem_L>0. The initial mem_L=0 attempt
  failed with exit 255; diagnostics remain in its unique external run directory.
  No compatible memory entry index existed. Only this missing auxiliary index
  was generated under `/home/irthn/ann-research/research-v3/manifests/P0_S1M_ENTRY_20261008T083427Z_45b2b5b8b763`.
  Its deterministic sample is every 100th original base vector (10,000 rows).
  Existing repository builder parameters: R32/L64/alpha1.2/T8/l2. The four
  existing disk/PQ files are symlinked there and were not copied/rebuilt.
  Setup includes sampling script, exact build command, log, source/input hashes,
  SHA256SUMS and Python environment freeze.
- No collectors are missing. MLflow was installed only in `.venv-research`
  (3.17.0; jsonschema 4.26.0). Missing Boost headers were downloaded as the
  single Ubuntu `libboost1.83-dev` package and extracted into ignored
  `.deps-research`, using CPLUS_INCLUDE_PATH solely to find required headers.
  No system packages or ANN optimization/search flags were changed.
- One additional LIGHT smoke validated real collectors; no parameter sweep.
- No ANN core semantic changes, no SIFT10M activity, no main modification,
  and no generated large artifacts committed. No D1/D4/D6 work started.

## PR #2 profile/provenance validation — 2026-10-08

Both blockers in the review comment were addressed entirely in research tooling,
schemas and documentation. Required stable profiles are `legacy-research`
(version `legacy-research/v1`) and `pipeann-b9ec4ba` (version
`pipeann-b9ec4ba/v1`), both parser `search-table/v1`. Canonical argv includes
required nbr_type; identical `P99 Lat` labels map to distinct source-audited
percentiles. All unknown measurements/provenance stay null.

Both canonical worktrees were inspected before edits and remain clean at
`b9ec4ba86ff5d70bec277984777197f28dc2cf42`. The existing binary lives in `PipeANN`,
not `PipeANN-p0`, so this smoke declares `PipeANN` as its actual subject.
Its captured `pipeann.dir/flags.make` defines BG_IO_THREAD/NDEBUG/USE_AVX2/
USE_TCMALLOC/USE_URING with native O3 compilation. No source, binary, input or
index rebuild was needed. The official `PipeANN-p0` invocation is documented
in `P0_EXPERIMENTS.md` for a binary actually produced from that worktree.

Exact legacy dry-run command, from the research repository (exit 0):

```bash
.venv-research/bin/python tools/research/run_ann_experiment.py --benchmark-profile legacy-research --subject-repo /home/irthn/ann-research/Parallel_ANN_Research --executable build/tests/search_disk_index --dataset-path /home/irthn/ann-research/data/sift1m --query /home/irthn/ann-research/data/sift1m/query.fbin --ground-truth /home/irthn/ann-research/data/sift1m/gt.bin --index-id sift1m-existing-disk-entry10k --index-prefix /home/irthn/ann-research/research-v3/manifests/P0_S1M_ENTRY_20261008T083427Z_45b2b5b8b763/sift1m --threads 8 --wcap 32 --k 10 --l-search 20 --mem-l 10 --trace-mode OFF --no-mlflow --dry-run
```

Exact canonical dry-run command, from the research repository (exit 0):

```bash
.venv-research/bin/python tools/research/run_ann_experiment.py --benchmark-profile pipeann-b9ec4ba --subject-repo /home/irthn/ann-research/PipeANN --executable /home/irthn/ann-research/PipeANN/build/tests/search_disk_index --dataset-path /home/irthn/ann-research/data/sift1m --query /home/irthn/ann-research/data/sift1m/query.fbin --ground-truth /home/irthn/ann-research/data/sift1m/gt.bin --index-id sift1m-original-pq --index-prefix /home/irthn/ann-research/indexes/sift1m/sift1m --neighbor-type pq --threads 8 --wcap 32 --k 10 --l-search 75 --mem-l 0 --trace-mode OFF --mlflow --dry-run
```

Both dry runs printed resolved binary, inputs, exact argv, profile versions,
separate provenance, OFF mode, MLflow state and all three collectors (available
but disabled in OFF). Neither prospective run directory was created.

Exactly one canonical SIFT1M smoke was then executed with the identical
canonical command **without `--dry-run`** (10,000 queries, T8/W32/K10/L75,
mem_L0, pq, l2, search mode 2, OFF, MLflow enabled). Benchmark argv:

```bash
/home/irthn/ann-research/PipeANN/build/tests/search_disk_index float /home/irthn/ann-research/indexes/sift1m/sift1m 8 32 /home/irthn/ann-research/data/sift1m/query.fbin /home/irthn/ann-research/data/sift1m/gt.bin 10 l2 pq 2 0 75
```

| QPS | Recall (%) | Mean latency (us) | p99 (us) | p999 | Hops | I/Os | Wall (s) | Exit |
| ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 3823.98 | 99.32 | 2080.17 | 2799.00 | null | 0.00 | 91.86 | 2.716 | 0 |

The zero mean hops is the value emitted by this executable; no missing counter
was inferred. p50/p95/p999 remain null. No direct QPS comparison with the old
legacy L20/mem_L10 smoke is valid; build/search configurations and warmup
behavior differ. This is canonical-contract infrastructure validation, not a
controlled official baseline or an instrumentation-overhead result.

Run ID: `P0_sift1m_T8_W32_OFF_R001_20261008T090958680296Z_1c566b913f494669ab5b81b76c714133`.

Artifact directory: `/home/irthn/ann-research/research-v3/runs/P0_sift1m_T8_W32_OFF_R001_20261008T090958680296Z_1c566b913f494669ab5b81b76c714133`.

MLflow run ID: `3578751ff0a8463e82e2beedcc2852b8`; verified FINISHED, profile/version/parser
params and tags, independent harness/subject commits, and metric equality with
local summary. Canonical p99 is mirrored; p999 is absent in MLflow. Local
manifest/summary pass v2 schemas and every run file passes SHA256SUMS.

Actual manifest provenance at invocation:

```json
{
  "harness_repo_root": "/home/irthn/ann-research/Parallel_ANN_Research",
  "harness_repo_remote": "https://github.com/Irthn1311/Parallel_ANN_Research.git",
  "harness_git_commit": "a31c79ff9a54949ea258728820edfa663a292908",
  "harness_git_branch": "research/p0-observability-mlflow",
  "harness_git_dirty": true,
  "subject_repo_root": "/home/irthn/ann-research/PipeANN",
  "subject_repo_remote": "https://github.com/thustorage/PipeANN.git",
  "subject_git_commit": "b9ec4ba86ff5d70bec277984777197f28dc2cf42",
  "subject_git_branch": "main",
  "subject_git_dirty": false,
  "executable_sha256": "a02ce69d1467727344c8620a254b4cba51d12616d3da171ef7c1a6668a9e8bc5"
}
```

Harness was a31c79f plus the working patch, correctly dirty. Subject was the clean
b9ec4ba worktree; its HEAD alone is not proof of compilation, so binary hash and
build metadata are recorded independently. The existing four successful legacy
smokes and the failed initial legacy run were preserved byte-for-byte (33 run
artifact files verified). The derived index migrated additively to include the
new row, leaving the historical profile/subject cells empty. Original canonical
binary/index/query/truth sizes and modification times were unchanged.

Validation: **38 research unit tests passed (original 22 plus 16 new tests)**:

```bash
.venv-research/bin/python -m unittest discover -s tests/research -v
git diff --check
git diff -- src include tests/search_disk_index.cpp CMakeLists.txt build.sh
```

New tests verify exact argv for both profiles, required/valid neighbor type,
profile-specific input companions and percentile nulls, v2 schemas, profile and
provenance MLflow mirroring, distinct temporary harness/subject Git repositories,
subject commit/dirty state, discovery/explicit precedence, invalid worktrees,
unknown provenance, v1 schema retention and additive index migration.

Index files larger than 64 MiB still have sha256=null. A cached/full large-input
hashing strategy remains a required follow-up **before official SIFT10M**;
this patch does not redesign hashing or repeatedly hash multi-GB inputs.
Terminal HTTPS Git authentication remains unavailable; publication uses the
already connected GitHub app for a non-force fast-forward with expected HEAD.
PR #2 stays unmerged. ANN core/search semantics, main and SIFT10M remain untouched;
no D1/D4/D6 work or generated artifact commits.
