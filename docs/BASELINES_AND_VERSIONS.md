# Baselines and versions

| Name | Source | Role |
|---|---|---|
| PAPER_STOCK | tag0.1.0, `d18dcd16fece1c9d1dea356d783ebba2ed649e54`, tree`8e6ee6b0dc71db7dfa9db742c2f7066929202bc2` | Unmodified reference source; GCC13 cannot compile its float reduction intrinsic as written |
| PAPER_GCC13_PORTABLE | owner subject`c4cd32c6816c063f56ecc64f9d7b63c909202cab`, tree`23fbb256528c67454cd4348bc58dfee700dffa06` | Actual measured paper-derived executable; only AVX2 horizontal reduction +4/−1 |
| MODERN_GOLDEN | `b9ec4ba86ff5d70bec277984777197f28dc2cf42` | Preserved2026 secondary reference, never substituted for paper |

[Portable patch](../patches/gcc13-portability.patch) preserves real-number reduction meaning; floating reassociation can affect near ties. Existing optimized and ASan/UBSan tests each covered10,000 float and6,000 uint8 cases. No bitwise identity claim. Flags: OVERLAP_INIT,DYN_PIPE_WIDTH,AVX2,OpenMP,Ofast/O3,march=native. Native memory entry and mem_L10 are required; mem_L0 must not be patched into the artifact baseline.

Owner binary SHA256s (a peer rebuild is a new binary identity):

- Paper search: `5f5fa8d99cc83b523c71b7025e5f0b9aa61f45d42816804ed6d88755ebaa310b`
- Paper disk builder: `f9f0124e737caa56aafe4441d3c42051c4f264a9412eff6e232f8baff1037e8a`
- Modern search: `a02ce69d1467727344c8620a254b4cba51d12616d3da171ef7c1a6668a9e8bc5`

## Comparison boundary

| Factor | Paper native | Historical modern |
|---|---|---|
| Index | Paper-native R64/L100/PQ32 | Modern-built R64/L100/PQ32; different bytes/semantics |
| Initialization | OVERLAP_INIT, mem_L10,100,004-node entry | mem_L0 |
| Driver warmup | Two complete L200 passes | Different/no corresponding driver warmup |
| Printed tail | labelP99, code0.999 → P99.9 | code0.99 → P99 |
| Current operating policy | Observed Custom Mode60/90W MMIO | Earlier Performance Mode conditions |

Historical modern T16/T8−8.51% is not paper evidence, not a matched paper/modern speedup and not a mechanism diagnosis. No new modern head-to-head is authorized by the current paper-only protocol. [46-commit evolution audit](research/paper-rebaseline-20261012/02_UPSTREAM_EVOLUTION_2025_2026.md) remains source context, not ablation evidence.
