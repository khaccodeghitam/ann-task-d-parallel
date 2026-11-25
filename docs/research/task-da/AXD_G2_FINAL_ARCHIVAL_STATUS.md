# A×D G2 v2 (`design-3.1`) · Final Archival & Repository Closeout Status

- **Date:** 2026-11-25
- **Protocol & Scope:** `AXD-G2-V2-3A-20261123` · revision **`design-3.1`** (`bc897419...`) · **`GO_A_FIXED_COHORT`** · **`GO_B_SYSTEM_FIXED_COHORT`** · **`EXPLORATORY_HOST_SPECIFIC`** · **`graph_population_ci = NOT_ESTIMABLE`**.
- **Companion Closeout Documents:** [Final Audit](AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) · [Results](AXD_G2_V2_DESIGN3_1_RESULTS.md) · [Evidence Manifest](AXD_G2_V2_DESIGN3_1_EVIDENCE_MANIFEST.md) · [Closeout & G3 Decision](AXD_G2_CLOSEOUT_AND_G3_DECISION.md).

---

## 1. Gate-by-Gate Closeout Status Ledger

| Milestone | Status | Verification Summary |
|---|---|---|
| **Independent Final Audit** | **`AUDIT COMPLETE`** | **`AUDIT_PASS`** (`DISCREPANCIES_COUNT = 0`); `144/144` OFF (`1.44M` rows), `18/18` Quality ON (`180k` rows), `6/6` R90 graphs, `20k` bootstrap resamples, BUILD–SEARCH verified (`max_stat_diff = 0.0`). Independent audit sealed at `../../../../artifact-evidence/axd-g2-v2-final-audit-design3_1/` (`BUNDLE.sha256` `26a873dc...`, `4/4 OK`) and portable CLI script placed at [scripts/audit_g2_v2_design3_1_final.py](../../../scripts/audit_g2_v2_design3_1_final.py). |
| **Local Evidence Archival** | **`LOCAL ARCHIVE COMPLETE`** | Tier 1 Core (`238.51 MiB`, `1,505` files) and Tier 2 Forensic (`534.69 MiB`, `3,565` files) created under `../../../../archives/`, checksummed (`ARCHIVES.sha256`), fully extracted into temporary verification dirs, verified `100%` file-by-file against `.manifest.json`, and verified on all `5/5` (Tier 1) and `15/15` (Tier 2) nested `BUNDLE.sha256` seals. Original `artifact-evidence/` untouched (`134.96 GiB` free disk remaining). |
| **Git Repository Commit** | **`GIT COMMIT PENDING`** | Exact **21-file allowlist** audited (`0` binaries, `0` secrets, `0` raw JSONL, `0` tracked modifications, `56/56` dataset-free G2 regression tests PASS, freezes `29/29`, `26/26`, `24/24` OK). **No `git add`, `commit`, `push`, `merge`, or PR executed** — awaiting owner review & approval. |
| **Remote Private Archival** | **`REMOTE ARCHIVE PENDING`** | `origin` (`khaccodeghitam/ann-task-d-parallel`) is **`PUBLIC`** and must **NOT** receive unredacted raw archives; `upstream-irthn` (`Irthn1311/Parallel_ANN_Research`) is **`PRIVATE`**. Private remote upload options and round-trip SHA-256 verification protocol prepared (§6); **zero remote upload performed**. |
| **Formal G2 Closeout** | **`G2 CLOSEOUT PENDING`** | Remains pending until owner approves and completes (1) Git allowlist commit, and (2) verified private remote archive upload + checksum check. **G3 and R91 remain `NOT_OPENED`.** |

---

## 2. Verified Local Evidence Archives (`../../../../archives/`)

Both archives were built deterministically (`GNU tar`, sorted members, uid/gid `0`, single-threaded `zstd -6`) without modifying or deleting any file in `../../../../artifact-evidence/`.

| Archive / Metadata Artifact | Absolute Path | Files | Raw Size (`B`) | Compressed Size (`B` / `MiB`) | Ratio | Full SHA-256 | Restore & Nested BUNDLE Check |
|---|---|---:|---:|---:|---:|---|---|
| **Tier 1 — Core Reproducibility** | `/home/thinhbui/Documents/ChatGPT/Research ANN/archives/axd-g2-v2-design3_1-tier1-core-20261125.tar.zst` | `1,505` | `1,166,930,041` (`1.087 GiB`) | `250,096,372` (`238.51 MiB`) | `4.666×` | `5fdac3f82ececb225da0fa82cb92f1d5b78fbaae931f7d85c0ad46ec494fa363` | **`PASS`** (`1,505/1,505` files + **`5/5`** nested `BUNDLE.sha256`) |
| Tier 1 Manifest | `/home/thinhbui/Documents/ChatGPT/Research ANN/archives/axd-g2-v2-design3_1-tier1-core-20261125.manifest.json` | — | `398,721` | — | — | `4037f849bd6e4e7153376d2d3a205ff33a0f8f092d832d020700f0a72b515520` | **`PASS`** (`sha256sum -c`) |
| **Tier 2 — Full Forensic** | `/home/thinhbui/Documents/ChatGPT/Research ANN/archives/axd-g2-v2-design3_1-tier2-forensic-20261125.tar.zst` | `3,565` | `2,699,096,580` (`2.514 GiB`) | `560,663,082` (`534.69 MiB`) | `4.814×` | `1e160af6005da08cb1e03f0b3d3ea9fc1a412d471326b7378811f3052ef0e02a` | **`PASS`** (`3,565/3,565` files + **`15/15`** nested `BUNDLE.sha256`) |
| Tier 2 Manifest | `/home/thinhbui/Documents/ChatGPT/Research ANN/archives/axd-g2-v2-design3_1-tier2-forensic-20261125.manifest.json` | — | `959,024` | — | — | `25380c659ac8bc63780ba2fc9f4de3411ae6baf0048de83e52d8bc29db475bc3` | **`PASS`** (`sha256sum -c`) |
| Combined Checksums | `/home/thinhbui/Documents/ChatGPT/Research ANN/archives/ARCHIVES.sha256` | `4` | `476` | — | — | `067448961f0796e1a13e81d7a4d97d6dfd6ee5bde5db1cfdbda982526756f54f` | **`PASS`** (`4/4 OK`) |

### 2.1 Contents & Nested `BUNDLE.sha256` Verification After Full Temp Extraction

- **Tier 1 Core (`1,505` files, `5/5` nested bundles verified):**
  1. `artifact-evidence/axd-g2-v2-off-design3_1_run2/` (`1299/1299 OK`, `c2b4d8f1...`) + `axd-g2-v2-off-design3_1_run2-analysis.json` (`f0a35394...`) + `.console.log` (`c2a736c8...`)
  2. `artifact-evidence/axd-g2-v2-quality-design3/` (`166/166 OK`, `5e3a41d0...`) + `.console.log` (`0 B`)
  3. `artifact-evidence/axd-g2-v2-design3-qualification-20261124T094602Z/` (`2/2 OK`, `24fc2b71...`)
  4. `artifact-evidence/axd-g2-v2-final-audit-design3_1/` (`4/4 OK`, `26a873dc...`: `audit_results.json`, `independent_final_audit.py`, `audit_g2_v2_design3_1_final.py`, `AUDIT_PROVENANCE.json`)
  5. `provenance/local_freeze_bundles/axd-g2-v2-design3-freeze-20261124/` (`4/4 OK`, `69c1951b...`: frozen `off_plan_design3_final.json`, `quality_plan_design3_final.json`, `audit_design3.json`, `verification_suite_design3.log`)
  - Plus `axd-g2-v2-inputs-design3/` (`v2_test_10000.ids`), canonical Tier 1 owner approvals (`4` files), `provenance/query_splits/` (`val_10k.ids`, `warmup_val_100.ids`), `provenance/frozen_manifests/` (`11` frozen protocol/schema/lock/build-ref files), `provenance/graph_transfer_manifests/` (`TRANSFER_MANIFEST.json`, `SHA256SUMS.txt`), and `provenance/README_EXTERNAL_DEPENDENCIES.json`.
- **Tier 2 Forensic (`3,565` files, `15/15` nested bundles verified):**
  - Includes **all of Tier 1** (with full `axd-g2-v2-approvals/` directory, all `11` files) **plus**:
    - `axd-g2-v2-off-design3/` (`11/11 OK`, `cf7d991f...`) + `.console.log`
    - `axd-g2-v2-off-design3_1/` (`1080/1080 OK`, `bbc9f25d...`) + `.console.log`
    - `axd-g2-v2-design3-qualification-20261124T082344Z/` (`2/2 OK`, `178bada3...`)
    - `axd-g2-v2-preflight-20261124/` (`2/2 OK`, `cc079410...`) & `axd-g2-v2-preflight-recovery-20261124/` (`8/8 OK`, `02027ca0...`)
    - `axd-g2-validation-20261122-G81SkWjO/` (`562/562 OK`, `82e740bc...`, Stage 5 incl. `6` `b432` validation baselines)
    - `axd-g2-stage6-test-quality-20261123/` (`101/101 OK`, `cd65a8ac...`, Stage 6)
    - `axd-g1-runtime-20261122-Ik1dBvXi/` (`229/229 OK`, `46760827...`, G1 runtime parity & loader audit)
    - `provenance/local_freeze_bundles/axd-g2-v2-preapproval-audit-20261123-ge85t3xl/` (`10/10 OK`, `9c3afe41...`)
    - `provenance/local_freeze_bundles/axd-g2-v2-remediation-20261123-a3df2che/` (`36/36 OK`, `33693d7b...`)

---

## 3. Reproducibility & Dependency Completeness Audit (`self_contained = false`)

> [!IMPORTANT]
> **Neither Tier 1 nor Tier 2 is self-contained.** Re-running the frozen offline analyzer (`g2_v2_design3_1_analyzer.py`) requires Tier 1 + the `task-d` repository source + pinned Python `3.12.3` (`numpy==2.5.5`, `jsonschema==4.26.0`). Re-running the full independent audit (`scripts/audit_g2_v2_design3_1_final.py`, including `verify_artifacts()`, Recall@10 recomputation, and Stage 5 validation parity) requires the external dependencies explicitly inventoried below:

| Dependency | In Tier 1? | In Tier 2? | Storage Location & Source | Exact Full SHA-256 & Size | Accessibility |
|---|---|---|---|---|---|
| `6` R90 v1.3 `.graph` files | **NO** | **NO** | `task-d/.local/artifacts/task-a-r90-v13-six-original-graphs/TASK_A_R90_V13_MST1M_SIX_ORIGINAL_GRAPHS/` · Task A transfer TAR `e59f5889...`, commit `f5e48bb6...` | `stock_r1`: `db4f5257f06d7ca6df0a040d19590d201bc3e9b1eab7bf0f36265732969716cc` (`215,313,724 B`); `stock_r2`: `5de325e9bbb0b46208c4878b3af77ae79c7c1821096eb11064efab5c15d0ae84` (`215,413,516 B`); `stock_r3`: `a7eb1ad15ff31130ce8411169f19b41d9bde75577ad5b5416e1b53a90ecbd010` (`215,432,108 B`); `fast_r1`: `104a1bc69711e494dbf562772b867752dd915e53ff7ed4142763cdc98fb354e9` (`215,398,220 B`); `fast_r2`: `4b69a53c548cdb47714902c2201fe732daf668683056aae9efa724982e11731a` (`215,429,104 B`); `fast_r3`: `7c80157e8165e2792151e4934078fd7bd2fa2deebad2ad9864ba6aaf24da0462` (`215,460,436 B`) | Local disk + owner TAR backup (private Task A delivery; not on public URL) |
| `base.1M.fbin` | **NO** | **NO** | `../graph/data/MSTuring_1M_v1/base.1M.fbin` · Big-ANN-Benchmarks MS-Turing-1M | `44e83e1dd4c65999b75873101adc5ac06ca900d259a2befd05c2c3aa28ff4042` (`400,000,008 B`) | Public dataset (re-downloadable) + local disk |
| `query.public.100K.fbin` | **NO** | **NO** | `../graph/data/MSTuring_1M_v1/query.public.100K.fbin` · Big-ANN-Benchmarks MS-Turing-1M | `48d087a17bec15a5ec9ea526fe9bd14ac31bbbb5cd200817b341adbb77695644` (`40,000,008 B`) | Public dataset (re-downloadable) + local disk |
| `groundtruth.public.100K.ibin` | **NO** | **NO** | `../graph/data/MSTuring_1M_v1/groundtruth.public.100K.ibin` · Big-ANN-Benchmarks MS-Turing-1M | `fa5acf5ab262b42355296e99f920e6aa863f48820ca6f70fa37ca7966634c344` (`80,000,008 B`) | Public dataset (re-downloadable) + local disk |
| Query ID lists (`val`, `warmup`, `test`) | **YES** | **YES** | `artifact-evidence/axd-g2-v2-inputs-design3/` & `provenance/query_splits/` inside archive | `val`: `a3c948e9...`; `warmup`: `199ca606...`; `test`: `457abdc1...` | Inside both Tier 1 & Tier 2 archives |
| Stage 5 `b432` validation baselines (`6` files) | **NO** | **YES** | `artifact-evidence/axd-g2-validation-20261122-G81SkWjO/` (`BUNDLE` `82e740bc...`) | `e449dc71...`, `1cfd5446...`, `7a94e488...`, `b39a8414...`, `2e74388f...`, `f92d0412...` | Inside Tier 2 archive + local disk |
| Native ELF `task_da_p2_eval` & OS `.so` libs | **NO** | **NO** | `task-d/build-task-da/task_da_p2_eval` (source `f2cd634`, GCC `13.3.0`) + `/lib/x86_64-linux-gnu/` (`glibc 2.39`) | ELF `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1` (`211,176 B`); `libstdc++.so.6` `1fd75fe7...`, `libgcc_s.so.1` `d93224d2...`, `libc.so.6` `755a371e...`, `libm.so.6` `5dcc4d25...`, `ld-linux-x86-64.so.2` `5fc09408...` | Local Ubuntu 24.04 Ryzen host (source rebuildable from `f2cd634`, bit-identity not guaranteed on other OS) |
| Analyzer source, frozen protocol & audit script | Manifests/Audit **YES**; full repo **NO** | Manifests/Audit **YES**; full repo **NO** | `task-d` Git repo (`5bc7de6` + 21 allowlisted files) + pinned venv `/home/thinhbui/.local/share/axd-g2-v2-design2/venv` (`Python 3.12.3` `e50d468e...`, `requirements-g2-v2-design3.lock`) | `design-3.1` freeze `bc897419...`; `scripts/audit_g2_v2_design3_1_final.py` `41c22671...`; `audit_results.json` in `axd-g2-v2-final-audit-design3_1/` | Git repo (`origin` + `upstream-irthn`) + PyPI locked wheels (`--require-hashes`) |

---

## 4. Audited Git Commit Allowlist (`21` Files, Pending Owner Approval)

All `21` untracked files in `task-d/` were inspected (`0` tracked edits, `0` binaries, `0` secrets/tokens, `0` raw JSONL/graphs/datasets/archives; total `~345 KiB`; `56/56` dataset-free G2 regression tests PASS; freezes `29/29`, `26/26`, `24/24` OK).

| Category | Count | Exact Allowlist Paths |
|---|---:|---|
| **Research source code (frozen `design-3.1`)** | `3` | `research/task_da/g2_v2_design3_1_analyzer.py`, `research/task_da/g2_v2_design3_1_contract.py`, `research/task_da/g2_v2_design3_1_runner.py` |
| **Protocol, schema & freeze manifests** | `4` | `configs/axd_g2_v2_design3_1.schema.json`, `configs/axd_g2_v2_design3_1_approval.UNAPPROVED.json`, `docs/research/task-da/AXD_G2_V2_DESIGN3_1_FREEZE_MANIFEST.json`, `docs/research/task-da/AXD_G2_V2_DESIGN3_1_FREEZE.sha256` |
| **Tests, execution & independent audit scripts** | `6` | `tests/research/test_g2_v2_design3_1.py`, `scripts/prepare_quiet_tty_env.sh`, `scripts/run_g2_v2_design3_off.sh`, `scripts/run_g2_v2_design3_1_off.sh`, `scripts/run_g2_v2_design3_1_off_run2.sh`, `scripts/audit_g2_v2_design3_1_final.py` |
| **Research documentation & closeout suite** | `8` | `docs/research/task-da/AXD_G2_PREREG_V2_DESIGN3_1_AMENDMENT.md`, `docs/research/task-da/AXD_G2_V2_DESIGN3_OFF_EXECUTION_RUNBOOK.md`, `docs/research/task-da/AXD_G2_V2_DESIGN3_QUALITY_AUDIT_AND_OFF_READINESS.md`, `docs/research/task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md`, `docs/research/task-da/AXD_G2_V2_DESIGN3_1_RESULTS.md`, `docs/research/task-da/AXD_G2_V2_DESIGN3_1_EVIDENCE_MANIFEST.md`, `docs/research/task-da/AXD_G2_CLOSEOUT_AND_G3_DECISION.md`, `docs/research/task-da/AXD_G2_FINAL_ARCHIVAL_STATUS.md` |

**Explicitly excluded from Git (never stage):** `../artifact-evidence/`, `../archives/`, `.local/`, `build-task-da/`, `../graph/data/`, all `*.jsonl`, `*.graph`, `*.fbin`, `*.ibin`, `*.tar.zst`.

### Proposed Commit Command & Message (Execute ONLY After Owner Approval)

```bash
cd "/home/thinhbui/Documents/ChatGPT/Research ANN/task-d"
git add -- \
  configs/axd_g2_v2_design3_1.schema.json \
  configs/axd_g2_v2_design3_1_approval.UNAPPROVED.json \
  docs/research/task-da/AXD_G2_CLOSEOUT_AND_G3_DECISION.md \
  docs/research/task-da/AXD_G2_FINAL_ARCHIVAL_STATUS.md \
  docs/research/task-da/AXD_G2_PREREG_V2_DESIGN3_1_AMENDMENT.md \
  docs/research/task-da/AXD_G2_V2_DESIGN3_1_EVIDENCE_MANIFEST.md \
  docs/research/task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md \
  docs/research/task-da/AXD_G2_V2_DESIGN3_1_FREEZE.sha256 \
  docs/research/task-da/AXD_G2_V2_DESIGN3_1_FREEZE_MANIFEST.json \
  docs/research/task-da/AXD_G2_V2_DESIGN3_1_RESULTS.md \
  docs/research/task-da/AXD_G2_V2_DESIGN3_OFF_EXECUTION_RUNBOOK.md \
  docs/research/task-da/AXD_G2_V2_DESIGN3_QUALITY_AUDIT_AND_OFF_READINESS.md \
  research/task_da/g2_v2_design3_1_analyzer.py \
  research/task_da/g2_v2_design3_1_contract.py \
  research/task_da/g2_v2_design3_1_runner.py \
  scripts/audit_g2_v2_design3_1_final.py \
  scripts/prepare_quiet_tty_env.sh \
  scripts/run_g2_v2_design3_1_off.sh \
  scripts/run_g2_v2_design3_1_off_run2.sh \
  scripts/run_g2_v2_design3_off.sh \
  tests/research/test_g2_v2_design3_1.py
```

Proposed commit message:
```text
research(task-da): archive frozen G2 v2 design-3.1 package, independent audit, and closeout docs

- Add frozen design-3.1 OFF parser compatibility amendment (29/29 SHA-256 verified)
- Add quiet-TTY preparation, OFF runbook/wrappers, and portable independent audit script
- Record audited G2 v2 run2 closeout (AUDIT_PASS, GO_A_FIXED_COHORT -6.033%, GO_B_SYSTEM_FIXED_COHORT, EXPLORATORY_HOST_SPECIFIC)
- Document Tier 1/Tier 2 local evidence archives, external dependencies, and G3 decision (CLOSEOUT recommended; G3 not opened)
```

---

## 5. Sensitivity & Privacy Risk Audit

1. **Zero secrets/tokens/keys detected** across all `21` Git allowlist files (`0` hits for GitHub/AWS/JWT/private-key/password patterns).
2. **Local username & paths (`/home/thinhbui/...`) present in 12 Git allowlist files** (matching already-committed public files at `5bc7de6`). Because `origin` (`khaccodeghitam/ann-task-d-parallel`) is **`PUBLIC`**, owner should confirm acceptability before pushing to `origin` (noting frozen `design-3.1` files must not be edited without invalidating `AXD_G2_V2_DESIGN3_1_FREEZE.sha256`).
3. **Raw evidence archives (`Tier 1` & `Tier 2`) contain sensitive operational telemetry:** local usernames, absolute filesystem paths, full `/proc` process name snapshots (`host.jsonl`, `manifest.json`), hardware thermal/sensor paths, and signed approval metadata (`owner: "thinhbui"`). **Never upload raw Tier 1/Tier 2 archives to any public release or public bucket.**

---

## 6. Remote Private Archival Plan (`REMOTE ARCHIVE PENDING` — Zero Auto-Upload)

Both compressed archives fit comfortably under GitHub's `2 GiB` per-release-asset limit (`238.51 MiB` Tier 1, `534.69 MiB` Tier 2).

| Option | Target | Fit & Privacy | Remote SHA-256 Verification & Round-Trip Download |
|---|---|---|---|
| **Option 1 (Recommended — Best Fit with Existing `gh` Auth)** | **Private GitHub Release** on a **private** repository (either existing private `Irthn1311/Parallel_ANN_Research` if collaborator-authorized, or a dedicated new private archive repo e.g. `khaccodeghitam/ann-task-d-evidence-private`) | Strictly private (`isPrivate: true`); works immediately with logged-in `gh` CLI (`repo` scope); immutable tagged release assets (`< 2 GiB`) | Upload `.tar.zst`, `.manifest.json`, and `ARCHIVES.sha256`; verify via `gh release view <tag> --json assets` (API digest/size) + round-trip `gh release download` to `/tmp/verify_dl/` + `sha256sum -c ARCHIVES.sha256` |
| **Option 2 (Redundant Institutional Backup)** | **Private Google Drive / Institutional Cloud** (alongside existing private Task A/D research Drive folder) | Private access-controlled; easy advisor sharing without GitHub access; combine with Option 1 for 3-2-1 backup | Upload `Tier 1`, `Tier 2`, manifests, and `ARCHIVES.sha256`; re-download (or verify Drive MD5/SHA256 via API/rclone) and run `sha256sum -c ARCHIVES.sha256` locally |
| **Prohibited** | **`khaccodeghitam/ann-task-d-parallel` (`origin`) GitHub Releases** | **PUBLIC repo (`isPrivate: false`)** — violates raw-telemetry privacy constraint unless redacted derivative is explicitly approved | Do **NOT** upload unredacted Tier 1/Tier 2 archives here |

### Owner Remote Upload & Verification Template (Option 1 — Run Only After Owner Approves Target Private Repo)

```bash
# Example using a dedicated PRIVATE GitHub repository (replace <OWNER>/<PRIVATE_REPO> after creating/approving it)
PRIVATE_REPO="<OWNER>/<PRIVATE_ARCHIVE_REPO>"
TAG="axd-g2-v2-design3_1-archive-20261125"
ARCHIVES="/home/thinhbui/Documents/ChatGPT/Research ANN/archives"

# 0. Verify target repository is strictly PRIVATE before uploading
test "$(gh repo view "$PRIVATE_REPO" --json isPrivate -q .isPrivate)" = "true"

# 1. Create private release and upload archives + manifests + ARCHIVES.sha256
gh release create "$TAG" --repo "$PRIVATE_REPO" \
  --title "A×D G2 v2 design-3.1 Audited Evidence Archives (Private)" \
  --notes "Private Tier 1 Core (238.5 MiB) and Tier 2 Forensic (534.7 MiB) archives; NOT self-contained (external graphs/dataset/ELF pinned by SHA-256)." \
  "$ARCHIVES/axd-g2-v2-design3_1-tier1-core-20261125.tar.zst" \
  "$ARCHIVES/axd-g2-v2-design3_1-tier1-core-20261125.manifest.json" \
  "$ARCHIVES/axd-g2-v2-design3_1-tier2-forensic-20261125.tar.zst" \
  "$ARCHIVES/axd-g2-v2-design3_1-tier2-forensic-20261125.manifest.json" \
  "$ARCHIVES/ARCHIVES.sha256"

# 2. Round-trip download & remote SHA-256 verification
mkdir -p /tmp/axd_remote_verify && cd /tmp/axd_remote_verify
gh release download "$TAG" --repo "$PRIVATE_REPO"
sha256sum -c ARCHIVES.sha256
rm -rf /tmp/axd_remote_verify
```
