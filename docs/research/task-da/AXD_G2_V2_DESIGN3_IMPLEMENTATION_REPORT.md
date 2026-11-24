# A×D G2 v2 · Controlled Amendment `design-3` Implementation Report

- **Official Stage 5 Verdict:** **`DESIGN3_READY_FOR_QUALIFICATION`** *(Stage 1–3 triển khai, kiểm thử, kiểm toán và đóng băng độc lập đã **PASS 100%**; Stage 4 `900s` qualification được bàn giao bằng một lệnh ngắn để owner chạy trực tiếp trên minimal Linux TTY sau khi đăng xuất Ubuntu Desktop — không chạy `900s` qualification trong phiên desktop đang tải `25.99%`).*
- **Protocol & Frozen Identity:** `AXD-G2-V2-3A-20261123` · revision **`design-3`** · schema **`axd_g2_v2.3`** · **`EXPLORATORY_HOST_SPECIFIC`** · `p=2`, `S=16`, `common beam = 432`.
- **Canonical Freeze Manifest:** [AXD_G2_V2_DESIGN3_FREEZE_MANIFEST.json](AXD_G2_V2_DESIGN3_FREEZE_MANIFEST.json) · SHA-256: **`425c748329292ffe15db2c52bdf53f5d219b47d1ecf95ac3c76a5429814159ae`** · Checksums: [AXD_G2_V2_DESIGN3_FREEZE.sha256](AXD_G2_V2_DESIGN3_FREEZE.sha256) (`26/26 OK`).
- **Execution Accounting:** `Quality ON = 0 / 18` · `G2 OFF = 0 / 144` (`NOT_OPEN`) · `Profiler = 0` · `v2_test_10000.ids materialized = false` · `design-2` (`24/24` files) & historical v1 (`cb6433cb...`) **UNCHANGED**.
- **Related Documents:** [AXD_G2_PREREG_V2_DESIGN3_AMENDMENT.md](AXD_G2_PREREG_V2_DESIGN3_AMENDMENT.md) · [AXD_G2_V2_DESIGN3_PREQUALIFICATION_AUDIT.md](AXD_G2_V2_DESIGN3_PREQUALIFICATION_AUDIT.md) · [AXD_G2_V2_B1_QUIET_FEASIBILITY_REVIEW.md](AXD_G2_V2_B1_QUIET_FEASIBILITY_REVIEW.md).

---

## 1. Kiến trúc Triển khai Độc lập `design-3` (6 Sửa đổi Có Kiểm soát)

Toàn bộ mã và cấu hình `design-3` được triển khai thành các tệp mới tách biệt hoàn toàn với `design-2` (không ghi đè một byte nào của `design-2` hay base guard `tools/research/run_paper_fullfan_check.py`):

| # | Hạng mục sửa đổi | Triển khai thực tế trong `design-3` | Kết quả kiểm chứng định lượng |
|---:|---|---|---|
| **1** | **Loại bỏ quét trùng `/proc`** | [g2_v2_design3_guard.py](../../../research/task_da/g2_v2_design3_guard.py) (`host_snapshot_v3`): dùng `os.scandir('/proc')` + `os.open`/`os.read` quét `/proc/[0-9]*/stat` đúng **1 lần/giây**, cache đường dẫn sysfs tĩnh (`hwmon`/`power`/`cpufreq`), xuất `processes` gọn không mất thông tin (bỏ qua PID `ticks == 0`). | Đo sống `10 s` trên Ryzen 4650U: monitor CPU giảm từ **`5.67%–6.84%`** của 1 core (`2.83%–3.42%` p2 ở `design-2`) xuống **`1.62%` của 1 core (`0.81%` công suất p2 — giảm `3.5×–4.2×`)**, `avg_obs_cpu = 18.11 ms`, JSONL gọn còn `~13.7 KB/s`. |
| **2** | **Hạch toán tường minh `watchdog_pid` & `monitor`** | `run_guarded_v3()` tái sử dụng nguyên bản `watchdog` / `terminate_group` / `CoolingGuard` từ frozen `run_paper_fullfan_check.py`, lưu `watchdog_pid` & `watchdog_start_ticks` vào `manifest.json` và truyền vào `host_snapshot_v3(..., watchdog_pid=wd)` để trừ chính xác cả `owned + monitor + watchdog`. | `test_watchdog_and_monitor_excluded_zero_false_abort` & `test_process_result_fixture_checks_watchdog_topology_and_ram` **PASS** (bắt lỗi mismatch `watchdog_pid` và `start_ticks`). |
| **3** | **Trừ ròng theo cửa sổ (thay per-1s `max(0, ·)`)** | `window_accounting(start_cap, end_cap)` tính duy nhất một phép trừ ròng giữa hai đầu cửa sổ `W`: `max(0, Δbusy(W) - Δowned(W) - Δmonitor(W) - Δwatchdog(W))`, đồng thời kiểm bảo toàn Linux `fs/proc/stat.c` (`0 <= agg - sum(cpu0..11) <= 6 × 12`, phát hiện và xử lý chính xác floor-truncation `nsec_to_clock_t` của kernel 7.0). | `test_net_window_subtraction_eliminates_quantization_rectification_false_abort` (`±2` tick phase jitter mỗi giây trong `20 s`, true foreign = `0`) cho **`0` false abort**, `foreign_all_fraction <= 0.001`. |
| **4** | **Guard phân tầng theo Topology CCX (`cpu0..cpu11`)** | `ContentionV3` đọc per-CPU `/proc/stat` + `processor` (trường #39 của `/proc/<pid>/stat`), tính ước lượng bảo toàn `min(ΔF_all, max(max(0, ΔB(S) - E), ΔF_procs(S)))` đảm bảo `0 <= f_workers <= f_ccx0 <= f_all`. **Pha `OFF` / `qualification`:** `[0..3] <= 0.01` (`10s`), `CCX0 [0..5] <= 0.02` (`10s`), `all [0..11] <= 0.025` (`15s`), single foreign process `<= 0.10` (`10s`), instant reject `KNOWN_CPU_JOBS`. | `host_contract()` xác minh sống `CCX0 = 0-5`, `CCX1 = 6-11`; unit tests chứng minh xung OS `300 ms` ở `CPU 9` (`CCX1`) **PASS**, trong khi tải trên `CPU 1` (SMT sibling), `CPU 4` (`CCX0` L3), hard-IRQ storm trên `CPU 0`, hoặc single process `12%` ở `CCX1` đều **FAIL** tức thời. |
| **5** | **Tách chính sách `QUALITY_ONLY` vs `OFF`** | `PHASE_POLICIES['quality']`: giữ nguyên toàn bộ safety/thermal (`85/95°C`), `AC`, `MemAvailable`, `disk`, `swap`, `KNOWN_CPU_JOBS` và ghi đầy đủ telemetry phân tầng; áp trần chống quá tải `all [0..11] <= 0.10` (`15s`) & single process `<= 0.25` (`10s`), preflight `>= 10s`. Pha `OFF` giữ đủ 3 tầng nghiêm ngặt, preflight `>= 15s`. | `test_quality_phase_allows_small_ccx1_os_load_but_blocks_overload_and_thermal` **PASS**. |
| **6** | **Paired foreign-load balance diagnostics & Cách ly Approval** | [g2_v2_design3_analyzer.py](../../../research/task_da/g2_v2_design3_analyzer.py) giữ nguyên 100% công thức `design-2` và bổ sung `noise_balance` (`paired Δforeign = opt - base` mean/CI95 qua 12 block + Spearman correlation + `imbalance_warning`). [g2_v2_design3_contract.py](../../../research/task_da/g2_v2_design3_contract.py) yêu cầu `schema = "axd_g2_v2.3"`, `revision = "design-3"`, `qualification_sha256` -> từ chối mọi approval `design-2`. | `test_estimands_are_mathematically_identical_to_design2` **PASS**; kiểm trực tiếp trên tệp approval `design-2` thật (`ad6f60cb...`) bị từ chối với `design-2 or mismatched revision approval rejected`. |

---

## 2. Danh mục Tệp Đóng băng Độc lập & Kế hoạch Lệnh (`design-3`)

- **Freeze Manifest:** [AXD_G2_V2_DESIGN3_FREEZE_MANIFEST.json](AXD_G2_V2_DESIGN3_FREEZE_MANIFEST.json) (`425c748329292ffe15db2c52bdf53f5d219b47d1ecf95ac3c76a5429814159ae`, khóa `25` component files).
- **Schema & Configs:**
  - [axd_g2_v2_design3.schema.json](../../../configs/axd_g2_v2_design3.schema.json) (`axd_g2_v2.3`, `11` definitions gồm `#/$defs/qualification`)
  - [axd_g2_v2_design3_approval.UNAPPROVED.json](../../../configs/axd_g2_v2_design3_approval.UNAPPROVED.json) *(mẫu cố ý invalid; từ chối bởi runner)*
  - [axd_g2_v2_design3_artifacts.proposed.json](../../../configs/axd_g2_v2_design3_artifacts.proposed.json) *(cùng 6 graph/binary/inputs bất biến; đường dẫn output riêng `axd-g2-v2-quality-design3` & `axd-g2-v2-off-design3`)*
  - [requirements-g2-v2-design3.lock](../../../requirements-g2-v2-design3.lock) *(khớp chính xác 7 wheel SHA-256)*
- **Executable Modules & Tests:**
  - [g2_v2_design3_contract.py](../../../research/task_da/g2_v2_design3_contract.py) · [g2_v2_design3_guard.py](../../../research/task_da/g2_v2_design3_guard.py) · [g2_v2_design3_analyzer.py](../../../research/task_da/g2_v2_design3_analyzer.py) · [g2_v2_design3_runner.py](../../../research/task_da/g2_v2_design3_runner.py) · [g2_v2_design3_qualify.py](../../../research/task_da/g2_v2_design3_qualify.py)
  - [run_g2_v2_design3_qualify.sh](../../../scripts/run_g2_v2_design3_qualify.sh) · [test_g2_v2_design3.py](../../../tests/research/test_g2_v2_design3.py) (`17/17 PASS`)
- **Final Command Plans & Freeze Evidence Bundle (Metadata Only — 0 ANN Inputs Opened):**
  - Thư mục chứng từ đóng băng: [.local/artifacts/axd-g2-v2-design3-freeze-20261124](../../../.local/artifacts/axd-g2-v2-design3-freeze-20261124/) · [BUNDLE.sha256](../../../.local/artifacts/axd-g2-v2-design3-freeze-20261124/BUNDLE.sha256) (`69c1951b...`)
  - [quality_plan_design3_final.json](../../../.local/artifacts/axd-g2-v2-design3-freeze-20261124/quality_plan_design3_final.json) (`18` ON commands, `beam=432`, `p=2`, `S=16`)
  - [off_plan_design3_final.json](../../../.local/artifacts/axd-g2-v2-design3-freeze-20261124/off_plan_design3_final.json) (`144` OFF commands, `12` balanced blocks, `6 AB / 6 BA` mỗi graph)
  - [verification_suite_design3.log](../../../.local/artifacts/axd-g2-v2-design3-freeze-20261124/verification_suite_design3.log) (`568 tests: 554 PASS, 14 skipped, 0 errors/failures`)

---

## 3. Stage 4 — Bàn giao Lệnh Ngắn Chạy Qualification `900 giây` trên Minimal TTY

**Lý do không chạy `900 s` qualification ngay trong phiên hiện tại:** Đo sống bằng `host_snapshot_v3` trong phiên Ubuntu Desktop hiện tại ghi nhận tải nền `all = 25.99%` (`msedge` chiếm `20.3%` của 1 core, `workers = 6.83%`, `ccx0 = 15.10%`), không đáp ứng điều kiện host tối giản của Stage 4. Theo chỉ thị Stage 4, dừng ở bước bàn giao **một lệnh ngắn duy nhất** cho owner tự chạy tại minimal TTY:

### Cách chạy (1 lệnh ngắn sau khi đăng xuất Ubuntu Desktop)
1. Lưu công việc, **đăng xuất khỏi Ubuntu Desktop** (Log Out), sau đó nhấn **`Ctrl+Alt+F3`** để vào Linux text TTY (đảm bảo cắm nguồn AC và không chạy tác vụ nền khác).
2. Đăng nhập vào TTY và chạy **đúng một lệnh**:
   ```sh
   "/home/thinhbui/Documents/ChatGPT/Research ANN/task-d/scripts/run_g2_v2_design3_qualify.sh"
   ```
3. Script sẽ tự động:
   - Chạy đúng **`900 giây` (`15 phút`)** ở chế độ **read-only** bằng đúng guard `design-3` đóng băng (không chạy ANN, không mở test panel, không đổi ngưỡng).
   - Lưu toàn bộ raw telemetry (`qualification_telemetry.jsonl`), báo cáo tổng hợp (`qualification_result.json`), và niêm phong **`BUNDLE.sha256`** vào một thư mục mới dưới `/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-design3-qualification-<UTC>/`.
   - In tóm tắt JSON (gồm `verdict: QUALIFICATION_PASS | QUALIFICATION_HOLD`, số cửa sổ `10s`/`15s` PASS/FAIL, `monitor_1core_pct`, `tctl_C`, `max_workers_10s`, `max_ccx0_10s`, `max_all_15s`, `max_single_10s`, nguyên nhân FAIL nếu có, và `qualification_result_sha256`).
4. **Quy tắc sau khi chạy:**
   - Nếu kết quả là **`QUALIFICATION_HOLD`** (exit code `2`): **giữ nguyên raw evidence và ghi `DESIGN3_HOLD`** — không tự đổi ngưỡng rồi chạy lại.
   - Nếu kết quả là **`QUALIFICATION_PASS`** (exit code `0`): báo lại đường dẫn thư mục qualification để lập checklist cho owner ký **approval receipt mới của `design-3`** (gắn đúng `freeze_sha256 = 425c7483...` và `qualification_sha256` vừa tạo).

---

## 4. Kết luận Stage 5

- **Official Status:** **`DESIGN3_READY_FOR_QUALIFICATION`** *(chưa lập checklist ký approval cho đến khi qualification `900 s` trên minimal TTY đạt `QUALIFICATION_PASS`).*
- **Preserved Restrictions:** `Quality ON = 0/18`, `G2 OFF = 0/144`, `Profiler = 0`, `v2_test_10000.ids` chưa materialize, `design-2` (`24/24` OK) & historical v1 nguyên vẹn, `Task A Google Sheets` không sửa, không tự commit, không tự ký approval.
