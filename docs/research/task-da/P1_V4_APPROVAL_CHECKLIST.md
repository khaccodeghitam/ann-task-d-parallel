# Task D × Task A — P1 V4 & P2 Gate Approval Checklist

- **Date:** 2026-11-18
- **Purpose:** Formal research-owner sign-off gate separating verified facts, preserved `HOLD` statuses, pending owner decisions, V4 P1 PASS criteria, and P2 Multi-Walker prerequisites.
- **Authority Rule:** Agent must **not** self-approve Protocol V4 or begin V4/P2 runs until the owner resolves Section 2 below.

---

## 1. Evidence & Preserved Status Ledger

| Item / Scope | Current Status | Proven Basis |
|---|---|---|
| **12/12 Data & Formal Graphs + 4 ELFs + 261 Raw Receipts** | **VERIFIED ON DISK** | SHA-256 verified ([experiment_manifest_v3_reconciled.json](experiment_manifest_v3_reconciled.json)); zero edits to immutable assets. |
| **GT Protocol v2 Validator (`--gt-aux-min -1e-5`)** | **`PASS`** | Default `0.0` preserved; exact rank-0 matches accepted cleanly (`val_10k: 1`, `test_90k: 2`) without changing GT file. |
| **P1 Common-Engine Correctness, Parity & Determinism (`V3`)** | **`PASS`** | `1,804,000 / 1,804,000` paired ON/OFF queries exact (`0` mismatches); `0` incomplete top-10; `--jobs 1` repeat == `--jobs 6`; `17/17` post-run immutable SHAs exact; Release & ASan CTest + 512 unittests pass. |
| **P1 V3 Quality Calibration (`t0990 = 0.990`)** | **`9 / 9 PASS`** | All `9` graphs passed `>= 0.990` on `test_90k`, though `A3_r1@896` (`0.990041`) and `A3_r3@896` (`0.990129`) sit very close to floor. |
| **P1 V3 Quality Calibration (`t0998 = 0.998`)** | **`2 / 9 PASS, 7 / 9 FAIL`** | `A1_r2@928` & `A3_r2@2304` passed; `7` cells (`A0_r1..r3, A1_r1, A1_r3@896`, `A3_r1@2176`, `A3_r3@2112`) failed `test_90k`, traced to zero-margin threshold selection bias on a flat plateau + correlated queries (`r=0.71–0.91`). |
| **Historical P0 Overall (Preregistration v1)** | **`HOLD`** | Missing historical runtime CLI seed, unrecoverable R86 host telemetry, Zen2 vs AVX-512 host mismatch. Remains `HOLD`. |
| **Full P1 Gate (Current V3)** | **`HOLD`** | Blocked by `7/9` `t0998` quality misses under V3 rules. |
| **P2 Multi-Walker & P3 Performance Benchmarking** | **`HOLD / CLOSED`** | P2 blocked by Full P1 Gate `HOLD`; P3 additionally blocked by `P0 = HOLD` and unqualified host `thinhbui-linux`. |

---

## 2. Decisions Requiring Explicit Research-Owner Sign-Off Before Running V4

| # | Decision Item | Options | Recommended Choice | Owner Decision (`[ ]` Select) |
|---|---|---|---|---|
| **D1** | **Approve Protocol V4 Addendum** ([PROTOCOL_V4_APPROVAL_READY.md](PROTOCOL_V4_APPROVAL_READY.md)) | Approve V4 execution in new isolated evidence dir (leaving V1/V2/V3 & V3 `frozen_calibration_manifest.json` unchanged) vs Hold all P1/V2 work. | **Approve Protocol V4 execution** (after selecting D2–D4). | `[ ] APPROVE V4` / `[ ] HOLD` |
| **D2** | **Validation Beam Selection Criterion** (`val_10k` only) | **(a) Query-level Two-Sided 95% LCB** (`mean - 1.96 * SE_q >= target`, equals `evaluate_p1.py` `recall_ci95_low`); **(b) Effective-N Wilson 95% LCB** (`N_eff = 100k / deff`); **(c) Fixed pre-registered margin**. | **(a) Query-level Two-Sided 95% LCB** (matches bootstrap `p025` & `evaluate_p1` `recall_ci95_low` exactly; adjusts for `deff = 1.14–1.95`). | `[ ] (a) LCB95_q` / `[ ] (b) Eff-Wilson` / `[ ] (c) Other` |
| **D3** | **Holdout Verification Track** (Anti-Leakage Rule) | **Track A:** Supply/verify an unseen independent query + exact GT holdout (confirmatory claim). **Track B:** Re-evaluate frozen V4 beams on existing `test_90k` strictly disclosed as `EXPLORATORY / POST-HOC GATE VERIFICATION` (no unseen-confirmation claim). | **Track A** if unseen queries/GT can be provided; otherwise **Track B** with strict post-hoc classification. | `[ ] Track A (New Holdout)` / `[ ] Track B (Post-Hoc test_90k)` |
| **D4** | **P2 Entry Policy After V4** | **Option B (Recommended):** Keep all P2 `HOLD` until BOTH `0.990` and `0.998` satisfy Full V4 P1 Gate. **Option A:** Amend scope via separate addendum to run `t0990`-only non-benchmark P2 engineering (`0.998` remains closed). | **Option B** (single clean baseline across `0.990 + 0.998`, avoids thin `A3@896` `t0990` margin before `p > 1`). | `[ ] Option B (Wait Full V4 P1)` / `[ ] Option A (t0990 Addendum)` |
| **D5** | **Authorize V4 Compute Budget** | Run clean sequential `--jobs 6` V4 campaign (~2.5–3.0 hours under Track B; ~8–9 GB external disk). | **Authorize clean isolated V4 run** after D1–D4 approval. | `[ ] AUTHORIZED` / `[ ] DEFER` |

---

## 3. Gate Exit Criteria (Strict Checklist After Execution)

### Criteria to Promote **Full P1 Gate (under Protocol V4)** from `HOLD` -> `PASS`
- [ ] All `18/18` `(arm, rep, target)` cells find `b_V4* <= 4096` clearing D2 criterion on `val_10k` (`prev_grid` < threshold).
- [ ] `18/18` `val_10k` `ON/OFF` parity **PASS** (`0` mismatches, `0` incomplete top-10, valid 64-bit counters) before freezing `frozen_calibration_manifest_v4.json`.
- [ ] On designated holdout (D3 Track A or Track B): **`18/18` cells achieve `Recall@10 >= target` (`0.990` and `0.998`)**, `18/18` `ON/OFF` parity **PASS**, `0` incomplete top-10 queries.
- [ ] Phase 5 post-run determinism (`--jobs 1` repeat == `--jobs 6`), `17/17` immutable asset SHA-256 verification, `EVIDENCE_CHECKSUMS.csv`, Release & ASan CTest, and `unittest` all pass.
- [ ] Track B limitation (if chosen) and `P0 = HOLD` explicitly stated in final V4 Gate Decision report.

### Mandatory Prerequisites Before Opening **P2 Multi-Walker (`workers > 1`)**
- [ ] Full V4 P1 Gate (`PASS` above) — *or* explicit owner-signed Option A `t0990`-only Scope Addendum.
- [ ] Written **P2 Multi-Walker Protocol & Shared-State Contract** freezing: worker frontier/visited-set synchronization semantics, per-worker + aggregate 64-bit counter invariants, deterministic tie-breaking/parity rules (`ON/OFF`), quality-matching constraint vs frozen `workers=1` beams, and strict **no P3 QPS / no `tai-linux` hardware comparison** guardrail on `thinhbui-linux` (since `P0 = HOLD` and `P3 = CLOSED`).
