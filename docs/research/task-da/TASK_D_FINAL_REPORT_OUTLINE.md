# Task D · Đề cương Báo cáo Khoa học Cuối cùng (Final Report Outline)

Đề cương dưới đây được thiết kế sẵn sàng để triển khai thành **Báo cáo Chuyên đề / Báo cáo Nghiên cứu Thực nghiệm Hệ thống (Experimental Systems & Empirical Study)** cho Task D (và phần tích hợp Task A × Task D). Mỗi mục đều ánh xạ trực tiếp tới tài liệu nguồn đã kiểm toán, bảng/hình tương ứng, và ranh giới tuyên bố hợp lệ.

---

## Tiêu đề đề xuất (không overclaim)
- **Tiếng Việt:** *Nghiên cứu Thực nghiệm Thực thi Song song, Tương tác Cấu trúc Đồ thị và Tối ưu Đường cơ sở Tìm kiếm ANN Đa lõi (Task D & Tích hợp Task A × Task D)*
- **Tiếng Anh:** *An Experimental Systems Study of Intra-Query Parallel Graph-Based ANN Traversal: Baseline Hygiene Optimization, Negative Scheduling Findings, and Joint BUILD–SEARCH Integration*

---

## Tóm tắt (Abstract — 250–300 từ)
- **Nội dung:** Định vị báo cáo là *nghiên cứu thực nghiệm hệ thống, tối ưu kỹ thuật đường cơ sở, nghiên cứu kết quả âm có phạm vi và nghiên cứu khả năng tái lập* (không tuyên bố phát minh thuật toán mới). Đặt bài toán tìm kiếm ANN trên đồ thị ở quy mô 1M–10M; tóm lược 3 cụm khảo sát (`D01–D10`); nêu trung thực các kết quả âm có phạm vi loại bỏ những hướng lập lịch không hiệu quả (E0/E2 queue-role, PipeANN H-lanes, H3 overlap seed assignment); trình bày tối ưu kỹ thuật bảo toàn kết quả bit-exact **`B1+A1`** và kiểm định chính thức tích hợp A×D G2 v2 `design-3.1` trên 6 đồ thị cố định R90 v1.3 (`AUDIT_PASS`): **Measured SEARCH (Host D)** giảm **`−6.033%`** mean latency OFF (Primary `CI95 [5.977%, 6.090%]`, Joint boot `[5.954%, 6.113%]`), **`−74.98%`** duplicate L2, **`−12.22%`** total L2, RSS không đổi; **Measured BUILD (Host A)** `Fast v2` giảm **`−20.03%`** mà không phát hiện tương tác thống kê với `B1+A1` (`+0.037 µs`, `CI95 [−2.58, +2.66] µs`); **Modeled Two-Host BUILD–SEARCH** dự báo tiết kiệm `30.34 s` (`Q=100k`) và `227.19 s` (`Q=1M`, loại trừ truyền/nạp). Nhấn mạnh phạm vi **`EXPLORATORY_HOST_SPECIFIC`** và **`graph_population_ci = NOT_ESTIMABLE`**.

---

## Chương 1 · Giới thiệu & Tiến hóa Bài toán Nghiên cứu (2–3 trang)
- **1.1 Bối cảnh & Động lực:** Vì sao tìm kiếm ANN dựa trên đồ thị (Vamana/DiskANN, NSG, PiPNN) phải cân bằng giữa độ chính xác (`Recall@k`), chi phí xây dựng (`BUILD`), và độ trễ/mở rộng song song nội query (`SEARCH`).
- **1.2 Câu hỏi nghiên cứu cốt lõi (RQ1–RQ4):**
  - *RQ1:* Hiệu năng và giới hạn mở rộng đa luồng/pipeline thực tế của hệ thống hiện có trên phần cứng phổ thông là gì?
  - *RQ2:* Cấu trúc đồ thị từ quá trình BUILD (Task A) tương tác như thế nào với tìm kiếm đa walker (Task D) tại Recall khớp?
  - *RQ3:* Những nguồn lãng phí thực sự nằm ở đâu — ở lập lịch động phức tạp (queue-role, TP-CG, overlap) hay ở thiết kế đường cơ sở (visited publication, frontier management)?
  - *RQ4:* Cải thiện BUILD (Task A `Fast v2`) và cải thiện SEARCH (Task D `B1+A1`) có cộng hưởng hay triệt tiêu nhau khi tích hợp?
- **1.3 Tiến hóa định hướng nghiên cứu & Hiến chương kiểm chứng:** Tóm lược 4 kỷ nguyên từ [TASK_D_RESEARCH_TIMELINE.md](TASK_D_RESEARCH_TIMELINE.md) và nguyên tắc [RESEARCH_PHILOSOPHY.md](../../../RESEARCH_PHILOSOPHY.md).
- **1.4 Tóm lược đóng góp & phạm vi:** Dẫn từ [TASK_D_SCIENTIFIC_CONTRIBUTIONS_AND_LIMITATIONS.md](TASK_D_SCIENTIFIC_CONTRIBUTIONS_AND_LIMITATIONS.md).
- **Hình 1.1:** Sơ đồ hành trình 4 kỷ nguyên và các cổng quyết định `PASS / HOLD / NO-GO / PIVOT / GO`.

---

## Chương 2 · Cơ sở Lý thuyết & Khảo sát 3 Cụm Thực thi Song song ANN (4–5 trang)
- **2.1 Định nghĩa bài toán & Mô hình Work–Span–Cost:** `Recall@k`, `T(G,p,R*)`, `S(G,p)`, `E(G,p)`, `I_D(G,p)`, `Δ_int`, và 6 nhóm tiêu chí đánh giá.
- **2.2 Hệ phân loại Task D (`D01–D10`) & Khảo sát 3 Cụm:**
  - *Cụm 1 — Multi-core Parallel Graph Traversal:* Speed-ANN (2022), iQAN (PPoPP '23), ParlayANN (PPoPP '24), AverSearch (2025).
  - *Cụm 2 — CPU–SSD Pipeline & Scheduling:* DiskANN (2019), PipeANN (OSDI '25), LAANN (2026), PageANN, Starling, SPANN (ghi rõ `SURVEY COMPLETE / EXPERIMENTAL CLAIMS OPEN`).
  - *Cụm 3 — GPU Data Parallelism:* FAISS GPU (2017 — WarpSelect, GEMM, IVFADC), CAGRA (ICDE '24), FusionANNS (FAST '25), Hitcher (ghi rõ `0` thực nghiệm GPU).
- **2.3 Khoảng trống nghiên cứu & Đối chiếu Prior Art bổ sung:** Çatalyürek & Aykanat (1999), GraphIt, ADSampling, FINGER, GINGER (2026), PiPNN / PiPNN II (2026), MARGO, GLIDE ([H3_NOVELTY_AND_PRIOR_ART_AUDIT.md](H3_NOVELTY_AND_PRIOR_ART_AUDIT.md)).
- **Bảng 2.1:** Bảng so sánh cơ chế, giả định, khoảng trống mở và trạng thái thực nghiệm của 3 Cụm (tách bạch tuyệt đối số liệu paper).
- **Evidence references:** `CUM1_MULTICORE_GRAPH_TRAVERSAL_FINAL.pdf`, `CUM2_CPU_SSD_PIPELINE_SCHEDULING_FINAL.pdf`, `CUM3_GPU_DATA_PARALLELISM_FINAL.pdf`, [RESEARCH_ROADMAP.md](../../RESEARCH_ROADMAP.md), [02_UPSTREAM_EVOLUTION_2025_2026.md](../paper-rebaseline-20261012/02_UPSTREAM_EVOLUTION_2025_2026.md), [H3_NOVELTY_AND_PRIOR_ART_AUDIT.md](H3_NOVELTY_AND_PRIOR_ART_AUDIT.md).

---

## Chương 3 · Phương pháp luận Benchmark, Kiểm soát Nhiễu & Đảm bảo Tái lập (3–4 trang)
- **3.1 Kiến trúc đối chứng công bằng:** Tách tuyệt đối `Mode OFF` (đo thời gian) vs `Mode ON` (đếm công); xác minh độc lập `squared_l2` bằng `float64`; khóa manifest SHA-256 và tiền đăng ký trước khi chạy.
- **3.2 Kiểm soát môi trường phần cứng & nhiệt:**
  - Bài học i7-12700H: xung đột `OMP_PROC_BIND=spread` vs `iou-sqp` (`E0b`), giới hạn nhiệt `100°C` → hợp đồng **Custom Full-Fan `60/90 W`** ([EXPERIMENTAL_ENVIRONMENT_V1.md](../../EXPERIMENTAL_ENVIRONMENT_V1.md)).
  - Bài học Ryzen 4650U: tiến hóa bộ giám sát nhiễu từ `design-2` (tự sinh `3×` nhiễu + clamping `5×`) → **`design-3`/`3.1`** (quét `/proc` 1 lượt, tách ngưỡng theo CCX `[0..3] / [0..5] / [0..11]`, Qualification `900s`, `prepare_quiet_tty_env.sh`, cơ chế fail-closed `HOLD`).
- **3.3 Phương pháp thống kê, 4 họ khoảng tin cậy & Hiệu chỉnh chất lượng không thiên lệch:**
  - Khắc phục *winner's curse* (`P1.5`) và ngưỡng bất khả thi `span <= 0.0001` ở `N=3,000` (Stage 6) bằng quy tắc assurance `z = 4.2279` (`common beam = 432`), `LCB95` đồng thời (`z = 2.394`), kiểm định tương đương Gate B (`±0.0005`), thiết kế 12 block cân bằng `AB/BA`.
  - Phân biệt rõ 4 họ CI (+ drift): **Primary block-$t$ (`df=11`) `[5.977%, 6.090%]`**, **Query-only bootstrap (`10k`) `[5.970%, 6.096%]`**, **Joint bootstrap (`10k`) `[5.954%, 6.113%]`** (và Drift `df=5` `[5.991%, 6.075%]`), đối lập dứt khoát với **`Graph population CI = NOT_ESTIMABLE`** (`SEED=555`).
- **Bảng 3.1 & Bảng 3.2:** (3.1) Tiến hóa giao thức G2 (`v1 → v2 design-2 → design-3 → design-3.1`) và các rào cản đã giải quyết; (3.2) Bảng đối chiếu 4 họ CI và ý nghĩa suy luận ([TASK_D_FINAL_EXPERIMENT_RESULTS.md](TASK_D_FINAL_EXPERIMENT_RESULTS.md) Phần E.2).
- **Evidence references:** [EXPERIMENTAL_ENVIRONMENT_V1.md](../../EXPERIMENTAL_ENVIRONMENT_V1.md), [P1_5_QUALITY_FAILURE_ANALYSIS.md](P1_5_QUALITY_FAILURE_ANALYSIS.md), [AXD_G2_QUALITY_HOLD_RESOLUTION_DECISION.md](AXD_G2_QUALITY_HOLD_RESOLUTION_DECISION.md), [AXD_G2_V2_B1_QUIET_FEASIBILITY_REVIEW.md](AXD_G2_V2_B1_QUIET_FEASIBILITY_REVIEW.md), `AXD_G2_V2_DESIGN3_1_FREEZE.sha256`.

---

## Chương 4 · Các Kết quả Âm & Chuyển hướng Dựa trên Bằng chứng (4–5 trang)
- **4.1 Giai đoạn 1 — PipeANN SIFT10M (`Issue #32`) & Các nhánh cơ chế âm:**
  - Kết quả đạt chuẩn **Issue #32 (`36/36`)**: `T16 vs T8 = −13.36%` (`CI90 [−14.35%, −11.49%]`, `P99.9 = 83.55 ms`); bảo lưu `D1 UNTESTED`, `D4 NOT TESTED`, `D6 INCONCLUSIVE`.
  - Sàng lọc âm `H-G` (`2.56 GB`, `0` gain), `H-QV1` (`−0.000122` utility), `H-V` (`NO-GO`), `H-F` (`INCONCLUSIVE/NO-GO`).
- **4.2 Chuỗi AverSearch Queue-Role (`E0–E3`):**
  - `E0` (`108` cấu hình lưới, `432` lượt, `MODEL_ONLY`): Responsive vs `min(Fixed-1, Fixed-2)` đạt **`3` thắng** (chỉ tại `m=2, d=5, s=0`) / **`15` hòa** / **`90` thua (`90/108`)**; đối chiếu riêng `69/13/26` vs `Fixed-1 (1:3)` và `30/8/70` vs `Fixed-2 (2:2)` → **`REFUTED_WITH_SCOPE`** (giả thuyết trên AverSearch thật giữ nguyên `INCONCLUSIVE`).
  - `E2` (SIFT1M NSG): nút cổ chai 1 mutex (`Fixed-1 19.21` > `Adaptive-3 15.09` > `Fixed-2 10.72 QPS`) + dừng nhiệt → `FORMAL NO-GO`.
- **4.3 Giai đoạn 2 — Tương tác Đồ thị × Worker trên R86 (`P0–P4`, `H1–H3`):**
  - `P0/P1 HOLD` (`t0998` trượt `7/9`, `SEED=555`, `A3-R2` đỉnh `840923`).
  - `Stage D` (`378` lượt): **H1** có điều kiện (`A0 1.55×` vs `A3 1.43×` ở `p2 S16`, đảo dấu ở `p4 S16`); `std::set → flat` xóa >`50%` khoảng cách ban đầu → **`TP-CG = PIVOT / NOT_OPENED`**.
  - Sàng lọc **H3 Overlap** (`6,095` round): `79–80%` dup L2 là `emergent–emergent`, chỉ `0.33%` là `seed–seed`; `sig-128` thua degree `−0.97%` đến `−1.12%` → **Scoped `NO-GO`**.
  - Kiểm toán đo lường cuối `20/11`: bác bỏ mô hình cộng timer cũ (`−196 µs` residual); phase observer bị gắn **`NOT_VALIDATED_OUTSIDE_EQUIVALENCE_BUDGET`** vì dù ước lượng điểm `−1.717%` nằm trong `±2%`, **cận dưới `CI95 = −2.851%` nằm ngoài `[−2%, +2%]`** (`CI95 [−2.851%, −0.570%]`); PMU bị chặn (`perf_event_paranoid=4`).
- **Bảng 4.1:** Tổng hợp toàn bộ các quyết định `HOLD / NO-GO / PIVOT` có phạm vi kèm bằng chứng định lượng (dẫn từ [TASK_D_FINAL_EXPERIMENT_RESULTS.md](TASK_D_FINAL_EXPERIMENT_RESULTS.md) Phần B & D và [TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md](TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md) §5).
- **Evidence references:** [CUSTOM_FULLFAN_SIFT10M_20261013.md](../CUSTOM_FULLFAN_SIFT10M_20261013.md), [ISSUE29_DECISION_MEMO.md](../ISSUE29_DECISION_MEMO.md), [AVERSEARCH_QUEUE_ROLE_REVIEW.md](../AVERSEARCH_QUEUE_ROLE_REVIEW.md), `results/queue_role_review_20261029/SUMMARY.json`, [STAGE_D_E_REPLICATION_AND_H3_DECISION.md](STAGE_D_E_REPLICATION_AND_H3_DECISION.md), [H3_OVERLAP_SIGNAL_SCREENING_RESULTS.md](H3_OVERLAP_SIGNAL_SCREENING_RESULTS.md), [MEASUREMENT_VALIDITY_AND_PHASE_AUDIT.md](MEASUREMENT_VALIDITY_AND_PHASE_AUDIT.md).

---

## Chương 5 · Phân tích Kỹ thuật Engine Đa Walker & Tối ưu `B1+A1` (4–5 trang)
- **5.1 Kiến trúc BSP `P2SearchSession`:** Cấu trúc CSR, `WorkerState` căn lề 64B, `LocalRoundSet` Fibonacci hash reset $O(1)$, mảng epoch `uint16_t` (`4n` B), hàng rào `work_seq_/done_seq` không khóa.
- **5.2 Nút cổ chai của Baseline (`flat + baseline + full`):** (i) Đỉnh bị loại bởi `global_worst` không ghi vào `settled_epoch_` → tính lại L2 xuyên round; (ii) Dựng lại toàn bộ `active_frontier_` và nạp tới `B/p` hạt giống vào `std::set local_pending` dù chỉ pop tối đa `S`.
- **5.3 Thiết kế `B1` (`barrier_all_evaled`) & `A1` (`incremental`):** Luồng xử lý chi tiết & Pseudocode đối chiếu (dẫn trực tiếp từ [TASK_D_B1_A1_TECHNICAL_EXPLANATION.md](TASK_D_B1_A1_TECHNICAL_EXPLANATION.md)).
- **5.4 Chứng minh tính bất biến đầu ra, độ phức tạp & Trade-off:** Chứng minh tính tương đương quỹ đạo (monotone `global_worst`, ngưỡng `steps < S`), phân tích độ phức tạp theo `(B, p, S, M_r)`, giải thích ảo giác tăng `merge_time_ns` ON (`+35.89 µs`), và phân tích giới hạn `p=4` xuyên CCX trên R86.
- **5.5 Định vị trung thực so với Prior Art:** Vì sao `B1+A1` là *baseline engineering hygiene optimization*, không phải thuật toán tìm kiếm mới.
- **Bảng 5.1 & Hình 5.1:** Bảng đối chiếu độ phức tạp/bất biến giữa Baseline, B1, A1, `B1+A1` & Prior Art; sơ đồ luồng một superstep BSP làm nổi bật `local_newly_evaled` và `max_dispatch = p × S`.
- **Evidence references:** [`research/task_da/search_common/p2_engine.hpp`](../../../research/task_da/search_common/p2_engine.hpp) (`f2cd634`), [TASK_D_B1_A1_TECHNICAL_EXPLANATION.md](TASK_D_B1_A1_TECHNICAL_EXPLANATION.md), [B1_A1_PILOT_HANDOFF_20261119.md](B1_A1_PILOT_HANDOFF_20261119.md), [B1_A1_NARROW_REPLICATION_REPORT_20261119.md](B1_A1_NARROW_REPLICATION_REPORT_20261119.md), [H3_NOVELTY_AND_PRIOR_ART_AUDIT.md](H3_NOVELTY_AND_PRIOR_ART_AUDIT.md).

---

## Chương 6 · Đánh giá Thực nghiệm Tích hợp Task A × Task D (G1 & G2 `design-3.1`) (5–6 trang)
- **6.1 Thiết kế thực nghiệm 2×2 trên R90 P0A v1.3:** `6` đồ thị gốc (`3 Stock + 3 Fast v2`, `C160/K1024/N2`) × `{base, B1+A1}`, `p=2`, `S=16`, `beam=432`, `v2_test_10000.ids`, `12` block cân bằng (`144` OFF + `18` ON).
- **6.2 Kiểm định tiền đề & minh bạch hóa các lượt `HOLD`:** `G1_RUNTIME_PASS`, Qualification #1 FAIL → #2 PASS, Quality ON `18/18 PASS`, và hai biên bản `HOLD` được bảo lưu tách biệt (`design-3` #1/144 `KeyError`; `design-3.1 run1` #120/144 `snap.firmware-updater`).
- **6.3 Kết quả Hiệu năng OFF — Measured SEARCH trên Host D (`GO_A_FIXED_COHORT`, `run2` `144/144`):**
  - Bảng chi tiết theo từng đồ thị, từng nhánh (`Stock` vs `Fast`) và gộp chung: **`−6.033%`** (`1.0642×`, Primary `df=11 [5.977%, 6.090%]`, Query-only boot `[5.970%, 6.096%]`, Joint boot `[5.954%, 6.113%]`, Drift `[5.991%, 6.075%]`, `graph_population_ci = NOT_ESTIMABLE`), `P50 −6.01%`, `P95 −4.22%`, `P99 −4.09%`, `QPS_wall 276.25 → 293.99`, Peak RSS `+9.4 KiB`, `Proc CPU-s −7.07%`.
  - Kiểm chứng độ bền: cân bằng thứ tự `AB (6.025%)` vs `BA (6.041%)`, `Spearman ρ = +0.035` theo thời gian block, `LOO [6.023%, 6.040%]`, `noise_balance.imbalance_warning = false`, nhiệt độ `Tctl max 78.5°C`.
- **6.4 Phân tích Cơ chế Công việc ON (`18/18`) & Đính chính sai số ghi tay:**
  - `100%` bit-exact parity trên `20,000` truy vấn duy nhất (`10k` test + `10k` val) và `1,620,000` bản ghi thực thi G2 v2 (`1,440,000` OFF + `180,000` ON mới), gồm `120,000` cặp đối chứng ON base-vs-opt (`60k` test + `60k` val vs Stage 5) và `144/144` process OFF khớp digest chuẩn (`0` sai lệch).
  - Bảng bộ đếm chính xác từ `audit_results.json`: dup L2 `−74.98%` (`3712.81 → 928.77/q`), total L2 `−12.22%` (`22776.97 → 19992.93/q`), `already_seen +2784.04/q` (`1-đổi-1`), `unique L2` (`19,064.16`) & `expansions` `Δ=0`; ghi chú đính chính minh bạch hai sai số ghi tay trong tài liệu tường thuật lịch sử ([TASK_D_FINAL_RESEARCH_SYNTHESIS.md](TASK_D_FINAL_RESEARCH_SYNTHESIS.md) §3).
- **6.5 Phân tích Tích hợp BUILD–SEARCH Hai Máy (`GO_B_SYSTEM_FIXED_COHORT`):**
  - Tách bạch rõ **Measured BUILD (Host A: `Fast v2 42.257 → 33.793 s`, `−20.03%`)**, **Measured SEARCH (Host D)**, và **Modeled Two-Host BUILD–SEARCH**.
  - Xác nhận Gate B tương đương Recall (`+0.000117 [−0.000051, +0.000284]`) và **không phát hiện tương tác 2×2 có ý nghĩa thống kê** (`Fast_gain − Stock_gain = +0.037 µs`, `CI95 [−2.582, +2.655] µs` — bị chặn chặt quanh 0, tương thích với mô hình xấp xỉ cộng tính; không diễn giải CI chứa 0 thành chứng minh tương tác bằng 0 tuyệt đối hay độc lập hoàn toàn).
  - Trình bày bảng mô hình cộng hai máy (ghi rõ **không phải native end-to-end single-host**, loại trừ transfer/load; `30.336 s` và `227.194 s` là **thời gian tiết kiệm mô hình hóa `saved_s`**, không phải tổng thời gian): `Q=1, 10k [DERIVED], 100k` (`404.244 → 373.908 s`, tiết kiệm `30.336 s`), `1M` (`3662.131 → 3434.938 s`, tiết kiệm `227.194 s`).
- **6.6 Đối chiếu nhất quán với kết quả R86 `A3`:** Giải thích vì sao R90 `b432` cho mức giảm `6.03%` (ít round hơn: `14.9` vs `31.7`) trong khi R86 `A3 b970` cho `10.1%–12.3%`.
- **Bảng 6.1–6.3 & Hình 6.1–6.3:** Bảng kết quả `run2` & 4 họ CI (Phần E.2), bảng bộ đếm ON `audit_results.json`, bảng BUILD–SEARCH hai máy (Phần E.3), biểu đồ giảm latency qua 12 block & phân phối P50/P95/P99, biểu đồ phân rã `Unique / Intra-dup / Cross-dup L2`.
- **Evidence references:** [AXD_G1_RUNTIME_PARITY_REPORT.md](AXD_G1_RUNTIME_PARITY_REPORT.md), [AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md](AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md), [AXD_G2_FINAL_CLOSEOUT_STATUS.md](AXD_G2_FINAL_CLOSEOUT_STATUS.md), `axd-g2-v2-off-design3_1_run2-analysis.json`, `audit_results.json`, `quality.json`.

---

## Chương 7 · Đe dọa Tính hợp lệ, Đóng góp & Hướng phát triển (2–3 trang)
- **7.1 Threats to Validity:** Tổng hợp từ [TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md](TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md) (fixed cohort `SEED=555`, single host `Ryzen`, `jobs=1`, hai máy BUILD–SEARCH, không có PMU/RAPL, `v2_test_10000` thuộc `public 100K`, Cụm 2/3 dừng ở khảo sát).
- **7.2 Tổng kết đóng góp trung thực:** 5 trụ cột từ [TASK_D_SCIENTIFIC_CONTRIBUTIONS_AND_LIMITATIONS.md](TASK_D_SCIENTIFIC_CONTRIBUTIONS_AND_LIMITATIONS.md).
- **7.3 Hướng mở có điều kiện (`G3 NOT_OPENED`):** Chỉ nêu dưới dạng đề xuất tương lai (đồ thị đa gốc RNG độc lập, dataset thứ 2, cross-host `i5-14600KF`/server, phép đo single-host end-to-end, đối chứng native iQAN/ParlayANN, PMU profiling với quyền hợp lệ).
- **Bảng 7.1:** Bảng tổng hợp Threats to Validity, giới hạn suy luận & điều kiện mở rộng (`G3 NOT_OPENED`).
- **Evidence references:** [TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md](TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md), [TASK_D_SCIENTIFIC_CONTRIBUTIONS_AND_LIMITATIONS.md](TASK_D_SCIENTIFIC_CONTRIBUTIONS_AND_LIMITATIONS.md), [AXD_G2_CLOSEOUT_AND_G3_DECISION.md](AXD_G2_CLOSEOUT_AND_G3_DECISION.md), [I5_14600KF_REPLICATION_PROTOCOL.md](I5_14600KF_REPLICATION_PROTOCOL.md), [TASK_A_R4_R5_FEASIBILITY_REVIEW.md](TASK_A_R4_R5_FEASIBILITY_REVIEW.md).

---

## Tài liệu tham khảo & Phụ lục Tái lập (Reproducibility Appendix)
- **Tài liệu tham khảo:** PipeANN (OSDI '25), DiskANN (NeurIPS '19), Speed-ANN (2022), iQAN (PPoPP '23), ParlayANN (PPoPP '24), AverSearch (2025), LAANN (2026), FAISS GPU (2017), CAGRA (ICDE '24), FusionANNS (FAST '25), GraphIt (2018), Çatalyürek & Aykanat (TPDS '99), ADSampling (2023), FINGER, GINGER (2026), PiPNN & PiPNN II (2026), MARGO (PVLDB '25), GLIDE (ICDE '26), Big-ANN-Benchmarks (NeurIPS '21).
- **Phụ lục A:** Danh sách commit Git (`4bc70ff`, `d0f4816`), PRIVATE GitHub Release (`axd-g2-v2-design3.1-closeout-20261125`), bảng SHA-256 `9/9` assets và hướng dẫn chạy lại kiểm toán độc lập `scripts/audit_g2_v2_design3_1_final.py` ([AXD_G2_FINAL_CLOSEOUT_STATUS.md](AXD_G2_FINAL_CLOSEOUT_STATUS.md)).
- **Phụ lục B:** Ma trận Claim–Evidence đầy đủ ([TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md](TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md)).
