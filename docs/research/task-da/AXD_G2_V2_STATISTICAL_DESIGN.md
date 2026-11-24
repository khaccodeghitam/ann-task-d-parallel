# A×D G2 v2 · Statistical design

**EXPLORATORY_HOST_SPECIFIC · DESIGN_FOR_OWNER_APPROVAL · NO EXECUTION**  
Protocol `AXD-G2-V2-3A-20261123`, revision `design-2`, 23/11/2026. [Prereg v2](AXD_G2_PREREG_V2.md) là hợp đồng phạm vi; [criteria](AXD_G2_V2_GO_NO_GO_CRITERIA.md) khóa quyết định. Mọi số v2 bên dưới là phép tính thiết kế hoặc giả định planning, không phải phép đo Search mới.

## 1. Estimand và đơn vị độc lập

Gọi `R_gq=|Top10_returned ∩ Top10_GT|/10`. Đây là biến theo **query**, thuộc {0,0.1,…,1}. Mười GT hit của một query phụ thuộc nhau; không dùng N×10 Bernoulli độc lập để thu hẹp SE. Các graph dùng chung query nên cũng phụ thuộc nhau.

| Lớp | Đơn vị và uncertainty | Cách báo v2 |
|---|---|---|
| Query | 10.000 ID khác nhau từ pool lịch sử, cùng ID trên mọi cell | SE của recall/difference theo query; paired query bootstrap latency/tail riêng |
| Process | 12 execution block, mỗi block đủ sáu graph và hai policy | Paired block CI của OFF; sensitivity qua 6 cặp block liền nhau |
| Graph | Sáu graph cố định, ba invocation/arm, root independence chưa biết | Sáu effect, range, arm breakdown, leave-one-graph-out; không có population graph CI |
| Host/session | Một Ryzen 4650U và các khoảng thời gian được chạy | Điều kiện hóa trên môi trường này; không suy CI giữa CPU/ngày/dataset |

**A:** hiệu ứng bật B1+A1 trên cùng graph tại cùng Recall, trung bình đồng trọng số sáu graph. **B:** chênh Stock/Fast tại chất lượng tương đương của hai arm trong cohort đã nhận. Hai estimand không chia sẻ một cổng span. Build number r1/r2/r3 không chứng minh random seed được ghép cặp giữa hai arm.

Primary timing inference điều kiện trên fixed graph/panel/host. Mở rộng sang query pool dùng model exchangeability và sensitivity riêng; hash rank xác định không tạo được tính độc lập lịch sử. “CI95” trong hồ sơ này là khoảng danh nghĩa dưới các giả định được nêu, không phải bảo đảm phân phối tự do.

## 2. Vì sao span 0.0001 ở N=3.000 sai về định cỡ

Độ phân giải mean Recall ở N=3.000 là `1/(10N)=0.00003333`. Span 0.0001 chỉ cho phép chênh **3 hit** giữa cực đại và cực tiểu. Trên common beam 420, covariance thực nghiệm của hits validation Stage 5 cho SD của paired query difference khoảng **0.01460–0.02350**; vì vậy:

`SE(pair difference; N=3.000) = SD/√N ≈0.000267–0.000429`.

Một SE đã lớn hơn tolerance 2,7–4,3 lần. Sai số 95% một pair khoảng ±0.00052–0.00084; chọn max/min trong sáu graph làm span còn rộng hơn. Với N=10.000, SE pair vẫn khoảng 0.000146–0.000235; tăng N lên 10k **không cứu được** span 0.0001.

Muốn half-width CI95 **một pair** bằng 0.0001, công thức planning `N=(1.96×SD/0.0001)²` cho khoảng **81.888–212.153 query**. Đây chỉ là precision cho một pair, chưa phải power equivalence toàn bộ sáu graph và có phần vượt cả public pool 100k. Thêm process repeats trên cùng IDs không làm Recall deterministic có thêm query độc lập.

[Resolution v1](AXD_G2_QUALITY_HOLD_RESOLUTION_DECISION.md) đã báo mô phỏng CLT zero-mean, covariance validation, B=50.000: xác suất span≤0.0001 khoảng 0,03% ở 3k và 0,55% ở 10k. Các tỷ lệ đó phụ thuộc model và covariance; không phải định lý “bất khả thi tuyệt đối”. Trong thiết kế này, phép tính SE/precision ở trên là lý do độc lập để bỏ **vai trò khoa học** của span khỏi A trong protocol mới. Điều đó không đổi kết quả FAIL cổng span của v1.

Stage 6 đo span 0.001033 và paired SE cực trị khoảng 0.000393 trên đúng test cũ. Số này mô tả lịch sử, không dùng để chọn một threshold vừa đủ vượt kết quả ấy. Không có threshold v2 được định nghĩa bằng span Stage 6 cộng epsilon.

## 3. Gate A: absolute Recall floor và power

### 3.1 Floor, interval và lý do

Đề xuất floor **R₀=0.990** cho workload Recall@10 cao: trung bình cho phép thiếu tối đa 0,1 top-10 neighbor/query. Đây là operating target được owner chọn lại để duyệt, phù hợp câu hỏi Search high recall; không tuyên bố đáp ứng ứng dụng/SLA ngoài nghiên cứu, cũng không dùng điểm .998 của lane khác.

Ở fixed graph:

`r_g = mean_q R_gq`, `SE_g = sample_SD(R_gq)/√N`.

Gate yêu cầu cả sáu graph có `r_g ≥ R₀` và

`LCB_g = r_g − z(1−0.05/6)×SE_g ≥ R₀`, với `z=2.39397980`.

Bonferroni tạo **simultaneous one-sided nominal 95% bounds cho sáu graph tại p đã khóa**, không cần giả định các graph độc lập. Hai policy exact output parity chia sẻ cùng Recall; không xem đó là 12 graph. Báo thêm CI95 hai phía từng graph để người đọc thấy precision, nhưng không thay gate bằng CI tiện lợi hơn. Xấp xỉ normal cho mean theo query được dùng nhất quán; không dùng Wilson/binomial trên 100.000 hit giả độc lập.

Không áp dụng finite population correction trong gate: inference mục tiêu là query distribution được pool lịch sử đại diện theo model, không chỉ mean hữu hạn của 81k ID. Nếu chỉ hỏi mean trên đúng pool hữu hạn và giả định lấy mẫu ngẫu nhiên không hoàn lại, FPC khoảng `√((81000−10000)/80999)=0.936`; có thể báo phụ, không dùng để cứu PASS.

### 3.2 Cỡ mẫu cho floor khác với cỡ mẫu cho parity

Giả sử query SD 0.036, dựa trên quy mô validation đã thấy, và true margin `m=R−R₀`. Planning normal:

- Power 80% cho **một graph**, dùng critical value simultaneous: `N≈[(2.394+0.842)×0.036/m]²`.
- Mục tiêu xác suất **cả sáu graph** PASS ≥80% bằng union bound Type II: mỗi graph power ≥96,667%; `N≈[(2.394+1.834)×0.036/m]²`.

| True Recall giả định | Margin m | N cho một graph 80% | N cho cả sáu ≥80%, conservative |
|---:|---:|---:|---:|
| 0.9910 | 0.0010 | 13.568 | 23.167 |
| 0.9913 | 0.0013 | 8.029 | 13.708 |
| 0.9915 | 0.0015 | 6.031 | 10.297 |

N=10k không mặc nhiên đủ cho mọi operating point. Vì vậy calibration v2 dùng **assurance rule** `r_gb−4.22789444×SE_gb≥0.990` trên cả sáu graph, lấy common beam nhỏ nhất trong grid validation cố định. Công thức là tổng critical floor và dự phòng Type II nói trên, không đặt theo khả năng test dễ PASS. SD/mean ước lượng từ validation tạo plug-in optimism; true power vẫn UNKNOWN trước test.

Replay từ hits Stage 5 ở common b=432: min Recall validation 0.991590, max query SD khoảng 0.034386, min assurance score 0.99013620; b=424 min score 0.98988202. Ứng viên mới là b=432, dù bộ beam v1 là 420/420/420/420/416/412. Không sửa bộ beam cũ hoặc chạy evaluator để lấy con số replay. Nếu owner không chấp nhận operating point/power trade-off này, phải sửa **thiết kế trước test**, không chọn threshold sau test.

Exact ordered Top-10 và L2² parity trên 60.000 graph-query pair là kiểm tra đúng đắn trên toàn panel, không phải equivalence bằng thiếu ý nghĩa thống kê. Zero mismatch không chứng minh thuật toán đúng với mọi input; query/root/host khác vẫn ngoài phạm vi. Không lấy zero variance của paired ΔRecall để khẳng định uncertainty của absolute Recall bằng zero.

## 4. Gate B: equivalence cấp arm, không nhầm với không khác biệt

Trên query q:

`d_q = (R_F1q+R_F2q+R_F3q)/3 − (R_S1q+R_S2q+R_S3q)/3`.

Tính `d̄ ± t(0.975,N−1)×sample_SD(d_q)/√N`; giữ covariance bằng tính difference trước rồi mới SE. Không lấy SD giữa ba graph chia √30.000 và không giả định Stock-rj/Fast-rj là paired build.

**Equivalence margin đề xuất ε_R=0.0005**, tức 0,05 percentage point Recall, hoặc 0,005 hit/query, bằng **5% miss budget 1−0.990**. Đó là ngân sách sai khác chất lượng kỹ thuật chờ owner duyệt, không phải tolerance đã có từ ứng dụng và không được suy từ span test cũ. Không biết ảnh hưởng latency của 0.0005 Recall chính xác là bao nhiêu; equivalence này chỉ cho phép tuyên bố “matched trong ±0.0005”, không “quality identical”.

Gate: CI95 nằm **hoàn toàn bên trong (−ε_R,+ε_R)**. Không thêm điều kiện point≤0.0003; không áp span≤0.0006. **CI95 containment chặt hơn TOST α=0.05 thông thường**, vốn tương ứng CI90; nếu gọi TOST ở đây thì mỗi one-sided test dùng α=0.025. Không tráo hai cách sau khi xem dữ liệu. [Lakens, Equivalence Tests](https://doi.org/10.1177/1948550617697177).

Common beam cho sáu graph tại một p chặn lợi thế được cấp beam thấp riêng cho Fast. Nó không tự làm graph quality tương đương; gate B vẫn có thể HOLD. Gate A PASS/B HOLD không ngăn phép thử A, nhưng ngăn tuyên bố Stock/Fast thắng tại matched Recall hoặc ΔT matched quality.

### 4.1 N cho B

Validation common beams cho SD(d_q) khoảng 0.0086–0.0098; dùng **0.010** làm kịch bản planning làm tròn, không coi là cận trên được chứng minh. Ở N=10k, SE≈0.0001, half-width CI95≈0.000196. Với normal/known-SD approximation:

`Power = Φ((ε−1.96SE−δ)/SE) − Φ((−ε+1.96SE−δ)/SE)` khi `ε>1.96SE`, δ là true arm difference.

| True absolute gap giả định | Power ở N=10k, SD=0.010 | N conservative cho ≥80% bằng `(1.96+1.282)² SD²/(ε−|δ|)²` |
|---:|---:|---:|
| 0 | 99,76% | 4.204 |
| 0.0002 | 85,08% | 11.676 |
| 0.0003 | 51,60% | 26.270 |

Công thức N conservative yêu cầu central 80% sampling error nằm trong khoảng hẹp nhất còn lại, nên có thể lớn hơn N từ exact normal power. Khi δ sát margin, N cần tăng nhanh; true δ ngoài margin không thể được chữa bằng tăng N. Không mở test bổ sung để đạt PASS trong v2. Nếu CI quá rộng hoặc equivalence không đạt, kết quả B là HOLD/không matched, không sửa ε_R.

N cho A là floor/parity và paired latency precision; N cho B là equivalence khác biệt nhỏ liên-arm. Không dùng power của B để chứng minh A đủ power hoặc ngược lại. Equivalence arm không chứng minh mọi Stock–Fast graph pair tương đương. Báo Recall từng graph, toàn ma trận paired difference/CI mô tả và min/max; không che graph yếu bằng arm average. Root population equivalence vẫn NOT_ESTIMABLE.

## 5. Process-level paired timing cho A

Mỗi process cho arithmetic mean latency `B_gb` và `C_gb` (base/opt). Định nghĩa:

`x_gb=log(B_gb/C_gb)`, `x_b=(1/6)Σ_g x_gb`, `x̄=(1/12)Σ_b x_b`.

CI95 chính: `x̄ ± t(0.975,11)×SD(x_b)/√12`, với t≈2.201. Biến đổi đơn điệu sang speedup `exp(x)` và reduction `1−exp(−x)`. Đây là geometric aggregation của mean-latency ratios; không phải ratio của arithmetic latency toàn cohort. Báo cả hai cùng absolute µs/query, không gắn CI của estimator này cho estimator kia.

Các graph trong block chia sẻ host drift; lấy block làm đơn vị tránh xem 72 graph-pair measurements là 72 lần lặp ngoài độc lập. Cặp base/opt liền nhau và balanced AB/BA giảm drift/order confounding, không loại hết chúng. CI paired dùng SD của difference/log-ratio, theo nguyên tắc [NIST paired observations](https://www.itl.nist.gov/div898/handbook/prc/section3/prc311.htm).

Mỗi graph có CI qua 12 x_gb (df=11); Stock/Fast subgroup lấy mean ba graph **trong block** trước khi CI. Không bootstrap ba graph như independent-root population. Các per-graph/subgroup CI mô tả không là sáu discovery test độc lập. Primary chỉ có một endpoint mean latency; p50/QPS/secondary contrasts không tạo primary mới.

Primary duy nhất là **geometric paired mean-latency ratio**, giữ nguyên estimator design-1. Arithmetic cohort mean latency và ratio-of-means là secondary descriptive/BUILD–SEARCH inputs; không được dùng để đổi quyết định 3%. Strict CI/TOST comparisons dùng tie epsilon1e-12 (log-effect hoặc Recall scale); numeric tie giữ HOLD, không làm PASS.

### 5.1 Minimum practical effect và số repeat

Đề xuất reduction **3%**: θ=`−log(0.97)=0.03045921`. GO đòi lower CI>θ, không chỉ point≥3% và lower CI>0. Đây là mức sẵn sàng chấp nhận độ phức tạp của policy thêm vào: ở latency 3–6 ms, tiết kiệm 90–180 µs/query, 9–18 s/100k query; là phép đổi đơn vị planning. Chưa có SLA hoặc phân tích chi phí bảo trì để chứng minh 3% là tối ưu. Owner phải chấp nhận con số này trước mở test; không lấy gain lịch sử A3 làm dự báo R90.

Giả sử SD process-block log-ratio là 1/3/5% (giả định, không đo R90 OFF). Với 12 block, half-width CI95 log-effect xấp xỉ **0,64/1,91/3,18 percentage point** gần gốc. Normal planning cho 80% power kiểm effect lớn hơn θ:

`m≈[(1.96+0.842)×σ_process / (−log(1−true_gain)−θ)]²`.

| True reduction giả định | m khi SD=1% | SD=3% | SD=5% |
|---:|---:|---:|---:|
| 5% | 2 | 17 | 46 |
| 6% | 1 | 8 | 20 |
| 8% | 1 | 3 | 8 |

Các m=1/2 là giới hạn của normal planning, không thiết kế t-CI khả dụng; Student-t và dependence làm m thực cần lớn hơn. **12 block được khóa vì cân bằng đủ sáu vị trí × hai order và budget nhỏ**, không vì bảo đảm 80% ở mọi variance/effect. Hiệu ứng thật chỉ 5% với SD3% có thể vẫn HOLD. Không tăng m khi thấy CI gần đạt.

Drift sensitivity bắt buộc: ghép block (0,1), (2,3), …, (10,11), lấy sáu mean log-effects và CI95 t df=5. GO cần cả CI12 và CI6 lower>θ. Nếu drift kéo dài hơn hai block hoặc môi trường thay đổi có hệ thống mà pairing không kiểm soát, inference còn UNKNOWN/HOLD; không kiểm normality rồi chọn phương pháp cho kết quả đẹp.

## 6. Query-level uncertainty của latency và tail

10k timing queries không phải 10k process repeats. Phân bố latency có cả query difficulty, cache/order và host noise; dùng hai sensitivity đã khóa thay vì chỉ một CI quá hẹp:

1. **Query-only:** giữ mọi process cố định; resample 100 khối query liên tiếp, mỗi khối 100 vị trí trong hash order, có hoàn lại để được 10k. Dùng cùng vị trí resample cho mọi graph/policy/repeat. Tính lại arithmetic mean và percentiles trong từng process rồi estimator toàn cohort.
2. **Joint query × process:** resample 12 execution block có hoàn lại và 100 query-position blocks như trên, độc lập giữa hai chiều; cùng indices trên mọi paired cell. Không resample từng policy riêng; không làm mất tương quan query/host.

Dùng **10.000 bootstrap replicates cho mỗi scheme**, PRNG chuẩn Python `random.Random(20261123)`, percentile CI theo thứ tự statistic, nội suy tuyến tính q×(B−1). Mỗi scheme khởi tạo RNG riêng cùng seed; mỗi replicate query-only dùng 100 lần `randrange(100)` cho query blocks; joint dùng trước 12 lần `randrange(12)` cho execution blocks, rồi 100 lần `randrange(100)` cho query blocks. Khóa phiên bản Python/analyzer trong receipt. Query-only cho sensitivity conditional trên host observations; joint cho sensitivity query/process theo model crossed blocks. Không resample graph. Block length 100 là lựa chọn bảo thủ đơn giản (~100 query clusters), không chứng minh bao hết temporal dependence. Báo sensitivity drift ở §5 cùng với bootstrap; GO yêu cầu joint CI95 lower reduction>3% nữa. Nếu các khoảng mâu thuẫn, HOLD uncertainty, không chọn khoảng hẹp nhất.

Triển khai hậu kỳ phải dùng block sums/batched array operations cho mean; tail có thể dùng integer query multiplicities trên latency order đã sort, lấy hai weighted ranks và nội suy đúng q×(N−1). Cách này phải cho đúng kết quả của sample lặp thật, không được đổi sang approximation khác để tiết kiệm thời gian. Không viết generic instrumentation framework. Analyzer đã triển khai với batched exact weighted ranks và đã đối chiếu explicit resampling trên fixtures; đầy đủ10.000 replicates được kiểm trên tensor tổng hợp. Runtime trên ANN/nonconstant tail chưa đo, không suy từ fixture speed. Dự trù offline riêng ở prereg, không coi xử lý hậu kỳ là ANN throughput gain.

Planning query precision: nếu SD của paired query difference chia baseline mean là c, half-width relative h xấp xỉ `1.96c/√N`. Muốn h=2%, N≈385/2.401/9.604 khi c=0.2/0.5/1.0. **c chưa biết**; clustering, ratio và serial noise có thể làm N cần lớn hơn. Vì thế N=10k không được gọi là power calculation đã xác nhận cho latency. Không cộng N qua 12 repeats như query IDs mới.

Percentile được tính trên latency gốc từng process, không lấy percentile của query ratios và không gộp 12 process thành một latency distribution rồi bỏ process variance. N=10k có khoảng 500 điểm phía trên p95, 100 phía trên p99 (3k chỉ khoảng 30 điểm phía trên p99). Rank CI95 binomial lý tưởng cho percentile xấp xỉ p95 rank **9457–9543**, p99 **9880–9920**; độ rộng theo thời gian còn phụ thuộc mật độ tail và serial dependence. Không chuyển rank precision thành một bảo đảm ±x% latency.

## 7. Tail và RAM là cổng bảo vệ riêng

Cho graph g/block b:

- `u95_gb=log(p95_opt/p95_base)`, `u99_gb=log(p99_opt/p99_base)`.
- `v_gb=(RSS_opt−RSS_base)/max(65536 KiB,0.10×RSS_base)`.

RAM chỉ dùng integer KiB dương từ `p2_eval_summary.vm_hwm_kib` đến capture gần cuối process; wrapper sampled RSS là diagnostic phụ. Mỗi cặp phải qua **hard gate** `10(C−B)≤max(655360,B)`, equality PASS. Vượt hoặc thiếu/zero/âm/nonfinite/fractional RSS: HOLD_RAM/INVALID, dừng và giữ raw; không averaging hay chạy bù. Combo-first chỉ đánh giá relative cap sau base cùng cặp; live absolute RAM guard vẫn áp. Chỉ với đầy đủ cặp hợp lệ mới tính aggregate uncertainty. Convert KiB/MiB rõ ràng. Cho từng graph lấy mean qua 12 block, simultaneous one-sided upper bounds dùng **t(1−0.05/18,11)** cho 18 graph×endpoint (6×p95/p99/RAM); không giả định endpoint độc lập. Tail budgets đề xuất p95≤+5%, p99≤+10%; RAM budget≤max(64 MiB,10% baseline). So trên scale log cho tail và scale v cho RAM. Mean các log-quantile ratio là geometric typical process-tail change, phải báo cả max quan sát từng process.

Đây là envelope kỹ thuật được đề xuất lại cho pilot, không lấy từ việc xem OFF v2. p99 được budget rộng hơn p95 do nhạy với noise và số điểm tail ít hơn; CI rộng vẫn HOLD, không miễn gate. RAM budget giới hạn overhead triển khai nhỏ trong bối cảnh search process lịch sử ~0,83 GiB; không suy mức này từ RAM của BUILD host A. Safety guard về available RAM/swap vẫn áp độc lập và có thể dừng sớm hơn.

GO cần **mọi per-pair RAM hard gate** cùng đủ 18 upper bounds không vượt budget. Uncertainty quá rộng là HOLD. Lower bound đồng thời vượt budget là bằng chứng regression, có thể PIVOT dù mean nhanh. Báo query/joint bootstrap tail CI như sensitivity; nếu upper joint per-graph CI95 vượt budget, HOLD claim an toàn tail (không dùng để đảo một fail của simultaneous bounds).

## 8. B: Search, BUILD–SEARCH và scaling

Latency arm trong một block là arithmetic mean ba process means; QPS arm là mean ba QPS_wall, ghi rõ đây là trung bình index, không cộng throughput ba index. So cùng policy giữa Stock/Fast bằng log arm ratios qua block; gộp ba graph trước SE để giữ covariance thời gian. Cross-arm không có paired-root CI, dù cùng query.

BUILD time/graph bytes có ba giá trị mỗi arm từ receipt cũ; báo toàn bộ và arithmetic mean/range. Không t-test roots độc lập khi independence chưa xác minh. `T(Q)` và break-even dùng arithmetic latency. Với mỗi block và contrast U−V, tính `ΔT_b(Q)=mean_BUILD_U−mean_BUILD_V+Q×(mean_latency_U,b−mean_latency_V,b)` bằng giây; point là mean qua block, CI95 t df=11 và joint bootstrap sensitivity giữ BUILD constants cố định. Same-construction contrasts có BUILD difference bằng 0. Positive ΔT nghĩa V tiết kiệm tổng thời gian so với U. Break-even là nghiệm dương của `ΔBUILD+Q×Δlatency=0`; nếu slope bằng 0 hoặc nghiệm không dương thì báo không có break-even dương, không ép một giá trị. CI process/query có điều kiện trên sáu BUILD đã quan sát. Hai host BUILD/SEARCH, load/transfer chưa đo và thiếu population BUILD variance ngăn tuyên bố end-to-end deployment gain tổng quát. Không nhập chi phí mới từ i5-14600KF.

Design-2 freeze **p2-only**. Scaling p1/p4 không được thực thi hoặc suy luận bởi package này. Muốn extension phải prereg riêng trước dữ liệu extension, có balanced worker order và Recall matching; không gọi cùng block ordinal ở các strata tuần tự là contemporaneous pairing. Công thức speedup/efficiency giữ ý nghĩa L1/Lp và speedup/p nhưng chưa có dữ liệu hoặc claim scaling.

## 9. Khóa phân tích và giới hạn kết luận

Không có interim efficacy look, early GO, optional stopping hay thêm query/repeat sau khi biết effect. Guard/quota dừng vì an toàn/resource cho kết quả incomplete/HOLD; không impute cặp bị thiếu, không loại slow run, không đổi estimator hoặc giới hạn graph để cứu primary.

Trước test, receipt phải chứa SHA của bốn tài liệu, panel/ordering, selected-beam manifest, balanced schedule, runner/analyzer và Python/package versions. Runner/analyzer/CPU-RAM guard extension/schema đã triển khai, version `axd_g2_v2.2` và hash trong freeze manifest. Chỉ chuẩn bị package; không có authorization để chạy. Các threshold/CPU windows/hard-stop và host profile tuân [prereg](AXD_G2_PREREG_V2.md) §8; không thay estimator/beam/query split sau kết quả. Dataset-free tests của repo không thay thế future receipts/gates.

Nếu muốn power lớn hơn hoặc biên Recall hẹp hơn, cần một **thiết kế mới trước dữ liệu kế tiếp**, có thể tăng query ngoài public pool, independent-root graph và host replication. Không có cách phân tích nào biến pool đã dùng, một host và sáu root chưa xác minh thành fresh confirmatory evidence. Nhiều query/repeat không khắc phục được giới hạn graph/root hoặc thiên lệch tái thiết kế sau v1.
