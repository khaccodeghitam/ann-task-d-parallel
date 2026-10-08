# E0b SIFT10M paired reproducibility — Issue #10

**E0B_PROCEED** under the frozen paired-block protocol. Thirty-six accepted runs (12 blocks), no exclusions. This is an operational reproducibility gate under a specified placement/observer regime, not an instrumentation-overhead proof or novelty claim. G0 Stage B/C remain unexecuted.

## Exact state and protocol

- Campaign: `E0B_SIFT10M_20261008T151707400337Z`.
- Evidence: `/home/irthn/ann-research/research-v3/campaigns/E0B_SIFT10M_20261008T151707400337Z/`.
- PLAN SHA256: `fcdaf174e9404c3ded663a8e5f84f35df2d89785f28bcee9871f43ded996e576`.
- Main/base: `481b61e86efc36dbc213b707de0cf7f9e7fbd192`.
- Measurement harness: `be9a5ba4b4edeeb5fe512c8f6910dfeb5015925a`, clean throughout measurement. Report/analyzer commit is the commit containing this document, created after all runs.
- Golden subject: `b9ec4ba86ff5d70bec277984777197f28dc2cf42`; binary SHA256 `a02ce69d1467727344c8620a254b4cba51d12616d3da171ef7c1a6668a9e8bc5`.
- Instrumented subject: `3bdcc064cb96aae4cd845bd2bb6adc5f5ba63e19`; binary SHA256 `d51066cc5fe0cf2df71149e23910ce654dcc259ed271fea28ae7002c53a8bd18`.
- INPUT_PACKAGE SHA256: `47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3`.
- INDEX_PACKAGE SHA256: `8955f8bca0c8ebb5afbd2a69e9760fc829d22ba76a4ef7b482339e88b2489595`.
- [Frozen PLAN.json](plans/E0B_SIFT10M_20261008T151707400337Z.json), [PLAN.md](plans/E0B_SIFT10M_20261008T151707400337Z.md), [PLAN.sha256](plans/E0B_SIFT10M_20261008T151707400337Z.sha256).

The tracked plan snapshots preserve the exact original bytes. The checksum file retains the external filename `PLAN.json`; use `sha256sum docs/research/plans/E0B_SIFT10M_20261008T151707400337Z.json` when checking the renamed tracked snapshot.

Issue #10 and all requested P0/G0/SIFT10M documents were read before changes/measurement. Both ANN trees were clean at the expected commits. No ANN source or binary was rebuilt or edited. Existing SIFT10M canonical inputs/index and 10K queries were reused. All runs use uint8/l2/pq/mode2/T8/W32/K10/L100/mem_L0 and pipeann-b9ec4ba (printed P99 means percentile 0.99).

STOCK: golden, OFF trace mode, no causal trace. OFF: instrumented, causal enabled, trace OFF. LIGHT: instrumented, causal enabled, trace LIGHT. Every variant explicitly enables host telemetry (mpstat/pidstat/iostat, 1 s), package bindings and local MLflow. Same external pidstat -h -t -u -w process/thread observer and runtime snapshots at 0.35/1.2 s after benchmark discovery. No raw traces/events/telemetry are uploaded to MLflow. Observer overhead is part of this uniform protocol.

Pause policy: 5 s after harness finalization between runs within a block; 15 s between blocks; no final pause. Actual pause logs preserve requested/elapsed times. No warmup benchmark, cache flush, power/governor/EPP/NVMe scheduler tuning, affinity selection by QPS, or host-interference exclusion. All observed runs remain in the campaign.

## Placement preflight and runtime observations

`lscpu` confirms i7-12700H: 20 logical CPUs / 14 physical cores, P-core siblings 0–11 and single-thread E cores 12–19. The non-scientific OpenMP probe used g++ -O2 -fopenmp, with spread/threads; no ANN workload or QPS was involved. Two probes accepted libgomp settings, singleton masks and zero migrations over 30 observations per worker. Worker CPU sequence: 0,3,6,9,12,14,16,18. This mixes P/E cores; it does not isolate search from kernel helpers.

Frozen environment: OMP_PROC_BIND=spread, OMP_PLACES=threads, OMP_NUM_THREADS=8, MKL_NUM_THREADS=8, OMP_DYNAMIC=FALSE, LC_ALL=C, S_TIME_FORMAT=ISO; OMP_DISPLAY_ENV/OMP_DISPLAY_AFFINITY/GOMP_CPU_AFFINITY unset. Raw per-run commands, host snapshots, task affinities, ps and io_uring fdinfo are preserved. A non-iou task is not automatically equated with an OpenMP worker (a background task also exists); LIGHT query counters provide explicit worker/TID identities when available.

## Full package audit and historical integrity

Pre/post commands: .venv-research/bin/python tools/research/package_manifest.py verify <INPUT_PACKAGE.json|INDEX_PACKAGE.json> --full-components. Exact argv, stdout/stderr, UTC boundaries, duration and digest are preserved in adjacent audit files. All full-content audits pass and bracket every accepted measurement. No repair, chmod, regeneration or rebuild occurred.

| Audit | Start UTC | End UTC | Seconds | Result |
| --- | --- | --- | ---: | --- |
| pre_input | 2026-10-08T15:19:47.885171+00:00 | 2026-10-08T15:19:48.636523+00:00 | 0.751406 | PASS |
| pre_index | 2026-10-08T15:19:48.636789+00:00 | 2026-10-08T15:19:51.032116+00:00 | 2.395389 | PASS |
| post_input | 2026-10-08T16:25:10.584306+00:00 | 2026-10-08T16:25:11.327301+00:00 | 0.742995 | PASS |
| post_index | 2026-10-08T16:25:11.327507+00:00 | 2026-10-08T16:25:13.706499+00:00 | 2.378999 | PASS |

Integrity: 504 finalized run files checked against SHA256SUMS; 586 old run files unchanged. Golden/instrumented subject commits, binary hashes/size/mtime, and frozen PLAN unchanged. Issue #8 campaign files remain unchanged. Local artifacts are authoritative; MLflow readback is a separate mirror-integrity check.

## Paired values and deterministic statistics

Primary statistical unit is BLOCK. Percent performance delta = 100×(target/reference−1); recall delta is target−reference in percentage points. Decimal conversion of printed metrics avoids decimal-boundary roundoff; results are then represented as floats. MAD = median absolute deviation from the paired median; median absolute paired delta = median(|delta|), a distinct quantity.

Bootstrap: 12 block observations resampled with replacement, 20000 samples, random.Random seed 20261008. The same index draws are used for each comparison/metric; each resample contributes its median. CI90 is linearly interpolated 5th/95th percentiles (p×(n−1)). These are per-metric intervals, not a simultaneous confidence claim; no query/request/telemetry-sample bootstrap or p-values.

| Block | OFF/STOCK QPS % | LIGHT/OFF QPS % | OFF/STOCK latency % | LIGHT/OFF latency % | OFF−STOCK recall pp | LIGHT−OFF recall pp |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B01 | -0.454630 | 0.065244 | 0.456245 | -0.070083 | 0.000000 | 0.000000 |
| B02 | -1.396080 | -0.281294 | 1.429803 | 0.271159 | 0.000000 | 0.000000 |
| B03 | 1.520302 | -1.404521 | -1.500192 | 1.440125 | 0.000000 | 0.000000 |
| B04 | 1.488881 | -0.213556 | -1.462808 | 0.208657 | 0.000000 | 0.000000 |
| B05 | -0.065433 | -0.860537 | 0.060310 | 0.877692 | 0.000000 | 0.000000 |
| B06 | -2.084885 | 1.692015 | 2.134446 | -1.670258 | 0.000000 | 0.000000 |
| B07 | -0.214853 | -0.243400 | 0.217825 | 0.219703 | 0.000000 | 0.000000 |
| B08 | -1.343339 | 0.713682 | 1.377424 | -0.721013 | 0.000000 | 0.000000 |
| B09 | -0.130208 | 0.325945 | 0.137264 | -0.329802 | 0.000000 | 0.000000 |
| B10 | 2.679252 | -1.383601 | -2.622920 | 1.411524 | 0.000000 | 0.000000 |
| B11 | -0.037310 | 0.093310 | 0.022650 | -0.079639 | 0.000000 | 0.000000 |
| B12 | -0.187547 | 0.244269 | 0.181634 | -0.242396 | 0.000000 | 0.000000 |

| Comparison | Metric | Mean | Median | Median absolute paired delta | Sample SD | Min | Max | MAD | CI90 median | Gate |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| OFF_vs_STOCK | qps | -0.018821 | -0.158878 | 0.898984 | 1.352211 | -2.084885 | 2.679252 | 0.740107 | [-0.765443, 0.679336] | PROCEED |
| OFF_vs_STOCK | mean_latency_us | 0.035973 | 0.159449 | 0.916834 | 1.350544 | -2.622920 | 2.134446 | 0.757385 | [-0.662772, 0.779529] | PROCEED |
| OFF_vs_STOCK | recall | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | PROCEED |
| LIGHT_vs_OFF | qps | -0.104370 | -0.074156 | 0.303620 | 0.865077 | -1.404521 | 1.692015 | 0.359263 | [-0.537047, 0.244269] | PROCEED |
| LIGHT_vs_OFF | mean_latency_us | 0.109639 | 0.069287 | 0.300480 | 0.871059 | -1.670258 | 1.440125 | 0.355386 | [-0.242396, 0.543174] | PROCEED |
| LIGHT_vs_OFF | recall | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | [0.000000, 0.000000] | PROCEED |

Performance margins stay 3% OFF/STOCK and 5% LIGHT/OFF for QPS and mean latency separately. PROCEED requires |paired median|≤margin and CI entirely inside the symmetric interval; FAIL requires CI fully outside in one direction; otherwise INCONCLUSIVE. Recall uses paired CI entirely inside ±0.02 pp, fully outside => FAIL, crossing => INCONCLUSIVE. The old global max−min recall span is not a gate. This is a different predeclared paired design, not a changed numerical tolerance.

**Final classification: E0B_PROCEED.** Required traces and all six performance/recall decisions determine this label. No manual promotion or threshold change was made. A missing block/order/config/telemetry/package/provenance mismatch would instead be campaign INVALID/STOP, with no fabricated classification.

## Run-level diagnostics (not gate inputs)

Host telemetry and raw thread logs are diagnostic samples, not independent experiments. The table uses per-run arithmetic sample means; context-switch rates labeled leader come from pidstat’s process/leader row, not an assumed sum over all worker/kernel tasks. Individual thread rates remain in analysis.json and raw pidstat_threads.log. NVMe rows are device-wide and may include other activity. Snapshot temperatures/frequencies do not cover every instant of a run.

| Block/variant | CPU usr/sys/idle % | Process CPU % | Leader voluntary/involuntary /s | NVMe read IOPS | KiB/s | r_await ms | aqu-sz | util % |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| B01/STOCK | 19.54/22.25/58.12 | 797.69 | 0.03/8168.72 | 12719.935 | 50950.151 | 0.060 | 0.765 | 6.635 |
| B01/OFF | 18.83/22.16/59.00 | 797.61 | 0.03/8148.09 | 12656.452 | 50650.280 | 0.060 | 0.741 | 6.143 |
| B01/LIGHT | 19.11/22.27/58.55 | 797.68 | 0.06/8143.26 | 12666.043 | 50687.570 | 0.060 | 0.777 | 5.724 |
| B02/STOCK | 19.12/22.17/58.69 | 797.14 | 0.03/8148.83 | 12735.140 | 50964.387 | 0.060 | 0.744 | 3.549 |
| B02/LIGHT | 19.09/22.17/58.70 | 797.67 | 0.03/8130.73 | 12546.792 | 50210.612 | 0.060 | 0.759 | 6.232 |
| B02/OFF | 19.44/22.20/58.26 | 797.72 | 0.03/8137.50 | 12581.489 | 50350.468 | 0.060 | 0.788 | 5.827 |
| B03/OFF | 18.81/22.19/58.97 | 797.61 | 0.03/8145.89 | 12683.667 | 50758.364 | 0.060 | 0.743 | 4.483 |
| B03/STOCK | 19.14/22.25/58.58 | 797.70 | 0.03/8124.78 | 12493.170 | 49997.404 | 0.060 | 0.756 | 4.521 |
| B03/LIGHT | 19.34/22.18/58.44 | 797.73 | 0.03/8123.93 | 12505.223 | 50047.234 | 0.060 | 0.768 | 4.807 |
| B04/OFF | 19.05/22.23/58.66 | 797.64 | 0.04/8151.44 | 12705.477 | 50845.390 | 0.061 | 0.785 | 5.380 |
| B04/LIGHT | 19.08/22.25/58.61 | 797.72 | 0.03/8133.69 | 12681.591 | 50749.806 | 0.060 | 0.763 | 4.794 |
| B04/STOCK | 19.02/22.16/58.77 | 797.77 | 0.04/8150.36 | 12523.622 | 50128.996 | 0.061 | 0.775 | 5.579 |
| B05/LIGHT | 19.12/22.17/58.68 | 797.78 | 0.03/8121.28 | 12501.915 | 50030.170 | 0.060 | 0.768 | 5.918 |
| B05/STOCK | 18.96/22.24/58.76 | 797.21 | 0.05/8138.04 | 12598.809 | 50418.680 | 0.060 | 0.762 | 5.680 |
| B05/OFF | 18.76/22.16/59.06 | 797.80 | 0.06/8127.97 | 12600.128 | 50423.617 | 0.060 | 0.754 | 5.521 |
| B06/LIGHT | 19.24/22.27/58.45 | 797.29 | 0.03/8133.01 | 12600.181 | 50432.468 | 0.060 | 0.764 | 3.311 |
| B06/OFF | 19.68/22.13/58.15 | 797.71 | 0.04/8110.06 | 12411.031 | 49671.616 | 0.062 | 0.782 | 4.643 |
| B06/STOCK | 18.75/22.14/59.10 | 797.80 | 0.03/8153.34 | 12677.774 | 50734.581 | 0.060 | 0.755 | 5.713 |
| B07/STOCK | 19.14/22.35/58.45 | 797.76 | 0.04/8141.13 | 12633.968 | 50558.796 | 0.060 | 0.768 | 5.484 |
| B07/OFF | 19.29/22.08/58.58 | 797.62 | 0.05/8122.97 | 12600.468 | 50440.596 | 0.060 | 0.776 | 5.418 |
| B07/LIGHT | 19.05/22.13/58.80 | 797.60 | 0.04/8126.58 | 12573.713 | 50318.213 | 0.060 | 0.756 | 4.853 |
| B08/STOCK | 18.94/22.20/58.84 | 797.75 | 0.05/8156.98 | 12733.280 | 50959.398 | 0.060 | 0.741 | 5.302 |
| B08/LIGHT | 18.91/22.16/58.91 | 797.59 | 0.03/8141.29 | 12653.301 | 50636.985 | 0.060 | 0.741 | 5.308 |
| B08/OFF | 19.15/22.22/58.58 | 797.79 | 0.03/8131.56 | 12565.117 | 50283.529 | 0.060 | 0.771 | 4.385 |
| B09/OFF | 18.76/22.21/59.02 | 797.70 | 0.03/8152.03 | 12669.250 | 50699.965 | 0.060 | 0.744 | 5.857 |
| B09/STOCK | 18.76/22.23/58.98 | 797.69 | 0.04/8144.77 | 12686.494 | 50771.782 | 0.060 | 0.743 | 4.591 |
| B09/LIGHT | 18.79/22.20/58.99 | 797.78 | 0.03/8148.23 | 12724.806 | 50966.710 | 0.060 | 0.764 | 6.340 |
| B10/OFF | 18.92/22.24/58.80 | 797.69 | 0.03/8157.52 | 12739.455 | 51348.738 | 0.060 | 0.758 | 6.225 |
| B10/LIGHT | 20.53/22.20/57.19 | 797.70 | 0.03/8125.43 | 12555.851 | 50638.979 | 0.061 | 0.776 | 6.118 |
| B10/STOCK | 19.97/22.23/57.68 | 797.62 | 0.04/8107.03 | 12380.800 | 49570.232 | 0.061 | 0.793 | 4.744 |
| B11/LIGHT | 18.63/22.05/59.31 | 797.57 | 0.03/8153.74 | 12652.741 | 50634.060 | 0.060 | 0.751 | 4.805 |
| B11/STOCK | 18.49/22.07/59.43 | 797.65 | 0.03/8151.22 | 12647.415 | 50615.251 | 0.060 | 0.741 | 5.278 |
| B11/OFF | 18.85/22.22/58.87 | 797.70 | 0.04/8137.14 | 12645.355 | 50604.645 | 0.060 | 0.785 | 6.025 |
| B12/LIGHT | 18.83/22.19/58.95 | 797.59 | 0.03/8143.38 | 12588.778 | 50379.618 | 0.060 | 0.771 | 5.735 |
| B12/OFF | 18.54/22.09/59.36 | 797.73 | 0.03/8149.76 | 12580.923 | 50384.500 | 0.060 | 0.756 | 8.134 |
| B12/STOCK | 18.49/22.07/59.43 | 797.62 | 0.03/8156.31 | 12581.032 | 50346.766 | 0.060 | 0.746 | 4.127 |

| Block/variant | Before/after load1 | Before/after MemAvailable KiB | Before/after package °C | Runtime CPU0 MHz snapshots | Non-iou task affinity CPUs | io_uring fdinfo / snapshots |
| --- | --- | --- | --- | --- | --- | --- |
| B01/STOCK | 0.86/13.67 | 9875252/9947544 | 58.0/62.0 | 4430.9, 4211.9 | 0,12,14,16,18,3,6,9 | 2/2 |
| B01/OFF | 12.58/14.73 | 10003108/10110040 | 60.0/60.0 | 4533.9, 3800.0 | 0,12,14,16,18,3,6,9 | 2/2 |
| B01/LIGHT | 13.63/15.64 | 10115328/9933140 | 58.0/76.0 | 4514.9, 4000.0 | 0,12,14,16,18,3,6,9 | 2/2 |
| B02/STOCK | 12.25/14.91 | 9960380/9883180 | 56.0/65.0 | 4515.3, 4136.6 | 0,12,14,16,18,3,6,9 | 2/2 |
| B02/LIGHT | 13.72/16.27 | 9923188/9865848 | 58.0/63.0 | 4382.6, 3959.3 | 0,12,14,16,18,3,6,9 | 2/2 |
| B02/OFF | 15.13/15.86 | 9898400/9913152 | 60.0/65.0 | 4368.8, 3900.0 | 0,12,14,16,18,3,6,9 | 2/2 |
| B03/OFF | 12.34/14.74 | 9934476/9881472 | 57.0/76.0 | 4370.9, 4000.0 | 0,12,14,16,18,3,6,9 | 2/2 |
| B03/STOCK | 13.56/16.30 | 9913252/9918456 | 59.0/66.0 | 4465.0, 4143.3 | 0,12,14,16,18,3,6,9 | 2/2 |
| B03/LIGHT | 15.07/15.39 | 9899328/9859184 | 58.0/67.0 | 4600.0, 4160.8 | 0,12,14,16,18,3,6,9 | 2/2 |
| B04/OFF | 11.98/14.69 | 9886652/9904848 | 55.0/69.0 | 4339.7, 4100.0 | 0,12,14,16,18,3,6,9 | 2/2 |
| B04/LIGHT | 13.60/15.49 | 9898324/9888784 | 56.0/62.0 | 4415.4, 4148.4 | 0,12,14,16,18,3,6,9 | 2/2 |
| B04/STOCK | 14.33/16.79 | 9891640/9842444 | 59.0/62.0 | 2867.5, 4172.8 | 0,12,14,16,18,3,6,9 | 2/2 |
| B05/LIGHT | 13.22/14.98 | 9835448/9827028 | 58.0/69.0 | 4305.4, 4100.0 | 0,12,14,16,18,3,6,9 | 2/2 |
| B05/STOCK | 13.78/15.10 | 9831360/9768708 | 59.0/59.0 | 4347.9, 4100.0 | 0,12,14,16,18,3,6,9 | 2/2 |
| B05/OFF | 13.89/16.56 | 9795408/9808844 | 61.0/70.0 | 4434.7, 4176.9 | 0,12,14,16,18,3,6,9 | 2/2 |
| B06/LIGHT | 13.12/16.57 | 9773360/9884064 | 57.0/73.0 | 4397.8, 4100.0 | 0,12,14,16,18,3,6,9 | 2/2 |
| B06/OFF | 15.97/16.67 | 9886840/9851940 | 59.0/67.0 | 4360.2, 4000.0 | 0,12,14,16,18,3,6,9 | 2/2 |
| B06/STOCK | 15.42/16.53 | 9879236/9810472 | 55.0/64.0 | 4394.9, 4167.1 | 0,12,14,16,18,3,6,9 | 2/2 |
| B07/STOCK | 13.02/16.39 | 9887316/9899472 | 55.0/61.0 | 4540.2, 4190.5 | 0,12,14,16,18,3,6,9 | 2/2 |
| B07/OFF | 15.08/15.47 | 9903016/9752844 | 56.0/83.0 | 4436.6, 4261.4 | 0,12,14,16,18,3,6,9 | 2/2 |
| B07/LIGHT | 14.23/15.16 | 9776660/9765320 | 60.0/65.0 | 4100.0, 4182.9 | 0,12,14,16,18,3,6,9 | 2/2 |
| B08/STOCK | 12.08/15.98 | 9781664/9778864 | 54.0/65.0 | 4401.2, 4179.1 | 0,12,14,16,18,3,6,9 | 2/2 |
| B08/LIGHT | 14.78/16.41 | 9778680/9776924 | 59.0/68.0 | 4411.5, 4108.8 | 0,12,14,16,18,3,6,9 | 2/2 |
| B08/OFF | 15.10/15.92 | 9773868/9786008 | 59.0/66.0 | 4341.5, 3999.9 | 0,12,14,16,18,3,6,9 | 2/2 |
| B09/OFF | 12.53/14.66 | 9814324/9782844 | 55.0/61.0 | 4310.5, 4100.0 | 0,12,14,16,18,3,6,9 | 2/2 |
| B09/STOCK | 13.49/15.15 | 9796408/9835656 | 57.0/64.0 | 4492.5, 4105.8 | 0,12,14,16,18,3,6,9 | 2/2 |
| B09/LIGHT | 13.94/16.68 | 9854076/9952268 | 58.0/69.0 | 4505.6, 4100.0 | 0,12,14,16,18,3,6,9 | 2/2 |
| B10/OFF | 13.06/16.15 | 9989688/9839236 | 54.0/66.0 | 4426.1, 4115.3 | 0,12,14,16,18,3,6,9 | 2/2 |
| B10/LIGHT | 14.86/15.51 | 9864820/12266588 | 57.0/63.0 | 4441.8, 4100.0 | 0,12,14,16,18,3,6,9 | 2/2 |
| B10/STOCK | 14.43/16.80 | 12262456/12315736 | 59.0/66.0 | 3032.5, 4100.0 | 0,12,14,16,18,3,6,9 | 2/2 |
| B11/LIGHT | 13.21/16.26 | 12344116/12271788 | 55.0/69.0 | 4482.9, 4184.5 | 0,12,14,16,18,3,6,9 | 2/2 |
| B11/STOCK | 15.04/15.48 | 12302208/12289212 | 60.0/64.0 | 4483.5, 4100.0 | 0,12,14,16,18,3,6,9 | 2/2 |
| B11/OFF | 14.24/15.24 | 12369108/12318816 | 60.0/63.0 | 4599.2, 4106.2 | 0,12,14,16,18,3,6,9 | 2/2 |
| B12/LIGHT | 11.86/15.77 | 12345860/12297320 | 54.0/66.0 | 4501.4, 4135.1 | 0,12,14,16,18,3,6,9 | 2/2 |
| B12/OFF | 14.50/16.26 | 12313556/12288372 | 56.0/64.0 | 4324.1, 4000.0 | 0,12,14,16,18,3,6,9 | 2/2 |
| B12/STOCK | 14.96/15.57 | 12343948/12345640 | 58.0/72.0 | 4599.1, 4166.8 | 0,12,14,16,18,3,6,9 | 2/2 |

Group range/median is descriptive only, not an E0b gate. Issue #8 STOCK reference spreads were 3.3323% QPS and 3.3908% mean latency; the new placement and uniform observers differ, so these are not controlled causal before/after estimates.

| Variant | QPS range/median % | Mean-latency range/median % |
| --- | ---: | ---: | ---: |
| STOCK | 3.061701 | 3.106473 |
| OFF | 2.335575 | 2.358133 |
| LIGHT | 1.628604 | 1.643583 |

Observed 72 runtime snapshots: iou-sqp count range 8–8 per snapshot; iou-wrk count range 0–0. These are observed tasks at two instants per run, not a complete kernel-thread lifetime census. No task-count assumption is inferred from source.

Recorded settings: governors ['powersave']; EPP ['balance_performance']; NVMe scheduler ['[none] mq-deadline']. Before/after swap-used range 519468–563840 KiB. Power limits, queue attributes and all policies' current/max frequencies remain in raw host snapshots; settings were observed, not tuned.

The largest OFF/STOCK QPS paired delta is B10 (+2.679252%): OFF 107.69 QPS, STOCK 104.88 QPS. MemAvailable rises from roughly 9.4 to 11.7 GiB during B10 LIGHT and stays higher afterward; system usr/idle samples also change. The B07 OFF after-snapshot reaches 83°C. These observations are retained, including the slower B10 STOCK. Snapshots do not identify what freed memory or establish that these host changes caused a performance difference.

## Interpretation and unresolved causes

**Measured fact:** runtime task snapshots show search tasks and their named iou-sqp helpers can have the same singleton CPU affinity under spread/threads. This is runtime evidence, not an inference that one SQPOLL thread exists per worker from source alone. Exact task identities/counts, CPU usage, allowed masks, last CPU and fdinfo are in the preserved snapshots. iou-wrk absence in a snapshot is not proof no worker ever ran.

**Statistical summary:** the paired CI decisions apply only to this frozen placement, hybrid core mix, uniform telemetry/observer policy and 12 blocks. Slow runs are retained. See all per-run QPS/latency/P99/I/O/recall below; no result is silently excluded.

**Interpretation:** host scheduling/resource sharing is consistent with observed co-affinity and context-switch activity. Issue #8 used unset placement and unmatched telemetry, so this is not a controlled placement-only comparison with that campaign. Frequency/thermal/load snapshots and cyclic orders help characterize variability, but cannot assign the old ~3.3% group spread to a single cause. A reproducible paired effect here would not prove equivalence in an unbound or differently placed regime.

**Unknown cause:** independent contributions of placement, frequency/thermal drift, background load, kernel scheduling and completion-observation delay remain unresolved. No hardware-I/O latency or dependency-starvation attribution follows; IO_SUBMIT/CQE hooks and their userspace-observed interval remain unchanged. No D1/D4/D6 solution or hypothesis conclusion.

No G0 Stage B/C was resumed, regardless of classification. Any later resume requires a separate issue and explicit protocol, with the measured placement confound considered before measurement.

## Validation and immutable run inventory

151 research Python tests pass (115 existing + 5 host-telemetry tests + 31 E0b tests); git diff --check passes. Tests cover all permutations, completeness/order, paired math/absolute median/MAD, deterministic CI, all gates, paired recall, trace invalidity, matched telemetry, packages/provenance/placement and thread diagnostics. Synthetic files suffice. Analyzer reads local finalized evidence only. Separate readback verifies all 36 MLflow mirrors FINISHED with matching package digests, harness/subject commits, T/W/L/K, trace mode, status and validity; they do not supply scientific metrics.

All 24 required instrumented traces have trace_valid=true, with zero dropped events, ordering violations, negative hidden counts, unmatched causal events, table overflows and outstanding correlations. OFF validity checks its no-op protocol; LIGHT checks aggregate query counters, not per-event DETAIL invariants. STOCK has trace_valid=null. No DETAIL campaign was executed.

`--host-telemetry`/`--no-host-telemetry` decouple collectors from OFF/LIGHT/DETAIL. Omitted flags retain historical OFF=off and LIGHT/DETAIL=on behavior. Optional additive schema-v2 fields record effective request and CLI override; historical finalized manifests and run-index schema are not reinterpreted or rewritten. OFF+telemetry emits system metrics/raw logs without ANN events or stub query metrics.

| Block/variant | QPS | Mean latency us | P99 us | Recall % | Mean IO/query | Run ID | MLflow ID |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| B01/STOCK | 107.78 | 74172.8 | 121984 | 99.09 | 118.48 | `P0_sift10m_T8_W32_OFF_R001_20261008T152227003516Z_98654020ef014d2fb4b1b238472ccceb` | `c164173fba004d35a5057c71202f7253` |
| B01/OFF | 107.29 | 74511.2 | 121986 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R001_20261008T152407509607Z_8dbe4d33fdac48cdb4988cb968641b20` | `df950b8cc837465a9e24df0714e33908` |
| B01/LIGHT | 107.36 | 74459 | 123197 | 99.09 | 118.49 | `P0_sift10m_T8_W32_LIGHT_R001_20261008T152548503845Z_9a16c4f2b5ed4228a93068b7357403a5` | `84527a0a8a1c4c008898bd59085225df` |
| B02/STOCK | 108.16 | 73910.2 | 121986 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R002_20261008T152739478920Z_5e4aef1c3c30434a9c7bfb4ce2cb0c57` | `d54aa1d88a944834beb732424e6f69a5` |
| B02/LIGHT | 106.35 | 75170.2 | 123978 | 99.09 | 118.49 | `P0_sift10m_T8_W32_LIGHT_R002_20261008T152919658547Z_edbf46b1869f40fab3a09165cb240c29` | `87ef6d972e7c4a49b8270c0d81eb02bd` |
| B02/OFF | 106.65 | 74967 | 123137 | 99.09 | 118.48 | `P0_sift10m_T8_W32_OFF_R002_20261008T153101580999Z_92f1b7812dd94db580d98c9ffcfa9fb0` | `673a8c2779c843bd99aa43a3bdb0013e` |
| B03/OFF | 107.51 | 74352.6 | 123987 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R003_20261008T153253083987Z_a9a2a9b3ecb24dc8a36b18da2273b28a` | `c9069603ace84292b3fc77890198770e` |
| B03/STOCK | 105.9 | 75485 | 121976 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R003_20261008T153433831065Z_890af55864ac44bf816d18bcb1a5ad14` | `99e11a78ef664a25a356a1454f063e34` |
| B03/LIGHT | 106 | 75423.3 | 122981 | 99.09 | 118.49 | `P0_sift10m_T8_W32_LIGHT_R003_20261008T153615984027Z_178f9206cf204d029fe785458d7a8d71` | `7a10360df14a4747919a422237111557` |
| B04/OFF | 107.7 | 74231.9 | 120968 | 99.09 | 118.48 | `P0_sift10m_T8_W32_OFF_R004_20261008T153808202267Z_699728975cb54c8baf1196b308bb3654` | `4e8b1e57d08e4dcea83c1be298784d54` |
| B04/LIGHT | 107.47 | 74386.8 | 122966 | 99.09 | 118.5 | `P0_sift10m_T8_W32_LIGHT_R004_20261008T153948789139Z_166a82b15fe748218001880d63913a23` | `0e4a4c6a52e4482a97bccdc59af8f45f` |
| B04/STOCK | 106.12 | 75333.9 | 120970 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R004_20261008T154129648972Z_50611d6de8684001bb662969642870f0` | `c8e4acba098443c28f06413cfe25d09e` |
| B05/LIGHT | 105.99 | 75432 | 121987 | 99.09 | 118.5 | `P0_sift10m_T8_W32_LIGHT_R005_20261008T154321634253Z_e9b2c0f5f58945dcb7e4dc93bffe423d` | `b1fe3fd7a14643a1a73b033e4d7a21af` |
| B05/STOCK | 106.98 | 74730.6 | 121973 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R005_20261008T154503779596Z_1b5d32cf78184751b8e87542991ea24d` | `1ceb064f62ea479882d4e43ea140d67d` |
| B05/OFF | 106.91 | 74775.7 | 121987 | 99.09 | 118.5 | `P0_sift10m_T8_W32_OFF_R005_20261008T154645026265Z_3c25d14b489f4a468e158694fac53ca7` | `21460de0ba0742b18b03cea53365f2ca` |
| B06/LIGHT | 106.98 | 74720.8 | 122171 | 99.09 | 118.49 | `P0_sift10m_T8_W32_LIGHT_R006_20261008T154836303638Z_0dbdc8b83474416bb8b13036362db78c` | `036389b37f0544c48ff642ca5740be7a` |
| B06/OFF | 105.2 | 75990.1 | 122002 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R006_20261008T155017667904Z_7d29e41ebdc54aa8b18c8effd7028ef2` | `fa058af34e9a46f9bb95214ea1332c08` |
| B06/STOCK | 107.44 | 74402 | 122988 | 99.09 | 118.48 | `P0_sift10m_T8_W32_OFF_R006_20261008T155200472625Z_f462a7dbd54d40dcb6fd125979770308` | `68d7616bd12546a8b3f0bfa64d75483c` |
| B07/STOCK | 107.05 | 74679.4 | 121963 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R007_20261008T155351214706Z_80860499c1db48a3830c1c7be42e637b` | `ad5b452e1d544a25b3735fd1f77c2c06` |
| B07/OFF | 106.82 | 74842 | 125957 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R007_20261008T155532309267Z_1b4f5cfbb7694b80b780a6d481de82b2` | `4a0cf2c546e8417cb109b6c175f0820c` |
| B07/LIGHT | 106.56 | 75006.4 | 124640 | 99.09 | 118.49 | `P0_sift10m_T8_W32_LIGHT_R007_20261008T155713712803Z_98a0586d416d459b8100950354ce1cb7` | `62809a7674d048e1ae9e2b19b4d7c01a` |
| B08/STOCK | 107.94 | 74054.9 | 120981 | 99.09 | 118.48 | `P0_sift10m_T8_W32_OFF_R008_20261008T155905483857Z_ef22477868f74edcb3c7d39566d97e13` | `cf686130239d41adbd7984b579f362ab` |
| B08/LIGHT | 107.25 | 74533.7 | 120989 | 99.09 | 118.48 | `P0_sift10m_T8_W32_LIGHT_R008_20261008T160045829787Z_cb368655d6a04d7ea3845cc27d36ce16` | `9f7281f94cdd4d6d8a48c0baed8c0051` |
| B08/OFF | 106.49 | 75075 | 123239 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R008_20261008T160226898220Z_a99f07a273b2463fa52b2744ec101a82` | `a27a7bde196943e2a4b9075c94dd3475` |
| B09/OFF | 107.38 | 74447.8 | 121987 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R009_20261008T160418539017Z_cac7f947d85e47c593b8929288758b1a` | `5d6888ef3958434dab3c1b16a492b7ab` |
| B09/STOCK | 107.52 | 74345.8 | 121989 | 99.09 | 118.48 | `P0_sift10m_T8_W32_OFF_R009_20261008T160559441164Z_0a4cbcd6cf09469aad8ea8d6243c43cb` | `8c1d791a7f2c454b8ad43c0c3fd24c92` |
| B09/LIGHT | 107.73 | 74202.3 | 121984 | 99.09 | 118.49 | `P0_sift10m_T8_W32_LIGHT_R009_20261008T160740164318Z_1c0e9bef84b448fa872cbfd4951a6f75` | `f160defd177748ab9100996f3feb50d5` |
| B10/OFF | 107.69 | 74229 | 121986 | 99.09 | 118.48 | `P0_sift10m_T8_W32_OFF_R010_20261008T160930820578Z_ecc9a6084353429eb99700f691fe2bfa` | `20668b25403e4205ac548038d2f11ca5` |
| B10/LIGHT | 106.2 | 75276.7 | 123977 | 99.09 | 118.48 | `P0_sift10m_T8_W32_LIGHT_R010_20261008T161111422206Z_0c685f2eced543ffb6def637b2954023` | `c5eaa6c0aea34911aff5087ed5c9808c` |
| B10/STOCK | 104.88 | 76228.4 | 122693 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R010_20261008T161253474335Z_eb60c3ee3582487abf3dd3a500604168` | `d3d0589c51244ae682dd367f9571d6e3` |
| B11/LIGHT | 107.27 | 74527.1 | 122975 | 99.09 | 118.49 | `P0_sift10m_T8_W32_LIGHT_R011_20261008T161446561068Z_787f03e82e6c4c94b795045a1e1102f6` | `a4375b5d56bd45cba0896f1f29c788e9` |
| B11/STOCK | 107.21 | 74569.7 | 123310 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R011_20261008T161627638210Z_cf0fd1b1d60b4c5898706462ce3da3b6` | `1526c48381374702a49537edbe8b21ac` |
| B11/OFF | 107.17 | 74586.6 | 125951 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R011_20261008T161808633968Z_62d8191a0306410fb5c56397f80b2836` | `ded923297f34441381da2684a6bd410d` |
| B12/LIGHT | 106.7 | 74918.1 | 123889 | 99.09 | 118.5 | `P0_sift10m_T8_W32_LIGHT_R012_20261008T161959715735Z_64b3027727f24c88a551c508b2d42352` | `292de2ad473c4fc095f9082f9d12e0d8` |
| B12/OFF | 106.44 | 75100.1 | 123300 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R012_20261008T162141246883Z_1ce775754284496eb9cba119eb66d11a` | `8b10a7ac4c2742ebbf59bb65728644a4` |
| B12/STOCK | 106.64 | 74964 | 123002 | 99.09 | 118.49 | `P0_sift10m_T8_W32_OFF_R012_20261008T162322929707Z_5d892ee0e64e40f68acd8fcbeaf95c5a` | `60a136e4646641dfa29193fd10147bab` |

Run artifacts: `~/ann-research/research-v3/runs/<run_id>/`. Exact per-run harness command/environment/argv and runtime observers: campaign `executions/Bxx_VARIANT/`. Frozen execution script and host snapshot source hashes are in PLAN; the exact sources remain alongside local campaign evidence. Raw events, telemetry, MLflow database, data/index and build products remain external/ignored.

```bash
.venv-research/bin/python -m unittest discover -s tests/research -v
git diff --check
.venv-research/bin/python tools/research/analyze_e0b.py --campaign ~/ann-research/research-v3/campaigns/E0B_SIFT10M_20261008T151707400337Z --output /new/analysis-directory
```

ANN source unchanged; FIFO unchanged; width policy unchanged; io_uring unchanged; no D1/D4 implementation; G0 Stage B/C not resumed; SIFT100M untouched; main untouched; no large/generated artifacts committed; no novelty claim.
