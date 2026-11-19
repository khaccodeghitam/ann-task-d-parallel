# Task D × Task A — P2 Follow-Up (Stages A–E), R1/R2/R3 Replication & H3 Decision Report

- **Document Status:** **`STAGE_A_TO_E_COMPLETE_H3_PIVOT`**
- **Protocol Scope:** Exploratory P2 (`Recall@10 >= 0.990`, `--jobs 1`, `workers ∈ {1, 2, 4}`) theo [PROTOCOL_V4_1_P2_EXPLORATORY_0990_ADDENDUM.md](PROTOCOL_V4_1_P2_EXPLORATORY_0990_ADDENDUM.md), [counter_schema_p2.json](counter_schema_p2.json), và [P2_MULTIWALKER_IMPLEMENTATION_STATUS.md](P2_MULTIWALKER_IMPLEMENTATION_STATUS.md).
- **Observed Host:** `thinhbui-linux` (`AMD Ryzen 5 PRO 4650U`, 6 cores / 12 threads, pinned `[0]`, `[0,2]`, `[0,2,4,6]`). **Kết quả mang tính `EXPLORATORY_HOST_SPECIFIC`.**
- **Secondary Host (`i5-14600KF`):** **`NOT_AVAILABLE_ON_THIS_HOST_NOT_RUN`** (không có máy đích trong môi trường chạy; không suy đoán số đo liên máy).
- **External Evidence Root (ngoài git repo):** `../artifact-evidence/p2-followup-20261118/` (`1,777` tệp đã băm SHA-256 trong `EVIDENCE_CHECKSUMS.csv`, tổng `2,491.26 MiB`; `18/18` tệp gốc bất biến `base/query/GT`, `val_10k/test_90k`, `PRE_REGISTRATION.md`, `experiment_manifest.yaml`, `PROTOCOL_V2.md`, `PROTOCOL_V3_P1_ADDENDUM.md`, và 9 đồ thị `A0/A1/A3 × r1..r3` xác minh nguyên vẹn).

> [!IMPORTANT]
> **Preserved Gates & Research Discipline (Không thay đổi):**
> - `Historical P0`: **`HOLD`** | `Full P1 Gate`: **`HOLD`** | `Target 0.998 (t0998)`: **`HOLD`**
> - `Protocol V4 (D1–D5)`: **`UNAPPROVED / PENDING`** | `P3 Official Benchmark`: **`CLOSED`** | `TP-CG / H3`: **`NOT_OPENED`** *(khuyến nghị `PIVOT` ở Mục 6; chưa triển khai TP-CG trong nhiệm vụ này)*.

---

## 1. Giai đoạn A — Evidence Audit (`COMPLETE`)

Kiểm toán đầy đủ toàn bộ evidence pilot tại `../artifact-evidence/p2-exploratory-0990-20261118/` qua script `../artifact-evidence/p2-followup-20261118/stage_a_audit.py` (`stage_a_audit_report.json`):

1. **Checksum & Artifact Integrity:** **`227/227`** tệp trong `EVIDENCE_CHECKSUMS.csv` khớp chính xác cả `bytes` lẫn `SHA-256` (`mismatches = []`).
2. **Protocol & Split Integrity:** Khớp `45` lượt `OFF` (5 repeats interleaved/cell) và `18` lượt `ON` (2 repeats/cell), `workers ∈ {1, 2, 4}`, `sync_interval = 8`, `--jobs 1`, `complete_top_k = 3000`, `100` queries warmup trên `val_10k` tách rời hoàn toàn (`disjoint`) khỏi `3,000` queries pilot từ `test_90k`.
3. **Separator Verification (`duplicate_expansions` vs `already_seen_attempts`):** Xác minh trên `3,000/3,000` queries mỗi lượt `ON` rằng `expansions == unique_expansions + duplicate_expansions` và hoàn toàn tách biệt với `already_seen_attempts`. Ví dụ trên `A3_r1`: ở `p=2`, `duplicate_expansions = 7.14` trong khi `already_seen_attempts = 6180.64`; ở `p=4`, `duplicate_expansions = 20.70` trong khi `already_seen_attempts = 6321.07` (cũng kiểm chứng `ON rep0 == ON rep1` xác định cho mọi counter thuật toán).
4. **Giải thích `reported paired speedup` vs `ratio of aggregate means`:**
   - Pilot ban đầu [H1_GRAPH_WORKER_PILOT.md](H1_GRAPH_WORKER_PILOT.md) báo cáo **mean of paired per-repeat ratios** $\frac{1}{5}\sum_{i=1}^5 (T_{1,i} / T_{p,i})$, cao hơn **ratio of aggregate means** $\bar{T}_1 / \bar{T}_p$ một lượng dương `+0.00026` đến `+0.01052`:

| Graph × Workers | `reported_paired_mean` (`CI95 t4`) | `ratio_of_aggregate_means` (`delta CI95`) | Chênh lệch (`paired - agg`) | Nguyên nhân thống kê & nhiệt |
|---|---:|---:|---:|---|
| `A0_r1 p=2` | `1.4296` `[1.3823, 1.4770]` | `1.4293` `[1.3756, 1.4830]` | `+0.00033` | Bất đẳng thức Jensen ($\mathbb{E}[1/T_p] > 1/\mathbb{E}[T_p]$) |
| `A0_r1 p=4` | `2.2196` `[2.0994, 2.3398]` | `2.2178` `[2.1216, 2.3140]` | `+0.00180` | Jensen + biến thiên rep0..4 |
| `A1_r1 p=2` | `1.4724` `[1.3686, 1.5763]` | `1.4722` `[1.3718, 1.5725]` | `+0.00026` | Jensen nhỏ dù `A1 p=1 rep1` có burst `6030.07 us` |
| `A1_r1 p=4` | `2.2809` `[2.1108, 2.4510]` | `2.2793` `[2.1035, 2.4550]` | `+0.00158` | Tương tự |
| `A3_r1 p=2` | `1.1727` `[1.0781, 1.2672]` | `1.1682` `[1.0596, 1.2768]` | `+0.00446` | Jensen phóng đại bởi điểm ấm `rep0 = 7845.61 us` |
| `A3_r1 p=4` | `1.8791` `[1.6973, 2.0610]` | `1.8686` `[1.6571, 2.0801]` | `+0.01052` | Điểm chậm `rep0 = 5037.18 us` đẩy `ratio_of_agg` xuống mạnh hơn `mean(T1_i/Tp_i)` |

> **Quy tắc báo cáo từ Stage B trở đi:** Luôn báo cáo rõ **`ratio_of_aggregate_means`** làm chỉ số tỷ lệ trung bình tổng thể chính khi tổng hợp giữa replicate, kèm `paired_speedup` để minh bạch ghép cặp trong cùng block repeat.

---

## 2. Giai đoạn B — Strict Matched Recall (`val_10k` ONLY) & So sánh Common Beam vs Matched Recall (`COMPLETE`)

### 2.1 Bất khả thi của step-32 lattice (`|ΔRecall| <= 0.0001`)

Kiểm tra vét cạn toàn bộ bộ ba beam `(b1, b2, b4)` trên lưới step-32 cũ (`beam <= 4096`) với `val_10k.ids` (`stage_b_val10k_fine/matched_recall_frozen_manifest.json`) cho kết quả **`valid_matched_triples_le_0001 = []`** trên cả 3 đồ thị `R1`:

| Graph | Các mức step-32 đạt `LCB95_q >= 0.990` | Bộ ba có khoảng cách nhỏ nhất | `max_gap` | Đạt `<= 0.0001`? |
|---|---|---|---:|---|
| `A0_r1` | `416, 448` (`p=1,2,4`) | `(448, 448, 448)` -> `0.99223 / 0.99237 / 0.99256` | `0.00033` | **KHÔNG** |
| `A1_r1` | `416, 448` (`p=1,2,4`) | `(416, 416, 416)` -> `0.99099 / 0.99124 / 0.99131` | `0.00032` | **KHÔNG** |
| `A3_r1` | `p=1,2: 960..1024`, `p=4: 928..1024` | `(960, 960, 928)` -> `0.99100 / 0.99114 / 0.99095` | `0.00019` | **KHÔNG** |

Không nới ngưỡng: giữ nguyên dung sai `|ΔRecall| <= 0.0001` và chuyển sang hiệu chỉnh lưới tinh **chỉ trên `val_10k`** quanh vùng giao nhau `0.991315 ± 0.00005` (`test_90k` không hề được dùng để retune).

### 2.2 Khóa beam trên `val_10k` & Đối chiếu Common Beam vs Strict Matched Recall (`e0bddc77...`)

Bộ beam khóa trên `val_10k` đạt **`global_9cell_recall_span = 0.000090 <= 0.0001`** (`0.99127 .. 0.99136`, toàn bộ `LCB95_q >= 0.990`). Kết quả chạy lại Pilot H1 (`45 OFF + 18 ON`, `stage_b_h1_off_summary.json`, cùng binary `e0bddc77ffd977c6705cd2b51074e8bcc9ced8e4325e3eb8899d2e4bb51b47c2`):

| Graph × `p` | Common Beam (`beam` / `test3k` / `paired_spd`) | Strict Matched Recall (`val10k_beam` / `val10k_rec` / `test3k` / `mean_us` / `paired_spd` / `agg_spd`) | Nhận xét so sánh |
|---|---|---|---|
| `A0_r1 p=1` | `416` / `0.99070` / `1.0000x` | **`420`** / `0.99129` / `0.99093` / `5515.27 us` / `1.0000x` / `1.0000x` | Tăng `+4` beam cho `p=1` bù hiệu ứng chia biên song song |
| `A0_r1 p=2` | `416` / `0.99100` / `1.4296x` | **`416`** / `0.99133` / `0.99100` / `3721.34 us` / `1.4821x` / `1.4821x` | Loại được overshoot `+0.00030 -> +0.00007` trên test3k |
| `A0_r1 p=4` | `416` / `0.99130` / `2.2196x` | **`408`** / `0.99132` / `0.99100` / `2436.19 us` / `2.2656x` / `2.2639x` | Common beam overshoot `+0.00060`; matched hạ `beam=-8` cho speedup `+0.046x` |
| `A1_r1 p=1` | `416` / `0.99063` / `1.0000x` | **`426`** / `0.99136` / `0.99087` / `5534.46 us` / `1.0000x` / `1.0000x` | Tương tự |
| `A1_r1 p=2` | `416` / `0.99093` / `1.4724x` | **`424`** / `0.99136` / `0.99110` / `3933.74 us` / `1.4073x` / `1.4069x` | Matched giữ khe Recall hẹp hơn |
| `A1_r1 p=4` | `416` / `0.99133` / `2.2809x` | **`416`** / `0.99131` / `0.99133` / `2686.99 us` (`SD=222.57`) / `2.0709x` / `2.0597x` | Bị burst nhiệt trên repeat ấm (`SD=222.57 us`), động lực cần mở rộng Stage D `n=3` |
| `A3_r1 p=1` | `960` / `0.99023` / `1.0000x` | **`976`** / `0.99127` / `0.99040` / `8211.65 us` / `1.0000x` / `1.0000x` | Dịch chuyển `val->test` `~-0.00087` (không retune trên test) |
| `A3_r1 p=2` | `960` / `0.99027` / `1.1727x` | **`970`** / `0.99130` / `0.99037` / `6951.11 us` / `1.1818x` / `1.1813x` | Cân bằng nội tại chặt hơn (`0.99040` vs `0.99037`) |
| `A3_r1 p=4` | `960` / `0.99067` / `1.8791x` | **`960`** / `0.99130` / `0.99067` / `4232.28 us` / `1.9422x` / `1.9402x` | Matched tăng khoảng cách `p=4` lên `1.94x` nhờ `p=1` nâng lên `976` |

- **Khác biệt câu hỏi nghiên cứu:** **Common Beam** trả lời *"tại cùng tham số `beam`, `p=2,4` thay đổi hành vi duyệt và Recall ra sao?"* (cho Recall tự tăng `+0.0004..+0.0007` theo `p`). **Strict Matched Recall** trả lời *"tại cùng mức chất lượng `Recall@10` đã hiệu chỉnh trước trên `val_10k`, `p=2,4` đem lại bao nhiêu parallel speedup thuần túy?"*

---

## 3. Giai đoạn C — H2 Controlled Ablations (`A0-R1`, `A3-R1`, `COMPLETE`)

### 3.1 Giai đoạn C1: Quét `sync_interval ∈ {4, 8, 16, 32}` giữ nguyên `std::set` (`22` nhánh)

Thực hiện qua `stage_c_sync_val10k.py` và `stage_c_sync_ablation.py` (`stage_c_sync_ablation_summary.json`, mỗi nhánh `5 OFF + 1 ON`):

- **Phát hiện 1 — `S` làm trôi Recall dương nếu cố định beam:** Trên `val_10k`, khi tăng `S = 4 -> 8 -> 16 -> 32` ở cùng beam: `A0_r1 p=4@408` tăng `0.99122 -> 0.99132 -> 0.99141 -> 0.99163`; `A3_r1 p=4@960` tăng `0.99122 -> 0.99130 -> 0.99132 -> 0.99144`. Vì vậy mọi nhánh ở bảng dưới có beam hiệu chỉnh trên `val_10k`, kèm nhánh đối chứng `_fix` giữ nguyên beam của `S=8` để tách tác dụng giảm sync vs tác dụng giảm beam:

| Arm (`std::set`) | `beam` | `test3k` | `mean_us` | `agg_spd` | `merges` | `merge_us` | `bar_us` | `dup_exp` | `dup_de` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `A0_r1 p=1` (`S=8`) | `420` | `0.99093` | `5528.44` | `1.0000x` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` |
| `A0_r1 p=2 S=4` | `416` | `0.99090` | `3996.19` | `1.3834x` | `53.5` | `641.0` | `343.5` | `2.2` | `3197.3` |
| `A0_r1 p=2 S=8` | `416` | `0.99100` | `3759.13` | `1.4707x` | `27.2` | `541.9` | `259.6` | `6.0` | `3270.3` |
| `A0_r1 p=2 S=16` | `412` | `0.99087` | `3677.31` | **`1.5034x`** | `14.1` | `473.4` | `220.1` | `16.0` | `3560.3` |
| `A0_r1 p=2 S=32` (`S32_fix=416`) | `412` (`416`) | `0.99097` (`0.99120`) | `3714.45` (`3880.86`) | `1.4884x` (`1.4245x`) | `7.9` | `471.3` (`480.8`) | `194.1` (`195.0`) | `40.0` | `4544.1` |
| `A0_r1 p=4 S=4` | `408` | `0.99090` | `2673.53` | `2.0678x` | `27.2` | `647.6` | `881.0` | `6.6` | `3320.0` |
| `A0_r1 p=4 S=8` | `408` | `0.99100` | `2684.33` | `2.0595x` | `14.3` | `562.7` | `693.2` | `18.1` | `3774.5` |
| `A0_r1 p=4 S=16` | `400` | `0.99083` | `2601.73` | **`2.1249x`** | `8.0` | `547.6` | `616.2` | `51.3` | `5128.8` |
| `A0_r1 p=4 S=32` (`S32_fix=408`) | `396` (`408`) | `0.99107` (`0.99147`) | `2935.10` (`2969.03`) | `1.8836x` (`1.8620x`) | `5.0` | `586.2` (`612.3`) | `666.7` (`712.0`) | `129.6` | `8735.4` |
| `A3_r1 p=1` (`S=8`) | `976` | `0.99040` | `8314.19` | `1.0000x` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` |
| `A3_r1 p=2 S=4` | `974` | `0.99047` | `8131.81` | `1.0224x` | `123.2` | `1795.9` | `835.3` | `2.6` | `4971.7` |
| `A3_r1 p=2 S=8` | `970` | `0.99037` | `6894.94` | `1.2058x` | `62.0` | `1372.4` | `576.9` | `7.2` | `4993.6` |
| `A3_r1 p=2 S=16` | **`970`** | `0.99037` | `6190.16` | **`1.3431x`** | `31.6` | `1129.8` | `452.0` | `17.2` | `5152.0` |
| `A3_r1 p=2 S=32` (`S32_fix=970`) | `966` (`970`) | `0.99040` (`0.99043`) | `6038.44` (`6180.94`) | `1.3769x` (`1.3451x`) | `16.3` | `1020.8` (`989.1`) | `384.6` (`368.5`) | `41.9` | `5618.0` |
| `A3_r1 p=4 S=4` | `960` | `0.99060` | `4684.80` | `1.7747x` | `61.8` | `1491.8` | `1680.4` | `7.6` | `5044.5` |
| `A3_r1 p=4 S=8` | `960` | `0.99067` | `4381.31` | `1.8977x` | `31.7` | `1244.8` | `1232.9` | `20.7` | `5351.7` |
| `A3_r1 p=4 S=16` | **`960`** | `0.99070` | `4209.03` | **`1.9753x`** | `16.7` | `1135.8` | `1108.4` | `54.1` | `6213.8` |
| `A3_r1 p=4 S=32` (`S32_fix=960`) | `948` (`960`) | `0.99057` (`0.99080`) | `4525.33` (`4531.98`) | `1.8373x` (`1.8346x`) | `9.1` | `1165.0` (`1243.5`) | `970.5` (`1202.6`) | `134.8` | `8369.6` |

- **Kết luận Stage C1:** Trên `A3_r1 p=2`, giảm tần suất đồng bộ `S=4->8->16` giữ **nguyên beam `970`** mà vẫn tăng speedup `1.0224x -> 1.2058x -> 1.3431x` do `merges` giảm nửa (`62.0 -> 31.6`). Nhưng với **`std::set` RB-tree**, `merge_us` trên `A3_r1` đụng sàn cứng **`~1136–1244 us`** ở `p=4`, còn `S=32` làm `dup_exp` vọt lên `129.6` (`A0`) / `134.8` (`A3`), đảo chiều làm chậm cả hai đồ thị.

### 3.2 Giai đoạn C2: Triển khai & kiểm chứng `--merge-impl set|flat` (`22` nhánh, binary `ff46d6ac...`)

Sau khi C1 xác nhận cấu trúc `std::set` trong `worker 0` là điểm nghẽn chính, triển khai `MergeImpl::kFlat` (`--merge-impl set|flat`, mặc định giữ nguyên `set`) trong [p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp) và [p2_eval.cpp](../../../research/task_da/search_common/p2_eval.cpp) thay `std::set` toàn cục bằng buffer `std::vector<Hit>` sắp xếp/gộp tuyến tính theo đúng quan hệ thứ tự `(squared_l2, id)`:

- **Correctness Parity Gate (bắt buộc trước khi đo benchmark):**
  - Binary Release `task_da_p2_eval`: `SHA-256 = ff46d6ac8895d519054548575c3187544716c0fdf2bbdad83db8a0a8cc7f8759`, 0 compiler warnings.
  - Release CTest `24/24 OK` (`tests/research/test_task_da.py` gồm unit test `set == flat` từng bit và từ chối flag không hợp lệ); `ASan+UBSan+LSan` CTest `24/24 OK`; `14/14` cặp kiểm chứng đồ thị thực (`smoke_500` `A0/A3 × p={1,2,4} × S={4,8,16}`) và `ASan 100q A3_r1 p=4 flat` đều đạt **bit-identical `ids`, `squared_l2`, và toàn bộ counter thuật toán**.
- **Controlled Ablation `set` vs `flat` trên cùng binary `ff46d6ac...` (`stage_c_merge_ablation_summary.json`):**

| Graph × `p` × `S` (`beam`) | `set`: `mean_us` / `agg_spd` / `merge_us` | `flat`: `mean_us` / `agg_spd` / `merge_us` | Thay đổi (`flat - set`) | Ghi chú parity |
|---|---:|---:|---:|---|
| `A0_r1 p=2 S=8 (B=416)` | `3827.77` / `1.4176x` / `545.9` | `3577.11` / **`1.5169x`** / `352.4` | **`+0.0993x`** (`-193.5 us` merge) | `test3k=0.99100` y hệt |
| `A0_r1 p=2 S=16 (B=412)` | `3644.27` / `1.4889x` / `476.3` | `3519.83` / **`1.5416x`** / `341.2` | **`+0.0527x`** (`-135.1 us` merge) | `test3k=0.99087` y hệt |
| `A0_r1 p=4 S=8 (B=408)` | `2313.08` / `2.3458x` / `536.3` | `2173.27` / **`2.4967x`** / `405.5` | **`+0.1509x`** (`-130.8 us` merge) | `test3k=0.99100` y hệt |
| `A0_r1 p=4 S=16 (B=400)` | `2414.49` / `2.2473x` / `526.0` | `2374.35` / `2.2853x` / `473.9` | `+0.0380x` (`-52.1 us` merge) | `test3k=0.99083` y hệt |
| `A3_r1 p=2 S=8 (B=970)` | `6780.47` / `1.2094x` / `1351.8` | `6190.13` / `1.3247x` / `718.2` | **`+0.1153x`** (`-633.6 us` merge) | `test3k=0.99037` y hệt |
| `A3_r1 p=2 S=16 (B=970)` | `6174.36` / `1.3281x` / `1118.0` | `5723.08` / **`1.4328x`** / `625.7` | **`+0.1047x`** (`-492.3 us` merge) | `test3k=0.99037` y hệt |
| `A3_r1 p=4 S=8 (B=960)` | `4101.14` / `1.9994x` / `1239.4` | `3584.69` / `2.2875x` / `709.9` | **`+0.2881x`** (`-529.5 us` merge) | `test3k=0.99067` y hệt |
| `A3_r1 p=4 S=16 (B=960)` | `4102.32` / `1.9989x` / `1138.6` | `3514.83` / **`2.3330x`** / `707.8` | **`+0.3341x`** (`-430.8 us` merge) | `test3k=0.99070` y hệt |

*(Tham chiếu baseline `p=1` cùng lượt C2: `A0_r1 = 5426.09 us`, `A3_r1 = 8200.00 us`. Ngoài ra `S=4 flat`: `A0 p=2 = 1.4697x`, `A0 p=4 = 2.4992x`, `A3 p=2 = 1.1429x`, `A3 p=4 = 2.1183x`.)*

---

## 4. Giai đoạn D — Replication trên `A0/A1/A3 × R1/R2/R3 × p={1,2,4}` (`COMPLETE`, binary thống nhất `ff46d6ac...`)

Để loại hoàn toàn sai lệch ghép giữa hai bản binary, toàn bộ Giai đoạn D chạy mới hoàn toàn 100% trên binary thống nhất `ff46d6ac8895d519054548575c3187544716c0fdf2bbdad83db8a0a8cc7f8759` (`git_head = b0a95f4d4a8c0a5e9d100caa18c57ef448fe8251`).

### 4.1 Hiệu chỉnh 45 ô trên `val_10k` (`stage_d_val10k_45cells_manifest.json`)

- Toàn bộ `45` ô `(graph ∈ A0/A1/A3 × R1/R2/R3, S ∈ {8,16}, p ∈ {1,2,4})` đạt Recall trên `val_10k` trong khoảng **`[0.99127, 0.99136]`** (**`global_recall_span = 0.000090 <= 0.0001`**, `45/45` đạt `LCB95_q >= 0.990`, `test_90k` tuyệt đối không chạm khi hiệu chỉnh):

| Graph | `S=8` (`p=1 / p=2 / p=4` beam & `val10k`) | `S=16` (`p=2 / p=4` beam & `val10k`) |
|---|---|---|
| `A0_r1` | `420 (0.99129) / 416 (0.99133) / 408 (0.99132)` | `412 (0.99127) / 402 (0.99127)` |
| `A0_r2` | `426 (0.99133) / 422 (0.99132) / 414 (0.99130)` | `420 (0.99133) / 412 (0.99133)` |
| `A0_r3` | `422 (0.99132) / 418 (0.99130) / 410 (0.99129)` | `418 (0.99135) / 410 (0.99135)` |
| `A1_r1` | `426 (0.99136) / 424 (0.99136) / 416 (0.99131)` | `419 (0.99132) / 412 (0.99127)` |
| `A1_r2` | `422 (0.99131) / 416 (0.99129) / 412 (0.99136)` | `416 (0.99132) / 404 (0.99127)` |
| `A1_r3` | `424 (0.99127) / 422 (0.99128) / 416 (0.99133)` | `421 (0.99128) / 412 (0.99133)` |
| `A3_r1` | `976 (0.99127) / 970 (0.99130) / 960 (0.99130)` | `970 (0.99131) / 960 (0.99132)` |
| `A3_r2` | `988 (0.99127) / 990 (0.99135) / 980 (0.99132)` | `986 (0.99132) / 976 (0.99127)` |
| `A3_r3` | `976 (0.99128) / 966 (0.99130) / 952 (0.99136)` | `966 (0.99134) / 944 (0.99129)` |

### 4.2 Ma trận Replication `63` ô × (`5 OFF` + `1 ON` = `378` lượt)

- Toàn vẹn kỹ thuật từ `../artifact-evidence/p2-followup-20261118/stage_d_replication/stage_d_replication_summary.json` & `STAGE_D_REPLICATION_SUMMARY.csv`:
  - **`63/63`** kiểm tra parity `ON vs OFF` và counter invariants **`PASS`**; **`0`** `incomplete_top_k`.
  - Chất lượng trên `3,000` test queries độc lập giữ vững sàn: `test3k_recall` **`[0.990367, 0.991333]`**, **`63/63 >= 0.990`**.

#### Bảng 1 — Tổng hợp Outer Replicate (`n = 3` seeds `R1, R2, R3`, Student-$t_{df=2}$ 95% CI)

| Arm | Config | `lat_us` (`mean ± sd`) | `agg_speedup` (`mean [CI95 t2]`) | Seed `R1 / R2 / R3` | `eff` | `test3k_rec` | `merge_us` | `bar_us` | `dup_exp` | `dup_de` |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| **`A0`** | `p1_base` | `5489.0 ± 25.9` | `1.0000` | `1.0 / 1.0 / 1.0` | `1.000` | `0.99086 ± 0.00016` | `0.0` | `0.0` | `0.0` | `0.0` |
| **`A0`** | `p2_S8_set` | `3781.4 ± 80.9` | `1.4520 [1.3838, 1.5201]` | `1.4596 / 1.4215 / 1.4747` | `0.726` | `0.99096 ± 0.00014` | `543.3` | `259.0` | `6.0` | `3298.5` |
| **`A0`** | `p2_S8_flat` | `3605.2 ± 36.2` | `1.5227 [1.4693, 1.5760]` | `1.5025 / 1.5453 / 1.5202` | `0.761` | `0.99096 ± 0.00014` | `354.4` | `261.5` | `6.0` | `3298.5` |
| **`A0`** | **`p2_S16_flat`** | `3545.4 ± 61.2` | **`1.5484 [1.4959, 1.6010]`** | `1.5615 / 1.5241 / 1.5598` | `0.774` | `0.99093 ± 0.00012` | `346.3` | `215.9` | `16.1` | `3611.4` |
| **`A0`** | `p4_S8_set` | `2403.4 ± 26.6` | `2.2840 [2.2418, 2.3261]` | `2.2988 / 2.2877 / 2.2655` | `0.571` | `0.99110 ± 0.00012` | `558.5` | `637.7` | `18.2` | `3804.4` |
| **`A0`** | **`p4_S8_flat`** | `2279.0 ± 17.8` | **`2.4086 [2.3799, 2.4372]`** | `2.4150 / 2.4155 / 2.3952` | **`0.602`** | `0.99110 ± 0.00012` | `406.6` | `577.7` | `18.2` | `3804.4` |
| **`A0`** | `p4_S16_flat` | `2466.6 ± 24.0` | `2.2254 [2.1929, 2.2580]` | `2.2374 / 2.2275 / 2.2114` | `0.556` | `0.99113 ± 0.00015` | `485.9` | `682.2` | `51.4` | `5222.1` |
| **`A1`** | `p1_base` | `5534.5 ± 63.1` | `1.0000` | `1.0 / 1.0 / 1.0` | `1.000` | `0.99081 ± 0.00016` | `0.0` | `0.0` | `0.0` | `0.0` |
| **`A1`** | `p2_S8_set` | `3822.7 ± 77.6` | `1.4480 [1.4034, 1.4926]` | `1.4648 / 1.4502 / 1.4291` | `0.724` | `0.99097 ± 0.00013` | `556.5` | `266.8` | `6.1` | `3321.5` |
| **`A1`** | **`p2_S8_flat`** | `3563.1 ± 40.9` | **`1.5533 [1.5442, 1.5624]`** | `1.5492 / 1.5544 / 1.5563` | **`0.777`** | `0.99097 ± 0.00013` | `352.7` | `258.2` | `6.1` | `3321.5` |
| **`A1`** | `p2_S16_flat` | `3578.7 ± 61.0` | `1.5467 [1.5054, 1.5879]` | `1.5646 / 1.5435 / 1.5319` | `0.773` | `0.99106 ± 0.00008` | `360.0` | `255.8` | `16.1` | `3632.2` |
| **`A1`** | `p4_S8_set` | `2441.9 ± 31.7` | `2.2668 [2.1572, 2.3765]` | `2.3064 / 2.2193 / 2.2748` | `0.567` | `0.99122 ± 0.00012` | `546.3` | `573.5` | `18.2` | `3842.6` |
| **`A1`** | **`p4_S8_flat`** | `2345.1 ± 98.1` | **`2.3634 [2.0591, 2.6677]`** | `2.4127 / 2.2239* / 2.4536` | **`0.591`** | `0.99122 ± 0.00012` | `420.5` | `694.2` | `18.2` | `3842.6` |
| **`A1`** | `p4_S16_flat` | `2494.7 ± 15.0` | `2.2186 [2.1294, 2.3079]` | `2.2367 / 2.1773 / 2.2419` | `0.555` | `0.99116 ± 0.00020` | `476.3` | `567.4` | `51.5` | `5239.3` |
| **`A3`** | `p1_base` | `8214.2 ± 42.9` | `1.0000` | `1.0 / 1.0 / 1.0` | `1.000` | `0.99051 ± 0.00022` | `0.0` | `0.0` | `0.0` | `0.0` |
| **`A3`** | `p2_S8_set` | `6847.6 ± 143.2` | `1.1998 [1.1524, 1.2473]` | `1.2036 / 1.1791 / 1.2168` | `0.600` | `0.99046 ± 0.00015` | `1391.3` | `581.0` | `7.1` | `5026.2` |
| **`A3`** | `p2_S8_flat` | `6168.4 ± 72.4` | `1.3317 [1.3047, 1.3587]` | `1.3443 / 1.3260 / 1.3249` | `0.666` | `0.99046 ± 0.00015` | `727.9` | `571.2` | `7.1` | `5026.2` |
| **`A3`** | **`p2_S16_flat`** | `5741.3 ± 109.3` | **`1.4310 [1.3807, 1.4813]`** | `1.4512 / 1.4107 / 1.4310` | **`0.715`** | `0.99049 ± 0.00018` | `645.8` | `460.3` | `17.1` | `5176.8` |
| **`A3`** | `p4_S8_set` | `4181.2 ± 59.7` | `1.9648 [1.9108, 2.0187]` | `1.9538 / 1.9507 / 1.9898` | `0.491` | `0.99064 ± 0.00007` | `1237.0` | `1198.7` | `20.8` | `5379.6` |
| **`A3`** | `p4_S8_flat` | `3630.7 ± 75.5` | `2.2630 [2.1634, 2.3626]` | `2.3092 / 2.2414 / 2.2383` | `0.566` | `0.99064 ± 0.00007` | `709.0` | `1223.4` | `20.8` | `5379.6` |
| **`A3`** | **`p4_S16_flat`** | `3596.7 ± 59.7` | **`2.2841 [2.2176, 2.3506]`** | `2.2881 / 2.2556 / 2.3087` | **`0.571`** | `0.99063 ± 0.00009` | `718.7` | `1039.4` | `54.2` | `6219.8` |

*\*Ghi chú trung thực về `A1_r2 p4_S8_flat`: `mean = 2457.68 us` (`stdev = 200.92 us`, 5 repeats = `2546.14, 2272.74, 2725.31, 2243.31, 2500.91 us`) do xung nhiệt laptop ở một số repeats, làm speedup tại seed `r2` là `2.2239x` trong khi `r1 = 2.4127x`, `r3 = 2.4536x`. Toàn bộ 5 lượt được giữ nguyên tuyệt đối theo `AGENTS.md` (không loại bỏ slow run).*

#### Bảng 2 — Contrasts ghép cặp theo Seed đồ thị (`n = 3`, Student-$t_{df=2}$ 95% CI)

| Contrast nhóm đồ thị / Ablation | `A0 - A3` (hoặc `flat - set`) | `A1 - A3` (hoặc `S16 - S8 @ flat`) | `A0 - A1` |
|---|---|---|---|
| **`p2_S8_set`** (baseline) | **`+0.2521`** `[+0.2310, +0.2732]` | **`+0.2482`** `[+0.1699, +0.3264]` | `+0.0039` `[-0.0905, +0.0983]` |
| **`p2_S8_flat`** | **`+0.1909`** `[+0.1147, +0.2672]` | **`+0.2216`** `[+0.1856, +0.2575]` | `-0.0306` `[-0.0786, +0.0174]` |
| **`p2_S16_flat`** | **`+0.1175`** `[+0.0929, +0.1421]` | **`+0.1157`** `[+0.0757, +0.1556]` | `+0.0018` `[-0.0579, +0.0615]` |
| **`p4_S8_set`** (baseline) | **`+0.3192`** `[+0.2250, +0.4134]` | **`+0.3021`** `[+0.1913, +0.4128]` | `+0.0171` `[-0.0932, +0.1275]` |
| **`p4_S8_flat`** | **`+0.1456`** `[+0.0573, +0.2339]` | `+0.1004` `[-0.1888, +0.3896]` | `+0.0451` `[-0.2786, +0.3689]` |
| **`p4_S16_flat`** *(dưới tối ưu của A0/A1)* | `-0.0587` `[-0.1462, +0.0289]` | `-0.0655` `[-0.0990, -0.0320]` | `+0.0068` `[-0.0943, +0.1079]` |
| **Best-fixed-per-arm `p=4`**: `A0(S8_flat) - A3(S16_flat)` | **`+0.1244`** `[+0.0333, +0.2156]` | `A1(S8_flat)-A3(S16_flat): +0.0793` `[-0.1607, +0.3193]` | — |
| **Ablation `A0` (`p=2` / `p=4`)** | `flat-set@S8`: `+0.0707 [-0.0434,+0.1849]` / **`+0.1246 [+0.1064,+0.1428]`** | `S16-S8@flat`: `+0.0258 [-0.0781,+0.1297]` / **`-0.1831 [-0.1961,-0.1701]`** | — |
| **Ablation `A1` (`p=2` / `p=4`)** | `flat-set@S8`: **`+0.1053 [+0.0520,+0.1585]`** / `+0.0966 [-0.1207,+0.3139]` | `S16-S8@flat`: `-0.0066 [-0.0570,+0.0437]` / `-0.1448 [-0.3604,+0.0709]` | — |
| **Ablation `A3` (`p=2` / `p=4`)** | `flat-set@S8`: **`+0.1319 [+0.0801,+0.1837]`** / **`+0.2982 [+0.1644,+0.4320]`** | `S16-S8@flat`: **`+0.0992 [+0.0679,+0.1306]`** / `+0.0211 [-0.0935,+0.1357]` | — |

#### Bảng 3 — Phân rã Excess Latency (`stage_d_decomposition.json`, `n=3`)

Định nghĩa: $\text{ideal} = T_1 / p$, $\text{excess} = T_p - \text{ideal}$, `dup = (T1 * ((dep - de1)/de1)) / p`, `merge = merge_time_ns * 1e-3`, `bar/p = (barrier_wait_ns * 1e-3) / p`, `idle/p = (worker_idle_ns * 1e-3) / p`:

| Arm × Config | `T1 (us)` | `Tp (us)` | `excess (us)` | `merge (us / %Tp / %exc)` | `dup (us)` | `bar/p (us)` | `idle/p (us)` | `res (us)` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `A0 p2_S8_set` | `5489.0` | `3781.4` | `1036.9` | `543.3` (`14.4% / 52.4%`) | `495.7` | `129.5` | `1.5` | `-133.1` |
| `A0 p2_S16_flat` | `5489.0` | `3545.4` | `800.9` | `346.3` (`9.8% / 43.2%`) | `541.9` | `107.9` | `0.8` | `-196.0` |
| `A0 p4_S8_set` | `5489.0` | `2403.4` | `1031.2` | `558.5` (`23.2% / 54.2%`) | `290.4` | `159.4` | `3.4` | `+19.4` |
| **`A0 p4_S8_flat`** | `5489.0` | `2279.0` | `906.8` | **`406.6` (`17.8% / 44.8%`)** | **`290.4`** | **`144.4`** | `3.4` | `+61.9` |
| `A1 p4_S8_flat` | `5534.5` | `2345.1` | `961.5` | `420.5` (`17.9% / 43.7%`) | `302.5` | `173.6` | `4.2` | `+60.7` |
| `A3 p2_S8_set` | `8214.2` | `6847.6` | `2740.5` | `1391.3` (`20.3% / 50.8%`) | `797.5` | `290.5` | `0.8` | `+260.3` |
| `A3 p2_S16_flat` | `8214.2` | `5741.3` | `1634.2` | `645.8` (`11.2% / 39.5%`) | `822.7` | `230.1` | `0.7` | `-65.1` |
| `A3 p4_S8_set` | `8214.2` | `4181.2` | `2127.6` | `1237.0` (`29.6% / 58.1%`) | `424.5` | `299.7` | `2.3` | `+164.2` |
| **`A3 p4_S8_flat`** | `8214.2` | `3630.7` | `1577.1` | **`709.0` (`19.5% / 45.0%`)** | `424.5` | `305.9` | `2.3` | `+135.5` |
| **`A3 p4_S16_flat`** | `8214.2` | `3596.7` | `1543.1` | **`718.7` (`20.0% / 46.6%`)** | **`489.2`** | **`259.9`** | `1.8` | `+73.6` |

*(Ghi chú mô hình: ở `p=2`, công thức tuyến tính `dup` nhân thêm L2 evals với đơn giá `T1/de1` không tính đến khấu hao cache/batch khi nhiều neighbor dùng chung tải DRAM hoặc chồng lấp nhẹ với phần khác, khiến tổng cộng từng phần vượt `excess` [`acc = 104%–128%`, `res < 0`]; còn ở `p=4`, `acc = 91.4%–98.1%` để lại một phần dư dương nhỏ `+19.4..+164.2 us` từ overhead đánh thức barrier/cạnh tranh bộ nhớ dùng chung.)*

---

## 5. Tổng hợp Kết luận Thực nghiệm cho H1 & H2

1. **Xác nhận H1 có tái lập trên `R1/R2/R3`:**
   - **`A0` vs `A1` đồng nhất về hiệu năng song song:** `A0 - A1` có CI95 cắt `0` trên mọi cấu hình `p=2,4` (`-0.0306` đến `+0.0451`).
   - **`A3` có parallel speedup thấp hơn nhất quán so với `A0/A1` ở baseline `S8_set`:** `A0 - A3 = +0.2521x [+0.2310, +0.2732]` (`p=2`) và `+0.3192x [+0.2250, +0.4134]` (`p=4`); `A1 - A3` gần tương đương (`+0.2482x`, `+0.3021x`).
   - **Tác động đồ thị tồn dư sau khi tối ưu triển khai (`flat` + best static `S`):** Khoảng cách `A0 - A3` thu hẹp hơn một nửa nhưng **không biến mất**: ở `p=2`, ngay tại cấu hình tốt nhất `S16_flat` của `A3`, `A0 - A3 = +0.1175x [+0.0929, +0.1421]` (`1.5484x` vs `1.4310x`); ở `p=4`, so sánh tối ưu tĩnh riêng từng đồ thị **`A0(S8_flat) - A3(S16_flat) = +0.1244x [+0.0333, +0.2156]`** (`2.4086x` vs `2.2841x`, `A3` đạt `94.8%` speedup của `A0`). Đồng thời **`S` tối ưu phụ thuộc đồ thị**: trên `p=4`, `S16` làm `A0` chậm mạnh (`-0.1831x [-0.1961, -0.1701]`) vì phình `dup_de` (`3804 -> 5222`), trong khi trên `A3`, `S=16` giữ ngang/nhỉnh hơn `S=8` (`+0.0211x`, và `+0.0992x [+0.0679, +0.1306]` ở `p=2`) nhờ cắt giảm gần nửa số lần đồng bộ trên beam ~`960–980`.
2. **Giải thích H2 — Tách bạch Chi phí Đồ thị vs Chi phí Triển khai:**
   - **~48–60% mức hụt ban đầu của `A3` là lỗi cấu trúc dữ liệu (`std::set` RB-tree) + `S=8` chật:** Chỉ riêng đổi sang `flat` tăng `A3 p=4 S=8` thêm `+0.2982x [+0.1644, +0.4320]` (`1.9648x -> 2.2630x`), cắt `merge_us` từ `1237 us` xuống `709 us`.
   - **Phần hụt còn lại thuộc về cấu trúc đồ thị `A3`:** Cắt tỉa `C/K` ép `A3` cần `beam ~ 944–990` (gấp `2.3x` `A0/A1` `402–426`). Đường đi dài hơn tạo gấp đôi số round barrier (`~17–32` vs `8–14` ở `p=4`), giữ `serial_merge_us ~ 709–719 us` (so với `407 us`), tổng barrier wait `1039–1223 us` (so với `578–694 us`), và `5.0k–6.2k` L2 eval trùng lặp (`17.2%–19.4%`). Ngược lại, `worker_idle_ns` không đáng kể ở cả 3 đồ thị (`<= 17 us` tổng `p` luồng, `< 5 us/worker`), chứng tỏ round-robin `active_frontier` cân tải tốt (`workload_imbalance <= 1.006`).

---

## 6. Giai đoạn E — Quyết định cho `H3 (TP-CG)`: **`PIVOT`** (`NOT_OPENED`)

### 6.1 Khung tiêu chí đánh giá `GO` / `HOLD` / `PIVOT`
- **`GO` cho TP-CG** chỉ hợp lệ nếu sau khi khắc phục bottleneck hiển nhiên của merger, biên dao động pha `S` còn headroom đủ lớn (thực tế thường cần `> 5–10%` trên nhiều hạt giống) **và** chi phí tuần tự tại barrier không còn lấn át lợi ích điều chỉnh `S`.
- **`HOLD`** phù hợp nếu dữ liệu chưa đủ (thiếu `R2/R3` hoặc cấu hình chưa ổn định). Nay `R1/R2/R3` đã tái lập sạch.
- **`PIVOT`** là quyết định đúng khi bằng chứng chỉ rõ **nghẽn cổ chai chi phối (`40–43%` tổn thất so với lý tưởng `4x`) KHÔNG nằm ở việc `S` cố định giữa các pha**, còn dư địa của TP-CG tĩnh-vs-động chỉ ở mức một vài phần trăm.

### 6.2 Lý do định lượng chọn **`PIVOT`**
1. **Dư địa (headroom) của dynamic `S` quá nhỏ sau `flat`:**
   - Trên `A0 p=4`: `S4_flat = 2.4992x`, `S8_flat = 2.4967x` (Stage C2) / `2.4086x` (Stage D `n=3`), `S16_flat = 2.2254x`. Hiệu số giữa các bước `S` tối ưu cận trên chỉ quanh `<= 1–3%` (`< 40–100 us`), trong khi khoảng trống tới lý tưởng `4.0x` (`1372 us`) là **`907 us`** (`+66%` trên latency)!
   - Trên `A3 p=4`: `S8_flat = 2.2630x`, `S16_flat = 2.2841x` (chênh lệch chỉ `+0.0211x`, `< 1%`), trong khi tổng excess là **`1543–1577 us`**. Đổi `S` theo pha trên engine single-writer hiện tại không thể lấy lại `709–719 us` của bước quét `global_best` + lọc `active_frontier` ở `merge_time_ns`, cũng không xóa được `~290–489 us/worker` do tính L2 trùng giữa các worker không chia sẻ `visited` trong round.
2. **Ba nút thắt thực sự đáng nghiên cứu trước `TP-CG` (theo thứ tự ưu tiên):**
   - **Pivot 1 — Xác nhận đa kiến trúc trên `i5-14600KF` (nếu có máy):** Tách ảnh hưởng nhiệt/CCX của laptop `Ryzen 5 PRO 4650U` (`A1_r2` có biến thiên nhiệt `SD=201 us`) bằng cách chạy lại chính ma trận `Stage D` (cùng binary logic, không đổi beam trên test).
   - **Pivot 2 — Tối ưu hóa incremental `merge / frontier scan` (`407–719 us`, chiếm `17.8–20.0%` tổng latency `p=4`):** Hiện mỗi barrier `worker 0` quét lại toàn bộ mảng `global_best` (`beam` phần tử) và mảng `global_expanded_epoch_` để dựng lại `active_frontier`. Cần đo/khắc phục phần quét tuần tự này (hoặc đánh dấu trạng thái expanded ngay trên cấu trúc `Hit`/incremental ready queue) trước khi đụng đến chính sách điều phối `S`.
   - **Pivot 3 — Chia sẻ claim/visited nhẹ trong round để cắt `3.8k–6.2k` L2 trùng (`17–19%`):** Cần một thử nghiệm đối chứng đo đánh đổi giữa atomic relaxed bitset / CAS-byte claim tại điểm chuẩn bị tính L2 (không chạm vào inner neighbor loop cho những đỉnh đã có trên local cache) so với false-sharing L1/L2.
3. **Điều kiện tiên quyết nếu tương lai mở lại đánh giá `TP-CG`:**
   - Mọi baseline tĩnh `S ∈ {4, 8, 16}` đều phải dùng cùng merger đã tối ưu (`flat` hoặc bản incremental mới nhất) và cùng binary SHA-256.
   - Đánh giá bắt buộc ở **Strict Matched Recall (`|ΔRecall| <= 0.0001` trên `val_10k` độc lập)** để tránh đánh đồng mức tăng Recall trôi theo `S` với lợi ích thuật toán.
   - Báo cáo đồng thời `ratio_of_aggregate_means` trên **`n = 3` graph replicates** (`R1/R2/R3`) kèm định mức cải thiện tối thiểu vượt trên biến thiên nhiệt giữa các seed trước khi coi là gain thực.

---

## 7. Hồ sơ Tái lập & Kiểm chứng (`OBSERVED` sau chỉnh sửa cuối cùng)

- **Mã nguồn / Binary:** [p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp), [p2_eval.cpp](../../../research/task_da/search_common/p2_eval.cpp), [test_task_da.py](../../../tests/research/test_task_da.py) (`task_da_p2_eval` SHA-256 `ff46d6ac8895d519054548575c3187544716c0fdf2bbdad83db8a0a8cc7f8759`).
- **Evidence Directory & Index Checksums:**
  - Audit Stage A: `../artifact-evidence/p2-followup-20261118/stage_a_audit_report.json`
  - Stage B Fine Calibration + Pilot: `../artifact-evidence/p2-followup-20261118/stage_b_val10k_fine/matched_recall_frozen_manifest.json`, `stage_b_matched_pilot/stage_b_h1_off_summary.json`
  - Stage C1 (`sync` `std::set`): `../artifact-evidence/p2-followup-20261118/stage_c_sync_ablation/stage_c_sync_ablation_summary.json`
  - Stage C2 (`set` vs `flat`): `../artifact-evidence/p2-followup-20261118/stage_c_merge_ablation/stage_c_merge_ablation_summary.json`
  - Stage D (`45-cell val_10k` + `63-cell R1/R2/R3` + decomposition): `../artifact-evidence/p2-followup-20261118/stage_d_val10k_r2_r3/stage_d_val10k_45cells_manifest.json`, `stage_d_replication/stage_d_replication_summary.json`, `stage_d_replication/STAGE_D_REPLICATION_SUMMARY.csv`, `stage_d_replication/stage_d_decomposition.json`
  - Toàn bộ checksums: `../artifact-evidence/p2-followup-20261118/EVIDENCE_CHECKSUMS.csv` (`1,777` tệp, `2,491.26 MiB`, `18/18` immutable hashes Verified).
- **Trạng thái chưa chạy / môi trường chặn (ghi nhận nguyên trạng):**
  - `i5-14600KF`: **`NOT_AVAILABLE_ON_THIS_HOST_NOT_RUN`**.
  - `GCC 13 TSan`: **`ENV_BLOCKED`** bởi ASLR kernel host (giữ nguyên sysctl bảo mật).
  - `tests/research` 3 module phụ thuộc `numpy` cũ (`test_algorithm_studies`, `test_issue29`, `test_paper_native_v3`): **`PARTIAL_ENV_DEP`** thiếu gói Python tùy chọn `numpy`; toàn bộ `test_task_da.py` (`24/24`) và các ca không phụ thuộc `numpy` đều **`PASS`**.
