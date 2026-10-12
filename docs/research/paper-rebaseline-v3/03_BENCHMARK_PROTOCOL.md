# Prospective v3 contracts and blocked execution

Three genuinely predeclared immutable records exist locally:

| Contract | SHA256 | Timing/status |
|---|---|---|
| BUILD_PLAN.json | `085f23a483936d1671f269007b212e5a197e893f95bcc5713dd310fbe15ba012` | Written before T8 construction |
| BUILD_T4_PLAN.json | `f77c4c1ba2bf2555221012f3d833088a05581fe54f2c34ab259d1fa7d79f261a` | Written before the single new T4 resource amendment |
| SEARCH_DESIGN.json | `b32acd39f13e644a597f976cb4ac82fc4c5a6d2bf479dd3545df0d2bb3b78df4` | Written before any search; never became execution-ready |
| PLAN.json | `2436c7c579fe3af3feecac5ade0b87bf1fae910e85f8cf3758b3c388c6c20a08` | Archived blocked ledger; execution_ready=false; never execute |

The final ledger is not retrospectively called an accepted measurement plan. The original v1/v2 plans remain unchanged/non-runnable. The amendment preserves T8 failure, changes only user-space construction threads/prefix and has no third attempt. No performance result was observed to choose T4 or the pause policy.

Build safety:≤1GiB MemAvailable,≤20GiB free disk, AC-state change, foreign recognized ANN process, readable critical-trip proximity≤2°C, package≥98°C sustained10s, swap growth>64MiB sustained10s, owned timeout =>STOP. Readable critical proximity can stop immediately, without needing10s sustained heat. T8 timeout7200s; T4 timeout5400s. A standalone RAPL policy readout transition is logged, not fatal. No source evidence shows a benign cap transition corrupts graph construction. Build output nondeterminism/thread timing is recorded by actual bytes, not constant-power speed claims.

Search design preserves K10/L100/mode2/uint8/l2/PQ/W32, paper mem_L10, modern mem_L0, exact canonical10K query/GT. Native environment requests OMP_NUM_THREADS=T,MKL_NUM_THREADS8,OMP_DYNAMIC=FALSE; binding/places/GOMP affinity unset. Builder source itself sets MKL/OMP threads from the T argument. No CPU pinning, governor, RAPL, scheduling or storage policy changes.

Primary order (source run_order):

| Block | Frozen cells |
|---|---|
|1|PAPER_T1 PAPER_T4 PAPER_T8 PAPER_T16 MODERN_T8 MODERN_T16|
|2|PAPER_T4 PAPER_T8 PAPER_T16 MODERN_T8 MODERN_T16 PAPER_T1|
|3|PAPER_T8 PAPER_T16 MODERN_T8 MODERN_T16 PAPER_T1 PAPER_T4|
|4|PAPER_T16 MODERN_T8 MODERN_T16 PAPER_T1 PAPER_T4 PAPER_T8|
|5|MODERN_T8 MODERN_T16 PAPER_T1 PAPER_T4 PAPER_T8 PAPER_T16|
|6|MODERN_T16 PAPER_T1 PAPER_T4 PAPER_T8 PAPER_T16 MODERN_T8|

Then24 fixed T8 W32 L50/75/125/150 version-native cases and6 paper T8 L100 W16/64 cases, all order rows in PLAN/runs.csv. Secondary requires all36 primary cases and six comparable blocks. Fixed pauses20s within blocks/60s between blocks,120s settling after correctness, selected prospectively because construction had already demonstrated limited thermal headroom. Suite cap3600s, per-run600s. None of these sleeps or searches was executed.

Search comparability is separate: any sampled power/RAPL transition anywhere in a complete six-cell process/gap block =>ENV_CONFOUNDED; incomplete readable policy=>UNKNOWN. Preserve all measurements and no performance retry/exclusion. Between-block benign transitions do not retroactively invalidate stable blocks. This whole-process rule is deliberately conservative: it cannot precisely localize a transition to the search timer and can reject potentially comparable timing windows. Future phase-aware refinement would require its own predeclared contract, not post-hoc relabeling.

Statistics: run/block unit, report every run and mean/median/SD/MAD/min/max. Paired deltas100(target/reference−1),20,000 block-bootstrap draws, seed20261012, percentileCI90 with linear p(n−1) interpolation. No request/query pseudoreplication. All actual statistics are absent because construction failed; no bootstrap is run on invented values.
