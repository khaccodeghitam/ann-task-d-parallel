# P0 SIFT1M smoke report — 2026-10-08

Implemented Issue #1 on `research/p0-observability-mlflow` from
`de55ccb092d45564a2153a7091ef65d23b0692e4`.
Validation ran before publication, with the harness changes correctly recorded
as `git_dirty=true`. ANN source, headers, benchmark source, and CMake defaults
remained byte-identical to that starting commit. Final commit SHA is reported
in the final implementation response and PR.

## Exact validation command

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

## Observed measurements

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

Evidence root: `/home/irthn/ann-research/research-v3`. All four runs succeeded.

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
