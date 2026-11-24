# A×D G2 v2 · Query split và reuse audit

**EXPLORATORY_HOST_SPECIFIC · ID_ONLY_AUDIT · TEST_NOT_OPEN**  
Protocol `AXD-G2-V2-3A-20261123`, revision `design-2`, 23/11/2026. [Prereg](AXD_G2_PREREG_V2.md) · [Statistical design](AXD_G2_V2_STATISTICAL_DESIGN.md).

Kết quả: pool nhánh 3a có đúng **81.000 ID**, panel v2 xác định có **10.000 ID duy nhất**, overlap bằng 0 với validation và cả ba panel test nhỏ cũ. Đã tính SHA dự kiến trong bộ nhớ, **chưa ghi file ID mới, chưa truyền panel vào evaluator, chưa mở GT/output Recall theo panel mới**. Chỉ đọc ID lists, metadata và evidence đã có. Không tính một kết quả test v2 nào trong audit này.

**Design-2 note:** các count/SHA/membership dưới đây là ID-only audit đã có từ design-1, giữ nguyên. Remediation chỉ cập nhật protocol revision và scope p2-only; không đọc lại test IDs/GT/output, không materialize hoặc thay split. Beam432/hash panel không đổi; runner chỉ xác minh file sau authorization riêng.

## 1. Ý nghĩa chính xác của “chưa sử dụng”

81k là `test_90k \ (pilot3k ∪ disjoint3k ∪ narrow3k)`. Nó chưa thuộc các panel nhỏ đã dùng tại D cho P2/B1+A1; G1 và Stage 5 R90 tại D dùng validation, Stage 6 dùng narrow3k. **Không được hiểu là 81k chưa từng được bất kỳ nhóm nào search trên R90 hoặc graph khác.** Public 100K đã được Task A đánh giá; test_90k đã dùng ở R86/P1. Tách panel hiện tại chỉ tránh lặp lại các quan sát nhỏ dùng trực tiếp cho quyết định D/v1, không xóa lịch sử Task A/P1.

Vì vậy, cách ghi hợp lệ là: **“panel rời 10k, held out khỏi calibration v2 và các panel nhỏ D đã kiểm kê, từ public query pool lịch sử; EXPLORATORY_HOST_SPECIFIC.”** Không dùng “fresh independent holdout”, “untouched public queries”, “unseen confirmatory” hoặc “R90 chưa từng thấy các ID này” trên phạm vi toàn Task A×D.

Evidence lịch sử: [Resolution](AXD_G2_QUALITY_HOLD_RESOLUTION_DECISION.md), [Stage 5 reuse audit](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/split_and_reuse_audit.json), [Stage 6 report](AXD_G2_TEST_QUALITY_REPORT.md), [P1 validation](P1_FULL_VALIDATION_REPORT.md). Các nhãn v1 vẫn giữ nguyên, không chỉnh report cũ để diễn giải lại split.

## 2. Input identity

Các đường dẫn raw trong tài liệu này là tương đối từ file hiện tại; không chép private query vectors, GT hoặc ID list vào Git.

| Input | Shape / mapping | SHA-256 |
|---|---|---|
| `base.1M.fbin` | 1.000.000×100 FP32; row index=graph vertex ID | `44e83e1dd4c65999b75873101adc5ac06ca900d259a2befd05c2c3aa28ff4042` |
| `query.public.100K.fbin` | 100.000×100 FP32; query ID là row 0-based [0,99999] | `48d087a17bec15a5ec9ea526fe9bd14ac31bbbb5cd200817b341adbb77695644` |
| `groundtruth.public.100K.ibin` | 100.000×100, toàn ID block rồi auxiliary distance block | `fa5acf5ab262b42355296e99f920e6aa863f48820ca6f70fa37ca7966634c344` |

Ba identity lấy từ [G1 graph/input manifest](AXD_G1_GRAPH_ARTIFACT_MANIFEST.md); task này không rehash hàng GB vector/graph hay tính lại exact GT. Trước quality execution phải reverify full input/graph/ELF pins theo prereg. Recall dùng top-10 GT **IDs** đúng hàng query, không dùng auxiliary distance để chọn query hay làm quality gate. Không đổi metric/index mapping.

## 3. Audit trực tiếp các ID list bất biến

Các SHA sau được tính lại từ bytes file ID trong task tài liệu này; mọi file có count=unique count và mọi ID nằm trong [0,99999].

| Panel và vị trí evidence | N | SHA-256 |
|---|---:|---|
| [val_10k](../../../../artifact-evidence/p1-full-validation-20261117T225717+0700/split/val_10k.ids) | 10.000 | `a3c948e9aac4f40c1fb818a6f784c4fbb56473a0769affe3344493ed4eb87f57` |
| [test_90k](../../../../artifact-evidence/p1-full-validation-20261117T225717+0700/split/test_90k.ids) | 90.000 | `af871517d88aaad90549ba2fde0d4ed745f59400037a757f17bc93fa479bbfa3` |
| [pilot_test_3000](../../../../artifact-evidence/p2-exploratory-0990-20261118/pilot_r1/pilot_test_3000.ids) | 3.000 | `18d8b901e925d71c0ddb2d043bf2cba12edab4061859da833bd1ccc37790c1b0` |
| [disjoint_test_3000](../../../../artifact-evidence/p2-pivot-b1-a1-20261119/disjoint_test_3000.ids) | 3.000 | `c91dcae377afc8161856377842930c691b2ea19e337d1361576538b5ab39abfc` |
| [narrow_test_3000](../../../../artifact-evidence/p2-b1-a1-narrow-20261119/narrow_test_3000.ids) | 3.000 | `77fda0316a8bb559c75e113ec3d750de0cf93403a11be474fc375c94c927c90b` |
| [warmup_val_100](../../../../artifact-evidence/p2-exploratory-0990-20261118/pilot_r1/warmup_val_100.ids) | 100 | `199ca6066269641347280d6ef4eaab39efee3397b87c23cd74d38ee85bcd4783` |
| [P1 dry_500](../../../../artifact-evidence/p1-full-validation-20261117T225717+0700/dry_run/dry_500.ids) | 500 | `253a1266f8b23fadc9906138e1e14e1ae5033537a18b5b8b3d327b1c6bf5e063` |
| [H3 panel_64](../../../../artifact-evidence/h3-overlap-screening-20261120/panel_64.ids) | 64 | `a19636b81c0b1197184cf1395f1decd50bd800993435d5e272c9805e5cb93545` |
| [Validity panel_64](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/panel_64.ids) | 64 | `a19636b81c0b1197184cf1395f1decd50bd800993435d5e272c9805e5cb93545` |

G1 smoke `smoke_val_500.ids` có SHA `54f9eae4c2039f613fe63e2a27a40fadd7b498ab31f195f54fe7340d845ae9a6`, là 500 ID đầu của val theo receipt G1. ASAN 100 bằng warmup; các tên alias không tạo query mới.

| Kiểm tra tập hợp | Kết quả |
|---|---:|
| val ∩ test90 | 0 |
| val ∪ test90 | Đúng toàn bộ {0,…,99999} |
| pilot ∩ disjoint; pilot ∩ narrow; disjoint ∩ narrow | 0; 0; 0 |
| Ba panel 3k đều là subset của test90 | PASS |
| Union ba panel 3k | 9.000 |
| Pool test90 trừ union | **81.000** |
| Warmup100/dry500/H3-64/validity64 là subset của val | PASS cả bốn |
| Pool ∩ các panel validation trên | 0 |

Kiểm kê bằng `rg --files ../artifact-evidence -g '*.ids'` tìm thấy các panel kể trên và aliases smoke/ASAN; không tìm thấy panel đã chạy R4/R5 mới trong durable root này. [R4/R5 prereg](B1_A1_R4_R5_CONFIRMATION_PREREG_20261119.md) là kế hoạch có điều kiện, không phải receipt thực thi. Kết quả inventory chỉ bao phủ durable root cục bộ và hồ sơ đã đọc; không chứng minh không có artifact chưa bàn giao ở máy khác. Nếu phát hiện thêm D/R90 exposure trước freeze, dừng audit và giải trình trước test; không âm thầm đổi seed/pool.

## 4. Quy tắc xác định panel v2, khóa trước test

Không stratify theo độ khó, GT hits, latency, beam response hoặc kết quả Task A. Không thử nhiều salt để chọn panel có Recall dễ đạt. Prefix được ghi đúng một lần trong thiết kế này:

`axd-g2-v2-3a-test10k-20261123/`

Với mỗi ID trong pool, key là `(SHA256(prefix + decimal_ID).digest(), ID)`. Lấy 10.000 key nhỏ nhất theo thứ tự bytes unsigned của digest, giữ nguyên thứ tự rank làm execution order. ID thập phân ASCII, không dấu cộng, không padding, không newline trong hash input. Serialization file mới là một ID thập phân/dòng, LF `\n`, có LF cuối file, không BOM/header/comment.

Pseudocode tái lập, chỉ thao tác ID:

```python
pool = set(test90) - (set(pilot3k) | set(disjoint3k) | set(narrow3k))
assert len(pool) == 81_000
prefix = "axd-g2-v2-3a-test10k-20261123/"
ordered = sorted(pool, key=lambda q: (sha256((prefix + str(q)).encode("ascii")).digest(), q))
panel = ordered[:10_000]
serialized = "".join(f"{q}\n" for q in panel).encode("ascii")
# Chỉ write serialized vào external campaign directory sau authorization.
```

| Identity tính trong bộ nhớ | Giá trị |
|---|---|
| SHA pool, serialize **ID tăng dần**, 81k dòng | `ab1de8ef151cc0fffce9b859d3f6f674bdf81581afe592a633aa605e3f4acef1` |
| Proposed filename | `v2_test_10000.ids` |
| SHA panel, serialize **hash-rank order**, 10k dòng | **`457abdc13abc95d8d0f48ff32919a6013f5ed4bca469f9075312ae80dfe44b0d`** |
| 10 ID đầu để kiểm order | `32792,20400,17878,72872,61505,35404,40783,34564,23435,79120` |
| Số ID còn trong pool sau chọn | 71.000; không được mở thêm để cứu test v2 |

Hash pool và panel có hai canonical orders khác nhau được nêu rõ; không so nhầm hai SHA. SHA panel khóa cả membership và thứ tự, không chỉ set. Sau owner approval tạo file một lần ở campaign directory mới, kiểm count/unique/bounds/SHA/overlap trước evaluator. Không dùng file test cũ làm đường dẫn alias hoặc ghi đè nó.

## 5. Ma trận overlap của panel v2

| Tập so với panel v2 10k | Số ID trùng |
|---|---:|
| val_10k | 0 |
| warmup_val_100, dry_500, H3/validity64 | 0 từng tập |
| pilot3k / disjoint3k / narrow3k | 0 / 0 / 0 |
| test_90k lịch sử R86/P1 | **10.000** |
| public 100K Task A đã đánh giá | **10.000** |
| Panel v2 với chính nó | 10.000, count=unique count |

Validation chọn beam; warmup dùng 100 query validation cũ trước từng process; test panel dùng toàn bộ 10k cho cả quality ON và performance OFF tương lai. Không dùng test 10k làm warmup hoặc chọn 3k thuận lợi để giảm chi phí. Việc dùng ON để quality gate rồi OFF cùng panel là validation của cấu hình đã khóa, không cho phép retune; mọi gate fail được giữ nguyên.

Design-2 chỉ hỗ trợ p2. p1/p4 cần extension prereg riêng trước dữ liệu extension, không tự mở bằng approval hiện tại. Lặp lại query qua graph, policy, mode, worker và process chỉ tạo repeated measurements; unique query N vẫn bằng 10k.

## 6. Phạm vi xác minh và preservation

Đã kiểm SHA manifest Stage 5 `82e740bcd6224bd28dfa2dcdbedba4902515b0fc578ed923250ef5d568337e15` (562 entries), Stage 6 `cd65a8acf17b59f0b566750994f1ef7aa6a81c3a0ac89081add5af256927841f` (101 entries). Đã đối chiếu digest payload được đọc để phân tích: 60 file hits Stage 5 + quality_table/reuse audit (**62 mục**) và **12 hits Stage 6**. Đây là kiểm các payload dùng trong phân tích, không tuyên bố rehash toàn bộ 663 payload hoặc graph/vector GB trong task này.

Prereg v1 SHA `cb6433cb2c04108653cca7e8d63ed9688f3b19fa68a0b236acccc28d766393eb` được giữ nguyên; snapshot SHA các tài liệu hiện có được dùng để hậu kiểm không sửa Stage 5/6/report lịch sử. Không thay ID lists, graph, source, binary hoặc raw evidence. Không có Google Sheets write, không có benchmark/profiler, không có i5-14600KF.

**Giới hạn không khắc phục bằng split:** lịch sử dùng public pool, lựa chọn v2 sau khi biết v1, validation đã nhìn, một host, sáu graph chưa chứng minh root độc lập và không có query/GT mới ngoài public 100K. Có thể giảm direct reuse và khóa tránh feedback tiếp theo; không thể đổi nhãn thành confirmatory chỉ bằng tên panel hoặc SHA mới.
