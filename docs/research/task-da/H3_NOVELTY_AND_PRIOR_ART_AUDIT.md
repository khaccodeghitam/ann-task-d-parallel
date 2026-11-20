# H3 — Novelty and prior-art audit

Ngày kiểm toán: **2026-11-20**. Phạm vi: đọc tài liệu, source và evidence; không triển khai H3, chạy search/benchmark, dựng graph hay dùng i5-14600KF.

**Quyết định: original TP-CG dynamic scheduling = PIVOT; overlap-aware frontier assignment = MORE EVIDENCE. H3 vẫn NOT_OPENED.** Chưa xác lập đóng góp thuật toán khác biệt. Việc gom seed có láng giềng chung dưới ràng buộc cân bằng đã có một mô hình hypergraph trực tiếp; chữ ký bit và heuristic đổi chỗ tự chúng chưa tạo novelty.

## 1. Freeze và baseline được bảo toàn

Đã đọc [Research Philosophy](../../../RESEARCH_PHILOSOPHY.md), [Start Here](../../START_HERE.md), ba tài liệu tiếp nối và source P2. Điểm bắt đầu là branch `research/task-da-pivot-b1-a1-20261119`, HEAD `40bb7c54017f3ea21d6f1a5fd2fbbe920b3d2e1e`. Git chỉ có hai tệp untracked có sẵn: post-replication review và preregistration R4/R5. Không có tracked modification lúc bắt đầu.

| Kiểm tra lại bytes hiện diện trong lượt này | Kết quả |
| --- | --- |
| Narrow raw `BUNDLE.sha256` | 713/713 khớp; không có tệp dư |
| Narrow export `CHECKSUMS.sha256` | 4/4 khớp; không có tệp dư |
| Pilot resume `BUNDLE.sha256` | 896/896 khớp; không có tệp dư |
| Pilot gốc `EVIDENCE_CHECKSUMS.csv` | 232/232 khớp |
| Stage D/E `EVIDENCE_CHECKSUMS.csv` | 1.777/1.777 khớp |
| `frozen.json.files_sha256` | 23/23 khớp, gồm Release/sanitizer, runner, guard, protocol, inputs |
| Manifest V3: A0/A1/A3 × R1–R3 và base/query/GT | 9/9 graph + 3/3 input khớp SHA-256 |
| Task A: bốn source core và H17 OFF builder | 4/4 source khớp `source_sha256.txt`; ELF khớp SHA lịch sử |

Các đường dẫn evidence dưới đây tương đối với tài liệu này; raw tiếp tục nằm ngoài Git. [Raw manifest](../../../../artifact-evidence/p2-b1-a1-narrow-20261119/BUNDLE.sha256) có SHA `2b6677895dce4a274fd288f71e31e57b3051313e19b05f8cd12ce7022fae4ffe`; [export manifest](../../../../artifact-evidence/p2-b1-a1-narrow-analysis-20261119/CHECKSUMS.sha256) có SHA `483804c96aefbe954693f615537aaebe8d059d59f4790ff8ae5f808331e52fb8`. [Freeze](../../../../artifact-evidence/p2-b1-a1-narrow-20261119/frozen.json) có SHA `526a0724f300f63f46c7d1baa27b6e8b0f3008c8e589c8e74432b50053e23cf9`. Manifest V3 có SHA `9094fb348269918077b37e901b887eae7ac1662c74a45aa43a237cd227e57d16`.

[Stage D/E manifest](../../../../artifact-evidence/p2-followup-20261118/EVIDENCE_CHECKSUMS.csv) kiểm lại có SHA `4e3298e92352e4718b729024d41ab48fbd7a7503770ee24231bfdf3a5e2480eb`. Các phép băm là kiểm toàn vẹn, không chạy lại historical experiments. Validation tài liệu/test cuối được ghi ở [feasibility review, mục 8](TASK_A_R4_R5_FEASIBILITY_REVIEW.md#8-quyết-định-và-validation-của-lượt-tài-liệu).

Freeze pilot/tag vẫn là `f2cd634b837a70735c3e31e5956f0524bfc26675` / `task-da-b1-a1-pilot-freeze-20261119`; freeze Stage D/E vẫn là `87d4a8149416b22ccf8854f72c7c72f09197cfa3` / `task-da-p2-stage-de-freeze-20261119`. Preregistration narrow ở `574420778c6e239d58bbce3df9d86136a47f90c9`. Không thay binary, input, graph, raw, manifest hoặc plan cũ.

**Baseline mạnh nhất hiện có cho phép so sánh kế tiếp là flat merge + fixed S + B1+A1**, với round-robin dispatch. Bằng chứng mạnh nhất nằm ở **A3, p=2, S=16, K=10, jobs=1, Ryzen 4650U**, Release SHA `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1`, sanitizer SHA `c3151165f23cffeec41d6ec508a2339b9eb7db627f708d470dcfc0b622c09ea7`. Đây là baseline làm việc, không phải tuyên bố thắng phổ quát trên A0/A1/p=4 hoặc mọi host. A0-R1 disjoint vẫn fail point floor 0,990. Beam A3 R1/R2/R3 là 970/986/966 theo lựa chọn lịch sử; không tune lại trong lượt này.

[Narrow report](B1_A1_NARROW_REPLICATION_REPORT_20261119.md) ghi gain paired R2 12,29%, R3 10,08%, outer chính 11,19% với CI95 [−2,84%, 25,21%]: **HOLD** theo preregistration. R1–R3 cùng root 555, không được đổi tên thành independent RNG seeds. [Post-review](B1_A1_POST_REPLICATION_REVIEW_20261119.md) và [preregistration R4/R5](B1_A1_R4_R5_CONFIRMATION_PREREG_20261119.md) giữ nguyên nội dung, kể cả những giới hạn cần làm rõ ở báo cáo feasibility mới.

[Stage D/E decision](STAGE_D_E_REPLICATION_AND_H3_DECISION.md#6-giai-đoạn-e--quyết-định-cho-h3-tp-cg-pivot-not_opened) và [post-stage audit](POST_STAGE_DE_AUDIT_AND_H3_PIVOT_PLAN.md) là căn cứ lịch sử cho PIVOT: trên engine flat trước B1/A1, các fixed-S tốt nhất gần nhau trong khi overhead khác còn lớn. **Static-S sweep không phải cận trên toán học cho mọi dynamic schedule**, và chưa đo lại dynamic-vs-fixed trên baseline B1+A1 sạch. PIVOT ở đây là quyết định dừng claim TP-CG gốc vì evidence/novelty chưa đủ, không phải chứng minh mọi adaptive scheduling vô ích. Đề xuất i5 trong tài liệu cũ không được kích hoạt bởi lượt screening này.

### Đề xuất commit bảo toàn, chưa thực hiện

Đề xuất commit riêng `docs(task-da): preserve post-replication audit and conditional R4/R5 preregistration`, chỉ chứa hai tệp có sẵn sau:

| Tệp | SHA-256 bytes hiện tại |
| --- | --- |
| `B1_A1_POST_REPLICATION_REVIEW_20261119.md` | `59b8774fa17de6c34010d13d95fdb602b10e053f5dd06dffb176e1c3bb565920` |
| `B1_A1_R4_R5_CONFIRMATION_PREREG_20261119.md` | `ab06155c90a3daab175bac804922a2e95479716afca2deea2a844bf9e4aca205` |

Sau đó có thể commit riêng ba báo cáo screening mới. Không amend/rewrite commit cũ, không di chuyển tag, không merge. Commit bảo toàn tài liệu không kích hoạt preregistration hay mở H3.

## 2. Corpus và giới hạn audit

Đọc nguồn sơ cấp trực tuyến ngày 2026-11-20: Speed-ANN §§4.1–4.4, Algorithms 2–3; iQAN §§5.1–5.5 và artifact appendix; AverSearch §§3–4, Algorithms 3–5; CAGRA §IV; PipeANN §3; GraphIt §§2.2, 4–6; hypergraph decomposition §3; ParlayANN §§3–4.5. Đối chiếu cả negative results/overhead, không lấy abstract speedup làm chứng cứ cho H3.

Đây là **paper-level mechanism audit**, cộng source-level audit của P2 và builder lịch sử. Không tái lập binary tác giả. Không chứng nhận absence trên toàn bộ literature, artifact code, patent hoặc mọi công trình 2026. Các truy vấn bổ sung gồm `intra-query parallel graph approximate nearest neighbor scheduling CPU locality redundancy`, `ANN frontier partitioning parallel CPU`, `graph ANN neighborhood overlap parallel` và `overlap-aware graph-based search`; kết quả tìm kiếm chỉ giúp chọn nguồn, không chứng minh novelty.

## 3. Ma trận cơ chế

Các ô tiếng Anh ngắn giữ tên cơ chế chính xác. “Not specified” nghĩa là chưa thấy quy tắc ấy trong phần đã đọc, không phải chứng minh công trình không thể có nó.

| Cơ chế | [Speed-ANN, §§4.1–4.4](https://johnpzh.github.io/assets/papers/arXiv-2022_Speed-ANN_Zhen.pdf) | [iQAN, §5](https://johnpzh.github.io/assets/papers/PPoPP-2023_iQAN_Zhen.CameraReady.pdf) | [AverSearch v2, §§4.2–4.4](https://arxiv.org/html/2504.20461v2#S4) |
| --- | --- | --- | --- |
| Worker assignment | Even split of unchecked candidates; local best-first paths | Path-wise workers with private queues | Queue maintainers and distance calculators in subgroups |
| Frontier partitioning | Global queue divided into local queues | Global/local candidate pools; staged width | Sub-queues, shared L-threshold, global transfer buffer |
| Neighborhood overlap | Neighbor grouping changes storage locality; no seed-overlap assignment rule specified | No seed-adjacency-overlap objective specified | Explicitly recognizes shared destination vertices |
| Duplicate evaluation avoidance | Loose shared visited; tolerates races/recomputation | Loose shared bit-vector visited; distinct from unnecessary path exploration | Distance array and ready flags reuse computed distances |
| Load balancing | Even candidate count; progressively activates workers | Staged worker/expansion width | Work stealing: long queues offload, short queues take work |
| Synchronization | Update-position checker triggers global merge | Average update position triggers lazy global synchronization | Asynchronous polling and shared structures |
| Scheduling overhead | Checker/metric, private queues, merge, layout memory | Queue operations, update-position metric, synchronization | Threshold scans, buffer traffic, polling, role allocation, distance-array memory |

Speed-ANN và iQAN là các công trình cùng nhóm tác giả, có cơ chế chồng lấn; không đếm chúng như hai kiểm chứng độc lập. Trong Speed-ANN, **round-robin checker** là luân phiên người kiểm tra sync; pseudocode chia seed chỉ quy định chia đều, không đủ để suy ra chính xác mapping `rank % workers` như P2. Neighbor grouping là bố trí vector/index trong bộ nhớ, khác với quyết định worker theo giao adjacency ở một query/round. [Speed-ANN §4.3–4.4](https://johnpzh.github.io/assets/papers/arXiv-2022_Speed-ANN_Zhen.pdf)

Trong iQAN, “redundancy” còn chỉ các expansion không hứa hẹn do local search đi quá xa, không đồng nhất với tính lại cùng `(query, vertex)`. AUP điều khiển **khi nào merge**; nó không phải phép đo giao neighborhood. [iQAN §§5.2–5.3](https://johnpzh.github.io/assets/papers/PPoPP-2023_iQAN_Zhen.CameraReady.pdf)

| Cơ chế | [CAGRA v2, §IV](https://arxiv.org/html/2308.15136v2#S4) | [PipeANN, §3](https://www.usenix.org/system/files/osdi25-guo.pdf) | [GraphIt, §2.2 và scheduling](https://arxiv.org/html/1805.00923) | [Hypergraph decomposition, §3](https://faculty.cc.gatech.edu/~umit/assets/pdf/Catalyurek96.pdf) |
| --- | --- | --- | --- | --- |
| Worker assignment | GPU teams/CTAs per query | Priority-driven SSD I/O pipeline | Vertex/edge chunks; static or dynamic scheduling | Assign task vertices to processors |
| Frontier partitioning | Top-M/candidate buffers; per-CTA lists in multi-CTA | Search candidate and outstanding-I/O state | Sparse/dense frontiers; segmented subgraphs | Partition task set under balance constraints |
| Neighborhood overlap | Candidate dedup; no overlap-guided CPU seed mapping specified | No CPU seed-overlap mapping specified | Locality and partitioning tradeoffs; not ANN rank dispatch | Shared data represented by hyperedges |
| Duplicate evaluation avoidance | Visited hash; forgettable or standard management | Visited/I/O state is distinct from P2 local_seen | Algorithm-specific updates and synchronization | Minimize repeated communication of shared data |
| Load balancing | Hardware mapping and team size | Keep I/O pipeline occupied | Edge-aware vertex chunks; work stealing | Weighted part balance |
| Synchronization | GPU buffer/hash coordination | Asynchronous I/O overlaps search compute | Atomics and iteration boundaries depend on schedule | Runtime synchronization outside partition objective |
| Scheduling overhead | Hash, buffer selection, CTA/kernel costs | Speculation/state and I/O management | Degree scans, partition/merge, stealing and atomics | Partition computation and storage |

CAGRA dùng cờ parented, top-M và visited hash: frontier flag/dedup không thể là novelty độc lập của H3. GPU mapping cũng không chứng minh gain CPU. PipeSearch giải bài toán thứ tự compute/I/O SSD, nên không phải reproduction baseline cho P2 RAM. [CAGRA §IV-B–C](https://arxiv.org/html/2308.15136v2#S4), [PipeANN](https://www.usenix.org/system/files/osdi25-guo.pdf)

ParlayANN cung cấp deterministic parallel graph construction, batching và search/layout optimizations; không được dùng chữ “parallel ANN” để suy ra nó đã thử cùng cơ chế intra-query dispatch. Nó là prior art cần giữ riêng giữa **build** và **search**. [ParlayANN §§3–4.5](https://arxiv.org/html/2305.04359)

## 4. Đối chiếu toán học: vì sao gom overlap chưa đủ mới

Suy luận của audit, dưới giả định **mọi seed đều được expand một lần, chỉ một hop, visited đầu round cố định**: tạo hypergraph với một vertex cho mỗi seed; mỗi ID láng giềng chưa visited là một hyperedge nối các seed chứa nó. Gọi `lambda(v)` là số worker có ít nhất một seed nối tới `v`.

```text
U_w = union of eligible neighbors of seeds assigned to worker w
D_seed = sum_w |U_w| - |union_w U_w| = sum_v (lambda(v) - 1)
M_seed = max_w |U_w|
```

Mục tiêu giảm `D_seed` chính là connectivity-minus-one trên hypergraph này. Mục tiêu shared-data partitioning và cân bằng đã có trước ANN; không được đặt claim thuật toán mới chỉ bằng đổi tên thành overlap-aware ANN. Nguồn định nghĩa cut-net/connectivity và cân bằng: [Çatalyürek–Aykanat, §3.1–3.2, bản tiền thân 1996](https://faculty.cc.gatech.edu/~umit/assets/pdf/Catalyurek96.pdf). Bài journal mở rộng năm 1999 có [DOI 10.1109/71.780863](https://doi.org/10.1109/71.780863); audit này không gán PDF 1996 thành bản journal 1999.

Với hai worker, đặt `G=|U_0 ∪ U_1|` cố định thì `M_seed=(G+D_seed+||U_0|-|U_1||)/2`. Chỉ tối thiểu tổng union mà bỏ imbalance có thể chọn sai critical path. Mô hình cũng chưa phản ánh neighbor-check, local queue và các đỉnh mới chen lên trước seed. Đây là điều kiện của proxy, không phải định lý latency ANN.

## 5. Novelty ledger và contribution còn thiếu

| Claim dự kiến | Đánh giá | Cần chứng cứ gì để thay đổi |
| --- | --- | --- |
| Dynamic S, staged width hoặc merge khi thấy redundancy | Prior art trực tiếp; PIVOT khỏi claim gốc | Cơ chế mới phân biệt rõ với AUP/staged, không chỉ ngưỡng khác |
| Atomic/shared visited, distance memo, flat queue, expanded flag | Baseline/system techniques | Không đặt làm contribution thuật toán H3 |
| Overlap grouping + degree balance | Hypergraph/locality scheduling đã biết | Chỉ chuyển miền áp dụng chưa đủ |
| Chữ ký adjacency 128 bit + rank-pair swaps | Heuristic feasibility candidate; novelty UNKNOWN | So với generic constrained partitioning, degree-only và signature placebo |
| Online rule biết khi nào seed overlap dự báo được round critical work | Có thể là câu hỏi nghiên cứu có giá trị | Dẫn xuất từ multi-step search, chi phí giới hạn, dự báo ngoài panel phát triển |
| Rank constraint bảo toàn Recall | Chưa có bảo đảm | Đổi local queues vẫn đổi đường đi; cần chứng minh phù hợp hoặc recall-matched evidence |

Một đóng góp có thể kiểm chứng cần đồng thời: đặc tả quan hệ giữa overlap và **công thực expand**, quy tắc phân công có budget và fallback, cùng ablation chứng minh lợi ích vượt degree/load-aware và generic hypergraph heuristic. Nếu chỉ thu được một heuristic partitioning quen thuộc nhanh hơn nhờ code, gọi đúng là tối ưu implementation. Không tạo thuật toán mới để lấp tên H3.

## 6. Kết luận và cổng

Theory: **MODEL_SUPPORTED** cho cơ hội giảm tính lặp ở proxy một hop. Feasibility online: **UNKNOWN**. Gain ANN mới: **NOT_MEASURED**. Novelty thuật toán: **NOT_ESTABLISHED**. Kế hoạch bằng chứng tối thiểu nằm ở [overlap screening plan](H3_OVERLAP_SIGNAL_SCREENING_PLAN.md); không có phê duyệt prototype ngầm trong tài liệu này.

Historical P0 / Full P1 / t0998 = **HOLD**; Protocol V4 D1–D5 = **UNAPPROVED**; P3 Official = **CLOSED**; H3/TP-CG = **NOT_OPENED**. D1 = **UNTESTED**, D4 = **NOT TESTED**, D6 = **INCONCLUSIVE** trên đúng subject lịch sử. PAPER_STOCK, PAPER_GCC13_PORTABLE và MODERN_GOLDEN tiếp tục riêng biệt. T16 lịch sử không chứng minh D mechanism hay H3. H-V/H-G/H-C/H-F/H-QV giữ là các lane độc lập.

**Original TP-CG: PIVOT. Overlap-aware assignment: MORE EVIDENCE.**
