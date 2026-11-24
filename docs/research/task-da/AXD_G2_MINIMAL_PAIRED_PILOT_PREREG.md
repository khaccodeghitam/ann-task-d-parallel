# A×D G2 · Minimal paired pilot preregistration

**VALIDATION_ONLY_LOCKED · TEST/OFF_NOT_AUTHORIZED, ngày 22/11/2026.** G1_RUNTIME_PASS trên sáu original graph, beam 384, p=2/S16 và 500 query. Stock r3 ở smoke đạt 0,9896 và cả sáu LCB95 smoke dưới 0,990. Pilot G2 phải qua calibration và quality gate riêng dưới đây. Bản này cụ thể hóa đề xuất A×D ngày 20/11. [G1 report](AXD_G1_RUNTIME_PARITY_REPORT.md) · [Kế hoạch gốc](AXD_JOINT_BUILD_SEARCH_GO_NO_GO_PLAN.md)

Câu hỏi là B1+A1 có giảm chi phí search trên Fast mới ở matched Recall, và Fast+B1+A1 có lợi ích BUILD–SEARCH tại workload đã khóa. Đối tượng là cohort cố định sáu MS-Turing-1M R90 P0A v1.3 H85, C160/K1024/N2, Stock/Fast × ba BUILD OFF. Root policy cùng seed ban đầu 555, independence NOT_VERIFIED. Đơn vị ngoài là file graph, mỗi graph có năm process pair. Nhãn evidence EXPLORATORY_HOST_SPECIFIC.

| Graph arm | D-base | D-opt |
|---|---|---|
| Stock r1/r2/r3 | flat, fixed-S, baseline/full | flat, fixed-S, barrier_all_evaled/incremental |
| Fast r1/r2/r3 | flat, fixed-S, baseline/full | flat, fixed-S, barrier_all_evaled/incremental |

Primary dùng p=2, S=16, jobs=1, K=10, entry=0, CPU [0,2], metric squared L2 double trên FP32 gốc, tie theo ID. Hai policy trong mỗi graph dùng cùng beam và cùng query order. Đồ thị được đọc PiPNN trực tiếp. Chỉ dùng đúng sáu SHA trong manifest đã nhận. [Manifest và đường dẫn graph](AXD_G1_GRAPH_ARTIFACT_MANIFEST.md)

| Danh tính khóa | Giá trị |
|---|---|
| Frozen search source | Commit `f2cd634b837a70735c3e31e5956f0524bfc26675` |
| Search ELF Release, cả hai policy/ON/OFF | SHA-256 `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1` |
| Task A source provenance | Commit `f5e48bb681812ce51aed7272f30ecefc85ed427b` và source_manifest SHA `5f42250caa47659daf978a73355857e355cc86096571d327518e676d41f1423b` |
| Highway | `6bc2d47793bae9c521fb4150936669647700765d` |
| Stock OFF builder ELF | SHA-256 `13bef65c01d4638959b16b74fc2b8b6130b433ebc09fff8f436c8b1503e688c9` |
| Fast OFF builder ELF | SHA-256 `fcfb16d0ca2b498f94db8383dfc311c2e7ba88cb3036281accd5f30c6d876793` |
| Base 1M×100 FP32 | SHA-256 `44e83e1dd4c65999b75873101adc5ac06ca900d259a2befd05c2c3aa28ff4042` |
| Query 100K×100 FP32 | SHA-256 `48d087a17bec15a5ec9ea526fe9bd14ac31bbbb5cd200817b341adbb77695644` |
| GT 100K×100, ID block rồi distance block | SHA-256 `fa5acf5ab262b42355296e99f920e6aa863f48820ca6f70fa37ca7966634c344` |

Compiler/flags/source hashes của ELF D giữ theo freeze, ghi lại ELF SHA và build receipt vào mỗi campaign. Ghi host, OS/kernel, CPU topology, allowed/requested/observed CPUs và package pin vào prereg receipt trước process đầu. Thay đổi binary hoặc graph phải trở lại review correctness/provenance.

| Panel | SHA-256 |
|---|---|
| `val_10k.ids` | `a3c948e9aac4f40c1fb818a6f784c4fbb56473a0769affe3344493ed4eb87f57` |
| `narrow_test_3000.ids` | `77fda0316a8bb559c75e113ec3d750de0cf93403a11be474fc375c94c927c90b` |
| `warmup_val_100.ids` | `199ca6066269641347280d6ef4eaab39efee3397b87c23cd74d38ee85bcd4783` |
| `smoke_val_500.ids` | `54f9eae4c2039f613fe63e2a27a40fadd7b498ab31f195f54fe7340d845ae9a6` |

Validation 10k và test 3k rời nhau. Test 3k đã dùng ở nghiên cứu narrow trước và public 100K đã được A search. Việc chọn beam G2 chỉ dùng validation. Giữ nguyên test panel và tên nhãn exploratory. 100 warmup là panel validation đã pin.

**Calibration validation-only đã được owner cho phép trong task hiện tại, khóa trước lượt đầu.** Trên từng graph, chạy D-base ON ở grid cố định 384,400,404,408,412,416,420,424,432 trên val_10k. Recall theo query là số ID trả về thuộc top-10 GT chia 10. Tính point, SE từ sample SD theo query và LCB95=point−1,96×SE. Giữ điểm có LCB95≥0,990. Chọn bộ sáu beam có span point≤0,0001, tối thiểu hóa max sai lệch khỏi 0,9913. Hòa thì chọn tổng beam nhỏ hơn, sau đó thứ tự từ điển Stock r1–r3/Fast r1–r3. Nếu không có bộ hợp lệ, HOLD ở grid đã đăng ký.

Khóa một beam/graph cho cả hai policy trước test. D-opt ON trên toàn val_10k phải khớp ordered top-10/L2² với D-base tại beam chọn, đầy đủ 10 ID duy nhất/query và qua logical counter invariants. Chạy hai policy ON trên test 3k. Mọi graph phải có point test≥0,990, span giữa sáu graph≤0,0001 và exact parity trong graph. Báo cả LCB95 test và paired ΔRecall theo query. Quality trượt giữ HOLD và bảo toàn kết quả.

**Paired OFF sau quality PASS.** Năm block, mỗi block có sáu cặp base/opt. Danh sách gốc là [Stock1,Fast1,Stock2,Fast2,Stock3,Fast3]. Block b=0..4 xoay trái danh sách b vị trí. Trong từng cặp, base trước opt khi (b+i) chẵn, với i là vị trí 0-based của graph trong danh sách gốc, còn lại opt trước base. Mỗi process có 100 warmup rồi 3.000 test query, jobs=1, cùng beam đã khóa. Chạy tuần tự dưới khóa chung, lưu toàn bộ lượt kể cả lượt chậm/lỗi. Mỗi output OFF phải khớp query/ordered top-10/L2² của ON tương ứng. Một parity/guard failure dừng campaign và giữ HOLD, bảo toàn partial receipts.

Budget đề xuất gồm 54 base validation ON, 6 opt validation ON tại beam chọn, 12 test ON và 60 process OFF. Quota 3 giờ máy tuần tự gồm cooldown, dừng khi hết quota. G1 đã có receipt riêng. Phạm vi chính là sáu graph và hai policy tại p=2/S16.

**Endpoint và inference.** Tính mean, p50, p95 trong từng process từ per-query latency OFF theo định nghĩa percentile của frozen evaluator. Với graph g và block b, lấy B_gb/C_gb là mean base/opt. Chênh latency là B_gb−C_gb, gain là 100×(1−C_gb/B_gb). Báo từng graph, năm hiệu số và CI95 Student-t df=4. QPS batch thực nếu xuất được tính queries/batch_wall, kèm jobs=1.

Đối với kết luận trên cohort cố định, mỗi block đóng góp mean đồng trọng số của sáu graph, hoặc ba Fast khi endpoint dành cho Fast. CI95 chính dùng năm block, df=4, có điều kiện trên cohort, query và host. Báo cả ba điểm graph Fast và phạm vi giữa BUILD. CI qua ba graph có thể báo thêm với giả định exchangeability ghi rõ. CI quần thể independent root là NOT_ESTIMABLE khi chưa có receipt root độc lập. Query count và process repeat không làm tăng số graph. Stock-r1 và Fast-r1 có cùng số thứ tự, còn pairing chính là base/opt trên chính graph đó.

Tail endpoint trên Fast dùng 100×(p95_opt/p95_base−1) theo từng graph/block, đồng trọng số qua ba graph trong block rồi CI t qua năm block. Báo cả từng graph để thể hiện heterogeneity.

ON work được chấm từ test ON riêng, gồm total/unique/duplicate L2, expansions, frontier insertions và rounds. Dùng accounting và B1/A1 invariants frozen. Các timer merge/worker-wait được trình bày theo đúng cửa sổ quan sát, kèm đơn vị.

BUILD dùng receipt của chính sáu SHA đã search. BUILD mean Stock/Fast hiện là khoảng 42,2567/33,7933 s, ΔB≈8,4633 s. Với Q₀=100.000 query nối tiếp/index, T(Q)=BUILD+Q×mean_OFF_query. Với Stock-base, Fast-base và Stock-opt, tính trực tiếp ΔT so với Fast-opt bằng giây. Báo Q=1, Q₀ và điểm hòa vốn dương nếu có. CI ΔT trong pilot điều kiện trên BUILD đã quan sát, biến thiên từ paired block search. Host dựng A và host search D tạo một mô hình triển khai hai host, với chi phí chuyển/nạp báo riêng. BUILD% và SEARCH% giữ là hai endpoint riêng.

**Guard/resource.** AMD Ryzen 5 PRO 4650U, CPU 0/2 trên hai core vật lý cùng L3. Preflight thermal/AC/RAM/disk/swap/foreign process và heartbeat watchdog phải hoạt động. Dùng guard Ryzen frozen, từ chối start Tctl≥85°C, dừng ở ≥95°C hoặc critical trip/AC/resource/heartbeat failure. Ghi sensor validity, CPU quan sát, telemetry, memory high-water, peak RSS, disk/index bytes và competing process samples. Giữ cấu hình host của lượt được duyệt, ghi nhận môi trường đo thực tế. Capture compiler/ELF identity và full argv từng process.

| Quyết định đề xuất chờ owner khóa | Điều kiện |
|---|---|
| GO_AxD, cohort đã đo | Mọi provenance/parity/quality/guard gate PASS, cả ba Fast có mean opt thấp hơn base, mean Fast gain≥5% và CI95 conditional có cận dưới>0, ΔB>0, ΔT(Q₀) vs Stock-base có cận dưới>0, Fast-opt có ΔT ước lượng dương so với cả Fast-base và Stock-opt, upper CI95 của tăng p95 Fast vs Fast-base≤5% |
| HOLD | Quality/provenance/parity/guard/quota trượt, thiếu cặp, hoặc bất định còn bao cả lợi ích đáng kể và vô ích |
| PIVOT_TO_TASK_A | Pilot hợp lệ và BUILD/quality có lợi, trong khi upper CI95 Fast gain<5% hoặc lower CI95 của tăng p95>5% |

Pha validation-only được phép trong task hiện tại theo khóa thực thi dưới đây. Held-out test và paired OFF cần authorization tiếp theo. Phần timing G2 hiện NOT_OPEN. Historical P0/Full P1/t0998/B1+A1 HOLD, P3 official CLOSED, V4 D1–D5 UNAPPROVED, H3/TP-CG NOT_OPENED. [Readiness](AXD_G2_PREREG_READINESS.md)


**Khóa thực thi cho task quality calibration ngày 22/11/2026.** Chạy tối đa 54 process baseline ON (6 graph × 9 beam) và chỉ khi có bộ sáu beam hợp lệ mới chạy tối đa 6 process B1+A1 ON trên validation 10k tại các beam đã chọn. Giữ nguyên grid [384,400,404,408,412,416,420,424,432], p=2/S16, flat, entry=0, K=10, jobs=1, CPU [0,2]. Một process nhận một beam, 100 warmup validation và 10.000 validation queries. Budget tối đa 600.000 query được chấm + 6.000 warmup, 60 process, timeout 180 giây/process, quota tổng 3 giờ kể cả cooldown. Mọi process chạy tuần tự dưới guard Ryzen và khóa chung.

Giữ estimator LCB95=mean−1,96×SE theo query đã đề xuất. Dùng query làm đơn vị, mỗi query có recall là số hit trong top-10 GT chia 10. SE dùng sample variance/n. Đây là LCB chuẩn xấp xỉ danh nghĩa tại từng điểm, có điều kiện trên graph và sampling của panel. Việc chọn trong chín beam trên cùng validation làm khoảng tại beam chọn mang tính calibration. Test ở pha sau mới kiểm tra cấu hình khóa. Giữ nguyên floor 0,990 và span 0,0001. Target 0,998 CLOSED trong task này.

Validation/test rời nhau theo query ID. Test 3k đã quan sát trong P1 và narrow B1+A1, cả 100k từng được Task A search. Test tương lai được giữ khỏi việc chọn beam của campaign hiện tại và mang nhãn EXPLORATORY_HOST_SPECIFIC. Chưa có panel xác nhận unseen trong package hiện tại. Kiểm tra lịch sử này không chuyển split exploratory thành một test xác nhận độc lập.

Báo từng graph/policy, point, SE, LCB95 và N. Với uncertainty cấp cohort cố định, dùng mean recall của sáu graph trong từng query rồi lấy SE trên 10k query, giữ tương quan do dùng chung panel. Báo cả min/max giữa graph. CI quần thể independent-root NOT_ESTIMABLE khi root independence chưa được chứng minh.

Nếu không có điểm qua LCB cho một graph hoặc không có bộ sáu beam qua matching, dừng ở HOLD_QUALITY, ghi toàn bộ grid. Nếu có bộ hợp lệ, chạy B1+A1 trên đúng beam đã chọn và kiểm exact ordered IDs/L2² cùng logical counters theo freeze. Bất kỳ mismatch/correctness/guard/quota failure giữ HOLD và lưu raw. Chọn beam theo validation, test IDs không được truyền vào evaluator trong task này. Dừng sau báo cáo calibration và quality/test gate.
