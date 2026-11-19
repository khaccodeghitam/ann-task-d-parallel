# Task D × Task A — P2 Multi-Walker Implementation & Correctness Status

- **Document Status:** **`P2_CORRECTNESS_PASS_AND_STAGE_A_TO_E_FOLLOWUP_COMPLETE`** *(Hoàn tất Cổng Correctness bản gốc `e0bddc77...` + Pilot Exploratory R1 trong [H1_GRAPH_WORKER_PILOT.md](H1_GRAPH_WORKER_PILOT.md), [H2_WORK_OVERHEAD_PILOT.md](H2_WORK_OVERHEAD_PILOT.md), và hoàn tất bổ sung `--merge-impl flat`, Stage A–E R1/R2/R3 Replication & quyết định `H3 = PIVOT` trên bản `ff46d6ac...` trong [STAGE_D_E_REPLICATION_AND_H3_DECISION.md](STAGE_D_E_REPLICATION_AND_H3_DECISION.md).)*
- **Protocol Anchor:** [PROTOCOL_V4_1_P2_EXPLORATORY_0990_ADDENDUM.md](PROTOCOL_V4_1_P2_EXPLORATORY_0990_ADDENDUM.md) (`P2-EXP-1..4` Owner Decision 2026-11-18).
- **Counter Schema:** [counter_schema_p2.json](counter_schema_p2.json).
- **Target Scope:** Intra-query multi-walker `p ∈ {1, 2, 4}` trên cùng 1 truy vấn (`--jobs` liên-truy-vấn cố định `1`), chỉ mở exploratory tại `Recall@10 >= 0.990`. Không thay đổi trạng thái `HOLD` của `P0 / Full P1 / t0998`, `CLOSED` của `P3 official`, hoặc `NOT_OPENED` của `TP-CG / H3`.

---

## 1. Kiến trúc thiết kế P2 Multi-Walker (`search_common/p2_engine.hpp`)

### 1.1 Quy tắc kế thừa & công bằng `p=1` vs `p=2,4`
- Giữ nguyên tuyệt đối `task_da::Index::search<Instrument>` trong `research/task_da/search_common/engine.hpp`, `smoke.cpp`, và `p1_eval.cpp` (`task_da_smoke`, `task_da_p1_eval` không sửa đổi hành vi P1).
- Trong engine P2 (`P2SearchSession`):
  - **Cấu trúc visited chung (`settled_epoch_`):** Mảng `uint16_t settled_epoch_[n]` dùng chung theo query epoch (`2 MB` cho `n = 1,000,000`, tăng `query_epoch_` theo từng query và chỉ reset khi wrap `65535 -> 0`). Cả `p=1` lẫn `p=2,4` đều dùng cùng cơ chế persistent epoch này để tránh chi phí `malloc + memset(1 MB)` giả tạo mỗi query.
  - **`p == 1` (`search_single<Instrument>`):** Thực thi y nguyên thứ tự `entry_best_first_v1` của `Index::search` trên `std::set<Hit> best, pending`, cho kết quả (`ids`, `squared_l2`, toàn bộ 5 counter P1) khớp từng bit với `task_da_p1_eval`.

### 1.2 Frontier, Ownership, Merge & Termination (`p ∈ {2, 4}`)
1. **Khởi tạo trên `entry` (Worker 0 trước Round 0):**
   - Tính L2 cho `entry`, đánh dấu `settled_epoch_[entry] = query_epoch_` và `global_expanded_epoch_[entry] = query_epoch_`.
   - Duyệt toàn bộ kề của `entry`, đánh dấu `settled_epoch_[nbr]`, chèn vào `global_best` (`beam`-bounded).
   - Trích `active_frontier = { h in global_best : !expanded(h.id) }` theo thứ tự `(squared_l2, id)`. Nếu rỗng (ví dụ đồ thị cô lập tại `entry`), kết thúc ngay trả về top-`k` từ `global_best`.
   - Ngược lại chia đều `active_frontier` theo vòng tròn (`idx % p`) vào `worker_state[w].init_seeds`.

2. **Pha song song trong từng Round (`sync_interval = S` steps/worker):**
   - Trong pha song song, **`settled_epoch_` hoàn toàn read-only** (chỉ Merger `worker 0` cập nhật ở rào chắn merge), loại bỏ hoàn toàn data race và atomic ping-pong trên mảng `2 MB`.
   - Mỗi worker `w ∈ {0..p-1}` giữ state cục bộ cache-line-padded (`alignas(64)`):
     - `local_seen`: bảng băm open-addressing L1-friendly theo round (`uint32_t keys/stamps`, `reset()` O(1)), tự động grow nếu load `>= 50%`.
     - `local_pending` & `local_top`: `std::set<Hit>` bounded theo cả `global_worst_hit` lẫn `local_top` (`beam`).
     - `local_discovered`, `local_expanded`, và (`Instrument=true` only) `local_newly_evaled`.
   - Nếu `init_seeds` của worker `w` rỗng: worker `w` không pop/expand trong round đó và ghi nhận `idle_round` (`worker_idle_ns` khi `Instrument=true`).
   - Nếu `!init_seeds.empty()`: worker `w` pop tối đa `S` đỉnh tốt nhất từ `local_pending`. Với mỗi cung kề `nbr`:
     - Nếu `settled_epoch_[nbr] == query_epoch_` hoặc `local_seen.contains_or_insert(nbr)` hit -> tăng `already_seen_attempts` và bỏ qua.
     - Nếu chưa thấy trong round/epoch -> tính squared-L2 (`++distance_evaluations`). Nếu lọt ngưỡng cắt -> đưa vào `local_top`, `local_pending`, `local_discovered`.

3. **Rào chắn Merge & Tái cân bằng (Single-Writer `worker 0`):**
   - Toàn bộ `p` workers đồng bộ qua cặp sense atomic barrier `acquire/release` (spin + `_mm_pause` ngắn rồi `std::this_thread::yield()`, không tạo thread theo từng query; các thread helper `1..p-1` sống bền bỉ suốt phiên `P2SearchSession` và `join()` sạch trước bước ghi đĩa).
   - `Worker 0` hợp nhất `local_discovered[0..p-1]` vào `global_best` (giới hạn `beam`, cắt bớt phần tử xấu nhất), đánh dấu `settled_epoch_` cho mọi đỉnh mới phát hiện, và đánh dấu `global_expanded_epoch_` cho mọi đỉnh trong `local_expanded[0..p-1]`.
   - **Đo trùng lặp thật (`Instrument = true`):**
     - `unique_expansions` vs `duplicate_expansions`: đếm số đỉnh thực sự được popped & expanded nhiều hơn 1 lần bởi nhiều worker trong cùng round async `S`-step (`expansions == unique_expansions + duplicate_expansions`). Hoàn toàn tách biệt với `already_seen_attempts`.
     - `unique_distance_evaluations` vs `duplicate_distance_evaluations`: đếm số đỉnh bị nhiều worker đồng thời tính L2 trong cùng round trước barrier.
   - **Điều kiện dừng:** Tạo `active_frontier = { h in global_best : global_expanded_epoch_[h.id] != query_epoch_ }`. Chỉ dừng khi `active_frontier` hoàn toàn rỗng (bảo đảm mọi phần tử còn trụ trong top-`beam` đều đã được duyệt, không deadlock/livelock); ngược lại chia lại round-robin `(idx % p)` vào `init_seeds` cho round kế tiếp.

4. **Tách biệt Instrumentation (`OFF` vs `ON`):**
   - Template `<bool Instrument>`: chế độ `OFF` (`Instrument = false`) không đọc đồng hồ round, không cấp phát/chạm `disc_seen_`/`exp_seen_`, không đếm bất kỳ counter nội vòng nào.
   - Trong `task_da_p2_eval`, mọi thời gian đo `p50/p95/QPS` dùng strictly `workers ∈ {1,2,4}` với `--jobs` liên-truy-vấn cố định `= 1`, đo thuần pha search sau warmup, sau đó hủy session rồi mới serialize JSONL/summary.

---

## 2. Trạng thái Verification & Cổng Correctness (Bước 2 — Đã thực thi thực tế)

| Kiểm thử | Trạng thái | Bằng chứng thực nghiệm quan sát |
|---|---|---|
| **Release build (`task_da_p2_eval`)** | **`PASS`** | `g++ 13.3.0`, `-std=c++17 -Wall -Wextra -Wpedantic -Werror -O3 -DNDEBUG`, 0 warnings; SHA-256 `e0bddc77ffd977c6705cd2b51074e8bcc9ced8e4325e3eb8899d2e4bb51b47c2`; Release CTest `1/1 Passed (0.63s)`, `24/24 OK`. |
| **Unit + Exact Brute-Force Oracle (`p=1,2,4`)** | **`PASS`** | Kiểm thử trong [test_task_da.py](../../../tests/research/test_task_da.py): đồ thị ngẫu nhiên liên thông `n=48, beam=48` khớp exact brute-force oracle `Recall@5 == 1.0` trên `p=1,2,4`; đồ thị không liên thông (không pad ID), hòa khoảng cách (`tie-break` tăng dần ID), self-loop/duplicate arc, chain bậc 1 (`per_worker_idle_rounds > 0`), và đồ thị kim cương ép `duplicate_expansions >= 1` & `duplicate_distance_evaluations >= 1` đều `OK`. Từ chối đúng `--jobs != 1`, `--workers 3`, sai `--cpu-list`, ghi đè file. |
| **`p=1` bit-identical parity vs `task_da_p1_eval`** | **`PASS`** | Khớp từng bit (`ids`, `squared_l2`, và toàn bộ 5 counter P1) trên cả synthetic `n=48` lẫn **500 queries thực `smoke_val_500.ids`** trên cả `A0-R1` (`beam=416`) và `A3-R1` (`beam=896`). |
| **`ASan + UBSan + LSan` (`build-task-da-asan`)** | **`PASS`** | `ctest --test-dir build-task-da-asan` (`detect_leaks` mặc định ON): `24/24 OK (3.09s)` **0 UB, 0 race/UAF, 0 memory leak**. Stress đồ thị thực **100 queries `A0-R1 p=4 ON & OFF`** trên `task_da_p2_eval` ASan binary: `ON/OFF exact match = true`, exit 0. |
| **`TSan` (`ThreadSanitizer`, GCC 13.3)** | **`ENV_BLOCKED`** | Biên dịch sạch `build-task-da-tsan`, nhưng runtime bị chặn trước `main()` bởi nhân Linux host ASLR entropy (`FATAL: ThreadSanitizer: unexpected memory mapping`, exit 66 — xảy ra đồng nhất trên cả `task_da_smoke` đơn luồng lẫn `p2_eval`); giữ nguyên cấu hình bảo mật host không thay sysctl (`NO sudo/security change`). |
| **Real-Graph Smoke (`500` queries `val_10k` trên `A0-R1` & `A3-R1`, `p=1,2,4`)** | **`PASS`** | Evidence ngoài repo `artifact-evidence/p2-exploratory-0990-20261118/smoke_gate/smoke_gate_report.json`: `incomplete_top_k_queries = 0/500`, `ON/OFF exact_ids_match = true`, `exact_squared_l2_match = true`, `counter_invariants_pass = true`, `OFF vs OFF_rep2` xác định từng ID trên mọi `(graph, p)` (`p=1,2,4`), pinned `sched_getcpu()` khớp `[0]`, `[0,2]`, `[0,2,4,6]`, Peak RSS `VmHWM ~ 851 MiB (A0-R1)` / `~798 MiB (A3-R1)`. |
| **Dataset-free `tests/research` suite** | **`PARTIAL_ENV_DEP`** | Với `PYTHONPATH=.deps-research`: `451` ca thực thi đều `OK` (`10` skipped); `3` module (`test_algorithm_studies`, `test_issue29`, `test_paper_native_v3`) báo `ImportError: No module named 'numpy'` do thiếu gói tùy chọn `numpy` trong Python environment của host. Toàn bộ kiểm thử `test_task_da.py` (`24/24` trong CTest) đạt `100% PASS`. |

> [!NOTE]
> **Ghi chú trung thực từ Smoke Gate (`500` queries `val_10k`, chưa hiệu chỉnh Beam 2a):**
> - Ở `A0-R1 (beam=416)`: Recall@10 smoke là `0.9918` (`p=1`), `0.9920` (`p=2`), `0.9920` (`p=4`) — chất lượng giữ vững cho `p=2,4`.
> - Ở `A3-R1 (beam=896)` (V3 cũ): Recall@10 smoke là `0.9890` (`p=1`), `0.9890` (`p=2`), `0.9892` (`p=4`) — tái khẳng định biên V3 của `A3` sát ngưỡng `0.990` và lý do bắt buộc hiệu chỉnh **Điều khoản Beam 2a** trên trọn vẹn `val_10k.ids` (`10,000` queries) trước khi mở H1/H2.

---

## 3. Liên kết Bước 3–4 (Calibration & Pilot `R1` `EXPLORATORY_HOST_SPECIFIC`, bản `e0bddc77...`)

- **Beam Policy 2a Calibration (`val_10k`):** Đã khóa `A0_r1 = 416`, `A1_r1 = 416`, `A3_r1 = 960` (tất cả `p=1,2,4` đạt `LCB95_q >= 0.990` trên `10,000` queries).
- **Pilot H1 (`OFF`, 5 interleaved repeats, `3,000` queries):** Xem [H1_GRAPH_WORKER_PILOT.md](H1_GRAPH_WORKER_PILOT.md).
- **Pilot H2 (`ON`, 2 repeats, phân rã chi phí):** Xem [H2_WORK_OVERHEAD_PILOT.md](H2_WORK_OVERHEAD_PILOT.md).

---

## 4. Cập nhật Stage C2–E: `--merge-impl set|flat` & Replication `R1/R2/R3` (`ff46d6ac...`)

- **Bổ sung triển khai (`--merge-impl set|flat`, mặc định `set`):** Thêm `MergeImpl::kSet` và `MergeImpl::kFlat` vào [p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp) và [p2_eval.cpp](../../../research/task_da/search_common/p2_eval.cpp); nhánh `flat` thay thế `std::set` toàn cục ở `Worker 0` bằng `std::vector<Hit>` sắp xếp/gộp tuyến tính giữ đúng thứ tự `(squared_l2, id)`, **không thay đổi `p=1`** và **khớp từng bit (`ids`, `squared_l2`, mọi counter thuật toán) với `set`**.
- **Xác minh lại cổng Correctness trên binary `task_da_p2_eval` (`SHA-256: ff46d6ac8895d519054548575c3187544716c0fdf2bbdad83db8a0a8cc7f8759`):**
  - Release CTest: `24/24 OK`; `ASan+UBSan+LSan` CTest: `24/24 OK` (bao gồm kiểm thử unit `set == flat` và từ chối flag lỗi trong [test_task_da.py](../../../tests/research/test_task_da.py)); `TSan` giữ nguyên `ENV_BLOCKED` bởi ASLR kernel host.
  - Smoke parity thực tế: `14/14` cặp `smoke_500` (`A0/A3 × p={1,2,4} × S={4,8,16}`) + `ASan 100q A3_r1 p=4 flat` PASS; Stage D `63/63` ô `ON/OFF` exact parity & invariants PASS.
- **Replication `R1/R2/R3` & Quyết định `H3`:** Xem đầy đủ số liệu Stages A–E tại [STAGE_D_E_REPLICATION_AND_H3_DECISION.md](STAGE_D_E_REPLICATION_AND_H3_DECISION.md) và [P2_FOLLOWUP_CHECKPOINT_20261119.md](P2_FOLLOWUP_CHECKPOINT_20261119.md).
- **Hạng mục giữ nguyên `HOLD / CLOSED / NOT_OPENED / NOT_RUN`:** `Historical P0 = HOLD`, `Full P1 Gate = HOLD`, `t0998 = HOLD`, `Protocol V4 D1–D5 = UNAPPROVED`, `P3 official = CLOSED`, `TP-CG / H3 = NOT_OPENED` *(Stage E khuyến nghị **`PIVOT`**)*, `i5-14600KF = NOT_AVAILABLE_ON_THIS_HOST_NOT_RUN`.
