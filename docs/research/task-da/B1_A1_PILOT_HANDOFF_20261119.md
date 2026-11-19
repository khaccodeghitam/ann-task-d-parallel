# Task D · Kiểm toán và hoàn tất pilot B1/A1 trên Ryzen 4650U

**Trạng thái chuyển từ PARTIAL sang COMPLETE.** Đã chạy đúng phần còn thiếu trên AMD Ryzen 5 PRO 4650U. B1 cắt 67–87% số L2 trùng. B1+A1 giảm 11,59% latency mean trên A3_r1 p=2 S=16, còn cả hai ô p=4 best-fixed có CI95 bao gồm 0. Quyết định **HOLD** mở rộng toàn ma trận.

| Phần tiếp quản | Trạng thái cuối | Xác minh |
| --- | --- | --- |
| Pilot A1 và B1+A1 | COMPLETE · PASS parity | 85 OFF và 17 ON, đủ 5 repeats cho 17 arm. Mỗi OFF khớp ON ở top-10 ID và squared L2. B1+A1 khớp B1 về counter thuật toán. A1 khớp baseline. |
| Tập 3.000 query rời | COMPLETE · A0 dưới ngưỡng Recall | 8/8 ON đủ top-10. Bốn biến thể trùng kết quả theo từng đồ thị. A0 0,98940, A3 0,99110. |
| Giám sát và niêm phong | COMPLETE | 110/110 lượt mới thoát 0, 0 guard stop, 883/883 tệp evidence khớp SHA-256 và số byte. |
| Kiểm thử dataset-free sau pilot | COMPLETE · PASS | 516 ca thu thập, 505 pass và 11 skip có điều kiện. |

## Trạng thái bàn giao từ Gemini

| Phase | Trạng thái khi tiếp quản | Bằng chứng |
| --- | --- | --- |
| CTest Release | COMPLETE · PASS | 1/1 CTest suite, 25/25 ca Python/native, 0 skip. |
| CTest ASan+UBSan+LSan | COMPLETE · PASS | 1/1 suite, 25/25 ca, 0 skip. Build GCC Linux dùng `-fsanitize=address,undefined`, với LSan tích hợp trong ASan. |
| Correctness gate | COMPLETE · PASS | 35 lượt smoke_500 Release, 6 lượt sanitizer 100q. Gemini task-1258 thoát 0. |
| Pilot 1 · B1 | COMPLETE | 60 OFF, 12 ON, đủ 5 repeats/cell. Gemini task-1262 thoát 0. |
| Pilot 2 · A1 và B1+A1 | NOT RUN | Chưa có thư mục/checkpoint trong evidence Gemini. |
| Tập 3.000 query rời | NOT RUN | Tệp IDs đã có checksum. Chưa có kết quả. |
| Toàn bộ pilot | **PARTIAL** | Dòng `PIVOT_B1_A1_COMPLETE` trong từng log đánh dấu stage được yêu cầu qua `--stage`. |

### Git, correctness và dữ liệu

- Nhánh `research/task-da-pivot-b1-a1-20261119`. HEAD và tag `task-da-p2-stage-de-freeze-20261119` cùng trỏ tới `87d4a8149416b22ccf8854f72c7c72f09197cfa3`. Working tree khi tiếp quản có bốn tệp sửa từ Gemini và index sạch. `p2_engine.hpp` triển khai B1/A1, `p2_eval.cpp` thêm cờ và metadata, `test_task_da.py` thêm test parity. Diff còn có sửa cú pháp CLI trong runner i5. Các lệnh thực nghiệm dùng trình chạy của pilot Ryzen. `git diff --check` sạch.
- Kiểm tra tiến trình trước khi đo dựa trên tên executable và đối số script. Không thấy hai tên này trong namespace của phiên và cả hai stage được Gemini ghi đã thoát 0. Danh sách tiến trình host được xác minh trực tiếp trong lúc resume và chỉ thấy phiên tiếp quản cùng evaluator của phiên. Đối chiếu 232/232 tệp theo độ dài và SHA-256, đủ 113 lượt JSON/JSONL, đủ query đúng thứ tự, đúng graph/beam/cờ/CPU, 0 hàng thiếu top-10. Kiểm lại mean/p50/p95 từ nanosecond trong JSONL, tổng counter từ ON và Recall@10 từ ground truth.
- Smoke_500 trên A0_r1/A3_r1 qua 5 ô p/S. Mỗi biến thể có parity ON/OFF tuyệt đối về query ID, top-10 ID và squared L2. Baseline của smoke có ON, còn parity ON với cả 5 OFF của baseline được kiểm trên pilot 3.000 query. A1 giữ nguyên mọi counter thuật toán trên cả hai visited policy. B1 giữ nguyên expansion, unique L2, frontier insertion và số lần merge. Số lượt L2 trùng giảm đúng bằng số lượt `already_seen_attempts` tăng.
- ASan 100 query thực trên A3_r1 p=4 S=16 có 6/6 lượt đủ top-10. Cả ba biến thể đạt ON/OFF parity và khớp từng kết quả của 100 query đầu trong smoke Release tương ứng. Log correctness ghi exit 0 và không có lỗi sanitizer. Hai bộ CTest được kiểm qua log gốc, không chạy lại.
- Đối chiếu freeze trực tiếp với 7 JSONL ON Stage D đã kiểm SHA-256. Baseline mới `baseline+full` khớp từng query về ID, squared L2 và mọi counter thuật toán, gồm hai p=1 và năm ô đa worker. Đây là kết quả về tương đương hành vi trong mẫu. Perf freeze ở những phiên đo trước chỉ là mốc lịch sử.

## Thiết kế so sánh

- Cùng AMD Ryzen 5 PRO 4650U, cùng binary Release và bộ MS-Turing-1M, (K=10), jobs=1 và 100 query warmup. Affinity process cho từng worker khớp p=1 `[0]`, p=2 `[0,2]`, p=4 `[0,2,4,6]`. CPU 6 ở nhóm L3 còn lại. Tập pilot 3.000 query lấy từ `test_90k` và tách khỏi warmup. Tập disjoint lấy 3.000 ID đầu còn lại theo thứ tự test split.
- Flat merge, frozen beam và fixed S giữ nguyên trong từng ô. Theo kế hoạch freeze, đối chứng best-fixed p=4 là A0_r1 S=8 (beam 408) và A3_r1 S=16 (beam 960). Với p=2 cả hai dùng S=16 (beam 412 và 970). A3_r1 p=4 S=8 là đối chứng phụ đã định trước. Các beam đến từ chọn trên val_10k, có LCB95 Recall@10 ≥0.990. Stage C2 từng ghi nhận A0 p=4 S=4 gần ngang S=8, nên best-fixed ở đây chỉ áp dụng cho lựa chọn đã freeze.
- Block B1 có baseline và B1. Block A1 có baseline, A1 và B1+A1. Các lượt đối chứng mới thuộc lịch Pilot A1 của Gemini và cung cấp baseline cùng block. Trong mỗi repeat, runner xoay thứ tự arm và đảo ở repeat lẻ. Hai arm p=1 là mốc scaling phụ. Số liệu dưới đây dùng baseline đa worker cùng ô p/S làm mẫu số.
- App dùng `baseline|barrier_all_evaled` cho visited và `full|incremental` cho frontier. B1 công bố các đỉnh đã tính L2 khi mọi worker đến barrier. A1 giữ bit expanded trên flat entry, điều phối tối đa `p*S` seed mỗi round và tránh đưa seed đuôi không thể được pop trong round vào cây local. Việc đo logical work và thời gian dùng ON/OFF riêng theo protocol.

- Đọc archive Gemini và ghi Pilot A1/tập rời vào thư mục mới. Runner gốc chỉ kiểm tra tệp summary để bỏ qua lượt. Phiên này xác minh bảng kê SHA-256 và JSONL gốc trước khi chọn hai stage còn thiếu. Mỗi lượt mới có checkpoint gồm digest của JSON/JSONL, manifest giám sát và log. Checkpoint hợp lệ phải có exit 0, không có guard failure, đúng hash và đúng nội dung. Các summary hay raw của Gemini giữ nguyên.

## Kết luận và quyết định

1. **B1 giảm 67,45–87,18% L2 trùng và khoảng 12–14,5% tổng L2** trên năm ô pilot. Tại hai đối chứng p=4 best-fixed, A0_r1 giảm từ 3.774,5 xuống 1.118,8 L2 trùng/query (70,36%), A3_r1 từ 6.213,8 xuống 2.022,7 (67,45%). Các lần tính lặp còn lại phù hợp với việc B1 chỉ chia sẻ visited ở barrier. Top-10 và số L2 unique giữ nguyên trong các phép kiểm.
2. **A1 chặn việc phát seed dư. Mức tiết kiệm thời gian frontier riêng vẫn chưa xác định.** Counter `frontier_insertions` chỉ đếm chèn ứng viên trong traversal. Với A1, `merge_time_ns` tăng 32–157 µs/query ở cả năm ô trong block A1. Timer bao gồm thu counter và chuẩn bị seed của A1, trong khi dispatch của baseline nằm ngoài cửa sổ đó. Barrier là tổng thời gian chờ của các worker, có thể lớn hơn thời gian chờ trên đường găng. Các số ON mô tả từng lượt chẩn đoán trong chế độ instrumentation.
3. **Công giảm chuyển thành latency thấp hơn rõ nhất ở A3_r1 p=2 S=16.** B1 giảm 4,53% so với baseline B1, A1 giảm 5,87% và combo giảm 11,59% so với baseline A1. Cả ba CI95 ghép cặp của latency mean đều nằm dưới 0 trong ô này. Riêng A1 giữ nguyên số lần tính khoảng cách và expansion, nhưng latency OFF vẫn giảm ở ô đó.
4. **Combo vượt A1 ở A3_r1 p=2** với Δ = −332,2 µs/query, CI95 [−424,6, −239,8]. Chênh lệch chuẩn hóa theo baseline giữa combo và B1 cùng ô là −409,2 µs/query, CI95 [−616,9, −201,4], với giới hạn so sánh qua hai block. CI95 của tương tác gồm 0 ở cả năm ô. Dữ liệu vì vậy chưa xác định lợi ích ngoài tổng hiệu ứng riêng. Ở p=4, phép so sánh combo với từng biến thể đều còn bất định.
5. **Hai baseline p=4 best-fixed vẫn giữ vai trò đối chứng chính.** B1 chậm hơn lần lượt 1,19% (A0_r1) và 5,93% (A3_r1) theo ước lượng điểm, dù L2 trùng giảm mạnh. Combo nhanh hơn khoảng 2,66% và 2,95%, với CI95 của Δ lần lượt [−265,6, 142,1] và [−235,7, 21,2] µs/query. A1 riêng cũng có CI95 bao gồm 0 ở cả hai. Combo p=2 A3_r1 đạt 5,13 ms, trong khi baseline p=4 A3_r1 cùng block đạt 3,63 ms. Lợi ích p=2 áp dụng khi giữ ngân sách hai worker.
6. **HOLD mở rộng toàn ma trận sang R2/R3.** Tín hiệu A3_r1 p=2 S=16 đủ để đề xuất một phép tái lập hẹp trên A3_r2/r3 nếu mở phase tiếp theo. Hướng kiểm chứng là bốn phương án trong cùng block, beam chọn trên val_10k, quality gate trên split độc lập với việc chọn cấu hình và lặp process để kiểm tra cả hiệu ứng combo lẫn tương tác. Kết quả p=4 hiện chưa đủ căn cứ để mở rộng. Pilot tiếp quản có nhãn **EXPLORATORY_HOST_SPECIFIC**.

### Giới hạn

- Một graph seed cho mỗi arm A0/A3. CI95 phản ánh dao động 5 process repeats trên cùng seed, cùng tập query. Có nhiều tương phản thăm dò với CI danh nghĩa. Tín hiệu A3 p=2 cần xác nhận trên seed khác. Tương phản qua hai block nhạy với trôi trạng thái host và khác biệt observer.
- Pilot B1 của Gemini có observed affinity và VmHWM trong JSON. Lệnh gốc gọi evaluator trực tiếp, không có chuỗi nhiệt/điện hay log safety guard theo lượt. Block tiếp quản có telemetry và watchdog theo từng evaluator, start Tctl dưới 85 °C, stop ở mẫu Tctl ≥95 °C, kiểm tra AC, RAM, disk, swap và critical trips. Không loại lượt chậm.
- Tập pilot 3.000 query đã được dùng ở Stage D. Tập kiểm tra rời dùng ON và một lượt/cấu hình, nhằm kiểm output và quan sát logical work. Timing OFF lặp dùng tập pilot. A0_r1 p=4 S=8 đạt 0,98940 ± 0,00069 SE cho cả bốn phương án, nên ô này trượt point floor 0,990 trên tập rời. A3_r1 p=4 S=16 đạt 0,99110 ± 0,00068 SE, qua point floor. Mốc này dùng point estimate từ mẫu nhỏ có độ bất định đáng kể. Parity đặt phần hụt Recall của A0 ở cả baseline đã freeze cấu hình và ba biến thể.
- Chưa đo A0/A3 R2/R3 cho B1/A1, A1 graph arm, toàn bộ test_90k cho ablation, B2 hoặc TP-CG. Theo freeze, Historical P0 / Full P1 / t0998 ở **HOLD**, Protocol V4 D1–D5 ở **UNAPPROVED**, P3 Official ở **CLOSED** và TP-CG/H3 ở **NOT_OPENED**.

## Recall và latency OFF

Latency tính bằng µs. Mean, p50 và p95 là trung bình qua 5 lượt process, kèm CI95 Student-t (df=4). p50/p95 được tính trên 3.000 query trong từng lượt. Speedup là tỷ số hai latency mean tổng hợp so với baseline trong cùng block.

| Đồ thị · p/S | Phương án | Recall@10 | Mean [CI95] | p50 [CI95] | p95 [CI95] | × vs flat cùng block |
| --- | --- | --- | --- | --- | --- | --- |
| A0_r1 · 2/16 | Baseline · B1 | 0.99087 | 3669.7 [3544.0, 3795.3] | 3683.9 [3613.4, 3754.3] | 4584.4 [4142.2, 5026.5] | 1.0000 |
| A0_r1 · 2/16 | B1 | 0.99087 | 3599.9 [3444.7, 3755.1] | 3591.3 [3488.0, 3694.6] | 4682.6 [4301.7, 5063.5] | 1.0194 |
| A0_r1 · 2/16 | Baseline · A1 | 0.99087 | 3699.0 [3435.9, 3962.0] | 3744.8 [3545.0, 3944.6] | 4476.0 [4031.3, 4920.8] | 1.0000 |
| A0_r1 · 2/16 | A1 | 0.99087 | 3557.1 [3475.4, 3638.8] | 3625.2 [3591.5, 3658.8] | 4246.9 [3998.1, 4495.6] | 1.0399 |
| A0_r1 · 2/16 | B1+A1 | 0.99087 | 3398.6 [3298.9, 3498.2] | 3467.2 [3411.2, 3523.2] | 4117.8 [3823.5, 4412.1] | 1.0884 |
| A0_r1 · 4/8 | Baseline · B1 | 0.99100 | 2298.5 [2174.6, 2422.3] | 2303.0 [2199.3, 2406.6] | 2760.9 [2529.0, 2992.8] | 1.0000 |
| A0_r1 · 4/8 | B1 | 0.99100 | 2325.8 [2179.9, 2471.7] | 2326.6 [2220.9, 2432.3] | 2885.3 [2586.8, 3183.8] | 0.9883 |
| A0_r1 · 4/8 | Baseline · A1 | 0.99100 | 2321.9 [2139.3, 2504.5] | 2320.6 [2182.2, 2459.0] | 2849.8 [2501.8, 3197.8] | 1.0000 |
| A0_r1 · 4/8 | A1 | 0.99100 | 2260.9 [2184.7, 2337.1] | 2282.9 [2204.4, 2361.4] | 2707.5 [2606.3, 2808.7] | 1.0270 |
| A0_r1 · 4/8 | B1+A1 | 0.99100 | 2260.1 [2229.6, 2290.7] | 2284.5 [2246.1, 2323.0] | 2737.2 [2609.8, 2864.6] | 1.0273 |
| A3_r1 · 2/16 | Baseline · B1 | 0.99037 | 5825.5 [5778.1, 5872.8] | 5909.7 [5876.8, 5942.5] | 7096.4 [6952.2, 7240.6] | 1.0000 |
| A3_r1 · 2/16 | B1 | 0.99037 | 5561.6 [5360.6, 5762.7] | 5640.8 [5495.9, 5785.8] | 6938.7 [6382.6, 7494.8] | 1.0474 |
| A3_r1 · 2/16 | Baseline · A1 | 0.99037 | 5806.6 [5682.1, 5931.2] | 5923.7 [5839.1, 6008.3] | 6993.3 [6670.4, 7316.3] | 1.0000 |
| A3_r1 · 2/16 | A1 | 0.99037 | 5465.8 [5357.3, 5574.4] | 5592.8 [5524.2, 5661.4] | 6597.4 [6308.2, 6886.5] | 1.0623 |
| A3_r1 · 2/16 | B1+A1 | 0.99037 | 5133.6 [5080.7, 5186.5] | 5280.1 [5236.1, 5324.1] | 6265.4 [6153.2, 6377.5] | 1.1311 |
| A3_r1 · 4/8 | Baseline · B1 | 0.99067 | 3842.9 [3060.5, 4625.3] | 3867.4 [3202.3, 4532.6] | 4698.7 [3133.6, 6263.7] | 1.0000 |
| A3_r1 · 4/8 | B1 | 0.99067 | 3691.2 [3326.8, 4055.7] | 3719.8 [3433.6, 4006.1] | 4594.6 [3754.4, 5434.8] | 1.0411 |
| A3_r1 · 4/8 | Baseline · A1 | 0.99067 | 3660.8 [3510.5, 3811.2] | 3705.0 [3554.3, 3855.7] | 4402.7 [4191.5, 4613.8] | 1.0000 |
| A3_r1 · 4/8 | A1 | 0.99067 | 3633.1 [3402.0, 3864.2] | 3646.9 [3465.3, 3828.5] | 4490.5 [4021.4, 4959.5] | 1.0076 |
| A3_r1 · 4/8 | B1+A1 | 0.99067 | 3629.9 [3047.3, 4212.5] | 3634.6 [3222.0, 4047.3] | 4633.1 [3238.6, 6027.6] | 1.0085 |
| A3_r1 · 4/16 | Baseline · B1 | 0.99070 | 3741.2 [3435.4, 4046.9] | 3778.3 [3503.5, 4053.1] | 4567.4 [3997.7, 5137.1] | 1.0000 |
| A3_r1 · 4/16 | B1 | 0.99070 | 3962.9 [3185.6, 4740.2] | 3947.4 [3277.1, 4617.6] | 5071.0 [3676.7, 6465.3] | 0.9441 |
| A3_r1 · 4/16 | Baseline · A1 | 0.99070 | 3630.1 [3453.3, 3806.9] | 3669.7 [3506.9, 3832.5] | 4421.1 [4142.8, 4699.5] | 1.0000 |
| A3_r1 · 4/16 | A1 | 0.99070 | 3650.1 [3464.4, 3835.8] | 3669.1 [3503.5, 3834.6] | 4551.2 [4194.3, 4908.2] | 0.9945 |
| A3_r1 · 4/16 | B1+A1 | 0.99070 | 3522.9 [3315.7, 3730.0] | 3571.6 [3395.8, 3747.4] | 4374.7 [3969.8, 4779.6] | 1.0304 |

## Chênh lệch latency mean ghép cặp

Δ tính bằng µs/query. Giá trị âm tương ứng với phương án nhanh hơn. CI95 dùng lượt process ghép theo repeat trong từng block. Combo − B1 qua block lấy (Combo − baseline A1) − (B1 − baseline B1). Tương tác lấy (Combo − A1) − (B1 − baseline B1). Hai tương phản qua block dùng sai số chuẩn của hai hiệu số với giả định hai block độc lập và hệ số t với df=4.

| Đồ thị · p/S | B1 − base | A1 − base | Combo − base | Combo − A1 | Combo − B1 qua block | Tương tác qua block |
| --- | --- | --- | --- | --- | --- | --- |
| A0_r1 · 2/16 | -69.8 [-256.7, 117.2] | -141.8 [-326.3, 42.6] | -300.4 [-620.7, 19.9] | -158.5 [-304.9, -12.2] | -230.6 [-601.5, 140.3] | -88.8 [-326.2, 148.7] |
| A0_r1 · 4/8 | 27.3 [-73.2, 127.8] | -61.0 [-222.8, 100.8] | -61.8 [-265.6, 142.1] | -0.8 [-72.8, 71.2] | -89.1 [-316.4, 138.2] | -28.1 [-151.7, 95.6] |
| A3_r1 · 2/16 | -263.9 [-456.1, -71.6] | -340.8 [-476.3, -205.2] | -673.0 [-751.8, -594.2] | -332.2 [-424.6, -239.8] | -409.2 [-616.9, -201.4] | -68.4 [-281.7, 144.9] |
| A3_r1 · 4/8 | -151.7 [-605.8, 302.4] | -27.7 [-163.8, 108.4] | -30.9 [-584.1, 522.3] | -3.2 [-539.6, 533.2] | 120.8 [-594.9, 836.5] | 148.5 [-554.3, 851.3] |
| A3_r1 · 4/16 | 221.7 [-274.1, 717.6] | 20.0 [-106.2, 146.3] | -107.2 [-235.7, 21.2] | -127.3 [-310.6, 56.0] | -329.0 [-841.2, 183.3] | -349.0 [-877.7, 179.7] |

## Công thực hiện ON

Mỗi hàng lấy từ một lượt instrumented ON trên 3.000 query. Hai cột thời gian dùng µs/query. RAM là khoảng VmHWM của 5 process OFF, tính bằng MiB.

| Đồ thị · p/S | Phương án | L2 trùng/query | Tổng L2/query | Merge µs | Barrier µs | RAM MiB |
| --- | --- | --- | --- | --- | --- | --- |
| A0_r1 · 2/16 | Baseline · B1 | 3560.3 | 21857.4 | 342.1 | 220.7 | 851.1–851.3 |
| A0_r1 · 2/16 | B1 | 918.0 | 19215.1 | 350.4 | 234.6 | 851.1–851.3 |
| A0_r1 · 2/16 | Baseline · A1 | 3560.3 | 21857.4 | 350.6 | 246.7 | 851.2–851.3 |
| A0_r1 · 2/16 | A1 | 3560.3 | 21857.4 | 384.2 | 248.1 | 851.1–851.3 |
| A0_r1 · 2/16 | B1+A1 | 918.0 | 19215.1 | 405.0 | 256.6 | 851.1–851.3 |
| A0_r1 · 4/8 | Baseline · B1 | 3774.5 | 22223.8 | 407.6 | 600.4 | 851.0–851.3 |
| A0_r1 · 4/8 | B1 | 1118.8 | 19568.0 | 443.3 | 743.0 | 851.1–851.3 |
| A0_r1 · 4/8 | Baseline · A1 | 3774.5 | 22223.8 | 426.7 | 700.4 | 851.1–851.3 |
| A0_r1 · 4/8 | A1 | 3774.5 | 22223.8 | 458.9 | 662.9 | 851.1–851.3 |
| A0_r1 · 4/8 | B1+A1 | 1118.8 | 19568.0 | 477.7 | 685.7 | 851.1–851.3 |
| A3_r1 · 2/16 | Baseline · B1 | 5152.0 | 30988.2 | 644.5 | 484.5 | 797.6–797.8 |
| A3_r1 · 2/16 | B1 | 660.4 | 26496.6 | 670.1 | 527.8 | 797.5–797.7 |
| A3_r1 · 2/16 | Baseline · A1 | 5152.0 | 30988.2 | 648.8 | 556.3 | 797.4–797.8 |
| A3_r1 · 2/16 | A1 | 5152.0 | 30988.2 | 793.2 | 486.8 | 797.6–797.8 |
| A3_r1 · 2/16 | B1+A1 | 660.4 | 26496.6 | 770.4 | 477.3 | 797.7–797.8 |
| A3_r1 · 4/8 | Baseline · B1 | 5351.7 | 31150.9 | 888.6 | 2439.4 | 797.6–797.8 |
| A3_r1 · 4/8 | B1 | 854.8 | 26654.1 | 784.4 | 1554.0 | 797.7–797.8 |
| A3_r1 · 4/8 | Baseline · A1 | 5351.7 | 31150.9 | 738.5 | 1366.9 | 797.6–797.7 |
| A3_r1 · 4/8 | A1 | 5351.7 | 31150.9 | 895.9 | 1319.7 | 797.6–797.8 |
| A3_r1 · 4/8 | B1+A1 | 854.8 | 26654.1 | 892.0 | 1313.0 | 797.7–797.7 |
| A3_r1 · 4/16 | Baseline · B1 | 6213.8 | 32081.9 | 740.6 | 1184.2 | 797.6–797.8 |
| A3_r1 · 4/16 | B1 | 2022.7 | 27890.8 | 765.6 | 1233.2 | 797.6–797.8 |
| A3_r1 · 4/16 | Baseline · A1 | 6213.8 | 32081.9 | 729.4 | 1127.9 | 797.5–797.7 |
| A3_r1 · 4/16 | A1 | 6213.8 | 32081.9 | 831.5 | 1105.7 | 797.6–797.8 |
| A3_r1 · 4/16 | B1+A1 | 2022.7 | 27890.8 | 834.8 | 1109.2 | 797.6–797.8 |

### Kiểm chứng tập query rời

| Đồ thị · p/S | Phương án | Recall@10 | L2 trùng/query | Merge µs | Barrier µs |
| --- | --- | --- | --- | --- | --- |
| A0_r1 · p4_S8 | Baseline | 0.98940 | 3772.0 | 422.7 | 692.2 |
| A0_r1 · p4_S8 | B1 | 0.98940 | 1111.5 | 436.0 | 695.2 |
| A0_r1 · p4_S8 | A1 | 0.98940 | 3772.0 | 486.5 | 992.3 |
| A0_r1 · p4_S8 | B1+A1 | 0.98940 | 1111.5 | 470.8 | 679.2 |
| A3_r1 · p4_S16 | Baseline | 0.99110 | 6211.6 | 739.5 | 1166.3 |
| A3_r1 · p4_S16 | B1 | 0.99110 | 2028.2 | 739.1 | 1123.4 |
| A3_r1 · p4_S16 | A1 | 0.99110 | 6211.6 | 857.0 | 1270.2 |
| A3_r1 · p4_S16 | B1+A1 | 0.99110 | 2028.2 | 839.9 | 1105.9 |

### Telemetry của các lượt resume đã qua kiểm tra

| Phase | Lượt | Tctl °C min–max | MemAvailable GiB thấp nhất | VmHWM MiB min–max OFF | Số mẫu |
| --- | --- | --- | --- | --- | --- |
| off | 85 | 50.8–90.5 | 6.47 | 797.4–851.3 | 1498 |
| on | 17 | 67.4–90.8 | 7.16 | — | 316 |
| disjoint_test_3k_check | 8 | 70.2–83.8 | 7.42 | — | 123 |

## Tái lập và SHA-256

Chạy lệnh từ root repository. `G` là evidence Gemini ở ngoài repo. `R` là bundle của lần tiếp quản. Các đường dẫn trong CSV tính tương đối theo thư mục chứa manifest. Trường `result_file` giữ vị trí tuyệt đối lúc ghi. Khi dùng bản sao, mở JSONL cùng thư mục với summary theo basename của trường đó.

```bash
G=../artifact-evidence/p2-pivot-b1-a1-20261119
R=../artifact-evidence/p2-pivot-b1-a1-resume-20261119

git status --short --branch
git rev-parse HEAD 'task-da-p2-stage-de-freeze-20261119^{commit}'
git diff --check
git diff --binary | sha256sum
sha256sum "$G/EVIDENCE_CHECKSUMS.csv" "$R/evidence/EVIDENCE_CHECKSUMS.csv"
(cd "$R" && sha256sum -c BUNDLE.sha256)
PYTHONDONTWRITEBYTECODE=1 python3 "$R/audit.py"
PYTHONDONTWRITEBYTECODE=1 python3 "$R/tables.py"
```

`audit.py` kiểm tra các lượt Gemini và đối chiếu freeze. `tables.py` dựng lại các bảng từ summary đã kiểm JSONL. Để tái đo có chủ đích trên Ryzen 4650U, chép `audit.py` và `resume.py` sang thư mục mới, chạy `resume.py --preflight` rồi `python3 -u resume.py` từ root repo. Đây là lệnh khởi tạo block A1 và kiểm tập rời trong thư mục mới. Mỗi lượt có lệnh đầy đủ trong `command.sh`, exit code và giám sát trong `manifest.json` / `host.jsonl`. Script Gemini tại `$G/run_pivot_b1_a1_pilot.py` là nguồn protocol và lịch chạy. Lệnh `--stage all` của script gốc có thể ghi lại summary/checksum cũ và chỉ kiểm tra sự hiện diện của summary khi bỏ qua lượt.

```bash
# Kiểm thử lại build hiện tại nếu cần tái lập gate synthetic.
ctest --test-dir build-task-da -V
ctest --test-dir build-task-da-asan -V
PYTHONPATH="$PWD/.venv-research/lib/python3.12/site-packages" \
  /usr/bin/python3 -m unittest discover -s tests/research -v
```

| Danh tính | SHA-256 |
| --- | --- |
| Diff Gemini trên commit freeze | `d2767141bc504195e9daab2e1f7fc6129f1fa8097ca652b9e75f3a8d58415549` |
| Binary freeze Release | `ff46d6ac8895d519054548575c3187544716c0fdf2bbdad83db8a0a8cc7f8759` |
| Binary pilot Release · GCC 13.3.0 `-O3 -DNDEBUG` | `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1` |
| Binary pilot sanitizer · GCC 13.3.0 `-O2 -g -DNDEBUG -fsanitize=address,undefined` | `c3151165f23cffeec41d6ec508a2339b9eb7db627f708d470dcfc0b622c09ea7` |
| Manifest evidence Gemini · 232 tệp | `eda452166aa05eb6bd3934e45f2aaf6aecfb57122ff54d3f9340b2b99c725067` |
| Script protocol Gemini | `c6ef2c8fc02143015b7597841aeec28d3027365eb0f607bc2c4674120b82aedd` |
| Protocol P2 Exploratory 0.990 | `ea18b0530e2fa66beae342456ff34634b0ddcb49eacb5c94856cc10c4df4ba8a` |
| Kế hoạch pivot và chọn fixed S | `f6642091bf81277e3aa6a951025cdc96cf2390b46a52b0b701bf7fc6eeec70b0` |
| Manifest beam val_10k Stage D | `f98c0454f065e8debf10e7849f2ebcd1061d294980c8ddad5f836269175b4bc5` |
| Manifest đầu vào V3 | `9094fb348269918077b37e901b887eae7ac1662c74a45aa43a237cd227e57d16` |
| Base MS-Turing-1M | `44e83e1dd4c65999b75873101adc5ac06ca900d259a2befd05c2c3aa28ff4042` |
| Query file | `48d087a17bec15a5ec9ea526fe9bd14ac31bbbb5cd200817b341adbb77695644` |
| Ground truth | `fa5acf5ab262b42355296e99f920e6aa863f48820ca6f70fa37ca7966634c344` |
| Index A0_r1 | `55df31ac9b7716f779dca332ce9360c9e21a065f9298ec1c92c8ccdd37d72522` |
| Index A3_r1 | `0fff20ec47502c675c4905787d319390e49fa5bee856ac16c814c74697c5fbb2` |
| Query IDs Pilot 3.000 | `18d8b901e925d71c0ddb2d043bf2cba12edab4061859da833bd1ccc37790c1b0` |
| Warmup IDs và ASan 100 | `199ca6066269641347280d6ef4eaab39efee3397b87c23cd74d38ee85bcd4783` |
| Smoke_500 IDs | `54f9eae4c2039f613fe63e2a27a40fadd7b498ab31f195f54fe7340d845ae9a6` |
| Disjoint 3.000 IDs | `c91dcae377afc8161856377842930c691b2ea19e337d1361576538b5ab39abfc` |
| Resume wrapper | `0cf76c6e72fe8da698d7c7da041430a7312d54894e4861f3ee31660f4bd454d9` |
| Manifest evidence mới | `7b55703ad2787ec9659922a7782e562f8f82c2a65bc098c3a3b65fe7312ab541` |
| BUNDLE.sha256 · 896 tệp đã kiểm | `1c0df3150aafaf5fae6aee26018a6309201e0376e41ccb016c380e3ed6c1c173` |

Đối chiếu [kế hoạch chọn baseline](POST_STAGE_DE_AUDIT_AND_H3_PIVOT_PLAN.md), [checkpoint freeze](P2_FOLLOWUP_CHECKPOINT_20261119.md) và [addendum chất lượng](PROTOCOL_V4_1_P2_EXPLORATORY_0990_ADDENDUM.md).
