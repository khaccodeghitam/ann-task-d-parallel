# Task D × Task A — Pilot Exploratory H2: Work Inflation, Duplicate Expansions & Sync Breakdown

- **Document Status:** **`EXPLORATORY_HOST_SPECIFIC_DIAGNOSTIC_R1_ONLY`**
- **Protocol Anchor:** [PROTOCOL_V4_1_P2_EXPLORATORY_0990_ADDENDUM.md](PROTOCOL_V4_1_P2_EXPLORATORY_0990_ADDENDUM.md), [counter_schema_p2.json](counter_schema_p2.json), [H1_GRAPH_WORKER_PILOT.md](H1_GRAPH_WORKER_PILOT.md).
- **Non-Overreach Declaration:** Kết quả dưới đây thu từ các lần chạy `Mode ON` **tách riêng hoàn toàn** khỏi các lần chạy timing `Mode OFF` của H1, trên cùng `pilot_test_3000.ids` (`3,000` queries) và `warmup_val_100.ids` tại `thinhbui-linux` (`Ryzen 5 PRO 4650U`). Không thay đổi trạng thái `HOLD / CLOSED / NOT_OPENED` của `P0 / Full P1 / t0998 / P3 / TP-CG`. `R2` và `R3` hiện là **`NOT_RUN`**.

---

## 1. Bảng tổng hợp Counter H2 (`Mode ON`, `N = 3,000`, trung bình / truy vấn)

Tất cả 9/9 cấu hình đều đạt **`ON/OFF exact_ids_match = True`**, **`counter_invariants_pass = True`**, `distance_evaluations == 1 + neighbor_attempts - already_seen_attempts`, và lặp `ON rep0 == ON rep1` xác định tuyệt đối trên mọi bộ đếm thuật toán.

| Graph (`beam`) | `p` | `dist_evals` (`uniq + dup`) | `dup_de_rate` | `expansions` (`uniq + dup`) | **`dup_exp_rate`** | `seen_attempts` | `merges` | `merge_time` (us) | `barrier_wait` (us) | `sync_wait` (us) | `idle` (us) | `imbalance` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **`A0_r1`** (`416`) | `1` | `18192.8` (`18192.8 + 0.0`) | `0.00%` | `419.8` (`419.8 + 0.00`) | `0.00%` | `5807.1` | `0.00` | `0.0` | `0.0` | `0.0` | `0.0` | `1.0000` |
| **`A0_r1`** (`416`) | `2` | `21660.6` (`18390.3 + 3270.3`) | **`15.10%`** | `429.8` (`423.8 + 6.01`) | **`1.40%`** | `2920.3` | `27.23` | `544.5` | `268.0` | `812.1` | `2.2` | `1.0038` |
| **`A0_r1`** (`416`) | `4` | `22614.9` (`18759.7 + 3855.1`) | **`17.05%`** | `449.2` (`431.0 + 18.21`) | **`4.05%`** | `3098.5` | `14.60` | `561.3` | `624.0` | `2304.6` | `17.3` | `1.0120` |
| **`A1_r1`** (`416`) | `1` | `18199.9` (`18199.9 + 0.0`) | `0.00%` | `419.8` (`419.8 + 0.00`) | `0.00%` | `5813.3` | `0.00` | `0.0` | `0.0` | `0.0` | `0.0` | `1.0000` |
| **`A1_r1`** (`416`) | `2` | `21675.6` (`18397.2 + 3278.4`) | **`15.12%`** | `429.9` (`423.8 + 6.11`) | **`1.42%`** | `2924.0` | `27.25` | `538.4` | `267.8` | `805.8` | `2.2` | `1.0038` |
| **`A1_r1`** (`416`) | `4` | `22628.2` (`18771.6 + 3856.6`) | **`17.04%`** | `449.3` (`431.2 + 18.15`) | **`4.04%`** | `3101.4` | `14.61` | `560.6` | `624.2` | `2302.6` | `18.0` | `1.0119` |
| **`A3_r1`** (`960`) | `1` | `25448.9` (`25448.9 + 0.0`) | `0.00%` | `963.6` (`963.6 + 0.00`) | `0.00%` | `10813.0` | `0.00` | `0.0` | `0.0` | `0.0` | `0.0` | `1.0000` |
| **`A3_r1`** (`960`) | `2` | `30501.8` (`25570.2 + 4931.6`) | **`16.17%`** | `974.6` (`967.4 + 7.14`) | **`0.73%`** | `6180.6` | **`61.29`** | **`1346.7`** | `574.1` | `1920.0` | `1.4` | `1.0017` |
| **`A3_r1`** (`960`) | `4` | `31150.9` (`25799.2 + 5351.7`) | **`17.18%`** | `995.0` (`974.3 + 20.70`) | **`2.08%`** | `6321.1` | **`31.68`** | **`1253.0`** | `1229.1` | `4981.5` | `11.8` | `1.0054` |

*(Ghi chú: `barrier_wait` và `sync_wait` là tổng worker-ns trên các worker hoạt động; giá trị trung bình trễ trên critical path là `barrier_wait / p`.)*

---

## 2. Phân rã cơ chế H2: Điều gì giải thích sự khác biệt?

Bằng chứng thực nghiệm tách rõ **hai tầng nhân quả hoàn toàn khác nhau**: (A) **biến thiên giữa các đồ thị (`A0/A1` vs `A3`)** và (B) **biến thiên giữa các truy vấn trong cùng một đồ thị**.

### 2.1 Tại sao `A3_r1` scale kém hơn `A0_r1 / A1_r1`? (So sánh liên đồ thị)

Sử dụng độ trễ median theo từng truy vấn qua 5 repeats `OFF` (`T(1)/p` làm chuẩn lý tưởng, đơn vị `us`):

| Graph (`beam`) | `p` | `T_med(1)/p` (Lý tưởng) | `T_med(p)` (Quan sát) | Phần dư chậm `Excess` | Ước lượng `Dup Work` (`ΔDE/p`) | **`Serial Merge Time`** (`% Excess`) | `Barrier Wait / p` | `Idle / p` | Tổng giải thích (`% Excess`) | Phần dư chưa giải thích |
|---|---|---|---|---|---|---|---|---|---|---|
| **`A0_r1`** (`416`) | `2` | `2667.7` | `3704.8` | `+1037.1` | `508.5` | **`544.5` (`52.5%`)** | `134.0` | `1.1` | `1188.1` (`114.6%`) | `-151.0` |
| **`A0_r1`** (`416`) | `4` | `1333.8` | `2410.1` | `+1076.3` | `324.2` | **`561.3` (`52.2%`)** | `156.0` | `4.3` | `1045.9` (`97.2%`) | `+30.4` |
| **`A1_r1`** (`416`) | `2` | `2673.0` | `3688.7` | `+1015.6` | `510.5` | **`538.4` (`53.0%`)** | `133.9` | `1.1` | `1183.9` (`116.6%`) | `-168.2` |
| **`A1_r1`** (`416`) | `4` | `1336.5` | `2402.1` | `+1065.6` | `325.2` | **`560.6` (`52.6%`)** | `156.0` | `4.5` | `1046.3` (`98.2%`) | `+19.3` |
| **`A3_r1`** (`960`) | `2` | `4003.3` | `6645.9` | **`+2642.6`** | `794.9` | **`1346.7` (`51.0%`)** | `287.0` | `0.7` | `2429.4` (`91.9%`) | `+213.2` |
| **`A3_r1`** (`960`) | `4` | `2001.7` | `4144.2` | **`+2142.5`** | `448.5` | **`1253.0` (`58.5%`)** | `307.3` | `2.9` | `2011.7` (`93.9%`) | `+130.8` |

**Ba phát hiện chính cho khác biệt liên đồ thị:**
1. **`duplicate_expansions` và `workload_imbalance` KHÔNG phải nguyên nhân khiến `A3` tụt speedup:**
   - Tỉ lệ `duplicate_expansions` của `A3_r1` thực tế **thấp hơn một nửa** so với `A0/A1` (`0.73% / 2.08%` vs `1.40% / 4.05%`), tỉ lệ `duplicate_distance_evaluations` xấp xỉ nhau (`16.17%–17.18%` vs `15.10%–17.05%`), `workload_imbalance` dưới `1.2%` ở mọi nhánh (`1.0017–1.0120`), và `worker_idle_ns` không đáng kể (`< 18 us`, phần lớn `< 0.5%` tổng thời gian).
   - Đồng thời, `already_seen_attempts` (`10,813` ở `A3 p=1` giảm xuống `6,181 / 6,321` ở `p=2,4`) và `duplicate_distance_evaluations` (`4,932 / 5,352`) tách biệt rành mạch: cả hai không đồng nhất với `duplicate_expansions` (`7.14 / 20.70` đỉnh).
2. **Thủ phạm chính trong kiến trúc đồng bộ `S=8` là tần suất đồng bộ `sync_merge_count` và chi phí hợp nhất tuần tự (`serial merge_time_ns` + `barrier_wait_ns`):**
   - Do tỉa cạnh `C/K`, `A3` cần **`beam = 960`** (`2.31x` so với `416` trên `A0/A1`) và **`2.30x` số lần expand (`963.6` vs `419.8`)** trong khi trung bình chỉ có ~`37.6` cung/expand (so với `57.2` trên `A0/A1`) -> chỉ tăng `1.40x` số lần tính L2 nhưng phải đi qua **`2.25x` (`61.29` vs `27.23`) số rào chắn hợp nhất ở `p=2`** và **`2.17x` (`31.68` vs `14.60`) ở `p=4`**.
   - Mỗi lần hợp nhất lại chèn/cắt trên `std::set<Hit>` kích thước lớn hơn (`beam = 960` vs `416`), đẩy **`merge_time_ns` lên `1346.7 us` (`p=2`) và `1253.0 us` (`p=4`) — gấp `2.23x–2.47x` so với `A0/A1` (`538–561 us`), tự nó chiếm `51.0%–58.5%` toàn bộ độ trễ chậm dư so với `T(1)/p`**. Tổng các thành phần đo được giải thích **`~91.9%–98.2%`** (tới `114–117%` ở `p=2 A0/A1` khi công thức `ΔDE/p` gán cả chi phí duyệt không phải L2 vào phép tính khoảng cách).
3. **Vai trò kiểm chứng của `A1_r1` (`H17`-only control):**
   - Mọi bộ đếm và tỷ phần phân rã của `A1_r1` đều khớp gần như tuyệt đối với `A0_r1` (`dup_de_rate`: `15.12% / 17.04%` vs `15.10% / 17.05%`; `merge_time`: `538.4 / 560.6 us` vs `544.5 / 561.3 us`; `sync_merge_count`: `27.25 / 14.61` vs `27.23 / 14.60`), chứng minh nhánh `H17` đơn lẻ không gây suy giảm hay thay đổi hành vi H2.

### 2.2 Điều gì giải thích biến thiên Speedup giữa các truy vấn trong cùng đồ thị?

| Graph (`beam`) | `p` | Speedup `p05 / p50 / p95` (per-query OFF median) | **`r(dup_de_rate, speedup)`** | `r(total_expansions, speedup)` | `r(dup_exp, speedup)` | `r(sync_merges, speedup)` | `dup_de_rate` `p05 / p50 / p95` |
|---|---|---|---|---|---|---|---|
| **`A0_r1`** (`416`) | `2` | `1.252x / 1.455x / 1.537x` | **`-0.8756`** | `-0.2050` | `-0.1674` | `-0.1042` | `10.0% / 14.1% / 26.0%` |
| **`A0_r1`** (`416`) | `4` | `1.854x / 2.241x / 2.417x` | **`-0.8078`** | `-0.3252` | `-0.2693` | `-0.1822` | `11.5% / 16.2% / 27.8%` |
| **`A1_r1`** (`416`) | `2` | `1.261x / 1.463x / 1.544x` | **`-0.8678`** | `-0.2075` | `-0.1752` | `-0.1020` | `9.9% / 14.1% / 26.2%` |
| **`A1_r1`** (`416`) | `4` | `1.867x / 2.248x / 2.427x` | **`-0.7955`** | `-0.3001` | `-0.2526` | `-0.1616` | `11.5% / 16.3% / 27.9%` |
| **`A3_r1`** (`960`) | `2` | `0.966x / 1.220x / 1.308x` | **`-0.8967`** | `-0.1681` | `-0.1403` | `-0.1161` | `11.8% / 15.6% / 26.9%` |
| **`A3_r1`** (`960`) | `4` | `1.497x / 1.965x / 2.138x` | **`-0.8491`** | `-0.2315` | `-0.1861` | `-0.1279` | `12.7% / 16.6% / 27.6%` |

- Trong nội bộ **cả 3 đồ thị**, `sync_merge_count` gần như không đổi giữa các truy vấn (`p25–p75` chỉ dao động `0–1` vòng), nên **`duplicate_distance_eval_rate` (`r = -0.80 đến -0.90`, tương ứng $R^2 \approx 63\%\text{–}80\%$)** trở thành yếu tố dự báo mạnh nhất cho phân bố speedup từng truy vấn: ở những truy vấn mà nhiều worker đồng thời va vào cùng vùng dày đặc trong cửa sổ `S=8` (`dup_de_rate p95 ≈ 27%`), speedup tại `A3_r1 p=2` tụt xuống `p05 = 0.966x`.

---

## 3. Tính nhạy thiết kế & Các điểm còn bỏ ngỏ (`INCONCLUSIVE` / Caveats)

1. **Tương tác giữa đồ thị `A3` và thiết kế hợp nhất `std::set` / `S=8` (`Baseline Sensitivity`):**
   - Trong cài đặt baseline P2 hiện tại, hợp nhất tuần tự trên `std::set<Hit>` chiếm hơn phân nửa phần chậm dư (`~51–59%`). Vì vậy kết quả H2 chứng minh **cơ chế chậm của `A3` trên baseline local-frontier + barrier `S=8` này** là tổng hợp của (i) nhu cầu `beam = 960` / nhiều bước expand tạo ra gấp `2.2x` rào chắn đồng bộ, và (ii) chi phí `std::set` merge tỉ lệ thuận với số rào chắn & `beam`. Chưa thể kết luận `A3` sẽ giữ nguyên mức tụt hiệu suất trên một thiết kế khác (ví dụ thay `std::set` bằng flat sorted vector merge hoặc khóa chia sẻ / `shared atomic seen` hoặc bước đồng bộ `S` lớn hơn) — điều này cố ý không chỉnh sau khi xem dữ liệu để giữ nguyên tính bất thiên vị của baseline.
2. **Phần dư và độ xấp xỉ phân rã:**
   - Phép phân rã dùng độ trễ trung bình `Mode OFF` phối hợp với bộ đếm thu trong các lần chạy `Mode ON` riêng biệt; công thức `est_dup_work = T(1) * (ΔDE / DE_1) / p` giả định toàn bộ `T(1)` tỉ lệ tuyến tính với số phép tính L2, gây sai số xấp xỉ `-151` đến `+213 us` (chênh nhẹ âm trên `A0/A1 p=2`). Do đó đây là bằng chứng định lượng thăm dò, **không** phải suy diễn nhân quả hoàn toàn trên phần cứng `i5-14600KF`.
3. **Các bước chưa chạy (`NOT_RUN`):** `R2`, `R3`, chạy trên `i5-14600KF`, kiểm tra với biến thể merge nhẹ hơn hoặc `S != 8`, và toàn bộ `TP-CG / H3` (`NOT_OPENED`).
