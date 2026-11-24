# A×D G2 · Paired OFF Latency Pilot Preregistration Review (`DO NOT EXECUTE`)

- **Execution Status:** **`NOT_OPEN / BLOCKED_BY_STAGE6_QUALITY_HOLD`** *(Tài liệu chuẩn bị kế hoạch & kiểm soát prereg cho Stage 8 theo yêu cầu owner; **CHƯA thực thi bất kỳ lượt OFF benchmark nào**, `OFF_executions = 0`).*
- **Prerequisite Audit:** [Stage 6 Test Quality Report](AXD_G2_TEST_QUALITY_REPORT.md) · [Stage 6 Final Decision](AXD_G2_STAGE6_FINAL_DECISION.md) · [Locked Prereg](AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md).

---

## 1. Blocker Hiện tại Cần Owner Quyết định Trước khi Mở OFF Pilot

Stage 6 trên `narrow_test_3000.ids` cho kết quả **phân tách rất rõ giữa hai cấp độ kiểm tra**:
- **Đạt 100% ở cấp độ trong cùng graph (`within-graph`):** `baseline` vs `B1+A1` đạt **exact ordered top-10 & `squared_l2` parity (`ΔRecall = 0` trên `18,000/18,000` queries)**, `6/6` counter invariants `PASS`, `12/12` point `Recall@10 >= 0.990633 >= 0.990`, `0` guard failure.
- **Trượt cổng cứng ở cấp độ liên graph (`cross-graph`):** `span(test)` giữa 6 graph = **`0.001033`** (`31` hits / `30,000`, `stock_r1 = 0.991667` vs `fast_r3 = 0.990633`) vượt giới hạn `0.0001` (`3` hits) của prereg hiện hành -> giữ **`QUALITY_HOLD`**.

**Vì vậy, trước khi owner phê duyệt chạy G2 OFF pilot, cần chọn rõ một trong ba phương án (không tự nới ngưỡng):**
1. **Phương án 1 — Giữ `QUALITY_HOLD`, không mở G2 OFF** ở thiết kế hiện tại (an toàn tối đa nếu mục tiêu đòi hỏi cross-graph test span `<= 0.0001` trên `3,000` query).
2. **Phương án 2 — Tu chính prereg chính thức (`Prereg Amendment v1.1`) thu hẹp endpoint OFF về within-graph `B1+A1 vs baseline` trước khi chạy OFF:** Bởi vì trong cùng graph (`Stock r1..r3`, `Fast r1..r3`), `base` và `B1+A1` khớp từng bit (`ΔRecall = 0` tuyệt đối trên cả `val_10k` lẫn `narrow_test_3000.ids`), endpoint chính *"B1+A1 có giảm OFF latency trên từng graph Fast/Stock tại exact matched Recall không?"* không chịu sai lệch cross-graph span; còn so sánh liên-arm `Stock vs Fast` được gắn nhãn phụ trợ kèm ghi nhận chênh `Stock_avg - Fast_avg = +0.000233` (`95% CI [-0.000080, +0.000547]`).
3. **Phương án 3 — Giữ nguyên so sánh liên-arm nhưng đăng ký lại test span hợp lý theo phương sai mẫu `N` (hoặc chạy trên panel unseen mới độc lập lớn hơn)** qua một prereg amendment riêng trước mọi lượt đo mới.

---

## 2. Thiết kế Kế hoạch Paired OFF Latency Pilot (Chờ Owner Phê duyệt — KHÔNG CHẠY)

Nếu và chỉ nếu owner phê duyệt bằng văn bản một phương án tháo gỡ `QUALITY_HOLD` ở Mục 1, chiến dịch G2 OFF sẽ tuân thủ chặt cấu hình sau:

### 2.1 Ma trận, Chủ thể & Thông số Khóa
- **Cohort & Arms:** `6` original R90 v1.3 graphs (`MS-Turing1M_{stock,fast}_off_r{1,2,3}.graph`, khớp đúng 6 SHA-256) × `2` policies:
  - `D-base`: `--merge-impl flat --visited-policy baseline --frontier-mode full`
  - `D-opt (B1+A1)`: `--merge-impl flat --visited-policy barrier_all_evaled --frontier-mode incremental`
- **Beams khóa từ validation (không retune trên test):** `Stock r1/r2/r3 = 420/420/420`; `Fast r1 = 420`, `Fast r2 = 416`, `Fast r3 = 412`.
- **Tham số search:** `p = 2`, `S = 16`, `jobs = 1`, `entry = 0`, `K = 10`, `metric = squared L2 double trên FP32 gốc`, Release ELF SHA-256 `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1` (nguồn đóng băng `f2cd634`).
- **Query & Warmup:** `100` warmup (`warmup_val_100.ids`, `199ca606...`) + `3,000` test queries (`narrow_test_3000.ids`, `77fda031...`), **`--mode OFF`** (tắt toàn bộ đồng hồ nội bộ và bộ đếm ON). **Gắn nhãn `EXPLORATORY_HOST_SPECIFIC`** (không gọi là unseen confirmatory).

### 2.2 Số lần lặp, Thứ tự Ghép cặp & Kiểm soát Nhiệt/Tài nguyên
- **Số lần lặp (`60` tiến trình OFF tuần tự):** `5` blocks (`b = 0..4`) × `6` graph pairs (`base` + `opt`) = **`60` OFF processes** (`180,000` scored query executions + `6,000` warmups; dự kiến wall ~`15–20 phút` tổng kể cả cooldown, nằm xa dưới quota `3 giờ`).
- **Thứ tự xoay vòng chống trôi nhiệt (theo đúng prereg dòng 41):**
  - Danh sách gốc `G = [Stock1, Fast1, Stock2, Fast2, Stock3, Fast3]` (`i = 0..5`).
  - Block `b = 0..4` xoay trái `G` đi `b` vị trí.
  - Trong từng cặp của graph có chỉ số gốc `i`: chạy `base` trước `opt` khi `(b + i)` chẵn, và chạy `opt` trước `base` khi `(b + i)` lẻ.
- **CPU Affinity & Host Guard:**
  - Host: `AMD Ryzen 5 PRO 4650U`, pin `--cpu-list 0,2` (2 core vật lý dùng chung L3, `MKL_NUM_THREADS=1`), xác minh `requested_cpus == observed_cpus == [0, 2]` ở mọi receipt.
  - Khóa độc quyền `/tmp/task-da-pivot-4650u.lock`, dùng frozen `RyzenGuard` (`run_paper_fullfan_check.py` `232ed904...` + `resume.py` `0cf76c6e...`): preflight fail-closed kiểm sensor + AC + RAM + disk + swap + foreign ANN process + watchdog; chỉ bắt đầu khi `Tctl < 85°C` (chờ cooldown tối đa `180s`), dừng khẩn cấp khi `Tctl >= 95°C`; timeout `180s/process`.
  - **Không loại bỏ lượt chạy chậm (`never discard slow runs`).**
- **Hậu kiểm Parity OFF vs ON bắt buộc:** Mỗi output JSONL của `60` lượt OFF phải khớp từng bit (`query_id`, ordered top-10 `ids`, `squared_l2`) với output `ON` tương ứng đã lưu trong Stage 6 ([axd-g2-stage6-test-quality-20261123](../../../../artifact-evidence/axd-g2-stage6-test-quality-20261123/)). Một lỗi parity hoặc guard sẽ dừng ngay chiến dịch, giữ `HOLD` và bảo toàn toàn bộ raw receipts.

### 2.3 Chỉ số Đo, Suy luận Thống kê & Tách biệt ON / BUILD–SEARCH
1. **Latency & QPS (thuần từ OFF mode):**
   - Trong từng process OFF: xuất `mean`, `p50`, `p95`, `p99` (từ per-query `latency_ns` theo định nghĩa nội suy tuyến tính của frozen evaluator) và `QPS_wall = queries / batch_wall_s` (kèm `jobs = 1`).
   - Báo speedup & giảm latency theo **từng graph** (`B_gb - C_gb`, `gain_% = 100 × (1 - C_gb / B_gb)`, `ratio_of_agg_means = mean(B_g)/mean(C_g)`, và 5 cặp `b = 0..4` kèm CI95 Student-$t_{df=4}$) và **theo từng policy/cohort** (mean đồng trọng số của 3 Fast và của 6 graph trong từng block -> CI95 Student-$t_{df=4}$ có điều kiện trên cohort cố định, panel và host; báo thêm range 3 graph; ghi rõ `independent-root population CI = NOT_ESTIMABLE`).
   - Tail endpoint trên Fast: `100 × (p95_opt / p95_base - 1)` theo từng graph & block (`df = 4`).
2. **Tách biệt ON Counters:** Toàn bộ công việc logic (`total/unique/duplicate L2`, `expansions`, `frontier_insertions`, `sync_merge_count`) giữ ở **evidence ON riêng của Stage 6**, không trộn vào phép đo OFF.
3. **Tách biệt BUILD / SEARCH Trade-off:**
   - Giữ `BUILD%` và `SEARCH%` là hai endpoint riêng biệt.
   - Dùng receipt BUILD chính xác của 6 SHA gốc (`Stock mean ≈ 42.2567 s`, `Fast mean ≈ 33.7933 s`, `ΔB ≈ 8.4633 s`), tính $T(Q) = \text{BUILD} + Q \times \text{mean\_OFF\_query}$ tại `Q = 1`, `Q0 = 100,000` và điểm hòa vốn dương (nếu có) giữa `Fast-opt` so với `Stock-base`, `Fast-base`, `Stock-opt`, ghi rõ đây là mô hình hai host (A dựng, D search; chi phí chuyển/nạp báo riêng).

---

## 3. Checklist Trước khi Trình Owner Phê duyệt OFF Pilot

- [ ] Owner quyết định bằng văn bản phương án xử lý `QUALITY_HOLD` (Phương án 1 / 2 / 3 tại Mục 1).
- [ ] Xác nhận giữ nguyên 6 graph R90 v1.3, 6 beam khóa, ELF `7a2685e5...`, và `narrow_test_3000.ids` (`EXPLORATORY_HOST_SPECIFIC`).
- [ ] Xác nhận lịch 5 block × 6 cặp (`60` OFF runs), CPU `[0, 2]`, guard `RyzenGuard` (`<85°C` start / `<95°C` abort) và quota `3 giờ`.
- [ ] Xác nhận không chạy đồng thời trên `i5-14600KF`, `10M`, không tạo graph mới, không mở `H3/TP-CG` và không sửa các gate lịch sử.
