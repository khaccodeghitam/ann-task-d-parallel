# H3 — Overlap signal screening plan

Ngày: **2026-11-20**. Trạng thái **DESIGN ONLY / NOT RUN**. Quyết định hiện tại: **MORE EVIDENCE**, H3 = **NOT_OPENED**. Không có H3 prototype, trace binary mới, sidecar mới, benchmark hay graph mới được tạo trong lượt này.

## 1. Câu hỏi nhỏ cần trả lời

Trên baseline **flat + fixed S + B1+A1 + round-robin**, overlap giữa neighborhood của các seed sắp dispatch có dự báo được phần công trùng **trên worker chậm nhất** không, và còn lợi ích sau chi phí đọc metadata/lập lịch không?

Tách bốn tầng bằng chứng: (i) cấu trúc adjacency; (ii) proxy một hop trên snapshot thật; (iii) cơ chế search nhiều bước; (iv) latency ANN OFF ở Recall matched. Chỉ (iv) cho phép kết luận real latency savings. Offline savings ở (ii) không phải throughput ANN; correlation ở trace ON không phải causal speedup.

## 2. Những gì evidence hiện có thực sự cung cấp

Đã kiểm hash [freeze và raw narrow](../../../../artifact-evidence/p2-b1-a1-narrow-20261119/frozen.json), đọc [report](B1_A1_NARROW_REPLICATION_REPORT_20261119.md), [counter schema](counter_schema_p2.json) và [P2 engine](../../../research/task_da/search_common/p2_engine.hpp). JSONL hiện có theo query, không có danh sách seed/visited/expanded IDs theo round hoặc latency từng round.

Đọc lại đủ 3.000 query ON combo mỗi graph, không chạy evaluator:

| A3 | Tổng L2/query | Unique L2/query | Duplicate L2/query | Duplicate / tổng L2 | Rounds/query |
| --- | ---: | ---: | ---: | ---: | ---: |
| R2, beam 986 | 27.050,668 | 26.386,014 | 664,654 | 2,457% | 32,087 |
| R3, beam 966 | 26.585,618 | 25.919,429 | 666,189 | 2,506% | 31,415 |

Đây là **observed historical counters, tái tổng hợp**, không phải signal overlap mới. B1 ghi mọi `local_newly_evaled` vào `settled_epoch_` ở barrier; trong round mỗi worker có `local_seen` riêng. Source vì thế hỗ trợ cơ chế collision nội round còn lại. Chưa biết collision do các seed dispatch trực tiếp, do các đỉnh phát sinh chen lên đầu queue, hay cả hai. Duplicate expansions cũng khác duplicate distance evaluations.

Không lấy graph-wide clustering coefficient, overlap của top-10 output hay seed ngẫu nhiên làm bằng chứng thay cho frontier thật. Không thể phục hồi frontier duy nhất từ output/counters hiện có. `max(sum_round work_w)` từ counter query cũng không thay cho `sum_round max(work_w)`.

Nếu chỉ xóa cùng lượng duplicate, giữ mọi thứ khác và giả định chi phí L2 đều nhau, mức tiết kiệm **tổng công L2** tối đa xấp xỉ 2,5%. Đây không phải cận latency chung: critical path, locality và số expansion/round có thể đổi. Muốn gain latency 5% cần chứng minh thêm cơ chế, không nhân tỷ lệ duplicate thành kỳ vọng speedup.

## 3. Panel nhỏ và ranh giới thực thi được đề nghị

Mọi bước dưới đây là phạm vi đề nghị cho owner xem xét, chưa phải lệnh thực thi được kích hoạt. Chủ ý là một observer nhỏ dành cho câu hỏi này, không tạo tracing/scheduling framework.

1. Chỉ graph **A0/A1/A3 × R1–R3 hiện có**, SHA từ [manifest V3](experiment_manifest_v3_reconciled.json), không chỉnh adjacency hoặc serialization. Bắt đầu A3-R1, sau khi observer hợp lệ mới A3-R2/R3. Chỉ mở A0/A1 nếu A3 chưa bị bác hoặc cần negative control đã định trước.
2. Primary duy nhất `p=2, S=16, flat, B1+A1, K=10, jobs=1, entry=0`. Giữ beam A3 R1/R2/R3 = 970/986/966. Khi mở A0/A1, lấy nguyên beam `S16,p2` của từng graph ở calibration Stage D đã freeze; xuất thành bảng/hash trước khi trace. Không tune theo overlap hoặc test. Không dùng p=4 như một vòng tìm gain thay thế nếu p=2 thất bại; nó cần amendment riêng.
3. Lấy **64 query từ val_10k** theo byte SHA-256 của ASCII `task-d-h3-overlap-screen-v1/<decimal-ID>`, hòa theo ID; 32 đầu là development, 32 sau là screening panel khóa. Cùng ID/thứ tự cho mọi graph. Khóa ID/hash trước capture. Validation đã từng được xem, nên gọi đúng exploratory, không gọi unseen test.
4. Giới hạn 128 round được ghi/query, buffer tối đa 8 MiB/query, disk tối đa 512 MiB/graph và tổng 4,5 GiB nếu tới đủ chín graph. Không mở rộng quota sau khi thấy tín hiệu. Nếu chạm cap, dừng ghi, để search baseline kết thúc; ghi overflow và số round/event thiếu. Nếu cần dừng study vì guard, giữ mọi output. Không bỏ query chậm/incomplete; phân tích toàn query chỉ trên phần complete, báo coverage/censoring và không GO nếu cap làm thiếu bằng chứng quan trọng.
5. Trace/search tương lai chỉ chạy tuần tự trên Ryzen 4650U native với guard hiện có đã xác minh sensor/AC/PID namespace, lock và telemetry; không chạy i5. Guard từ chối start Tctl ≥85°C, dừng ≥95°C theo protocol đã khóa. Không đổi fan/power/affinity hệ thống. Lượt này chỉ đọc/checksum, không dùng quota chạy ANN.

Các output tương lai dùng thư mục evidence **mới** bên ngoài Git, raw không ghi vào bundle cũ; repo chỉ nhận summary, schema, identity và relative links. Ghi source commit + diff SHA, compiler/flags, observer/Release SHA, input/graph/package/protocol/panel SHA, guard identity và command/env. Binary baseline đã freeze giữ nguyên.

## 4. Observer tối thiểu, không đổi kết quả search

Các điểm đọc đề nghị dựa trên source hiện tại: dispatch seed ở `init_seeds`, worker loop `run_worker_round`, `local_newly_evaled`, merge sau `done_seq`. B1 đọc global settled cố định trong round và chỉ main thread công bố khi tất cả workers hoàn tất. Không thêm shared visited, đổi queue, merge, tie-break, S hay worker assignment trong capture.

| Record | Nội dung cần có | Cách giới hạn/không tác động quyết định |
| --- | --- | --- |
| Query header | Graph/query/beam/engine IDs, result fingerprint, capture status | Một lần/query |
| Trước release round | Round ID; đúng ordered dispatched seeds `(rank,ID,L2,worker)`; global worst/full-beam; frontier fingerprint | Copy tối đa p×S=32 seeds; không quét/copy toàn beam để làm scheduler |
| Eligible snapshot | Với mỗi arc của dispatched seed, bit `settled_epoch[nbr]==q_epoch` ở đầu round | Đọc cùng trạng thái trước release; lưu bitmask, adjacency lấy lại từ graph immutable; không copy visited 1M phần tử/round |
| Sau local loop | Expanded IDs theo thứ tự, phân loại dispatched-seed/emergent; L2 events `(parent,neighbor)` theo worker; local counters | Append vào buffer riêng đã cấp phát trước; không atomics/I/O/clock trên từng cạnh |
| Biên thời gian | `t_prepare`, `t_release`, `t_start[w]`, `t_done[w]`, `t_arrived`, `t_merge_end` | Clock monotonic chung; cùng định nghĩa ở mọi record |
| Sau merge | Next frontier/dispatch fingerprint và final output | Chỉ kiểm toán; không feed ngược vào search |

Ghi cả chi phí chuẩn bị/copy observer riêng. Không thêm barrier trong worker loop, không để worker đọc record của worker khác. Flush sau query, ngoài cửa sổ search latency; chi phí append vẫn có thể perturb cache/thời gian, vì vậy trace timing chỉ là ON. Khi buffer đầy, cờ overflow ngừng ghi, không đổi đường search.

Observer phải qua dataset-free synthetic parity rồi bounded panel parity trước mọi phân tích: frozen OFF, observer compiled-out, counters ON, trace ON phải có **identical ordered top-10 IDs và squared L2** từng query; ON/trace còn phải khớp expansions, total/unique/duplicate L2, rounds và frontier/expanded fingerprints khi có. Dùng kiểm tra độc lập số L2 và counter conservation. Nếu mismatch, dừng và sửa observer trong phạm vi riêng, không diễn giải thành kết quả H3. Thiết kế dùng thread-local buffers tránh race; “observer không đổi search” là acceptance criterion, chưa được chứng nhận bởi tài liệu này.

### Phân rã thời gian

```text
prepare_r = t_release - t_prepare
arrival_span_r = t_arrived - t_release
worker_work[w,r] = t_done[w] - t_start[w]
dispatch_delay[w,r] = t_start[w] - t_release
peer_wait[w,r] = max(0, t_arrived - t_done[w])
merge_r = t_merge_end - t_arrived
round_wall_r = t_merge_end - t_prepare
```

`sum_w peer_wait` là worker-nanoseconds, không được cộng thêm vào `round_wall`. `arrival_span` chứa dispatch/skew/coordination; không đồng nhất với `max worker_work`. `merge_time_ns` lịch sử của incremental đã chứa chuẩn bị dispatch khác full; cần timestamps mới tách rõ phần đó, không sửa nhãn dữ liệu cũ.

## 5. Exact overlap và liên hệ với công thực

Cho ordered seed set `F_r` tại synchronization boundary; `V_r` là settled đầu round. Định nghĩa `E(s)=set(N_out(s))\V_r`, đồng thời giữ raw arc degree riêng vì graph có thể chứa duplicate arcs. Với assignment `A`, dùng:

```text
U_w(A) = union_{s assigned to w} E(s)
D_seed(A) = sum_w |U_w(A)| - |union_w U_w(A)|
M_seed(A) = max_w |U_w(A)|
J_seed(i,j) = |E(i) intersect E(j)| / |E(i) union E(j)|
```

Empty union có Jaccard quy ước 0 và cờ empty. Báo cả overlap thô `N_out` và eligible overlap; không chỉ số Jaccard dễ che kích thước tuyệt đối.

Từ trace tính `L2_w,r`, max/imbalance, duplicate IDs giữa worker, neighbor attempts, expansions, queue insertions và tỷ lệ dispatched seeds thực sự được pop. Phân loại duplicate theo các parent tạo L2 event: seed–seed, seed–emergent, emergent–emergent. Mỗi event dư chỉ tính một lần theo worker/event order khóa; đối với p=2, giao tập L2 hai worker cho phần trùng nội round. Đối soát tổng query với counters cũ; các lượt entry/initial fanout được ghi riêng, không gán vào một round giả.

Trên RR trace kiểm tra liên hệ `D_seed`, `M_seed`, eligible/raw degree và phase với: actual duplicate L2, `max L2_w,r`, `max worker_work`, peer-wait và round wall. Báo scatter/bin summaries, Spearman và phân tích phần dư có kiểm soát số seed/degree/visited fraction/round phase; chỉ dùng model tuyến tính nhỏ có cross-validation theo **query**, không fit một profiler tổng quát. So sánh degree-only predictor với degree+overlap bằng held-panel error. Nếu overlap không thêm khả năng dự báo ngoài degree, nó chưa có cơ sở làm scheduler mới.

Không coi các round/query là independent graph replicates. Tóm tắt theo query trước, ghép cặp cùng round; bootstrap toàn query, giữ mọi round của query trong cùng resample. Báo riêng mỗi graph; R1 là development, R2/R3 kiểm tra chuyển giao. Ba graph cùng RNG root và cùng query pool đặt giới hạn outer inference; không pool hàng nghìn round thành CI có hàng nghìn replicate.

## 6. Counterfactual offline trên cùng seed set

Mọi policy nhận **cùng F_r, V_r, budget và cap seed/worker**. Seed set toàn round và rank order đầu vào không đổi. Mỗi worker nhận floor/ceil(m/2) seed, local initial order vẫn `(L2,ID)`.

| Policy | Quy tắc offline khóa trước | Vai trò |
| --- | --- | --- |
| RR | Rank 0-based `i % 2` | Mapping frozen flat+B1+A1; RR và baseline đầy đủ là một arm, không đếm hai lần |
| Degree/load-aware | Theo rank pairs; xét hai orientation, chọn lexicographic `(max cumulative sum raw-degree, imbalance)`, hòa RR | Đối chứng rẻ cùng rank constraint, không dùng overlap |
| Exact eligible-load | Cùng quy tắc nhưng degree là `|E(s)|` | Đối chứng offline có thông tin visited; không gọi là online miễn phí |
| Exact overlap, quartet | Quy tắc quartet kế thừa post-review, thay popcount bằng cardinality exact; chọn `(max local union, sum local union)`, hòa RR; tail RR | Kiểm tra ceiling của đúng heuristic đang được đề xuất, không phải oracle tối ưu toàn round |
| Exact overlap, accumulated | Cùng rank-pair orientations, tính marginal union với **mọi seed đã gán trong round** | Phân biệt mất lợi ích do chỉ nhìn quartet với thiếu tín hiệu topology |
| Signature-128 quartet | Mô phỏng nguyên quy tắc post-review, chữ ký hash adjacency thô, cùng tie-break | Đo approximation error của candidate có sẵn; chưa xây sidecar toàn graph |
| Signature placebo | Hoán vị chữ ký giữa node cùng raw degree bằng thứ tự hash ID đã khóa | Cùng chi phí/proxy-degree, phá liên hệ topology |

Quartet kế thừa nghĩa là với `a,b,c,d` theo rank: giao `a,b` cho 0/1; chọn RR hoặc đổi chỗ `c,d`, mỗi worker nhận một seed từ mỗi rank pair; điểm của quartet độc lập các quartet khác. Không được báo local optimum của từng quartet như optimum của toàn round. Candidate khác chỉ là phép so sánh proxy, không được tự nâng thành H3.

Để có ceiling rõ, ở p=2 và m≤32 có tối đa **2^16 rank-pair orientations**; cố định orientation cặp đầu nhờ worker symmetry khi mục tiêu đối xứng. Có thể duyệt exact trên tối đa tám round chọn trước bằng quantiles vị trí round/query của panel, chỉ offline. Báo objective tối ưu và tie policy; không gọi đó là optimum của multi-step ANN. Nếu quá budget thì không chạy solver, báo UNKNOWN; không dùng heuristic làm chứng minh thiếu headroom.

Tính cho từng assignment `ΔD_seed`, `ΔM_seed`, arc-load, imbalance, seed-count/rank distribution, tỷ lệ tốt hơn/bằng/tệ hơn RR và degree. Tổng hợp **toàn round union**, không cộng pairwise overlaps vì láng giềng chung nhiều seed sẽ bị đếm quá mức. Không dùng ground truth hoặc query distance bổ sung để chọn assignment.

**Giới hạn counterfactual:** trong engine thật, newly discovered candidate có thể đẩy một dispatched seed ra sau ngân sách S. Vì vậy `D_seed` không phải upper bound đã chứng minh cho actual duplicate toàn search, và exact one-hop policy không tạo được counterfactual latency/Recall nhiều bước. Không tái sử dụng timestamp RR làm “thời gian policy mới”. Replay đổi đường đi cần một phạm vi prototype và distance computation riêng đã được owner duyệt.

## 7. Cost model, bộ nhớ và trường hợp xấu

Mô hình dự đoán theo round, hệ số chỉ được fit trên development ON rồi khóa:

```text
C_w,r = c_L2 * L2_w,r + c_arc * attempts_w,r
        + c_queue * queue_ops_w,r + residual_w,r
T_r ≈ C_prepare,r + C_schedule,r + max_w(C_w,r + dispatch_delay_w,r)
      + C_coord,r + C_merge,r
predicted_net_saving = predicted_RR_critical_work
                       - predicted_policy_critical_work - incremental_schedule_cost
```

Không trừ summed barrier-wait lần nữa. Các hệ số phụ thuộc cache/host; fit residual lớn hoặc không chuyển giao được là MORE EVIDENCE, không bù bằng claim locality chưa đo.

Chi phí exact union online là `O(sum degree(seed))` đọc arc và lookup visited trước search, tối đa 2.048 arc/round ở 32 seed, header max-degree 64; all-pairs naive tới 496 cặp. Đây là phí tuần tự/đọc lại adjacency, không miễn phí. Exact solver chỉ dành offline.

Chữ ký kế thừa: 128 bit/node, **16.000.000 byte/graph** (15,26 MiB), dựng một lượt `O(n+m)` cạnh, không tính vào ANN online nhưng phải báo build time/amortization nếu sau này dùng. Chỉ load graph sidecar đang xét. Mỗi round tối đa 512 byte signature payload, có thể chạm tới 32 cache line rời (~2 KiB ở line 64 byte), cộng OR/popcount, branch, degree metadata và seed reorder. Tổng bộ nhớ gồm sidecar, alignment/header/checksum và scratch; không chỉ payload.

Hash đề nghị để khóa phép simulation nếu được duyệt: `bit = low7(SHA256(ASCII "task-d-h3-adj128-v1/<neighbor-ID>"))`; tính ngoài search, bit order little-endian trong 16 byte. Cùng mapping trên mọi graph, không chọn salt theo kết quả. Đây là chữ ký occupancy, **không phải MinHash**, không cho Jaccard unbiased. Với u ID khác nhau, occupancy kỳ vọng `128*(1-(127/128)^u)`; u=128 chỉ khoảng 81 bit, u=512 gần 126 bit. Collision, raw-vs-unvisited mismatch và OR toàn round gần bão hòa có thể phá tín hiệu. Đánh giá signature dựa trên cùng exact sets; không sửa số bit trên screening panel để cứu kết quả.

Budget đề nghị cho giai đoạn feasibility sau này: scheduler+metadata online tổng/query không quá **1% baseline mean OFF** và không quá **20% predicted gross critical-work saving** trên panel development. Hai ngưỡng là tiêu chuẩn nghiên cứu đề nghị, chưa có số đo hoặc authorization. Nếu không đạt, bỏ sidecar hoặc fallback RR; không che chi phí bằng timing chỉ sau dispatch. Báo cả cold/warm metadata costs, p50/p95 và trường hợp query không có ích; microbenchmark scheduler sẽ không được gọi ANN speedup.

Các falsifier/counterexample cần giữ:

- Overlap bằng 0 hoặc mọi neighbor đã settled: RR cùng công, scheduler chỉ thêm phí.
- Duplicate chủ yếu từ emergent–emergent: seed one-hop grouping không chạm đúng nguồn.
- Ít seed hoặc worker gần hết việc: sorting/metadata không có thời gian hoàn vốn.
- Degree-only đã đạt cùng critical work: topology không thêm giá trị.
- Gom overlap giảm tổng L2 nhưng tăng max-worker work. Ví dụ bốn seed đều degree 20: `N(a)=N(c)=X`, `|X|=20`; b,d mỗi seed có 5 phần tử của X không giao nhau và 15 phần tử riêng. RR `(a,c)|(b,d)` cho union 20/40, D=10, M=40; đổi c,d cho 35/35, D=20, M=35. Ít duplicate hơn vẫn chậm hơn trong mô hình chi phí union.
- Rank-pair constraint không bảo đảm Recall: grouping có thể giảm đa dạng đường, thay seed thực được pop, tăng rounds hoặc bỏ một nhánh hứa hẹn. Offline one-hop không định lượng được nguy cơ này.
- Chữ ký collision, footprint/cache miss hoặc việc tính overlap trước release làm tăng đường tuần tự. Không lấy saved work của worker vốn đến sớm để dự đoán giảm latency.

## 8. Quy tắc quyết định sau screening, chưa áp dụng

| Quan sát ở panel đã khóa | Quyết định đề nghị |
| --- | --- |
| Observer/raw thiếu hoặc cap/parity/cost chưa hợp lệ | MORE EVIDENCE; không suy ra negative khoa học |
| Exact rank-constrained ceiling không giảm M_seed trên A3-R2/R3 và không có liên hệ với actual critical work | NO-GO cho seed one-hop overlap scheduling trong phạm vi này |
| Exact có ích nhưng chữ ký thật không hơn placebo/degree, hoặc net model ≤0 vì overhead | NO-GO cho candidate signature-128; không tự đổi thuật toán để cứu H3 |
| Degree baseline giải thích toàn bộ cải thiện | NO-GO cho claim đóng góp overlap; chỉ còn tối ưu baseline |
| Tín hiệu chuyển giao ở R2/R3; overlap dự báo tốt hơn degree; net modeled saving có query-bootstrap CI95 lower >0 và point ≥5%; budget đạt; novelty argument khác generic heuristic còn đứng vững | Đề nghị GO TO PROTOTYPE cho owner; H3 vẫn chưa mở trước phê duyệt |
| Các trường hợp còn lại, uncertainty lớn hoặc chỉ một graph thuận lợi | MORE EVIDENCE, không thêm repeats/chọn panel theo gain |

Ngưỡng 5% là minimum useful **modeled query-level** signal đề nghị, không phải expected gain; phải khóa trước thu trace. CI ở đây có điều kiện trên graph và query panel, chưa giải quyết độc lập R1–R3. Không đóng cả họ topology nếu một proxy thất bại; NO-GO có phạm vi rõ như bảng.

## 9. H3 testable chỉ sau tín hiệu và phê duyệt riêng

Hiện chưa đủ bằng chứng để chốt H3 hoặc chọn một assignment mới. Nếu qua mục 8, hồ sơ xin prototype phải khóa một rule duy nhất từ screening: seed eligibility/rank constraint, marginal cost, order/ties, signature/hash, cap, fallback và điều kiện bảo đảm dữ liệu. Fallback tối thiểu là **RR nguyên trạng** khi ít hơn bốn seed, thiếu/invalid metadata, model không vượt budget/margin hoặc predictor chưa được calibration. Quyết định fallback chỉ dùng thông tin đầu round và ngưỡng khóa trên development, không oracle về latency tương lai.

Protocol prototype tương lai cần:

- Baselines RR trên fixed flat+B1+A1; degree/load-aware cùng constraint; generic balanced overlap heuristic; legacy flat+fixed-S không B1/A1 chỉ làm mốc phụ. Staged/AUP phù hợp khi claim mở sang đổi sync/width; phải có arm riêng cùng baseline sạch, không gộp staged vào overlap arm.
- A3 trước; R1 development, R2/R3 panel khóa; không chọn graph tốt. A0/A1 chỉ kiểm transfer sau gate, và A0-R1 cần quality gate riêng vì fail lịch sử. Không dùng R4/R5 để rescue H3 hoặc ngược lại.
- Calibrate beam riêng từng arm chỉ trên validation để matched Recall@10: floor LCB95 ≥0,990 theo quy ước lịch sử và point span ≤0,0001; khóa beam trước test. Nếu cùng beam có parity thì báo; không giả định parity cho đổi worker. Test không chọn beam. Output đầy đủ, distances kiểm độc lập; thiếu chất lượng dừng trước timing.
- Test panel mới đối với selection P2/H3, liệt kê exclusions và SHA trước mở kết quả; thừa nhận toàn query pool từng được P1 xem. ON counters/trace và OFF latency chạy riêng. OFF phải khớp ON **trong cùng arm**, không bắt buộc IDs khác arm giống nhau nếu Recall matched hợp lệ.
- Tối thiểu năm block OFF paired/graph, arm order cân bằng khóa trước; không thêm lượt do CI rộng. Mean latency là endpoint chính, p50/p95 và work là phụ. Ghi scheduler cost trong OFF wall time. Guard tuần tự, giữ mọi lượt chậm/lỗi; thiếu block hoặc guard trip là HOLD.
- Ablations: exact vs sketch; overlap vs degree; signature placebo; rank constraint; fallback on/off; chi phí metadata có mặt nhưng quyết định RR. Memo distance là đối chứng cơ chế mạnh nếu mở claim tránh shared lookup, nhưng cần thiết kế parity/memory riêng và phê duyệt.
- Báo paired gain theo process block, CI95 trong graph, outer graph means trọng số bằng nhau có caveat same root; query rows/rounds không tăng n_outer. Tách predicted work, actual ON work và actual OFF gain; báo cả lost Recall, negative cases, build/space cost và uncertainty.

## 10. Trạng thái kết thúc lượt này

**MORE EVIDENCE** do chưa có snapshot để thực hiện phép kiểm falsifiable. Không có số liệu overlap/round latency mới, không GO TO PROTOTYPE, không scientific NO-GO giả tạo. Original TP-CG giữ **PIVOT**. Historical P0/Full P1/t0998 **HOLD**, V4 D1–D5 **UNAPPROVED**, P3 **CLOSED**, H3 **NOT_OPENED**; D1/D4/D6 giữ **UNTESTED / NOT TESTED / INCONCLUSIVE**. [Novelty audit](H3_NOVELTY_AND_PRIOR_ART_AUDIT.md) và [R4/R5 feasibility](TASK_A_R4_R5_FEASIBILITY_REVIEW.md) là các quyết định riêng.
