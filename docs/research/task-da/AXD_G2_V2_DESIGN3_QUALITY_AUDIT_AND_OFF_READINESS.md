# A×D G2 v2 (`design-3`) · Independent Quality ON Audit & Performance OFF Readiness Report

- **Official Readiness Verdict:** **`READY_FOR_OFF_OWNER_APPROVAL`** *(toàn bộ 18/18 Quality ON đã vượt qua kiểm toán và replay độc lập 100%; **`G2 OFF` hiện vẫn ở trạng thái `NOT_OPEN`** chờ quyết định phạm vi và chữ ký riêng của owner).*
- **Protocol & Frozen Identity:** `AXD-G2-V2-3A-20261123` · revision **`design-3`** · schema **`axd_g2_v2.3`** · **`EXPLORATORY_HOST_SPECIFIC`** · `p=2`, `S=16`, `common beam = 432`.
- **Audited Quality Evidence (external, immutable):** `../../../../artifact-evidence/axd-g2-v2-quality-design3/` (`198 MiB`, `166/166` entries trong `BUNDLE.sha256` **OK**, `NO_HOLD_JSON`).
  - `quality.json` SHA-256: **`360e1d29fc3c8f3c03e381ce57dea2e826459f7534577d6d24ec6ac81a54c59f`**
  - `complete.json`: `elapsed_s = 939.660009621 s` (`15.66 phút`, trong hạn mức `quota_s = 3600 s`)
- **Unsigned OFF Draft Approval (ngoài frozen package):** `../../../../artifact-evidence/axd-g2-v2-approvals/design3_off_approval.DRAFT_UNSIGNED.json` *(chưa ký: `owner=""`, `approved_at=""`, `scope="UNAPPROVED"`, `quota_s=0`, `quiet_host_confirmed=false`).*
- **Non-Mutation & Scope Disclosure:** Phiên kiểm toán này **không** chạy lại 18 Quality ON, **không** chạy OFF benchmark (`0/144`), **không** tự ký approval, **không** sửa frozen package/guard/thresholds/Task A, và **không** suy luận speedup OFF từ counters hay thời gian ON.

---

## 1. Kiểm toán Độc lập 18/18 Quality ON (`axd-g2-v2-quality-design3`)

### 1.1 Toàn vẹn Bằng chứng, Provenance & Replay Quy trình

| Hạng mục kiểm toán độc lập | Kết quả kiểm chứng trực tiếp | Trạng thái |
|---|---|---|
| `BUNDLE.sha256` của chiến dịch Quality | `166 / 166` file khớp SHA-256; không tồn tại `HOLD.json` | **`PASS`** |
| `quality_context()` + schemas (`start`, `complete`, `quality`, `artifacts`) | Khớp 100% schema `axd_g2_v2.3`; `quality_sha256 = 360e1d29...a54c59f` khớp `complete.json` | **`PASS`** |
| Provenance freeze, approval & qualification | `DESIGN3_FREEZE` `26/26 OK`; `DESIGN2_FREEZE` `24/24 OK`; `FREEZE_BUNDLE` `4/4 OK`; `QUAL_PASS (20261124T094602Z)` `2/2 OK`; `QUAL_HOLD (20261124T082344Z)` `2/2 OK`; `load_freeze(environment=True)` PASS; `verify_artifacts()` PASS (`5/5` `.so`, `binary/base/queries/gt/val/warmup/test`, `6/6` R90 v1.3 graphs, `6/6` Stage 5 baselines) | **`PASS`** |
| Test panel `v2_test_10000.ids` trên đĩa | `SHA-256 = 457abdc13abc95d8d0f48ff32919a6013f5ed4bca469f9075312ae80dfe44b0d`; `count = 10,000`, `unique = 10,000`, biên `[0, 99999]`; 10 ID đầu `32792,20400,17878,72872,61505,35404,40783,34564,23435,79120`; **`overlap = 0`** với `val_10k`, `pilot_3k`, `disjoint_3k`, `narrow_3k`, `warmup_100` | **`PASS`** |
| Replay `18` preflight JSONL + `18` process receipts (`180,000` truy vấn ON) | `18/18` `exit_code == 0`, `guard_failure is None`, `wall_time_s` `39.65–42.75 s < 180 s`, chạy tuần tự tuyệt đối không chồng lấn thời gian; `process_result()` tính lại khớp từng byte `metrics.json`; `make_guard(..., phase="quality")` replay `0` lỗi | **`PASS`** |
| An toàn nhiệt / tài nguyên & nhiễu chẩn đoán | `Tctl = 40.00–85.75°C` (`< 95°C` abort; mọi preflight đều `10.43–10.54 s` không cần chờ hạ nhiệt); `AC = 1` liên tục; `min MemAvailable = 13.25 GiB`; `min free disk = 138.09 GiB`; `max swap = 0 B`; `max RSS = 851.4 MiB`. Nhiễu nền chẩn đoán suốt 18 lượt: `max_workers_10s = 0.00500`, `max_ccx0_10s = 0.00799`, `max_all_15s = 0.00733` *(đều dưới 50% ngay cả so với trần nghiêm ngặt của pha OFF!)* | **`PASS`** |
| Parity Validation `beam=432` (6 lượt `opt` vs 6 Stage 5 baseline) | `60,000 / 60,000` truy vấn khớp tuyệt đối ordered Top-10 IDs & `squared_l2`; giảm duplicate L2 **`74.98%–75.15%`** (`27,888,121–27,922,054` lượt/graph); khớp từng byte `quality.json["validation"]` | **`PASS`** |

### 1.2 Bảng Kết quả Độc lập trên 6 Graph R90 v1.3 (`test` 10.000 truy vấn ON, `beam=432`, `p=2`, `S=16`)

*(Toàn bộ giá trị Recall@10, SE, LCB95, exact parity, và duplicate L2 được replay trực tiếp từ 12 tệp `beam_432_p2_ON.jsonl` và `groundtruth.public.100K.ibin`; khớp `quality.json` tới `1e-15`. **Không** suy luận speedup OFF từ các counters ON dưới đây.)*

| Graph (`arm`) | Ordered Top-10 & L2² Parity | Recall@10 (`SE`) | Simultaneous `LCB95` (`z=2.3940`, sàn `0.990`) | Two-sided CI95 (mô tả) | Baseline Dup L2 | B1+A1 Dup L2 | Dup L2 Tiết kiệm tuyệt đối (`/query`) | Giảm Dup L2 vs Baseline (`%` Total L2) |
|---|---|---:|---:|---|---:|---:|---:|---:|
| `stock_off_r1` | **100% (`10,000/10,000`)** | `0.99209` (`0.000324`) | **`0.991315`** (`PASS`) | `[0.99146, 0.99272]` | `37,122,927` | `9,293,937` | **`27,828,990`** (`2,782.9`) | **`-74.96%`** (`-12.22%`) |
| `stock_off_r2` | **100% (`10,000/10,000`)** | `0.99197` (`0.000327`) | **`0.991188`** (`PASS`) | `[0.99133, 0.99261]` | `37,118,438` | `9,278,693` | **`27,839,745`** (`2,784.0`) | **`-75.00%`** (`-12.22%`) |
| `stock_off_r3` | **100% (`10,000/10,000`)** | `0.99209` (`0.000324`) | **`0.991314`** (`PASS`) | `[0.99145, 0.99273]` | `37,118,583` | `9,275,125` | **`27,843,458`** (`2,784.3`) | **`-75.01%`** (`-12.22%`) |
| `fast_off_r1` | **100% (`10,000/10,000`)** | `0.99229` (`0.000324`) | **`0.991514`** (`PASS`) | `[0.99166, 0.99292]` | `37,131,047` | `9,277,617` | **`27,853,430`** (`2,785.3`) | **`-75.01%`** (`-12.23%`) |
| `fast_off_r2` | **100% (`10,000/10,000`)** | `0.99197` (`0.000325`) | **`0.991193`** (`PASS`) | `[0.99133, 0.99261]` | `37,137,585` | `9,296,971` | **`27,840,614`** (`2,784.1`) | **`-74.97%`** (`-12.22%`) |
| `fast_off_r3` | **100% (`10,000/10,000`)** | `0.99224` (`0.000323`) | **`0.991467`** (`PASS`) | `[0.99161, 0.99287]` | `37,139,906` | `9,304,037` | **`27,835,869`** (`2,783.6`) | **`-74.95%`** (`-12.22%`) |

- **Gate A (`A_pass = true`):** cả 6 graph có point Recall `0.99197–0.99229` (span liên graph `0.00032`) và simultaneous one-sided `LCB95` `0.991188–0.991514 >= 0.990`; `60,000/60,000` cặp test và `60,000/60,000` cặp validation đạt exact ordered Top-10 & `squared_l2` parity; toàn bộ bất biến counter (`distance_evaluations` giảm đúng bằng `duplicate_distance_evaluations` giảm và bằng `already_seen_attempts` tăng) PASS 100%.

### 1.3 Giải thích `arm_difference`, `arm_ci95` và Ý nghĩa Khoa học của Gate B

Theo [AXD_G2_V2_STATISTICAL_DESIGN.md](AXD_G2_V2_STATISTICAL_DESIGN.md) §4 và [g2_v2_design3_analyzer.py](../../../research/task_da/g2_v2_design3_analyzer.py#L182-L197):
- Với từng truy vấn $q \in \{1,\dots,10000\}$ trên cùng panel, tính chênh lệch Recall ghép cặp theo truy vấn giữa hai arm:
  $$d_q = \frac{R_{\text{Fast1},q} + R_{\text{Fast2},q} + R_{\text{Fast3},q}}{3} - \frac{R_{\text{Stock1},q} + R_{\text{Stock2},q} + R_{\text{Stock3},q}}{3}$$
  Việc lấy hiệu **trước rồi mới tính SE** bảo toàn đúng hiệp phương sai (covariance) giữa các đồ thị dùng chung cùng truy vấn, không giả định sai rằng `Stock-r_i` và `Fast-r_i` là cặp random-seed khớp nhau và không thổi phồng cỡ mẫu thành `30,000`.
- **Kết quả replay chính xác:**
  - Mean arm Stock = `0.992050`; Mean arm Fast = `0.992167`.
  - **`arm_difference` ($\bar{d} = \text{Fast} - \text{Stock}$) = `+0.00011667`** (`+0.0117` điểm phần trăm, tương đương chỉ `+0.00117` hit/truy vấn).
  - `SD(d_q) = 0.008544`, `SE(d̄) = 0.00008544`, $t_{0.975,\,9999} = 1.960201$.
  - **`arm_ci95 = [-0.00005081, +0.00028414]`** — nằm **trọn vẹn bên trong** biên tương đương khóa trước **`(-0.0005, +0.0005)`** (dư biên `+0.000449` ở đầu dưới và `+0.000216` ở đầu trên) ⇒ **`B_pass = true`**.
- **Ý nghĩa khoa học chính xác (không phóng đại):**
  1. **Đây là kiểm định tương đương (equivalence test, chặt hơn TOST $\alpha=0.05$ vì dùng CI95 hai phía tức mỗi phía $\alpha=0.025$), KHÔNG phải suy luận sai từ `p > 0.05`.**
  2. Biên `±0.0005` bằng `±5%` ngân sách miss (`1 - 0.990 = 0.010`) tại common `beam = 432`. `B_pass = true` cho phép tuyên bố hai arm Stock và Fast có Recall **tương đương trong biên ±0.0005 trên fixed cohort 6 graph và panel 10k này**, chứ không tuyên bố "chất lượng giống hệt tuyệt đối" hay tổng quát hóa ra quần thể random-root (`independent-root population CI = NOT_ESTIMABLE`).
  3. **Tác động lên quyết định mở OFF:** Gate B PASS mở quyền (nếu owner phê duyệt) sử dụng scope **`OFF_AB`** để đánh giá thêm secondary `BUILD–SEARCH ΔT(Q)` mà không vi phạm điều kiện matched-quality.

---

## 2. Chuẩn bị Giai đoạn Performance OFF (`design-3`)

### 2.1 Điều kiện Mở `OFF_A` vs `OFF_AB`, Thứ tự, Số Tiến trình, Quota & Điểm Quyết định của Owner

Đối chiếu trực tiếp [g2_v2_design3_contract.py](../../../research/task_da/g2_v2_design3_contract.py#L125-L151), [g2_v2_design3_runner.py](../../../research/task_da/g2_v2_design3_runner.py#L219-L251) và [AXD_G2_PREREG_V2.md](AXD_G2_PREREG_V2.md) §5, §9:

| Khía cạnh hợp đồng `design-3` | `scope = "OFF_A"` | `scope = "OFF_AB"` |
|---|---|---|
| Điều kiện Quality Gate bắt buộc | `A_pass == true` & `parity == true` *(đã đạt)* | `A_pass == true`, `parity == true` **và `B_pass == true`** *(cả hai đã đạt)* |
| Điều kiện Qualification & Freeze | Tái sử dụng trực tiếp **`design-3`** (`425c7483...`) + **`QUALIFICATION_PASS 20261124T094602Z`** (`f64b9f9a...`) + **`quality.json`** (`360e1d29...`) | Giống hệt `OFF_A` |
| Số tiến trình & lịch chạy OFF | **Đúng 144 tiến trình OFF** (`12 blocks × 6 graphs × 2 policies`) | **Chính xác cùng 144 tiến trình OFF** *(0 tiến trình bổ sung)* |
| `quota_s` / timeout / preflight | `quota_s = 10800 s` (`3 giờ`), `timeout = 180 s/process`, `preflight >= 15 s/process` | Giống hệt `OFF_A` |
| Phân tích `g2_v2_design3_analyzer.py` | Chỉ đánh giá **Primary Estimand A** (within-graph B1+A1 vs Baseline trên 6 graph); `build_search.status = "NOT_AUTHORIZED_B"` | Đánh giá **Primary Estimand A + Secondary Estimand B** (thêm 4 contrast cross-arm & `BUILD–SEARCH ΔT(Q)` tại `Q = 1, 100k, 1M`) |
| Quyền mở mặc định | **KHÔNG tự mở** — cần owner ký approval mới | **KHÔNG tự mở** — cần owner ký approval mới |

**Đề xuất lựa chọn scope phù hợp với protocol (không mặc định mở 144 OFF):**
- **Lưu ý kiến trúc quan trọng:** Trong frozen `design-3`, runner khóa cứng toàn bộ `12` block cân bằng (`144` OFF) làm một chiến dịch nguyên khối duy nhất — **không** tồn tại pha OFF nhỏ hơn (`< 144`) vì protocol cấm interim efficacy look, early GO hay chạy từng phần rồi nối lại (tạo pha nhỏ sẽ đòi hỏi revision `design-4` mới, trong khi `design-3` không có bất kỳ lỗi nào).
- **Ba lựa chọn minh bạch để owner tự quyết định:**
  1. **Chọn `scope = "OFF_AB"` *(khuyến nghị nếu owner quyết định mở pha OFF)***: tốn **đúng bằng thời gian và số tiến trình của `OFF_A`** (`144` tiến trình, `quota_s = 10800`), nhưng vì `B_pass = true` đã đạt rõ ràng nên tận dụng trọn vẹn cùng bộ dữ liệu OFF cho cả Estimand A và Estimand B (`BUILD–SEARCH ΔT(Q)`).
  2. **Chọn `scope = "OFF_A"` *(phạm vi tuyên bố bảo thủ tối thiểu)***: chạy cùng 144 tiến trình nhưng khóa cứng chỉ kết luận within-graph B1+A1 (`GO_A_FIXED_COHORT / HOLD / PIVOT_TO_TASK_A`), giữ `build_search = NOT_AUTHORIZED_B`.
  3. **Giữ `HOLD` / chưa mở OFF lúc này:** tiếp tục giữ `OFF = NOT_OPEN` nếu chưa có khung thời gian ~2–2,5 giờ liên tục cắm nguồn AC trên `multi-user.target` (toàn bộ bằng chứng `QUALIFICATION_PASS` và `QUALITY_GATE_PASS` vẫn có hiệu lực qua các lần boot miễn giữ kernel `7.0.0-43-generic` và không nâng cấp `glibc`/`libstdc++`/`python3.12`).

### 2.2 Xác minh Kế hoạch Factorial 144 OFF & Phương pháp Đo/Thống kê Đã Khóa

- **Kế hoạch 144 OFF đã đóng băng:** [.local/artifacts/axd-g2-v2-design3-freeze-20261124/off_plan_design3_final.json](../../../.local/artifacts/axd-g2-v2-design3-freeze-20261124/off_plan_design3_final.json) (`SHA-256 = 1bf543150f5d9927a2837be0e0e59e051d9fd2815f48e3f13067a54cc780d95e`), khớp từng byte với `g2_v2_design3_runner.plan(..., "off", ...)`:
  - Factorial đầy đủ `2 arms (Stock/Fast) × 3 graphs/arm × 2 policies (base/opt) × 12 blocks = 144` tiến trình `--mode OFF`, `beam=432`, `p=2`, `CPU [0,2]`, `S=16`, `flat`, `jobs=1`, `warmup=100`, `N=10,000` (`v2_test_10000.ids`).
  - Cân bằng tuyệt đối: trong `12` block, mỗi graph xuất hiện **đúng 2 lần ở mỗi vị trí `0..5`** (`1` lần `base→opt` và `1` lần `opt→base`, tổng **`6 AB / 6 BA`** trên mỗi graph), hai policy của cùng graph luôn chạy **liền kề nhau**.
  - Mọi tiến trình OFF đều kiểm `check_reference()` đối chiếu bit-exact ordered Top-10 & `squared_l2` với đúng `beam_432_p2_ON.jsonl` trong `quality.json`.
- **Phương pháp đo & ngưỡng quyết định đã khóa trong [g2_v2_design3_analyzer.py](../../../research/task_da/g2_v2_design3_analyzer.py):**
  - **Mean / Percentiles / Speedup / CPU / RSS:** `mean_us` = trung bình số học `latency_ns/1000` trên `N=10,000`; `p50/p95/p99` dùng nội suy tuyến tính `q×(N-1)` khớp `p2_eval_summary.json` tới `1e-5` (và `1e-8` trong analyzer); `qps_wall = N / batch_wall_s`; `cpu_percent = 100 × cpu_s / wall_s`, `cpu_capacity_percent = cpu_percent / 2`; `rss_kib = p2_eval_summary.vm_hwm_kib` (integer KiB dương).
  - **Primary Estimand A & Ngưỡng thực dụng tối thiểu `3%`:**
    - $x_{gb} = \log(\text{mean\_base}_{gb} / \text{mean\_opt}_{gb})$, $x_b = \frac{1}{6}\sum_g x_{gb}$, $\theta = -\log(0.97) = 0.03045921$.
    - **`GO_A_FIXED_COHORT`** đòi hỏi đồng thời:
      1. Cận dưới **cả 3 khoảng tin cậy 95%** đều vượt $\theta + 10^{-12}$: `primary_log_ci95` (`12` blocks, $t_{df=11}$), `drift_log_ci95` (`6` cặp block kề nhau, $t_{df=5}$), và `joint_bootstrap` (`10,000` replicates, `query_block = 100`, `seed = 20261123`).
      2. **Ổn định (`stability_pass`):** cả 6 graph có point reduction `> 0`; cả arm Stock và arm Fast đều point reduction `>= 3%`; cả 6 phân tích leave-one-graph-out đều `>= 3%` (kèm `graph_log_ci95` cho từng graph).
      3. **An toàn Tail & RAM (`safety_pass`):** mọi cặp đạt integer hard gate `10(C - B) <= max(655360, B)` (`<= max(64 MiB, 10% B)`), và cả `18` simultaneous upper bounds ($t_{1-0.05/18,\,11}$) + `joint_bootstrap` tail upper95 đều không vượt **`p95 <= +5%`**, **`p99 <= +10%`**, **`RAM <= 1.0`**.
    - **`PIVOT_TO_TASK_A`:** nếu cận trên `primary_log_ci95` **và** cận trên `fast_arm_ci95` đều `< θ - 1e-12`, hoặc tồn tại lower simultaneous bound của `p95`/`p99`/RAM vượt ngân sách.
  - **Paired Foreign-Load Noise Balance (`noise_balance`):** tính `Δforeign = opt - base` trên `12` block × `6` graph cho cả 3 tầng (`all`, `workers`, `ccx0`), `CI95 (df=11)`, tương quan Spearman với `x_gb` và cờ `imbalance_warning` *(chỉ để chẩn đoán, không lọc bỏ lượt chạy và không cứu `HOLD` thành `GO`)*.

### 2.3 Tái sử dụng `design-3` + `QUALIFICATION_PASS` & Dự toán Thời gian / Tài nguyên Pha OFF

- **Không cần `design-4` hay chạy lại qualification:**
  - `verify_qualification()` và `authorize()` xác nhận biên nhận `QUALIFICATION_PASS` (`20261124T094602Z`) tái sử dụng trực tiếp cho pha OFF.
  - Trong toàn bộ 18 lượt Quality ON thực tế trên `multi-user.target` + tắt `cups-browsed`/`Avahi`, nhiễu nền tối đa chỉ là `workers_10s = 0.00500` (`<= 0.01`), `ccx0_10s = 0.00799` (`<= 0.02`), `all_15s = 0.00733` (`<= 0.025`) — chứng minh môi trường vận hành `design-3` có biên an toàn `2.0×–3.4×` dưới ngưỡng nghiêm ngặt của pha OFF.
- **Dự toán thời gian & tài nguyên (mốc lập ngân sách từ 18 ON; KHÔNG phải dự báo tốc độ OFF):**
  - **Preflight pha `off` (`>= 15 s/process`):** `144 × ~15.5 s ≈ 2,232 s` (`~37 phút`).
  - **Thực thi `144` tiến trình OFF:** dùng mốc bảo thủ `35–42 s/process` từ wall-time ON (`39.65–42.75 s`) cho `~5,040–6,048 s` (`~84–101 phút`).
  - **Tổng thời gian thu thập 144 OFF:** ước tính **`~121–138 phút` (`~2.0–2.3 giờ`)**, nằm gọn trong trần cứng **`quota_s = 10800 s` (`3.0 giờ`)** với biên dự phòng `~42–59 phút` *(nhiệt độ đỉnh ON là `85.75°C`, preflight `15 s` ở OFF còn giúp hạ nhiệt tốt hơn `10 s` ở ON)*.
  - **Dung lượng đĩa & RAM:** 18 ON tốn `198 MiB` (`~11 MiB/process`) → 144 OFF (không có `counters` trong JSONL) dự kiến **`~0.9–1.6 GiB`**, rất nhỏ so với **`138.09 GiB` trống** (sàn `25 GiB` đầu phiên / `20 GiB` khi chạy). Peak RSS `~0.83 GiB` / `13.25 GiB` RAM khả dụng.
  - **Hậu kỳ offline (`g2_v2_design3_analyzer.py`):** chạy tách biệt sau khi kết thúc 144 OFF (quota riêng `10800 s`, dự trù `0.5–2 giờ` cho `10,000` bootstrap replicates trên tensor `12×6×2×10,000`).
- **Quy trình an toàn Ubuntu cho pha OFF sau này:** bắt buộc dùng **GRUB boot một lần `systemd.unit=multi-user.target`** (kernel `7.0.0-43-generic`), kiểm tra `gdm.service` = `inactive`, rồi chỉ tạm dừng `cups-browsed.service`, `avahi-daemon.socket`, `avahi-daemon.service` (và tùy chọn `sysstat-collect.timer`, `fwupd-refresh.timer`). **Tuyệt đối không chạy `systemctl stop gdm.service` từ TTY.**

---

## 3. Hướng dẫn Owner Tự Phê duyệt OFF & Kiểm tra Contract (Read-Only, 0 ANN)

Bản nháp chưa ký đã được tạo ngoài frozen package tại:
`../../../../artifact-evidence/axd-g2-v2-approvals/design3_off_approval.DRAFT_UNSIGNED.json`

Gồm `8` trường pinned đã điền đúng SHA (`schema`, `protocol`, `revision`, `freeze_sha256`, `artifacts_sha256`, `qualification_sha256`, `quality_sha256 = 360e1d29...a54c59f`, `output_directory = .../axd-g2-v2-off-design3`) và **5 trường để trống/chưa xác nhận để owner tự quyết định và điền**:
- `owner`: tên/định danh owner thật (vd `"thinhbui"`)
- `approved_at`: ISO-8601 có múi giờ (vd `"2026-11-24T22:45:00+07:00"`)
- `scope`: owner tự chọn **`"OFF_AB"`** *(khuyến nghị nếu mở OFF)* hoặc **`"OFF_A"`**
- `quota_s`: **`10800`** *(3 giờ, cố định cho pha OFF)*
- `quiet_host_confirmed`: **`true`** *(chỉ bật khi xác nhận chạy trên `multi-user.target` + tắt `cups-browsed`/`Avahi` + nguồn AC)*

### Bước 1 — Tạo bản sao & tự điền 5 trường owner (CHỈ KHI owner quyết định mở OFF)
```bash
cp "/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-approvals/design3_off_approval.DRAFT_UNSIGNED.json" \
   "/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-approvals/design3_off_approval.json"
# -> Owner mở design3_off_approval.json và tự điền 5 trường trên.
```

### Bước 2 — Xác minh Receipt OFF bằng Contract Verifier `design-3` (Read-Only, 0 ANN)
```bash
cd "/home/thinhbui/Documents/ChatGPT/Research ANN/task-d"
APPROVAL="/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-approvals/design3_off_approval.json"
QUAL="/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-design3-qualification-20261124T094602Z/qualification_result.json"
QUALITY="/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-quality-design3/quality.json"

env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT \
  /home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python - "$APPROVAL" "$QUAL" "$QUALITY" <<'PY'
import json, sys
from pathlib import Path
from research.task_da.g2_v2_design3_contract import FREEZE, authorize, load_freeze, sha
from research.task_da.g2_v2_design3_runner import quality_context, verify_qualification

approval_path, qual_path, quality_path = map(Path, sys.argv[1:4])
load_freeze(environment=True)
verify_qualification(qual_path)
quality_context(quality_path)
approval = json.loads(approval_path.read_text())
scope = authorize(
    approval,
    sha(FREEZE),
    sha("configs/axd_g2_v2_design3_artifacts.proposed.json"),
    "off",
    "/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-off-design3",
    qualification_digest=sha(qual_path),
    quality_digest=sha(quality_path),
)
print("DESIGN3_OFF_APPROVAL_CHECK=PASS", "scope=", scope, "approval_sha256=", sha(approval_path))
PY
```

---

## 4. Kết luận

- **Official Status:** **`READY_FOR_OFF_OWNER_APPROVAL`**
- **Bước tiếp theo:** Owner xem xét bảng kiểm toán Quality ON và quyết định giữa `OFF_AB`, `OFF_A`, hoặc tiếp tục giữ `OFF = NOT_OPEN`. Chỉ sau khi owner tự tạo và xác minh `design3_off_approval.json` (`DESIGN3_OFF_APPROVAL_CHECK=PASS`) mới chuyển sang bước chuẩn bị thực thi OFF trên `multi-user.target`.
