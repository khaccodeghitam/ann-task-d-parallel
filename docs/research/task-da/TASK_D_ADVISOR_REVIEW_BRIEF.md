# Task D · Bản Tóm tắt Trình Giảng viên Hướng dẫn (Advisor Review Brief)

- **Ngày báo cáo:** 2026-11-25
- **Trạng thái chương trình:** **`AUDIT COMPLETE`** · **`GIT PUSH VERIFIED`** (`PRIVATE`) · **`REMOTE SHA256 VERIFIED (9/9)`** · **`G2 CLOSEOUT COMPLETE`** · **`RESEARCH PAUSED`** · **`G3 NOT_OPENED`**.
- **Định vị học thuật đề xuất:** **Nghiên cứu Thực nghiệm Hệ thống (*Experimental Systems Research*)**, **Tối ưu Kỹ thuật Đường cơ sở (*Engineering Optimization / Baseline Hygiene*)**, **Nghiên cứu Kết quả Âm có Phạm vi (*Negative-Result Study*)** và **Nghiên cứu Khả năng Tái lập (*Reproducibility Study*)** — **không** tuyên bố phát minh thuật toán mới.
- **Bộ hồ sơ tổng hợp đi kèm:** [Tổng hợp toàn diện](TASK_D_FINAL_RESEARCH_SYNTHESIS.md) · [Dòng thời gian](TASK_D_RESEARCH_TIMELINE.md) · [Kỹ thuật B1+A1](TASK_D_B1_A1_TECHNICAL_EXPLANATION.md) · [Bảng thực nghiệm](TASK_D_FINAL_EXPERIMENT_RESULTS.md) · [Ma trận Claim–Evidence](TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md) · [Đóng góp & Giới hạn](TASK_D_SCIENTIFIC_CONTRIBUTIONS_AND_LIMITATIONS.md) · [Đề cương báo cáo](TASK_D_FINAL_REPORT_OUTLINE.md).

---

## 1. Đề tài ban đầu & Vấn đề nghiên cứu

**Đề tài:** *Thực thi song song và lập lịch trong tìm kiếm láng giềng gần nhất xấp xỉ (ANN) dựa trên đồ thị (Task D — Parallel Execution & Scheduling), kết hợp đánh giá tích hợp BUILD–SEARCH với Task A.*

Xuất phát từ bài toán tối ưu thực thi song song trên chỉ mục ANN dựa trên đồ thị (khởi đầu với đánh giá thực nghiệm **PipeANN** CPU–SSD trên SIFT10M, sau đó mở rộng khảo sát hệ thống qua 3 cụm Parallel ANN và thiết kế đề xuất liên nhóm **Task A × Task D**), nghiên cứu hội tụ về bốn câu hỏi kiểm chứng được trên phần cứng sẵn có:
1. Giới hạn mở rộng thực tế và các bẫy đo lường của thực thi song song ANN trên phần cứng phổ thông là gì?
2. Cấu trúc đồ thị từ quá trình **BUILD** (Task A) tương tác như thế nào với tìm kiếm **đa walker nội query** (Task D) tại Recall khớp?
3. Nguồn lãng phí thực sự nằm ở lập lịch động phức tạp (queue-role, TP-CG, overlap seed assignment) hay ở vệ sinh đường cơ sở (*baseline hygiene*)?
4. Cải thiện BUILD của Task A (`Fast v2`) và cải thiện SEARCH của Task D (`B1+A1`) tương tác với nhau ra sao khi tích hợp?

---

## 2. Ba cụm Parallel ANN đã khảo sát (`D01–D10`)

| Cụm nghiên cứu | Hệ thống / Công trình tiêu biểu | Trọng tâm phân loại (`D01–D10`) | Trạng thái & Ranh giới |
|---|---|---|---|
| **Cụm 1 · Multi-core Graph Traversal** | Speed-ANN (2022), iQAN (PPoPP '23), ParlayANN (PPoPP '24), AverSearch (2025) | Song song nội query vs liên query, đồng bộ AUP/BSP, visited tracking, queue-role (`D01–D03`, `D07`) | **Trọng tâm thực nghiệm chính** (E0–E3, P0–P4, H1–H3, `B1+A1`, G1 & G2 v2 `design-3.1`) |
| **Cụm 2 · CPU–SSD Pipeline Scheduling** | DiskANN (2019), PipeANN (OSDI '25), LAANN (2026), PageANN, Starling, SPANN | Bất đồng bộ `io_uring`, căn hàng I/O, batch width, prefetch/look-ahead (`D04–D06`, `D09–D10`) | Hoàn thành baseline **PipeANN SIFT10M** (`Issue #32`, `36/36`) & sàng lọc âm `H-G/H-QV1/H-V/H-F`; hướng mở rộng sau đó dừng ở **`SURVEY COMPLETE`** |
| **Cụm 3 · GPU Data Parallelism** | FAISS GPU (2017 — WarpSelect, GEMM, IVFADC), CAGRA (ICDE '24), FusionANNS (FAST '25), Hitcher | Warp-level selection, batching SIMD/SIMT, chia tải CPU–SSD–GPU (`D08`) | **`SURVEY COMPLETE / EXPERIMENTAL CLAIMS OPEN`** (`0` code/benchmark GPU) |

---

## 3. Các hướng cải tiến đã thử nghiệm & Các kết quả âm có phạm vi (*Scoped Negative Findings*)

Mọi hướng không đạt tiêu chuẩn định lượng hoặc trùng prior art đều được đóng chặn kịp thời theo nguyên tắc [RESEARCH_PHILOSOPHY.md](../../../RESEARCH_PHILOSOPHY.md) (luôn giữ đúng phạm vi, không suy rộng phổ quát):

1. **PipeANN SIFT10M (`Issue #32` & nhánh sàng lọc `H-G/H-QV1/H-V/H-F`):**
   - Trên laptop `i7-12700H` khóa hợp đồng nhiệt **Custom Full-Fan `60/90 W`** (`36/36` lượt `PAPER_GCC13_PORTABLE`), tăng `T8 → T16` làm giảm QPS **`−13.36%`** (`CI90 [−14.35%, −11.49%]`, `P99.9: 4.40 → 83.55 ms`) tại Recall khớp `99.21%`; cơ chế nhân quả `D1/D4/D6` được giữ nguyên trạng thái lịch sử (`UNTESTED / NOT TESTED / INCONCLUSIVE`).
   - Trên exact surrogate SIFT10M (`48` q / `96` trạng thái): **`H-G`** (raw Jaccard overlap) tốn `2.56 GB` metadata nhưng cho **`0` cải thiện**; **`H-QV1`** (margin giá rẻ) làm xấu utility (`−0.0001224`); **`H-V`** và **`H-F`** đều **`NO-GO`**.
2. **Điều phối vai trò hàng đợi động kiểu AverSearch (`E0–E3`):**
   - **`E0`** (mô hình tổng hợp 2 tầng, `108` cấu hình lưới `N, m, d, s, o`, `432` lượt, `MODEL_ONLY`): so với phân chia tĩnh tốt hơn từng ô `min(Fixed-1, Fixed-2)`, chính sách động chỉ đạt **`3` thắng** (tất cả đều cần phí chuyển `s = 0`, `m=2, d=5`) / **`15` hòa** / **`90` thua (`90/108`)** (đối chiếu riêng: `69/13/26` vs `Fixed-1` và `30/8/70` vs `Fixed-2`) → bác bỏ tuyên bố ưu việt phổ quát trong mô hình (**`REFUTED_WITH_SCOPE`**), còn giả thuyết trên mã gốc AverSearch giữ **`INCONCLUSIVE`**.
   - **`E2`** (nguyên mẫu 1 mutex trên SIFT1M NSG, `Ryzen 4650U`): tăng maintainer gây tranh chấp khóa nặng (`Fixed-1 19.21` > `Adaptive-3 15.09` > `Fixed-2 10.72 QPS`, `Fixed-3` dừng nhiệt `90.25°C`) → **`FORMAL NO-GO`**.
3. **Tương tác đồ thị × worker trên R86 (`Stage D`, `378` lượt) & Lập lịch `TP-CG` / `H3 Overlap`:**
   - **H1** chỉ đúng có điều kiện (`p2 S16`: `A0 1.55×` vs `A3 1.43×`, nhưng đảo dấu ở `p4 S16`); việc thay `std::set` bằng mảng phẳng `flat` xóa >`50%` khoảng cách speedup ban đầu.
   - **`TP-CG`** trùng prior art Speed-ANN/iQAN/AverSearch nên dừng ở **`PIVOT / NOT_OPENED`**.
   - **`H3` Overlap-Aware Seed Assignment** (`6,095` round sau `B1+A1` trên R86 `A3`, `p=2, S=16`): `79–80%` duplicate L2 còn lại phát sinh động giữa round (*emergent–emergent*), chỉ `0.33%` là `seed–seed`; sketch `sig-128` thua cân bằng bậc `−0.97%` đến `−1.12%` và tốn `28.5–29.7 µs/q` → **Scoped `NO-GO`**.
4. **Kiểm toán đo lường & bẫy phương pháp luận (`P1.5`, Stage 6, `design-2`, Phase Audit `20/11`):**
   - Phát hiện *winner's curse* (`t0998` trượt `7/9`), ngưỡng `span <= 0.0001` bất khả thi ở `N=3,000` ($P=0.03\%$), tự nhiễu `3×` của monitor `design-2`, và lỗi cộng timer gây residual âm (`−196 µs`).
   - Tại kiểm toán `20/11`, phase observer bị gắn **`NOT_VALIDATED_OUTSIDE_EQUIVALENCE_BUDGET`** vì dù ước lượng điểm `−1.717%` nằm trong biên `±2%`, **cận dưới `CI95 = −2.851%` rơi ngoài `[−2%, +2%]`** (`CI95 [−2.851%, −0.570%]`); đồng thời `perf_event_paranoid = 4` chặn PMU nên phân rã chu kỳ phần cứng OFF giữ nguyên trạng thái **`UNKNOWN`**.

---

## 4. Lý do PIVOT sang `B1+A1`

Thay vì ép triển khai các bộ lập lịch động phức tạp (`E0–E3`, `TP-CG`, `H3`) vốn hoặc trùng prior art, hoặc bị triệt tiêu lợi ích bởi chi phí lập lịch và đặc tính phát sinh động giữa round, phân tích trực tiếp đường cơ sở BSP trong `p2_engine.hpp` (`flat + baseline + full`) phát hiện hai nguồn lãng phí **có thực, định lượng rõ ràng và loại bỏ được mà không làm thay đổi quỹ đạo tìm kiếm**:
1. Tỷ lệ tính lại khoảng cách L2 xuyên round cao (trên R90 `b432` là `~3,713` dup L2/truy vấn, tương đương `16.3%` tổng L2; trên R86 `A3 b970` còn cao hơn).
2. Chi phí dựng lại toàn bộ `active_frontier_` và nạp thừa hàng trăm hạt giống vào `std::set local_pending` ở mỗi superstep trong khi mỗi worker chỉ mở rộng tối đa `S = 16` đỉnh.

Do đó, Task D quyết định **PIVOT** sang tối ưu *baseline engineering hygiene* **`B1+A1`** kết hợp kiểm định tích hợp liên nhóm **Task A × Task D (G2 v2)** theo giao thức đóng băng nghiêm ngặt.

---

## 5. Cơ chế kỹ thuật của `B1+A1` ([`research/task_da/search_common/p2_engine.hpp`](../../../research/task_da/search_common/p2_engine.hpp), `f2cd634`)

Trong engine tìm kiếm C++17 BSP nội query (`P2SearchSession`, đọc trực tiếp `.pipnn`/`.nsg`, `p=2`, `S=16`, đồng bộ bằng `work_seq_/done_seq` không khóa trong pha worker):
- **`B1` (`barrier_all_evaled`):** Thay vì chỉ đánh dấu `settled_epoch_` cho các đỉnh sống sót trong beam, mỗi worker ghi mọi đỉnh đã tính L2 vào bộ đệm riêng `local_newly_evaled` và công bố phẳng vào `settled_epoch_` tại barrier đơn luồng cuối round → **triệt tiêu 100% tính lại L2 xuyên round**, không dùng khóa hay atomic trong pha worker.
- **`A1` (`incremental`):** Nhúng cờ `expanded` trực tiếp vào mảng beam phẳng `FlatEntry`, hợp nhất pha merge–dispatch thành một lượt quét, và dừng cấp phát ngay khi đủ tối đa `p × S` hạt giống chưa mở rộng → giảm chi phí nạp `std::set local_pending` từ $O((B/p)\log(B/p))$ xuống $O(S\log S)$.
- **Tính bất biến bit-exact:** Vì `global_worst` chỉ giảm đơn điệu theo round (đỉnh đã bị loại khỏi beam sẽ không bao giờ được nhận lại ở round sau) và mỗi worker dừng sau đúng `steps < S` lần pop, `B1+A1` **bảo toàn 100% quỹ đạo tìm kiếm, `unique L2`, `expansions`, Top-10 IDs và `squared_l2`** giống hệt baseline.

---

## 6. Kết quả thực nghiệm chính (đã kiểm toán độc lập `AUDIT_PASS`, `0` sai lệch)

### 6.1 Measured SEARCH trên Host D (`G2 v2 design-3.1 run2`, `Ryzen 5 PRO 4650U`, `multi-user.target`)
Thực nghiệm 2×2 trên `6` đồ thị cố định R90 v1.3 (`3 Stock + 3 Fast v2`, `MS-Turing-1M`, `common beam = 432`, `p=2, S=16, jobs=1`), gồm `18/18` lượt **Quality ON** và `144/144` lượt **Performance OFF** (`12` block cân bằng `36 AB / 36 BA`, `1299/1299` `BUNDLE.sha256` PASS, sau 2 biên bản `HOLD` lịch sử được niêm phong tách biệt):

- **Hiệu năng OFF (`GO_A_FIXED_COHORT`):**
  - Mean latency giảm **`6.033%`** (`1.0642×`, `3619.71 → 3401.33 µs`), `QPS_wall` tăng `276.25 → 293.99` (`+6.42%`), `6/6` đồ thị đều > `5.99%`, `imbalance_warning = false`, `Tctl max = 78.5°C`.
  - Cải thiện đồng đều ở các phân vị đuôi: **`P50 −6.01%`**, **`P95 −4.22%`**, **`P99 −4.09%`**; Peak RSS không đổi (**`+9.4 KiB`**); `Proc CPU-s` giảm **`−7.07%`**.
  - **Phân biệt 4 họ khoảng tin cậy:**
    - *Primary block-$t$ (`df=11`)*: **`[5.977%, 6.090%]`** (Drift `df=5`: `[5.991%, 6.075%]`).
    - *Query-only bootstrap (`10,000`)*: **`[5.970%, 6.096%]`**.
    - *Joint bootstrap (`10,000`)*: **`[5.954%, 6.113%]`**.
    - *Graph population CI*: **`NOT_ESTIMABLE`** (do `6` đồ thị dùng chung `SEED = 555`).
- **Chất lượng & Cơ chế ON (`18/18`, `166/166` SHA):**
  - Phạm vi kiểm định: `20,000` truy vấn duy nhất (`10k` test + `10k` val), **`1,620,000` bản ghi thực thi G2 v2** (`1,440,000` OFF + `180,000` ON mới), **`0` sai lệch** trên toàn bộ `120,000` cặp đối chứng ON base-vs-opt (`60k` test + `60k` val vs Stage 5) và `144/144` process OFF khớp digest chuẩn.
  - Duplicate L2 giảm **`−74.98%`** (`3,712.81 → 928.77/q`), Total L2 giảm **`−12.22%`** (`22,776.97 → 19,992.93/q`), khớp `1-đổi-1` với `already_seen` (`+2,784.04/q`); `unique L2` (`19,064.16`) và `expansions` bất biến (`Δ = 0`).
  - **Gate A** (`LCB95 ≥ 0.99119`, vượt ngưỡng `0.990`) và **Gate B** (`Fast − Stock = +0.000117`, `CI95 [−0.000051, +0.000284]` ⊂ `±0.0005`) đều **PASS**.

### 6.2 Measured BUILD (Host A) & Modeled Two-Host BUILD–SEARCH (`GO_B_SYSTEM_FIXED_COHORT`)
- **Measured BUILD (Host A — Task A `Fast v2`):** Giảm từ `42.257 s → 33.793 s` (**`−8.463 s`, `−20.03%`**), giữ nguyên topology `C160/K1024/N2` (khác hoàn toàn `R86 A3` cắt `C64/K512` làm suy giảm nặng tốc độ Search).
- **Tương tác 2×2 (Measured SEARCH trên Host D):** `Fast − Stock` trung tính (`+0.33/+0.37 µs`, CI chứa 0); hiệu ứng tương tác `Fast_gain − Stock_gain` = **`+0.037 µs`, `CI95 [−2.582, +2.655] µs`** (`log +0.000016 [−0.000734, +0.000766]`). Không phát hiện tương tác có ý nghĩa thống kê và khoảng tin cậy bị chặn chặt quanh 0 (`±1.2%` độ lớn gain), tương thích với mô hình xấp xỉ cộng tính (*không* diễn giải CI chứa 0 thành chứng minh tương tác bằng 0 tuyệt đối hay độc lập hoàn toàn).
- **Modeled Two-Host BUILD–SEARCH** (*mô hình cộng hai máy ghép biên nhận BUILD cố định Host A với SEARCH đo trên Host D, **không phải** đo native single-host end-to-end, loại trừ truyền tải/nạp chỉ mục `~3.9 s`*): tổ hợp `fast_opt` trội hơn `stock_base` ở mọi `Q ≥ 1`, dự báo tiết kiệm **`30.336 s`** tại `Q=100k` (`404.244 → 373.908 s`) và **`227.194 s`** tại `Q=1M` (`3662.131 → 3434.938 s`).

### 6.3 Kết quả khám phá bổ sung trên R86 (`EXPLORATORY / HOLD`)
Trên đồ thị `R86 A3` (`beam ≈ 970`, nhiều round hơn `31.7` vs `14.9`), `B1+A1` giảm `10.08%–12.29%` theo từng build (đóng góp cộng từ B1 và A1), nhưng kiểm định outer 2-build (`df=1`) ở **`HOLD`** (`CI95 [−2.84%, +25.21%]`), và ở `p=4` xuyên 2 CCX lợi ích không ổn định (`CI95` chứa 0, có ca tăng `p95`).

---

## 7. Đóng góp riêng của Task D & Đóng góp kết hợp Task A × Task D

- **Đóng góp riêng của Task D:**
  1. *Khảo sát & kiểm toán prior art:* Hệ phân loại `D01–D10` xuyên 3 cụm và đối chiếu prior art mức cơ chế giúp ngăn tái phát minh thuật toán đã có.
  2. *Phương pháp luận benchmark & kiểm soát nhiễu:* Hợp đồng nhiệt `60/90 W`, giải pháp chống *winner's curse* (`LCB95` đồng thời), bộ bảo vệ nhiễu tách CCX + Qualification `900s` + kỷ luật fail-closed `HOLD`.
  3. *Tối ưu kỹ thuật đường cơ sở `B1+A1` & kết quả âm có giá trị:* Cải thiện `6.03%` latency OFF bảo toàn 100% bit-exact trong cohort cố định R90, kèm bộ bằng chứng kết quả âm có phạm vi (E0, E2, PipeANN H-lanes, H3 overlap, phase observer audit).
  4. *Khả năng tái lập & lưu trữ khoa học:* Đóng băng SHA-256 (`29/29`), kiểm toán độc lập `0` sai lệch, lưu trữ PRIVATE Release `9/9` assets xác minh round-trip.
- **Đóng góp kết hợp Task A × Task D:**
  - Làm rõ bằng chứng đối lập giữa hai cách tăng tốc BUILD: cắt cấu trúc `C/K` (`A3`) gây thiệt hại lớn cho Search và parallel scaling, trong khi tối ưu bảo toàn topology (`Fast v2`) giảm `20.03%` BUILD mà không gây bất lợi cho Search và cộng hưởng tốt với `B1+A1` trong đánh giá tích hợp G2 v2 (`GO_A_FIXED_COHORT` + `GO_B_SYSTEM_FIXED_COHORT`).

---

## 8. Giới hạn cốt lõi

1. **Không suy rộng quần thể đồ thị (`graph_population_ci = NOT_ESTIMABLE`):** `6` đồ thị R90 dùng chung `SEED = 555` + bất định 4 luồng (không phải 6 gốc RNG độc lập).
2. **Phạm vi đơn máy, đơn tập dữ liệu (`EXPLORATORY_HOST_SPECIFIC`):** Một host (`Ryzen 5 PRO 4650U`, `schedutil`), một dataset (`MS-Turing-1M` 100D), một điểm vận hành (`p=2, S=16, beam=432, jobs=1`). `i5-14600KF`, dataset thứ 2 cho Task D, `10M/R91`, và concurrent serving (`jobs > 1`) đều **`NOT_RUN`**.
3. **Mô hình BUILD–SEARCH hai máy chưa phải đo đầu–cuối 1 máy:** Loại trừ truyền/nạp chỉ mục (`~3.9 s`) và không chứa phương sai BUILD hạt giống mới.
4. **Hạn chế đo phần cứng & phạm vi cụm:** PMU (`perf_event_paranoid = 4`) và năng lượng RAPL đều **`NOT_MEASURED`**; chưa có ablation tách riêng `B1-only` vs `A1-only` trên R90; tập `v2_test_10000` trích từ `public 100K`; Cụm 2 (sau PipeANN baseline) và Cụm 3 (GPU) dừng ở mức khảo sát.

---

## 9. Các câu hỏi cần giảng viên xác nhận

1. **Định vị học thuật của báo cáo:** Giảng viên có đồng ý chốt báo cáo cuối cùng theo hướng **Nghiên cứu Thực nghiệm Hệ thống, Tối ưu Kỹ thuật Đường cơ sở, Kết quả Âm & Khả năng Tái lập** (không tuyên bố phát minh thuật toán mới) hay không?
2. **Phạm vi 3 Cụm trong báo cáo:** Trình bày Cụm 2 (sau PipeANN baseline) và Cụm 3 (GPU) ở Chương Khảo sát/Định vị và tập trung Chương Thực nghiệm vào Cụm 1 + Tích hợp Task A × Task D đã phù hợp mục tiêu học phần/đề tài chưa?
3. **Mức độ chấp nhận ranh giới `EXPLORATORY_HOST_SPECIFIC` & mô hình hai máy:** Kết quả `GO_A_FIXED_COHORT` + `GO_B_SYSTEM_FIXED_COHORT` (công bố minh bạch `SEED=555`, 1 host, mô hình hai máy) đã đủ ngưỡng đóng kết thực nghiệm hay giảng viên yêu cầu bổ sung phép đối chứng nào?
4. **Cấu trúc phối hợp báo cáo với Task A:** Phần tích hợp A×D G2 nên đặt thành một chương/mục dùng chung số liệu kiểm toán (`audit_results.json`) giữa hai báo cáo hay trình bày độc lập trên từng báo cáo?
5. **Quyết định chính thức về G3:** Giảng viên có phê duyệt giữ nguyên **`G3 NOT_OPENED`** để chuyển thẳng sang viết báo cáo chính thức theo [TASK_D_FINAL_REPORT_OUTLINE.md](TASK_D_FINAL_REPORT_OUTLINE.md) không?

---

## 10. Khuyến nghị về G3: **Giữ nguyên `G3 NOT_OPENED`**

- **Lý do:** Mục tiêu kiểm chứng tích hợp cốt lõi của G2 đã hoàn thành trọn vẹn (`144/144` OFF + `18/18` ON, `AUDIT_PASS`, `GO_A`, `GO_B`, lưu trữ PRIVATE xác minh `9/9`). Mở G3 để vượt ranh giới `NOT_ESTIMABLE` đòi hỏi chi phí rất lớn ngoài phạm vi hiện tại: sửa mã Task A hỗ trợ gốc RNG độc lập + đồng bộ ISA, chạy thêm phần cứng thứ 2 (`i5-14600KF`/server có quyền `perf`), thêm dataset thứ 2 hoặc quy mô `10M` (`R91`), và đo single-host end-to-end đầy đủ.
- **Đề xuất:** Duy trì **`G2 CLOSEOUT COMPLETE · RESEARCH PAUSED · G3 NOT_OPENED`**, chốt 5 quyết định trên với giảng viên, rồi triển khai viết báo cáo cuối cùng theo đề cương 7 chương. Chỉ mở đề cương G3 mới nếu giảng viên yêu cầu bắt buộc bằng chứng suy rộng quần thể hoặc cross-host để nghiệm thu.
