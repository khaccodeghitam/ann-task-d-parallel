# Xin ý kiến giảng viên về hướng kết thúc Task D × Task A

**Đề nghị chọn A, hoàn thành báo cáo nghiên cứu thực nghiệm và kết quả âm.** Đề xuất ngày 15/11 đặt một điều kiện trước khi phát triển thuật toán mới. Nhóm cần tìm được chi phí đáng kể do cách phân việc gây ra và có tín hiệu đủ rẻ để giảm chi phí ấy. Đến ngày 20/11, nhóm đã đo được quan hệ giữa graph, cấu hình worker và latency trên một hệ thống cụ thể. Điều kiện để mở thuật toán mới vẫn chưa đạt. [Đề xuất gốc và đối chiếu từng cổng](ORIGINAL_PROPOSAL_FINAL_REASSESSMENT.md)

| Nội dung trao đổi | Nhóm có thể trình bày |
|---|---|
| **H1 · Graph nào tận dụng được nhiều worker hơn?** | Trên MS-Turing-1M và Ryzen 4650U, ở cùng p=2, flat merge và S=16, speedup trung bình là 1,55× trên A0 và 1,43× trên A3. Beam đã hiệu chỉnh để Recall rất gần nhau trên validation. Cặp A0/A3 vẫn có chênh lệch chất lượng trên test. Ở p=4, lựa chọn S có thể đổi thứ tự về speedup tương đối. |
| **H2 · Vì sao lại khác?** | Ở p=2/S16 trước tối ưu B1+A1, A3 cần khoảng 32 round/query và A0 cần 14. A3 cũng có nhiều lần tính khoảng cách trùng hơn. Nhóm xác định được chỗ engine lặp công, nhưng chưa biết bao nhiêu phần latency bình thường đến riêng từ L2, frontier hay cache. |
| **B1+A1 đem lại gì?** | B1 công bố đầy đủ node đã tính khoảng cách tại biên đồng bộ. A1 chỉ chuẩn bị phần frontier cần cho round kế. Cùng top-10 và khoảng cách, latency giảm 12,29% và 10,08% trên hai build A3 được kiểm lại. CI95 qua hai build là [−2,84%, 25,21%], nên mở rộng kết luận vẫn **HOLD**. Đây là đóng góp kỹ thuật cho baseline. |
| **Vì sao dừng H3?** | Trên 6.095 round của ba graph A3, sketch overlap để gán seed kém cân tải theo degree và không vượt đối chứng placebo một cách ổn định. Kết quả là sàng lọc offline. TP-CG chưa triển khai. Trong phép kiểm cuối, 384/384 output khớp nhưng CI95 cho chênh lệch latency của observer vượt biên tương đương ±2%. Nhóm chưa xác định được bottleneck OFF để nhắm tới. |

**Điểm cần giữ trong báo cáo.** Ba lần build lịch sử cùng gốc ngẫu nhiên 555. A0 trên panel disjoint trượt sàn Recall (0,98940). Chưa có so sánh native với các engine ngoài, dữ liệu thứ hai hoặc kết quả cross-host. Giảng viên có thể đánh giá giá trị của phép đo tương tác và quyết định dừng có căn cứ, còn điều kiện nghiệm thu và khả năng công bố vẫn cần xem xét riêng. [Ma trận bằng chứng](TASK_D_EVIDENCE_AND_CLAIM_MATRIX.md)

**Lựa chọn A — đề nghị hiện tại.** Chốt bản thảo quanh ba phát hiện có thể kiểm lại: scaling phụ thuộc đồng thời vào graph và baseline, B1+A1 giảm công và latency trong các build đã đo, và overlap chưa trả được chi phí lập lịch. Xin giảng viên xác nhận phạm vi claim này có đáp ứng mục tiêu học thuật của đề tài hay cần bổ sung đối chứng cụ thể. [Bản thảo](TASK_D_EXPERIMENTAL_SYSTEMS_STUDY_DRAFT.md)

**Lựa chọn B — chỉ khi giảng viên yêu cầu một đề tài thuật toán.** Giảng viên và owner cần thống nhất câu hỏi, phạm vi và giả thuyết mới, khác prior art, cùng tiêu chí bác bỏ và đối chứng đủ mạnh. Nếu cần cohort độc lập, Task A còn phải xác nhận builder, ISA và cách cấp seed trước khi owner xét R4/R5. Đây là quyết định riêng với việc hoàn thành bản thảo hiện tại. [Đánh giá khả thi R4/R5](TASK_A_R4_R5_FEASIBILITY_REVIEW.md)

**Trạng thái bàn giao.** Historical P0, Full P1 và t0998 **HOLD**. P3 official **CLOSED**. H3/TP-CG **NOT_OPENED**. i5-14600KF **NOT_RUN**.
