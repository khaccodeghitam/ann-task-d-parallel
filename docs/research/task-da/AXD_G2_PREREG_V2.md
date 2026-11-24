# A×D G2 · Preregistration v2 · nhánh 3a

**EXPLORATORY_HOST_SPECIFIC · DESIGN_FOR_OWNER_APPROVAL · DO NOT EXECUTE**  
Ngày soạn: 23/11/2026. Protocol identity: `AXD-G2-V2-3A-20261123`, revision `design-2`.

Theo quyết định của owner, **đóng v1 tại `QUALITY_HOLD`**. Tài liệu mới này không sửa prereg v1, Stage 5, Stage 6 hoặc quyết định lịch sử. G2 OFF của v2 vẫn `NOT_OPEN`; task soạn tài liệu này thực hiện **0 benchmark, 0 profiler, 0 G2 OFF**. Các giá trị dưới đây là đề xuất cụ thể để phê duyệt, chưa phải quyền thực thi.

Toàn bộ `public 100K` đã được Task A đánh giá; `test_90k` đã được dùng trong R86/P1. Panel v2 chỉ rời các panel nhỏ đã dùng tại D/R90 được kiểm kê, **không phải fresh independent holdout**. Sáu graph có `root independence NOT_VERIFIED`; `independent-root population CI = NOT_ESTIMABLE`.

Tài liệu đi cùng: [Statistical design](AXD_G2_V2_STATISTICAL_DESIGN.md), [Query split audit](AXD_G2_V2_QUERY_SPLIT_AUDIT.md), [GO/HOLD/PIVOT](AXD_G2_V2_GO_NO_GO_CRITERIA.md). Cả bốn tạo thành một protocol; phải khóa cùng revision và SHA trước khi mở test.

**Remediation design-2:** xử lý F1–F3/C1–C4 của [pre-approval audit](AXD_G2_V2_PRE_APPROVAL_AUDIT.md). Package hiện chỉ hỗ trợ **p=2/S=16**, beam **432** cố định, cùng panel/hash và 12 block như design-1. Runner/analyzer, schema và dependency lock đã được triển khai; xem [remediation và re-audit](AXD_G2_V2_PRE_APPROVAL_REMEDIATION.md). Không có authorization hoặc kết quả quality/performance mới.

## 1. Điểm xuất phát và giả thuyết có thể bác bỏ

[Resolution decision](AXD_G2_QUALITY_HOLD_RESOLUTION_DECISION.md) và [Stage 6](AXD_G2_TEST_QUALITY_REPORT.md) ghi exact parity nội graph, giảm duplicate L2 trong ON khoảng 74%, nhưng v1 trượt span liên graph. Đây là bằng chứng về correctness và công việc logic, chưa phải bằng chứng về latency OFF.

Cơ chế giả định: B1 tránh một phần L2 trùng, A1 giảm công cập nhật frontier, nhưng thêm bookkeeping/synchronization. Lợi ích thời gian chỉ xuất hiện nếu công tiết kiệm trên critical path lớn hơn overhead và ảnh hưởng locality. Duplicate L2 giảm mà OFF latency không cải thiện thực dụng là kết quả âm có giá trị cho tổ hợp triển khai này. Không suy ra đóng góp riêng B1/A1 hoặc tính mới thuật toán từ phép thử hai policy.

| Câu hỏi | Đối chứng và phạm vi | Endpoint |
|---|---|---|
| **Primary · Estimand A** | Baseline vs B1+A1 trên chính graph đó, cùng query/order, beam, p, S, engine và Recall exact | **Geometric mean của paired mean-latency ratios OFF** là primary; p50/p95/p99, QPS, speedup, peak RAM; total/unique/duplicate L2 từ ON riêng |
| **Secondary · Estimand B** | Trung bình đồng trọng số ba Stock vs ba Fast, tại Recall tương đương trong cohort cố định | BUILD wall/size lịch sử đúng SHA, Recall, OFF latency/QPS; scaling NOT_SUPPORTED trong design-2; BUILD–SEARCH theo workload |

Primary bao gồm **cả sáu graph**, mỗi graph trọng số 1/6; Stock/Fast riêng là breakdown đã định trước. Không đổi primary sang graph/arm có kết quả tốt. Span liên graph không phải điều kiện matching của A. B có cổng tương đương riêng, không được dùng quality floor để thay thế equivalence.

## 2. Định danh bất biến và compatibility

Dùng sáu graph gốc trong [G1 manifest](AXD_G1_GRAPH_ARTIFACT_MANIFEST.md), trực tiếp PiPNN, không build lại/convert/sửa adjacency. Recipe R90 P0A v1.3 H85: MS-Turing-1M, C160/K1024/N2, degree cap 64, entry 0. R1 cùng số với R1 ở arm kia không tạo thành cặp build độc lập.

| Thành phần | Identity khóa |
|---|---|
| Search source | `f2cd634b837a70735c3e31e5956f0524bfc26675` |
| Search ELF Release, chung ON/OFF và hai policy | `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1` |
| Task A source / source manifest | `f5e48bb681812ce51aed7272f30ecefc85ed427b` / `5f42250caa47659daf978a73355857e355cc86096571d327518e676d41f1423b` |
| Highway | `6bc2d47793bae9c521fb4150936669647700765d` |
| Stock / Fast OFF builder ELF | `13bef65c01d4638959b16b74fc2b8b6130b433ebc09fff8f436c8b1503e688c9` / `fcfb16d0ca2b498f94db8383dfc311c2e7ba88cb3036281accd5f30c6d876793` |
| Transfer package TAR | `e59f5889f1271a801ff350866bfdffdf7764c372aac65e06d93c2d6a3c48029d` |
| TRANSFER_MANIFEST / SHA256SUMS | `df092d838b717430e75148bc2c47ab4611af95eed8f014646f5520a3273e2d52` / `62b0db1a07336840fecb083c1235e608e75937d74f5db6e9a7ffc9a9c99a6e75` |
| BUILD / structural manifest | `0c76f3e5bc3dc0d82f70aa1aadac9b26c5b0e8f4607f31d9aa6d8b0b0a4121c3` / `9550858dcb763349ed5180b3b65577e48a600e54becc0ecb9c755970a4d4bbfb` |

Full SHA của sáu graph, base/query/GT và số byte được dẫn ở manifest G1 và audit split; chúng là phần bắt buộc của receipt v2. Không dùng HEAD hiện tại để thay cho frozen search source. HEAD lúc soạn là `f54b1bb653652dd13e760cc00c9fb46d0e643c1c`; v1 và các báo cáo G1/G2 đang có tài liệu untracked, nên không dựa vào Git commit để giả định đã niêm phong chúng.

Frozen evaluator đã có warmup riêng, per-query latency, batch wall, linear-interpolated percentiles và ON/OFF trong cùng ELF. G1 chứng minh runtime parity tại p=2/beam 384; chưa chứng nhận mọi cấu hình v2. Nếu thiếu khả năng xuất endpoint hay receipt cần thiết, **HOLD compatibility**, không âm thầm build ELF mới. Thay source/binary là revision/subject mới cần review trước test.

## 3. Panel và validation-only calibration

Giữ `val_10k.ids` và `warmup_val_100.ids` cũ. Không dùng `narrow_test_3000.ids` để calibration, performance hoặc test chính v2. Không lấy một subset thuận lợi của panel mới để timing.

Panel `v2_test_10000.ids` gồm đúng 10.000 ID từ pool 81.000 đã audit. Chọn theo SHA-256 rank với prefix ASCII `axd-g2-v2-3a-test10k-20261123/`, ID thập phân không padding; hòa theo ID tăng. Giữ thứ tự hash rank cho mọi cell/repeat. SHA serialization ASCII một ID/dòng, LF cuối file: **`457abdc13abc95d8d0f48ff32919a6013f5ed4bca469f9075312ae80dfe44b0d`**. Đây là hash được tính trong bộ nhớ từ ID, chưa tạo file query hay xem output test. [Audit và recipe đầy đủ](AXD_G2_V2_QUERY_SPLIT_AUDIT.md).

**Provenance chọn beam đã khóa ở design-1, giữ nguyên trong design-2:**

1. Tại p=2, dùng grid validation đã freeze `[384,400,404,408,412,416,420,424,432]`. Reuse đủ 54 baseline ON Stage 5 sau kiểm identity; không chạy lại các cell hợp lệ.
2. Với từng beam chung b và graph g, tính mean Recall `r_gb`, sample SE theo 10.000 query. Quy tắc đã chọn **một beam chung nhỏ nhất** thỏa trên cả sáu graph:
   `r_gb − [z(1−0.05/6) + z(1−0.20/6)] × SE_gb ≥ 0.990`.
   Hệ số tổng là **4.22789444**. Đây là dự phòng thiết kế cho gate floor đồng thời 95% và mục tiêu power toàn cohort khoảng 80%, dựa trên plug-in validation; không phải chứng nhận power đạt được.
3. Replay số học trên hits Stage 5 cho **beam v2 b=432 chung đã khóa**: min assurance score `0.99013620`; b=424 có `0.98988202`, không đạt. Đây là operating point đề xuất trong tài liệu mới, **không thay bộ beam v1 hoặc file cấu hình nào**. Runner design-2 hard-code beam 432, không có cờ sweep/retune; baseline/opt dùng cùng b. Receipt trước test chỉ xác nhận identity lựa chọn đã khóa.
4. Sau phê duyệt quality phase, chạy 6 B1+A1 ON validation tại b đã khóa; đối chiếu với baseline tương ứng. Không mở grid mới, đổi floor/margin, hay quay xuống beam khác sau khi xem test. Provenance/identity của 432 không khớp thì HOLD, không chọn beam khác.

Dùng power rule thay vì tối ưu span/target point sau khi đã biết Stage 6. Việc thiết kế v2 có biết kết quả v1 và chọn operating point từ validation cũ vẫn là tái thiết kế exploratory, không được mô tả là thiết kế mù.

## 4. Quality test gate trước performance

Quality phase tương lai: 6 graph × 2 policy = **12 test ON**, mỗi process 100 warmup validation + toàn bộ 10k test; p=2, S=16, jobs=1, K=10, flat, entry=0, squared L2 tích lũy double trên FP32, tie theo ID.

**Gate A bắt buộc:** đúng identities, đủ 10 ID duy nhất/query, exact ordered IDs/L2² baseline–opt ở 60.000 graph-query pair và trên validation tại b mới; counter accounting/invariants frozen PASS; zero guard failure. Sáu Recall khác nhau phải có point và **simultaneous one-sided LCB95 ≥0.990**: `r_g − z(1−0.05/6) × SE_g`, hệ số **2.39397980**. Hai policy exact parity không tạo 12 phép kiểm Recall độc lập.

**Gate B riêng:** trên cùng query, `d_q = mean(Fast recalls) − mean(Stock recalls)`; **CI95 hai phía** của mean d phải nằm trọn trong **(−0.0005,+0.0005)**. Đây là tương đương Recall cấp arm của cohort này. Không thay bằng “p>0.05”, point gap nhỏ hoặc noninferiority một phía. Common beam loại lợi thế hạ beam riêng cho Fast; CI equivalence vẫn cần vì common beam không bảo đảm Recall bằng nhau. Không đặt cổng span 0.0006 hay point-gap 0.0003 từ đề xuất cũ.

Nếu A PASS/B HOLD: owner có thể mở đúng ma trận within-graph A; B, ΔT tại matched Recall và tuyên bố Fast thắng Stock vẫn HOLD. Mọi cell Stock/Fast vẫn giữ trong báo cáo, kèm Recall; không loại graph. Test trượt không dẫn đến đổi panel/beam trong v2.

## 5. Performance p=2: kế hoạch chưa thực thi

Baseline: `flat, baseline/full`. B1+A1: `flat, barrier_all_evaled/incremental`. Dùng `--mode OFF`, p=2, S=16, jobs=1, CPU `[0,2]` theo topology đã ghi; không bật profiler/round trace. Instrumentation ON là chiến dịch diagnostic riêng đã có ở quality phase, không dùng ON timing cho kết luận Search.

**12 block × 6 graph × 2 policy = 144 process OFF**, đủ 10k query/process. Mỗi process mới thực hiện đúng **100 warmup validation** trước cửa sổ đo. Warmup không đi vào Recall/latency/QPS test; không warmup bằng test; không drop thêm query đầu vì chậm.

Balanced order được khóa bằng công thức, không chọn lại seed:

- `G=[Stock1,Fast1,Stock2,Fast2,Stock3,Fast3]`, index gốc `i=0..5`.
- Block `b=0..11`: xoay trái G đi `b mod 6` vị trí.
- Trong cặp graph i: base→opt nếu `(i+b+floor(b/6)) mod 2=0`, ngược lại opt→base.

Mỗi graph xuất hiện hai lần ở mỗi vị trí; một lần mỗi policy order ở vị trí đó, tổng 6 AB/6 BA. Cặp luôn liền nhau, guard kiểm trước từng process. N=10k và query order giống nhau trong mọi process. Không benchmark CPU nặng đồng thời, jobs không phải số worker search. Không thay fan/power/security/global affinity; không dùng i5-14600KF.

Mỗi OFF phải khớp ordered IDs/L2² của ON v2 đúng graph/policy/p/beam. Giữ cả lượt chậm, mọi timeout/partial/error và telemetry. Không loại outlier hoặc thêm repeat để đổi CI. Một process lỗi/guard/parity failure: dừng, bảo toàn raw và HOLD campaign; không tự chạy lại để lấp cặp. Nếu muốn recovery cần kế hoạch riêng, ghi rõ conditioning/thiếu dữ liệu trước khi chạy tiếp.

**Cửa sổ endpoint:** `latency_ns` bao quanh `session.search` từng query; mean µs là tổng latency/N. Percentile dùng vị trí `q×(N−1)`, nội suy tuyến tính của evaluator. `QPS_wall=N/batch_wall_s`, không ép bằng `1/mean_latency`. Batch wall gồm vòng query, không gồm load graph/base/query, warmup và serialize JSONL sau đó. Báo load/startup/end-to-end riêng nếu receipt có; không gọi QPS jobs=1 là throughput nhiều query đồng thời. Primary RAM field duy nhất là `p2_eval_summary.vm_hwm_kib`, integer KiB dương, captured sau search/output serialization và trước final summary/exit; bao gồm load/warmup/results buffer đến capture. Wrapper sampled RSS chỉ là diagnostic phụ. Không đổi nguồn hoặc suy riêng RAM lõi search.

## 6. Secondary B và multi-worker scaling

Tại p=2, giữ đủ factorial Stock/Fast × baseline/opt. So Fast-base với Stock-base, Fast-opt với Stock-opt; Fast-opt vs Stock-base là đối chiếu tích hợp, không thay primary A. Tính latency và QPS cấp arm bằng đồng trọng số ba graph trong mỗi block; không ghép Stock-r1/Fast-r1 như matched build.

BUILD là **receipt lịch sử đúng sáu SHA**, không chạy BUILD mới. Báo từng invocation, host, threads, ELF/package/source/protocol, range và mean; graph size lấy byte thật, tổng 1.292.447.108 B. Mean BUILD đã báo Stock/Fast khoảng 42.2567/33.7933 s, ΔB=8.4633 s; không suy CI quần thể từ ba root chưa xác minh. Không so thời gian BUILD host A như thể đã đo trên Ryzen D.

Tính `T(Q)=BUILD+Q×mean_OFF_latency` tại Q=1, 100.000 và 1.000.000; báo break-even dương nếu có. Search term dùng arithmetic mean latency, không lấy geometric ratio thay vào. CI chỉ có điều kiện trên BUILD đã quan sát; transfer/load không đo được thì để UNKNOWN và loại rõ khỏi T. Chỉ diễn giải matched-quality khi gate B đạt.

**Phạm vi đóng băng design-2 là p2-only.** p1/p4 = `NOT_SUPPORTED / NOT_AUTHORIZED` trong runner; không còn lựa chọn tự mở scaling trong approval package này. Điều này đóng confound strata p2→p1→p4 được audit chỉ ra. Nếu owner muốn scaling sau này cần extension prereg riêng, order worker strata cân bằng, calibration/quality riêng và phê duyệt trước dữ liệu extension; không được dùng kết quả p2 để đổi primary/beam/panel v2.

Trong extension tương lai, speedup `L1/Lp`, throughput ratio `QPSp/QPS1`, efficiency `speedup/p` phải báo cùng Recall, topology và session uncertainty. Chưa có claim scaling hoặc multi-query serving throughput trong nghiên cứu p2 này.

## 7. Inference và giá trị thực dụng

Primary: mỗi graph/block có `x_gb=log(mean_base/mean_opt)`; block có `x_b=mean_g(x_gb)`. Báo log CI t qua 12 block (df=11), chuyển sang giảm latency `1−exp(−x)` và speedup `exp(x)`. Báo thêm arithmetic mean latency, µs tiết kiệm và ratio of arithmetic means để người đọc kiểm nghĩa. Không tráo estimator giữa quyết định và báo cáo.

Khóa **minimum practically important geometric reduction =3%**, tức `θ=−log(0.97)`. GO cần cận dưới CI12, drift-CI6 và joint-bootstrap CI95 vượt θ. **Không** áp ngưỡng 3% cho arithmetic mixture latency và không thay estimator sau dữ liệu. Numeric strict comparisons có tie rule bảo thủ `1e-12` trên scale đang xét: trong khoảng đó coi là chưa vượt ngưỡng, giữ HOLD; không nới threshold. Áp dụng cùng các kiểm tra uncertainty/heterogeneity/tail/RAM trong [decision criteria](AXD_G2_V2_GO_NO_GO_CRITERIA.md). Đây là lựa chọn kỹ thuật để owner duyệt, không phải SLA có sẵn hoặc dự báo gain. Với một process có 3–6 ms/query, giảm riêng process đó 3% tương ứng 90–180 µs/query; geometric gain toàn cohort không bảo đảm arithmetic savings đó. Đây không phải kết quả OFF v2.

Phân tích tách query uncertainty, process repeat và graph uncertainty; không biến 1,44 triệu query executions thành 1,44 triệu lần lặp độc lập. Query bootstrap và drift sensitivity đã khóa trong [statistical design](AXD_G2_V2_STATISTICAL_DESIGN.md). Quyết định theo cohort cố định và host, không khẳng định tổng quát sang root/CPU/dataset khác.

## 8. Guard, provenance receipt và ngân sách Ryzen

Chỉ host AMD Ryzen 5 PRO 4650U. Giữ guard đã dùng: base guard SHA `232ed904b54359af17161c2f785b81c77097aad4d99f68325e08faf88cfefcbb`, Ryzen adapter SHA `0cf76c6e72fe8da698d7c7da041430a7312d54894e4861f3ee31660f4bd454d9`. Start Tctl<85°C; abort ≥95°C hoặc critical trip/AC/RAM/disk/swap/heartbeat/foreign benchmark failure. Cooldown tối đa 180s trước process; timeout 180s/process. Không nâng ngưỡng khi quota thiếu. Guard/sensor fail-closed và lock chung `/tmp/task-da-pivot-4650u.lock` phải hoạt động.

**RAM hard gate khác aggregate CI:** với mỗi cặp graph/block, `C−B ≤ max(65536 KiB,0.10 B)` bắt buộc, B/C là HWM integer KiB dương. So sánh integer tương đương `10(C−B) ≤ max(655360,B)`; equality PASS, vượt dù 1 KiB HOLD_RAM và dừng sau cặp, giữ cả hai lượt. Combo-first phải đợi base cùng cặp để biết relative limit; live absolute MemAvailable guard vẫn bảo vệ trong lúc chạy. Thiếu/zero/âm/nonfinite/fractional RSS = INVALID/ABORT. Aggregate mean normalized overhead + CI95 family18 chỉ là gate bổ sung, không che hard exceedance.

**CPU diagnostic/affinity/contention khóa trước test:**

- Nguồn CPU là `/proc/<owned_pid>/stat` utime+stime / `CLK_TCK`; kiểm PID+start_ticks, không cộng thread counters lần nữa. Window first-to-last alive samples, gồm một phần load/warmup/output, không gọi là search-only. `CPU%=100ΔCPU_s/Δwall_s` có thể >100%; capacity%=CPU%/2, không clamp. Monitor CPU được ghi/tách riêng. [Linux proc semantics](https://docs.kernel.org/filesystems/proc.html).
- Cadence 1 Hz, interval hợp lệ 0.5–2 s, window CPU ≥5 s; missing/reset/PID reuse/gap>2 s = INVALID/ABORT. Quiet preflight ≥5 s trước mỗi process, ghi toàn bộ JSONL; cooldown chỉ do start-temperature, tối đa180s và trong phase quota.
- CPU workers giữ `[0,2]`; profile yêu cầu hai core vật lý 0/1, sibling lists `0-1`,`2-3`, cùng L3 `0-5`, inherited process/monitor mask `0..11`, Linux kernel `7.0.0-43-generic`, CLK_TCK=100 trên Ryzen4650U. Đây là profile khóa cho owner duyệt; runtime phải khớp, không sửa global/parent affinity hoặc fan/power. Frozen evaluator tự pin worker threads; requested=observed=[0,2] phải khớp ở mỗi receipt.
- Dùng `/proc/stat` host busy (user+nice+system+irq+softirq+steal; không idle/iowait và không double-count guest), trừ owned CPU và monitor CPU, clamp phần dư âm do snapshot rounding về0. Trên rolling window ≥5 s, foreign busy/(wall×2) phải **≤0.01**; >0.01 abort/HOLD. Mức 1% capacity là engineering noise budget bằng **1/3 mức effect tối thiểu3%**, không phải ngưỡng empirical hoặc bảo đảm latency noise<1%. Không học/nới threshold từ test.
- Owner phải xác nhận quiet host/no other CPU-heavy benchmark trong approval receipt. Named CPU/ANN jobs bị chặn ngay; unknown-name sustained CPU job vẫn bị phát hiện qua host aggregate. Ngưỡng này không chứng minh không có mọi transient workload. Snapshot giữ PID/start/name/counter deltas, không cần cmdline/stack. Không kill process khác. Nếu không đọc được PID khác, host aggregate vẫn phải khả dụng; own/monitor counters thiếu thì fail-closed.
- MemAvailable **>1GiB**, disk **>20GiB**, swap growth>64MiB trong≥10s abort, AC available/unchanged. Mỗi phase bắt đầu cần disk **>25GiB** (20GiB floor+5GiB output reserve), sau đó giữ floor20GiB. Không nới guard. Một run chậm nhưng hợp lệ được giữ; contention/invalid/guard/quota failure giữ raw, dừng toàn campaign, không loại riêng một row rồi tính GO hoặc chạy bù.

**Freeze implementation:** [runner](../../../research/task_da/g2_v2_runner.py), [guard extension](../../../research/task_da/g2_v2_guard.py), [analyzer](../../../research/task_da/g2_v2_analyzer.py), [contract](../../../research/task_da/g2_v2_contract.py); full SHA ở [freeze manifest](../../../configs/axd_g2_v2_freeze.json). Search source vẫn f2cd634/ELF7a2685e5; wrapper source identity là base HEAD f54b1bb + content-SHA overlay, không giả mạo một commit mới. Compiler GCC13.3.0 frontend SHA `1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769`, compile flags `-O3 -DNDEBUG -std=c++17 -Wall -Wextra -Wpedantic -Werror`, link `-O3 -DNDEBUG`, không rebuild. Exact Python3.12.3/7 packages và wheel hashes ở [requirements-g2-v2.lock](../../../requirements-g2-v2.lock); schema `axd_g2_v2.2` ở [schema](../../../configs/axd_g2_v2.schema.json). Existing frozen base guard và các helper được hash riêng; không sửa chúng. Interpreter executable và năm native runtime libraries cũng có byte pins trong manifest; kiểm lại sau authorization. Loader overrides LD_PRELOAD/LD_LIBRARY_PATH/LD_AUDIT không được phép. Pin compiler/flags là recovered metadata phù hợp ELF .comment, không tuyên bố đã rebuild tái tạo binary.

Receipt phải chụp OS/kernel/CPU topology, allowed/requested/observed CPU, compiler/link/ISA/flags/package pins theo freeze, full argv/env, protocol/doc SHA, source/ELF/input/graph/panel SHA, sensor/AC/host contention và raw output/exit code từng process. Rehash immutable subjects trước/sau, lập BUNDLE ngoài Git. Raw mới nằm trong directory mới riêng dưới external artifact root được owner duyệt, không chèn vào Stage 5/6; Git chỉ nhận summary và relative links. Task hiện tại chỉ tạo fixture/audit evidence và command plans, chưa tạo execution campaign hoặc test-ID file. Proposed artifact paths và full argv plans được lưu để owner review; native host configuration thực tế chỉ được ghi sau authorization khi preflight, chưa được chứng nhận trong task này.

| Hạng mục tương lai | Số process | Chi phí dự trù, không phải performance measurement |
|---|---:|---|
| p2 validation opt + test ON | 6+12=18 | Khoảng 14–18 phút, chưa tính audit/cooldown |
| p2 OFF 12 block | 144 | Khoảng 108–132 phút theo dự trù 60 OFF/10k =45–55 phút của resolution; không có đo OFF R90 để xác nhận |
| p2 tổng, gồm verification/cooldown | 162 process mới | Khoảng **2,5–3,5 giờ**, đề xuất hard quota **4 giờ**; raw khoảng **1,5–3 GiB**, reserve ≥5 GiB ngoài input/graph |
| Scaling p1/p4 | 0 trong package design-2 | NOT_SUPPORTED; cần extension prereg/phê duyệt riêng, không nằm trong quota p2 |

Cơ sở tài nguyên: Stage 5 ON 60 process/10k tốn 2.688 s; Stage 6 ON 12 process/3k tốn khoảng 3,06 phút, peak RSS khoảng 0,831 GiB. Đây chỉ là mốc lập ngân sách, không suy gain OFF. Không tái sử dụng quota 3 giờ của v1 như thể đủ cho 12 block và scaling. Một slow process/cooldown dài có thể làm hết quota; khi đó HOLD incomplete, không rút số repeat.

Các khoảng giờ trên là thu thập/verification/cooldown, **chưa xác nhận chi phí bootstrap hậu kỳ**. Dự trù thêm 0,5–2 giờ xử lý offline cho p2 bằng analyzer vectorized/batched, quota phân tích đề xuất 3 giờ; thời gian thực UNKNOWN trước triển khai. Không chạy hậu kỳ CPU nặng đồng thời benchmark. Không triển khai bootstrap bằng hàng tỷ vòng lặp Python/sort lại toàn bộ sample: dùng query-block sums cho mean và weighted empirical order statistics cho tail, tái tạo đúng percentile đã khóa. Nếu analyzer chưa khả thi trong budget, sửa implementation/định cỡ trước test, không giảm số bootstrap sau khi thấy CI. Tổng dự trù p2 gồm hậu kỳ khoảng **3–5,5 giờ**; chưa có chi phí điện năng đo được.

## 9. Phê duyệt theo hai bước

Hiện tại chỉ hoàn tất thiết kế/audit số học trên evidence cũ. Trước bất kỳ test mới nào, owner phải duyệt bốn tài liệu, các ngưỡng, panel/hash, beam rule, host/guard/quota và scope p2-only; ghi dated receipt cùng SHA của đúng bốn file và runner/analyzer/schema/dependency lock đã freeze. Approval thiết kế không ngầm cho phép chạy benchmark.

Sau authorization riêng cho quality-only, tạo file ID theo recipe đã khóa, rehash, chạy đúng quality phase và xuất gate report. **Mở performance cần owner phê duyệt tiếp trên báo cáo cụ thể:** A PASS; B PASS nếu muốn kết luận cross-arm; đầy đủ parity/provenance/guard và schedule/analysis receipt. Không cần quality B PASS để đo A, nhưng phải ghi B HOLD rõ ràng trước OFF. Không thực hiện bất kỳ bước chạy nào trong task soạn tài liệu này.

Historical P0/Full P1/t0998/B1+A1 official HOLD, P3 CLOSED, V4 D1–D5 UNAPPROVED, H3/TP-CG NOT_OPENED; i5-14600KF NOT_RUN; Task A Google Sheets UNMODIFIED. Không dùng nghiên cứu này để đổi nhãn D1 UNTESTED, D4 NOT TESTED, D6 INCONCLUSIVE hoặc làm bằng chứng cho lịch sử T16.

## 10. Verification và state sau remediation

Design-1 có test-suite dependency failures đã được giải quyết trong [audit design-1](AXD_G2_V2_PRE_APPROVAL_AUDIT.md), không sửa report đó. Design-2 kiểm RAM/CPU/affinity contract, exact parity/counters, weighted percentiles, strict 3% boundary, full 10.000 bootstrap resamples và schema bằng fixtures dataset-free; xem [remediation/re-audit và checksum](AXD_G2_V2_PRE_APPROVAL_REMEDIATION.md). Không dùng fixture timings hoặc simulated GO làm ANN evidence. Quality và OFF authorization vẫn chưa có; không có test v2/performance result mới.
