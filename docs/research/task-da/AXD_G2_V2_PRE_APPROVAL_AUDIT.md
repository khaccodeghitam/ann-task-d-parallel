# A×D G2 v2 · Final pre-approval audit

**Kết luận: `NOT_READY_FOR_APPROVAL` · Quyết định hiện tại: `HOLD_PRE_APPROVAL`.**  
Ngày: 23/11/2026. Scope: `EXPLORATORY_HOST_SPECIFIC`, protocol `AXD-G2-V2-3A-20261123`, revision được audit `design-1`. G2 performance vẫn `NOT_OPEN`.

Dataset-free test failures đã được giải quyết bằng dependency trong môi trường tạm: **521 tests, 507 executed PASS, 14 native tests skipped theo opt-in có sẵn, 0 errors/failures**. Không tìm thấy lỗi implementation hoặc test trong suite này. Tuy nhiên, ba blocker còn mở: **hợp đồng RAM mỗi process không khớp công thức gate trung bình; CPU utilization/kiểm soát tải CPU cạnh tranh chưa được định nghĩa đủ; chưa có runner/analyzer v2 cùng receipts và checks bắt buộc theo chính prereg**. Không dùng test-suite PASS thay cho ba điều kiện này.

Audit thực hiện tái tính bằng code riêng trên frozen **validation** và dữ liệu toán học tổng hợp, không dùng kết quả tính tạm của lượt soạn trước. Đây là kiểm toán bằng phép tính độc lập, không phải peer review từ một người/agent thứ hai. **Không chạy ANN benchmark, profiler, G2 OFF, native ANN evaluator, không mở test v2 hoặc đọc query/GT/output theo panel v2; không tạo/đổi split, không retune beam.** Không sửa historical evidence, bốn tài liệu prereg, Google Sheets, source/ELF hoặc dependency manifests; không commit.

## 1. Hồ sơ được kiểm toán và evidence mới

Đọc lại [Research Philosophy](../../../RESEARCH_PHILOSOPHY.md), [Start Here](../../START_HERE.md), [resolution QUALITY_HOLD](AXD_G2_QUALITY_HOLD_RESOLUTION_DECISION.md), frozen G1 source/identity và Stage 5 validation bundle. V1 vẫn đóng tại QUALITY_HOLD; audit này không đổi Stage 5/6 hay bất kỳ kết luận performance nào.

| Tài liệu được audit, không sửa | SHA-256 trước = sau |
|---|---|
| [AXD_G2_PREREG_V2.md](AXD_G2_PREREG_V2.md) | `4c91adbcb16ebfbe97acd5dfda5f964bfe7a0a805edd6794d5b06254af811981` |
| [AXD_G2_V2_STATISTICAL_DESIGN.md](AXD_G2_V2_STATISTICAL_DESIGN.md) | `7213347035154a14121b67876745c65813fe01a7997fb7bcabd438388c0dac5b` |
| [AXD_G2_V2_QUERY_SPLIT_AUDIT.md](AXD_G2_V2_QUERY_SPLIT_AUDIT.md) | `7ca984331e17e7c5230b5c8b821ce473ee5fdcf66f386117dc10f4e0e57d5dbf` |
| [AXD_G2_V2_GO_NO_GO_CRITERIA.md](AXD_G2_V2_GO_NO_GO_CRITERIA.md) | `24175575aa3e37f83c13a050f7533182caf7fc7a9e426921ace97b3d240c901d` |

HEAD được audit: `f54b1bb653652dd13e760cc00c9fb46d0e643c1c`. Bốn prereg hiện untracked; SHA nội dung là identity có hiệu lực cho audit này, không giả định chúng đã nằm trong HEAD. Snapshot bảo vệ **100 file**: 95 tài liệu có sẵn, hai requirements, workflow CI, current evaluator source và guard source. Hậu kiểm không có thay đổi các file đó; tracked/staged diff giữ nguyên rỗng. Chỉ thêm báo cáo này và evidence audit mới trong `.local/` đã được Git ignore.

Evidence compact, không chứa query list/GT/ANN raw mới: [audit bundle](../../../.local/artifacts/axd-g2-v2-preapproval-audit-20261123-ge85t3xl/), [BUNDLE.sha256](../../../.local/artifacts/axd-g2-v2-preapproval-audit-20261123-ge85t3xl/BUNDLE.sha256) gồm 10 payload, manifest SHA **`9c3afe4170179c3716aa0c1601596081c03ef3d3b75a1d625876fb0d8ff81915`**. Bundle nằm ngoài Git tracking; muốn chia sẻ cho reviewer phải bàn giao bundle riêng. Venv/cache chỉ ở `/tmp`, không cần bảo quản như research artifact.

## 2. Resolve tám lỗi test-suite

### 2.1 Chẩn đoán và môi trường dự án khuyến nghị

[CI research workflow](../../../.github/workflows/research.yml) dùng Python **3.12**, cài [requirements-lite.txt](../../../requirements-lite.txt), rồi chạy `python -m unittest discover -s tests/research -v`. Manifest lite có đúng `numpy>=1.26,<3` và `jsonschema>=4.20,<5`. [requirements-research.txt](../../../requirements-research.txt) là tooling optional, có mlflow/jsonschema pin; không cần mlflow để chạy suite dataset-free. Không có dependency thiếu trong manifest lite đối với tám lỗi đang xét.

`.venv` hiện hữu dùng Python 3.12.3, không có numpy/jsonschema và còn không có pip. Python hệ thống không có ensurepip, nên tạo venv có bootstrap pip mặc định thất bại. **Không cài apt/sudo hoặc sửa Python hệ thống**. Dùng venv tạm do `venv` đã tạo phần isolation, rồi dùng standalone pip zipapp chính thức để cài wheels vào đúng venv đó. Pip có tài liệu cho cơ chế standalone này; zipapp được đánh dấu experimental, chỉ dùng để provisioning môi trường audit tạm, không trở thành dependency của evaluator. [pip installation documentation](https://pip.pypa.io/en/stable/installation/).

Venv tạm: `/tmp/axd-g2-v2-preapproval-20261123-ge85t3xl/venv`, `sys.prefix` ở đây, `sys.base_prefix=/usr`, không bật system-site-packages. Pip zipapp 26.3 tải từ PyPA; install dùng public PyPI, `--only-binary=:all:`, `--isolated`, theo requirements-lite. Lượt network trong sandbox thất bại, sau đó tải/cài qua các command escalation đã được chấp thuận; không có thay đổi môi trường hệ thống hoặc `.venv` cũ.

Exact packages: Python **3.12.3**, numpy **2.5.5**, jsonschema **4.26.0**, attrs **26.1.0**, jsonschema-specifications **2025.9.1**, referencing **0.37.0**, rpds-py **2026.9.1**, typing_extensions **4.16.0**. [Environment receipt](../../../.local/artifacts/axd-g2-v2-preapproval-audit-20261123-ge85t3xl/environment.json), [wheel URLs/digests và install report](../../../.local/artifacts/axd-g2-v2-preapproval-audit-20261123-ge85t3xl/pip_install_report.json). `pip check`: **No broken requirements found**. Ranges trong manifest chưa phải lockfile; receipt này pin exact environment đã PASS, không chứng nhận mọi phiên bản trong các ranges đều tương thích.

### 2.2 Phân loại đủ tám lỗi

Đã chạy lại baseline trên `.venv` cũ, thu đúng **342 tests, 8 errors, 14 skipped**; không chỉ dựa vào mô tả lượt trước.

| Lỗi baseline | Nguyên nhân trực tiếp | Phân loại sau clean rerun |
|---|---|---|
| `test_algorithm_studies` import | thiếu numpy | Dependency/environment; resolved |
| `test_issue29` import | thiếu numpy | Dependency/environment; resolved |
| `test_paper_native_v3` import | thiếu numpy | Dependency/environment; resolved |
| `test_causal_trace` import | thiếu jsonschema | Dependency/environment; resolved |
| `test_distributed_sampling` import | thiếu jsonschema | Dependency/environment; resolved |
| `test_package_manifest` import | thiếu jsonschema | Dependency/environment; resolved |
| `test_run_ann_experiment` import | thiếu jsonschema | Dependency/environment; resolved |
| `test_v1_v2_reader_compatibility` | import gián tiếp `test_causal_trace`, thiếu jsonschema | Dependency/environment; resolved |

Không sửa assertions, implementation, fixtures, discovery pattern hoặc thêm decorator skip. Native opt-in variables đã vắng từ đầu audit; cùng năm biến được unset rõ trong cả hai lượt để tuân thủ cấm native ANN execution:

```sh
env -u TASK_DA_SMOKE -u TASK_DA_P1_EVAL -u TASK_DA_P2_EVAL \
    -u TASK_DA_PHASE_EVAL -u TASK_DA_P2_TRACE_EVAL \
    /tmp/axd-g2-v2-preapproval-20261123-ge85t3xl/venv/bin/python \
    -m unittest discover -s tests/research -v
```

| Môi trường | Discovered | Executed PASS | Errors | Native skipped | Verdict |
|---|---:|---:|---:|---:|---|
| `.venv` cũ | 342 | 320 | 8 | 14 | FAIL_ENVIRONMENT |
| Venv tạm + requirements-lite | **521** | **507** | **0** | **14** | **DATASET_FREE_SUITE_PASS** |

Số discovered tăng vì các module trước đây không import được nay được discover đầy đủ. Cùng 14 native tests skipped ở hai lượt: 7 native smoke, 3 native P2, 1 native P1, 1 phase observer, 2 trace. Đây là opt-in có sẵn trong repository và ngoài scope task, **không phải bỏ test hỏng để đạt PASS**. Unit tests dùng fixtures/synthetic subprocess của chính tests; không bật binary ANN hoặc native integration. Không suy từ 507 checks này rằng frozen ELF hoặc v2 quality gate đã PASS.

[Baseline log](../../../.local/artifacts/axd-g2-v2-preapproval-audit-20261123-ge85t3xl/baseline_unittest.log), [clean log](../../../.local/artifacts/axd-g2-v2-preapproval-audit-20261123-ge85t3xl/clean_unittest.log), [diff lỗi/skips](../../../.local/artifacts/axd-g2-v2-preapproval-audit-20261123-ge85t3xl/suite_comparison.json). `scripts/check_research_docs.py` cũng PASS trên 11 active files mà script quản lý; các link báo cáo audit được kiểm riêng, không giả định script đó bao phủ bốn prereg v2.

## 3. Statistical validity: PASS và giới hạn

[Independent calculation source](../../../.local/artifacts/axd-g2-v2-preapproval-audit-20261123-ge85t3xl/independent_math_audit.py) và [results](../../../.local/artifacts/axd-g2-v2-preapproval-audit-20261123-ge85t3xl/independent_math_results.json) dùng NumPy cho replay/Monte Carlo và tự tính Student-t quantiles qua incomplete beta. Không cài thêm SciPy, không gọi evaluator, không dùng test outputs. Monte Carlo bên dưới chỉ là power dưới model giả định, không phải measured ANN gain.

| Hạng mục | Kết quả audit |
|---|---|
| Primary effect | `x_gb=log(B_gb/C_gb)`, mean đồng trọng số sáu graph trong block, rồi t-CI qua 12 block: đúng cho **mean log-ratio** dưới giả định block phù hợp |
| CI transform | Speedup `exp(x)`; reduction `1−exp(−x)`; so lower x với `−log(.97)=0.0304592075`: đúng, không nhầm speedup 1.03 với reduction 3% |
| Student-t | t(.975,11)=**2.2009851601**, t(.975,5)=**2.5705818356**: khớp prereg |
| Query uncertainty | Recall theo query, giữ pairing/covariance giữa graph; không dùng N×10 hits hoặc N×repeats như quan sát độc lập: PASS design |
| Process uncertainty | Block aggregation tránh xem 72 graph-pairs là 72 outer repeats; 6 adjacent-block pairs là sensitivity: PASS cấu trúc, assumptions chưa kiểm chứng |
| Graph uncertainty | Fixed six; independent-root population CI NOT_ESTIMABLE: đúng. Process/query repeats không tăng số root |
| Floor multiplicity | Bonferroni one-sided sáu graph, z=**2.3939797998**: đúng về multiplicity, coverage vẫn nominal do CLT theo query |
| Assurance rule | z-floor + z(1−.20/6)=**4.2278944356**: đúng đại số; là plug-in calibration proxy, không phải power guarantee sau selection |
| Equivalence B | CI95 chứa trọn trong ±0.0005 tương ứng TOST mỗi phía α=.025, chặt hơn TOST α=.05/CI90: đúng; “p>0.05” không được thay thế |
| Tail/RAM multiplicity | One-sided upper t(1−.05/18,11)=**3.4368413385** cho 18 graph×endpoint tại p2: đúng về Bonferroni nếu marginal intervals hợp lệ |
| Không optional stopping | Đủ repeats hoặc HOLD incomplete; không drop slow run, không thêm m/query để cứu CI: PASS design |

Cách paired t dựa trên SD của paired effects, không SD độc lập hai policy, phù hợp [NIST paired observations](https://www.itl.nist.gov/div898/handbook/prc/section3/prc311.htm). Quy tắc CI90/TOST được đối chiếu với [tài liệu phương pháp của Lakens](https://github.com/Lakens/statistical_inferences/blob/master/09-equivalencetest.qmd).

### 3.1 Minimum improvement 3%: hợp lệ như lựa chọn kỹ thuật, chưa có bằng chứng kinh tế

**Không tìm thấy cơ sở empirical/SLA/maintenance-cost chứng minh 3% là mức tối ưu.** Prereg đã ghi đúng đây là đề xuất cần owner duyệt; không dùng kết quả OFF R90 để chọn nó. Mức này không tự sai vì chưa có SLA, nhưng owner cần ký rõ ý nghĩa và chấp nhận rủi ro underpower. Không đề xuất thay 3% trong audit này.

Điểm cần làm rõ khi ký: 3% hiện áp dụng cho **geometric aggregate của các tỷ số mean latency từng graph/process**. Nó không bảo đảm arithmetic mean latency của một workload trộn graph giảm 3%. Phản ví dụ tổng hợp: base `[1,1,1,1,1,100]` ms, opt `[0.9,0.9,0.9,0.9,0.9,99.9]` ms. Geometric reduction=**8,4209%**, Fast subgroup=6,8141%, mọi leave-one-out≥8,1018%, nhưng ratio-of-arithmetic-means chỉ giảm **0,5714%**. Không phải số R90; ví dụ chỉ chứng minh hai estimand khác nhau dù stability point screens đạt.

Công thức hiện tại **hợp lệ cho estimand geometric đã công bố**; không gọi đây là lỗi đại số. Cần ghi cùng tên estimand trong ledger/approval, và mọi phép `T(Q)` vẫn dùng arithmetic means. Nếu owner muốn primary là savings của một mixture workload, phải sửa estimand/CI trước dữ liệu mới; không đổi sau test và không chọn estimator thuận lợi hơn.

### 3.2 Sample size/power và giả định chưa có bằng chứng

Các bảng floor N và equivalence power trong prereg được tái tính khớp. Với SD Recall giả định 0.036, true floor margin .001/.0013/.0015: N cho all-six power≥80% conservative lần lượt **23.167 / 13.708 / 10.297**. N=10k không tự đủ. Ở B, SD arm-difference giả định .010, N=10k: equivalence power khoảng **99,76% / 85,08% / 51,60%** khi true absolute gap 0/.0002/.0003. Các con số là normal planning, không power đã được đo trên panel v2.

Đã thêm kiểm power tổng hợp có Student-t và điều kiện CI6 thực sự được dùng trong GO: 200.000 simulations/kịch bản, seed 20261123, 12 independent normal block log-effects, SD=.03. MC standard error tối đa khoảng 0,12 percentage point. Kết quả chưa gồm bootstrap, heterogeneity, tail/RAM hoặc quality gate:

| True reduction giả định | P(CI12 lower>3%) | P(CI6 lower>3%) | P(cả hai đạt) |
|---:|---:|---:|---:|
| 3% đúng boundary | 2,47% | 2,50% | 1,46% |
| 5% | 59,18% | 49,36% | **45,39%** |
| 6% | 90,83% | 82,22% | **80,87%** |
| 8% | 99,98% | 99,72% | 99,72% |

Vì GO yêu cầu thêm bootstrap và các safety/stability gates, all-gates power không thể lớn hơn xác suất cả hai CI trong bảng, dưới model này. **Không có bảo đảm 80% power cho 5% gain ở m=12/SD3%.** Đây không phải lý do retune m trong audit; owner có thể chấp nhận fixed-budget exploratory pilot với khả năng HOLD cao. Nếu yêu cầu power cam kết thì phải redesign trước test, không thêm repeat hậu kiểm.

Assumptions chưa được xác minh trên R90 v2 OFF: SD process log-effect 1/3/5%; block independence/stationarity và log-effect gần normal; sensitivity ghép hai block đủ bao drift; exchangeability query từ pool lịch sử; block length 100 đủ giữ temporal dependence; coverage percentile bootstrap cho nonlinear mean ratios/p99 với chỉ 12 process blocks; power cho tail/RAM family18; warmup100 đạt trạng thái mong muốn; precision/budget hậu kỳ. Không có phép đọc frozen validation nào xác nhận được các assumption timing này.

Joint query×process resampling có cấu trúc crossed bootstrap hợp lý như sensitivity, nhưng không tự bảo đảm exact coverage. [Owen, The pigeonhole bootstrap](https://arxiv.org/abs/0712.1111) cũng phân biệt consistency dưới model với một bootstrap exact cho mọi cấu trúc crossed data. Tài liệu đó không chứng minh trực tiếp coverage cho p99/ratio/host drift trong v2. Analyzer phải kiểm trên fixtures biết đáp án và ghi phạm vi assumptions; không được diễn giải các CI là distribution-free.

### 3.3 Multiple comparisons và post-selection

Primary có một effect; ba điều kiện CI12/CI6/joint đều bắt buộc nên không phải chọn interval thuận lợi trong ba cái. Chúng có thể tăng false HOLD; không được coi ba CI là đồng thời coverage95 chỉ vì từng cái nominal95. Heterogeneity/leave-one-out là point screens, không phải population tests. Floor6 và safety18 có Bonferroni riêng. Các CI secondary Stock/Fast, ba Q và p1/p4 không có family-wide discovery guarantee chung; phải tiếp tục ghi exploratory, không chọn contrast/p tốt rồi quảng bá như confirmatory GO.

Rule chọn beam xem 54 validation cells; hệ số assurance không phải Bonferroni cho cả 54 cell và không cần được quảng bá như thế. Selected-beam validation CI/power proxy chịu post-selection optimism; đánh giá test cấu hình khóa mới là kiểm tiếp theo. Thiết kế v2 được lập sau v1 và toàn public pool đã bị Task A/R86/P1 quan sát: **không còn fresh-independent inference**, dù split rời và không trực tiếp retune test trong v2. Disclosure hiện tại đúng và cần giữ nguyên.

## 4. Common beam, schedule và quality matching

### 4.1 Validation-only replay của common beam 432: PASS số học

Đã đọc đúng **54 baseline validation hit vectors**, kiểm từng SHA với Stage 5 BUNDLE và length=10k, hit∈[0,10]. Không đọc test panel/GT. SHA manifest Stage 5 khớp `82e740bcd6224bd28dfa2dcdbedba4902515b0fc578ed923250ef5d568337e15`.

| Common beam | Min assurance score độc lập | Qua rule ≥0.990? |
|---:|---:|---|
| 420 | 0.9897348523 | Không |
| 424 | 0.9898820172 | Không |
| **432** | **0.9901362004** | **Có** |

Cả chín beam trong grid được xét; **432 là ứng viên duy nhất đạt**, không chỉ là beam tốt nhất trong ba dòng minh họa. Ở 432, min validation Recall=.991590, max query SD=.03438590; arm difference Fast−Stock=.00008333, SD(d_q)=.00863459. Đây là replay frozen validation, **không phải test PASS, không phải retune, không cập nhật beam manifest/config**. B1+A1 validation parity tại 432 còn chưa có receipt mới; không dùng parity ở 420/416/412 để chứng nhận nó.

### 4.2 Execution order: PASS cấu trúc, chưa chạy

Enum lại công thức schedule: mỗi graph có 6 AB/6 BA, xuất hiện đúng một AB và một BA ở mỗi vị trí trong sáu vị trí. **12×6×2=144 OFF processes dự kiến**, 1.440.000 scored query executions, 14.400 warmup executions, 10.000 unique query IDs theo split đã công bố. Tất cả là số kế hoạch; **OFF executions thực tế trong audit=0**.

P2 mới: 6 opt validation +12 test ON +144 OFF=162 process dự kiến. Scaling thêm 84 base validation +12 opt validation +24 test ON +288 OFF=408; tổng tối đa=570, arithmetic khớp. Không có khả năng dừng sớm để GO hoặc giảm repeat vì quota thiếu.

### 4.3 Quality matching: PASS hợp đồng, runtime chưa thể xác minh

| Nội dung | Design audit | Chưa được phép/không thể xác minh tại đây |
|---|---|---|
| A cùng graph | Mỗi base/opt pair cùng graph SHA, entry/metric/K/p/S/beam | Receipt v2 actual argv/load/output chưa có |
| A cùng query | Cùng panel SHA/order, 100 validation warmup; toàn 10k timing | Không mở hoặc tái tạo panel trong audit này |
| A cùng quality | Exact ordered Top10/L2², counters, floor/LCB bắt buộc | Chưa có exact parity và quality v2 tại b432 |
| Không đổi Recall lấy latency | A exact parity, B common beam+equivalence; test fail giữ HOLD | Common beam tự nó không chứng minh Recall equivalent |
| Stock/Fast | Arm-level paired Recall CI95 trong ±.0005 trước cross-arm claim; nếu B HOLD chỉ A-only | Không chứng minh equivalence mọi graph pair hoặc population roots |
| Không dùng test để tune | Split/salt/rule/threshold/repeats khóa trước test; không grid expansion hoặc rescue panel | Lịch sử public-pool exposure vẫn tồn tại |

Panel/hash đã công bố là `457abdc13abc95d8d0f48ff32919a6013f5ed4bca469f9075312ae80dfe44b0d`. Audit hiện tại chỉ kiểm tính nhất quán của **spec và SHA được ghi trong tài liệu**; theo hard restriction, không đọc lại ID test/GT hoặc materialize panel để kiểm membership. Audit split trước là evidence được dẫn, không được trình bày như một lần mở test độc lập ở đây.

Gate B cho phép quality sai khác trong margin đã duyệt, không quality exact. Vì quan hệ Recall→latency chưa được ước lượng, vẫn có thể có advantage nhỏ bên trong margin; phải ghi tolerance cạnh cross-arm result, không tuyên bố zero quality confounding. Không yêu cầu thêm sweeps để ước lượng nó trong task này.

## 5. Resource và performance gates

Đã kiểm frozen evaluator source tại commit `f2cd634b837a70735c3e31e5956f0524bfc26675`, không coi current HEAD observer source là source của ELF frozen. Frozen `p2_eval.cpp` SHA **`b356ba8df3170a7ddd7d3cd4a63ab6d30361f806cb408dd4e5ad1ca4a59d9f85`**, frozen engine `c4b1bdc2…`, loader `2ca38624…`; ELF trên đĩa vẫn **`7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1`**. Current `p2_eval.cpp` SHA khác (`10bb2857…`) do observer ở HEAD; không rebuild hoặc thay subject. [Identity receipt](../../../.local/artifacts/axd-g2-v2-preapproval-audit-20261123-ge85t3xl/verification_identity.json).

| Endpoint/guard | Đã đầy đủ về thiết kế/static source? | Kết luận |
|---|---|---|
| Recall@10/LCB95 | Có query estimator/floor/multiplicity và parity | PASS_SPEC; runtime NOT_VERIFIED |
| Mean/p50/p95/p99 latency | Frozen source đo quanh `session.search` và result assignment; percentile linear q(N−1), per-process | PASS_SPEC; tail coverage/precision chưa xác nhận |
| QPS | N/batch_wall, vòng query sau warmup, trước serialize; không đồng nhất nghịch đảo mean | PASS_SPEC; jobs1 không là multi-query serving throughput |
| Distance/duplicate L2 | ON diagnostic riêng, OFF không dùng ON timing | PASS_SPEC; không suy causality hay gain từ counters |
| Peak RSS/RAM | Có ELF VmHWM và wrapper sampled high-water, nhưng source/window chưa chọn duy nhất; budget/gate mâu thuẫn | **FAIL_READINESS F1** |
| CPU utilization | Có raw task stat/schedstat và cpufreq, chưa có endpoint/đơn vị/normalization/window đã khóa | **FAIL_COMPLETENESS F2** |
| Foreign CPU load | Guard kiểm narrow ANN identities, không mọi heavy CPU job; loadavg log không chứng minh exclusivity | **FAIL_OPERATIONAL_CONTRACT F2** |
| Thermal/AC/watchdog | Frozen base guard+Ryzen adapter có fail-closed checks; start<85°C, abort≥95°C; watchdog độc lập | PASS_STATIC; actual host preflight còn NOT_VERIFIED |
| Disk/RAM/swap safety | Source có numeric limits mạnh hơn raw reserve được liệt kê ngắn trong prereg | Cần ghi đủ trong receipt/budget, F2 |
| Speedup/efficiency p1/2/4 | Có L1/Lp, QPSp/QPS1 và chia p, quality CI riêng | PASS_FORMULA; scaling module HOLD về execution/session control |

### F1 · BLOCKER: RAM mỗi process khác RAM mean gate

Ledger criteria §1 nói budget `max(64 MiB,10% baseline peak RSS)` **mỗi paired process**. Statistical design §7 lại lấy mean `v_gb` qua 12 block và upper t-bound trên **mean**. Hai hợp đồng không tương đương.

Phản ví dụ toán học: `v=[2,0,0,0,0,0,0,0,0,0,0,0]`. Một cặp vượt gấp đôi budget; mean=1/6, SE=1/6. Upper simultaneous bound là `1/6 + 3.4368413385/6 = 0.73947356 <1`, nên mean gate vẫn PASS. Safety MemAvailable guard không thay cho relative RAM regression gate.

**Sửa cần thiết trước ký:** thống nhất rõ budget theo từng cặp hay expected/typical process. Khuyến nghị giữ hợp đồng “mỗi process”: thêm `max_b v_gb≤1` cho GO, vẫn giữ CI mean; bất kỳ excursion được lưu và HOLD_RAM, không drop. Nếu owner chọn chỉ giới hạn mean thì phải sửa wording và chấp nhận giới hạn đó một cách tường minh, không gọi là per-process guarantee.

Đồng thời khóa primary RAM field/window: ví dụ `p2_eval_summary.vm_hwm_kib>0` đến thời điểm capture gần cuối process, wrapper RSS là audit phụ. Frozen ELF capture HWM sau search/output serialization nhưng trước final summary/exit; wrapper polling 1s có cửa sổ khác. Không trộn field hoặc tự chọn nguồn cho kết quả thuận lợi. Thiếu/âm/nonfinite metric phải HOLD, không coi là zero overhead. Thêm fixture data-free cho phản ví dụ trên vào analyzer tương lai.

### F2 · BLOCKER: CPU telemetry và exclusivity chưa thành hợp đồng có thể kiểm

`paper_portable_v2.host_snapshot` lưu raw task `/proc/.../stat`, `schedstat`, cpufreq, loadavg; `observer_cpu_s` là CPU của **monitor**, không phải CPU utilization của ANN process. Không có derived CPU utilization v2 hoặc quy tắc cadence/window/đủ mẫu trong prereg. Base guard+adapter chỉ nhận diện các tên ANN được liệt kê và một script pilot; một heavy CPU workload tên khác có thể không bị chặn. Không khẳng định đã có competitor thực tế trong audit; đây là lỗ hổng enforcement của điều kiện “không chạy đồng thời CPU nặng”.

**Sửa cần thiết:** freeze telemetry schema từ wrapper, không thêm profiler/hot-path instrumentation: CPU user+system time của owned process, wall window tương ứng, CLK_TCK nếu lấy tick, process utilization có thể >100%, normalized theo p khi cần; ghi rõ full-invocation hay search-window. Không cộng process aggregate với các thread times lần nữa. Khóa sampling/missing-data policy và thủ tục quiet-host/foreign-load preflight có thể kiểm trước/during run; threshold/cách xử lý phải được duyệt trước test. Khi vi phạm, dừng/HOLD và giữ raw, không kill process không thuộc campaign hoặc xóa slow run. Utilization là diagnostic, không thay latency/QPS.

Static source numeric limits phải được đưa vào runner receipt: **MemAvailable>1 GiB, disk free>20 GiB**, swap growth>64 MiB kéo dài≥10s thì stop; AC phải available/unchanged; Tctl missing/invalid fail-closed; critical trip stop; start<85°C/abort≥95°C, cooldown180s/timeout180s. Raw reserve≥5 GiB p2 hoặc 10 GiB full không thay disk floor20 GiB: initial disk budget phải tính **floor20 GiB cộng output dự trù/headroom**, tránh campaign tự hết disk quota giữa lượt. Không sửa guard để nới giới hạn.

### F3 · BLOCKER: chưa có package v2 thực thi/analysis được khóa

Chính prereg §9 và criteria §5 đòi runner/analyzer/schedule cùng SHA và data-free checks trước quality execution. Repository inventory và hồ sơ hiện tại chưa cung cấp v2 runner/analyzer receipts đó. Stage 5/6 scripts là protocol cũ, không tự trở thành runner 12-block/assurance/CI/joint-bootstrap v2. 521 unit tests kiểm code hiện hữu, không kiểm một analyzer v2 chưa có.

**Sửa cần thiết:** chuẩn bị wrapper/analyzer nhỏ theo protocol, schedule manifest và receipt schema; data-free fixtures cho pairing/log signs, CI transforms, mean vs geometric distinction, equivalence boundaries, 18-endpoint multiplicity, weighted percentile bootstrap khớp explicit resampling, missing pairs, missing RSS/CPU samples, timeouts/guard stops và không overwrite. Khóa exact dependency versions/SHA và kiểm feasible memory/algorithmic work trước test; không cần ANN benchmark hoặc mở panel để làm việc này. Không yêu cầu generic framework hoặc sửa frozen search engine.

### Các điểm bổ sung trước owner sign-off

- **C1 — Estimand label:** ghi rõ 3% là geometric aggregate trong ledger/approval; không quảng bá như arithmetic mixture saving. Không đổi numerical threshold hoặc estimator trong audit này.
- **C2 — Scaling:** thứ tự strata p2→p1→p4 confound worker count với thời gian/host state; pairing cùng block ordinal không tạo contemporaneous control. Giữ scaling `NOT_RUN/HOLD` nếu không chọn; nếu muốn approval scaling inferential, cần lịch cân bằng worker strata trước test và analysis cho session effect, hoặc owner giới hạn rõ kết luận descriptive. Không dùng scaling để cứu primary p2.
- **C3 — Rendering:** statistical design §4.1 dùng header `| True |δ| giả định |...`, dấu pipe chưa escape làm lệch số cột Markdown. Sửa thành `| True absolute gap |...` hoặc escape pipes, không đổi dữ liệu/power.
- **C4 — Nguồn power/cost:** nhận 12-block budget là screening budget; planning thu thập p2 2,5–3,5h và bootstrap0,5–2h chưa được đo; hard caps4h+3h phân tích không bảo đảm hoàn thành. Chưa có runtime/p99/RAM power hoặc expected gain R90 OFF.

## 6. Tổng hợp PASS / FAIL / NOT_VERIFIED

| Nhóm | PASS | FAIL / cần sửa | Chưa thể xác minh hoặc giới hạn được chấp nhận |
|---|---|---|---|
| Dependency/tests | Tám lỗi phân loại đủ; clean521/0errors; không patch test | Không còn dependency blocker cho audit environment | `.venv` cũ vẫn thiếu packages; CI ranges không phải universal compatibility proof |
| Statistics | Paired formulas, CI transforms, N/power arithmetic, multiplicity cơ bản | F1 RAM contract; C1 cần wording/sign-off; C3 rendering | Normality/independence/coverage/all-gates power/3% business value |
| Quality | Cùng graph/query/target; exact A; separate B equivalence; no test tuning | Không thấy bypass quality trong spec | Actual v2 quality/parity tại432 chưa chạy; panel không mở lại; root population CI unavailable |
| Runtime/resources | Frozen ELF/guard hashes; endpoints static; thermal fail-closed | F2 CPU/load/disk operational contract; F3 runner/analyzer freeze | Actual Ryzen sensor/AC/affinity/readiness, timings/tails/RSS/cooldown |
| Scaling | Formulas và quality requirements | C2 nếu muốn inferential scaling approval | Cross-L3 effect, host drift, beam/quality p1/p4 chưa measured |
| Preservation | Bốn prereg/95 existing docs và protected files giữ nguyên | Không có historical edit/source/ELF/split/Sheet/commit | Không tuyên bố rehash toàn bộ inputs/graphs GB trong task này |

Việc quality v2 hoặc actual host preflight chưa chạy **không tự nó là lỗi thiết kế**: chúng đúng là bước sau một quality-only authorization. Kết luận NOT_READY ở đây dựa vào F1–F3 còn mở ngay ở hồ sơ trước authorization, không yêu cầu chạy test trái hard restrictions để “hoàn tất audit”.

## 7. Bảng GO / HOLD / PIVOT

| Quyết định | Điều kiện | Trạng thái hiện tại |
|---|---|---|
| **GO_DESIGN / READY_FOR_OWNER_APPROVAL** | F1–F3 đóng bằng revision/receipts cụ thể; C1–C4 được xử lý hoặc owner chấp nhận scope; test bundle PASS; hashes khóa | **Chưa đạt** |
| GO_QUALITY_ONLY | Owner ký đúng revision/package, host/budget/scope; không bao gồm OFF | Chưa được cấp trong task này |
| GO_OFF_A | Actual A quality PASS, parity/provenance/guard đầy đủ, owner cấp quyền performance riêng | NOT_OPEN; chưa chạy quality v2 |
| GO_OFF_A+B | Thêm B equivalence PASS; mọi cross-arm interpretation giữ đúng margin/fixed-cohort scope | NOT_OPEN |
| GO_RESEARCH sau OFF | Quality và đủ m; CI/heterogeneity/tail/RAM đạt tiêu chí đã khóa và sửa hợp đồng F1 | Không đánh giá: không có số liệu OFF v2 |
| **HOLD_PRE_APPROVAL** | Hợp đồng hoặc execution/analysis package còn blocker | **Quyết định audit hiện tại** |
| HOLD_QUALITY / HOLD_UNCERTAINTY | Sau authorization, gate trượt hoặc CI/incomplete chưa đủ | Quy tắc tương lai; không gán fail cho panel chưa chạy |
| PIVOT_TO_TASK_A | Campaign hợp lệ loại lợi ích latency thực dụng hoặc chứng minh chi phí vượt budget theo tiêu chí khóa | **Chưa có cơ sở**; không dùng lỗi môi trường hay thiếu runner để kết luận B1+A1 vô ích |

## 8. Checklist owner ký duyệt

Không ký dòng approval execution khi F1–F3 còn mở. Có thể ký xác nhận đã nhận audit; điều đó không phải quyền chạy benchmark.

- [ ] **F1 closed:** RAM per-process/mean scope thống nhất, source RSS/window/missing-data policy khóa, phản ví dụ vượt budget được xử lý đúng trong fixture.
- [ ] **F2 closed:** CPU utilization schema/window/normalization và quiet-host/load procedure khóa; receipt ghi đúng disk>20GiB, RAM/swap/AC/thermal/watchdog limits và đủ output headroom; không nới frozen guard.
- [ ] **F3 closed:** runner/analyzer/schedule v2 có SHA, exact packages và dataset-free fixture results; không đổi frozen ELF/source/graph/split.
- [ ] **C1 accepted:** 3% áp đúng geometric paired estimator; arithmetic savings/T(Q) báo riêng; floor.990, equivalence±.0005, p95+5%, p99+10%, RAM budget được duyệt vì lý do kỹ thuật trước test.
- [ ] **C2 chosen:** p2-only, hoặc scaling scope/order/CI/session assumptions được giải quyết trước test đầu; p1/p4 không mở theo kết quả p2.
- [ ] **C3/C4 addressed:** bảng Markdown sửa; nhận giới hạn power/cost, fixed m=12 không tăng để cứu CI; quality fail/slow/error/partial luôn giữ raw và HOLD.
- [ ] Nhận `EXPLORATORY_HOST_SPECIFIC`, public100K/Task A và test90k/R86/P1 reuse; sáu graph roots chưa độc lập; không claim fresh independent holdout hoặc population graph gain.
- [ ] Revision được duyệt: `________`; SHA bốn prereg mới: `________`; runner/analyzer/schedule SHA: `________`; evidence bundle: `________`.
- [ ] Owner: `________`; ngày/giờ: `________`; phạm vi quyền đầu tiên: **QUALITY_ONLY**; host **Ryzen 4650U**, quota `________`, raw destination `________`; không i5-14600KF/Sheets write/commit.
- [ ] Sau quality-only, owner review report thực tế và ký **approval OFF riêng**: A-only nếu A PASS/B HOLD, hoặc A+B nếu cả hai PASS; không suy quyền OFF từ chữ ký quality-only.

Bốn prereg `design-1` được cố ý giữ nguyên trong task này để audit có đối tượng SHA rõ ràng. F1/F2/C1/C3 là phát hiện cụ thể có thể làm cơ sở sửa revision tiếp theo; không có sửa threshold/beam/split nào được thực hiện ngầm. Đóng F1–F3 cần công việc chuẩn bị có thể kiểm bằng synthetic fixtures và tài liệu, không cần ANN execution.

**Kết luận cuối cùng: `NOT_READY_FOR_APPROVAL`.**
