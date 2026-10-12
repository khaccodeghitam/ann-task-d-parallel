# Prospective benchmark protocol and observed host

PLAN `c79e74cb5e40fe59065c8de147ba582804f7557698b90f093d912f8d85ccf205` is frozen at `/home/irthn/ann-research/research-v3/campaigns/PAPER_REBASELINE_SIFT10M_20261012T144741235340Z/PLAN.json` and mirrored here.
**BLOCKED_PROSPECTIVE_DESIGN**, execution_ready=false. It records the requested
suite and predeclared estimands before performance observations; it is not a
fully ready execution plan. No accepted or rejected ANN run has been launched.

Primary36 stock runs, six paired blocks:
```
B01: PAPER_T1 → PAPER_T4 → PAPER_T8 → PAPER_T16 → MODERN_T8 → MODERN_T16
B02: PAPER_T4 → PAPER_T8 → PAPER_T16 → MODERN_T8 → MODERN_T16 → PAPER_T1
B03: PAPER_T8 → PAPER_T16 → MODERN_T8 → MODERN_T16 → PAPER_T1 → PAPER_T4
B04: PAPER_T16 → MODERN_T8 → MODERN_T16 → PAPER_T1 → PAPER_T4 → PAPER_T8
B05: MODERN_T8 → MODERN_T16 → PAPER_T1 → PAPER_T4 → PAPER_T8 → PAPER_T16
B06: MODERN_T16 → PAPER_T1 → PAPER_T4 → PAPER_T8 → PAPER_T16 → MODERN_T8
```
Every cell appears once in each order position. Sweep24: L50/75/125/150 atT8/W32
for each version, three repetitions with fixed alternating/rotated order.
Width6: artifact T8/L100 W16/64×3. All66 command templates and environments are
explicit in PLAN; paper prefix is a **proposed absent** native-index path.
Requested mem_L0 is incompatible with default artifact; this plan must never
be relabeled executable by filling in a binary hash after an unsupported change.

Search query/GT identities are frozen; K10, uint8/L2/PQ/mode2. Environment:
OMP_NUM_THREADS=T, MKL_NUM_THREADS=8, OMP_DYNAMIC=FALSE, LC_ALL=C,
S_TIME_FORMAT=ISO; OMP_PROC_BIND/OMP_PLACES/GOMP_CPU_AFFINITY unset.
No pinning, drop-cache, governor/EPP/scheduler/power/NVMe change.
Five-second gaps between finalized cases,15 seconds between primary blocks,
no last pause. Stock warmup behavior is part of each version's contract, not
removed to improve numbers. Equal external observers must distinguish loading,
paper warmups, measured parallel loop and teardown.

**DIRECT MEASUREMENT:** `/dev/nvme0n1p6` ext4, initial free125272764416 bytes,
RAM16542265344/MemAvailable14192574464 bytes, swap initially unused.
Native i7-12700H hybrid20 logical/14 physical. AC online1 observed in snapshots;
governor powersave; readable RAPL-MMIO package PL1=115000000µW, PL2=135000000µW,
other RAPL interface PL1=200000000µW. These are policy readings, **not actual
power consumption or proof of Performance Mode/stable power**. Lenovo mode
was not independently established. Temperatures/frequencies are timestamped
snapshots in host JSON, not sustained-run evidence. No quiet qualification was
claimed because no benchmark proceeded. Absence of Firefox in a snapshot is
not proof of zero interactive/background load.

Prospective safety guards: stop on reliable package≥98°C for10s, proximity≤2°C
to known critical trip, immediate critical/system warning, AC/readable power
policy change, MemAvailable≤1GiB, significant swap growth, free storage≤20GiB,
extraneous ANN process. Never kill unrelated user processes. Reliable-sensor
absence is UNKNOWN, not safety certification. Exact executable swap/resource
monitoring must be finalized before a new runnable plan; no generic monitor
was built around an already-invalid search contract. Cap active build/benchmark
commands at3h; record idle/export/audit overhead separately.

Primary unit=complete block. Deltas100×(A/B−1),20,000 resamples, seed20261012,
median estimator, CI90 5th/95th linear p(n−1) quantiles. Report all values plus
mean/median/sampleSD/MAD/min/max; no request/query pseudo-replication. There is
no invented equivalence threshold. Curves retain every fixed-L run and recall;
recall-matched interpolation only inside measured overlap, with explicit method
and no extrapolation. Native-index system comparison does not isolate search.

Acceptance requires executable/index correctness smokes, query count10000,
valid/nonduplicate output IDs and finite distances, conservative diagnostic
parser, no CQE/read errors even exit0, exact identity/env, matched observable
coverage and full pre/post package audits. Sparse1s device-wide telemetry is not
precise search-only CPU/SSD utilization. Missing required evidence invalidates;
slow results remain. No retry, substitution or replacement campaign occurred.
