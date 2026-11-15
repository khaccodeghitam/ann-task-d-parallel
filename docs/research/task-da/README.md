# Task D × Task A — P0/P1 implementation, 2026-11-15

**P0 HOLD; P1 HOLD on real artifacts. Source audit and synthetic compatibility
checks are separate deliverables, not a passed research gate. No benchmark ran.**

The study asks whether A0/A3 graph topology changes intra-query parallel scaling
at matched Recall. Start with MS-Turing-1M; A1 isolates H17 from C/K changes.
The implementation is on a new branch from Task D `main`; historical engines,
frozen E1–E3 evidence and both repositories' `main` branches remain unchanged.

## Read in this order

1. [Source/evidence audit](SOURCE_AUDIT.md), [manifest](experiment_manifest.yaml).
2. [Pre-registration](PRE_REGISTRATION.md), [format contract](graph_format_contract.md).
3. [Compatibility report](GRAPH_COMPATIBILITY_REPORT.md), [engine semantics](engine_parity_audit.md).
4. [Validation](VALIDATION.md), [remaining work](NEXT_STEPS.md).

The `.yaml` manifest is JSON syntax (a YAML 1.2 subset), deliberately readable by
Python's standard library without a YAML dependency. Null means unavailable or
unverified, never zero. No graph files, vectors, GT, binaries or raw historical
logs are included in this change. Sheet excerpts are **A-OBS reported**.

## Reproduce dataset-free checks

From repository root, with CMake >=3.20, a C++17 compiler and Python >=3.11:

```sh
cmake -S research/task_da -B build-task-da -DCMAKE_BUILD_TYPE=Release
cmake --build build-task-da -j2
ctest --test-dir build-task-da --output-on-failure
python3 -m unittest discover -s tests/research -p test_task_da.py -v
```

CTest passes the native executable to Python; the standalone Python command
explicitly skips native tests unless `TASK_DA_SMOKE` names that executable.
The complete repository suite also needs `requirements-lite.txt`.
Do not compile the unrelated PipeANN root CMake project for these checks.

## Read-only artifact gate

Make a new local copy of the manifest and fill artifact paths; retain the pinned
reported hashes. Supply the external artifact root explicitly:

```sh
python3 -m research.task_da.preflight docs/research/task-da/experiment_manifest.yaml --artifact-root /path/to/artifacts
```

Exit 1 = HOLD; exit 2 = an artifact failed integrity/structure. This utility
checks availability and graph structure, and cannot certify host stability,
build provenance, vector/GT correctness or research gates. It deliberately
does not promote P0/P1 to PASS, even when files are available.

## Audit and optional lossless conversion

```sh
python3 -m research.task_da.graph_audit /path/to/graph.pipnn --format pipnn --entry 0 --expected-n 1000000
python3 -m research.task_da.graph_audit /path/to/graph.pipnn --format pipnn --entry 0 --expected-n 1000000 --convert-to nsg --output /new/path/graph.nsg --per-node-output /new/path/node-digests.jsonl
```

Conversion is optional: the native loader directly reads either format. Both
outputs use exclusive creation. Interrupted outputs are retained, not silently
reused. Do not infer semantic parity just from equal edge counts or sorted edges.
Per-node digests include node ID, degree and the original ordered adjacency.

## Correctness smoke after input verification

```sh
build-task-da/task_da_smoke pipnn /path/to/graph.pipnn /path/to/base.fbin /path/to/query.fbin 0 10 384 ON 32 > /new/path/smoke.jsonl
python3 -m research.task_da.evaluate_smoke /new/path/smoke.jsonl /path/to/groundtruth.ibin --base-count 1000000 --k 10
```

Use an unused result path; the shell redirection itself does not enforce
exclusive creation. The executable limits each call to 32 queries, emits no
latency/QPS, and supports only one worker. `384` is an example beam, **not** a
calibrated common-engine setting. Repeat ON/OFF and both representations and
check IDs/distances. Smoke Recall on 32 queries cannot establish 0.998 campaign
quality or a throughput gain.
