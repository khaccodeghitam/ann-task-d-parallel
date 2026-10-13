# Issue #32 — Custom Full-Fan SIFT10M paper baseline

**Outcome: 36/36 stock runs qualified; all 12 independent quality validations passed; pre/post package audits passed.** This is a valid campaign for the locked Custom operating condition. It measures the paper-portable subject only.

Campaign `CUSTOM_FULLFAN_SIFT10M_20261013T115304462961Z`; external raw evidence is held in the local workspace under `research-v3/campaigns/` and is not committed. The frozen PLAN SHA256 is `37bc6b41eb49eec856c5fd67a465bd56f327dfaeb8f28d289420b5a47e066c81`. The GitHub-facing projection intentionally omits absolute paths, raw machine dumps and query-level result CSVs. The plan binds harness commit `f9ab1dbb128c5b65a34455358164e7e3cbdc1fdd`, wrapper source digest `8edb351f6c0df700eb4f14d9dec7c4a73053c9e7233832b1243957edf79f7b3e`, and thermal-guard digest `232ed904b54359af17161c2f785b81c77097aad4d99f68325e08faf88cfefcbb`.

## Subject and inputs

- Upstream artifact: PipeANN 0.1.0, `d18dcd16fece1c9d1dea356d783ebba2ed649e54` (tree `8e6ee6b0dc71db7dfa9db742c2f7066929202bc2`). Measured subject: `PAPER_GCC13_PORTABLE`, commit `c4cd32c6816c063f56ecc64f9d7b63c909202cab`, tree `23fbb256528c67454cd4348bc58dfee700dffa06`; the only source adjustment is the documented GCC13 AVX2 float horizontal-reduction portability patch.
- Search binary SHA256: `5f5fa8d99cc83b523c71b7025e5f0b9aa61f45d42816804ed6d88755ebaa310b`.
- Canonical SIFT10M INPUT package SHA256: `47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3`; paper-native INDEX package SHA256: `7140a47ac53b0480752059b5cb428b4d56dc627533974803b5ae4413827a7470`. Both passed full component checks before and after.
- Search configuration: uint8, L2, PQ, mode 2, K10, mem_L10, canonical 10k queries, native OVERLAP_INIT. Core/extension defaults W32 and L100. No index rebuild occurred.
- Stock CLI shape (T shown as 8 or 16; path variables stand for the audited local manifests): `search_disk_index uint8 <paper-index-prefix> <T> <W> <canonical-query.bbin> <canonical-gt_10m.bin> 10 l2 2 10 <Lsearch>`. Environment: `OMP_NUM_THREADS=<T> MKL_NUM_THREADS=8 OMP_DYNAMIC=FALSE`, with `OMP_PROC_BIND`, `OMP_PLACES`, and `GOMP_CPU_AFFINITY` unset. The executable performs its source-defined two L=200 warmups before the timed phase. Per-run `command.sh` and environment are sealed in the local evidence.

## Operator and environment

Owner explicitly confirmed manual full-fan, stable AC and no interaction during the campaign at `2026-10-13T11:54:03Z`; the preflight had independently recorded `platform_profile=custom`, MMIO PL1/PL2 60/90 W and AC online. The owner confirmation was recorded before the run plan froze; fan RPM was **not measured**. The wrapper initially saw two sysfs paths for each MMIO register. Source and inode checks established they were aliases of the same physical register with matching values; the execution correction accepts only positively identified same-inode aliases and still rejects distinct or conflicting registers. Five focused alias tests passed before execution. AC was online and platform profile was `custom`. MMIO PL1/PL2 readouts were 60/90 W within ±1 W throughout; limits are not actual consumed watts. The initial package sensor read 33°C; maximum sampled package temperature was **84°C** in stock runs and **86°C** in all quality commands. Campaign qualification and guard completed without a stop. Minimum sampled available memory was approximately **12.1 GiB** for stock.

The wrapper captured 1 Hz mixed process-lifetime snapshots: 576 stock and 193 quality samples. Stock runs had 12–38 samples each; observed collection wall time peaked at 164 ms and observed maximum scheduling lateness was under 3 ms. These include index loading, two warmup passes, timed search and teardown. The snapshots record observer CPU time, but these measurements do not establish benchmark observer-effect equivalence. The executable log reports `sq_poll: 1`; external snapshots observed no `iou-sqp` task records. This does not establish that no SQPOLL activity occurred. No phase-aligned CPU utilization, device IOPS/latency, fan RPM or causal scheduling evidence is claimed.

## Core paired result

The six frozen T8/T16 paired-block QPS changes (T16 relative to T8) were `-14.70%, -13.95%, -11.85%, -14.35%, -9.03%, -12.76%`. Median **-13.36%**, mean **-12.77%**, sample SD **2.12 percentage points**, deterministic 20,000-resample block bootstrap CI90 **[-14.35%, -11.49%]**. All six paired values are below zero. Leave-one-block-out medians span -13.95% to -12.76%. The recall paired median is 0.000 percentage points (CI90 [-0.010, 0.005]); recall is effectively matched at the printed 0.01-point precision.

This establishes a repeated T16 lower-QPS observation for this paper-portable executable, native index, host and Custom 60/90 W condition. It does not identify a cause, prove a general ANN scaling law, or transfer to the original paper binary or modern 2026 subject.

## Configuration summaries

| Cell | Runs | Median QPS | Mean latency (µs) | P99.9 (µs) | Recall@10 (%) | App I/O/query |
|---|---:|---:|---:|---:|---:|---:|
| T1_W32_L100 | 3 | 1059.89 | 899.90 | 1326.0 | 99.230 | 107.70 |
| T4_W32_L100 | 3 | 2681.85 | 1439.81 | 2156.0 | 99.210 | 107.12 |
| T8_W32_L100 | 6 | 3571.99 | 2166.63 | 4397.5 | 99.210 | 106.90 |
| T16_W32_L100 | 6 | 3104.62 | 4987.13 | 83554.5 | 99.210 | 106.94 |
| T8_W32_L50 | 3 | 5736.31 | 1335.09 | 2249.0 | 97.210 | 58.50 |
| T8_W32_L75 | 3 | 4394.56 | 1749.27 | 2788.0 | 98.640 | 82.50 |
| T8_W32_L125 | 3 | 3004.26 | 2571.30 | 3930.0 | 99.510 | 131.46 |
| T8_W32_L150 | 3 | 2602.97 | 2972.99 | 4345.0 | 99.670 | 156.09 |
| T8_W16_L100 | 3 | 3563.90 | 2176.45 | 3219.0 | 99.210 | 105.95 |
| T8_W64_L100 | 3 | 3567.15 | 2162.63 | 3317.0 | 99.210 | 106.91 |

The paper driver’s tail statistic is **P99.9** (source percentile 0.999), even though the legacy console heading says P99. P50, P95 and P99 are **NOT_MEASURED** from the stock binary. Mean I/O/query is an application counter, not device-level I/O latency. The width setting is a configured cap; actual time-weighted width was not measured.

## Full run ledger and validity

- [`runs.csv`](runs.csv) contains every one of the 36 stock runs in frozen chronological order, with run IDs, metrics, times and per-run host sample summaries.
- [`quality.csv`](quality.csv) contains all 12 separate 10,000-query quality checks; each independently checked 100,000 rows, valid/unique IDs, finite nonnegative distances, exact uint8 squared-L2 distances and recall against canonical ground truth.
- [`paired.csv`](paired.csv) contains the six block pairs and raw pair deltas.
- [`PLAN.json`](PLAN.json) is a sanitized projection; its linked original frozen execution plan is identified by the digest above and remains in local evidence.

All 36 stock runs returned successfully and were classified QUALIFIED by the frozen wrapper; there were no invalid or incomplete runs and no retries. Full audits passed. Raw logs, exact command manifests, one-hertz telemetry, 100k-row validation outputs, and sealed checksums remain local in the campaign evidence directory.

## Interpretation

The controlled repeated result supports that T16/W32 delivered lower throughput than T8/W32 in this campaign while recall remained matched. The mechanism remains unresolved. The observed CPU, frequency and SQPOLL process snapshots span multiple phases and cannot distinguish scheduling delay, hybrid-core placement, polling, device wait or search dependency. The small L/W sweeps show recall and application I/O changing with L; W16/W64 have very similar QPS and recall at T8 for this test. These are descriptive settings comparisons, not causal mechanism tests.

The separate earlier one-run Custom T8 value and the historic modern PipeANN results use different evidence and are not pooled or presented as a direct comparison. D1 remains UNTESTED, D6 INCONCLUSIVE, D4 NOT TESTED. No novelty or algorithm improvement is claimed.

## Reproduction

The executable command and every per-run environment are preserved in local raw manifests. The runner and MMIO-alias identity correction are versioned in this branch; inspect `configs/custom_fullfan_campaign.json` and `tools/research/issue29_campaign.py`. Do not rerun this campaign as a quickstart: raw evidence is authoritative and the full procedure requires a new prospective approval and frozen campaign.
