# A×D G2 v2 · Stage 0 Preflight Recovery Report (B3 & B1)

- **Recovery Scope:** Khắc phục **B3** (môi trường Python bền vững) và điều tra định lượng **B1** (CPU quiet host) từ trạng thái `BLOCKED_PREFLIGHT` của package `AXD-G2-V2-3A-20261123` (`design-2`, `p=2`, `S=16`, `beam=432`, `EXPLORATORY_HOST_SPECIFIC`).
- **Tóm tắt Trạng thái sau Recovery:**
  - **B3 (Durable Python Environment):** **`PASS`** *(không sửa `freeze.json`, không sửa system Python, không sửa `.venv` cũ).*
  - **B1 (Host CPU Quiet `<= 1%` p2 capacity):** **`HOLD`** *(phiên desktop hiện tại vẫn ở `8.59% – 15.37%` ngay cả khi `msedge` gần như rỗi; cần owner kiểm chứng trực tiếp trên minimal TTY; dự phòng đề xuất revision có kiểm soát nếu minimal TTY vẫn trượt).*
  - **B2 (Signed Owner Approval Artifact):** **`WAITING_OWNER`** *(chưa có chữ ký/receipt bên ngoài; xem [AXD_G2_V2_OWNER_APPROVAL_CHECKLIST.md](AXD_G2_V2_OWNER_APPROVAL_CHECKLIST.md)).*
  - **B4 (`v2_test_10000.ids` Materialization):** **`NOT_EXECUTED`** *(chưa tạo tệp test IDs trước khi B1–B3 hoàn tất).*
  - **Execution Counts:** **`Quality ON = 0 / 18`** · **`G2 OFF = 0 / 144` (`NOT_OPEN`)** · **`Profiler = 0`**.
- **Durable Recovery Evidence Bundle:** [axd-g2-v2-preflight-recovery-20261124](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/) · [BUNDLE.sha256](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/BUNDLE.sha256) (`02027ca01ddea3cc783c7d1cb7cf57e49cbe3e9e24b3d6104223d315c8bbd34b`).
- **Related Documents:** [AXD_G2_V2_QUALITY_RESULTS.md](AXD_G2_V2_QUALITY_RESULTS.md) · [AXD_G2_V2_QUALITY_GATE_DECISION.md](AXD_G2_V2_QUALITY_GATE_DECISION.md) · [AXD_G2_V2_OWNER_APPROVAL_CHECKLIST.md](AXD_G2_V2_OWNER_APPROVAL_CHECKLIST.md) · [AXD_G2_V2_PRE_APPROVAL_REMEDIATION.md](AXD_G2_V2_PRE_APPROVAL_REMEDIATION.md).

---

## 1. Stage 1 — Khôi phục Môi trường Python Bền vững (B3: **`PASS`**)

### 1.1 Kiểm kê Môi trường Trước và Sau Recovery
- **Python hệ thống (`/usr/bin/python3.12`):** Phiên bản `3.12.3`, SHA-256 `e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f` (khớp 100% `configs/axd_g2_v2_freeze.json`); không có `ensurepip`/`pip` hệ thống, không được sửa đổi.
- **`.venv` sẵn có của repo:** Không sửa đổi (vẫn rỗng `[]` phân phối cài đặt).
- **`.venv-research` sẵn có của repo:** Không sửa đổi; chỉ dùng `pip 26.3` của nó với cờ `--python <target_venv>/bin/python --isolated --only-binary=:all: --require-hashes --no-deps` để cấp phát wheel sạch cho venv mục tiêu mới.
- **Lưu ý kỹ thuật về đường dẫn chứa khoảng trắng (bảo toàn đầy đủ log thử đầu):**
  - Thử nghiệm ban đầu đặt venv tại `.local/venvs/axd-g2-v2-design2` (nằm dưới thư mục `Research ANN` chứa khoảng trắng) cài đủ 7 gói và đạt `load_freeze(environment=True) = PASS`, nhưng bộ `unittest` gặp đúng `1/551` lỗi lặp lại ở `test_sigterm_stops_benchmark_and_collectors` ([verification_suite.log](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/verification_suite.log), [verification_suite_rerun2.log](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/verification_suite_rerun2.log)) vì test này ghi shebang `#!{sys.executable}` và kernel Linux tách shebang tại dấu cách trong `Research ANN`.
  - Di dời venv bền vững sang đường dẫn **ngoài `/tmp`, bền vững qua reboot, không chứa khoảng trắng, và nằm ngoài Git tracking**:
    **`/home/thinhbui/.local/share/axd-g2-v2-design2/venv`** (dọn bỏ thư mục tạm `.local/venvs/axd-g2-v2-design2`).

### 1.2 Xác minh Đầy đủ 7 Gói Khóa, Wheel SHA-256, `load_freeze(environment=True)` & Test Suite

Nguồn xác minh: [env_verification.json](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/env_verification.json) · [pip_install_report_durable.json](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/pip_install_report_durable.json) · [verification_suite_durable.log](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/verification_suite_durable.log).

- **Executable & Freeze Identity:**
  - `sys.executable`: `/home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python`
  - `Path(sys.executable).resolve()`: `/usr/bin/python3.12` -> SHA-256 `e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f` (**KHỚP 100%** `freeze.json`).
  - `sys.prefix`: `/home/thinhbui/.local/share/axd-g2-v2-design2/venv` · `sys.base_prefix`: `/usr` · `pip check`: **`No broken requirements found.`**
  - `configs/axd_g2_v2_freeze.json` SHA-256: `91186d57e5992e1df70f86a55ba928ad4d6613bb0b67ccbee0f485cc380d1749` (**KHÔNG THAY ĐỔI**).
  - `load_freeze(environment=True)`: **`PASS`** (kiểm đồng thời 22 component files + Python version + executable SHA + 7 exact packages).

| Gói trong `requirements-g2-v2.lock` | Phiên bản cài đặt | Wheel SHA-256 (khớp `--require-hashes`) | Trạng thái |
|---|---:|---|---|
| `attrs` | `26.1.0` | `c647aa4a12dfbad9333ca4e71fe62ddc36f4e63b2d260a37a8b83d2f043ac309` | **`PASS`** |
| `jsonschema` | `4.26.0` | `d489f15263b8d200f8387e64b4c3a75f06629559fb73deb8fdfb525f2dab50ce` | **`PASS`** |
| `jsonschema-specifications` | `2025.9.1` | `98802fee3a11ee76ecaca44429fda8a41bff98b00a0f2838151b113f210cc6fe` | **`PASS`** |
| `numpy` | `2.5.5` | `704d819265e5d1064d932968e9ee85fff2103ccc78c05b878c06943ba27b8507` | **`PASS`** |
| `referencing` | `0.37.0` | `381329a9f99628c9069361716891d34ad94af76e461dcb0335825aecc7692231` | **`PASS`** |
| `rpds-py` | `2026.9.1` | `addeda51556dac7c1a2f14cda62db8b621cd12afba3091d03a96c72932387eab` | **`PASS`** |
| `typing_extensions` | `4.16.0` | `481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8` | **`PASS`** |

- **Tổng phân phối trong venv:** Đúng `7` gói trên (không dư gói nào).
- **Dataset-free test suite:**
  ```sh
  env -u TASK_DA_SMOKE -u TASK_DA_P1_EVAL -u TASK_DA_P2_EVAL \
      -u TASK_DA_PHASE_EVAL -u TASK_DA_P2_TRACE_EVAL \
      /home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python \
      -m unittest discover -s tests/research -v
  ```
  Kết quả: **`Ran 551 tests in 19.200s — OK (skipped=14)`** (`537 executed PASS`, `14 native opt-in skipped`, `0 failures`, `0 errors`; gồm `30/30 PASS` trong `tests/research/test_g2_v2.py`).
- **Kết luận B3:** **`PASS`** — Không có mismatch nào, không cần revision cho `freeze.json`.

---

## 2. Stage 2 — Điều tra Host CPU Quiet (B1: **`HOLD`**)

### 2.1 Xác nhận Công thức Guard & Topology Phần cứng
Đối chiếu trực tiếp mã nguồn [g2_v2_guard.py](../../../research/task_da/g2_v2_guard.py) (dòng 12–16, 25–87, 113–128):
- **Công thức:** `foreign_busy_s = max(0, host_busy_s - owned_cpu_s - monitor_cpu_s)` với `host_busy_ticks = user + nice + system + irq + softirq + steal` từ `/proc/stat` (bỏ `idle` và `iowait`, không cộng trùng `guest`), quy đổi qua `CLK_TCK = 100`.
- **Giới hạn đóng băng:** Trên mọi cửa sổ cuộn `wall_s >= 5.0 s` (`cadence 1 Hz`, `0.5 s <= dt <= 2.0 s`):
  $$\frac{\text{foreign\_busy\_s}}{\text{wall\_s} \times 2} \le 0.01 \iff \text{foreign\_busy\_s} / \text{wall\_s} \le 0.02\text{ CPU-s/s}$$
  *(tức tổng tải của **mọi** tiến trình khác ngoài `owned_pid` và `monitor_pid` trên **cả 12 luồng logic** cộng lại không được vượt `2%` của một luồng CPU đơn).*
- **Topology & affinity `[0, 2]` (`host_contract()` = `PASS`):** `AMD Ryzen 5 PRO 4650U`, `cpus=[0, 2]` ánh xạ sang 2 physical core độc lập (`core_id = 0` siblings `0-1`, `core_id = 1` siblings `2-3`), chung L3 `0-5`, `allowed_cpus = [0..11]`, `kernel = 7.0.0-43-generic`, `CLK_TCK = 100`. `Tctl = 44.5–57.25°C` (`<< 85°C`), `AC/online = 1`, `MemAvailable = 10.03 GiB`, `free_disk = 137.87 GiB`, `swap_used = 0 B`, không có named CPU/ANN job (`stress-ng`, `sysbench`, `task_da_p2_eval`, ...).

### 2.2 Quan sát Read-Only Mới (15 giây) & Phân rã Tải Nền theo Tiến trình

Nguồn raw: [b1_quiet_investigation.json](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/b1_quiet_investigation.json) và [live_quiet_observation_stage2.jsonl](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/live_quiet_observation_stage2.jsonl) (`15` bước 1 Hz, tổng `wall_s = 16.4058 s`, không kill bất kỳ tiến trình nào).

- **Đối chiếu 2 lần đo thực tế:**
  - Lần 1 (`00:04`, `7s`, `msedge` đang chạy nặng): rolling fraction = **`0.5030 – 0.5441` (`50.3% – 54.4%`)** (`FAIL`).
  - Lần 2 (`00:20`, `15s`, `msedge` đã gần như rỗi ở `0.12%`): `mean = 0.10972` (**`10.97%`**), rolling `>= 5s` range = **`0.08589 – 0.15372` (`8.59% – 15.37%`)** (`0/11` cửa sổ cuộn đạt `<= 1.0%` -> **`FAIL`**).

| Nhóm / Tiến trình (`comm`) | Tổng CPU trong `16.4058 s` | Tỷ lệ trên công suất p2 (`/(wall×2)`) | So với ngưỡng `1.00%` |
|---|---:|---:|---|
| `gnome-shell` (desktop compositor) | `1.470 s` | **`4.48%`** | Vượt `4.5×` một mình |
| `agy` (phiên CLI agent tương tác) | `1.020 s` | **`3.11%`** | Vượt `3.1×` một mình |
| `gnome-terminal-` (cửa sổ terminal GUI) | `0.890 s` | **`2.71%`** | Vượt `2.7×` một mình |
| `ChatGPT` + `codex` (Electron app) | `0.340 s` | **`1.04%`** | Vượt `1.0×` một mình |
| `iostat` (tiến trình giám sát ngắn) | `0.110 s` | `0.34%` | — |
| `msedge` (lúc gần rỗi) | `0.040 s` | `0.12%` | *(tăng lên >50% khi có tab hoạt động)* |
| `Xwayland` | `0.010 s` | `0.03%` | — |
| **Phần dư thuần OS/Kernel/IRQ** (`irq/*-iwlwifi` `0.090 s`, `kworker/*` `0.140 s`, `irq/9-acpi` `0.020 s`, `rcu_preempt` `0.020 s`, `systemd-oomd`/`upowerd`/`tracker-miner-f` `0.030 s`) | **`0.300 s`** | **`0.91%`** *(nếu gồm cả `iostat`: `1.25%`)* | **Sát ranh giới `1.00%`** |
| **Tổng đo thực tế từ `/proc/stat` (đã trừ monitor `0.93 s`)** | **`3.600 s`** | **`10.97%`** *(rolling `8.59%–15.37%`)* | **`FAIL (HOLD)`** |

### 2.3 Đánh giá Khả thi trên Minimal TTY & Dự phòng Revision (Không Tự Nới Ngưỡng)

1. **Trong phiên desktop GUI + `agy` hiện tại:** **Chắc chắn KHÔNG thể đạt `<= 1.0%`** vì riêng `gnome-shell` (`4.48%`), `agy` (`3.11%`), `gnome-terminal-` (`2.71%`) và `ChatGPT` (`1.04%`) từng thành phần đều vượt trần `1.00%`.
2. **Trong phiên minimal Linux TTY (`Ctrl+Alt+F3` hoặc SSH sau khi đóng trình duyệt/Electron/agent):**
   - Loại bỏ các ứng dụng tương tác và desktop GUI cắt bỏ ~`11.5%`, đưa nền hệ thống về **~`0.6% – 0.91%`** (phần `kworker/gfx`/`dm_vblank` và `iwlwifi` có thể giảm thêm khi chuyển sang text TTY không vẽ đồ họa và không truyền mạng).
   - **Vì vậy `<= 0.01` CHƯA bị bác bỏ tuyệt đối**, nhưng **biên an toàn thực tế rất mỏng** (`< 0.1%–0.4%` trước các xung ngắn của `kworker`, `iwlwifi`, `systemd-oomd`, `tracker-miner-f` trong suốt 18 lượt ON hoặc 144 lượt OFF).
   - **Chưa gán `B1_HOLD_NOISE_THRESHOLD_INFEASIBLE` lúc này** vì chưa có phép đo thực tế của owner trên minimal TTY; trạng thái hiện tại là **`B1 = HOLD` (`HOLD_DESKTOP_CONTENTION_MINIMAL_TTY_UNVERIFIED`)**.
3. **Hướng dẫn owner kiểm tra an toàn trên minimal TTY (không tự kill process):**
   - Lưu công việc và tự đóng an toàn `msedge`, `ChatGPT`/Codex, các ứng dụng media/chat/IDE, và thoát phiên `agy` tương tác.
   - Chuyển sang Linux text console **`Ctrl+Alt+F3`** (hoặc đăng nhập SSH từ máy khác sau khi khóa/tắt màn hình desktop), không mở trình duyệt/GUI.
   - Chạy đúng lệnh đọc-chỉ 30 giây trong [AXD_G2_V2_OWNER_APPROVAL_CHECKLIST.md](AXD_G2_V2_OWNER_APPROVAL_CHECKLIST.md) Mục 2 để xác minh `all rolling <= 0.01` trong `>= 30 s` liên tiếp.
4. **Đề xuất dự phòng (chỉ kích hoạt thành `B1_HOLD_NOISE_THRESHOLD_INFEASIBLE` nếu owner chạy kiểm tra 30 s trên minimal TTY mà vẫn vượt `0.01`):**
   - Không tự sửa `g2_v2_guard.py` trong `design-2`. Nếu minimal TTY sạch vẫn dao động `0.8%–2.0%` do nền kernel/IRQ của 12 luồng Ubuntu Desktop, owner có thể xem xét một **controlled protocol revision riêng (`design-3`)** khóa **trước** mọi lượt chạy:
     - Giữ nguyên chặn cứng tức thời mọi named CPU/ANN job (`KNOWN_CPU_JOBS`) và mọi single foreign process kéo dài `> 0.05` CPU-s/s trên cửa sổ `>= 5 s`;
     - Calibrate ngưỡng tổng tải nền toàn máy 12 luồng theo mức nền thực đo của minimal TTY (ví dụ `<= 0.025` hoặc `0.03` trên 12 luồng tương đương `0.05–0.06` CPU-s/s, tức `< 0.5%` tổng công suất 12 luồng), tách báo cáo diagnostic per-core / per-process đầy đủ trong mọi JSONL.
   - Mọi revision như vậy sẽ đòi hỏi cập nhật `freeze.json` và bộ test + phê duyệt mới của owner trước khi chạy.

---

## 3. Chỉ mục Raw Evidence & Bảo toàn Đóng băng

| Tệp / Hạng mục | Đường dẫn tương đối | SHA-256 | Trạng thái |
|---|---|---|---|
| Recovery BUNDLE manifest | [BUNDLE.sha256](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/BUNDLE.sha256) | `02027ca01ddea3cc783c7d1cb7cf57e49cbe3e9e24b3d6104223d315c8bbd34b` | `NEW (8/8 verified)` |
| B3 env verification JSON | [env_verification.json](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/env_verification.json) | *(trong BUNDLE.sha256)* | `B3 = PASS` |
| B3 pip install report | [pip_install_report_durable.json](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/pip_install_report_durable.json) | *(trong BUNDLE.sha256)* | `7/7 wheel hashes OK` |
| B3 durable unittest log | [verification_suite_durable.log](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/verification_suite_durable.log) | *(trong BUNDLE.sha256)* | `551 tests: 537 PASS, 14 skip, 0 FAIL` |
| B1 15s quiet investigation JSON | [b1_quiet_investigation.json](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/b1_quiet_investigation.json) | *(trong BUNDLE.sha256)* | `B1 = HOLD (8.59%–15.37%)` |
| B1 15s raw JSONL telemetry | [live_quiet_observation_stage2.jsonl](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/live_quiet_observation_stage2.jsonl) | *(trong BUNDLE.sha256)* | `16 snapshots` |
| Design-2 remediation SHA | [AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256](AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256) | *(24/24 OK)* | `UNCHANGED` |
| `UNAPPROVED` template | [axd_g2_v2_approval.UNAPPROVED.json](../../../configs/axd_g2_v2_approval.UNAPPROVED.json) | `0f76abc61992312e7e3fb5d447b0d0b4a3210c62958bb62065581efa37bb69ab` | `UNCHANGED` |
| Historical v1 prereg | [AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md](AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md) | `cb6433cb2c04108653cca7e8d63ed9688f3b19fa68a0b236acccc28d766393eb` | `UNCHANGED` |
| `.venv` cũ & system Python | `.venv/`, `/usr/bin/python3.12` | `e50d468e...` | `UNCHANGED` |
