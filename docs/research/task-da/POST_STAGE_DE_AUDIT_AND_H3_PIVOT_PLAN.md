# Task D — Post Stage D/E Audit, Environment Verification & H3 PIVOT Preparation

- **Document Status:** **`AUDIT_COMPLETE_ENV_VERIFIED_PIVOT_DESIGNED_H3_HOLD`**
- **Anchor:** [STAGE_D_E_REPLICATION_AND_H3_DECISION.md](STAGE_D_E_REPLICATION_AND_H3_DECISION.md) & [P2_FOLLOWUP_CHECKPOINT_20261119.md](P2_FOLLOWUP_CHECKPOINT_20261119.md) (`COMPLETE_AT_STAGE_E_H3_PIVOT`).
- **Scope Guard:** Không triển khai TP-CG dynamic scheduling, không triển khai Ablation A/B vào C++ và không chạy benchmark lớn trước khi người phụ trách duyệt. Giữ nguyên: `Historical P0 = HOLD`, `Full P1 = HOLD`, `t0998 = HOLD`, `Protocol V4 D1–D5 = UNAPPROVED`, `P3 Official = CLOSED`, `TP-CG / H3 = NOT_OPENED`.

---

## 1. Giai đoạn 1 — Kiểm toán Toàn diện & Đề xuất Freeze (`COMPLETE`)

### 1.1 Xác minh Evidence, Checksums, Raw JSON/JSONL và Binary SHA-256
- **Evidence Checksums (`../artifact-evidence/p2-followup-20261118/EVIDENCE_CHECKSUMS.csv`):** Tái băm độc lập toàn bộ **`1,777 / 1,777`** tệp (`2,491.26 MiB`) -> `missing = 0`, `mismatches = 0`, `extra_unhashed = 0`.
- **Tệp bất biến & Baseline P1 (xác minh SHA-256 nguyên trạng, không bị sửa):**
  - `PRE_REGISTRATION.md` (`8290d116...`), `experiment_manifest.yaml` (`f73fe3b0...`), `PROTOCOL_V2.md` (`2dd08617...`), `PROTOCOL_V3_P1_ADDENDUM.md` (`c81d26cc...`), `P1_V4_APPROVAL_CHECKLIST.md` (`15a92ec1...`), `P1_FULL_GATE_DECISION.md` (`9f2d235b...`).
  - P1 engine gốc bất biến: `engine.hpp` (`2ca38624...`), `smoke.cpp` (`ff4ce1ea...`), `p1_eval.cpp` (`e5c15d0f...`).
  - Binary Stage D thống nhất: `build-task-da/task_da_p2_eval` (`ff46d6ac8895d519054548575c3187544716c0fdf2bbdad83db8a0a8cc7f8759`), `build-task-da-asan/task_da_p2_eval` (`6557fec319f9366d42560f56a6af480493428e731ef90df026f743b3d5494f67`).
  - Dataset `MSTuring_1M_v1` (`base`, `query`, `groundtruth`), splits (`val_10k.ids`, `test_90k.ids`), và toàn bộ 9 đồ thị `A0/A1/A3 × r1..r3` khớp 100% SHA-256 (`17/17` kiểm lại qua `run_i5_14600kf_replication.py --dry-run`).
- **Tái tính độc lập toàn bộ số liệu Stage D từ raw (`315 OFF` + `63 ON` tệp `p2_eval_summary.json` và raw `JSONL` so với `groundtruth.public.100K.ibin`):**
  - Metadata: `bad_meta = 0` (`315/315` `OFF` có `jobs == 1`, `mode == OFF`, `complete_top_k_count == 3000`, `observed_cpus` khớp chính xác `[0]`, `[0,2]`, `[0,2,4,6]`).
  - Sai khác tối đa so với `stage_d_replication_summary.json` & `STAGE_D_REPLICATION_SUMMARY.csv`: `max_diff_lat = 9.09e-13 us`, `max_diff_spd = 8.88e-16`, `max_diff_rec = 1.11e-16`, `max_csv_lat = 0.00`, `max_csv_spd = 0.00`.
  - **Tái tính Outer Replicate `n = 3` (`R1, R2, R3`, Student-$t_{df=2} = 4.30265$):** `max_ci_diff = 6.28e-12`, `max_contrast_diff = 6.68e-12`. Mỗi seed đồ thị là **1 đơn vị độc lập ngoài (outer replicate, `n=3`)**; 5 lượt lặp process `OFF` trong từng seed là **inner repeats (`n=5`)** để giảm nhiễu nhiệt trên từng đồ thị trước khi tổng hợp `n=3`.

### 1.2 Phân biệt 3 khái niệm Recall từ raw Stage D (Minh bạch sai số)

| Tầng chất lượng | Phạm vi đo | Kết quả định lượng quan sát (`OBSERVED`) | Ý nghĩa & Giới hạn |
|---|---|---|---|
| **1. Validation-matched Recall (`val_10k`)** | `10,000` queries, `45` ô hiệu chỉnh | `min = 0.99127`, `max = 0.99136`, **`span = 0.000090 <= 0.0001`**; **`45/45` đạt `LCB95_q >= 0.990`**. | Đạt tuyệt đối điều kiện khớp chất lượng trước khi đóng băng (không dùng test để retune). |
| **2. Test Recall Floor (`test_3000`)** | `3,000` queries held-out, `63` ô | Point estimate: **`63/63 >= 0.990`** (`0.99037 .. 0.99133`). Tuy nhiên **`59/63` ô có `test_3000 LCB95_q < 0.990`** (`min = 0.988835`, `max = 0.990081`). | `test_3000` chỉ đạt **exploratory point floor**, **KHÔNG** đạt LCB95 floor vì cỡ mẫu `3,000` có `1.96×SE ≈ 0.0012–0.0016`. Xác nhận chính thức cần `test_90k` (Protocol V4 vẫn `PENDING`). |
| **3. Test-quality Matching thực tế (`test_3000`)** | So sánh thực tế giữa `p=1,2,4` và giữa `A0/A1/A3` trên `test_3000` | Toàn cục `63` ô: `span = 0.00097` (`0.99037 .. 0.99133`). Trung bình theo arm: `A0` (`p1=0.99086`, `p4_S8=0.99110`, `p4-p1=+0.00024`), `A1` (`p1=0.99081`, `p4_S8=0.99122`, `p4-p1=+0.00041`), `A3` (`p1=0.99051`, `p4_S8=0.99064`, `p4-p1=+0.00013`). Within-seed span: `0.00007` (`A0_r1`) đến `0.00060` (`A0_r3`, `A1_r3`). | Trên tập held-out, `A3` lệch thấp hơn `A0/A1` khoảng `~0.00035–0.00058` do dịch chuyển phân phối `val->test`, còn `p=4` cao nhẹ hơn `p=1` (`+0.00013..+0.00041`). Không retune trên test để tránh rò rỉ dữ liệu, nhưng phải nêu rõ sai khác thực tế này khi diễn giải speedup. |

### 1.3 Kiểm tra Selection Bias khi chọn Best `(S, merge)` từ Pilot Stage C
1. **Kiểm chứng ngoài mẫu hạt giống (`R2, R3` chưa từng xuất hiện ở Stage C) và nhánh chưa thấy (`A1` không chạy ở Stage C):**
   - `flat - set @ S8` tái lập mạnh trên hạt giống chưa thấy `R2/R3` và nhánh `A1`:
     - `A0 p=4`: `r1 = +0.1162` vs `unseen r2,r3 mean = +0.1288` (`+0.1278, +0.1298`).
     - `A3 p=4`: `r1 = +0.3554` vs `unseen r2,r3 mean = +0.2696` (`+0.2907, +0.2485`).
     - `A1` (hoàn toàn ngoài mẫu Stage C): `p=2 unseen = +0.1157`, `p=4 unseen = +0.0918`.
   - Hiệu ứng `S16 - S8 @ flat` tái lập đúng chiều trên hạt giống ngoài mẫu:
     - `A0 p=4`: `r1 = -0.1776` vs `unseen r2,r3 = -0.1859`; `A1 p=4`: `r1 = -0.1760`, `unseen r2,r3 = -0.1292` (đều chậm đi mạnh ở `S=16`).
     - `A3 p=2`: `r1 = +0.1069` vs `unseen r2,r3 = +0.0954`; `A3 p=4`: `r1 = -0.0211` nhưng `unseen r2,r3 = +0.0423` (`+0.0142, +0.0704`).
   -> Kết luận về chiều hướng `flat > set` và phân hóa `S_opt(A0/A1) = 8` vs `S_opt(A3) = 16` **không phải ảo giác khớp quá trên `R1`**.
2. **Hai nguồn selection bias tồn dư cần ghi nhận trung thực:**
   - **Tái sử dụng cùng tập `pilot_test_3000.ids` (`SHA-256: 18d8b901...`)** xuyên suốt Stage B, C1, C2 và D. Dù không chọn beam trên tập này, việc dùng cùng `3,000` queries để đánh giá `S=8` vs `S=16` ở cả C và D vẫn tạo rủi ro phụ thuộc tập query. Khắc phục trong các bước tới bằng tùy chọn `--disjoint-test-ids` trích tập rời rạc từ `87,000` queries còn lại của `test_90k.ids`.
   - **Bỏ sót `S=4 flat` trong Stage D & hiệu ứng `best-fixed-per-arm`:** Ở Stage C2, `A0_r1 p=4 S=4 flat` (`2.4992x`) ngang ngửa `S=8 flat` (`2.4967x`) nhưng không đưa vào Stage D; và khi báo cáo `A0(S8_flat) - A3(S16_flat) = +0.1244x`, cần luôn trình bày song hành với contrast cùng cấu hình (`S8_flat: +0.1456x`, `S16_flat: -0.0587x`).

### 1.4 Trạng thái Git & Đề xuất Commit/Tag Tái lập (Chưa tự thực thi)
- **Hiện trạng nhánh:** `research/task-d-a-p0-p1-20261115`, `HEAD = b0a95f4`.
  - Tracked modified (`3` tệp): `research/task_da/CMakeLists.txt`, `research/task_da/evaluate_smoke.py`, `tests/research/test_task_da.py` (`git diff --check` = `0`).
  - Untracked mới: source P1/P2 (`evaluate_p1.py`, `evaluate_p2.py`, `run_i5_14600kf_replication.py`, `search_common/p1_eval.cpp`, `p2_engine.hpp`, `p2_eval.cpp`) và các tài liệu/summary trong `docs/research/task-da/`.
  - Toàn bộ build (`build-task-da*`), venv (`.venv-research`, `.deps-research`) và raw data (`../artifact-evidence/`) đều nằm ngoài git / được `.gitignore` loại trừ.
- **Đề xuất lệnh freeze để owner xem xét chạy (không tự commit/tag/merge):**

```bash
# Commit 1: Mã nguồn C++/Python & kiểm thử P1/P2 + i5-14600KF runner
git add research/task_da/CMakeLists.txt \
        research/task_da/evaluate_smoke.py \
        research/task_da/evaluate_p1.py \
        research/task_da/evaluate_p2.py \
        research/task_da/run_i5_14600kf_replication.py \
        research/task_da/search_common/p1_eval.cpp \
        research/task_da/search_common/p2_engine.hpp \
        research/task_da/search_common/p2_eval.cpp \
        tests/research/test_task_da.py
git commit -m "feat(task-da): add P2 multi-walker set/flat engine, tests, and i5-14600KF runner"

# Commit 2: Báo cáo P0/P1/P2, Stage A-E Replication, Audit & H3 PIVOT Plan
git add docs/research/task-da/
git commit -m "docs(task-da): freeze Stage A-E replication evidence, audit, and H3 PIVOT plan"

# Annotated tag tái lập (chỉ gắn trên nhánh nghiên cứu, chưa merge main)
git tag -a task-da-p2-stage-de-freeze-20261119 -m "Freeze Task D x A P2 Stage A-E (H1/H2 replicated on 4650U, H3=PIVOT/HOLD)"
```

---

## 2. Giai đoạn 2 — Môi trường Kiểm thử Đầy đủ (`COMPLETE`)

Đã tạo virtual environment cục bộ `.venv-research` (đã có trong `.gitignore`, **không chạm `/usr/bin/python3` hệ thống**, **không tắt ASLR/bảo mật**) chứa `numpy 2.5.5`, `jsonschema 4.26.0`, `pyyaml 6.0.3`.

| Bộ kiểm thử | Lệnh / Cấu hình | Kết quả | PASS | FAIL | SKIP | ENV_BLOCKED |
|---|---|---|---:|---:|---:|---:|
| **Python suite (dataset-free)** | `PYTHONPATH="$PWD/.venv-research/lib/python3.12/site-packages" /usr/bin/python3 -m unittest discover -s tests/research -v` | **`PASS`** (`16.871s`) | **`505`** | `0` | `10`* | `0` |
| **Python suite + Release native** | Như trên + `TASK_DA_{SMOKE,P1_EVAL,P2_EVAL}` (`build-task-da`) | **`PASS`** (`17.565s`) | **`515`** | `0` | `0` | `0` |
| **Python suite + ASan+UBSan+LSan** | Như trên + `build-task-da-asan` | **`PASS`** (`20.692s`) | **`515`** | `0` | `0` | `0` |
| **Lưu ý chạy trực tiếp `.venv-research/bin/python`** | `.venv-research/bin/python -m unittest discover -s tests/research -v` | **`1 FAIL (path-space)`** | `514` | `1`† | `0` | `0` |
| **GCC 13 `TSan` (`build-task-da-tsan`)** | `build-task-da-tsan/task_da_p2_eval --help` | **`ENV_BLOCKED`** (`rc=66`) | `0` | `0` | `0` | **`1`**‡ |

*\*10 ca skipped trong chế độ dataset-free là 10 ca native CMake của `test_task_da.py`, đã đạt `10/10 PASS` trong cả hai lượt chạy có binary Release và ASan+UBSan+LSan.*
*†Khi gọi trực tiếp `.venv-research/bin/python`, `test_sigterm_stops_benchmark_and_collectors` (`tests/research/test_run_ann_experiment.py:364`) ghi shebang `#!{sys.executable}` có khoảng trắng trong tên thư mục cha `Research ANN`, khiến nhân Linux cắt dòng shebang; dùng `/usr/bin/python3` cùng `PYTHONPATH="$PWD/.venv-research/lib/python3.12/site-packages"` giải quyết sạch mà không sửa test hay system Python.*
*‡`FATAL: ThreadSanitizer: unexpected memory mapping` do entropy ASLR nhân Linux host; giữ nguyên cấu hình bảo mật theo `AGENTS.md`.*

---

## 3. Giai đoạn 3 — Chuẩn bị Benchmark `i5-14600KF` (`READY / NOT_RUN`)

- **Trạng thái thực thi:** **`NOT_RUN`** (máy hiện tại là `AMD Ryzen 5 PRO 4650U`).
- **Tài liệu & Công cụ đã xuất:**
  - Protocol & checklist đầy đủ: [I5_14600KF_REPLICATION_PROTOCOL.md](I5_14600KF_REPLICATION_PROTOCOL.md)
  - Script runner tự động: [run_i5_14600kf_replication.py](../../../research/task_da/run_i5_14600kf_replication.py)
- **Kiểm chứng cục bộ trước bàn giao:**
  - `--dry-run`: xác minh đủ `17/17` SHA-256 input, ghi nhận `is_i5_14600kf: false`, `Status: NOT_RUN` (`exit = 0`).
  - Fail-closed guard (không có `--dry-run`): từ chối chạy ngay lập tức trên `4650U` (`exit = 1`).
  - Synthetic hybrid sysfs parser test (`cpu_core = 0-11`, `cpu_atom = 12-19`, cặp HT `(0,1)..(10,11)`): chọn đúng `{'1': [0], '2': [0, 2], '4': [0, 2, 4, 6]}` loại bỏ hoàn toàn E-cores và HT siblings.

---

## 4. Giai đoạn 4 — Thiết kế Hai Thí nghiệm PIVOT Tách biệt (`DESIGN ONLY — CHƯA TRIỂN KHAI`)

**Nguyên tắc bất biến cho cả hai thí nghiệm:**
1. **Baseline duy nhất:** Best fixed `S + flat` trên binary `ff46d6ac...` (`A0: p=2 S=16 flat, p=4 S=8 flat`; `A3: p=2 S=16 flat, p=4 S=16 flat`).
2. **Không thay A và B cùng lúc trong thí nghiệm đầu tiên** (tách riêng biến độc lập qua cờ CLI mặc định giữ hành vi cũ).
3. **Không gọi A hay B là thuật toán mới** (Mục 5.4 chứng minh cả hai là kỹ thuật hệ thống đã có trong tài liệu).
4. **Cổng bắt buộc trước khi chạy pilot:** Release + ASan+UBSan+LSan CTest `24/24 OK` + unit tests chuyên biệt + smoke `500` queries thực PASS; **chỉ chạy pilot sau khi người phụ trách phê duyệt**.

### 4.1 Ablation A — Incremental Frontier Maintenance (`--frontier-mode full|incremental`)

- **Phát hiện từ đọc mã nguồn [p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp):**
  1. `p2_engine.hpp:732–737`: Sau mỗi barrier `FlatMerge`, Worker 0 quét lại toàn bộ `global_best_vec_` (độ dài `beam` ~ `408–980`) và tra cứu ngẫu nhiên mảng `2 MB` `global_expanded_epoch_[hit.second]` để dựng lại `active_frontier_` từ đầu.
  2. `p2_engine.hpp:614–619` và `353–355`: Toàn bộ `active_frontier_` (có thể tới `100–240` đỉnh/worker trên `A3`) bị copy vào `init_seeds` rồi **chèn lại vào cây đỏ-đen `std::set<Hit> ws.local_pending`** mỗi round, dù mỗi worker chỉ pop tối đa `S` (`8` hoặc `16`) đỉnh trước barrier kế tiếp!
- **Cơ chế đề xuất (giữ 100% tương đương ngữ nghĩa với `flat`):**
  - **Bước A1 (Inline expanded bit + Bounded `p*S` dispatch):**
    - Thay `global_best_vec_` bằng `struct FlatEntry { Hit hit; uint8_t expanded; }` (đánh dấu `expanded = 1` ngay trong pha merge tuyến tính hoặc qua bảng `global_expanded_epoch_` chỉ cho phần tử thực sự thay đổi), và đếm `unexpanded_count` tăng/giảm chính xác để kiểm tra dừng `O(1)` (`unexpanded_count == 0`).
    - Chỉ trích tối đa `K_dispatch = p * S` phần tử tốt nhất chưa expand từ `global_best_vec_` để chia round-robin vào `init_seeds` (mỗi worker nhận tối đa `S` seed tốt nhất; về mặt toán học một worker không bao giờ pop quá `S` đỉnh trong một round `S`-step nên mọi seed thứ `> S` trong `init_seeds` **chắc chắn không bao giờ được pop** trong round đó!).
  - **Phần source dự kiến chỉnh:** `research/task_da/search_common/p2_engine.hpp` (`lines 27, 170, 276–279, 353–355, 586–619, 686–745`), `research/task_da/search_common/p2_eval.cpp` (thêm `--frontier-mode full|incremental`, mặc định `full`), `tests/research/test_task_da.py` (thêm unit test parity `incremental == full` từng bit).
- **Rủi ro correctness cần kiểm soát:**
  1. **Điều kiện dừng giả (`premature termination`):** Nếu dùng `K_dispatch = p * S`, không được lấy `init_seeds.empty()` làm điều kiện dừng mà phải kiểm tra toàn bộ `global_best_vec_` không còn phần tử chưa expand (`unexpanded_count == 0`).
  2. **Eviction tại biên `beam`:** Khi một đỉnh mới đẩy đỉnh xấu nhất ra khỏi top-`beam`, cần cập nhật đúng `unexpanded_count` tùy thuộc đỉnh bị loại đã expand hay chưa.
  3. **Bắt buộc bit-identical parity với `flat`:** Vì không seed thứ `> S` nào có thể được pop trong round `S`-step, thứ tự mở rộng và kết quả (`ids`, `squared_l2`, mọi counter thuật toán) của **A1 phải khớp từng bit 100%** với `--merge-impl flat --frontier-mode full`! Bất kỳ sai lệch ID nào = BUG fail-closed.
- **Phạm vi pilot đề xuất (chờ duyệt):** `A0_r1` & `A3_r1` (`p ∈ {1,2,4}`, `S ∈ {8,16}`, `5 OFF + 1 ON` trên `test_3000` và kiểm chéo một tập rời rạc `3,000` queries từ `test_90k.ids`), đo `Recall`, `OFF latency`, `ON merge_us`, `barrier_us`, `dup_de`, và so sánh trực tiếp với `flat` baseline.

### 4.2 Ablation B — Lightweight Shared Claim/Visited Before L2 (`--visited-policy baseline|barrier_all_evaled|atomic_claim`)

- **Phát hiện mấu chốt từ mã nguồn `p2_engine.hpp:374–388, 689–694` và kiểm chứng counter Stage C1:**
  - Ở `p = 1` (`search_single`, `p2_engine.hpp:455`), `settled_epoch_[node] = q_epoch` được đánh dấu cho **MỌI** đỉnh đã tính `squared_l2`, kể cả đỉnh bị loại khỏi `best`.
  - Ở `p = 2, 4` (`search_multi`, `p2_engine.hpp:384, 689–694`), các đỉnh đã tính `squared_l2` nhưng bị loại bởi `!(hit < global_worst)` **KHÔNG** nằm trong `ws.local_discovered`, nên **KHÔNG BAO GIỜ** được đánh dấu vào `settled_epoch_`!
  - Đối chiếu số liệu `ON` Stage C1 chứng minh ngay: ở `p=2, S=4` dù chỉ có `2.2` (`A0`) / `2.6` (`A3`) `duplicate_expansions`, **`already_seen_attempts` tụt mạnh `+3,121` (`A0`) / `+4,879` (`A3`) so với `p=1`**, còn **`duplicate_distance_evaluations` vọt lên `3,197` (`A0`) / `4,972` (`A3`)**!
  - **Hệ quả định lượng:** Khoảng **~75%–90% tổng `duplicate_distance_evaluations` ở `S=4, S=8` là tái tính L2 XUYÊN ROUND (cross-round) của các đỉnh từng bị loại**, chứ không phải đụng độ song song trong cùng round!
- **Cơ chế đề xuất (tách làm 2 bước con độc lập, đều giữ nguyên `flat` merger không thay A):**
  - **Bước B1 — `barrier_all_evaled` (Xác định, không atomic, 0 RFO contention):**
    - Ghi nhận mọi `nbr` đã tính `squared_l2` vào buffer `ws.local_evaled` (kích hoạt trong cả Mode `OFF`), và tại pha merge Worker 0 đánh dấu `settled_epoch_[id] = q_epoch` cho toàn bộ `ws.local_evaled`.
    - Loại sạch tái tính L2 xuyên round mà **giữ tính xác định 100%** và **không gây cache-line ping-pong** trong pha song song.
  - **Bước B2 — `atomic_claim` (Lightweight shared claim trước `squared_l2`):**
    - Chuyển `settled_epoch_` thành `std::vector<std::atomic<uint16_t>> claim_epoch_` (`2 MB`). Trước khi tính `squared_l2(nbr, query)`, worker kiểm tra fast-path `load(relaxed) == q_epoch`; nếu chưa, thực hiện `exchange(q_epoch, std::memory_order_relaxed) == q_epoch` (hoặc `compare_exchange_weak` chỉ khi miss) để giành quyền tính L2 duy nhất cho `nbr` trên toàn bộ `p` workers trong cả truy vấn.
- **Phần source dự kiến chỉnh:** `research/task_da/search_common/p2_engine.hpp` (`lines 152, 265–266, 345, 374–395, 686–695`), `research/task_da/search_common/p2_eval.cpp` (`--visited-policy baseline|barrier_all_evaled|atomic_claim`, mặc định `baseline`), `tests/research/test_task_da.py`.
- **Rủi ro correctness & hiệu năng cần kiểm soát:**
  1. **Rủi ro mất ứng viên (`lost discovery bug`) ở B2:** Trong `p2_engine.hpp:385`, worker chỉ đẩy vào `local_discovered` nếu vượt cả `global_worst` lẫn `ws.local_top.rbegin()`. Nếu Worker A claim `nbr` rồi loại nó do `ws.local_top` của A chặt hơn `global_worst`, trong khi Worker B có thể giữ nó, `nbr` bị mất vĩnh viễn! **Biện pháp bắt buộc:** Khi dùng B2, mọi đỉnh vượt `global_worst` (vốn chỉ-đọc và đồng nhất giữa mọi worker trong round) phải được đẩy vào `local_discovered` bất kể `ws.local_top`, loại trừ hoàn toàn mất ứng viên so với ngưỡng toàn cục.
  2. **Phi xác định (`non-determinism`) & dịch chuyển Recall ở B2:** Vì thứ tự worker nào claim trước phụ thuộc lịch CPU, B2 sẽ **không khớp từng bit** giữa các lần chạy và có thể làm dịch nhẹ Recall -> bắt buộc tái đo Recall trên `val_10k` và kiểm tra độ ổn định Recall qua nhiều repeats (còn B1 vẫn hoàn toàn xác định từng bit giữa `ON`/`OFF` và giữa các repeats!).
  3. **RFO cache-line ping-pong (đặc biệt trên dual-CCX `4650U`):** Ghi `atomic::exchange` trên mảng `2 MB` bởi 4 core khác CCX có thể làm tăng độ trễ bộ nhớ vượt lợi ích tiết kiệm L2 -> phải đo trực tiếp `OFF latency` so với `B1` trên cả `4650U` và (khi có máy) `i5-14600KF`.
- **Phạm vi pilot đề xuất (chờ duyệt):** Chạy lần lượt `baseline (flat)` -> `B1 (barrier_all_evaled)` -> `B2 (atomic_claim)` trên `A0_r1` & `A3_r1` (`p=2,4`, `S=8,16`, `5 OFF + 1 ON`), đo `Recall`, `OFF latency`, `ON dup_de`, `already_seen_attempts`, `merge_us`, `barrier_us` và overhead thực tế của ghi `local_evaled` / `atomic::exchange`.

---

## 5. Giai đoạn 5 — Báo cáo Quyết định & Kiểm tra Prior-Art

### 5.1 Những kết quả H1/H2 nào đủ tin cậy trong phạm vi hiện tại?
- **Đủ tin cậy (trong phạm vi `EXPLORATORY_HOST_SPECIFIC` trên `Ryzen 5 PRO 4650U`, `Recall@10 >= 0.990`, `n = 3` graph seeds `R1/R2/R3`):**
  1. `A0` và `A1` có hành vi mở rộng song song đồng nhất (`A0 - A1` CI95 cắt `0` trên mọi cấu hình `p=2,4`).
  2. `A3` có parallel speedup thấp hơn rõ rệt so với `A0/A1` ở baseline `S8_set` (`A0 - A3 = +0.2521x` ở `p=2`, `+0.3192x` ở `p=4`), và **~48–60%** mức hụt này đến từ lỗi cấu trúc `std::set` toàn cục + `S=8` quá khít (`flat - set` tại `A3 p=4 S=8` tăng `+0.2982x [+0.1644, +0.4320]`).
  3. Sau khi sửa `flat` và chọn `S` tĩnh tốt nhất, **tác động đồ thị tồn dư của `A3` vẫn có thật và tái lập trên cả 3 seed** (`p=2 S16_flat`: `A0 - A3 = +0.1175x [+0.0929, +0.1421]`; `p=4` best-fixed: `A0(S8_flat) - A3(S16_flat) = +0.1244x [+0.0333, +0.2156]`), đồng thời `S_opt(A3)` dịch phải (`S=16`) so với `S_opt(A0/A1) = 8` ở `p=4`.
  4. `worker_idle_ns` không phải nguyên nhân chính (`< 5 us/worker`, `workload_imbalance <= 1.006`).
- **Giới hạn phạm vi (KHÔNG được khái quát quá mức):**
  - Chưa xác nhận đa kiến trúc (`i5-14600KF = NOT_RUN`); `A1_r2 p=4` chịu nhiễu nhiệt laptop (`SD = 201 us`).
  - `test_3000` chỉ là exploratory point floor (`59/63` ô có `test_3000 LCB95 < 0.990`), có độ lệch test-quality thực tế `~0.00035` giữa `A3` và `A0/A1`, và tái sử dụng cùng `pilot_test_3000.ids` giữa Stage C và D.

### 5.2 Bottleneck nào vẫn tồn tại sau `flat + fixed S`?
Xếp theo tỷ trọng đóng góp vào `excess_us` ở `p = 4` (`stage_d_decomposition.json`):
1. **Serial `merge_time_ns` & dựng lại `active_frontier` + `std::set` cục bộ:** `406.6 us` (`17.8%` tổng `tp` trên `A0`) và `709.0–718.7 us` (`19.5%–20.0%` tổng `tp` trên `A3`), kèm chi phí chèn lại hàng trăm `init_seeds` vào `std::set local_pending` mỗi round.
2. **Duplicate distance evaluations (`3,804–6,220` L2s, ước tính `290.4–489.2 us/p`):** Nay đã xác định **~75%–90% ở `S=4, S=8` là tái tính L2 xuyên round của các đỉnh từng bị loại** do `settled_epoch_` không đánh dấu đỉnh bị loại, phần còn lại (`~10–25%` ở `S=8`, tăng mạnh ở `S=16`) là đụng độ đồng thời trong cùng round.
3. **Barrier wait (`bar/p = 144.4–259.9 us`, tổng `578–1223 us`):** Phản ánh chênh lệch thời gian hoàn thành `S` bước giữa các worker do phân bố bậc kề/cache miss khác nhau.

### 5.3 Thí nghiệm PIVOT nào có khả năng cải thiện hiệu năng ròng cao nhất?
1. **Khả năng cao nhất (Rủi ro thấp, lợi ích ròng chắc chắn nhất):** **Ablation B1 (`barrier_all_evaled`)** và **Ablation A1 (Inline expanded bit + Bounded `p*S` dispatch)** — B1 loại bỏ ngay `~3,000–4,800` L2 eval dư thừa xuyên round mà không có atomic RFO overhead và giữ 100% tính xác định; A1 cắt trực tiếp quét `2 MB` `global_expanded_epoch_` và loại chi phí chèn dư `~100–240` seed vào `std::set local_pending` mà giữ 100% bit-identical parity.
2. **Khả năng trung bình / phụ thuộc kiến trúc:** **Ablation B2 (`atomic_claim`)** — lợi ích giảm thêm `~500–1,500` L2 trùng trong round có thể bị triệt tiêu một phần bởi cache-line RFO trên dual-CCX `Ryzen 5 PRO 4650U`, nhưng nhiều khả năng lợi hơn trên shared L3 ring của `i5-14600KF`. Cần đo thực nghiệm riêng sau B1.

### 5.4 Kiểm tra Prior-Art (`Speed-ANN`, `iQAN`, `AverSearch`, `ParlayANN` / `DiskANN` / `HNSW`)

| Cơ chế trong nghiên cứu này | Đã xuất hiện ở đâu trong tài liệu prior-art? | Đánh giá tính mới (`Novelty`) |
|---|---|---|
| **Hàng đợi cục bộ (`local_pending`) + gộp định kỳ vào hàng đợi toàn cục (`S`-step sync)** | **Speed-ANN** (Peng et al., 2022) và **iQAN** (Peng et al., PPoPP '23: local priority queues `LS[t]` gộp vào global `S` sau mỗi nhịp bước). | **KHÔNG MỚI** — nền tảng chuẩn của path-wise intra-query parallelism. |
| **Mảng phẳng sắp xếp có cờ `checked/expanded` nội tuyến & tái sử dụng frontier (Ablation A)** | **iQAN** (PPoPP '23, Algorithm 2: cờ `checked` gắn với ứng viên trong pool dung lượng `L`), **NSG / DiskANN / HNSW** (sorted candidate pool với cờ `checked` + quét từ vị trí `nk` chưa check đầu tiên). | **KHÔNG MỚI** — kỹ thuật cấu trúc dữ liệu chuẩn; ở đây chỉ sửa điểm yếu triển khai của baseline P2. |
| **Đánh dấu mọi đỉnh đã tính khoảng cách & `visited` chia sẻ lỏng/atomic trước khi tính L2 (Ablation B1 & B2)** | **iQAN** (PPoPP '23: shared loosely-synchronized `is_visited` map kiểm tra & đánh dấu ngay trước tính khoảng cách), **ParlayANN** / **DiskANN** / **HNSW parallel** (atomic bitset / CAS test-and-set tránh tính L2 lặp). | **KHÔNG MỚI** — B1 là khắc phục thiếu sót đánh dấu `settled_epoch_` trong baseline P2; B2 là shared atomic visited phổ biến. |
| **Tách vai trò bất đồng bộ (queue maintenance vs distance workers) & bỏ barrier đồng bộ cứng** | **AverSearch** (arXiv:2504.20461v2, §§4.2–4.4: kiến trúc hoàn toàn bất đồng bộ, tách global workload balancer, sub-queues và distance units; repo đã có kiểm toán riêng tại [AVERSEARCH_QUEUE_ROLE_E1.md](../AVERSEARCH_QUEUE_ROLE_E1.md)). | **KHÔNG MỚI** — ngoài phạm vi P2 hiện tại và chưa có mã nguồn gốc xác minh được của tác giả. |

> [!IMPORTANT]
> **Kết luận Prior-Art:** Cả **Ablation A** lẫn **Ablation B1/B2** đều **KHÔNG phải thuật toán mới**; chúng là bước **tăng cường vệ sinh baseline (`baseline hygiene`)** để loại bỏ các lỗi triển khai (như quét thừa `global_expanded_epoch_`, chèn thừa vào `std::set`, và quên đánh dấu `settled_epoch_` cho đỉnh bị loại) trước khi đánh giá bất kỳ giả thuyết thuật toán mới nào.

### 5.5 Có đủ căn cứ mở một H3 mới không, hay tiếp tục `HOLD`?
- **Quyết định khuyến nghị:** **TIẾP TỤC `HOLD` đối với H3 (`TP-CG / H3 = NOT_OPENED`).**
- **Lý do:**
  1. Dư địa của lịch đồng bộ `S` động (TP-CG) trên engine hiện tại quá nhỏ (`< 1–3%`), trong khi các lỗi vệ sinh baseline (**B1** bỏ quên `settled_epoch_` cho đỉnh bị loại gây `~3.0k–4.8k` L2 trùng xuyên round, và **A1** quét `2 MB` + chèn thừa `std::set`) vẫn đang chiếm phần lớn overhead.
  2. Chưa có dữ liệu đối chứng trên `i5-14600KF` và chưa kiểm tra trên tập query `test_90k` rời rạc khỏi `pilot_test_3000.ids`.
  3. **Trình tự đề xuất chờ người phụ trách phê duyệt trước khi thực thi:**
     - **Bước 1 (Pilot nhỏ, tách biệt):** Triển khai và kiểm chứng đúng cổng correctness cho **Ablation B1** (đánh dấu đủ `settled_epoch_` ở barrier) -> chạy pilot nhỏ trên `A0_r1, A3_r1`; sau đó tách riêng **Ablation A1** (inline `expanded` + bounded `p*S` dispatch, giữ `flat` + parity 100%) -> chạy pilot nhỏ; chỉ sau đó mới thử **Ablation B2** (`atomic_claim`).
     - **Bước 2 (Đa kiến trúc):** Chạy [run_i5_14600kf_replication.py](../../../research/task_da/run_i5_14600kf_replication.py) trên máy `i5-14600KF` khi có quyền truy cập (kèm tùy chọn `--disjoint-test-ids`).
     - **Bước 3 (Đánh giá mở H3 mới):** Chỉ sau khi có baseline sạch (không còn lỗi triển khai B1/A1) và thấy rõ khoảng trống thực sự còn lại giữa đồ thị `A0/A1/A3` trên cả 2 kiến trúc mới quyết định xem có tồn tại một giả thuyết H3 mới thật sự có tính mới (khác với `iQAN`/`AverSearch`) hay không.
