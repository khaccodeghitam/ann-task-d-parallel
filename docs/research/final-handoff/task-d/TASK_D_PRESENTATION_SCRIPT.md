# Trình bày Task D trước giảng viên

[PowerPoint 12 slide với ghi chú người nói](TASK_D_ADVISOR_PRESENTATION.pptx) · [PDF để trình chiếu](TASK_D_ADVISOR_PRESENTATION.pdf) · [Câu hỏi phản biện](TASK_D_DEFENSE_QA.md) · [Phiếu quyết định](TASK_D_FINAL_ADVISOR_DECISION_CHECKLIST.md)

Bản nhóm **5:00** dùng slide 1, 3, 4, 5, 6, 8, 10. Bản cá nhân **11:55** dùng slide 1–10. Slide 11–12 dành cho phản biện ngoài thời lượng chính. Thời lượng gồm cả thời gian chỉ vào hình và chuyển trang. Các slide trọng tâm là 4 (cơ chế), 6 (SEARCH) và 8 (tích hợp).

| Slide | Nội dung | Bản nhóm | Bản cá nhân |
|---:|---|---:|---:|
| 1 | Tổng quan | 0:00–0:25 | 0:00–0:40 |
| 2 | Khảo sát | Bỏ qua | 0:40–1:45 |
| 3 | Giả thuyết | 0:25–1:05 | 1:45–3:05 |
| 4 | Cơ chế | 1:05–2:00 | 3:05–4:35 |
| 5 | Thiết kế G2 | 2:00–2:45 | 4:35–5:50 |
| 6 | Kết quả chính | 2:45–3:35 | 5:50–7:05 |
| 7 | Kết quả cơ chế | Bỏ qua | 7:05–8:15 |
| 8 | Tích hợp A × D | 3:35–4:30 | 8:15–9:45 |
| 9 | Đóng mục tiêu | Bỏ qua | 9:45–10:50 |
| 10 | Quyết định | 4:30–5:00 | 10:50–11:55 |
| 11 | Dự phòng | Dự phòng | Dự phòng |
| 12 | Dự phòng | Dự phòng | Dự phòng |

## Slide 1. Khi hai worker cùng tìm láng giềng gần nhất

**Thông điệp trên màn hình.** Task D nghiên cứu cách chia việc trong một truy vấn trên đồ thị ANN. Trên sáu đồ thị R90 cố định, B1+A1 giảm độ trễ tìm kiếm trung bình 6.033151% và giữ nguyên kết quả top-10.

**Lời nói bản 5 phút.** Thưa thầy, Task D khảo sát cách thực thi song song một truy vấn tìm láng giềng gần nhất trên đồ thị. Khi hai worker đi theo hai đường khác nhau, cả hai có thể gặp cùng một đỉnh. Em muốn biết có thể giảm phép tính lặp mà vẫn giữ đúng kết quả top-10 hay không. Trên sáu graph cố định của Task A, mức giảm độ trễ trung bình là 6.033151%.

**Ghi chú người nói cho bản cá nhân.** Thưa thầy và các bạn, mỗi truy vấn ANN cần tìm những vector gần nó trong một tập lớn. Khi tìm trên đồ thị, hai worker có thể đi theo hai nhánh khác nhau rồi gặp lại cùng một đỉnh. Nếu cả hai lại tính khoảng cách tới đỉnh đó, ta đã dùng thêm CPU dù câu trả lời có thể giữ nguyên. Task D đặt câu hỏi liệu có thể bớt phần công lặp này mà vẫn giữ kết quả từng truy vấn hay không. Em sẽ đi từ câu hỏi đó đến thực nghiệm trên sáu đồ thị Task A bàn giao. Con số 6.033151% trên màn hình là mức giảm độ trễ SEARCH trung bình của cohort ấy.

[Nguồn tại mốc a0916db](../../task-da/TASK_D_FINAL_RESEARCH_SYNTHESIS.md)

## Slide 2. Ba cách song song hóa, ba chi phí khác nhau

**Thông điệp trên màn hình.** CPU đa lõi chia các bước mở rộng đồ thị. CPU–SSD chồng lấp tính toán với chờ I/O. GPU gom phép tính theo lô và chọn top-k trên phần cứng song song.

**Ghi chú người nói cho bản cá nhân.** Trong khảo sát, em phân biệt ba kiểu tài nguyên. Với CPU đa lõi, một truy vấn có thể chia các nhánh duyệt cho nhiều worker, như hướng multi-walker trong Speed-ANN và iQAN. Với CPU–SSD, DiskANN và PipeANN phải quyết định khi nào phát yêu cầu đọc tiếp trong khi các yêu cầu trước còn đang chờ. Với GPU, FAISS và CAGRA tận dụng các nhóm luồng để tính khoảng cách hoặc tìm ứng viên. Cả ba đều khai thác song song nhưng nút chờ khác nhau. D10 là số truy vấn được phục vụ đồng thời, cắt ngang cả ba cụm. Trong G2, em giữ jobs=1 để đo tác động *bên trong* một truy vấn. Cụm GPU có kết quả khảo sát. Phần thực nghiệm mới tập trung vào CPU và đồ thị của Task A.

[Nguồn tại mốc a0916db](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md)

## Slide 3. Những giả thuyết đã đổi hướng nghiên cứu

**Thông điệp trên màn hình.** E0: chính sách động chỉ thắng 3/108 ô trước đối chứng tĩnh tốt nhất. Trên R86, lợi ích của đổi lịch tĩnh còn nhỏ sau khi sửa bước merge. Sàng lọc offline H3 cho thấy phần lớn L2 trùng phát sinh sau khi cấp seed.

**Lời nói bản 5 phút.** Khảo sát ba cụm CPU, CPU–SSD và GPU dẫn đến một câu hỏi nhỏ hơn về CPU đa lõi. Trong mô hình E0, lịch động chỉ thắng đối chứng tĩnh tốt nhất ở 3 trên 108 cấu hình. Với TP-CG, phương pháp gần prior art và phần lợi ích có thể khai thác nhỏ. Trên 6,095 round R86, phần lớn khoảng cách trùng còn lại phát sinh từ ứng viên mới sau khi cấp seed. Nhóm vì vậy chọn hai thao tác có thể kiểm tra ngay trong engine.

**Ghi chú người nói cho bản cá nhân.** Với PipeANN, phép đo SIFT10M trên PAPER_GCC13_PORTABLE cho thấy từ T8 lên T16, QPS giảm 13.36%. Chỉ riêng hiện tượng này chưa chỉ ra nguyên nhân. Với AverSearch, em thử ý tưởng chuyển worker giữa tính toán và bảo trì hàng đợi. Trong E0, nếu ở mỗi ô lấy cách chia tĩnh tốt hơn làm chuẩn, chính sách động thắng ba, hòa mười lăm, thua chín mươi ô. Trong nguyên mẫu E2, một mutex tuần tự hóa bảo trì, cấu hình một maintainer nhanh hơn cấu hình thích nghi. Sang R86, sau khi thay bước merge dùng set bằng mảng phẳng, dư địa đổi lịch tĩnh nhỏ đi. TP-CG trùng hướng prior art. Một thử nghiệm offline riêng cho thấy 79–80% L2 trùng còn lại phát sinh giữa các ứng viên mới trong round. Gán lại seed từ đầu thiếu tín hiệu để trả phí lập lịch. Vì vậy em quay lại kiểm tra phần công lặp có thể nhận diện trực tiếp trong engine.

[Nguồn tại mốc a0916db](../../task-da/TASK_D_RESEARCH_TIMELINE.md)

## Slide 4. B1 ghi nhớ đỉnh đã đo, A1 giới hạn seed

**Thông điệp trên màn hình.** Cuối mỗi round, B1 công bố các đỉnh worker đã tính khoảng cách. A1 lưu cờ expanded trong beam và cấp tối đa p × S seed chưa mở rộng cho round sau.

**Lời nói bản 5 phút.** Hãy lấy một đỉnh x mà worker đã tính khoảng cách nhưng x trượt khỏi beam. Sang round sau đường đi khác lại gặp x. B1 công bố toàn bộ các đỉnh đã đo tại barrier. Vì ngưỡng nhận của beam đã đầy chỉ chặt hơn, worker có thể bỏ phép tính lại cho x. A1 xử lý việc cấp hạt giống. Thay vì dựng lại frontier và cấp toàn bộ seed, engine giữ cờ expanded ngay trong beam và ưu tiên những seed có thể được dùng ở round kế. Hai worker, mỗi worker tối đa 16 bước, nên chỉ cần cấp tối đa 32 seed.

**Ghi chú người nói cho bản cá nhân.** Hãy hình dung worker thứ nhất ở round này tính khoảng cách đến đỉnh x nhưng x ở ngoài beam. Sang round sau worker thứ hai gặp lại x từ một nhánh khác. Điểm x và query chưa đổi. Khi beam đã đầy, ngưỡng nhận chỉ có thể chặt hơn. B1 cho mỗi worker ghi ID đã tính vào bộ đệm riêng, rồi coordinator công bố các ID tại barrier. Worker ở round sau có thể bỏ phép L2 cho x. Trùng ngay trong cùng round vẫn có thể xảy ra. A1 giải quyết khâu chuẩn bị tiếp theo. Baseline dựng lại frontier và phát nhiều seed dù mỗi worker chỉ có tối đa S lượt mở rộng. A1 giữ cờ expanded trong beam và chỉ cấp p × S seed, phân theo thứ tự đã xác định. Với p=2 và S=16 là tối đa 32 seed cho vòng kế tiếp. Đó là giới hạn khâu cấp phát, khác với tổng số đỉnh mới mà worker có thể phát hiện. Kiểm chứng ngữ nghĩa nằm ở đối chiếu output và các bộ đếm bất biến.

[Nguồn tại mốc a0916db](../../task-da/TASK_D_B1_A1_TECHNICAL_EXPLANATION.md)

## Slide 5. Hai chính sách tìm kiếm trên hai loại đồ thị

**Thông điệp trên màn hình.** Ba graph Stock, ba graph Fast v2. Mỗi graph chạy cả baseline và B1+A1. 12 block cân bằng cho 72 cặp đối chứng. Đo trên MS-Turing-1M với p=2, S=16, beam=432, jobs=1.

**Lời nói bản 5 phút.** Task A cung cấp ba graph Stock và ba graph Fast v2 trên MS-Turing-1M. Trên mỗi graph, Task D so chính sách gốc với B1+A1 theo từng cặp. Giữ chung beam 432, p bằng hai, S bằng mười sáu, jobs bằng một. Nhóm dùng 18 lượt bật counter để kiểm đầu ra, rồi tắt counter cho 144 lượt đo thời gian. Mỗi lượt thuộc một trong 12 block cân bằng. Các tiến trình từ hai lần dừng trước được lưu để kiểm toán.

**Ghi chú người nói cho bản cá nhân.** Thiết kế có hai yếu tố. Task A cung cấp ba bản dựng Stock và ba bản Fast v2, cùng cấu hình R90 P0A v1.3. Task D chạy hai chính sách tìm kiếm trên chính từng graph. Như vậy có thể hỏi riêng tác dụng đổi chính sách trong cùng graph và tác dụng đó khác bao nhiêu giữa hai nhóm graph. Cả bốn arm dùng chung panel test mười nghìn query, beam 432 và hai worker trên Ryzen 5 PRO 4650U. Trước khi đo tốc độ, 18 tiến trình Quality ON kiểm chứng đầu ra, recall và counter. Sau đó 12 block Performance OFF cân bằng thứ tự chạy, mỗi block có sáu cặp. Tổng số là 72 cặp hay 144 tiến trình. Các phép xử lý tiếp theo dùng nguyên chiến dịch run2 đã qua guard. Điều này giữ cho mức chênh giữa hai chính sách có một đối chứng cùng điều kiện.

[Nguồn tại mốc a0916db](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)

## Slide 6. SEARCH giảm 6.033151% độ trễ trung bình

**Thông điệp trên màn hình.** Mean OFF đi từ 3,619.71 xuống 3,401.33 µs/query. CI95 block-t của mức giảm là [5.976580%, 6.089687%]. Throughput ở jobs=1 tăng từ 276.25 lên 293.99 query/s.

**Lời nói bản 5 phút.** Trên Ryzen 5 PRO 4650U, trung bình từ 3.62 xuống 3.40 mili giây mỗi truy vấn. CI95 theo block của mức giảm 6.033151% là từ 5.976580 đến 6.089687%. QPS tuần tự tăng từ 276 lên 294. Có hai mẫu số cần phân biệt: số phép L2 tính lại giảm 74.98%, còn tổng phép L2 giảm 12.22%. Số đỉnh duy nhất và kết quả top-10 giữ nguyên trên các phép đối chiếu. Cả sáu graph thuộc cohort cố định, nên nhãn quyết định là GO_A_FIXED_COHORT.

**Ghi chú người nói cho bản cá nhân.** Ở đường cơ sở, một query mất trung bình khoảng 3.62 mili giây. Với B1+A1, con số còn khoảng 3.40 mili giây. Đây là số mô tả trung bình gộp. Với phép ước lượng chính, nhóm ghép baseline và opt trong từng block trên cùng graph, tính chênh trên thang log rồi đổi về phần trăm giảm. Kết quả là 6.033151%. Khoảng 95% theo block từ 5.976580 đến 6.089687%, nằm trên ngưỡng 3% đã đăng ký. P95 từ 4,099.02 xuống 3,926.16 micro giây, và P99 từ 4,228.25 xuống 4,055.39. QPS_wall tăng 6.42% với đúng một query được xử lý tại một thời điểm. Nếu nhiều client cùng đợi, tốc độ và đuôi phân phối còn phụ thuộc tranh chấp giữa các query. Trên cohort này, quyết định là GO_A_FIXED_COHORT.

[Nguồn tại mốc a0916db](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md)

## Slide 7. Phần tiết kiệm nằm ở các phép L2 tính lại

**Thông điệp trên màn hình.** Duplicate L2 giảm 74.98%. Tất cả phép L2 giảm 12.22%. Unique L2 và số lần mở rộng giữ nguyên. Top-10 ID, thứ tự và squared L2 khớp từng bit trong các phép kiểm.

**Ghi chú người nói cho bản cá nhân.** Em xin giải thích hai phần trăm dễ nhầm nhất. Mẫu số của 74.98% là khoảng 3,713 lần tính lại khoảng cách mỗi query trong baseline. Sau khi bật B1+A1 còn khoảng 929 lần. Mẫu số của 12.22% lớn hơn nhiều, gồm toàn bộ gần 22,777 lần L2. Chênh lệch tuyệt đối trong hai phép tính là cùng một lượng, khoảng 2,784 phép cho mỗi query. Counter already_seen tăng tương ứng. Số đỉnh đo khoảng cách duy nhất vẫn khoảng 19,064, số lần mở rộng vẫn khoảng 457. Top-10 giữ nguyên cả ID, thứ tự và khoảng cách bình phương. Các counter này giải thích phần công giảm, trong khi đồng hồ OFF đo hiệu năng toàn truy vấn, bao gồm duyệt cạnh, hàng đợi và đồng bộ. Vì thế ta có mức giảm độ trễ 6.03%. G2 chưa có ablation riêng từng thành phần trên R90.

[Nguồn tại mốc a0916db](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)

## Slide 8. BUILD đo trên Host A, SEARCH đo trên Host D

**Thông điệp trên màn hình.** Task A giảm 20.03% thời gian dựng chỉ mục. Ghép hằng số BUILD với SEARCH đã đo cho ước lượng tiết kiệm 30.336 s ở 100 nghìn query và 227.194 s ở một triệu query.

**Lời nói bản 5 phút.** Trên Host A, Task A giảm thời gian BUILD từ 42.257 xuống 33.793 giây, tương ứng 20.03%. Trên Host D, Task D đo SEARCH. Nhóm cộng BUILD với Q nhân SEARCH để ước lượng chi phí cho Q truy vấn. Ở một trăm nghìn query, mô hình ước lượng tiết kiệm 30.336 giây. Ở một triệu query, tiết kiệm 227.194 giây. Hai con số là chênh lệch giữa hai cấu hình. Mô hình loại chi phí truyền và nạp chỉ mục. Khoảng tin cậy của tương tác SEARCH giữa Fast và Stock chứa 0. Bằng chứng cho phép báo cáo lợi ích trên cohort hiện có.

**Ghi chú người nói cho bản cá nhân.** Task A đo thời gian BUILD bốn luồng trên Host A. Ba Stock cho trung bình 42.257 giây, ba Fast v2 cho 33.793 giây, tiết kiệm khoảng 8.463 giây mỗi lần dựng. Task D đo SEARCH trên Host D. Chẳng hạn so hai đầu của thiết kế, stock_base mất 3,619.87 micro giây mỗi query và fast_opt mất 3,401.14. Để ước lượng giá trị chung, em cộng thời gian dựng với Q nhân thời gian tìm kiếm trung bình, sau khi đổi cùng đơn vị. Ở Q bằng một trăm nghìn, tổng dự báo từ 404.244 xuống 373.908 giây, chênh 30.336 giây. Ở một triệu query, chênh 227.194 giây. Mô hình điều kiện trên các biên nhận BUILD đã có và loại chi phí truyền, nạp chỉ mục. Với phép thử tương tác riêng trên SEARCH, mức chênh gain Fast trừ Stock là +0.037 micro giây với CI95 từ −2.582 đến +2.655. Dữ liệu tương thích với lợi ích xấp xỉ cộng trong phạm vi đó.

[Nguồn tại mốc a0916db](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md)

## Slide 9. Ba mục tiêu và phạm vi kết luận

**Thông điệp trên màn hình.** Khảo sát ba cụm và phân loại D01–D10. Sàng lọc các giả thuyết lập lịch. Cài đặt, đối chứng B1+A1 trên R90. Sáu graph cùng SEED=555 và một host SEARCH giới hạn suy rộng.

**Ghi chú người nói cho bản cá nhân.** Đối với mục tiêu trình bày thuật toán và cải tiến, hồ sơ gồm phân loại D01–D10, so sánh ba cụm và giải thích mã của B1+A1. Đối với mục tiêu đề xuất hướng song song, E0, TP-CG và H3 cho thấy nên dừng ý tưởng nào, trước đối chứng nào và vì sao. Đối với mục tiêu cài đặt, engine, kiểm tra parity cùng kết quả G2 cung cấp bằng chứng trên R90. Giới hạn ở đây rất cụ thể. Sáu graph dùng cùng seed 555 và có bất định từ build đa luồng. Chúng cho phép so sánh trong cohort nhưng chưa cung cấp sáu gốc RNG độc lập. Mới có một host SEARCH, một dataset và một cấu hình p=2 chính thức. Vì vậy nghiên cứu giữ nhãn EXPLORATORY_HOST_SPECIFIC. Tính mới thuật toán và khả năng chuyển kết quả sang host khác còn mở.

[Nguồn tại mốc a0916db](../../task-da/TASK_D_SCIENTIFIC_CONTRIBUTIONS_AND_LIMITATIONS.md)

## Slide 10. Ba quyết định cần giảng viên xác nhận

**Thông điệp trên màn hình.** Xin ý kiến về cách định vị đóng góp hệ thống, phạm vi ba cụm trong báo cáo và cách trình bày A × D. Đề nghị giữ G3 NOT_OPENED sau khi G2 đã đóng.

**Lời nói bản 5 phút.** Nhóm đã có khảo sát ba cụm, một chuỗi giả thuyết được kiểm tra và một engine được đo đối chứng. Em xin ý kiến thầy về việc định vị đây là nghiên cứu hệ thống, đặt phần A × D thành một mục dùng chung và giữ G3 chưa mở. Sáu graph có cùng seed, một host SEARCH và một dataset là giới hạn của kết luận. G2 đã đóng, kiểm toán độc lập ghi nhận 0 sai lệch.

**Ghi chú người nói cho bản cá nhân.** Em đề nghị giảng viên chốt ba nhóm quyết định để nhóm viết báo cáo. Thứ nhất là cách định vị học thuật của đóng góp: một nghiên cứu hệ thống có kết quả âm, cải tiến đường cơ sở và thực nghiệm kiểm toán được. Thứ hai là phạm vi học phần: trình bày cả ba cụm ở phần khảo sát và tập trung bằng chứng native vào CPU. Thứ ba là phần chung A × D: ghi rõ quyền sở hữu BUILD, SEARCH, và công thức tích hợp trên hai host. Hai cổng GO được đánh giá trên cohort cố định, G2 đã đóng và nghiên cứu đang tạm dừng. Nếu thầy cần thêm bằng chứng cho một kết luận cụ thể, nhóm xin ghi rõ kết luận ấy và đối chứng cần thiết để owner quyết định phạm vi sau. Đề xuất hiện tại là giữ G3 NOT_OPENED.

[Nguồn tại mốc a0916db](../../task-da/TASK_D_ADVISOR_REVIEW_BRIEF.md)

## Slide 11. Các khoảng tin cậy trả lời câu hỏi khác nhau

**Thông điệp trên màn hình.** Block-t mô tả lặp thực thi. Query-only bootstrap lấy mẫu lại query. Joint bootstrap gộp hai nguồn bất định trên sáu graph cố định. graph_population_ci = NOT_ESTIMABLE.

**Lời khi được hỏi.** Nếu thầy hỏi tại sao có nhiều khoảng 95%, em sẽ hỏi lại nguồn dao động cần xét. Khi cố định cả graph lẫn query, ta có 12 block để ước lượng độ lặp tiến trình bằng block-t, df=11. Ghép block kề thành sáu cặp cho kiểm tra drift, df=5. Query-only lấy mẫu lại theo cụm query trên các run đã quan sát. Joint bootstrap lấy mẫu cả block và query. Cả ba cách đều điều kiện trên sáu graph. Không cách nào tạo ra các gốc build RNG độc lập để suy rộng sang quần thể. Điểm quan trọng cho quyết định là các cận dưới cần xét ở G2 đều trên ngưỡng 3%.

[Nguồn tại mốc a0916db](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)

## Slide 12. Hai HOLD và hai cấp đối chứng kết quả

**Thông điệp trên màn hình.** 120,000 so sánh ON gồm 60k test và 60k validation với chuẩn Stage 5. Mỗi tiến trình trong 144/144 OFF khớp digest ON chuẩn. Phân tích hiệu năng chỉ dùng toàn bộ run2.

**Lời khi được hỏi.** Nếu thầy hỏi về các lần dừng hoặc số mẫu, em mở slide này. Design-3 dừng sau lần OFF đầu do parser yêu cầu khóa counters trong khi binary OFF bỏ khóa đó. Tu chính design-3.1 sửa giao diện parser. Run1 dừng ở tiến trình 120 vì guard phát hiện tải nền, sau 119 tiến trình sạch. Toàn bộ run1 được niêm phong. Run2 chạy trọn 144 tiến trình theo lịch mới từ đầu. Về chất lượng, 20,000 query phân biệt tạo ra 1,620,000 bản ghi lặp. Có 120,000 so sánh ON theo query, gồm test và validation với baseline Stage 5 beam 432. Các digest của 144 tiến trình OFF đều khớp chuẩn ON. Kiểm toán độc lập phát lại dữ liệu và ghi nhận AUDIT_PASS, 0 sai lệch.

[Nguồn tại mốc a0916db](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)
