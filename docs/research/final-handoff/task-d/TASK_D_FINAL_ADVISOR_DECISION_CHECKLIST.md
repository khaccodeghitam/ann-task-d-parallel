# Phiếu quyết định của giảng viên hướng dẫn

**Ngày chuẩn bị 25/11/2026 · Trạng thái học thuật: ADVISOR_DECISION_REQUIRED.** G2 đã hoàn tất và nghiên cứu đang tạm dừng. Giảng viên có thể ghi nhận phần đã đạt, yêu cầu sửa cách trình bày, hoặc chỉ ra câu hỏi khoa học còn thiếu. Hai quyết định dưới đây giữ trống để ghi tại buổi duyệt.

## Căn cứ trước khi quyết định

| Câu hỏi thẩm định | Kết quả có thể kiểm tại buổi duyệt |
|---|---|
| Mục tiêu 1 có giải thích được cách ANN khai thác song song? | Báo cáo chương 2 dùng ba cụm và D01–D10. Chương 5 trình bày hai thay đổi, pseudocode, ví dụ, invariant và đánh đổi. [Báo cáo](TASK_D_MASTER_RESEARCH_REPORT.md) |
| Mục tiêu 2 có giả thuyết, đối chứng và điều kiện bác bỏ? | E0 so với hai lịch tĩnh; sàng lọc H3 tính cả chi phí tín hiệu. TP-CG dừng trước prototype. Các kết quả âm và inconclusive còn nguyên scope. [Ma trận mục tiêu](TASK_D_OBJECTIVE_CLOSURE_MATRIX.md) |
| Mục tiêu 3 đã đo gì trên dữ liệu thật? | MS-Turing-1M, sáu graph R90, hai worker, S=16, b432. 18/18 ON và 144/144 OFF. Mean giảm 6.033151%, CI95 block-t [5.976580%, 6.089687%], duplicate/total L2 giảm 74.98%/12.22%. [Kết quả](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md) |
| Đóng góp nào thuộc A, D, và cả nhóm? | A đo BUILD giảm 20.03%. D đo SEARCH và kiểm parity. Hai thành viên cùng diễn giải bốn arm và mô hình hai máy. Tương tác +0.037 µs, CI95 [−2.582, +2.655]. [Handoff A×D](TASK_A_D_INTEGRATION_HANDOFF.md) |
| Có thể kiểm lại một claim từ slide? | Từ slide 6 hoặc 8 mở bảng 06 hoặc 12, lần tới analysis JSON và audit JSON. Hai số 30.336 s và 227.194 s lần lượt là tiết kiệm mô hình ở 100k và 1M query. [Chỉ mục bằng chứng](TASK_D_EVIDENCE_INDEX.md) |
| Điều gì còn ngoài bằng chứng? | Phạm vi EXPLORATORY_HOST_SPECIFIC. Phương sai quần thể graph chưa ước lượng được, p=4 còn bất định, tỷ lệ thời gian OFF theo pha chưa xác thực. Chưa có kết luận novelty, concurrent serving hay chi phí triển khai đầu–cuối. [Giới hạn](../../task-da/TASK_D_SCIENTIFIC_CONTRIBUTIONS_AND_LIMITATIONS.md) |

## E4 · Phạm vi và cách đưa vào báo cáo nhóm

Đề nghị ghi nhận phần khảo sát, phần thử giả thuyết có kết quả âm, phần cải tiến hệ thống B1+A1 và số đo G2 trong cohort cố định. Nhóm xin ý kiến liệu phạm vi đó đáp ứng yêu cầu học phần về ba mục tiêu. [Bản ghép](TASK_D_GROUP_REPORT_CONTRIBUTION.md)

- [ ] Chấp thuận trình bày theo phạm vi trên.
- [ ] Chấp thuận sau khi sửa mục tiêu, câu chữ, bảng hoặc hình được ghi bên dưới.
- [ ] Cần bổ sung minh chứng trước khi quyết định.

Mục/claim cần sửa và điều kiện đạt: ___________________________________________

## E5 · Dừng ở G2 hay lập đề xuất riêng

Khuyến nghị giữ **G2 CLOSEOUT COMPLETE · RESEARCH PAUSED · G3 NOT_OPENED**. Nếu câu hỏi là độ ổn định qua seed, thêm lần lặp process trên sáu graph hiện tại vẫn để nguyên gốc RNG. Nếu câu hỏi là chi phí vận hành, phép đo tương lai cần xác định host, workload và cửa sổ transfer/load. Giảng viên có thể chọn yêu cầu một đề xuất với tiêu chí phân biệt cụ thể.

- [ ] Giữ dừng ở G2 và dùng thời gian còn lại cho báo cáo nhóm.
- [ ] Yêu cầu soạn đề xuất riêng, ghi câu hỏi, đối chứng, tiêu chí đạt/dừng và tài nguyên cần có.
- [ ] Hoãn quyết định tới khi xem bằng chứng được chỉ định.

Câu hỏi / bằng chứng cần xem: _______________________________________________

Người ghi quyết định: ____________________  Ngày: ______________

Bước owner thực hiện sau buổi duyệt: _________________________________________
