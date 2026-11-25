# Task D · Giải thích Kỹ thuật B1+A1 từ Mã nguồn Thực tế

Tài liệu này truy vết trực tiếp mã nguồn C++17 đóng băng của engine tìm kiếm đa walker (`P2SearchSession`) để giải thích chính xác cơ chế hoạt động của **Baseline**, **B1**, **A1**, và **B1+A1**. Mọi chi tiết đều gắn số dòng thực tế trong mã nguồn; phân biệt rành mạch **cơ chế đã xác nhận/chứng minh từ mã** với **giả thuyết chưa đo được trực tiếp (ví dụ phân rã chu kỳ CPU/cache)**, và **không tuyên bố `B1+A1` là thuật toán mới**.

---

## 1. Truy xuất nguồn mã đóng băng

- **Commit đóng băng dùng để biên dịch binary G2:** `f2cd634b837a70735c3e31e5956f0524bfc26675` (tag `task-da-b1-a1-pilot-freeze-20261119`), compiler `g++ 13.3.0` (`-O3 -DNDEBUG -std=c++17 -Wall -Wextra -Wpedantic -Werror`).
- **Tệp mã nguồn gốc & SHA-256:**
  - [engine.hpp](../../../research/task_da/search_common/engine.hpp) (`2ca38624...`): cấu trúc `Graph` (CSR), `Vectors`, `load_graph`, `load_fbin`, baseline tuần tự `Index::search`.
  - [p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp) (tại `f2cd634`: `c4b1bdc2...`; tại `HEAD` chỉ bổ sung các khối `#ifdef TASK_DA_ROUND_TRACE` ở commit `6bdf65f` cho công cụ quan sát H3, không đổi một dòng logic nào khi biên dịch Release chuẩn).
  - [p2_eval.cpp](../../../research/task_da/search_common/p2_eval.cpp) (tại `f2cd634`: `b356ba8d...`): driver CLI, đo thời gian từng query (`std::chrono::steady_clock`), xuất JSONL (bỏ khóa `"counters"` ở `--mode OFF`).
  - **Binary Release đóng băng (`task_da_p2_eval`, `211,176 B`):** SHA-256 `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1`.
- **Lưu ý đặt tên:** Ký hiệu `A1` trong tài liệu này chỉ tham số engine Task D (`--frontier-mode incremental`), hoàn toàn khác nhánh đồ thị `A1` (`H17 C160/K1024/N2`) của Task A.

---

## 2. Kiến trúc chung của Engine Đa Walker (BSP Intra-Query Parallelism)

Engine `P2SearchSession` ([p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L178-L1057)) chạy từng query một (`--jobs 1`) nhưng huy động `p ∈ {1, 2, 4}` worker song song trong cùng một query theo mô hình **Bulk Synchronous Parallel (BSP)** với chu kỳ đồng bộ `S = sync_interval_` bước mở rộng mỗi round (`S = 16` ở G2).

### 2.1 Cấu trúc dữ liệu cốt lõi
1. **Đồ thị & Vector chỉ đọc (dùng chung mọi worker):**
   - `Graph` (`offsets[n+1]`, `edges[m]` định dạng CSR, giữ nguyên thứ tự cạnh gốc, [engine.hpp](../../../research/task_da/search_common/engine.hpp#L35-L73)).
   - `Vectors` (`values[n × d]` liên tiếp, `float32`; khoảng cách `squared_l2` tính ở độ chính xác `double`, khóa sắp xếp xác định `Hit = std::pair<double, Id>`, [p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L376-L386)).
2. **Mảng epoch toàn cục tái sử dụng $O(1)$ giữa các query ([p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L317-L360)):**
   - `settled_epoch_[n]` (`std::vector<uint16_t>`, `2 MiB` với `n = 10^6`): đánh dấu đỉnh đã "yên vị" ở các barrier trước của query hiện tại (`== q_epoch`). Trong pha worker chạy song song, mảng này **chỉ đọc hoàn toàn** (không lock, không atomic RMW, không tranh chấp cache line giữa các lõi).
   - `global_expanded_epoch_[n]` (`std::vector<uint16_t>`, `2 MiB`): đánh dấu đỉnh đã được mở rộng toàn cục ở query hiện tại.
   - Mỗi query chỉ tăng `query_epoch_` lên `1`; chỉ `std::fill` về `0` khi tràn `uint16_t` (mỗi `65,535` query), triệt tiêu chi phí $O(n)$ `memset` mỗi query.
3. **Trạng thái riêng từng worker chống false sharing (`alignas(64) WorkerState`, [p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L154-L174)):**
   - `init_seeds` (`std::vector<Hit>`): danh sách hạt giống được Worker 0 cấp phát cho round kế.
   - `local_top` (`std::set<Hit>`, kích thước $\le B$), `local_pending` (`std::set<Hit>`): hàng đợi best-first cục bộ trong round.
   - `local_discovered` (`std::vector<Hit>`): các ứng viên tốt vượt ngưỡng toàn cục & lọt vào `local_top`.
   - `local_expanded` (`std::vector<Id>`): các đỉnh thực sự được pop để mở rộng trong round ($\le S$).
   - `local_newly_evaled` (`std::vector<Id>`): mọi đỉnh vừa được tính `squared_l2` trong round (được nạp ở Mode ON hoặc khi bật B1).
   - `local_seen` (`LocalRoundSet`, [p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L103-L152)): bảng băm phẳng open-addressing kích thước lũy thừa của 2 (khởi tạo `4096` ô), băm Fibonacci `(id * 2654435761u) & mask`, reset $O(1)$ theo `epoch` ở đầu mỗi round để khử trùng lặp cục bộ trong phạm vi một worker.
4. **Cơ chế song song & đồng bộ không khóa ([p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L219-L231), [#L487-L521](../../../research/task_da/search_common/p2_engine.hpp#L487-L521), [#L787-L801](../../../research/task_da/search_common/p2_engine.hpp#L787-L801)):**
   - Khởi tạo sẵn `p − 1` luồng phụ cố định cho cả phiên (`P2SearchSession`), ghim lõi vật lý bằng `pthread_setaffinity_np` (ví dụ `p=2 → CPU [0,2]` cùng một L3 CCX0 trên Ryzen 4650U).
   - Worker 0 phát lệnh bắt đầu round bằng `work_seq_.store(next_seq, memory_order_release)`, tự chạy phần việc của Worker 0 (`run_worker_round(0, q_epoch)`), rồi đợi từng luồng phụ hoàn thành qua `worker_states_[w].done_seq.load(memory_order_acquire) >= next_seq`.
   - Cả hai phía đều spin tối đa `2048` vòng với `__builtin_ia32_pause()` rồi chuyển sang `std::this_thread::yield()`.
   - **Pha gộp đơn luồng (Single-Writer Merge, [p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L814-L1014)):** Khi mọi luồng phụ dừng chờ `work_seq_`, chỉ mình Worker 0 cập nhật `settled_epoch_`, `global_expanded_epoch_`, tập beam toàn cục và phân phát `init_seeds` cho round tiếp theo — đảm bảo tính tất định tuyệt đối và `0` tranh chấp đồng bộ trong pha gộp.

---

## 3. Phân biệt cơ chế: Baseline vs B1 vs A1 vs B1+A1

Tổ hợp 3 công tắc biên dịch qua template `search_multi<Instrument, FlatMerge, MarkAllEvaled, IncFrontier>` ([p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L286-L298), [#L587](../../../research/task_da/search_common/p2_engine.hpp#L587)):

| Cấu hình | Cờ CLI (`task_da_p2_eval`) | Template flags | Vai trò lịch sử |
|---|---|---|---|
| Legacy P2 (Pilot R1 / Stage B–C1) | `--merge-impl set --visited-policy baseline --frontier-mode full` | `Flat=0, B1=0, A1=0` | Nút cổ chai `std::set` merge (đã thay thế ở Stage C2) |
| **Baseline (B1+A1 & G2)** | `--merge-impl flat --visited-policy baseline --frontier-mode full` | `Flat=1, B1=0, A1=0` | Đường cơ sở chuẩn cho toàn bộ thử nghiệm B1/A1 và G2 |
| **B1 đơn lẻ** | `--merge-impl flat --visited-policy barrier_all_evaled --frontier-mode full` | `Flat=1, B1=1, A1=0` | Cô lập tác dụng công bố đầy đủ visited tại barrier |
| **A1 đơn lẻ** | `--merge-impl flat --visited-policy baseline --frontier-mode incremental` | `Flat=1, B1=0, A1=1` | Cô lập tác dụng frontier tăng dần + giới hạn gửi hạt giống |
| **B1+A1 (`opt` / `combo`)** | `--merge-impl flat --visited-policy barrier_all_evaled --frontier-mode incremental` | `Flat=1, B1=1, A1=1` | Cấu hình tối ưu kiểm định chính thức trong G2 `design-3.1` |

### 3.1 Baseline (`flat + baseline + full`) hoạt động như thế nào?
1. **Khởi tạo tuần tự tại đỉnh `entry` ([p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L619-L689)):** Worker 0 mở rộng `entry`, tính L2 cho toàn bộ láng giềng của `entry`, đánh dấu chúng vào `settled_epoch_`, lưu top-$B$ vào `global_best_vec_` (mảng phẳng đã sắp xếp), và quét `global_best_vec_` để dựng `active_frontier_` gồm mọi đỉnh chưa mở rộng.
2. **Phân phát toàn bộ frontier (`!IncFrontier`, [#L745-L752](../../../research/task_da/search_common/p2_engine.hpp#L745-L752)):** Ở đầu *mỗi round*, Worker 0 chia vòng tròn **toàn bộ `active_frontier_`** (có thể tới `B = 432` ở R90 hoặc `B = 970` ở R86 A3) cho `p` worker. Kết quả: mỗi worker phải nạp tới `B/p` hạt giống (tới `~216`–`485` phần tử) vào cây đỏ-đen `std::set<Hit> local_pending` ([p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L421-L423)) dù mỗi round chỉ mở rộng tối đa **`S = 16`** đỉnh!
3. **Mở rộng cục bộ (`MarkAllEvaled = false`, [#L430-L473](../../../research/task_da/search_common/p2_engine.hpp#L430-L473)):** Với mỗi láng giềng `nbr` chưa có trong `settled_epoch_` và `local_seen`, worker tính `squared_l2(nbr, query)`. **Điểm yếu chí mạng ở dòng 460:** nếu beam toàn cục đã đầy (`has_full`) và `!(hit < global_worst)`, worker **bỏ qua ngay `nbr` mà không đưa vào `local_discovered`**.
4. **Gộp tại barrier ([p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L874-L884), [#L977-L1006](../../../research/task_da/search_common/p2_engine.hpp#L977-L1006)):**
   - Baseline **chỉ ghi `settled_epoch_[id] = q_epoch` cho các đỉnh nằm trong `local_discovered` và `local_expanded`**. Mọi đỉnh đã tính `squared_l2` nhưng bị loại bởi `global_worst` (chiếm đa số đỉnh được đánh giá sau khi beam đầy!) **không bao giờ được ghi vào `settled_epoch_`**. Ở các round sau, bất cứ khi nào một đỉnh mới có cạnh trỏ tới đỉnh đã bị loại ấy, worker lại tính `squared_l2` lại từ đầu.
   - Sau khi `std::sort` + `std::unique` + gộp tuyến tính 2 mảng (`global_best_vec_` và `merge_scratch_`) để giữ top-$B$, Baseline quét lại toàn bộ `global_best_vec_` (`O(B)` truy cập ngẫu nhiên vào mảng `2 MiB` `global_expanded_epoch_`) để dựng mới `active_frontier_` từ đầu.

### 3.2 B1 (`VisitedPolicy::kBarrierAllEvaled`) thay đổi điều gì?
- **Trong pha worker ([p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L453-L455)):** Ngay sau khi tính `squared_l2(nbr, query)` (trước lệnh lọc `if (has_full && !(hit < global_worst)) continue;` ở dòng 460), worker ghi `nbr` vào vector cục bộ phẳng `ws.local_newly_evaled.push_back(nbr)` — ghi tuần tự bộ nhớ riêng, `0` lock, `0` atomic.
- **Tại barrier đơn luồng ([p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L844-L848)):** Worker 0 duyệt `ws.local_newly_evaled` của mọi worker hoạt động và ghi `settled_epoch_[id] = q_epoch`.
- **Vì sao B1 cắt mạnh Duplicate L2 và Total L2:**
  - **Triệt tiêu 100% tính lại xuyên round (cross-round recomputation):** Một đỉnh đã bị tính `squared_l2` ở round $r$ (dù vào beam hay bị loại ngay lập tức) chắc chắn có `settled_epoch_[id] == q_epoch` từ round $r+1$ trở đi, nên bị bỏ qua ngay ở dòng 445 (`already_seen_attempts` tăng đúng bằng số duplicate L2 được cứu — trên G2 `design-3.1` là `+2,784.0351/q` khớp `1-đổi-1` với `−2,784.0351/q` duplicate L2!).
  - **Phần trùng lặp còn lại (~`25%` trên R90 `b432`, `928.77/q`; ~`13%` trên R86 A3 `b970`, `660–666/q`):** Chỉ còn duy nhất va chạm **nội round giữa các worker khác nhau** (2 worker độc lập cùng gặp một đỉnh chưa từng thấy trong cùng superstep $S$ trước khi về barrier).
  - **Vì sao Total L2 giảm theo (`−12.2230%` trên G2 R90; `−14.35–14.45%` trên R86 A3):** Bởi vì $\text{Total L2} = \text{Unique L2} + \text{Duplicate L2}$. `Unique L2` bất biến tuyệt đối (`19,064.1601/q` trên G2, $\Delta = 0$), nên loại bỏ `2,784.04` phép tính trùng trực tiếp xóa đúng `2,784.04` phép tính khỏi tổng L2!

### 3.3 A1 (`FrontierMode::kIncremental`) thay đổi điều gì?
- **Cấu trúc beam phẳng tích hợp cờ mở rộng ([p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L301-L304), [#L331-L332](../../../research/task_da/search_common/p2_engine.hpp#L331-L332)):** Dùng `std::vector<FlatEntry> global_best_flat_` với `struct FlatEntry { Hit hit; uint8_t expanded; };`, loại bỏ hoàn toàn `active_frontier_` và giảm tra cứu ngẫu nhiên vào mảng `2 MiB` `global_expanded_epoch_`.
- **Giới hạn gửi hạt giống `max_dispatch = p × S` ([p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L691), [#L944-L948](../../../research/task_da/search_common/p2_engine.hpp#L944-L948), [#L964-L971](../../../research/task_da/search_common/p2_engine.hpp#L964-L971)):** Thay vì đẩy tới `B/p` (`216–485`) hạt giống vào `std::set local_pending` mỗi worker mỗi round, A1 chỉ gửi tối đa `p × S` (`2 × 16 = 32` hạt giống tổng, tức $\le 16$ hạt giống/worker) trực tiếp vào `ws.init_seeds`. Điều này xóa bỏ hàng trăm phép cấp phát nút và cân bằng cây đỏ-đen vô ích mỗi round trên mỗi worker.
- **Gộp 1 lượt & đường tắt khi không có ứng viên mới ([p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp#L900-L976)):**
  - Nếu `!merge_scratch_.empty()`: Gộp tuyến tính 2 mảng, cập nhật cờ `expanded` (chỉ tra `global_expanded_epoch_` với phần tử ở vùng `i <= prev_last_disp`), theo dõi con trỏ `first_unexp` và phát `init_seeds` ngay trong **một vòng quét liên tiếp duy nhất** qua $O(B)$ bộ nhớ.
  - Nếu `merge_scratch_.empty()` (không có ứng viên nào tốt hơn `cur_worst` ở round vừa rồi): Bỏ qua toàn bộ sort/merge, quét tăng dần từ `first_unexp` và dừng sớm ngay khi `dispatched == max_dispatch && i >= prev_last_disp`.

### 3.4 B1+A1 thay đổi luồng traversal tổng thể như thế nào?
- **Lưu ý quan trọng:** `B1+A1` **KHÔNG thay đổi thứ tự mở rộng đỉnh, KHÔNG thay đổi đồ thị, KHÔNG thay đổi điều kiện dừng, và KHÔNG thay đổi tập đỉnh duy nhất được khám phá** so với Baseline (`flat + baseline + full`). Trên toàn bộ `20,000` truy vấn duy nhất (`10,000` test + `10,000` val) — tương ứng `180,000` bản ghi ON mới (`120,000` cặp đối chứng ON base-vs-opt gồm `60k` test + `60k` val vs Stage 5) và `1,440,000` bản ghi OFF (`144/144` đối chứng digest OFF-vs-ON) của G2 `design-3.1` — các bộ đếm `unique_distance_evaluations`, `expansions`, `unique_expansions`, `duplicate_expansions`, `neighbor_attempts`, `frontier_insertions`, và `sync_merge_count` giữa `base` và `opt` có sai khác bằng **`0`** tuyệt đối.
- `B1+A1` chỉ cắt hai nguồn lãng phí thuần túy trong cùng một quỹ đạo tìm kiếm: (1) B1 loại bỏ tính lại L2 xuyên round nhờ công bố visited toàn diện tại barrier; (2) A1 loại bỏ dựng lại toàn bộ frontier và nạp hàng trăm hạt giống thừa vào `local_pending` mỗi round.

---

## 4. Điều kiện bảo toàn tính đúng đắn (Chứng minh bất biến ngữ nghĩa)

**Mệnh đề (Tính tương đương quỹ đạo và đầu ra với Baseline `flat + baseline + full`):** Với mọi đồ thị hữu hạn $G$, query $q$, tham số $k \le B$, $p \in \{2,4\}$, $S \ge 1$, đầu ra `hits` (ID, thứ tự, `squared_l2`) và chuỗi các đỉnh được mở rộng của `B1+A1` trùng khớp tuyệt đối với Baseline.

**Phác thảo chứng minh trực tiếp từ mã (`p2_engine.hpp`):**
1. **Bất biến của B1 (`MarkAllEvaled`):**
   - `global_best` duy trì đúng top-$B$ cặp `(distance, Id)` nhỏ nhất từng thấy, nên ngưỡng xấu nhất `global_worst(r)` là hàm **đơn điệu không tăng** theo số round $r$ kể từ khi `|global_best| == B`.
   - Xét một đỉnh $v$ bất kỳ được tính `squared_l2(v, q)` ở round $r$:
     - Nếu $v$ được đưa vào `local_discovered` ở round $r$, Baseline đã đánh dấu `settled_epoch_[v] = q_epoch` (dòng 879) — hành vi trùng khớp với B1.
     - Nếu $v$ *không* vào `local_discovered` ở round $r$, chỉ có 2 trường hợp (dòng 460–464): (a) `has_full` đúng và `hit(v) >= global_worst(r) >= global_worst(r')` với mọi $r' > r$; hoặc (b) `|local_top| == B` và `hit(v) >= worst(local_top)`, trong khi cả $B$ phần tử tốt hơn trong `local_top` đều đã được đẩy vào `local_discovered` và gộp vào `global_best` ở cuối round $r$, suy ra `global_worst(r+1) <= worst(local_top) <= hit(v)`.
   - Trong cả hai trường hợp, dù ở round $r' > r$ có tính lại $v$ như Baseline, `hit(v)` **không bao giờ** vượt qua dòng 460 (`hit < global_worst`) và không làm đổi `local_top`, `local_pending` hay `global_best`. Do đó đánh dấu `settled_epoch_[v] = q_epoch` ở cuối round $r$ bảo toàn 100% quỹ đạo tìm kiếm.
2. **Bất biến của A1 (`IncFrontier` + `max_dispatch = p × S`):**
   - Trong mỗi round, mỗi worker chỉ lặp tối đa `S` lần (`while (steps < sync_interval_ && !ws.local_pending.empty())`, dòng 431) và mỗi bước luôn pop phần tử nhỏ nhất (`local_pending.begin()`).
   - Khi chia vòng tròn danh sách các đỉnh chưa mở rộng đã sắp tăng dần theo `Hit`, `S` hạt giống đầu tiên cấp cho worker $w$ có khoảng cách nhỏ hơn chặt hạt giống thứ $S+1$ (và mọi hạt giống đứng sau) của cùng worker $w$. Trong quá trình chạy round, các láng giềng mới nạp vào `local_pending` chỉ có thể *làm giảm* hoặc giữ nguyên thứ hạng cần pop; một hạt giống đầu vào chỉ bị trục xuất khỏi `local_pending` nếu có đủ $B$ phần tử tốt hơn (dòng 466–470), khi đó mọi hạt giống thứ $\ge S+1$ cũng lớn hơn nên cũng bị loại.
   - Do vậy, worker $w$ **không bao giờ pop tới hạt giống thứ $S+1$**. Việc chỉ gửi tối đa `p × S` hạt giống (mỗi worker $\le S$) sinh ra tập `local_expanded`, `local_newly_evaled` và `local_discovered` trùng khớp tuyệt đối với Baseline.
   - Ngoài ra, con trỏ `first_unexp` và `prev_last_disp` chỉ cập nhật `expanded = 1` cho các đỉnh ở vị trí `i <= prev_last_disp` (là tập duy nhất có thể đã được gửi và mở rộng ở round ngay trước) và giữ nguyên phần tử mới chèn từ `merge_scratch_` bằng kiểm tra `global_expanded_epoch_[h.second] == q_epoch` (dòng 929).
3. **Kiểm chứng thực nghiệm:** Khớp bit-exact `100%` (ID, thứ tự và `squared_l2`, sai lệch `0`) trên toàn bộ `120,000` cặp đối chứng ON base-vs-opt (`60k` test + `60k` val đối chiếu Stage 5 `b432`, trên `180,000` bản ghi ON mới) và `144/144` tiến trình OFF (`1,440,000` bản ghi OFF đối chiếu digest test ON, `720,000` cặp OFF base-vs-opt) của G2 `design-3.1`, cũng như toàn bộ các lượt pilot/narrow replication trên R86 (`A0`, `A3`).

---

## 5. Quan hệ giảm công ↔ giảm độ trễ, Overhead & Trade-off

### 5.1 Cơ chế đã xác nhận vs Giả thuyết chưa kiểm chứng

| Khía cạnh | Đã xác nhận từ mã & thực nghiệm | Chưa kiểm chứng / Không đo trực tiếp (`UNKNOWN`) |
|---|---|---|
| **Giảm công L2 (B1)** | Giảm `−74.9846%` duplicate L2 (`3712.81 → 928.77/q`) và `−12.2230%` total L2 (`22776.97 → 19992.93/q`) trên G2 R90 (`b432`); giảm `−87.0–87.3%` dup L2 và `−14.35–14.45%` total L2 trên R86 A3 (`b966–986`). | Tỷ trọng chu kỳ CPU riêng biệt (*exclusive cycles*) của L2 so với truy cập ngẫu nhiên bộ nhớ/cache L3/DRAM (`perf_event_paranoid = 4`, PMU **`NOT_MEASURED`**). |
| **Giảm công frontier (A1)** | Trên R86 `A3-R2/R3 p=2 S=16`, A1 đơn lẻ giảm OFF latency `6.50%` và `5.93%` dù **không đổi 1 phép tính L2 nào** — chứng minh rõ chi phí `std::set local_pending` và dựng lại `active_frontier_` là thực tế. | Tách đóng góp riêng giữa *B1 đơn lẻ* và *A1 đơn lẻ* trên bộ đồ thị R90 `b432` (G2 v2 chỉ đo `base` vs `B1+A1` kết hợp). |
| **Tính cộng của B1 & A1** | Trên R86 `A3-R2/R3`, số hạng tương tác `combo − A1 − B1 + base` có `CI95` chứa `0` (`R2: +72.3 [−137.9, +282.6] µs`; `R3: −20.9 [−197.7, +155.8] µs`) — hiệu ứng mang tính cộng tuyến tính, chưa chứng minh siêu cộng hưởng. | Tương tác siêu cộng hưởng ở quy mô beam lớn hơn hoặc CPU nhiều lõi hơn. |
| **Vì sao giảm latency (`6.03%`) nhỏ hơn giảm total L2 (`12.22%`) trên G2?** | (1) Một phần thời gian tường là các phần bất biến không giảm theo B1 (tạo ứng viên, `local_seen`, mở rộng `std::set`, phần merge tuyến tính, đồng bộ barrier, `19,064.16` phép L2 duy nhất). (2) B1 thêm công ghi tuần tự `local_newly_evaled` và ghi ngẫu nhiên `settled_epoch_` tại barrier. (3) G2 dùng `beam = 432` (~`14.87` round/query) nhỏ hơn R86 A3 (`beam = 970`, ~`31.7` round/query), nên lợi ích A1 theo tỷ lệ nhỏ hơn. | Phân rã định lượng chính xác từng micro-giây trong chế độ OFF (ước lượng điểm phase observer `−1.717%` nằm trong `±2%`, nhưng cận dưới `CI95 = −2.851%` nằm ngoài `[−2%, +2%]` → `NOT_VALIDATED_OUTSIDE_EQUIVALENCE_BUDGET`; PMU `NOT_MEASURED`). |

### 5.2 Overhead & Trade-offs
1. **Ghi bổ sung tại barrier (B1):** Mỗi round ghi tối đa $O(p \cdot S \cdot d_{\max})$ ID vào `ws.local_newly_evaled` rồi Worker 0 ghi ngẫu nhiên vào `settled_epoch_` (`2 MiB`, vừa L3 `4 MiB` của CCX0 trên Ryzen 4650U).
2. **Ảo giác tăng `merge_time_ns` trong chế độ ON (`+35.89 µs/q` trên G2, `348.51 → 384.39 µs`):** Trong Baseline, thao tác phân phát `init_seeds` nằm ở *đầu round sau* (dòng 745–752, ngoài cửa sổ `merge_time_ns`), còn trong A1 thao tác đó được gộp *vào bên trong* pha merge (dòng 944–948, nằm trong `merge_time_ns`). Do đó tăng `merge_time_ns` ON là dịch chuyển ranh giới đo, không phải tăng tổng chi phí — thực tế latency OFF vẫn giảm ròng `−218.38 µs/q`.
3. **Giới hạn mở rộng sang `p=4` xuyên CCX:** Trên Ryzen 4650U (`2 × 4 MiB` L3), khi chạy `p=4` (`[0,2,4,6]` vắt qua 2 CCX), pilot R86 R1 cho thấy B1 đơn lẻ chậm nhẹ theo ước lượng điểm (`+1.19%` A0, `+5.93%` A3), mọi `CI95` của `B1+A1` chứa `0`, và `A3-R1 p=4 S=8` bị **tăng `p95` `+5.2%`** (`4402.7 → 4633.1 µs`). Đây là bằng chứng rằng hiệu quả `B1+A1` **phụ thuộc cấu hình `(p, S, kiến trúc cache)`**, không tự động dương ở mọi `p`.
4. **Chi phí RAM:** Gần như bằng `0` (`ΔPeak RSS = +9.39 KiB` trung bình trên `871.7 MiB` ở G2; `72/72` cặp vượt hard gate RAM).

---

## 6. Độ phức tạp thời gian và không gian (Các cận chứng minh được)

Ký hiệu: $n$ số đỉnh, $d$ số chiều vector, $d_{\max}$ bậc ra tối đa (`64`), $B$ kích thước beam (`432` ở G2), $p$ số worker, $S$ chu kỳ đồng bộ (`16`), $R$ số round mỗi query, $M_r \le p \cdot S \cdot d_{\max}$ số láng giềng mới được đánh giá ở round $r$, $C_r \le M_r$ số ứng viên lọt `local_discovered` vượt ngưỡng `cur_worst`.

| Thành phần | Baseline (`flat + baseline + full`) | B1+A1 (`flat + barrier_all_evaled + incremental`) | Ghi chú |
|---|---|---|---|
| **Nạp hạt giống mỗi worker / round** | $O\big(\frac{B}{p}\log\frac{B}{p}\big)$ | $O(S \log S)$ (với $S \ll B/p$) | A1 cắt giảm khi $p \cdot S < B$ (ví dụ $32 \ll 432$ hoặc $32 \ll 970$) |
| **Gộp & dựng frontier tại barrier / round** | $O(C_r \log C_r + B)$ + `O(B)` tra cứu `global_expanded_epoch_` + `O(B)` chép `init_seeds` | Nếu $C_r > 0$: $O(C_r \log C_r + B)$ trong **1 lượt quét**; nếu $C_r = 0$: $O(B - \text{first\_unexp})$ dừng sớm khi đủ $pS$ | A1 giảm số lượt quét bộ nhớ & số truy cập mảng `2 MiB` |
| **Công bố visited tại barrier / round** | $O(C_r + pS)$ (chỉ `discovered` + `expanded`) | $O(M_r + pS)$ (mọi đỉnh đã tính L2) | B1 trả $O(M_r)$ ghi `uint16_t` để tiết kiệm $O(d)$ FLOPs/đỉnh bị tính lại |
| **Số lần tính L2 / query** | $O(U \cdot d + D_{\text{cross}} \cdot d + D_{\text{intra}} \cdot d)$ | $O(U \cdot d + D_{\text{intra}} \cdot d)$ ($D_{\text{cross}} = 0$) | $U$: đỉnh duy nhất; B1 triệt tiêu hoàn toàn $D_{\text{cross}}$ |
| **Không gian phụ trợ phiên (`P2SearchSession`)** | $4n$ byte (2 mảng `uint16_t` epoch) + $O(p \cdot (B + \text{cap}_{\text{seen}}))$ | $4n$ byte + $O(p \cdot (B + \text{cap}_{\text{seen}} + S \cdot d_{\max}))$ | Không đổi tiệm cận bộ nhớ theo $n$; `FlatEntry` thêm `~8 B` (padding) $\times B \approx 3.5\text{ KiB}$ |

> **Ranh giới lý thuyết:** `B1+A1` **không thay đổi độ phức tạp tiệm cận theo $n$** của tìm kiếm ANN trên đồ thị; nó chỉ cải thiện hằng số nhân của công L2 dư thừa ($D_{\text{cross}} \to 0$) và chi phí quản trị frontier theo $(B, p, S)$ trong cùng quỹ đạo tìm kiếm.

---

## 7. Pseudocode đối chiếu (Bám sát `p2_engine.hpp:388–1056`)

```text
ALGORITHM 1: Baseline_Flat_Full(G, X, q, k, B, p, S)        [Flat=1, MarkAll=0, IncFrontier=0]
  q_epoch ← next_query_epoch()
  Expand G.entry on Worker 0; mark settled_epoch_[entry & nbrs] ← q_epoch;
  mark global_expanded_epoch_[entry] ← q_epoch; insert top-B into sorted global_best_vec
  active_frontier ← [h in global_best_vec : global_expanded_epoch_[h.id] ≠ q_epoch]

  WHILE active_frontier is not empty:
    (has_full, global_worst) ← (|global_best_vec| == B, global_best_vec.back())
    Clear worker[0..p-1].init_seeds
    FOR i = 0 .. |active_frontier| - 1:                     // FULL frontier (up to B seeds!)
      worker[i mod p].init_seeds.push(active_frontier[i])

    // PARALLEL SUPERSTEP (Worker 0 + p-1 pinned helpers via work_seq_ / done_seq)
    PARALLEL FOR w = 0 .. p - 1:
      IF worker[w].init_seeds empty: continue
      Reset worker[w].local_seen (O(1) epoch), local_top, local_pending, local_discovered, local_expanded
      Insert ALL worker[w].init_seeds into std::set local_pending   // up to B/p RB-tree inserts!
      steps ← 0
      WHILE steps < S AND local_pending not empty:
        u ← pop_min(local_pending); local_expanded.push(u); steps ← steps + 1
        FOR v in G.neighbors(u):
          IF settled_epoch_[v] == q_epoch OR local_seen.contains_or_insert(v): continue
          dist ← squared_l2_f64(X[v], q); hit ← (dist, v)
          IF has_full AND NOT (hit < global_worst): continue        // REJECTED: NEVER marked settled!
          IF |local_top| < B OR hit < max(local_top):
            Insert hit into local_top, local_pending; local_discovered.push(hit)
            IF |local_top| > B: evict max(local_top) from local_top & local_pending

    // SINGLE-WRITER BARRIER MERGE (Worker 0)
    FOR w = 0 .. p - 1:
      FOR u in worker[w].local_expanded: global_expanded_epoch_[u] ← settled_epoch_[u] ← q_epoch
      FOR hit in worker[w].local_discovered:
        settled_epoch_[hit.id] ← q_epoch                            // ONLY discovered nodes marked!
        IF NOT has_full OR hit < global_best_vec.back(): merge_scratch.push(hit)
    IF merge_scratch not empty:
      Sort & deduplicate merge_scratch; linear 2-way merge with global_best_vec truncated to B
    Rebuild active_frontier by scanning ALL global_best_vec against global_expanded_epoch_
  RETURN first k elements of global_best_vec
```

```text
ALGORITHM 2: Optimized_B1_A1(G, X, q, k, B, p, S)           [Flat=1, MarkAll=1 (B1), IncFrontier=1 (A1)]
  q_epoch ← next_query_epoch(); max_dispatch ← p * S
  Expand G.entry on Worker 0; build sorted global_best_flat of FlatEntry{hit, expanded}
  Dispatch first min(unexpanded, max_dispatch) entries round-robin into worker[w].init_seeds;
  record (dispatched, first_unexp, prev_last_disp)

  WHILE dispatched > 0:
    (has_full, global_worst) ← (|global_best_flat| == B, global_best_flat.back().hit)

    // PARALLEL SUPERSTEP
    PARALLEL FOR w = 0 .. p - 1:
      IF worker[w].init_seeds empty: continue
      Reset local_seen, local_top, local_pending, local_discovered, local_expanded, local_newly_evaled
      Insert worker[w].init_seeds into local_pending                // [A1] at most S seeds/worker!
      steps ← 0
      WHILE steps < S AND local_pending not empty:
        u ← pop_min(local_pending); local_expanded.push(u); steps ← steps + 1
        FOR v in G.neighbors(u):
          IF settled_epoch_[v] == q_epoch OR local_seen.contains_or_insert(v): continue
          dist ← squared_l2_f64(X[v], q); hit ← (dist, v)
          worker[w].local_newly_evaled.push(v)                      // [B1] record ALL evaluated IDs!
          IF has_full AND NOT (hit < global_worst): continue
          IF |local_top| < B OR hit < max(local_top):
            Insert hit into local_top, local_pending; local_discovered.push(hit)
            IF |local_top| > B: evict max(local_top) from local_top & local_pending

    // SINGLE-WRITER BARRIER MERGE (Worker 0)
    FOR w = 0 .. p - 1:
      FOR v in worker[w].local_newly_evaled: settled_epoch_[v] ← q_epoch   // [B1] publish ALL evaled!
      FOR u in worker[w].local_expanded: global_expanded_epoch_[u] ← settled_epoch_[u] ← q_epoch
      FOR hit in worker[w].local_discovered:
        IF NOT has_full OR hit < global_best_flat.back().hit: merge_scratch.push(hit)

    // [A1] FUSED MERGE + INLINE EXPANDED UPDATE + BOUNDED DISPATCH (<= p * S)
    Clear worker[0..p-1].init_seeds; dispatched ← 0; next_first_unexp ← B; next_last_disp ← 0
    IF merge_scratch not empty:
      Sort & deduplicate merge_scratch
      Single-pass 2-way merge(global_best_flat, merge_scratch) → next_best_flat (size <= B):
        Update inline expanded bit (only checking global_expanded_epoch_ when i <= prev_last_disp or new)
        IF entry.expanded == 0:
          Track next_first_unexp; IF dispatched < max_dispatch:
            worker[dispatched mod p].init_seeds.push(entry.hit); dispatched += 1; next_last_disp ← out_idx
      Swap(global_best_flat, next_best_flat)
    ELSE:                                                           // [A1] fast suffix scan!
      FOR i = first_unexp .. |global_best_flat| - 1:
        IF global_best_flat[i].expanded == 0:
          IF i <= prev_last_disp AND global_expanded_epoch_[id] == q_epoch:
            global_best_flat[i].expanded ← 1; continue
          Track next_first_unexp; IF dispatched < max_dispatch:
            worker[dispatched mod p].init_seeds.push(entry.hit); dispatched += 1; next_last_disp ← i
          IF dispatched == max_dispatch AND i >= prev_last_disp: BREAK
    first_unexp ← (next_first_unexp == B) ? |global_best_flat| : next_first_unexp
    prev_last_disp ← next_last_disp
  RETURN first k hits of global_best_flat
```

---

## 8. Định vị khoa học trung thực (Không thổi phồng thành thuật toán mới)

Theo kiểm toán prior art trong [H3_NOVELTY_AND_PRIOR_ART_AUDIT.md](H3_NOVELTY_AND_PRIOR_ART_AUDIT.md) và [POST_STAGE_DE_AUDIT_AND_H3_PIVOT_PLAN.md](POST_STAGE_DE_AUDIT_AND_H3_PIVOT_PLAN.md):
- Đánh dấu visited trước/sau tính khoảng cách đã có trong iQAN (`is_visited`), DiskANN/HNSW song song và ParlayANN.
- Duy trì tập ứng viên phẳng có cờ `checked`/`expanded` nội tuyến và con trỏ phần tử chưa mở rộng đầu tiên đã có trong NSG, DiskANN, iQAN và GINGER (§4.3).
- Do đó, **`B1+A1` là một tối ưu kỹ thuật hệ thống / vệ sinh đường cơ sở (*baseline engineering hygiene optimization*) có chứng minh bảo toàn ngữ nghĩa tuyệt đối**, giúp làm sạch đường cơ sở đa walker BSP và mang lại cải thiện thực đo tái lập được (`−6.033%` trên G2 R90 cố định, `−10.08%` đến `−12.29%` theo từng build trên R86 A3) — **không phải là phát minh thuật toán tìm kiếm ANN mới**.
