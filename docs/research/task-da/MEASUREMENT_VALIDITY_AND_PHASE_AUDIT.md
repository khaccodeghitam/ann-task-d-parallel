# Task D — Final measurement-validity and phase audit

Ngày: **2026-11-20**. Scope: **EXPLORATORY_HOST_SPECIFIC**, Ryzen 5 PRO 4650U, A3-R1, p=2, S=16, beam=970, flat+B1+A1, RR, jobs=1, đúng 64 validation IDs của H3.

**Kết luận: correctness PASS; equivalence của observer với frozen OFF NOT_VALIDATED.** Ba cặp cho thay đổi latency observer −1,72%, CI95 **[−2,85%; −0,57%]**, không nằm hoàn toàn trong budget ±2% đã đăng ký. Vì vậy chưa có phân rã exclusive của latency OFF đủ điều kiện để mở một scheduler mới. Profiler bị từ chối bởi quyền hiện có: **L2/frontier-in-worker/cache-stall profiling NOT_MEASURED**. Không đổi security settings và không chạy thêm lượt để cứu gate.

## 1. Freeze và evidence identity

- Đã review và commit riêng hai báo cáo [latency budget](TASK_D_LATENCY_BUDGET_AND_UPPER_BOUNDS.md) và [research direction](H3_RESEARCH_DIRECTION_DECISION.md) tại **`32160b6370e66004a76f23547898ee026a752cb8`**. Commit trước **`6bdf65f`** bảo toàn H3 instrumentation/offline tools/NO-GO.
- Trước đo, rehash **3.993 entries của bảy historical bundles**, **23/23 narrow frozen pins**, và H3 source identities: tất cả khớp. [Integrity receipt](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/integrity.json). Hai tài liệu B1 post-review/preregistration có sẵn vẫn nguyên byte, ngoài commit Stage 1.
- Frozen OFF binary SHA256: **`7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1`**. Không rebuild/ghi đè executable này hoặc source common engine. Stage D/E tag vẫn peel về `87d4a8149416b22ccf8854f72c7c72f09197cfa3`, B1+A1 về `f2cd634b837a70735c3e31e5956f0524bfc26675`.
- Graph SHA256 **`0fff20ec47502c675c4905787d319390e49fa5bee856ac16c814c74697c5fbb2`**. Panel SHA256 **`a19636b81c0b1197184cf1395f1decd50bd800993435d5e272c9805e5cb93545`**. Base/query/GT được xác minh theo input manifest và frozen pins. Warmup giữ nguyên 100 validation IDs; không tuning/test-policy selection.
- Observer là một **copy riêng** của source hiện có, build GCC 13.3, `-O3 -DNDEBUG -g -std=c++17 -Wall -Wextra -Wpedantic -Werror -pthread`. SHA256 **`3e59c909c4f70d1f2a4ad18e986c275754c00d5aacac5de941b9bfd76b295f67`**. [Build identity](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/observer/build_identity.json), [exact patch](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/observer/observer.patch). `-g`, changed field/code layout và clocks là một combined build/observer intervention; không giả định chỉ clocks có thể gây drift.

Raw mới ở **`../artifact-evidence/task-d-final-measurement-validity-20261120/`**, ngoài Git; [manifest](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/CHECKSUMS.sha256) niêm phong **74 tệp**, SHA256 **`1af5626e530bf0bd37e4977c3dae18b1e0860f3c29d1205dce4679e95694098f`**. Có plan trước đo, command/host/process receipts, binary/source/patch, JSONL, checkpoints, tests và analysis. [Final identities](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/final_identities.json) phân biệt nguồn frozen với các tool mới chưa commit lúc chạy.

## 2. Thiết kế đo và correctness gate

[Plan đã khóa trước process đầu](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/preregistered.json): đúng **3 cặp /6 real ANN processes**, thứ tự `OFF→observer`, `observer→OFF`, `OFF→observer`. Mỗi process 100 warmups +64 query; CPU list giữ nguyên protocol `0,2`. Không điều chỉnh host, fan/power/governor/SMT/security; không process termination ngoài process group thuộc watchdog. Không retry hoặc loại lượt chậm.

Observer chạy **logical counters OFF**, cộng các clock ở biên round/worker/coordinator vào scalar tổng query. Không có clock ở mỗi L2/edge, không lưu candidate/neighborhood/event trace và không đổi assignment, visited, pruning, termination hay precision. Nó thêm 11 `uint64`/result, hai timestamps/worker và khoảng tám clock reads/round khi cả hai worker hoạt động. JSON được serialize ngoài search interval. Giá trị `phase_off` nghĩa là counters OFF trong observer build, **không đồng nhất với frozen OFF**.

Với trần sáu process, cả ba cặp dành cho validity của observer nhẹ như kế hoạch trước. Counters ON và heavy trace được kiểm lại từ **sealed raw cũ**, không chạy thêm ON/trace processes. Những comparisons đó không được gọi là overhead nhân quả đương thời.

Correctness trước khi sử dụng số đo:

1. Synthetic native contract **1/1 PASS**: frozen/observer OFF/ON outputs bằng nhau; logical counters ON bằng nhau; phase conservation và round counts đúng. [Log](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/observer_synthetic_tests.log). Đây không phải một sanitizer/race-check mới.
2. Archived real OFF/ON/trace outputs và non-time counters khớp; kiểm độc lập **640 returned distances**, sai số tối đa **7,77e−16 <1e−12**. Recall64 = **0,990625**, chỉ descriptive cho panel nhỏ, không thay quality gate đầy đủ.
3. Mọi process mới khớp query IDs/order/top-10/distances với frozen reference: **384/384 query results**, không incomplete. Mỗi observer query khớp round count của sealed ON, mọi phase sum ≤ query elapsed. [Capture checks](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/capture_checks.json).
4. Sequential lock, RyzenGuard và independent heartbeat watchdog hoạt động; fail-closed missing-temperature/95°C injection được kiểm trước đo. **6/6 exit 0**, không guard failure; 30 host samples, Tctl **60,25–77,00°C** trong các process. Telemetry bao gồm load/warmup/search, không phải sensor timeline riêng của 64 search queries.
5. Dataset-free suite cuối: **521 tests, 507 pass, 14 skip**; native observer test là opt-in riêng ở trên. [Log](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/unittest.log).

## 3. Actual frozen OFF và observer validity

Mean latency µs/query, không gồm load/output; tất cả query và process đều giữ:

| Pair | Order | Frozen OFF | Observer, counters OFF | Observer/OFF −1 |
| --- | --- | ---: | ---: | ---: |
| 1 | OFF → observer | 5.070,620 | 4.979,748 | −1,792% |
| 2 | observer → OFF | 5.194,120 | 5.083,303 | −2,134% |
| 3 | OFF → observer | 5.084,772 | 5.022,535 | −1,224% |

Frozen OFF mean qua ba process **5.116,504 µs**, process SD **67,589 µs**. Observer mean **5.028,529 µs**. Đây là repeatability của **một graph/panel**, không ba graph replicates, không serving-tail evidence.

Đăng ký dùng `l_i = log(mean_observer_i / mean_OFF_i)`; CI là `mean(l) ± t(0.975,df=2)*sd(l)/sqrt(3)`, rồi đổi về %. Estimate **−1,717% [−2,851%; −0,570%]**. Tất cả CI phải nằm trong **[−2%; +2%]** mới PASS. Gate hiện **NOT_VALIDATED_OUTSIDE_EQUIVALENCE_BUDGET**; không đổi ngưỡng hoặc dùng query bootstrap để làm hẹp CI. CI này có điều kiện theo giả định log-ratios giữa process pairs độc lập và gần normal; n=3 không kiểm chứng được giả định đó, và order chỉ cân bằng được một phần.

Observer nhanh hơn không chứng minh overhead âm hoặc optimization mới. Có thể liên quan code/data layout, host/order state hoặc observer perturbation; chưa phân biệt nguyên nhân. Gate thất bại là **chưa xác nhận equivalence**, không phải chứng minh ba cặp này vô dụng hoặc mọi instrumentation đều không thể dùng. Theo kế hoạch, không kéo phase shares sang OFF như measured attribution và không thêm cặp.

## 4. Phase windows đo được trong observer execution

Mỗi round dùng bốn mốc trên coordinator: `release`, `arrived`, `gather_end`, `frontier_end`. Worker có `start/done`. Chỉ giữ tổng scalar; ba observer processes đều **2.024 rounds/64 query =31,625 rounds/query**. Tổng 6.072 round observations lặp cùng query/graph **không phải 6.072 độc lập** và không phải 6.095 rounds của H3 cũ trên ba graph.

```text
A = sum(arrived - release)                 worker + start/arrival delays
G = sum(gather_end - arrived)              gather / publication / scratch collection
F = sum(frontier_end - gather_end)         global sort/unique/merge/prune + seed dispatch
R = query elapsed - A - G - F              initial serial work, gaps, aggregation, tail
T_observer = A + G + F + R
```

G gồm đọc worker state, B1 settled/expanded publication và gom `local_discovered` vào scratch; không phải visited-only cost. F gồm clear seed buffers, sort/unique scratch, capped flat merge, expanded-flag updates, next-seed selection/assignment hoặc scan nhánh empty-scratch; không phải pure sort. Initial entry L2/expansion nằm ở R. A gồm local queue/seen/reset, adjacency, exact L2, visited, insert/erase và start/arrival delays; không thể gán toàn A cho distance.

| Disjoint window | Mean µs/query | % T_observer | Phạm vi suy luận |
| --- | ---: | ---: | --- |
| A worker/arrival | 4.482,587 | 89,143% | Lớn nhất trong observer; nguyên nhân exclusive UNKNOWN |
| G gather/publication | 48,973 | 0,974% | Mandatory work + scratch collection |
| F frontier/dispatch | 474,541 | 9,437% | Potential systems envelope, không toàn bộ removable |
| G+F coordinator | 523,514 | 10,411% | Tổng hai hàng trên, **không cộng lại** vào conservation |
| R other | 22,428 | 0,446% | Initial search + observer aggregation/gaps |

Các số riêng từng process nằm trong [analysis.json](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/analysis.json), từng query trong [query_summary.csv](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/query_summary.csv). Không lấy 10,411% làm “measured OFF merge fraction”. Ngay cả total-latency equivalence PASS cũng chưa tự chứng minh từng phase không bị perturb; ở đây gate tổng còn chưa PASS.

### Synchronization trên critical path và worker-time

| Đại lượng | µs/query | Diễn giải |
| --- | ---: | --- |
| `sum(arrived - max(done_w))` | 3,201 | Arrival tail sau worker cuối xong; nằm **trong A** |
| `sum_w,sum_r(arrived - done_w)` | 456,944 | Summed worker-time, overlap worker chậm; **không cộng vào T** |
| `sum_r(max d_w - sum d_w/2)` | 225,741 | Dispersion duration từng round; không phải bare barrier |
| `sum_r((arrived-release) - sum d_w/2)` | 232,475 | Ideal divisible-work/zero-start-delay ceiling, 4,623% observer wall |

`d_w=done_w-start_w`; idle worker góp 0 vào work nhưng capacity vẫn p=2 trong ceiling lý tưởng. Hàng cuối giả định fixed total processing work chia tùy ý, cùng tốc độ core, không dependency/cost và G/F/R giữ nguyên. Nó đã gồm arrival/start effects; **không cộng** hàng 1 hoặc 3 vào hàng 4. Đây không phải scheduler khả thi hay OFF speedup bound đã validate.

Trong engine frozen, `barrier_wait_ns` cũng là tổng worker-ns. `sync_wait_ns` còn chứa helper parked time trong coordinator; không cộng nó với merge/barrier. `merge_time_ns` bắt đầu khi tất cả worker tới và kết thúc sau gathering, ON distinct/counter accounting, B1 publication, global frontier và dispatch. Trace build còn copy trace trong cửa sổ đó. Vì vậy neither `barrier/p` nor `merge_time_ns` là exclusive cost của một primitive. Source audit không hỗ trợ cách cộng các timer cũ thành causal decomposition.

## 5. Counters ON / heavy trace và profiler availability

Sealed H3 A3-R1, cùng 64 IDs nhưng **epoch cũ, một process/mode, ordered và không paired**:

| Mode/binary | Mean µs/query | Descriptive comparison |
| --- | ---: | --- |
| Frozen OFF | 5.224,956 | Historical frozen reference |
| Trace-capable build, OFF, capture disabled | 5.016,150 | −4,00% vs historical frozen OFF: build/order confounding đã hiện rõ |
| Same build, counters ON, capture disabled | 5.579,866 | +11,24% vs same-build OFF |
| Same build, counters ON + trace | 6.294,181 | +12,80% vs counters ON; +20,46% vs historical frozen OFF |

Raw này đã qua parity nhưng không qua contemporary observer equivalence. Không gọi các chênh lệch trên là isolated instrumentation tax hoặc dùng để hiệu chỉnh OFF mới. Panel 3.000-query B1 pilot có ON–OFF chỉ khoảng 3,5–5,3% ở A3 p2: độ khác nhau giữa panel/epoch càng ngăn việc dùng một hệ số overhead chung. Không trừ snapshot/copy hay ON unique tracking để tái tạo latency OFF.

**Profiler:** `/usr/bin/perf` có mặt; một permission probe native `perf stat -e task-clock,cycles,instructions,cache-references,cache-misses -- true` trả exit 1, “Access to performance monitoring and observability operations is limited”, `perf_event_paranoid=4`, `kptr_restrict=1`. [Probe receipt](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/profiler_permission_probe.json) ghi rõ stderr excerpt được chép từ tool output của **một** lần probe. Không chạy ANN dưới perf; không sudo/sysctl/capability changes; nhánh dừng tại đây.

Exclusive L2 cycles/time, local frontier operations time, cache misses/stalls, memory bandwidth và IPC: **NOT_MEASURED**. Nguồn code cho biết chúng có mặt, không cho biết runtime share. Không dùng RSS, frequency hoặc logical L2 count làm PMU substitute; không tự chuyển sang profiler/instrumentation nặng khác.

## 6. Quantitative opportunity và các upper bounds có điều kiện

Các bound sau áp dụng trước hết **trong execution observer**, zero-cost removal, giữ trajectory/other timings cố định. Phase transfer sang OFF chưa đạt gate. Chúng overlap/nest, **không được cộng**.

| Mục tiêu loại bỏ | Conditional gross ceiling | Giới hạn |
| --- | --- | --- |
| Whole coordinator | 523,514 µs /10,411% observer | G+F gồm mandatory publication/dispatch, không toàn bộ removable; OFF bound UNKNOWN |
| Whole global frontier/dispatch window | 474,541 µs /9,437% | Pure merge nhỏ hơn hoặc bằng window; chưa có thuật toán xóa được window |
| Bare arrival tail, completion times fixed | 3,201 µs /0,064% | Không loại straggler hoặc coordinator |
| Perfect fixed-work balance/zero delays | 232,475 µs /4,623% | Divisible work oracle; không bound mọi dynamic worker/S policy có thay work/trajectory |
| All L2 including initial entry | Broad A+R ≤4.505,015 µs /89,589% | Có rất nhiều queue/visited/unrelated work; exclusive L2/OFF share UNKNOWN |
| Local frontier maintenance | Nằm trong A+R, không có bound hẹp hơn | Không coi toàn worker phase là frontier-only |
| Memory/cache stalls | Chỉ có trivial ≤T | Có thể nằm trong mọi window; NOT_MEASURED |
| Duplicate elimination | H3 count oracle vẫn chỉ count/work bound | Không nhân trực tiếp ~2,5% duplicate L2 thành % latency |

Sensitivity, **không phải net gain dự báo**: 5% frozen OFF mới = **255,825 µs/query**. Một controller có cost giả định 1% OFF = **51,165 µs/query**, khoảng **1,618 µs/round**. Nếu chuyển được toàn 523,514 µs coordinator quan sát sang OFF và không gây work/Recall change, phải loại ít nhất **58,64%** cửa sổ ấy để còn 5% net sau controller. Khả năng này chưa được chứng minh và current observer không xác nhận phép transfer đó.

Chỉ cân bằng fixed work: ngay oracle lý tưởng 232,475 µs cũng dưới mục tiêu 255,825 µs; trừ controller giả định còn **181,310 µs**, khoảng **3,54%** frozen OFF nếu cost transfer đúng. Không thể dùng phép tính này để bác mọi scheduler có thể giảm work hoặc coordinator; nó chỉ làm yếu cơ chế **redistribute cùng work** ở scope hiện tại. Negative observer delta không được ghi thành controller credit, và không cộng controller/observer costs vào các window đã chứa chúng.

**Research gate:** chưa chứng minh một exclusive removable OFF component ≥10%, chưa có cheap signal + conservative net gain đủ rõ, chưa có novelty khác prior art. Vậy **không mở H3/TP-CG**. Có systems headroom khả dĩ ở global frontier/local worker work, nhưng bottleneck nhân quả có thể cải thiện trong latency OFF hiện **UNKNOWN**.

## 7. Stop và trạng thái giữ nguyên

Đã dùng hết ba cặp cho phép; **không thêm process, trace, graph, tuning hoặc prototype**. Measurement-validity gate chưa đạt và PMU branch dừng; next action là [original proposal reassessment](ORIGINAL_PROPOSAL_FINAL_REASSESSMENT.md), không một campaign khác. Không sửa các báo cáo đã freeze để xóa mâu thuẫn; audit mới giới hạn cách diễn giải chúng.

Historical P0 / Full P1 / t0998 **HOLD**; Protocol V4 D1–D5 **UNAPPROVED**; P3 official **CLOSED**; TP-CG **NOT_OPENED**; i5-14600KF **NOT_RUN**. Overlap H3 giữ **NO-GO trong scope đã screen**. D1 **UNTESTED**, D4 **NOT TESTED**, D6 **INCONCLUSIVE** trên các historical subjects; các lane H-V/H-G/H-C/H-F/H-QV không thay đổi.
