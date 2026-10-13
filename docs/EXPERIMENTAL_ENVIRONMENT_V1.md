# ANN Experimental Environment v1 — Custom / Full Fan

**Status:** Prospective operating contract for new paper SIFT10M measurements. Introduced after Issue #29; **not** a retroactive relabeling or result. Read [Issue #29 decision memo](research/ISSUE29_DECISION_MEMO.md) and [benchmark method](BENCHMARK_METHOD.md).

## Why this becomes the default

The historical native SIFT10M build completed in Linux `platform_profile=custom`, with owner-confirmed full-fan setting and observed MMIO power limits **PL1/PL2 = 60/90 W**. Package temperature peaked at **69°C sampled** during that build. Subsequent independent *search* qualification in `performance`, **115/135 W**, reached **98–100°C**. These are **different workloads**, so they do **not** constitute a matched A/B performance comparison, do not establish fan RPM or attribute cooling to fans alone, and do not show Custom necessarily maximizes QPS.

**For the next series, the laboratory chooses Custom 60/90 W as a fixed, safety-oriented, reproducible operating condition.** Report this choice prominently; it is not the maximum-performance operating point for every CPU.

## Operator preparation (outside the benchmark scripts)

1. Manually choose **Custom Mode** in the Lenovo firmware/platform utility, with fan curve manually set to maximum (the script must not change it). Connect AC, elevate the laptop, maintain clear vents and stable room conditions.
2. Ensure observed Linux `/sys/firmware/acpi/platform_profile` is `custom`. Observe MMIO package power limit registers, **PL1 approximately 60 W; PL2 approximately 90 W**. These are *limits*, **not measured package consumption**. Fan RPM is `NOT_MEASURED` unless an independent supported tachometer becomes available. Record operator confirmation and timestamp separately.
3. If profile/limits are not observed correctly or hardware readings are unavailable, **do not start any qualification or stock run**. Do not ask scripts to tune/fix power, frequency, affinity, ACPI, Secure Boot or fan mode.
4. Keep owner authorization for workload execution separate from any authority to edit the laptop. No sudo and no thermal-protection bypass.

## Predeclared host gates

Use `configs/custom_fullfan_campaign.json`, which pins this contract and inherits the qualified subject/index package. The harness must verify the expected Custom/MMIO state **before initial qualification and before every subsequent invocation**. Fail closed on missing/ambiguous MMIO values, wrong profile, wrong limits (default tolerance ±1 W), host transition or missing sensors.

Preserve the Issue #29 hard safety constraints: one-hertz Intel `coretemp` package readings, independent watchdog, stop at sampled `>=99°C` once or `>=97°C` for ten seconds, critical-trip handling, startup `>=85°C` reject, AC/memory/disk/swap/foreign-process checks, and process-group cleanup. A successful qualification does not guarantee safe later runs. These safeguards may be strengthened prospectively but not weakened to get a PASS. Do not automatically retry on heat.

## Execution sequence (single Codex mission, bounded)

- New unique external evidence directory and frozen prospective plan/checksums. Re-audit canonical base/query/GT, native disk/PQ, three memory-entry components and pinned `PAPER_GCC13_PORTABLE` stock/quality binaries. **Never rebuild the 10M index by default.**
- Under the *same* Custom 60/90 W condition: independently qualify **T16/W32 then T8/W32**, K10/L100/mem_L10, 10,000 queries, verified 100,000 result rows each. Both must pass correctness, observed host guards, and identity checks. Never use quality-binary QPS as headline stock performance.
- Only after both: run **six alternating paired T8/T16 blocks = 12 stock processes**, with balanced order, short thermal gaps and post-core quality checks. Derive block-paired median/mean deltas and bootstrap uncertainty; log actual per-run recall, mean/P99.9, QPS, app I/O/query, temperatures and policy. Some QC requirements are global; if a mandatory gate fails, the completed stock runs remain PROVISIONAL.
- Conditional after core success and continued host stability: **T1 and T4 ×3 each** and **L50/75/125/150 ×3** plus **W16/W64 ×3** (18 extension runs). Independently qualify each configuration before first stock use.
- If any thermal, integrity or policy gate fails, stop host execution, **retain real evidence with honest labels**, no silent replacement/campaign continuation. Complete non-host documentation/offline analysis within the same Codex mission if useful.

## Scientific comparability

Only treat repeated runs under the same frozen profile, power limits, host and subject as one benchmark campaign. Previous Performance115/135 W results are **separate exploratory evidence**. The Custom full-fan SIFT10M construction PASS and single T8 search result are **separate evidence** from a future repeated search campaign. A new paper benchmark does not by itself compare against modern PipeANN: index/search contract and matched-recall conditions must be harmonized later. The native paper executable reports **P99.9**, even when its printed label says P99.

Once new Proposed ANN policies exist, evaluate **the baseline and the proposed method under the same Custom 60/90 W envelope**, with paired blocks, matched recall and all relevant resource/build costs. Do not privilege an idea because it is unfamiliar or because a profiler shows an unrelated bottleneck.

## Teammate reproducibility / deliverables

Use [START_HERE](START_HERE.md), [artifact provisioning](DATASETS_AND_ARTIFACTS.md) and [Issue #29 workflow](ISSUE29_WORKFLOW.md). On another machine, `custom` or identical MMIO registers may be unavailable: classify the host as **UNSUPPORTED_FOR_THIS_LOCKED_PROFILE**, require a *new separately named host protocol*, never impersonate this laptop’s run. Produce a sealed manifest, commands, actual evidence, result labels, tests and draft PR. No credentials/data/index/binary upload. Update the README/benchmark docs to point to this profile.

**Scientific lanes remain independent:** H-QV1 inexpensive feature tests have not improved held-out selection utility; H-F simulations are not ANN speedups. Do not launch source-intrusive replay or motif metadata integration as part of this thermal/baseline mission.
