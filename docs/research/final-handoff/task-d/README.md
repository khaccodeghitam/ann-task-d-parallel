# Hồ sơ bàn giao Task D

Task D nghiên cứu thực thi song song khi tìm láng giềng trên đồ thị. Trên MS-Turing-1M, sáu graph R90 và Ryzen 5 PRO 4650U, B1+A1 giảm **6.033151% mean latency** ở cùng kết quả top-10. Duplicate L2 giảm **74.98%**, total L2 giảm **12.22%**. **20.03%** là mức giảm BUILD do Task A đo trên Host A. Kết quả ghép BUILD và SEARCH là mô hình hai máy, xem riêng ở tài liệu A×D.

**TASK_D_HANDOFF_READY** · [Kiểm định cuối](HANDOFF_PROGRESS.md)

**Mốc khoa học:** SCIENTIFIC_REVIEW_PASS · RESEARCH_SYNTHESIS_COMPLETE · G2 CLOSEOUT COMPLETE · AUDIT_PASS, 0 discrepancies · REMOTE SHA256 VERIFIED 9/9 · RESEARCH PAUSED · G3 NOT_OPENED. Phạm vi **EXPLORATORY_HOST_SPECIFIC**, **graph_population_ci = NOT_ESTIMABLE**. Tình trạng xác nhận học thuật còn chờ giảng viên.

## Dùng hồ sơ theo công việc

| Việc cần làm | Mở tài liệu | Cách dùng |
|---|---|---|
| Duyệt toàn bộ nghiên cứu | [Master Report](TASK_D_MASTER_RESEARCH_REPORT.md) · [PDF để đọc/in](TASK_D_MASTER_RESEARCH_REPORT.pdf) · [Word để biên tập](TASK_D_MASTER_RESEARCH_REPORT.docx) | Đọc tóm tắt, chương 6 và 7 trước. Dùng chương 4 cho các lần HOLD/NO-GO và chương 5 để giải thích mã. |
| Đóng các mục tiêu được giao | [Objective Closure Matrix](TASK_D_OBJECTIVE_CLOSURE_MATRIX.md) | Tìm REQ-C1–C3 cho ba mục tiêu học phần. Dùng REQ-D1–D9 cho các hướng đi và kết quả âm. |
| Ghép phần cá nhân vào báo cáo nhóm | [Mô-đun báo cáo nhóm](TASK_D_GROUP_REPORT_CONTRIBUTION.md) · [Word với bảng sửa được](TASK_D_GROUP_REPORT_CONTRIBUTION.docx) | Chèn từ phần “Nhiệm vụ” đến “Kết luận”. Hướng dẫn và câu chuyển đoạn nằm cuối bản Markdown. |
| Đối chiếu hai thành viên A và D | [Bảng tích hợp A×D](TASK_A_D_INTEGRATION_HANDOFF.md) · [Dữ liệu chuẩn chưa làm tròn](tables/table14_axd_canonical_integration.json) | Sao chép bốn arm từ cùng nguồn. Giữ chữ “mô hình hai máy” ở tiêu đề biểu đồ T(Q) và phân biệt tổng thời gian với thời gian tiết kiệm. |
| Chọn hình, caption và bảng | [Chỉ mục 16 hình, 14 bảng/dữ liệu](TASK_D_FIGURE_TABLE_INDEX.md) · [figures/](figures/) · [tables/](tables/) | Dùng hình 06–07 cho cơ chế, 09 và 12 cho SEARCH, 14–15 cho BUILD và mô hình. SVG cho bản in, PNG cho phần mềm yêu cầu ảnh raster. |
| Truy từ claim về nguồn | [Evidence Index](TASK_D_EVIDENCE_INDEX.md) · [Claim–Evidence Matrix đã kiểm duyệt](../../task-da/TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md) | Dùng E01–E05 để so raw JSON/biên nhận, S01–S06 để xem đề bài và tài liệu khảo sát gốc. |
| Trình bày trước giảng viên | [PowerPoint và speaker notes](TASK_D_ADVISOR_PRESENTATION.pptx) · [PDF slide](TASK_D_ADVISOR_PRESENTATION.pdf) · [Kịch bản hai thời lượng](TASK_D_PRESENTATION_SCRIPT.md) | Bản 5 phút: slide 1, 3, 4, 5, 6, 8, 10. Bản 11 phút 55 giây: slide 1–10. Hai slide cuối dùng khi có câu hỏi. |
| Chuẩn bị phản biện và chốt buổi duyệt | [36 câu Q&A](TASK_D_DEFENSE_QA.md) · [Phiếu quyết định](TASK_D_FINAL_ADVISOR_DECISION_CHECKLIST.md) | Tập trả lời ngắn trước, mở nguồn khi cần. Ghi ý kiến thực tế vào E4/E5 của phiếu. |
| Kiểm tra lần bàn giao này | [Nhật ký CP0–CP6 và kiểm định](HANDOFF_PROGRESS.md) | Có kiểm kê lúc tiếp quản, thay đổi của Codex, lỗi đã xử lý, phạm vi test và kết quả cuối. |

Các phép đo và verdict trong hồ sơ có nguồn tại commit `a0916db45563ae90bbe8d4e73ad202b6a2991d3e` cùng các artifact đã niêm phong. Khi sao chép hình/bảng, giữ chú thích, đơn vị và giới hạn cohort. Khi cần tái lập hình, dùng hai lệnh trong chỉ mục hình/bảng, không cần chạy lại ANN. Tài liệu và index riêng của nhóm vẫn cần quyền truy cập trên máy khác; owner duyệt riêng việc phát hành.
