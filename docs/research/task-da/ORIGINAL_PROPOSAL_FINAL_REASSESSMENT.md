# Task D × Task A — Final reassessment of the 15/11 proposal

Ngày: **2026-11-20**. **A — NO-GO mở/triển khai một H3 mới trong scope hiện tại. B — tiếp tục chốt một experimental systems report có giới hạn; publication readiness chưa xác lập.** Final measurement-validity study đã chạy đủ ba cặp, correctness PASS nhưng observer equivalence chưa đạt; PMU không được phép. Không có căn cứ mới để mở lại TP-CG.

Đây là quyết định phân bổ nghiên cứu dựa trên evidence hiện có, **không phải chứng minh mọi topology/progress-aware scheduler đều bất khả thi**. Bottleneck có thể cải thiện lớn nhất của latency OFF vẫn **UNKNOWN**. Không biến một observer failure thành kết quả âm về toàn bộ algorithm family.

## 1. Đối chiếu đúng đề xuất gốc

Đã đọc trực tiếp [DOCX đề xuất ngày 15/11](../../../../source-evidence/TASK_D_A_GRAPH_TOPOLOGY_PARALLEL_TRAVERSAL_PROPOSAL_20261115.docx), SHA256 **`a7aef4ba2ed867ed8799f72baec463ab5bd59c6fbdd190327d38b6953b260b45`**, và [bản extract có sẵn](../../../../source-evidence/proposal_drive_extract.txt). [Text trích từ XML DOCX trong lượt này](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/proposal_docx_text.txt) cùng original hashes nằm trong sealed evidence. Không sửa file gốc, không lấy một presentation về sau thay định nghĩa proposal.

Đề xuất phân biệt rõ H1–H2 là khảo sát tương tác, H3 mới là phương pháp. P4 yêu cầu **bottleneck thuộc quyền can thiệp Task D và signal đủ rẻ** trước P5. P5 yêu cầu cost-gated policy, best-fixed/staged đối chứng, fallback và ablations; P6 chấp nhận negative-result report đúng chuẩn. Vì vậy kết thúc mà không có H3 thắng baseline là một outcome hợp lệ của proposal; nó không tự hoàn tất mọi điều kiện đánh giá độc lập.

Hai báo cáo trước đã review/freeze riêng ở **`32160b6`**; H3 code/tools/NO-GO ở **`6bdf65f`**. [Final measurement audit](MEASUREMENT_VALIDITY_AND_PHASE_AUDIT.md) và [sealed raw manifest](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/CHECKSUMS.sha256), SHA256 **`1af5626e530bf0bd37e4977c3dae18b1e0860f3c29d1205dce4679e95694098f`**, là evidence mới; không thay historical baseline hoặc protocol.

## 2. H1, H2, H3 đã đi được đến đâu?

| Hypothesis gốc | Evidence ủng hộ / thay đổi cách hiểu | Kết luận có phạm vi |
| --- | --- | --- |
| **H1: build/serial cost tốt không mặc nhiên cho multiworker scalability tốt** | H1/H2 pilot, Stage D/E A0/A1/A3 p1/2/4 cho graph/configuration-dependent latency, rounds và inflation. Trước B1/A1, Stage D best-flat A0−A3 speedup contrast p2 S16 là +0,1175x, CI ghi trong report [+0,0929;+0,1421]; best-fixed p4 +0,1244x [+0,0333;+0,2156]. Flat/S làm gap nhỏ hơn nhiều so legacy set/S8. | **SUPPORTED_WITH_EXPLORATORY_SCOPE**, không phải causal topology theorem hoặc confirmatory population result. Đây là difference of speedups, **không phải** log-interaction estimand Δ_int của proposal và không thay trực tiếp tiêu chí 5% đã preregister. |
| **H2: topology/frontier/work/sync interactions tạo execution cost có thể can thiệp** | Counter semantics, B1 duplicate suppression, A1 frontier ablation và round-level stragglers làm rõ nhiều cơ chế trong common engine. Final observer cho thấy global frontier/dispatch là một window đáng kể trong execution đó. | **PARTIALLY_SUPPORTED; CAUSAL OFF ATTRIBUTION UNKNOWN.** Chưa phân được L2/queue/memory cost hoặc chứng minh cheap signal dự đoán **net OFF benefit**. H2 chưa được hiểu đầy đủ. |
| **H3: topology/progress-aware policy giảm cost vượt overhead và best-fixed/staged** | Original dynamic-S TP-CG chưa mở. Overlap candidate có exact signal nhưng cheap sketch không thắng degree/placebo và cost contract; final study không bổ sung positive online algorithm result. | **NO-GO mở prototype lúc này; TP-CG NOT_OPENED.** Không phải REFUTED cho mọi policy có thể đổi work/trajectory. |

Các giới hạn quyết định độ mạnh của H1/H2:

- R1–R3 là ba build invocations **cùng RNG root 555**, không ba independent seed replicates. CI theo cohort cũ có tính điều kiện; không pool rounds/process/query để thay graph independence.
- Stage D validation matching span ≤0,0001 là điểm mạnh. Test3k có floor pass nhưng không đồng nghĩa mọi cặp đều exact-matched ở tolerance ấy. H1 pilot ban đầu còn Recall drift; không kéo nó sang một claim clean, matched-Recall mạnh hơn.
- A0↔A1 control không cho thấy tương phản chắc trong nhiều cell, nhưng CI chứa 0 **không chứng minh equivalence**. A3 thay C/K đồng thời đổi degree, beam/traversal và locality; chưa tách được một topology descriptor là nguyên nhân độc lập.
- Best available **flat + historically selected fixed S + B1+A1** là reference hiện tại, không legacy set/S8. Sau B1/A1 còn thiếu clean A1-graph matrix và p4 R2/R3; không chuyển gap trước B1/A1 thành remaining headroom hiện nay.
- B1+A1 A3 p2 paired gains từng graph ~10–12% là systems ablation, outer CI95 **[−2,84%;25,21%] vẫn HOLD**; p4 chưa chắc chắn, A0 disjoint Recall 0,98940 FAIL phải giữ. Không gọi những thay đổi baseline này là H3 algorithm novelty.

Các con số/limitations trên truy về [Stage D/E](STAGE_D_E_REPLICATION_AND_H3_DECISION.md), [B1+A1 narrow replication](B1_A1_NARROW_REPLICATION_REPORT_20261119.md) và [latency budget](TASK_D_LATENCY_BUDGET_AND_UPPER_BOUNDS.md). Những mô hình cũ dùng `T1/DE1`, `barrier/p`, hoặc residual gần zero không phải exclusive causal decomposition; không tái sử dụng tỷ lệ “đã giải thích 90–100% excess”.

## 3. Final measurement thay đổi quyết định gì?

**Observed:** ba frozen OFF processes trên A3-R1 p2/S16 có mean **5,1165 ms/query**, SD process **0,0676 ms**. Tất cả 384 outputs mới khớp; independent 640 distance checks PASS; 521 dataset-free tests cho **507 pass/14 skip**, native synthetic observer contract **1/1 PASS**. Không đổi search semantics.

**Measurement validity:** observer/frozen paired change **−1,717%**, process-level t2 CI95 **[−2,851%;−0,570%]**; equivalence budget ±2% **chưa đạt**. Không nhận “observer nhanh hơn” làm algorithmic win. Đây là combined build/observer drift, không tách được clocks khỏi layout/host effects. Đã dừng đúng sáu real processes, không đổi budget để PASS.

**Observed trong observer, chưa transfer sang OFF:** worker/arrival **89,14%**, gather/publication **0,97%**, global frontier/dispatch **9,44%**; whole coordinator **10,41%**. Bare arrival tail chỉ **3,2 µs /0,064%**; summed worker wait **456,9 µs** không phải serial latency. Perfect divisible fixed-work/zero-delay ceiling **232,5 µs /4,62% observer wall** không chứng minh một scheduler khả thi, không bound policy có đổi tổng work.

**Model only:** mục tiêu 5% OFF là **255,8 µs/query**. Nếu giả định controller 1% OFF, budget ~**51,2 µs/query /1,62 µs/round**. Với giả định chưa kiểm được rằng coordinator cost transfer nguyên sang OFF, phải xóa ~**58,6%** của cả coordinator window để còn 5% net. Mere fixed-work balance oracle còn dưới mục tiêu trước overhead. Không cộng overlapping timers, không nhân tỷ lệ giảm logical L2 thành speedup.

**NOT_MEASURED:** perf permission probe bị từ chối ở `perf_event_paranoid=4`; không chạy profiler trên ANN, không thay quyền. Exclusive L2, local queue/visited cost, cache/stall/bandwidth/IPC không có profile hợp lệ. Worker window lớn không chứng minh distance-bound hay memory-bound. Coordinator envelope cũng chưa chứng minh một removable component ≥10% OFF. **P4 bottleneck-plus-cheap-signal condition vẫn chưa đạt.**

Đây là outcome phân biệt được **measurement validity** với **algorithm value**: không có đủ căn cứ để hứa net gain, cũng không có căn cứ để tuyên bố hệ thống không còn bất kỳ headroom nào.

## 4. P0–P6: exploratory achievements và điều kiện còn thiếu

Bảng này đối chiếu **nội dung proposal**, không cấp lại quyền chạy và không nâng official gates.

| Proposal gate / điều kiện gốc | Đã có trong exploratory scope | Chưa đạt / trạng thái cần giữ |
| --- | --- | --- |
| **P0 — freeze inputs/source/binary/host/provenance** | A0/A1/A3 artifacts, input hashes, common-engine subject, native Ryzen guards và new protocol receipts đã kiểm được. Final rehash 3.993 entries +23 pins đều khớp. | **Historical P0 HOLD**: historical Task A host/seed execution contract chưa tái dựng đủ; same-root nondeterminism không thay independent seed policy. Không relabel Ryzen thành historical host hoặc i5. |
| **P1 — compatible topology-preserving loader, valid Recall** | Common engine đọc `.pipnn`, IDs/metric/entry/topology contract; historical serial correctness/ON-OFF parity **PASS**, ~1.804.000 pair checks. V3 t0990 serial test 9/9 floor pass. | **Full P1 HOLD**, t0998 2/9 pass, 7/9 fail; V4 D1–D5 chưa phê duyệt. Serial correctness không tự cho phép mọi multiworker quality claim; A0 clean-baseline disjoint fail còn tồn tại. |
| **P2 — serial/multiwalker + counters correctness, timing separation** | p1/2/4 engine và scoped correctness/sanitizer/smoke evidence đã có theo P2-EXP authorization; p1 giữ serial path; fresh copy-only observer output/logical-counter checks pass trên fixture. | Technical implementation không phải Speed-ANN/AverSearch source-parity reproduction. Final observer **chưa equivalence**; L2/frontier/cache phase attribution chưa valid. Không đổi Full P1/P3 bằng P2 exploratory. |
| **P3 — repeated Graph×Workers, quality-controlled interaction** | Legacy H1/H2, Stage D validation grid +63 cells/5 OFF +1 ON, A1 control, flat/S ablations; tất cả slow runs giữ lại. Có conditional cohort evidence cho interaction/configuration dependence. | **P3 official CLOSED**. Independent-root replication thiếu, full exact Recall matching/selection uncertainty chưa khép, clean B1+A1 matrix chưa đủ. Không coi current64 query/3 pairs là phép thay thế full study. |
| **P4 — causal bottleneck + cheap online signal** | Source/timer audit, duplicate provenance, seed/emergent split, oracle/placebo controls; có per-round worker/arrival và coordinator windows. | **Exploratory PARTIAL / NOT SATISFIED để mở P5.** OFF phase transfer chưa valid, profiler NOT_MEASURED, cheap overlap không vượt strong controls; chưa chứng minh scheduling headroom đủ sau cost. Không nói đã giải thích đầy đủ H2. |
| **P5 — TP-CG method beats strong fixed/staged, with overhead/fallback/ablations** | Chỉ feasibility/novelty screening và scoped overlap NO-GO; không có TP-CG transition/controller implementation. | **NOT_OPENED**; không positive online matched-Recall gain, không distinct mechanism. Best-fixed flat+S+B1+A1 và staged/one-shot phù hợp vẫn bắt buộc nếu sau này có candidate thật. |
| **P6 — independent evaluation, extension, six metric groups or proper negative report** | Reproducible exploratory artifacts, scoped negative overlap report, uncertainty/threats và proposal reassessment; đáp ứng một phần negative-report path. | **NOT COMPLETED**, không P6 PASS: thiếu broader datasets/graph families, independent cohort, strong external baselines và loaded-throughput/resource characterization. Negative report không tự tạo generalization hoặc novelty. |

P4/P5 chưa đạt là lý do nghiên cứu để dừng implementation hiện tại; **không phải chờ mọi historical D-hypothesis được giải quyết**. H-V/H-G/H-C/H-F/H-QV là các lane khác, không được tự nhập vào Task D để cứu một H3.

## 5. Có khoảng trống thuật toán khác prior art không?

Đọc lại primary papers; mapping theo cơ chế, không theo tên:

| Cơ chế mà TP-CG/các hướng cứu H3 có thể dựa vào | Prior art đã có | Điều còn phải khác để thành contribution |
| --- | --- | --- |
| Local search queues, nhiều walkers, tăng width theo stage, điều chỉnh synchronization theo progress/redundancy | [Speed-ANN §§4.2–4.4](https://johnpzh.github.io/assets/papers/arXiv-2022_Speed-ANN_Zhen.pdf); [iQAN §5](https://johnpzh.github.io/assets/papers/PPoPP-2023_iQAN_Zhen.CameraReady.pdf) có staged expansion và AUP-based redundancy-aware synchronization. | Một observable/decision rule cụ thể khác các rule đó, có objective/cost semantics và failure cases; generic “topology-aware + hysteresis” chưa đủ. |
| Giảm global materialization/barrier, approximate global threshold, buffer balancing, speculative distance tasks/reuse | [AverSearch §§4.2–4.4](https://arxiv.org/html/2504.20461v2#S4) có asynchronous L-threshold, shared buffer/work stealing, maintainer/calculator separation và ready-distance array. | Không chỉ thay tên role/threshold/memoization hoặc ghép known ingredients; phải chỉ ra algorithmic difference và matched-Recall net gain. |
| Neighborhood-overlap assignment | [H3 novelty audit](H3_NOVELTY_AND_PRIOR_ART_AUDIT.md) không coi combination của partition/sketch/load heuristics là novelty. [Screening results](H3_OVERLAP_SIGNAL_SCREENING_RESULTS.md) có exact signal nhưng sketch không hơn degree/placebo; exact advantage so eligible-load chỉ ~0,11–0,12% proxy. | Cheap reliable signal + effect beyond load-aware trên cùng seeds, cost/quality contract và novelty proof. Current candidate không đáp ứng. |

Đối chiếu paper chứng minh các cơ chế **đã tồn tại**, không chứng minh mọi conditional scheduler đều đã được phát minh. Author-code/binary reproduction vẫn **UNVERIFIED** trong study này; không dùng paper speedups làm expected Task D gains. Các optimization families khác như distance prefilters/containers đã được giới hạn trong [direction review](H3_RESEARCH_DIRECTION_DECISION.md); không tự mở hướng thứ ba ở đây. Những MARGO/GLIDE/PiPNN-II links trong proposal không phải một external baseline vừa được reproduce và không được lấy làm bằng chứng novelty mới trong lượt này.

**Đáp án hiện tại:** chưa xác lập được mechanism khác Speed-ANN/iQAN/AverSearch vừa có empirical budget, cheap signal và net-gain feasibility. Tiềm năng nghiên cứu rộng hơn **OPEN/UNKNOWN**; **không có một H3 cụ thể đáng triển khai ngay**. Không đặt tên một biến thể mới chỉ để đáp ứng mục tiêu có thuật toán.

## 6. Hai kết luận độc lập

### A — Tiếp tục hướng thuật toán mới

**NO-GO mở/triển khai H3 trong phạm vi hiện tại; giữ TP-CG NOT_OPENED và original TP-CG PIVOT.** Overlap NO-GO giữ nguyên ở scope 64 IDs/graph, 6.095 rounds tổng, offline counterfactual, không online latency gain. Final three-pair measurement bổ sung observer validity limitation, không cung cấp positive algorithm evidence.

Muốn đổi quyết định trong tương lai phải có đồng thời: một removable OFF component đo hợp lệ, signal đủ rẻ dự đoán **critical-path/net** benefit, một rule khác prior art và prospective matched-Recall comparison với best fixed/staged. Không suy ra GO chỉ từ coordinator có mặt hoặc `L2 count` lớn. Không tự yêu cầu campaign mới để trì hoãn quyết định NO-GO hiện tại.

### B — Experimental systems study

**Có cơ sở tiếp tục chốt technical experimental systems report**, với contribution candidate là những kết luận **có điều kiện** về topology/configuration × scaling, sensitivity với baseline/observer, semantics của synchronization timers và negative results của scheduling hypotheses. Không gọi đây là thuật toán mới hoặc đủ tiêu chuẩn công bố.

Giữ các kết quả có giá trị sau:

1. H1 conditional scaling/absolute-latency/Recall observations, A1 control và graph-dependent S; không claim một descriptor topology gây latency độc lập.
2. H2 work/duplicate/round diagnostics và timer semantics; bỏ **cách diễn giải nhân quả** không hợp lệ của old additive decomposition, giữ raw/report lịch sử nguyên byte.
3. Flat/B1/A1 paired ablations, exact output parity, failed-quality/slow runs và uncertainty. Baseline mạnh thay đổi làm shrink “scheduler opportunity”; đó là một systems finding, không algorithm novelty.
4. H3 exact-vs-cheap/load/placebo/cost negative result và **final observer equivalence chưa đạt**, thay vì xóa các measurement failures khỏi narrative.

Để hướng tới một bài báo còn cần đặt claim cụ thể so với characterization đã có trong Speed-ANN/iQAN; strong serial + CPU intra-query implementations được reproduce công bằng; matched Recall trên nhiều operating points; dataset/graph-family khác; independent-root cohort do Task A/owner chốt semantics; valid attribution/overhead và uncertainty. Nếu claim throughput/service cần inter-query concurrency/resource accounting riêng, không inverse latency của jobs=1. Cross-host generalization cần host được duyệt khác; **i5 vẫn NOT_RUN**. Những việc này là research requirements tương lai, không authorization chạy trong lượt này.

## 7. Bước nhỏ nhất và final stop

**Ngay bây giờ:** chốt evidence và biên soạn scoped systems/negative-result report từ artifacts đã có. Không thêm run để buộc observer equivalence, không thêm graph hoặc scheduling variant. Measurement-validity gate đã thực hiện xong với outcome NOT_VALIDATED; uncertainty là kết quả cần giữ.

Nếu owner sau này muốn tái mở attribution, bước đầu là **design review của một measurement method** có khả năng đạt equivalence/phase-specific validity với quyền hiện có, trước bất kỳ real ANN process khác. Không đề nghị nới security, không sửa ±2% budget hồi tố và không tự động đổi profiler. Chỉ khi có evidence mới đáp ứng P4 lẫn novelty mới xét P5.

| Câu hỏi quyết định | Trả lời |
| --- | --- |
| Đã xác định bottleneck OFF lớn có thể cải thiện? | **Chưa — UNKNOWN**; observer cho candidate envelope, PMU/exclusive attribution thiếu. |
| Có lý do mở lại original TP-CG? | **Không theo evidence hiện tại.** |
| Có H3 khác prior art đáng implement? | **Chưa có; NO-GO hiện tại.** |
| Systems study có giá trị tiếp tục? | **Có, với claim hẹp và negative findings; publication readiness UNKNOWN.** |
| Có thí nghiệm tiếp tự động? | **Không.** Dừng tại báo cáo; future measurement/algorithm scope cần owner quyết định riêng. |

Official gates giữ nguyên: **Historical P0 / Full P1 / t0998 HOLD; P3 official CLOSED; TP-CG NOT_OPENED; i5-14600KF NOT_RUN.** V4 D1–D5 UNAPPROVED. D1 UNTESTED, D4 NOT TESTED, D6 INCONCLUSIVE trên subjects lịch sử. Không graph mới/R4/R5, không seed/binary historical changes, không H3 online hoặc large benchmark trong lượt này.
