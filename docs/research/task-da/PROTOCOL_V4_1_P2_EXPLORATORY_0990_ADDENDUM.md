# Task D × Task A — Addendum Đề Xuất Mở P2/H1/H2 Exploratory ở Ngưỡng `Recall@10 >= 0.990`

- **Document Status:** **`SCOPED_OWNER_APPROVED_P2_EXPLORATORY_0990_ONLY`** *(Owner Decision 2026-11-18; chỉ mở P2 Exploratory tại `Recall@10 >= 0.990` theo `P2-EXP-1..4`.)*
- **Date:** 2026-11-18
- **Purpose:** Tách riêng quyền chạy thăm dò (**P2 Multi-Walker Correctness + Pilot H1/H2 ở ngưỡng `Recall@10 >= 0.990`**) ra khỏi trạng thái chặn của `Full P1 Gate` và ngưỡng `0.998`, tuân thủ Stage 0 Hard Gate trước khi viết hoặc benchmark bất kỳ mã đa luồng nội-truy-vấn nào.

> [!IMPORTANT]
> **Ràng buộc phạm vi phê duyệt (Owner Decision 2026-11-18):**
> - Chỉ phê duyệt `P2-EXP-1..4` (`p = 1, 2, 4` intra-query multi-walker + correctness + exploratory H1/H2 tại `Recall@10 >= 0.990`).
> - **Không** tự chuyển `Historical P0`, `Full P1 Gate`, hoặc `t0998 (0.998)` từ `HOLD` sang `PASS`.
> - **Không** xem đây là phê duyệt `Protocol V4 (D1–D5)` hay `P3 official`; [P1_V4_APPROVAL_CHECKLIST.md](P1_V4_APPROVAL_CHECKLIST.md) giữ nguyên trạng thái chưa ký `D1–D5`.
> - **Không** mở `TP-CG / H3`.
> - Mọi ghi chú số như `A3 ~960` bên dưới chỉ là minh họa lịch sử; mọi `beam(G, p)` bắt buộc phải hiệu chỉnh thực nghiệm lại trên `val_10k` theo Điều khoản 2a (tuyệt đối không dùng `test_90k` để chọn hay chỉnh `beam`).
> - Trên `thinhbui-linux` (`Ryzen 5 PRO 4650U`), kết quả H1/H2 nếu chạy được đánh dấu bắt buộc **`EXPLORATORY_HOST_SPECIFIC`** và **tách biệt hoàn toàn** khỏi máy target `i5-14600KF 32 GB RAM`.

---

## 1. Trạng thái bảo toàn nguyên vẹn (`OBSERVED`, không thay đổi khi duyệt Addendum này)

| Hạng mục | Trạng thái bảo toàn | Bằng chứng gốc giữ nguyên |
|---|---|---|
| **Historical P0 (Preregistration v1)** | **`HOLD`** | Thiếu runtime CLI seed trong receipts Task A (`SEED=555` + `PARLAY_NUM_THREADS=4`), thiếu telemetry nhiệt/governor gốc trên `tai-linux`, phần cứng `thinhbui-linux` (`Zen2 AVX2`) khác `tai-linux` (`AVX-512`). |
| **P1 V3 Correctness & ON/OFF Parity (`workers=1`)** | **`PASS`** | `1,804,000 / 1,804,000` cặp `ON/OFF` khớp tuyệt đối (`0` lệch), `0` incomplete top-10, determinism `--jobs 1` == `--jobs 6` khớp SHA-256. |
| **P1 V3 Quality Calibration (`t0990 = 0.990`)** | **`9 / 9 PASS` (V3)** | `A0` (`416`: `0.991133–0.991206`), `A1` (`416`: `0.991138–0.991223`), `A3` (`896, 928, 896`: `0.990041, 0.990730, 0.990129`) trên `test_90k`. |
| **P1 V3 Quality Calibration (`t0998 = 0.998`)** | **`2 / 9 PASS, 7 / 9 FAIL` (`HOLD`)** | Bị chặn theo V3 (`A0/A1@896`, `A3_r1@2176`, `A3_r3@2112` < `0.998`); giữ nguyên trạng thái `HOLD` và **nằm ngoài phạm vi addendum này**. |
| **Full P1 Gate (`0.990 + 0.998`)** | **`HOLD`** | Không nâng trạng thái Full P1 Gate bằng addendum exploratory `0.990`. |
| **P3 Chính thức / Cross-host Task A QPS** | **`CLOSED`** | Cấm mọi so sánh QPS/latency trực tiếp giữa Task D và kết quả Task A trên `tai-linux`. |
| **TP-CG (Scheduler mới / H3)** | **`NOT_OPENED`** | Tuyệt đối chưa thiết kế, chưa triển khai và chưa đánh giá trong phạm vi P2/H1/H2. |

---

## 2. Cơ sở đề xuất & điều kiện biên cho `Recall@10 >= 0.990` (`PROPOSED`)

1. **Tái xác nhận các giới hạn hiện tại trên mã nguồn (`OBSERVED`):**
   - Trong `research/task_da/search_common/p1_eval.cpp`, `--jobs N` (`query_batch_jobs`) chỉ chạy song song **liên-truy-vấn (inter-query)** trên bể luồng ngoài `evaluate_queries`, hoàn toàn **không phải** `p` intra-query workers.
   - E3 role-switch (`origin/codex/e3-phase-aware-adaptation`, `c6cc91b1`, GPL-3.0) là bộ tách vai maintainer/calculator có mutex toàn cục và cyclic-ID seeding; theo [SOURCE_AUDIT.md](SOURCE_AUDIT.md) và [engine_parity_audit.md](engine_parity_audit.md), **không dùng E3 thay thế hay giả lập P2 multi-walker MIT**.
2. **Xử lý biên an toàn cho `A3` tại `0.990` trước khi chạy `p > 1` (`PROPOSED`):**
   - Trong V3, `A0/A1` (`beam=416`) đã qua cả `val_10k LCB95` lẫn `test_90k` (`0.99113–0.99122`, dư `> +0.0011` trên `0.990`).
   - Ngược lại, ở V3 `A3_r1@896` (`0.990041`) và `A3_r3@896` (`0.990129`) bám rất sát ngưỡng `0.990` (`+4.1e-5` và `+1.29e-4`) nên khi đổi thứ tự duyệt ở `p=2,4`, chất lượng có thể rớt nhẹ dưới `0.990`. Do đó đề xuất một trong hai điều khoản rõ ràng khi phê duyệt:
     - **Điều khoản Beam 2a (Khuyến nghị):** Chốt `beam` của `p=1` theo quy tắc V4 `LCB95` trên `val_10k` (giữ `A0/A1 = 416`, đẩy `A3` lên `~960` qua `val_10k` LCB95), rồi với `p=2,4` dùng `beam(p)` được chọn chỉ trên `val_10k` (không tuning trên `test_90k`) để bảo đảm `Recall@10 >= 0.990` tương đương giữa `p=1,2,4`; **hoặc**
     - **Điều khoản Beam 2b:** Khảo sát ở fixed V3 `416` (`A0/A1`) và `896/928/896` (`A3`), nhưng nếu bất kỳ cấu hình `(graph, p)` nào có `Recall@10 < 0.990` hoặc chênh lệch vượt ngưỡng matched-Recall `> 0.0001` theo [PRE_REGISTRATION.md](PRE_REGISTRATION.md), **bắt buộc gắn nhãn `NOT_COMPARABLE`** và không kết luận speedup.

---

## 3. Hợp đồng kỹ thuật bắt buộc cho Giai đoạn 1–5 (chỉ kích hoạt sau phê duyệt)

### 3.1 Thiết kế P2 Multi-Walker (`p in {1, 2, 4}` trên cùng 1 truy vấn)
- Kế thừa `task_da::Index` (MIT license, giữ nguyên hành vi `p=1` `entry_best_first_v1` không regression, tách nhánh/commit rõ ràng, không ghi đè evidence P1).
- Tài liệu thiết kế trước khi benchmark phải cố định rõ:
  1. **Frontier & Queue Ownership:** Cấu trúc queue cục bộ theo worker và cơ chế chia sẻ/steal/merge để kiểm soát trùng lặp và cân bằng tải.
  2. **Visited / Claim Ownership:** Cấu trúc đánh dấu phát hiện (`discovered/claimed` vs `expanded`), phân biệt rành mạch `already_seen_attempts` (gặp lại cung trỏ vào đỉnh đã phát hiện) với **`duplicate_expansions`** (nhiều worker thực sự pop và duyệt cùng một đỉnh nếu thiết kế cho phép hoặc race claim).
  3. **Synchronization & Termination:** Cơ chế kết thúc không deadlock/livelock khi đủ `beam` và toàn bộ pending/in-flight trống, hợp nhất top-k cuối cùng xác định theo `(squared_l2, id)`.
  4. **Instrumentation Separation:** Template tách `search<false>` (OFF đo thời gian, không ghi counter nội vòng) vs `search<true>` (ON thu thập counter). Trong timing runs P2/H1 (`OFF`), **ép `--jobs 1` liên-truy-vấn** (chạy tuần tự từng query với `p` intra-query workers) để `p` phản ánh đúng số luồng xử lý nội-truy-vấn, không cộng chồng với inter-query threads.

### 3.2 Cổng Correctness Bắt Buộc Trước H1/H2 (`Gate-Before-Timing`)
Không đo latency/speedup nếu một trong các bước sau chưa PASS:
1. **Unit & Exact Oracle Tests:** Kiểm thử trên graph nhỏ có oracle brute-force (`p=1,2,4`), đồ thị không liên thông, hòa khoảng cách (`tie-break`), không pad ID giả.
2. **Sanitizers & Race Check:** `ASan + UBSan` và `TSan` (ThreadSanitizer nếu toolchain hỗ trợ; ghi nhận rõ nếu môi trường giới hạn) trên các ca `p=2, 4` đa luồng không có data race, UAF hay deadlock.
3. **Real-Graph Smoke (`~500` queries trên `A0-R1` & `A3-R1`):** Kiểm tra `100% complete top-10`, ID hợp lệ `[0, 1000000)`, lặp lại nhiều lần ổn định, **`ON/OFF` parity** về tính đúng đắn bất biến counter (riêng `p=2/4` không bắt buộc khớp IDs với `p=1` nếu lịch trình duyệt khác, nhưng phải giữ nguyên chất lượng `>= 0.990` và nhất quán cấu trúc output giữa `ON`/`OFF`).
4. **Cập nhật Counter Schema V2 cho Multi-Walker:** Không áp nguyên công thức bảo toàn đơn-luồng (`distance_evaluations == 1 + neighbor_attempts - already_seen_attempts`) nếu mô hình bất đồng bộ cho phép concurrent discovery/duplicate expansion; phải định nghĩa công thức bất biến chính xác cho từng loại counter.

### 3.3 Thiết kế Pilot H1 & H2 (`EXPLORATORY`)
- **Tập dữ liệu & Phân tách Query:** Sử dụng MS-Turing-1M (`base.1M.fbin`, `query.public.100K.fbin`, `groundtruth.public.100K.ibin`, `--gt-aux-min -1e-5`). Trích một tập cố định `2.000–5.000` queries từ `test_90k.ids` (ghi danh sách IDs và SHA-256 trước khi chạy). **Bắt buộc ghi nhãn mọi kết quả là `EXPLORATORY` (không phải unseen confirmatory) vì `query.public.100K` và `test_90k` đã từng được quan sát trong Task A và P1.**
- **Phạm vi Pilot khởi đầu:** Ưu tiên `A0-R1` và `A3-R1` × `p ∈ {1, 2, 4}`; mở rộng `A1-R1` (tách H17 khỏi C/K) khi 2 cấu hình đầu ổn định; sau đó mới xét `R2/R3`.
- **H1 Latency & Scaling (`Mode OFF`):**
  - Warmup cố định (ví dụ `100` queries từ `val_10k`), xen kẽ thứ tự `(graph, p)` (`p=1,2,4`), tối thiểu `>= 5` process-level repeats trên từng cấu hình, báo cáo per-query `p50/p95` latency, QPS ở `concurrency=1`, `Speedup = T(G,1)/T(G,p)`, `Efficiency = Speedup/p`, độ lệch giữa `A0/A1/A3` và khoảng bất định (`95% CI / dispersion`).
  - Không suy diễn kết luận nhân quả nếu thiếu `A1-R1` hoặc bị confounding chất lượng (`NOT_COMPARABLE`).
- **H2 Overhead & Work Diagnostics (`Mode ON` riêng biệt):**
  - Thu thập đầy đủ: `distance_evaluations/query`, `total_expansions`, `unique_expansions`, `duplicate_expansions` thực sự (tách biệt với `already_seen_attempts`), `per_worker_expansions` & `workload_imbalance`, `sync/merge_count`, `sync/queue wait time`, `worker_idle` (nếu đo đáng tin; nếu không thì ghi `NOT_MEASURED`), `frontier overlap/useful progress`.
- **Hardware & Topology Preflight:**
  - Chạy và ghi lại `lscpu`, `lscpu -e`, `free -h`, host profile, affinity, kernel, compiler, flags, SHA binary và nhiệt/tần số (nếu đọc được).
  - **Quy tắc affinity theo phần cứng thực tế:** Trên `thinhbui-linux` (`Ryzen 5 PRO 4650U`, 6 physical cores / 12 SMT threads, 2 CCX L3), cặp `CPU 0,1`, `2,3`, `4,5`, `6,7`, `8,9`, `10,11` là các anh em SMT; nếu chạy trên **i5-14600KF**, bắt buộc kiểm tra `lscpu -e` trước để xác định đúng CPU IDs của `1/2/4` **P-cores vật lý tách biệt**, không giả định mù quáng `0,2,4,6`. GPU không tham gia.

---

## 4. Trạng thái phê duyệt từ người phụ trách (2026-11-18)

| Mục | Nội dung phê duyệt | Trạng thái đã xác nhận |
|---|---|---|
| **P2-EXP-1** | Cho phép mở **P2 Exploratory** chỉ tại ngưỡng **`Recall@10 >= 0.990`** (`P0`, `t0998`, `Full P1 Gate`, `P3`, `TP-CG` giữ nguyên `HOLD/CLOSED/NOT_OPENED`) | `[x] APPROVE` (Owner Decision 2026-11-18) |
| **P2-EXP-2** | Quy tắc chọn `beam` cho `p=1,2,4` ở `0.990` | `[x] Điều khoản 2a` (Hiệu chỉnh thực nghiệm trên `val_10k` bằng `LCB95_q >= 0.990` cho từng `(graph, p)`; **không** hardcoded `A3=960`, **không** dùng `test_90k` để chọn beam) |
| **P2-EXP-3** | Môi trường thực thi & số queries Pilot H1/H2 (`2.000–5.000` queries từ `test_90k.ids`, nhãn `EXPLORATORY`) | `[x] thinhbui-linux (Ryzen 5 PRO 4650U)` *(Impl, correctness, smoke & mọi pilot H1/H2 đánh dấu **`EXPLORATORY_HOST_SPECIFIC`**; tách biệt `i5-14600KF 32 GB RAM`)* |
| **P2-EXP-4** | Cho phép triển khai Giai đoạn 1–2 (code MIT `p=1,2,4` multi-walker + correctness tests) trước khi đo Giai đoạn 3–4 | `[x] AUTHORIZED` (Hard Gate correctness trước mọi đo đạc H1/H2) |
