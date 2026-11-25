# A×D G2 Closeout & G3 Decision Brief

- **G2 Closeout Status:** **`G2_CLOSED_AUDIT_PASS`** (`GO_A_FIXED_COHORT` + `GO_B_SYSTEM_FIXED_COHORT` under `EXPLORATORY_HOST_SPECIFIC`).
- **Recommended Next Step:** **`CLOSEOUT`** *(formally close G2 Task A × Task D with scoped systems findings; do **not** open `design-3.2`, R91, or G3 automatically. Convene a separate **`G3 REVIEW`** only if owner/supervisor explicitly requires claims beyond fixed-cohort/single-host scope).*
- **Date:** 2026-11-25 · **Protocol:** `AXD-G2-V2-3A-20261123` (`design-3.1`, freeze `bc897419...`).
- **Companion Documents:** [Final Audit](AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) · [Results](AXD_G2_V2_DESIGN3_1_RESULTS.md) · [Evidence Manifest](AXD_G2_V2_DESIGN3_1_EVIDENCE_MANIFEST.md).

---

## 1. Executive Summary of G2 Closeout

With the completion and independent audit (`0` discrepancies across `1,440,000` OFF rows, `180,000` ON rows, `1,299/1,299` `BUNDLE.sha256`, and `6/6` R90 v1.3 graph hashes) of `design-3.1` `run2`, the A×D G2 research scope has achieved a clean, pre-registered, reproducible conclusion:

- **Task D Search Optimization (`B1+A1` vs `baseline` at `p = 2, S = 16, beam = 432`):** Delivers **`6.033%`** geometric paired latency reduction (`CI95 [5.977%, 6.090%]`, `1.0642×`, `-218.38 µs/query`) with **100% bit-exact Top-10 & `squared_l2` parity**, improved tail latencies (`P95 -4.22%`, `P99 -4.09%`), and flat memory (`+9.4 KiB` mean, `72/72` RAM hard gate PASS) ⇒ **`GO_A_FIXED_COHORT`**.
- **Joint A×D System (`Fast` BUILD + `B1+A1` Search vs `Stock` BUILD + `baseline` Search):** `Fast` saves **`8.463 s/index` (`-20.03%`)** in historical Host A BUILD with equivalent Recall@10 (`Gate B PASS`), zero Search latency penalty (`+0.33/+0.37 µs`, CIs contain `0`), and **zero BUILD × B1+A1 interaction** (`+0.037 µs`, `CI95 [-2.58, +2.66] µs`). Combined two-host modeled savings reach **`30.336 s`** at `Q = 100,000` and **`227.194 s`** at `Q = 1,000,000` ⇒ **`GO_B_SYSTEM_FIXED_COHORT`**.

All pre-registered G2 research questions have been answered cleanly within scope. Further runs inside `design-3.1` or a `design-3.2` patch would add zero scientific value to G2.

---

## 2. Threats to Validity

| Validity Dimension | Threat / Limitation | Severity | Mitigation Applied in G2 v2 | Residual Impact |
|---|---|---|---|---|
| **Internal Validity** | Background OS/timer noise (`avahi`, `gnome-shell`, `firmware-notifier`) | Controlled | Clean `multi-user.target` TTY + `prepare_quiet_tty_env.sh` + topology guard (`max host 0.0070 <= 0.025`); `imbalance_warning = false`; `AB` (`6.025%`) ≈ `BA` (`6.041%`) | Minimal within `run2`; historical HOLDs preserved transparently |
| **Internal Validity** | Dynamic CPU frequency (`schedutil`, `balanced` profile) & slight thermal difference (`-0.57°C` during `opt`) | Low | Consecutive paired execution + balanced order; start `Tctl` (`-0.28°C`) and worker clocks (`+5.2 MHz`, `0.14%`) both statistically balanced (CIs include 0) | Cannot explain `6.03%` latency gain; fixed-frequency host test remains unmeasured |
| **Construct Validity** | Two-host BUILD–SEARCH model excludes transfer, serialization, and graph-load time | High (for deployment claims) | Explicitly isolated and labeled `two hosts; transfer/load excluded and UNKNOWN`; non-batch local wall (`~3.91 s`) reported separately | Prohibits claiming single-host end-to-end deployment speedup |
| **Construct Validity** | Process-window `cpu_seconds` includes load/warmup/output; `RAPL` empty; `perf_event_paranoid = 4` | Medium | Reported with explicit window label; ON counters separated from OFF wall time | Prohibits exclusive OFF cycle-level or Joules/query attribution |
| **Construct Validity** | Combined `B1+A1` only (no solo-B1 or solo-A1 arm in G2 v2) | Medium | Explicitly scoped as combined policy effect | Prohibits attributing the `6.03%` gain to `B1` or `A1` individually |
| **Statistical Conclusion** | `n = 6` fixed graphs with `root independence NOT_VERIFIED` (`graph_population_ci = NOT_ESTIMABLE`) | High | Block/query CIs explicitly scoped to fixed cohort; per-graph & LOO reported; zero population-CI fabrication | Narrow CIs (`±0.06 pp`) do **not** reflect across-seed/build variance |
| **Statistical Conclusion** | Public `100K` / `test_90k` prior exposure & post-v1 redesign | Medium–High | Disjoint `v2_test_10000.ids` hash-ranked before execution; common beam locked validation-only; labeled `EXPLORATORY_HOST_SPECIFIC` | Prohibits labeling G2 v2 as a blind fresh confirmatory holdout |
| **External Validity** | Single CPU (`Ryzen 5 PRO 4650U`), single dataset (`MS-Turing-1M`), single point (`p=2, S=16, beam=432, jobs=1`) | High | Scoped explicitly in all titles, JSON labels, and claim boundaries | Prohibits generalization to `p=1/4`, multi-query serving, Intel CPUs, `10M`, or other datasets/graph families |

---

## 3. Permitted vs. Prohibited Scientific Claims

| Domain | Permitted Claim (Supported by Audited G2 v2 Evidence) | Prohibited Claim (Unsupported — Must NOT Be Made) |
|---|---|---|
| **B1+A1 Search Effect** | On the fixed 6-graph MS-Turing-1M R90 v1.3 cohort at `p = 2, S = 16, beam = 432, jobs = 1` on `AMD Ryzen 5 PRO 4650U`, `B1+A1` reduces OFF mean search latency by **`6.03%`** (`CI95 [5.98%, 6.09%]`, `1.064×`), improves P50/P95/P99 (`-6.0%/-4.2%/-4.1%`), keeps peak RSS flat (`+9.4 KiB`), and preserves 100% bit-exact Top-10 & `L2²` parity. | Claiming `B1+A1` is a **novel ANN algorithm**, claiming `6%` speedup generalizes to other CPUs/datasets/graph families/`p=4`/concurrent serving, or attributing the gain solely to B1 or solely to A1. |
| **Mechanism** | In ON diagnostics, `B1+A1` cuts duplicate L2 evaluations by `75.0%` (`-12.22%` total L2) with identical search trajectories while increasing ON merge bookkeeping (`+35.9 µs/q`), directionally consistent with the net `-6.03%` OFF latency reduction. | Claiming exclusive OFF cycle-level attribution, proving cache/IPC behavior (PMU `NOT_MEASURED`), or equating `-12.22%` logical L2 reduction with expected wall speedup. |
| **Fast vs Stock (Task A)** | At common `beam = 432` on this cohort, `Fast` and `Stock` satisfy cross-arm Recall@10 equivalence (`±0.0005`), exhibit statistically indistinguishable OFF search latency (`+0.33/+0.37 µs`), and show zero BUILD × B1+A1 interaction (`+0.037 µs`). | Claiming `Fast` improves search latency over `Stock`, claiming exact identical Recall across random seeds, or claiming population equivalence across independent graph roots. |
| **BUILD–SEARCH System** | Under the two-host additive model (historical Host A BUILD + measured Host D SEARCH, excluding transfer/load), `Fast + B1+A1` saves `30.34 s` at `Q = 100,000` and `227.19 s` at `Q = 1,000,000`, strictly outperforming `Stock+base`, `Fast+base`, and `Stock+opt` in this fixed cohort. | Claiming measured single-host end-to-end deployment savings including network/disk transfer and index loading, or claiming population BUILD CI across independent builds. |
| **Evidence Tier** | Rigorous, pre-registered, fully audited **`EXPLORATORY_HOST_SPECIFIC`** systems study with complete raw provenance and preserved negative/HOLD history. | Claiming "fresh independent confirmatory holdout" or "publication-ready generalization across architectures and benchmarks". |

---

## 4. Answered vs. Open Research Questions

### Answered Within G2 Scope
1. **Does `B1+A1` achieve `> 3%` practical OFF Search latency reduction on R90 v1.3 C160/K1024 graphs at exact Recall parity (`p=2, S=16, beam=432`)?** → **Yes (`6.033%`, CI `[5.977%, 6.090%]`, `GO_A_FIXED_COHORT`)**, resolving the historical `HOLD` left by narrow A3 replication (`CI [-2.84%, 25.21%]`).
2. **Does `B1+A1` harm tail latency (`P95/P99`) or memory (`VmHWM`)?** → **No** — tails improve (`-4.22% / -4.09%`) and RAM is flat (`+9.4 KiB`, `72/72` PASS).
3. **Does `Fast` R90 v1.3 construction hurt Search quality or Search latency on Task D's common multi-worker engine, or interact with `B1+A1`?** → **No** — Gate B Recall equivalence PASS (`+0.000117`), Search latency neutral (`+0.33/+0.37 µs`), interaction zero (`+0.037 µs`).
4. **Do Task A BUILD gains and Task D Search gains compose additively in the two-host `BUILD–SEARCH` model?** → **Yes (`GO_B_SYSTEM_FIXED_COHORT`)** — `+8.46 s` BUILD + `+21.87 s` SEARCH = `+30.34 s` at `Q = 100k`.

### Remaining Open Questions (Outside G2 Scope)
1. **Single-host end-to-end `BUILD + load + SEARCH`:** What is the measured single-machine total time when BUILD and SEARCH run on the same host (including graph write/read/load)?
2. **Multi-worker scaling (`p = 1, 2, 4`) & B1-vs-A1 decomposition:** Does `B1+A1`'s `6.03%` gain shrink or grow at `p = 4` (where inter-worker duplicate L2 is larger) vs `p = 1` (serial baseline), and how much comes from B1 vs A1 separately?
3. **Cross-host & cross-dataset generalization:** Does the ~`6%` gain hold on a desktop/server x86 CPU (e.g., `i5-14600KF` or Xeon), on `SIFT1M` / `10M` scale, or on non-PiPNN graph families (HNSW/NSG/Vamana)?
4. **Independent-root population inference:** What is the true between-seed variance when `k >= 5` verifiably independent RNG roots are built per arm?
5. **Exclusive OFF microarchitectural attribution & energy:** What fraction of the remaining `3.40 ms/query` is L2 compute vs memory stalls vs synchronization (requires permitted PMU/RAPL access)?

---

## 5. Preserved Historical Gate Ledger (Unchanged Outside G2)

All non-G2 historical decisions remain strictly untouched:
- **Historical P0 / Full P1 / `t0998` / historical A3 `B1+A1` official:** `HOLD`
- **P3 official:** `CLOSED`
- **H3 candidate overlap / TP-CG:** `NO-GO` / `NOT_OPENED` (per [ORIGINAL_PROPOSAL_FINAL_REASSESSMENT.md](ORIGINAL_PROPOSAL_FINAL_REASSESSMENT.md))
- **Protocol V4 D1–D5:** `UNAPPROVED` · **D1 `UNTESTED`**, **D4 `NOT TESTED`**, **D6 `INCONCLUSIVE`**
- **R91 / `10M` / `i5-14600KF`:** `NOT_OPENED` / `NOT_RUN`
- **Task A Google Sheets:** `UNMODIFIED`

---

## 6. G3 Decision Analysis & Recommendation

### Primary Recommendation: **`CLOSEOUT` (Do Not Automatically Open G3)**

**Why `CLOSEOUT` is the scientifically optimal default decision:**
1. **G2 objectives are 100% fulfilled:** Both `GO_A_FIXED_COHORT` and `GO_B_SYSTEM_FIXED_COHORT` passed every pre-registered gate with `0` audit discrepancies and high precision (`±0.06 pp`), while transparently documenting all limitations and historical HOLDs.
2. **Diminishing returns without a new external target:** `B1+A1` is already established as a clean systems/implementation optimization rather than an H3 algorithmic novelty (`H3/TP-CG` remains `NO-GO`). Running additional local Ryzen experiments without an explicit external requirement (e.g., paper venue, thesis committee requirement, or deployment target) risks engineering churn without changing the core scientific contribution.
3. **Clean archival milestone:** Closing G2 now allows committing the audited documentation and sealing the `1.12 GiB` Core Evidence Archive cleanly before considering any separate research phase.

### When to Trigger **`G3 REVIEW`** Instead (Owner/Supervisor-Gated Decision Matrix)

Convene a separate **G3 Design & Preregistration Review** (strictly after closing G2; never modifying G2 freeze/results) **only if** owner or supervisor explicitly requires one of the following stronger claims:

| Candidate G3 Scope | Claim It Unlocks (Currently Blocked) | Estimated Cost / Prerequisite | Priority If Publication Required |
|---|---|---|---|
| **G3-A: Cross-Host + Single-Host End-to-End (`i5-14600KF` or server CPU)** | Eliminates single-host & two-host BUILD–SEARCH confounders; measures BUILD + load + SEARCH on one machine + PMU/RAPL if unlocked | New host qualification + fresh prereg + owner approval (~`3–5 h` compute) | **High** (closes biggest systems validity gap) |
| **G3-B: Scaling (`p = 1, 2, 4`) + B1/A1 Solo Ablation** | Separates B1 vs A1 mechanisms; measures parallel scaling efficiency vs `p = 1` serial baseline | Balanced worker-strata prereg + new quality calibration at `p=1, 4` (~`4–6 h`) | **Medium–High** (strongest mechanistic depth) |
| **G3-C: Second Dataset (`SIFT1M`) & Independent-Root Cohort** | Estimates real `graph_population_ci` and tests cross-dataset generalization | Requires Task A to verify independent RNG roots (`>= 5` builds/arm) + new splits | **High for external paper**, **Unnecessary for internal closeout** |
| **G3-D: Concurrent Multi-Query Serving (`jobs > 1`)** | Measures real serving throughput/tail under load | Requires separate serving harness & SLO definition (new software subject) | **Low** (out of current intra-query scope) |

**Actionable Verdict:** Proceed with **`CLOSEOUT`** of G2 (owner review of the 4 documents, optional git commit of untracked `design-3.1` + closeout docs, and owner-approved local archival of Tier 1 Core Evidence). Escalate to **`G3 REVIEW`** **only if** the supervisor explicitly requests one of G3-A/B/C above.
