# Thực thi song song trong tìm kiếm láng giềng trên đồ thị

*Bản dự thảo bàn giao để ghép vào báo cáo nhóm. Phần từ “Nhiệm vụ” đến “Kết luận” có thể dùng trực tiếp. Gợi ý vị trí ghép ở cuối tài liệu.*

## Nhiệm vụ và kết quả khảo sát

Với một truy vấn ANN, chỉ sau khi mở rộng một đỉnh, bộ tìm kiếm mới biết các ứng viên tiếp theo. Nhiều lõi có thể xét các nhánh đã sẵn sàng cùng lúc, nhưng các nhánh có thể gặp lại cùng một đỉnh và các worker phải phối hợp để giữ danh sách ứng viên tốt nhất. Task D nghiên cứu khi nào việc phân phối công việc rút ngắn thời gian trả lời ở cùng chất lượng tìm kiếm.

Khảo sát dẫn đến ba cách đặt bài toán. Trên CPU nhiều lõi, Speed-ANN và iQAN cho các walker tiến trên nhiều nhánh trước khi hợp nhất. Khoảng cách giữa các lần đồng bộ chi phối cả tiến độ lẫn số phép tính lặp. Trong hệ CPU–SSD, DiskANN gom yêu cầu đọc và PipeANN cho phát yêu cầu kế tiếp trong lúc xử lý dữ liệu đã về. Đại lượng cần xem ở đây là phần I/O nằm trên đường găng. Trên GPU, FAISS khai thác song song dữ liệu khi tính khoảng cách và chọn top-k, với hiệu quả phụ thuộc batch và bộ nhớ. Từ ba cụm, nhóm chọn câu hỏi có thể kiểm trực tiếp trên CPU: nếu giữ đồ thị và quy tắc chọn ứng viên, có thể giảm công việc của từng vòng mà vẫn trả về cùng kết quả hay không? [Bảng phân loại cơ chế](tables/table02_taxonomy_d01_d10.csv)

## Những phép thử dẫn tới B1+A1

Trên SIFT10M, PipeANN bản paper portable giảm 13.36% QPS khi tăng từ 8 lên 16 luồng ở cấu hình Issue 32. Hiện tượng này đặt ra câu hỏi về tranh chấp tài nguyên, còn nguyên nhân D1/D4/D6 vẫn chưa được xác lập. Ở nhánh phân vai theo AverSearch, chính sách đổi vai chỉ thắng đường bao hai lịch tĩnh trong 3/108 cấu hình mô hình. Trên prototype SIFT1M dùng chung một mutex, lịch tĩnh một maintainer đạt 19.21 QPS, cao hơn lịch thích nghi 15.09 QPS. Việc tiếp tục thêm vai trò không giải quyết điểm tuần tự hóa này. [Dòng thời gian và đối chứng](../../task-da/TASK_D_RESEARCH_TIMELINE.md)

Trên các đồ thị R86 của Task A, chênh lệch speedup giữa các graph phụ thuộc cả số worker, chu kỳ đồng bộ và cấu trúc frontier của baseline. Khi thử dùng độ chồng lặp của seed để đổi lịch, khoảng 79–80% công việc trùng trong trace phát sinh giữa các nhánh được khám phá sau lúc giao seed. Tín hiệu rẻ không thắng đối chứng degree sau khi tính phí. Nhóm dừng TP-CG trước khi cài policy online và quay lại kiểm tra công việc thừa trong chính engine đối chứng. [Sàng lọc H3](../../task-da/H3_OVERLAP_SIGNAL_SCREENING_RESULTS.md)

## Thay đổi của Task D và thiết kế đánh giá

Engine dùng các vòng đồng bộ. Trong một vòng, mỗi worker mở rộng tối đa S bước trên frontier cục bộ, sau đó coordinator hợp nhất kết quả. Với **B1**, worker ghi lại các đỉnh mới đã tính khoảng cách. Coordinator đánh dấu chúng tại barrier để các vòng sau có thể bỏ qua phép tính từng làm. Hai worker vẫn có thể cùng tính một đỉnh trong một vòng. Với **A1**, coordinator duy trì frontier tăng dần và chỉ chuyển cho worker phần đầu mà quota S có thể dùng. Do đó worker giảm số thao tác nạp seed vào hàng đợi. Các thay đổi thuộc phần thực thi của Task D. [Phân tích mã nguồn B1 và A1](../../task-da/TASK_D_B1_A1_TECHNICAL_EXPLANATION.md)

Nhóm so hai chính sách trên từng graph trong sáu graph R90 P0A v1.3 của Task A, gồm ba Stock và ba Fast v2. SEARCH dùng MS-Turing-1M trên Ryzen 5 PRO 4650U, p=2, S=16, beam=432, jobs=1. Chế độ ON dùng để so IDs, thứ tự, squared L2 và đếm công việc. Chế độ OFF dùng để đo thời gian. Mười hai block cân bằng tạo 72 cặp tiến trình, chia đều hai thứ tự baseline trước và B1+A1 trước. Hai lần chạy từng bị HOLD được giữ trong hồ sơ lịch sử; kết quả chính dùng trọn run2. [Audit độc lập](../../task-da/AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md)

## Kết quả SEARCH trên Host D

| Đại lượng trên cohort cố định | Baseline | B1+A1 |
|---|---:|---:|
| Mean latency OFF (µs/query) | 3 619.71 | 3 401.33 |
| P95 / P99 OFF (µs/query) | 4 099.02 / 4 228.25 | 3 926.16 / 4 055.39 |
| QPS theo wall time (jobs=1) | 276.25 | 293.99 |
| Duplicate L2 ON (lần/query) | 3 712.81 | 928.77 |
| Total L2 ON (lần/query) | 22 776.97 | 19 992.93 |
| Recall@10 trung bình | 0.992108 | 0.992108 |

Mức giảm mean latency theo ước lượng ghép cặp là **6.033151%**, CI95 block-t **[5.976580%, 6.089687%]**. Duplicate L2 giảm 74.98%, total L2 giảm 12.22%, trong khi unique L2 giữ ở 19 064.16 mỗi truy vấn. Khoảng cách giữa mức giảm số phép tính lặp và thời gian cho thấy query vẫn phải trả chi phí mở rộng đỉnh, thao tác frontier và đồng bộ. Mức đóng góp riêng của mỗi chi phí vào latency OFF chưa được định lượng. Có 120 000 cặp đối chứng ON và 144/144 tiến trình OFF khớp digest tham chiếu trên các panel dùng để xác minh. [Bảng kết quả bốn arm và hai hàng gộp](tables/table05_g2_2x2_arms_summary.csv)

## Kết quả chung với Task A

Task A xây đồ thị Fast v2 với tiền lọc FP32 trước bước đóng gói. Trên Host A, thời gian BUILD trung bình của ba receipt mỗi arm giảm từ 42.257 xuống 33.793 giây, tương ứng **20.03%**. Task D đo SEARCH trên chính các graph đã chuyển giao. Hiệu giữa mức tiết kiệm SEARCH trên Fast và trên Stock là +0.037 µs, CI95 [−2.582, +2.655] µs. Với độ phân giải của phép thử, nhóm chưa phát hiện tương tác.

Với Q truy vấn thực hiện tuần tự, cộng thời gian BUILD trên Host A với Q lần thời gian SEARCH trên Host D cho dự báo tiết kiệm **30.336 giây ở Q=100 000** và **227.194 giây ở Q=1 000 000**, khi so Fast+B1+A1 với Stock+baseline. Mô hình loại chi phí truyền và nạp chỉ mục. Đóng góp của Task A được đo một lần theo mỗi lần xây, còn phần SEARCH tích luỹ theo số truy vấn. [Bảng tích hợp dùng chung](TASK_A_D_INTEGRATION_HANDOFF.md)

## Kết luận

Task D xác định được công việc lặp có thể loại bỏ, sửa engine tại barrier và frontier, rồi kiểm tra đồng thời quỹ đạo truy vấn, chất lượng và thời gian. Sáu graph cùng gốc RNG 555 giới hạn suy luận ở cohort đã đo. Kết luận phù hợp là một cải tiến hệ thống trên cấu hình CPU cụ thể, với kết quả âm được lưu cho các lịch động đã sàng lọc. Trạng thái nghiên cứu là G2 CLOSEOUT COMPLETE, RESEARCH PAUSED và G3 NOT_OPENED. [Ma trận claim–evidence](../../task-da/TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md)

## Gợi ý ghép vào bản chung

Đặt hai đoạn khảo sát sau phần giới thiệu graph ANN. Trong chương phương pháp, nối từ phần Task A bằng câu “Sau khi cố định từng đồ thị đã xây, nhóm thay đổi chính sách thực thi truy vấn trên cùng các cạnh và cùng tập test.” Đặt bảng SEARCH cạnh bảng BUILD của Task A và giữ một bảng 2×2 duy nhất ở phần kết quả chung. Nếu cần rút ngắn, giữ phương pháp B1+A1, bảng SEARCH và đoạn mô hình hai máy. Câu chuyển sang thảo luận là “Phép thử ghép cặp giải thích được lợi ích trên cohort hiện tại, còn tác động của seed mới, host khác và tải nhiều truy vấn đồng thời vẫn là câu hỏi mở.”
