# A×D G2 v2 (`design-3.1`) · Final Closeout Status (Git Push & Private Remote Archival Verified)

- **Closeout Date:** 2026-11-25
- **Protocol & Revision:** `AXD-G2-V2-3A-20261123` · frozen revision **`design-3.1`** (`AXD_G2_V2_DESIGN3_1_FREEZE_MANIFEST.json` SHA-256: `bc8974193970b1663a53e08bc7de16b91013f11866965f872a78d775b7b28f5e`)
- **Repository (`origin`):** `khaccodeghitam/ann-task-d-parallel` · Visibility verified **`PRIVATE`** (`isPrivate: true`, branch `main`)
- **Primary Evidence & Code Commit:** `4bc70ff867c3945f39514be7df86cadb9849671d` (exact 21-file allowlist; `LOCAL == REMOTE` verified)
- **Private Remote Release:** [`axd-g2-v2-design3.1-closeout-20261125`](https://github.com/khaccodeghitam/ann-task-d-parallel/releases/tag/axd-g2-v2-design3.1-closeout-20261125) (targets `4bc70ff867c3945f39514be7df86cadb9849671d`; `9/9` assets uploaded & independently round-trip SHA-256 verified)
- **Companion Closeout Documents:** [Final Audit](AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) · [Results](AXD_G2_V2_DESIGN3_1_RESULTS.md) · [Evidence Manifest](AXD_G2_V2_DESIGN3_1_EVIDENCE_MANIFEST.md) · [Closeout & G3 Decision](AXD_G2_CLOSEOUT_AND_G3_DECISION.md) · [Pre-Push Archival Ledger](AXD_G2_FINAL_ARCHIVAL_STATUS.md)

---

## 1. Final Closeout Status Summary

All audit, local archival, Git commit/push, private remote release upload, and independent round-trip SHA-256 verification gates have **PASSED**:

| Closeout Gate | Final Status | Verified Evidence |
|---|---|---|
| **Independent Final Audit** | **`AUDIT COMPLETE`** | **`AUDIT_PASS`**, `DISCREPANCIES_COUNT = 0`; `144/144` OFF (`1299/1299` `BUNDLE.sha256`), `18/18` Quality ON (`166/166` `BUNDLE.sha256`), `6/6` R90 graphs, `20k` bootstrap resamples, BUILD–SEARCH verified (`max_stat_diff = 0.0`). |
| **Local Evidence & Dependency Archival** | **`LOCAL ARCHIVE COMPLETE`** | Sealed Tier 1 Core (`238.51 MiB`, `1,505` files, `5/5` nested `BUNDLE.sha256`), sealed Tier 2 Forensic (`534.69 MiB`, `3,565` files, `15/15` nested `BUNDLE.sha256`), and supplemental Private Dependency Archive (`944.38 MiB`, 6 R90 graphs TAR + frozen ELF, inner `6/6` `SHA256SUMS.txt` verified); original `artifact-evidence/` and `ARCHIVES.sha256` (`4/4 OK`) untouched. |
| **Git Repository Commit** | **`GIT COMMIT COMPLETE`** | Commit `4bc70ff867c3945f39514be7df86cadb9849671d` on `main` (exact `21`-file allowlist; `0` secrets, `0` raw evidence/datasets/graphs/ELF/archives; freezes `29/29`, `26/26`, `24/24` OK). This status document is preserved in the immediately following separate documentation closeout commit on `main`. |
| **Git Push Verification** | **`GIT PUSH VERIFIED`** | Pushed cleanly to PRIVATE `origin main` (`khaccodeghitam/ann-task-d-parallel`, `isPrivate=true`); `LOCAL_COMMIT_SHA == REMOTE_COMMIT_SHA`; no `--force` push; `upstream-irthn` untouched; no merges or PRs. |
| **Private Remote Release Upload** | **`REMOTE ARCHIVE COMPLETE`** | Created PRIVATE GitHub Release `axd-g2-v2-design3.1-closeout-20261125` targeting `4bc70ff867c3945f39514be7df86cadb9849671d` with all `9` release assets (`1.68 GiB` total) after confirming `isPrivate=true` and `visibility=PRIVATE`. |
| **Remote Integrity Verification** | **`REMOTE SHA256 VERIFIED`** | Independently downloaded all `9/9` assets into a clean temp directory; verified `RELEASE_ASSETS.sha256` (`8/8 OK`), `ARCHIVES.sha256` (`4/4 OK`), `9/9` exact local-vs-remote byte & SHA-256 match, `zstd -t` PASS and `tar --zstd -tf` exact member-list match against manifests for all `3` `.tar.zst` archives; temp dir cleaned without touching local evidence. |
| **G2 Research Closeout** | **`G2 CLOSEOUT COMPLETE`** | All scientific, engineering, provenance, Git, and private remote archival obligations for A×D G2 v2 (`design-3.1`) are complete and immutable. |
| **Program Cadence** | **`RESEARCH PAUSED`** | Execution paused cleanly after verified G2 closeout. No new benchmarks, no parameter/protocol changes, and no edits to Task A external spreadsheets were performed. |
| **Next-Phase Gate** | **`G3 NOT_OPENED`** | G3 / R91 / `design-3.2` remain strictly **`NOT_OPENED`** per owner closeout authorization and [AXD_G2_CLOSEOUT_AND_G3_DECISION.md](AXD_G2_CLOSEOUT_AND_G3_DECISION.md). |

---

## 2. Git Repository Provenance (`PRIVATE` `origin`)

- **Remote `origin`:** `https://github.com/khaccodeghitam/ann-task-d-parallel.git`
- **Verified Visibility (API/CLI):** `isPrivate: true` · `visibility: "PRIVATE"` · `viewerPermission: "ADMIN"`
- **Branch & Upstream:** `main` tracking `origin/main`
- **Untouched Remotes:** `upstream-irthn` (`Irthn1311/Parallel_ANN_Research`) was **NOT** pushed to, modified, or targeted.
- **Freeze Verification:**
  - `design-3.1`: `29/29 OK` ([AXD_G2_V2_DESIGN3_1_FREEZE.sha256](AXD_G2_V2_DESIGN3_1_FREEZE.sha256), manifest SHA-256 `bc8974193970b1663a53e08bc7de16b91013f11866965f872a78d775b7b28f5e`)
  - `design-3`: `26/26 OK` (manifest SHA-256 `425c748329292ffe15db2c52bdf53f5d219b47d1ecf95ac3c76a5429814159ae`)
  - `design-2`: `24/24 OK`
- **Commit Lineage on `origin/main`:**
  1. **Base pre-closeout parent:** `5bc7de698f38f1e0257e0b1cce2f39196de71ff0`
  2. **Primary G2 v2 `design-3.1` archival commit (21 allowlist files):** `4bc70ff867c3945f39514be7df86cadb9849671d` — `research(task-da): archive frozen G2 v2 design-3.1 package, independent audit, and closeout docs` (`LOCAL == REMOTE` verified; targeted by the private release tag `axd-g2-v2-design3.1-closeout-20261125`)
  3. **Separate Final Closeout Status documentation commit:** immediately follows `4bc70ff867c3945f39514be7df86cadb9849671d` on `main`, adding solely `docs/research/task-da/AXD_G2_FINAL_CLOSEOUT_STATUS.md` after verifying `REMOTE SHA256 VERIFIED`.

---

## 3. Private GitHub Release & Verified Asset Manifest (`9/9` Assets)

- **Release Tag:** `axd-g2-v2-design3.1-closeout-20261125`
- **Release URL:** `https://github.com/khaccodeghitam/ann-task-d-parallel/releases/tag/axd-g2-v2-design3.1-closeout-20261125`
- **Target Commit:** `4bc70ff867c3945f39514be7df86cadb9849671d`
- **Access Control:** Protected by repository visibility **`PRIVATE`** (`isPrivate: true`); never publish publicly because Tier 1/Tier 2 contain raw host `/proc` telemetry and local operational paths.

| # | Release Asset Filename | Size (`B`) | Size (Human) | Full SHA-256 | Local vs. Remote Match |
|---:|---|---:|---:|---|---|
| 1 | `axd-g2-v2-design3_1-tier1-core-20261125.tar.zst` | `250,096,372` | `238.51 MiB` | `5fdac3f82ececb225da0fa82cb92f1d5b78fbaae931f7d85c0ad46ec494fa363` | **`EXACT MATCH`** (`zstd -t` PASS · `1,505` members) |
| 2 | `axd-g2-v2-design3_1-tier1-core-20261125.manifest.json` | `398,721` | `389.38 KiB` | `4037f849bd6e4e7153376d2d3a205ff33a0f8f092d832d020700f0a72b515520` | **`EXACT MATCH`** |
| 3 | `axd-g2-v2-design3_1-tier2-forensic-20261125.tar.zst` | `560,663,082` | `534.69 MiB` | `1e160af6005da08cb1e03f0b3d3ea9fc1a412d471326b7378811f3052ef0e02a` | **`EXACT MATCH`** (`zstd -t` PASS · `3,565` members) |
| 4 | `axd-g2-v2-design3_1-tier2-forensic-20261125.manifest.json` | `959,024` | `936.55 KiB` | `25380c659ac8bc63780ba2fc9f4de3411ae6baf0048de83e52d8bc29db475bc3` | **`EXACT MATCH`** |
| 5 | `axd-g2-v2-design3_1-dependencies-r90-graphs-and-elf-20261125.tar.zst` | `990,252,799` | `944.38 MiB` | `626bac6ff34215ca8d3f94e9d0e3ebf0d7a4f330b3e1499e45fc99a0a65897e4` | **`EXACT MATCH`** (`zstd -t` PASS · `4` members) |
| 6 | `axd-g2-v2-design3_1-dependencies-r90-graphs-and-elf-20261125.manifest.json` | `6,791` | `6.63 KiB` | `6d7f471030f54baabff9793dbb293aca32bf54e01e327d1b0dbb85dc04c4aea7` | **`EXACT MATCH`** |
| 7 | `axd-g2-v2-design3_1-audit-provenance.json` | `1,948` | `1.90 KiB` | `08ea39c9c4bb845506f55990f4d4f73f78660c3944531ea5014701ddca6fac0b` | **`EXACT MATCH`** |
| 8 | `ARCHIVES.sha256` | `476` | `476 B` | `067448961f0796e1a13e81d7a4d97d6dfd6ee5bde5db1cfdbda982526756f54f` | **`EXACT MATCH`** (`4/4 OK`, sealed original untouched) |
| 9 | `RELEASE_ASSETS.sha256` | `942` | `942 B` | `5d9dcb39fed7365209ab154dbeda89103748d811a8d9174626e436aab9b039e5` | **`EXACT MATCH`** (`8/8 OK`) |

---

## 4. Independent Round-Trip Remote Verification Results

After upload completed, all `9` release assets were independently downloaded from GitHub Release `axd-g2-v2-design3.1-closeout-20261125` into a clean temporary directory (`/tmp/axd_g2_remote_verify_20261125/`) and audited:

- **Repository visibility check:** `isPrivate = true`, `visibility = PRIVATE` (**PASS**).
- **Remote Git commit check:** `git ls-remote origin refs/heads/main` == `4bc70ff867c3945f39514be7df86cadb9849671d` == local `HEAD` (**PASS**).
- **Asset count & upload state:** `9/9` assets in `state: "uploaded"`, API sizes identical to local and downloaded byte sizes (**PASS**).
- **Checksum checks on downloaded copies:** `sha256sum -c RELEASE_ASSETS.sha256` (`8/8 OK`), `sha256sum -c ARCHIVES.sha256` (`4/4 OK`), and independent SHA-256 comparison across all `9/9` downloaded vs. local files (`9/9 EXACT MATCH`) (**PASS**).
- **Archive stream & member integrity on downloaded `.tar.zst` files:**
  - `axd-g2-v2-design3_1-tier1-core-20261125.tar.zst`: `zstd -t` PASS · `tar --zstd -tf` exact `1,505`-path match to manifest (**PASS**).
  - `axd-g2-v2-design3_1-tier2-forensic-20261125.tar.zst`: `zstd -t` PASS · `tar --zstd -tf` exact `3,565`-path match to manifest (**PASS**).
  - `axd-g2-v2-design3_1-dependencies-r90-graphs-and-elf-20261125.tar.zst`: `zstd -t` PASS · `tar --zstd -tf` exact `4`-path match to manifest (**PASS**).
- **Local preservation & cleanup:** Temporary download directory deleted cleanly; local `../artifact-evidence/` and `../archives/` left completely intact.

---

## 5. External Dependencies Completeness & Remaining Limitations

Adding the supplemental Private Dependency Archive closes the single largest private-backup gap identified during archival preparation (all `6` Task A R90 v1.3 `.graph` artifacts + frozen `task_da_p2_eval` ELF), while strictly respecting third-party dataset and OS redistribution terms:

| Dependency Class | Preserved Remotely (PRIVATE)? | Location & Verification | Remaining Limitation / Re-acquisition Path |
|---|---|---|---|
| **Code, frozen protocol (`design-3.1`/`3`/`2`), schema, lockfile, audit CLI** | **YES (Git)** | `khaccodeghitam/ann-task-d-parallel` (`main`, `4bc70ff867c3945f39514be7df86cadb9849671d`) + [audit_g2_v2_design3_1_final.py](../../../scripts/audit_g2_v2_design3_1_final.py) + [g2_v2_design3_1_analyzer.py](../../../research/task_da/g2_v2_design3_1_analyzer.py) | Install locked Python wheels (`numpy==2.5.5`, `jsonschema==4.26.0`, etc.) on Python `3.12.3` from PyPI using `requirements-g2-v2-design3.lock` (`2f311d28...`). |
| **Raw Performance OFF (`144/144`), Quality ON (`18/18`), Qualification, Final Audit, Freeze Bundles** | **YES (Tier 1 & Tier 2)** | Release assets #1–#4 (`5/5` & `15/15` nested `BUNDLE.sha256` verified) + #7 `AUDIT_PROVENANCE.json` | None for offline re-analysis; Tier 2 additionally includes Stage 5 `b432` validation baselines (`82e740bc...`), Stage 6, G1 parity, and prior HOLD bundles. |
| **Task A `6` R90 v1.3 `.graph` files (`stock_r1..3`, `fast_r1..3`) & transfer TAR** | **YES (Dependency Archive)** | Release asset #5 (`626bac6f...`): original `TASK_A_R90_V13_MST1M_SIX_ORIGINAL_GRAPHS.tar` (`1,292,482,560 B`, SHA-256 `e59f5889f1271a801ff350866bfdffdf7764c372aac65e06d93c2d6a3c48029d`), inner `SHA256SUMS.txt` verified `6/6` | Fully recoverable from private GitHub Release; no longer dependent on local disk alone. |
| **Frozen native Release ELF `task_da_p2_eval`** | **YES (Dependency Archive)** | Release asset #5 (`626bac6f...`): `binary/task_da_p2_eval` (`211,176 B`, SHA-256 `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1`), source commit `f2cd634b...` | Executable requires compatible `x86_64` Linux `glibc >= 2.39` / `libstdc++6` runtime; timing reproducibility remains host-specific. |
| **MS-Turing-1M v1 dataset (`base.1M.fbin`, `query.public.100K.fbin`, `groundtruth.public.100K.ibin`)** | **NO (Pinned by SHA-256)** | Pinned in `EXTERNAL_DATASET_AND_OS_RUNTIME_MANIFEST.json` inside asset #5 (`44e83e1d...`, `48d087a1...`, `fa5acf5a...`) | Intentionally not redistributed to respect third-party dataset terms; publicly re-downloadable from `https://big-ann-benchmarks.com/neurips21.html` and verified against pinned SHA-256s. |
| **Ubuntu 24.04 OS runtime `.so` libs & toolchain (`g++-13`, `libc6`, `libstdc++6`, `libgcc-s1`, `python3.12`)** | **NO (Pinned by dpkg + SHA-256)** | Pinned in asset #5 manifest (`g++-13=13.3.0-6ubuntu2~24.04.1`, `libc6=2.39-0ubuntu8.12`, `libstdc++6=14.2.0-4ubuntu2~24.04.1`, `libgcc-s1=14.2.0-4ubuntu2~24.04.1`, `python3.12=3.12.3-1ubuntu0.17` + all `.so` SHA-256s) | Intentionally not redistributed; re-provision on Ubuntu 24.04 LTS x86_64. Exact latency magnitude is host-specific (`AMD Ryzen 5 PRO 4650U`, Linux `7.0.0-43-generic`). |

---

## 6. Audited Scientific Verdict, Claims & Explicit Boundaries

- **Independent Audit Verdict:** **`AUDIT_PASS`** (`DISCREPANCIES_COUNT = 0`; `audit_results.json` SHA-256 `c79e45a3482a702b8ca0aa48c68089c86875db025e002e8523109abb656e9c66`).
- **Primary Decisions (`AXD-G2-V2-3A-20261123` · `design-3.1`):**
  - **`GO_A_FIXED_COHORT`:** Mean latency reduction **`6.033151%`** (`CI95: [5.976580%, 6.089687%]`, speedup **`1.064205×`**) across `144/144` Performance OFF runs (`72` matched pairs, `12` balanced blocks, `1,299/1,299` `BUNDLE.sha256`, `NO_HOLD_JSON`, `noise_balance.imbalance_warning = false`; RAM hard gate, stability, and safety all **PASS**).
  - **`GO_B_SYSTEM_FIXED_COHORT`:** Across `18/18` Quality ON runs (`166/166` `BUNDLE.sha256`), duplicate L2 distance evaluations reduced **`74.98%`**, total L2 distance evaluations reduced **`12.22%`**, end-to-end BUILD+SEARCH total time **`30.336 s`** (`Q=100k`) and **`227.194 s`** (`Q=1M`); B quality gate **PASS**.
- **Mandatory Scientific Scope & Limitations (Non-Negotiable):**
  - **Evidence Label:** **`EXPLORATORY_HOST_SPECIFIC`**
  - **Graph-Population Inference:** **`graph_population_ci = NOT_ESTIMABLE`**
  - **Bounded Claim Scope:** Conclusions apply strictly to the fixed `6`-graph R90 v1.3 cohort (`3 stock + 3 fast`), `MS-Turing-1M` (`v2_test_10000`), fixed search configuration (`beam432`, `p2`, `S16`), and the measured quiet-TTY `AMD Ryzen 5 PRO 4650U` Ubuntu 24.04 host. No claim of population-level generalization across unseen graph cohorts, datasets, parameter regimes, or hardware platforms is made.
  - **Program Boundary:** **`G2 CLOSEOUT COMPLETE`** · **`RESEARCH PAUSED`** · **`G3 NOT_OPENED`**.
