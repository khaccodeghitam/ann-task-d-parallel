# A×D · Kiểm toán G1 và điều kiện mở pilot BUILD–SEARCH

**Ngày 22/11/2026, G0 PASS trên R90 P0A v1.3. G1 PASS ở mức hợp đồng định dạng, BLOCKED ở runtime. G2 chưa mở.** Task A đã chạy Search/Recall trên đúng 18 graph OFF mà đề xuất v2.0 yêu cầu. Đã nối được full SHA-256 của từng graph từ BUILD đến kết quả Search. Chọn **sáu graph MS-Turing-1M v1.3, Stock và Fast v2, mỗi arm ba lần BUILD OFF**. Artifact còn thiếu cho G1 là **bytes của sáu graph đó** để D tự băm, nạp và kiểm parity. [Đề xuất v2.0, §IV.1–2 và VII][v2] · [Kế hoạch A×D, §2–3](AXD_JOINT_BUILD_SEARCH_GO_NO_GO_PLAN.md) · [Manifest Search gốc của A][screen]

## 1. Cohort và bằng chứng mới

Đã đọc trực tiếp sổ Task A ngày 22/11, kiểm lại danh mục lúc 11:08 UTC, có 102 tab. Dòng 6 của tab native 24 còn mô tả thời điểm vừa xong BUILD. Dòng 60–61 đã cập nhật Search, dẫn đến các tab fixed, matched và final. Đối chiếu với JSON native tại commit Task A `64b7d147ecff7d637be78abdf77e7f56358c5fac` giải quyết được khác biệt giữa snapshot ngày 20/11 và trạng thái hiện tại. [Native 24, dòng 52–61][native] · [Tổng kết v1.3][final-a]

| Cohort | Bằng chứng trên chính cohort | Quyết định A×D |
|---|---|---|
| **R90 P0A v1.3 H85, MS-Turing-1M** | Cùng recipe, 3 Stock + 3 Fast OFF, H17 có thêm 3 OFF. Mean BUILD Stock/Fast là 42,257/33,793 s. Cả 9 graph MS đạt Recall@10 ≥0,990 tại beam 384 và ≥0,998 tại 896 trên 100.000 query. Có cả calibration và Search lặp theo ngưỡng. [BUILD][build] · [Fixed][fixed] · [Matched][matched] | **Chọn cho thiết kế 2×2**. Đủ ba invocation/arm và giữ đúng đối chứng Stock/Fast của v2.0. H17 là arm tùy chọn. |
| **R91 G2A2, MS-Turing-1M** | 12 BUILD cùng phiên, 4 CPU, Stock/Fast × G2A1/SketchOnly/SketchLocks × 2 lần. Cả 12 qua audit cấu trúc và fixed-beam 100KQ, đạt 0,990 tại 384 và 0,998 tại 896. Full manifest SHA-256 `c9ba8bc6b885a688c111978d8f5203f571806905736ee13577c7ff5016250940` theo sổ A. Mỗi graph có một invocation Search. [BUILD 12][r91build] · [FULL sau cả R1 và R2][r91full] | Bằng chứng riêng cho các thay đổi bộ nhớ. Chọn một variant chỉ còn 2 lần/arm. Gộp các variant sẽ thay đổi phép so sánh. Chưa có matched-Recall lặp cho cohort này. |
| **R91 G2A3 mới nhất** | Audit source, patch và compile 4 ELF đã qua. Tab cuối ghi 8/8 BUILD SIFT100K/1 CPU cho cùng SHA. Ma trận MS-Turing-1M/4 CPU × 12 mới có gói chạy, Search trên các graph đó là bước sau. [Audit][r91audit] · [Patch][r91patch] · [Compile][r91compile] · [100K và trạng thái 1M, dòng 31–38][r91last] | Chưa có cohort G2A3 1M kèm quality. |
| **R91 G1M-D, 10M** | Có paired QPS trên một Stock và một Fast ở 10M. [Pilot 10M][r9110m] | Khác kích thước và số lần dựng. Nằm ngoài phép thử 1M. |

**G0 đã hoàn tất ở phạm vi Search/Recall native của A.** Kiểm đủ 24 dòng BUILD, tách 6 ON/1 CPU. Trên 18 OFF/4 CPU, khóa nối là dataset, arm, rep **và đủ 64 hex SHA-256**. Cả 18 khớp qua manifest BUILD, audit cấu trúc, prereg Search, fixed-screen receipt, calibration và ba receipt timing/graph. Tổng cộng 63 điểm Recall fixed, 18 lượt calibration, 54 lượt timing và 108 quan sát theo target. Chín graph SIFT cũng qua hai floor tại 80/160 trên 10.000 query. Trên MS, calibration chọn beam 368 cho cả ba arm tại floor 0,990, và 880/864/864 cho Stock/H17/Fast tại 0,998. Receipt A ghi số query, SHA stdout và Recall gộp theo beam. Kiểm đủ 10 ID duy nhất theo từng query trên engine D thuộc G1. Matched Recall, top-10 parity và latency của D trên sáu graph vẫn chưa đo. [Manifest BUILD][build] · [Screen][screen] · [Calibration][cal] · [Timing][timing] · [Kết quả theo ngưỡng][matched]

## 2. Graph, source và workload đã định danh

Mỗi dòng dưới đây là một file gốc trong `experiments/R90/r90_p0a_v13_h85_24build_native_v1/graphs/` trên máy Task A. Số cạnh lấy từ audit của A. Recall lấy trực tiếp từ manifest native ở độ chính xác ghi trong JSON. Đã kiểm checksum của manifest. Việc băm lại **nội dung file graph tại D** còn chờ bàn giao. [Audit cấu trúc][struct] · [Receipt theo graph][screen]

| File cần bàn giao | SHA-256 của graph theo BUILD và Search | Cạnh có hướng | R@10 · 384 | R@10 · 896 |
|---|---|---:|---:|---:|
| `MS-Turing1M_stock_off_r1.graph` | `db4f5257f06d7ca6df0a040d19590d201bc3e9b1eab7bf0f36265732969716cc` | 52.828.429 | 0,99109298 | 0,99819601 |
| `MS-Turing1M_stock_off_r2.graph` | `5de325e9bbb0b46208c4878b3af77ae79c7c1821096eb11064efab5c15d0ae84` | 52.853.377 | 0,99099100 | 0,99814701 |
| `MS-Turing1M_stock_off_r3.graph` | `a7eb1ad15ff31130ce8411169f19b41d9bde75577ad5b5416e1b53a90ecbd010` | 52.858.025 | 0,99106097 | 0,99819303 |
| `MS-Turing1M_fast_off_r1.graph` | `104a1bc69711e494dbf562772b867752dd915e53ff7ed4142763cdc98fb354e9` | 52.849.553 | 0,99112803 | 0,99818999 |
| `MS-Turing1M_fast_off_r2.graph` | `4b69a53c548cdb47714902c2201fe732daf668683056aae9efa724982e11731a` | 52.857.274 | 0,99106300 | 0,99820000 |
| `MS-Turing1M_fast_off_r3.graph` | `7c80157e8165e2792151e4934078fd7bd2fa2deebad2ad9864ba6aaf24da0462` | 52.865.107 | 0,99103701 | 0,99819100 |

**Construction.** Đã băm 18 GNU-time receipt OFF, đối chiếu từng digest với manifest BUILD và đọc argv. Cùng CPU 0,2,4,6, `-num_clusters 2 -cluster_size 1024 -table_size 160 -top_level_leaders 100 -fanout_scheme 10,3,1 -mst_deg 2 -prune 1 -prune_all 1 -prune_degree 64 -hash_bits 12 -alpha 1.1 -k 0`. C160 là sức chứa bảng khi dựng, K1024 là kích thước cluster, N2 là số vòng cluster. Degree cap của graph xuất ra là 64. Stock dùng Highway, H17 dùng packed top-2, Fast v2 thêm FP32 prefilter vào H17. [Receipt argv mẫu][argv] · [Source manifest][source] · [Compile provenance][compile]

| OFF builder | SHA-256 của source tree theo manifest A | SHA-256 của ELF trong receipt BUILD |
|---|---|---|
| Stock | `236222ce948678bcf230686bb2e5957995f28ac813fe445fcb991d5bcf83e1f9` | `13bef65c01d4638959b16b74fc2b8b6130b433ebc09fff8f436c8b1503e688c9` |
| Fast v2 | `de97c4d9020eb2de9fbdab6051fd01f40d6f6e960ff8a75e08ce8545a49bb25c` | `fcfb16d0ca2b498f94db8383dfc311c2e7ba88cb3036281accd5f30c6d876793` |
| H17, tùy chọn | Như Stock, bật `R71_H17_TOP2` lúc biên dịch | `be9feed5e618587f2d153fcaf7d7284279ae8ed4173c2e3796104058b8e4b22e` |

H85 Highway ở commit `6bc2d47793bae9c521fb4150936669647700765d`, GCC 13.3.0 có SHA-256 `1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769`. Mỗi ELF có digest của `compile_commands` theo arm. Với clustering, source đúng v1.3 khởi tạo `SEED=555`, cập nhật qua `parlay::hash64` giữa các vòng. `SketchHash` dùng seed mặc định 0. Argv BUILD không truyền seed theo rep. Có ba invocation bốn luồng dùng chung chính sách seed. Độc lập thống kê giữa các lần dựng là **NOT_VERIFIED**. Số thứ tự r1/r2/r3 không xác lập ghép cặp root giữa hai arm. [Source clustering][cluster] · [SketchHash][hash] · [Compile provenance][compile]

| Input MS-Turing | Header (hàng × chiều/rộng) | Byte tại D | SHA-256 của file tại D, khớp prereg A |
|---|---:|---:|---|
| `base.1M.fbin` | 1.000.000 × 100 | 400.000.008 | `44e83e1dd4c65999b75873101adc5ac06ca900d259a2befd05c2c3aa28ff4042` |
| `query.public.100K.fbin` | 100.000 × 100 | 40.000.008 | `48d087a17bec15a5ec9ea526fe9bd14ac31bbbb5cd200817b341adbb77695644` |
| `groundtruth.public.100K.ibin` | 100.000 × 100 | 80.000.008 | `fa5acf5ab262b42355296e99f920e6aa863f48820ca6f70fa37ca7966634c344` |

Evaluator MS của A là R86 highbeam v4, source SHA-256 `6aa0e38a3b0a536ccbcd3bfe0ca690257ab963215b5135d642cbb60d259c3f89`, ELF `bb6576ad3e1e0cc770535aa06355c664993ca70bd1170d6dd4d202ab5767e144`. Đã băm bản source/ELF có tại D và khớp pin của A. D dùng một ELF Release B1+A1 cho base/opt và ON/OFF, SHA-256 `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1`. [Prereg Search và input A][inputs] · [Evaluator A][eval-a] · [Pins B1+A1 tại D](../../../../artifact-evidence/p2-b1-a1-narrow-20261119/frozen.json)

## 3. Điều kiện READY / PENDING / BLOCKED

| Điều kiện | Trạng thái | Bằng chứng hoặc phần còn thiếu |
|---|---|---|
| G0 · kết quả A gắn với SHA | **READY · PASS** | 18/18 OFF, đúng hai dataset và ba arm. SHA khớp từ BUILD tới Search, có recipe, source tree, compiler, ELF và chính sách root. |
| Node ID và vector indexing | **READY · tĩnh** | Builder tạo ID `0..n−1`, xuất hàng `G[i]` cho `Points[i]`. D truy cập hàng `i` tại offset `i × d`. FBIN có header LE-u32, payload float32 row-major, D kiểm kích thước và giá trị hữu hạn. |
| Adjacency và edge semantics | **READY · tĩnh** | Writer Stock/Fast cùng blob Git `a499d389fa0fe4f3bb1cfa983aaac59423537830`. Layout LE-u32 là `n, max_degree, degrees[n], neighbors[]`. Mỗi hàng chứa đích của các cung đi ra theo thứ tự ghi. D giải mã trực tiếp sang CSR, bảo toàn hướng, thứ tự, bội số, self-loop và hàng rỗng. A báo 24/24 audit đủ hàng, cả ba số đếm (ID ngoài miền, self-loop, hàng có neighbor trùng) đều bằng 0. [Writer][writer] · [Loader D][loader] |
| Entry | **READY · tĩnh** | PiPNN không lưu entry trong file. Evaluator MS của A gọi `random=false, start_point=0, k=10`. D truyền `entry=0` nhất quán cho hai policy. Directed reachability từ 0 trên từng file v1.3 tại D còn chờ bytes. [Evaluator A][eval-a] · [Hợp đồng D](graph_format_contract.md) |
| Distance, GT và Recall | **READY · hợp đồng** | Cùng squared L2 trên FP32. Source evaluator A dùng tích lũy float và cho phép ID đồng khoảng cách với hạng 10 trong GT. D tích lũy double, xếp theo `(L2², ID)` và chấm bằng giao với đúng 10 ID đầu. IBIN lưu toàn bộ ID u32 rồi toàn bộ distance f32. D dùng query ID để lấy đúng hàng GT. Điểm native A qua floor chỉ đóng G0. [Recall A][recall-a] · [Hợp đồng D](graph_format_contract.md) |
| Direct loader / converter | **READY · source và fixture** | Đường chính là đọc PiPNN gốc. Freeze đã PASS PiPNN → NSG → PiPNN byte-exact, so từng hàng + entry và ON/OFF trên fixture. Có precedent kiểm cấu trúc chín graph R86 ở entry 0. Các receipt này có danh tính riêng. [Kiểm thử format](GRAPH_COMPATIBILITY_REPORT.md) · [Đối soát R86](P0_P1_FINAL_RECONCILIATION_REPORT.md) |
| Graph files Stock/Fast · 3 + 3 | **BLOCKED · 0/6 tại D** | Kho bàn giao `../../graph/experiments/` (tính từ gốc checkout D) có 9 file R86 A0/A1/A3. Mirror Task A loại `*.graph` và archive graph. Kích thước dự kiến của 6 file là **1.292.447.108 byte** theo công thức format và số cạnh. [Chính sách mirror][mirror] |
| H17 · 3 OFF MS | **READY · G0**, **PENDING · tùy chọn** | Có full SHA và Recall theo graph trong manifest. Chỉ cần bytes H17 nếu owner đưa arm này vào phạm vi. [Manifest Search][screen] |
| Split, engine và kết quả D | **READY · pins**, **BLOCKED · G1 runtime** | Đã kiểm 23/23 pin narrow, gồm ELF và split. 500 ID smoke đúng 500 ID đầu của validation 10k, validation và test 3k rời nhau. Còn thiếu receipt nạp, kiểm hàng/entry, top-10 và L2² trên **sáu graph v1.3**. |
| Beam, matched quality trên D và quyền chạy | **PENDING** | Chưa chọn beam trên validation của từng graph mới, chưa có D test quality và phê duyệt chạy pilot. |
| G2 · pilot p2 | **BLOCKED** | Điều kiện mở là G0 + G1 PASS trên cohort đã chọn và owner duyệt prereg. Quality gate dưới đây đứng trước mọi timing. |

## 4. Gate correctness/parity nhỏ nhất trước benchmark

1. **Bàn giao sáu file bất biến ở §2.** Kiểm full SHA từng file, header `(1.000.000, 64)`, từng degree, miền ID, số cạnh và độ dài `8 + 4n + 4m`, hết file đúng vị trí. Đọc độc lập các hàng có thứ tự, ghi digest canonical `LE32(n)` rồi `LE32(id, degree, neighbors…)` cho từng hàng, header max, entry và số đỉnh đến được bằng BFS có hướng từ 0. Nếu phải đổi container, đối chiếu từng hàng byte-for-byte, entry, declared max và round-trip. Đường nạp trực tiếp đã có nên không cần tạo bản chuyển để chạy gate. [Audit reader](../../../research/task_da/graph_audit.py) · [Hợp đồng](graph_format_contract.md)
2. **Smoke trên validation, chỉ xét correctness.** Giữ cả sáu graph. Dùng 500 ID đã khóa, SHA-256 `54f9eae4c2039f613fe63e2a27a40fadd7b498ab31f195f54fe7340d845ae9a6`. Một beam định trước trong grid (đề nghị 384 cho smoke), `p=2, S=16, jobs=1, flat, K=10, entry=0`. So `baseline/full` với `barrier_all_evaled/incremental`, mỗi policy ON và OFF, cùng ELF và cùng graph. Có thể kiểm Stock r1 trước để phát hiện lỗi nạp sớm. G1 PASS cần đủ 24 invocation correctness theo kế hoạch, dưới guard trên Ryzen đã được duyệt. Mỗi query phải trả đủ 10 ID khác nhau trong miền, cùng thứ tự query, cùng top-10 **theo thứ tự** và cùng L2² cho bốn output. Tính L2² độc lập trên các ID trả về của một mẫu khóa trước để kiểm mapping, kiểm Recall theo đúng hàng GT và invariants ON của B1/A1. Khi có sai khác, dừng ở G1 và lưu receipt lỗi. [Gate đã đề xuất, §3](AXD_JOINT_BUILD_SEARCH_GO_NO_GO_PLAN.md) · [Invariants freeze](B1_A1_PILOT_HANDOFF_20261119.md)
3. **Mở G2 có điều kiện.** Sau G1 PASS và owner duyệt prereg metric, grid beam, ngưỡng, lịch ghép cặp, host và quota, mới mở phần quality của G2 trên Ryzen 5 PRO 4650U có guard. Chọn một beam/graph dùng cho cả hai policy, chỉ trên `val_10k`, theo grid đã đề xuất. Validation LCB95 từng graph ≥0,990 và span point giữa sáu graph ≤0,0001. Khóa beam trước test. Kiểm base/opt khớp trên toàn validation và test ON. Trên 3.000 test ID đã khóa, từng graph phải đạt point Recall ≥0,990, span ≤0,0001 và đủ output, báo cả LCB95. Chỉ mở timing OFF sau khi các điều kiện này đạt. Nếu trượt, giữ beam/panel và dừng trước timing. [Kế hoạch, §3 và §5](AXD_JOINT_BUILD_SEARCH_GO_NO_GO_PLAN.md)

## 5. Dấu vết kiểm toán và freeze

Đã băm lại các JSON gốc ở commit Task A nêu trên và kiểm liên kết SHA bên trong. Các digest chính để tái kiểm là `5f42250caa47659daf978a73355857e355cc86096571d327518e676d41f1423b` (source manifest), `81dd161594fb92c8dc3c8bea54c004afdbdc6f7ba71d8ed5b187ecd01d64d89e` (compile), `0c76f3e5bc3dc0d82f70aa1aadac9b26c5b0e8f4607f31d9aa6d8b0b0a4121c3` (BUILD), `9550858dcb763349ed5180b3b65577e48a600e54becc0ecb9c755970a4d4bbfb` (structure), `767c8b95dcf9f2e91bb06612b1c0d82ee9814ea3e6b220cd755601705a1738ed` (fixed Search) và `861c8734cab66a6d2dcbcee9aca56a981ab364ea7e14e04e64e9177bf3ddd7a7` (fixed summary). DOCX v2.0 ngày 20/11 đọc từ bản tải về có SHA-256 `9641dae30d1fb1c521b5c24ec7675a3cc650c7886e5a95423338ea4107afe23e`. [BUILD][build] · [Search][screen] · [Summary][screen-summary] · [Đề xuất][v2]

Task D ở branch `research/task-da-pivot-b1-a1-20261119`, HEAD `f54b1bb653652dd13e760cc00c9fb46d0e643c1c`. Đầu lượt, staged diff và tracked diff rỗng. Bốn tài liệu chưa track sẵn là `AXD_JOINT_BUILD_SEARCH_GO_NO_GO_PLAN.md`, `TASK_D_FINAL_GO_PIVOT_DECISION.md`, `TASK_D_SIX_CRITERIA_EVIDENCE_SCORECARD.md` và `TASK_D_TEAM_DIRECTION_COMPARISON.md`. Đã kiểm đích tag B1+A1 `f2cd634b837a70735c3e31e5956f0524bfc26675`, Stage D/E `87d4a8149416b22ccf8854f72c7c72f09197cfa3`, 11 digest manifest freeze và 23 payload pin của narrow study. Chỉ thêm báo cáo này. Không chạy evaluator, BUILD, benchmark latency hay thí nghiệm thay thế. Historical P0, Full P1, t0998 và B1+A1 giữ **HOLD**, Protocol V4 D1–D5 **UNAPPROVED**, P3 official **CLOSED**, H3/TP-CG **NOT_OPENED**, i5-14600KF **NOT_RUN**. [Chỉ mục freeze](TASK_D_FINAL_REPRODUCIBILITY_INDEX.md) · [Review B1+A1](B1_A1_POST_REPLICATION_REVIEW_20261119.md)

[v2]: https://docs.google.com/document/d/1QeCLkvaUOu9UkJRcQfXEzi-B8D_9ZMff/edit
[native]: https://docs.google.com/spreadsheets/d/12ApqgMV8YykflyFXUT2VMbUhgyiGirtoOmRWCXCz3Ek/edit#gid=1711192618&range=A52:L61
[fixed]: https://docs.google.com/spreadsheets/d/12ApqgMV8YykflyFXUT2VMbUhgyiGirtoOmRWCXCz3Ek/edit#gid=1711192619&range=A54:I71
[matched]: https://docs.google.com/spreadsheets/d/12ApqgMV8YykflyFXUT2VMbUhgyiGirtoOmRWCXCz3Ek/edit#gid=1711192620&range=A1:M22
[final-a]: https://docs.google.com/spreadsheets/d/12ApqgMV8YykflyFXUT2VMbUhgyiGirtoOmRWCXCz3Ek/edit#gid=1711192621
[r91build]: https://docs.google.com/spreadsheets/d/12ApqgMV8YykflyFXUT2VMbUhgyiGirtoOmRWCXCz3Ek/edit#gid=1711212619
[r91full]: https://docs.google.com/spreadsheets/d/12ApqgMV8YykflyFXUT2VMbUhgyiGirtoOmRWCXCz3Ek/edit#gid=1711212621&range=A1:G21
[r91audit]: https://docs.google.com/spreadsheets/d/12ApqgMV8YykflyFXUT2VMbUhgyiGirtoOmRWCXCz3Ek/edit#gid=1711212622
[r91patch]: https://docs.google.com/spreadsheets/d/12ApqgMV8YykflyFXUT2VMbUhgyiGirtoOmRWCXCz3Ek/edit#gid=1711212623
[r91compile]: https://docs.google.com/spreadsheets/d/12ApqgMV8YykflyFXUT2VMbUhgyiGirtoOmRWCXCz3Ek/edit#gid=1711212624
[r91last]: https://docs.google.com/spreadsheets/d/12ApqgMV8YykflyFXUT2VMbUhgyiGirtoOmRWCXCz3Ek/edit#gid=1711212625&range=A31:G38
[r9110m]: https://docs.google.com/spreadsheets/d/12ApqgMV8YykflyFXUT2VMbUhgyiGirtoOmRWCXCz3Ek/edit#gid=1711212606
[mirror]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/README.md
[source]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/experiments/R90/r90_p0a_v13_historical_highway_6bc2_controlled_v1/source_manifest.json
[compile]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/experiments/R90/r90_p0a_v13_historical_highway_6bc2_controlled_v1/compile_provenance_audit.json
[cluster]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/experiments/R90/r90_p0a_v13_historical_highway_6bc2_controlled_v1/source/stock_off/algorithms/PipNN/pipnn.h
[hash]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/experiments/R90/r90_p0a_v13_historical_highway_6bc2_controlled_v1/source/stock_off/algorithms/utils/hash.h
[writer]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/experiments/R90/r90_p0a_v13_historical_highway_6bc2_controlled_v1/source/stock_off/algorithms/utils/graph.h#L271-L295
[argv]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/experiments/R90/r90_p0a_v13_h85_24build_native_v1/logs/MS-Turing1M_stock_off_r1.time
[build]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/experiments/R90/r90_p0a_v13_h85_24build_native_v1/full1m_manifest.json
[struct]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/experiments/R90/r90_p0a_v13_h85_24build_native_v1/audit1m_buildonly.json
[inputs]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/experiments/R90/r90_p0a_v13_h85_18graph_quality_screen_v1/preregister.json
[screen]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/experiments/R90/r90_p0a_v13_h85_18graph_quality_screen_v1/full_manifest.json
[screen-summary]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/experiments/R90/r90_p0a_v13_h85_18graph_quality_screen_v1/quality_screen_summary.json
[cal]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/experiments/R90/r90_p0a_v13_h85_matched_threshold_repeat_1m_v1/calibration_manifest.json
[timing]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/experiments/R90/r90_p0a_v13_h85_matched_threshold_repeat_1m_v1/timing_manifest.json
[eval-a]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/experiments/R86/msturing_1m_eval/r86_msturing1m_graph_recall_v4_highbeam.cc
[recall-a]: https://github.com/nuyntai19/ann-task-a-research/blob/64b7d147ecff7d637be78abdf77e7f56358c5fac/experiments/H70/pipnn-clean-443a328/algorithms/utils/check_nn_recall.h#L59-L111
[loader]: https://github.com/khaccodeghitam/ann-task-d-parallel/blob/f2cd634b837a70735c3e31e5956f0524bfc26675/research/task_da/search_common/engine.hpp#L42-L95
