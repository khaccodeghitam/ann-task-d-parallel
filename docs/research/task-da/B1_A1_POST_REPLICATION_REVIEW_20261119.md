# Task D · Kiểm toán B1+A1 và quyết định nghiên cứu H3

**B1+A1 giữ HOLD. Hướng H3 chuyển sang PIVOT, triển khai giữ HOLD.** B1+A1 giảm mean latency khoảng 10–12% trên ba graph A3 đã quan sát ở Ryzen 5 PRO 4650U. Thiết kế R4/R5 ở trạng thái chờ Task A xác nhận khả năng dựng graph cùng phương pháp trên Ryzen và chờ owner duyệt phạm vi mới. H3/TP-CG vẫn `NOT_OPENED`. [Báo cáo gốc tại commit 40bb7c5](B1_A1_NARROW_REPLICATION_REPORT_20261119.md), [thiết kế R4/R5](B1_A1_R4_R5_CONFIRMATION_PREREG_20261119.md).

## 1. Provenance và raw evidence

- HEAD lúc bắt đầu audit là `40bb7c54017f3ea21d6f1a5fd2fbbe920b3d2e1e`, working tree sạch. Commit đăng ký trước `574420778c6e239d58bbce3df9d86136a47f90c9` có timestamp 11:42:49 UTC, trước process đầu tiên lúc 11:43:05 UTC ngày 19/11. Tag pilot trỏ đến `f2cd634b837a70735c3e31e5956f0524bfc26675`, tag Stage D/E trỏ đến `87d4a8149416b22ccf8854f72c7c72f09197cfa3`. Diff từ freeze pilot đến HEAD chỉ thêm hai tài liệu và hai script runner/phân tích của nghiên cứu hẹp.
- Tái băm đủ **713/713** tệp raw, **4/4** tệp export, **896/896** tệp pilot resume và **232/232** tệp pilot ban đầu. Các manifest khớp và không có tệp dư ngoài manifest. **23/23** đường dẫn khóa trong `frozen.json` khớp nội dung hiện diện, gồm hai evaluator, hai graph, dataset/ground truth, split, source runner, guard và protocol. SHA-256 của manifest raw là `2b6677895dce4a274fd288f71e31e57b3051313e19b05f8cd12ce7022fae4ffe`, của manifest export là `483804c96aefbe954693f615537aaebe8d059d59f4790ff8ae5f808331e52fb8`. [Manifest raw](../../../../artifact-evidence/p2-b1-a1-narrow-20261119/BUNDLE.sha256), [manifest export](../../../../artifact-evidence/p2-b1-a1-narrow-analysis-20261119/CHECKSUMS.sha256), [danh tính đã khóa](../../../../artifact-evidence/p2-b1-a1-narrow-20261119/frozen.json).
- Đọc độc lập JSONL của 40 process OFF R2/R3 và 25 process OFF R1, cộng latency theo query, tái tính mean/p50/p95 và ghép cặp bằng block. Chạy lại analyzer tại commit báo cáo với output trong `/tmp` cho `analysis.json`, `raw_query_latency.csv` và `quality.csv` giống export từng byte. Đường dẫn nguồn trong process CSV phụ thuộc vị trí export. [Analyzer đã niêm phong](../../../research/task_da/analyze_b1_a1_narrow.py), [analysis.json](../../../../artifact-evidence/p2-b1-a1-narrow-analysis-20261119/analysis.json).
- 88/88 manifest evaluator ghi exit 0, guard không trip và 1.873 mẫu watchdog. Receipt xác nhận thứ tự tuần tự, đúng lịch OFF và đúng cấu hình `p=2, S=16, K=10, jobs=1, flat`, CPU quan sát `[0,2]` trong các lượt validation/test/timing đã phân tích. Giữ đủ 40 lượt OFF. Telemetry ghi Tctl 74,0–88,6 °C trong OFF và có burst CPU từ ứng dụng desktop. Khoảng tin cậy có điều kiện trên môi trường Ryzen quan sát được.
- Lượt audit chạy kiểm thử dataset-free, **516 ca, 505 pass, 11 skip**. Chỉ thêm hai tài liệu bàn giao, giữ nguyên các commit, raw, code và binary đã khóa. Không dựng graph, đo benchmark hay chạy i5-14600KF.

## 2. Tái tính latency và đơn vị suy luận

Trong mỗi block, lấy mean latency từ toàn bộ query của từng process OFF. Với `B_i` là mean của flat+S và `C_i` là mean của combo, mức giảm ghép cặp là `d_i = 100 × (1 − C_i/B_i)`. CI95 hai phía là `mean(d) ± t(0.975, n−1) × SD(d)/√n`. Mỗi graph có năm block. Ở tầng outer, mỗi graph đóng góp một mean của năm block, với trọng số bằng nhau. Tỷ số riêng `100 × (1 − mean(C)/mean(B))` cho 11,59% ở R1, 12,32% ở R2 và 10,09% ở R3.

| Graph | Mean base → combo, µs/query | Tiết kiệm ghép cặp, µs [CI95] | Giảm ghép cặp, % [CI95] |
| --- | ---: | ---: | ---: |
| R1 pilot | 5.806,62 → 5.133,61 | 673,02 [594,24, 751,80] | 11,58 [10,47, 12,69] |
| R2 | 6.040,37 → 5.296,16 | 744,22 [568,52, 919,91] | 12,29 [9,64, 14,94] |
| R3 | 5.838,12 → 5.249,34 | 588,78 [466,99, 710,57] | 10,08 [8,03, 12,13] |
| **R2/R3, outer chính** | — | — | **11,19 [−2,84, 25,21]** |
| R1/R2/R3, mô tả bổ sung | — | — | 11,32 [8,52, 14,12] |

| Arm so với base | R2, % [CI95] | R3, % [CI95] | Outer R2/R3, % [CI95] |
| --- | ---: | ---: | ---: |
| B1 | 6,96 [4,95, 8,97] | 3,78 [0,61, 6,94] | 5,37 [−14,82, 25,55] |
| A1 | 6,50 [3,15, 9,86] | 5,93 [4,72, 7,14] | 6,22 [2,60, 9,83] |

CI trong từng graph mô tả nhiễu của năm block ghép cặp trên graph đó, với hệ số t bằng 2,776 tại df=4. Qua hai graph, chênh lệch ước lượng là 2,208 điểm phần trăm, SE của mean outer là 1,104 điểm phần trăm, và hệ số t tại df=1 là 12,706. Bán kính outer vì thế là **14,029 điểm phần trăm**, lớn hơn mean 11,186%. Tiêu chí theo từng graph đã đạt, còn tiêu chí cận dưới outer dương chưa đạt. Thêm process trên cùng graph có thể làm điểm ước lượng của graph chính xác hơn. Việc đó giữ nguyên số graph và bậc tự do outer. R1 đã góp phần chọn giả thuyết, dùng tập query cũ và có block baseline riêng cho B1. Khoảng ba graph mang tính mô tả. Hai CI của tương tác B1×A1 tính bằng µs đều chứa 0.

Đơn vị outer được ký hiệu R1/R2/R3. Receipt Task A cho thấy chúng là **ba invocations dựng graph riêng với cùng cấu hình H17 OFF và seed nội bộ `555`**, với biến thiên gắn với build song song bốn luồng. SHA khác nhau và số cạnh lần lượt là 38.354.907, 38.354.443, 38.354.592, nên các file khác cả số cạnh. Chưa có chứng cứ về ba RNG seed độc lập hoặc về mức độc lập thống kê của các draw khi cùng builder và input. CI outer đã đăng ký được đọc như khoảng có điều kiện, dựa trên giả định các lần dựng riêng có thể dùng làm replicate trao đổi được. Các lần lặp process và hàng query đều nằm bên trong graph. R2/R3 chia sẻ cùng workload, cùng máy và epoch đo. [Provenance Task A, mục 4.3](../../../../artifact-evidence/TaskA_R86_Artifact_Recovery_20261117/TASK_A_R86_ARTIFACT_RECOVERY_REPORT.md), [manifest V3](experiment_manifest_v3_reconciled.json).

## 3. Chất lượng và lựa chọn beam

Tái tính Recall@10 bằng số ID trùng với top-10 ground truth của từng query chia 10, rồi lấy mean trên query. Theo quy ước lịch sử của giao thức, `LCB95 = mean − 1.96 × SE` là đầu dưới của CI chuẩn xấp xỉ hai phía 95%, với SE tính từ độ lệch chuẩn mẫu của Recall theo query.

| Graph và beam | Validation point (10.000) | Validation LCB95 | Test point (3.000) | Test LCB95 |
| --- | ---: | ---: | ---: | ---: |
| R1 · 970, test pilot cũ | 0,991310 | 0,990546 | 0,990367 | 0,988835 |
| R2 · 986 | 0,991320 | 0,990563 | 0,991033 | 0,989643 |
| R3 · 966 | 0,991340 | 0,990563 | 0,990500 | 0,989024 |

Validation LCB95 đo điều kiện để chốt beam, và cả hai graph mới vượt 0,990. Test point Recall đo chất lượng quan sát trên tập 3.000 query, và cả hai graph mới vượt point floor exploratory 0,990. Test LCB95 biểu thị độ bất định của ước lượng test, và cả hai cận đều dưới 0,990. Mọi arm R2/R3 có cùng thứ tự query, top-10 ID và squared L2 trên validation, test ON và 40 lượt timing OFF. A0-R1 disjoint lịch sử vẫn `FAIL` tại 0,98940.

Hồ sơ thực thi xác nhận beam **986/966** được lấy từ đúng cell Stage D `selected_45_cells.<graph>.S16.2`, khóa trong preregistration trước lượt test mới. Baseline validation của từng graph khớp top-10 ID và squared L2 với JSONL Stage D đã kiểm hash. Cả tám lượt validation, tám lượt test ON và 40 lượt OFF dùng đúng beam khóa. Tập test là đúng 3.000 ID đầu của `test_90k.ids` sau khi loại hai tập pilot, rời `val_10k` và cả hai pilot. **Không phát hiện tuning beam dựa trên test trong lượt replication này.** P2 pilot trước đó đã góp phần chọn cấu hình và giả thuyết, và `test_90k` từng được dùng tại P1. Phạm vi suy luận vẫn là `EXPLORATORY_HOST_SPECIFIC`. [Preregistration R2/R3](B1_A1_NARROW_REPLICATION_PLAN_20261119.md), [beam Stage D đã khóa](../../../../artifact-evidence/p2-followup-20261118/stage_d_val10k_r2_r3/stage_d_val10k_45cells_manifest.json).

## 4. Cơ chế đã biết và prior art

- **B1** công bố ở barrier mọi đỉnh đã tính L2, kể cả ứng viên bị loại. R2 giảm 5.234,46 → 664,65 duplicate L2/query, R3 giảm 5.122,23 → 666,19, tương ứng 87,3% và 87,0% duplicate. Phần giảm tương ứng **14,45% và 14,35% tổng L2**. Các lượt ON cho thấy số unique L2, expansions, frontier insertions và rounds giữ nguyên trong cặp toggle B1 theo từng query. Mỗi lần L2 trùng biến mất đi kèm một `already_seen_attempt` tăng thêm. Gain B1 về mean latency OFF là 6,96% và 3,78%. Counters này chưa tách chi phí theo critical path khỏi chi phí lookup, ghi visited và đồng bộ.
- **A1** dùng cờ expanded trong flat frontier và chặn dispatch ở tối đa `p × S = 32` seed/round. Bỏ phần đuôi đã biết không thể được pop trong round giúp tránh chèn lại seed vào cây local. Gain A1 riêng là 6,50% và 5,93%. `frontier_insertions` đo ứng viên trong traversal, còn số lần chèn seed thực tế chưa có counter. `merge_time_ns` ON bao gồm cửa sổ công việc khác nhau giữa full và incremental. `barrier_wait_ns` là tổng worker-wait. Hai số này chưa cung cấp phân rã wall latency.
- **B1+A1** là tối ưu baseline của P2, với kết quả về latency trên một workload tại `jobs=1`. Bộ bằng chứng hiện tại giữ cách phân việc và chu kỳ đồng bộ cố định. [Nguồn engine đã freeze](../../../research/task_da/search_common/p2_engine.hpp), [báo cáo raw và counters](B1_A1_NARROW_REPLICATION_REPORT_20261119.md).

| Công trình | Cơ chế đã có và hệ quả cho H3 |
| --- | --- |
| Speed-ANN | Mở rộng nhiều ứng viên, local best-first queues, chia ứng viên chưa expand cho worker, shared visited lỏng và đồng bộ thích nghi theo vị trí cập nhật queue để tránh mở rộng dư. Chỉnh lịch merge theo trạng thái frontier đã có tiền lệ trực tiếp. [§§4.2–4.4 và Algorithms 2–3](https://johnpzh.github.io/assets/papers/arXiv-2022_Speed-ANN_Zhen.pdf) |
| iQAN | Path-wise parallelism với staged expansion, nhiều bước local giữa các lần merge, vị trí cập nhật để đồng bộ khi cần, và shared visiting map chấp nhận một số L2 lặp để giảm tranh chấp. Flag checked trong candidate pool và dedup theo visited là các kỹ thuật phía baseline. [§5 và pseudocode](https://johnpzh.github.io/assets/papers/PPoPP-2023_iQAN_Zhen.CameraReady.pdf) |
| AverSearch | Tách global workload balancer, sub-queue maintainers và distance calculators. Trao đổi bất đồng bộ, distance array để tái sử dụng kết quả và speculative expansion khi calculator rảnh. Hướng bỏ barrier, phân vai và tính distance trước đã được triển khai ở đây. [§§4.2–4.4](https://arxiv.org/html/2504.20461v2) |
| CAGRA và PipeANN | CAGRA mở rộng theo nhóm parent trên GPU và quản lý visited bằng hash table, gồm chế độ nhiều CTA. PipeSearch dùng thứ tự ưu tiên ứng viên để phát đọc SSD sớm, chồng I/O với compute. Cả hai cung cấp prior art cho expansion song song và speculation. [CAGRA §IV-B–C](https://arxiv.org/html/2308.15136v2), [PipeANN §3](https://www.usenix.org/system/files/osdi25-guo.pdf) |
| Hypergraph partitioning | Việc phân công tài nguyên theo tập dữ liệu dùng chung dưới ràng buộc cân bằng có tiền lệ rộng. Dùng overlap làm mục tiêu tự thân mang ít tính mới. [Çatalyürek và Aykanat, 1999](https://www.cs.bilkent.edu.tr/~aykanat/papersAbs/99IEEETPDSabs.html) |

## 5. Hướng H3 duy nhất để sàng lọc

**Phân công seed frontier theo overlap adjacency dưới ràng buộc thứ hạng.** Giả thuyết `PROPOSED` là một phần khoảng 665 duplicate L2/query còn lại sau B1+A1 xuất phát từ các seed cạnh nhau về rank nhưng bị chia sang hai worker dù có nhiều láng giềng chung. Dồn các seed có overlap thích hợp về cùng worker có thể tận dụng `local_seen` để tránh tính lặp, đồng thời giữ phân bổ rank cân bằng. Counters hiện có chưa cho biết phần trùng do seed dispatch so với các đỉnh mới sinh trong round.

**Quy tắc.** Với `p=2, S=16`, lấy đúng tối đa 32 seed chưa expand theo thứ tự `(squared_l2, ID)` của B1+A1. Chia theo nhóm bốn seed liên tiếp `a,b,c,d`. Giao `a,b` cho worker 0/1. Xét hai cách giao `c,d` để mỗi worker vẫn nhận một seed từ mỗi cặp rank liên tiếp. Với mỗi cách, lấy OR của hai chữ ký adjacency 128 bit trên mỗi worker rồi tính popcount `u0, u1`. Chọn cách có cặp `(max(u0,u1), u0+u1)` nhỏ hơn theo thứ tự từ điển. Hòa và phần đuôi dưới bốn seed dùng round-robin. Chữ ký đặt một bit theo hash ID láng giềng với hash đã khóa, cố định theo graph. Giữ nguyên graph, ngân sách round, visited policy, merge và hàng đợi local. Đổi worker có thể đổi thứ tự mở rộng và output nên phải đo Recall.

**Phần có thể đóng góp.** Kiểm nghiệm một chính sách chọn worker theo overlap của chính các ứng viên sắp dispatch, ở mỗi query/round với cùng tập seed và ràng buộc mỗi worker nhận một seed từ mỗi cặp rank. Speed-ANN/iQAN điều khiển chia việc và thời điểm đồng bộ, AverSearch chia workload rồi chia sẻ kết quả distance, còn hypergraph partitioning đã có mục tiêu cân bằng và đồng định vị. Trong các nguồn trên, chưa tìm thấy quy tắc dispatch ANN này. Tính mới ở phạm vi rộng hơn vẫn `UNKNOWN`. Cần tiếp tục đối chiếu các chính sách phân công theo locality và overlap trước khi đặt claim. Hướng này liên hệ với H-G ở giả thuyết về topology. H-G vẫn là một lane độc lập.

**Chi phí và đối chứng.** Sidecar chữ ký tốn 16 MB trên 1M đỉnh, dựng offline một lượt qua cạnh. Mỗi round đọc tối đa 32 chữ ký, tương đương 512 byte payload với các cache-line load có thể phân tán. Tối đa tám nhóm thực hiện OR/popcount và một quyết định trên đường tuần tự trước dispatch. Lợi ích cần giảm công của worker chậm nhất hoặc giảm round đủ để bù chi phí đó. Khoảng 665 duplicate còn lại chỉ chiếm khoảng 2,5% L2 sau B1 ở workload quan sát. Baseline chính là frozen **B1+A1 + flat + best-fixed S** với round-robin, trước hết tại `S=16`. Đối chứng âm hoán vị chữ ký giữa các đỉnh cùng bậc để giữ chi phí scheduler và phá tín hiệu topology. Đối chứng mạnh về cơ chế là round-robin với shared distance memo lưu kết quả L2 nhưng mỗi worker vẫn áp dụng quy tắc admission và mở rộng local ban đầu. So sánh này kiểm tra liệu né atomic/shared lookup bằng phân công có thực sự đáng giá.

**Cách bác bỏ.** Trên một panel validation đã khóa, bắt đầu bằng so sánh exact union của láng giềng chưa visited, dùng đúng snapshot tại đầu round, giữa round-robin và cách giao tối ưu trong mỗi nhóm bốn. Đo giao giữa hai union và `max(|U0|,|U1|)` trên cả tập seed của round. Đây là phép sàng lọc offline cho proxy, vì các seed có thể bị lấn chỗ bởi ứng viên phát sinh. Dừng hướng này nếu ngay cả phép tính exact thiếu tín hiệu giảm công của worker chậm ở hai graph, hoặc chữ ký thật không tốt hơn hoán vị trên panel. Các raw hiện tại có counters theo query và thiếu snapshot dispatch/visited, nên lấy mẫu trace thực cần một phạm vi được duyệt riêng. Nếu screening qua, một thử nghiệm hẹp đã duyệt có thể đòi floor Recall@10 và `|ΔRecall| ≤ 0,0001` ở beam chọn chỉ trên validation, kiểm tra công worker chậm, rounds và mean/p95 OFF. Bác mục tiêu latency nếu CI95 upper của mean gain so với B1+A1 dưới 5%, hoặc dừng vì chất lượng nếu có giảm Recall lặp lại ngoài biên. Gain trên proxy offline chỉ là bằng chứng về điều kiện cơ chế.

## 6. Quyết định và bước tiếp

**PIVOT** khỏi việc xem dynamic `S`, atomic visited hoặc bỏ barrier riêng lẻ là đóng góp H3. **HOLD** triển khai hướng phân công theo overlap vì dư địa quan sát nhỏ, nguồn duplicate còn lại chưa định vị và tính mới chưa xác lập. **Ưu tiên khoa học trước mắt** là xác minh với Task A liệu có thể dựng hai A3 build replicate đủ điều kiện trên Ryzen. Nếu đủ điều kiện và owner duyệt, phép xác nhận nhỏ chỉ cần hai arm ở R4/R5. Nếu Task A không thể bảo toàn phương pháp, đóng thiết kế đó ở HOLD và ưu tiên một phép sàng lọc H3 offline được duyệt riêng thay cho việc thêm process repeats trên graph cũ. [Thiết kế xác nhận](B1_A1_R4_R5_CONFIRMATION_PREREG_20261119.md).

Historical P0, Full P1 và t0998 giữ `HOLD`, Protocol V4 D1–D5 giữ `UNAPPROVED`, P3 Official giữ `CLOSED`, H3/TP-CG giữ `NOT_OPENED`. D1 giữ `UNTESTED`, D4 giữ `NOT TESTED`, D6 giữ `INCONCLUSIVE` trên subject lịch sử của từng giả thuyết.
