# Task D × Task A — Pilot Exploratory H1: Graph × Intra-Query Workers (`Recall@10 >= 0.990`)

- **Document Status:** **`EXPLORATORY_HOST_SPECIFIC_PILOT_COMPLETE_R1_ONLY`**
- **Protocol Scope:** [PROTOCOL_V4_1_P2_EXPLORATORY_0990_ADDENDUM.md](PROTOCOL_V4_1_P2_EXPLORATORY_0990_ADDENDUM.md) (`P2-EXP-1..4`, Owner Decision 2026-11-18).
- **Non-Overreach Declaration:** Kết quả trong tài liệu này chỉ là bằng chứng **thăm dò đặc thù phần cứng (`EXPLORATORY_HOST_SPECIFIC`)** tại mục tiêu `Recall@10 >= 0.990`. Tài liệu này **không** mở lại hay chuyển trạng thái `Historical P0 (HOLD)`, `Full P1 Gate (HOLD)`, `t0998 (HOLD)`, `Protocol V4 D1–D5 (UNAPPROVED)`, `P3 Official / Cross-Host Task A QPS (CLOSED)`, hoặc `TP-CG / H3 (NOT_OPENED)`. Các hạt giống đồ thị `R2` và `R3` ở Giai đoạn P2 hiện là **`NOT_RUN`**.

---

## 1. Môi trường thực thi & Điều kiện cố định (`OBSERVED`)

| Tham số | Giá trị thực tế quan sát |
|---|---|
| **Host (`EXPLORATORY_HOST_SPECIFIC`)** | `thinhbui-linux` (`AMD Ryzen 5 PRO 4650U`, `6` physical cores / `12` SMT threads, `2 x 4 MiB` L3 CCX0 `[0..5]` & CCX1 `[6..11]`), `14 GiB` (`MemTotal`), governor `schedutil` *(tách biệt hoàn toàn khỏi target benchmark `i5-14600KF 32 GB RAM`)* |
| **Core Pinning (`lscpu -e`)** | `p=1`: CPU `0` (Core 0, L3 #0); `p=2`: CPUs `0,2` (Core 0–1, cùng L3 #0); `p=4`: CPUs `0,2,4,6` (4 physical cores tách biệt, Core 0–2 trên L3 #0 + Core 3 trên L3 #1, không dùng SMT siblings) |
| **Binary & Engine** | `task_da_p2_eval` (`sha256: e0bddc77...b47c2`), `p2_engine.hpp` (`sync_interval = 8`, persistent `settled_epoch_`, `jobs = 1` liên-truy-vấn, `Mode OFF` thuần timing) |
| **Calibration (Policy 2a, `val_10k` ONLY)** | Hiệu chỉnh độc lập trên trọn vẹn `val_10k.ids` (`10,000` queries, `sha256: a3c948e9...`), ngưỡng `LCB95_q = mean - 1.96 * SE_q >= 0.990`; **không dùng `test_90k`** để chọn beam |
| **Pilot & Warmup Splits** | Warmup cố định `100` queries từ `val_10k` (`warmup_val_100.ids`, `sha256: 199ca606...`); Pilot cố định `3,000` queries trích đều từ `test_90k` (`pilot_test_3000.ids`, `sha256: 18d8b901...`), 0 phần tử trùng |
| **Lặp & Nhiệt độ / RAM quan sát** | `5` process-level interleaved repeats (`rep 0..4`) đảo vòng thứ tự graph và `p`; `acpitz thermal_zone0`: `59.0–84.0 °C`; `MemAvailable`: `>= 8.14 GiB`; Peak RSS `VmHWM`: `~851 MiB` (`A0/A1`), `~798 MiB` (`A3`) |

---

## 2. Kết quả Hiệu chỉnh Beam Policy 2a (`val_10k`, `N = 10,000`)

| Graph | Beam | `p=1` Mean / `LCB95_q` | `p=2` Mean / `LCB95_q` | `p=4` Mean / `LCB95_q` | Quyết định Policy 2a |
|---|---|---|---|---|---|
| **`A0_r1`** | `384` | `0.98996 / 0.98922` (`FAIL`) | `0.99022 / 0.98949` (`FAIL`) | `0.99055 / 0.98984` (`FAIL`) | Dưới ngưỡng `LCB95` |
| **`A0_r1`** | **`416`** | **`0.99114 / 0.99045`** (`PASS`) | **`0.99133 / 0.99065`** (`PASS`) | **`0.99164 / 0.99098`** (`PASS`) | **CHỌN `beam = 416`** |
| **`A1_r1`** | `384` | `0.98987 / 0.98913` (`FAIL`) | `0.99004 / 0.98931` (`FAIL`) | `0.99029 / 0.98957` (`FAIL`) | Dưới ngưỡng `LCB95` |
| **`A1_r1`** | **`416`** | **`0.99099 / 0.99029`** (`PASS`) | **`0.99111 / 0.99042`** (`PASS`) | **`0.99131 / 0.99063`** (`PASS`) | **CHỌN `beam = 416`** |
| **`A3_r1`** | `896` | `0.99019 / 0.98935` (`FAIL`) | `0.99029 / 0.98946` (`FAIL`) | `0.99051 / 0.98971` (`FAIL`) | Dưới ngưỡng `LCB95` |
| **`A3_r1`** | `928` | `0.99060 / 0.98979` (`FAIL`) | `0.99074 / 0.98995` (`FAIL`) | `0.99095 / 0.99018` (`PASS`) | Chưa đạt ở `p=1,2` |
| **`A3_r1`** | **`960`** | **`0.99100 / 0.99021`** (`PASS`) | **`0.99114 / 0.99036`** (`PASS`) | **`0.99130 / 0.99055`** (`PASS`) | **CHỌN `beam = 960`** |

> [!NOTE]
> `beam = 960` cho `A3_r1` không bị gán cứng trước — giá trị này rút trực tiếp từ bước thang 32 trên `val_10k`, nơi `@896` và `@928` đều trượt `LCB95 >= 0.990` ở `p=1,2`. Ngoài ra không thực hiện bất kỳ điều chỉnh beam nào sau khi quan sát `pilot_test_3000`.

---

## 3. Kết quả Pilot H1 (`Mode OFF`, `N = 3,000` queries × `5` interleaved repeats)

| Graph (`beam`) | `p` | `Recall@10` (`N=3000`) | `Mean Lat ± SD` (us) | Median-Run Mean (us) | `p50` (us) | `p95` (us) | QPS (`c=1`) | **Mean Speedup** `[95% CI t_4]` | Median-Run Speedup | Efficiency (`Speedup/p`) |
|---|---|---|---|---|---|---|---|---|---|---|
| **`A0_r1`** (`416`) | `1` | `0.990700` | `5408.88 ± 125.01` | `5353.76` | `5592.74` | `6526.94` | `184.95` | `1.0000` `[1.000, 1.000]` | `1.0000` | `100.0%` |
| **`A0_r1`** (`416`) | `2` | `0.991000` | `3784.30 ± 74.04` | `3806.47` | `3849.72` | `4456.20` | `264.32` | **`1.4296`** `[1.382, 1.477]` | `1.4355` | **`71.5%`** |
| **`A0_r1`** (`416`) | `4` | `0.991300` | `2438.86 ± 63.90` | `2427.64` | `2466.37` | `2830.16` | `410.22` | **`2.2196`** `[2.099, 2.340]` | `2.2002` | **`55.5%`** |
| **`A1_r1`** (`416`) | `1` | `0.990633` | `5502.29 ± 295.85` | `5383.36` | `5648.77` | `6689.23` | `182.13` | `1.0000` `[1.000, 1.000]` | `1.0000` | `100.0%` |
| **`A1_r1`** (`416`) | `2` | `0.990933` | `3737.56 ± 41.29` | `3724.32` | `3826.15` | `4289.75` | `267.57` | **`1.4724`** `[1.369, 1.576]` | `1.4473` | **`73.6%`** |
| **`A1_r1`** (`416`) | `4` | `0.991333` | `2414.04 ± 75.02` | `2418.23` | `2458.40` | `2758.39` | `414.54` | **`2.2809`** `[2.111, 2.451]` | `2.2233` | **`57.0%`** |
| **`A3_r1`** (`960`) | `1` | `0.990233` | `8109.53 ± 81.39` | `8155.24` | `8383.10` | `10137.65` | `123.32` | `1.0000` `[1.000, 1.000]` | `1.0000` | `100.0%` |
| **`A3_r1`** (`960`) | `2` | `0.990267` | `6941.87 ± 515.18` | `6701.79` | `7000.08` | `8445.58` | `144.63` | **`1.1727`** `[1.078, 1.267]` | `1.2040` | **`58.6%`** |
| **`A3_r1`** (`960`) | `4` | `0.990667` | `4339.92 ± 393.18` | `4184.26` | `4371.80` | `5233.41` | `231.77` | **`1.8791`** `[1.697, 2.061]` | `1.9459` | **`47.0%`** |

*(Toàn bộ 9 cấu hình có `incomplete_top_k_queries = 0 / 3000`.)*

---

## 4. Đánh giá giả thuyết H1 & Cảnh báo trung thực

### 4.1 Kết luận thăm dò (`EXPLORATORY`) cho H1
1. **`A3_r1` scaling thấp hơn rõ rệt so với cả `A0_r1` và `A1_r1` trên cùng phần cứng và engine P2:**
   - Tại **`p = 2`**: Speedup trung bình của `A3_r1` chỉ đạt **`1.173x`** (`[1.078, 1.267]`, median `1.204x`), thấp hơn hẳn **`A0_r1` (`1.430x`, `[1.382, 1.477]`)** và **`A1_r1` (`1.472x`, `[1.369, 1.576]`)** — khoảng tin cậy 95% **không giao nhau**, chênh hiệu suất `-12.9pp` đến `-15.0pp`.
   - Tại **`p = 4`**: Speedup trung bình của `A3_r1` đạt **`1.879x`** (`[1.697, 2.061]`, median `1.946x`), vẫn thấp hơn rõ rệt **`A0_r1` (`2.220x`, `[2.099, 2.340]`)** và **`A1_r1` (`2.281x`, `[2.111, 2.451]`)** — khoảng tin cậy 95% **không giao nhau** ở ước lượng mean (median lệch ~`-0.25x` đến `-0.28x`).
2. **Vai trò đối chứng `A1_r1` (`H17`-only control):**
   - `A1_r1` cho kết quả gần như đồng nhất với `A0_r1` ở cả độ trễ cơ sở `p=1` (median `5383.4 us` vs `5353.8 us`) lẫn parallel speedup (`1.447x / 2.223x` vs `1.435x / 2.200x` theo median). Do đó khác biệt `H1` không bắt nguồn từ nhánh `H17` mà gắn trực tiếp với biến đổi cắt tỉa cạnh `C/K` trên `A3` và đòi hỏi `beam = 960` tại `0.990`. (Cơ chế chi tiết xem [H2_WORK_OVERHEAD_PILOT.md](H2_WORK_OVERHEAD_PILOT.md).)

### 4.2 Giới hạn & Cảnh báo bắt buộc (Mandatory Limitations)
1. **Ràng buộc matched-quality `<= 0.0001` trên bước lưới beam 32:**
   - Toàn bộ 9/9 cấu hình đều đạt **`Recall@10 >= 0.990`** (`0.99023` đến `0.99133`). Tuy nhiên vì lưới bước 32 cố định beam theo từng graph, `p=4` đạt recall **cao hơn** `p=1` (`+0.00043` ở `A3`, `+0.00060` ở `A0`, `+0.00070` ở `A1`), nên tiêu chí đối xứng chặt `|ΔRecall| <= 0.0001` không thỏa theo nghĩa chênh lệch tuyệt đối (dù là dịch chuyển **dương / không hy sinh chất lượng**). Giữa `A0@416` (`0.99070`) và `A3@960` (`0.99023`) ở `p=1` cũng có độ lệch `-0.00047`. Không có cấu hình nào bị `Recall < 0.990`, nhưng so sánh `p=4` vs `p=1` nên đọc kèm ghi chú positive recall drift này.
   - Ở cỡ mẫu pilot `N=3,000`, `LCB95_q` trên riêng tập 3,000 nằm từ `0.98868` đến `0.99008` do sai số chuẩn tăng $\sqrt{10000/3000} \approx 1.83\times$ so với `val_10k` (nơi 9/9 cấu hình đã vượt `LCB95_q >= 0.990`).
2. **Dao động nhiệt (`thermal throttling` nhẹ trên laptop `Ryzen 5 PRO 4650U`) & cấu trúc CCX:**
   - `A3_r1 p=2 rep=0` đạt `84.0 °C` cho mean `7845.6 us` trong khi `rep 1..4` (`78–82 °C`) cho `6628–6884 us` (`SD = 515.18 us`); tương tự `A1_r1 p=1 rep=1` chạm `80.0 °C` cho `6030.1 us` vs `5334–5390 us` (`SD = 295.85 us`). Không loại bỏ bất kỳ lần chạy chậm nào; kết luận vẫn giữ nguyên khi xét **median-run** (`A3: 1.204x / 1.946x` vs `A0: 1.435x / 2.200x` vs `A1: 1.447x / 2.223x`).
   - Trên Ryzen 4650U, `p=2` (`0,2`) nằm chung L3 `4 MiB`, còn `p=4` (`0,2,4,6`) bắc qua 2 CCX L3; không ngoại suy trực tiếp con số speedup sang CPU mục tiêu `i5-14600KF`.
3. **Phạm vi hạt giống còn lại:** `R2` và `R3` hiện là **`NOT_RUN`**; các file dữ liệu thô nằm ngoài repo tại `artifact-evidence/p2-exploratory-0990-20261118/pilot_r1/` (`H1_GRAPH_WORKER_SUMMARY.csv`).
