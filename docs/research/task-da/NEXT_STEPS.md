# Next executable steps and stopping conditions

1. Recover A0/A1/A3 OFF formal graphs R1–R3 and the exact base/query/split-GT files
   using the hashes in the manifest. Obtain original raw receipts, build source
   commit/diff, compiler flags and seed/randomness identity; nine sheet hashes do
   not prove nine available or reproducible files. Raw receipts and graphs stay
   external; publish compact relative-path inventories and hashes.
2. Resolve the benchmark host and guard in a new protocol. Run read-only hash and
   shape validation, exact-GT spot checks and structural audit on every graph.
   Inspect disconnectedness and zero-degree diagnostics without repairing edges.
3. Run bounded common-engine p=1 smoke on A0/A3 with both ON/OFF, direct PiPNN and
   optional NSG representation. Record actual Recall, identities and ordered-row
   parity. A positive synthetic result does not close P1. If representation needs
   topology changes, issue a scoped NO-GO instead of silently modifying graphs.
4. Once P1 passes, implement/test p=1/2/4 fixed multi-walker/staged traversal with
   local frontiers and explicit visited/merge/termination semantics. Measure ON
   overhead with a qualified control. First compare to a strong fixed baseline;
   this P1 reference implementation alone is not a strong performance competitor.
5. Execute the preregistered P3 A0/A3 × 1/4 pilot, then A1 and p=2. Keep complete
   OFF latency samples and separate ON work traces, paired order and repeats.
6. P4 diagnoses degree/work, overlap/sync, or locality. Open P5 only when that
   diagnosis supports a cheap Task D scheduling signal; otherwise report a
   scoped negative/inconclusive result. Do not extend E3 or tune thermal behavior
   to manufacture an ANN contribution.

Current disposition: P0 HOLD; P1 HOLD (synthetic PASS only); P2 partial one-worker
baseline; P3/P4 HOLD for missing prerequisites; P5/P6 NOT_OPEN. Nothing in this
PR demonstrates an ANN speedup, topology effect, multi-core benefit or novelty.
