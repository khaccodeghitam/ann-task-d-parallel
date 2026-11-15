# Validation receipt — synthetic only

No MS-Turing graph or real-data benchmark was run. Environment used GCC 13.3.0,
CMake 3.28.3 and Python 3.12.3. Binary SHA and final source hashes are recorded in
`validation_receipt.json`; these local binaries are not Task A's reported binaries.

| Check | Result | Scope |
|---|---|---|
| Release configure/build with warnings as errors | PASS | Isolated `research/task_da` target |
| Release CTest | PASS | 18 unittest cases, including native subprocess cases |
| ASan + UBSan | PASS | Same fixture cases, halt on errors |
| ASan + UBSan + LeakSanitizer outside process tracing | PASS | Same cases; no host configuration changes |
| Complete `tests/research` regression | PASS | 509 tests, no skips, native binary explicitly supplied |
| Missing-artifact preflight | Expected HOLD / exit 1 | 12 unavailable graph/data artifacts; no benchmark execution |
| Documentation links and whitespace | PASS | Existing active-doc checker plus new local link check |

Fixture coverage: ordered directed adjacency; duplicate/self-loop preservation;
degree histogram and exact directed reachability; isolated singleton; exact
PiPNN↔NSG round trip; per-node digests; entry and order mismatches rejected;
invalid counts/degree/IDs and every truncated prefix; no overwrite; multiple
bounded beams with ON/OFF and representation parity; ID tie break; incomplete
top-k on disconnected graph; independent brute-force L2 on 37-node ring-connected
random graph (12 queries, k=10, beam=n); a bounded-beam counterexample; split-GT
Recall and malformed-result validation. These are meaningful correctness tests,
not evidence of performance or useful Recall on A0/A3.

Initial full regression lacked jsonschema (5 import errors); installed the
declared test dependency into a local ignored dependency directory and reran the
complete suite successfully. Initial LeakSanitizer invocation under process
tracing failed with `LeakSanitizer does not work under ptrace`. ASan/UBSan passed
with leak checking disabled; a separate permitted run outside tracing then
passed with leak checking enabled. Neither initial environment failure is
silently classified as a successful run. No TSan was run: the new engine is
single-threaded and no multi-worker race-freedom claim exists.

Final test logs and the initial missing-dependency log remain outside Git under
the workspace evidence directory; the initial LeakSanitizer diagnostic is also
recorded above and in the chat's command output. Only compact identities and
summaries are committed. Rerunning fixtures does
not recreate historical ANN graphs or constitute an independent graph build.
