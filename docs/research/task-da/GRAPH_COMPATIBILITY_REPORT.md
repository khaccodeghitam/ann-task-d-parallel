# P1 compatibility report

**Gate HOLD for A0/A3 on MS-Turing-1M. Synthetic representation checks PASS.**

Source inspection supports a lossless representation path: the PiPNN file
contains ordered directed adjacency indexed by vector row, readable directly
by the new common loader or convertible to NSG with an explicit entry point.
There is no source-level requirement to add, prune, sort or relabel edges.
This is a feasibility finding, not validation of unavailable graph bytes.

The direct loader produces CSR adjacency for both formats. The Python audit
independently parses the original files, checks structure, computes degree and
reachability diagnostics, and compares every ordered row after conversion.
The C++ executable uses the same search policy on each loaded representation.
Fixtures include asymmetric edges, duplicates, self-loops, isolated nodes, ties,
malformed input and a counterexample where a narrow beam misses a routing path.

| Check | Status | Scope |
|---|---|---|
| Source layout understood | PASS | Pinned code/docs; no graph files involved |
| PiPNN → NSG → PiPNN exact bytes | PASS | Synthetic input, including header max and adjacency order |
| Per-node adjacency equality + entry | PASS | Synthetic conversion; reordered row correctly rejected |
| Native format/ON-OFF results parity | PASS | Multiple beams and synthetic graphs |
| Independent exact L2 oracle | PASS | Connected fixture with beam=n; not approximate quality evidence |
| Truncated/malformed input rejection | PASS | Python and native tests |
| A0/A3 SHA, topology audit, smoke GT | HOLD | Graph/base/query/GT bytes unavailable |
| One common engine at p=1/2/4 | HOLD | p=1 implemented; p>1 intentionally not implemented yet |
| P1 research gate | HOLD | Cannot replace real-artifact checks with fixtures |

NO-GO is reserved for a demonstrated incompatibility requiring topology changes
or incompatible search semantics. No such research finding has been established.
The NSG-only historical loader is not directly compatible with PiPNN bytes;
renaming `.pipnn` to `.nsg` is specifically unsupported.

See [graph_audit.json](graph_audit.json) for an explicitly synthetic receipt and
[format contract](graph_format_contract.md) for the digest and metric semantics.
