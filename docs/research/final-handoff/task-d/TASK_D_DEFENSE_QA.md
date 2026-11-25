# Phản biện Task D

36 câu hỏi dùng khi trao đổi với giảng viên. Đọc câu trả lời trực tiếp trước, mở phần giải thích khi người nghe hỏi về cơ chế hoặc phạm vi. Các liên kết trỏ vào tài liệu nội bộ tại mốc `a0916db`.

## Câu hỏi nghiên cứu và khảo sát

### 1. ANN là gì và đo độ đúng thế nào?

**Trả lời trực tiếp.** ANN tìm các vector gần query với chi phí thấp hơn tìm kiếm vét cạn. Recall@10 đo mức trùng với top-10 chuẩn.

**Giải thích kỹ thuật.** Với một query, lấy số ID nằm trong cả danh sách trả về và danh sách mười láng giềng chuẩn, rồi chia cho 10. Điểm chất lượng của panel là trung bình theo query. Khoảng cách bình phương L2 vẫn xác định cùng thứ tự như L2 khi so vector hữu hạn.

**Tuyên bố cần tránh.** Đồng nhất recall trung bình cao với đúng tuyệt đối cho từng query. [Minh chứng](../../task-da/AXD_G2_V2_QUALITY_RESULTS.md)

### 2. Vì sao cần song song bên trong truy vấn?

**Trả lời trực tiếp.** Nhiều worker có thể mở rộng các đỉnh khác nhau khi cần giảm thời gian trả lời một query.

**Giải thích kỹ thuật.** Lợi ích phụ thuộc vào số ứng viên sẵn sàng đồng thời, công lặp và thời gian chờ nhau. Nếu đường phụ thuộc dài hoặc tăng worker làm tăng L2 trùng, độ trễ có thể tăng. Thiết kế jobs=1 của G2 cô lập câu hỏi này với áp lực nhiều người dùng.

**Tuyên bố cần tránh.** Suy từ số lõi ra tăng tốc tuyến tính. [Minh chứng](../../task-da/TASK_D_B1_A1_TECHNICAL_EXPLANATION.md)

### 3. Vì sao dùng graph-based ANN?

**Trả lời trực tiếp.** Đồ thị cho phép theo dõi từng lần mở rộng và từng lần hai walker cùng gặp một vector.

**Giải thích kỹ thuật.** Task A đã bàn giao graph có provenance và ground truth phù hợp. Cùng đồ thị, Task D có thể đổi cách xử lý frontier và visited trong engine, giữ nguyên input, thứ tự cạnh và metric. Nhờ vậy ta có đối chứng theo từng query cho giả thuyết công lặp.

**Tuyên bố cần tránh.** Tuyên bố đồ thị luôn tốt hơn IVF hoặc các họ chỉ mục khác. [Minh chứng](../../task-da/AXD_G1_GRAPH_ARTIFACT_MANIFEST.md)

### 4. Khoảng trống cụ thể nằm ở đâu?

**Trả lời trực tiếp.** Chưa rõ giảm công lặp ở barrier và cấp ít seed hơn có tạo lợi ích ròng tại chất lượng cố định trên graph của Task A hay không.

**Giải thích kỹ thuật.** Cách đặt câu hỏi buộc tối ưu qua hai phép kiểm: đầu ra trong cùng graph phải khớp, và latency OFF phải giảm sau khi tính cả chi phí đánh dấu và merge. Nếu chỉ thấy counter thay đổi thì câu hỏi về lợi ích trên đường thực thi vẫn chưa được giải đáp.

**Tuyên bố cần tránh.** Đồng nhất khoảng trống định lượng trong tích hợp này với một nguyên lý thuật toán chưa từng có. [Minh chứng](../../task-da/TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md)

### 5. Vì sao không chọn GPU làm trọng tâm thực nghiệm?

**Trả lời trực tiếp.** Bài toán tích hợp được chốt trên graph Task A và engine CPU. Cụm GPU cung cấp đối chiếu về cách khai thác song song.

**Giải thích kỹ thuật.** Khảo sát có FAISS GPU và CAGRA. Một phép so sánh GPU cần workload, batch, VRAM và baseline GPU tương thích. G2 đóng băng một cấu hình CPU jobs=1. Thay phần cứng sẽ đặt ra một câu hỏi khác. Trạng thái của cụm GPU là SURVEY_COMPLETE với 0 benchmark GPU.

**Tuyên bố cần tránh.** Xếp hạng CPU nhanh hơn GPU bằng số liệu khác workload. [Minh chứng](../../task-da/TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md)

### 6. Vì sao rời nhánh AverSearch?

**Trả lời trực tiếp.** Trong E0, ưu thế của điều phối động phụ thuộc rất mạnh vào chi phí chuyển vai trò. E2 còn bị tuần tự hóa khi bảo trì hàng đợi.

**Giải thích kỹ thuật.** Trên 108 cấu hình mô hình, so chính sách động với phương án tĩnh tốt hơn trong từng ô cho 3 thắng, 15 hòa, 90 thua. Trên nguyên mẫu một mutex, Fixed-1 đạt 19.21 QPS, Adaptive-3 đạt 15.09 và Fixed-2 đạt 10.72. Chiến dịch E2 dừng ở ngưỡng nhiệt. E3 chỉ qua fixture.

**Tuyên bố cần tránh.** Gọi kết quả E0 là throughput thực hoặc tuyên bố phủ định AverSearch gốc. [Minh chứng](../../task-da/TASK_D_RESEARCH_TIMELINE.md)

### 7. Tại sao dừng TP-CG?

**Trả lời trực tiếp.** Điều kiện để đầu tư cho bộ lập lịch động chưa đạt, và các cơ chế đề xuất đã gần với prior art.

**Giải thích kỹ thuật.** Khi chuyển global merge từ set sang mảng phẳng, hơn nửa khoảng cách scaling ban đầu biến mất. Phần dư có thể thu từ chỉnh S tĩnh chỉ ở mức nhỏ. Một bộ điều khiển phải còn đủ lợi ích để trả chi phí quan sát và ra quyết định. P5 giữ NOT_OPENED, TP-CG giữ PIVOT.

**Tuyên bố cần tránh.** Mô tả TP-CG là thuật toán đã triển khai và benchmark thất bại. [Minh chứng](../../task-da/POST_STAGE_DE_AUDIT_AND_H3_PIVOT_PLAN.md)

### 8. Vì sao hướng H3 gán seed theo overlap nhận NO-GO?

**Trả lời trực tiếp.** Seed đầu round dự báo kém nơi phát sinh phần lớn các phép tính trùng còn lại.

**Giải thích kỹ thuật.** Qua 6,095 round R86 A3 sau B1+A1, 79–80% duplicate L2 còn lại có hai đầu đều phát sinh trong round. Phần seed–seed chỉ chiếm 0.33% tổng L2. Sketch 128-bit thua cách cân bằng degree khoảng 0.97–1.12% và tốn 28.5–29.7 µs/query. Đây là sàng lọc offline cho một cơ chế, cấu hình và cohort xác định.

**Tuyên bố cần tránh.** Đổi mẫu số của 0.33% sang duplicate L2 hoặc bác bỏ mọi lịch dựa vào topology. [Minh chứng](../../task-da/H3_OVERLAP_SIGNAL_SCREENING_RESULTS.md)

## Cơ chế và tính đúng đắn

### 9. B1 làm gì và còn sót loại trùng nào?

**Trả lời trực tiếp.** B1 công bố tất cả đỉnh đã được tính khoảng cách khi các worker gặp nhau ở barrier.

**Giải thích kỹ thuật.** Trong round, mỗi worker tích lũy các ID vào local_newly_evaled. Cuối round, coordinator đánh dấu settled_epoch_ theo query. Ở round sau worker có thể bỏ lần tính lại cùng ID. Hai worker trong cùng round vẫn có thể khám phá cùng một ID trước lần công bố kế tiếp.

**Tuyên bố cần tránh.** Tuyên bố xóa mọi phép L2 trùng. [Minh chứng](../../task-da/TASK_D_B1_A1_TECHNICAL_EXPLANATION.md)

### 10. A1 thay đổi bước nào?

**Trả lời trực tiếp.** A1 giữ cờ expanded trong beam và giảm số seed cần chuẩn bị cho round kế.

**Giải thích kỹ thuật.** Baseline dựng lại active frontier rồi đưa nhiều seed vào local_pending. Mỗi worker chỉ có ngân sách S lần pop nên thứ tự phát xác định cho phép dừng sau tối đa p × S seed. Ở G2 con số này là 32. Thao tác tìm kiếm ứng viên mới trong round vẫn tiếp tục theo quy tắc của engine.

**Tuyên bố cần tránh.** Coi 32 là giới hạn tổng số phép L2 trên mỗi round. [Minh chứng](../../task-da/TASK_D_B1_A1_TECHNICAL_EXPLANATION.md)

### 11. Bằng chứng nào cho việc giữ đúng kết quả?

**Trả lời trực tiếp.** Cơ chế giữ quy tắc chọn và mở rộng đỉnh, rồi kiểm tra bit-exact xác nhận trên cohort.

**Giải thích kỹ thuật.** Với top-B đã đầy, ngưỡng cặp (khoảng cách, ID) tệ nhất chỉ chặt hơn. Một ứng viên đã trượt ngưỡng này không cần tính lại ở vòng sau khi query, graph và metric cố định. Với cấp seed có thứ tự, mỗi worker chỉ có S lượt mở rộng. Thực nghiệm kiểm cả top-10 ordered IDs, squared L2, unique L2 và expansions giữa hai policy.

**Tuyên bố cần tránh.** Suy rằng hai loại graph Fast và Stock trả kết quả bit-exact với nhau. [Minh chứng](../../task-da/TASK_D_B1_A1_TECHNICAL_EXPLANATION.md)

### 12. B1+A1 có phải thuật toán ANN mới?

**Trả lời trực tiếp.** Hồ sơ định vị B1+A1 là tối ưu đường cơ sở của một engine BSP.

**Giải thích kỹ thuật.** Visited marking, cập nhật frontier và batching có quan hệ rõ với prior art trong graph traversal. Phần có bằng chứng là cách cài hai thay đổi trong engine cụ thể, kiểm tra điều kiện giữ quỹ đạo và định lượng tác dụng qua ON/OFF trên graph bàn giao.

**Tuyên bố cần tránh.** Tuyên bố nguyên lý truy vấn mới hoặc ưu việt trước mọi engine. [Minh chứng](../../task-da/H3_NOVELTY_AND_PRIOR_ART_AUDIT.md)

### 13. Vì sao duplicate L2 giảm 74.98% nhưng độ trễ chỉ giảm 6.03%?

**Trả lời trực tiếp.** 74.98% áp cho công tính trùng, vốn chỉ là một phần của tổng số phép L2 và tổng thời gian.

**Giải thích kỹ thuật.** Baseline có 3,712.81 L2 trùng trong 22,776.97 L2/query. Sau tối ưu còn 928.77 L2 trùng. Chênh khoảng 2,784 phép chỉ tương ứng 12.22% tổng L2. Duyệt cạnh, hàng đợi, đồng bộ và phần công mới của B1 đều đi vào đồng hồ OFF. G2 chưa tách được số µs do riêng B1 và A1 tiết kiệm.

**Tuyên bố cần tránh.** Nhân tỷ lệ giảm counter với latency để suy phần thời gian của một pha. [Minh chứng](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md)

### 14. Có biết nguyên nhân p=4 thiếu ổn định không?

**Trả lời trực tiếp.** Đo được mức cải thiện phụ thuộc cấu hình. Nguyên nhân phần cứng chi tiết còn mở.

**Giải thích kỹ thuật.** Ở pilot R86, khoảng tin cậy tại p=4 chứa 0 và A3-R1/p4/S8 có p95 tăng 5.2%. Bốn worker trải hai miền CCX có thể làm chi phí phối hợp khác đi. PMU chưa cung cấp bằng chứng nhân quả cho cơ chế này. G2 chính thức dùng p=2.

**Tuyên bố cần tránh.** Khẳng định cache miss xuyên CCX gây ra toàn bộ biến động. [Minh chứng](../../task-da/B1_A1_PILOT_HANDOFF_20261119.md)

### 15. Vì sao dùng p=2, S=16?

**Trả lời trực tiếp.** Đây là điểm vận hành đã có tín hiệu trên R86 và được chọn trước cho phép kiểm hẹp R90.

**Giải thích kỹ thuật.** R86 A3 ở hai worker và 16 bước mỗi round có giảm độ trễ trong từng build với output parity, trong khi p=4 thiếu ổn định. G2 khóa p, S, jobs=1 và beam 432 trước khi đo. So sánh trong ô cố định giúp kiểm tác dụng đổi policy mà không đồng thời đổi ngân sách worker.

**Tuyên bố cần tránh.** Gọi đây là cấu hình tối ưu toàn cục. [Minh chứng](../../task-da/AXD_G2_PREREG_V2.md)

## Thiết kế, chất lượng và thống kê

### 16. Tại sao chọn MS-Turing-1M?

**Trả lời trực tiếp.** Đây là dataset chung có graph và receipts Task A để ghép đối chứng BUILD với SEARCH.

**Giải thích kỹ thuật.** Cùng dữ liệu vector, panel query, ground truth và loader giữ định danh đỉnh, ta có thể kiểm parity trên toàn cohort R90. Tập v2_test_10000 tách khỏi validation và các panel nhỏ của D nhưng xuất phát từ public 100K từng được dùng trong lịch sử. Kết quả vẫn mang nhãn thăm dò trên host cụ thể.

**Tuyên bố cần tránh.** Gọi panel là một holdout mới hoàn toàn đối với cả dự án. [Minh chứng](../../task-da/AXD_G2_V2_QUERY_SPLIT_AUDIT.md)

### 17. Recall thay đổi bao nhiêu?

**Trả lời trực tiếp.** Trong cùng graph, hai policy cho cùng kết quả trên các phép đối chiếu. Recall trung bình gộp là 0.992108.

**Giải thích kỹ thuật.** Gate A đòi cận dưới đồng thời trên cả sáu graph đạt 0.990, mức nhỏ nhất là 0.991188. Gate B kiểm hiệu recall trung bình Fast–Stock với biên đã định, CI95 [−0.000051, +0.000284] nằm trong ±0.0005. Tuyên bố theo Gate B chỉ áp cho recall trong thiết kế này.

**Tuyên bố cần tránh.** Suy từ Gate B rằng latency, topology hoặc mọi metric giữa Fast và Stock đều tương đương. [Minh chứng](../../task-da/AXD_G2_V2_QUALITY_RESULTS.md)

### 18. Tại sao tách Quality ON và Performance OFF?

**Trả lời trực tiếp.** Bật bộ đếm giúp kiểm cơ chế nhưng thay đổi chi phí quan sát. Độ trễ được lấy từ engine chạy OFF.

**Giải thích kỹ thuật.** ON ghi các counter công việc. OFF bỏ trường counters, đo thời gian theo cấu hình chính thức. Digest top-10 ordered IDs và squared L2 của mỗi tiến trình OFF khớp chuẩn Quality ON. Do đó có móc nối giữa tính đúng và thời gian trong khi vẫn bảo toàn điều kiện đo.

**Tuyên bố cần tránh.** Cộng timer ON thành độ trễ OFF. [Minh chứng](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)

### 19. 20,000 truy vấn có quan hệ gì với 1,620,000 bản ghi?

**Trả lời trực tiếp.** 20,000 là số query phân biệt. 1,620,000 đếm các lần query được thực thi lặp lại trên graph, policy và block.

**Giải thích kỹ thuật.** Có 10k query test và 10k validation. V2 tạo 180,000 bản ghi ON mới và 1,440,000 OFF. OFF gồm 144 tiến trình, mỗi tiến trình 10k bản ghi test. Lặp query là chủ ý của thiết kế cặp, nên không thể gán cho từng dòng tính độc lập của một query mới.

**Tuyên bố cần tránh.** Nói đã thử 1.62 triệu người dùng hoặc query độc lập. [Minh chứng](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md)

### 20. 120,000 so sánh parity ON và 144/144 parity OFF là gì?

**Trả lời trực tiếp.** ON đối chiếu kết quả từng query. OFF đối chiếu digest đầu ra theo tiến trình.

**Giải thích kỹ thuật.** 60k ON test ghép sáu graph × 10k query × hai policy thành 60k cặp. 60k validation đối chiếu policy tối ưu với baseline beam 432 đã có tại Stage 5. Ở OFF, từng tiến trình trong 144 tiến trình có digest theo đúng thứ tự ID và squared L2 trùng với chuẩn ON. Hai con số có đơn vị đếm khác nhau.

**Tuyên bố cần tránh.** Gọi 120,000 là số query phân biệt hoặc 144 là số query. [Minh chứng](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)

### 21. Tại sao cần khoảng tin cậy khi đã chạy đủ 144 lượt?

**Trả lời trực tiếp.** Lịch chạy đầy đủ cho số quan sát. Khoảng tin cậy cho biết độ bất định của phép ước lượng trong thiết kế đó.

**Giải thích kỹ thuật.** Các cặp nằm trong 12 block cân bằng theo graph và thứ tự. Primary block-t df=11 cho CI95 giảm [5.976580%, 6.089687%]. Cận dưới so với ngưỡng 3% quyết định độ chắc của lợi ích trong cohort. Nếu lấy mọi dòng query lặp làm quan sát độc lập, khoảng tin cậy có thể quá hẹp.

**Tuyên bố cần tránh.** Diễn giải 95% thành 95% graph tương lai sẽ đạt mức cải thiện này. [Minh chứng](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)

### 22. Query-only, joint bootstrap và drift khác nhau thế nào?

**Trả lời trực tiếp.** Mỗi phép đổi nguồn bất định đang được mô tả.

**Giải thích kỹ thuật.** Drift block-t ghép 12 block thành 6 cặp block kề nhau (df=5). Query-only lấy mẫu lại các cụm query trên những run đã có và cho [5.970252%, 6.095760%]. Joint bootstrap thêm biến thiên lặp tiến trình và cho [5.954283%, 6.113015%]. Các khoảng phần trăm đều giữ cohort graph cố định.

**Tuyên bố cần tránh.** Lấy CI bootstrap thay cho một CI quần thể graph. [Minh chứng](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md)

### 23. Vì sao hai lần HOLD không nối vào run2?

**Trả lời trực tiếp.** Giao thức cần một lịch đầy đủ có thứ tự đã định và guard hợp lệ. Mỗi lần dừng có nguyên nhân và biên bản riêng.

**Giải thích kỹ thuật.** Ở design-3, parser nhầm trường counters bị bỏ với giá trị null. Design-3.1 run1 hoàn thành 119 lượt sạch rồi dừng ở #120 do tải CPU ngoại lai 0.0266 vượt ngưỡng 0.0250. Chỉ dùng đầy đủ run2 tránh việc lựa chọn hoặc ghép hậu nghiệm những đoạn thuận lợi. Các bundle cũ vẫn phục vụ audit.

**Tuyên bố cần tránh.** Gọi các lượt HOLD là outlier đã bỏ vì quá chậm. [Minh chứng](../../task-da/TASK_D_RESEARCH_TIMELINE.md)

### 24. Tại sao graph_population_ci = NOT_ESTIMABLE?

**Trả lời trực tiếp.** Sáu graph không cung cấp sáu gốc RNG độc lập cho phép suy rộng đó.

**Giải thích kỹ thuật.** Ba Stock và ba Fast là các lần build có cùng seed 555, với bất định do bốn luồng. Lặp thêm query hay nhiều process trên chính sáu graph chỉ tăng thông tin trong cohort đã chọn. Muốn ước lượng quần thể build cần thiết kế lấy mẫu gốc độc lập kèm phân tích ở cấp build.

**Tuyên bố cần tránh.** Coi ba build mỗi arm như ba mẫu seed độc lập. [Minh chứng](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)

## Tích hợp, đóng góp và giới hạn

### 25. Task A đã cải thiện điều gì?

**Trả lời trực tiếp.** Task A giảm thời gian dựng graph R90 P0A v1.3 khoảng 20.03% trên Host A.

**Giải thích kỹ thuật.** Fast v2 tối ưu khâu BUILD ở cấu hình C160/K1024/N2. Sáu receipts lịch sử, ba mỗi arm, cho trung bình 42.257 s ở Stock và 33.793 s ở Fast. Chênh 8.463 s dùng giá trị trước làm tròn. Công việc xây dựng và đo BUILD thuộc Task A.

**Tuyên bố cần tránh.** Quy 20.03% BUILD cho B1+A1 hoặc thay receipts R90 bằng kết quả R91. [Minh chứng](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md)

### 26. Task D đã cải thiện điều gì?

**Trả lời trực tiếp.** Task D giảm độ trễ SEARCH trung bình 6.033151% trong cohort sáu graph R90.

**Giải thích kỹ thuật.** Phép so chính là baseline với B1+A1 trên cùng graph, p=2 và jobs=1. P95 giảm khoảng 4.22%, P99 giảm 4.09%, QPS_wall tăng 6.42%. Cặp số 3,619.71 và 3,401.33 µs là mô tả trung bình gộp. Ước lượng chính tính theo log-ratio ghép cặp.

**Tuyên bố cần tránh.** Đổi mức giảm latency thành mức tăng QPS bằng cùng một tỷ lệ. [Minh chứng](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md)

### 27. Hai cải tiến có cộng hưởng hay hoàn toàn độc lập không?

**Trả lời trực tiếp.** G2 chưa phát hiện tương tác SEARCH khác 0 trong phép so đã định.

**Giải thích kỹ thuật.** Tính mức giảm latency do B1+A1 trên các graph Fast rồi trừ mức giảm trên các graph Stock. Chênh +0.037 µs, CI95 [−2.582, +2.655] µs bao gồm cả hai dấu. Kết quả tương thích với xấp xỉ cộng tính trong điều kiện kiểm tra. Phép kiểm chất lượng recall với biên riêng không thay thế phép kiểm tương đương SEARCH.

**Tuyên bố cần tránh.** Tuyên bố có cộng hưởng, chứng minh độc lập tuyệt đối hoặc tương đương latency. [Minh chứng](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)

### 28. Mô hình BUILD–SEARCH có phải thời gian chạy end-to-end thực tế?

**Trả lời trực tiếp.** Đây là dự báo hai host có điều kiện trên sáu receipts BUILD cố định.

**Giải thích kỹ thuật.** T(Q) = BUILD_A + Q × mean_SEARCH_D, với SEARCH đổi ra s/query. So fast_opt với stock_base ở Q=100k cho 404.244 s và 373.908 s, tiết kiệm 30.336 s. Chi phí truyền và nạp chỉ mục nằm ngoài công thức. Chênh cửa sổ process và batch bao gồm nhiều hoạt động, nên không dùng để gán đơn giá load hoặc transfer.

**Tuyên bố cần tránh.** Gọi 30.336 s là tổng runtime hoặc tuyên bố đo single-host end-to-end. [Minh chứng](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)

### 29. Sáu phần trăm có ý nghĩa khoa học gì?

**Trả lời trực tiếp.** Nó trả lời một giả thuyết có ngưỡng định trước, kèm kiểm tra chất lượng và chi phí.

**Giải thích kỹ thuật.** Ở cùng điểm vận hành, cận dưới của primary, drift và joint CI vượt ngưỡng giảm 3%. Mức giảm quan sát đi cùng mẫu counter dự kiến và đầu ra khớp. Đó là bằng chứng thực nghiệm cho chi phí của công lặp trong engine này. Giá trị kinh tế thực tế còn phụ thuộc workload triển khai.

**Tuyên bố cần tránh.** Gọi 6% là cải thiện phổ quát, hoặc đổi thành mức tiết kiệm tiền khi thiếu mô hình chi phí. [Minh chứng](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)

### 30. Đóng góp học thuật nào có bằng chứng?

**Trả lời trực tiếp.** Hồ sơ cho thấy có khảo sát cơ chế, giả thuyết có thể bác bỏ và một phép đo tích hợp tái kiểm được.

**Giải thích kỹ thuật.** Task D đối chiếu ba cụm, lưu cả các kết quả âm, thiết kế đối chứng ON/OFF giữ đầu ra, và công khai phạm vi trong báo cáo nội bộ. Trên graph Task A bàn giao, thiết kế 2×2 định lượng mức giảm công lặp và latency. Đây là đóng góp nghiên cứu hệ thống; vị trí của nó trong tiêu chí học phần cần giảng viên xác nhận.

**Tuyên bố cần tránh.** Đồng nhất đóng góp thực nghiệm với phát minh thuật toán hay nghiệm thu của thầy. [Minh chứng](../../task-da/TASK_D_SCIENTIFIC_CONTRIBUTIONS_AND_LIMITATIONS.md)

### 31. Vì sao chưa mở G3?

**Trả lời trực tiếp.** G2 đã trả lời câu hỏi trên cohort cố định. G3 sẽ cần một câu hỏi và nguồn lực mới.

**Giải thích kỹ thuật.** Nếu cần kết luận cho host thứ hai, dataset thứ hai hoặc quần thể build, phải xác định đối chứng mới, đơn vị lấy mẫu và điều kiện tài nguyên. AUDIT_PASS và 9/9 assets được xác minh bảo đảm khả năng đối soát kết quả hiện tại. Giữ G2 CLOSEOUT COMPLETE, RESEARCH PAUSED, G3 NOT_OPENED.

**Tuyên bố cần tránh.** Diễn giải GO_A hoặc GO_B thành phê duyệt tự động một thực nghiệm mới. [Minh chứng](../../task-da/AXD_G2_CLOSEOUT_AND_G3_DECISION.md)

### 32. Nếu thầy yêu cầu thêm thí nghiệm, cần chứng minh điều gì?

**Trả lời trực tiếp.** Cần chốt phát biểu mà bằng chứng hiện tại còn thiếu trước khi chọn phép thử.

**Giải thích kỹ thuật.** Ví dụ, để tách công của B1 khỏi A1 trên R90 cần đối chứng baseline, B1-only, A1-only và combo ở cùng chất lượng. Muốn suy rộng quần thể graph thì thêm biến thiên độc lập ở cấp build. Muốn nói về triển khai đầu–cuối thì đo đầy đủ BUILD, truyền, nạp và SEARCH trong môi trường xác định. Đó là các đề cương tương ứng với ba câu hỏi khác nhau.

**Tuyên bố cần tránh.** Cam kết đã hoặc sẽ chạy ngay sau buổi bảo vệ. [Minh chứng](../../task-da/TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md)

### 33. Process CPU time giảm có cho biết tiết kiệm năng lượng hay thời gian CPU chỉ riêng search không?

**Trả lời trực tiếp.** Process CPU time giảm 7.07% trong cửa sổ cả tiến trình. Năng lượng vẫn chưa được đo.

**Giải thích kỹ thuật.** Mẫu /proc bao trùm cả các công việc ngoài batch query như khởi tạo, warmup và ghi kết quả. Peak RSS thay đổi khoảng +9.4 KiB. Thiếu watt hoặc joule/query, và thời gian tường của một truy vấn dùng hai worker khác với tổng CPU time qua các worker.

**Tuyên bố cần tránh.** Gọi CPU time này là search-only CPU hoặc tiết kiệm 7.07% năng lượng. [Minh chứng](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md)

### 34. Vì sao phase observer vẫn NOT_VALIDATED dù điểm ước lượng chỉ −1.717%?

**Trả lời trực tiếp.** Cả CI phải nằm trong biên ±2%. Cận dưới −2.851% nằm ngoài biên.

**Giải thích kỹ thuật.** CI95 là [−2.851%, −0.570%]. Điểm ước lượng riêng lẻ nằm trong ngân sách nhưng phép kiểm tương đương chưa đạt. Một số khoảng đo pha còn chồng lấp theo worker. Vì thế vẫn dùng OFF làm chuẩn latency, ON để mô tả cơ chế.

**Tuyên bố cần tránh.** Nói điểm −1.717% vượt biên hoặc quy toàn bộ chênh lệch latency cho một timer. [Minh chứng](../../task-da/MEASUREMENT_VALIDITY_AND_PHASE_AUDIT.md)

### 35. R86 và R90 có thể ghép chung để có thêm graph không?

**Trả lời trực tiếp.** Chúng trả lời hai thiết kế khác nhau và cần giữ verdict riêng.

**Giải thích kỹ thuật.** R86 A3-R2/R3 p=2 S=16 giảm theo từng build 12.29% và 10.08%, nhưng CI ngoài hai build [−2.84%, +25.21%] nên HOLD. R90 P0A v1.3 có graph, beam, panel và quy tắc G2 riêng. R91 thuộc ngoài cohort G2. Trộn các giai đoạn sẽ làm mất estimand đã đăng ký.

**Tuyên bố cần tránh.** Lấy trung bình 10–12% R86 với 6% R90 hoặc dùng R91 thay R90. [Minh chứng](../../task-da/B1_A1_NARROW_REPLICATION_REPORT_20261119.md)

### 36. Hai sửa số lịch sử nào cần lưu ý khi viết slide nhóm?

**Trả lời trực tiếp.** Dùng chênh counter đã kiểm toán và ghi 30.336 s, 227.194 s là số giây tiết kiệm theo mô hình.

**Giải thích kỹ thuật.** Đối soát ON cho already_seen tăng 2,784.0351/query, khớp một đổi một với duplicate L2 giảm. Merge timer ON đi từ 348.5078 lên 384.3943 µs/query. Ở Q=1M, tổng mô hình từ 3,662.131 xuống 3,434.938 s, chênh 227.194 s trước làm tròn. Dùng số đầy đủ khi tính rồi làm tròn để trình bày.

**Tuyên bố cần tránh.** Chép số ghi tay cũ hoặc ghi chênh tiết kiệm làm thời gian chạy. [Minh chứng](../../task-da/TASK_D_FINAL_RESEARCH_SYNTHESIS.md)
