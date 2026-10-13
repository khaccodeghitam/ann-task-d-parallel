# Issue29 reproduction and acceptance

PR28 is merged into main at `5ec0841fcd04e9c06824ef3e10b59f4b08d58ed7`. This follow-up is a separate feature branch, not a rewrite of PR28. [Actual decision memo](research/ISSUE29_DECISION_MEMO.md) records thermal stop and executed offline research. Historical reports remain unchanged.

Provide external canonical base/query/GT and a **separate** paper-native disk/PQ package plus memory graph, memory `.data` and memory `.tags`. Import/verify via [artifact workflow](DATASETS_AND_ARTIFACTS.md); no data download/build is implicit. Full foreign-host data transfer and search remain **NOT_VERIFIED**.

Data-free preview (does not invoke ANN):

```sh
python tools/research/issue29_campaign.py --config configs/issue29_campaign.json --output unused --dry-run
python -m unittest discover -s tests/research -v
python scripts/check_research_docs.py
```

Historical benchmark reproduction uses its sealed original plan. Do not append to `ISSUE29_20261013T110233068975Z` or automatically launch a replacement. The following execution interface exists for a **separately authorized new campaign**, not permission to bypass this mission's thermal stop:

```sh
set -a; . ./.env; set +a
python tools/research/issue29_campaign.py --config configs/issue29_campaign.json --output "$ANN_RESEARCH_ROOT/evidence/NEW_UNIQUE_CAMPAIGN"
```

Config binds this host's stock/quality hashes; another toolchain must bind and validate its own new subject/plan, never impersonate the owner binary. No fan/power changes by software. Initial profile/policies stay fixed for every command; startup package<85°C, rich1Hz collector and independent heartbeat watchdog, unchanged99°C-once/97°C10s guard. Full9-component pre/post audits. QualificationT16 thenT8 FIRST; only then6 alternating T8/T16 blocks; post-core T16/T8 quality;3each T1/T4 references; optional12L and6W cases. Every new configuration is quality-checked before first stock use. Commands have240s cap, total3600s cap,5s gap,15s block/stage separation. No retry/automatic cooling loop. Any failure stops progression, all completed stock outputs remain PROVISIONAL under this strict frozen contract.

Offline regeneration (no ANN execution; caller supplies preserved raw file):

```sh
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python research/oracle_disagreement.py \
  --rows "$ANN_RESEARCH_ROOT/research-v3/campaigns/PAPER_BASELINE_RESEARCH_20261013T092006889480Z/real-studies-bounded/candidate_rows.csv" \
  --output "$ANN_RESEARCH_ROOT/evidence/NEW_OFFLINE_OUTPUT"
python research/summarize_issue29.py --rows "$SAVED_CANDIDATE_CSV" --output new_strata.json
python tools/research/analyze_issue29.py --campaign "$ISSUE29_HOST_CAMPAIGN" --output new_host_analysis.json
```

Rows missing? Stop that analysis; never generate substitute candidates. The original210-file archive seal verifies input rows. Hashes, plans and outputs are local authoritative evidence; compact committed summaries are derived. `analyze_issue29.py` checks sealed logs/plan, independently validates even a terminated command's saved CSV **without promoting its failure**, and repeats full content verification. On this mission stock count is0; paired effect is null. This analyzer's qualification audit does not certify a future successful full campaign by itself.

Train/validation/test retain original whole-query partitions; model list, ridge1e−3, features and controls fixed prospectively. Test was previously inspected: reused held-out audit, not pristine validation. All uncertainty resamples queries, never candidates. Saved exact-distance surrogate and synthetic service units are not nativePQ state or ANN throughput.

Tests in existing and fresh dependency-only environments:451pass each. GitHub Actions uses synthetic tests only; remote workflow execution is not asserted without verification. Foreign-host full source build/large transfer/search remain NOT_VERIFIED. Raw CSVs, quality binary, canonical data/index and original evidence stay external; no binary/data upload or license grant implied.
