# Chỉ mục hình và bảng Task D

Mỗi chú thích bên dưới có thể chèn cùng hình vào báo cáo nhóm. Dùng SVG cho bản in, PNG khi phần mềm trình chiếu yêu cầu ảnh raster. Các số thập phân trong dữ liệu máy đọc dùng dấu chấm.

**Phạm vi dùng trong chỉ mục**

- **A** — Task A đo BUILD lịch sử trên Host A (tai-linux), 4 luồng, MS-Turing-1M, R90 P0A v1.3 Stock/Fast v2, ba lần dựng mỗi nhánh, cùng SEED=555.
- **D** — Task D đo SEARCH OFF trên Ryzen 5 PRO 4650U, một luồng truy vấn với hai worker, S=16, beam=432, trên chính sáu graph đó và 10.000 query test. Chỉ run2 đóng góp vào 144 process.
- **O** — Quality ON cùng cấu hình; 18 process gồm 12 test và 6 validation. Số đếm trung bình trong bảng là dữ liệu test ON. So sánh bit-exact có thêm baseline validation từ Stage 5.
- **M** — Tổng mô hình của BUILD trên A và Q lần mean SEARCH trên D. Mọi CI của mô hình giữ nguyên sáu thời gian BUILD. Transfer và load bị loại khỏi công thức.

## Hình

| Hình và định dạng | Đơn vị và phạm vi | Chú thích để ghép báo cáo | Dữ liệu và bằng chứng |
|---|---|---|---|
| **H01. Dòng thời gian** · [PNG](figures/fig01_research_timeline.png) · [SVG](figures/fig01_research_timeline.svg) | Ngày và verdict; nhiều chiến dịch | Từ baseline PipeANN đến hai cổng GO trên R90. Các HOLD lịch sử vẫn hiện diện; xem mốc từng giai đoạn trước khi so kết quả. | [T01](tables/table01_research_timeline.csv) · [Dòng thời gian](../../task-da/TASK_D_RESEARCH_TIMELINE.md) |
| **H02. Ba cụm song song** · [PNG](figures/fig02_parallel_ann_taxonomy.png) · [SVG](figures/fig02_parallel_ann_taxonomy.svg) | Phân loại; CPU, CPU–SSD, GPU | D01–D09 mô tả cơ chế theo pha và tài nguyên. D10 mô tả nhiều truy vấn đồng thời, có thể kết hợp với cả ba cụm. GPU có bằng chứng khảo sát. | [T02](tables/table02_taxonomy_d01_d10.csv) · [Tổng hợp §2–3](../../task-da/TASK_D_FINAL_RESEARCH_SYNTHESIS.md) |
| **H03. So sánh công trình** · [PNG](figures/fig03_prior_art_comparison.png) · [SVG](figures/fig03_prior_art_comparison.svg) | Định tính; ngữ cảnh mỗi bài | Đọc theo cột pha, cách song song, đồng bộ và chi phí. Dòng PipeANN có quan sát lịch sử riêng; dòng cuối là phép đo G2. | [T03](tables/table03_prior_art_comparison.csv) · [Đối chiếu prior art](../../task-da/H3_NOVELTY_AND_PRIOR_ART_AUDIT.md) · [Sổ kết quả](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md) |
| **H04. Từ giả thuyết tới quyết định** · [PNG](figures/fig04_research_workflow_decisions.png) · [SVG](figures/fig04_research_workflow_decisions.svg) | Cổng nghiên cứu qua nhiều cohort | Mỗi hàng gắn một lựa chọn với phép thử và quyết định; không gộp số liệu giữa SIFT, R86 và R90. | [T04](tables/table04_workflow_decisions.csv) · [Dòng thời gian](../../task-da/TASK_D_RESEARCH_TIMELINE.md) |
| **H05. Baseline BSP** · [PNG](figures/fig05_baseline_multiwalker_arch.png) · [SVG](figures/fig05_baseline_multiwalker_arch.svg) | Đỉnh, worker và vòng; D | Worker 0 phát seed; hai worker mở rộng trên trạng thái cục bộ. Sau barrier, worker 0 hợp nhất trước khi phát lượt mới. Sơ đồ lấy từ mã. | [p2_engine.hpp](../../../../research/task_da/search_common/p2_engine.hpp) · [Mã và bất biến](../../task-da/TASK_D_B1_A1_TECHNICAL_EXPLANATION.md) |
| **H06. B1 trước và sau** · [PNG](figures/fig06_b1_before_after.png) · [SVG](figures/fig06_b1_before_after.svg) | Số L2/truy vấn; D và O | Một đỉnh đã tính rồi bị loại được ghi vào local_newly_evaled. Công bố ID sau barrier giúp vòng sau bỏ qua. Con số cạnh sơ đồ so baseline với tổ hợp B1+A1. | [T09](tables/table09_on_l2_counters.csv) · [Mã và bất biến](../../task-da/TASK_D_B1_A1_TECHNICAL_EXPLANATION.md) |
| **H07. A1 trước và sau** · [PNG](figures/fig07_a1_before_after.png) · [SVG](figures/fig07_a1_before_after.svg) | Số seed/worker/vòng; D | Với S=16, một worker lấy tối đa 16 phần tử từ hàng đợi. Có thể giới hạn seed mà vẫn giữ thứ tự mở rộng. Sơ đồ 0/1 minh họa trạng thái, không phải dữ liệu thời gian. | [Mã và bất biến](../../task-da/TASK_D_B1_A1_TECHNICAL_EXPLANATION.md) · [p2_engine.hpp](../../../../research/task_da/search_common/p2_engine.hpp) |
| **H08. Thiết kế G2** · [PNG](figures/fig08_g2_experimental_design_2x2.png) · [SVG](figures/fig08_g2_experimental_design_2x2.svg) | Số process và block, µs/q, q/s; A, D, O | Hai nhánh graph × hai policy search. Mỗi ô có 36 process OFF. Mười hai block cân bằng tạo 72 cặp. Số ON ở từng ô là phần test, ngoài ra có 6 tiến trình val. | [T05](tables/table05_g2_2x2_arms_summary.csv) · [Kiểm toán G2](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) |
| **H09. Mean latency và các khoảng 95%** · [PNG](figures/fig09_mean_latency_and_cis.png) · [SVG](figures/fig09_mean_latency_and_cis.svg) | µs/truy vấn và % giảm; D | Chiều cao cột dùng trung bình số học, trục tung bắt đầu ở 3.000 µs. CI bên phải áp dụng cho giảm latency tương đối theo log-ratio ghép cặp. Đơn vị lặp thống kê khác nhau theo từng hàng. | [T05](tables/table05_g2_2x2_arms_summary.csv) · [T06](tables/table06_ci_families.csv) · [Thiết kế thống kê](../../task-da/AXD_G2_V2_STATISTICAL_DESIGN.md) · [Kiểm toán G2](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) |
| **H10. Độ trễ trung vị và đuôi** · [PNG](figures/fig10_latency_quantiles_p50_p95_p99.png) · [SVG](figures/fig10_latency_quantiles_p50_p95_p99.svg) | µs/truy vấn, %; D | P50/P95/P99 là trung bình các phân vị từng process ở jobs=1. P95/P99 có thêm upper bound ở cổng chất lượng hiệu năng. | [T07](tables/table07_latency_quantiles.csv) · [Kiểm toán G2](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) |
| **H11. QPS theo nhánh** · [PNG](figures/fig11_qps_comparison.png) · [SVG](figures/fig11_qps_comparison.svg) | Truy vấn/giây; D | Mỗi process xử lý lần lượt 10.000 truy vấn, hai worker cùng xử lý một query. QPS_wall tăng từ 276.25 lên 293.99 khi gộp sáu graph. | [T08](tables/table08_qps_by_arm.csv) · [Run2](../../task-da/AXD_G2_V2_DESIGN3_1_RESULTS.md) |
| **H12. L2 và already-seen** · [PNG](figures/fig12_duplicate_and_total_l2.png) · [SVG](figures/fig12_duplicate_and_total_l2.svg) | Phép tính hoặc lượt chặn/truy vấn; O | Mỗi query bớt 2,784.0351 phép L2 trùng và thêm cùng số lượt chặn already-seen. Count ON giải thích mức giảm công; tỷ trọng chu kỳ của từng pha OFF chưa được xác định. | [T09](tables/table09_on_l2_counters.csv) · [Kiểm toán G2](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) · [Tổng hợp §2–3](../../task-da/TASK_D_FINAL_RESEARCH_SYNTHESIS.md) |
| **H13. Từng graph và leave-one-out** · [PNG](figures/fig13_per_graph_r90_results.png) · [SVG](figures/fig13_per_graph_r90_results.svg) | % giảm, CI95, µs/q, q/s; D và O | Hiệu ứng ở cả sáu graph cùng dấu. Bỏ một graph mỗi lần cho khoảng điểm 6.023–6.040%. Khoảng này là kiểm tra độ nhạy, khác CI qua 12 block của mỗi graph. | [T10](tables/table10_per_graph_r90.csv) · [Kiểm toán G2](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) |
| **H14. Thời gian dựng chỉ mục** · [PNG](figures/fig14_measured_build_comparison.png) · [SVG](figures/fig14_measured_build_comparison.svg) | Giây/graph; A | Ba BUILD Stock trung bình 42.257 s và ba BUILD Fast v2 trung bình 33.793 s. RSS tham khảo từ tab R90_P0A_V13_NATIVE_24_RESULTS, theo GiB. Toàn bộ thuộc Task A. | [T11](tables/table11_measured_build_host_a.csv) · [Biên nhận BUILD](../../../../configs/axd_g2_v2_build_reference.json) |
| **H15. Thời gian mô hình hai máy** · [PNG](figures/fig15_modeled_two_host_build_search.png) · [SVG](figures/fig15_modeled_two_host_build_search.svg) | Giây theo số query Q; M | Ở Q=100.000, tổng mô hình giảm từ 404.244 s xuống 373.908 s; mức tiết kiệm là 30.336 s. Màu phân rã theo chênh BUILD và chênh SEARCH giữa hai ô của thiết kế. | [T12](tables/table12_modeled_two_host_build_search.csv) · [Kiểm toán G2](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) · [Tổng hợp §2–3](../../task-da/TASK_D_FINAL_RESEARCH_SYNTHESIS.md) |
| **H16. Ma trận đóng mục tiêu** · [PNG](figures/fig16_objective_closure_matrix.png) · [SVG](figures/fig16_objective_closure_matrix.svg) | 26 mục; lịch sử và hồ sơ | Màu thể hiện mức đáp ứng theo từng mục. Xem ma trận chữ để phân biệt trạng thái đầu việc với verdict của từng phép thử. E4 và E5 dành cho giảng viên. | [T13](tables/table13_objective_closure_summary.csv) · [Ma trận đầy đủ](TASK_D_OBJECTIVE_CLOSURE_MATRIX.md) |

## Bảng và dữ liệu nguồn

| Bảng | Đơn vị và phạm vi | Chú thích, phép tính và giới hạn | Nguồn kiểm tra |
|---|---|---|---|
| [T01](tables/table01_research_timeline.csv) · **Các mốc quyết định** | Ngày, verdict; nhiều cohort | 12 mốc chọn để minh họa quá trình thay đổi hướng. Thứ tự hàng theo giai đoạn, một số mốc chồng lấn thời gian. | [Dòng thời gian](../../task-da/TASK_D_RESEARCH_TIMELINE.md) |
| [T02](tables/table02_taxonomy_d01_d10.csv) · **D01–D10** | Mã phân loại; khảo sát | Ghi pha, tài nguyên, ví dụ, mức bằng chứng. D06 trong taxonomy là adaptive I/O width; D6 trong chẩn đoán lịch sử là FIFO head-of-line. | [Tổng hợp §2–3](../../task-da/TASK_D_FINAL_RESEARCH_SYNTHESIS.md) |
| [T03](tables/table03_prior_art_comparison.csv) · **Các hệ thống tham chiếu** | Định tính; theo bài | Cơ chế, trade-off và nhãn PAPER/OBS. Các công trình có phần cứng, recall và pha khác nhau. | [Sổ kết quả](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md) · [Đối chiếu prior art](../../task-da/H3_NOVELTY_AND_PRIOR_ART_AUDIT.md) |
| [T04](tables/table04_workflow_decisions.csv) · **Chuỗi quyết định** | Mốc và verdict | Mỗi hàng đi từ khoảng trống tới phép thử. E0 là mô hình, E2 là số liệu thực nghiệm chưa đủ chiến dịch. | [Dòng thời gian](../../task-da/TASK_D_RESEARCH_TIMELINE.md) |
| [T05](tables/table05_g2_2x2_arms_summary.csv) · **Bốn ô G2 và hai hàng gộp** | µs/q, q/s, count/q, CPU-s/process, KiB; D và O | Hai hàng overall là tổng hợp, không phải hai nhánh bổ sung. CPU time đo suốt đời process. CI bỏ trống ở baseline tự đối chiếu. | [Run2](../../task-da/AXD_G2_V2_DESIGN3_1_RESULTS.md) · [Kiểm toán G2](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) |
| [T06](tables/table06_ci_families.csv) · **Các họ CI** | Điểm và hai biên 95%, %; D | Primary block-t có df=11, drift có df=5, hai bootstrap đều 10.000 lần. Cột trống cho graph population mang nghĩa NOT_ESTIMABLE. | [Thiết kế thống kê](../../task-da/AXD_G2_V2_STATISTICAL_DESIGN.md) · [Kiểm toán G2](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) |
| [T07](tables/table07_latency_quantiles.csv) · **Mean và các phân vị** | µs/q, %; D | Mean là tỷ số số học mô tả. % của phân vị lấy từ log-ratio đã kiểm toán; chênh µs tính từ hai cột trung bình. | [Kiểm toán G2](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) |
| [T08](tables/table08_qps_by_arm.csv) · **QPS theo nhánh** | q/s, %; D | Gain bằng 100 × (opt/base − 1) từ QPS_wall. Đo batch tuần tự ở jobs=1. | [Run2](../../task-da/AXD_G2_V2_DESIGN3_1_RESULTS.md) |
| [T09](tables/table09_on_l2_counters.csv) · **Bộ đếm cơ chế** | count/q, rounds/q hoặc µs/q; O | Các tên kết thúc bằng _ns giữ nguyên tên counter gốc; giá trị đã chia 1.000 ở những dòng có unit µs/q. Bộ đếm test ON dùng giá trị đã hiệu chỉnh. | [Tổng hợp §2–3](../../task-da/TASK_D_FINAL_RESEARCH_SYNTHESIS.md) · [Kiểm toán G2](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) |
| [T10](tables/table10_per_graph_r90.csv) · **Sáu graph R90** | Recall@10, µs/q, q/s, %; D và O | Mỗi hàng có cận dưới recall, latency CI theo block và điểm LOO khi bỏ graph hiện tại. Không mặc định các lần build độc lập. | [Kiểm toán G2](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) |
| [T11](tables/table11_measured_build_host_a.csv) · **Sáu biên nhận BUILD** | Giây, byte, MiB; A | Khớp graph ID với thời gian BUILD, SHA-256 graph, builder ELF và receipt. Dùng r1–r3 làm ID hiện vật. | [Biên nhận BUILD](../../../../configs/axd_g2_v2_build_reference.json) |
| [T12](tables/table12_modeled_two_host_build_search.csv) · **Bốn workload trong mô hình** | Q và giây, %; M | Q=1, 100k, 1M có saved_s và CI ở JSON gốc; Q=10k tính từ means nên bỏ trống CI. ΔSEARCH dùng Stock+base trừ Fast+opt. Giá trị này gồm cả chênh giữa hai graph arm. | [Kiểm toán G2](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) · [Tổng hợp §2–3](../../task-da/TASK_D_FINAL_RESEARCH_SYNTHESIS.md) |
| [T13](tables/table13_objective_closure_summary.csv) · **Tóm tắt đóng mục tiêu** | 26 mục, 9 trạng thái | Tóm tắt phục vụ hình H16. Xem văn bản đối chiếu cho yêu cầu gốc, phương pháp, hạn chế và quyết định còn lại. | [Ma trận đầy đủ](TASK_D_OBJECTIVE_CLOSURE_MATRIX.md) |
| [T14](tables/table14_axd_canonical_integration.json) · **Bảng số chuẩn A×D** | Số đo A, D, O và dự báo M | JSON gom sáu graph kèm SHA, bốn ô BUILD/SEARCH, recall và hai gate, CI và interaction, các workload với T(Q) và ΔT. Dùng bảng này khi ghép số liệu giữa hai thành viên. | [Biên nhận BUILD](../../../../configs/axd_g2_v2_build_reference.json) · [Kiểm toán G2](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md) · [Tổng hợp §2–3](../../task-da/TASK_D_FINAL_RESEARCH_SYNTHESIS.md) |

## Tái lập từ dữ liệu đã lưu

Chạy từ thư mục gốc repository. Lệnh đầu chỉ cần Python 3, Pillow và font DejaVu Sans/Mono theo đường dẫn trong script. Thư mục đích tạo mới giúp đối chiếu byte mà vẫn giữ được bản bàn giao ban đầu. H05–H07 là sơ đồ mã nguồn, các nhãn định tính và bố cục của chúng nằm trong script.

```bash
workdir=$(mktemp -d)
python3 docs/research/final-handoff/task-d/tables/generate_figures.py --output "$workdir/figures"
diff -qr docs/research/final-handoff/task-d/figures "$workdir/figures"
```

Để tái trích T01–T14, cần checkout này cùng ba JSON riêng tư ở thư mục evidence đã lưu trữ. Exporter kiểm tra SHA-256 của analysis, audit, quality và build reference trước khi ghi. Các bảng lịch sử, taxonomy và mục tiêu là dữ liệu biên tập trong exporter, có nguồn đối chiếu trong chỉ mục trên. Khi chỉ có compact bundle, dùng trực tiếp các bảng đã bàn giao để dựng hình.

```bash
python3 docs/research/final-handoff/task-d/tables/export_verified_tables.py --evidence ../artifact-evidence --output "$workdir/tables"
for table in "$workdir"/tables/table*; do
    cmp "$table" "docs/research/final-handoff/task-d/tables/$(basename "$table")" || exit 1
done
```

[Script xuất bảng](tables/export_verified_tables.py) · [Script dựng hình](tables/generate_figures.py) · [Chỉ mục chứng cứ](TASK_D_EVIDENCE_INDEX.md)
