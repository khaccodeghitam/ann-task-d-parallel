# Chỉ mục bằng chứng và cách truy xuất

Tìm theo câu hỏi. Nếu cần trích một con số G2, bắt đầu ở E01–E04. Nếu cần biết một mục tiêu đến từ đâu, xem S01–S06. Bằng chứng ngoài Git được liên kết tương đối theo bố cục workspace của owner. Một checkout riêng vẫn có thể đọc báo cáo và các bảng tóm tắt trong Git sau khi bộ bàn giao được duyệt.

## Từ kết luận tới artifact

| ID và câu hỏi | Nguồn định danh | Phần cần đọc |
|---|---|---|
| E01 · SEARCH, CI, interaction, mô hình | [axd-g2-v2-off-design3_1_run2-analysis.json](../../../../../artifact-evidence/axd-g2-v2-off-design3_1_run2-analysis.json) · `f0a35394f028550a…` | primary_reduction, primary_reduction_ci95, query_bootstrap, joint_bootstrap, build_search. Các trường reduction gốc là phân số, nhân 100 để ra %. |
| E02 · Kiểm toán độc lập | [audit_results.json](../../../../../artifact-evidence/axd-g2-v2-final-audit-design3_1/audit_results.json) · `c79e45a3482a702b…` | checks, discrepancies, summary_stats và quality_mechanism.test. Dùng values từ JSON khi prose lịch sử có sai số ghi tay. |
| E03 · Chất lượng | [quality.json](../../../../../artifact-evidence/axd-g2-v2-quality-design3/quality.json) · `360e1d29fc3c8f3c…` | A_pass, B_pass, lcb95, arm_ci95, parity. Giữ riêng kết quả test và đối chiếu validation với Stage 5. |
| E04 · Biên nhận thực thi | [BUNDLE.sha256](../../../../../artifact-evidence/axd-g2-v2-off-design3_1_run2/BUNDLE.sha256) · `c2b4d8f1c6e0cc00…` | 1299 mục niêm phong của run2. Lịch 72 cặp và 144 process, inputs/graph/process digests. |
| E05 · Biên nhận ON | [BUNDLE.sha256](../../../../../artifact-evidence/axd-g2-v2-quality-design3/BUNDLE.sha256) · `5e3a41d07b274b29…` | 166 mục, 18 process ON mới. Kiểm lại quỹ đạo, Recall, đếm công việc. |
| E06 · HOLD đầu và HOLD thứ hai | [HOLD.json](../../../../../artifact-evidence/axd-g2-v2-off-design3/HOLD.json) · `8187bb38b1316099…` | Lỗi parser counters ở design-3. Giữ nguyên receipt đầu tiên và lý do HOLD. |
| E07 · HOLD run1 | [HOLD.json](../../../../../artifact-evidence/axd-g2-v2-off-design3_1/HOLD.json) · `4e078fc11b518fad…` | Guard vượt ngưỡng ở #120; lần hoàn chỉnh là run2, không tái dùng kết quả run1. |
| E08 · Danh tính BUILD | [Sáu receipt đóng băng](../../../../configs/axd_g2_v2_build_reference.json) · [Kiểm tra graph/loader](../../task-da/AXD_G1_RUNTIME_PARITY_REPORT.md) | Tra từng graph theo build arm và r1–r3, SHA, source, compiler/builder và wall_s. |
| E09 · Đồ thị, ELF, package và protocol | [Manifest danh tính](../../task-da/AXD_G2_V2_DESIGN3_1_EVIDENCE_MANIFEST.md) · [Freeze JSON](../../task-da/AXD_G2_V2_DESIGN3_1_FREEZE_MANIFEST.json) · [Danh sách 29 SHA](../../task-da/AXD_G2_V2_DESIGN3_1_FREEZE.sha256) | SEARCH source f2cd634b837a70735c3e31e5956f0524bfc26675, ELF 7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1, AXD-G2-V2-3A-20261123 design-3.1. Gồm SHA dữ liệu, GT, panel và đồ thị. |
| E10 · Archive cuối | [Biên bản release PRIVATE](../../task-da/AXD_G2_FINAL_CLOSEOUT_STATUS.md) · [Mục lục asset cục bộ](../../../../../archives/RELEASE_ASSETS.sha256) | Tier 1 số liệu chính, Tier 2 lịch sử HOLD và chẩn đoán, dependencies sáu graph và ELF. Biên bản sau cùng d0f4816 xác minh 9/9 asset bằng tải ngược; văn bản archival trước đó mô tả trạng thái cũ. Vector/GT là dependency ngoài release. |
| E11 · Nguồn gốc B1+A1 | [Header engine](../../../../research/task_da/search_common/p2_engine.hpp) · [Kiểm định hẹp R86](../../task-da/B1_A1_NARROW_REPLICATION_REPORT_20261119.md) | Lấy bản mã ở f2cd634. R86 có kết quả theo build và outer HOLD, R90 kiểm bundle chính sách. |
| E12 · Giả thuyết, E0–E3 và P0–P6 | [E0](../../AVERSEARCH_QUEUE_ROLE_E0.md) · [E1](../../AVERSEARCH_QUEUE_ROLE_E1.md) · [Lịch sử E2/E3](../../task-da/TASK_D_RESEARCH_TIMELINE.md) · [Đối chiếu proposal](../../task-da/ORIGINAL_PROPOSAL_FINAL_REASSESSMENT.md) | E2 native thiết kế một mutex, E3 mức fixture. H1 có điều kiện, H2 hỗ trợ một phần; H3/TP-CG dừng. |
| E13 · H3 và độ tin cậy phép đo | [Prior-art audit](../../task-da/H3_NOVELTY_AND_PRIOR_ART_AUDIT.md) · [Screening](../../task-da/H3_OVERLAP_SIGNAL_SCREENING_RESULTS.md) · [Phase observer](../../task-da/MEASUREMENT_VALIDITY_AND_PHASE_AUDIT.md) | Trace và cost model sàng lọc. CI observer vượt biên tương đương ở một phía. Chi phí pha riêng trong OFF còn chưa xác định. |
| E14 · PipeANN và các lane | [Hiến chương](../../../../RESEARCH_PHILOSOPHY.md) · [Issue 29](../../ISSUE29_DECISION_MEMO.md) · [SIFT10M Issue 32](../../CUSTOM_FULLFAN_SIFT10M_20261013.md) · [D6](../../G0C2_SIFT10M_D6_CAUSAL_DIAGNOSTICS.md) | Kiểm đúng binary, index, host và workload khi trích số. Các lane H-V/H-G/H-C/H-F/H-QV có kết luận riêng. |

## Tám tài liệu tổng hợp ở a0916db

| Tài liệu | Dùng để |
|---|---|
| [TASK_D_ADVISOR_REVIEW_BRIEF](../../task-da/TASK_D_ADVISOR_REVIEW_BRIEF.md) | Hướng dẫn thảo luận và yêu cầu quyết định. Dùng CI tương tác khi viết lại lời trình bày. |
| [TASK_D_B1_A1_TECHNICAL_EXPLANATION](../../task-da/TASK_D_B1_A1_TECHNICAL_EXPLANATION.md) | B1/A1, invariant, pseudocode và giới hạn. |
| [TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX](../../task-da/TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md) | Nhãn và phạm vi từng claim dương, âm, mô hình, giả thuyết. |
| [TASK_D_FINAL_EXPERIMENT_RESULTS](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md) | Số liệu chính, hai HOLD, bốn arm, đuôi và CI. |
| [TASK_D_FINAL_REPORT_OUTLINE](../../task-da/TASK_D_FINAL_REPORT_OUTLINE.md) | Cấu trúc luận giải bảy chương. |
| [TASK_D_FINAL_RESEARCH_SYNTHESIS](../../task-da/TASK_D_FINAL_RESEARCH_SYNTHESIS.md) | Kết luận và hai nhóm đính chính ở §3. |
| [TASK_D_RESEARCH_TIMELINE](../../task-da/TASK_D_RESEARCH_TIMELINE.md) | Diễn biến theo chủ thể và mốc thời gian. |
| [TASK_D_SCIENTIFIC_CONTRIBUTIONS_AND_LIMITATIONS](../../task-da/TASK_D_SCIENTIFIC_CONTRIBUTIONS_AND_LIMITATIONS.md) | Đóng góp, giới hạn và điều kiện mở rộng. |

## Tài liệu nguyên bản của nhóm và hồ sơ khảo sát

S01 là kế hoạch mốc đầu, S02–S04 là các tài liệu giao việc, S05 là hồ sơ khảo sát và S06 là đề xuất/hướng kết nối. Trích đoạn trong ma trận có chỉ số mục/tiêu đề để tìm trong PDF hoặc DOCX. Góp ý 16/10 do trưởng nhóm ghi lại sau họp 15/10.

| Mã | Tài liệu thực tế | SHA-256 (16 ký tự đầu) |
|---|---|---|
| S01 | [KE_HOACH_PHAN_CONG_TUAN_1_GATE_0_ANN.pdf](../../../../../../seminar%20chuyen%20de/KE_HOACH_PHAN_CONG_TUAN_1_GATE_0_ANN.pdf) | `40fd23407b47a73e` |
| S02 | [Phan_cong_4_task_Research_Parallel_ANN.pdf](../../../../../../seminar%20chuyen%20de/group-report/Phan_cong_4_task_Research_Parallel_ANN.pdf) | `32bb62337e3cd0ce` |
| S03 | [01_Gop_y_thay_va_huong_dieu_chinh_16_10_2026.pdf](../../../../../../seminar%20chuyen%20de/group-report/01_Gop_y_thay_va_huong_dieu_chinh_16_10_2026.pdf) | `f21106792fa5945b` |
| S04 | [02_Phan_cong_Parallel_ANN_v2_16_10_2026.pdf](../../../../../../seminar%20chuyen%20de/group-report/02_Phan_cong_Parallel_ANN_v2_16_10_2026.pdf) | `bf3a4b3bf1446b2c` |
| S05 | [research.docx](../../../../../../seminar%20chuyen%20de/group-report/research.docx) | `b97ff1ea6ae0fe61` |
| S05 | [Bước 5(1).pdf](../../../../../../seminar%20chuyen%20de/my%20research/task%20D/B%C6%B0%E1%BB%9Bc%205%281%29.pdf) | `f91206f151ac8fa4` |
| S05 | [CUM2_CPU_SSD_PIPELINE_SCHEDULING_FINAL.pdf](../../../../../../seminar%20chuyen%20de/my%20research/task%20D/CUM2_CPU_SSD_PIPELINE_SCHEDULING_FINAL.pdf) | `ff225e4a21d2f6e0` |
| S05 | [CUM2_CPU_SSD_PIPELINE_SCHEDULING_UPDATED_Q1_Q8.pdf](../../../../../../seminar%20chuyen%20de/my%20research/task%20D/CUM2_CPU_SSD_PIPELINE_SCHEDULING_UPDATED_Q1_Q8.pdf) | `8633eb68f989370d` |
| S05 | [CUM3_GPU_DATA_PARALLELISM_FINAL.pdf](../../../../../../seminar%20chuyen%20de/my%20research/task%20D/CUM3_GPU_DATA_PARALLELISM_FINAL.pdf) | `b7d3621658bf1024` |
| S05 | [Cum1_Multi_Core_Graph_Traversal_Final.docx](../../../../../../seminar%20chuyen%20de/my%20research/task%20D/Cum1_Multi_Core_Graph_Traversal_Final.docx) | `5738240e262711bf` |
| S05 | [HỆ THỐNG TASK D.pdf](../../../../../../seminar%20chuyen%20de/my%20research/task%20D/H%E1%BB%86%20TH%E1%BB%90NG%20TASK%20D.pdf) | `3798f8b032deb526` |
| S05 | [Tổng hợp ngắn — Speed-ANN, iQAN và AverSearch (Cụm 1) (1).docx](../../../../../../seminar%20chuyen%20de/my%20research/task%20D/T%E1%BB%95ng%20h%E1%BB%A3p%20ng%E1%BA%AFn%20%E2%80%94%20Speed-ANN%2C%20iQAN%20v%C3%A0%20AverSearch%20%28C%E1%BB%A5m%201%29%20%281%29.docx) | `09b83e98db989a92` |
| S05 | [cụm 2 tổng hợp.pdf](../../../../../../seminar%20chuyen%20de/my%20research/task%20D/c%E1%BB%A5m%202%20t%E1%BB%95ng%20h%E1%BB%A3p.pdf) | `4d6b518da78e9290` |
| S05 | [cụm 3.pdf](../../../../../../seminar%20chuyen%20de/my%20research/task%20D/c%E1%BB%A5m%203.pdf) | `ecb9a41edbe82f3d` |
| S05 | [osdi25-guo.pdf](../../../../../../seminar%20chuyen%20de/paper/osdi25-guo.pdf) | `d25187ae7e826ae2` |
| S06 | [TASK_D_A_GRAPH_TOPOLOGY_PARALLEL_TRAVERSAL_PROPOSAL_20261115.docx](../../../../../source-evidence/TASK_D_A_GRAPH_TOPOLOGY_PARALLEL_TRAVERSAL_PROPOSAL_20261115.docx) | `a7aef4ba2ed867ed` |
| S06 | [kết nối ý tưởng task D và task A.pdf](../../../../../../seminar%20chuyen%20de/my%20research/connect%20task%20D%20to%20A/k%E1%BA%BFt%20n%E1%BB%91i%20%C3%BD%20t%C6%B0%E1%BB%9Fng%20task%20D%20v%C3%A0%20task%20A.pdf) | `e58a8d99d304fb1f` |
| S06 | [Lo_trinh_ANN_danh_cho_Thinh.pdf](../../../../../../seminar%20chuyen%20de/Lo_trinh_ANN_danh_cho_Thinh.pdf) | `60050843b5307598` |
| S06 | [SOLUTION_PipeANN_Load_Adaptive_v2.pdf](../../../../../../seminar%20chuyen%20de/SOLUTION_PipeANN_Load_Adaptive_v2.pdf) | `d7a8344c9965eba5` |
| S06 | [De_xuat_Task_D_x_Task_A_BUILD_SEARCH_v2_20261120.docx](../../../../../../../../Downloads/De_xuat_Task_D_x_Task_A_BUILD_SEARCH_v2_20261120.docx) | `9641dae30d1fb1c5` |

Bản kết nối A×D dạng PDF lưu các trang dưới dạng ảnh, bản trích văn bản của Antigravity gần như rỗng. Để kiểm yêu cầu H1–H3/P0–P6, dùng DOCX gốc 15/11 có SHA đầy đủ a7aef4ba2ed867ed8799f72baec463ab5bd59c6fbdd190327d38b6953b260b45 và [bản trích có thể tìm kiếm](../../../../../source-evidence/proposal_drive_extract.txt). Các báo cáo cụm và danh mục 01_PAPERS cung cấp nguồn, section, giới hạn và URL công trình. Xem thư mục tài liệu tham khảo ở cuối [báo cáo chính](TASK_D_MASTER_RESEARCH_REPORT.md). Bộ bàn giao chỉ đóng gói số liệu tổng hợp; bản PDF riêng của mọi paper khảo sát chưa có đầy đủ trong workspace.

## Nguồn Google Sheets và mốc thời gian

- **Task D.** Đọc trực tiếp tab 18_TASK_OWNERSHIP, gid 227080822, A1:G9. Đây là phân công ở thời điểm R86. Các chữ HOLD/NOT_STARTED trong sheet phải được đối chiếu với biên nhận sau này. Antigravity cũng có các snapshot 01_PAPERS, 02_TAXONOMY và 15_EVIDENCE_MATRIX. [Workbook Task D](https://docs.google.com/spreadsheets/d/1Fk4HsVFz6xlNz31QjJwrVuC8E2q4BGTfjJB0oinUvwE/edit#gid=227080822)
- **Task A.** Đọc trực tiếp tab R90_P0A_V13_FINAL_SUMMARY, gid 1711192621, A1:H19. Dòng 9 cho MS-Turing1M, Stock 42.2567 s so với Fast v2 33.7933 s. Các tab R91 thuộc nhánh riêng. Số liệu G2 lấy từ receipt R90 đã đóng băng. [Workbook Task A](https://docs.google.com/spreadsheets/d/12ApqgMV8YykflyFXUT2VMbUhgyiGirtoOmRWCXCz3Ek/edit#gid=1711192621)

## Nguồn còn thiếu và phạm vi sử dụng

- **SOURCE_MISSING** đối với bản nộp lịch sử đúng tên TASK_D_PARALLEL_RESEARCH.md theo §D6 ngày 14/10. Các đầu ra tương ứng được truy vết tại cuối [ma trận](TASK_D_OBJECTIVE_CLOSURE_MATRIX.md).
- **SOURCE_MISSING** đối với template báo cáo nhóm cuối và biên bản giảng viên nghiệm thu Task D trong nguồn đã giao. Vì thế bản ghép là một mô-đun có thể sửa, hai mục E4/E5 để mở cho giảng viên. Mục tiêu 1–3 dùng câu chữ trong Master Prompt.
- Các điều kiện ngoài cohort như host thứ hai đo SEARCH, dataset thứ hai, independent RNG và phục vụ concurrent là NOT_RUN. Đây là giới hạn thiết kế, không phải thiếu một receipt đã phải tồn tại.
- Khi chuyển máy, các liên kết tới seminar, archives và artifact-evidence cần quyền truy cập thư mục riêng của nhóm. Các tài liệu trong Git, danh tính theo SHA và bảng thu gọn đủ để đọc kết quả. Không cần mở lại chiến dịch.

Trong thư mục paper tại chỗ có PDF PipeANN. Đối với các bài khác, có thể dùng liên kết của tác giả/nhà xuất bản trong mục tài liệu tham khảo. DOI của ParlayANN xác định bài PPoPP 2024, nhưng trang đích trả HTTP 403 cho công cụ kiểm tra liên kết. Có thể đọc bản công khai của tác giả tại [arXiv](https://arxiv.org/abs/2305.04359).
