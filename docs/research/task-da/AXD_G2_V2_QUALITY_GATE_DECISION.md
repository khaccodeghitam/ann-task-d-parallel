# A×D G2 v2 · Quality Gate Decision (`design-2`)

- **Official Quality Gate Verdict:** **`BLOCKED_EXECUTION_OR_PROVENANCE`** *(Stage 0 sub-status: **`BLOCKED_PREFLIGHT`** — đã khắc phục xong **B3 = `PASS`**, còn **B1 = `HOLD`** và **B2 = `WAITING_OWNER`**; **B4 = `NOT_EXECUTED`**).*
- **Protocol & Scope:** `AXD-G2-V2-3A-20261123` · revision `design-2` · `p=2`, `S=16`, `common beam = 432` · **`EXPLORATORY_HOST_SPECIFIC`**.
- **Execution Accounting:** **`Quality ON = 0 / 18`** · **`G2 OFF = 0 / 144` (`NOT_OPEN`)** · **`Profiler = 0`** · **`v2_test_10000.ids materialized = false`**.
- **Supporting Reports & Raw Bundles:**
  - Preflight Recovery (B3 & B1): [AXD_G2_V2_PREFLIGHT_RECOVERY_REPORT.md](AXD_G2_V2_PREFLIGHT_RECOVERY_REPORT.md) · [Recovery BUNDLE.sha256](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/BUNDLE.sha256) (`02027ca0...`)
  - Owner Approval Guide (B2): [AXD_G2_V2_OWNER_APPROVAL_CHECKLIST.md](AXD_G2_V2_OWNER_APPROVAL_CHECKLIST.md)
  - Initial Stage 0 Preflight Results: [AXD_G2_V2_QUALITY_RESULTS.md](AXD_G2_V2_QUALITY_RESULTS.md) · [Initial Preflight BUNDLE.sha256](../../../../artifact-evidence/axd-g2-v2-preflight-20261124/BUNDLE.sha256) (`cc079410...`)

---

## 1. Bảng Tổng hợp Trạng thái Stage 0 Blockers (Cập nhật sau Preflight Recovery)

| Blocker | Hạng mục | Trạng thái cập nhật | Bằng chứng xác minh |
|---|---|---|---|
| **B3** | Môi trường Python bền vững đúng `requirements-g2-v2.lock` | **`PASS` (RESOLVED)** | Đã tạo venv bền vững ngoài `/tmp`, không khoảng trắng tại `/home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python`; `resolved = /usr/bin/python3.12` (`e50d468e...`); cài đủ `7/7` gói với `--require-hashes` khớp từng wheel SHA; `load_freeze(environment=True) = PASS`; dataset-free suite **`551 tests: 537 executed PASS, 14 native opt-in skipped, 0 failures, 0 errors`**; không sửa `freeze.json`, `.venv` hay system Python. |
| **B1** | Host CPU quiet (`foreign_busy_s / (wall_s × 2) <= 0.01` over `>= 5 s`) | **`HOLD` (ACTIVE BLOCKER)** | Quan sát đọc-chỉ `15 s` mới bằng `g2_v2_guard.CoolingGuard`: ngay cả khi `msedge` gần rỗi (`0.12%`), tải nền tổng vẫn ở **`10.97%` trung bình (`8.59% – 15.37%` rolling)** do `gnome-shell` (`4.48%`), `agy` (`3.11%`), `gnome-terminal-` (`2.71%`) và `ChatGPT` (`1.04%`). Phần dư thuần OS/kernel/IRQ quan sát được ở **`~0.91%`** (sát trần `1.00%`). Chưa kiểm trên minimal TTY nên chưa gán `B1_HOLD_NOISE_THRESHOLD_INFEASIBLE`; không kill process ngoài phạm vi, không nới ngưỡng `0.01`, không gán `quiet_host_confirmed = true`. |
| **B2** | Approval Receipt bên ngoài do owner ký hợp lệ (`axd_g2_v2.2`) | **`WAITING_OWNER` (ACTIVE BLOCKER)** | Chỉ có template `configs/axd_g2_v2_approval.UNAPPROVED.json` (`0f76abc6...`, giữ nguyên không sửa). Đã chuẩn bị đầy đủ đặc tả trường, mẫu JSON và lệnh dry-run xác minh tại [AXD_G2_V2_OWNER_APPROVAL_CHECKLIST.md](AXD_G2_V2_OWNER_APPROVAL_CHECKLIST.md) chờ owner tự ký sau khi B1 PASS trên minimal TTY. |
| **B4** | Materialize `v2_test_10000.ids` (`457abdc1...`) | **`NOT_EXECUTED` (POST-APPROVAL)** | Chưa tạo tệp đúng kỷ luật chỉ materialize sau khi B1, B2, B3 cùng PASS. |

*(Toàn bộ các tài sản đóng băng khác — `24/24` checksum remediation, `22/22` components, `6/6` graph R90 v1.3, `6/6` Stage 5 b432 baselines, Release ELF `7a2685e5...`, compiler `/usr/bin/c++`, `5/5` thư viện native `.so`, `base/queries/gt/val/warmup`, `host_contract()` Ryzen `cpus=[0,2]`, `Tctl = 44.5–57.25°C`, `AC=1`, `MemAvailable = 10.03 GiB`, `free_disk = 137.87 GiB`, `swap = 0 B` — đều giữ **`PASS 100%`**.)*

---

## 2. Lý do Giữ Kết luận `BLOCKED_EXECUTION_OR_PROVENANCE` (`BLOCKED_PREFLIGHT`)

1. Dù **B3 đã hoàn toàn được khắc phục (`PASS`)** mà không cần bất kỳ thay đổi nào tới `configs/axd_g2_v2_freeze.json`, hai cổng bắt buộc **B1 (quiet host thực tế `<= 1%`)** và **B2 (signed owner approval receipt bên ngoài)** vẫn chưa thỏa mãn.
2. Không có tiến trình ANN quality nào được chạy (`Quality ON = 0/18`, `G2 OFF = 0/144`), do đó chưa có dữ liệu để đánh giá `QUALITY_GATE_PASS` hay `QUALITY_HOLD`; phân loại Stage 3 chính xác duy nhất là **`BLOCKED_EXECUTION_OR_PROVENANCE`** (`BLOCKED_PREFLIGHT`).

---

## 3. Hành động Kế tiếp dành cho Owner (Không Tự Chuyển Stage)

Thực hiện đúng trình tự trong [AXD_G2_V2_OWNER_APPROVAL_CHECKLIST.md](AXD_G2_V2_OWNER_APPROVAL_CHECKLIST.md):
1. **Owner đóng ứng dụng desktop/GUI (`msedge`, `ChatGPT`, `agy`) và kiểm tra 30 s trên minimal Linux TTY (`Ctrl+Alt+F3` hoặc SSH)** bằng lệnh đọc-chỉ đã cung cấp:
   - Nếu `B1_QUIET_PASS=True` -> chuyển sang bước 2.
   - Nếu vẫn thất bại trên minimal TTY sạch -> dừng ở `B1_HOLD_NOISE_THRESHOLD_INFEASIBLE` và xem xét đề xuất controlled revision `design-3` có cơ sở định lượng tại [AXD_G2_V2_PREFLIGHT_RECOVERY_REPORT.md](AXD_G2_V2_PREFLIGHT_RECOVERY_REPORT.md) §2.3 (không tự nới ngưỡng trong `design-2`).
2. **Owner tự điền và lưu tệp Approval Receipt `QUALITY_ONLY` bên ngoài frozen package** (kèm `owner`, `approved_at` có múi giờ, `quiet_host_confirmed: true`, `quota_s: 3600`, không sửa `UNAPPROVED` template) và xác minh bằng lệnh dry-run `g2_v2_contract.authorize()`.
3. **Chỉ sau khi B1, B2 và B3 cùng PASS:** materialize một lần `v2_test_10000.ids` (kiểm SHA `457abdc1...` và overlap = 0) rồi khởi chạy đúng `18` tiến trình ON `QUALITY_ONLY` bằng `/home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python -m research.task_da.g2_v2_runner execute --phase quality ...`. Pha `144 OFF` vẫn **`NOT_OPEN`** và đòi hỏi phê duyệt riêng sau báo cáo quality.

---

## 4. Sổ Bảo toàn Cổng & Hạn chế (Preserved Gate Ledger)

- `B3 (Durable Python Environment)`: **`PASS`** (`/home/thinhbui/.local/share/axd-g2-v2-design2/venv`).
- `B1 (Host CPU Quiet <= 1%)`: **`HOLD`** (chờ owner kiểm chứng trên minimal TTY).
- `B2 (Owner Approval Receipt)`: **`WAITING_OWNER`** (`UNAPPROVED` template nguyên vẹn).
- `B4 (v2_test_10000.ids Materialization)`: **`NOT_EXECUTED`**.
- `G2 v2 Quality-Only Phase`: **`0 / 18`** (`BLOCKED_EXECUTION_OR_PROVENANCE` / `BLOCKED_PREFLIGHT`).
- `G2 v2 OFF Performance Phase`: **`0 / 144`** (`NOT_OPEN / NOT_AUTHORIZED`).
- `Historical G2 v1`: **`QUALITY_HOLD`** (bất biến, SHA `cb6433cb...`).
- `Design-2 Freeze Package`: **`24/24` SHA-256 remediation OK**, `22/22` components OK, `freeze.json` SHA `91186d57...` không đổi.
- `Profiler`: **`0`** · `New Graphs`: **`0`** · `10M`: **`NOT_RUN`** · `i5-14600KF`: **`NOT_RUN`** · `H3/TP-CG`: **`NOT_OPENED`** · `Task A Google Sheets`: **`UNMODIFIED`** · `Git Commit`: **`NONE`**.
