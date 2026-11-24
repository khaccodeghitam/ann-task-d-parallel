# A×D G2 v2 · Controlled Preregistration Amendment `design-3`

- **Protocol & Revision:** `AXD-G2-V2-3A-20261123` · revision **`design-3`** · schema **`axd_g2_v2.3`** · **`EXPLORATORY_HOST_SPECIFIC`** · `p=2`, `S=16`, `common beam = 432`.
- **Authorization Posture:** Owner phê duyệt **Phương án A** (triển khai, kiểm thử, kiểm toán và đóng băng `design-3`) từ [AXD_G2_V2_B1_QUIET_FEASIBILITY_REVIEW.md](AXD_G2_V2_B1_QUIET_FEASIBILITY_REVIEW.md). **KHÔNG** cấp quyền chạy `18` Quality ON hay `144` G2 OFF; toàn bộ package `design-2` (`91186d57...`) và historical v1 (`cb6433cb...`) giữ nguyên bất biến.
- **Pre-Data Integrity Disclosure:** Bản tu chính này được thiết lập khi **`Quality ON = 0/18`**, **`G2 OFF = 0/144`**, và **`v2_test_10000.ids` chưa được materialize**. Không có bất kỳ dữ liệu quality v2 hay performance OFF nào được sử dụng để lựa chọn ngưỡng.

---

## 1. Thành phần Giữ Nguyên Tuyệt đối từ `design-2` (`ZERO Retuning`)

1. **Cohort & Binary:** `6` graph gốc R90 v1.3 (`stock_off_r1..r3`, `fast_off_r1..r3`, khớp đúng 6 SHA), Release ELF `task_da_p2_eval` (`7a2685e5...`), nguồn search đóng băng `f2cd634`, compiler `/usr/bin/c++` (`1353e9bd...`), `5` thư viện native `.so`, `base/queries/gt/val/warmup`, `6` Stage 5 b432 validation baselines, và reference BUILD host A.
2. **Search Parameters & Split:** `p=2`, `S=16`, `flat`, `jobs=1`, `K=10`, `entry=0`, `CPU [0, 2]`, `common beam = 432`, `warmup_val_100.ids`, `val_10k.ids`, và công thức khóa `v2_test_10000.ids` (`SHA-256 = 457abdc13abc95d8d0f48ff32919a6013f5ed4bca469f9075312ae80dfe44b0d`).
3. **Quality & Statistical Estimands:** Gate A (`simultaneous one-sided LCB95 >= 0.990`, `z = 2.39397980`, exact ordered Top-10 & `squared_l2` parity, counter invariants), Gate B (`arm CI95 ∈ (-0.0005, +0.0005)`), Primary (`geometric paired mean-latency reduction > 3%`, `θ = -log(0.97)`, `CI12`, `drift CI6`, `query/joint bootstrap 10,000 resamples`), Tail (`p95 <= +5%`, `p99 <= +10%`), RAM (`per-pair integer hard gate 10(C-B) <= max(655360, B)` + simultaneous aggregate CI), `12` balanced OFF blocks (`6 AB / 6 BA` mỗi graph), `BUILD–SEARCH ΔT(Q)`, nhãn `EXPLORATORY_HOST_SPECIFIC` (`independent-root population CI = NOT_ESTIMABLE`).
4. **Hardware Safety Guards:** `Tctl < 85°C` start / `>= 95°C` abort, critical sensor trip, `AC online` & unchanged, `MemAvailable > 1 GiB`, `free_disk > 25 GiB` initial / `> 20 GiB` running, `swap growth <= 64 MiB` over `>= 10 s`, timeout `180 s/process`, lock độc quyền `/tmp/task-da-pivot-4650u.lock`, không kill process ngoài phạm vi, không bỏ lượt chậm, không tự retry OFF.

---

## 2. Sáu Sửa đổi Có Kiểm soát Duy nhất của `design-3` (Chỉ Tầng B1 Guard & Telemetry)

1. **Loại bỏ quét trùng `/proc` (`g2_v2_design3_guard.host_snapshot_v3`):** Hợp nhất quét `/proc/[0-9]*/stat` thành **đúng một lượt duy nhất** mỗi giây (lấy đồng thời `comm`, `utime+stime`, `starttime`, `processor` CPU #39, phát hiện `KNOWN_CPU_JOBS` và legacy ANN, serialization rút gọn không mất thông tin cho các PID `ticks == 0`) — không sửa `tools/research/paper_portable_v2.py` hay `run_paper_fullfan_check.py`.
2. **Hạch toán tường minh `watchdog_pid` cùng `owned_pid` và `monitor_pid`:** `run_guarded_v3()` ghi `watchdog_pid` và `watchdog_start_ticks` vào `manifest.json`, truyền `watchdog_pid` vào mọi snapshot để trừ chính xác CPU của tiến trình watchdog khỏi tải ngoại lai.
3. **Phép trừ ròng theo cửa sổ (`window_accounting`, thay thế per-1s `max(0, ·)`):** Trên cửa sổ `W` từ snapshot `start` tới `end`:
   $$\Delta F_{\text{all}}(W) = \max\Big(0,\; \Delta B_{\text{all}}(W) - \Delta O(W) - \Delta M(W) - \Delta D(W)\Big)$$
   triệt tiêu sai số dương tính (`5×` rectification bias) do lượng tử hóa `CLK_TCK = 100` (`10 ms`).
4. **Kiểm soát phân tầng theo Topology CCX (Ryzen 5 PRO 4650U, mẫu số thống nhất `wall_W × 2`):**
   - Đọc đồng thời dòng tổng `cpu` và 12 dòng `cpu0..cpu11` từ `/proc/stat`, xác minh bảo toàn `agg ≈ sum(cpu0..cpu11)`.
   - Với tập CPU $S \in \{S_{\text{w}} = \{0,1,2,3\},\; S_{\text{ccx0}} = \{0..5\}\}$, dùng ước lượng bảo toàn không che giấu:
     $$\Delta F(S, W) = \min\Big(\Delta F_{\text{all}}(W),\; \max\big(\max(0, \Delta B(S, W) - E(W)),\; \Delta F_{\text{procs}}(S, W)\big)\Big)$$
     trong đó $E(W) = \Delta O(W) + \Delta M(W) + \Delta D(W)$ và $\Delta F_{\text{procs}}(S, W)$ là tổng CPU theo tiến trình ngoại lai chạy trên $S$ -> luôn bảo toàn bất đẳng thức đơn điệu $0 \le f_{\text{workers}} \le f_{\text{ccx0}} \le f_{\text{all}}$.
   - **Chính sách pha `OFF` & `qualification`:**
     - Worker cores + SMT `{0,1,2,3}` (`W >= 10 s`): **`<= 0.01`** (`<= 1.0%` p2 = `0.02` CPU-s/s).
     - CCX-0 / Shared L3 `{0..5}` (`W >= 10 s`): **`<= 0.02`** (`<= 2.0%` p2 = `0.04` CPU-s/s).
     - Toàn host `{0..11}` (`W >= 15 s`): **`<= 0.025`** (`<= 2.5%` p2 = `0.05` CPU-s/s = `0.42%` toàn máy 12 luồng).
     - Single foreign process cap (`W >= 10 s`): **`<= 0.10`** (`<= 10%` của 1 core).
     - Instant hard abort với mọi `KNOWN_CPU_JOBS`; preflight quiet window `>= 15 s`.
5. **Tách ngưỡng contention cho pha `QUALITY_ONLY` (`18` ON xác định):**
   - Giữ toàn bộ safety/thermal/RAM/disk/swap/AC/`KNOWN_CPU_JOBS` và ghi đủ telemetry phân tầng; áp trần chống quá tải `foreign_all(15s)/(wall×2) <= 0.10` và single process `<= 0.25` (`W >= 10 s`), preflight `>= 10 s`. Không dùng thời gian ON làm số đo hiệu năng.
6. **Chẩn đoán cân bằng nhiễu ghép cặp & Cách ly Approval Receipt:**
   - Analyzer bổ sung `noise_balance` báo `paired Δforeign = opt - base` (mean + `CI95` qua `12` block, `df=11`) và tương quan Spearman với `x_gb = log(B_gb/C_gb)` (chỉ chẩn đoán, không lọc bỏ lượt chạy và không cứu `HOLD`).
   - `g2_v2_design3_contract.authorize()` yêu cầu `schema = "axd_g2_v2.3"`, `revision = "design-3"`, `freeze_sha256` của `design-3`, và **`qualification_sha256`** trỏ tới một biên nhận qualification `900 s` đạt **`QUALIFICATION_PASS`** -> **từ chối tuyệt đối mọi approval receipt của `design-2`**.
