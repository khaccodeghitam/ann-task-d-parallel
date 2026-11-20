# Graph topology và hiệu quả duyệt ANN song song trong một truy vấn

**Bản thảo nghiên cứu thực nghiệm, 20/11/2026.** Phạm vi gồm một họ graph PiPNN trên MS-Turing-1M, một common search engine và một CPU Ryzen 5 PRO 4650U.

**Tóm tắt.** Trên cùng engine, hai worker cho speedup 1,55× trên A0 và 1,43× trên A3 khi dùng flat merge và đồng bộ sau 16 bước, với beam được hiệu chỉnh để Recall@10 trên validation nằm trong khoảng rộng 0,00009. Đổi cấu trúc frontier và cách công bố visited làm thay đổi cả số công việc và latency. Trên hai build A3 dùng để kiểm tra lại, B1+A1 giảm latency lần lượt 12,29% và 10,08% ở cùng kết quả tìm kiếm. Khoảng tin cậy chính qua hai build chứa 0. Seed overlap dự báo được một phần công trùng, nhưng chính sách dùng sketch không vượt cân bằng theo degree trong mô phỏng trên snapshot. Kiểm tra cuối cùng đạt output parity nhưng chưa xác nhận được observer tương đương với baseline OFF về latency. Các kết quả hỗ trợ một nghiên cứu về độ nhạy của scaling với graph và cách triển khai. Chúng chưa xác lập được cơ chế scheduling mới. [Ma trận claim và nguồn số](TASK_D_EVIDENCE_AND_CLAIM_MATRIX.md)

## 1. Introduction và câu hỏi nghiên cứu

Khi chọn một ANN graph, nhóm xây index và nhóm chạy search tối ưu hai chi phí khác nhau. Theo ledger Task A dùng trong đề xuất ngày 15/11, A3 giảm median BUILD từ 41,98 s xuống 28,73 s và peak RSS từ khoảng 3.045 xuống 2.164 MiB so với A0. Cùng ledger ghi nhận search QPS của A3 thấp hơn ở cả hai sàn Recall. Các số này giải thích vì sao chọn cặp A0/A3. Task D dùng các graph đã xây để đo lại **latency hoàn thành một query khi nhiều CPU worker cùng duyệt**. [Đề xuất và bảng nguồn](../../../../source-evidence/proposal_drive_extract.txt) · [Ledger R86](../../../../source-evidence/R86_MST1M_FORMAL_QPS.json)

Ba câu hỏi dẫn tới ba mức kết luận. **H1** hỏi quan hệ giữa lựa chọn graph và strong scaling khi kiểm soát chất lượng. **H2** hỏi phần nào của khác biệt đi cùng work inflation, số round, merge và thời gian chờ. **H3** chỉ đáng đầu tư nếu một tín hiệu quan sát được giúp ra quyết định rẻ hơn phần thời gian nó tiết kiệm. Câu hỏi cuối đòi một phép đối chứng với baseline fixed đã tối ưu. [Preregistration](PRE_REGISTRATION.md)

## 2. Related work

Speed-ANN cho nhiều walker mở rộng những đường đi cục bộ song song, dùng local queues và điều chỉnh việc hợp nhất. iQAN phân tích đánh đổi giữa lượng công thừa và độ sâu duyệt, cho chiều rộng expansion tăng theo giai đoạn và quyết định đồng bộ dựa trên vị trí cập nhật trong queue. Vì vậy, một quan sát rằng S hoặc số worker thích hợp thay đổi theo graph mới chỉ nêu điều kiện thiết kế. Đóng góp scheduling cần chỉ ra khi nào quy tắc quyết định của nó cho kết quả tốt hơn các cơ chế này. [Speed-ANN, §§4.2–4.4](https://johnpzh.github.io/assets/papers/arXiv-2022_Speed-ANN_Zhen.pdf) · [iQAN, §5](https://johnpzh.github.io/assets/papers/PPoPP-2023_iQAN_Zhen.CameraReady.pdf)

AverSearch giảm phụ thuộc giữa các worker bằng ngưỡng top-L lấy từ snapshot bất đồng bộ. Shared buffer phân phối lại công, còn mảng distance có cờ ready cho phép queue maintainer dùng lại kết quả của distance worker. Phân công vai trò động, tránh tính lại distance và cân tải đều đã có đối chứng trực tiếp trong prior art. Các engine của tác giả chưa được tái lập trên panel Task D. [AverSearch, §§4.2–4.4](https://arxiv.org/html/2504.20461v2#S4)

PiPNN xây graph bằng cách tìm cạnh ứng viên trong các partition chồng lặp rồi prune cạnh. PiPNN II tiếp tục tối ưu các bước xây index. Trong thí nghiệm này, topology đầu vào là kết quả của recipe Task A. Worker của Task D chỉ đọc adjacency đã khóa. ParlayANN cung cấp một tham chiếu rộng hơn về cách xây và đánh giá các graph ANN song song, phù hợp khi thiết kế so sánh ngoài common engine. [PiPNN](https://arxiv.org/abs/2602.21247) · [PiPNN II](https://arxiv.org/abs/2611.05690) · [ParlayANN](https://arxiv.org/abs/2305.04359)

## 3. Experimental setup và reproducibility

MS-Turing-1M có một triệu base vectors, 100 chiều, float32. Search dùng squared L2, đỉnh vào 0, top-10. Cả ba arm dùng chung loader và search semantics. A0 là cấu hình stock C160/K1024/N2. A1 bật H17 với C/K/N tương ứng A0. A3 bật H17 với C64/K512/N2. Trong R1, số cạnh có hướng lần lượt là 52.856.043, 52.876.723 và 38.354.907. Bậc trung bình tương ứng 52,86, 52,88 và 38,35. P95 degree lần lượt 64, 64 và 51. A1 là đối chứng cho riêng H17 ở recipe A0. So sánh A1 với A3 đồng thời thay C và K. [Manifest](experiment_manifest_v3_reconciled.json) · [Audit A0](../../../../artifact-evidence/p0-p1-20261117T151056+0700/graph-audit-R86_MST1M_A0_OFF_FORMAL_R1.stdout) · [A1](../../../../artifact-evidence/p0-p1-20261117T151056+0700/graph-audit-R86_MST1M_A1_OFF_FORMAL_R1.stdout) · [A3](../../../../artifact-evidence/p0-p1-20261117T151056+0700/graph-audit-R86_MST1M_A3_OFF_FORMAL_R1.stdout)

Trên Ryzen 4650U, p1 dùng CPU 0, p2 dùng 0/2 cùng miền L3 và p4 dùng 0/2/4/6 trải qua hai miền L3. Mỗi process có jobs=1, 100 validation warmups và đo elapsed time từng query sau khi đã nạp dữ liệu. Worker có local frontier và visited cục bộ trong round. Đến biên đồng bộ, coordinator thu kết quả, cập nhật visited, hợp nhất frontier và phát seed cho round tiếp. S là số expansion tối đa mỗi worker trong một round. OFF đo latency. ON ghi counters trong process riêng. [P2 engine và hợp đồng correctness](P2_MULTIWALKER_IMPLEMENTATION_STATUS.md)

Split định trước gồm 10k validation và 90k test từ 100k public queries. P1 đã quan sát cả pool. H1/Stage D dùng panel 3k trích từ test, B1 replication có panel 3k khác khóa trước. H3 và final audit dùng validation. Stage D có 5 process OFF và 1 ON mỗi ô. Speedup trong bảng dưới được tính từ tỷ số mean latency p1/p trên cùng build, rồi lấy trung bình qua build. CI giữa process trong build và CI giữa build trả lời hai câu hỏi riêng. R1–R3 đều dùng root 555. [Hồ sơ các panel, binary và manifest](TASK_D_FINAL_REPRODUCIBILITY_INDEX.md)

## 4. Graph construction × multi-worker interaction (H1)

Bảng dùng cohort Stage D trước khi đưa B1+A1 vào baseline. Latency là ms/query, timing OFF. Cột p4 dùng S đã chọn riêng cho từng arm trong sweep lịch sử.

| Graph | p1 | p2, S16 flat | Speedup p2 | p4, best-fixed flat | Speedup p4 |
|---|---:|---:|---:|---:|---:|
| A0 | 5,489 | 3,545 | 1,5484× | 2,279 (S8) | 2,4086× |
| A1 | 5,535 | 3,579 | 1,5467× | 2,345 (S8) | 2,3634× |
| A3 | 8,214 | 5,741 | 1,4310× | 3,597 (S16) | 2,2841× |

A3 có ít cạnh hơn nhưng cần beam khoảng 944–990 ở các điểm đã chọn, trong khi A0/A1 cần khoảng 402–426. A3 chậm hơn tuyệt đối ở cả ba mức p. Với p2 flat S16, chênh speedup A0−A3 là 0,1175×, CI95 theo ba build [0,0929, 0,1421]. Giá trị tương ứng ở S8/set là 0,2521×. Lựa chọn merge và S đã thay đổi đáng kể kích thước hiệu ứng. [Stage D/E, bảng 1–2](STAGE_D_E_REPLICATION_AND_H3_DECISION.md)

Có thể tính lại estimand của đề xuất, Δ = log(speedup A0) − log(speedup A3), từ các tỷ số chưa làm tròn trong raw summary. Ở p2 flat S16, Δ lần lượt là 0,0733, 0,0773 và 0,0862, trung bình 0,0789. Ở p4, dùng best-fixed theo arm cho trung bình 0,0531. Nếu giữ S16 cho cả hai arm, trung bình đổi dấu thành −0,0260. Nói cách khác, ở p4/S16 A3 có speedup tương đối cao hơn dù latency tuyệt đối vẫn lớn hơn. Các giá trị tính lại chỉ mô tả ba build cùng root. [Dữ liệu từng build](../../../../artifact-evidence/p2-followup-20261118/stage_d_replication/stage_d_replication_summary.json)

Strict matching đạt trên validation ở cả 45 điểm, với Recall 0,99127–0,99136. Trên 3k test, 63/63 ô timing đạt point floor 0,990. Tuy nhiên A0-R1 và A3-R1 tại p2/S16 chênh 0,00050 trên test, gấp năm lần tolerance 0,0001. Vì vậy H1 hỗ trợ quan hệ giữa arm, cấu hình và scaling sau hiệu chỉnh validation. Bằng chứng về hiệu ứng tại strict test Recall còn thiếu. [Recall và SE theo ô](../../../../artifact-evidence/p2-followup-20261118/stage_d_replication/STAGE_D_REPLICATION_SUMMARY.csv)

## 5. Synchronization, merge và workload diagnostics (H2)

Tại p2/S16 flat của Stage D, A0 thực hiện trung bình 22.102 L2 và 14,20 round/query. A3 thực hiện 31.111 L2 và 31,71 round. Trong đó lần lượt 3.611 và 5.177 L2 trùng. Cửa sổ coordinator của process ON tăng từ khoảng 346 lên 646 µs/query. Quan sát này gắn độ rộng beam, độ dài traversal và tần suất công bố trạng thái với một chi phí hệ thống có thể đo. Việc tách ảnh hưởng riêng của degree, locality và beam còn cần đối chứng. [Tổng hợp ON/OFF](../../../../artifact-evidence/task-d-latency-audit-20261120/observed_budget.csv)

Worker đến sớm có thể chờ trong khi worker còn lại vẫn mở rộng đỉnh. Do đó tổng worker-wait có đơn vị worker-ns và chồng lên công của worker chậm. Cửa sổ gọi là merge còn bao gồm ON accounting, công bố visited, prune và dispatch. Trong mô hình H2 cũ, lấy latency p1 chia số L2 làm đơn giá rồi cộng merge và barrier/p cho residual khoảng −196 µs ở A0 p2/S16. Chính điểm đo này cho thấy các phần gán chi phí chưa tạo thành một phân rã wall-time. [Định nghĩa timer và kiểm toán residual](TASK_D_LATENCY_BUDGET_AND_UPPER_BOUNDS.md)

## 6. Baseline optimizations

Flat merge chuyển việc hợp nhất global candidates sang buffer được sắp thứ tự. Tại A3 p4/S8, mean OFF đổi từ 4,181 ms (set) xuống 3,631 ms (flat). Khi đã dùng flat, tăng S từ 8 lên 16 ở p2 giúp A3 giảm mean từ 6,168 xuống 5,741 ms. Ở p4 A0, cùng thay đổi S làm mean tăng từ 2,279 lên 2,467 ms. Vì vậy đối chứng dùng cho H3 là **flat + S fixed đã chọn theo graph/p + B1+A1** tại những ô có dữ liệu. S này đã được chọn trước B1+A1. [Ablations và lựa chọn fixed S](STAGE_D_E_REPLICATION_AND_H3_DECISION.md)

**B1** công bố tất cả node đã tính L2 tại barrier sẵn có, kể cả node bị loại khỏi frontier. Worker ở round sau có thể bỏ việc tính lại. **A1** duy trì frontier tăng dần cùng trạng thái expanded, giới hạn seed dispatch ở p×S và tránh nạp lại đuôi frontier vào local queue. Top-10, thứ tự và squared L2 của bốn arm khớp theo query trên các panel so sánh. Ở A3 p2/S16, số duplicate L2 trên R2 giảm từ 5.234 xuống 665/query và trên R3 từ 5.122 xuống 666/query. Gain OFF của B1 riêng khác nhau, 6,96% và 3,78%, dù mức giảm count đều khoảng 87%. [Bốn ablation](B1_A1_NARROW_REPLICATION_REPORT_20261119.md)

| A3 p2/S16 | OFF base → combo (ms) | Giảm latency ghép cặp [CI95 trong build] | Test Recall / LCB95 |
|---|---:|---:|---:|
| R1, pilot khám phá | 5,807 → 5,134 | 11,58% [10,47%, 12,69%] | 0,99037 / 0,98884 |
| R2, replication | 6,040 → 5,296 | 12,29% [9,64%, 14,94%] | 0,99103 / 0,98964 |
| R3, replication | 5,838 → 5,249 | 10,08% [8,03%, 12,13%] | 0,99050 / 0,98902 |

R2/R3 dùng cùng panel 3k mới. Ước lượng chính là trung bình hai gain, 11,19%, CI95 t với một bậc tự do [−2,84%, 25,21%]. Kết quả đạt điều kiện trong từng build và trượt điều kiện outer, nên **HOLD**. R1 đã được dùng chọn giả thuyết. Việc đưa R1 vào CI bổ sung không đổi quyết định đăng ký trước. Ở pilot p4 các CI best-fixed chứa 0 và A0-R1 trên panel disjoint chỉ đạt Recall 0,98940. [Bảng process và diễn giải](B1_A1_POST_REPLICATION_REVIEW_20261119.md)

## 7. Kết quả âm của H3

Đề xuất TP-CG dự tính điều chỉnh số walker hoặc thời điểm sync khi lợi ích kỳ vọng vượt chi phí đổi chế độ. Sweep fixed cho thấy việc chọn baseline ảnh hưởng đến dư địa biểu kiến của scheduler. Stage E chọn PIVOT. **TP-CG online chưa mở**, do đó chưa có số đo thắng hoặc thua của controller so với fixed/staged. [Quyết định Stage E](STAGE_D_E_REPLICATION_AND_H3_DECISION.md)

Nhánh overlap kiểm tra một điều kiện cụ thể hơn. Với A3 p2/S16 trên ba build, RR cung cấp 6.095 snapshot từ cùng 64 validation IDs mỗi graph. Với mỗi snapshot, nhóm giữ nguyên seed và ước lượng công bằng số neighbor đủ điều kiện phân biệt trong hợp của từng worker. So sánh trên 32 query held cho thấy exact greedy chỉ cải thiện max-worker proxy thêm 0,106–0,120% so với cân bằng theo số neighbor đủ điều kiện. Sketch 128 bit kém degree 0,97–1,12% và không cho lợi thế ổn định so với hoán đổi sketch trong nhóm cùng degree. Greedy dùng giao nhau chính xác nhưng không bảo đảm nghiệm tối ưu toàn cục. [Thiết kế offline và placebo](H3_OVERLAP_SIGNAL_SCREENING_RESULTS.md)

Chỉ khoảng 0,33% tổng số L2 là lần tính trùng giữa hai seed. Khoảng 79–80% số trùng đến từ hai đỉnh xuất hiện trong lúc worker đã bắt đầu duyệt. Vì vậy, đo overlap ở đầu round thấy được tín hiệu nhưng chỉ nhìn được một phần đường đi. Kernel sketch offline tốn khoảng 29–30 µs/query held. Sau khi trừ kernel trong mô hình chuyển đổi proxy thành thời gian, ước lượng net theo R1/R2/R3 là +0,100%, −0,025%, −0,041% của frozen OFF, với cả ba CI chứa 0. Ngưỡng đăng ký là 5%. Quyết định **NO-GO cho prototype overlap đã sàng lọc** dựa trên đối chứng và cost. Latency và Recall của một policy online thay đường duyệt vẫn chưa đo. [Cost/quality và uncertainty](../../../../artifact-evidence/h3-overlap-screening-20261120/offline_analysis/cost_quality.json)

## 8. Final measurement-validity gate

Trên A3-R1, beam 970, p2/S16 flat+B1+A1 và đúng 64 validation IDs, ba cặp OFF/observer cho mean frozen OFF 5,1165 ms/query (SD process 0,0676 ms). Observer chỉ đọc clock ở biên worker và biên pha. Cả 384 kết quả khớp. Tỷ lệ thay đổi ghép cặp là −1,717%, CI95 [−2,851%, −0,570%]. Giao thức yêu cầu toàn bộ CI nằm trong [−2%, +2%]. Kết quả **NOT_VALIDATED** vì cận dưới vượt biên, kể cả khi cả ba lượt observer đều nhanh hơn. [Ba cặp và validity gate](MEASUREMENT_VALIDITY_AND_PHASE_AUDIT.md)

Trong execution có observer, mean 5,029 ms phân thành 4,483 ms worker/arrival, 0,049 ms thu kết quả và publish, 0,475 ms global frontier/dispatch, 0,022 ms còn lại. Arrival tail sau worker cuối chỉ 3,2 µs, trong khi tổng worker-wait là 457 µs. Với giả định chia tùy ý toàn bộ công cố định và triệt tiêu thời gian bắt đầu/đến, cận tiết kiệm là 232,5 µs/query trên execution đó. Cơ chế đổi cả đường đi có thể làm thay đổi tổng công. Việc chuyển các tỷ lệ pha này sang OFF chưa được xác nhận. Linux từ chối permission probe ở perf_event_paranoid=4. Exclusive L2, local frontier time và cache stalls vẫn **NOT_MEASURED**. [Phân tích từ raw](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/analysis.json)

## 9. Threats to validity và phạm vi suy rộng

- **Chất lượng và selection.** Beam được chọn trên validation. Public test pool đã từng được quan sát, và pilot R1 đã định hướng chọn A3 p2. Panel disjoint giảm trùng ID với pilot nhưng LCB test R2/R3 dưới 0,990. Bằng chứng mạnh nhất cho phép so B1/A1 trong cùng build là output parity.
- **Đơn vị lặp.** Ba invocation cùng root có thể khác nhau do xây song song. Các CI theo build mô tả cohort đó. Lặp process đo biến thiên trên một binary/graph/panel. Số query và số round lớn không bổ sung một RNG root độc lập.
- **Host và baseline.** P4 trải qua hai miền L3 trên laptop. Lượt chậm ở A1-R2 p4/S8 vẫn nằm trong bảng. A1 graph thiếu ma trận B1+A1 đầy đủ, p4 clean thiếu R2/R3. Cùng tên timer qua các phiên bản có thể bao phủ lượng công khác nhau.
- **Khả năng áp dụng.** Hiện có một dataset và một họ graph. Jobs=1 đo latency một query. Dữ liệu chưa xác lập loaded throughput, tail dưới tải, năng lượng, hành vi trên i5 hoặc lợi thế trước các engine ngoài. [Phạm vi, gates và bằng chứng thiếu](ORIGINAL_PROPOSAL_FINAL_REASSESSMENT.md)

## 10. Conclusion và future work

Trên các graph đã thử, lựa chọn recipe thay đổi beam cần thiết và scaling quan sát được. Sửa merge, visited và frontier làm thay đổi cả latency lẫn kích thước của chênh lệch giữa graph. Hai kết quả âm xác định rõ nơi nên dừng: sketch overlap chưa vượt các đối chứng đơn giản, và observer chưa đạt điều kiện để quy chi phí pha cho OFF. Bottleneck nhân quả lớn nhất của frozen OFF còn **UNKNOWN**.

Đề nghị chốt case study với các giới hạn này. Một claim rộng hơn cần đối chứng native với engine CPU mạnh ở matched Recall, dataset và họ graph bổ sung, cùng cohort có policy RNG độc lập được Task A xác nhận. Đề tài thuật toán mới cần giả thuyết và scope riêng nếu giảng viên yêu cầu. Historical P0, Full P1 và t0998 **HOLD**, P3 official **CLOSED**, H3/TP-CG **NOT_OPENED**, i5 **NOT_RUN**. [Quyết định cần giảng viên và owner](TASK_D_SUPERVISOR_DECISION_BRIEF_VI.md)
