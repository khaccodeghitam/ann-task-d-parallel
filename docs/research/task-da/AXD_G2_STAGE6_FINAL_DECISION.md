# A×D G2 · Stage 6 Final Decision

- **Official Conclusion:** **`QUALITY_HOLD`**
- **Scope:** **`EXPLORATORY_HOST_SPECIFIC`** (`AMD Ryzen 5 PRO 4650U`, 6 original R90 v1.3 graphs, `p=2`, `S=16`, `narrow_test_3000.ids` đã reuse lịch sử; **không** tự mở G2 OFF; **không** gọi là fresh untouched holdout).
- **Evidence Index:**
  - Stage 5 Validation Calibration (`54` base + `6` B1+A1, `562` files): [BUNDLE.sha256](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/BUNDLE.sha256) (`82e740bc...`) · [AXD_G2_VALIDATION_CALIBRATION_REPORT.md](AXD_G2_VALIDATION_CALIBRATION_REPORT.md)
  - Stage 6 Test Quality ON (`12` runs, `101` files): [BUNDLE.sha256](../../../../artifact-evidence/axd-g2-stage6-test-quality-20261123/BUNDLE.sha256) (`cd65a8ac...`) · [AXD_G2_TEST_QUALITY_REPORT.md](AXD_G2_TEST_QUALITY_REPORT.md)
  - Stage 8 OFF Pilot Plan (`NOT_OPEN`): [AXD_G2_OFF_PILOT_PREREG_REVIEW.md](AXD_G2_OFF_PILOT_PREREG_REVIEW.md)

---

## 1. Tóm tắt Quyết định & Bằng chứng Phân tách

| Hạng mục kiểm tra (`narrow_test_3000.ids`, `N = 3,000`) | Tiêu chuẩn Prereg đóng băng | Kết quả quan sát | Trạng thái |
|---|---|---|---|
| Provenance, 6 graph SHA, ELF `7a2685e5...`, `562/562` Stage 5 bundle | Khớp 100% trước/sau | Khớp 100% (3 báo cáo Stage 5 untracked `??` tại `HEAD=f54b1bb`) | **`PASS`** |
| Execution & Ryzen Guard (`12` ON runs, `0` OFF) | `exit=0`, `0` guard failure, `CPU [0,2]` | `12/12` `exit=0`, `0` guard failure, `Tctl 58.1–83.8°C` | **`PASS`** |
| Point Recall Floor từng graph × policy | `Recall@10 >= 0.990` | `12/12 >= 0.990` (`0.990633 .. 0.991667`, mean `0.991039`) | **`PASS`** |
| Within-graph Parity (`baseline` vs `B1+A1`) | Ordered top-10 & `L2²` khớp tuyệt đối, `ΔRecall = 0` | **`0/18,000` sai khác**, `ΔRecall = 0.000000` trên mọi query | **`PASS`** |
| Logical Counter Invariants (`ON`) | Toàn bộ accounting & B1/A1 invariants PASS | **`6/6` PASS** (`dup_L2/q` giảm `73.9%–74.7%`) | **`PASS`** |
| **Cross-graph Matching Span trên `test3k`** | **`span(point) <= 0.0001`** (`<= 3` hits / `30,000`) | **`0.001033`** (`31` hits: `stock_r1 0.991667` vs `fast_r3 0.990633`) | **`FAIL -> QUALITY_HOLD`** |
| Nominal `LCB95` trên `test3k` (mô tả, `N=3,000`) | Báo cáo minh bạch (không phải cổng cứng test) | `2/6` `>= 0.990`, `4/6` `< 0.990` (`0.989345 .. 0.990435`); cohort `0.989878` | **`REPORTED`** |

---

## 2. Lý do Chọn **`QUALITY_HOLD`** (Không Chọn `READY_FOR_OFF_PILOT_REVIEW`)

1. Prereg đã khóa tại [AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md](AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md) (dòng 39) quy định tường minh: *"Mọi graph phải có point test≥0,990, span giữa sáu graph≤0,0001 và exact parity trong graph. ... Quality trượt giữ HOLD và bảo toàn kết quả."*
2. Dù **within-graph parity (`base` vs `B1+A1`) hoàn hảo tuyệt đối (`ΔRecall = 0`)** và **từng graph không lệch có ý nghĩa so với `val_10k` (`|z| <= 0.86`)**, khoảng `span = 0.001033` trên `narrow_test_3000.ids` vượt giới hạn `0.0001` hơn `10×` (phản ánh đồng thời phương sai mẫu ở `N=3,000` với paired `SE = 0.000393` và hiệu ứng hồi quy hậu chọn lọc ở `fast_off_r3 beam=412`).
3. Theo kỷ luật nghiên cứu (`AGENTS.md`), **tuyệt đối không tự sửa ngưỡng hồi tố, không retune beam trên `narrow_test_3000.ids`, và không tự động chuyển sang G2 OFF.**

---

## 3. Khuyến nghị Hành động Chờ Owner Quyết định

1. **Freeze Git (tùy chọn của owner):** Commit các báo cáo `AXD_G1_*` và `AXD_G2_*` trên nhánh `research/task-da-pivot-b1-a1-20261119` để chính thức track toàn bộ chuỗi G1–Stage 6 trong Git (chưa tự commit/merge).
2. **Quyết định đối với G2 OFF Pilot:** Xem 3 phương án trong [AXD_G2_OFF_PILOT_PREREG_REVIEW.md](AXD_G2_OFF_PILOT_PREREG_REVIEW.md) Mục 1 (giữ `QUALITY_HOLD`, hoặc ban hành Prereg Amendment v1.1 khoanh phạm vi OFF chính vào within-graph `B1+A1 vs baseline` nơi `ΔRecall = 0` tuyệt đối, hoặc đánh giá lại với ngưỡng span / panel unseen mới qua prereg riêng).
3. **Các giới hạn & cổng giữ nguyên không đổi:**
   - `G2 OFF Latency Benchmark = NOT_OPEN`; `i5-14600KF = NOT_RUN`; `10M = NOT_RUN`; `H3/TP-CG = NOT_OPENED`; `Historical P0 / Full P1 / t0998 / B1+A1 official = HOLD`; `P3 official = CLOSED`; `Protocol V4 D1–D5 = UNAPPROVED`.
   - **Google Sheets:** Không sửa Google Sheets Task A; không có công cụ/quyền truy cập Google Sheets API trong phiên này nên cập nhật Google Sheets Task D ở trạng thái `NOT_EXECUTED_NO_TOOL_ACCESS` (dữ liệu sẵn sàng điền từ bảng Stage 7 ở [AXD_G2_TEST_QUALITY_REPORT.md](AXD_G2_TEST_QUALITY_REPORT.md)).
