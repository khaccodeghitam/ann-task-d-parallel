# Version-native comparison boundary

**VERIFIED SOURCE FACT:** Primary historical reference is official0.1.0 source d18dcd1, executed only through the explicitly labeled GCC13-portable c4cd32c variant. Secondary reference remains golden b9ec4ba. Neither modern main nor the original paper tree changed. No current version-vs-version result exists.

Even a future successful native comparison would differ in graph/PQ bytes, construction thread count4 vs8, entry mem_L10 vs0, and two L200 warmups vs no driver warmup. Same nominal R64/Lbuild100/PQ32 and identical dataset/GT do not isolate traversal code. They also do not guarantee equal recall. Compare observed recall–throughput overlap without extrapolation, and label the whole version-native system comparison. Do not attribute a delta to a candidate-pool, prefetch or lock commit without ablations.

Paper printed P99 meansP99.9; modern printed P99 meansP99. No common-tail comparison can be filled from that label. A post-timer exporter would provide distribution samples for correctness/diagnostics, but its uncalibrated timing cannot substitute for stock-like measurements.

The previously completed [47-commit source study](../paper-rebaseline-20261012/02_UPSTREAM_EVOLUTION_2025_2026.md) is preserved. Its candidate-pool/frontier reconstruction, prefetch, codecs/vector operations, runtime/locking, and non-active updates/filter/server changes are source facts or mechanistic hypotheses, not demonstrated gains in this task. The latest audited lock-table commit is secondary historical context, not a new measured binary.

**UNKNOWN:** Artifact scaling, modern/paper advantage, index compatibility loading, per-mechanism attribution. The old quiet modern−8.5096% T16/T8 belongs only to its earlier b9ec4ba campaign and host/protocol; it does not predict or measure the artifact. No OSDI100M/1B server claim is reproduced by this laptop setup.
