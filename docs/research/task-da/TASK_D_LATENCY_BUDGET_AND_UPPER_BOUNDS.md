# Task D — Latency budget và các cận trên có điều kiện

Ngày: **2026-11-20**. **Còn một miền công/overhead lớn chưa phân rã được, nhưng chưa xác định bottleneck nhân quả lớn nhất của latency OFF.** Sau B1+A1, điều phối tuần tự vẫn chiếm khoảng 14% thời gian ON ở A3 p2 và 22–24% ở pilot p4. Phần worker lớn hơn nhiều, nhưng chưa tách được L2 khỏi queue, visited và memory stalls. Không thể chuyển các tỷ lệ này thành lời hứa latency gain.

Lượt này chỉ kiểm checksum, đọc source/raw, tái tổng hợp số liệu và chạy tests dataset-free. **Không chạy ANN, profiler, benchmark mới hoặc tạo graph.** Hai hướng nghiên cứu được đánh giá trong [research direction decision](H3_RESEARCH_DIRECTION_DECISION.md).

## 1. Freeze, tests và phạm vi evidence

Đã bảo toàn code instrumentation, công cụ offline, tests và báo cáo H3 NO-GO bằng commit riêng **`6bdf65f`** (`research(task-da): freeze bounded overlap screening and scoped NO-GO`, 11 tệp). Không sửa nội dung screening trước khi commit. Ba tài liệu feasibility đã nằm ở `1d38389`. Hai tài liệu B1+A1 post-review/preregistration có sẵn vẫn nguyên byte và untracked, ngoài commit này.

Tái băm **3.993 manifest entries** thuộc bảy bundle, tất cả khớp; đây là số entry kiểm tra, không phải số replicate. Cụ thể: H1/H2 227; Stage D/E 1.777; pilot B1/A1 gốc 232; pilot resume 896; narrow raw 713; narrow export 4; H3 screening 144. **23/23 pins** narrow freeze khớp, gồm evaluator lịch sử và input. Source hiện tại của H3 khớp archived identities/capture source; khác biệt CMake sau capture chỉ là target offline đã được ghi nhận trong bundle.

Tag Stage D/E vẫn peel về **`87d4a8149416b22ccf8854f72c7c72f09197cfa3`**, tag B1+A1 về **`f2cd634b837a70735c3e31e5956f0524bfc26675`**. Không di chuyển tag, rewrite history, merge hoặc ghi đè raw. Tests dataset-free kiểm lại trong lượt này: **520 collected, 507 pass, 13 skip**. Sealed Release và native ASan+UBSan+LSan logs của screening ghi 25 common +4 trace/offline tests pass mỗi build; không chạy lại native integration trong lượt audit.

| Tầng evidence | Subject và phạm vi | Giới hạn cần giữ |
| --- | --- | --- |
| [H1](H1_GRAPH_WORKER_PILOT.md), [H2](H2_WORK_OVERHEAD_PILOT.md) | R1, S8, engine set cũ; 3.000 query; 5 OFF +2 ON/cell | Recall drift, host noise; trước flat/B1/A1 |
| [Stage D/E](STAGE_D_E_REPLICATION_AND_H3_DECISION.md) | `ff46d6ac...`; A0/A1/A3 × R1–R3, p1/2/4; 63 cell | Cùng root 555; lựa chọn S/merge từ panel pilot; chưa có B1/A1 |
| [B1/A1 pilot](B1_A1_PILOT_HANDOFF_20261119.md) | `7a2685e5...`; R1 A0/A3, p2/p4, một số cell | p4 chưa replicated R2/R3; A0 disjoint Recall fail |
| [Narrow replication](B1_A1_NARROW_REPLICATION_REPORT_20261119.md) | Cùng evaluator pilot; A3-R2/R3 p2 S16, 5 block OFF | Outer CI chứa 0, quyết định HOLD |
| [H3 screening](H3_OVERLAP_SIGNAL_SCREENING_RESULTS.md) | Trace `4903d426...`; A3 p2 S16 B1+A1, **64 validation IDs/graph, 6.095 rounds tổng** | 32 development +32 held; one OFF/ON process per mode; counterfactual **offline**, **không có online latency gain** |

Không gộp latency qua các epoch/query panel/binary. R1–R3 là các invocation build riêng **cùng RNG root 555**, không phải ba independent RNG seeds. `A1` graph arm của Task A khác toggle `A1` incremental frontier của Task D.

Audit tái tổng hợp 97 configuration groups từ 591 process summaries của các phase đích và đọc timestamps của ba tệp trace. Các metadata ngoài phase đích được lọc rõ trong script. Export mới, chỉ gồm dữ liệu dẫn xuất, nằm ngoài Git: [budget.json](../../../../artifact-evidence/task-d-latency-audit-20261120/budget.json), [observed_budget.csv](../../../../artifact-evidence/task-d-latency-audit-20261120/observed_budget.csv), [source/integrity index](../../../../artifact-evidence/task-d-latency-audit-20261120/integrity.json). [CHECKSUMS.sha256](../../../../artifact-evidence/task-d-latency-audit-20261120/CHECKSUMS.sha256), 8 tệp được niêm phong, có SHA **`003a3ad68f287904c23ac8254f7deac86cff2696c65fa66fc408efcadbb7d685`**. Raw H3 manifest vẫn **`fb6b1c81dee38ed78eb5de23f589668638097faf60e4d395f6e6cc5f67ac8f15`**.

## 2. Những đại lượng có thể và không thể cộng

`T_OFF` là elapsed query latency của process OFF. `merge_time_ns` là elapsed thời gian main thread từ khi mọi worker tới đến khi hoàn tất công vòng đó, **không chỉ thao tác merge**. Ở source hiện tại nó còn gồm ON distinct tracking, visited/expanded publication, trộn/prune global frontier và chuẩn bị dispatch tiếp. Ở trace build nó còn chứa copy record. Khởi tạo local queues và local search nằm ở worker phase.

`barrier_wait_ns` là **tổng worker-nanoseconds**, cộng khoảng `t_arrived - work_done[w]` của worker hoạt động. Các khoảng này chồng nhau và chồng thời gian worker chậm vẫn tính toán. Nó không phải elapsed thời gian một barrier primitive. `sync_wait_ns` còn cộng thời gian helper đỗ trong serial merge, nên **không được cộng sync_wait + merge + barrier** thành query latency.

`barrier_wait/p` chỉ là average worker-wait. Nó không tự động là query time có thể xóa, hoặc chi phí primitive đồng bộ. Counter query-level `max(sum_round work_w)` cũng không thay cho `sum_round max(work_w)`; imbalance tổng query gần 1 không loại trừ straggler từng round.

Các bảng H2/Stage D cũ dùng `T1/DE1` làm đơn giá L2 rồi cộng với merge/wait để “giải thích excess”. Đây là **mô hình**, không phải measured distance time: T1 còn chứa queue, adjacency, visited và memory effects. Ví dụ Stage D A0 p2 S16 flat có excess ~800,9 µs nhưng tổng modeled duplicate 541,9 + merge 346,3 + barrier/p 107,9 + idle/p 0,8 ≈997 µs, residual **−196 µs**. Điều này không chứng minh một bottleneck âm hoặc xác nhận đầy đủ nhân quả. Tài liệu cũ được giữ nguyên; audit này thay cách sử dụng số liệu đó.

Tương tự, `T1/p` là scaling reference, không phải lower bound đã chứng minh cho thuật toán khác đường đi/cache/Recall. Static-S sweep không phải oracle cho mọi dynamic schedule. Phần excess so với lý tưởng không được tự gán cho graph topology, synchronization hay một D-hypothesis.

## 3. Tiến triển baseline: observed OFF và ON

H1 legacy S8/set cho mean OFF p1/p2/p4 lần lượt: A0 **5.408,9 /3.784,3 /2.438,9 µs**, A1 **5.502,3 /3.737,6 /2.414,0**, A3 **8.109,5 /6.941,9 /4.339,9**. H2 thấy A3 cần ~2,3× expansions và ~2,2× rounds so với A0/A1 ở p2, cùng merge window lớn hơn. Đây là kết quả trên baseline ban đầu, không phải ngân sách còn nguyên sau các ablation.

Stage D, mean qua ba graph builds, **trước B1+A1**, flat và fixed-S đã chọn. µs/query; B là summed worker-wait ON:

| Arm | p/S | T_OFF | T_ON | M_ON | B_ON | L2 tổng / trùng | Rounds |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A0 | 1/8 | 5.489,0 | 5.530,4 | 0 | 0 | 18.457 /0 | 0 |
| A0 | 2/16 | 3.545,4 | 3.771,7 | 346,3 | 215,9 | 22.102 /3.611 | 14,20 |
| A0 | 4/8 | 2.279,0 | 2.480,9 | 406,6 | 577,7 | 22.363 /3.804 | 14,39 |
| A1 | 1/8 | 5.534,5 | 5.492,5 | 0 | 0 | 18.511 /0 | 0 |
| A1 | 2/8 | 3.563,1 | 3.772,1 | 352,7 | 258,2 | 21.889 /3.322 | 27,60 |
| A1 | 4/8 | 2.345,1 | 2.608,5 | 420,5 | 694,2 | 22.558 /3.843 | 14,54 |
| A3 | 1/8 | 8.214,2 | 8.287,2 | 0 | 0 | 25.919 /0 | 0 |
| A3 | 2/16 | 5.741,3 | 6.113,8 | 645,8 | 460,3 | 31.111 /5.177 | 31,71 |
| A3 | 4/16 | 3.596,7 | 4.000,2 | 718,7 | 1.039,4 | 32.093 /6.220 | 16,70 |

All raw Stage D flat S8/S16 cells are exported. For context, A3 p2 S8 flat was 6.168,4 µs vs S16 5.741,3; A0 p4 S16 was 2.466,6 vs S8 2.279,0. S selection is graph/configuration dependent. These differences do not establish an adaptive-S contribution.

Latest available **flat + fixed S + B1+A1**, paired blocks for OFF, one separate ON process/cell:

| Graph | p/S | T_OFF ± SD | T_ON | M_ON (% T_ON) | B_ON | L2 tổng / trùng |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| A0-R1 | 2/16 | 3.398,6 ±80,2 | 3.727,8 | 405,0 (10,86%) | 256,6 | 19.215 /918 |
| A0-R1 | 4/8 | 2.260,1 ±24,6 | 2.506,2 | 477,7 (19,06%) | 685,7 | 19.568 /1.119 |
| A3-R1 | 2/16 | 5.133,6 ±42,6 | 5.404,8 | 770,4 (14,25%) | 477,3 | 26.497 /660 |
| A3-R2 | 2/16 | 5.296,2 ±47,4 | 5.516,6 | 794,5 (14,40%) | 471,5 | 27.051 /665 |
| A3-R3 | 2/16 | 5.249,3 ±92,4 | 5.432,6 | 778,1 (14,32%) | 464,6 | 26.586 /666 |
| A3-R1 | 4/8 | 3.629,9 ±469,2 | 3.783,8 | 892,0 (23,58%) | 1.313,0 | 26.654 /855 |
| A3-R1 | 4/16 | 3.522,9 ±166,9 | 3.869,1 | 834,8 (21,58%) | 1.109,2 | 27.891 /2.023 |

Latest same-block p1 references: A0-R1 5.523,3 µs, A3-R1 8.366,6 µs. p1 delegates to the existing serial path; B1/A1 multiworker toggles do not define a new serial algorithm. **A1-graph B1+A1 matrix, and A0/A1/A3 p4 B1+A1 R2/R3, are missing.** p4 R1 S8/S16 ablations are inconclusive; “best-fixed” is the historically selected reference, not a newly proved post-B1/A1 optimum.

B1 suppresses 87% duplicate L2 on A3-R2/R3 while OFF gain differs, 6,96% vs 3,78%; equal counter savings are not equal latency savings. Combo paired gain is 12,29% /10,08%, but primary outer CI95 **[−2,84%;25,21%]** retains HOLD. The increase in M_ON with A1 despite lower OFF latency also prevents using the old and incremental timer windows as identical causal components. R1 A0 disjoint point Recall remains 0,98940 FAIL; no universal A0/A1/A3 clean-baseline quality claim is added.

## 4. Trace wall-time conservation on the current A3 p2 baseline

Recompute directly from each timestamp, then average all 64 queries/graph. The following columns are **disjoint elapsed windows within the same trace ON query**:

```text
P = sum(release - prepare)                 observer snapshot preparation
A = sum(arrived - release)                parallel worker/arrival phase
M = sum(end - arrived)                    coordinator phase including record copy
R = query latency - P - A - M             initialization, gaps and tail
T_trace = P + A + M + R
```

µs/query:

| Graph | T_trace | P | A | M | R | Copy contained in M | M minus copy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A3-R1 | 6.294,18 | 800,58 | 4.496,84 | 972,35 | 24,42 | 190,94 | 781,41 |
| A3-R2 | 6.375,20 | 819,39 | 4.536,77 | 995,65 | 23,39 | 195,63 | 800,02 |
| A3-R3 | 6.217,37 | 794,06 | 4.438,51 | 961,83 | 22,96 | 192,03 | 769,80 |

A is **71,16–71,44%** of trace wall. It contains L2, adjacency/visited, local `std::set` work, event append, start delays and arrival observation. M minus copy is **12,38–12,55%**, still containing ON accounting and necessary publication, not pure merge. No PMU or exclusive L2/queue profiling is available to split either further.

Let worker durations be `d_w = done_w - start_w` and `a_r = arrived-release`:

| Quantity from trace, µs/query | R1 | R2 | R3 | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Summed worker barrier-wait B | 533,24 | 545,12 | 518,89 | Worker-time; not serial elapsed |
| Arrival tail `sum(arrived-max(done))` | 2,89 | 3,17 | 3,54 | Upper window for arrival observation after all recorded workers finish |
| Processing imbalance proxy `sum(max d - sum d/2)` | 264,08 | 269,44 | 257,32 | Work-duration dispersion in perturbed ON execution |
| Ideal divisible-work/zero-delay ceiling `sum(a_r - sum d/2)` | 275,64 | 280,44 | 267,83 | 4,31–4,40% of trace wall, under very strong assumptions |

The last line assumes all observed worker work can be arbitrarily split across two identical available workers, with zero start/coordination cost and fixed total processing time, while P/M/R stay unchanged. It ignores graph dependencies, queue state and per-worker S; it is **not a feasible scheduler result or an OFF ceiling**. It includes start/arrival effects already; do not add the arrival-tail or imbalance-proxy rows to it. The ~3 µs tail is distinct from the ~0,8 ms coordinator and the much larger wait accumulated by the early worker.

## 5. Bottleneck-by-bottleneck conditional upper bounds

Define a zero-cost oracle that removes exactly a specified phase's cost, preserving all other work, decisions and timing. Within that observed execution, saved wall time cannot exceed the removed critical-path phase. Moving this bound to OFF additionally requires that phase costs and cache/host conditions transfer; evidence does **not** establish that assumption. Bounds below overlap/nest and **must not be summed**.

| Bottleneck | Observed evidence | Upper bound with conditions | OFF status |
| --- | --- | --- | --- |
| **All exact-distance computation** | ~26,5–27,1k L2/query after B1, no exclusive distance timer | On the trace, all L2 lies in A+R: cap **4,46–4,56 ms**, **71,5–71,8%** T_trace, if other phases fixed. This is a broad envelope containing much unrelated work. | **UNKNOWN** exclusive share; no nontrivial distance-only OFF bound |
| **Global coordinator/merge/frontier preparation** | M_ON ~0,77–0,79 ms at p2; p4 R1 ~0,83–0,89 ms | Erasing the entire measured M_ON gives caps **14,25–14,40% ON** at A3 p2 and **21,58–23,58% ON** at p4. Trace M excluding copy gives a separate **12,38–12,55% trace** cap. Includes counters/mandatory work, so an implementation cannot claim the entire cap. | Potentially material envelope; pure merge, publication and OFF share **UNKNOWN** |
| **All frontier/search-container maintenance**, including local queues | Local queue operations interleaved with L2; global work in M | Broad trace envelope A+(M-copy)+R = T_trace−P−copy, about **84,1–84,2%**. This also contains L2/visited and is deliberately loose. | **UNKNOWN**; cannot treat the worker remainder as distance-only or queue-only |
| **Bare arrival synchronization/observation** | Explicit arrival tail ~2,9–3,5 µs/query | With worker completion times fixed, zeroing this tail saves at most **0,046–0,057% trace wall**. Does not remove publication/merge or make the slow worker faster. | Not a demonstrated large primitive cost; old scalar B only supplies a very loose tail cap, not B/p elapsed savings |
| **Imbalance/straggler work** | Per-round timing above; no p4 round trace | Ideal divisible-work/zero-delay cap **268–280 µs**, **4,31–4,40% trace**; feasibility unproved. At p4 only aggregate counters/timers exist. | **UNKNOWN** OFF; p4 ceiling beyond trivial query time not identified |
| **Duplicate distance evaluations** | A3 p2 duplicates 2,46–2,51% in narrow, 2,44–2,66% screening | Fixed observed-path ownership oracle removes at most **469–483 critical-worker L2/query**, **3,27–3,43% of summed max-worker L2**. This is a count/work ceiling. Its time ceiling still lies inside A+R, not the counter percentage. | **UNKNOWN** time. For uniform marginal cost c, conditional savings ≤c×saved critical L2; c is not measured |
| **Memory/cache effects** | CPU/L3 topology, RSS and host telemetry; no valid cache-miss/stall/bandwidth profile | No nontrivial isolated bound; conservative cap is **whole T**. Memory stalls may occur in distance, queue, visited and merge, already inside their windows. | **UNKNOWN**; do not call the search memory-bound from these data |
| **Instrumentation** | Explicit P+copy ~0,99–1,02 ms; trace vs counters ON +11,44–13,81% descriptively | Zero-cost snapshot+copy oracle, other timing fixed, removes at most those windows. Total observer also affects append/accounting/cache; its full exclusive cost is not isolated. | **UNKNOWN** causal overhead. Do not subtract P+copy from trace to invent OFF latency |

For duplicate-only improvement, a 5% saving of screening frozen OFF would require roughly **542–565 ns per eliminated critical-path L2** before any lookup/publication overhead, assuming the optimistic ownership oracle and uniform cost. There is no measured marginal-distance cost to validate this assumption. `worker_ns/max_L2` includes queue and memory effects and is not that measurement. Seed–seed duplicates account for only ~0,33% total L2; the rest are mostly emergent–emergent. Grouping seed overlap cannot claim all duplicate ownership savings.

Observed ON−OFF differences after B1+A1 at A3 p2 are about **3,5–5,3%**, but ON is a separate process and host state differs; elsewhere A1 p1 ON is even below mean OFF. Such comparisons characterize measurement uncertainty, not a pure instrumentation tax. H3 four-mode timing was ordered and unreplicated; no online algorithm gain was measured.

## 6. What remains UNKNOWN and the smallest proposed measurement

The audit does **not** identify whether L2/memory or local/global frontier work is the largest removable OFF cost. It does identify why counting duplicates or dividing summed wait is insufficient. The clean coordinator remains large enough to investigate as a systems question, especially p4; that is not evidence for a novel H3 mechanism.

**Proposed next step only, NOT RUN:** a narrow phase/sampling audit on A3-R1 p2 S16 flat+B1+A1, using the same locked validation panel and frozen beam, before expanding to any other configuration. No scheduler or distance semantics changes.

1. Use one separate symbolized build, record flags/hash, retain the frozen executable; verify exact outputs/non-time counters. Add only coarse boundaries around coordinator accounting/publication versus actual global merge/frontier/dispatch. No clock on every L2/edge and no new event trace.
2. At most three paired baseline/observer processes on the existing 64-query panel, with fixed warmups and alternating order; all guarded/sequential on Ryzen. This is a measurement-validity check, not a new performance claim. Predefine a ±2% observer-drift budget and require the paired process-level CI to lie entirely within it; a wide interval that merely includes zero is insufficient. Otherwise report UNKNOWN and redesign the observer; do not treat queries as independent process repeats.
3. If existing permissions permit, at most one short sampling pass on the symbolized process to distinguish inlined distance, queue and visited/adjacency code; include PMU stalls/cache/bandwidth only if event support, multiplexing and attribution are valid. Keep samples and owned process identities. Permission failure or too few attributable samples remains UNKNOWN; no security/sysctl changes or automatic longer campaign.
4. Evidence gate: require non-overlapping phase conservation, usable sample uncertainty and an exclusive removable component plausibly ≥10% of OFF before commissioning a focused systems optimization. Novelty remains a separate gate; even this result would not open H3. If the largest exclusive component cannot clear a 5% net-gain ceiling after a conservative overhead budget, stop that optimization line.

No profiler was implemented or launched in this turn. This plan is the smallest measurement that could change the direction decision; adding more H3 overlap query repeats would not resolve these unknowns.

## 7. Preserved decisions

Overlap-aware H3 **NO-GO within its screened scope**; original TP-CG **PIVOT / NOT_OPENED**. Historical P0 / Full P1 / t0998 **HOLD**; V4 D1–D5 **UNAPPROVED**; P3 Official **CLOSED**; i5-14600KF **NOT_RUN**. D1 **UNTESTED**, D4 **NOT TESTED**, D6 **INCONCLUSIVE** on their historical subjects. PAPER_STOCK / PAPER_GCC13_PORTABLE / MODERN_GOLDEN and H-V/H-G/H-C/H-F/H-QV remain distinct. No new algorithm, graph or official pass is created by this audit.
