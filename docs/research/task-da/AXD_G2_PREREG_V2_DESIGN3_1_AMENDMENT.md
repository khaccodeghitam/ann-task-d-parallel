# A×D G2 v2 · Controlled Amendment `design-3.1` (OFF `counters` Parser Compatibility Fix)

- **Root Cause Status:** **`ROOT_CAUSE_CONFIRMED`**
- **Protocol & Revision:** `AXD-G2-V2-3A-20261123` · revision **`design-3.1`** · schema **`axd_g2_v2.3.1`** · **`EXPLORATORY_HOST_SPECIFIC`** · `p=2`, `S=16`, `common beam = 432`.
- **Immutable Ancestors Preserved Byte-for-Byte:**
  - `design-3` freeze (`425c748329292ffe15db2c52bdf53f5d219b47d1ecf95ac3c76a5429814159ae`, `26/26` files untouched)
  - `design-2` freeze (`91186d57e5992e1df70f86a55ba928ad4d6613bb0b67ccbee0f485cc380d1749`, `24/24` files untouched)
  - `OFF_EXECUTION_HOLD` evidence (`axd-g2-v2-off-design3`, `11/11` `BUNDLE.sha256` untouched)
  - Signed `design-3` approvals (`design3_quality_only_approval.json`, `design3_off_approval.json` untouched)
- **Execution Posture:** **`0` new native ANN runs**, **`0` OFF executions**, **`0` re-runs of Qualification or Quality ON**; awaiting owner review & fresh `design-3.1` approval receipt before any future full 144-OFF campaign in a dedicated new output directory (`axd-g2-v2-off-design3_1`).

---

## 1. Root Cause Summary (`KeyError: 'counters'` on `b0_stock_off_r1_base_test`)

1. **Native P2 OFF producer (`task_da_p2_eval`, frozen ELF `7a2685e5...`, frozen source `f2cd634:research/task_da/search_common/p2_eval.cpp` lines 397–441):**
   - When `--mode ON` (`instrument == true`), `p2_eval.cpp` emits `"counters":{...}` (19 keys total).
   - When `--mode OFF` (`instrument == false`), `p2_eval.cpp` **omits the `"counters"` key entirely** (18 keys total; the literal `"null"` never appears anywhere in `p2_eval.cpp`).
   - Verified empirically on **10,000 / 10,000** rows of preserved HOLD `b0_stock_off_r1_base_test/beam_432_p2_OFF.jsonl` and **524 / 524** historical native `*_p2_OFF.jsonl` artifacts across `artifact-evidence/`.
   - By contrast, older P1/smoke C++ binaries (`p1_eval.cpp:175–177`, `smoke.cpp:37`) emitted `"counters":null`.
2. **Parser defect in frozen `g2_v2_design3_analyzer.py:153` (inherited from `g2_v2_analyzer.py:104`):**
   - `output_digest()` assumed the P1 schema (`require(row['counters'] is None, 'OFF counters must be null')`), causing an immediate `KeyError: 'counters'` on the very first valid native P2 OFF row despite `exit_code == 0`, `guard_failure is None`, zero `stderr`, clean telemetry, and 100% bit-exact parity with Quality ON (`output_digest = d090e2a14cef76ef34854aee328efc6486443153b6e2b0c9024be68aed712e9b`).
3. **Why prior tests and dry-runs did not detect it:**
   - Synthetic unit fixtures in `test_g2_v2_design3.py:435` and `test_g2_v2.py:163` fabricated `counters=None` instead of matching native `p2_eval.cpp` OFF output.
   - `NativeP2MultiWalkerTests` in `test_task_da.py` validated real native OFF outputs via `evaluate_p2.check_p2_on_off_parity()`, which used `r_off.get('counters') is not None` and therefore passed silently on omitted keys.
   - The `18/18` Quality ON campaign only executed the `mode == 'ON'` branch of `output_digest()`; `--dry-run` and `plan` never execute native ANN or invoke `output_digest()`.

---

## 2. Minimal Controlled Changes in `design-3.1`

Only the OFF/ON JSONL row parser and its contract/runner linkage are amended in new versioned files:

1. **`research/task_da/g2_v2_design3_1_analyzer.py`:**
   - Replaces `row['counters'] is None` with explicit 4-state classification (`classify_counters_field`: `absent`, `explicit_null`, `object`, `malformed`) and `validate_row_counters()` — **no uncontrolled `row.get('counters')`**.
   - `mode == 'OFF'`: accepts ONLY `absent` (`'counters' not in row`, exact frozen `task_da_p2_eval` producer format); explicitly rejects `explicit_null`, `object` (including `{}`), and `malformed` values with distinct `ValueError` diagnostics.
   - `mode == 'ON'`: requires exact 17-key `object` with strict non-bool integer/list types and full `validate_p2_counters_row(row, 1000000)` algebraic invariants; explicitly rejects `absent`, `explicit_null`, and `malformed`.
   - Enforces strict required-key presence, exact field types (rejecting `bool` as `int`), and exact allowed-key sets (rejecting unexpected fields like `rounds`, `trace_overflow`, `phase_audit`).
   - Delegates 100% of statistical, quality, bootstrap, tail, RAM hard-gate, BUILD-SEARCH, and `noise_balance` math verbatim to frozen `g2_v2_design3_analyzer`.
2. **`research/task_da/g2_v2_design3_1_contract.py` & `configs/axd_g2_v2_design3_1.schema.json`:**
   - Pins `revision = "design-3.1"`, `schema = "axd_g2_v2.3.1"`, and `parent_design3_freeze_sha256 = "425c748329292ffe15db2c52bdf53f5d219b47d1ecf95ac3c76a5429814159ae"`.
   - Programmatically enforces invariance of all 21 shared components and all 21 shared binary/graph/runtime/host/statistical freeze sections against frozen `design-3`.
   - Rejects all `design-2` and `design-3` approvals and explicitly forbids targeting the preserved HOLD directory `axd-g2-v2-off-design3`.
3. **`research/task_da/g2_v2_design3_1_runner.py`:**
   - Reuses frozen `g2_v2_design3_guard.py` (`6795656a...`) verbatim (0 changes to environment control or noise guards).
   - Implements explicit cryptographic reuse verification for immutable `design-3` Qualification PASS (`verify_qualification`) and 18/18 Quality ON (`quality_context`), plus `design-3.1` `process_result`, `check_reference`, `execute`, and `load_campaign`.
   - Enforces full 144-process OFF execution from scratch in a new output directory (`0` partial resume, `0` auto-retry).

---

## 3. Formal Reuse Contract for `design-3` Qualification PASS & 18/18 Quality ON

Re-running Qualification (`900 s`) or Quality ON (`18/18`) is **NOT technically required**, provided all of the following programmatically enforced contract invariants hold at execution and analysis time:

| Upstream Evidence | Reused Artifact & SHA-256 | Why Valid Without Re-Run | Programmatic Contract Checks in `design-3.1` |
|---|---|---|---|
| **900s Qualification PASS** | `axd-g2-v2-design3-qualification-20261124T094602Z/qualification_result.json` (`f64b9f9a...c49cb`) + raw telemetry (`83251566...`) | `g2_v2_design3_guard.py`, `g2_v2_design3_qualify.py`, host profile, kernel `7.0.0-43-generic`, and OFF noise tiers are **100% byte-identical**; qualification never invokes `output_digest()`. | `verify_parent_design3_invariants()` verifies parent freeze `425c7483...` + identical guard/host/policy pins; `verify_qualification()` verifies schema `axd_g2_v2.3`, `QUALIFICATION_PASS`, `0` window/hard failures, `>= 899s`, and raw telemetry SHA-256; owner approval pins `qualification_sha256`. |
| **18/18 Quality ON (`Gate A & B PASS`)** | `axd-g2-v2-quality-design3/quality.json` (`360e1d29...a54c59f`), `complete.json`, `start.json`, `18` `metrics.json`, `18` preflights, `12` test ON references (`166/166` `BUNDLE.sha256`) | Native binary `7a2685e5...`, `5` `.so`, `6` R90 v1.3 graphs, `v2_test_10000.ids`, `beam=432`, `p=2`, `S=16`, guard, and ON validation/digest/Gate A/B math are **100% unchanged**; Quality ON never executed the OFF branch. | `quality_context()` verifies `NO HOLD.json`, parent freeze `425c7483...`, matching `artifacts_sha256` & `qualification_sha256` in `start.json`, `18/18` receipt + preflight SHAs, `12/12` ON reference SHAs, and `A_pass`/`B_pass`/`parity`/`duplicate_reduction`; `check_reference()` re-validates every ON reference through `design-3.1` `output_digest(..., mode='ON')`. |

*(If kernel `7.0.0-43-generic`, any pinned `.so` runtime library, Python 3.12.3/venv, binary, or any of the 26 frozen `design-3` files changes before execution, `load_freeze()` / `host_contract()` / `verify_artifacts()` fails closed automatically.)*

---

## 4. Owner Review & Approval Conditions Before Any Future 144-OFF Execution

1. **Preserve HOLD Evidence:** Leave `axd-g2-v2-off-design3` (`11/11` `BUNDLE.sha256`) and signed `design3_off_approval.json` (`aa9a98d4...`) completely untouched.
2. **Verify Frozen Integrity:** Confirm `design-3` `26/26 OK`, `design-2` `24/24 OK`, and `design-3.1` freeze checksums `OK`, plus passing offline regression test suite (`tests/research/test_g2_v2_design3_1.py`).
3. **Sign New `design-3.1` Approval Receipt:** Copy `artifact-evidence/axd-g2-v2-approvals/design3_1_off_approval.DRAFT_UNSIGNED.json` to `design3_1_off_approval.json` and fill `owner`, `approved_at` (with timezone), `scope` (`"OFF_AB"` or `"OFF_A"`), `quota_s = 10800`, and `quiet_host_confirmed = true`, targeting the dedicated new output directory `artifact-evidence/axd-g2-v2-off-design3_1`.
4. **Full Fresh 144-Process Run on Quiet TTY:** Execute full 144/144 OFF from block 0 (`0` partial resume) via `python -m research.task_da.g2_v2_design3_1_runner execute --phase off ...` under the same `multi-user.target` + paused mDNS/timers protocol, followed by offline analysis via `python -m research.task_da.g2_v2_design3_1_analyzer`.
