# Báo Cáo Đối Chiếu Provenance Cuối Cùng Task D × Task A (P0/P1 Final Reconciliation)

**Ngày:** 2026-11-17  
**Nhánh Task D:** `research/task-d-a-p0-p1-20261115` (gốc commit `b0a95f4d4a8c0a5e9d100caa18c57ef448fe8251`, `main` nguyên vẹn, PR #57 giữ trạng thái closed/unmerged)  
**Repo Task A đồng bộ cục bộ:** `/home/thinhbui/Documents/ChatGPT/Research ANN/task-a` (`main` tại `f0c33362b622fb768b5533aa6fd9ebdf7cd2781a`)  
**Tài liệu đối chiếu cùng bộ:** [P0_P1_FINAL_RECONCILIATION_SUMMARY.json](P0_P1_FINAL_RECONCILIATION_SUMMARY.json), [P0_P1_FINAL_RECONCILIATION_SUMMARY.csv](P0_P1_FINAL_RECONCILIATION_SUMMARY.csv), [experiment_manifest_v3_reconciled.json](experiment_manifest_v3_reconciled.json)  
**Bản v1/v2 được giữ nguyên hoàn toàn:** [experiment_manifest.yaml](experiment_manifest.yaml), [PRE_REGISTRATION.md](PRE_REGISTRATION.md), [experiment_manifest_v2_resolved.json](experiment_manifest_v2_resolved.json), [PROTOCOL_V2.md](PROTOCOL_V2.md), [P0_P1_V2_RECOVERY_AND_SMOKE_REPORT.md](P0_P1_V2_RECOVERY_AND_SMOKE_REPORT.md)  
**Thư mục evidence ngoài repo (không ghi đè lịch sử):**
- Evidence kiểm toán cuối cùng này: `artifact-evidence/p0-p1-final-reconciliation-20261117T223637+0700`
- Gói thu hồi Task A (input mới): `artifact-evidence/TaskA_R86_Artifact_Recovery_20261117`
- Gói recovery handoff v2: `artifact-evidence/p0-p1-recovery-20261117T161322+0700`
- Gói P1 bounded smoke v2: `artifact-evidence/p0-p1-v2-smoke-20261117T170810+0700`

---

## 1. Giải Quyết Checksum Cross-Host (`TASK_A_R86_CHECKSUMS.sha256` -> `thinhbui-linux`)

File gốc `/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/TaskA_R86_Artifact_Recovery_20261117/TASK_A_R86_CHECKSUMS.sha256` (SHA-256 `6bf86df550bd58bbdff653aca8e5117f1eb2873fc22b64fb94d4834de0a96c62`, 428 dòng) **được giữ nguyên 100%**, không tạo symlink giả `/home/tai`. Lệnh `sha256sum -c TASK_A_R86_CHECKSUMS.sha256` thất bại trên máy `thinhbui` (`exit_code=1`, 338 dòng lỗi `No such file or directory`) hoàn toàn do 338/428 dòng dùng đường dẫn tuyệt đối của máy `tai-linux` (`/home/tai/ann-task-a/...`), **không phải lỗi sai checksum**.

Khi ánh xạ qua `TASK_A_R86_RECOVERY_INVENTORY.csv` (338 dòng) và `TASK_A_R86_RECOVERY_INVENTORY.json` tới các gốc lưu trữ thực tế trên `thinhbui-linux`:

| Phạm vi kiểm tra | Tổng mục | `VERIFIED` | `NOT_TRANSFERRED` | `MISSING` | `HASH_MISMATCH` | Bằng chứng xác thực |
|---|---:|---:|---:|---:|---:|---|
| 90 dòng tương đối (`recovered_artifacts/...`) trong `TASK_A_R86_CHECKSUMS.sha256` | 90 | 90 | 0 | 0 | 0 | Trực tiếp trong `TaskA_R86_Artifact_Recovery_20261117` |
| 338 dòng `/home/tai/...` trong `TASK_A_R86_CHECKSUMS.sha256` & inventory | 338 | 327 | 11 | 0 | 0 | 90 tại `TaskA_R86_Artifact_Recovery_20261117`, 12 tại `/home/thinhbui/Documents/ChatGPT/graph`, 225 tại `p0-p1-recovery-20261117T161322+0700` *(ngoài ra 163/338 mục cũng khớp tại repo `task-a` commit `f0c33362`)* |
| **Tổng 428 dòng `TASK_A_R86_CHECKSUMS.sha256`** | **428** | **417** | **11** | **0** | **0** | Không có bất kỳ file sai hash nào |
| `+36` tệp `calib_{t0990,t0998}_beam_*.{json,log}` trong `p0-p1-recovery` (`9×4`) | 36 | 36 | 0 | 0 | 0 | Khớp `EVIDENCE_CHECKSUMS.csv` + `log_sha256` của `calibrated_*.json` |
| **Manifest checksum mới `THINHBUI_CHECKSUMS_LOCAL.sha256`** | **363 tệp duy nhất** | **363** | — | **0** | **0** | `sha256sum -c THINHBUI_CHECKSUMS_LOCAL.sha256` trả về **`exit_code=0`** (`363/363 OK`) |

Chi tiết 11 mục `NOT_TRANSFERRED` (loại trừ có chủ đích, không thuộc tập formal `A0/A1/A3` chuyển giao sang `thinhbui`):
- **9 companion heavy graphs (`A2, A4, D0 × r1..r3`):** `GRAPH_A2_R1..R3` (`964e8ce3...`, `d099a815...`, `aa791b42...`), `GRAPH_A4_R1..R3` (`149ec7f3...`, `69d3e528...`, `53a6b0d3...`), `GRAPH_D0_R1..R3` (`2dd3409c...`, `ff67de6d...`, `4d4b7755...`).
- **2 historical reference ELFs không chép vào `recovered_artifacts`:** `EXE_COMP_G0_STOCK_OFF_R86HW` (`r86_v1_2_builds/stock_off/...`, `ba8e621f...`) và `EXE_COMP_R85_A1C_EVAL_REF` (`r85_a1c_matched_search/r85_a1c_graph_recall`, `11587916...`).

---

## 2. Xác Minh Provenance Source-to-Binary & Cơ Chế Ngẫu Nhiên

Tất cả các tệp ELF được kiểm tra **hoàn toàn tĩnh** (`sha256sum`, `file -b`, `LC_ALL=C readelf -h/-n/-d/-p .comment`, `objdump -d --no-show-raw-insn`); **tuyệt đối không chạy bất kỳ ELF lịch sử nào**.

### 2.1. Chuỗi Source -> Patch -> Staged Tree -> Builders -> Search Evaluators

1. **Chuỗi source & patch tái tạo byte-exact (`210/210` files, `0` sai lệch):**
   - Repo cơ sở `H70` (`task-a/experiments/H70/pipnn-clean-443a328`) thuộc commit upstream `443a328dc71a3b7be753d52ca2b3c9a4ba77f3fd`.
   - Áp dụng ngược `H70_git_diff.patch` (`d6bcbe9aaae95c0916fa58599355cc93040a19ff41b89bb6109a7b3be5739121`) bằng `patch -p1 -R --batch --dry-run` lên `H70` cho `rc=0` (chứng minh `H70` dirty ĐÚNG trên 4 file: `CMakeLists.txt`, `algorithms/PipNN/CMakeLists.txt`, `pipnn.h`, `pipnn_utils.h`).
   - Áp dụng xuôi `R86_counter_source_v1_2.patch` (`70c9088092f58c16be6835cddad6710003216723164bd74fff81510c909e0a8c`, khớp `R86_STAGING_PROVENANCE.json` và `g0_manifest.json`) bằng `patch -p1 --batch --forward` lên `H70` cho `rc=0`, tạo ra cây source trùng khớp từng byte trên toàn bộ **210/210** tệp của `R86/r86_v1_2_source` (chỉ bỏ qua 8 symlink lủng `*/parlay` và file metadata `R86_STAGING_PROVENANCE.json`).
   - 4 tệp lõi khớp `jvYREW/source_sha256.txt`: `CMakeLists.txt` (`198badc6...`), `algorithms/PipNN/CMakeLists.txt` (`19d5eb89...`), `algorithms/PipNN/pipnn.h` (`77a9b97e...`), `algorithms/PipNN/pipnn_utils.h` (`33b09c3c...`).

2. **CMake, Dependencies, Depfiles & Builder ELFs (`jvYREW` & `MVzZH3`):**
   - `FETCHCONTENT_FULLY_DISCONNECTED=ON` pin 4 thư viện ngoại tuyến: `highway` (`6bc2d47793bae9c521fb4150936669647700765d`), `parlaylib` (`51017699dcc421f80479cdb238d3092233ad0d26`), `eigen` (`3147391d946bb4b6c68edd901f2add6ac1f31f8c`), `abseil-cpp` (`bc257a88f7c1939f24e0379f14a3589e926c950c`).
   - Compiler & flags: `/usr/bin/c++` GCC `13.3.0-6ubuntu2~24.04.1`, CMake `3.28.3`, `-march=native -ffast-math -O3 -DNDEBUG -std=gnu++17 -fPIE`, riêng `build_h17_off` thêm `-DR71_H17_TOP2=1`.
   - `cmake_pch.hxx.gch.d` trong cả `build_stock_off` và `build_h17_off` ghi 444 token đường dẫn `/home/tai/...`, xác nhận compiler đã nạp đúng 14 header từ `r86_v1_2_source` cùng đúng 4 `_deps`.
   - Hai bản build Stock OFF độc lập (`MVzZH3` `05:50 UTC` và `jvYREW` `07:29 UTC`) cho ra ELF **trùng từng byte** (`aa2d174e...`, BuildID `7abbf2c2...`), và khớp `A_builder_stock_off` (`A0`) cũng như `B_builder_h17_off` (`5f673586...`, `A1/A3`) trong toàn bộ 27 build logs/receipts và `campaign_manifest.json` (`f0d1d807...`).
   - **Phát hiện ISA tĩnh quan trọng:** `objdump -d` trên `A_builder_stock_off` và `B_builder_h17_off` phát hiện thanh ghi/lệnh **AVX-512 (`%zmm`, `uses_zmm_avx512=true`)** sinh bởi `-march=native` trên `tai-linux`, trong khi máy hiện tại `thinhbui-linux` dùng `AMD Ryzen 5 PRO 4650U` (Zen 2, tối đa AVX2, không hỗ trợ AVX-512).

3. **Search Evaluators (`v3` & `v4_highbeam`):**
   - `r86_msturing1m_eval_native_link_v3.json` và `r86_msturing1m_highbeam_v4_manifest.json` ghi đầy đủ câu lệnh `/usr/bin/c++` và danh sách static libs `.a`, cùng 11/11 header tại `h70_eval_headers/` khớp 100% `H70` (`443a328dc7`).
   - Khác biệt nguồn duy nhất giữa `v3` (`91078479...`) và `v4` (`6aa0e38a...`) là ngưỡng CLI `beam > 512` thành `beam > 4096`. Cả hai đều liên kết tĩnh qua `_deps` của `r86_v1_2_builds/stock_off` (`highway` `0e0a01da...`) và dùng `checkRecall(..., /*random=*/false, /*start_point=*/0u, /*k=*/10L, QueryParams(10L, beam, 1.35, ...))`.
   - Cả `C_search_eval_v3` (`ea6c757b...`, BuildID `bbac7c10...`) và `D_search_eval_v4_highbeam` (`bb6576ad...`, BuildID `3edea046...`) đều dùng `GCC 13.3.0` và không sinh `-MD/-MF` compiler `.d` depfile (compile logs `0` byte `e3b0c442...`).

| ELF (bên trong `recovered_artifacts/executables/`) | Vai trò | Size (B) | SHA-256 | BuildID (SHA-1) | AVX-512 `%zmm` |
|---|---|---:|---|---|---|
| `A_builder_stock_off/neighbors-pipnn_FLOAT_T_EUCLIDEAN` | Builder Stock OFF (`A0`) | 2,836,408 | `aa2d174ed063070045f1fbbc8051b1d97b851168b2f3bf53ee32215a867583be` | `7abbf2c2d610aff0e43b636fc87fd697de067db9` | Có (`true`) |
| `A_builder_stock_off_MVzZH3_duplicate/...` | Bản control trùng byte | 2,836,408 | `aa2d174ed063070045f1fbbc8051b1d97b851168b2f3bf53ee32215a867583be` | `7abbf2c2d610aff0e43b636fc87fd697de067db9` | Có (`true`) |
| `B_builder_h17_off/neighbors-pipnn_FLOAT_T_EUCLIDEAN` | Builder H17 OFF (`A1/A3`) | 2,840,040 | `5f673586210f93b424fc81791ec7873cb74600843b5004c0a4aaaf32bf936297` | `930b31acc375459f7a02723312e1b7620ae45ba9` | Có (`true`) |
| `C_search_eval_v3/r86_msturing1m_graph_recall_v3` | Search eval `v3` (`beam<=512`) | 553,840 | `ea6c757b47b1267b7009ff0a1a80a3fdeaaf59740c4c2036712accf9ba0d0af5` | `bbac7c10ab38f7063081c6c06c02c5df86680b87` | Không (`false`) |
| `D_search_eval_v4_highbeam/r86_msturing1m_graph_recall_v4_highbeam` | Search eval `v4` (`beam<=4096`) | 553,856 | `bb6576ad3e1e0cc770535aa06355c664993ca70bd1170d6dd4d202ab5767e144` | `3edea046a21c076d27cc233f0dfeda125d7b06fa` | Không (`false`) |
| 4 companion ELFs (`D0_v2`, `jvYREW_stock_on`, `jvYREW_h17_on`, `G11_counter64`) | Companions `R86` | — | `7c2aad71...`, `396ef852...`, `ef707479...`, `a98b8748...` | `1fed297b...`, `3508e967...`, `5d215929...`, `39627f90...` | — |

### 2.2. Kiểm Toán `SEED = 555` và Đường Dẫn Randomness

- **Không tồn tại CLI `-seed`:** `neighborsTime.C` và `parse_command_line.h` không nhận cờ `-seed`; các file `build_command.json` / `build_result.json` không ghi trường `seed`, vì vậy **`runtime seed = NOT_RECORDED`**.
- **Đường dẫn thực tế trong `r86_v1_2_source`:**
  - `pipnn.h:498` gán cứng `size_t SEED = 555;`, truyền vào `RecursivelySketch` (`425`), và cập nhật qua `SEED = parlay::hash64(SEED);` (`429`) giữa 2 cluster pass (`num_clusters=2`).
  - `RecursivelySketch` (`325, 352`) dùng `next_seed = parlay::hash64(seed)` và `next_seed + cluster_id`; `SelectAndAssignLeaders` (`253`) dùng `seed + depth * 1337 + i * 7` cấp cho `std::mt19937 prng(seed)` (`70`); `SplitDuplicates` (`181`) dùng `std::mt19937 prng(seed + depth + parent_size)`.
  - Đoạn `std::random_device rd; std::mt19937 rng(rd()); parlay::random rnd(uni(rng));` ở `pipnn.h:373–376` tạo biến cục bộ `rnd` **hoàn toàn không được dùng** trong toàn bộ `pipnn.h`.
  - `SketchHash` / `Hash_Family` (`hash.h:15`) dùng mặc định `int seed = 0`; dòng `G[i].random_permute()` (`pipnn.h:557`) bị comment bỏ.
- **Hệ quả phương pháp luận:** Biến thiên SHA-256 giữa 3 graph `r1, r2, r3` trong mỗi arm phát sinh từ thực thi song song **`PARLAY_NUM_THREADS=4`** (`taskset -c 0,2,4,6`, thứ tự chèn/evict có khóa vào LSH reservoir trong `merge_neighbors`), **chứ không phải từ các RNG seed độc lập**. Do đó không suy diễn runtime seed và không tuyên bố 3 graph replicate là các mẫu ngẫu nhiên độc lập theo nghĩa PRNG seed riêng biệt.

---

## 3. Blockers Đã Đóng vs Blockers Còn Lại (v2 -> v3 Reconciled Preflight)

Chạy `python3 -m research.task_da.preflight docs/research/task-da/experiment_manifest_v3_reconciled.json --artifact-root "/home/thinhbui/Documents/ChatGPT/graph"` (lưu log ở `p0-p1-final-reconciliation-20261117T223637+0700/preflight_v3_reconciled.json`):
- **Kết quả:** `exit_code = 1`, `scope = ARTIFACT_PREFLIGHT_ONLY`, `P0 = HOLD`, `P1 = HOLD`, `12/12 AVAILABLE`, `9/9 structure PASS`, số blockers giảm từ **`28` (v2) xuống còn `10` (v3)**.

### 3.1. Các blockers đã đóng hoàn toàn hoặc đóng ở chuỗi builder
- `campaign_manifest.json` (`f0d1d807...`): **ĐÓNG**.
- 4/4 ELF lịch sử bắt buộc (`aa2d174e...` × 2, `5f673586...`, `ea6c757b...`, `bb6576ad...`) + 4 companion ELFs: **ĐÓNG**.
- 18 blockers `build_source_commit` và `build_source_diff_sha256` trên 9 graph (`preflight` v2 -> v3): **ĐÓNG** qua H70 `443a328dc7` + 2 patch + `210/210` files khớp byte.
- CMake metadata, `flags.make`, `link.txt`, `CMakeCache.txt`, `compile_commands.json`, `cmake_pch.hxx.gch.d`, 4 dependency commits cho builders: **ĐÓNG**.
- JSON manifests compile/link và `11/11` H70 headers cho evaluator `v3/v4`: **ĐÓNG** (chỉ khuyết `.d` depfile).
- Mapping cross-host checksum trên `thinhbui` (`363/363` file cục bộ `sha256sum -c` rc=0, phân tách 11 `NOT_TRANSFERRED`): **ĐÓNG**.

### 3.2. Các blockers còn lại (không tự nâng toàn bộ P0 lên PASS)
1. **`R86_RUNTIME_SEED_RECEIPT` (`NOT_RECORDED`, 9 blockers trong `preflight`):** Chưa từng có CLI `-seed` hay bản ghi runtime seed; 3 replicate `r1..r3` dùng chung `SEED=555`.
2. **`R86_CONTEMPORANEOUS_HOST_RECEIPT` (`HISTORICAL_UNRECOVERABLE`, phần tử blocker thứ 10):** R86 (13–15/11/2026) không lưu receipt `lscpu`/NUMA/SMT/`scaling_governor`/thermal/`MemTotal`/`/etc/os-release` cùng thời điểm (H85 ngày 11/11 chỉ là bối cảnh, còn ELFs R86 dùng AVX-512 trong khi `thinhbui-linux` là Zen 2 AVX2).
3. **`CURRENT_HOST_QUALIFICATION` (`NOT_QUALIFIED` cho P3):** `thinhbui-linux` (`AMD Ryzen 5 PRO 4650U`, 6 cores / 12 threads SMT on, governor `schedutil`) chưa được chuẩn hóa cấu hình đo P3.
4. **`MS_TURING_1M_REPRO_MANIFEST.json` (`MISSING` — chưa từng được tạo ở Task A)** và chứng nhận brute-force toàn bộ 100K GT ngoài 35 query đã kiểm chứng (`NOT_CERTIFIED_FULL_100K_EXACT`).
5. **`EVAL_V3_V4_COMPILER_DEPFILE` (`NOT_VERIFIED`):** Thiếu `.d` do gọi trực tiếp `g++` không `-MD/-MF`.
6. **`R86_V1_2_SOURCE_STANDALONE_GIT_COMMIT` (`NOT_RECORDED`):** Thư mục staging không có `.git` (đã thay thế bằng chứng minh patch chain `H70 -> R86`).
7. **Full P1 validation/calibration chưa chạy** (mới chạy P1 bounded smoke 32 queries trên `A0-R1` & `A3-R1`).

---

## 4. Phân Loại Quyết Định Gate Theo 7 Phạm Vi (+ P0 Tổng Thể)

| # | Phạm vi | Quyết định | Căn cứ trực tiếp |
|---:|---|---|---|
| 1 | **`P0 binary/artifact identity`** | **PASS** *(trong phạm vi A0/A1/A3 + 4/4 ELF chính)* | `417/428` dòng `TASK_A_R86_CHECKSUMS.sha256` + `36` `calib_*` (`363/363` file cục bộ) PASS `sha256sum -c`; `12/12` graph/data + `261/261` receipts + `4/4` ELF bắt buộc khớp SHA; `11` mục ngoài scope (`A2/A4/D0` graphs & 2 ref ELFs) ghi rõ `NOT_TRANSFERRED`; `0` sai hash. |
| 2 | **`P0 source/build provenance`** | **PASS_SCOPED_WITH_DOCUMENTED_GAPS** | Chuỗi `H70 443a328dc7` -> 2 patches -> `210/210` files `r86_v1_2_source` -> `jvYREW` CMake/flags/depfiles/`_deps` -> BuildID & GCC `13.3.0`, plus `v3/v4` manifest & source `SEED=555` đều đã kiểm chứng. Mở có giới hạn rõ: thiếu `.git` riêng trong `r86_v1_2_source`, thiếu `.d` depfile ở `v3/v4`, thiếu `MS_TURING_1M_REPRO_MANIFEST.json`, và runtime `seed = NOT_RECORDED`. |
| 3 | **`P0 historical host reproducibility`** | **HOLD (`HISTORICAL_UNRECOVERABLE` / `HOST_MISMATCH`)** | Không có R86 contemporaneous host/governor/thermal/NUMA/SMT receipt; hơn nữa binary build gốc chứa AVX-512 `%zmm` trong khi `thinhbui-linux` là Zen 2 AVX2 + `schedutil`. Không thể tái lập thời gian/QPS lịch sử trên máy hiện tại. |
| — | *`P0 overall` (cổng tổng thể `PRE_REGISTRATION.md`)* | **HOLD** | Theo `PRE_REGISTRATION.md` và `preflight` (`exit=1`, `10` blockers), không nâng toàn bộ P0 thành blanket PASS. Nếu muốn tiếp tục trên 9 graph `A0/A1/A3 × R1..R3` đã xác thực byte, protocol P1/P2 của Task D phải ghi rõ chấp nhận 9 graph bất biến này với giới hạn seed/host lịch sử không thể hồi phục (mọi phép đo mới chạy hoàn toàn bằng common-engine trên host đã qualify). |
| 4 | **`P1 GT và graph compatibility`** | **PASS_UNDER_PROTOCOL_V2** | `9/9` graph PASS `graph_audit.py` dưới `entry_point=0` (`A3-R2` node `840923` giữ nguyên); GT `fa5acf5a...` bất biến, opt-in `--gt-aux-min -1e-5` (mặc định giữ `0.0`) xử lý đúng 3 giá trị `-2.38e-7..-3.58e-7`, khớp `check_nn_recall.h` ID-only và `510/510` unit tests PASS. *(Chú ý: full 100K GT exactness ngoài 35 query vẫn `NOT_CERTIFIED`).* |
| 5 | **`P1 bounded correctness smoke`** | **PASS_SCOPED_CORRECTNESS_ONLY** | `task_da_smoke` (`0d462c09...`) chạy `p=1` ON/OFF trên `A0-R1` (`beam=384`, `Recall@10=0.9875`) và `A3-R1` (`beam=832`, `Recall@10=0.96875`), `q=[0..31]`: IDs và `squared_l2` ON/OFF trùng khớp 100%, sai số tối đa vs f64 là `7.77e-16`. Không kết luận về 100K Recall floor hay QPS/latency. |
| 6 | **`Full P1 validation/calibration`** | **READY_TO_EXECUTE_NOT_YET_RUN** | Điều kiện provenance, GT validator v2 và smoke correctness đều đã đạt; chỉ còn việc xây dựng & chạy chiến dịch validation/calibration 1-worker trên common-engine cho toàn bộ 9 graph (`A0, A1, A3 × R1..R3`) theo `PRE_REGISTRATION.md`. |
| 7 | **`P2/P3 readiness`** | **HOLD (CHƯA SẴN SÀNG)** | **P2 multi-walker** bị chặn bởi Full P1 validation/calibration + tài liệu thiết kế/đặc tả P2 (`p=1` parity, race tests, counter mở rộng). **P3 benchmark** bị chặn thêm bởi host qualification trên `thinhbui-linux` (hoặc máy benchmark mục tiêu). |

---

## 5. Kế Hoạch Thực Hiện Full P1 Validation / Calibration (Tiếp Theo)

Do 12/12 asset dữ liệu/graph, provenance builder/source, và GT Protocol v2 đã được kiểm chứng, phần còn thiếu để đóng P1 là thực thi quy trình validation/calibration bằng **một common-engine duy nhất** (`task_da::Index` với `entry_point=0`, không dùng các ELF lịch sử AVX-512):

1. **Chuẩn hóa tập query split tiền đăng ký (`PRE_REGISTRATION.md`):**
   - Tạo và lưu SHA-256 của bảng phân tách cố định từ 100,000 query ID sắp xếp theo `SHA256("task-da-v1:20261115:<decimal-id>")`: **10,000 queries đầu làm validation**, **90,000 queries còn lại giữ nguyên cho test** (không chạm test split khi hiệu chỉnh beam).
   - Kiểm tra xem 4 query bị ảnh hưởng bởi node `840923` trên `A3-R2` (`23741, 47069, 66279, 89193`) và 3 query có rank-0 negative (`45219, 48571, 95033`) rơi vào split nào; nếu có trên 10K validation, chạy kiểm tra brute-force `float64` toàn bộ 10K validation (và lý tưởng cả 100K GT nếu muốn nâng GT từ `NOT_CERTIFIED` lên `CERTIFIED`).
2. **Xây dựng runner calibration phi-thời-gian (`non-timing` P1 validation binary/evaluator):**
   - Mở rộng ngoài giới hạn `32` query của `task_da_smoke` sang công cụ `P1` tách riêng khỏi P3 timing (sử dụng `--gt-aux-min -1e-5` làm chính sách đo Recall theo Protocol v2, lưu toàn bộ JSONL/summary ở thư mục evidence mới ngoài repo).
   - So sánh đối chiếu chính sách dừng giữa `entry_best_first_v1` (không dùng `cut=1.35`) và `QueryParams(cut=1.35)` của Task A nếu `entry_best_first_v1` ở beam tham chiếu không đạt floor `0.990`/`0.998`.
3. **Sweep calibration triển vọng trên toàn bộ 9 graphs (`A0, A1, A3 × R1..R3`, `p=1`):**
   - Chạy lần lượt cho từng graph (không ghi đè, không bỏ chạy chậm) trên tập **10,000 validation queries**, dùng dải beam rộng thay vì giả định beam của Task A (`384/896`, `832/2176`).
   - Ghi nhận: (a) điểm vận hành đạt ngưỡng `0.990` và `0.998` của từng graph (`R1..R3`); (b) mức khớp Recall song đôi (`|ΔRecall| <= 0.0001` theo `PRE_REGISTRATION.md`) giữa `A0`, kiểm chứng điều khiển `A1`, và `A3`; (c) đối chứng **ON vs OFF semantic parity** ở quy mô 10K validation trên các beam ứng viên.
4. **Đóng băng cấu hình P1 & kiểm tra ngoại lệ `A3-R2`:**
   - Công bố bảng calibration P1 trên `docs/research/task-da/` và khóa cấu hình beam ứng viên trước khi mở bất kỳ thử nghiệm P2/P3 nào trên tập 90K held-out.

---

## 6. Điều Kiện Bắt Buộc Để Mở Khóa P2 Multi-Walker (và Chuẩn Bị P3)

Chỉ được mở triển khai **P2 multi-walker (`p = 1, 2, 4`)** và sau đó **P3 benchmark** khi thỏa mãn đầy đủ các cổng sau:

1. **Cổng P0/P1 tiên quyết:**
   - **Full P1 validation/calibration hoàn tất & PASS** trên đủ 9 graph (`A0, A1, A3 × R1..R3`) ở `p=1` với common-engine.
   - Quyết định chính thức của owner cho P0: chấp nhận tái sử dụng 9 graph bất biến với phạm vi P0 `HOLD` đã tài liệu hóa (không suy diễn runtime seed hay host lịch sử `tai-linux`) làm điểm tựa bất biến cho phép đo mới của Task D.
2. **Điều kiện mở P2 Multi-Walker (chưa đo latency/speedup chính thức):**
   - Tài liệu thiết kế rõ kiến trúc song song trong nội bộ truy vấn: cấu trúc queue cục bộ (`local beam/pending`), quyền sở hữu/đồng bộ bảng `visited` (bitmap/lock-free), cơ chế `merge`, quy tắc kết thúc xác định hay speculative, và giữ nguyên `entry_point=0`, không sửa topology graph.
   - Mở rộng `counter_schema.json` cho các counter hiện còn đánh dấu `NOT_MEASURED` khi `p > 1` (`multi_worker_distance_attribution`, `duplicate_expansions_trace`, `sync_wait`, `merge_count`, `idle_cycles`).
   - **Kiểm tra đúng đắn bắt buộc:** chế độ `p=1` của code P2 phải khớp byte/IDs/distances với `entry_best_first_v1`; `p=1, 2, 4` vượt qua **ThreadSanitizer / AddressSanitizer** trên fixture tổng hợp và kiểm tra `beam=n` vs exact-oracle trước khi chạy trên 1M graph.
3. **Điều kiện bổ sung trước khi mở P3 Benchmarking (chưa chạy ở bước này):**
   - **Host Qualification trên máy chạy thực tế (`thinhbui-linux` hoặc máy đo mới):** khắc phục/cố định chính sách tần số (`schedutil` -> `performance` hoặc thiết lập được phê duyệt có kiểm soát bởi host owner), lập bản đồ nhân vật lý/SMT và policy `taskset`/`OMP`/`PARLAY` trên 6 cores / 12 threads Zen 2, khóa RAM resident (`O(n)` visited allocation không bị tái cấp phát lặp trong vòng timing, loại I/O khỏi search timer theo `PRE_REGISTRATION.md`), ghi thermal/frequency throttling guard và ngưỡng ổn định pilot trước/sau mỗi run.
   - **Tách bạch so sánh:** Không so sánh QPS thô giữa chạy trên `thinhbui-linux` (AVX2) với QPS lịch sử trên `tai-linux` (AVX-512).
