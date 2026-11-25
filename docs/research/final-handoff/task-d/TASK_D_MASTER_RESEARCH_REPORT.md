# Thực thi song song trong tìm kiếm láng giềng gần đúng trên đồ thị

**Báo cáo nghiên cứu Task D và kết quả tích hợp với Task A · 25/11/2026**

## Tóm tắt

Khi tìm láng giềng trên đồ thị, mỗi lần mở rộng một đỉnh mới tiết lộ tập ứng viên kế tiếp. Thêm luồng xử lý có thể rút ngắn đường phụ thuộc nhưng cũng làm nhiều luồng đánh giá cùng một đỉnh. Task D khảo sát ba cách khai thác song song trên CPU, CPU–SSD và GPU, rồi thử các giả thuyết về phân vai, đồng bộ và giao việc giữa các luồng. Mô hình hàng đợi, phép thử một mutex và sàng lọc dựa trên độ trùng láng giềng đều cho thấy những trường hợp mà chi phí điều phối lấn át lợi ích dự kiến. Trên engine đa walker, hai thay đổi nhỏ có dự đoán kiểm tra được. B1 công bố các đỉnh đã tính khoảng cách khi kết thúc vòng. A1 chỉ giao số hạt giống mà worker có thể mở rộng trong một vòng. Trên sáu đồ thị MS-Turing-1M cố định, cấu hình hai worker giảm **6.033151%** độ trễ trung bình, với khoảng tin cậy 95% theo khối **[5.976580%, 6.089687%]**. ID, thứ tự và khoảng cách của top-10 giữ nguyên trong các đối chứng. Bộ đếm cho thấy số lần tính L2 trùng giảm **74.98%**, tổng số lần tính L2 giảm **12.22%**. Trên máy xây dựng chỉ mục, Task A đo được mức giảm **20.03%** thời gian BUILD. Ghép hai phép đo trong mô hình hai máy cho mức tiết kiệm 30.336 giây tại 100.000 truy vấn, với chi phí truyền và nạp nằm ngoài mô hình. Kết luận áp dụng cho máy tìm kiếm, tập truy vấn và sáu đồ thị đã đo. Các lần xây dựng dùng chung gốc ngẫu nhiên nên phương sai giữa những gốc mới vẫn chưa xác định. [Kết quả đã kiểm duyệt](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md)

## Chương 1. Bài toán và sự thay đổi câu hỏi nghiên cứu

Trong một dịch vụ tìm kiếm bằng vector, BUILD quyết định đỉnh nào nối với nhau, còn SEARCH quyết định đi qua những cạnh nào để trả lời truy vấn. Có thể xây dựng nhanh một đồ thị thưa nhưng phải đi nhiều bước hơn mới đạt cùng recall. Ngược lại, SEARCH có thể tính hai khoảng cách đồng thời và kết thúc sớm hơn dù tổng công tăng. Muốn đánh giá đóng góp của lập lịch, cần cố định dữ liệu, đo chất lượng trả về và so các chính sách trên cùng đồ thị.

Phân công ban đầu giao Task D khảo sát đường thực thi, chi phí đồng bộ và giới hạn mở rộng của ANN. Thử nghiệm PipeANN cho thấy tăng từ 8 lên 16 luồng có thể làm QPS giảm ở cùng chất lượng. Sau góp ý ngày 15/10 và bản phân công điều chỉnh ngày 16/10, nhóm chuyển sang tìm các cơ chế đã công bố, đối chiếu đánh đổi của từng cơ chế rồi mới chọn một giả thuyết có thể bác bỏ. Khảo sát bao phủ cả GPU, trong khi cài đặt tập trung vào CPU đa lõi. Đề xuất ngày 15/11 kết nối hai nhiệm vụ qua sản phẩm cụ thể là đồ thị bất biến do Task A xây dựng. Task D tự xây engine dùng chung để giữ đường tìm kiếm có thể so sánh. [Dòng thời gian](../../task-da/TASK_D_RESEARCH_TIMELINE.md) · [Đối chiếu phân công và bằng chứng](TASK_D_OBJECTIVE_CLOSURE_MATRIX.md)

| Câu hỏi nghiên cứu | Quan sát cần có để trả lời |
|---|---|
| RQ1. Khi nào thêm song song giúp ích trên hệ thống hiện có? | Đo QPS, latency và recall dưới môi trường ổn định. Kết quả paper, mô hình và chạy native có nguồn riêng. |
| RQ2. Cấu trúc đồ thị từ BUILD ảnh hưởng thế nào đến scaling của SEARCH? | Đổi số worker trên từng đồ thị, sau đó đối chiếu chênh lệch speedup ở cùng mục tiêu recall và quy tắc hiệu chỉnh. |
| RQ3. Công lặp đến từ điều phối hay từ chính đường cơ sở? | So với chính sách tĩnh mạnh và đường cơ sở có phép gộp hiệu quả. Đối chiếu số lần tính khoảng cách, kết quả từng query và thời gian thực. |
| RQ4. Hiệu ứng của chính sách SEARCH thay đổi bao nhiêu khi dùng đồ thị Fast của Task A? | Đo đầy đủ bốn ô Stock/Fast × baseline/B1+A1, tính hiệu của hai chênh lệch. Đánh giá chi phí BUILD bằng biên nhận đúng đồ thị. |

Chuỗi bằng chứng đi từ SIFT10M trên SSD, qua phép thử hàng đợi, tới MS-Turing-1M trong RAM. R86 dùng các đồ thị A0/A1/A3 để khám phá tương tác với số worker. R90 P0A v1.3 cung cấp sáu đồ thị cho quyết định G2. R91 nằm ngoài nghiên cứu này. Ký hiệu **A1 của Task A** ở R86 chỉ nhánh xây dựng H17. **A1 của Task D** chỉ cách quản lý frontier trong engine tìm kiếm. [Tổng hợp phạm vi](../../task-da/TASK_D_FINAL_RESEARCH_SYNTHESIS.md)

## Chương 2. Từ truy vấn láng giềng đến ba họ thực thi

### 2.1 Chất lượng, công và đường phụ thuộc

Cho điểm truy vấn q và tập vector X, truy vấn k-NN chính xác lấy k điểm có khoảng cách nhỏ nhất. ANN cho phép trả về một tập gần đúng để đổi lấy chi phí thấp hơn. Với ground truth Gₖ(q) và kết quả Rₖ(q), Recall@k là |Gₖ(q) ∩ Rₖ(q)|/k, sau đó lấy trung bình theo query. Cùng một Recall@10 trung bình vẫn có thể trả về các ID khác nhau. Vì vậy phép kiểm đúng đắn giữa hai chính sách của D so cả thứ tự ID và khoảng cách bình phương của từng kết quả.

Trên đồ thị, tìm kiếm best-first duy trì một **beam** gồm tối đa B ứng viên tốt nhất hiện biết. Phần chưa mở rộng là **frontier**. Mở rộng một đỉnh cần đọc danh sách kề, lọc đỉnh đã thấy, tính khoảng cách tới q và cập nhật thứ tự ưu tiên. Mở nhiều đỉnh trước khi chia sẻ kết quả có thể rút ngắn số lượt chờ nhưng trả giá bằng mở rộng thừa. Song song *nội truy vấn* phân việc của một query cho nhiều worker. Song song *liên truy vấn* phục vụ nhiều query đồng thời. Mức tăng throughput khi chạy nhiều query không trực tiếp cho biết một query có kết thúc sớm hơn hay không.

Gọi W là tổng công, L là thời gian trên chuỗi phụ thuộc dài nhất, p là số worker. Trong mô hình lý tưởng với đơn vị công đồng nhất, Tₚ ≥ max(W/p,L). Trên máy thật mỗi vòng BSP còn chờ worker chậm nhất và gộp trạng thái. Đặt T(G,p,R*) là latency tại mục tiêu recall R*, speedup = T(G,1,R*)/T(G,p,R*), hiệu suất = speedup/p. Hệ số phình công khoảng cách = số L2(p)/số L2(1). So hai đồ thị bằng chênh lệch speedup đòi hỏi báo cả độ trễ tuyệt đối vì hai mẫu số tuần tự có thể rất khác. Sáu nhóm chỉ tiêu trong nghiên cứu gồm chất lượng truy xuất, công thuật toán, độ phức tạp và scaling, latency/QPS/speedup, tài nguyên, cùng overhead và đánh đổi. Các phép đo BUILD còn xét thời gian, dung lượng đồ thị và RSS. [Bảng tiêu chí](../../task-da/TASK_D_SIX_CRITERIA_EVIDENCE_SCORECARD.md)

### 2.2 Các cơ chế đã khảo sát

| Cụm và công trình | Công việc có thể chạy song song | Giá phải trả và đối chứng cần thiết |
|---|---|---|
| CPU · ParlayANN (D01) | Trong BUILD, nhiều điểm dùng cùng snapshot rồi gộp cạnh ngược theo batch. | Batch lớn cần thêm bộ nhớ tạm. Chất lượng đồ thị và thời gian SEARCH phải được đo sau BUILD. |
| CPU · Speed-ANN, iQAN (D02–D03) | Chia láng giềng của một đỉnh theo cạnh, hoặc giao các đường duyệt cho nhiều walker với hàng đợi riêng rồi đồng bộ. | Bậc thấp giới hạn song song theo cạnh. Đồng bộ chậm có thể khiến walker làm lại công. iQAN và Speed-ANN thuộc cùng dòng nghiên cứu. |
| CPU · AverSearch (D03) | Tách vai trò điều phối, duy trì hàng đợi và tính khoảng cách để chồng lấp các bước. | Tỉ lệ vai trò phù hợp thay đổi theo tải. Chuyển vai trò có chi phí, phải so với cấu hình tĩnh tốt nhất. |
| CPU–SSD · DiskANN (D04) | Phát một lô yêu cầu đọc theo beam, tận dụng song song thiết bị. | Qua biên lô phải đợi yêu cầu chậm, còn W lớn tạo thêm lượt đọc. |
| CPU–SSD · PipeANN (D05–D07) | Pipeline liên tục, điều chỉnh W theo query, đan xen phát I/O và xử lý completion. | Phát sớm có thể đọc ứng viên về sau bị loại. Ba mã phân loại mô tả các cơ chế phối hợp trong cùng hệ thống. |
| CPU–SSD · LAANN (D08) | Dò trước dữ liệu trong RAM và ưu tiên yêu cầu trên nền bố trí trang. | Trả thêm CPU để tránh đọc SSD. Muốn quy kết tác dụng cho lịch phát phải cố định layout, cache và đối chứng. |
| GPU · FAISS GPU, CAGRA, FusionANNS (D09) | FAISS khai thác GEMM và chọn top-k trong warp. CAGRA song song hóa các bước trên đồ thị, FusionANNS khảo sát phối hợp nhiều tầng tài nguyên. | Kích thước batch, VRAM, thanh ghi, truyền dữ liệu và gộp kết quả quyết định chi phí. Task D chưa chạy benchmark GPU. |
| Phục vụ · concurrency (D10) | Nhiều truy vấn cùng sử dụng CPU, ổ đĩa hoặc GPU. | QPS tải cao và tail có hàng đợi phụ thuộc mô hình request. G2 chỉ khảo sát jobs=1. |

D01–D10 là mã taxonomy; D1–D6 trong hồ sơ PipeANN là mã giả thuyết lịch sử. Hai hệ mã trả lời những câu hỏi khác nhau. Đối với cụm CPU–SSD, dự án có phép đo đường cơ sở PipeANN và các sàng lọc. Đối với phương pháp cải tiến SSD mới và toàn bộ phần GPU, bằng chứng là khảo sát. [Taxonomy đầy đủ](tables/table02_taxonomy_d01_d10.csv) · [So sánh prior art](tables/table03_prior_art_comparison.csv)

### 2.3 Từ khoảng trống đến giả thuyết

Một câu hỏi có thể kiểm chứng là liệu thông tin sẵn có đầu mỗi vòng có dự đoán đủ phần công trùng *sau khi* đường cơ sở đã được sửa hay không. Với hai worker, nếu hai hạt giống có nhiều láng giềng chung, việc giao chúng cùng worker có thể tiết kiệm L2. Nhưng phép gán như vậy có thể làm lệch tải hoặc tốn thời gian tính độ trùng hơn số L2 cứu được. Mục tiêu giảm số phân vùng cùng đụng một láng giềng đã gần với mục tiêu connectivity của phân hoạch siêu đồ thị. Tương tự, cờ visited và con trỏ ứng viên chưa kiểm tra đã xuất hiện trong các hệ graph ANN. Đóng góp cần được đánh giá qua dự đoán và thí nghiệm phân biệt cụ thể. [Kiểm toán prior art H3](../../task-da/H3_NOVELTY_AND_PRIOR_ART_AUDIT.md)

## Chương 3. Thiết kế đo lường

### 3.1 Dữ liệu, hệ thống và đơn vị quan sát

G2 dùng 1.000.000 vector cơ sở MS-Turing, mỗi vector có 100 tọa độ float32. Tệp public có 100.000 query và ground truth tương ứng. Các ID đầu tiên của từng hàng ground truth xác định top-10. Graph ID ánh xạ trực tiếp tới hàng của tệp base. Tất cả sáu graph có entry 0, bậc ra tối đa 64, có đường đi từ entry tới đủ 1M đỉnh. Khi so cấu trúc CSR do loader tạo với thứ tự cạnh đọc độc lập từ file, cả 6M hàng khớp từng vị trí. Thay đổi thứ tự cạnh có thể làm thay đổi quỹ đạo tìm kiếm, nên cùng số đỉnh và cùng bậc trung bình chưa đủ để ghép hai phép đo. [Manifest graph, dữ liệu và ground truth](../../task-da/AXD_G1_GRAPH_ARTIFACT_MANIFEST.md)

Host D là AMD Ryzen 5 PRO 4650U. Trong G2, hai worker chạy trên CPU logic 0 và 2. Chính sách xung schedutil được giữ theo protocol. Một tiến trình tìm từng query theo thứ tự đã khóa, jobs=1, có 100 query warmup. Binary C++17 dùng GCC 13.3.0 Release, cùng một ELF phục vụ hai chế độ. Timestamp OFF đo SEARCH cho từng query. QPS_wall đo số query hoàn thành trên thời gian tường của batch. Peak RSS tính bằng KiB, CPU-s tính theo thời gian CPU toàn tiến trình, gồm cả nạp dữ liệu, warmup và ghi kết quả. ON xuất work counters và kết quả để so ID, thứ tự và squared L2 với đối chứng. Bật bộ đếm có thể làm đổi timing, nên sai khác của timer ON chỉ được dùng chẩn đoán. [Giao thức v2](../../task-da/AXD_G2_PREREG_V2.md) · [Kiểm toán phép đo](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)

### 3.2 Hiệu chỉnh trước test, bảo vệ và lịch đo

Ở R86, chọn beam nhỏ nhất vừa vượt mức recall trên validation đã khiến 7/9 cấu hình hụt ngưỡng 0.998 khi sang test. G2 v1 còn yêu cầu span của sáu điểm recall ≤0.0001, nhạy với nhiễu lấy mẫu. G2 v2 dùng **một beam cho cả sáu graph**. Chọn beam nhỏ nhất trong lưới thỏa mean − 4.2279 × SE ≥ 0.990 cho cả sáu trên validation; kết quả là 432. Trên test, Gate A yêu cầu mỗi graph qua sàn 0.990 với cận dưới đồng thời một phía (z ≈ 2.394), cùng parity nội graph. Gate B đặt biên cho chênh lệch Recall Fast − Stock là (−0.0005, +0.0005). Hai gate trả lời hai câu hỏi khác nhau, giữ chất lượng trên mỗi graph và so chất lượng trung bình giữa hai nhóm graph. [Hiệu chỉnh và quy tắc quyết định](../../task-da/AXD_G2_V2_GO_NO_GO_CRITERIA.md)

Bộ giám sát kiểm tra trạng thái nguồn, nhiệt, bộ nhớ và CPU ngoài tiến trình. Khi khảo sát thiết kế cho Ryzen, hai lượt đọc /proc trong chính monitor đã gây 2.83–3.42% tải, cao hơn cap dự kiến 1%. Bản sửa trước đo giảm xuống một lượt đọc và kiểm tải ở ba phạm vi CPU bằng các ngưỡng riêng. Qualification 900 giây lần thứ nhất trượt do tiến trình nền, lần hai đạt 853/853 và 848/848 cửa sổ theo hai phép kiểm. Guard tiếp tục hoạt động trong campaign. Một guard đủ nhạy có thể làm mất cả lượt chạy dài; lý do dừng và dữ liệu đã thu đều là một phần của biên bản. [B1 feasibility](../../task-da/AXD_G2_V2_B1_QUIET_FEASIBILITY_REVIEW.md) · [Qualification](../../task-da/AXD_G2_V2_DESIGN3_QUALIFICATION_ANALYSIS_20261124.md)

Mỗi block có 6 graph × 2 policy. Cả campaign có 12 block, 72 cặp tiến trình, 36 cặp baseline trước và 36 cặp B1+A1 trước. Với mỗi cặp, lấy log tỉ số mean latency, bình quân theo graph trong block, tính khoảng t theo block rồi biến đổi về phần trăm giảm. Vì biến đổi log và trọng số đã khóa, hiệu số từ hai mean hiển thị đã làm tròn chỉ là phép kiểm gần đúng. Số query nhân với số lượt lặp không phải cỡ mẫu độc lập của phép t. [Thiết kế thống kê](../../task-da/AXD_G2_V2_STATISTICAL_DESIGN.md)

| Khoảng 95% cho mức giảm mean SEARCH | Giá trị | Biến thiên được khảo sát |
|---|---:|---|
| Primary block-t, df=11 | [5.976580%, 6.089687%] | 12 block trên cùng sáu graph và panel test |
| Drift, df=5 | [5.991262%, 6.075021%] | Ghép các block kề nhau thành sáu cặp để kiểm độ nhạy theo thời gian |
| Query-only bootstrap | [5.970252%, 6.095760%] | 10.000 mẫu bootstrap theo khối 100 query, giữ các lần chạy quan sát được |
| Joint bootstrap | [5.954283%, 6.113015%] | Lấy mẫu lại cả query và lượt chạy, vẫn điều kiện hóa theo sáu graph |
| Graph population | NOT_ESTIMABLE | Ba lần build mỗi arm dùng cùng SEED=555 và bốn luồng bất định. Sự khác nhau giữa file graph chưa xác lập sáu gốc RNG độc lập. |

Các điều kiện GO còn gồm cận dưới vượt mức cải thiện thực dụng 3%, kiểm từng graph và bỏ lần lượt một graph, trần hồi quy p95/p99 (+5%/+10%), giới hạn RAM trên từng cặp và kiểm counters. Tập test 10k không giao validation 10k hay ba panel 3k trước đó nhưng được lấy từ public pool đã từng dùng ở nghiên cứu khác. Thiết kế v2 có sau khi đã biết kết quả v1. Hai điều kiện này là lý do giữ EXPLORATORY_HOST_SPECIFIC. [Split audit](../../task-da/AXD_G2_V2_QUERY_SPLIT_AUDIT.md) · [CI đầy đủ](tables/table06_ci_families.csv)

## Chương 4. Những hướng đã thử và quyết định dừng

### 4.1 PipeANN và giới hạn của suy luận từ QPS

Giả thuyết ban đầu là pipeline CPU–SSD có thể bị thiếu công sẵn sàng hoặc bị chặn do thứ tự công bố các completion. Những hiện tượng này có thể cho dấu hiệu bề mặt giống nhau là tăng luồng nhưng giảm throughput. Dự án đo các chế độ LIGHT/DETAIL riêng và rà lại cả môi trường chạy. Kết quả G0-B với NVMe IOPS giảm khi lên T16 gợi ý nên phân biệt nút nghẽn CPU/kernel với giả thuyết thiếu băng thông SSD. Ở G0-C2, không cặp nào trong ba cặp đạt dấu hiệu head-of-line ≥2× đã đặt trước. Bằng chứng là **D6 INCONCLUSIVE**. D1 giữ **UNTESTED**, D4 **NOT TESTED**. Với các mã D2/D3/D5, báo cáo này không có kết quả kiểm định cơ chế độc lập để bổ sung. [Chẩn đoán FIFO](../../G0C2_SIFT10M_D6_CAUSAL_DIAGNOSTICS.md) · [Phạm vi các giả thuyết](../../../../RESEARCH_PHILOSOPHY.md)

Ba subject phải giữ đúng danh tính. MODERN_GOLDEN có screening W32 từng thấy median T16/T8 −8.51%. PAPER_STOCK là mã lịch sử gặp vấn đề biên dịch trên GCC 13. PAPER_GCC13_PORTABLE là bản vá portability tối thiểu dùng cho so sánh theo paper. Lần thử Issue #29 dừng vì 100°C. PR #30 lưu biên nhiệt và kiểm oracle. PR #31 khóa môi trường full-fan 60/90 W. Issue #32 hoàn thành 36/36 stock runs và 12/12 kiểm chất lượng trên SIFT10M. Ở W32, T16 giảm 13.36% QPS so với T8 (CI90 [−14.35%, −11.49%]), cùng Recall 99.21%, trong khi P99.9 tăng từ 4.40 lên 83.55 ms. Độ trễ đuôi tăng là bằng chứng về hiện tượng scaling ở subject này. Muốn quy nguyên nhân cho một cơ chế cần thêm phép quan sát phân biệt. [Issue #29](../../ISSUE29_DECISION_MEMO.md) · [Issue #32](../../CUSTOM_FULLFAN_SIFT10M_20261013.md)

Sàng lọc H-G hỏi liệu độ trùng danh sách kề có giúp chọn ứng viên. Trên surrogate, 2.56 GB metadata không tạo gain. H-QV1 dùng tín hiệu margin giá rẻ nhưng utility thay đổi −0.000122. H-V và H-F cũng chưa tạo lập bằng chứng tăng throughput native. H-C là hướng tài nguyên CPU riêng. Các phép sàng lọc trả lời giá trị đầu tư vào từng tín hiệu ở phép thử đó; chúng không xác định cơ chế của T16. [Lộ trình các lane](../../../RESEARCH_ROADMAP.md)

### 4.2 E0–E3. Có nên chuyển worker giữa các vai trò?

Nếu hàng đợi điểm số dài dần, chuyển một worker từ duy trì hàng đợi sang tính khoảng cách có vẻ hợp lý. E0 so chính sách phản ứng với hai phân vai cố định trên 108 tổ hợp cường độ công, độ dài lô và chi phí quan sát/chuyển vai trò. So với đường bao tĩnh tốt hơn trong từng ô, chính sách động thắng 3, hòa 15 và thua 90. Cả ba lần thắng cần phí chuyển bằng 0. Số liệu tính bằng tick mô hình, đủ bác bỏ phát biểu “thích nghi luôn tốt hơn” trong lưới mô hình. E1 sau đó xác thực fixture của nguyên mẫu độc lập. E2 chạy SIFT1M NSG với bốn worker dùng chung một mutex. Trong các lượt thu được, Fixed-1 đạt 19.21 QPS, Adaptive-3 đạt 15.09, Fixed-2 đạt 10.72. Cùng tranh mutex khiến thêm người duy trì hàng đợi không tạo thêm phần việc độc lập. Chiến dịch dừng nhiệt ở 90.25°C, chỉ hoàn thành 3/36 lượt, do đó quyết định formal NO-GO áp dụng cho thiết kế một mutex. E3 thay đổi vai trò một lần theo pha, chỉ đạt fixture validation. Hiệu quả native trên triển khai gốc AverSearch vẫn INCONCLUSIVE. [E0](../../AVERSEARCH_QUEUE_ROLE_REVIEW.md) · [E1–E3 và phạm vi source](../../task-da/SOURCE_AUDIT.md)

### 4.3 P0–P6 và H1–H3. Cấu trúc đồ thị thay đổi chi phí nhiều worker ra sao?

R86 A0 là Stock C160/K1024/N2, A1 là H17 cùng tham số, A3 là H17 C64/K512/N2. A3 có BUILD median 28.73 s so với 41.98 s ở A0 trên Host A, song cần beam lớn hơn ở SEARCH. P0 xác minh byte identity nhưng thiếu log host lịch sử và có chung root 555, nên giữ HOLD. P1 kiểm loader, khoảng cách và serial parity trên chín graph. 1.804M đối chiếu ON/OFF đạt, t0990 qua 9/9, t0998 trượt 7/9. Full P1 vẫn HOLD. Khi phần P2 thăm dò t0990 được mở riêng, nhóm có thể so các worker trong cùng engine và lưu OFF/ON tách biệt. P3 chính thức vẫn CLOSED. [Reconciliation](../../task-da/P0_P1_FINAL_RECONCILIATION_REPORT.md) · [P1](../../task-da/P1_FULL_GATE_DECISION.md) · [Phạm vi P2](../../task-da/PROTOCOL_V4_1_P2_EXPLORATORY_0990_ADDENDUM.md)

**H1.** Nếu graph ảnh hưởng scaling, chênh lệch speedup phải thấy được sau khi hai arm dùng cùng quy tắc chất lượng. Stage D có 63 ô × (5 OFF + 1 ON) = 378 lượt. Với p=2, S=16, flat merge, A0 đạt 1.5484× và A3 đạt 1.4310× so với tuần tự tương ứng. Khoảng chênh khoảng +0.1175× với CI95 [+0.0929, +0.1421]. Ở cùng p=4, S=16, dấu đảo chiều. 63/63 điểm recall qua 0.990 nhưng 59/63 cận dưới dưới mức này. Có bằng chứng tương tác có điều kiện giữa graph, số worker và nhịp đồng bộ. Kết quả chưa đủ để xếp loại “graph tốt cho song song” theo một chỉ số duy nhất. [Stage D và E](../../task-da/STAGE_D_E_REPLICATION_AND_H3_DECISION.md)

**H2.** Một phần chênh lệch trước đó có thể do chính phép gộp global beam bằng std::set. Thay bằng flat merge đã làm mất khoảng 48–60% phần suy giảm được xem xét. Trên A3, nhiều vòng hơn tạo thêm cơ hội gặp lại những đỉnh đã tính khoảng cách. B1+A1 ra đời từ đối chứng này. Pilot R1 trên A3, p=2/S=16 giảm latency 11.58%. R2 và R3 lần lượt giảm 12.29% và 10.08%, song CI95 ngoài theo hai build là [−2.84%, +25.21%] với df=1, nên narrow replication giữ **HOLD**. Trong pilot p=4, các CI của combo chứa 0 và ở A3/S8 p95 xấu hơn 5.2%. Bốn worker trải qua hai miền L3, tăng chia sẻ dữ liệu là giải thích khả dĩ nhưng chưa có PMU chứng minh. Cấu hình p=2/S=16 là điểm đã có tín hiệu và kiểm soát được cho G2. [Pilot R1](../../task-da/B1_A1_PILOT_HANDOFF_20261119.md) · [Narrow R2/R3](../../task-da/B1_A1_NARROW_REPLICATION_REPORT_20261119.md)

**H3.** TP-CG chỉ đáng cài nếu tín hiệu rẻ có thể điều chỉnh số walker hoặc nhịp đồng bộ để thắng lịch tĩnh mạnh sau khi tính cả chi phí ra quyết định. Stage E chuyển hướng khi baseline mạnh hơn đã hấp thụ phần lớn vấn đề ban đầu. Tiếp đó nhóm thử phạm vi nhỏ hơn là gán seed dựa trên overlap. Trace 6.095 vòng trên A3-R1..R3, p=2/S=16 và 64 query cho thấy 79–80% duplicate L2 còn lại xảy ra giữa hai đỉnh phát sinh sau khi bắt đầu vòng. Phần seed–seed chỉ chiếm khoảng 0.33% **tổng** L2. Sketch 128 bit thua phương án cân bằng bậc 0.97–1.12% theo proxy và riêng kernel đã tốn 28.5–29.7 µs/query. Scoped NO-GO đối với cơ chế đã thử. P5/TP-CG online **NOT_OPENED**, P6 mở rộng cross-host/graph/dataset **NOT_RUN**. [Sàng lọc overlap](../../task-da/H3_OVERLAP_SIGNAL_SCREENING_RESULTS.md) · [Đánh giá lại P0–P6](../../task-da/ORIGINAL_PROPOSAL_FINAL_REASSESSMENT.md)

**P4 và tính hợp lệ của quan sát.** Lấy toàn bộ T₁ chia cho số L2 để làm đơn giá khoảng cách rồi cộng timer merge/wait đã cho một residual khoảng −196 µs ở một ô Stage D. T₁ chứa cả truy cập đồ thị và quản lý hàng đợi, nên cách cộng này không xác định được các thành phần độc lập. Trên A3-R1, phase observer có chênh lệch điểm −1.717% so với frozen OFF nhưng CI95 [−2.851%, −0.570%] vượt biên tương đương ±2% ở cận dưới. Trạng thái **NOT_VALIDATED_OUTSIDE_EQUIVALENCE_BUDGET**. Thiếu PMU nên chưa tách được thời gian cache, compute và barrier trên đường găng OFF. P4 giữ HOLD phần chẩn đoán nhân quả. [Kiểm toán đo lường](../../task-da/MEASUREMENT_VALIDITY_AND_PHASE_AUDIT.md)

## Chương 5. B1+A1 trong engine BSP

### 5.1 Một vòng tìm kiếm chạy như thế nào?

P2SearchSession giữ graph CSR và các vector chỉ đọc. Khi tạo session nhiều worker, driver tạo p−1 luồng phụ một lần. Worker 0 cũng thực hiện tìm kiếm. Mỗi query có mã epoch riêng để tái sử dụng hai mảng uint16 đánh dấu settled và expanded. Khi mã sắp được dùng lại do tràn, mảng được xóa. Worker 0 mở entry và nạp beam ban đầu. Ở mỗi vòng, các worker nhận seed theo round-robin và cùng đọc một snapshot của ngưỡng beam. Mỗi worker có local_seen cho vòng hiện tại, local_pending là tập có thứ tự để lấy ứng viên gần nhất, local_top để giới hạn ứng viên mới, cùng danh sách đã mở rộng và ứng viên đưa về gộp. So sánh theo cặp (squared_l2, ID) cho thứ tự xác định kể cả khi khoảng cách bằng nhau.

Worker 0 tăng work_seq bằng release-store. Luồng phụ đọc bằng acquire-load, mở tối đa S đỉnh rồi công bố done_seq. Khi đủ tín hiệu, worker 0 là tác nhân duy nhất gộp beam và cập nhật epoch. Không worker nào ghi vào settled_epoch trong khi worker khác đang mở rộng. Cuối session, cờ shutdown đánh thức các luồng và destructor chờ chúng kết thúc. Mã nguồn đóng băng dùng cho giải thích là f2cd634, tệp p2_engine.hpp tại commit đó, các hàm run_worker_round, worker_loop và search_multi. [Đối chiếu source và ELF](../../task-da/TASK_D_B1_A1_TECHNICAL_EXPLANATION.md) · [Mã engine trong checkout](../../../../research/task_da/search_common/p2_engine.hpp)

### 5.2 Hai thay đổi trong cùng đường tìm kiếm

Ở baseline G2, phép gộp đã dùng mảng phẳng. Baseline đánh dấu các đỉnh được mở và các ứng viên đã được đưa vào local_discovered. Khi beam đã đầy, một đỉnh vừa tính L2 có thể bị loại ngay vì đứng sau phần tử xấu nhất. Đỉnh đó chưa có dấu toàn cục, nên một cạnh tới nó ở vòng sau lại kích hoạt một phép L2. B1 (barrier_all_evaled) ghi mọi ID vừa đánh giá vào local_newly_evaled, kể cả ID bị loại, rồi công bố các ID tại barrier. Hai worker vẫn có thể trùng L2 trong cùng vòng.

Ở baseline, mỗi vòng dựng lại active_frontier bằng cách lọc beam, chia toàn bộ frontier cho worker rồi chèn tất cả seed vào local_pending. A1 (incremental) gắn cờ expanded vào từng phần tử của beam phẳng. Khi gộp hai dãy ứng viên, nó đồng thời lấy tối đa p×S phần tử chưa mở theo đúng thứ tự round-robin. Khi không có ứng viên mới, nó có thể tiếp tục quét từ phần tử chưa mở đầu tiên và dừng sớm. A1 vẫn giữ toàn bộ top-B trong beam. Việc chặn số seed chỉ áp dụng cho lần giao việc kế tiếp.

~~~text
Baseline, mỗi vòng
  Frontier ← mọi phần tử trong beam chưa được mở, sắp theo (L2², ID)
  Chia toàn bộ Frontier theo vòng tròn cho p worker
  Mỗi worker lặp tối đa S lần lấy min(local_pending) để mở rộng
    Với mỗi láng giềng chưa settled và chưa thấy tại worker trong vòng
      Tính L2², chỉ đưa ứng viên đủ tốt vào local_discovered và hàng đợi
  Tại barrier đánh dấu discovered và expanded, hợp các ứng viên, giữ top-B

B1+A1, mỗi vòng
  Nhận các seed đã chuẩn bị từ lần gộp trước (tối đa S cho mỗi worker)
  Dùng cùng luật lấy min, cùng hàm L2² và cùng ngưỡng
    Sau khi tính L2² ghi ID vào local_newly_evaled trước bước loại ứng viên
  Tại barrier đánh dấu mọi ID vừa tính và cập nhật expanded
  Gộp theo cùng thứ tự, giữ top-B với cờ expanded
  Trong lần quét này giao tối đa p×S seed chưa mở cho vòng kế
  Khi hết seed chưa mở, trả k phần tử đầu của beam
~~~

**Ví dụ đồ thị minh họa, không dùng làm số liệu thực nghiệm.** Giả sử sau một vòng đã có beam đủ bốn ứng viên u, v, w, x theo thứ tự tăng dần, với khoảng cách bình phương x bằng 9. Có các cạnh u→z và w→z, với khoảng cách đến z bằng 16. Chọn p=2 và S=1. Baseline giao [u,w] và [v,x]. Mỗi worker chỉ có thể mở seed đầu, nên A1 chỉ cần giao [u] và [v]. Nếu quét u gặp z, cả hai policy cùng tính 16 và bỏ z. Giả sử không có ứng viên mới tốt hơn và vòng sau mở w. Baseline tính lại 16, còn B1 tra epoch và bỏ qua. Beam giữ thứ tự cũ. Nếu *cả u và v* cùng trỏ tới z ở vòng đầu, cả hai worker vẫn tính 16 vì chỉ công bố sau barrier. [Sơ đồ B1](figures/fig06_b1_before_after.svg) · [Sơ đồ A1](figures/fig07_a1_before_after.svg)

### 5.3 Điều kiện bảo toàn kết quả và chi phí

**B1.** Với graph, query, số học và tie-break cố định, một ID có cùng hit ở mọi lần đánh giá. Ngưỡng xấu nhất của global top-B đã đầy chỉ có thể tốt lên khi nhận thêm ứng viên. Vì vậy hit đã thua ngưỡng không thể thắng ở vòng sau. Một hit bị loại bởi local top-B cũng đã có B hit khác tốt hơn trong cùng vòng. Những ứng viên được nhận đã đi vào bước gộp. Ghi dấu sau vòng bỏ được lần tính lại mà không làm mất hit có thể cải thiện beam sau đó. **A1.** Theo thứ tự toàn phần, seed thứ S+1 của một worker có S seed đi trước. Worker chỉ được pop S lần. Ứng viên mới chen vào có thể đẩy lượt pop của seed ra sau. Trong code, seed cũ đã settled, local_top chỉ quản lý ứng viên mới. Vì vậy giới hạn giao prefix không đổi thứ tự những seed mà worker có thể mở trong vòng. Duy trì cờ expanded và xử lý ứng viên mới theo đúng epoch là điều kiện để áp dụng lập luận này qua nhiều vòng. Phép kiểm bit-exact ở Chương 6 kiểm hậu quả quan sát được của các bất biến trên cohort.

| Thành phần | Chi phí và giả định |
|---|---|
| Nạp seed vào cây có thứ tự | Đặt F là số ứng viên chưa mở, F≤B. Baseline giao tối đa ceil(F/p) seed/worker. A1 chặn ở S. Chèn m seed tốn O(m log(m+1)). A1 tiết kiệm rõ khi F lớn hơn pS. |
| Đánh dấu | Nếu một vòng thực hiện M lượt đánh giá, B1 giữ thêm tối đa M ID và ghi chúng tại barrier. M ≤ pS × bậc ra tối đa. Global epoch dùng 4n byte cho hai mảng, graph và vector dùng chung. |
| Tính khoảng cách | Với vector d chiều, mỗi L2 tốn O(d). B1 bỏ phần đánh giá lại giữa các vòng, duy trì U đánh giá duy nhất và các va chạm trong vòng. Mức tiết kiệm phụ thuộc số cạnh gặp lại. |
| Gộp | Với C ứng viên nhận từ worker, sort/unique và gộp top-B tốn O(C log(C+1)+B) ở vòng có cập nhật. A1 gộp luôn bước chuẩn bị seed. Khi C=0 có thể dừng sớm, còn trường hợp xấu vẫn quét beam. |
| Phạm vi | Dữ liệu graph/vector tốn O(n+m+nd) cho n đỉnh, m cung, d chiều. Hai policy vẫn cần beam và trạng thái theo worker. Cận chi phí một thao tác không cho biết số vòng tới nghiệm hay chi phí cache trên một host khác. |

Trên R86 A3-R2/R3, riêng A1 giảm 6.50% và 5.93% latency OFF dù số L2 giữ nguyên. R90 chỉ so tổ hợp với baseline. Cùng baseline mạnh và các ablation R86 giúp phân biệt cơ chế, song chưa thể phân bổ 6.033151% của R90 thành bao nhiêu điểm phần trăm cho từng thay đổi. Việc ghi thêm visited và thay vị trí chuẩn bị seed cũng thay cửa sổ merge_time trong ON. Các timer ON đo công điều phối của phiên được quan sát, không cho phép trừ trực tiếp khỏi latency OFF. [Ablation và giới hạn](../../task-da/B1_A1_NARROW_REPLICATION_REPORT_20261119.md) · [Giải thích kỹ thuật đã kiểm duyệt](../../task-da/TASK_D_B1_A1_TECHNICAL_EXPLANATION.md)

## Chương 6. Thực nghiệm R90 và tích hợp Task A × Task D

### 6.1 Từ G0 đến hai lượt OFF bị dừng

G0 chọn câu hỏi tích hợp và thống nhất bốn tổ hợp, đặt điều kiện nhận đủ graph có provenance trước khi đo. G1 xác minh 6/6 canonical adjacency, 30/30 tiến trình đối chứng, 30.000 phép kiểm khoảng cách f64 có sai số 0.0. Đây là kiểm tương thích. Stage 5 của G2 v1 sau đó hiệu chỉnh trên validation. Stage 6 chạy test 3k đạt điểm recall nhưng có span 0.001033, vượt 0.0001. G2 v1 giữ QUALITY_HOLD. Trong v2, design-2 dừng ở guard, design-3 qua qualification và quality ON như Chương 3. [Kế hoạch cổng tích hợp](../../task-da/AXD_JOINT_BUILD_SEARCH_GO_NO_GO_PLAN.md) · [G1 runtime](../../task-da/AXD_G1_RUNTIME_PARITY_REPORT.md) · [Stage 6](../../task-da/AXD_G2_STAGE6_FINAL_DECISION.md)

| Lượt OFF | Điều xảy ra | Sử dụng trong phân tích |
|---|---|---|
| design-3 | Tiến trình đầu thành công, parser yêu cầu khóa counters trong khi binary OFF bỏ khóa, gây KeyError | HOLD, niêm phong 11/11 file. Bản 3.1 chỉ sửa parser, giữ nguyên engine, ngưỡng, qualification và quality. |
| design-3.1 run1 | Hoàn tất 119/144, dừng ở #120 khi timer firmware đẩy tải host 0.0266 vượt cap 0.0250 | HOLD, niêm phong 1080/1080. Không đưa receipt vào ước lượng run2. |
| design-3.1 run2 | Chạy lại từ block 0, đủ 144/144 OFF, 1299/1299 tệp khớp manifest, Tctl tối đa 78.5°C | Toàn bộ 12 block đi vào ước lượng đã đăng ký. |

### 6.2 Đúng đắn và chất lượng

Có **20.000 query ID duy nhất** qua hai panel, 10k test và 10k validation. Bộ 18 tiến trình ON mới gồm 12 test (base và opt trên sáu graph) và sáu val opt. Sáu val base từ Stage 5 tại beam 432 cung cấp tham chiếu. Điều đó cho **120.000 đối chiếu ON** từng cặp base/opt, 60k test và 60k val. Tất cả có top-10 cùng ID, thứ tự, squared L2. Mỗi tiến trình OFF đối chiếu digest với test ON đúng graph/policy, đạt **144/144**. Khối lượng chạy mới là 180.000 bản ghi ON và 1.440.000 OFF, tổng **1.620.000 execution records**. Từng query được xử lý nhiều lần cho các điều kiện khác nhau. [Quality ON](../../task-da/AXD_G2_V2_QUALITY_RESULTS.md) · [Audit cuối](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)

Cận dưới Recall@10 đồng thời thấp nhất là 0.991188, vượt 0.990. Giữa hai nhánh build, Fast − Stock = +0.000117, CI95 [−0.000051, +0.000284] nằm trong biên Gate B ±0.0005 cho **Recall trung bình của cohort**. Parity base/opt trong cùng graph và kiểm biên recall giữa hai nhóm graph có đối tượng khác nhau. Chưa có kiểm định tương đương cho thời gian SEARCH Fast/Stock.

### 6.3 Measured SEARCH trên Host D

| R90, arm | Recall@10 | Mean µs/query | P50 / P95 / P99 (µs) | QPS_wall | CPU-s tiến trình | Peak RSS (KiB) |
|---|---:|---:|---|---:|---:|---:|
| Stock + baseline | 0.992050 | 3619.87 | 3735.78 / 4100.25 / 4229.57 | 276.24 | 76.073 | 871687.8 |
| Stock + B1+A1 | 0.992050 | 3401.51 | 3511.46 / 3926.75 / 4057.93 | 293.97 | 70.661 | 871678.6 |
| Fast v2 + baseline | 0.992167 | 3619.54 | 3736.64 / 4097.79 / 4226.94 | 276.26 | 76.164 | 871704.0 |
| Fast v2 + B1+A1 | 0.992167 | 3401.14 | 3511.66 / 3925.58 / 4052.84 | 294.00 | 70.818 | 871732.0 |

Mỗi arm có 36 tiến trình OFF (3 graph × 12 block). Gộp theo policy, mean 3619.71 → 3401.33 µs, mức giảm geometric paired **6.033151%**, speedup **1.064205×**. Cận dưới primary, drift và joint ở Chương 3 đều vượt 3%. P50 giảm 6.01%, P95 giảm 4.22%, P99 giảm 4.09%. Các số này là so sánh tóm tắt quantile theo lượt. QPS một luồng truy vấn tăng 276.25 → 293.99. CPU-s trung bình mỗi tiến trình giảm 76.118 → 70.740. Chênh peak RSS gộp +9.39 KiB. Các điều kiện giới hạn tail, RAM, thứ tự và nhiễu ghi trong audit đều đạt. Kết luận **GO_A_FIXED_COHORT**. [Bảng bốn arm](tables/table05_g2_2x2_arms_summary.csv) · [Chi tiết từng graph](tables/table10_per_graph_r90.csv)

| Fixed graph | Stock r1 | Stock r2 | Stock r3 | Fast r1 | Fast r2 | Fast r3 |
|---|---:|---:|---:|---:|---:|---:|
| Mức giảm mean latency ghép cặp (%) | 6.0633 | 5.9985 | 6.0353 | 6.0086 | 6.0834 | 6.0097 |
| Recall@10 (hai policy khớp trong graph) | 0.99209 | 0.99197 | 0.99209 | 0.99229 | 0.99197 | 0.99224 |

Sáu phép bỏ lần lượt một graph cho khoảng điểm 6.023–6.040%. Nhóm AB đạt 6.025%, BA đạt 6.041%. Những phép kiểm này hạn chế khả năng một graph hoặc thứ tự chạy duy nhất chi phối kết quả. Chúng giữ cố định cohort. [Kết quả run2](../../task-da/AXD_G2_V2_DESIGN3_1_RESULTS.md)

### 6.4 Dấu vết của cơ chế trong Quality ON

| Bộ đếm trung bình mỗi query | Baseline | B1+A1 | Thay đổi |
|---|---:|---:|---:|
| L2 duy nhất | 19064.1601 | 19064.1601 | 0 |
| L2 trùng | 3712.8081 | 928.7730 | −2784.0351 (−74.98%) |
| Tổng L2 | 22776.9682 | 19992.9331 | −2784.0351 (−12.22%) |
| Gặp ID đã thấy | 3293.2500 | 6077.2851 | +2784.0351 |
| Lượt xét láng giềng | 26069.2182 | 26069.2182 | 0 |
| Số lần mở rộng / số lần chèn frontier | 456.6799 / 2548.8228 | 456.6799 / 2548.8228 | 0 / 0 |
| Vòng gộp | 14.8660 | 14.8660 | 0 |

Dấu hiệu một-đổi-một là 2784.0351 lần gặp ID đã thấy tăng thêm đi kèm đúng số lượt L2 trùng bị bỏ. Mức giảm 74.98% có mẫu số là **phần L2 trùng**. Phần này chỉ là một phần của tổng L2; tổng L2 lại chỉ là một phần của thời gian tường gồm hàng đợi, đọc danh sách kề, gộp và đồng bộ. Trong ON, merge_time 348.5078 → 384.3943 µs/query, barrier_wait 219.7238 → 224.3944, sync_wait 568.0947 → 608.6533. A1 đưa bước giao seed vào cửa sổ đo merge. Với observer chưa qua kiểm tương đương và thiếu PMU, chưa thể gán bao nhiêu µs OFF tiết kiệm cho cache hay từng phép toán. Các giá trị chính xác ở đây phản ánh **erratum thứ nhất** về các số chép tay ở §5 của báo cáo lịch sử. [Dữ liệu ON](tables/table09_on_l2_counters.csv) · [Đính chính đầy đủ](../../task-da/TASK_D_FINAL_RESEARCH_SYNTHESIS.md)

### 6.5 Measured BUILD trên Host A và mô hình hai máy

Task A đo BUILD trên tai-linux với bốn luồng, H85 Highway 6bc2d477, C160/K1024/N2. Biên nhận Stock là 42.57, 41.99, 42.21 s; Fast v2 là 33.84, 33.74, 33.80 s. Fast v2 giảm số lần đóng gói trong builder. Mean BUILD giảm 42.257 → 33.793 s, tiết kiệm khoảng **8.463 s (20.03%)** cho một lần xây chỉ mục. Peak RSS BUILD trung bình theo biên nhận là 3,118,754.667 KiB (Stock) và 3,115,521.333 KiB (Fast), xấp xỉ 2.9743 và 2.9712 GiB. Tổng sáu graph 1.292.447.108 byte. Task D dùng lại đúng sáu file để đo SEARCH trên Host D. [Biên nhận BUILD](../../../../configs/axd_g2_v2_build_reference.json) · [Provenance cohort](../../task-da/AXD_G1_GRAPH_ARTIFACT_MANIFEST.md)

Khi giữ nguyên policy, mean SEARCH theo quy ước Fast trừ Stock là −0.330 µs cho baseline và −0.367 µs cho B1+A1. CI của cả hai contrast chứa 0. Hiệu ứng SEARCH trong từng nhánh là khoảng 218.36 µs (Stock) và 218.40 µs (Fast). Hiệu của hai hiệu ứng, Fast_gain − Stock_gain, là **+0.037 µs, CI95 [−2.582, +2.655] µs**. Dữ liệu tương thích với chênh lệch nhỏ theo cả hai chiều. Chưa phát hiện tương tác và chưa thể kết luận hai cơ chế độc lập tuyệt đối hoặc cộng hưởng. [Kết quả thực nghiệm](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md)

Với nhánh xây dựng g, policy s và Q truy vấn tuần tự, mô hình tính T(g,s,Q) = BUILD_HostA(g) + Q × mean_SEARCH_HostD(g,s) / 1.000.000, dùng BUILD tính bằng giây và mean tính bằng µs. So sánh đường chéo Stock/base với Fast/opt cho chênh SEARCH 218.730 µs/query vì **cả hai** yếu tố đổi. Đây là đại lượng khác với mức giảm mean SEARCH của B1+A1 khi giữ graph.

| Q | T(Stock,base), s | T(Fast,opt), s | Tiết kiệm ΔT, s | CI95 block-t cho ΔT, s |
|---:|---:|---:|---:|---|
| 100.000 | 404.244 | 373.908 | 30.336 | [30.071, 30.602] |
| 1.000.000 | 3662.131 | 3434.938 | 227.194 | [224.537, 229.850] |

Tại 100k, khoảng 8.463 s đến từ BUILD, 21.873 s đến từ chênh SEARCH đường chéo. Các CI điều kiện hóa trên sáu biên nhận BUILD cố định. Chi phí truyền file giữa hai máy và nạp index nằm ngoài T. Khoảng 3.91–3.93 s non-batch quan sát cục bộ còn gồm warmup và ghi file, không đo toàn bộ chi phí triển khai. **Erratum thứ hai** xác định 30.336 và 227.194 là *số giây tiết kiệm*, hai cột T là *tổng thời gian mô hình hóa*. G2 đạt **GO_B_SYSTEM_FIXED_COHORT** theo mô hình này. Một lần triển khai BUILD–SEARCH trọn vẹn trên cùng máy chưa được đo. [Bảng mô hình](tables/table12_modeled_two_host_build_search.csv) · [Kiểm toán và giới hạn triển khai](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)

## Chương 7. Đóng góp, giới hạn và quyết định

### 7.1 Trả lời các câu hỏi nghiên cứu

| Câu hỏi | Kết luận | Điều còn chưa biết |
|---|---|---|
| RQ1 · Giới hạn scaling | Một cấu hình PipeANN ở T16 có QPS thấp hơn T8 dù recall khớp. Trên CPU trong RAM, hai hay bốn walker có thể tăng tốc so với một worker của R86, với mức lợi ích phụ thuộc S. | Đường găng thực sự của từng query trên CPU–SSD và serving nhiều query ở R90. |
| RQ2 · Graph × worker | Ở R86, đổi A0 sang A3 thay cả số vòng, số L2 và speedup, thậm chí đổi dấu contrast khi thay S. Cần xem graph cùng với điểm vận hành. | Độ lớn tương tác trên build độc lập và strict matched-recall trên toàn bộ ma trận. |
| RQ3 · Lãng phí và điều phối | Việc bỏ dấu visited cho hit bị loại và gửi toàn bộ frontier tạo công có thể tránh. B1+A1 giữ kết quả từng query và giảm thời gian thực đo. E0/E2 và H3 chỉ ra những tình huống không đủ ngân sách cho điều phối phức tạp. | Tỷ trọng chu kỳ OFF của từng phần và lợi ích riêng B1, A1 trên R90. |
| RQ4 · Kết hợp hai pha | Fast v2 giảm BUILD trên Host A. B1+A1 giảm SEARCH trên Host D ở cả hai loại graph. Dữ liệu fixed cohort cho phép chiếu số giây tiết kiệm với Q xác định. | Interaction population, truyền và nạp khi triển khai, chi phí đầu–cuối native trên một máy. |

**Mục tiêu 1** có sản phẩm là khung D01–D10, so sánh cơ chế theo pha và mô tả thuật toán đến mức mã nguồn. **Mục tiêu 2** có các giả thuyết có đối chứng, có điều kiện dừng và có kết quả âm. TP-CG chưa mở cài đặt. **Mục tiêu 3** có engine, dữ liệu bất biến, phân tách ON/OFF và thử nghiệm tích hợp G2 đã audit. P3 chính thức, chạy chéo host, GPU và dataset thứ hai có trạng thái riêng. C1 đóng COMPLETE, C2 và C3 đóng COMPLETE_WITH_SCOPE theo ma trận bàn giao. Việc giảng viên chấp nhận các giới hạn cho báo cáo của môn học là quyết định riêng. [Ma trận đóng mục tiêu](TASK_D_OBJECTIVE_CLOSURE_MATRIX.md)

Đóng góp khảo sát là nối pha BUILD và SEARCH bằng taxonomy đủ chi tiết để nhận ra hai phương pháp trùng cơ chế. Đóng góp phương pháp là thiết kế kiểm tra chất lượng trước timing, nhận diện observer tự gây nhiễu, với các lần HOLD còn truy xuất được. Đóng góp kỹ thuật là triển khai cặp thay đổi cụ thể trên baseline đa walker và kiểm mức giảm công đi cùng parity. Phần A×D thêm một phép kiểm tương tác ở chất lượng được ràng buộc và một mô hình thời gian có đơn vị, nguồn và biên hệ thống rõ ràng. So với prior art đã có visited/checked và frontier phẳng, bằng chứng hiện tại định vị công trình là **nghiên cứu hệ thống thực nghiệm**. [Đóng góp và giới hạn](../../task-da/TASK_D_SCIENTIFIC_CONTRIBUTIONS_AND_LIMITATIONS.md)

### 7.2 Các nguy cơ đối với diễn giải

- **Giá trị nội tại.** Cặp baseline/opt dùng chung binary và output được đối chiếu tận ID. Guard và thứ tự AB/BA giảm ảnh hưởng của tải và drift. Governor động vẫn hoạt động. Việc thay vị trí đo của timer ON và giới hạn observer khiến phân rã chu kỳ OFF còn UNKNOWN.
- **Đại lượng đại diện.** Số phép tính khoảng cách khác thời gian CPU, CPU-s khác năng lượng. Máy không có chuỗi RAPL hợp lệ trong hồ sơ đo. Phase observer và work counters không thể điền thay số joule/query. QPS với jobs=1 chưa mô tả throughput khi các request tranh tài nguyên.
- **Độ khái quát.** Chỉ một host SEARCH chính, một dataset G2, một điểm p/S/beam và sáu graph cùng SEED=555. Panel rời nhau theo ID nhưng lấy từ public pool đã được sử dụng. **EXPLORATORY_HOST_SPECIFIC** và **graph_population_ci = NOT_ESTIMABLE** áp dụng cả khi CI theo block rất hẹp.
- **Phạm vi tích hợp.** Lợi ích tổng có điều kiện trên thời gian BUILD lịch sử và giả định Q query tuần tự trên index xây một lần. Thay tần suất rebuild, topology, tải đồng thời hay môi trường triển khai sẽ thay câu hỏi cần đo. [Audit giới hạn](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)

**Quyết định ở mốc đóng hồ sơ.** G2 CLOSEOUT COMPLETE, RESEARCH PAUSED, G3 NOT_OPENED. Nếu giảng viên yêu cầu kiểm tra khả năng suy rộng qua RNG, đối tượng cần thay đổi là gốc build độc lập. Nếu câu hỏi là khả năng triển khai, phép đo cần bao gồm cả BUILD, truyền/nạp và SEARCH trong cùng kịch bản. Một bộ lặp lớn hơn trên sáu graph cũ không trả lời hai câu hỏi đó. Đây là những câu hỏi cho đề cương tương lai nếu owner và giảng viên yêu cầu. [Quyết định đóng G2](../../task-da/AXD_G2_CLOSEOUT_AND_G3_DECISION.md) · [Các quyết định để giảng viên xem xét](TASK_D_FINAL_ADVISOR_DECISION_CHECKLIST.md)

## Tài liệu tham khảo

Các công trình dưới đây là nguồn cho so sánh cơ chế ở Chương 2. Năm, tên hệ thống và vị trí được dùng theo danh mục paper đã khảo sát.

1. Speed-ANN (2022), §4 thuật toán 2–3, §5 về đường duyệt và phép gộp. [Bản tác giả](https://arxiv.org/pdf/2201.13007)
2. iQAN (PPoPP 2023), §§4–6, path-wise traversal và đồng bộ. [Bản camera-ready](https://johnpzh.github.io/assets/papers/PPoPP-2023_iQAN_Zhen.CameraReady.pdf)
3. ParlayANN (PPoPP 2024), §§3–5, batch snapshot và xử lý cạnh ngược. [Bài báo](https://doi.org/10.1145/3627535.3638475)
4. AverSearch (2025), §4 về phân vai và §5.3 về giới hạn nguồn công. [Bản tác giả v2](https://arxiv.org/html/2504.20461v2)
5. DiskANN (NeurIPS 2019), §§3.1–3.3, graph Vamana và batched SSD beam search. [Kỷ yếu NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2019/hash/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Abstract.html)
6. PipeANN (OSDI 2025), §§3–4, Fig. 10, cơ chế xen kẽ issue–explore. [Kỷ yếu USENIX](https://www.usenix.org/system/files/osdi25-guo.pdf)
7. LAANN (2026), §§3–6, memory-first look-ahead và thứ tự ưu tiên. [Bản tác giả](https://arxiv.org/pdf/2606.02784)
8. FAISS GPU (2017), §§4–6, WarpSelect, GEMM và pipeline chọn top-k. [Bản tác giả](https://arxiv.org/pdf/1702.08734)

## Phụ lục. Cách lần từ một kết luận về bằng chứng

| Kết luận trong báo cáo | Đầu mối bằng chứng | Phép kiểm và giới hạn |
|---|---|---|
| Giảm thời gian SEARCH 6.033151% | [C1 và các giới hạn U1–U4](../../task-da/TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md), [CI](tables/table06_ci_families.csv) | Đọc ước lượng log ghép cặp và CI theo 12 block. Không lấy 1.44M dòng làm df. |
| Bảo toàn kết quả và giảm L2 | [C2 và C4](../../task-da/TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md), [counters](tables/table09_on_l2_counters.csv) | Kiểm unique + duplicate = total, thay đổi already_seen bằng số L2 được bỏ. Liên hệ với parity ON và digest OFF. |
| Fast v2 giảm BUILD, có lợi ích mô hình hai máy | [Sáu biên nhận](../../../../configs/axd_g2_v2_build_reference.json), [bảng tích hợp A×D](TASK_A_D_INTEGRATION_HANDOFF.md) | Đối chiếu graph SHA, đơn vị µs sang giây, tính lại ΔT theo từng Q, điều kiện hóa trên BUILD. |
| Các lần bác bỏ và chuyển hướng | [N1–N5 và các mục chưa thực nghiệm](../../task-da/TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md), [dòng thời gian](../../task-da/TASK_D_RESEARCH_TIMELINE.md) | Lần ngược từ từng nhánh tới protocol, subject và điều kiện dừng riêng. |
| Đóng mục tiêu và lưu trữ | [Ma trận](TASK_D_OBJECTIVE_CLOSURE_MATRIX.md), [evidence index](TASK_D_EVIDENCE_INDEX.md), [trạng thái lưu trữ](../../task-da/AXD_G2_FINAL_CLOSEOUT_STATUS.md) | Kiểm chỉ số và phạm vi trước khi trích sang báo cáo nhóm. |

**Nhận diện phiên bản.** Source engine tại f2cd634b837a70735c3e31e5956f0524bfc26675, ELF SHA-256 7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1. Graph Task A theo f5e48bb681812ce51aed7272f30ecefc85ed427b. Protocol AXD-G2-V2-3A-20261123, design-3.1, manifest SHA-256 bc8974193970b1663a53e08bc7de16b91013f11866965f872a78d775b7b28f5e. Commit 4bc70ff đóng gói bằng chứng, d0f4816 ghi kết quả xác minh kho lưu trữ, a0916db45563ae90bbe8d4e73ad202b6a2991d3e tổng hợp khoa học. [Manifest mã, giao thức, graph, binary và đầu vào](../../task-da/AXD_G2_V2_DESIGN3_1_EVIDENCE_MANIFEST.md)

**Tái kiểm chỉ đọc từ gốc checkout D.** Ba lệnh sau lần lượt xem mã thực sự dùng để build, kiểm 29 mục niêm phong và đối chiếu hai đầu ra phân tích cục bộ với digest gốc. Hai file JSON nằm trong bộ bằng chứng riêng của owner. Đối chiếu kết quả với f0a35394f028550a1f14f4928467a62e5d09363a2ef26cffa160d0c7e200615c (analysis) và c79e45a3482a702b8ca0aa48c68089c86875db025e002e8523109abb656e9c66 (independent audit).

~~~sh
git show f2cd634:research/task_da/search_common/p2_engine.hpp
sha256sum -c docs/research/task-da/AXD_G2_V2_DESIGN3_1_FREEZE.sha256
sha256sum ../artifact-evidence/axd-g2-v2-off-design3_1_run2-analysis.json ../artifact-evidence/axd-g2-v2-final-audit-design3_1/audit_results.json
~~~

Biên bản audit ghi **AUDIT_PASS, 0 discrepancies**. Release riêng tư có tag axd-g2-v2-design3.1-closeout-20261125. Tier 1 chứa phần lõi, Tier 2 giữ dấu vết forensic, gói dependencies giữ sáu graph và ELF. Mốc closeout đã tải ngược và đối chiếu byte/SHA cho **9/9** asset. Bản tổng hợp bàn giao có thể dùng mà không phân phối lại dữ liệu vector hay tệp raw. [Archive và manifest gốc](../../task-da/AXD_G2_FINAL_CLOSEOUT_STATUS.md)
