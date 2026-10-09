# D1-O1 design and source-contract validation

## Outcome

**D1_O1_DESIGN_ONLY**, the explicitly permitted Issue #20 stopping outcome.
No candidate-readiness instrumentation is shipped and no new ANN binary is built.
This does not satisfy D1_O1_READY, does not classify D1 scientifically, and does
not inherit a readiness or observer-comparability pass from an older E0 campaign.
D1 hypothesis UNTESTED; D1 observability NO; D6 INCONCLUSIVE; D4 NOT TESTED.

The source audit supports safe selector-result observations, but those point
observations cannot answer the required continuous kill test on their own. A
correct observer needs coordinated candidate mutation hooks, residual publication
identities, selection/pre-send phases and conservative scheduling attribution.
Adding a partial set of counters would not establish conservation or the durations
required for READY. The scope decision is to stop before that broader observer
interface/protocol implementation, as Issue20 allows. It is not a claim that all
future observational implementations necessarily change ANN semantics.

## Source-grounded findings

- `next_read_nbr`, `next_calc_nbr`, `frontier` mutate marker/flag/visited state.
  Test-only repeated calls expose this contract; no extra ANN selector is added.
- The batch merge trims old candidates and new discoveries separately, then moves
  storage in bulk. Discovery, admission, current rank and eviction are different.
- A selected candidate can be evicted while its copied FIFO request remains live.
  Its page can subsequently enter id_buf_map with no eligible live calc candidate.
  Map non-emptiness is not calc readiness, nor is reserve128 a residency bound.
- Selection clears flag before the active lock call. Current IO_SELECT is after
  lock/req preparation and cannot account for selected-before-send delay.
- Calc selection marks visited before expansion, and the current tracer frees
  physical request correlation at publication. No guessed expansion/request edge.
- Cache-ready publication has no physical submit/CQE. It remains separate from
  physical userspace-observed I/O and hidden completion counters.
- The generic single-insert duplicate sentinel has a non-full size side effect.
  The normal neighbor batch's visited-set dedup precondition avoids that fixture
  path; no algorithm bugfix or assertion about real workload incidence is made.

The [state model and kill test](D1_O1_STATE_MODEL_AND_KILL_TEST.md) maps each fact
to exact source hooks, overlapping populations and conservative UNKNOWN states.
Its prospective threshold snapshot [D1_KILL_DESIGN_V1.json](plans/D1_KILL_DESIGN_V1.json)
has SHA256 `15bf2ea1598978fc90546d425cc75676cb314aa52fc23c70d660e067abbe2846`.
It is an unexecuted design, not a frozen accepted-measurement campaign.

## Identity and evidence

Research branch `research/d1-o1-candidate-readiness-observability`, base
`4c5e00eec1b9ce4acb8d18781a5b19d2129e4dad`. Both ANN worktrees were clean before
and after validation and remain at the same commits/trees/binary hashes:

| Subject | Commit | Tree | Search binary SHA256 |
| --- | --- | --- | --- |
| Golden PipeANN | b9ec4ba86ff5d70bec277984777197f28dc2cf42 | 6bb51b8b20d39adb8dd04b44a14348e7f5d7bb1a | a02ce69d1467727344c8620a254b4cba51d12616d3da171ef7c1a6668a9e8bc5 |
| Instrumented PipeANN-p0 | 35222026893ff7d1b45586fcdd8165a5ce592cd3 | a0f730206dd5d5e7e2c06bdf5894c583a79613ca | f5795e43c3be1f2515bd37e21ad1fbab45b2849c859724629a8c6edea5e418dd |

[D1_O1_SOURCE_AUDIT.json](subject/D1_O1_SOURCE_AUDIT.json) records exact source
SHA256s and existing build flags. New subject commit/tree/patch/binary are **none**.
Existing exact subject reproduction remains in [G0C1_REPRODUCE.md](subject/G0C1_REPRODUCE.md)
and the existing P0/G0C1 patches and commit objects; none were changed.

External evidence:
`/home/irthn/ann-research/research-v3/notes/D1_O1_20261009T101745695033Z/`.
This is source/test/replay evidence, not a benchmark campaign. It contains compiler
argv/logs, test logs, preservation hashes and replay results; none are committed.

## Tests actually run

**318 Python research tests PASS**: 305 historical tests plus 13 new replay tests.
The existing suite includes malformed physical/cache/FIFO traces, missing/lost
events, interleaved workers, sample coverage and PANTRC01/02 compatibility.
The new tests enforce canonical JSON equivalence without boolean/number coercion,
run-order preservation, duplicate-key/collision rejection, finite values, exclusive
new output and preservation of historical baselines/failure diagnostics.

```bash
.venv-research/bin/python -m unittest discover -s tests/research -v
git diff --check
```

**14 actual-header C++ source-contract probes PASS in each of two builds**:
optimized O3/NDEBUG and ASan+UBSan (28 successful probe executions). They include
empty/read-eligible controls, selected-before-send, ready-unselected, selector and
frontier mutations, frontier rewind, admission/rejection/eviction, published-but-
ineligible, rescore identity/flags, duplicate sentinel and distance ties.
Assertions remain active under NDEBUG through explicit checked exceptions.
These are read-only fixtures against the real subject header, with no stubs;
fixture publication sets simulate the existing ready predicate. They are **not**
an end-to-end candidate observer, lock/cache reader test or new tracer certification.

Exact commands, with OUT pointing to the exclusive evidence directory above:

```bash
/usr/bin/c++ -std=c++17 -fopenmp -Wall -Wextra -O3 -DNDEBUG \
  -I/home/irthn/ann-research/PipeANN-p0/include \
  /home/irthn/ann-research/Parallel_ANN_Research/tests/research/candidate_readiness_contract.cpp \
  -o "$OUT/candidate_contract_optimized"
"$OUT/candidate_contract_optimized"
/usr/bin/c++ -std=c++17 -fopenmp -Wall -Wextra -O1 -g \
  -fsanitize=address,undefined -fno-omit-frame-pointer \
  -I/home/irthn/ann-research/PipeANN-p0/include \
  /home/irthn/ann-research/Parallel_ANN_Research/tests/research/candidate_readiness_contract.cpp \
  -o "$OUT/candidate_contract_asan_ubsan"
"$OUT/candidate_contract_asan_ubsan"
```

No ASan/UBSan diagnostic was emitted; both compilers/executables exited0.
No ANN source was touched even to build these fixture executables.

## Historical replay and immutable evidence

The new read-only helper runs the unchanged authoritative local analyzers:

```bash
.venv-research/bin/python tools/research/replay_research_history.py \
  --campaign-root /home/irthn/ann-research/research-v3/campaigns \
  --output "$OUT/historical_replay_verified"
```

The output directory must be new and outside historical campaigns. Results compare
canonical JSON (including normalized numeric histogram keys), not incidental
formatting. All five comparisons pass:

| Historical campaign | Baseline directory | Canonical result SHA256 |
| --- | --- | --- |
| E0B_SIFT10M_20261008T151707400337Z | analysis | f1bcdc8d2ee0a754707e60a8ae684375b8d08ac91b0ccc9d772a0aab30b9474b |
| E0C_SIFT10M_20261009T055255739318Z | analysis | d5fda8246fea7cb8f63843006cff7c4920a8f5548ef95d8f2ca8acdb234e86c3 |
| G0B_SIFT10M_20261009T063743710720Z | analysis_final | 69467e66d8fa24466a8be88d51c6955541a1193e1f97d62a01ed7aca0c0d81fe |
| G0C1_SIFT10M_20261009T073827804239Z | analysis | 520e456263cde6d627a4406a1ec4c750137f14e577ff209eb54fa7f9f063e623 |
| G0C2_SIFT10M_20261009T090432438598Z | analysis_verified | a369f9a78b14bba462699e94152489649409e5028a933466cfc0df3298305fd5 |

An initial helper invocation referred to a nonexistent G0C1 `analysis_final` path;
its failure log/new derived results remain in `historical_replay/`. The explicit
baseline mapping was corrected to its actual `analysis/` directory and replayed
into a separate new directory. No historical result or analyzer changed.

Before/after full SHA256/size comparison of **4,968 existing files** under external
`runs/` and `campaigns/` passes with identical path sets and contents. Replayed
outputs live under the new notes directory. Historical package audits, MLflow IDs,
plans, traces, status semantics and campaign findings remain unchanged; no new
MLflow run or finalized ANN run was created.

## Conditional gates and limitations

| Gate | This Issue20 outcome |
| --- | --- |
| Exact source audit, state definitions, prospective falsifiers | Complete |
| New observables / candidate conservation / readiness trace health | Not implemented or certified; UNKNOWN |
| Optimized/sanitized actual-source contract fixtures | PASS, limited as described above |
| Full Python regression and five historical replays | PASS |
| New subject/binary identity | None; existing hashes unchanged |
| T1/T8/T16 new observer DETAIL smokes | Not applicable: no new observer/binary |
| New 12-block36-run native E0 | Not applicable, not inherited and not claimed PASS |
| T16 observer consistency calibration | Not applicable; prerequisite to any future implementation |
| New pre/post full-component package audit | Not applicable: no accepted measurements/package changes |
| Official D1 kill test | Not executed; separate authorization/protocol required |

Package **manifest digests only** were rechecked and match frozen INPUT
`47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3` and INDEX
`8955f8bca0c8ebb5afbd2a69e9760fc829d22ba76a4ef7b482339e88b2489595`.
This is not called a new full-component audit. Historical full pre/post audit
acceptance is checked during campaign replay. Data/index files were not rewritten,
rebuilt or used in new accepted benchmark runs.

Unknowns remain: continuous candidate eligibility, pool/residency conservation,
pre-send lock/resource duration, off-CPU/critical-path attribution and active-query
occupancy. Existing timestamp interval IO_SUBMIT→IO_CQE_SEEN remains
**userspace-observed I/O interval**, not device hardware latency. Publication HOL
is an application interval, not automatically query-critical time. No timing hook
or historical trace interpretation changes.

## Next scientific step and publication boundary

Review the source-grounded full observer prerequisites and prospective kill-test
thresholds before authorizing a separate implementation. Require all mutation and
phase coverage, bounded identity storage and complete synthetic controls first;
then new subject smokes/native E0/T16 consistency/full package audits. Only after
those gates may a separately frozen D1 necessity/kill-test campaign evaluate the
design's NO-GO or prioritization conditions. No claimed D1 effectiveness or speedup.

This PR adds two reports, prospective JSON design, source fingerprint metadata,
actual-header contract tests and a read-only historical replay helper/tests. ANN
search/candidate selection/FIFO/width/distance/io_uring/graph/golden/main remain
unchanged. No D1/D4 implementation, FIFO fix, adaptive W, motif modification,
SIFT100M, new scientific campaign or novelty claim. No dataset/index/binary/raw
trace/telemetry/MLflow artifact is committed. Publish only this research branch as
a **Draft PR**, leave main and both subjects unchanged, and stop without merging.
