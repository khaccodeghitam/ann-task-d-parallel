# P0 source and evidence audit

Audit date: 2026-11-15 (Asia/Ho_Chi_Minh). Evidence labels: SOURCE = inspected
code/document; A-OBS = reported Task A measurement; SYNTHETIC = new artificial
fixture; OPEN = unverified. No new D-OBS performance evidence exists.

## Proposal and identity

Read the full proposal obtained from Drive file
`1R_Mo28f_AsgXAntO8GRBfCuwEsu0I3Au`,
`TASK_D_A_GRAPH_TOPOLOGY_PARALLEL_TRAVERSAL_PROPOSAL_20261115.docx`.
SHA256 `a7aef4ba2ed867ed8799f72baec463ab5bd59c6fbdd190327d38b6953b260b45`.
The same-named file in local Downloads has identical bytes. The exact filename
ending `(1).docx` was not available; identity with that copy is NOT_VERIFIED.
The preceding chat's P0–P6 summary agrees with this document's stages.
The user's correction supersedes the stale proposal checklist: **h17, no 587**.

## Repositories pinned, not assumed to be measurement source

| Repository/ref | Inspected SHA | Role |
|---|---|---|
| Task D main | `be93cafce7247242c4a9f0bfba1fbc20112e28c7` | Base of this isolated research branch |
| Task D codex/e3-phase-aware-adaptation | `c6cc91b15a07236f84e4fdf2ea7b1652af6e3723` | E1/E2/E3 source and frozen validation |
| Task A main | `0e8efb2` (full in manifest) | Initial source repository |
| Task A research/r85-h17-flat-tuning-20261111 | `4e49912618d021fceb7bf3faa769479b4e539cd6` | R85 SIFT1M runners/source overlay/history |
| Task A research/h17-two-tier-r77 | `d1b5b1a44122a6ce667ece548ea95a3b12df2d19` | H17/TwoTier implementation reference |
| Task A backup/r86-source-only-20261114 | `2558e018c71f412b4e4e4eddb79264c7ce6ac730` | R86 curated source, graph writer and acquisition/evaluator contracts |

Task A repository: <https://github.com/nuyntai19/ann-task-a-research>.
Task D repository: <https://github.com/Irthn1311/Parallel_ANN_Research>.
File-level identities and exact paths are in [source_files.json](source_files.json).

R86 `source_snapshot_r86_20261114/README_SOURCE_SNAPSHOT.md` explicitly excludes
data/graph/binary/log/result trees and is not a complete dependency checkout.
The frozen `E_PROTOCOL` rows have blank source_commit/source_diff fields and
unrecorded seed/random-source provenance. The snapshot SHA must **not** be
retroactively substituted for a measured graph's builder source SHA.
The formal build script itself imports pinned external scripts/binaries.
Source presence is insufficient to reproduce those artifacts.

## Task A observations and caveats

Source workbook: <https://docs.google.com/spreadsheets/d/12ApqgMV8YykflyFXUT2VMbUhgyiGirtoOmRWCXCz3Ek/edit>.
The user-linked gid 1711111131 resolves to `R86_WN_SCALING`, not FORMAL_QPS.
Metadata and exact sheet titles were read before the bounded reads.

| Evidence | Location | What is actually supported |
|---|---|---|
| Formal QPS | R86_MST1M_FORMAL_QPS!A1:T16, gid 1711111138 | Sheet reports 18 OFF builds, 36 calibrations, 180 native Search processes; 3 independent graphs × 5 processes at each floor |
| C/K/N arm separation | R86_MST1M_5ARM_FACTOR!A1:S17 | ON counters are BUILD work; OFF timing/QPS come from separate graphs |
| Graph/data identities | E_PROTOCOL!A47:X64 | 9 OFF A0/A1/A3 graph hashes and base/query/GT hashes copied into manifest; files absent locally |
| W(n) | R86_WN_SCALING!A1:X19 | Sheet reports 15/15 raw-evidence audits; graph binaries excluded, graph-byte hashes not independently recomputed in that audit |
| Other inspected context | FILE_CONTRACT!A1:X13, R86_MST1M_WORK_ON_4ARM!A1:X65, B_SEARCH!A1:Z6 | Contract/work distinctions; early B_SEARCH rows are SIFT100K and are not formal MS-Turing receipts |

| Arm | BUILD median seconds | RSS MiB | QPS floor .990 | QPS floor .998 |
|---|---:|---:|---:|---:|
| A0 Stock C160/K1024/N2 | 41.98 | 3045.074219 | 1225.922 | 562.069 |
| A1 H17 C160/K1024/N2 | 36.39 | 3052.769531 | 1226.076 | 562.358 |
| A3 H17 C64/K512/N2 | 28.73 | 2164.050781 | 842.017 | 342.719 |

These are A-OBS, median-of-three graph medians, each median-of-five processes.
A0 vs A3 Recall medians are .99103302 vs .99028999 at the .990 floor and
.99817401 vs .99806798 at .998. **Quality-floor matched is not exactly matched
Recall.** A3 QPS differences (~−31.3%, −39.0%) are not multi-worker regressions
and do not establish topology causality. A1 is the necessary H17-only control.
Native per-query p50/p95/p99 and search distance-work are NOT_MEASURED here.
Never substitute `1e6/QPS` for measured latency, or BUILD W_P/W_A/W_L for search work.

The Factor tab retains older caveats claiming A3 SHA/bytes are pending; its row
8 readback addendum explicitly supersedes that text. A3 ON graph SHA is reported
as `ee7fd5aad6694ea6947b4568dd7ba9f04c63a6f461373f6a695fce87edf00931`.
It is an ON BUILD graph and **not one of the nine OFF formal graph artifacts**.

## Task D evidence reconciliation

At pinned E3 ref, `docs/research/e1-inspired/E2_PARTIAL_RESULTS.md` reports
full-10K QPS 19.209/10.718/15.093 and Recall@100 .997106/.997188/.997129.
The proposal's approximately 19.19/10.70/15.04 and .997163/.997221/.997155 are
the **8K test split** of those runs. There is no contradiction after naming the
split. They are unpaired descriptive runs with thermal/order confounding.

`E3_VALIDATION.md`: IMPLEMENTED_FIXTURE_VALIDATED, no SIFT1M speedup;
maintenance remains serialized under one mutex. `engine.hpp` requires >=2
workers split into maintainer/calculator roles, and seeds entry neighbors plus
cyclic IDs to fill capacity. That is not a one-worker/multi-walker parity engine.
No E3 code or claim is promoted into the new common baseline.

## Availability and decisions

AVAILABLE: both repository histories, specified Task A branches, source format
contracts, proposal copy, spreadsheet reported measurements, new synthetic tests.
MISSING locally: all 9 OFF graph files, base/query/GT files, original builder and
Search binaries, native raw receipts/logs. Targeted search of the workspace,
Documents and Downloads found no matching graph/data artifacts; Git excludes them.
NOT_VERIFIED: seed/build provenance, exact `(1)` proposal copy, qualified host,
real-graph compatibility and real Recall, policy parity with Task A/iQAN/E3.

P0/P1 = HOLD. No evidence yet warrants a research NO-GO. Directly passing PiPNN
bytes to an NSG loader is NO-GO **for that loading method**. Converting while
altering adjacency/order/IDs would be NO-GO for topology-only comparison.
