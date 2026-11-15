# Graph format contract v1

The implemented profile is **little-endian unsigned 32-bit IDs/fields**, matching
the inspected `Graph<unsigned int>` writer on the measured platform. Upstream
serialization uses native integer bytes and has no endian/version marker; other
endianness/ID widths require a new explicit format profile, never auto-detection.

| Field | PiPNN | NSG |
|---|---|---|
| Header | n, maximum degree | maximum degree, entry ID |
| Degrees | n consecutive uint32 degrees | degree before each node's adjacency |
| Adjacency | concatenated rows in node-ID order | n degree/adjacency records |
| Entry | not serialized; explicit common policy input | serialized; an override must match |
| Vertex count | serialized, checked against base | supplied externally from base count |
| Vectors/metric | not in graph file | not in graph file |

PiPNN source: R86 `r86_v1_2_source/algorithms/utils/graph.h`, constructor and
`save()` (lines 210–293 in the pinned file), also compared with stock/H17 copies.
NSG contract: Task D E1 source audit and `main.cpp` binding the external iQAN
loader. Upstream iQAN source/binary parity itself is NOT_VERIFIED by this PR.

For n nodes and m directed arcs both representations have `8 + 4*n + 4*m`
bytes. Similar length does not make their layout interchangeable. `C`, builder
`K`, `N`, and pruned maximum degree are distinct parameters; C160 is not a
160-degree search graph by definition. Do not derive node count from a suffix.

Reject zero vertices, missing/invalid entry, count mismatch, partial uint32,
truncated degree/edge sections, degree above header maximum, out-of-range IDs,
trailing bytes or unknown formats. Preserve self-loops, duplicate arcs, zero
degree, direction and original edge order; diagnose rather than repair them.
Reachability is exact directed BFS from the selected entry, not a strong
connectivity proof. Disconnected graphs may return fewer than k reachable IDs.

The canonical ordered digest is SHA256 of `LE32(n)` followed for each node by
`LE32(id) || LE32(degree) || LE32(neighbor_0) || ...`. Per-node digest excludes
the outer n. Entry and header maximum are separately recorded, so digest alone
does not imply entry parity. Round trip preserves the declared maximum as well.
Compare exact node byte strings, not only hashes; save before/after per-node
hashes when converting real artifacts.

Vector profile: `.fbin = LE32(n), LE32(d), n*d IEEE754 float32 row-major`.
Rows map directly to graph IDs with no normalization, reordering or quantization.
Distance = squared L2 with double accumulation over original float32 values;
ties use increasing ID. All vectors/queries must be finite. This accumulation
need not match Task A float/SIMD rankings on near ties; quality must be measured.

MS-Turing `.ibin` GT profile comes from R86 acquisition code: header (query
count, GT width), **all uint32 IDs**, then **all float32 distances**. It is not
the interleaved ID/distance profile described in Task D's old iQAN loader.
The smoke evaluator uses GT top-k ID membership, validates sampled GT rows and
does not assume that GT distances are squared L2. Whole-file hash validation and
independent exact distance spot checks remain required before a real campaign.
