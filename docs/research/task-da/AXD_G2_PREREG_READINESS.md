# A×D G2 · Prereg Readiness sau Validation Calibration

- **Current Status:** **`VALIDATION_QUALITY_READY_FOR_REVIEW`** *(G0 `PASS`, `G1_RUNTIME_PASS`, G2 Validation Calibration `54/54` baseline + `6/6` B1+A1 `COMPLETE_VALID` và `PASS`; Held-out Test 3k ON `NOT_RUN`, G2 OFF Performance **`NOT_OPEN`**).*
- **Scope:** **`EXPLORATORY_HOST_SPECIFIC`** (cohort cố định 6 graph R90 v1.3 trên `AMD Ryzen 5 PRO 4650U`, `p=2`, `S=16`, `jobs=1`, `CPU [0,2]`).
- **Links:** [Calibration Report](AXD_G2_VALIDATION_CALIBRATION_REPORT.md) · [Quality & Test Gate](AXD_G2_QUALITY_AND_TEST_GATE.md) · [Prereg đã khóa](AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md) · [Durable Evidence Bundle](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/BUNDLE.sha256).

---

## Bảng Trạng thái Các Cổng G2

| Điều kiện | Trạng thái | Bằng chứng xác minh |
|---|---|---|
| G0 Task A & static graph contract | **`PASS`** | Audit ngày 22/11 (`AXD_G1_COMPATIBILITY_AND_READINESS_AUDIT.md`) |
| G1: `6/6` original graph SHA, `229/229` G1 bundle & `23/23` frozen pins | **`PASS`** | Re-verified 100% sau calibration ([final_verification.json](../../../../artifact-evidence/axd-g2-validation-20261122-G81SkWjO/final_verification.json)) |
| Search source `f2cd634` & Release ELF `7a2685e5...` | **`PASS`** | Khớp SHA-256 trước/sau, `git diff` rỗng |
| G2 Baseline validation grid (`6 graph × 9 beam`, `val_10k`, `ON`) | **`PASS (54/54 COMPLETE_VALID)`** | `0` guard failure, `60/60` `observed_cpus == [0,2]`, `Tctl 67.6–91.4°C` |
| G2 Frozen beam selection (`LCB95 >= 0.990`, `span <= 0.0001`) | **`PASS`** | `5` bộ hợp lệ; chọn duy nhất **`(420, 420, 420, 420, 416, 412)`** (`span = 0.00008`, `LCB95 ∈ [0.990542, 0.990640]`) |
| G2 B1+A1 validation paired parity & logical counters (`val_10k`) | **`PASS (6/6 COMPLETE_VALID)`** | `60,000/60,000` queries exact ordered top-10 + `L2²`, `ΔRecall = 0`, `replay_quality.py` PASS |
| Durable backup & checksum verification (`/tmp` giữ nguyên) | **`PASS`** | `558/558` byte-identical copy + `562/562` `BUNDLE.sha256` (`82e740bc...`) |
| G2 Held-out `narrow_test_3000.ids` Quality Check (`12` ON runs) | **`NOT_RUN`** | Chờ owner review & phê duyệt riêng; panel đã reuse lịch sử (`EXPLORATORY`) |
| G2 Paired OFF Latency Benchmark (`60` OFF runs) | **`NOT_OPEN`** | Cần Test Quality PASS và owner phê duyệt riêng |
| Historical P0 / Full P1 / `t0998` / P3 official / V4 D1–D5 / H3 TP-CG | **`HOLD / CLOSED / NOT_OPENED`** | Giữ nguyên trạng thái lịch sử |

---

## Tóm tắt Điều kiện Đề xuất Bước Tiếp theo

- **Đủ điều kiện để đề xuất review mở pha Test Quality ON (`12` tiến trình trên `narrow_test_3000.ids`)** với đúng bộ beam khóa `(420, 420, 420, 420, 416, 412)` và phạm vi **`EXPLORATORY_HOST_SPECIFIC`**.
- **Chưa đủ điều kiện mở G2 OFF performance hoặc kết luận confirmatory:** (i) chưa chạy kiểm tra chất lượng trên `narrow_test_3000.ids`, (ii) `LCB95` trên `val_10k` mang tính post-selection calibration, (iii) `narrow_test_3000.ids` đã từng dùng trong P1/narrow B1+A1 và `public 100K` đã được Task A đánh giá, và (iv) `independent-root population CI = NOT_ESTIMABLE` (`root independence NOT_VERIFIED`).
