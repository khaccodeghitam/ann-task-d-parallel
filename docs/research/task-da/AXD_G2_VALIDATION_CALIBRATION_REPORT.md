# A×D G2 · Validation-Only Quality Calibration Report

- **Final Verdict:** **`VALIDATION_QUALITY_READY_FOR_REVIEW`** *(trạng thái máy trong [result.json](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/result.json): `READY_FOR_HELDOUT_QUALITY_CHECK`; nhãn phạm vi: **`EXPLORATORY_HOST_SPECIFIC`**; `test_executions = 0`, `OFF_executions = 0`, `G2 OFF performance = NOT_OPEN`).*
- **Durable Evidence Directory:** [axd-g2-validation-20261122-G81SkWjO](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/) (`562` tệp băm trong [BUNDLE.sha256](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/BUNDLE.sha256), tổng `642.17 MiB`, `BUNDLE.sha256` SHA-256: `82e740bcd6224bd28dfa2dcdbedba4902515b0fc578ed923250ef5d568337e15`).
- **Anchor Documents:** [Prereg đã khóa](AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md) (`cb6433cb...`, giữ nguyên từng byte) · [G1 Graph Manifest](AXD_G1_GRAPH_ARTIFACT_MANIFEST.md) · [G1 Runtime Report](AXD_G1_RUNTIME_PARITY_REPORT.md) · [Quality & Test Gate](AXD_G2_QUALITY_AND_TEST_GATE.md) · [G2 Readiness](AXD_G2_PREREG_READINESS.md).

---

## 1. Stage 0 — Recovery, Provenance & Integrity Audit (`PASS`)

1. **Tình trạng tiến trình & thư mục `/tmp`:** Không có tiến trình calibration nào đang chạy tại thời điểm kiểm tra (`2026-11-23 01:14+07:00`). Kiểm tra thực tế `/tmp/axd-g2-validation-20261122-G81SkWjO/` xác nhận lượt chạy trước đã hoàn tất trọn vẹn **cả 54/54 ô baseline** lẫn **6/6 ô B1+A1** lúc `00:34+07:00` (`CALIBRATION_COMPLETE READY_FOR_HELDOUT_QUALITY_CHECK`), nhưng chưa chạy bước kiểm toán hậu kỳ, sao lưu durable và xuất báo cáo.
2. **Phân loại toàn bộ 60 ô (tái kiểm độc lập từ raw JSONL, `manifest.json`, `p2_eval_summary.json`, `hits_*.u8`):**
   - **Baseline grid (`6 graph × 9 beam = 54 ô`):** **`54/54 COMPLETE_VALID`**, `0 IN_PROGRESS`, `0 FAILED`, `0 MISSING`. **Không chạy lại bất kỳ ô hợp lệ nào.**
   - **B1+A1 validation (`6 graph × 1 beam chọn = 6 ô`):** **`6/6 COMPLETE_VALID`**, `0 IN_PROGRESS`, `0 FAILED`, `0 MISSING`.
3. **Bảo toàn `/tmp` & sao lưu durable:** Không xóa hay ghi đè bất kỳ tệp nào trong `/tmp/axd-g2-validation-20261122-G81SkWjO/`. Đã sao chép trọn vẹn sang durable `../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/` và kiểm chứng **`558/558` tệp khớp SHA-256 từng byte** giữa `/tmp` và bản durable; sau đó chạy [final_audit.py](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/final_audit.py), [replay_quality.py](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/replay_quality.py) (`QUALITY_REPLAY_PASS 60 cells`), xuất [full_60cell_quality_matrix.csv](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/full_60cell_quality_matrix.csv) và niêm phong [BUNDLE.sha256](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/BUNDLE.sha256) (`562/562` tái xác minh).
4. **Tính nhất quán giao thức & danh tính khóa (không có `BLOCKED_PROTOCOL_MISMATCH`):**
   - Git `HEAD = f54b1bb653652dd13e760cc00c9fb46d0e643c1c` (`research/task-da-pivot-b1-a1-20261119`), `git diff` rỗng.
   - Mã nguồn search đóng băng tại commit `f2cd634b837a70735c3e31e5956f0524bfc26675` (`p2_engine.hpp` `c4b1bdc2...`, `p2_eval.cpp` `b356ba8d...`, `engine.hpp` `2ca38624...`) khớp chính xác bản lưu trong G1 và Release ELF `build-task-da/task_da_p2_eval` (`7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1`). *(Ghi chú minh bạch: các commit sau `f2cd634` trên nhánh chỉ bổ sung observer `p2_round_trace.hpp` ở HEAD mà không build lại ELF đóng băng `7a2685e5...`.)*
   - Khớp chính xác: `AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md == locked_prereg.md` (`cb6433cb...`), `6/6` graph gốc R90 v1.3, `23/23` frozen pins (gồm `val_10k.ids` `a3c948e9...`, `narrow_test_3000.ids` `77fda031...`, `warmup_val_100.ids` `199ca606...`, `base/query/GT`), và `229/229` tệp G1 bundle (`46760827...`).
5. **Resource Guard & Telemetry ([final_verification.json](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/final_verification.json)):**
   - Host: `AMD Ryzen 5 PRO 4650U`, cấu hình `p=2`, `S=16`, `flat`, `jobs=1`, `entry=0`, `K=10`, `requested_cpus == observed_cpus == [0, 2]` trên `60/60` lượt.
   - `60/60` tiến trình thoát `exit_code = 0`, **`0` guard failure**, `2,715` mẫu telemetry host, `Tctl = 67.625°C – 91.375°C` (dưới ngưỡng abort `95°C`), `peak_rss_max = 871,808 KiB`, tổng thời gian wall `2,688.0 s` (`44.8 phút` << quota `10,800 s`). Mọi `argv` đều dùng `val_10k.ids` và `--mode ON`; **`0` lượt held-out test, `0` lượt OFF.**

---

## 2. Stage 2 — Lựa chọn Beam theo Quy tắc Đã Khóa (`val_10k` ONLY)

Áp dụng đúng quy tắc trong [locked_protocol.json](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/locked_protocol.json): giữ các điểm baseline có `nominal LCB95 = mean - 1.96 × SE >= 0.990` (với `N = 10,000`), xét mọi bộ 6 beam `(Stock r1, Stock r2, Stock r3, Fast r1, Fast r2, Fast r3)` có `span(point) <= 0.0001` (`<= 10` GT hits trên `100,000`), cực tiểu hóa theo thứ tự `(max |point - 0.9913|, sum(beams), tuple_lex)`.

### 2.1 Các ứng viên không đạt ngưỡng `nominal LCB95 >= 0.990` (`11/54` ô baseline)
*(Toàn bộ `54/54` ô đều có point `Recall@10 >= 0.99004`, nhưng `11/54` ô trượt ngưỡng nominal `LCB95 >= 0.990` và bị loại trước bước ghép cặp:)*

| Graph | Các beam bị loại (`LCB95 < 0.990`) | Beam thấp nhất đạt `LCB95 >= 0.990` |
|---|---|---:|
| `MS-Turing1M_stock_off_r1.graph` | `384` (`0.99004 / LCB 0.989302`), `400` (`0.99054 / LCB 0.989822`), `404` (`0.99066 / LCB 0.989948`) | `408` (`LCB 0.990123`) |
| `MS-Turing1M_stock_off_r2.graph` | `384` (`0.99009 / LCB 0.989344`), `400` (`0.99063 / LCB 0.989906`) | `404` (`LCB 0.990062`) |
| `MS-Turing1M_stock_off_r3.graph` | `384` (`0.99009 / LCB 0.989342`), `400` (`0.99060 / LCB 0.989874`) | `404` (`LCB 0.990030`) |
| `MS-Turing1M_fast_off_r1.graph` | `384` (`0.99015 / LCB 0.989421`), `400` (`0.99063 / LCB 0.989919`) | `404` (`LCB 0.990001`) |
| `MS-Turing1M_fast_off_r2.graph` | `384` (`0.99030 / LCB 0.989574`) | `400` (`LCB 0.990055`) |
| `MS-Turing1M_fast_off_r3.graph` | `384` (`0.99039 / LCB 0.989671`) | `400` (`LCB 0.990182`) |

### 2.2 Toàn bộ 5 bộ 6-beam hợp lệ & Bộ được chọn ([beam_selection.json](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/beam_selection.json))

| Hạng | Bộ beam `(Stock r1,r2,r3, Fast r1,r2,r3)` | Tổng beam | `max \|point - 0.9913\|` | `span(point)` | `total_hits / 100,000` từng graph | Quyết định |
|---:|---|---:|---:|---:|---|---|
| **#1** | **`(420, 420, 420, 420, 416, 412)`** | **`2,508`** | **`0.00006`** (`6` hits) | **`0.00008`** (`8` hits) | `[99127, 99124, 99128, 99132, 99129, 99127]` | **SELECTED** |
| #2 | `(424, 424, 424, 424, 420, 416)` | `2,532` | `0.00016` (`16` hits) | `0.00009` (`9` hits) | `[99143, 99138, 99137, 99146, 99140, 99142]` | Eligible |
| #3 | `(416, 416, 416, 416, 412, 408)` | `2,484` | `0.00018` (`18` hits) | `0.00006` (`6` hits) | `[99117, 99118, 99112, 99113, 99114, 99115]` | Eligible |
| #4 | `(412, 412, 412, 412, 408, 404)` | `2,460` | `0.00033` (`33` hits) | `0.00007` (`7` hits) | `[99100, 99104, 99098, 99104, 99097, 99099]` | Eligible |
| #5 | `(408, 408, 408, 408, 404, 400)` | `2,436` | `0.00049` (`49` hits) | `0.00008` (`8` hits) | `[99083, 99089, 99088, 99089, 99081, 99088]` | Eligible |

- **Phân biệt Nominal Fixed-Beam CI vs Post-Selection Uncertainty:** Mỗi `nominal LCB95 = mean - 1.96 × SE` ở trên chỉ là cận dưới chuẩn xấp xỉ danh nghĩa tại **một điểm beam cố định** (có điều kiện trên 6 graph này và việc lấy mẫu `val_10k`). Do bộ `(420, 420, 420, 420, 416, 412)` được **lựa chọn từ 9 ứng viên/graph trên chính tập `val_10k`**, khoảng tin cậy tại beam đã chọn mang tính **calibration nội bộ**, chịu hiệu ứng chọn lọc hậu kiểm (post-selection inference) và **không được coi là chứng nhận thống kê độc lập**.

---

## 3. Stage 3 — Kiểm chứng 6/6 Ô B1+A1 tại Các Beam Đã Chọn (`PASS`)

Tại đúng bộ beam khóa `(420, 420, 420, 420, 416, 412)`, đã đối chiếu độc lập toàn bộ `6 × 10,000 = 60,000` cặp query giữa **baseline** (`flat, baseline/full`) và **B1+A1** (`flat, barrier_all_evaled/incremental`):

| Graph | Beam khóa | Base `Recall@10` / `LCB95` | B1+A1 `Recall@10` / `LCB95` | Ordered top-10 & `L2²` Parity | Logical Counter Invariants | Chẩn đoán ON `dup_L2/q` (base -> B1+A1) |
|---|---:|---:|---:|---|---|---:|
| `stock_off_r1` | `420` | `0.991270` / `0.990583` | `0.991270` / `0.990583` | **EXACT (`10,000/10,000`, `Δ=0`)** | **PASS** | `3611.1 -> 922.3` (`-74.5%`) |
| `stock_off_r2` | `420` | `0.991240` / `0.990542` | `0.991240` / `0.990542` | **EXACT (`10,000/10,000`, `Δ=0`)** | **PASS** | `3614.6 -> 926.8` (`-74.4%`) |
| `stock_off_r3` | `420` | `0.991280` / `0.990586` | `0.991280` / `0.990586` | **EXACT (`10,000/10,000`, `Δ=0`)** | **PASS** | `3610.6 -> 922.6` (`-74.4%`) |
| `fast_off_r1` | `420` | `0.991320` / `0.990640` | `0.991320` / `0.990640` | **EXACT (`10,000/10,000`, `Δ=0`)** | **PASS** | `3612.1 -> 921.7` (`-74.5%`) |
| `fast_off_r2` | `416` | `0.991290` / `0.990606` | `0.991290` / `0.990606` | **EXACT (`10,000/10,000`, `Δ=0`)** | **PASS** | `3567.1 -> 916.2` (`-74.3%`) |
| `fast_off_r3` | `412` | `0.991270` / `0.990586` | `0.991270` / `0.990586` | **EXACT (`10,000/10,000`, `Δ=0`)** | **PASS** | `3532.0 -> 919.5` (`-74.0%`) |

- **Bất biến counter xác minh trên `60,000/60,000` queries:** `unique_distance_evaluations`, `expansions`, `unique_expansions`, `duplicate_expansions`, `neighbor_attempts`, `frontier_insertions`, `sync_merge_count`, `per_worker_expansions`, `per_worker_idle_rounds` khớp từng đơn vị giữa `base` và `B1+A1`; mỗi phép L2 trùng tiết kiệm chuyển chính xác sang `already_seen_attempts`.
- **Cohort fixed-6-graph summary (bảo toàn tương quan dùng chung `val_10k`):** `mean = 0.991278`, `query_SE = 0.00032577`, `nominal LCB95 = 0.990640` (có điều kiện trên đúng 6 graph này; `population independent-root CI = NOT_ESTIMABLE`).
- **Ranh giới hiệu năng:** Toàn bộ 60 lượt chạy ở chế độ **`ON`** phục vụ hiệu chỉnh chất lượng; **tuyệt đối không dùng thời gian chạy calibration để tuyên bố performance speedup**.

---

## 4. Stage 4 — Đánh giá Khoa học, Rò rỉ/Tái sử dụng & Giới hạn

1. **Sáu graph có đều vượt ngưỡng đã đăng ký không?** **Có** — tại bộ beam chọn `(420, 420, 420, 420, 416, 412)`, cả 6 graph × 2 policy (`12/12` ô chọn) đều đạt `Recall@10 ∈ [0.991240, 0.991320]` và `nominal LCB95 ∈ [0.990542, 0.990640] >= 0.990` trên `val_10k`.
2. **B1+A1 có giữ chất lượng so với baseline không?** **Có, tuyệt đối từng bit** — `0/60,000` sai khác về ordered top-10 IDs, `squared_l2`, và Recall (`ΔRecall = 0` trên từng query), thỏa toàn bộ logical counter invariants.
3. **Có tồn tại bộ beam matching phù hợp protocol không?** **Có** — tồn tại `5` bộ hợp lệ trong grid cố định 9 beam; quy tắc khóa chọn duy nhất `(420, 420, 420, 420, 416, 412)` với `span = 0.00008 <= 0.0001` (không mở rộng grid, không sửa ngưỡng).
4. **Kết quả có phụ thuộc post-selection inference không?** **Có.** Việc quét 9 mức beam rồi chọn bộ gần `0.9913` nhất trên cùng `val_10k` làm cho khoảng `LCB95` trên `val_10k` tại beam chọn là ước lượng hậu chọn lọc (calibration), có xu hướng lạc quan nhẹ so với đánh giá trên tập mới độc lập. Ngoài ra, `600,000` query executions đều dùng chung `10,000` query IDs, không làm tăng số graph hay số query độc lập.
5. **Tình trạng rò rỉ / tái sử dụng của `val_10k` và `test3k` ([split_and_reuse_audit.json](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/split_and_reuse_audit.json)):**
   - `val_10k.ids` (`a3c948e9...`) và `narrow_test_3000.ids` (`77fda031...`) có `overlap_ids = 0` (rời nhau hoàn toàn theo ID), và trong lượt này `test_executions = 0` (không dùng test để chọn beam).
   - **Tuy nhiên**, toàn bộ `3,000` query của `narrow_test_3000.ids` **đã từng được dùng trong P1 và nghiên cứu narrow B1+A1 trước đó**, đồng thời toàn bộ `public 100K` **đã được Task A đánh giá**. Do đó **không được gọi `test3k` là fresh untouched holdout**.
6. **Confirmatory hay Exploratory?** Chỉ đủ cơ sở cho **`EXPLORATORY_HOST_SPECIFIC`** (cohort cố định 6 graph với `root independence NOT_VERIFIED`, `independent-root population CI = NOT_ESTIMABLE`, và chưa có panel query/GT unseen độc lập cho suy luận confirmatory).

---

## 5. Ma trận Đầy đủ 60 Ô Validation Calibration (`val_10k`, `p=2`, `S=16`, `ON`)

Nguồn CSV đồng bộ: [full_60cell_quality_matrix.csv](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/full_60cell_quality_matrix.csv) · [quality_table.csv](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/quality_table.csv).

| Graph | Policy | Beam | Query count | Recall@10 | SE | Nominal LCB95 | Matching status | Quality status |
|---|---|---:|---:|---:|---:|---:|---|---|
| `stock_off_r1` | baseline (`baseline/full`) | 384 | 10000 | 0.990040 | 0.00037669 | 0.989302 | `INELIGIBLE_LCB_LT_0990` | `FAIL_LCB95_HOLD` |
| `stock_off_r1` | baseline (`baseline/full`) | 400 | 10000 | 0.990540 | 0.00036642 | 0.989822 | `INELIGIBLE_LCB_LT_0990` | `FAIL_LCB95_HOLD` |
| `stock_off_r1` | baseline (`baseline/full`) | 404 | 10000 | 0.990660 | 0.00036344 | 0.989948 | `INELIGIBLE_LCB_LT_0990` | `FAIL_LCB95_HOLD` |
| `stock_off_r1` | baseline (`baseline/full`) | 408 | 10000 | 0.990830 | 0.00036070 | 0.990123 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `stock_off_r1` | baseline (`baseline/full`) | 412 | 10000 | 0.991000 | 0.00035709 | 0.990300 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `stock_off_r1` | baseline (`baseline/full`) | 416 | 10000 | 0.991170 | 0.00035202 | 0.990480 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| **`stock_off_r1`** | **baseline (`baseline/full`)** | **420** | **10000** | **0.991270** | **0.00035027** | **0.990583** | **`SELECTED_TUPLE (span=0.00008)`** | **`PASS_LCB95`** |
| `stock_off_r1` | baseline (`baseline/full`) | 424 | 10000 | 0.991430 | 0.00034694 | 0.990750 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `stock_off_r1` | baseline (`baseline/full`) | 432 | 10000 | 0.991730 | 0.00033893 | 0.991066 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `stock_off_r2` | baseline (`baseline/full`) | 384 | 10000 | 0.990090 | 0.00038065 | 0.989344 | `INELIGIBLE_LCB_LT_0990` | `FAIL_LCB95_HOLD` |
| `stock_off_r2` | baseline (`baseline/full`) | 400 | 10000 | 0.990630 | 0.00036923 | 0.989906 | `INELIGIBLE_LCB_LT_0990` | `FAIL_LCB95_HOLD` |
| `stock_off_r2` | baseline (`baseline/full`) | 404 | 10000 | 0.990780 | 0.00036621 | 0.990062 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `stock_off_r2` | baseline (`baseline/full`) | 408 | 10000 | 0.990890 | 0.00036499 | 0.990175 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `stock_off_r2` | baseline (`baseline/full`) | 412 | 10000 | 0.991040 | 0.00036164 | 0.990331 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `stock_off_r2` | baseline (`baseline/full`) | 416 | 10000 | 0.991180 | 0.00035726 | 0.990480 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| **`stock_off_r2`** | **baseline (`baseline/full`)** | **420** | **10000** | **0.991240** | **0.00035600** | **0.990542** | **`SELECTED_TUPLE (span=0.00008)`** | **`PASS_LCB95`** |
| `stock_off_r2` | baseline (`baseline/full`) | 424 | 10000 | 0.991380 | 0.00035325 | 0.990688 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `stock_off_r2` | baseline (`baseline/full`) | 432 | 10000 | 0.991590 | 0.00034386 | 0.990916 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `stock_off_r3` | baseline (`baseline/full`) | 384 | 10000 | 0.990090 | 0.00038144 | 0.989342 | `INELIGIBLE_LCB_LT_0990` | `FAIL_LCB95_HOLD` |
| `stock_off_r3` | baseline (`baseline/full`) | 400 | 10000 | 0.990600 | 0.00037038 | 0.989874 | `INELIGIBLE_LCB_LT_0990` | `FAIL_LCB95_HOLD` |
| `stock_off_r3` | baseline (`baseline/full`) | 404 | 10000 | 0.990750 | 0.00036737 | 0.990030 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `stock_off_r3` | baseline (`baseline/full`) | 408 | 10000 | 0.990880 | 0.00036455 | 0.990165 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `stock_off_r3` | baseline (`baseline/full`) | 412 | 10000 | 0.990980 | 0.00036287 | 0.990269 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `stock_off_r3` | baseline (`baseline/full`) | 416 | 10000 | 0.991120 | 0.00036018 | 0.990414 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| **`stock_off_r3`** | **baseline (`baseline/full`)** | **420** | **10000** | **0.991280** | **0.00035385** | **0.990586** | **`SELECTED_TUPLE (span=0.00008)`** | **`PASS_LCB95`** |
| `stock_off_r3` | baseline (`baseline/full`) | 424 | 10000 | 0.991370 | 0.00035194 | 0.990680 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `stock_off_r3` | baseline (`baseline/full`) | 432 | 10000 | 0.991750 | 0.00033542 | 0.991093 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r1` | baseline (`baseline/full`) | 384 | 10000 | 0.990150 | 0.00037204 | 0.989421 | `INELIGIBLE_LCB_LT_0990` | `FAIL_LCB95_HOLD` |
| `fast_off_r1` | baseline (`baseline/full`) | 400 | 10000 | 0.990630 | 0.00036268 | 0.989919 | `INELIGIBLE_LCB_LT_0990` | `FAIL_LCB95_HOLD` |
| `fast_off_r1` | baseline (`baseline/full`) | 404 | 10000 | 0.990710 | 0.00036150 | 0.990001 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r1` | baseline (`baseline/full`) | 408 | 10000 | 0.990890 | 0.00035807 | 0.990188 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r1` | baseline (`baseline/full`) | 412 | 10000 | 0.991040 | 0.00035353 | 0.990347 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r1` | baseline (`baseline/full`) | 416 | 10000 | 0.991130 | 0.00035220 | 0.990440 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| **`fast_off_r1`** | **baseline (`baseline/full`)** | **420** | **10000** | **0.991320** | **0.00034710** | **0.990640** | **`SELECTED_TUPLE (span=0.00008)`** | **`PASS_LCB95`** |
| `fast_off_r1` | baseline (`baseline/full`) | 424 | 10000 | 0.991460 | 0.00034427 | 0.990785 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r1` | baseline (`baseline/full`) | 432 | 10000 | 0.991720 | 0.00033787 | 0.991058 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r2` | baseline (`baseline/full`) | 384 | 10000 | 0.990300 | 0.00037041 | 0.989574 | `INELIGIBLE_LCB_LT_0990` | `FAIL_LCB95_HOLD` |
| `fast_off_r2` | baseline (`baseline/full`) | 400 | 10000 | 0.990760 | 0.00035983 | 0.990055 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r2` | baseline (`baseline/full`) | 404 | 10000 | 0.990810 | 0.00035870 | 0.990107 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r2` | baseline (`baseline/full`) | 408 | 10000 | 0.990970 | 0.00035575 | 0.990273 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r2` | baseline (`baseline/full`) | 412 | 10000 | 0.991140 | 0.00035123 | 0.990452 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| **`fast_off_r2`** | **baseline (`baseline/full`)** | **416** | **10000** | **0.991290** | **0.00034889** | **0.990606** | **`SELECTED_TUPLE (span=0.00008)`** | **`PASS_LCB95`** |
| `fast_off_r2` | baseline (`baseline/full`) | 420 | 10000 | 0.991400 | 0.00034528 | 0.990723 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r2` | baseline (`baseline/full`) | 424 | 10000 | 0.991510 | 0.00034103 | 0.990842 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r2` | baseline (`baseline/full`) | 432 | 10000 | 0.991780 | 0.00033534 | 0.991123 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r3` | baseline (`baseline/full`) | 384 | 10000 | 0.990390 | 0.00036699 | 0.989671 | `INELIGIBLE_LCB_LT_0990` | `FAIL_LCB95_HOLD` |
| `fast_off_r3` | baseline (`baseline/full`) | 400 | 10000 | 0.990880 | 0.00035594 | 0.990182 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r3` | baseline (`baseline/full`) | 404 | 10000 | 0.990990 | 0.00035355 | 0.990297 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r3` | baseline (`baseline/full`) | 408 | 10000 | 0.991150 | 0.00035140 | 0.990461 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| **`fast_off_r3`** | **baseline (`baseline/full`)** | **412** | **10000** | **0.991270** | **0.00034913** | **0.990586** | **`SELECTED_TUPLE (span=0.00008)`** | **`PASS_LCB95`** |
| `fast_off_r3` | baseline (`baseline/full`) | 416 | 10000 | 0.991420 | 0.00034619 | 0.990741 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r3` | baseline (`baseline/full`) | 420 | 10000 | 0.991530 | 0.00034371 | 0.990856 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r3` | baseline (`baseline/full`) | 424 | 10000 | 0.991620 | 0.00034204 | 0.990950 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| `fast_off_r3` | baseline (`baseline/full`) | 432 | 10000 | 0.991820 | 0.00033782 | 0.991158 | `ELIGIBLE_NOT_SELECTED` | `PASS_LCB95` |
| **`stock_off_r1`** | **B1+A1 (`barrier_all_evaled/incremental`)** | **420** | **10000** | **0.991270** | **0.00035027** | **0.990583** | **`MATCHED_EXACT_PARITY (Δ=0, span=0.00008)`** | **`PASS_LCB95_AND_PARITY`** |
| **`stock_off_r2`** | **B1+A1 (`barrier_all_evaled/incremental`)** | **420** | **10000** | **0.991240** | **0.00035600** | **0.990542** | **`MATCHED_EXACT_PARITY (Δ=0, span=0.00008)`** | **`PASS_LCB95_AND_PARITY`** |
| **`stock_off_r3`** | **B1+A1 (`barrier_all_evaled/incremental`)** | **420** | **10000** | **0.991280** | **0.00035385** | **0.990586** | **`MATCHED_EXACT_PARITY (Δ=0, span=0.00008)`** | **`PASS_LCB95_AND_PARITY`** |
| **`fast_off_r1`** | **B1+A1 (`barrier_all_evaled/incremental`)** | **420** | **10000** | **0.991320** | **0.00034710** | **0.990640** | **`MATCHED_EXACT_PARITY (Δ=0, span=0.00008)`** | **`PASS_LCB95_AND_PARITY`** |
| **`fast_off_r2`** | **B1+A1 (`barrier_all_evaled/incremental`)** | **416** | **10000** | **0.991290** | **0.00034889** | **0.990606** | **`MATCHED_EXACT_PARITY (Δ=0, span=0.00008)`** | **`PASS_LCB95_AND_PARITY`** |
| **`fast_off_r3`** | **B1+A1 (`barrier_all_evaled/incremental`)** | **412** | **10000** | **0.991270** | **0.00034913** | **0.990586** | **`MATCHED_EXACT_PARITY (Δ=0, span=0.00008)`** | **`PASS_LCB95_AND_PARITY`** |
