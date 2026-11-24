# A×D G2 · Quality and Test Gate

- **Gate Verdict:** **`VALIDATION_QUALITY_READY_FOR_REVIEW`** *(máy ghi trong `result.json`: `READY_FOR_HELDOUT_QUALITY_CHECK`; phạm vi: **`EXPLORATORY_HOST_SPECIFIC`**; `test_executions = 0`, `OFF_executions = 0`, `G2 OFF performance = NOT_OPEN`).*
- **Reference Calibration Report:** [AXD_G2_VALIDATION_CALIBRATION_REPORT.md](AXD_G2_VALIDATION_CALIBRATION_REPORT.md) · [Prereg đã khóa](AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md) · [G2 Readiness](AXD_G2_PREREG_READINESS.md).

---

## 1. Bộ Beam Khóa Sau Validation Calibration (`val_10k` ONLY)

Bộ beam sau đây được khóa cố định cho **cả hai policy** (`baseline`: `flat, baseline/full` và `B1+A1`: `flat, barrier_all_evaled/incremental`) tại `p=2`, `S=16`, `jobs=1`, `entry=0`, `K=10`, `CPU [0,2]`:

| Graph (R90 v1.3 original) | Graph SHA-256 | Beam khóa | Validation `Recall@10` (`base == B1+A1`) | Validation `LCB95` (`base == B1+A1`) | Parity `base vs B1+A1` (`10,000` queries) |
|---|---|---:|---:|---:|---|
| `MS-Turing1M_stock_off_r1.graph` | `db4f5257...9716cc` | **`420`** | `0.991270` | `0.990583` | `EXACT (ΔRecall = 0)` |
| `MS-Turing1M_stock_off_r2.graph` | `5de325e9...0ae84` | **`420`** | `0.991240` | `0.990542` | `EXACT (ΔRecall = 0)` |
| `MS-Turing1M_stock_off_r3.graph` | `a7eb1ad1...bd010` | **`420`** | `0.991280` | `0.990586` | `EXACT (ΔRecall = 0)` |
| `MS-Turing1M_fast_off_r1.graph` | `104a1bc6...354e9` | **`420`** | `0.991320` | `0.990640` | `EXACT (ΔRecall = 0)` |
| `MS-Turing1M_fast_off_r2.graph` | `4b69a53c...1731a` | **`416`** | `0.991290` | `0.990606` | `EXACT (ΔRecall = 0)` |
| `MS-Turing1M_fast_off_r3.graph` | `7c80157e...a0462` | **`412`** | `0.991270` | `0.990586` | `EXACT (ΔRecall = 0)` |

- **Matching trên `val_10k`:** `span = 0.00008 <= 0.0001` (`max_dev_from_0.9913 = 0.00006`); cohort fixed-6-graph `mean = 0.991278`, `query_SE = 0.00032577`, `nominal LCB95 = 0.990640`.

---

## 2. Minh bạch Provenance & Lịch sử Tái sử dụng Panel Test (`narrow_test_3000.ids`)

Kiểm toán tại [split_and_reuse_audit.json](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/split_and_reuse_audit.json):
- `val_10k.ids` (`a3c948e9...`, `10,000` queries) và `narrow_test_3000.ids` (`77fda031...`, `3,000` queries) có **`overlap_ids = 0`**; `narrow_test_3000.ids` hoàn toàn không được chạy trong lượt calibration hiện tại (`test_executions = 0`).
- **Cảnh báo tái sử dụng bắt buộc:** Cả `3,000` query của `narrow_test_3000.ids` **đã từng được dùng trong P1 và nghiên cứu narrow B1+A1 trước đó**, và toàn bộ `public 100K` **đã được Task A đánh giá**. Vì vậy:
  - **Không được gọi `narrow_test_3000.ids` là fresh untouched holdout.**
  - Kết quả đánh giá test tiếp theo chỉ mang giá trị **`EXPLORATORY_HOST_SPECIFIC`**, không đủ cơ sở cho chứng nhận chất lượng confirmatory trên query unseen.
  - Suy luận quần thể independent-root là **`NOT_ESTIMABLE`** (`root independence NOT_VERIFIED` — 6 graph thuộc cohort cố định với cùng seed gốc 555).

---

## 3. Điều kiện Mở & Đóng cho Bước Đánh giá Tiếp theo (Chưa tự động chạy)

1. **Bước tiếp theo đề xuất (chỉ khi owner phê duyệt riêng):** Chạy **12 tiến trình `ON`** trên `narrow_test_3000.ids` (`6 graph × 2 policy`) với đúng 6 beam khóa ở Mục 1 và đúng ELF `7a2685e5...`.
2. **Ngưỡng PASS bắt buộc của pha Test Quality ON (`narrow_test_3000.ids`):**
   - Mỗi graph (cả `base` và `B1+A1`) đạt point `Recall@10 >= 0.990` (báo thêm `nominal LCB95` và paired `ΔRecall` theo query; giữ nguyên quy tắc prereg không tự sửa ngưỡng).
   - `span(point)` giữa 6 graph `<= 0.0001`.
   - `Exact ordered top-10 IDs` và `squared_l2` khớp tuyệt đối giữa `base` và `B1+A1` trên `3,000/3,000` query/graph, `10` ID duy nhất/query, và qua toàn bộ logical counter invariants + guard Ryzen.
3. **Quy tắc dừng & Cấm retune:**
   - Nếu bất kỳ graph/policy nào trượt point floor `0.990`, trượt `span <= 0.0001`, hoặc sai parity/invariant/guard -> **dừng ngay ở `HOLD_QUALITY`**, lưu toàn bộ raw và **không dùng kết quả test để chỉnh beam, S, policy hay panel**.
   - **Không tự động chuyển `VALIDATION_QUALITY_READY_FOR_REVIEW` thành `G2 PERFORMANCE GO`.** Pha `60` tiến trình `OFF` paired latency chỉ được mở sau khi (i) pha Test Quality ON đạt PASS và (ii) owner phê duyệt riêng chiến dịch OFF.
4. **Các cổng lịch sử giữ nguyên không đổi:** `Historical P0 = HOLD`, `Full P1 = HOLD`, `Target 0.998 (t0998) = CLOSED/HOLD`, `B1+A1 official = HOLD`, `P3 official = CLOSED`, `Protocol V4 D1–D5 = UNAPPROVED`, `H3/TP-CG = NOT_OPENED`, `10M = NOT_RUN`, `i5-14600KF = NOT_RUN`.
