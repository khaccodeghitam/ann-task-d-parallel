# G0-C2 SIFT10M D6 causal diagnostics

**G0C2_COMPLETE; sampled D6_INCONCLUSIVE; system-wide D6=INCONCLUSIVE.** Fifteen replicated DETAIL runs have valid physical/cache/FIFO lifecycle evidence, exact16-query membership, 10,000 query counters per run, zero drops/overflows/unmatched/outstanding/order/negative-hidden failures, and FINISHED local MLflow mirrors. The operational ≥2× HOL elevation criterion is met in zero of three C/B and zero of three D/B pairs. Large absolute HOL or hidden time alone does not satisfy MATERIAL and does not prove throughput causation. D1 observability remains NO; D4 selector gate NOT TESTED.

## Frozen identities and execution

Campaign: `G0C2_SIFT10M_20261009T090432438598Z`. Local authoritative evidence: `/home/irthn/ann-research/research-v3/campaigns/G0C2_SIFT10M_20261009T090432438598Z`. Frozen PLAN SHA256: `cfec808b97757027f7c8155e10780e84e4bcb77c1d7bbaa4708c58a6e05bc06d`. The tracked plan/amendment copies under `docs/research/plans/` are byte-identical to the external originals. Issue18 and all comments were read before changes/measurement (no comments).

Main/research base `f2f07fb32c2b5f31bf33e457162721de4e645f45`; clean measurement harness `c2fafdd84cee70ee350cebd06653c7138d350006` on `research/g0c2-sift10m-detail-d6`. Final analysis/report changes are versioned in this PR; the measurement executable/harness identity in existing manifests is preserved. Golden `b9ec4ba86ff5d70bec277984777197f28dc2cf42` / SHA256 `a02ce69d1467727344c8620a254b4cba51d12616d3da171ef7c1a6668a9e8bc5`; instrumented subject `35222026893ff7d1b45586fcdd8165a5ce592cd3` / binary SHA256 `f5795e43c3be1f2515bd37e21ad1fbab45b2849c859724629a8c6edea5e418dd`. Both subjects stayed clean, read-only; neither binary was rebuilt.

INPUT_PACKAGE `47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3`; INDEX_PACKAGE `8955f8bca0c8ebb5afbd2a69e9760fc829d22ba76a4ef7b482339e88b2489595`. Existing uint8 BigANN first10M/D128, 10K canonical queries, Vamana R64/Lbuild100/PQ32. `pipeann-b9ec4ba`, pq/L2/mode2, K10/Lsearch100/mem_L0. A=T1/W32, B=T8/W32, C=T8/W64, D=T16/W32, E=T16/W16. R1 ABCDE; R2 BCDEA; R3 CDEAB. Native/unbound: OMP_NUM_THREADS=T, MKL_NUM_THREADS=8, OMP_DYNAMIC=FALSE; OMP_PROC_BIND/OMP_PLACES/GOMP_CPU_AFFINITY unset; LC_ALL=C/S_TIME_FORMAT=ISO. No affinity/governor/EPP/NVMe/power tuning.

DETAIL/PANTRC02, explicit_qids, capacity65536/worker, cumulative over benchmark (~17MiB/worker; ~272MiB atT16). Exact IDs: `1000,1533,2066,2600,3133,3666,4200,4733,5266,5800,6333,6866,7400,7933,8466,9000`. Sampling SHA256 `bb12f3bd4c1a370786765e1ebe6f5ef9883b6deab2d4437392090e3c3556deda`. Uniform mpstat/pidstat/iostat1s, external thread pidstat, host-before/after, runtime task/affinity/SQPOLL/fdinfo snapshots at0.35/1.2/2.5s after benchmark child discovery. Fixed5s pause after finalized validation/mirror except final; no exclusions or retries.

**Technical deviation — AMENDMENT_001:** A/R1 was already ANN/trace/checker/MLflow valid when the new analyzer incorrectly required OMP_DYNAMIC/GOMP_CPU_AFFINITY in the narrower historical runner manifest. This caused an execution stop, not an actual environment/trace failure. All three independently recorded /proc environment snapshots and exact command exports/unsets prove the frozen native environment. The dated/hashed amendment was frozen before continuation; a read-only compatibility adapter validated missing manifest keys against those independent observations, preserved A/R1, and resumed the remaining14 in the original order. PLAN, benchmark configuration, thresholds, subject, binary and measurement harness commit never changed. There was an additional technical investigation gap after A/R1; its mandatory5s pause began after delayed validation. No run was repeated or discarded. The final analyzer now directly supports narrower manifests without fabricating fields and has regression tests; existing artifacts are unchanged. This gap is an execution limitation, transparently retained rather than treated as a scientific exclusion.

Exact reproducible harness command (set T/W/repetition for each frozen position):

```sh
unset OMP_PROC_BIND OMP_PLACES GOMP_CPU_AFFINITY OMP_DISPLAY_AFFINITY OMP_DISPLAY_ENV
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OMP_DYNAMIC=FALSE LC_ALL=C S_TIME_FORMAT=ISO
.venv-research/bin/python tools/research/run_ann_experiment.py \
  --benchmark-profile pipeann-b9ec4ba --subject-repo ~/ann-research/PipeANN-p0 \
  --executable ~/ann-research/PipeANN-p0/build/tests/search_disk_index \
  --dataset-id sift10m --data-type uint8 \
  --dataset-path ~/ann-research/data/bigann/sift10m/canonical/base_10m.bbin \
  --query ~/ann-research/data/bigann/sift10m/canonical/query.bbin \
  --ground-truth ~/ann-research/data/bigann/sift10m/canonical/gt_10m.bin \
  --index-id sift10m-R64-L100-PQ32 --index-prefix ~/ann-research/indexes/sift10m/sift10m \
  --input-package-manifest ~/ann-research/data/bigann/sift10m/manifests/INPUT_PACKAGE.json \
  --index-package-manifest ~/ann-research/indexes/sift10m/INDEX_PACKAGE.json \
  --threads 8 --wcap 32 --k 10 --l-search 100 --mem-l 0 \
  --neighbor-type pq --distance-metric l2 --search-mode 2 \
  --causal-trace --trace-mode DETAIL --trace-detail-first-n 16 \
  --trace-sample-policy explicit_qids \
  --trace-sample-qids 1000,1533,2066,2600,3133,3666,4200,4733,5266,5800,6333,6866,7400,7933,8466,9000 \
  --trace-event-capacity 65536 --host-telemetry --telemetry-interval 1 \
  --mlflow --evidence-root ~/ann-research/research-v3 --timeout 300 --repetition 1
```

## Integrity and local evidence

Full-component audits bracket all measurements; stdout/stderr, exact argv, UTC times and duration retained in campaign. Any real integrity failure would have stopped the campaign without repair.

| Audit | Start UTC | End UTC | Duration s | Exit |
| --- | --- | --- | --- | --- |
| pre_input | 2026-10-09T09:04:46.823318+00:00 | 2026-10-09T09:04:47.979322+00:00 | 1.156 | 0 |
| pre_index | 2026-10-09T09:04:47.979589+00:00 | 2026-10-09T09:04:51.924849+00:00 | 3.945 | 0 |
| post_input | 2026-10-09T09:10:34.799491+00:00 | 2026-10-09T09:10:35.795112+00:00 | 0.996 | 0 |
| post_index | 2026-10-09T09:10:35.795345+00:00 | 2026-10-09T09:10:39.463745+00:00 | 3.668 | 0 |

Audit commands (run before and after):

```sh
.venv-research/bin/python tools/research/package_manifest.py verify ~/ann-research/data/bigann/sift10m/manifests/INPUT_PACKAGE.json --full-components
.venv-research/bin/python tools/research/package_manifest.py verify ~/ann-research/indexes/sift10m/INDEX_PACKAGE.json --full-components
```

All15 per-run SHA256SUMS plus external execution checksums verified; 240 run files; 2682 prior run files and all historical campaign files byte-identical. Golden/subject commit, cleanliness, binary SHA/size/mtime unchanged. Frozen execution code/PLAN and measurement harness files were verified at post-audit, before the final analyzer compatibility correction. Historical E0b/E0c/G0-B/G0-C1 analyzer replays produce exact serialized JSON-equivalent results; old tools/exporter/checker/schemas remain unchanged.

Run path is `~/ann-research/research-v3/runs/<run_id>/`; observer path is `<campaign>/executions/B<round>_<config>/`. Each stores manifest/summary/command/stdout, raw ANN trace, events.jsonl, query/system CSVs, trace_health/check, raw telemetry and SHA256SUMS. Independent checker stdout, runtime/host snapshots and mirror readback are outside run folders and separately checksummed. MLflow is only a local mirror; no raw events/telemetry uploaded.

| Config/rep | Run ID | MLflow ID | Events | Physical sampled requests | Query rows |
| --- | --- | --- | --- | --- | --- |
| A/R1 | `P0_sift10m_T1_W32_DETAIL_R001_20261009T090503633488Z_438f1b4febad480ca4ffe7a40d079f13` | `0ece3c1546864144bd2b072903f61342` | 10135 | 1935 | 10000 |
| B/R1 | `P0_sift10m_T8_W32_DETAIL_R001_20261009T090705519648Z_ec817782440e43ac806bef22e910f599` | `acb18d65a53a400c9ab19eeb8b6f1d9b` | 10049 | 1926 | 10000 |
| C/R1 | `P0_sift10m_T8_W64_DETAIL_R001_20261009T090718638920Z_70bcca4c9bb24406b85ea8ce89b47994` | `a7fc222ca86e45f58e540fa331082377` | 10095 | 1935 | 10000 |
| D/R1 | `P0_sift10m_T16_W32_DETAIL_R001_20261009T090731767228Z_7261f62f236141ca95c96e0ec0136fee` | `77d7457f0eee4e77a28a0dc89ed8e6a5` | 10033 | 1922 | 10000 |
| E/R1 | `P0_sift10m_T16_W16_DETAIL_R001_20261009T090745219976Z_5e1f2dfac73743a1a984257bb7570f53` | `8cb0fed7a986473fadf04e11f226ac19` | 9751 | 1907 | 10000 |
| B/R2 | `P0_sift10m_T8_W32_DETAIL_R002_20261009T090758807894Z_173653e489504dd18a3793b2c6467b39` | `e370c42e40c1406480652081b35d9a83` | 10032 | 1920 | 10000 |
| C/R2 | `P0_sift10m_T8_W64_DETAIL_R002_20261009T090811753452Z_9558dd9363b14356a8eec25f3eba65e2` | `27ce1d7e8a34410fb8ee523b213ed75c` | 10035 | 1924 | 10000 |
| D/R2 | `P0_sift10m_T16_W32_DETAIL_R002_20261009T090824680245Z_ec1828e5847b461994c840e09dfa7b11` | `52c256dac75045d9a334ae54b4b6eb97` | 10038 | 1922 | 10000 |
| E/R2 | `P0_sift10m_T16_W16_DETAIL_R002_20261009T090838270423Z_cf1cf85115b044feb826c9c94400a48f` | `2314a350f85b462da7d05e59a81c4f42` | 9728 | 1902 | 10000 |
| A/R2 | `P0_sift10m_T1_W32_DETAIL_R002_20261009T090851915127Z_26e438181cf842babec2fbbc54cdf19d` | `079b0c193a3b4a0d920820316be358e0` | 10147 | 1937 | 10000 |
| C/R3 | `P0_sift10m_T8_W64_DETAIL_R003_20261009T090913467983Z_b8e232939106482d80394119803dee62` | `45db2acaa818487bb902e7e5ed3bf82e` | 10083 | 1928 | 10000 |
| D/R3 | `P0_sift10m_T16_W32_DETAIL_R003_20261009T090926554555Z_c464404c71f841da9867fda7d26a71e4` | `05f6adcb59dd440896a1009d0629c16d` | 10027 | 1922 | 10000 |
| E/R3 | `P0_sift10m_T16_W16_DETAIL_R003_20261009T090940260645Z_c0ea5e3b7ab14326968122c1b077c908` | `bc7082bf07fb41d9b4a11d7c2296cdfb` | 9783 | 1913 | 10000 |
| A/R3 | `P0_sift10m_T1_W32_DETAIL_R003_20261009T090953949982Z_0f4a95e6e75746a6b48ecf564e1f6aa2` | `79b49f9bf1c94e6ebfaf311c1149b7ae` | 10138 | 1936 | 10000 |
| B/R3 | `P0_sift10m_T8_W32_DETAIL_R003_20261009T091015779549Z_083b9c9a7165498d9f926e5c74e43fbb` | `fd0edcbbca524dc499803038870b6eb6` | 10018 | 1923 | 10000 |


## Estimands and reconstruction

**DERIVED METRIC:** request observed_io=(CQE_seen-submit)/1000µs; HOL=(publish-CQE_seen)/1000µs. IO_SUBMIT remains after SQE preparation immediately before io_uring_submit; CQE_SEEN is userspace poll processing. Observed I/O includes scheduling/poll delay and is not hardware device latency. HOL is application publication delay and is not necessarily query critical-path delay. No expansion-to-request identity is invented.

Sort each query independently by timestamp, semantic rank, stock old_width chain for equal-time WIDTH_CHANGE, then request_seq/node/worker/TID/stable fields. Equal-time intervals integrate post-tie state; timestamp resolution cannot distinguish zero-duration transient maxima. Validate physical and cache FIFO lifecycle independently. Physical device_outstanding=submitted-CQE; hidden=CQE-published; total_unpublished=submitted-published, cache-only excluded. Integrate QUERY_START..QUERY_END. Width is unknown before WIDTH_INIT: meanW divides only initialized duration; cap/above32/bucket fractions divide full query duration, with unknown fraction explicit. Every request quantile is descriptive within its query/run; the top-level repetition is RUN, not request/query. Quantiles use linear p*(n-1) interpolation. No bootstrap or pseudoreplicated p-values.

## Replicated run-level causal measurements

HOL/observed tuples = p50/p95/p99/max µs across physical requests within a run (nonindependent descriptive values). Hidden fraction for the gate is the median of the16 individual query fractions, not a duration-weighted pooled fraction. The latter is separately reported. Zero-observed request denominators are counted; run ratios require positive observed p95.

| Run | HOL tuple µs | Observed tuple µs | HOL p95/IO p95 | Median query hidden>0 % | Duration-weighted hidden>0 % | TW mean hidden/outstanding/unpublished | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A/R1 | 8.06/80.54/116.66/195.25 | 65.72/117.78/161.96/244.15 | 0.684 | 44.89 | 44.51 | 2.080/7.320/9.399 | 0 |
| B/R1 | 45.72/242.16/396.46/555.60 | 104.59/262.04/376.87/683.91 | 0.924 | 63.02 | 63.10 | 3.223/5.583/8.806 | 0 |
| C/R1 | 55.78/234.53/322.19/539.13 | 100.04/274.02/369.95/620.27 | 0.856 | 64.31 | 64.13 | 3.426/5.538/8.964 | 0 |
| D/R1 | 19.39/210.69/998.91/6116.38 | 102.05/997.10/6101.65/6208.27 | 0.211 | 59.13 | 51.40 | 1.813/7.822/9.635 | 0 |
| E/R1 | 25.14/181.76/10044.62/12193.59 | 85.34/300.41/9049.72/12580.31 | 0.605 | 60.22 | 67.16 | 4.056/5.688/9.744 | 0 |
| B/R2 | 47.14/253.76/338.98/446.43 | 107.04/276.41/373.97/561.72 | 0.918 | 64.76 | 64.14 | 3.245/5.624/8.869 | 0 |
| C/R2 | 53.17/240.67/329.44/392.98 | 99.26/272.94/360.79/475.14 | 0.882 | 64.36 | 64.10 | 3.451/5.600/9.051 | 0 |
| D/R2 | 26.07/175.97/3824.30/6134.61 | 92.39/691.07/6033.84/8217.93 | 0.255 | 53.96 | 47.90 | 2.362/5.770/8.131 | 0 |
| E/R2 | 11.05/173.35/3031.93/8093.83 | 98.85/5970.92/5996.93/8999.94 | 0.029 | 60.62 | 25.41 | 1.054/5.890/6.944 | 0 |
| A/R2 | 7.04/78.93/100.45/165.68 | 66.13/118.86/161.54/250.16 | 0.664 | 43.56 | 43.24 | 2.010/7.357/9.367 | 0 |
| C/R3 | 39.86/243.15/373.28/513.58 | 103.37/260.78/374.48/608.58 | 0.932 | 63.35 | 63.19 | 3.281/5.806/9.087 | 0 |
| D/R3 | 20.00/165.12/6028.37/8145.27 | 90.32/393.87/6173.55/8214.66 | 0.419 | 57.33 | 61.71 | 2.818/6.686/9.504 | 0 |
| E/R3 | 28.17/211.94/3038.72/8045.24 | 84.98/325.82/6102.26/9026.39 | 0.650 | 64.96 | 52.74 | 1.734/4.788/6.522 | 0 |
| A/R3 | 7.62/80.33/110.30/182.62 | 65.67/119.42/162.27/233.54 | 0.673 | 43.60 | 44.51 | 2.062/7.316/9.378 | 0 |
| B/R3 | 54.00/279.44/451.01/1079.81 | 106.01/317.75/528.28/1214.81 | 0.879 | 64.18 | 65.98 | 3.410/5.548/8.959 | 0 |


Per configuration: three independent run p95s, with mean/median/min/max/sample SD (n−1). These summarize run-level variability, not an equivalence or overhead proof.

| Config | HOL p95 all3 µs | HOL mean/median/min/max/SD | IO p95 all3 µs | IO mean/median/min/max/SD |
| --- | --- | --- | --- | --- |
| A | 80.537, 78.926, 80.331 | 79.931/80.331/78.926/80.537/0.877 | 117.783, 118.857, 119.423 | 118.688/118.857/117.783/119.423/0.833 |
| B | 242.165, 253.759, 279.438 | 258.454/253.759/242.165/279.438/19.075 | 262.041, 276.410, 317.751 | 285.401/276.410/262.041/317.751/28.923 |
| C | 234.534, 240.666, 243.146 | 239.449/240.666/234.534/243.146/4.433 | 274.016, 272.942, 260.779 | 269.246/272.942/260.779/274.016/7.352 |
| D | 210.691, 175.969, 165.122 | 183.927/175.969/165.122/210.691/23.804 | 997.096, 691.069, 393.868 | 694.011/691.069/393.868/997.096/301.624 |
| E | 181.755, 173.348, 211.943 | 189.015/181.755/173.348/211.943/20.296 | 300.407, 5970.917, 325.823 | 2199.049/325.823/300.407/5970.917/3266.558 |


## Actual width and phase coverage

| Run | Sample max W | Mean/median query TW W | Initial/final W distribution | Mean query cap% | Mean query W>32% | Queries W>32 | Start min/median/max % | Five start bins |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A/R1 | 32 | 12.834/12.634 | 4:16 / 29:1,31:1,32:14 | 5.92 | 0.00 | 0 | 10.26/50.08/90.02 | [2, 4, 4, 4, 2] |
| B/R1 | 32 | 11.704/11.536 | 4:16 / 25:1,26:1,27:1,28:3,29:4,30:1,31:2,32:3 | 0.82 | 0.00 | 0 | 10.57/50.44/89.89 | [2, 4, 4, 4, 2] |
| C/R1 | 33 | 12.297/12.129 | 4:16 / 23:1,26:1,28:4,29:3,30:2,31:1,32:2,33:2 | 0.00 | 0.09 | 2 | 10.19/49.69/90.15 | [2, 4, 4, 4, 2] |
| D/R1 | 32 | 11.932/11.729 | 4:16 / 16:1,26:1,28:2,29:3,30:2,31:1,32:6 | 0.84 | 0.00 | 0 | 9.94/49.17/89.53 | [2, 4, 4, 4, 2] |
| E/R1 | 16 | 10.615/10.480 | 4:16 / 16:16 | 44.39 | 0.00 | 0 | 10.11/49.39/89.15 | [2, 4, 4, 4, 2] |
| B/R2 | 32 | 11.667/11.420 | 4:16 / 26:1,27:1,28:1,29:5,30:2,31:1,32:5 | 1.09 | 0.00 | 0 | 10.25/50.16/89.98 | [2, 4, 4, 4, 2] |
| C/R2 | 36 | 11.799/11.964 | 4:16 / 25:1,26:2,27:3,28:4,29:1,30:1,31:2,33:1,36:1 | 0.00 | 1.03 | 2 | 10.20/50.13/90.02 | [2, 4, 4, 4, 2] |
| D/R2 | 32 | 12.905/11.669 | 4:16 / 24:1,27:2,29:3,30:2,31:2,32:6 | 5.87 | 0.00 | 0 | 9.84/50.08/89.88 | [2, 4, 4, 4, 2] |
| E/R2 | 16 | 8.958/9.037 | 4:16 / 15:1,16:15 | 28.65 | 0.00 | 0 | 9.79/49.34/89.88 | [3, 3, 4, 4, 2] |
| A/R2 | 32 | 12.957/13.028 | 4:16 / 31:1,32:15 | 7.27 | 0.00 | 0 | 10.12/50.15/90.07 | [2, 4, 4, 4, 2] |
| C/R3 | 40 | 12.072/11.567 | 4:16 / 28:4,29:2,30:5,31:2,33:1,38:1,40:1 | 0.00 | 1.64 | 3 | 10.22/50.29/90.05 | [2, 4, 4, 4, 2] |
| D/R3 | 32 | 12.214/10.496 | 4:16 / 20:1,25:1,27:1,28:3,29:1,30:3,31:2,32:4 | 1.06 | 0.00 | 0 | 10.10/49.76/89.98 | [2, 4, 4, 4, 2] |
| E/R3 | 16 | 8.842/9.429 | 4:16 / 16:16 | 28.27 | 0.00 | 0 | 9.95/49.75/89.58 | [2, 4, 4, 4, 2] |
| A/R3 | 32 | 12.826/12.655 | 4:16 / 28:1,29:1,32:14 | 5.27 | 0.00 | 0 | 10.13/50.03/90.03 | [2, 4, 4, 4, 2] |
| B/R3 | 31 | 11.549/11.550 | 4:16 / 25:2,26:1,27:4,28:3,29:1,30:2,31:3 | 0.00 | 0.00 | 0 | 10.20/50.03/89.99 | [2, 4, 4, 4, 2] |


**DERIVED METRIC:** C sample maxima33/36/40, only2/2/3 of16 queries spend any time above32; across-query mean above32 residency0.09/1.03/1.64%. C never reaches64. Mean query time-weighted W11.80–12.30, versus its much larger terminal widths; Wcap is not actual W and final W is not mean W. E caps at16 and changes width residency, but HOL/hidden behavior is not uniformly reduced across all repeats.

All15 runs cover5/5 bins;14 runs have2/4/4/4/2 starts and E/R2 has3/3/4/4/2; no phase gate fails. All sample boundaries lie inside benchmark origin/end. **INTERPRETATION:** this distributed cohort covers coarse workload time. **UNRESOLVED:** total active-query occupancy and complete dispatch progress are absent. Later qid or broad phase coverage does not certify steady state or representative behavior of the other9984 queries.

## Operational D6 gate and paired comparisons

| Regime/ref | Three HOL p95 ratios | ≥2× confirmations | Median3 per-run HOL/IO ratios | Median3 median-query hidden fractions | MATERIAL | LOW |
| --- | --- | --- | --- | --- | --- | --- |
| C/B | 0.968, 0.948, 0.870 | 0 | 0.882 | 64.31 | False | False |
| D/B | 0.870, 0.693, 0.591 | 0 | 0.255 | 57.33 | False | False |


**DERIVED VERDICT:** D6_INCONCLUSIVE. Neither C nor D shows≥2× matched B HOL p95 in2/3 repetitions (both0/3). Therefore MATERIAL fails despite large HOL/IO ratios or hidden fractions. LOW fails because required ratios/fractions are not<10% for all runs. Phase is adequate by the frozen operational check, so this verdict is not caused by phase failure. All ratios defined; no zero-B confirmation. Gate uses median of run ratios rather than ratio of medians, and median-query hidden fractions rather than duration-weighted pooling. LOW additionally guards any >B elevation in≥2/3 pairs, the conservative definition frozen in PLAN. **system_wide_D6=INCONCLUSIVE**, independently of this sample-conditional verdict.

| Comparison | Rep | HOL p95 delta µs | HOL p95 ratio | Observed p95 delta µs | Median query hidden fraction delta pp |
| --- | --- | --- | --- | --- | --- |
| C_vs_B | 1 | -7.630 | 0.968 | 11.974 | 1.293 |
| C_vs_B | 2 | -13.093 | 0.948 | -3.468 | -0.405 |
| C_vs_B | 3 | -36.292 | 0.870 | -56.972 | -0.834 |
| D_vs_B | 1 | -31.474 | 0.870 | 735.054 | -3.885 |
| D_vs_B | 2 | -77.791 | 0.693 | 414.658 | -10.800 |
| D_vs_B | 3 | -114.316 | 0.591 | 76.117 | -6.856 |
| E_vs_D | 1 | -28.935 | 0.863 | -696.689 | 1.091 |
| E_vs_D | 2 | -2.621 | 0.985 | 5279.848 | 6.656 |
| E_vs_D | 3 | 46.821 | 1.284 | -68.045 | 7.633 |
| B_vs_A | 1 | 161.627 | 3.007 | 144.258 | 18.123 |
| B_vs_A | 2 | 174.833 | 3.215 | 157.554 | 21.202 |
| B_vs_A | 3 | 199.107 | 3.479 | 198.328 | 20.581 |


**INTERPRETATION:** C/B has similar or lower p95 publication HOL in this cohort despite W64; D/B has lower HOL p95 yet longer/more variable observed-I/O intervals and occasional millisecond HOL tails. E/D changes both observed intervals and HOL inconsistently, including a very large E/R2 p95 observed interval. A/B shows absolute concurrency-dependent intervals, not a causal FIFO throughput effect. Same-qid query tables below retain different per-query/phase/worker patterns instead of pretending deterministic runtime order. Per-query p95 and hidden distributions are retained in analysis JSON as an aggregation sensitivity check; they do not replace the frozen pooled-physical-request gate.

## Logical work and benchmark context

DETAIL benchmark values are diagnostic context; no matched headline comparison with G0-B LIGHT. Prior separately characterized G0-B median QPS: B3282/C3304/D2847, D p99≈29.5ms, ~123 I/O/query atT8/T16. Different subject/version/mode/time: no direct DETAIL-vs-LIGHT QPS or overhead conclusion.

| Run | DETAIL QPS | Mean lat µs | P99 µs | Recall@10 % | Benchmark mean I/O | Sample submit=CQE=publish | Sample expanded | Sample cache ready/published | Whole-workload submit/cache/expand |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A/R1 | 878.04 | 1127.14 | 1429.0 | 99.16 | 125.23 | 1935 | 1887 | 0/0 | 1252306/0/1209251 |
| B/R1 | 3032.48 | 2622.84 | 4285.0 | 99.14 | 122.7 | 1926 | 1879 | 0/0 | 1227031/0/1186690 |
| C/R1 | 3008.58 | 2642.32 | 5217.0 | 99.13 | 122.71 | 1935 | 1886 | 0/0 | 1227097/0/1187054 |
| D/R1 | 2681.98 | 5930.86 | 30849.0 | 99.13 | 122.65 | 1922 | 1877 | 0/0 | 1226492/0/1186203 |
| E/R1 | 2558.66 | 6157.27 | 34081.0 | 99.13 | 121.55 | 1907 | 1867 | 0/0 | 1215528/0/1185239 |
| B/R2 | 3046.01 | 2612.37 | 3726.0 | 99.13 | 122.7 | 1920 | 1875 | 0/0 | 1227028/0/1186793 |
| C/R2 | 3070.84 | 2589.63 | 3530.0 | 99.15 | 122.67 | 1924 | 1879 | 0/0 | 1226658/0/1186396 |
| D/R2 | 2596.06 | 6107.16 | 37788.0 | 99.13 | 122.83 | 1922 | 1871 | 0/0 | 1228259/0/1187813 |
| E/R2 | 2606.97 | 6096.14 | 27429.0 | 99.12 | 121.52 | 1902 | 1865 | 0/0 | 1215247/0/1184697 |
| A/R2 | 873.99 | 1133.11 | 1639.0 | 99.16 | 125.22 | 1937 | 1888 | 0/0 | 1252163/0/1209108 |
| C/R3 | 3054.02 | 2603.99 | 3693.0 | 99.13 | 122.65 | 1928 | 1878 | 0/0 | 1226502/0/1186440 |
| D/R3 | 2555.14 | 6209.18 | 37180.0 | 99.14 | 122.85 | 1922 | 1874 | 0/0 | 1228492/0/1187710 |
| E/R3 | 2652.22 | 5983.51 | 33986.0 | 99.11 | 121.53 | 1913 | 1875 | 0/0 | 1215321/0/1185023 |
| A/R3 | 875.46 | 1130.48 | 1493.0 | 99.16 | 125.21 | 1936 | 1889 | 0/0 | 1252131/0/1208917 |
| B/R3 | 3066.11 | 2594.55 | 3608.0 | 99.13 | 122.68 | 1923 | 1876 | 0/0 | 1226759/0/1186762 |


Every sampled/cache publication is lifecycle/FIFO-valid; physical query submit=CQE=publish. Published-minus-expanded is a count difference only. No claim of frontier redundancy or dependency starvation follows from these counts or greater inflight I/O.

## Host/NVMe/SQPOLL diagnostics

Available1s sample means include index loading/startup/search/partial intervals; whole NVMe activity can include other processes. Temporal coverage is retained per series in analysis JSON. Short T8/T16 windows are not precise steady-state averages. Device utilization alone is not proof of bandwidth/IOPS saturation. Measured CPU idle is20.71–26.19% atT8 versus7.20–7.81% atT16, sys35.60–36.31% versus42.38–46.60%; NVMe read IOPS are318k–325k atT8 versus280k–295k atT16. These limited-window observations are consistent with greater host/kernel pressure atT16; they do not isolate a cause or establish SSD saturation.

| Run | CPU usr% | sys% | idle% | Process CPU% | Read IOPS | Read KiB/s | r_await ms | aqu-sz | util% | N CPU/process/NVMe | Span CPU/NVMe s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A/R1 | 8.41 | 5.29 | 86.16 | 196.08 | 101506.83 | 406196.33 | 0.07 | 7.30 | 77.95 | 12/12/12 | 11.0/11.0 |
| B/R1 | 40.80 | 36.18 | 22.80 | 1411.21 | 318753.59 | 1275030.30 | 0.12 | 38.82 | 69.83 | 3/3/3 | 2.0/2.0 |
| C/R1 | 42.92 | 36.31 | 20.71 | 1395.48 | 318235.33 | 1274886.67 | 0.12 | 37.90 | 70.93 | 3/3/3 | 2.0/2.0 |
| D/R1 | 48.42 | 44.08 | 7.50 | 1783.50 | 295155.30 | 1180642.19 | 0.11 | 31.68 | 69.83 | 4/4/4 | 3.0/3.0 |
| E/R1 | 45.67 | 46.60 | 7.71 | 1745.58 | 281763.94 | 1127079.72 | 0.10 | 28.78 | 71.19 | 4/4/4 | 3.0/3.0 |
| B/R2 | 38.72 | 35.84 | 25.18 | 1426.33 | 323775.00 | 1295121.33 | 0.12 | 39.57 | 64.57 | 3/3/3 | 2.0/2.0 |
| C/R2 | 38.10 | 35.60 | 26.19 | 1422.33 | 325026.00 | 1300124.00 | 0.12 | 39.14 | 71.07 | 3/3/3 | 2.0/2.0 |
| D/R2 | 49.32 | 42.83 | 7.81 | 1761.00 | 286817.00 | 1147297.00 | 0.11 | 30.42 | 70.88 | 4/4/4 | 3.0/3.0 |
| E/R2 | 50.02 | 42.38 | 7.58 | 1769.25 | 284619.53 | 1138491.05 | 0.10 | 29.56 | 68.84 | 4/4/4 | 3.0/3.0 |
| A/R2 | 6.72 | 5.20 | 87.78 | 196.17 | 101046.92 | 404191.33 | 0.07 | 7.37 | 77.59 | 12/12/12 | 11.0/11.0 |
| C/R3 | 43.21 | 35.89 | 20.79 | 1400.00 | 318060.00 | 1272264.00 | 0.12 | 38.14 | 73.07 | 3/3/3 | 2.0/2.0 |
| D/R3 | 48.91 | 43.77 | 7.20 | 1673.25 | 280036.60 | 1120172.32 | 0.10 | 28.84 | 72.67 | 4/4/4 | 3.0/3.0 |
| E/R3 | 47.05 | 45.22 | 7.74 | 1761.22 | 290998.35 | 1164018.35 | 0.10 | 30.04 | 73.03 | 4/4/4 | 3.0/3.0 |
| A/R3 | 8.72 | 5.51 | 85.58 | 195.92 | 100927.42 | 403786.67 | 0.07 | 7.27 | 76.38 | 12/12/12 | 11.0/11.0 |
| B/R3 | 41.04 | 36.27 | 22.61 | 1421.48 | 324608.90 | 1298452.94 | 0.12 | 39.23 | 65.68 | 3/3/3 | 2.0/2.0 |


| Run | SQPOLL task rows/snapshot | iou-wrk rows | Benchmark task masks | Last CPUs (union) | fdinfo available | Process voluntary/involuntary cs/s | Package temp °C snapshots | CPU freq MHz snapshots min–max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A/R1 | [0, 1, 1] | [0, 0, 0] | 0-19 | 4,5,8,12,18,19 | True | 0.00/4.75 | 61.0–86.0 | 400–4473 |
| B/R1 | [8, 8, 8] | [0, 0, 0] | 0-19 | 0,1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 | True | 1.33/65.22 | 56.0–86.0 | 400–4317 |
| C/R1 | [8, 8, 8] | [0, 0, 0] | 0-19 | 0,1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19 | True | 1.00/52.67 | 56.0–87.0 | 400–4664 |
| D/R1 | [16, 16, 16] | [0, 0, 0] | 0-19 | 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 | True | 1.24/278.96 | 59.0–88.0 | 400–4386 |
| E/R1 | [16, 16, 16] | [0, 0, 0] | 0-19 | 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 | True | 1.25/145.41 | 64.0–88.0 | 400–4400 |
| B/R2 | [8, 8, 8] | [0, 0, 0] | 0-19 | 0,1,2,3,4,5,6,8,9,10,11,12,13,14,15,16,17,18,19 | True | 1.98/27.60 | 60.0–90.0 | 400–4559 |
| C/R2 | [8, 8, 8] | [0, 0, 0] | 0-19 | 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 | True | 1.00/3.33 | 56.0–84.0 | 400–4651 |
| D/R2 | [16, 16, 16] | [0, 0, 0] | 0-19 | 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 | True | 1.50/98.67 | 55.0–86.0 | 400–4651 |
| E/R2 | [16, 16, 16] | [0, 0, 0] | 0-19 | 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 | True | 1.25/179.25 | 56.0–86.0 | 400–4488 |
| A/R2 | [0, 1, 1] | [0, 0, 0] | 0-19 | 4,8,13,17,18 | True | 0.00/10.42 | 56.0–90.0 | 400–4588 |
| C/R3 | [8, 8, 8] | [0, 0, 0] | 0-19 | 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 | True | 1.33/66.00 | 61.0–84.0 | 398–4247 |
| D/R3 | [16, 16, 16] | [0, 0, 0] | 0-19 | 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 | True | 1.00/216.00 | 59.0–88.0 | 400–4209 |
| E/R3 | [16, 16, 16] | [0, 0, 0] | 0-19 | 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 | True | 1.00/172.90 | 61.0–87.0 | 400–4213 |
| A/R3 | [0, 1, 1] | [0, 0, 0] | 0-19 | 4,8,15,18,19 | True | 0.00/21.67 | 60.0–89.0 | 399–4312 |
| B/R3 | [8, 8, 8] | [0, 0, 0] | 0-19 | 0,3,4,5,6,8,9,10,11,12,13,14,15,16,17,18,19 | True | 1.67/8.00 | 59.0–90.0 | 399–4406 |


**MEASURED FACT:** runtime snapshots observe1/8/16 SQPOLL task rows during T1/T8/T16 runs (the first T1 startup snapshot can precede rings). Benchmark task masks include0–19, last CPUs span native CPUs; no affinity restriction was introduced. No iou-wrk rows were observed; that is not proof none ever existed. SQPOLL tasks are present in /proc benchmark task groups on this kernel; their independently read allowed masks are0–19. SQPOLL-specific last CPUs, full ps rows, task context switches and fdinfo payloads are retained in runtime snapshots. The task-mask/CPU union table includes both benchmark and SQPOLL tasks; traced query worker/TID fields identify only sampled executing workers, not every auxiliary task. The observed SQPOLL scaling is runtime evidence in these snapshots, not a source-only universal assertion.

CPU governor remained powersave, EPP balance_performance; NVMe scheduler [none] mq-deadline and queue settings recorded without tuning. Frequency/temperature/load/MemAvailable/swap snapshots are retained. **INTERPRETATION:** T16 has userspace-observed millisecond tails consistent with some mixture of I/O waiting, poll scheduling and host contention. **UNRESOLVED:** the relative contributions; sparse telemetry cannot assign cause, SSD saturation, or a critical-path FIFO mechanism. High completed-hidden maxima and HOL can coexist with lower p95 HOL than B.

## Per-run, per-query retained diagnostics

All240 sampled query records remain grouped in15 runs. Physical N means IO_SELECT/IO_SUBMIT/IO_CQE_SEEN/IO_PUBLISH counts each (cache count0 in these samples); expansion may be absent for some published nodes. HOL and I/O tuples are p50/p95/p99/maxµs; max physical hidden/outstanding/unpublished are post-timestamp-tie extrema. Phase start/end are relative nanoseconds and fractions of traced benchmark duration. Width buckets are fractions of total query time in1–4/5–8/9–16/17–32/33–64/65+; unknown prefix is separately reported. Timing/occupancy and width tables do not assume independent queries or requests.

### A/R1 — `P0_sift10m_T1_W32_DETAIL_R001_20261009T090503633488Z_438f1b4febad480ca4ffe7a40d079f13`


| QID | Physical N | Expanded | Pub−expanded | HOL tuple µs | IO tuple µs | TW hidden/outstanding/unpublished | Max hidden/outstanding/unpublished | Hidden>0/≥2 % | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 119 | 116 | 3 | 7.64/41.36/46.60/54.88 | 63.00/108.71/115.74/116.68 | 1.50/7.57/9.07 | 12/24/27 | 51.27/31.16 | 0 |
| 1533 | 121 | 119 | 2 | 4.62/95.52/136.78/140.18 | 65.34/122.97/174.15/203.85 | 2.45/6.82/9.27 | 20/20/25 | 44.89/34.01 | 0 |
| 2066 | 121 | 117 | 4 | 7.74/48.14/73.26/85.47 | 65.90/107.70/127.32/155.81 | 1.48/7.55/9.03 | 15/25/25 | 44.44/28.55 | 0 |
| 2600 | 118 | 114 | 4 | 20.71/118.63/136.14/142.39 | 66.77/119.05/161.13/203.63 | 2.84/6.53/9.38 | 18/21/24 | 52.05/39.23 | 0 |
| 3133 | 119 | 118 | 1 | 3.57/49.17/58.37/60.59 | 69.85/107.95/120.39/122.06 | 1.51/8.04/9.55 | 12/27/30 | 45.37/27.71 | 0 |
| 3666 | 121 | 117 | 4 | 6.78/57.51/79.79/82.94 | 60.91/109.47/133.56/145.08 | 1.67/7.24/8.91 | 15/23/26 | 43.86/28.52 | 0 |
| 4200 | 123 | 123 | 0 | 8.74/85.70/128.93/195.25 | 69.95/149.45/206.53/244.15 | 2.08/6.85/8.94 | 14/20/25 | 49.14/38.83 | 0 |
| 4733 | 116 | 111 | 5 | 10.25/82.23/94.33/114.70 | 61.21/107.73/146.79/154.65 | 2.26/6.96/9.22 | 16/21/22 | 56.69/35.92 | 0 |
| 5266 | 123 | 120 | 3 | 7.46/79.96/91.50/97.20 | 66.15/105.51/152.18/171.35 | 2.03/6.89/8.92 | 21/24/27 | 41.08/27.75 | 0 |
| 5800 | 117 | 117 | 0 | 15.74/91.70/102.96/122.08 | 69.49/135.51/177.74/194.91 | 3.26/8.93/12.19 | 18/24/28 | 45.62/38.36 | 0 |
| 6333 | 119 | 118 | 1 | 7.63/75.68/96.19/99.17 | 69.95/130.88/159.85/175.18 | 2.24/7.49/9.73 | 17/24/28 | 41.73/33.44 | 0 |
| 6866 | 119 | 117 | 2 | 8.45/80.94/89.26/96.35 | 70.12/125.01/150.98/160.36 | 2.17/7.79/9.97 | 17/27/28 | 45.76/32.28 | 0 |
| 7400 | 123 | 117 | 6 | 9.79/60.23/74.40/87.40 | 62.71/113.26/137.79/152.97 | 1.74/6.71/8.45 | 20/22/25 | 41.11/29.38 | 0 |
| 7933 | 130 | 125 | 5 | 0.16/59.77/77.13/79.13 | 65.06/108.79/131.65/155.44 | 1.45/7.32/8.77 | 14/24/30 | 31.01/26.02 | 0 |
| 8466 | 121 | 121 | 0 | 5.95/81.55/118.59/122.83 | 69.57/118.61/137.12/183.83 | 1.96/7.00/8.96 | 16/26/28 | 35.10/28.36 | 0 |
| 9000 | 125 | 117 | 8 | 8.80/87.84/110.62/117.19 | 69.35/116.87/163.91/183.41 | 2.67/8.14/10.80 | 19/22/28 | 44.90/35.44 | 0 |


| QID | Worker/TID | Start/end relative ns | Start/end phase % | Initial/final/max/change W | TW mean W | At cap/above32/unknown % | Width-bucket % 1–4/5–8/9–16/17–32/33–64/65+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 0/12994 | 1168864398/1169975804 | 10.26/10.27 | 4/32/32/28 | 12.129 | 4.88/0.00/0.65 | 49.14/5.39/13.79/31.03/0.00/0.00 |
| 1533 | 0/12994 | 1771322921/1772663930 | 15.55/15.56 | 4/32/32/28 | 12.315 | 9.13/0.00/0.44 | 43.76/11.84/10.21/33.75/0.00/0.00 |
| 2066 | 0/12994 | 2376334518/2377471461 | 20.87/20.88 | 4/32/32/28 | 11.409 | 1.53/0.00/0.54 | 47.36/8.56/15.40/28.15/0.00/0.00 |
| 2600 | 0/12994 | 2982084713/2983413232 | 26.18/26.20 | 4/29/29/25 | 11.879 | 0.00/0.00/0.47 | 39.99/10.20/18.12/31.21/0.00/0.00 |
| 3133 | 0/12994 | 3581080677/3582157098 | 31.44/31.45 | 4/32/32/28 | 12.602 | 11.61/0.00/0.66 | 42.02/11.76/13.25/32.31/0.00/0.00 |
| 3666 | 0/12994 | 4189785309/4190938569 | 36.79/36.80 | 4/32/32/28 | 11.855 | 2.39/0.00/0.56 | 50.15/5.72/9.04/34.54/0.00/0.00 |
| 4200 | 0/12994 | 4794170169/4795561825 | 42.09/42.11 | 4/32/32/28 | 12.667 | 0.57/0.00/0.62 | 48.20/4.28/11.57/35.33/0.00/0.00 |
| 4733 | 0/12994 | 5400385072/5401521920 | 47.42/47.43 | 4/32/32/28 | 13.357 | 0.54/0.00/0.81 | 34.05/7.89/19.12/38.14/0.00/0.00 |
| 5266 | 0/12994 | 6007174094/6008442082 | 52.75/52.76 | 4/32/32/28 | 12.903 | 9.72/0.00/0.85 | 45.93/6.45/12.58/34.20/0.00/0.00 |
| 5800 | 0/12994 | 6616992912/6618001197 | 58.10/58.11 | 4/32/32/28 | 14.592 | 1.99/0.00/0.86 | 38.74/7.47/10.40/42.53/0.00/0.00 |
| 6333 | 0/12994 | 7219424349/7220618205 | 63.39/63.40 | 4/32/32/28 | 12.481 | 6.24/0.00/0.91 | 47.42/9.69/9.71/32.27/0.00/0.00 |
| 6866 | 0/12994 | 7824922716/7826077248 | 68.71/68.72 | 4/32/32/28 | 13.262 | 11.49/0.00/0.81 | 45.29/6.14/12.27/35.49/0.00/0.00 |
| 7400 | 0/12994 | 8429646481/8430946356 | 74.02/74.03 | 4/32/32/28 | 13.421 | 0.54/0.00/0.85 | 41.15/5.35/13.57/39.08/0.00/0.00 |
| 7933 | 0/12994 | 9037374719/9038657234 | 79.35/79.36 | 4/32/32/28 | 15.027 | 21.07/0.00/0.88 | 43.35/4.58/9.41/41.78/0.00/0.00 |
| 8466 | 0/12994 | 9643832332/9645105605 | 84.68/84.69 | 4/31/31/27 | 11.189 | 0.00/0.00/0.81 | 47.32/11.10/13.18/27.59/0.00/0.00 |
| 9000 | 0/12994 | 10252659250/10253793320 | 90.02/90.03 | 4/32/32/28 | 14.262 | 12.96/0.00/0.93 | 43.28/6.55/9.62/39.61/0.00/0.00 |


### B/R1 — `P0_sift10m_T8_W32_DETAIL_R001_20261009T090705519648Z_ec817782440e43ac806bef22e910f599`


| QID | Physical N | Expanded | Pub−expanded | HOL tuple µs | IO tuple µs | TW hidden/outstanding/unpublished | Max hidden/outstanding/unpublished | Hidden>0/≥2 % | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 118 | 114 | 4 | 55.39/220.59/249.19/269.84 | 111.38/288.87/336.23/394.51 | 2.86/5.68/8.54 | 15/19/23 | 66.61/49.16 | 0 |
| 1533 | 119 | 119 | 0 | 23.00/255.49/363.52/373.21 | 108.06/304.80/373.01/441.53 | 2.63/5.43/8.05 | 15/21/21 | 57.31/45.36 | 0 |
| 2066 | 122 | 118 | 4 | 52.42/196.94/215.89/242.55 | 97.46/228.84/294.45/312.73 | 3.29/5.83/9.12 | 16/16/21 | 62.93/53.45 | 0 |
| 2600 | 116 | 113 | 3 | 25.82/232.06/383.91/454.89 | 106.16/293.84/387.16/532.74 | 3.34/6.84/10.18 | 17/17/24 | 67.17/56.58 | 0 |
| 3133 | 119 | 118 | 1 | 37.40/166.25/177.46/201.89 | 113.55/247.09/297.63/307.27 | 2.87/6.53/9.39 | 23/21/28 | 58.79/42.37 | 0 |
| 3666 | 122 | 117 | 5 | 56.36/246.16/296.82/332.03 | 93.09/231.95/311.87/409.33 | 4.01/6.32/10.33 | 24/20/25 | 73.14/55.54 | 0 |
| 4200 | 122 | 120 | 2 | 67.93/250.60/324.45/363.63 | 135.27/320.89/385.57/415.47 | 2.77/5.22/7.99 | 13/16/20 | 66.33/56.89 | 0 |
| 4733 | 116 | 111 | 5 | 56.71/160.33/198.34/210.20 | 92.13/231.02/272.15/294.43 | 3.21/5.69/8.90 | 16/20/25 | 69.24/52.68 | 0 |
| 5266 | 123 | 120 | 3 | 80.82/202.15/299.55/327.54 | 112.04/252.54/288.78/436.59 | 4.36/6.75/11.11 | 21/22/23 | 70.05/49.73 | 0 |
| 5800 | 115 | 114 | 1 | 95.82/431.23/481.94/507.92 | 97.57/330.98/453.80/595.00 | 5.76/5.15/10.91 | 23/18/23 | 64.29/57.41 | 0 |
| 6333 | 118 | 116 | 2 | 43.38/237.47/316.61/333.95 | 104.46/257.29/336.77/411.86 | 3.07/5.65/8.71 | 18/19/23 | 59.66/38.41 | 0 |
| 6866 | 118 | 116 | 2 | 47.06/161.44/213.27/235.42 | 107.37/222.89/323.05/370.02 | 2.35/5.25/7.60 | 17/23/23 | 62.25/43.52 | 0 |
| 7400 | 123 | 118 | 5 | 44.39/188.11/267.43/304.12 | 87.62/247.64/379.76/389.49 | 2.43/4.78/7.21 | 15/18/22 | 63.10/48.43 | 0 |
| 7933 | 127 | 124 | 3 | 35.85/166.25/215.93/229.73 | 103.29/250.21/329.14/342.07 | 2.35/5.41/7.76 | 15/16/21 | 56.61/45.47 | 0 |
| 8466 | 122 | 120 | 2 | 36.47/444.56/549.24/555.60 | 95.98/252.34/427.08/683.91 | 3.31/4.32/7.63 | 13/17/22 | 57.34/48.43 | 0 |
| 9000 | 126 | 121 | 5 | 42.64/250.68/290.01/343.80 | 104.74/251.40/354.91/412.22 | 3.39/5.85/9.24 | 16/17/22 | 59.20/43.36 | 0 |


| QID | Worker/TID | Start/end relative ns | Start/end phase % | Initial/final/max/change W | TW mean W | At cap/above32/unknown % | Width-bucket % 1–4/5–8/9–16/17–32/33–64/65+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 5/13386 | 348630708/351453683 | 10.57/10.66 | 4/30/30/26 | 10.479 | 0.00/0.00/0.34 | 42.73/8.45/25.91/22.57/0.00/0.00 |
| 1533 | 7/13388 | 535642524/538411942 | 16.24/16.33 | 4/29/29/25 | 11.730 | 0.00/0.00/0.44 | 37.44/10.27/21.22/30.63/0.00/0.00 |
| 2066 | 7/13388 | 708561821/710991591 | 21.49/21.56 | 4/26/26/22 | 11.342 | 0.00/0.00/0.38 | 35.50/12.67/22.25/29.19/0.00/0.00 |
| 2600 | 1/13382 | 882408851/884609344 | 26.76/26.83 | 4/32/32/28 | 15.799 | 8.16/0.00/0.46 | 27.91/8.73/17.68/45.23/0.00/0.00 |
| 3133 | 2/13383 | 1056266694/1058556475 | 32.03/32.10 | 4/32/32/28 | 11.259 | 3.22/0.00/0.41 | 44.13/12.82/17.64/25.01/0.00/0.00 |
| 3666 | 2/13383 | 1230885196/1233139842 | 37.33/37.39 | 4/32/32/28 | 13.050 | 1.70/0.00/0.25 | 35.80/13.15/15.56/35.24/0.00/0.00 |
| 4200 | 5/13386 | 1403825058/1407476859 | 42.57/42.68 | 4/27/27/23 | 10.132 | 0.00/0.00/0.21 | 41.99/13.12/21.75/22.93/0.00/0.00 |
| 4733 | 3/13384 | 1576683170/1579047416 | 47.81/47.88 | 4/31/31/27 | 12.988 | 0.00/0.00/0.43 | 40.45/6.50/16.07/36.55/0.00/0.00 |
| 5266 | 7/13388 | 1749733781/1752040104 | 53.06/53.13 | 4/28/28/24 | 13.183 | 0.00/0.00/0.54 | 31.72/11.75/10.57/45.42/0.00/0.00 |
| 5800 | 3/13384 | 1923481901/1926369598 | 58.33/58.42 | 4/25/25/21 | 12.038 | 0.00/0.00/0.25 | 22.99/19.74/28.95/28.07/0.00/0.00 |
| 6333 | 4/13385 | 2095735604/2098393178 | 63.55/63.63 | 4/28/28/24 | 10.959 | 0.00/0.00/0.33 | 47.82/6.65/18.25/26.95/0.00/0.00 |
| 6866 | 0/13374 | 2268582699/2271302486 | 68.79/68.88 | 4/29/29/25 | 9.923 | 0.00/0.00/0.56 | 52.26/8.38/14.65/24.16/0.00/0.00 |
| 7400 | 1/13382 | 2441756810/2444724330 | 74.05/74.14 | 4/29/29/25 | 10.926 | 0.00/0.00/0.34 | 41.73/8.59/25.44/23.89/0.00/0.00 |
| 7933 | 7/13388 | 2614224172/2617131518 | 79.28/79.36 | 4/31/31/27 | 11.842 | 0.00/0.00/0.32 | 43.10/9.99/16.78/29.81/0.00/0.00 |
| 8466 | 1/13382 | 2785124112/2788694508 | 84.46/84.57 | 4/29/29/25 | 9.809 | 0.00/0.00/0.44 | 41.60/9.50/33.87/14.60/0.00/0.00 |
| 9000 | 6/13387 | 2964188962/2966813298 | 89.89/89.97 | 4/28/28/24 | 11.808 | 0.00/0.00/0.46 | 39.20/5.16/18.52/36.67/0.00/0.00 |


### C/R1 — `P0_sift10m_T8_W64_DETAIL_R001_20261009T090718638920Z_70bcca4c9bb24406b85ea8ce89b47994`


| QID | Physical N | Expanded | Pub−expanded | HOL tuple µs | IO tuple µs | TW hidden/outstanding/unpublished | Max hidden/outstanding/unpublished | Hidden>0/≥2 % | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 120 | 114 | 6 | 88.56/273.89/329.10/358.55 | 118.78/348.60/398.44/428.73 | 4.30/6.05/10.35 | 18/18/24 | 68.35/60.49 | 0 |
| 1533 | 119 | 119 | 0 | 66.27/233.70/265.35/295.01 | 112.92/311.77/337.61/362.93 | 3.31/5.21/8.52 | 17/19/20 | 64.11/51.33 | 0 |
| 2066 | 120 | 117 | 3 | 38.07/231.21/255.86/267.10 | 85.65/236.04/355.75/370.88 | 3.67/5.52/9.19 | 23/19/26 | 67.83/50.81 | 0 |
| 2600 | 116 | 112 | 4 | 65.34/292.77/343.12/394.15 | 111.62/277.74/467.31/524.92 | 3.67/5.65/9.32 | 16/22/23 | 62.94/51.87 | 0 |
| 3133 | 119 | 117 | 2 | 65.96/228.85/277.69/295.60 | 91.60/248.01/355.55/374.29 | 3.27/4.97/8.24 | 16/19/20 | 72.40/55.94 | 0 |
| 3666 | 123 | 119 | 4 | 40.76/185.74/276.76/298.96 | 108.97/261.74/343.83/415.20 | 2.59/5.69/8.28 | 20/20/23 | 48.61/41.01 | 0 |
| 4200 | 122 | 120 | 2 | 44.59/185.73/222.33/252.56 | 116.49/253.37/298.42/317.26 | 2.69/5.39/8.08 | 18/19/21 | 61.47/45.28 | 0 |
| 4733 | 116 | 111 | 5 | 60.97/248.76/302.26/391.86 | 97.51/286.20/381.99/453.86 | 3.52/5.65/9.16 | 21/22/25 | 70.29/56.30 | 0 |
| 5266 | 125 | 122 | 3 | 68.47/189.31/219.03/242.07 | 97.70/242.51/289.97/345.35 | 3.80/6.00/9.80 | 19/21/25 | 64.51/46.80 | 0 |
| 5800 | 117 | 116 | 1 | 40.32/192.91/280.38/286.91 | 91.67/253.78/283.34/401.17 | 3.35/6.25/9.61 | 23/21/23 | 58.22/39.46 | 0 |
| 6333 | 117 | 114 | 3 | 72.33/276.18/322.08/330.28 | 87.07/280.66/401.13/428.89 | 3.81/5.03/8.84 | 16/17/23 | 69.58/60.52 | 0 |
| 6866 | 120 | 119 | 1 | 63.11/271.82/400.72/410.02 | 104.87/306.04/375.10/488.40 | 4.16/5.52/9.69 | 20/20/23 | 63.22/50.24 | 0 |
| 7400 | 123 | 119 | 4 | 41.69/189.79/338.09/410.65 | 93.43/239.99/427.77/480.50 | 2.56/5.09/7.65 | 12/18/24 | 63.29/52.44 | 0 |
| 7933 | 125 | 121 | 4 | 31.72/210.36/228.33/256.08 | 96.19/259.82/300.99/323.20 | 2.59/4.76/7.35 | 13/22/23 | 56.62/40.38 | 0 |
| 8466 | 119 | 116 | 3 | 55.80/152.47/182.75/197.83 | 112.63/228.83/270.76/285.25 | 2.82/5.95/8.77 | 21/20/23 | 65.97/49.82 | 0 |
| 9000 | 134 | 130 | 4 | 80.05/219.46/420.79/539.13 | 85.41/241.43/334.47/620.27 | 4.99/6.32/11.31 | 28/24/28 | 69.72/62.08 | 0 |


| QID | Worker/TID | Start/end relative ns | Start/end phase % | Initial/final/max/change W | TW mean W | At cap/above32/unknown % | Width-bucket % 1–4/5–8/9–16/17–32/33–64/65+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 5/13506 | 338659299/341592004 | 10.19/10.28 | 4/28/28/24 | 13.018 | 0.00/0.00/0.33 | 26.78/18.10/16.51/38.28/0.00/0.00 |
| 1533 | 4/13505 | 511560849/514634210 | 15.39/15.48 | 4/23/23/19 | 10.438 | 0.00/0.00/0.32 | 37.70/11.75/22.69/27.54/0.00/0.00 |
| 2066 | 7/13508 | 684260598/686712509 | 20.59/20.66 | 4/30/30/26 | 11.056 | 0.00/0.00/0.30 | 40.61/14.47/17.13/27.49/0.00/0.00 |
| 2600 | 0/13496 | 857869148/860632027 | 25.81/25.89 | 4/29/29/25 | 12.244 | 0.00/0.00/0.31 | 37.58/7.97/25.96/28.18/0.00/0.00 |
| 3133 | 6/13507 | 1032018500/1034820145 | 31.05/31.13 | 4/26/26/22 | 10.299 | 0.00/0.00/0.34 | 43.82/5.04/29.45/21.36/0.00/0.00 |
| 3666 | 0/13496 | 1207973220/1210636581 | 36.34/36.42 | 4/30/30/26 | 10.901 | 0.00/0.00/0.37 | 46.41/12.26/11.69/29.27/0.00/0.00 |
| 4200 | 1/13502 | 1389876373/1392790179 | 41.82/41.90 | 4/29/29/25 | 10.268 | 0.00/0.00/0.28 | 53.03/5.60/16.54/24.54/0.00/0.00 |
| 4733 | 2/13503 | 1564243457/1566785175 | 47.06/47.14 | 4/32/32/28 | 12.423 | 0.00/0.00/0.36 | 30.32/9.62/29.75/29.95/0.00/0.00 |
| 5266 | 6/13507 | 1738721458/1741189804 | 52.31/52.39 | 4/31/31/27 | 13.985 | 0.00/0.00/0.37 | 28.45/17.51/12.88/40.79/0.00/0.00 |
| 5800 | 6/13507 | 1929569302/1931798401 | 58.05/58.12 | 4/28/28/24 | 13.236 | 0.00/0.00/0.71 | 31.27/7.05/21.01/39.97/0.00/0.00 |
| 6333 | 2/13503 | 2113356172/2116054354 | 63.58/63.66 | 4/28/28/24 | 11.701 | 0.00/0.00/0.38 | 42.78/3.13/26.12/27.58/0.00/0.00 |
| 6866 | 4/13505 | 2295377965/2298323607 | 69.06/69.15 | 4/29/29/25 | 12.121 | 0.00/0.00/0.64 | 40.85/6.47/20.30/31.73/0.00/0.00 |
| 7400 | 1/13502 | 2473044723/2475878809 | 74.40/74.49 | 4/33/33/29 | 12.639 | 0.00/0.53/0.40 | 42.73/2.88/25.05/28.41/0.53/0.00 |
| 7933 | 5/13506 | 2647411146/2650513891 | 79.65/79.74 | 4/32/32/28 | 11.232 | 0.00/0.00/0.51 | 42.00/3.84/28.37/25.28/0.00/0.00 |
| 8466 | 4/13505 | 2822451870/2824944833 | 84.92/84.99 | 4/28/28/24 | 12.136 | 0.00/0.00/0.43 | 36.16/4.67/28.27/30.47/0.00/0.00 |
| 9000 | 1/13502 | 2996493257/2998901797 | 90.15/90.22 | 4/33/33/29 | 19.052 | 0.00/0.92/0.63 | 28.13/2.74/7.86/59.72/0.92/0.00 |


### D/R1 — `P0_sift10m_T16_W32_DETAIL_R001_20261009T090731767228Z_7261f62f236141ca95c96e0ec0136fee`


| QID | Physical N | Expanded | Pub−expanded | HOL tuple µs | IO tuple µs | TW hidden/outstanding/unpublished | Max hidden/outstanding/unpublished | Hidden>0/≥2 % | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 118 | 115 | 3 | 38.51/149.53/173.36/176.80 | 92.19/191.00/255.78/290.77 | 2.74/5.93/8.66 | 16/19/21 | 57.10/42.45 | 0 |
| 1533 | 120 | 119 | 1 | 59.93/301.59/5029.90/6116.38 | 105.95/510.99/5204.84/6189.34 | 2.13/3.17/5.30 | 18/17/23 | 77.85/74.23 | 0 |
| 2066 | 123 | 119 | 4 | 12.04/184.21/6047.29/6063.16 | 124.35/6023.65/6120.73/6124.27 | 2.71/10.14/12.85 | 17/25/26 | 83.78/80.72 | 0 |
| 2600 | 116 | 112 | 4 | 8.38/126.90/5147.78/6035.14 | 89.73/6088.41/6110.93/6118.20 | 2.05/10.62/12.68 | 19/19/25 | 87.30/83.10 | 0 |
| 3133 | 119 | 117 | 2 | 39.61/275.17/299.06/309.89 | 92.88/201.06/348.77/393.57 | 3.98/5.63/9.61 | 22/20/23 | 59.66/42.51 | 0 |
| 3666 | 121 | 117 | 4 | 11.83/119.15/130.21/133.12 | 80.66/6094.72/6111.14/6114.97 | 0.56/12.02/12.57 | 15/19/21 | 12.03/8.62 | 0 |
| 4200 | 122 | 121 | 1 | 34.70/147.75/230.53/281.87 | 103.85/222.82/406.00/1216.50 | 1.91/4.86/6.76 | 15/19/23 | 40.73/33.72 | 0 |
| 4733 | 115 | 108 | 7 | 24.41/193.75/297.88/299.18 | 106.02/6079.25/6148.18/6208.27 | 0.72/17.87/18.59 | 17/22/22 | 14.98/10.98 | 0 |
| 5266 | 117 | 114 | 3 | 1.43/637.73/998.92/999.10 | 982.10/999.14/1878.96/1995.84 | 0.46/6.02/6.49 | 12/13/13 | 10.67/8.28 | 0 |
| 5800 | 117 | 117 | 0 | 21.34/156.86/206.39/218.87 | 89.74/219.56/279.91/290.21 | 2.12/6.62/8.74 | 15/20/26 | 54.19/39.07 | 0 |
| 6333 | 118 | 116 | 2 | 33.51/226.10/231.56/233.98 | 85.03/271.84/315.27/331.26 | 3.29/5.62/8.90 | 15/21/24 | 58.60/52.00 | 0 |
| 6866 | 119 | 117 | 2 | 20.39/124.06/133.61/146.78 | 87.83/206.22/220.06/3054.96 | 0.92/3.34/4.26 | 16/26/28 | 20.77/16.89 | 0 |
| 7400 | 129 | 127 | 2 | 35.67/179.55/225.03/245.77 | 83.37/239.58/305.07/314.36 | 3.83/6.74/10.57 | 22/27/27 | 67.15/51.10 | 0 |
| 7933 | 125 | 121 | 4 | 5.88/290.05/368.01/3012.83 | 105.54/285.92/3034.55/3126.81 | 1.68/4.53/6.21 | 26/20/26 | 78.83/16.99 | 0 |
| 8466 | 121 | 120 | 1 | 7.13/196.91/291.35/6084.85 | 95.88/6021.97/6142.74/6150.68 | 1.47/7.44/8.91 | 21/24/26 | 87.12/11.18 | 0 |
| 9000 | 122 | 117 | 5 | 30.18/3124.92/3151.34/3205.00 | 88.28/3106.31/3217.38/3272.09 | 6.44/7.16/13.60 | 17/18/21 | 85.85/82.15 | 0 |


| QID | Worker/TID | Start/end relative ns | Start/end phase % | Initial/final/max/change W | TW mean W | At cap/above32/unknown % | Width-bucket % 1–4/5–8/9–16/17–32/33–64/65+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 0/13645 | 370777624/372891724 | 9.94/10.00 | 4/26/26/22 | 11.604 | 0.00/0.00/0.44 | 34.93/7.95/29.33/27.35/0.00/0.00 |
| 1533 | 3/13653 | 562281841/572603120 | 15.08/15.36 | 4/29/29/25 | 6.247 | 0.00/0.00/0.11 | 82.42/3.23/5.46/8.79/0.00/0.00 |
| 2066 | 8/13658 | 752741646/761482617 | 20.19/20.42 | 4/32/32/28 | 13.507 | 0.13/0.00/0.11 | 16.88/2.58/73.68/6.74/0.00/0.00 |
| 2600 | 2/13652 | 953560823/961568014 | 25.57/25.79 | 4/32/32/28 | 13.644 | 0.16/0.00/0.14 | 11.31/0.98/79.90/7.68/0.00/0.00 |
| 3133 | 6/13656 | 1148755375/1151107684 | 30.81/30.87 | 4/30/30/26 | 11.716 | 0.00/0.00/0.46 | 43.32/7.10/9.82/39.30/0.00/0.00 |
| 3666 | 0/13645 | 1340343091/1348265415 | 35.95/36.16 | 4/29/29/25 | 13.205 | 0.00/0.00/0.13 | 11.02/1.49/81.76/5.59/0.00/0.00 |
| 4200 | 4/13654 | 1540251952/1543517399 | 41.31/41.40 | 4/29/29/25 | 15.788 | 0.00/0.00/0.31 | 29.90/9.95/11.25/48.60/0.00/0.00 |
| 4733 | 14/13664 | 1733912056/1741984453 | 46.50/46.72 | 4/28/28/24 | 19.358 | 0.00/0.00/0.13 | 8.66/4.70/3.00/83.51/0.00/0.00 |
| 5266 | 6/13656 | 1932694971/1951705401 | 51.83/52.34 | 4/16/16/12 | 7.151 | 0.00/0.00/0.06 | 41.92/26.30/31.71/0.00/0.00/0.00 |
| 5800 | 8/13658 | 2130796873/2132751077 | 57.15/57.20 | 4/31/31/27 | 10.495 | 0.00/0.00/0.44 | 52.73/8.47/11.02/27.35/0.00/0.00 |
| 6333 | 4/13654 | 2333271597/2335536200 | 62.58/62.64 | 4/30/30/26 | 11.742 | 0.00/0.00/0.49 | 41.92/13.88/10.90/32.81/0.00/0.00 |
| 6866 | 3/13653 | 2534744508/2539516140 | 67.98/68.11 | 4/32/32/28 | 7.379 | 3.58/0.00/0.24 | 79.29/4.13/2.99/13.34/0.00/0.00 |
| 7400 | 12/13662 | 2736046862/2738046150 | 73.38/73.43 | 4/32/32/28 | 15.924 | 9.22/0.00/0.50 | 27.88/6.12/20.54/44.96/0.00/0.00 |
| 7933 | 12/13662 | 2936108820/2941745817 | 78.75/78.90 | 4/32/32/28 | 8.766 | 0.23/0.00/0.17 | 68.09/5.69/5.74/20.30/0.00/0.00 |
| 8466 | 5/13655 | 3134377709/3142758721 | 84.06/84.29 | 4/32/32/28 | 9.370 | 0.14/0.00/0.13 | 12.87/2.28/78.66/6.05/0.00/0.00 |
| 9000 | 0/13645 | 3338161894/3343346702 | 89.53/89.67 | 4/28/28/24 | 15.013 | 0.00/0.00/0.17 | 14.85/1.68/11.33/71.97/0.00/0.00 |


### E/R1 — `P0_sift10m_T16_W16_DETAIL_R001_20261009T090745219976Z_5e1f2dfac73743a1a984257bb7570f53`


| QID | Physical N | Expanded | Pub−expanded | HOL tuple µs | IO tuple µs | TW hidden/outstanding/unpublished | Max hidden/outstanding/unpublished | Hidden>0/≥2 % | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 119 | 115 | 4 | 23.04/181.59/9037.90/9041.48 | 79.06/9048.25/9081.92/9109.77 | 2.80/7.01/9.81 | 16/16/16 | 67.74/66.05 | 0 |
| 1533 | 117 | 116 | 1 | 27.02/218.11/282.11/290.51 | 95.00/260.24/3027.75/3034.42 | 1.23/4.62/5.84 | 16/16/16 | 24.37/16.82 | 0 |
| 2066 | 120 | 114 | 6 | 26.35/91.87/159.87/173.26 | 82.39/185.39/244.15/253.55 | 2.01/5.54/7.55 | 14/16/16 | 54.80/38.30 | 0 |
| 2600 | 115 | 112 | 3 | 30.13/186.79/243.68/10034.80 | 84.30/1065.57/10024.89/10126.67 | 1.22/3.45/4.67 | 16/16/16 | 86.13/8.15 | 0 |
| 3133 | 117 | 113 | 4 | 49.01/150.10/181.22/189.17 | 86.54/200.60/234.97/263.30 | 2.86/5.25/8.11 | 14/15/16 | 58.36/47.79 | 0 |
| 3666 | 119 | 117 | 2 | 25.73/195.18/242.50/246.37 | 77.24/203.39/302.93/327.93 | 2.80/5.35/8.15 | 13/16/16 | 58.23/48.11 | 0 |
| 4200 | 122 | 121 | 1 | 14.18/159.33/254.11/331.03 | 94.00/339.97/6015.22/6104.04 | 0.69/5.21/5.90 | 15/16/16 | 16.79/13.87 | 0 |
| 4733 | 115 | 110 | 5 | 36.64/117.90/132.70/138.65 | 74.48/184.71/222.79/250.22 | 2.62/5.85/8.47 | 14/15/16 | 59.29/50.65 | 0 |
| 5266 | 121 | 119 | 2 | 16.12/1119.08/1149.85/1170.88 | 82.97/1066.93/1228.71/1237.67 | 3.50/3.67/7.17 | 16/16/16 | 60.91/53.33 | 0 |
| 5800 | 116 | 115 | 1 | 24.81/195.47/224.31/237.97 | 93.21/281.46/311.29/328.75 | 3.32/6.81/10.13 | 13/15/16 | 63.33/55.45 | 0 |
| 6333 | 114 | 112 | 2 | 27.85/10050.96/10069.08/10075.60 | 104.88/4947.55/10129.69/10144.11 | 7.37/7.33/14.70 | 16/16/16 | 78.28/75.94 | 0 |
| 6866 | 119 | 117 | 2 | 10.17/90.33/126.99/155.25 | 82.28/181.36/203.44/220.88 | 1.95/7.22/9.17 | 10/16/16 | 59.36/45.64 | 0 |
| 7400 | 126 | 123 | 3 | 23.42/160.84/200.25/202.85 | 99.36/236.03/303.71/351.72 | 2.71/6.61/9.32 | 16/16/16 | 59.53/49.14 | 0 |
| 7933 | 125 | 123 | 2 | 19.57/2449.73/3034.85/3041.73 | 84.10/3073.24/3092.01/3115.42 | 4.67/7.15/11.82 | 16/16/16 | 75.34/70.65 | 0 |
| 8466 | 123 | 122 | 1 | 18.19/12135.40/12180.43/12193.59 | 111.19/452.96/12574.88/12580.31 | 9.05/5.23/14.28 | 15/16/16 | 90.01/85.93 | 0 |
| 9000 | 119 | 118 | 1 | 23.08/108.46/122.03/123.42 | 77.63/175.28/201.24/212.60 | 2.19/6.01/8.19 | 13/16/16 | 64.54/47.00 | 0 |


| QID | Worker/TID | Start/end relative ns | Start/end phase % | Initial/final/max/change W | TW mean W | At cap/above32/unknown % | Width-bucket % 1–4/5–8/9–16/17–32/33–64/65+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 15/13822 | 395228820/410218629 | 10.11/10.50 | 4/16/16/12 | 10.901 | 5.59/0.00/0.09 | 31.13/1.16/67.63/0.00/0.00/0.00 |
| 1533 | 1/13808 | 588494730/593826617 | 15.06/15.19 | 4/16/16/12 | 6.398 | 16.67/0.00/0.18 | 77.45/1.47/20.90/0.00/0.00/0.00 |
| 2066 | 0/13802 | 792434838/794580491 | 20.28/20.33 | 4/16/16/12 | 8.944 | 28.15/0.00/0.48 | 43.64/9.61/46.27/0.00/0.00/0.00 |
| 2600 | 15/13822 | 1003969737/1017197610 | 25.69/26.03 | 4/16/16/12 | 4.906 | 5.54/0.00/0.07 | 90.25/2.03/7.65/0.00/0.00/0.00 |
| 3133 | 6/13813 | 1210217236/1212563444 | 30.97/31.03 | 4/16/16/12 | 9.649 | 31.30/0.00/0.74 | 35.75/8.67/54.84/0.00/0.00/0.00 |
| 3666 | 14/13821 | 1406013062/1408278920 | 35.98/36.03 | 4/16/16/12 | 10.431 | 33.48/0.00/0.42 | 36.15/4.16/59.27/0.00/0.00/0.00 |
| 4200 | 13/13820 | 1612612224/1621070219 | 41.26/41.48 | 4/16/16/12 | 14.289 | 82.83/0.00/0.12 | 12.16/1.04/86.67/0.00/0.00/0.00 |
| 4733 | 4/13811 | 1828175273/1830002542 | 46.78/46.82 | 4/16/16/12 | 10.039 | 37.93/0.00/0.53 | 28.86/21.02/49.59/0.00/0.00/0.00 |
| 5266 | 6/13813 | 2032213140/2037420882 | 52.00/52.13 | 4/16/16/12 | 8.518 | 35.54/0.00/0.26 | 59.13/3.01/37.60/0.00/0.00/0.00 |
| 5800 | 15/13822 | 2228131746/2230157471 | 57.01/57.06 | 4/16/16/12 | 11.370 | 49.77/0.00/0.48 | 26.16/10.29/63.07/0.00/0.00/0.00 |
| 6333 | 4/13811 | 2430496961/2444762018 | 62.19/62.55 | 4/16/16/12 | 14.925 | 90.09/0.00/0.07 | 8.03/0.52/91.38/0.00/0.00/0.00 |
| 6866 | 2/13809 | 2630349013/2631941698 | 67.30/67.34 | 4/16/16/12 | 10.528 | 47.28/0.00/0.67 | 35.57/7.42/56.34/0.00/0.00/0.00 |
| 7400 | 8/13815 | 2839384514/2841592634 | 72.65/72.71 | 4/16/16/12 | 11.636 | 51.24/0.00/0.77 | 24.14/9.38/65.71/0.00/0.00/0.00 |
| 7933 | 5/13812 | 3063380430/3068805071 | 78.38/78.52 | 4/16/16/12 | 13.095 | 72.46/0.00/0.16 | 19.50/4.03/76.30/0.00/0.00/0.00 |
| 8466 | 1/13808 | 3274326932/3289569863 | 83.78/84.17 | 4/16/16/12 | 14.520 | 85.59/0.00/0.08 | 9.51/2.30/88.11/0.00/0.00/0.00 |
| 9000 | 12/13819 | 3484261601/3486153605 | 89.15/89.20 | 4/16/16/12 | 9.682 | 36.76/0.00/0.45 | 41.32/8.69/49.54/0.00/0.00/0.00 |


### B/R2 — `P0_sift10m_T8_W32_DETAIL_R002_20261009T090758807894Z_173653e489504dd18a3793b2c6467b39`


| QID | Physical N | Expanded | Pub−expanded | HOL tuple µs | IO tuple µs | TW hidden/outstanding/unpublished | Max hidden/outstanding/unpublished | Hidden>0/≥2 % | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 118 | 115 | 3 | 24.11/186.47/216.38/253.66 | 122.68/287.23/329.35/346.35 | 3.13/7.22/10.34 | 14/20/26 | 64.79/47.77 | 0 |
| 1533 | 119 | 118 | 1 | 49.45/216.99/270.52/287.52 | 93.03/262.93/305.48/359.26 | 3.07/5.01/8.08 | 17/19/21 | 62.67/43.80 | 0 |
| 2066 | 123 | 119 | 4 | 41.69/201.66/254.69/289.77 | 89.17/205.56/221.49/366.84 | 2.92/5.75/8.67 | 18/21/25 | 60.46/44.70 | 0 |
| 2600 | 118 | 114 | 4 | 42.09/262.29/325.41/336.03 | 110.70/318.51/415.89/435.50 | 3.16/5.56/8.72 | 18/16/20 | 55.88/47.32 | 0 |
| 3133 | 119 | 118 | 1 | 35.93/176.71/262.38/386.94 | 97.11/224.91/420.49/473.30 | 2.94/5.44/8.38 | 19/22/25 | 63.62/51.15 | 0 |
| 3666 | 119 | 114 | 5 | 47.19/158.47/229.91/236.04 | 86.13/224.93/268.39/278.00 | 3.43/6.56/9.99 | 16/20/26 | 69.14/52.36 | 0 |
| 4200 | 122 | 119 | 3 | 35.14/258.84/286.24/343.13 | 114.05/264.84/358.76/402.33 | 3.12/5.28/8.40 | 21/18/21 | 54.55/43.43 | 0 |
| 4733 | 115 | 109 | 6 | 75.60/260.71/296.43/306.97 | 105.62/328.10/372.48/378.46 | 3.71/5.37/9.09 | 17/19/23 | 73.20/69.19 | 0 |
| 5266 | 119 | 116 | 3 | 51.16/241.78/284.24/291.45 | 116.32/310.64/350.33/358.81 | 3.13/5.50/8.63 | 13/16/23 | 64.74/55.47 | 0 |
| 5800 | 117 | 117 | 0 | 64.20/317.99/394.56/446.43 | 133.69/273.79/346.02/561.72 | 4.70/7.19/11.89 | 26/21/26 | 65.61/55.50 | 0 |
| 6333 | 114 | 113 | 1 | 39.47/215.22/264.90/333.68 | 104.23/236.53/347.26/408.72 | 2.50/4.72/7.22 | 16/20/21 | 69.43/50.00 | 0 |
| 6866 | 119 | 119 | 0 | 33.99/229.88/294.36/323.00 | 118.49/293.56/362.39/395.89 | 2.83/5.79/8.62 | 16/17/23 | 63.92/53.39 | 0 |
| 7400 | 124 | 119 | 5 | 44.88/140.85/173.06/174.78 | 107.79/232.31/272.03/295.62 | 2.83/6.01/8.83 | 19/20/25 | 65.81/52.25 | 0 |
| 7933 | 126 | 122 | 4 | 39.69/300.97/335.50/347.93 | 105.43/246.75/387.98/452.34 | 3.01/5.02/8.03 | 18/26/26 | 55.26/41.66 | 0 |
| 8466 | 122 | 122 | 0 | 58.06/286.88/353.01/405.35 | 106.24/243.87/383.56/488.60 | 3.40/5.50/8.90 | 21/21/25 | 67.27/55.55 | 0 |
| 9000 | 126 | 121 | 5 | 46.54/340.36/383.32/407.66 | 103.71/316.84/428.96/477.69 | 4.11/5.15/9.26 | 17/18/20 | 71.90/52.99 | 0 |


| QID | Worker/TID | Start/end relative ns | Start/end phase % | Initial/final/max/change W | TW mean W | At cap/above32/unknown % | Width-bucket % 1–4/5–8/9–16/17–32/33–64/65+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 4/13945 | 336622284/338832890 | 10.25/10.32 | 4/32/32/28 | 13.306 | 2.74/0.00/0.35 | 38.41/5.35/20.71/35.19/0.00/0.00 |
| 1533 | 3/13944 | 511093270/513977136 | 15.57/15.66 | 4/28/28/24 | 10.058 | 0.00/0.00/0.25 | 51.15/7.70/15.02/25.88/0.00/0.00 |
| 2066 | 5/13946 | 684492214/686797939 | 20.85/20.92 | 4/32/32/28 | 10.658 | 0.39/0.00/0.35 | 48.58/5.74/24.24/21.09/0.00/0.00 |
| 2600 | 2/13943 | 859462591/862291312 | 26.18/26.27 | 4/26/26/22 | 11.111 | 0.00/0.00/0.34 | 38.35/7.91/23.98/29.43/0.00/0.00 |
| 3133 | 2/13943 | 1036062046/1038632326 | 31.56/31.64 | 4/29/29/25 | 10.923 | 0.00/0.00/0.38 | 45.18/11.91/18.08/24.45/0.00/0.00 |
| 3666 | 2/13943 | 1212081444/1214066157 | 36.92/36.98 | 4/32/32/28 | 13.076 | 0.58/0.00/0.50 | 35.36/6.75/24.06/33.33/0.00/0.00 |
| 4200 | 1/13942 | 1384081559/1387105180 | 42.16/42.25 | 4/29/29/25 | 11.538 | 0.00/0.00/0.36 | 45.64/5.87/12.92/35.22/0.00/0.00 |
| 4733 | 6/13947 | 1560331831/1563129360 | 47.53/47.61 | 4/29/29/25 | 12.113 | 0.00/0.00/0.34 | 29.93/16.15/25.79/27.79/0.00/0.00 |
| 5266 | 6/13947 | 1733370625/1736387507 | 52.80/52.89 | 4/30/30/26 | 11.302 | 0.00/0.00/0.31 | 39.19/17.11/12.87/30.52/0.00/0.00 |
| 5800 | 1/13942 | 1909149456/1911606921 | 58.15/58.23 | 4/29/29/25 | 13.482 | 0.00/0.00/0.38 | 34.50/4.94/21.68/38.50/0.00/0.00 |
| 6333 | 5/13946 | 2081272499/2084206832 | 63.40/63.49 | 4/29/29/25 | 8.767 | 0.00/0.00/0.24 | 49.39/14.91/18.23/17.24/0.00/0.00 |
| 6866 | 6/13947 | 2259590740/2262420774 | 68.83/68.91 | 4/31/31/27 | 12.290 | 0.00/0.00/0.59 | 37.83/10.81/19.34/31.44/0.00/0.00 |
| 7400 | 4/13945 | 2432171676/2434614417 | 74.08/74.16 | 4/32/32/28 | 13.257 | 5.65/0.00/0.41 | 38.70/5.29/21.33/34.27/0.00/0.00 |
| 7933 | 1/13942 | 2607521199/2610708775 | 79.43/79.52 | 4/32/32/28 | 12.871 | 8.12/0.00/0.28 | 44.53/7.65/16.78/30.76/0.00/0.00 |
| 8466 | 0/13936 | 2780614052/2783453691 | 84.70/84.78 | 4/30/30/26 | 10.934 | 0.00/0.00/0.24 | 44.99/11.22/13.35/30.21/0.00/0.00 |
| 9000 | 2/13943 | 2954145168/2957314262 | 89.98/90.08 | 4/27/27/23 | 10.988 | 0.00/0.00/0.45 | 37.91/5.10/34.78/21.76/0.00/0.00 |


### C/R2 — `P0_sift10m_T8_W64_DETAIL_R002_20261009T090811753452Z_9558dd9363b14356a8eec25f3eba65e2`


| QID | Physical N | Expanded | Pub−expanded | HOL tuple µs | IO tuple µs | TW hidden/outstanding/unpublished | Max hidden/outstanding/unpublished | Hidden>0/≥2 % | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 118 | 113 | 5 | 42.12/192.24/226.90/234.95 | 100.22/257.41/308.11/321.50 | 3.37/6.43/9.80 | 18/20/23 | 54.92/43.73 | 0 |
| 1533 | 120 | 119 | 1 | 54.84/186.92/250.09/255.66 | 106.99/292.63/327.59/330.87 | 2.76/5.47/8.24 | 16/16/22 | 62.59/47.30 | 0 |
| 2066 | 120 | 117 | 3 | 81.37/209.56/262.67/295.98 | 100.76/274.81/328.57/368.94 | 3.46/5.20/8.66 | 19/20/22 | 66.01/56.86 | 0 |
| 2600 | 117 | 115 | 2 | 14.98/281.31/382.47/385.58 | 109.72/210.17/312.28/475.14 | 2.72/6.51/9.23 | 14/26/28 | 54.39/41.56 | 0 |
| 3133 | 120 | 118 | 2 | 50.62/269.25/292.06/301.58 | 84.53/220.25/370.84/412.10 | 3.75/5.30/9.05 | 19/18/23 | 61.98/53.31 | 0 |
| 3666 | 120 | 117 | 3 | 48.99/286.38/312.52/359.21 | 83.20/262.36/413.77/424.61 | 3.77/5.32/9.08 | 17/19/20 | 65.59/51.97 | 0 |
| 4200 | 123 | 121 | 2 | 69.27/288.75/318.84/321.30 | 124.53/338.89/385.28/399.91 | 3.37/5.41/8.78 | 20/18/23 | 70.02/51.26 | 0 |
| 4733 | 114 | 109 | 5 | 40.58/136.50/168.61/189.91 | 90.99/248.19/276.62/293.63 | 2.27/5.50/7.76 | 16/21/22 | 64.48/40.25 | 0 |
| 5266 | 124 | 121 | 3 | 86.80/196.57/233.87/282.55 | 106.17/239.31/305.46/382.78 | 4.31/6.41/10.72 | 21/21/23 | 68.47/56.72 | 0 |
| 5800 | 117 | 117 | 0 | 70.92/227.07/315.21/354.90 | 107.50/287.74/357.44/430.52 | 4.23/6.34/10.58 | 18/17/24 | 68.42/60.43 | 0 |
| 6333 | 119 | 118 | 1 | 45.92/214.24/318.42/334.74 | 99.21/255.31/331.50/412.49 | 3.15/5.14/8.28 | 16/18/23 | 64.23/51.38 | 0 |
| 6866 | 118 | 116 | 2 | 53.48/153.88/196.05/213.77 | 99.74/212.47/309.68/349.29 | 2.72/5.76/8.48 | 19/17/22 | 57.52/50.24 | 0 |
| 7400 | 123 | 118 | 5 | 51.12/179.78/192.10/199.18 | 91.33/229.58/275.72/280.64 | 3.02/5.22/8.23 | 21/19/23 | 56.97/44.85 | 0 |
| 7933 | 125 | 122 | 3 | 65.03/328.08/380.87/392.98 | 87.97/277.95/422.42/465.34 | 4.07/4.85/8.92 | 18/21/23 | 61.30/49.02 | 0 |
| 8466 | 120 | 116 | 4 | 48.89/208.87/224.27/225.07 | 108.62/282.07/316.08/338.94 | 3.63/6.24/9.87 | 23/22/28 | 76.37/48.77 | 0 |
| 9000 | 126 | 122 | 4 | 81.54/324.47/383.50/386.11 | 88.82/317.11/407.28/463.89 | 4.37/5.25/9.62 | 20/18/23 | 68.32/62.46 | 0 |


| QID | Worker/TID | Start/end relative ns | Start/end phase % | Initial/final/max/change W | TW mean W | At cap/above32/unknown % | Width-bucket % 1–4/5–8/9–16/17–32/33–64/65+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 1/14041 | 332094609/334319472 | 10.20/10.27 | 4/31/31/27 | 12.244 | 0.00/0.00/0.44 | 40.77/4.23/20.73/33.84/0.00/0.00 |
| 1533 | 0/14035 | 504097376/506981717 | 15.48/15.57 | 4/28/28/24 | 10.561 | 0.00/0.00/0.25 | 44.71/10.55/19.64/24.85/0.00/0.00 |
| 2066 | 2/14042 | 679613184/682515597 | 20.87/20.96 | 4/25/25/21 | 11.959 | 0.00/0.00/0.31 | 36.92/5.21/26.06/31.50/0.00/0.00 |
| 2600 | 2/14042 | 853159588/855346497 | 26.20/26.27 | 4/36/36/32 | 14.290 | 0.00/16.11/0.40 | 42.30/9.57/11.98/19.64/16.11/0.00 |
| 3133 | 0/14035 | 1026261315/1028756524 | 31.51/31.59 | 4/26/26/22 | 10.834 | 0.00/0.00/0.40 | 41.32/17.52/11.30/29.45/0.00/0.00 |
| 3666 | 3/14043 | 1200036238/1202682579 | 36.85/36.93 | 4/27/27/23 | 11.742 | 0.00/0.00/0.60 | 36.18/5.42/29.53/28.28/0.00/0.00 |
| 4200 | 1/14041 | 1373629458/1377165290 | 42.18/42.29 | 4/27/27/23 | 10.924 | 0.00/0.00/0.41 | 44.62/11.74/13.15/30.08/0.00/0.00 |
| 4733 | 7/14047 | 1545492235/1547842014 | 47.46/47.53 | 4/30/30/26 | 11.005 | 0.00/0.00/0.45 | 38.34/19.27/17.16/24.79/0.00/0.00 |
| 5266 | 7/14047 | 1719194821/1721568711 | 52.79/52.87 | 4/28/28/24 | 12.804 | 0.00/0.00/0.44 | 26.44/11.13/25.64/36.34/0.00/0.00 |
| 5800 | 6/14046 | 1892680972/1895183131 | 58.12/58.20 | 4/27/27/23 | 12.031 | 0.00/0.00/0.44 | 32.37/11.89/20.23/35.06/0.00/0.00 |
| 6333 | 5/14045 | 2065982803/2068776244 | 63.44/63.53 | 4/26/26/22 | 9.850 | 0.00/0.00/0.26 | 49.43/10.27/20.51/19.53/0.00/0.00 |
| 6866 | 3/14043 | 2238560198/2240996882 | 68.74/68.82 | 4/28/28/24 | 10.867 | 0.00/0.00/0.45 | 45.66/6.58/20.28/27.03/0.00/0.00 |
| 7400 | 1/14041 | 2410998842/2413708140 | 74.04/74.12 | 4/29/29/25 | 12.246 | 0.00/0.00/0.40 | 38.50/9.29/17.69/34.13/0.00/0.00 |
| 7933 | 7/14047 | 2583956157/2586943595 | 79.35/79.44 | 4/31/31/27 | 12.569 | 0.00/0.00/0.31 | 38.00/2.08/31.13/28.48/0.00/0.00 |
| 8466 | 5/14045 | 2756531709/2758922996 | 84.65/84.72 | 4/33/33/29 | 11.969 | 0.00/0.36/0.27 | 45.47/7.01/16.65/30.24/0.36/0.00 |
| 9000 | 7/14047 | 2931428342/2934469786 | 90.02/90.11 | 4/28/28/24 | 12.886 | 0.00/0.00/0.33 | 33.14/9.06/18.50/38.97/0.00/0.00 |


### D/R2 — `P0_sift10m_T16_W32_DETAIL_R002_20261009T090824680245Z_ec1828e5847b461994c840e09dfa7b11`


| QID | Physical N | Expanded | Pub−expanded | HOL tuple µs | IO tuple µs | TW hidden/outstanding/unpublished | Max hidden/outstanding/unpublished | Hidden>0/≥2 % | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 118 | 112 | 6 | 26.09/182.98/3372.66/4047.69 | 77.92/250.51/4037.35/4187.10 | 2.25/4.47/6.72 | 19/23/23 | 85.00/79.97 | 0 |
| 1533 | 116 | 114 | 2 | 27.29/6049.39/6081.60/6082.58 | 100.50/6063.63/6160.49/8217.93 | 3.44/4.89/8.33 | 19/20/22 | 42.32/40.01 | 0 |
| 2066 | 120 | 116 | 4 | 23.86/169.94/191.00/198.09 | 85.79/195.56/270.53/6028.63 | 0.77/2.30/3.07 | 23/20/26 | 12.78/10.26 | 0 |
| 2600 | 117 | 116 | 1 | 26.24/126.77/6108.17/6122.88 | 83.16/191.81/6149.99/6188.20 | 4.35/4.58/8.93 | 16/22/26 | 90.29/85.25 | 0 |
| 3133 | 118 | 115 | 3 | 40.52/189.79/224.69/239.43 | 100.90/233.95/318.29/355.04 | 3.50/6.30/9.80 | 20/25/26 | 57.02/47.87 | 0 |
| 3666 | 121 | 116 | 5 | 18.55/162.69/6127.78/6134.61 | 88.27/201.96/269.10/6201.23 | 3.70/2.37/6.08 | 16/21/27 | 87.96/85.09 | 0 |
| 4200 | 120 | 118 | 2 | 32.44/164.02/223.46/238.91 | 110.96/318.66/438.04/483.07 | 2.08/5.39/7.47 | 16/20/22 | 56.74/47.23 | 0 |
| 4733 | 115 | 109 | 6 | 8.30/125.37/202.60/3044.06 | 196.38/4021.64/4041.07/4043.96 | 0.66/9.95/10.60 | 13/17/20 | 35.85/6.74 | 0 |
| 5266 | 124 | 121 | 3 | 23.47/3045.32/3067.81/3081.30 | 83.78/5969.64/5986.81/5989.94 | 3.53/11.96/15.49 | 18/20/23 | 36.24/35.40 | 0 |
| 5800 | 115 | 114 | 1 | 40.05/164.60/195.40/196.11 | 95.96/277.80/6025.17/6032.44 | 0.78/4.39/5.17 | 20/19/26 | 15.06/13.98 | 0 |
| 6333 | 118 | 116 | 2 | 32.59/174.81/240.37/3093.61 | 99.28/253.14/3145.90/3180.21 | 1.92/4.29/6.22 | 17/20/23 | 85.85/20.17 | 0 |
| 6866 | 120 | 118 | 2 | 16.75/130.75/165.34/184.53 | 83.01/197.55/234.52/259.40 | 2.58/7.18/9.76 | 20/24/27 | 48.56/39.07 | 0 |
| 7400 | 126 | 121 | 5 | 31.29/155.32/174.90/179.22 | 85.92/178.44/242.43/260.11 | 3.05/6.71/9.76 | 20/21/26 | 56.06/42.95 | 0 |
| 7933 | 128 | 125 | 3 | 32.89/136.44/161.08/169.88 | 84.45/195.66/272.62/319.92 | 2.33/5.32/7.66 | 21/21/24 | 52.75/37.68 | 0 |
| 8466 | 122 | 122 | 0 | 16.62/208.09/234.78/244.74 | 87.00/254.42/307.55/328.72 | 2.99/6.04/9.03 | 21/21/25 | 55.17/40.73 | 0 |
| 9000 | 124 | 118 | 6 | 25.74/126.33/166.99/195.39 | 95.01/230.79/6034.93/6035.86 | 0.65/4.67/5.31 | 15/21/24 | 15.90/11.28 | 0 |


| QID | Worker/TID | Start/end relative ns | Start/end phase % | Initial/final/max/change W | TW mean W | At cap/above32/unknown % | Width-bucket % 1–4/5–8/9–16/17–32/33–64/65+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 15/14150 | 378968397/385234792 | 9.84/10.00 | 4/29/29/25 | 7.503 | 0.00/0.00/0.17 | 18.32/66.87/5.37/9.27/0.00/0.00 |
| 1533 | 8/14143 | 587994316/605308810 | 15.26/15.71 | 4/24/24/20 | 11.336 | 0.00/0.00/0.05 | 58.76/1.30/1.78/38.11/0.00/0.00 |
| 2066 | 4/14139 | 793248780/801249920 | 20.59/20.80 | 4/30/30/26 | 24.614 | 0.00/0.00/0.13 | 11.72/2.42/3.61/82.12/0.00/0.00 |
| 2600 | 13/14148 | 1001210570/1008985335 | 25.99/26.19 | 4/32/32/28 | 9.539 | 0.18/0.00/0.12 | 9.08/2.86/82.05/5.89/0.00/0.00 |
| 3133 | 1/14136 | 1207007459/1209157390 | 31.33/31.39 | 4/31/31/27 | 13.558 | 0.00/0.00/0.51 | 28.07/9.71/28.03/33.67/0.00/0.00 |
| 3666 | 7/14142 | 1406518455/1414395950 | 36.51/36.72 | 4/32/32/28 | 27.853 | 78.41/0.00/0.12 | 9.37/1.73/2.77/86.01/0.00/0.00 |
| 4200 | 1/14136 | 1617608997/1620604741 | 41.99/42.07 | 4/31/31/27 | 9.704 | 0.00/0.00/0.56 | 41.61/21.21/17.01/19.62/0.00/0.00 |
| 4733 | 1/14136 | 1825882875/1836989701 | 47.40/47.69 | 4/27/27/23 | 12.002 | 0.00/0.00/0.14 | 10.68/1.07/72.30/15.81/0.00/0.00 |
| 5266 | 6/14141 | 2032208389/2042747937 | 52.76/53.03 | 4/29/29/25 | 17.036 | 0.00/0.00/0.09 | 3.92/1.64/3.97/90.39/0.00/0.00 |
| 5800 | 11/14146 | 2235141529/2243561119 | 58.03/58.24 | 4/29/29/25 | 5.977 | 0.00/0.00/0.14 | 84.99/3.15/3.73/7.99/0.00/0.00 |
| 6333 | 0/14130 | 2444936138/2450162178 | 63.47/63.61 | 4/27/27/23 | 7.630 | 0.00/0.00/0.18 | 70.29/6.27/9.56/13.69/0.00/0.00 |
| 6866 | 7/14142 | 2648496553/2650184709 | 68.76/68.80 | 4/32/32/28 | 13.062 | 3.84/0.00/0.51 | 34.34/12.84/16.96/35.36/0.00/0.00 |
| 7400 | 0/14130 | 2850270735/2852167062 | 73.99/74.04 | 4/32/32/28 | 15.141 | 8.15/0.00/0.50 | 26.71/12.91/13.05/46.83/0.00/0.00 |
| 7933 | 1/14136 | 3049520558/3052030352 | 79.17/79.23 | 4/32/32/28 | 13.654 | 0.51/0.00/0.46 | 44.44/2.58/15.50/37.01/0.00/0.00 |
| 8466 | 1/14136 | 3252138996/3254505387 | 84.43/84.49 | 4/30/30/26 | 11.239 | 0.00/0.00/0.49 | 46.02/3.20/23.64/26.65/0.00/0.00 |
| 9000 | 15/14150 | 3462174253/3470204806 | 89.88/90.09 | 4/32/32/28 | 6.641 | 2.89/0.00/0.11 | 83.22/3.08/2.71/10.88/0.00/0.00 |


### E/R2 — `P0_sift10m_T16_W16_DETAIL_R002_20261009T090838270423Z_cf1cf85115b044feb826c9c94400a48f`


| QID | Physical N | Expanded | Pub−expanded | HOL tuple µs | IO tuple µs | TW hidden/outstanding/unpublished | Max hidden/outstanding/unpublished | Hidden>0/≥2 % | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 119 | 114 | 5 | 27.75/209.33/2517.71/3031.95 | 113.91/268.12/2577.24/3131.36 | 2.31/4.03/6.35 | 13/16/16 | 87.72/82.20 | 0 |
| 1533 | 119 | 119 | 0 | 74.01/231.85/256.89/305.18 | 96.91/256.77/323.28/376.77 | 3.58/4.95/8.53 | 16/15/16 | 67.80/60.16 | 0 |
| 2066 | 121 | 116 | 5 | 20.08/99.69/125.09/173.59 | 85.06/188.00/243.96/265.39 | 1.77/5.64/7.41 | 12/15/16 | 62.01/37.17 | 0 |
| 2600 | 116 | 113 | 3 | 23.29/210.50/3180.97/3224.33 | 87.58/217.67/302.06/3296.30 | 3.98/3.05/7.03 | 13/16/16 | 84.79/76.49 | 0 |
| 3133 | 118 | 116 | 2 | 20.34/189.69/6087.64/6098.08 | 84.22/8971.76/8991.31/8999.94 | 1.73/5.88/7.61 | 15/15/16 | 43.58/41.56 | 0 |
| 3666 | 121 | 119 | 2 | 26.59/112.78/167.98/3015.32 | 76.71/201.65/3072.74/3087.63 | 1.43/3.87/5.29 | 13/16/16 | 79.37/15.51 | 0 |
| 4200 | 122 | 119 | 3 | 37.13/196.29/229.36/238.23 | 95.62/223.28/293.37/352.60 | 2.79/5.70/8.49 | 16/15/16 | 59.79/44.24 | 0 |
| 4733 | 114 | 109 | 5 | 12.25/119.38/144.38/160.09 | 75.64/169.88/224.80/250.36 | 2.02/6.05/8.08 | 12/16/16 | 56.91/44.64 | 0 |
| 5266 | 120 | 118 | 2 | 2.11/129.43/163.78/289.00 | 121.67/276.15/358.53/379.87 | 0.90/6.65/7.55 | 16/15/16 | 39.14/17.55 | 0 |
| 5800 | 115 | 114 | 1 | 30.36/2607.41/8076.70/8093.83 | 106.03/273.70/7062.79/8161.73 | 5.23/2.95/8.18 | 14/16/16 | 89.65/87.02 | 0 |
| 6333 | 114 | 113 | 1 | 17.25/122.14/139.64/148.16 | 79.02/194.78/220.74/234.13 | 2.02/5.79/7.81 | 14/15/16 | 61.45/36.89 | 0 |
| 6866 | 118 | 118 | 0 | 22.51/671.62/3042.08/3054.76 | 93.59/3098.08/3133.17/3137.43 | 4.63/6.86/11.48 | 13/16/16 | 83.56/77.72 | 0 |
| 7400 | 121 | 116 | 5 | 4.21/179.33/210.63/241.35 | 93.80/412.56/495.39/503.52 | 1.65/6.50/8.15 | 16/16/16 | 52.24/40.25 | 0 |
| 7933 | 125 | 124 | 1 | 10.06/69.78/151.48/173.35 | 80.75/182.50/238.96/6118.64 | 0.34/2.12/2.45 | 14/15/16 | 13.88/8.28 | 0 |
| 8466 | 122 | 122 | 0 | 17.55/142.57/165.05/185.45 | 78.56/248.20/3068.52/3076.68 | 0.89/4.69/5.58 | 14/16/16 | 22.37/18.51 | 0 |
| 9000 | 117 | 115 | 2 | 1.64/3.55/4.00/4.40 | 5978.71/5996.90/5997.80/5998.49 | 0.00/6.85/6.86 | 13/13/13 | 0.04/0.04 | 0 |


| QID | Worker/TID | Start/end relative ns | Start/end phase % | Initial/final/max/change W | TW mean W | At cap/above32/unknown % | Width-bucket % 1–4/5–8/9–16/17–32/33–64/65+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 2/14296 | 375654287/380770372 | 9.79/9.93 | 4/16/16/12 | 6.998 | 18.70/0.00/0.18 | 69.79/3.49/26.55/0.00/0.00/0.00 |
| 1533 | 2/14296 | 566502671/569362406 | 14.77/14.84 | 4/16/16/12 | 10.049 | 36.36/0.00/0.32 | 34.05/15.04/50.58/0.00/0.00/0.00 |
| 2066 | 14/14308 | 765976714/768189488 | 19.97/20.03 | 4/16/16/12 | 8.977 | 33.07/0.00/0.36 | 48.05/7.89/43.69/0.00/0.00/0.00 |
| 2600 | 1/14295 | 962653139/967845523 | 25.10/25.23 | 4/16/16/12 | 13.501 | 73.61/0.00/0.17 | 16.56/2.79/80.47/0.00/0.00/0.00 |
| 3133 | 9/14303 | 1158827585/1176011691 | 30.21/30.66 | 4/16/16/12 | 7.887 | 4.49/0.00/0.07 | 4.67/88.37/6.89/0.00/0.00/0.00 |
| 3666 | 7/14301 | 1367981710/1373252681 | 35.66/35.80 | 4/16/16/12 | 5.966 | 12.37/0.00/0.18 | 75.22/7.54/17.06/0.00/0.00/0.00 |
| 4200 | 14/14308 | 1578961086/1581388447 | 41.16/41.23 | 4/16/16/12 | 9.830 | 38.40/0.00/0.38 | 40.97/8.20/50.44/0.00/0.00/0.00 |
| 4733 | 10/14304 | 1785957692/1787681263 | 46.56/46.60 | 4/16/16/12 | 10.498 | 44.55/0.00/0.61 | 37.14/6.64/55.61/0.00/0.00/0.00 |
| 5266 | 12/14306 | 1999057093/2001716980 | 52.11/52.18 | 4/16/16/12 | 9.285 | 26.10/0.00/0.43 | 38.17/14.58/46.83/0.00/0.00/0.00 |
| 5800 | 1/14295 | 2199839445/2210211273 | 57.35/57.62 | 4/16/16/12 | 8.461 | 5.90/0.00/0.10 | 7.11/79.40/13.38/0.00/0.00/0.00 |
| 6333 | 11/14305 | 2402721709/2404622199 | 62.64/62.69 | 4/16/16/12 | 9.097 | 32.54/0.00/0.55 | 46.60/4.92/47.93/0.00/0.00/0.00 |
| 6866 | 14/14308 | 2600915929/2605872381 | 67.81/67.93 | 4/16/16/12 | 13.780 | 76.87/0.00/0.18 | 14.30/3.07/82.45/0.00/0.00/0.00 |
| 7400 | 5/14299 | 2807655876/2810541726 | 73.19/73.27 | 4/16/16/12 | 9.905 | 30.62/0.00/0.40 | 29.38/19.82/50.40/0.00/0.00/0.00 |
| 7933 | 9/14303 | 3024681117/3033081996 | 78.85/79.07 | 4/16/16/12 | 5.615 | 10.67/0.00/0.13 | 83.27/3.11/13.49/0.00/0.00/0.00 |
| 8466 | 0/14289 | 3238529892/3243632004 | 84.43/84.56 | 4/16/16/12 | 6.244 | 14.08/0.00/0.18 | 76.93/3.23/19.66/0.00/0.00/0.00 |
| 9000 | 15/14309 | 3447852081/3549872163 | 89.88/92.54 | 4/15/15/11 | 7.240 | 0.00/0.00/0.01 | 41.13/23.53/35.34/0.00/0.00/0.00 |


### A/R2 — `P0_sift10m_T1_W32_DETAIL_R002_20261009T090851915127Z_26e438181cf842babec2fbbc54cdf19d`


| QID | Physical N | Expanded | Pub−expanded | HOL tuple µs | IO tuple µs | TW hidden/outstanding/unpublished | Max hidden/outstanding/unpublished | Hidden>0/≥2 % | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 119 | 116 | 3 | 7.09/40.87/48.15/56.05 | 60.93/105.32/110.08/116.63 | 1.36/7.44/8.80 | 10/23/26 | 48.51/29.05 | 0 |
| 1533 | 122 | 119 | 3 | 7.05/90.53/137.89/140.06 | 64.15/112.52/159.24/202.25 | 2.31/7.08/9.38 | 20/21/24 | 40.46/34.69 | 0 |
| 2066 | 121 | 116 | 5 | 7.11/51.34/71.09/78.37 | 67.06/107.86/127.25/145.92 | 1.41/7.58/8.99 | 14/24/25 | 44.58/28.04 | 0 |
| 2600 | 118 | 114 | 4 | 10.30/63.01/80.36/85.56 | 70.04/119.98/144.21/149.17 | 1.98/7.04/9.01 | 15/22/25 | 47.70/31.82 | 0 |
| 3133 | 119 | 118 | 1 | 6.59/48.04/59.05/60.81 | 70.20/110.30/124.87/126.22 | 1.68/8.08/9.77 | 17/24/30 | 42.68/30.05 | 0 |
| 3666 | 121 | 117 | 4 | 7.78/67.00/83.55/85.05 | 60.15/116.28/146.84/148.73 | 1.90/7.20/9.10 | 19/24/28 | 43.08/29.68 | 0 |
| 4200 | 123 | 123 | 0 | 2.26/102.19/140.52/165.68 | 70.04/162.81/233.28/250.16 | 2.37/7.43/9.80 | 18/23/28 | 48.36/34.26 | 0 |
| 4733 | 116 | 111 | 5 | 9.09/81.80/93.83/115.19 | 61.27/106.44/146.71/154.50 | 2.17/6.91/9.09 | 16/21/22 | 55.95/34.56 | 0 |
| 5266 | 123 | 120 | 3 | 4.97/87.82/97.98/106.28 | 66.37/105.75/156.42/190.58 | 2.22/6.92/9.13 | 23/23/27 | 42.23/31.26 | 0 |
| 5800 | 117 | 117 | 0 | 14.19/92.24/99.04/120.09 | 69.99/137.61/168.58/193.68 | 3.03/8.81/11.83 | 18/23/28 | 44.05/38.15 | 0 |
| 6333 | 119 | 118 | 1 | 7.68/80.26/97.13/100.45 | 69.66/129.26/160.82/175.93 | 2.27/7.51/9.78 | 17/24/28 | 42.02/33.75 | 0 |
| 6866 | 120 | 119 | 1 | 7.40/89.63/102.16/106.17 | 70.81/141.21/164.18/194.00 | 2.48/7.78/10.26 | 18/29/29 | 46.09/30.63 | 0 |
| 7400 | 123 | 117 | 6 | 4.30/58.01/73.46/82.01 | 64.79/111.38/141.20/151.62 | 1.29/6.54/7.84 | 15/22/26 | 36.36/28.72 | 0 |
| 7933 | 128 | 124 | 4 | 0.39/62.07/68.58/73.98 | 62.42/114.52/133.27/152.68 | 1.62/6.98/8.60 | 13/21/27 | 32.63/28.06 | 0 |
| 8466 | 123 | 122 | 1 | 2.47/69.95/79.03/82.53 | 65.87/111.46/139.81/142.65 | 1.51/6.69/8.20 | 16/23/25 | 34.50/27.12 | 0 |
| 9000 | 125 | 117 | 8 | 9.73/88.89/110.90/112.33 | 69.69/117.05/151.02/183.84 | 2.76/8.32/11.08 | 24/26/29 | 45.66/32.67 | 0 |


| QID | Worker/TID | Start/end relative ns | Start/end phase % | Initial/final/max/change W | TW mean W | At cap/above32/unknown % | Width-bucket % 1–4/5–8/9–16/17–32/33–64/65+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 0/14407 | 1157713800/1158827304 | 10.12/10.13 | 4/32/32/28 | 12.047 | 4.54/0.00/0.59 | 48.77/5.24/13.79/31.62/0.00/0.00 |
| 1533 | 0/14407 | 1765396495/1766647608 | 15.43/15.44 | 4/31/31/27 | 12.248 | 0.00/0.00/0.58 | 47.14/5.81/10.98/35.48/0.00/0.00 |
| 2066 | 0/14407 | 2373333175/2374458330 | 20.74/20.75 | 4/32/32/28 | 11.432 | 5.54/0.00/0.57 | 46.36/9.14/15.55/28.39/0.00/0.00 |
| 2600 | 0/14407 | 2984945922/2986219835 | 26.09/26.10 | 4/32/32/28 | 11.745 | 0.57/0.00/0.53 | 41.64/11.55/15.84/30.43/0.00/0.00 |
| 3133 | 0/14407 | 3601575515/3602655271 | 31.48/31.49 | 4/32/32/28 | 13.056 | 11.82/0.00/0.68 | 42.16/10.55/13.07/33.54/0.00/0.00 |
| 3666 | 0/14407 | 4209033587/4210202339 | 36.79/36.80 | 4/32/32/28 | 12.481 | 6.22/0.00/0.64 | 49.52/5.71/8.67/35.46/0.00/0.00 |
| 4200 | 0/14407 | 4820575862/4821894245 | 42.13/42.14 | 4/32/32/28 | 13.967 | 12.80/0.00/0.65 | 51.01/4.43/5.84/38.06/0.00/0.00 |
| 4733 | 0/14407 | 5433045738/5434186083 | 47.48/47.49 | 4/32/32/28 | 13.476 | 5.21/0.00/0.97 | 34.16/8.01/19.02/37.85/0.00/0.00 |
| 5266 | 0/14407 | 6042629540/6043887739 | 52.81/52.82 | 4/32/32/28 | 13.000 | 9.36/0.00/0.79 | 46.03/6.48/12.65/34.05/0.00/0.00 |
| 5800 | 0/14407 | 6646491415/6647513116 | 58.09/58.10 | 4/32/32/28 | 14.292 | 1.39/0.00/1.11 | 38.54/7.67/9.64/43.03/0.00/0.00 |
| 6333 | 0/14407 | 7249595692/7250787303 | 63.36/63.37 | 4/32/32/28 | 12.503 | 6.31/0.00/0.77 | 47.40/9.72/9.80/32.32/0.00/0.00 |
| 6866 | 0/14407 | 7858666732/7859896942 | 68.68/68.69 | 4/32/32/28 | 13.566 | 9.44/0.00/0.77 | 45.48/7.85/7.94/37.96/0.00/0.00 |
| 7400 | 0/14407 | 8464366016/8465724663 | 73.98/73.99 | 4/32/32/28 | 13.140 | 9.18/0.00/0.77 | 44.98/4.96/17.06/32.23/0.00/0.00 |
| 7933 | 0/14407 | 9083009327/9084300948 | 79.38/79.40 | 4/32/32/28 | 14.473 | 18.50/0.00/0.79 | 42.58/4.85/13.29/38.48/0.00/0.00 |
| 8466 | 0/14407 | 9692748294/9694045769 | 84.71/84.72 | 4/32/32/28 | 11.551 | 5.56/0.00/0.80 | 46.34/9.84/17.04/25.99/0.00/0.00 |
| 9000 | 0/14407 | 10305696041/10306807337 | 90.07/90.08 | 4/32/32/28 | 14.343 | 9.93/0.00/0.91 | 44.13/6.78/8.91/39.27/0.00/0.00 |


### C/R3 — `P0_sift10m_T8_W64_DETAIL_R003_20261009T090913467983Z_b8e232939106482d80394119803dee62`


| QID | Physical N | Expanded | Pub−expanded | HOL tuple µs | IO tuple µs | TW hidden/outstanding/unpublished | Max hidden/outstanding/unpublished | Hidden>0/≥2 % | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 118 | 115 | 3 | 30.47/193.99/212.08/228.75 | 102.99/229.09/289.17/315.92 | 3.05/6.17/9.22 | 18/18/23 | 65.15/46.98 | 0 |
| 1533 | 124 | 121 | 3 | 63.64/225.33/280.69/288.77 | 132.08/275.42/331.18/358.69 | 4.34/8.26/12.60 | 20/24/28 | 67.37/58.21 | 0 |
| 2066 | 120 | 116 | 4 | 41.13/206.82/234.97/307.64 | 95.01/208.58/375.89/402.93 | 3.08/4.99/8.07 | 16/19/22 | 60.63/46.18 | 0 |
| 2600 | 117 | 116 | 1 | 8.07/128.54/151.85/205.71 | 118.37/234.14/279.63/290.37 | 2.02/7.18/9.19 | 13/21/25 | 55.84/30.59 | 0 |
| 3133 | 119 | 118 | 1 | 36.10/194.39/231.50/274.33 | 98.91/249.13/344.69/412.84 | 2.73/5.37/8.11 | 18/17/22 | 65.09/50.35 | 0 |
| 3666 | 121 | 118 | 3 | 41.19/160.61/191.77/198.01 | 100.47/201.69/283.37/333.24 | 2.71/5.50/8.21 | 20/21/22 | 61.96/41.42 | 0 |
| 4200 | 123 | 120 | 3 | 60.78/217.02/323.93/389.26 | 111.92/301.75/396.21/457.83 | 3.15/5.66/8.82 | 21/20/22 | 64.15/54.73 | 0 |
| 4733 | 116 | 111 | 5 | 37.67/145.44/213.06/250.19 | 98.60/256.72/309.86/326.22 | 2.75/6.20/8.96 | 18/22/24 | 63.45/51.52 | 0 |
| 5266 | 123 | 120 | 3 | 58.38/288.60/409.25/426.79 | 98.64/291.02/458.77/531.56 | 4.97/6.03/10.99 | 22/17/25 | 70.28/60.74 | 0 |
| 5800 | 116 | 115 | 1 | 50.43/315.91/363.43/372.73 | 109.84/308.69/400.31/441.85 | 4.55/7.07/11.63 | 17/20/25 | 62.77/55.00 | 0 |
| 6333 | 118 | 116 | 2 | 55.59/219.92/265.34/342.45 | 106.18/252.72/383.85/432.57 | 2.66/5.45/8.11 | 20/22/25 | 65.26/48.37 | 0 |
| 6866 | 120 | 117 | 3 | 25.07/116.18/146.98/149.20 | 96.57/195.88/239.84/251.52 | 2.15/6.00/8.15 | 13/20/23 | 56.25/42.84 | 0 |
| 7400 | 122 | 116 | 6 | 44.23/287.27/312.81/338.09 | 94.43/270.73/371.43/408.15 | 3.38/4.76/8.13 | 16/18/20 | 63.10/51.46 | 0 |
| 7933 | 126 | 119 | 7 | 22.76/255.03/357.90/429.74 | 104.09/207.13/361.62/500.97 | 2.53/5.19/7.73 | 18/25/30 | 61.16/50.15 | 0 |
| 8466 | 122 | 122 | 0 | 36.32/467.77/494.31/513.58 | 103.43/291.11/534.84/608.58 | 3.81/4.90/8.70 | 16/18/21 | 63.86/54.31 | 0 |
| 9000 | 123 | 118 | 5 | 80.30/303.83/319.45/370.21 | 101.20/281.99/336.80/439.22 | 4.43/5.68/10.12 | 22/20/22 | 63.25/49.61 | 0 |


| QID | Worker/TID | Start/end relative ns | Start/end phase % | Initial/final/max/change W | TW mean W | At cap/above32/unknown % | Width-bucket % 1–4/5–8/9–16/17–32/33–64/65+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 1/14510 | 334659869/336924721 | 10.22/10.29 | 4/28/28/24 | 11.508 | 0.00/0.00/0.42 | 47.16/4.35/14.93/33.14/0.00/0.00 |
| 1533 | 0/14501 | 511223160/513408807 | 15.61/15.68 | 4/38/38/34 | 15.908 | 0.00/6.43/0.34 | 23.57/14.06/13.78/41.81/6.43/0.00 |
| 2066 | 7/14516 | 684278585/687016647 | 20.90/20.98 | 4/30/30/26 | 11.112 | 0.00/0.00/0.32 | 33.18/18.50/21.99/26.00/0.00/0.00 |
| 2600 | 2/14511 | 860324493/862508072 | 26.27/26.34 | 4/33/33/29 | 11.832 | 0.00/0.59/0.77 | 43.36/5.92/21.78/27.57/0.59/0.00 |
| 3133 | 5/14514 | 1036712813/1039374184 | 31.66/31.74 | 4/28/28/24 | 9.754 | 0.00/0.00/0.30 | 45.37/9.03/25.34/19.97/0.00/0.00 |
| 3666 | 6/14515 | 1213750678/1216274681 | 37.07/37.15 | 4/30/30/26 | 10.182 | 0.00/0.00/0.38 | 46.04/11.99/14.90/26.70/0.00/0.00 |
| 4200 | 4/14513 | 1387644299/1390560146 | 42.38/42.47 | 4/30/30/26 | 11.417 | 0.00/0.00/0.28 | 50.56/5.11/10.49/33.56/0.00/0.00 |
| 4733 | 4/14513 | 1560115908/1562303643 | 47.65/47.71 | 4/31/31/27 | 12.249 | 0.00/0.00/0.35 | 31.90/16.00/18.82/32.93/0.00/0.00 |
| 5266 | 2/14511 | 1733133356/1735708462 | 52.93/53.01 | 4/31/31/27 | 15.285 | 0.00/0.00/0.55 | 18.75/14.82/20.98/44.89/0.00/0.00 |
| 5800 | 4/14513 | 1906335477/1908542596 | 58.22/58.29 | 4/30/30/26 | 13.224 | 0.00/0.00/0.55 | 29.43/9.43/18.02/42.56/0.00/0.00 |
| 6333 | 5/14514 | 2081340700/2084052075 | 63.56/63.65 | 4/28/28/24 | 11.626 | 0.00/0.00/0.35 | 48.08/3.01/20.94/27.62/0.00/0.00 |
| 6866 | 5/14514 | 2255265516/2257444024 | 68.88/68.94 | 4/29/29/25 | 9.991 | 0.00/0.00/0.41 | 49.31/7.20/22.05/21.03/0.00/0.00 |
| 7400 | 7/14516 | 2428327514/2431450041 | 74.16/74.26 | 4/29/29/25 | 10.583 | 0.00/0.00/0.28 | 41.18/8.97/26.49/23.09/0.00/0.00 |
| 7933 | 2/14511 | 2602511705/2605414268 | 79.48/79.57 | 4/40/40/36 | 14.888 | 0.00/19.22/0.24 | 39.67/6.23/21.35/13.29/19.22/0.00 |
| 8466 | 6/14515 | 2774125518/2777320204 | 84.72/84.82 | 4/28/28/24 | 10.567 | 0.00/0.00/0.24 | 36.21/11.37/35.74/16.45/0.00/0.00 |
| 9000 | 4/14513 | 2948622456/2951341512 | 90.05/90.13 | 4/30/30/26 | 13.019 | 0.00/0.00/0.27 | 33.69/5.66/20.35/40.04/0.00/0.00 |


### D/R3 — `P0_sift10m_T16_W32_DETAIL_R003_20261009T090926554555Z_c464404c71f841da9867fda7d26a71e4`


| QID | Physical N | Expanded | Pub−expanded | HOL tuple µs | IO tuple µs | TW hidden/outstanding/unpublished | Max hidden/outstanding/unpublished | Hidden>0/≥2 % | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 117 | 114 | 3 | 28.74/193.18/208.15/216.12 | 83.71/231.67/279.32/6002.95 | 0.73/2.36/3.08 | 19/23/26 | 12.73/10.51 | 0 |
| 1533 | 119 | 118 | 1 | 19.74/183.85/3474.22/4245.97 | 86.21/230.83/3536.93/4326.37 | 1.88/2.78/4.66 | 15/20/22 | 72.08/68.33 | 0 |
| 2066 | 122 | 119 | 3 | 19.94/117.14/130.06/141.07 | 75.94/165.28/217.22/238.62 | 2.19/5.64/7.83 | 15/18/19 | 52.29/33.18 | 0 |
| 2600 | 117 | 115 | 2 | 13.79/7052.82/7118.45/7121.09 | 93.66/7049.72/7195.60/7207.09 | 5.80/12.64/18.43 | 22/18/22 | 91.03/86.36 | 0 |
| 3133 | 117 | 112 | 5 | 33.27/148.14/173.05/178.55 | 75.98/176.55/220.73/247.57 | 2.71/5.59/8.30 | 17/20/22 | 52.74/37.69 | 0 |
| 3666 | 119 | 112 | 7 | 32.53/175.08/207.94/233.71 | 78.05/203.10/425.46/450.37 | 2.20/4.62/6.82 | 18/20/23 | 45.15/35.80 | 0 |
| 4200 | 122 | 120 | 2 | 23.05/203.24/311.66/358.17 | 96.52/383.91/450.18/505.09 | 2.39/7.16/9.56 | 20/21/24 | 61.34/47.20 | 0 |
| 4733 | 114 | 107 | 7 | 36.96/209.16/236.58/238.84 | 104.25/258.42/301.89/331.60 | 4.16/7.48/11.64 | 21/21/27 | 66.02/49.02 | 0 |
| 5266 | 119 | 116 | 3 | 8.52/1787.52/6029.61/6052.64 | 112.47/6037.44/6100.31/6118.44 | 4.41/11.74/16.16 | 21/22/23 | 87.46/83.74 | 0 |
| 5800 | 117 | 117 | 0 | 36.77/121.17/136.43/137.74 | 87.60/215.26/887.98/888.77 | 1.70/5.30/7.01 | 13/16/22 | 46.44/32.74 | 0 |
| 6333 | 117 | 115 | 2 | 9.35/115.70/149.51/6030.34 | 102.91/6101.96/6133.88/6137.24 | 1.22/10.51/11.73 | 14/21/27 | 86.62/8.85 | 0 |
| 6866 | 118 | 117 | 1 | 1.60/164.92/187.28/191.78 | 176.09/1048.57/2841.70/2873.36 | 0.37/4.97/5.34 | 15/13/16 | 9.89/8.48 | 0 |
| 7400 | 127 | 122 | 5 | 29.06/104.68/122.66/126.89 | 80.71/178.00/207.57/295.38 | 2.48/6.59/9.07 | 22/25/26 | 60.85/41.55 | 0 |
| 7933 | 128 | 125 | 3 | 18.47/151.35/171.00/174.89 | 86.61/223.84/6074.77/6095.88 | 0.65/4.45/5.10 | 20/22/26 | 14.58/9.78 | 0 |
| 8466 | 122 | 122 | 0 | 18.57/134.03/166.25/210.58 | 77.28/168.22/215.96/291.57 | 2.26/5.33/7.60 | 18/19/22 | 53.81/43.03 | 0 |
| 9000 | 127 | 123 | 4 | 36.71/8069.28/8133.56/8145.27 | 98.01/6102.15/8065.76/8214.66 | 4.89/5.17/10.06 | 19/20/26 | 89.58/52.20 | 0 |


| QID | Worker/TID | Start/end relative ns | Start/end phase % | Initial/final/max/change W | TW mean W | At cap/above32/unknown % | Width-bucket % 1–4/5–8/9–16/17–32/33–64/65+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 14/14666 | 395407111/403056712 | 10.10/10.30 | 4/30/30/26 | 6.153 | 0.00/0.00/0.13 | 85.57/1.25/2.96/10.08/0.00/0.00 |
| 1533 | 2/14654 | 600370227/607930049 | 15.34/15.53 | 4/28/28/24 | 5.863 | 0.00/0.00/0.12 | 83.38/3.26/6.18/7.06/0.00/0.00 |
| 2066 | 11/14663 | 805963119/807945069 | 20.59/20.64 | 4/29/29/25 | 10.099 | 0.00/0.00/0.58 | 40.21/12.53/29.09/17.59/0.00/0.00 |
| 2600 | 4/14656 | 1026548687/1035817193 | 26.23/26.47 | 4/28/28/24 | 19.124 | 0.00/0.00/0.12 | 12.63/1.87/2.98/82.41/0.00/0.00 |
| 3133 | 11/14663 | 1249492970/1251454393 | 31.93/31.98 | 4/25/25/21 | 10.894 | 0.00/0.00/1.07 | 41.94/7.74/22.14/27.11/0.00/0.00 |
| 3666 | 3/14655 | 1454928860/1457571096 | 37.18/37.24 | 4/32/32/28 | 9.374 | 0.51/0.00/0.46 | 54.93/8.30/14.84/21.48/0.00/0.00 |
| 4200 | 3/14655 | 1650174249/1652601108 | 42.16/42.23 | 4/31/31/27 | 12.637 | 0.00/0.00/0.70 | 41.44/11.88/11.71/34.26/0.00/0.00 |
| 4733 | 0/14647 | 1846941729/1848804033 | 47.19/47.24 | 4/32/32/28 | 15.354 | 4.19/0.00/0.51 | 25.32/8.34/19.76/46.07/0.00/0.00 |
| 5266 | 1/14653 | 2047851478/2057209800 | 52.33/52.56 | 4/30/30/26 | 16.866 | 0.00/0.00/0.12 | 22.67/1.37/3.20/72.65/0.00/0.00 |
| 5800 | 11/14663 | 2256345760/2259215428 | 57.65/57.73 | 4/27/27/23 | 8.282 | 0.00/0.00/0.39 | 60.46/7.82/16.29/15.04/0.00/0.00 |
| 6333 | 1/14653 | 2473565569/2481612292 | 63.20/63.41 | 4/30/30/26 | 24.265 | 0.00/0.00/0.12 | 13.88/1.07/4.21/80.71/0.00/0.00 |
| 6866 | 13/14665 | 2680925993/2687911727 | 68.50/68.68 | 4/20/20/16 | 6.372 | 0.00/0.00/0.21 | 69.19/8.24/16.75/5.62/0.00/0.00 |
| 7400 | 3/14655 | 2889041855/2890895493 | 73.82/73.87 | 4/32/32/28 | 14.585 | 11.33/0.00/0.57 | 31.74/11.51/14.76/41.41/0.00/0.00 |
| 7933 | 10/14662 | 3095628634/3104002020 | 79.10/79.31 | 4/32/32/28 | 6.405 | 0.93/0.00/0.14 | 83.35/4.71/2.16/9.63/0.00/0.00 |
| 8466 | 5/14657 | 3311691306/3313784341 | 84.62/84.67 | 4/28/28/24 | 9.538 | 0.00/0.00/0.52 | 49.08/7.96/25.09/17.35/0.00/0.00 |
| 9000 | 6/14658 | 3521575701/3538605054 | 89.98/90.42 | 4/31/31/27 | 19.611 | 0.00/0.00/0.08 | 4.32/36.37/3.40/55.83/0.00/0.00 |


### E/R3 — `P0_sift10m_T16_W16_DETAIL_R003_20261009T090940260645Z_c0ea5e3b7ab14326968122c1b077c908`


| QID | Physical N | Expanded | Pub−expanded | HOL tuple µs | IO tuple µs | TW hidden/outstanding/unpublished | Max hidden/outstanding/unpublished | Hidden>0/≥2 % | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 119 | 116 | 3 | 14.88/78.61/115.96/6022.49 | 79.56/163.77/6014.46/6143.96 | 1.20/3.82/5.02 | 10/16/16 | 91.28/9.32 | 0 |
| 1533 | 120 | 119 | 1 | 47.27/380.30/2556.60/3056.42 | 99.31/300.14/2563.11/3126.08 | 2.46/3.39/5.85 | 14/16/16 | 82.30/77.72 | 0 |
| 2066 | 124 | 119 | 5 | 23.56/129.61/6029.70/6035.01 | 82.94/6088.81/6158.27/6179.45 | 3.49/10.18/13.67 | 15/16/16 | 84.92/82.64 | 0 |
| 2600 | 118 | 114 | 4 | 18.07/164.56/187.54/189.75 | 76.28/233.50/9017.50/9026.39 | 0.41/4.36/4.78 | 16/16/16 | 9.29/6.28 | 0 |
| 3133 | 119 | 118 | 1 | 22.39/138.14/186.86/191.23 | 77.86/195.37/264.27/291.99 | 2.57/6.12/8.69 | 15/16/16 | 52.47/39.11 | 0 |
| 3666 | 120 | 118 | 2 | 47.77/207.58/262.75/303.08 | 98.36/352.50/3048.33/3054.96 | 1.48/5.00/6.48 | 14/16/16 | 31.10/22.95 | 0 |
| 4200 | 122 | 121 | 1 | 20.48/137.98/227.90/344.89 | 101.99/294.68/451.93/507.36 | 2.10/6.15/8.25 | 12/16/16 | 62.22/46.98 | 0 |
| 4733 | 115 | 111 | 4 | 112.61/286.83/330.33/3140.86 | 83.36/356.61/3205.49/3341.90 | 1.82/2.50/4.32 | 15/16/16 | 55.92/19.04 | 0 |
| 5266 | 120 | 118 | 2 | 44.80/155.09/179.35/205.02 | 84.39/211.68/265.75/278.11 | 2.72/5.42/8.14 | 15/16/16 | 67.87/48.22 | 0 |
| 5800 | 116 | 115 | 1 | 19.97/151.81/6040.36/6076.34 | 87.39/6094.95/6150.68/6161.21 | 2.81/9.74/12.55 | 14/16/16 | 88.12/84.60 | 0 |
| 6333 | 116 | 113 | 3 | 45.11/256.29/6027.09/6029.99 | 91.05/321.08/6093.06/6163.11 | 4.26/4.38/8.64 | 13/16/16 | 88.63/85.20 | 0 |
| 6866 | 116 | 113 | 3 | 8.33/214.78/258.59/267.16 | 79.91/252.96/327.55/339.13 | 3.34/6.37/9.71 | 15/16/16 | 59.18/43.49 | 0 |
| 7400 | 120 | 115 | 5 | 9.56/151.03/189.32/190.58 | 87.04/162.33/262.38/7059.29 | 0.54/2.04/2.58 | 16/16/16 | 13.28/9.41 | 0 |
| 7933 | 125 | 123 | 2 | 4.79/122.70/3041.49/3045.82 | 118.74/6027.94/6063.05/6069.75 | 0.61/4.29/4.90 | 16/16/16 | 16.33/15.05 | 0 |
| 8466 | 123 | 122 | 1 | 44.13/201.55/243.63/8045.24 | 83.32/260.28/8071.58/8127.59 | 1.47/3.44/4.91 | 16/15/16 | 90.72/12.82 | 0 |
| 9000 | 120 | 120 | 0 | 46.91/212.07/240.11/293.95 | 85.95/228.63/346.83/358.00 | 3.34/5.55/8.88 | 15/16/16 | 67.70/51.75 | 0 |


| QID | Worker/TID | Start/end relative ns | Start/end phase % | Initial/final/max/change W | TW mean W | At cap/above32/unknown % | Width-bucket % 1–4/5–8/9–16/17–32/33–64/65+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 1/14824 | 375009806/382559087 | 9.95/10.15 | 4/16/16/12 | 5.373 | 9.15/0.00/0.13 | 86.63/1.38/11.86/0.00/0.00/0.00 |
| 1533 | 2/14825 | 570216141/576363966 | 15.12/15.29 | 4/16/16/12 | 6.286 | 14.13/0.00/0.17 | 70.06/11.79/17.97/0.00/0.00/0.00 |
| 2066 | 9/14832 | 766756687/774995204 | 20.34/20.55 | 4/16/16/12 | 14.097 | 82.47/0.00/0.11 | 12.67/3.20/84.03/0.00/0.00/0.00 |
| 2600 | 14/14837 | 967032917/977814068 | 25.65/25.93 | 4/16/16/12 | 5.006 | 6.72/0.00/0.10 | 89.89/0.99/9.02/0.00/0.00/0.00 |
| 3133 | 1/14824 | 1175436696/1177262906 | 31.18/31.22 | 4/16/16/12 | 10.310 | 33.52/0.00/0.55 | 33.48/6.33/59.64/0.00/0.00/0.00 |
| 3666 | 6/14829 | 1378822548/1384130213 | 36.57/36.71 | 4/16/16/12 | 7.051 | 18.93/0.00/0.22 | 70.24/2.52/27.01/0.00/0.00/0.00 |
| 4200 | 6/14829 | 1578562014/1581084135 | 41.87/41.93 | 4/16/16/12 | 10.167 | 46.97/0.00/0.43 | 43.39/4.09/52.08/0.00/0.00/0.00 |
| 4733 | 6/14829 | 1777351419/1786481182 | 47.14/47.38 | 4/16/16/12 | 10.212 | 44.51/0.00/0.13 | 42.17/2.52/55.19/0.00/0.00/0.00 |
| 5266 | 8/14831 | 1973926053/1976254553 | 52.35/52.41 | 4/16/16/12 | 9.527 | 40.18/0.00/0.43 | 43.25/9.87/46.45/0.00/0.00/0.00 |
| 5800 | 5/14828 | 2167258804/2175208169 | 57.48/57.69 | 4/16/16/12 | 12.997 | 7.88/0.00/0.13 | 9.05/2.58/88.24/0.00/0.00/0.00 |
| 6333 | 1/14824 | 2369964922/2378607280 | 62.86/63.09 | 4/16/16/12 | 9.033 | 6.62/0.00/0.12 | 11.82/3.81/84.25/0.00/0.00/0.00 |
| 6866 | 3/14826 | 2569863791/2571918735 | 68.16/68.21 | 4/16/16/12 | 11.347 | 53.04/0.00/0.49 | 30.18/5.87/63.46/0.00/0.00/0.00 |
| 7400 | 6/14829 | 2768346707/2777591601 | 73.42/73.67 | 4/16/16/12 | 5.404 | 10.67/0.00/0.11 | 87.08/0.69/12.12/0.00/0.00/0.00 |
| 7933 | 7/14830 | 2972366208/2997742760 | 78.83/79.51 | 4/16/16/12 | 9.331 | 38.83/0.00/0.04 | 27.73/32.26/39.96/0.00/0.00/0.00 |
| 8466 | 12/14835 | 3167277855/3177980527 | 84.00/84.29 | 4/16/16/12 | 5.205 | 6.77/0.00/0.08 | 86.39/3.06/10.47/0.00/0.00/0.00 |
| 9000 | 12/14835 | 3377505000/3379848856 | 89.58/89.64 | 4/16/16/12 | 10.127 | 31.84/0.00/0.57 | 27.12/15.99/56.32/0.00/0.00/0.00 |


### A/R3 — `P0_sift10m_T1_W32_DETAIL_R003_20261009T090953949982Z_0f4a95e6e75746a6b48ecf564e1f6aa2`


| QID | Physical N | Expanded | Pub−expanded | HOL tuple µs | IO tuple µs | TW hidden/outstanding/unpublished | Max hidden/outstanding/unpublished | Hidden>0/≥2 % | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 120 | 116 | 4 | 7.08/43.93/66.09/71.37 | 63.68/111.68/117.11/134.17 | 1.50/7.58/9.08 | 16/23/27 | 51.39/28.11 | 0 |
| 1533 | 122 | 119 | 3 | 8.08/90.38/134.55/137.08 | 63.17/118.74/155.85/197.11 | 2.28/7.10/9.39 | 20/21/24 | 40.99/34.76 | 0 |
| 2066 | 121 | 117 | 4 | 7.42/51.86/73.71/95.67 | 65.57/109.08/127.29/151.86 | 1.56/7.63/9.19 | 15/25/26 | 44.00/31.21 | 0 |
| 2600 | 118 | 114 | 4 | 15.66/117.84/132.42/139.39 | 68.74/119.72/156.73/199.55 | 2.75/6.58/9.33 | 19/23/25 | 50.35/37.77 | 0 |
| 3133 | 119 | 118 | 1 | 5.30/50.49/57.88/62.34 | 69.79/109.84/112.67/126.66 | 1.51/8.02/9.53 | 13/26/29 | 45.38/27.48 | 0 |
| 3666 | 121 | 117 | 4 | 6.76/64.33/82.57/87.38 | 61.14/109.30/137.52/149.38 | 1.56/7.06/8.61 | 16/23/25 | 42.14/25.13 | 0 |
| 4200 | 123 | 123 | 0 | 7.10/96.82/116.45/182.62 | 69.86/168.02/207.32/233.54 | 2.20/7.07/9.27 | 14/20/26 | 51.21/39.62 | 0 |
| 4733 | 116 | 111 | 5 | 9.22/85.68/99.98/115.47 | 61.34/106.60/153.39/162.78 | 2.28/6.92/9.20 | 19/21/22 | 54.59/35.04 | 0 |
| 5266 | 123 | 120 | 3 | 9.23/76.89/83.24/89.63 | 64.23/112.48/146.32/167.59 | 1.91/6.82/8.72 | 23/26/29 | 41.52/25.90 | 0 |
| 5800 | 117 | 117 | 0 | 14.70/92.98/99.74/120.31 | 70.17/127.30/164.57/195.66 | 2.97/8.72/11.69 | 18/22/27 | 46.08/39.21 | 0 |
| 6333 | 119 | 118 | 1 | 7.35/84.30/102.40/107.39 | 69.66/137.42/165.20/179.68 | 2.38/7.54/9.92 | 18/24/29 | 43.20/30.17 | 0 |
| 6866 | 120 | 119 | 1 | 1.37/72.83/96.67/102.91 | 69.79/133.83/161.80/165.06 | 1.91/7.60/9.50 | 14/25/27 | 37.07/30.43 | 0 |
| 7400 | 123 | 117 | 6 | 10.32/55.87/77.50/89.62 | 63.97/115.69/141.56/153.77 | 1.88/6.74/8.62 | 20/23/25 | 42.50/30.29 | 0 |
| 7933 | 129 | 125 | 4 | 2.23/47.23/53.63/60.06 | 64.90/115.54/133.96/142.73 | 1.53/7.78/9.31 | 13/23/28 | 33.36/27.45 | 0 |
| 8466 | 121 | 121 | 0 | 7.58/61.40/91.91/95.00 | 61.53/124.45/148.67/156.79 | 1.86/6.81/8.68 | 18/20/23 | 40.76/32.30 | 0 |
| 9000 | 124 | 117 | 7 | 8.84/98.57/122.54/126.01 | 67.69/109.01/179.28/188.99 | 2.87/7.62/10.48 | 17/23/24 | 48.07/35.40 | 0 |


| QID | Worker/TID | Start/end relative ns | Start/end phase % | Initial/final/max/change W | TW mean W | At cap/above32/unknown % | Width-bucket % 1–4/5–8/9–16/17–32/33–64/65+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 0/14939 | 1157371727/1158516015 | 10.13/10.14 | 4/32/32/28 | 12.499 | 6.59/0.00/0.64 | 47.96/5.05/14.17/32.18/0.00/0.00 |
| 1533 | 0/14939 | 1769999433/1771251623 | 15.50/15.51 | 4/32/32/28 | 12.232 | 0.97/0.00/0.53 | 47.19/6.14/10.84/35.30/0.00/0.00 |
| 2066 | 0/14939 | 2375606850/2376735613 | 20.80/20.81 | 4/32/32/28 | 11.712 | 6.27/0.00/0.60 | 46.80/8.26/15.72/28.63/0.00/0.00 |
| 2600 | 0/14939 | 2993649599/2994970656 | 26.21/26.22 | 4/29/29/25 | 12.011 | 0.00/0.00/0.54 | 39.78/10.70/14.26/34.71/0.00/0.00 |
| 3133 | 0/14939 | 3599994420/3601070480 | 31.52/31.53 | 4/32/32/28 | 12.543 | 6.26/0.00/0.57 | 41.85/11.72/13.22/32.65/0.00/0.00 |
| 3666 | 0/14939 | 4205117152/4206286749 | 36.81/36.82 | 4/32/32/28 | 11.805 | 2.61/0.00/0.57 | 49.25/5.64/11.73/32.82/0.00/0.00 |
| 4200 | 0/14939 | 4809203036/4810550789 | 42.10/42.11 | 4/32/32/28 | 13.332 | 8.17/0.00/0.64 | 49.52/4.38/7.02/38.44/0.00/0.00 |
| 4733 | 0/14939 | 5411957086/5413106720 | 47.38/47.39 | 4/32/32/28 | 13.335 | 0.54/0.00/0.76 | 33.98/7.88/18.79/38.58/0.00/0.00 |
| 5266 | 0/14939 | 6018324664/6019609332 | 52.69/52.70 | 4/32/32/28 | 13.010 | 9.65/0.00/0.75 | 45.55/10.08/9.41/34.20/0.00/0.00 |
| 5800 | 0/14939 | 6624594416/6625613167 | 58.00/58.00 | 4/32/32/28 | 13.826 | 0.58/0.00/0.88 | 38.53/7.34/11.67/41.59/0.00/0.00 |
| 6333 | 0/14939 | 7231953402/7233159380 | 63.31/63.32 | 4/32/32/28 | 12.767 | 7.69/0.00/0.77 | 47.62/9.55/9.77/32.29/0.00/0.00 |
| 6866 | 0/14939 | 7838135251/7839343816 | 68.62/68.63 | 4/32/32/28 | 12.457 | 4.99/0.00/1.03 | 46.31/6.10/12.41/34.14/0.00/0.00 |
| 7400 | 0/14939 | 8449335318/8450640057 | 73.97/73.98 | 4/32/32/28 | 13.669 | 0.58/0.00/0.86 | 40.98/5.30/12.66/40.20/0.00/0.00 |
| 7933 | 0/14939 | 9071342880/9072539415 | 79.42/79.43 | 4/32/32/28 | 15.605 | 19.62/0.00/0.93 | 38.04/7.81/9.22/44.00/0.00/0.00 |
| 8466 | 0/14939 | 9677034776/9678312578 | 84.72/84.73 | 4/28/28/24 | 10.341 | 0.00/0.00/0.79 | 47.13/10.00/16.38/25.70/0.00/0.00 |
| 9000 | 0/14939 | 10284179451/10285378002 | 90.03/90.04 | 4/32/32/28 | 14.076 | 9.83/0.00/0.89 | 40.95/6.30/12.00/39.86/0.00/0.00 |


### B/R3 — `P0_sift10m_T8_W32_DETAIL_R003_20261009T091015779549Z_083b9c9a7165498d9f926e5c74e43fbb`


| QID | Physical N | Expanded | Pub−expanded | HOL tuple µs | IO tuple µs | TW hidden/outstanding/unpublished | Max hidden/outstanding/unpublished | Hidden>0/≥2 % | Zero IO denom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 119 | 116 | 3 | 39.35/208.34/287.37/289.23 | 116.05/270.62/311.86/368.08 | 2.81/6.09/8.91 | 20/20/25 | 61.25/50.31 | 0 |
| 1533 | 119 | 115 | 4 | 57.36/286.55/334.25/344.08 | 107.25/336.46/451.78/550.29 | 3.40/5.48/8.88 | 17/18/22 | 63.09/50.84 | 0 |
| 2066 | 121 | 116 | 5 | 30.87/144.06/183.02/194.10 | 94.21/218.90/278.80/301.92 | 2.59/5.89/8.48 | 15/22/24 | 65.29/46.72 | 0 |
| 2600 | 118 | 115 | 3 | 46.01/226.60/276.54/280.37 | 115.86/289.80/350.81/372.64 | 3.55/5.89/9.44 | 19/20/21 | 53.33/44.33 | 0 |
| 3133 | 119 | 117 | 2 | 61.87/234.73/345.50/374.88 | 104.94/260.86/320.98/447.52 | 3.66/5.74/9.40 | 17/18/20 | 60.47/50.32 | 0 |
| 3666 | 121 | 117 | 4 | 108.64/734.44/943.04/1079.81 | 119.08/815.67/1165.28/1214.81 | 3.94/5.23/9.17 | 18/20/20 | 82.43/64.33 | 0 |
| 4200 | 122 | 119 | 3 | 49.61/360.03/472.19/541.97 | 119.50/427.85/543.08/601.37 | 3.40/6.14/9.53 | 19/20/21 | 68.91/56.09 | 0 |
| 4733 | 116 | 111 | 5 | 35.16/192.16/248.94/251.58 | 94.20/236.57/349.41/401.70 | 2.94/6.29/9.24 | 15/19/24 | 55.81/45.13 | 0 |
| 5266 | 119 | 116 | 3 | 68.25/258.96/314.85/320.77 | 109.83/268.26/372.45/403.17 | 4.56/6.53/11.10 | 21/22/25 | 64.30/53.76 | 0 |
| 5800 | 116 | 115 | 1 | 59.94/377.14/441.42/453.28 | 94.11/301.91/465.22/529.25 | 4.87/6.37/11.25 | 17/19/23 | 62.52/59.03 | 0 |
| 6333 | 118 | 116 | 2 | 67.05/227.45/353.90/359.89 | 115.17/287.36/350.92/437.99 | 2.93/5.06/7.99 | 20/20/22 | 67.03/49.17 | 0 |
| 6866 | 120 | 118 | 2 | 61.10/255.88/323.62/340.13 | 95.97/274.33/398.13/470.31 | 3.52/5.27/8.78 | 18/22/23 | 67.11/52.04 | 0 |
| 7400 | 127 | 126 | 1 | 46.82/195.29/211.62/227.24 | 99.95/239.67/294.43/356.42 | 3.10/5.92/9.02 | 18/18/22 | 73.35/55.65 | 0 |
| 7933 | 127 | 124 | 3 | 50.36/243.48/479.57/480.31 | 113.69/333.98/466.11/546.64 | 2.55/4.68/7.23 | 23/18/24 | 60.03/47.58 | 0 |
| 8466 | 121 | 119 | 2 | 54.94/242.43/362.52/436.46 | 110.28/280.48/501.70/590.74 | 2.91/4.82/7.72 | 15/19/20 | 64.07/49.45 | 0 |
| 9000 | 120 | 116 | 4 | 88.71/307.89/353.15/362.82 | 90.71/289.27/416.16/438.18 | 3.85/4.86/8.71 | 17/19/20 | 69.22/60.81 | 0 |


| QID | Worker/TID | Start/end relative ns | Start/end phase % | Initial/final/max/change W | TW mean W | At cap/above32/unknown % | Width-bucket % 1–4/5–8/9–16/17–32/33–64/65+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 3/15128 | 332560638/335265465 | 10.20/10.28 | 4/31/31/27 | 10.979 | 0.00/0.00/0.34 | 40.64/20.29/11.36/27.36/0.00/0.00 |
| 1533 | 4/15129 | 504717073/507880996 | 15.48/15.57 | 4/27/27/23 | 11.931 | 0.00/0.00/0.32 | 39.03/8.23/21.34/31.07/0.00/0.00 |
| 2066 | 3/15128 | 676810583/679026747 | 20.75/20.82 | 4/29/29/25 | 11.268 | 0.00/0.00/0.36 | 42.23/11.53/17.58/28.31/0.00/0.00 |
| 2600 | 3/15128 | 849268397/852044380 | 26.04/26.12 | 4/25/25/21 | 12.101 | 0.00/0.00/0.38 | 34.10/11.57/16.35/37.59/0.00/0.00 |
| 3133 | 6/15131 | 1021448663/1024033235 | 31.32/31.40 | 4/25/25/21 | 11.831 | 0.00/0.00/0.43 | 28.37/13.21/31.38/26.61/0.00/0.00 |
| 3666 | 4/15129 | 1195799761/1201386408 | 36.66/36.84 | 4/27/27/23 | 10.193 | 0.00/0.00/0.29 | 28.49/13.10/43.75/14.37/0.00/0.00 |
| 4200 | 6/15131 | 1372701253/1375906706 | 42.09/42.19 | 4/28/28/24 | 12.676 | 0.00/0.00/0.31 | 37.80/6.46/15.43/40.00/0.00/0.00 |
| 4733 | 4/15129 | 1545299156/1547478625 | 47.38/47.45 | 4/30/30/26 | 13.281 | 0.00/0.00/0.54 | 34.33/8.03/16.01/41.09/0.00/0.00 |
| 5266 | 6/15131 | 1718043222/1720377396 | 52.68/52.75 | 4/30/30/26 | 14.624 | 0.00/0.00/0.44 | 34.26/5.63/12.76/46.92/0.00/0.00 |
| 5800 | 1/15126 | 1891408000/1893804059 | 57.99/58.07 | 4/27/27/23 | 12.930 | 0.00/0.00/0.43 | 31.46/9.53/14.50/44.07/0.00/0.00 |
| 6333 | 0/15120 | 2062728612/2065924683 | 63.25/63.34 | 4/27/27/23 | 9.588 | 0.00/0.00/0.24 | 45.50/16.89/17.30/20.07/0.00/0.00 |
| 6866 | 0/15120 | 2234530701/2237326899 | 68.51/68.60 | 4/28/28/24 | 10.621 | 0.00/0.00/0.27 | 40.56/16.60/14.28/28.29/0.00/0.00 |
| 7400 | 2/15127 | 2409337156/2411909586 | 73.87/73.95 | 4/31/31/27 | 12.752 | 0.00/0.00/0.49 | 28.49/12.78/26.17/32.08/0.00/0.00 |
| 7933 | 5/15130 | 2584214986/2588151005 | 79.23/79.36 | 4/31/31/27 | 9.798 | 0.00/0.00/0.21 | 61.38/4.14/9.86/24.41/0.00/0.00 |
| 8466 | 4/15129 | 2758971171/2762316982 | 84.59/84.70 | 4/28/28/24 | 9.819 | 0.00/0.00/0.41 | 41.82/10.12/30.52/17.12/0.00/0.00 |
| 9000 | 5/15130 | 2934869528/2938041213 | 89.99/90.08 | 4/26/26/22 | 10.397 | 0.00/0.00/0.40 | 31.70/18.78/28.80/20.32/0.00/0.00 |


## Verification, future experiment and stop

305 research Python tests pass, including malformed FIFO/request/query traces, equal-clock width chains, v1/v2 compatibility, negative state/counters, zero denominators, sampling/phase bins, exact D6 boundaries/median-of-ratios and missing repetitions, configuration/provenance/package/telemetry/checksum rejection, narrower-manifest runtime evidence and run/query grouping. Command:

```sh
.venv-research/bin/python -m unittest discover -s tests/research -v
git diff --check
.venv-research/bin/python tools/research/analyze_g0c2_d6.py --campaign /home/irthn/ann-research/research-v3/campaigns/G0C2_SIFT10M_20261009T090432438598Z --output /new/analysis-directory
```

**Recommended next scientific experiment:** separately authorize a controlled, semantics-audited FIFO-publication intervention or equivalent narrowly scoped timing diagnostic, predeclare matched native-placement comparisons, verify full physical/cache correlation and observer effects, and measure which HOL intervals block query-critical work. First add the minimal observational states needed to distinguish published-but-not-calc-ready, ready-but-unselected, known-unissued and issue-ready candidates described in D1_OBSERVABILITY_GAP; this is a proposal only. Use independently frozen broader/phase-replicated samples and active-query occupancy before generalizing to steady state/allqueries. No FIFO modification, D1/D4 instrumentation or implementation occurs here.

ANN source/search/FIFO/width/io_uring/golden/main unchanged, no binaries/data/index rebuilt, no SIFT100M, no novelty claim. No raw trace/CSV/telemetry/runs/MLflow DB/data/index/binary committed. Normal expected-parent fast-forward publication uses the authenticated GitHub connector because terminal Git credentials are absent. Open Draft PR and stop; do not merge or implement a solution.
