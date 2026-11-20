# Task D — Research direction sau H3 overlap NO-GO

Ngày: **2026-11-20**. **Khuyến nghị chọn B: chốt Task D trong phạm vi hiện tại thành experimental systems study; NO-GO mở một H3 mới để triển khai lúc này.** Giữ các kết quả H1/H2, ablation flat/S/B1/A1 và kết quả âm overlap, với phạm vi suy luận đúng. Đây chưa phải đánh giá đủ tiêu chuẩn công bố.

Còn headroom hệ thống đáng kiểm tra, đặc biệt coordinator và worker search-container work; **bottleneck nhân quả lớn nhất của latency OFF vẫn UNKNOWN**. Chưa có cơ chế thuật toán vừa có dư địa đã đo, chi phí khả thi và khác prior art. Không tạo một thuật toán mới trong lượt quyết định này.

## 1. Căn cứ và trạng thái bảo toàn

[Latency budget audit](TASK_D_LATENCY_BUDGET_AND_UPPER_BOUNDS.md) tái tổng hợp raw H1/H2, Stage D/E, B1+A1 và trace screening. Instrumentation/offline tools/tests/báo cáo NO-GO được freeze bằng commit riêng **`6bdf65f`**; ba tài liệu tiền đề ở `1d38389`. Seven evidence bundles, 3.993 manifest entries, và 23 narrow pins đều khớp. Tests dataset-free mới nhất: **507 pass, 13 skip /520 collected**. Baseline, historical raw, plans và freeze tags không đổi.

Các facts thay đổi quyết định:

- **Baseline mạnh hiện có:** best fixed flat+S+B1+A1, RR. Bằng chứng tốt nhất ở A3 p2/S16: mean OFF ~5,13–5,30 ms/query, gain so baseline cũ 10–12% từng graph; narrow outer CI vẫn chứa 0 nên **HOLD**. p4 B1+A1 mới có R1, gain không chắc chắn; A1-graph clean matrix chưa có. Không tuyên bố baseline này thắng mọi cấu hình.
- **Coordinator envelope còn đáng kể:** ~0,77–0,79 ms/query, 14,3% ON ở A3 p2; ~0,83–0,89 ms, 22–24% ON ở p4 R1. Đây không phải pure merge hay direct OFF saving.
- **Trace worker phase lớn nhất về thời gian quan sát:** ~4,44–4,54 ms, 71% trace ON; bao gồm L2, visited, queue, memory và observer. Chưa có phân rã exclusive.
- **Bare arrival tail nhỏ:** 2,9–3,5 µs/query; summed barrier wait không phải thời gian có thể xóa. Ideal divisible-work/zero-delay ceiling chỉ ~4,3–4,4% trace wall, với các giả định không được bảo đảm bởi graph search.
- **Duplicate p2 sau B1 chỉ khoảng 2,5% L2.** Seed–seed chiếm ~0,33% tổng L2; 79–80% duplicate thuộc emergent–emergent. Signature-128 không vượt degree/placebo. Exact overlap chỉ hơn eligible-load ~0,11–0,12% trên proxy max seed-union work.

H3 evidence chỉ gồm **64 validation queries mỗi graph, 32 development +32 held, 6.095 rounds trên A3-R1/R2/R3**. Mọi assignment khác RR là **offline counterfactual**. Không có online H3 latency gain hoặc changed-path Recall result. Ba graph cùng RNG root 555; không đổi tên thành independent seeds. Không kéo CI query/round thành graph replication.

## 2. Screening đúng hai họ cơ chế, không tự đặt H3 mới

Hai họ dưới đây tác động vào hai vị trí khác nhau: tổ chức frontier/coordination và quyết định tính khoảng cách. Chúng được xét để quyết định có khoảng trống nghiên cứu hay không; **không phải hai thuật toán H3 mới được đề xuất để cài đặt**. Các phép screening là thiết kế tương lai, chưa chạy, cần phê duyệt riêng.

### Họ 1 — Giảm materialization và đồng bộ global frontier

**Vấn đề được chứng minh đến đâu.** Whole coordinator window còn lớn trên baseline sạch; local `std::set` maintenance có mặt trong source nhưng thời gian exclusive chưa đo. Việc A1 giảm OFF trong khi M_ON tăng cho thấy timer window và chuẩn bị dispatch khác nhau; chưa biết phần nào có thể xóa mà không đổi search trajectory.

**Cơ chế đã có để đối chiếu.** Worker giữ local candidate pools, chia sẻ một threshold đại diện global top-L; local pools prune theo threshold và chuyển việc qua buffer khi lệch tải, thay vì đợi materialize/redistribute toàn bộ frontier ở mỗi barrier. Các biến thể sorted-array/checked-flag/batched merge giảm queue traffic nhưng giữ logic tìm kiếm tương tự. Đây là mô tả các cơ chế hiện hữu, không kết hợp chúng thành phương pháp mới.

**Prior-art boundary.** Speed-ANN có local queues và redundancy-aware merge; iQAN có staged width và AUP-triggered synchronization. [Speed-ANN §§4.2–4.4](https://johnpzh.github.io/assets/papers/arXiv-2022_Speed-ANN_Zhen.pdf), [iQAN §5](https://johnpzh.github.io/assets/papers/PPoPP-2023_iQAN_Zhen.CameraReady.pdf). AverSearch đã dùng asynchronous L-threshold, buffer-based work stealing và tách queue maintainer/distance calculators. [AverSearch §§4.2–4.4](https://arxiv.org/html/2504.20461v2#S4). Sorted beam, explored flag, first-unexplored position và sort-survivors/linear merge cũng được mô tả trực tiếp trong GINGER, dẫn về ParlayANN/SVS. [GINGER §4.3](https://arxiv.org/html/2611.08306v1#S4.SS3). Đổi container, bỏ barrier, đổi threshold hoặc ghép các kỹ thuật này chưa phải novelty.

**Cost/net-gain contract.** Gọi f_C là exclusive critical-path coordinator/frontier fraction **của OFF**, r_C là phần thực loại được, h_C là overhead/query của threshold scans, transfers, atomics và worker capacity bị lấy cho maintenance. Khi workload/Recall giữ phù hợp, mô hình sàng lọc là `net ≈ f_C*r_C - h_C/T_OFF`; f_C hiện chưa đo. Các tỷ lệ ON 14–24% chỉ là gross envelopes, không thay f_C.

Ví dụ nhạy cảm, không phải dự báo: nếu f_C=15%, loại một nửa với overhead 1% tổng latency thì net=6,5%; nếu f_C=5% thì chỉ 1,5%. Trên A3 p2, gain mục tiêu 5% tương đương ~260 µs/query; nếu thực chỉ có 0,8 ms coordinator chuyển được sang OFF thì phải xóa trên một phần ba nó trước overhead. Với 32 round/query, overhead 1% chỉ cho khoảng 1,6 µs/round. Các số này là yêu cầu break-even, không phải gain đã đo.

**Failure cases.** Threshold cũ gây work inflation, đẩy nhánh hứa hẹn ra ngoài budget hoặc hạ Recall; transfer/atomic gây cache traffic; pruning còn phải materialize top-L; p2 không có đủ worker dư để cấp một role riêng mà giữ cùng năng lực L2. Local-array replacement có thể tăng insertion/memmove khi beam~1.000. Đổi synchronization thay search semantics nên cần design review trước source change, dù Recall cuối có vẻ tương đương.

**Screening nhỏ được phép đề nghị.** Trước hết làm narrow phase/sampling audit trong báo cáo budget, không đổi thuật toán. Chỉ nếu có exclusive OFF budget đủ lớn mới dùng một bounded replay của **cơ chế prior art đã đặc tả**, đo candidate operations/data movement và overhead với exact sets; replay không được gọi là ANN latency. Mọi thử nghiệm online sau đó phải có design review, matched Recall và baseline fixed flat+S+B1+A1.

**GO/NO-GO.** GO cho feasibility tiếp theo chỉ khi removable component có lower-confidence evidence ≥10% OFF, conservative net ceiling ≥5%, overhead≤1% OFF và chỉ rõ một quy tắc thuật toán khác prior art. Nếu chỉ container/threshold/work-stealing có sẵn, **NO-GO cho claim H3 novel** dù có thể là systems optimization. Hiện tại: **không đạt novelty gate; f_C còn UNKNOWN; không triển khai**.

### Họ 2 — Tránh full-distance/vector traffic cho candidate không hứa hẹn

**Vấn đề được chứng minh đến đâu.** Sau B1 vẫn cần ~26–27k distance evaluations/query A3 p2, đa số unique. Worker phase lớn nhưng không có exclusive distance/memory time. Vì vậy đây là miền có thể lớn hơn duplicate elimination, chưa phải bottleneck L2 đã được xác nhận.

**Cơ chế đã có để đối chiếu.** Với threshold của candidate pool, dùng phép so sánh rẻ hơn full distance để quyết định một điểm khó vào frontier; chỉ tiếp tục đọc/tính đủ tọa độ hoặc full-precision score cho những điểm còn hứa hẹn. Một nhánh là incremental dimension sampling với kiểm định sai số; một nhánh là approximate score/prefilter và exact/refined scoring sau. Transform, auxiliary codes, query preparation, false positives và sai số đều thuộc chi phí, không được giả định miễn phí.

**Prior-art boundary.** ADSampling dùng randomly transformed coordinates và incremental sampling/hypothesis testing cho distance comparison. [ADSampling §3](https://arxiv.org/html/2303.09855). FINGER xấp xỉ khoảng cách qua góc giữa residual vectors để bỏ full computations không cần thiết. [FINGER](https://cdn.amazon.science/74/56/d9c1550a4afab9020fb063336769/finger-fast-inference-for-graph-based-approximate-nearest-neighbor-search.pdf). GINGER v1 ngày 2026-11-05 có 4-bit scoring, projected search, prefilters và refinement; không thể gọi coarse-to-fine scoring, prefix sketch hoặc beam-threshold filtering là ý tưởng mới. [GINGER §§3–4.2](https://arxiv.org/html/2611.08306v1). Speed-ANN/iQAN tối ưu đường đi/đồng bộ; AverSearch đã tái sử dụng distance qua array, nên memoization cũng không tạo novelty. Sources được đọc ở mức paper; author-code/binary equivalence chưa xác minh.

**Cost/net-gain contract.** Gọi f_D là fraction OFF thực sự thuộc distance/vector access có thể thay, r_D là tỷ lệ cost giảm sau filter/refinement, H_D gồm query transform, metadata/code reads, filtering, fallback/reranking và extra search do đổi score. `net ≈ f_D*r_D - H_D/T_OFF`. Không có f_D/r_D/H_D đo được để đưa point estimate trung thực.

Nếu f_D=40%, giảm một nửa và thêm 2% tổng overhead thì mô hình cho 18%; nếu f_D=10% thì chỉ 3%. Đây chỉ là sensitivity scenarios. Dữ liệu Task D hiện là **100 dimensions**, không phải các embedding hàng nghìn chiều; prefix/rotation/filter cost có thể chiếm phần lớn distance kernel. Không chuyển gain của paper khác thành expected gain Task D. Tối ưu SIMD/layout thuần túy cũng không đủ novelty thuật toán.

**Failure cases.** Distances gần threshold khiến filter phải hoàn tất hầu hết tọa độ; query projection/codes phá cache locality; sai số loại mất routing vertex làm tăng beam/rounds hoặc hạ Recall; graph thấp chiều không amortize được overhead. Full float32 inputs + double accumulation của common engine khác quantized navigation; đổi precision/ranking là thay search semantics, không phải instrumentation được phép sửa trong lượt này.

**Screening nhỏ được phép đề nghị.** Sau measurement-validity gate, nếu distance/vector share được đo đủ lớn, đặc tả **một phương pháp prior-art baseline** và cost/error contract; tối đa một panel validation nhỏ để đo rejection/refinement/error và tổng byte/operations. Trace hiện tại không có admission threshold cho mọi L2 event, nên chưa đủ replay DCO chính xác; không suy ra filter success chỉ từ final top-10. Capture bổ sung chỉ sau approval và design review, không hiện thực một H3 mới.

**GO/NO-GO.** GO cho feasibility chỉ nếu exclusive f_D cùng rejection/cost cho lower-bound net≥5% với uncertainty, matched-Recall feasibility và một algorithmic difference cụ thể với ADSampling/FINGER/GINGER. Nếu chỉ reproduce/recombine các phương pháp có sẵn, **NO-GO cho H3 novel**, có thể dùng làm stronger baseline ở một lane được duyệt khác. Hiện tại: **budget UNKNOWN, novelty gap chưa có, không triển khai**. H-V giữ là lane độc lập; audit này không chuyển hoặc mở lane đó.

## 3. Tại sao không mở hướng thứ ba để cứu H3?

Shared atomic visited/distance memo nằm trong prior-art envelope và B1 đã cắt phần lớn duplicate xuyên round. Overlap-128 đã thất bại so với placebo/degree; chính xác hơn chưa giải quyết chi phí và khoảng cách với eligible-load. Dynamic S đơn thuần chồng lấn staged/AUP của Speed-ANN/iQAN; static-S gần nhau không chứng minh bất khả thi nhưng cũng không cung cấp cơ chế mới. Không có căn cứ đặt tên thuật toán mới từ các ingredients này.

Hai họ được xét đều có thể có giá trị engineering hoặc baseline research. **Chưa họ nào cung cấp một H3 khác biệt thật sự để owner phê duyệt prototype.** Một improvement lớn trong profile tương lai chỉ trả lời “có budget”, không tự trả lời “có novelty”.

## 4. Đánh giá hai lựa chọn nghiên cứu

| Tiêu chí | A — Theo đuổi H3 thuật toán mới | B — Experimental systems study |
| --- | --- | --- |
| Claim khả dĩ | Cơ chế mới giảm critical-path cost tại Recall matched | Tác động topology/configuration lên scaling và mức nhạy với baseline/observer |
| Evidence hiện có | Chưa có cơ chế mới hoặc positive online gain; overlap candidate NO-GO | Có H1/H2, replicated flat/S results, B1/A1 ablations và negative screening có placebo |
| Novelty | Chưa xác lập; hai họ cơ chế có prior art mạnh | Có thể có empirical/methodological insight; literature comparison chưa đủ để khẳng định mới |
| Rủi ro chính | Tối ưu known implementation rồi gọi thành algorithm; chọn giả thuyết sau nhiều thử nghiệm | Single dataset/host, cùng RNG root, quality/selection bias và attribution chưa khép |
| Công việc tối thiểu còn thiếu | Exclusive latency budget, algorithmic difference, overhead/Recall proof và prospectively registered test | Giới hạn claim, mạnh hóa đối chứng, measurement attribution, đa dữ liệu/graph, artifact reproducibility |
| Quyết định hiện tại | **NO-GO triển khai H3 mới** | **Chọn B làm cách chốt Task D hiện tại; chưa publication-ready** |

### Giữ những kết quả nào?

1. **H1: observed topology/configuration × scaling association.** A3 cần beam/expansions/rounds lớn hơn ở matched validation Recall; A0/A1 gần nhau trong scope đã thử. Graph treatment đồng thời ảnh hưởng beam và traversal, nên không claim một graph metric đơn lẻ là nguyên nhân. Các CI dựa trên ba same-root build invocations có điều kiện; H1 ban đầu có recall drift và các lượt chậm đều được giữ.
2. **H2: work inflation và coordination diagnostics.** Giữ counters, nguồn duplicate và source-timer interpretation. Không giữ như kết luận nhân quả các tỷ phần “giải thích 90–100% excess” từ `T1/DE1` hay `barrier/p`; budget audit đã chỉ rõ vì sao phân rã đó không phải exclusive wall time.
3. **Flat/fixed-S/B1/A1: baseline ablations.** Giữ actual OFF contrasts với output parity, không gọi novel algorithms. B1+A1 A3 p2 lợi từng graph rõ nhưng outer rule vẫn HOLD; p4 thiếu precision/replication và A0 disjoint fail là kết quả cần xuất bản trong artifact, không bỏ để làm bảng đẹp.
4. **H3 negative result.** Giữ phát hiện overlap exact có predictive signal nhưng sketch không vượt placebo/degree, eligible-load giải thích phần lớn proxy gain, và runtime/footprint không đạt cost contract. Giới hạn NO-GO ở candidate/subject được screen; không có changed-path latency gain và không bác toàn bộ topology research.

### Cần gì thêm trước khi nói về một bài báo?

- **Prior-art/claim positioning:** Speed-ANN/iQAN đã có performance characterization; experimental study không mặc nhiên mới chỉ vì có nhiều bảng. Cần chứng minh insight nào vượt những phân tích đó, ví dụ một kết luận có thể tái lập về baseline/observer confounding qua nhiều engines, không chỉ một lỗi trong common engine.
- **Stronger baselines:** cùng hardware/input/workload/metric/K, beam/calibration chỉ trên validation, matched Recall và time/memory accounting. Tối thiểu baseline sạch hiện tại, một serial graph ANN implementation mạnh, và native CPU intra-query references Speed-ANN/iQAN/AverSearch khi artifact khả dụng/kiểm được. Không có artifact thì ghi UNVERIFIED và giới hạn claim, không thay reproduction bằng tên paper. Sorted candidate containers, visited structures và distance/layout optimizations cũng cần fair baseline vì [ParlayANN §4.5](https://arxiv.org/html/2305.04359#S4.SS5) đã có các tối ưu này.
- **Datasets/graphs:** ngoài MS-Turing-1M cần các workload công khai khác có chiều và intrinsic structure khác nhau, thí dụ một bộ ~96–128D và một bộ embedding cao chiều; thêm graph family ngoài recipe PiPNN đang dùng. Chọn theo hypothesis, không chọn dataset sau khi thấy gain. Đây là nhu cầu paper tương lai, **không phải authorization tạo index/benchmark trong lượt này**.
- **Replication và chất lượng:** phân biệt build nondeterminism cùng root với independent-root cohort; Task A/owner phải giải quyết seed/source semantics trước cohort mới. Không pool process/query thay graph replicates. Cần holdout/query distribution phù hợp, Recall point/LCB và actual matching được báo; toàn historical query pool đã từng được P1 xem. A0 quality fail phải xử lý bằng validation-only protocol mới hoặc giới hạn phạm vi.
- **Latency/throughput:** jobs=1 latency và inverse-latency QPS chưa đánh giá loaded throughput/resource efficiency. Nếu claim service scaling cần thêm inter-query concurrency/CPU-time/memory/energy hoặc goodput có protocol riêng. Cross-architecture claim cần host thứ hai được duyệt; hiện tại chỉ có Ryzen và i5 luôn NOT_RUN.
- **Attribution/artifact:** exclusive phase profiling với uncertainty, observer parity/overhead, proper PMU attribution nếu có; locked source/binary/package/protocol/raw; dataset-free tests và hướng dẫn reproduce không phụ thuộc hardcoded private paths. Không gắn PMC claim lên RSS/telemetry.

Vì các thiếu hụt này, kết quả hiện tại phù hợp một **technical research report và reproducible case study**. Chưa đủ cơ sở khẳng định tiêu chuẩn công bố hoặc chọn venue.

## 5. Quyết định thực thi và bước nhỏ nhất

**Không có H3 nào đáng triển khai ngay theo evidence hiện tại.** Khuyến nghị đóng mục tiêu tìm H3 mới trong phạm vi này và giữ Task D theo lựa chọn B. “Đóng mục tiêu” là khuyến nghị nghiên cứu, không đổi trạng thái official gate. Một giả thuyết thực sự khác sau này cần evidence/novelty review mới; không mở bằng việc thêm process repeats vào graph cũ.

**Bước thực nghiệm nhỏ nhất tiếp theo, nếu owner muốn lấp khoảng trống attribution cho systems study:** narrow phase/sampling audit A3-R1 p2/S16, cùng 64 validation IDs và baseline sạch, theo mục 6 của latency budget. Mục tiêu duy nhất là tách distance/vector access, local frontier và serial coordinator; không thử policy mới. Nếu observer không đạt budget/parity hoặc sample uncertainty không đủ, trả UNKNOWN; không tự mở rộng campaign. Sau đó mới quyết định một known systems optimization có đáng đo hay không. Không profiler/benchmark nào trong kế hoạch này đã được chạy ở lượt audit.

Trả lời trực tiếp:

| Câu hỏi | Kết luận |
| --- | --- |
| Còn bottleneck lớn chưa giải quyết? | Có một miền chi phí đáng kể chưa tách: coordinator và worker phase. **Bottleneck nhân quả lớn nhất OFF chưa xác định**, không claim memory/L2/merge chi phối tuyệt đối. |
| Có H3 đáng triển khai? | **Không trong phạm vi và bằng chứng hiện tại.** |
| Cơ chế nào khác prior art? | **Chưa xác lập được**; cả hai họ xét có prior art trực tiếp. |
| Nên giữ gì? | H1/H2 scoped observations, paired flat/S/B1/A1 gains và uncertainties, quality failures, same-root provenance, overlap NO-GO/placebo/cost evidence. |
| Tiếp theo nhỏ nhất? | Một measurement-validity/phase audit hẹp được duyệt riêng, phục vụ lựa chọn B, không H3 prototype. |

Official states giữ nguyên: Historical P0 / Full P1 / t0998 **HOLD**; Protocol V4 D1–D5 **UNAPPROVED**; P3 Official **CLOSED**; TP-CG/H3 **NOT_OPENED**, original TP-CG **PIVOT**; overlap candidate **NO-GO**; **i5-14600KF NOT_RUN**. D1 **UNTESTED**, D4 **NOT TESTED**, D6 **INCONCLUSIVE** trên các subject lịch sử. Không tạo graph, không thay seed hoặc binary lịch sử, không triển khai thuật toán mới trong lượt này.
