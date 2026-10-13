# Reproduction and session handoff

## Paths and immutable identities

Evidence `/home/irthn/ann-research/research-v3/campaigns/PAPER_REBASELINE_SIFT10M_20261012T144741235340Z`; research `/home/irthn/ann-research/Parallel_ANN_Research`; new branch
`research/pipeann-paper-rebaseline-20261012`, base `32939fc4b5a952a588e7708e756a1eba8d673f0f`.
Paper `/home/irthn/ann-research/PipeANN-paper` clean detached `d18dcd16fece1c9d1dea356d783ebba2ed649e54` /tree8e6ee6b0dc71db7dfa9db742c2f7066929202bc2.
Golden `/home/irthn/ann-research/PipeANN` commit `b9ec4ba86ff5d70bec277984777197f28dc2cf42`, search SHA256 `a02ce69d1467727344c8620a254b4cba51d12616d3da171ef7c1a6668a9e8bc5`.
Old instrumented `/home/irthn/ann-research/PipeANN-p0` remains34a485bafae48b4a53e6da4eb7996e0c22c08140.
Latest upstream audit `ad9d7be9f836fa49f5a8b678af1e3398ccec846a` is not selected as any benchmark subject.
PLAN `c79e74cb5e40fe59065c8de147ba582804f7557698b90f093d912f8d85ccf205` is a blocked, immutable design; no existing plan was altered.

Input `/home/irthn/ann-research/data/bigann/sift10m/manifests/INPUT_PACKAGE.json` digest `47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3`;
modern index `/home/irthn/ann-research/indexes/sift10m/INDEX_PACKAGE.json` digest `8955f8bca0c8ebb5afbd2a69e9760fc829d22ba76a4ef7b482339e88b2489595`. Existing components must remain intact.
No paper binary/native index digest exists. Proposed `indexes/sift10m-paper/sift10m`
is not a discovered or validated index. No real ANN run ID/MLflow ID exists here.

## Actual commands and repeatable checks

Read-only identity:
```sh
git -C ~/ann-research/PipeANN-paper rev-parse HEAD HEAD^{tree}
git -C ~/ann-research/PipeANN-paper describe --tags --exact-match
git -C ~/ann-research/PipeANN-paper status --short
sha256sum ~/ann-research/PipeANN/build/tests/search_disk_index
cd ~/ann-research/Parallel_ANN_Research
.venv-research/bin/python tools/research/package_manifest.py verify \
  ~/ann-research/data/bigann/sift10m/manifests/INPUT_PACKAGE.json --full-components
.venv-research/bin/python tools/research/package_manifest.py verify \
  ~/ann-research/indexes/sift10m/INDEX_PACKAGE.json --full-components
.venv-research/bin/python -B -m unittest discover -s tests/research -v
git diff --check
```

Build recipe and exact captured flags are in report01 /build/*.json. Repeating
the same GCC13 command reproduces the failure; it does not complete the baseline.
The default artifact source has not been patched. No sudo/package install is
required for audit or analysis; resolving compiler support must not silently
disable AVX2/OVERLAP_INIT or alter distance arithmetic.

**Unexecuted command template — invalid for default artifact mem_L0:**
```sh
env -u OMP_PROC_BIND -u OMP_PLACES -u GOMP_CPU_AFFINITY \
  OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OMP_DYNAMIC=FALSE \
  ~/ann-research/PipeANN-paper/build/tests/search_disk_index uint8 \
  ~/ann-research/indexes/sift10m-paper/sift10m 8 32 \
  ~/ann-research/data/bigann/sift10m/canonical/query.bbin \
  ~/ann-research/data/bigann/sift10m/canonical/gt_10m.bin 10 l2 2 0 100
```
Modern layout inserts `pq` immediately before mode2. Every prospective cell's
argv is frozen in PLAN; none was launched. Do not use the historical legacy-
research profile to infer paper mem0 readiness merely because positional layouts match.

Passive tooling:
```sh
.venv-research/bin/python tools/research/paper_rebaseline.py --show-order
```
This prints66 intended cases, runs no ANN and allocates no run directory. The
complete-ledger validation CLI accepts --plan/--plan-sha256/--records/--audits;
it intentionally rejects this execution_ready=false plan. It validates asserted
ledger checks, not independently every file byte: actual checksums, IDs, GT and
monitoring must be verified by an execution implementation before ledger creation.
No new general runner/profiler replaces the existing experiment infrastructure.

## Exact resumable blockers and next decisions

1. Establish a scientifically valid unprivileged portability/compiler solution
   for the AVX2 reduction. Existing CMake sets g++ internally; simply setting
   CXX may not select another compiler. Prove flags, arithmetic and binary identity;
   any shim/source patch belongs to a separately named reproducible variant.
2. Explicitly resolve the requested mem_L0/default-OVERLAP contradiction. The
   faithful artifact path uses positive mem_L with a new native entry graph.
   Disabling OVERLAP is a distinct build/configuration; adopting posttag fallback
   is a distinct source version. Neither is silently paper-default mem0.
3. Only after1–2, map artifact B budget correctly, refresh safe RAM/disk conditions,
   choose/verify new native index and capture builder resources/hashes. A shared
   modern index remains conditional until actual successful safe load/search/GT.
4. Freeze a new complete executable-ready plan with resolved identities,
   quality-smoke criteria, swap/thermal/power monitoring, exact phases/observer
   contracts and all66 orders. Do not modify this blocked PLAN to hide changes.
5. Preserve failures, full pre/post audits, native-index attribution and tail labels.

No owner permission is re-requested for already-authorized safe audit/build work;
the blockers concern the definition of a valid default baseline, not availability
of consent. No automatically chosen alternative compiler/flags/memL/subject exists.

## Evidence contents, verification and preservation

`source/`: pinned snapshots,47 actual diffs plus merge-parent diffs, host/header/
identity/charter/PR reads. `build/`: configure and reproduced failure logs,
CMakeCache, compilation database and flags. `audits/`: input/index full checks,
resource budget. `tests/`: full339-test stdout/stderr, focused results and diff-check.
`reports/`:00–08. Root: PLAN, SUMMARY, INTEGRITY, planned RUN_INDEX, empty
RUN_METRICS, absence-labeled derived CSVs, HOST_OBSERVATIONS and SHA256SUMS.
SHA256SUMS excludes itself; PUBLICATION has a separate sidecar after publication
to avoid modifying the finalized evidence checksum set. External logs/source/
large CSV/JSON/traces are not committed. Only small reports/blocked plan/passive
helper/tests are published as a new Draft PR; PR23/24/25 and main unchanged.

Historical preservation means no writes into old paths and unchanged subject
commit/cleanliness/binary hashes +canonical full input/index hashes. It does not
claim a new full before/after hash of every old campaign file; that was not done
in this task. Old classifications and protocols remain historical evidence.
This deliverable is a rigorous blocked rebaseline handoff, not completed OSDI results.
