# Task D × Task A — Intel Core i5-14600KF Replication Protocol & Checklist

- **Execution Status on Current Host (`thinhbui-linux`, AMD Ryzen 5 PRO 4650U):** **`NOT_RUN`** *(Không có quyền truy cập máy `i5-14600KF` trong môi trường hiện tại; tài liệu này xuất sẵn protocol, checklist, runner và lệnh chạy tái lập.)*
- **Runner Script:** [run_i5_14600kf_replication.py](../../../research/task_da/run_i5_14600kf_replication.py) *(đã kiểm chứng `--dry-run` xác minh `17/17` SHA-256 input, kiểm chứng bộ phân tích hybrid sysfs giả lập `i5-14600KF`, và kiểm chứng fail-closed từ chối chạy trên CPU khác `i5-14600KF`).*
- **Baseline Anchor:** [STAGE_D_E_REPLICATION_AND_H3_DECISION.md](STAGE_D_E_REPLICATION_AND_H3_DECISION.md) (`PROTOCOL_V4_1_P2_EXPLORATORY_0990`, `Recall@10 >= 0.990`).
- **Preserved Gates:** `Historical P0 = HOLD`, `Full P1 = HOLD`, `t0998 = HOLD`, `Protocol V4 D1–D5 = UNAPPROVED`, `P3 Official = CLOSED`, `TP-CG / H3 = NOT_OPENED`.

---

## 1. Kiến trúc Hybrid & Quy tắc CPU Affinity (Bắt buộc P-cores vật lý)

Intel Core `i5-14600KF` (Raptor Lake Refresh) có **6 P-cores (12 logical threads)** + **8 E-cores (8 logical threads)** = 20 logical CPUs. Để không làm nhiễu speedup bởi chênh lệch IPC/cache giữa P-core và E-core hoặc tranh chấp SMT/Hyper-Threading:

1. **Tự động phát hiện P-cores qua Linux sysfs (read-only, không dùng `sudo`):**
   - Đọc `/sys/devices/cpu_core/cpus` (tập logical CPUs thuộc P-cores, thường `0-11`) và `/sys/devices/cpu_atom/cpus` (tập E-cores, thường `12-19`).
   - Đọc `/sys/devices/system/cpu/cpu*/topology/thread_siblings_list` để nhóm từng cặp HT sibling và **chỉ chọn sibling đầu tiên (ID nhỏ nhất) của 4 P-core vật lý khác nhau** (thường `[0, 2, 4, 6]`).
2. **Quy tắc pin cho `p ∈ {1, 2, 4}`:**
   - `p = 1`: `[pcore_0]`
   - `p = 2`: `[pcore_0, pcore_1]`
   - `p = 4`: `[pcore_0, pcore_1, pcore_2, pcore_3]`
   - **Cấm tuyệt đối:** Không pin vào bất kỳ CPU nào thuộc `cpu_atom/cpus` (E-cores) và không đặt 2 worker trên cùng một P-core vật lý. Runner kiểm tra `observed_cpus == requested_cpus` sau mỗi lượt chạy và fail-closed nếu sai lệch.

---

## 2. Telemetry Nhiệt độ & Xung nhịp (Read-Only, Không `sudo`)

Trước và sau mỗi lượt lặp (`pre` và `post`), runner tự ghi `host_telemetry.json` từ các tệp chỉ-đọc:
- Nhiệt độ gói và từng core từ `/sys/class/hwmon/hwmon*/temp*_input` (`coretemp`).
- Xung nhịp hiện hành `/sys/devices/system/cpu/cpu<id>/cpufreq/scaling_cur_freq` và `scaling_governor`.
- `loadavg_1m`, `hostname`, `platform`, `cpu_model`.
- **Nguyên tắc an toàn (`AGENTS.md`):** Không gọi `sudo`, không đổi governor/turbo/fan/power limit, không tắt ASLR, không loại bỏ lượt chạy chậm (`never discard slow runs`).

---

## 3. Khóa Tập Dữ liệu, Đồ thị, Cấu hình & Quy tắc Không Trộn Máy

1. **Cùng ngữ nghĩa thuật toán & cùng input bất biến (`17` tệp kiểm SHA-256 trước khi chạy):**
   - Dataset `MSTuring_1M_v1`: `base.1M.fbin` (`44e83e1d...`), `query.public.100K.fbin` (`48d087a1...`), `groundtruth.public.100K.ibin` (`fa5acf5a...`).
   - Split: `val_10k.ids` (`a3c948e9...`), `test_90k.ids` (`af871517...`).
   - 9 đồ thị `A0/A1/A3 × r1..r3`: khớp đúng 9 SHA-256 khóa trong `run_i5_14600kf_replication.py`.
   - Manifest 45 ô `val_10k` đã đóng băng: `stage_d_val10k_45cells_manifest.json` (`SHA-256: f98c0454...`).
   - **Không hiệu chỉnh lại beam trên máy `i5-14600KF`:** Thuật toán xác định (`set` và `flat` đều deterministic từng bit), nên Recall và bộ beam đã khóa từ `val_10k` hoàn toàn độc lập phần cứng.
2. **Ma trận chạy:** Đúng `63` ô (`A0/A1/A3 × R1/R2/R3` × `{p1_base, p2_S8_set, p2_S8_flat, p2_S16_flat, p4_S8_set, p4_S8_flat, p4_S16_flat}`) × **`5` interleaved `OFF` repeats** (đảo thứ tự giữa các repeat block) + **`1` `ON` diagnostic riêng** (`378` lượt tuần tự, `--jobs 1`).
3. **Tùy chọn loại bỏ query-reuse bias (tách thư mục riêng):**
   - **Run 1 (Direct Cross-Host Replication):** Dùng đúng `pilot_test_3000.ids` (`SHA-256: 18d8b901...`) để so sánh định tính xu hướng trên cùng tập query với `Ryzen 5 PRO 4650U`.
   - **Run 2 (Tùy chọn, thư mục đầu ra riêng với `--disjoint-test-ids`):** Dùng `3,000` (hoặc nhiều hơn) query rời rạc hoàn toàn từ `87,000` query còn lại của `test_90k.ids` để kiểm tra chọn `best S` không bị selection bias từ tập pilot cũ.
4. **Cấm trộn dữ liệu liên máy:** Không bao giờ ghép `latency_us`, `QPS` hoặc `speedup` của `i5-14600KF` vào bảng trung bình hoặc CI95 của `Ryzen 5 PRO 4650U`. Mỗi máy xuất thư mục evidence và bảng outer `n=3` Student-$t_{df=2}$ CI95 độc lập.

---

## 4. Checklist Trước khi Chạy trên máy `i5-14600KF`

- [ ] Kiểm tra `git rev-parse HEAD` và trạng thái source khớp đúng bản freeze của Stage D (`p2_engine.hpp`, `p2_eval.cpp`, `CMakeLists.txt`).
- [ ] Build sạch Release (`build-task-da-i5`) và ASan+UBSan+LSan (`build-task-da-i5-asan`) trên chính máy `i5-14600KF` (ghi lại `g++ --version` và `sha256sum` của binary mới).
- [ ] Chạy `ctest --test-dir build-task-da-i5 -V` và `ctest --test-dir build-task-da-i5-asan -V` đạt `24/24 OK`.
- [ ] Xác nhận máy đang rảnh (`loadavg < 0.5`), không chạy tác vụ CPU nặng song song, không có tiến trình `task_da_p2_eval` khác đang chạy.
- [ ] Chạy `--dry-run` xác nhận `is_i5_14600kf: true`, `selected_4_physical_pcores` đúng 4 P-core vật lý, và `verified_inputs_count: 17`.
- [ ] Lưu toàn bộ output vào thư mục ngoài repo (ví dụ `../artifact-evidence/p2-i5-14600kf-<YYYYMMDD>/`) để không đưa dữ liệu thô vào git.

---

## 5. Lệnh Build, Preflight và Thực thi trên máy `i5-14600KF`

```bash
# 1. Build Release + ASan trên máy i5-14600KF (từ thư mục repo task-d)
cmake -S research/task_da -B build-task-da-i5 -DCMAKE_BUILD_TYPE=Release
cmake --build build-task-da-i5 -j4
ctest --test-dir build-task-da-i5 -V

cmake -S research/task_da -B build-task-da-i5-asan -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -fno-omit-frame-pointer"
cmake --build build-task-da-i5-asan -j4
ctest --test-dir build-task-da-i5-asan -V

# 2. Preflight (xác minh 4 P-cores vật lý + 17/17 SHA-256 input, chưa chạy benchmark)
python3 research/task_da/run_i5_14600kf_replication.py \
  --binary build-task-da-i5/task_da_p2_eval \
  --graph-root "/path/to/graph" \
  --v3-split-dir "/path/to/p1-full-validation-20261117T225717+0700/split" \
  --val10k-manifest "/path/to/p2-followup-20261118/stage_d_val10k_r2_r3/stage_d_val10k_45cells_manifest.json" \
  --pilot-ids "/path/to/p2-exploratory-0990-20261118/pilot_r1/pilot_test_3000.ids" \
  --warmup-ids "/path/to/p2-exploratory-0990-20261118/pilot_r1/warmup_val_100.ids" \
  --out-dir "../artifact-evidence/p2-i5-14600kf-replication" \
  --dry-run

# 3. Thực thi tuần tự Stage D Replication trên i5-14600KF (chỉ chạy sau khi Preflight PASS)
python3 -u research/task_da/run_i5_14600kf_replication.py \
  --binary build-task-da-i5/task_da_p2_eval \
  --graph-root "/path/to/graph" \
  --v3-split-dir "/path/to/p1-full-validation-20261117T225717+0700/split" \
  --val10k-manifest "/path/to/p2-followup-20261118/stage_d_val10k_r2_r3/stage_d_val10k_45cells_manifest.json" \
  --pilot-ids "/path/to/p2-exploratory-0990-20261118/pilot_r1/pilot_test_3000.ids" \
  --warmup-ids "/path/to/p2-exploratory-0990-20261118/pilot_r1/warmup_val_100.ids" \
  --out-dir "../artifact-evidence/p2-i5-14600kf-replication" \
  --repeats 5 \
  --resume
```
