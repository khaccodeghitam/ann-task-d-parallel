# Common engine policy and P2 boundary

`entry_best_first_v1` is an independent P1 correctness baseline, not an iQAN,
Speed-ANN, AverSearch, PiPNN Search or E3 reproduction. No external algorithm
source is linked or copied. This additive component uses the repository's MIT
license; the GPL E1/E3 engines remain separate historical references.

Single query, one worker, one explicit entry (proposed ID 0 for both A0/A3),
bounded best set of at most beam candidates and an ordered pending set. Pop the
nearest pending node, inspect its stored neighbors in order, compute squared L2
once per newly seen ID, and insert improving candidates. Eviction removes a
candidate from pending; an evicted/discovered ID is never revisited. Stop when
pending is empty, return up to k sorted unique IDs; report incomplete results
instead of padding disconnected graphs with arbitrary IDs. No hidden full scan.

With beam=n on a graph fully reachable from entry, every vertex is evaluated and
expanded once; independent brute-force top-k is the fixture oracle. With bounded
beam, exact Recall is not guaranteed (an explicit test demonstrates the miss).
Do not infer high Recall on a real graph from exhaustive-fixture correctness.

Template instantiations `search<false>`/`search<true>` remove ON counter increments
from the OFF path; both use identical candidate and termination semantics.
ON/OFF IDs and distances are tested over multiple beams. OFF JSON counters are
null, not zero. The correctness executable emits no timing/QPS and is limited
to 32 query rows per call. It loads all vectors/queries before search and uses
O(n) visited initialization per query. These costs must be included/optimized
consistently when a future timing harness is designed; current code is not
advertised as a performance baseline strong enough for improvement claims.

Counter meanings are in [counter_schema.json](counter_schema.json).
Already-seen edge attempts are not necessarily redundant expansions or useless
routing work. There are no per-worker/sync/merge/idle counters yet; they are
NOT_MEASURED rather than fabricated zeros. No tracing overhead benchmark ran.

P2 is PARTIAL implementation / HOLD research gate. Multi-walker traversal is
deferred until real P1 establishes useful reachability and measured single-worker
Recall. A future design must specify local queues, visited ownership, merge and
termination; p=1 parity, race tests and exact-oracle correctness precede p>1
benchmarks. E3's maintainer/calculator split cannot stand in for that design.
