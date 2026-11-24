# A×D G2 v2 · B1 Quiet-Host Feasibility Review (`design-2` vs Proposed `design-3`)

- **Recommendation / Decision:** **`HOLD`** *(giữ **`HOLD`** đối với thực thi dưới `design-2` với chẩn đoán **`B1_HOLD_NOISE_THRESHOLD_INFEASIBLE`** cho chiến dịch zero-retry trên Ubuntu Ryzen 5 PRO 4650U; **đề xuất** chủ sở hữu xem xét phê duyệt một **controlled pre-data preregistration amendment `design-3`** chỉ sửa tầng guard/telemetry B1 trước mọi lượt chạy mới — **không** tự sửa `design-2`, **không** tự phê duyệt `design-3`).*
- **Current Verified State (Zero Execution):**
  - **B3 (Durable Python Environment):** **`PASS`** (`/home/thinhbui/.local/share/axd-g2-v2-design2/venv`, `load_freeze(environment=True) = PASS`, `551` tests / `537 PASS` / `14 skipped` / `0 FAIL`).
  - **B2 (Signed Owner Approval Receipt):** **`APPROVAL_CONTRACT_CHECK=PASS`** ([quality_only_approval.json](../../../../artifact-evidence/axd-g2-v2-approvals/quality_only_approval.json), SHA-256 `ad6f60cbae6f5d0d9e907d71dc94624b5a15fa29e338edf3e108b33d968f4751`, `scope=QUALITY_ONLY`, `owner=<thinhbui>`, `approved_at=2026-11-24T07:28:46+07:00`). *(Ghi chú minh bạch: `quiet_host_confirmed: true` được ký dựa trên lượt `26/26 PASS` trước đó, nhưng lượt kiểm chứng tiếp theo sau khi đăng xuất Ubuntu Desktop đã trượt `17 PASS / 9 FAIL`.)*
  - **B1 (Quiet Host `<= 1%` p2 capacity):** **`HOLD` (`UNSTABLE / INFEASIBLE_FOR_ZERO_RETRY_CAMPAIGN`)**.
  - **Execution Counts:** **`Quality ON = 0 / 18`** · **`G2 OFF = 0 / 144` (`NOT_OPEN`)** · **`v2_test_10000.ids materialized = false`** · **`Profiler = 0`** · **không dùng dữ liệu performance để đề xuất ngưỡng**.
- **Audited Source & Frozen Evidence:**
  - Guard & runner code: [g2_v2_guard.py](../../../research/task_da/g2_v2_guard.py) (`86ce14ed...`) · [run_paper_fullfan_check.py](../../../tools/research/run_paper_fullfan_check.py) (`232ed904...`) · [paper_portable_v2.py](../../../tools/research/paper_portable_v2.py) (`df8b7425...`) · [g2_v2_runner.py](../../../research/task_da/g2_v2_runner.py) (`d1de7a0c...`) · [g2_v2_contract.py](../../../research/task_da/g2_v2_contract.py) (`565f7c3c...`) · script TTY `/home/thinhbui/b1.py`.
  - Raw quiet-host observations: [preflight 00:04 (7s)](../../../../artifact-evidence/axd-g2-v2-preflight-20261124/live_quiet_observation.jsonl) (`4ea27c7a...`) · [recovery 00:20 (15s)](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/live_quiet_observation_stage2.jsonl) & [b1_quiet_investigation.json](../../../../artifact-evidence/axd-g2-v2-preflight-recovery-20261124/b1_quiet_investigation.json) · historical Stage 5 (`2,715` samples) & Stage 6 (`187` samples) `host.jsonl`.
  - Preregistration & remediation anchors: [AXD_G2_PREREG_V2.md](AXD_G2_PREREG_V2.md) · [AXD_G2_V2_STATISTICAL_DESIGN.md](AXD_G2_V2_STATISTICAL_DESIGN.md) · [AXD_G2_V2_PRE_APPROVAL_REMEDIATION.md](AXD_G2_V2_PRE_APPROVAL_REMEDIATION.md) (`24/24` checksums `OK`, không sửa đổi).

---

## 1. Kiểm toán Mã nguồn `g2_v2_guard.py` & Toàn bộ Raw Observations Hiện có

### 1.1 Cơ chế Thực thi Chính xác của `design-2` Guard
Từ mã nguồn [g2_v2_guard.py](../../../research/task_da/g2_v2_guard.py), [run_paper_fullfan_check.py](../../../tools/research/run_paper_fullfan_check.py) và [paper_portable_v2.py](../../../tools/research/paper_portable_v2.py):

1. **Quét kép ở mỗi chu kỳ `1 Hz` (`snapshot()` dòng 138–141):**
   - Bước 1: `paper_portable_v2.host_snapshot()` đọc `/proc/meminfo`, `/sys/class/hwmon`, `/sys/class/power_supply`, `/sys/devices/system/cpu/*/cpufreq`, `/proc/<pid>/task/*`, và **quét toàn bộ `/proc/[0-9]*/comm`** (`~350–500` PID).
   - Bước 2: `g2_v2_guard.cpu_capture(pid)` đọc tổng `/proc/stat` dòng đầu (`cpu` cộng gộp **cả 12 luồng logic `cpu0..cpu11`**), đọc `/proc/<owned_pid>/stat`, đọc `/proc/<monitor_pid>/stat`, rồi **quét lại toàn bộ `/proc/[0-9]*/stat` lần thứ hai**!
2. **Tính tải ngoại lai từng khoảng 1 giây (`interval()` dòng 39–60):**
   - `host_busy_ticks = user + nice + system + irq + softirq + steal` (loại `idle` và `iowait`, không cộng trùng `guest`), chia `CLK_TCK = 100` (`1 tick = 10 ms`).
   - Tại **mỗi khoảng `dt ≈ 1.0–1.1 s`**, tính:
     `foreign_i = max(0.0, busy_i - owned_i - monitor_i)` *(kẹp dưới về `0` trước khi cộng dồn vào cửa sổ trượt!)*.
3. **Cửa sổ trượt & Cổng abort cứng (`Contention.observe()` dòng 63–87, `g2_v2_runner.py` dòng 194–230):**
   - Gom các khoảng gần nhất sao cho `wall_W = sum(dt_i) >= 5.0 s`; kiểm tra:
     $$\frac{\sum_{i \in W} \text{foreign}_i}{\text{wall}_W \times 2} \le 0.01 \quad (\text{tức } \le 0.02\text{ CPU-s/s} = 10\text{ ticks / }5\text{ s trên cả 12 luồng}).$$
   - Trong `quiet_preflight()`: chỉ cho phép chờ cooldown nhiệt (`['Tctl threshold']`); **một lần vi phạm contention là `ValueError` dừng ngay chiến dịch, ghi `HOLD.json`, KHÔNG retry (`require(not output.exists())`).**
   - Trong `run()`: `run_paper_fullfan_check.py` (dòng 128) còn `os.fork()` một **tiến trình `watchdog` độc lập** chạy song song mỗi 1 giây; bất kỳ lần `guard.check()` nào trả về `reasons != []` đều gửi `SIGTERM`/`SIGKILL` kết thúc tiến trình đo và abort toàn bộ campaign.

### 1.2 Tổng hợp Toàn bộ Dữ liệu Quiet-Host & Telemetry Đã Thu thập

| Nguồn quan sát | Phạm vi & Môi trường | `rolling_frac` (`<= 0.01` bắt buộc) | Tải của chính monitor (`mon / (wall×2)`) | Ghi nhận cốt lõi |
|---|---|---:|---:|---|
| `preflight_0004` (`7.745 s`, `8` snaps) | Ubuntu Desktop + `msedge` hoạt động + `agy` | `0.5030 – 0.5441` (`0/3` PASS) | **`3.42%`** (`6.84%` của 1 core, `0.53 s`) | `msedge` chiếm ưu thế; `gap = fgn - tracked_other` dao động `-0.26 s .. +0.19 s` |
| `recovery_0020` (`16.406 s`, `16` snaps) | Ubuntu Desktop + `msedge` gần rỗi (`0.12%`) + `agy` | `0.0859 – 0.1537` (`0/11` PASS; mean `10.97%`) | **`2.83%`** (`5.67%` của 1 core, `0.93 s`) | `gnome-shell` `4.48%`, `agy` `3.11%`, `gnome-terminal-` `2.71%`, `ChatGPT` `1.04%`, **OS/kernel thuần `0.91%`** (`1.25%` nếu gồm `iostat`) |
| Owner TTY Run A (`/home/thinhbui/b1.py`, `30 s`, `26` cửa sổ) | Sau đăng xuất Ubuntu Desktop, minimal TTY *(owner báo cáo trực tiếp, không lưu file log riêng)* | **`26 / 26 PASS`** | ~`2.5%–3.5%` *(cùng code `b1.py`)* | Chứng minh trong khoảng lặng ngắn `30 s` không dính xung timer, nền OS có thể rơi dưới `1.0%` |
| Owner TTY Run B (`/home/thinhbui/b1.py`, `30 s`, `26` cửa sổ) | Sau đăng xuất Ubuntu Desktop, minimal TTY *(owner báo cáo trực tiếp)* | **`17 PASS / 9 FAIL` (`34.6%` cửa sổ FAIL)** | ~`2.5%–3.5%` | Chứng minh cùng trạng thái đã đăng xuất Desktop vẫn bị các đợt xung hệ thống/lượng tử hóa đánh trượt bất định |
| Historical Stage 5 (`60` runs, `2,715` snaps) & Stage 6 (`12` runs, `187` snaps) | Chạy thực tế trên cùng Ryzen 4650U bằng base guard (`232ed904...`) | *(không có `v2_cpu`)* | Base `observer_cpu_s` riêng lẻ: `0.0177 s` (S5) / `0.0326 s` (S6), `collection_wall_s` tới `0.425 s` | `load1m` nền khi chạy `p=2`: median `2.85` (S5) / `1.81` (S6), cho thấy hệ thống luôn có nền hoạt động đa nhân |

---

## 2. Đánh giá Độ Phù hợp của Ngưỡng `foreign_busy_s / (wall_s × 2) <= 0.01` trên Ryzen 5 PRO 4650U

**Kết luận định lượng: Ngưỡng `<= 0.01` trên tổng 12 luồng với cửa sổ 5 giây và cơ chế zero-retry KHÔNG phù hợp cho vận hành tin cậy trên Ubuntu 24.04 + Ryzen 5 PRO 4650U.** Có 5 nguyên nhân độc lập đã được xác minh trực tiếp trên máy:

1. **Lệch chuẩn quy mô phần cứng (12-thread numerator ÷ 2-worker denominator):**
   - Kiểm tra trực tiếp `/sys/devices/system/cpu/cpu{0..11}` xác nhận Ryzen 5 PRO 4650U gồm **2 cụm CCX/L3 tách biệt hoàn toàn**:
     - **CCX 0 (`L3 shared 0-5`):** `core 0` (`cpu0, cpu1`), `core 1` (`cpu2, cpu3`), `core 2` (`cpu4, cpu5`) — nơi 2 worker ANN được ghim cố định vào **`[0, 2]`**. Ngoài ra `cpu0` là CPU nhận phần lớn ngắt mềm hệ thống (`softirq = 904` ticks so với `13–54` ticks trên `cpu6–11`).
     - **CCX 1 (`L3 shared 6-11`):** `core 4` (`cpu6, cpu7`), `core 5` (`cpu8, cpu9`), `core 6` (`cpu10, cpu11`) — **không dùng chung core vật lý, không dùng chung L1/L2 và không dùng chung L3 với `[0, 2]`**.
   - Ngưỡng `foreign_busy_s / (wall_s × 2) <= 0.01` giới hạn tổng tải ngoại lai trên **toàn bộ 12 luồng** ở **`0.02` CPU-s/s = `0.167%` năng lực toàn máy** (chỉ **`10` jiffies / `5 s`**). Một tác vụ bảo trì OS tốn đúng `110 ms` trên `CPU 9` (`CCX 1`) vẫn đủ làm trượt **`5` cửa sổ cuộn 5s liên tiếp** và hủy toàn bộ chiến dịch!
2. **Xung định kỳ từ `systemd` timers & dịch vụ hệ thống vẫn chạy sau khi đăng xuất Ubuntu Desktop:**
   - Kiểm tra trực tiếp `systemctl list-timers --all` trên chính host ghi nhận **18 system timers đang hoạt động ở mức root** kể cả khi không có phiên desktop người dùng:
     - **`sysstat-collect.timer`**: kích hoạt **mỗi 10 phút** (`07:10`, `07:20`, …, `08:10:17`, `08:20:00`).
     - Các timer đã chạy đúng khung giờ kiểm tra sáng 24/11: `fwupd-refresh.timer` (`07:07:16`), `apt-daily-upgrade.timer` (`07:19:48`), `anacron.timer` (`07:30:54`), `update-notifier-download.timer` (`07:57:11`), `systemd-tmpfiles-clean.timer` (`08:07:11`), cùng `gdm3` login greeter sau khi logout và các `kworker`/`iwlwifi`/`rcu_preempt`/`systemd-oomd` nền (đã đo phần dư tĩnh `~0.91%` ngay ở 16s yên tĩnh nhất).
3. **Xác suất sống sót chiến dịch bằng ~0% dưới quy tắc 1 lần vượt = Abort không retry:**
   - Chiến dịch `18` Quality ON (~`15 phút` ≈ `180` khối 5s không chồng lấp) chắc chắn đi qua **`1–2` chu kỳ `sysstat-collect.timer`**; chiến dịch `144` G2 OFF (~`2.5–3.5 giờ` ≈ `1,440–2,520` khối 5s) chắc chắn đi qua **`15–21` chu kỳ `sysstat-collect.timer`** cộng nhiều timer `anacron`/`fwupd`/`apt-daily`.
   - Tính xác suất sống sót độc lập $P(\text{survive}) = (1 - p)^K$ theo xác suất trượt $p$ của mỗi khối 5 giây:

| Xác suất trượt mỗi khối 5s ($p$) | `P(>=1 fail trong 30s)` | `P(18 ON Quality ~15 phút sống sót)` | `P(144 OFF ~2 giờ sống sót)` |
|---:|---:|---:|---:|
| `0.10%` | `0.6%` | `83.52%` | `23.68%` |
| `0.50%` | `3.0%` | `40.57%` | **`0.07%`** |
| `1.00%` | `5.9%` | **`16.38%`** | **`0.00%`** |
| `5.00%` | `26.5%` | **`0.01%`** | **`0.00%`** |
| `34.60%` *(quan sát Run B: 9/26)* | `92.2%` | **`0.00%`** | **`0.00%`** |

4. **Lỗi thống kê nội tại của phép tính từng giây (`max(0, ...)` rectification bias):** Xem Mục 3.3 bên dưới — tự tạo thêm `0.28%–0.57%` tải ngoại lai ảo ngay cả khi máy hoàn toàn rỗi.
5. **Áp đặt ngưỡng timing-noise cho pha `QUALITY_ONLY` mang tính xác định:** `18` tiến trình `QUALITY_ONLY` ON không dùng để đo latency OFF (chỉ kiểm exact ordered Top-10, `squared_l2`, Recall@10, logical counters vốn bất biến hoàn toàn trước các xung CPU nhỏ), nhưng lại chịu cùng nguy cơ abort toàn chiến dịch nếu dính một đợt `sysstat-collect` 10 phút!

---

## 3. Phân biệt Rạch ròi Ba Nguồn Tải CPU (Hệ thống vs Cạnh tranh Thực vs Công cụ Đo)

| Phân loại | Nguồn cụ thể đã xác minh trên host | Mức CPU đo được / đặc trưng | Tác động vật lý lên phép đo `p=2` trên `[0,2]` | Cách xử lý khoa học đúng |
|---|---|---|---|---|
| **A. Tải CPU hệ thống (OS / Kernel / Timers)** | `irq/*-iwlwifi` (`0.27%`), `kworker/*` (`0.43%`), `irq/9-acpi` + `rcu_preempt` + `systemd-oomd` + `upowerd` + `tracker-miner-f` (`0.21%`) -> sàn tĩnh **`~0.91%`**; xung ngắn định kỳ từ `sysstat-collect.timer` (mỗi 10 phút), `fwupd-refresh`, `anacron`, `apt-daily`, `systemd-tmpfiles-clean`, `gdm3` | Liên tục `0.5%–1.0%` + xung ngắn `100–300 ms` rải rác trên 12 luồng | Rất nhỏ trên `mean` nếu rơi ở CCX 1 (`cpu6–11`) và ngẫu nhiên độc lập với `base/opt`; có thể làm tăng nhẹ đuôi `p99` nếu rơi đúng `cpu0..3` | Ghi nhận đầy đủ; tách kiểm soát chặt trên **CCX 0 (`cpu0..3`)** khỏi xung ngắn `100 ms` trên toàn 12 luồng bằng cửa sổ dài hơn (`15 s`) & phép trừ ròng theo cửa sổ |
| **B. Tiến trình cạnh tranh thực sự (Real Competitors)** | Named CPU/ANN jobs (`stress-ng`, `sysbench`, `task_da_p2_eval`, …); ứng dụng nặng người dùng (`msedge` tới `50–60%`, `gnome-shell` `4.48%`, `agy` `3.11%`, `gnome-terminal-` `2.71%`, `ChatGPT` `1.04%`); bất kỳ job ẩn danh nào kéo dài `> 0.10` CPU-s/s hoặc chiếm core/L3 `CCX 0` | Kéo dài nhiều giây đến nhiều phút (`1%–60%+` công suất p2) | **Gây nhiễu thực sự và nghiêm trọng:** tranh core/SMT/L3 cache (`CCX 0`), chiếm băng thông DRAM, ăn ngân sách TDP/STAPM 15–25W của Ryzen 4650U, làm thiên lệch `mean`, `p95`, `p99` | **BẮT BUỘC CHẶN CỨNG** (hard abort tức thời với named jobs, hard abort với sustained single process và mọi contention trên `cpu0..3` / `CCX 0`) |
| **C. Nhiễu từ chính công cụ đo (Measurement Self-Noise)** | 1) **Quét kép `/proc` + 1 Hz JSONL flush** trong `paper_portable_v2.host_snapshot()` + `g2_v2_guard.cpu_capture()`<br>2) **Monitor không cách ly khỏi CCX 0** (`allowed_cpus=[0..11]`)<br>3) **Forked `watchdog` (`run_paper_fullfan_check.py` dòng 128)** không được trừ khỏi `foreign_busy_s`<br>4) **Per-1s `max(0, ...)` rectification bias** trên jiffy `10 ms` (`g2_v2_guard.py` dòng 51) | **Riêng monitor tốn `5.67%–6.84%` của 1 core (`2.83%–3.42%` công suất p2 — gấp `~3×` ngưỡng `1%`!)**; `max(0,...)` tạo thêm **`+0.28%..+0.57%`** trung bình (`+0.50%..+1.10%` p95) | **Nghịch lý lớn nhất của `design-2`:** chính monitor có thể chạy trên `cpu0..5` (dùng chung core/SMT/L3 với workers) gây nhiễu lớn gấp ~3× tải ngoại lai bị cấm; đồng thời làm tăng xác suất false-abort tới **`5.0%`** ở `SD = 2 ticks` khi tải ngoại lai thật = `0`! | **Sửa trực tiếp ở mã guard (`design-3`):** bỏ quét kép `/proc`, trừ đúng cả `watchdog_pid`, chuyển sang trừ ròng theo cửa sổ `W` (triệt tiêu `5×` rectification bias) |

### Minh chứng Định lượng cho Lỗi Rectification Bias (`g2_v2_guard.py` dòng 51)
Mô phỏng trực tiếp (`B = 20,000`, `true foreign = 0`, `CLK_TCK = 100`) độ lệch pha lượng tử hóa `e_t ~ round(N(0, σ²))` giữa đọc `/proc/stat` và `/proc/<owned>/stat` + `/proc/<monitor>/stat` khi 2 worker ANN tạo `200 ticks/s` và monitor tạo `6 ticks/s`:

| Độ lệch pha lượng tử hóa ($\sigma$, đơn vị tick = `10 ms`) | `design-2` (kẹp `max(0,·)` mỗi 1s rồi cộng 5s): Mean / p95 / `P(>0.01)` | Trừ ròng trên cửa sổ (`max(0, ΣΔ)`): Mean / p95 / `P(>0.01)` |
|---:|---|---|
| `0.5` tick (`5 ms`) | `0.00135` / `0.00300` / `0.00%` | `0.00027` / `0.00100` / `0.00%` |
| `1.0` tick (`10 ms`) | **`0.00282` / `0.00500`** / `0.01%` *(ăn mất 28%–50% ngân sách `0.01`)* | `0.00056` / `0.00200` / `0.00%` |
| `1.5` ticks (`15 ms`) | **`0.00424` / `0.00800`** / `0.48%` | `0.00085` / `0.00400` / `0.00%` |
| `2.0` ticks (`20 ms`) | **`0.00565` / `0.01100` / `5.01%`** *(tự gây false-abort khi máy rỗi 100%!)* | `0.00112` / `0.00500` / `0.01%` |

---

## 4. Đánh giá Rủi ro Khoa học Nếu Thay đổi Noise Threshold

Mọi điều chỉnh đối với ngưỡng nhiễu nền đều mang rủi ro khoa học thực sự và phải được đánh giá thẳng thắn trước khi owner ra quyết định:

1. **Tăng phương sai latency & tiêu thụ ngân sách điện/nhiệt dùng chung (TDP/DRAM):**
   - Trên laptop Ryzen 5 PRO 4650U, hai CCX tuy tách L1/L2/L3 nhưng vẫn chia sẻ **giới hạn công suất gói (package TDP/STAPM)** và **bộ điều khiển DRAM**. Nếu nới ngưỡng toàn máy quá mức, nhiễu nền làm tăng `SD(x_b)` giữa 12 block -> CI95 rộng hơn -> **giảm statistical power** (dễ rơi vào `HOLD` hơn, chứ không dễ tạo dương giả `GO` nếu nhiễu đối xứng).
2. **Độ nhạy cao hơn ở đuôi `p95` / `p99` so với `mean`:**
   - Một xung `150–200 ms` trên đúng `cpu0..3` (core/SMT của workers) có thể đẩy `p99` (`100` query chậm nhất trong `10,000`) tăng cục bộ ngay cả khi `mean` thay đổi `< 0.5%`. **Hệ quả thiết kế:** Tuyệt đối **KHÔNG được nới lỏng tại `cpu0..3`**; mọi điều chỉnh chỉ được phép phân tách phần xung vô hại trên `CCX 1` (`cpu6..11`) và sửa lỗi tính toán của chính công cụ đo.
3. **Nguy cơ thiên lệch hệ thống (Systematic Bias) nếu nhiễu mất cân bằng giữa `base` và `opt`:**
   - Lịch cân bằng 12 block (mỗi graph 6 AB + 6 BA, hai policy chạy liền nhau) làm kỳ vọng thiên lệch của xung OS ngẫu nhiên bằng `0`, nhưng không tự bảo đảm cân bằng trên mẫu hữu hạn `12` block nếu có một đợt cập nhật dài chạy trùng một pha. **Biện pháp kiểm soát bắt buộc:** ghi `foreign_busy` cho từng process trong `metrics.json` và bổ sung kiểm tra thống kê bắt buộc cho `paired Δforeign = foreign_opt - foreign_base` trong analyzer (không dùng để lọc bỏ lượt chạy, chỉ để phát hiện mất cân bằng nhiễu!).
4. **Rủi ro uy tín phương pháp luận (Perceived Post-hoc Threshold Loosening):**
   - Bất kỳ việc sửa ngưỡng nào sau khi thấy B1 trượt đều dễ bị nghi ngờ là "nới cổng cho dễ chạy". Tuy nhiên, điều kiện bảo vệ vững chắc ở đây là: **(a) `Quality ON = 0/18`, `G2 OFF = 0/144`, `v2_test_10000.ids` chưa materialize — hoàn toàn là pre-data operational amendment, ZERO dữ liệu quality/performance đã được nhìn**; và **(b) bản sửa đổi thực chất làm đo đạc *sạch hơn về vật lý* (giảm tự nhiễu monitor từ `3%` xuống `< 1%`, sửa lỗi rectification bias `5×`, giữ nguyên trần `<= 1%` tại đúng core/SMT `[0,1,2,3]` của worker).**
5. **Rủi ro bỏ lọt đối thủ thực sự nếu nới mù quáng:**
   - Nếu chỉ tăng một con số duy nhất từ `0.01` lên `0.05` hay `0.10` mà không có kiểm soát theo CCX và per-process, một ứng dụng đơn lẻ chiếm 10% core trên `cpu1` (SMT sibling của `cpu0`!) vẫn có thể lọt qua. Do đó **bác bỏ cách "nới một con số đơn thuần"**, chỉ chấp nhận thiết kế kiểm soát nhiều tầng như Mục 5.

---

## 5. Đề xuất Controlled Preregistration Amendment `design-3` (Chờ Owner Duyệt — Chưa Thực thi)

### 5.1 Toàn bộ Thành phần Giữ Nguyên 100% từ `design-2` (ZERO Retuning)
- Chủ thể & cấu hình: `6` graph R90 v1.3, Release ELF `7a2685e5...`, `p=2`, `S=16`, `common beam = 432`, `CPU [0,2]`, `jobs=1`, `K=10`, `entry=0`, `v2_test_10000.ids` (`457abdc1...`), `val_10k.ids`, `warmup_val_100.ids`.
- Toàn bộ cổng chất lượng, thống kê và quyết định: Gate A (`simultaneous LCB95 >= 0.990`, exact Top-10/L2 parity, counter invariants), Gate B (`arm CI95 ∈ (-0.0005, +0.0005)`), Primary (`geometric paired mean-latency reduction > 3%`, `CI12`, `drift CI6`, `joint bootstrap`), Tail (`p95 <= +5%`, `p99 <= +10%`), RAM (`per-pair integer hard gate` + `aggregate CI`), lịch `12` block cân bằng (`144` OFF), `Tctl < 85/95°C`, `AC`, `MemAvailable > 1 GiB`, `disk > 25/20 GiB`, `swap`, cấm bỏ lượt chậm/outlier, cấm tự retry OFF, nhãn **`EXPLORATORY_HOST_SPECIFIC`**.

### 5.2 Sáu Điều chỉnh Có Kiểm soát Duy nhất trong `design-3` (Chỉ Tầng B1 Guard & Telemetry)

1. **Sửa 3 lỗi kỹ thuật nội tại của công cụ đo (`g2_v2_guard.py`):**
   - **Bỏ quét kép `/proc`:** Đọc `/proc/stat` (cả dòng tổng `cpu` và 12 dòng `cpu0..cpu11`) + `/proc/<owned>/stat` + `/proc/<monitor>/stat` + `/proc/<watchdog>/stat`, và chỉ quét `/proc/[0-9]*/stat` **một lần duy nhất** mỗi giây (không quét lại `/comm` ở lớp `paper_portable_v2` khi đang chạy qua `g2_v2_guard` — giảm CPU tự sinh của monitor từ `~6%` xuống `< 1.5–2%` của 1 core).
   - **Trừ đúng `watchdog_pid`:** Truyền `watchdog_pid` từ wrapper vào bộ đếm loại trừ cùng với `owned_pid` và `monitor_pid` để watchdog không bị tính nhầm là tải ngoại lai. *(Không thay đổi global host affinity/fan/power/security theo `AGENTS.md`.)*
   - **Đổi sang phép trừ ròng theo cửa sổ (Window-Net Subtraction):** Thay `sum(max(0, busy_i - owned_i - monitor_i))` bằng:
     $$\text{foreign\_net}(W) = \max\Big(0,\; \Delta\text{busy}(W) - \Delta\text{owned}(W) - \Delta\text{monitor}(W) - \Delta\text{watchdog}(W)\Big)$$
     tính trực tiếp giữa snapshot đầu và cuối cửa sổ `W` -> triệt tiêu `5×` rectification bias từ sai số lượng tử hóa `10 ms` (xác suất false-abort ở `SD = 2 ticks` giảm từ `5.01%` xuống `0.01%`).
2. **Kiểm soát phân tầng theo Topology CCX (Per-CPU `/proc/stat` `cpu0..cpu11`) cho pha `OFF` (`144` runs):**
   - **Tầng 1 — Worker Cores & SMT Siblings (`CPUs {0, 1, 2, 3}`, cửa sổ trượt `W >= 10 s`):** Tải ngoại lai trên 4 luồng cùng 2 core vật lý của worker (đã trừ `owned` và phần `monitor`/`watchdog` nếu rơi vào đó) phải **`<= 0.01` (`<= 1.0%` công suất `p=2`, tức `<= 0.02` CPU-s/s)** — **giữ nguyên độ chặt `1%` tại nơi trực tiếp tác động latency & p99!** *(Cộng giới hạn `CCX 0 / L3 {0..5}` `<= 0.02` = `<= 0.04` CPU-s/s để bảo vệ L3 cache.)*
   - **Tầng 2 — Toàn máy 12 luồng (`CPUs {0..11}`, cửa sổ trượt `W >= 15 s`):**
     $$\frac{\text{foreign\_net}_{\text{all}}(W)}{\text{wall}_W \times 2} \le 0.025 \quad (\text{tức } \le 0.05\text{ CPU-s/s} = 0.42\%\text{ năng lực 12 luồng})$$
     *(Dưới cửa sổ `15 s`, mẫu số là `30 s`, cho phép tối đa `0.75 s` tổng tải hệ thống trên cả 12 luồng trong 15 giây — đủ hấp thụ một xung `100–250 ms` của `sysstat-collect` hay `kworker` trên `CCX 1` mà vẫn chặn mọi tải nền kéo dài `> 5%` của một core!)*
   - **Tầng 3 — Chặn cứng tức thời & Single-Process Cap:** Giữ nguyên abort tức thời khi xuất hiện bất kỳ `KNOWN_CPU_JOBS` nào, VÀ abort nếu **bất kỳ một tiến trình ngoại lai đơn lẻ nào** vượt **`> 0.10` CPU-s/s** (tức `> 10%` của 1 core) kéo dài trên cửa sổ `>= 10 s` (bắt ngay mọi ứng dụng ẩn danh như trình duyệt/compiler/indexer).
3. **Phân tách Cổng Contention giữa Pha `QUALITY_ONLY` (Xác định) và Pha `OFF` (Đo Latency):**
   - Pha `QUALITY_ONLY` (`18` ON runs) không sử dụng timing làm kết quả hiệu năng; giữ nguyên toàn bộ cổng an toàn phần cứng (`Tctl < 85/95°C`, `AC`, `MemAvailable`, `disk`, `swap`, `CPU [0,2]` observed, chặn tức thời `KNOWN_CPU_JOBS`), ghi đầy đủ telemetry phân tầng CCX vào `host.jsonl`, và chỉ hard-abort contention khi máy bị tải nặng thực sự (`foreign_net_all(15s)/(wall×2) > 0.10` hoặc single foreign process `> 0.25` CPU-s/s trong `>= 10 s`).
   - Pha `OFF` (`144` runs) áp dụng nghiêm ngặt đầy đủ cả **3 tầng** ở mục 2 trên đây.
4. **Cổng Kiểm định Tiền Thực nghiệm B1 Dài hạn (`15 phút` Minimal-TTY Qualification):**
   - Trước khi ký `quiet_host_confirmed: true` cho `design-3`, bắt buộc chạy và **lưu raw JSONL** một phiên kiểm tra liên tục **`15 phút` (`900 s` — đủ phủ trọn ít nhất 1 chu kỳ `sysstat-collect.timer` 10 phút)** ở trạng thái minimal TTY đã đăng xuất Desktop; yêu cầu **`100%` cửa sổ trượt vượt qua cả 3 tầng cổng `design-3`** (và báo cáo đầy đủ `p50/p95/max` của `foreign_workers_0_3`, `foreign_ccx0_0_5`, `foreign_all_15s`, `monitor_cpu`, `Tctl`).
5. **Kiểm toán Thống kê Nhiễu Hậu kỳ Bắt buộc (Trong `g2_v2_analyzer.py`):**
   - Lưu `mean_foreign_workers_0_3`, `mean_foreign_all_15s` và `max_foreign_all_15s` trong mọi `process` receipt (`metrics.json`).
   - Tính và báo cáo bắt buộc `paired Δforeign_gb = foreign_opt_gb - foreign_base_gb` (mean và `CI95` qua 12 block) và tương quan chẩn đoán giữa `Δforeign_gb` với `x_gb = log(B_gb/C_gb)` — đảm bảo minh bạch rằng nhiễu nền không tạo thiên lệch có hệ thống giữa `base` và `opt` (chỉ dùng để phát hiện/HOLD nếu mất cân bằng, tuyệt đối không dùng để loại bỏ lượt chạy hay cứu `GO`).
6. **Quản trị Đóng băng Độc lập cho `design-3`:**
   - Bảo toàn nguyên vẹn toàn bộ file & checksum của `design-2`; chỉ khi owner phê duyệt, tạo bộ `revision: "design-3"` + freeze manifest mới + bổ sung unit tests cho window-net subtraction, watchdog exclusion, per-CPU CCX guard, và phase-aware gating -> xác minh full dataset-free suite `0 failures` -> trình owner ký approval receipt mới khớp đúng `design-3` freeze SHA (thay thế approval cũ vốn ràng buộc `design-2` freeze SHA `91186d57...`).

---

## 6. So sánh `design-2` vs Đề xuất `design-3` & Khuyến nghị `GO / HOLD`

| Tiêu chí đối chiếu | `design-2` (Đóng băng hiện tại) | Đề xuất `design-3` (Controlled Pre-Data Amendment) |
|---|---|---|
| **Trạng thái hiện tại** | Đóng băng (`91186d57...`), `B3 PASS`, `B2 PASS`, **`B1 UNSTABLE (17/26 PASS)`** | **Đề xuất chờ owner duyệt** (chưa sửa code, chưa phê duyệt) |
| **Tự nhiễu của chính monitor** | **`2.83% – 3.42%` công suất p2** (quét kép `/proc`, gấp ~3× ngưỡng `1%`!) | **Giảm xuống `< 0.7%–1.0%`** (bỏ quét kép `/proc`) |
| **Xử lý `watchdog` fork** | **Chưa trừ** -> CPU của watchdog rò sang `foreign_busy_s` | **Trừ tường minh `watchdog_pid`** |
| **Rectification bias `10 ms` tick** | Kẹp `max(0,·)` từng 1s -> **`+0.28%..+0.57%`** nhiễu ảo (`5.0%` false-abort ở `SD=2 ticks`) | Trừ ròng theo cửa sổ `W` -> triệt tiêu `5×` bias (`0.01%` ở `SD=2 ticks`) |
| **Bảo vệ trực tiếp Core/SMT `[0,1,2,3]`** | Không phân biệt `CCX 0` với `CCX 1` (trộn chung 12 luồng) | **Giữ chặt `<= 1.0%`** ngay trên `CPUs {0,1,2,3}` + `<= 2.0%` trên `L3 {0..5}` |
| **Khả năng chịu xung OS `100–250 ms` ở `CCX 1` (`sysstat-collect` 10 phút)** | **Rất kém:** 1 xung `110 ms` đánh trượt 5 cửa sổ liên tiếp -> abort toàn campaign | **Ổn định:** cửa sổ `15 s` + ngưỡng toàn máy `<= 2.5%` (`0.42%` của 12 luồng) hấp thụ xung OS vô hại nhưng vẫn chặn mọi tải thực `> 5%` một core hoặc single process `> 10%` |
| **Pha `QUALITY_ONLY` (18 ON xác định)** | Bị abort toàn bộ chỉ vì 1 xung timer 10 phút dù Recall/Top-10 hoàn toàn xác định | Giữ toàn bộ safety guard & chặn `KNOWN_CPU_JOBS`, không false-abort vì xung OS nhỏ |
| **Xác suất hoàn tất 18 ON / 144 OFF (không retry)** | **Rất thấp / ~`0%`** (quan sát `9/26` trượt ở 30s; `sysstat-collect` chạy 10 phút/lần) | **Cao & kiểm chứng được trước** qua cổng qualification `15 phút` (`100% PASS` lưu raw JSONL) |
| **Rủi ro khoa học & liêm chính thống kê** | Không sửa ngưỡng, nhưng thực tế **không thể hoàn tất** chiến dịch `144 OFF` và bản thân monitor gây nhiễu `3%` | Hoàn toàn **pre-data** (`0/18` ON, `0/144` OFF), giữ nguyên 100% beam/panel/RAM/tail/3%, bổ sung kiểm toán cân bằng `Δforeign` trong analyzer; đòi hỏi cập nhật code/tests/freeze/approval mới |

### Khuyến nghị Cuối cùng Cho Owner: **`HOLD`** *(Không `GO` dưới `design-2`)*

1. **Khuyến nghị chính thức ngay lúc này: `HOLD` trên `design-2` (`B1_HOLD_NOISE_THRESHOLD_INFEASIBLE`).**
   - **Không khuyến nghị `GO` ngay dưới `design-2`**, dù `B3 = PASS` và `B2 = APPROVAL_CONTRACT_CHECK=PASS`: dữ liệu `17 PASS / 9 FAIL` sau đăng xuất Desktop cùng chu kỳ `sysstat-collect.timer` 10 phút và các lỗi tự nhiễu (`monitor ~3%`, `watchdog` chưa trừ, `max(0,·)` rectification bias) khiến cả 18 lượt `QUALITY_ONLY` lẫn 144 lượt `OFF` đứng trước nguy cơ abort gần như chắc chắn giữa chừng (và tạo thư mục output dở dang `HOLD.json` không thể resume).
2. **Ba phương án trình Owner quyết định bước kế tiếp (agent dừng tại đây, không tự chuyển stage):**
   - **Phương án A (Khuyến nghị mạnh nhất — Controlled Amendment `design-3`):** Giữ `design-2` đóng ở `HOLD`, owner phê duyệt bằng văn bản cho triển khai & đóng băng `design-3` theo đúng 6 điều chỉnh ở Mục 5.2 (chỉ tầng B1 guard/telemetry + unit tests, giữ nguyên 100% thống kê/beam/panel/RAM/tail/3% và nhãn `EXPLORATORY_HOST_SPECIFIC`), sau đó owner chạy kiểm định qualification **`15 phút` lưu raw JSONL** trên minimal TTY rồi mới ký approval `design-3` cho `QUALITY_ONLY`.
   - **Phương án B (Giữ nguyên `design-2`, xử lý hệ điều hành phía owner):** Nếu owner kiên quyết giữ nguyên `design-2` không sửa 1 dòng code nào, cần giữ `HOLD` cho tới khi owner tự kiểm soát các dịch vụ nền cấp hệ thống (`sysstat-collect`, `fwupd`, `anacron`, `gdm3` — thuộc quyền quản trị máy của owner, ngoài phạm vi agent) và chứng minh **`15 phút` liên tiếp `100% PASS` có lưu raw log** trước khi chạy `QUALITY_ONLY` *(chấp nhận rủi ro còn lại từ monitor `~3%`, `watchdog` và rectification bias khi có 2 luồng ANN chạy thật)*.
   - **Phương án C (Dừng dài hạn trên laptop 4650U):** Giữ **`HOLD`** cho G2 v2 trên host hiện tại và chỉ mở lại nếu có môi trường đo sạch hơn trong một preregistration tách biệt.

---

## 7. Xác nhận Tuân thủ Ràng buộc (Preservation Ledger)

- `design-2` threshold & `24/24` checksums [AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256](AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256): **`UNCHANGED (OK)`**.
- `design-3`: **`PROPOSAL_ONLY / NOT_IMPLEMENTED / NOT_APPROVED`**.
- `Quality ON`: **`0 / 18`** · `G2 OFF`: **`0 / 144` (`NOT_OPEN`)** · `Profiler`: **`0`** · `v2_test_10000.ids`: **`NOT_MATERIALIZED`**.
- `Historical v1 QUALITY_HOLD` (`cb6433cb...`), Stage 5/6 bundles, preflight bundles & `Task A Google Sheets`: **`UNCHANGED`**.
- `Git tracked diff`: **`EMPTY`** · `Git commit`: **`NONE`**.
