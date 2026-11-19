# Task D · Tái lập hẹp B1+A1 trên Ryzen 4650U

**HOLD theo tiêu chí outer đã đăng ký.** Tín hiệu B1+A1 khoảng 11,59% trên R1 lặp lại về hướng và độ lớn trên từng seed mới. Gain mean ghép cặp là **12,29%** trên R2 và **10,08%** trên R3 tại output tương đương. CI95 chính theo hai graph seed là **[−2,84%, 25,21%]**. Kết quả củng cố một tối ưu baseline trên Ryzen ở `p=2, S=16`.

## Phạm vi và kiểm toán

A3-R2 và A3-R3 dùng cùng binary pilot trên `thinhbui-linux` (AMD Ryzen 5 PRO 4650U). Mỗi query có `p=2`, `S=16`, `K=10`, `jobs=1`, flat merge, 100 warmup query và CPU `[0,2]` trên hai core vật lý khác nhau trong cùng L3. Đối chứng `base` dùng `baseline/full`, B1 dùng `barrier_all_evaled/full`, A1 dùng `baseline/incremental`, combo dùng `barrier_all_evaled/incremental`. Đăng ký beam, query selection, block và tiêu chí tại commit `574420778c6e239d58bbce3df9d86136a47f90c9`. [Kế hoạch đăng ký trước](B1_A1_NARROW_REPLICATION_PLAN_20261119.md)

Trước khi đo, working tree khớp diff pilot đã niêm phong (`d2767141bc504195e9daab2e1f7fc6129f1fa8097ca652b9e75f3a8d58415549`). Đã kiểm `BUNDLE.sha256` của 896 tệp resume, 232 tệp Gemini, 113 lượt Gemini và parity với 7 đối chứng Stage D. Đóng băng source và handoff ở commit `f2cd634b837a70735c3e31e5956f0524bfc26675`, tag `task-da-b1-a1-pilot-freeze-20261119`. Commit đó lưu nguyên diff kế thừa, gồm sửa hợp đồng CLI trong runner i5. Freeze Stage D/E vẫn trỏ tới `87d4a8149416b22ccf8854f72c7c72f09197cfa3`. [Báo cáo pilot và danh tính artifact](B1_A1_PILOT_HANDOFF_20261119.md), [Checkpoint Stage D/E](P2_FOLLOWUP_CHECKPOINT_20261119.md)

Correctness pass hai CTest suite Release và ASan+UBSan+LSan, mỗi suite 25 ca. 16 lượt Release smoke (500 query) và 16 lượt sanitizer (100 query) pass exact ON/OFF parity, top-10 đầy đủ và CPU quan sát `[0,2]`. 100 query sanitizer khớp output của Release. TSan có trạng thái lịch sử `ENV_BLOCKED`. Giữ Historical P0, Full P1 và t0998 `HOLD`, V4 D1–D5 `UNAPPROVED`, P3 Official `CLOSED`, H3/TP-CG `NOT_OPENED`. Phạm vi thực chạy là Ryzen R2/R3 được giao. [P2 exploratory addendum](PROTOCOL_V4_1_P2_EXPLORATORY_0990_ADDENDUM.md)

## Quality gate

Beam lấy trực tiếp từ calibration Stage D chỉ dùng `val_10k`. Mỗi hàng dùng chung beam cho bốn phương án. Từng query khớp chính xác top-10 ID và squared L2 giữa các phương án trên `val_10k` và tập 3.000 query. Span validation giữa hai seed là 0,00002. LCB95 dùng `Recall − 1.96 × SE` với query làm đơn vị. Cổng validation yêu cầu LCB95 ≥ 0,990. Cổng pilot 3.000 query yêu cầu point Recall ≥ 0,990 và strict matched Recall trong seed. LCB95 của test được báo riêng.

| Seed | Beam | Val point | Val LCB95 | Test point | Test LCB95 | Δ Recall từ baseline trong seed | Gate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| R1 pilot, tập test cũ | 970 | 0,99131 | 0,99055 | 0,99037 | 0,98884 | 0,00000 | Point floor pass, lịch sử |
| R2 | 986 | 0,99132 | 0,99056 | 0,99103 | 0,98964 | 0,00000 | PASS exploratory |
| R3 | 966 | 0,99134 | 0,99056 | 0,99050 | 0,98902 | 0,00000 | PASS exploratory |

Top-10 và squared L2 của baseline mới trên cả 10.000 query khớp raw đã kiểm checksum của calibration Stage D trên từng seed. Tập mới khóa trước khi chạy, SHA-256 `77fda0316a8bb559c75e113ec3d750de0cf93403a11be474fc375c94c927c90b`. Cả 3.000 ID đều rời khỏi hai tập 3.000 ID của pilot B1/A1. Chúng thuộc `test_90k` từng dùng trong P1, do đó evidence là `EXPLORATORY_HOST_SPECIFIC`. A0-R1 disjoint vẫn **FAIL** tại 0,98940 với beam gốc. Hai LCB95 test mới dưới 0,990 đặt giới hạn cho chất lượng có thể khẳng định từ mẫu 3.000 query.

## Latency OFF và quyết định thống kê

40 process OFF hoàn tất, mỗi seed có 5 block ghép cặp, mỗi block đủ 4 phương án. Các lượt OFF đều khớp top-10 và squared L2 với lượt ON của cùng seed. Giữ toàn bộ lượt theo lịch đã khóa. Các cột Mean, p50 và p95 lấy trung bình của thống kê trong từng process, đơn vị µs/query. Δ là mean latency tiết kiệm được (`base − arm`). Mức giảm và speedup lấy trung bình trên tỷ lệ ghép cặp trong block. CI95 theo Student-t (`df=4`), `d_z` chuẩn hóa Δ theo độ lệch chuẩn giữa các cặp. R1 có hai baseline lịch sử riêng cho hai block ablation.

| Seed | Arm | Mean | p50 | p95 | Δ µs | Giảm mean % [CI95] | Speedup | d_z |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| R1 | Base cho B1 | 5.825,5 | 5.909,7 | 7.096,4 | — | — | — | — |
| R1 | B1 | 5.561,6 | 5.640,8 | 6.938,7 | 263,9 | 4,53 [1,22, 7,85] | 1,048× | 1,70 |
| R1 | Base cho A1/combo | 5.806,6 | 5.923,7 | 6.993,3 | — | — | — | — |
| R1 | A1 | 5.465,8 | 5.592,8 | 6.597,4 | 340,8 | 5,85 [3,61, 8,10] | 1,062× | 3,12 |
| R1 | B1+A1 | 5.133,6 | 5.280,1 | 6.265,4 | 673,0 | 11,58 [10,47, 12,69] | 1,131× | 10,61 |
| R2 | Base | 6.040,4 | 6.121,9 | 7.402,6 | — | — | — | — |
| R2 | B1 | 5.618,8 | 5.746,9 | 6.831,8 | 421,6 | 6,96 [4,95, 8,97] | 1,075× | 4,03 |
| R2 | A1 | 5.645,4 | 5.759,7 | 6.817,6 | 394,9 | 6,50 [3,15, 9,86] | 1,070× | 2,33 |
| R2 | B1+A1 | 5.296,2 | 5.435,1 | 6.475,0 | 744,2 | 12,29 [9,64, 14,94] | 1,141× | 5,26 |
| R3 | Base | 5.838,1 | 5.954,9 | 7.023,9 | — | — | — | — |
| R3 | B1 | 5.616,8 | 5.700,1 | 7.078,7 | 221,3 | 3,78 [0,61, 6,94] | 1,040× | 1,47 |
| R3 | A1 | 5.491,6 | 5.631,9 | 6.581,9 | 346,6 | 5,93 [4,72, 7,14] | 1,063× | 5,88 |
| R3 | B1+A1 | 5.249,3 | 5.359,2 | 6.542,6 | 588,8 | 10,08 [8,03, 12,13] | 1,112× | 6,00 |

Con số lịch sử 11,59% là `1 − mean(combo)/mean(base)` trên R1. Cùng cách tính cho R2 là 12,32%, R3 là 10,09%. Trong phân tích ghép cặp, CI95 tiết kiệm tuyệt đối của combo là [568,5, 919,9] µs trên R2 và [467,0, 710,6] µs trên R3. CI95 % của cả hai seed chứa mốc 11,59% và có cận dưới vượt 5%. Dữ liệu xác nhận gain trên từng seed quan sát, với hai ước lượng cách nhau 2,21 điểm phần trăm. Kiểm định tương đương với đúng mức 11,59% nằm ngoài thiết kế.

| Tập outer graph seed | B1, giảm mean % [CI95] | A1, giảm mean % [CI95] | B1+A1, giảm mean % [CI95] | Combo speedup [CI95] |
| --- | --- | --- | --- | --- |
| R2/R3, chính, `n=2` | 5,37 [−14,82, 25,55] | 6,22 [2,60, 9,83] | 11,19 [−2,84, 25,21] | 1,127× [0,947, 1,306] |
| R1/R2/R3, bổ sung exploratory, `n=3` | 5,09 [0,96, 9,21] | 6,10 [5,22, 6,97] | 11,32 [8,52, 14,12] | 1,128× [1,092, 1,164] |

Mỗi seed có trọng số bằng nhau. Khoảng chính dùng Student-t `df=1` và chứa 0. Khoảng bổ sung dùng `df=2` và đưa vào R1, seed đã dùng để chọn giả thuyết, với query cũ và hai baseline pilot. R2/R3 dùng chung query nên CI outer có điều kiện trên workload và host. Tiêu chí đã đăng ký yêu cầu combo đạt ≥5% và CI95 có cận dưới >0 trên từng seed, đồng thời CI95 outer chính có cận dưới >0. Vế outer chưa đạt, nên kết luận nghiên cứu là **HOLD**.

Combo cho mean thấp nhất trên từng seed mới. So với B1, combo nhanh hơn 5,74% [4,27, 7,21] trên R2 và 6,52% [4,31, 8,73] trên R3. So với A1, combo nhanh hơn 6,17% [4,15, 8,19] trên R2 và 4,41% [2,50, 6,32] trên R3. A1 riêng ổn định hơn B1 theo hai ước lượng seed. B1 có mean hơi thấp hơn A1 ở R2 và mean cao hơn A1 ở R3. Tương tác `combo − a1 − b1 + base` là +72,3 µs [−137,9, 282,6] trên R2 và −20,9 µs [−197,7, 155,8] trên R3. CI95 chứa 0 ở cả hai seed, nên lợi ích bổ sung ngoài tổng hai hiệu ứng riêng vẫn chưa xác định.

## Công thực hiện trong lượt ON riêng

Số liệu trung bình theo query trên tập 3.000 mới. `Merge` gồm phần chuẩn bị dispatch ở incremental. `Barrier` là tổng worker-wait. `Frontier` đếm chèn ứng viên phát sinh trong traversal. Seed dispatch chưa có counter trực tiếp trong binary đã khóa.

| Seed | Arm | L2 trùng | Merge (µs) | Barrier (µs) | Frontier insertions | Rounds |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| R2 | Base | 5.234,46 | 661,7 | 499,3 | 3.901,39 | 32,09 |
| R2 | B1 | 664,65 | 651,9 | 510,0 | 3.901,39 | 32,09 |
| R2 | A1 | 5.234,46 | 810,3 | 514,3 | 3.901,39 | 32,09 |
| R2 | B1+A1 | 664,65 | 794,5 | 471,5 | 3.901,39 | 32,09 |
| R3 | Base | 5.122,23 | 641,6 | 463,1 | 3.837,37 | 31,41 |
| R3 | B1 | 666,19 | 635,3 | 478,3 | 3.837,37 | 31,41 |
| R3 | A1 | 5.122,23 | 807,5 | 487,2 | 3.837,37 | 31,41 |
| R3 | B1+A1 | 666,19 | 778,1 | 464,6 | 3.837,37 | 31,41 |

B1 giảm khoảng 87% duplicate L2 ở hai seed. Mỗi lần tính lặp giảm đi tương ứng với một `already_seen_attempt` tăng lên. Số unique L2, expansions, frontier insertions và rounds giữ nguyên theo từng query. B1 công bố đầy đủ các node đã được tính L2 tại barrier đang có. Cách làm này xử lý recomputation xuyên round. Va chạm khám phá trong cùng round vẫn có thể xảy ra do worker chỉ nhận visited chung ở biên round.

A1 giới hạn mỗi round ở tối đa 32 seed dispatch và tránh chèn lại phần đuôi vào cây local. Theo số round quan sát, cận trên trung bình của seed dispatch A1 là khoảng 1.027/query trên R2 và 1.005/query trên R3. Chênh lệch seed dispatch thực tế chưa đo được. Cửa sổ merge ON thay đổi theo phương án, nên mức tăng của bộ đếm thời gian đó không tách được chi phí frontier. Các bước gộp tuần tự, đồng bộ và trùng nội round vẫn tồn tại trong kiến trúc hiện tại. Thí nghiệm này giữ cách phân việc và ranh giới đồng bộ cố định, nên chưa thể quy phần latency còn lại cho một cơ chế song song cụ thể. [Thiết kế và giới hạn counter](POST_STAGE_DE_AUDIT_AND_H3_PIVOT_PLAN.md)

## Kết luận về cơ chế

B1+A1 hiện là tối ưu của baseline P2. B1 tránh tính lại L2 xuyên round bằng cách công bố đầy đủ visited. A1 giảm seed dispatch dư trong cùng lịch đồng bộ. Mức giảm L2 trùng gần bằng nhau trên R2/R3, trong khi gain B1 riêng lần lượt là 6,96% và 3,78%. Phần còn lại có thể gồm overhead đồng bộ, gộp tuần tự, trùng nội round và chi phí triển khai chưa tách được. Kết quả này chưa cung cấp đối chứng để xác định tỷ trọng của từng nguồn hoặc cơ sở mở một cơ chế mới. Quyết định **HOLD** áp dụng cho mở rộng từ nghiên cứu hẹp này. H3/TP-CG giữ `NOT_OPENED`, Full P1 giữ `HOLD`, P3 Official giữ `CLOSED`.

## Telemetry và bằng chứng tái lập

88/88 lượt evaluator thoát 0 với 1.873 mẫu watchdog. Trong 40 lượt OFF có 846 mẫu, Tctl 74,0–88,6 °C và MemAvailable thấp nhất khoảng 6,81 GiB. Tctl cao nhất qua mọi phase là 89,1 °C. AC online ở mọi mẫu. Dữ liệu cpufreq lấy từ sysfs dao động khoảng 1,38–4,00 GHz trên CPU 0/2 qua mọi phase. `pswpin` tăng 0 page và `pswpout` tăng 1 page trong các khoảng lấy mẫu nội lượt. Telemetry thấy các burst của `msedge` (đỉnh 185% một core) và `ChatGPT` (131%) qua toàn bộ study, vì vậy các CI có điều kiện trên môi trường desktop quan sát được. Guard không phát hiện evaluator ANN cạnh tranh. Kiểm thử dataset-free sau benchmark thu 516 ca, 505 pass và 11 skip có điều kiện.

| Danh tính | SHA-256 |
| --- | --- |
| Pilot Release | `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1` |
| Pilot ASan+UBSan+LSan | `c3151165f23cffeec41d6ec508a2339b9eb7db627f708d470dcfc0b622c09ea7` |
| Package manifest V3 | `9094fb348269918077b37e901b887eae7ac1662c74a45aa43a237cd227e57d16` |
| Graph A3-R2 | `3d6113e721fa26c8a82f77d2e5bcbc60b6e55352532814694afb146c9c5f9c6c` |
| Graph A3-R3 | `11f7a5059af309db0a08c4a9e0484d194c8ea5c6f17d8c8f9f67ceb299d85829` |
| Frozen study | `526a0724f300f63f46c7d1baa27b6e8b0f3008c8e589c8e74432b50053e23cf9` |
| Raw `BUNDLE.sha256`, 713 tệp | `2b6677895dce4a274fd288f71e31e57b3051313e19b05f8cd12ce7022fae4ffe` |
| Export `CHECKSUMS.sha256` | `483804c96aefbe954693f615537aaebe8d059d59f4790ff8ae5f808331e52fb8` |

Checkpoint `COMPLETE` là trạng thái thực thi, còn `HOLD` là quyết định nghiên cứu. Bundle raw ghi JSONL theo query, JSON theo process, manifest guard, host samples, lệnh đầy đủ và checkpoint từng lượt. Export CSV raw có 144.000 hàng test ON/OFF. CSV process gồm 40 lượt R2/R3 và 25 lượt R1 lịch sử. `analysis.json` có CI95 của mean/p50/p95, effect sizes, paired speedup và telemetry. [Checkpoint](../../../../artifact-evidence/p2-b1-a1-narrow-20261119/checkpoint.json), [Study freeze](../../../../artifact-evidence/p2-b1-a1-narrow-20261119/frozen.json), [Raw bundle checksums](../../../../artifact-evidence/p2-b1-a1-narrow-20261119/BUNDLE.sha256), [Raw CSV](../../../../artifact-evidence/p2-b1-a1-narrow-analysis-20261119/raw_query_latency.csv), [Process CSV](../../../../artifact-evidence/p2-b1-a1-narrow-analysis-20261119/process_latency.csv), [Quality CSV](../../../../artifact-evidence/p2-b1-a1-narrow-analysis-20261119/quality.csv), [Analysis JSON](../../../../artifact-evidence/p2-b1-a1-narrow-analysis-20261119/analysis.json), [Export checksums](../../../../artifact-evidence/p2-b1-a1-narrow-analysis-20261119/CHECKSUMS.sha256)

Từ root repository, kiểm lại hai bundle và tái phân tích bằng lệnh dưới đây. Đường dẫn output tái phân tích phải mới.

```bash
raw=../artifact-evidence/p2-b1-a1-narrow-20261119
results=../artifact-evidence/p2-b1-a1-narrow-analysis-20261119
(cd "$raw" && sha256sum --strict -c BUNDLE.sha256)
(cd "$results" && sha256sum --strict -c CHECKSUMS.sha256)
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 research/task_da/analyze_b1_a1_narrow.py \
  "$raw" "${results}-verify"
```

Để tái đo phạm vi đã đăng ký trên Ryzen native, dùng source pilot và hai binary đúng SHA-256 từ bảng trên. Runner tạo evidence mới, thực thi theo thứ tự correctness, validation, test ON rồi timing OFF. Guard cần thấy PID namespace của host. Thư mục output phải chưa tồn tại.

```bash
evidence_parent=$(realpath ../artifact-evidence)
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -u research/task_da/run_b1_a1_narrow.py \
  "$evidence_parent/p2-b1-a1-narrow-new-run"
```
