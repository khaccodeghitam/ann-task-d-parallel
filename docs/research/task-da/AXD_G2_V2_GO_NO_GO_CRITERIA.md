# A×D G2 v2 · GO / HOLD / PIVOT và approval contract

**EXPLORATORY_HOST_SPECIFIC · PROPOSED_CRITERIA · PERFORMANCE_NOT_OPEN**  
Protocol `AXD-G2-V2-3A-20261123`, revision `design-2`, 23/11/2026. [Prereg](AXD_G2_PREREG_V2.md) · [Statistical design](AXD_G2_V2_STATISTICAL_DESIGN.md) · [Split audit](AXD_G2_V2_QUERY_SPLIT_AUDIT.md).

**Hiện tại:** v1 đóng tại `QUALITY_HOLD` theo chỉ thị owner; v2 đã có package runner/analyzer được kiểm bằng dataset-free fixtures, chưa có quality test v2 hay timing v2. **Không có cơ sở GO hoặc PIVOT thực nghiệm mới trong task này.** Trạng thái tiếp theo là `AWAITING_OWNER_DESIGN_APPROVAL`, không phải tự mở performance. Historical evidence và trạng thái các lane khác giữ nguyên.

## 1. Threshold ledger phải khóa trước test

Các ngưỡng là lựa chọn thiết kế có lý do, không phải ước lượng lợi ích hoặc SLA đã được xác nhận. Owner phải duyệt tính phù hợp của chúng. Nếu muốn thay, làm trước test v2 và ghi revision; không lựa chọn theo việc kết quả dễ PASS.

| Tham số | Đề xuất v2 | Lý do và giới hạn |
|---|---|---|
| Absolute Recall floor | **0.990**, point và simultaneous one-sided LCB95 sáu graph | High-recall operating target, miss budget 0.010; không thừa kế máy móc point-only gate v1 |
| Recall interval | Mean/SE theo query, z(1−.05/6)=**2.39397980** | Giữ covariance, kiểm sáu graph; approximate simultaneous coverage |
| Validation assurance | Mean−**4.22789444**×SE≥0.990, common beam nhỏ nhất trong grid | Dự phòng khoảng 80% all-six floor power theo plug-in normal; không tối ưu span |
| Cross-arm equivalence | **CI95 nằm trong (−0.0005,+0.0005)** của Fast−Stock | ±5% miss budget; cấp arm fixed cohort. Không point-gap 0.0003, không span 0.0006 |
| Primary practical latency gain | **3% geometric paired reduction**, lower CI vượt 3% | Mức engineering tối thiểu chờ owner duyệt; không chỉ significance so với zero |
| Repeats | **12 complete blocks**, 144 p2 OFF processes | Đủ hai vòng sáu vị trí và 6 AB/6 BA/graph; không đảm bảo power mọi variance |
| p95 / p99 regression budget | **+5% / +10%** | Service envelope đề xuất, p99 nhạy/noisy hơn; CI rộng dẫn HOLD |
| RAM overhead budget | **max(64 MiB,10% baseline peak RSS)** mỗi paired process | **Mọi cặp** phải đạt integer hard gate, thêm aggregate CI; pinned ELF HWM đến capture, không thay available-memory guard |
| Tail/RAM uncertainty | Simultaneous upper bounds 18 endpoint, t(1−.05/18,11) | Tránh che graph regression bằng cohort mean; thêm bootstrap sensitivity |
| Heterogeneity | Sáu graph point gain>0; Stock/Fast point gain≥3%; mọi leave-one-out point gain≥3% | Không cho một graph/arm tốt quyết định GO toàn cohort; đây là stability screen, không chứng minh population homogeneity |
| CPU/load | /proc owned utime+stime, 1Hz, window≥5s; foreign CPU≤1% p2 capacity/≥5s | Noise budget=1/3 minimum3%, engineering proposal; vượt/missing/gap/PID reuse dừng, không drop/replace |
| Quota đề xuất | p2 **1 giờ quality +3 giờ OFF**, analysis riêng3h; scaling NOT_SUPPORTED | Bao gồm preflight/cooldown, không dùng lại quota pilot v1; incomplete là HOLD |

Common beam không chứng minh cross-arm Recall equivalent. Gate A không cần span; gate B không được bypass bằng exact parity nội graph. Không chấp nhận Fast thắng vì dùng beam thấp riêng hoặc Recall thấp ngoài equivalence margin.

## 2. Cổng trước OFF

| Gate | PASS phải có | Khi không đạt |
|---|---|---|
| Identity | Sáu graph/input/ELF/package/source pins khớp, protocol/panel/schedule/analyzer SHA khóa | HOLD_PROVENANCE, không substitute/build lại trong v2 |
| Split | Đúng 10k ID/order/SHA, rời val và ba panel3k; disclosure Task A/R86/P1 | HOLD_SPLIT; không đổi seed để chọn test khác |
| Validation lock | Beam chọn từ validation-only theo rule; validation base/opt exact IDs/L2² và counters | HOLD_CALIBRATION; không dùng test để sửa |
| A quality | Đủ Top10 duy nhất/query; exact ordered IDs/L2² trên 60k pair; six simultaneous LCB≥0.990; invariants PASS | QUALITY_HOLD_V2, không OFF |
| B quality | A PASS và arm Recall CI95 trọn trong ±0.0005 | HOLD_B; có thể xét mở A-only nếu owner duyệt rõ |
| Host/guard | Ryzen 4650U đúng topology/CPU list; sensor/AC/RAM/disk/swap/lock/watchdog/foreign CPU workload checks hoạt động | HOLD_SAFETY; không tăng ngưỡng hay kill process ngoài phạm vi |
| Owner performance approval | Dated approval trỏ đúng quality report và immutable receipts, xác định A-only hoặc A+B | PERFORMANCE_NOT_OPEN |

Giá trị point/LCB/CI phải lưu đầy đủ cả khi trượt; boundary equality của equivalence là không PASS. Exact parity là equality trên toàn bộ output, không tolerance trên Recall mean. Guard failure không được thay bằng “host trông ổn”.

Quality-only authorization tương lai không bao gồm OFF. Approval thiết kế hiện tại cũng không bao gồm bất kỳ benchmark nào. Đây là hai bước cần owner duyệt theo phạm vi user yêu cầu, không phải yêu cầu thêm xác nhận cho công việc phân tích/tạo tài liệu đã được phép.

## 3. Quy tắc kết luận sau một campaign hợp lệ, đủ dữ liệu

### GO_A_FIXED_COHORT

Tất cả điều kiện sau phải cùng đạt:

1. Gate A/provenance/parity/guard PASS, đủ **12 complete blocks trên cả sáu graph**; mọi OFF khớp ON v2 đúng cấu hình. Không bỏ lượt chậm/lỗi hoặc chọn repeat.
2. Primary fixed-cohort reduction có **lower CI95>3%** từ 12 block log-ratios; drift sensitivity 6 adjacent-block pairs cũng có lower CI95>3%; joint query×process bootstrap CI95 lower>3%. Các estimator và bootstrap giữ đúng statistical design.
3. Cả sáu graph có point reduction>0; riêng Stock và Fast đều point reduction≥3%; sáu phân tích bỏ lần lượt một graph đều point reduction≥3%. Trình bày đủ effect/CI từng graph, không chỉ overall.
4. Trên mỗi graph, upper bound đồng thời của p95/p99 regression không vượt +5%/+10%; **mọi cặp** RAM normalized overhead≤1 và upper bound aggregate≤1; integer comparison `10(C−B)≤max(655360,B)`. Upper joint-bootstrap per-graph tail CI95 cũng không vượt budgets. Không có swap/resource/CPU telemetry/contention failure. Missing/invalid RSS là INVALID, không zero; hard RAM vượt giữ raw và dừng ngay sau cặp, không dùng mean che giấu. Equality budget PASS, strict3% CI numeric ties≤1e-12 giữ HOLD.
5. Diagnostic ON cho thấy đúng accounting và giảm duplicate L2 trên cả sáu graph; total/unique/duplicate evaluations và added bookkeeping được báo riêng. Counter reduction không thay điều kiện latency. Nếu timing tốt mà work prediction không khớp, giữ HOLD phần giải thích cơ chế thay vì tuyên bố duplicate reduction gây gain.

Nhãn GO chỉ cho phép nói B1+A1 tạo cải thiện Search latency thực dụng **trên fixed cohort, query panel/pool theo model và Ryzen đã đo**, với tail/RAM trong envelope đã duyệt. Không nâng thành thuật toán mới, kết quả tất cả CPU hoặc independent-root generalization.

GO_A không cần B PASS. Nếu B HOLD, báo rõ “A PASS; cross-arm matched-quality conclusion HOLD”. Việc vẫn đo đủ sáu graph không trao quyền so Fast với Stock như chất lượng exact.

### GO_B_FIXED_COHORT / BUILD–SEARCH claim

Đây là nhãn riêng, không điều kiện để primary A có giá trị:

- A quality và B equivalence PASS; ma trận Stock/Fast × base/opt đầy đủ, cùng engine, p/S và common beam tại p đó.
- Báo chính xác BUILD times/graph sizes từ receipt lịch sử đúng SHA, Search OFF contemporaneous và QPS đúng cửa sổ. Mô hình hai host và CI conditional trên BUILD phải xuất hiện cạnh kết luận ΔT.
- Kết luận Fast tốt hơn ở một contrast latency cụ thể chỉ khi CI95 contrast hỗ trợ dấu lợi ích; CI còn bao zero là chưa đủ. Các contrast secondary phải được ghi là exploratory, không chọn một contrast tốt rồi đổi primary.
- Nếu gọi hệ thống kết hợp có lợi thực dụng tại **Q₀=100.000**, lower CI95 của `T_Stock-base−T_Fast-opt` phải >0; đồng thời point `T_Fast-opt` thấp hơn cả Fast-base và Stock-opt. Báo thêm CI của cả hai đối chiếu đó; khi CI bao zero chỉ nói lợi ích tích hợp chưa tách chắc khỏi cải tiến đơn. Không dùng ΔT để cứu GO_A đã trượt 3%.

Không có population BUILD CI khi root independence chưa biết. Nếu yêu cầu deployment end-to-end có transfer/load mới đo, giữ HOLD phần đó cho đến khi có thiết kế/receipt riêng.

### HOLD

Chọn HOLD cho đúng tầng, không gọi thiếu bằng chứng là thất bại thuật toán:

- Quality floor/equivalence, provenance, parity, guard, timeout, quota hoặc completeness không đạt.
- Primary CI còn bao cả vùng dưới và trên 3%; process/query/drift sensitivity mâu thuẫn; tail/RAM CI quá rộng.
- Effect chỉ rõ ở một graph, một construction arm; một leave-one-out dưới 3%; hoặc một graph point regression nhưng chưa chứng minh chi phí quá budget.
- A đạt nhưng B chưa equivalent: HOLD_B, có thể giữ GO_A scoped. scaling ngoài scope: NOT_SUPPORTED, không làm mất phép thử p2 hợp lệ.

Không tự thêm query/graph/repeat, đổi beam/S/policy order, lọc outlier, nới margin hoặc đổi arithmetic/geometric estimator sau khi biết kết quả. Partial receipts luôn được lưu; recovery hoặc nghiên cứu tăng precision là revision mới trước dữ liệu kế tiếp.

### PIVOT_TO_TASK_A_BUILD_SEARCH

Chỉ xét sau campaign A hợp lệ và đủ dữ liệu, hoặc có bằng chứng resource regression rõ trong campaign đã giữ raw:

- Upper CI95 primary reduction **<3%** và upper CI95 Fast-subgroup reduction **<3%**: loại lợi ích đạt mức thực dụng đã duyệt trong scope này. Có thể vẫn có gain nhỏ dương; không viết “B1+A1 vô tác dụng mọi graph”. Nếu Stock/Fast kết luận khác nhau, ưu tiên HOLD/scope-specific decision và công bố sự khác nhau.
- Hoặc lower simultaneous bound của p95/p99/RAM overhead vượt budget trên graph thuộc deployment target: chi phí phụ đã có bằng chứng lớn hơn envelope chấp nhận, dù mean latency có lợi. Report phải chỉ đúng graph/endpoint thay vì quy kết mọi cấu hình.
- Nếu duplicate L2 giảm nhưng CI OFF loại lợi ích ≥3%, đó là falsifier cho **giá trị Search của tổ hợp triển khai tại p2/S16 trên cohort này**, không bác bỏ lý thuyết tiết kiệm công và không xác nhận bottleneck D khác.

Hành động pivot là tập trung đánh giá Task A BUILD–SEARCH trade-off với Fast-only/Stock, vẫn cần matched Recall. Không gán mặc định Fast thắng BUILD–SEARCH nếu B không đạt; không sửa Task A Google Sheets hoặc mở build/search mới từ quyết định pivot này.

## 4. Scope freeze p2-only

Package design-2 chỉ hỗ trợ p=2/S16/CPU[0,2]/beam432. p1/p4 NOT_SUPPORTED và không có option approval để bật; extension sau này phải có prereg/order worker strata cân bằng/quality gates riêng trước dữ liệu extension. Không dùng p1/p4 thay primary p2 hoặc chọn sau khi thấy p2. Scope này đóng C2 mà không giả định host drift đã được khắc phục.

## 5. Hồ sơ owner cần duyệt để mở performance

**Bước 1 — trước quality-only execution (chưa được phép trong task này):**

- Đồng ý đóng v1 tại QUALITY_HOLD và giữ nguyên Stage 5/6; nhận nhãn exploratory/public-pool reuse và fixed-root limitations.
- Duyệt đúng bốn file v2 cùng SHA/revision, toàn threshold ledger và estimator; nhận rằng N10k/m12 không bảo đảm power trong mọi kịch bản.
- Duyệt panel recipe/hash, beam432 đã khóa, không retune, host 4650U, guard, không tune host, full 10k timing và budget 4 giờ; scope p2-only; không cấp quyền scaling.
- Nhận runner/analyzer/schedule/schema với source/base-commit + full content SHA, exact package/wheel pins, full argv plans và dataset-free checks phù hợp trong freeze manifest; panel chỉ được materialize/hash đúng recipe trong một task quality-only được phép. Không cần thay frozen search ELF.

**Bước 2 — trước OFF performance:**

- Có báo cáo quality v2 thực tế và receipts: A PASS, B PASS nếu mở B; 6 opt validation +12 test ON hoàn tất và parity/invariants/quality tables đầy đủ tại p2.
- Có beam manifest/panel SHA được khóa trước test; không có retune sau test; đủ audit immutable pins và host safety preflight.
- Có lịch 144 OFF đã cân bằng, quy tắc CI/stop/recovery, external raw destination đủ disk và quota còn đủ; owner phê duyệt bằng văn bản scope **A-only** hoặc **A+B**, không bao gồm p1/p4.

Không cần xin thêm quyền để hoàn tất bốn tài liệu hiện tại. Package code/schedule/schema đã reviewable qua freeze manifest và fixtures. Quality-only approval là bước kế tiếp; OFF vẫn cần quality receipts thực tế ở task được cấp phép tiếp, chưa có và không được giả định PASS.

## 6. Chênh lệch so với v1 và giới hạn quyết định

V2 tách A/B, dùng panel rời 10k từ pool lịch sử, common beam validation với power reserve, simultaneous floor thay point-only, equivalence CI thay global span, 12 block cân bằng thay 5 block, practical-effect CI>3%, thêm p99/RAM và query/process sensitivity. B có quality gate riêng; scaling ngoài package; span không chặn A.

Thiết kế hợp lệ hơn vì ràng buộc chất lượng bám đúng estimand, giữ pairing và đơn vị uncertainty, chống giảm Recall để lấy tốc độ và khóa quyết định trước dữ liệu mới. Nó không xóa post-v1 redesign, historical public-query exposure, validation reuse, một host, thiếu independent-root graphs hoặc uncertainty tail. Chi phí dự trù thu thập p2 **2,5–3,5 giờ** trên Ryzen, cap 4 giờ; scaling không nằm trong package hoặc quota hiện tại. Hậu kỳ p2 dự trù thêm **0,5–2 giờ** bằng analyzer vectorized/batched, quota riêng 3 giờ, thời gian thực chưa xác minh; tổng p2 khoảng **3–5,5 giờ**. Đây là planning từ ON cũ và ngân sách phân tích đề xuất, không phải measurement OFF mới.

Kết quả của task này chỉ là **thiết kế sẵn để owner review**. Không benchmark/profiler/G2 OFF, không sửa source/beam/graph/historical evidence, không i5-14600KF, không Google Sheets write.

Design-2 remediation được ghi ở [report/checksum/re-audit](AXD_G2_V2_PRE_APPROVAL_REMEDIATION.md). Audit cũ design-1 giữ nguyên như lịch sử, không phải trạng thái mới sau remediation. CPU affinity/profile/noise rule và invalid/abort source được khóa trong prereg§8 và executable contract; chỉ owner có thể duyệt thay đổi trước dữ liệu mới, không có auto-approval.
