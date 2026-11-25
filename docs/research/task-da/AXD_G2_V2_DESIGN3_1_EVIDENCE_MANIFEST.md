# A×D G2 v2 (`design-3.1`) · Evidence Manifest, Reproducibility & Archive Specification

- **Protocol & Revision:** `AXD-G2-V2-3A-20261123` · **`design-3.1`** (`bc897419...`) · **`AUDIT_PASS`** · **`EXPLORATORY_HOST_SPECIFIC`**.
- **Repository Base Commit:** `5bc7de698f38f1e0257e0b1cce2f39196de71ff0` (`main` / `research/task-da-pivot-b1-a1-20261119`; `0` tracked edits; `design-3.1` overlay + closeout docs untracked pending owner review — **no auto-commit/push/upload performed**).
- **Companion Documents:** [Final Audit](AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) · [Results](AXD_G2_V2_DESIGN3_1_RESULTS.md) · [Closeout & G3 Decision](AXD_G2_CLOSEOUT_AND_G3_DECISION.md).

---

## 1. Immutable Freeze, Code, Binary, Runtime & Input Provenance Ledger

### 1.1 Freeze Manifests & Verification Lists

| Artifact (relative to `task-d/`) | Entries | SHA-256 | Verified State |
|---|---:|---|---|
| [docs/research/task-da/AXD_G2_V2_DESIGN3_1_FREEZE_MANIFEST.json](AXD_G2_V2_DESIGN3_1_FREEZE_MANIFEST.json) | `28` components + pins | `bc8974193970b1663a53e08bc7de16b91013f11866965f872a78d775b7b28f5e` | **29/29 OK** (`AXD_G2_V2_DESIGN3_1_FREEZE.sha256`) |
| [docs/research/task-da/AXD_G2_V2_DESIGN3_FREEZE_MANIFEST.json](AXD_G2_V2_DESIGN3_FREEZE_MANIFEST.json) | `25` components + pins | `425c748329292ffe15db2c52bdf53f5d219b47d1ecf95ac3c76a5429814159ae` | **26/26 OK** (`AXD_G2_V2_DESIGN3_FREEZE.sha256`) |
| [configs/axd_g2_v2_freeze.json](../../../configs/axd_g2_v2_freeze.json) (`design-2`) | `22` components + pins | `91186d57e5992e1df70f86a55ba928ad4d6613bb0b67ccbee0f485cc380d1749` | **24/24 OK** (`AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256`) |
| [configs/axd_g2_v2_design3_artifacts.proposed.json](../../../configs/axd_g2_v2_design3_artifacts.proposed.json) | Artifact path map | `6b49cce57a9520ef650dafda0ffd1deb735d6546569d7bbc5b1cdf2a3045f068` | **OK** (`= run2/artifacts.json`) |
| [configs/axd_g2_v2_build_reference.json](../../../configs/axd_g2_v2_build_reference.json) | `6` Host A BUILD pins | `c9ad18b0062fea39609089b26817d43adc2cb4f495cd72c3a3ef7261abbc87b3` | **OK** |
| [configs/axd_g2_v2_design3_1.schema.json](../../../configs/axd_g2_v2_design3_1.schema.json) | Schema `axd_g2_v2.3.1` | `82e3d3515589dc68d227a42179e4942fd3c6bfcb107ebb80c795f0c93c128385` | **OK** |
| [scripts/run_g2_v2_design3_1_off_run2.sh](../../../scripts/run_g2_v2_design3_1_off_run2.sh) | Run2 orchestrator (external) | `fa10a1ceb204f1dbff4acf6f752e380e91895adfead9f46aa78f524a117bb07e` | **OK** |
| [scripts/prepare_quiet_tty_env.sh](../../../scripts/prepare_quiet_tty_env.sh) | Quiet TTY hygiene script | `7f68dbfbcb6b55fb6e9e310d78a5bff55b82fd2e06f7295d231d29cb12b65799` | **OK** (`--verify-restored` PASS) |

### 1.2 Frozen Search Source, Binary, Compiler, Runtime & Dataset Pins

| Component | Identity / Path | SHA-256 |
|---|---|---|
| Search Source Commit | `f2cd634b837a70735c3e31e5956f0524bfc26675` (`p2_eval.cpp` / `p2_engine.hpp` / `engine.hpp`) | `b356ba8d...` / `c4b1bdc2...` / `2ca38624...` |
| Search Release ELF | `build-task-da/task_da_p2_eval` | `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1` |
| Compiler & Pinned Python | `/usr/bin/c++` (GCC 13.3.0) · `/usr/bin/python3.12` (`3.12.3`) | `1353e9bd...` · `e50d468e...` |
| Native Runtime Libs (`5/5`) | `libstdc++.so.6`, `libgcc_s.so.1`, `libc.so.6`, `libm.so.6`, `ld-linux-x86-64.so.2` | `1fd75fe7...`, `d93224d2...`, `755a371e...`, `5dcc4d25...`, `5fc09408...` |
| Task A Source / Highway | `f5e48bb681812ce51aed7272f30ecefc85ed427b` · Highway `6bc2d47793bae9c521fb4150936669647700765d` | Stock ELF `13bef65c...` / Fast ELF `fcfb16d0...` |
| Transfer Package & Manifests | `TASK_A_R90_V13_MST1M_SIX_ORIGINAL_GRAPHS.tar` / `TRANSFER_MANIFEST.json` / `SHA256SUMS.txt` | `e59f5889...` / `df092d83...` / `62b0db1a...` |
| Dataset (`base`, `queries`, `gt`) | `MSTuring_1M_v1/{base.1M.fbin, query.public.100K.fbin, groundtruth.public.100K.ibin}` | `44e83e1d...` / `48d087a1...` / `fa5acf5a...` |
| Query Panels (`val`, `warmup`, `test`) | `val_10k.ids` / `warmup_val_100.ids` / `v2_test_10000.ids` | `a3c948e9...` / `199ca606...` / `457abdc1...` |
| `MS-Turing1M_stock_off_r1..r3.graph` | `215,313,724 B` / `215,413,516 B` / `215,432,108 B` | `db4f5257...` / `5de325e9...` / `a7eb1ad1...` |
| `MS-Turing1M_fast_off_r1..r3.graph` | `215,398,220 B` / `215,429,104 B` / `215,460,436 B` | `104a1bc6...` / `4b69a53c...` / `7c80157e...` |

---

## 2. External Evidence Bundle & Approval Inventory (`../../../../artifact-evidence/`)

### 2.1 Primary G2 v2 (`design-3.1` `run2`) & Reused Upstream Bundles (Tier 1 Core)

| Artifact / Bundle Path (relative to `artifact-evidence/`) | Role | Size | Entries (`BUNDLE`) | Key SHA-256 Digest(s) |
|---|---|---:|---:|---|
| **`axd-g2-v2-off-design3_1_run2/`** | **Primary 144-OFF campaign (`NO_HOLD_JSON`)** | `912 MiB` | **`1299/1299 OK`** | `BUNDLE.sha256` `c2b4d8f1c6e0cc004a3c2db100abce6ed48c85657c90fd9a4c38d81882925a84`; `complete.json` `6de28dd6...`; `start.json` `85a7b7e8...` |
| **`axd-g2-v2-off-design3_1_run2-analysis.json`** | **Frozen `design-3.1` analyzer output** | `36 KiB` | `1` | `f0a35394f028550a1f14f4928467a62e5d09363a2ef26cffa160d0c7e200615c` |
| **`axd-g2-v2-off-design3_1_run2.console.log`** | **Run2 TTY execution & seal log** | `4 KiB` | `1` | `c2a736c834391f2e779b20fc8b7af1ef8cb2d1e7f5a5f477d29e28849adc8990` |
| **`axd-g2-v2-approvals/design3_1_off_approval_run2.json`** | **Signed `run2` `OFF_AB` owner approval** | `1 KiB` | `1` | `edbe6e98005b358ade094747d33bab3edfc509dcf5b7d9327708a0041d44deba` |
| **`axd-g2-v2-quality-design3/`** | **Reused `18/18` Quality ON (`Gate A & B PASS`)** | `198 MiB` | **`166/166 OK`** | `BUNDLE.sha256` `5e3a41d07b274b29a5dc85016d6188195f58fb57b79e2f06ef76a767eadb6573`; `quality.json` `360e1d29...`; `complete.json` `a2c860d1...` |
| **`axd-g2-v2-design3-qualification-20261124T094602Z/`** | **Reused 900s `QUALIFICATION_PASS`** | `6.7 MiB` | **`2/2 OK`** | `BUNDLE.sha256` `24fc2b71...`; `qualification_result.json` `f64b9f9a...`; `telemetry` `83251566...` |
| **`axd-g2-v2-inputs-design3/`** | **Materialized `v2_test_10000.ids`** | `68 KiB` | `1` | `v2_test_10000.ids` `457abdc13abc95d8d0f48ff32919a6013f5ed4bca469f9075312ae80dfe44b0d` |
| `axd-g2-v2-approvals/design3_quality_only_approval.json` | Signed upstream `QUALITY_ONLY` approval | `1 KiB` | `1` | `bb482f042a226c14bc163efde6bebe8b865351cfd69dfa45c34298d802ce2002` |

*Tier 1 Core Total:* **`~1.12 GiB`** (complete reproducible primary + upstream evidence without duplicating the 1.29 GB graphs or MS-Turing-1M vectors).

### 2.2 Preserved Historical HOLD, Diagnostic & Ancestor Bundles (Tier 2 Forensic Archive, Never Merged into `run2`)

| Artifact / Bundle Path (relative to `artifact-evidence/`) | Historical Role | Size | Entries (`BUNDLE`) | Key SHA-256 Digest(s) |
|---|---|---:|---:|---|
| `axd-g2-v2-off-design3_1/` + `.console.log` | `design-3.1` run1 `OFF_EXECUTION_HOLD` (#120/144, `firmware-notifier`) | `754 MiB` | **`1080/1080 OK`** | `BUNDLE.sha256` `bbc9f25d...`; `HOLD.json` `4e078fc1...`; log `8e318747...`; approval `1bdcc80c...` |
| `axd-g2-v2-off-design3/` | `design-3` OFF `HOLD` (#1/144, `KeyError: 'counters'`) | `6.5 MiB` | **`11/11 OK`** | `BUNDLE.sha256` `cf7d991f...`; `HOLD.json` `8187bb38...`; approval `aa9a98d4...` |
| `axd-g2-v2-design3-qualification-20261124T082344Z/` | `design-3` Qualification #1 `QUALIFICATION_HOLD` | `8.6 MiB` | **`2/2 OK`** | `BUNDLE.sha256` `178bada3...`; `qualification_result.json` `c597e572...` |
| `axd-g2-v2-preflight-20261124/` & `-recovery-20261124/` | `design-2` Stage 0 `BLOCKED_PREFLIGHT` + B3 recovery | `1.2 MiB` | Verified | `cc079410...` / `02027ca0...` |
| `axd-g2-validation-20261122-G81SkWjO/` | G2 Stage 5 validation (`54` base + `6` opt; source of `b432` baselines) | `644 MiB` | `562/562` | `BUNDLE.sha256` `82e740bc...` |
| `axd-g2-stage6-test-quality-20261123/` | G2 v1 Stage 6 `QUALITY_HOLD` (`narrow_test_3000.ids`) | `40 MiB` | `101/101` | `BUNDLE.sha256` `cd65a8ac...` |
| `axd-g1-runtime-20261122-Ik1dBvXi/` | G1 graph compatibility & runtime parity audit | `12 MiB` | Verified | See [AXD_G1_GRAPH_ARTIFACT_MANIFEST.md](AXD_G1_GRAPH_ARTIFACT_MANIFEST.md) |
| `axd-g2-v2-approvals/` (all signed & unsigned drafts) | Complete approval audit trail | `48 KiB` | `10` files | Includes `design3_1_off_approval_run2.DRAFT_UNSIGNED.json` (`37210e82...`) |

*Tier 1 + Tier 2 Combined Total:* **`~2.58 GiB`** (excluding `base/queries/gt` and the 6 `.graph` binaries).

---

## 3. Offline Reproducibility Instructions (Zero New ANN Execution)

All commands below are strictly read-only with respect to raw evidence and frozen packages:

```bash
cd "/home/thinhbui/Documents/ChatGPT/Research ANN/task-d"
EV="/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence"
PY="/home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python"

# 1. Verify all 3 frozen packages (29/29, 26/26, 24/24)
sha256sum -c docs/research/task-da/AXD_G2_V2_DESIGN3_1_FREEZE.sha256
sha256sum -c docs/research/task-da/AXD_G2_V2_DESIGN3_FREEZE.sha256
sha256sum -c docs/research/task-da/AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256

# 2. Verify all external BUNDLE.sha256 seals (run2 1299/1299, quality 166/166, qual 2/2, HOLDs 11/11 & 1080/1080)
for d in axd-g2-v2-off-design3_1_run2 axd-g2-v2-quality-design3 \
         axd-g2-v2-design3-qualification-20261124T094602Z \
         axd-g2-v2-off-design3 axd-g2-v2-off-design3_1; do
  (cd "$EV/$d" && sha256sum -c BUNDLE.sha256 >/dev/null && echo "OK: $d ($(wc -l < BUNDLE.sha256) entries)")
done

# 3. Verify frozen design-3.1 dataset-free regression suite (0 ANN)
env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT "$PY" -m unittest tests/research/test_g2_v2_design3_1.py

# 4. Re-run frozen design-3.1 analyzer offline into a fresh temp path (ABSOLUTE paths required)
env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT "$PY" -m research.task_da.g2_v2_design3_1_analyzer \
  --campaign "$EV/axd-g2-v2-off-design3_1_run2" \
  --output "/tmp/reproduced_run2_analysis.json"
diff -u "$EV/axd-g2-v2-off-design3_1_run2-analysis.json" "/tmp/reproduced_run2_analysis.json"
```

---

## 4. Evidence Archive Proposal & Checksum Verification (Owner-Gated — No Auto-Upload)

> [!IMPORTANT]
> **No archive has been created or uploaded automatically.** Owner approval is required before creating release tarballs or uploading any raw evidence to external storage (Zenodo, OSF, Google Drive, GitHub Releases).

### 4.1 Recommended Archive Packaging Tiers

1. **Git Repository (`task-d`, Lightweight — Publishable Directly After Owner Review):**
   - Commit the `design-3.1` frozen package (`configs/`, `research/task_da/g2_v2_design3_1_*.py`, `tests/research/test_g2_v2_design3_1.py`, `docs/research/task-da/AXD_G2_*`), helper scripts (`scripts/prepare_quiet_tty_env.sh`, `scripts/run_g2_v2_design3_1_off_run2.sh`), and the 4 closeout documents.
   - **Never commit** `artifact-evidence/` raw JSONLs, `.local/artifacts/` graphs, or dataset binaries to Git; link by relative path and SHA-256.
2. **External Archive A — Core Reproducible Package (`~1.12 GiB` uncompressed, ~`120–220 MiB` `.tar.zst`/`.tar.xz`):**
   - Includes: `axd-g2-v2-off-design3_1_run2/`, `axd-g2-v2-off-design3_1_run2-analysis.json`, `axd-g2-v2-off-design3_1_run2.console.log`, `axd-g2-v2-quality-design3/`, `axd-g2-v2-design3-qualification-20261124T094602Z/`, `axd-g2-v2-inputs-design3/`, `axd-g2-v2-approvals/`.
   - Plus Stage 5 `b432` validation references (`6` files from `axd-g2-validation-20261122-G81SkWjO`) if standalone verification without the full `644 MiB` Stage 5 bundle is desired.
3. **External Archive B — Full Forensic Audit Trail (`~2.58 GiB` uncompressed):**
   - Archive A plus preserved HOLDs (`axd-g2-v2-off-design3`, `axd-g2-v2-off-design3_1`, `axd-g2-v2-design3-qualification-20261124T082344Z`), `design-2` preflight bundles, Stage 5 (`644 MiB`), Stage 6 (`40 MiB`), and G1 (`12 MiB`).
4. **Pre-Publication Hygiene Check:** Raw `start.json`, `manifest.json`, and `host.jsonl` files contain local usernames (`/home/thinhbui/...`), process lists (`comm`), and host metadata. Before any **public** upload, owner should confirm whether local absolute paths/usernames are acceptable for institutional/public release or should stay in restricted archival storage (note: sanitizing paths would alter `BUNDLE.sha256` and must only be done on a clearly labeled redacted derivative, never overwriting original sealed evidence).

### 4.2 Owner Command Template for Local Archive Creation & Verification (Run Only When Approved)

```bash
EV="/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence"
ARCHIVE_DIR="/home/thinhbui/Documents/ChatGPT/Research ANN/archives"
mkdir -p "$ARCHIVE_DIR"

# Create deterministic Core Archive A (uncompressed tar + zstd or gzip; does NOT modify source dirs)
tar --sort=name --owner=0 --group=0 --numeric-owner -C "$EV" -czf \
  "$ARCHIVE_DIR/axd-g2-v2-design3_1-run2-core-evidence-20261125.tar.gz" \
  axd-g2-v2-off-design3_1_run2 \
  axd-g2-v2-off-design3_1_run2-analysis.json \
  axd-g2-v2-off-design3_1_run2.console.log \
  axd-g2-v2-quality-design3 \
  axd-g2-v2-design3-qualification-20261124T094602Z \
  axd-g2-v2-inputs-design3 \
  axd-g2-v2-approvals

(cd "$ARCHIVE_DIR" && sha256sum axd-g2-v2-design3_1-run2-core-evidence-20261125.tar.gz > ARCHIVE.sha256 && sha256sum -c ARCHIVE.sha256)
```
