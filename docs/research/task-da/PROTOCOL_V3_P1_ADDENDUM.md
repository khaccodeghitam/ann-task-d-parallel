# Task D × Task A — Protocol Addendum cho Full P1 Validation & Calibration

**Ngày hiệu lực:** 2026-11-17  
**Tài liệu nền giữ nguyên không sửa:** [PRE_REGISTRATION.md](PRE_REGISTRATION.md) (v1), [experiment_manifest.yaml](experiment_manifest.yaml), [PROTOCOL_V2.md](PROTOCOL_V2.md), [experiment_manifest_v3_reconciled.json](experiment_manifest_v3_reconciled.json), [P0_P1_FINAL_RECONCILIATION_REPORT.md](P0_P1_FINAL_RECONCILIATION_REPORT.md)  
**Thư mục evidence chiến dịch P1:** `artifact-evidence/p1-full-validation-20261117T225717+0700`

---

## 1. Phân Tách Query Quyết Định (`10,000` Validation / `90,000` Test)

- Quy tắc cố định theo [PRE_REGISTRATION.md](PRE_REGISTRATION.md): sắp xếp 100.000 query IDs `0..99999` theo thứ tự tăng dần của `SHA256(UTF-8 "task-da-v1:20261115:<decimal-id>")`.
  - **Tập validation (`10,000` queries):** `split/val_10k.ids` — SHA-256 `a3c948e9aac4f40c1fb818a6f784c4fbb56473a0769affe3344493ed4eb87f57`. Bao gồm `q=48571` (có khoảng cách GT phụ hạng 0 âm `-2.384e-7`) và `q=23741` (chứa node `840923` unreachable trên `A3-R2`).
  - **Tập test đóng băng (`90,000` queries):** `split/test_90k.ids` — SHA-256 `af871517d88aaad90549ba2fde0d4ed745f59400037a757f17bc93fa479bbfa3`. Bao gồm `q=45219, 95033` (GT phụ âm) và `q=47069, 66279, 89193` (`A3-R2` `840923`).
- **Kiểm tra phân tách:** không giao nhau (`0` trùng lặp), hợp lại đúng 100.000 IDs. Khóa sắp xếp `"task-da-v1:20261115:<decimal-id>"` thuộc riêng chiến dịch common-engine Task D, hoàn toàn tách biệt với `SEED = 555` lịch sử của builder.
- **Giới hạn holdout:** `query.public.100K.fbin` đã từng được Task A sử dụng trước đó; do đó `val_10k` / `test_90k` là **internal validation/test holdout của chiến dịch common-engine mới**, không phải dataset ngoại lai chưa từng nhìn thấy. Tuyệt đối không dùng `test_90k` để chọn beam hay điều chỉnh ngưỡng.

---

## 2. Hợp Đồng Thực Thi Common Engine & So Sánh Ngữ Nghĩa với Task A

- **Công cụ P1 phi-hiệu-năng:** `task_da_p1_eval` (biên dịch từ `research/task_da/search_common/p1_eval.cpp` dùng trực tiếp `task_da::Index` trong `research/task_da/search_common/engine.hpp` không chỉnh sửa thuật toán, giữ nguyên `task_da_smoke` 32-query).
  - Tham số thực thi P1 chuẩn: `format=pipnn`, `entry_point=0`, `k=10`, `workers=1` mỗi truy vấn (`entry_best_first_v1`).
  - Tham số `--jobs N` chỉ phân phối song song *giữa các truy vấn độc lập* trên vùng dữ liệu `const` trong phạm vi non-timing P1 validation (mỗi truy vấn chạy thuần 1 worker, ghi file theo đúng thứ tự `qids`, đã kiểm chứng khớp bit-exact với `--jobs 1`). Không dùng để đo hay tuyên bố hiệu năng/QPS P3.
- **Đối chiếu ngữ nghĩa với Task A (`beamSearch.h` + `euclidian_point.h` + `check_nn_recall.h`):**
  1. `task_da::Index` không cắt nhánh theo `QP.cut = 1.35` và không dồn lô `candidates.size() < beamSize/8` (`offset`) như `filtered_beam_search` của Task A.
  2. `task_da::Index` dùng mảng `seen` chính xác (0 va chạm) và lưu `seen[node]=1` cho mọi đỉnh đã từng khám phá, còn Task A dùng bảng băm `hash_filter` có thể va chạm.
  3. `task_da::Index` tích lũy `squared_l2` bằng `double` và phá hòa `(distance, id)` tăng dần; Task A tích lũy bằng `float`.
  4. Do đó, common-engine mới **không mặc định phải chọn cùng beam** với giá trị lịch sử của Task A (`384/896` cho `A0/A1`, `832/2176` cho `A3`).

---

## 3. Quy Tắc Đánh Giá GT, Lưới Beam & Lựa Chọn Đóng Băng

- **Metric & Validator:** `Recall@10` tính nghiêm ngặt theo ID membership trong `truth[:10]` của GT bất biến `groundtruth.public.100K.ibin` (`fa5acf5a...`). Kiểm tra bằng `research/task_da/evaluate_p1.py` (kế thừa validator `evaluate_smoke.py`) với opt-in `--gt-aux-min -1e-5` (giá trị mặc định vẫn là `0.0`). Mọi hàng kết quả phải hoàn thành kiểm tra không trùng ID, trong `[0, 1000000)`, không NaN/Inf, không âm, sắp xếp tăng theo `(squared_l2, id)`.
- **Mạng lưới beam & Giới hạn tối đa (`MAX_BEAM = 4096`):**
  - Bước lưới đăng ký: bước **`32`** với `beam <= 1024`, bước **`64`** với `1024 < beam <= 4096`, tối đa `4096`.
  - **Tiêu chí chọn beam trên `val_10k`:** Chọn **giá trị `beam` nhỏ nhất trên lưới đã đăng ký** sao cho `Recall@10(val_10k) >= target` (`0.990` hoặc `0.998`), và kiểm chứng điểm lưới liền kề nhỏ hơn trực tiếp (`beam - step`) cho `Recall@10(val_10k) < target` (đảm bảo tính nhỏ nhất thực sự; phá hòa theo `beam` nhỏ nhất).
  - Nếu một `(graph, target)` không đạt `target` tại `beam <= 4096`, ghi `FAIL / HOLD` — tuyệt đối không nâng `MAX_BEAM` hay hạ `target`.
- **Kiểm tra ON/OFF Parity & Ranh giới Gate:**
  - Thực hiện so sánh ON vs OFF cho mọi `(graph, selected_beam)` trên đủ `val_10k` và kiểm định parity trên `test_90k` (kiểm tra trùng khớp `ids`, `squared_l2`, `complete_top_k`, bất biến 5 counter ON, `counters=null` ở OFF).
  - Bảo toàn `P0 overall = HOLD`; giữ P2 và P3 `CLOSED` trong suốt addendum này cho đến khi được phép chuyển pha riêng.
