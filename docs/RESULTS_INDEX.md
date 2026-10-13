# Results index

| Evidence | Status | Meaning |
|---|---|---|
| [Issue29 qualification + oracle audit](research/ISSUE29_DECISION_MEMO.md) | SKIPPED_THERMAL / OFFLINE_EXECUTED | T16 quality PASS; T8 quality hit100°C;0 new stock runs.48-query disagreement analysis and30 synthetic controls executed; no tested cheap-feature selection gain |
| [Full-fan native package and first stock point](research/PAPER_FULLFAN_SIFT10M_20261013.md) | Verified build/search PASS | Custom60/90W; oneT8 run5863.23QPS,99.206% independent recall; no replication/CI |
| [Issue #32 Custom Full-Fan SIFT10M campaign](research/CUSTOM_FULLFAN_SIFT10M_20261013.md) | **QUALIFIED: 36/36 stock runs** | Six paired T16/T8 blocks; median −13.36%, CI90 [−14.35%, −11.49%], under Custom 60/90 W |
| [Compact campaign data](../results/custom_fullfan_20261013/SUMMARY.json) / [all stock rows](../results/custom_fullfan_20261013/runs.csv) | Qualified local campaign summary | Paper GCC13-portable subject; no direct modern comparison |
| [Earlier Issue29 partial campaign](../results/paper_20261013/REPORT.md) | PARTIAL / UNCERTIFIED | Performance 115/135 W; retained as historical evidence, not upgraded by Issue #32 |
| [Real-graph studies](../results/paper_20261013/OFFLINE_STUDIES.json) | EXECUTED_REAL_GRAPH |48-query exact-distance surrogate, no actual paper replay |
| [Frontier simulator](../results/paper_20261013/FRONTIER_SIM.json) | EXECUTED |125 synthetic cases, simulated units only |
| [Modern quiet-stock](archive/HISTORY.md) | Preserved historical evidence |12 accepted modern runs, paired−8.51%, not paper-native evidence |

Raw archive IDs (external under the workspace's `research-v3/campaigns`, no transfer promised):

- `PAPER_FULLFAN_SIFT10M_20261013T081513543576Z` —57 originally sealed files, verified before mission.
- `PAPER_BASELINE_RESEARCH_20261013T092006889480Z` —new local audit/monitor/core/studies/incident evidence.

The original native INDEX_PACKAGE hash is`7140a47ac53b0480752059b5cb428b4d56dc627533974803b5ae4413827a7470`. Failed prior prefixes are never imported as complete indexes. No SIFT1M fallback was run after10M success. PR28 was subsequently merged at`5ec0841fcd04e9c06824ef3e10b59f4b08d58ed7`; its evidence labels remain unchanged. Issue29's new evidence archive is`ISSUE29_20261013T110233068975Z`; its follow-up code/report require the new feature branch until merged.

Issue #32 raw campaign: `CUSTOM_FULLFAN_SIFT10M_20261013T115304462961Z` (36 stock runs, 12 quality invocations; external local archive). Frozen plan SHA256 `37bc6b41eb49eec856c5fd67a465bd56f327dfaeb8f28d289420b5a47e066c81`. Earlier reports retain their original labels.
