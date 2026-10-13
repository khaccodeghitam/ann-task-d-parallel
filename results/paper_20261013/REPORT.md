# Paper baseline and first algorithm studies: partial mission

## Campaign validity and operating condition

**Not an accepted repeated baseline.** All18 planned core stock processes completed successfully, but the mandatory subsequent T16 quality arm reached package100°C and was terminated at1.115s, exit−15. No retry/replacement or extension was launched. **0/18 certified core,18 native-stock process outputs retained; extension0/18,18 skipped.** This certification failure does not prove the previous stock outputs were incorrect. It means the frozen quality gate did not finish, so they remain provisional.

Campaign archive ID`PAPER_BASELINE_RESEARCH_20261013T092006889480Z`; raw stock PLAN hash and pinned source/binary/package IDs are in [SUMMARY.json](SUMMARY.json). Full post-campaign nine-component audit passed. Native package remains usable and unchanged. Original successful full-fan package/first stock point remains separately valid.

All four monitor-screen and18 stock processes observed **Performance profile, MMIO PL1/PL2 115/135W**, not earlier Custom60/90W. No within-run sampled policy transition was found. Source of the pre-campaign condition change is UNKNOWN; no script changed settings. Stock maxima ranged73–98°C; late quality arm started90°C and reached100°C after1second. Sampling cannot rule out unobserved transients. Later owner mode update/reboot was recorded outside the frozen campaign, which was not resumed.

V1 ledger incorrectly attached the late quality-stage failure to last stock recordR18. Raw ledger/seal is preserved. R18's native exit0 is directly verified; failure belongs to `QUALITY_T16_W32_L100`. Prospective v2 fixes job attribution, adds a fixed5s quality gap and rejects quality startup≥85°C. No historical status is silently rewritten or promoted.

## Genuine but UNCERTIFIED stock measurements

|T/W32,L100,mem_L10|n|Median QPS|SampleSD QPS|Median mean latency,µs|Median P99.9,µs|Printed recall range,%|
|---|---:|---:|---:|---:|---:|---|
|T1|3|1696.12|1.88|546.03|801|99.23|
|T4|3|4386.41|12.01|860.69|1264|99.22|
|T8|6|5882.06|9.52|1299.80|1937.5|99.20–99.21|
|T16|6|5130.02|75.62|2984.75|72657.5|99.21|

Six provisional paired T16/T8 deltas,%: **−14.5232,−12.9745,−15.1482,−12.3765,−12.4868,−11.8735**. Median−12.7307%,mean−13.2305%,sampleSD1.3067pp; deterministic20,000 block-bootstrap CI90 **[−14.5232%,−12.1801%]**. These are derived statistics of completed outputs, **not a certified scientific result**. All values, log-ratio estimates, recall deltas and leave-one-block-out sensitivity are retained in JSON. No query/request pseudoreplication. The large T16 tail is an observation, not proof of scheduling, SSD or dependency mechanism.

[All stock rows](runs.csv), [planned/executed order](plan_order.csv), [chronological plot](chronological_qps.svg). No recall–QPS curve exists because extension was stopped, not because L was tuned. Stock P99 column is trueP99.9; P50/P95/P99 remain null. Application IO/query is about107, not device IOPS. Process-lifetime snapshots include loading/warmup; no precise search-phase CPU/NVMe attribution is made. Device-level bandwidth/await/queue telemetry was NOT_MEASURED in this minimal wrapper.

Monitor LITE–RICH–RICH–LITE retained same safety/watchdog. Two paired rich/lite QPS changes−0.4142% and−0.0407%; descriptive characterization only, no proof of negligible effect. Main stock mode uniformly rich. Observer selfCPU/collection timing remains in local logs. This small screen cannot establish precision for tail latency or all thread counts.

## MOTIF_SIGNAL_STUDY_01 and CANDIDATE_VALUE_ORACLE_01

**EXECUTED_REAL_GRAPH**, but on an independent exact-distance traversal surrogate, not replayed PipeANN/PQ state.48 queries, disjoint28/10/10 train/validation/test;96 states;1,152 candidates;2,000 uniform topology anchors;7,852 adjacency rows;95,242 exact distances. [Small results](OFFLINE_STUDIES.json). Read-only source-grounded parser validates IDs/degrees and bounded adjacency capacity. First mmap-vector attempt hit1GiB RSS guard and is preserved; engineering-only `pread` correction retained identical seed/sample/model/1GiB budget. Corrected run peaked456,676KiB RSS. No target-based sample/parameter retuning.

Sampled transitive closure opportunities5.2%,sampled cycle closure4.8%,mean edge Jaccard0.02731. These are sampled directed wedges, not global motif counts. Mean49.97 novel neighbors versus1.275 useful below-threshold neighbors;40.19% candidates had positive topK-sum utility gain. Novelty count is not exploration value.

|Model|Held-out RMSE|Mean within-state Spearman|Mean selectedGk|
|---|---:|---:|---:|
|Distance+degree+rank+history|0.032579|0.33025|0.0372703|
|+Overlap|0.032585|0.35147|0.0372703|
|Degree-stratified permuted overlap|0.032626|0.31653|0.0371479|

Overlap selected **no better candidate** than baseline on the10 held-out queries. Query-cluster selection-gain CI90[0,0] describes these unchanged choices, not universal equivalence. Oracle-best meanGk0.041455 supplies a small static upper gap over nearest choice0.037270; this is utility, **not QPS**. Exact overlap is not online-free: it requires unread adjacency or precomputed metadata;4bytes per640M directed edges costs2.56GB. Deprioritize this raw overlap feature; retain a conditional cheap H-QV feature-screening question. No deeper observer or ANN modification is justified by these results alone.

## PARALLEL_FRONTIER_SIM_01

**EXECUTED:**125 cases, five graph families×five policies×five fixed seeds, equal24-expansion budgets, p4, shared IO capacity2 and explicit scheduling/service costs. [All cases](FRONTIER_SIM.json).

- Chain: sequential and width4 both121.2575 simulated units; available-frontier span prevents parallel benefit.
- Branching: sequential121.265 vs same-budget width4 66.28 units, with recall1 in this case; random averaged recall0.8.
- Decoy dense cluster: distance batch recall0, anchor+oracle-overlap exploration recall1 within same budget; random recall0.6. This is a deliberately constructed mechanism example, not real-data improvement.
- Same-budget best-first and distance batch intentionally coincide; they are not two distinct algorithm wins.

Synthetic service units are not SSD/CPU elapsed time. A work/span lower bound is not a measured speedup. Oracle adjacency metadata cost and actual PQ frontier fidelity remain unresolved. H-F is MODEL_SUPPORTED_ONLY, empirical ANN gain UNKNOWN, novelty UNKNOWN.

## Reproduction and next decision

Feature-branch `scripts/ann.py summarize --output LOCAL_RAW_CAMPAIGN` correctly rejects the uncertified campaign. Explicit `--provisional` regenerates the labeled diagnostic statistics without new ANN execution. Offline commands and acceptance boundaries are in [roadmap](../../docs/RESEARCH_ROADMAP.md).

Keep the valid native package; do not automatically repeat this campaign. A future owner-selected stable cooling/power condition must first support prospective T16 correctness qualification, with source/binary identities unchanged. For algorithm research now, inspect saved oracle-best vs nearest-choice states and paid-feature costs offline. Raw overlap integration is NO-GO in this tested placement; H-QV remains conditional; H-F is synthetic only. D1 UNTESTED,D4 NOT TESTED,D6 INCONCLUSIVE remain unchanged. No novelty or end-to-end ANN speedup is claimed.
