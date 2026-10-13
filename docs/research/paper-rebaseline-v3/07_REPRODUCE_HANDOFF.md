# Exact handoff and preserved state

Evidence root: `/home/irthn/ann-research/research-v3/campaigns/PAPER_NATIVE_V3_SIFT10M_20261012T162845717948Z`. Versioned source/tool snapshot commit `6a420b88341fe630df415ee752095fabfb12214e`, treeafd6c6d5a41ec855db19f364dbebd4220d70afd0. Publication research commit is recorded externally in PUBLICATION.json after this documentation commit; immutable plans are not rewritten to embed it. Existing [Draft PR27](https://github.com/Irthn1311/Parallel_ANN_Research/pull/27) is extended without merging or force-push. PR23/24/25/26 remain separate.

Original paper d18dcd16fece1c9d1dea356d783ebba2ed649e54/tree8e6ee6b0dc71db7dfa9db742c2f7066929202bc2 clean/detached; portable c4cd32c6816c063f56ecc64f9d7b63c909202cab/tree23fbb256528c67454cd4348bc58dfee700dffa06 clean; golden b9ec4ba clean, binarya02ce69d1467727344c8620a254b4cba51d12616d3da171ef7c1a6668a9e8bc5 unchanged; old PipeANN-p0 actual34a485bafae48b4a53e6da4eb7996e0c22c08140 clean. No subject C++ file, source flag, FIFO, width, io_uring or host setting changed.

Both **executed failed** construction commands are preserved, not instructions to retry their prefixes:

```sh
/home/irthn/ann-research/PipeANN-paper-portable/build/tests/build_disk_index uint8 /home/irthn/ann-research/data/bigann/sift10m/canonical/base_10m.bbin /home/irthn/ann-research/indexes/sift10m-paper-v3/sift10m 64 100 0.298023223876953125 8 8 l2 0
/home/irthn/ann-research/PipeANN-paper-portable/build/tests/build_disk_index uint8 /home/irthn/ann-research/data/bigann/sift10m/canonical/base_10m.bbin /home/irthn/ann-research/indexes/sift10m-paper-v3-t4/sift10m 64 100 0.298023223876953125 8 4 l2 0
```

Actual invocation used `paper_native_v3.py --spec ... --output ...` with unchanged v2 collectors and safety rules except standalone RAPL policy changes. Initial availableRAM≥9GiB and storage≥45GiB admitted construction; stop guards remained active. Threads are user-space work limits, not host affinity/power tuning. Original sample/entry and both failed prefixes are immutable. No third attempt, resume, partial reuse, chmod or cleanup is authorized by this handoff itself.

After a suitable construction environment is available, create a new absent prefix and new predeclared contract; do not execute any of the archived blocked plans. Same builder/R64/L100/PQ-budget/M8 source/input, recorded thread choice, full stdout/stderr/resource/policy logs, and a complete disk graph are required. Only after builder success may `finalize_paper_native_index.py --evidence NEW_EVIDENCE --build-plan NEW_BUILD_PLAN.json` validate all graph coordinates/edges/PQ and copy the retained three entry components byte-for-byte. Native adapter models implicit tags. It is synthetic-tested, **not proven on a completed real native index yet**. Any emitted auxiliary components must also be identified/hashed; no such complete package was finalized here.

Then use separate post-timer probes for full10K IDs/distances/tie-aware recall. Freeze a new executable PLAN only after quality and full input/paper/modern audits pass. `run_paper_native_v3_suite.py` refuses non-ready/incorrect plans, source/binary mismatch, absent audits or full-corpus validation; no existing v3 PLAN can launch it. Production observability must include every readable power/profile state required by the final contract, not assume mode stability from one snapshot. The planned whole-process block criterion is conservative and may leave an insufficient comparable cohort; preserve that outcome.

No real standalone search command is provided as immediately safe; [02](02_SEARCH_CORRECTNESS.md) supplies the exact CLI for a future completed prefix. Legacy plans/specs do not become resumable by changing a boolean.

Reproduce code checks only:

```sh
cd /home/irthn/ann-research/Parallel_ANN_Research
.venv-research/bin/python -m unittest discover -s tests/research -v
git diff --check
```

Current390 tests PASS, including fake66-case order/pauses/checksums/analyzer and adverse safety/quality/provenance cases. Original481 v1 and103 v2 sealed evidence files verified unchanged. Canonical full pre/final-post hashes PASS; retained entry five hashes PASS. Raw evidence, telemetry, partial outputs, binaries and data stay external; Git contains small tools/tests/docs/derived blocked ledgers only.

Observer wall time is not ANN overhead: T8 median snapshot38.67ms, max48.67ms, ownCPU1.549s across60 snapshots; T4 median26.81ms, max43.97ms, ownCPU5.497s across393 snapshots. There is no profiler OFF/ON or search observer-effect measurement. Five-second sampling can miss thermal/policy transients; denied kernel-log access and sparse sensor observations do not prove global safety or causal throttling. No sudo or privilege modification was used.

Provenance limitation: the T8 launch did not capture a full Python-file fingerprint. Offline helper functions were added while its already-loaded guard/execute logic stayed unchanged; its frozen guard contract, builder hash and raw manifest remain authoritative. T4 explicitly bound wrapper SHA25633ce456cbe485d20936c7b3b8b1d2ba25148b9a66835318af1922b3b2c871def; its launch-time bytes match the subsequently versioned6a420b8 code snapshot. Do not claim6a420b8 was already the Git HEAD when T4 started. This limitation is recorded, not filled with a fabricated hash. No scientific search ran under either attempt.
