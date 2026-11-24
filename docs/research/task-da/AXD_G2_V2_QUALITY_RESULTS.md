# A×D G2 v2 · Quality-Only Preflight & Execution Results (`design-2`)

- **Stage 0 Preflight Status:** **`BLOCKED_PREFLIGHT`** *(dừng cứng trước Stage 1 theo quy tắc fail-closed; **không** nới guard, **không** tự gán `quiet_host_confirmed = true`, **không** tự ký approval).*
- **Stage 3 Gate Enum Verdict:** **`BLOCKED_EXECUTION_OR_PROVENANCE`** *(xem quyết định chính thức tại [AXD_G2_V2_QUALITY_GATE_DECISION.md](AXD_G2_V2_QUALITY_GATE_DECISION.md)).*
- **Protocol & Scope:** `AXD-G2-V2-3A-20261123` · revision `design-2` · `p=2`, `S=16`, `common beam = 432` · **`EXPLORATORY_HOST_SPECIFIC`** · `AMD Ryzen 5 PRO 4650U`.
- **Execution Counts:** `quality_ON_executed = 0 / 18` · `off_executed = 0 / 144` · `v2_test_10000.ids materialized = false` · `performance_claims = NONE`.
- **Preflight Raw Evidence Bundle:** [axd-g2-v2-preflight-20261124](../../../../artifact-evidence/axd-g2-v2-preflight-20261124/) · [BUNDLE.sha256](../../../../artifact-evidence/axd-g2-v2-preflight-20261124/BUNDLE.sha256) (`cc079410f73f8660bb2a0a913834536eee48c508d3220c49c0e2f33c03a6c40e`).

---

## 1. Kết quả Kiểm toán Stage 0 — Mandatory Preflight (7 Hạng mục)

Nguồn raw đầy đủ: [preflight_audit.json](../../../../artifact-evidence/axd-g2-v2-preflight-20261124/preflight_audit.json) (`e99bd5e6...`) và [live_quiet_observation.jsonl](../../../../artifact-evidence/axd-g2-v2-preflight-20261124/live_quiet_observation.jsonl) (`4ea27c7a...`).

| # | Hạng mục Stage 0 | Trạng thái | Bằng chứng xác minh trực tiếp |
|---:|---|---|---|
| **1** | Đọc `AXD_G2_V2_PRE_APPROVAL_REMEDIATION.md` & bộ protocol `design-2` | **`PASS`** | Đã đọc đầy đủ remediation (`99defa85...`), prereg v2 (`f197b4fa...`), split audit (`339437f1...`), GO/NO-GO (`243728d5...`), schema `axd_g2_v2.2` (`4584f91a...`), freeze manifest (`91186d57...`), `quality_plan_final.json`, và 4 module `g2_v2_{contract,guard,runner,analyzer}.py`. |
| **2a** | FINAL frozen SHA/checksums & 22 pinned components | **`PASS`** | `sha256sum -c docs/research/task-da/AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256` -> **`24/24 OK`** (`rc=0`); `configs/axd_g2_v2_freeze.json` = `91186d57e5992e1df70f86a55ba928ad4d6613bb0b67ccbee0f485cc380d1749`; **`22/22`** component files khớp từng byte; `.local/artifacts/axd-g2-v2-remediation-20261123-a3df2che/BUNDLE.sha256` xác minh `rc=0`. |
| **2b** | Exact Python dependency environment (`requirements-g2-v2.lock`) | **`FAIL (BLOCKER B3)`** | `/usr/bin/python3.12` khớp phiên bản `3.12.3` và SHA `e50d468e...`, nhưng môi trường tách biệt `/tmp/axd-g2-v2-preapproval-20261123-ge85t3xl/venv` **đã mất sau reboot** (`uptime = 23 min`). Cả `/usr/bin/python3` lẫn `.venv` đều **thiếu 7 gói khóa chính xác** (`numpy==2.5.5`, `jsonschema==4.26.0`, `attrs==26.1.0`, `jsonschema-specifications==2025.9.1`, `referencing==0.37.0`, `rpds-py==2026.9.1`, `typing_extensions==4.16.0`) -> `load_freeze(environment=True)` fail-closed. |
| **3** | Git status, untracked files & provenance runner / analyzer / compiler / native libs / binary | **`PASS`** | Nhánh `research/task-da-pivot-b1-a1-20261119`, `HEAD = f54b1bb653652dd13e760cc00c9fb46d0e643c1c`, `0` thay đổi tracked (`git diff` rỗng), `33` file overlay/doc chưa track đúng cấu trúc `wrapper_source_identity` của freeze. Runner (`d1de7a0c...`), analyzer (`97178bba...`), guard (`86ce14ed...`), contract (`565f7c3c...`), base guard (`232ed904...`), Release ELF `task_da_p2_eval` (`7a2685e5...`), `/usr/bin/c++` (`1353e9bd...`), `5/5` thư viện native `.so` khớp 100%; `LD_PRELOAD/LD_LIBRARY_PATH/LD_AUDIT` đều rỗng. |
| **4** | Six graph SHA, immutable inputs, Stage 5 b432 baselines & query/GT split SHA | **`PARTIAL / B4`** | **`6/6` graph R90 v1.3** (`db4f5257...`, `5de325e9...`, `a7eb1ad1...`, `104a1bc6...`, `4b69a53c...`, `7c80157e...`), **`5/5` input sẵn có** (`base` `44e83e1d...`, `queries` `48d087a1...`, `gt` `fa5acf5a...`, `val` `a3c948e9...`, `warmup` `199ca606...`), và **`6/6` Stage 5 b432 baseline JSONLs** khớp 100%. Riêng `v2_test_10000.ids` (SHA khóa `457abdc13abc95d8d0f48ff32919a6013f5ed4bca469f9075312ae80dfe44b0d`) **chưa tồn tại trên đĩa** (đúng thiết kế tiền phê duyệt; chỉ được materialize một lần sau khi có approval hợp lệ và preflight quiet PASS). |
| **5** | Host Ryzen, CPU affinity/topology, RAM, disk, nhiệt độ, AC & swap | **`PASS` (trừ CPU contention)** | `host_contract()` **PASS** (`AMD Ryzen 5 PRO 4650U`, `cpus=[0,2]`, `cores=['0','1']`, `siblings=['0-1','2-3']`, `l3_shared_lists=['0-5','0-5']`, `allowed_cpus=[0..11]`, `kernel=7.0.0-43-generic`, `clk_tck=100`). `k10temp Tctl = 48.375–57.875°C` (`<< 85°C`), `AC/online = 1`, `MemAvailable = 8.02 GiB` (`> 1 GiB`), `free_disk = 137.93 GiB` (`> 25 GiB`), `swap_used = 0 B`, không có named ANN/CPU job, không có lock tồn đọng `/tmp/task-da-pivot-4650u.lock`. |
| **6** | Xác minh host thực sự đủ quiet theo protocol (`foreign CPU <= 1%` of p2 capacity over `>= 5 s`) | **`FAIL (BLOCKER B1)`** | Quan sát đọc-chỉ 7 giây bằng đúng `g2_v2_guard.CoolingGuard` + `Contention`: **`foreign_busy_s / (wall_s × 2) = 0.5030 – 0.5441` (`50.3% – 54.4%`)**, vượt giới hạn đóng băng `0.01` (`1.0%` = `0.02` CPU-s/s trên toàn máy) tới **50×–54×**. Guard trả thẳng `['foreign CPU >1% of p2 capacity over >=5 seconds']`. Tác nhân chính: `msedge` (`PID 3014`: `0.95–1.20` CPU-s/s + các renderer khác), cộng thêm bản thân `agy` (`PID 6266`: `0.04–0.11` CPU-s/s = `2%–5.5%` p2 capacity!) và tiến trình desktop (`pipewire`, `ChatGPT`, `gnome-shell`). **Không thể gán `quiet_host_confirmed = true`.** |
| **7** | Approval artifact hợp lệ theo schema `axd_g2_v2.2` | **`FAIL (BLOCKER B2)`** | Chỉ tồn tại template cố ý không hợp lệ `configs/axd_g2_v2_approval.UNAPPROVED.json` (`0f76abc6...`, `scope = "UNAPPROVED"`, `owner = ""`, `approved_at = ""`, `quota_s = 0`, `quiet_host_confirmed = false`). **Chưa có tệp approval receipt bên ngoài do owner ký** cho đúng `freeze_sha256`, `artifacts_sha256`, `output_directory`, `scope = "QUALITY_ONLY"`, `quota_s = 3600`, và `quiet_host_confirmed = true` (sau khi host thực sự quiet). |

---

## 2. Nhật ký Quan sát Live Quiet-Host Telemetry (Read-Only, Không Can thiệp Tiến trình)

Trích từ [live_quiet_observation.jsonl](../../../../artifact-evidence/axd-g2-v2-preflight-20261124/live_quiet_observation.jsonl) (`7` khoảng đo 1 Hz liên tiếp bằng `g2_v2_guard.guard_module()`):

| Bước (`s`) | `Tctl (°C)` | `foreign_busy_s` (`s/s`) | Rolling `>= 5 s` fraction (`<= 0.01` bắt buộc) | Guard verdict | Top tiến trình cạnh tranh (`comm: CPU-s`) |
|---:|---:|---:|---:|---|---|
| `t+1` | `57.875` | `1.13` | `None` *(window < 5s)* | `[]` | `msedge` (1.03), `agy` (0.04) |
| `t+2` | `56.125` | `1.12` | `None` *(window < 5s)* | `[]` | `msedge` (1.01), `agy` (0.04) |
| `t+3` | `54.500` | `1.07` | `None` *(window < 5s)* | `[]` | `msedge` (0.98), `agy` (0.04) |
| `t+4` | `52.875` | `1.00` | `None` *(window < 5s)* | `[]` | `msedge` (0.90), `agy` (0.04) |
| **`t+5`** | `51.375` | `1.08` | **`0.5030` (`50.3%`)** | **`FAIL: foreign CPU >1%`** | `msedge` (`PID 3014`: 0.95, `2602`: 0.04, `5367`: 0.02), `agy` (`6266`: 0.04), `pipewire` (0.01) |
| **`t+6`** | `49.875` | `1.20` | **`0.5177` (`51.8%`)** | **`FAIL: foreign CPU >1%`** | `msedge` (>1.0), `agy` (0.04) |
| **`t+7`** | `48.375` | `1.34` | **`0.5441` (`54.4%`)** | **`FAIL: foreign CPU >1%`** | `msedge` (`PID 3014`: 1.20, `3071`: 0.02, `5367`: 0.02), `agy` (`6266`: 0.04), `pipewire` (0.01) |

- **Lưu ý kỹ thuật quan trọng cho owner:** Ngưỡng đóng băng `foreign_busy_s / (wall_s × 2) <= 0.01` tương đương **tổng CPU của toàn bộ tiến trình ngoài process đo + monitor trên cả 12 luồng phải `<= 0.02` CPU-s/s (`<= 2%` của một luồng đơn)**. Ngay cả khi tắt hẳn `msedge`, một phiên `agy` đang hoạt động (`0.04–0.11` CPU-s/s) cùng desktop GUI (`gnome-shell`, `ChatGPT`, `pipewire`) vẫn vượt `0.02` CPU-s/s; do đó cần kiểm tra quiet ở phiên terminal tối giản đã đóng trình duyệt/ứng dụng Electron **trước** khi xác nhận `quiet_host_confirmed = true`. Không tự ý kill tiến trình của user và không tự ý nới ngưỡng `0.01`.

---

## 3. Kế toán 18 Tiến trình Quality-Only ON theo `quality_plan_final.json`

Toàn bộ **`18/18`** tiến trình trong kế hoạch đóng băng ([quality_plan_final.json](../../../.local/artifacts/axd-g2-v2-remediation-20261123-a3df2che/quality_plan_final.json)) **CHƯA ĐƯỢC THỰC THI** do dừng tại Stage 0 `BLOCKED_PREFLIGHT`:

| Nhóm trong `quality_plan_final.json` | Số tiến trình kế hoạch | Valid | Invalid | Unexecuted (`BLOCKED_PREFLIGHT`) | Recall@10 / LCB95 / Parity / Invariants |
|---|---:|---:|---:|---:|---|
| Validation `opt` ON tại `beam=432` (`6` graph × `val_10k.ids`) | `6` | `0` | `0` | **`6`** | `NOT_MEASURED` |
| Test `base` & `opt` ON tại `beam=432` (`6` graph × `2` policy × `v2_test_10000.ids`) | `12` | `0` | `0` | **`12`** | `NOT_MEASURED` |
| **Tổng Quality-Only Phase** | **`18`** | **`0`** | **`0`** | **`18`** | **Chưa có phép đo Stage 1/Stage 2** |
| **G2 OFF Performance Phase (ngoài phạm vi duyệt)** | `144` | `0` | `0` | **`144` (`NOT_OPEN`)** | **`NOT_AUTHORIZED / NOT_OPEN`** |

- **Lưu ý giới hạn lịch sử (giữ nguyên không đổi):** Ngay cả khi Quality-Only Phase được mở khóa và chạy thành công sau này, toàn bộ kết quả vẫn mang nhãn **`EXPLORATORY_HOST_SPECIFIC`** do `public 100K` đã được Task A đánh giá, `test_90k` đã dùng trong R86/P1, và 6 graph R90 v1.3 có `root independence NOT_VERIFIED` (`independent-root population CI = NOT_ESTIMABLE`).

---

## 4. Chỉ mục Tái lập & Bảo toàn Bằng chứng (Reproducibility Index)

| Artifact | Đường dẫn tương đối | SHA-256 | Trạng thái |
|---|---|---|---|
| Preflight raw audit JSON | [preflight_audit.json](../../../../artifact-evidence/axd-g2-v2-preflight-20261124/preflight_audit.json) | `e99bd5e68c5851828ae55c9853d71aadb623f75ddc927d9f884003beeb091b5f` | `NEW (Stage 0 raw)` |
| Live quiet observation JSONL | [live_quiet_observation.jsonl](../../../../artifact-evidence/axd-g2-v2-preflight-20261124/live_quiet_observation.jsonl) | `4ea27c7ae176f46acdfc2355a859a284ad508ad27abf83c34b16c88c56a2eb3b` | `NEW (Stage 0 raw)` |
| Preflight bundle checksums | [BUNDLE.sha256](../../../../artifact-evidence/axd-g2-v2-preflight-20261124/BUNDLE.sha256) | `cc079410f73f8660bb2a0a913834536eee48c508d3220c49c0e2f33c03a6c40e` | `NEW (2/2 verified)` |
| Design-2 freeze manifest | [axd_g2_v2_freeze.json](../../../configs/axd_g2_v2_freeze.json) | `91186d57e5992e1df70f86a55ba928ad4d6613bb0b67ccbee0f485cc380d1749` | `UNCHANGED (22/22 OK)` |
| Design-2 remediation checksums | [AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256](AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256) | *(24/24 entries OK)* | `UNCHANGED` |
| Historical v1 prereg (`QUALITY_HOLD`) | [AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md](AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md) | `cb6433cb2c04108653cca7e8d63ed9688f3b19fa68a0b236acccc28d766393eb` | `UNCHANGED` |
| Stage 5 validation bundle | [BUNDLE.sha256](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/BUNDLE.sha256) | `82e740bcd6224bd28dfa2dcdbedba4902515b0fc578ed923250ef5d568337e15` | `UNCHANGED` |
| Stage 6 test quality bundle | [BUNDLE.sha256](../../../../artifact-evidence/axd-g2-stage6-test-quality-20261123/BUNDLE.sha256) | `cd65a8acf17b59f0b566750994f1ef7aa6a81c3a0ac89081add5af256927841f` | `UNCHANGED` |
| Reserved Quality output dir | `../artifact-evidence/axd-g2-v2-quality-design2/` | *(chưa tạo — bảo toàn cho lần chạy hợp lệ)* | `NOT_CREATED` |
| Reserved `v2_test_10000.ids` | `../artifact-evidence/axd-g2-v2-inputs-design2/v2_test_10000.ids` | *(chưa materialize trước approval)* | `NOT_CREATED` |
