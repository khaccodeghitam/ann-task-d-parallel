# A×D G2 · Stage 6 Test Quality Verification Report (`narrow_test_3000`)

- **Official Stage 6 Verdict:** **`QUALITY_HOLD`** *(giữ nguyên quy tắc prereg đóng băng; **không** tự nới ngưỡng `span <= 0.0001`, **không** retune beam trên test, **không** tự mở G2 OFF performance).*
- **Scope & Mandatory Disclosure:** **`EXPLORATORY_HOST_SPECIFIC`** — toàn bộ `3,000` query của `narrow_test_3000.ids` (`SHA-256: 77fda031...`) **đã từng được dùng trong P1 và nghiên cứu narrow B1+A1**, còn toàn bộ `public 100K` **đã được Task A đánh giá**. **Đây KHÔNG phải fresh untouched holdout và KHÔNG tuyên bố confirmatory unseen quality.**
- **Durable Evidence Directory:** [axd-g2-stage6-test-quality-20261123](../../../../artifact-evidence/axd-g2-stage6-test-quality-20261123/) (`101` tệp đã băm & tự xác minh trong [BUNDLE.sha256](../../../../artifact-evidence/axd-g2-stage6-test-quality-20261123/BUNDLE.sha256), tổng `39.03 MiB`, SHA-256: `cd65a8acf17b59f0b566750994f1ef7aa6a81c3a0ac89081add5af256927841f`).
- **Related Documents:** [Stage 5 Calibration Report](AXD_G2_VALIDATION_CALIBRATION_REPORT.md) · [Quality & Test Gate](AXD_G2_QUALITY_AND_TEST_GATE.md) · [OFF Pilot Prereg Review](AXD_G2_OFF_PILOT_PREREG_REVIEW.md) · [Stage 6 Final Decision](AXD_G2_STAGE6_FINAL_DECISION.md).

---

## 1. Stage 0 — Final Evidence & Git Audit (`PASS` Provenance / Untracked Docs Noted)

Kiểm toán trước khi chạy Stage 6 ([initial_provenance.json](../../../../artifact-evidence/axd-g2-stage6-test-quality-20261123/initial_provenance.json)):
1. **Git status & Stage 5 reports:** Nhánh `research/task-da-pivot-b1-a1-20261119`, `HEAD = f54b1bb653652dd13e760cc00c9fb46d0e643c1c`, `git diff` và `git diff --cached` rỗng (`0` tracked modifications). Ba báo cáo Stage 5 (`AXD_G2_VALIDATION_CALIBRATION_REPORT.md`, `AXD_G2_QUALITY_AND_TEST_GATE.md`, `AXD_G2_PREREG_READINESS.md`) cùng `AXD_G1_*` và `AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md` tồn tại nguyên vẹn trên đĩa và đã ghi SHA-256 trước chạy, nhưng hiện đang ở trạng thái **untracked (`??`)** do chưa có lệnh commit của owner (không tự commit/rewrite lịch sử).
2. **Stage 5 Durable Bundle:** Xác minh toàn bộ **`562/562`** mục trong [Stage 5 BUNDLE.sha256](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/BUNDLE.sha256) (`82e740bc...`) khớp SHA-256 trên ổ đĩa durable (không dựa vào `/tmp`).
3. **Frozen Source, ELF, Graphs, Query IDs, GT & Beams:**
   - Mã nguồn search đóng băng `f2cd634b837a70735c3e31e5956f0524bfc26675` khớp bản lưu G1 (`c4b1bdc2...`, `b356ba8d...`, `2ca38624...`); Release ELF `build-task-da/task_da_p2_eval` khớp `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1`.
   - `23/23` frozen pins khớp trước và sau khi chạy (gồm `narrow_test_3000.ids` `77fda031...`, `warmup_val_100.ids` `199ca606...`, `groundtruth.public.100K.ibin` `fa5acf5a...`, `overlap(val_10k, narrow_test_3000) = 0`).
   - `6/6` graph gốc R90 v1.3 khớp SHA-256 trước và sau chạy; bộ beam khóa: `Stock R1/R2/R3 = 420/420/420`, `Fast R1/R2/R3 = 420/416/412`. **Không chạy lại calibration.**

---

## 2. Stage 6 Execution & Guard Telemetry (`12/12` ON Processes, `0` OFF)

- **Thiết kế chạy thực tế:** `6` graph × `2` policies (`base`: `flat, baseline/full`; `combo`: `flat, barrier_all_evaled/incremental`) = **`12` tiến trình `ON` tuần tự** trên `AMD Ryzen 5 PRO 4650U`, `p=2`, `S=16`, `jobs=1`, `entry=0`, `K=10`, `CPU [0,2]`, `100` warmup (`warmup_val_100.ids`) + `3,000` test queries (`narrow_test_3000.ids`).
- **Guard & Telemetry ([stage6_test_quality_result.json](../../../../artifact-evidence/axd-g2-stage6-test-quality-20261123/stage6_test_quality_result.json)):** `12/12` tiến trình `exit_code = 0`, **`0` guard failure**, `187` mẫu host (`Tctl = 58.125–83.750°C`, dưới ngưỡng start `85°C` và abort `95°C`), `observed_cpus == [0, 2]` trên `12/12` lượt, `max_rss = 871,800 KiB`, `OFF_executions = 0`. *(Tuyệt đối không dùng thời gian chạy ON làm kết quả performance.)*

---

## 3. Stage 7 — Bảng Kết quả Chất lượng & Parity (`narrow_test_3000.ids`, `N = 3,000`)

Nguồn CSV đồng bộ: [stage6_test_quality_table.csv](../../../../artifact-evidence/axd-g2-stage6-test-quality-20261123/stage6_test_quality_table.csv).

| Graph | Policy | Beam | Recall@10 | LCB95 | Top-10 parity | L2 parity | Counter invariants | Status |
|---|---|---:|---:|---:|---|---|---|---|
| `stock_off_r1` | baseline (`baseline/full`) | 420 | `0.991667` | `0.990435` | `PASS` (`0/3000`) | `PASS` (`0/3000`) | `PASS` | `POINT_PASS / SPAN_HOLD` |
| `stock_off_r1` | B1+A1 (`barrier_all_evaled/incremental`) | 420 | `0.991667` | `0.990435` | `PASS` (`0/3000`) | `PASS` (`0/3000`) | `PASS` | `POINT_PASS / SPAN_HOLD` |
| `stock_off_r2` | baseline (`baseline/full`) | 420 | `0.990967` | `0.989761` | `PASS` (`0/3000`) | `PASS` (`0/3000`) | `PASS` | `POINT_PASS / LCB<0.990*` |
| `stock_off_r2` | B1+A1 (`barrier_all_evaled/incremental`) | 420 | `0.990967` | `0.989761` | `PASS` (`0/3000`) | `PASS` (`0/3000`) | `PASS` | `POINT_PASS / LCB<0.990*` |
| `stock_off_r3` | baseline (`baseline/full`) | 420 | `0.990833` | `0.989601` | `PASS` (`0/3000`) | `PASS` (`0/3000`) | `PASS` | `POINT_PASS / LCB<0.990*` |
| `stock_off_r3` | B1+A1 (`barrier_all_evaled/incremental`) | 420 | `0.990833` | `0.989601` | `PASS` (`0/3000`) | `PASS` (`0/3000`) | `PASS` | `POINT_PASS / LCB<0.990*` |
| `fast_off_r1` | baseline (`baseline/full`) | 420 | `0.990900` | `0.989613` | `PASS` (`0/3000`) | `PASS` (`0/3000`) | `PASS` | `POINT_PASS / LCB<0.990*` |
| `fast_off_r1` | B1+A1 (`barrier_all_evaled/incremental`) | 420 | `0.990900` | `0.989613` | `PASS` (`0/3000`) | `PASS` (`0/3000`) | `PASS` | `POINT_PASS / LCB<0.990*` |
| `fast_off_r2` | baseline (`baseline/full`) | 416 | `0.991233` | `0.990014` | `PASS` (`0/3000`) | `PASS` (`0/3000`) | `PASS` | `POINT_PASS / SPAN_HOLD` |
| `fast_off_r2` | B1+A1 (`barrier_all_evaled/incremental`) | 416 | `0.991233` | `0.990014` | `PASS` (`0/3000`) | `PASS` (`0/3000`) | `PASS` | `POINT_PASS / SPAN_HOLD` |
| `fast_off_r3` | baseline (`baseline/full`) | 412 | `0.990633` | `0.989345` | `PASS` (`0/3000`) | `PASS` (`0/3000`) | `PASS` | `POINT_PASS / SPAN_HOLD / LCB<0.990*` |
| `fast_off_r3` | B1+A1 (`barrier_all_evaled/incremental`) | 412 | `0.990633` | `0.989345` | `PASS` (`0/3000`) | `PASS` (`0/3000`) | `PASS` | `POINT_PASS / SPAN_HOLD / LCB<0.990*` |

*\*Ghi chú cổng prereg (`AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md` dòng 39): trên `test 3k`, prereg đặt ngưỡng cứng `point >= 0.990`, **`span giữa 6 graph <= 0.0001`**, và `exact parity trong graph` (báo `LCB95` mang tính mô tả vì `N=3,000` có `1.96×SE ≈ 0.0012–0.0013`). **Cổng cứng bị trượt trực tiếp là `span = 0.001033 > 0.0001`** (`31` GT hits so với mức trần `3` hits trên `30,000`).*

### Chẩn đoán ON Counters (Chỉ mang tính công việc logic, KHÔNG dùng suy ra OFF latency)

| Graph | Beam | `uniq_L2/q` (`base == B1+A1`) | `exp/q` (`base == B1+A1`) | `dup_L2/q` (`base -> B1+A1`) | Mức giảm `dup_L2/q` |
|---|---:|---:|---:|---:|---:|
| `stock_off_r1` | 420 | `18633.8` | `445.7` | `3584.8 -> 916.5` | `-74.4%` |
| `stock_off_r2` | 420 | `18633.1` | `445.5` | `3579.8 -> 910.4` | `-74.6%` |
| `stock_off_r3` | 420 | `18639.6` | `445.5` | `3573.5 -> 903.8` | `-74.7%` |
| `fast_off_r1` | 420 | `18633.8` | `445.7` | `3586.6 -> 914.6` | `-74.5%` |
| `fast_off_r2` | 416 | `18479.2` | `441.6` | `3542.9 -> 910.6` | `-74.3%` |
| `fast_off_r3` | 412 | `18313.2` | `437.6` | `3511.7 -> 916.8` | `-73.9%` |

---

## 4. Trả lời 5 Câu hỏi Đánh giá Stage 7

1. **Baseline và B1+A1 có giữ nguyên Top-10 không?** **Có — tuyệt đối 100% (`6/6` graph, `18,000/18,000` queries):** `0` sai khác về ordered top-10 IDs và `0` sai khác về `squared_l2`.
2. **Có `ΔRecall` khác `0` không?** **Không:** `paired ΔRecall = 0.000000` trên mọi graph và `0/18,000` query có `ΔRecall != 0`.
3. **Có graph nào không đạt quality floor đã đăng ký không?**
   - **Point floor (`>= 0.990`):** **Không graph nào trượt** (`12/12` đạt `0.990633 .. 0.991667`; trung bình cohort 6 graph = `0.991039`).
   - **Nominal `LCB95` (mô tả trên `N=3,000`):** `4/6` graph (`stock_r2: 0.989761`, `stock_r3: 0.989601`, `fast_r1: 0.989613`, `fast_r3: 0.989345`) và cohort fixed `LCB95` (`0.989878`) ở dưới `0.990` do `SE` ở `N=3,000` rộng gần gấp đôi `val_10k`.
   - **Cross-graph matching span (`<= 0.0001` — cổng bắt buộc trong prereg):** **TRƯỢT RÕ RỆT.** Quan sát `max - min = 0.991667 (stock_r1) - 0.990633 (fast_r3) = 0.001033` (`31` hits / `30,000`, vượt ngưỡng `0.0001` tới **`10.3×`**; paired `SE(stock_r1 - fast_r3) = 0.000393`, `95% CI = [+0.000264, +0.001803]`, `z = +2.63`). Trong khi đó chênh trung bình giữa hai arm không có ý nghĩa thống kê (`Stock_avg 0.991156 - Fast_avg 0.990922 = +0.000233`, paired `SE = 0.000160`, `95% CI = [-0.000080, +0.000547]`, `z = +1.46`).
4. **Có bất kỳ counter invariant nào bị vi phạm không?** **Không (`6/6` PASS):** mọi bất biến nội bộ (`de = uniq + dup`, `exp = uniq + dup`, `de + seen = nbr + 1`) và bất biến ghép cặp `base vs B1+A1` (`resume.invariant(..., True)`) đều đạt 100% trên toàn bộ `18,000` cặp query.
5. **Kết quả có khác đáng kể so với validation (`val_10k`) không?**
   - **Từng graph riêng lẻ:** **Không khác biệt có ý nghĩa thống kê** — tất cả 6 graph có `|z| <= 0.86` so với `val_10k`: `stock_r1 (+0.000397, z=+0.55)`, `stock_r2 (-0.000273, z=-0.38)`, `stock_r3 (-0.000447, z=-0.62)`, `fast_r1 (-0.000420, z=-0.57)`, `fast_r2 (-0.000057, z=-0.08)`, `fast_r3 (-0.000637, z=-0.86)`.
   - **Về mặt hồi quy hậu chọn lọc (post-selection reversion):** `fast_off_r3` được chọn beam thấp nhất (`412`, thấp hơn `420` 8 đơn vị) do đạt điểm cao trên `val_10k` (`0.991270`), và khi sang `narrow_test_3000.ids` đã lùi mạnh nhất (`-0.000637` xuống `0.990633`), ngược chiều với `stock_off_r1` (`+0.000397` lên `0.991667`), phơi bày rõ rủi ro chọn beam riêng từng graph trên validation với ngưỡng test span quá hẹp (`0.0001` = chỉ `3` hits ở `N=3,000`, nhỏ hơn cả `1×` paired SE!).

---

## 5. Giới hạn Bắt buộc & Lý do Giữ **`QUALITY_HOLD`**

- `narrow_test_3000.ids` **đã từng dùng trong P1 và narrow B1+A1** và `public 100K` đã qua Task A -> toàn bộ kết quả mang nhãn **`EXPLORATORY_HOST_SPECIFIC`**, tuyệt đối không phải confirmatory unseen holdout.
- Tuân thủ nghiêm prereg đóng băng (`AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md` dòng 39): vì `span(test) = 0.001033 > 0.0001`, cổng Test Quality giữ **`QUALITY_HOLD`** (không sửa ngưỡng hồi tố, không retune beam trên test, không mở G2 OFF).
