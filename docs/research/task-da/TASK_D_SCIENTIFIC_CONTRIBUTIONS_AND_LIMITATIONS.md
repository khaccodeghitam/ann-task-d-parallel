# Task D · Đánh giá Trung thực Đóng góp Khoa học & Giới hạn

Tài liệu này đánh giá trung thực giá trị học thuật, đóng góp kỹ thuật và các ranh giới chưa đạt của Task D sau khi đóng kết G2 v2 (`design-3.1`). **Định vị học thuật chuẩn xác:** nghiên cứu Task D là sự kết hợp của **nghiên cứu thực nghiệm hệ thống (*experimental systems research*)**, **tối ưu kỹ thuật đường cơ sở (*engineering optimization / baseline hygiene*)**, **nghiên cứu kết quả âm có phạm vi (*negative-result study*)** và **nghiên cứu khả năng tái lập (*reproducibility study*)**. **Nguyên tắc cốt lõi:** *không biến một tối ưu kỹ thuật hệ thống thành "thuật toán mới" chỉ bằng cách đổi tên*, và *không che giấu các giới hạn về suy rộng, phần cứng hay công cụ đo*.

---

## 1. Năm trụ cột đóng góp có bằng chứng vững chắc

### 1.1 Đóng góp khảo sát & hệ thống hóa tri thức (Survey Contribution)
- Xây dựng **hệ phân loại thực thi song song & lập lịch cho ANN (`D01–D10`)** xuyên suốt 3 cụm độc lập: **Cụm 1** (Multi-core Graph Traversal: Speed-ANN, iQAN, ParlayANN, AverSearch), **Cụm 2** (CPU–SSD Pipeline Scheduling: DiskANN, PipeANN, LAANN, PageANN, Starling, SPANN) và **Cụm 3** (GPU Data Parallelism: FAISS GPU, CAGRA, FusionANNS, Hitcher).
- Thực hiện **kiểm toán prior art ở mức cơ chế và mã nguồn** ([H3_NOVELTY_AND_PRIOR_ART_AUDIT.md](H3_NOVELTY_AND_PRIOR_ART_AUDIT.md), [02_UPSTREAM_EVOLUTION_2025_2026.md](../paper-rebaseline-20261012/02_UPSTREAM_EVOLUTION_2025_2026.md)), chỉ rõ sự đẳng cấu toán học giữa mục tiêu giảm overlap 1-hop với bài toán phân hoạch siêu đồ thị `connectivity-1` của Çatalyürek & Aykanat (1999), và chỉ rõ chồng lấn cơ chế với Speed-ANN, iQAN, AverSearch, ADSampling, FINGER và GINGER — ngăn chặn hiệu quả việc "tái phát minh thuật toán đã có".

### 1.2 Đóng góp về phương pháp luận benchmark & kiểm định thực nghiệm (Benchmark Methodology Contribution)
Đây là một trong những đóng góp nổi bật và khác biệt nhất của Task D:
- **Kỷ luật tách bạch tuyệt đối:** Tách hoàn toàn *Timing OFF* khỏi *Counter ON* (kiểm tra parity bit-exact trên `1,804,000` cặp ON/OFF ở P1 và trên toàn bộ cohort G2 v2: `20,000` truy vấn duy nhất [`10k` test + `10k` val], `1,620,000` bản ghi thực thi [`1,440,000` OFF + `180,000` ON mới], `120,000` cặp đối chứng ON base-vs-opt và `144/144` process OFF khớp digest), tách *paper-reported* khỏi *native measured*, và tách *đồ thị/môi trường cũ* khỏi *chiến dịch chính thức*.
- **Phát hiện & giải quyết các bẫy đo lường thực tế:**
  1. Phát hiện xung đột ghim luồng `OMP_PROC_BIND=spread` với `iou-sqp` (`107` vs `3,288 QPS`) và xây dựng hợp đồng nhiệt/công suất **Custom Full-Fan `60/90 W`** ([EXPERIMENTAL_ENVIRONMENT_V1.md](../../EXPERIMENTAL_ENVIRONMENT_V1.md)).
  2. Chẩn đoán *winner's curse* trong hiệu chỉnh beam không biên (`P1.5`) và sự bất khả thi thống kê của ngưỡng `span <= 0.0001` ở `N=3,000` (`P=0.03%`, Stage 6), thay thế bằng quy tắc đảm bảo thống kê đồng thời (`z = 4.2279` khi chọn beam trên `val_10k`, `LCB95` đồng thời `z = 2.394` ở Gate A, kiểm định tương đương `±0.0005` ở Gate B).
  3. Chẩn đoán tự nhiễu của bộ giám sát (`design-2` quét `/proc` 2 lượt + clamping bias `5×`), thiết kế bộ bảo vệ nhiễu tách CCX (`design-3`) + chứng minh bằng Qualification `900s` + kỷ luật **fail-closed `HOLD`** khi timer `snap.firmware-updater` kích hoạt ở lượt #120/144 (không gộp/vá dữ liệu, chạy mới trọn vẹn `144/144` ở `run2`).
  4. Bác bỏ các phép cộng timer không độc lập gây residual âm (`−196 µs`) và áp dụng cổng tương đương `±2%` yêu cầu **toàn bộ `CI95`** nằm trong `[−2%, +2%]` (giúp phát hiện và gắn nhãn `NOT_VALIDATED_OUTSIDE_EQUIVALENCE_BUDGET` cho phase observer vì cận dưới `CI95 = −2.851%` rơi ngoài biên dù ước lượng điểm `−1.717%` nằm trong `±2%`, [MEASUREMENT_VALIDITY_AND_PHASE_AUDIT.md](MEASUREMENT_VALIDITY_AND_PHASE_AUDIT.md)).
- **Kỷ luật kết quả âm (*Negative-Result Governance*):** Bảo lưu và công bố minh bạch toàn bộ các quyết định `NO-GO` / `HOLD` / `PIVOT` (E0, E2, PipeANN H-G/H-QV1/H-V/H-F, P1 `t0998`, TP-CG, H3 Overlap) thay vì chọn lọc chạy đẹp.

### 1.3 Đóng góp kỹ thuật hệ thống của `B1+A1` (Technical Engineering Contribution)
- Triển khai cặp tối ưu sạch, **không khóa/không atomic trong pha worker**, **bảo toàn 100% quỹ đạo và đầu ra bit-exact** trong engine BSP đa walker (`p2_engine.hpp`, `f2cd634`):
  - **B1 (`barrier_all_evaled`)**: ghi phẳng toàn bộ đỉnh đã tính L2 để công bố vào `settled_epoch_` tại barrier đơn luồng, triệt tiêu 100% tính lại L2 xuyên round.
  - **A1 (`incremental`)**: gộp cờ `expanded` vào mảng beam phẳng `FlatEntry`, hợp nhất merge + dispatch 1 lượt, giới hạn cấp phát `p × S` hạt giống giúp giảm nạp `std::set local_pending` từ $O((B/p)\log(B/p))$ xuống $O(S\log S)$.
- Hiệu quả được kiểm toán chặt chẽ ở G2 `design-3.1 run2` (`144/144` OFF + `18/18` ON): giảm **`74.98%`** duplicate L2, giảm **`12.22%`** total L2, giảm **`6.033%`** mean latency OFF (`CI95 [5.977%, 6.090%]`, `1.0642×`), cải thiện cả `P50/P95/P99` (`−6.01% / −4.22% / −4.09%`), và giữ Peak RSS không đổi (`+9.4 KiB`).

### 1.4 Đóng góp tích hợp BUILD–SEARCH liên nhóm (Task A × Task D Integration Contribution)
- Chứng minh thực nghiệm sự đối lập quan trọng giữa hai cách tăng tốc BUILD của Task A:
  - **Cắt cấu trúc `C/K` (`R86 A3`)**: giảm BUILD `−31.6%` nhưng làm giảm nghiêm trọng serial QPS (`−31%` đến `−39%`), cần beam gấp `2.3×`, và tạo tương tác bất lợi với parallel scaling ở một số cấu hình (`Stage D`).
  - **Giữ nguyên topology `C160/K1024/N2` + prefilter FP32 (`R90 Fast v2`):** tách bạch rõ 3 tầng kết quả:
    1. **Measured BUILD (Host A):** giảm `42.257 → 33.793 s` (`−8.463 s`, **`−20.03%`**).
    2. **Measured SEARCH (Host D):** giữ tương đương Recall@10 (Gate B PASS), trung tính về Search latency (`+0.33/+0.37 µs`, CI chứa 0), và **không phát hiện tương tác có ý nghĩa thống kê với `B1+A1`** (`Fast_gain − Stock_gain = +0.037 µs`, `CI95 [−2.582, +2.655] µs`, log `[−0.000734, +0.000766]` — bị chặn chặt quanh 0 và tương thích với mô hình xấp xỉ cộng tính; *không* diễn giải CI chứa 0 thành chứng minh tương tác bằng 0 tuyệt đối hay độc lập hoàn toàn).
    3. **Modeled Two-Host BUILD–SEARCH:** mô hình cộng ghép 2 máy (loại trừ truyền tải/nạp chỉ mục) dự báo tiết kiệm thời gian ở mọi quy mô truy vấn `Q ≥ 1` (`ΔT = 30.34 s` @ `Q=100k`, `227.19 s` @ `Q=1M`).

### 1.5 Đóng góp về khả năng tái lập & lưu trữ khoa học (Reproducibility Contribution)
- Toàn bộ giao thức, schema, lockfile Python (`--require-hashes`), mã kiểm toán độc lập ([audit_g2_v2_design3_1_final.py](../../../scripts/audit_g2_v2_design3_1_final.py)) và các gói đóng băng (`design-3.1` `29/29`, `design-3` `26/26`, `design-2` `24/24`) đều được ghim SHA-256.
- Toàn bộ bằng chứng G2 (`Tier 1 Core`, `Tier 2 Forensic`) cùng các phụ thuộc nhị phân dự án (`6` đồ thị R90 TAR + binary `task_da_p2_eval`) đã được lưu trữ tại PRIVATE GitHub Release `axd-g2-v2-design3.1-closeout-20261125` (`9/9` assets) và kiểm chứng round-trip SHA-256 thành công (`0` sai lệch).

---

## 2. So sánh trung thực với Prior Art & Vì sao KHÔNG gọi `B1+A1` là "thuật toán mới"

| Tiêu chí | Phương pháp đã khảo sát (Prior Art) | Task D `B1+A1` | Kết luận định vị |
|---|---|---|---|
| **Đánh dấu đỉnh đã thăm** | iQAN (`is_visited` trước tính khoảng cách), DiskANN/HNSW song song (atomic bitset), ParlayANN (visited hash/bitset) | `B1`: ghi `local_newly_evaled` trong pha worker rồi cập nhật `settled_epoch_` ở single-writer barrier | **Biến thể kỹ thuật sạch không atomic** trong mô hình BSP, không phải khái niệm mới về visited tracking |
| **Quản lý frontier phẳng & cờ mở rộng** | NSG, DiskANN (`nk` first-unchecked), iQAN (pool `S` + cờ `checked`), GINGER §4.3 (flat beam + explored bit + first-unexplored pointer) | `A1`: `FlatEntry{hit, expanded}` + con trỏ `first_unexp` + chặn gửi `p × S` hạt giống | **Kỹ thuật chuẩn mực (*baseline hygiene*)** để bỏ nút cổ chai dựng lại frontier và nạp thừa vào `std::set` |
| **Thay đổi quỹ đạo tìm kiếm / tiệm cận** | Speed-ANN / iQAN (AUP sync), AverSearch (speculative async), ADSampling / FINGER (giảm chiều/lọc sớm), CAGRA (GPU) | **Giữ nguyên 100% quỹ đạo, `unique L2`, `expansions`, và độ phức tạp tiệm cận theo $n$** | **Không tạo thuật toán duyệt đồ thị mới** — giá trị nằm ở tính bảo toàn tuyệt đối và kiểm chứng thực nghiệm nghiêm ngặt |

**Năm lý do trực diện khiến bằng chứng hiện có CHƯA đủ (và KHÔNG nên) gọi `B1+A1` là thuật toán mới:**
1. Hai thành phần cốt lõi (visited marking cho mọi đỉnh đánh giá; flat sorted beam + inline `expanded` bit) đều đã xuất hiện rộng rãi trong prior art (iQAN, NSG, DiskANN, GINGER).
2. `B1+A1` không đề xuất mô hình toán học mới về duyệt đồ thị, không thay đổi độ phức tạp tiệm cận, và không thay đổi cấu trúc đồ thị.
3. Chưa có đối chứng native ngang hàng với các engine C++ mạnh của tác giả khác (ParlayANN, iQAN gốc, DiskANN in-memory, HNSWlib).
4. Hiệu quả đo được ở `p=2` là `6.03%` (R90 `b432`) / `10–12%` (R86 `A3 b970`) nhưng chưa chứng minh được cải thiện dương ổn định ở `p=4` xuyên CCX.
5. Tự đổi tên một tối ưu *baseline hygiene* thành "thuật toán mới" sẽ vi phạm trực tiếp tinh thần trung thực của [RESEARCH_PHILOSOPHY.md](../../../RESEARCH_PHILOSOPHY.md) và dễ bị phản biện học thuật bác bỏ ngay ở vòng đọc đầu tiên.

---

## 3. Các giới hạn cốt lõi cần trao đổi thẳng thắn với giảng viên

1. **Giới hạn cohort cố định & phân biệt 4 họ CI (`graph_population_ci = NOT_ESTIMABLE`):** Cả 6 đồ thị R90 v1.3 (và 9 đồ thị R86 trước đó) đều dùng chung `SEED = 555` cứng trong mã Task A (`pipnn.h:498`), sự khác biệt giữa `r1/r2/r3` chỉ sinh từ bất định lịch trình 4 luồng. Ba khoảng tin cậy tính được trong G2 — **Primary block-$t$ (`df=11`) `[5.977%, 6.090%]`** (kèm Drift `df=5` `[5.991%, 6.075%]`), **Query-only bootstrap (`10k`) `[5.970%, 6.096%]`**, và **Joint bootstrap (`10k`) `[5.954%, 6.113%]`** — chỉ định lượng bất định lặp thực thi và/hoặc lấy mẫu truy vấn trên 6 đồ thị cố định, **hoàn toàn không phải** suy rộng quần thể đồ thị (**`graph_population_ci = NOT_ESTIMABLE`**).
2. **Giới hạn 1 host, 1 dataset, 1 điểm vận hành (`EXPLORATORY_HOST_SPECIFIC`):** Toàn bộ G2 v2 chỉ đo trên `AMD Ryzen 5 PRO 4650U` (`schedutil`), `MS-Turing-1M` (`1M × 100D`), tại `(p=2, S=16, beam=432, jobs=1)`. Chưa kiểm chứng cross-host (`Intel Core i5-14600KF = NOT_RUN`), chưa kiểm chứng dataset thứ 2 (SIFT10M/Deep10M) hay quy mô `10M` (`R91/G3 NOT_OPENED`), và chưa đo concurrent serving (`jobs > 1`).
3. **Mô hình BUILD–SEARCH hai máy chưa phải đo đầu–cuối 1 máy:** Thời gian BUILD lấy từ biên nhận lịch sử Host A (`tai-linux` AVX-512), thời gian SEARCH đo trên Host D (`Ryzen` AVX2), chưa tính truyền tải/nạp chỉ mục (`~3.9 s`) và không gồm phương sai BUILD hạt giống mới.
4. **Chưa có phân rã phần cứng PMU và năng lượng:** `perf_event_paranoid = 4` chặn `perf stat`, cảm biến RAPL rỗng (`0` mẫu), nên phân rã chu kỳ CPU/cache độc quyền (L2 vs bộ nhớ) và tiêu thụ năng lượng đều ở trạng thái **`NOT_MEASURED`**.
5. **Chưa tách riêng ablation `B1-only` vs `A1-only` trên R90** (chỉ có ablation tách riêng trên R86 `A3`), và **tập truy vấn `v2_test_10000.ids`** tuy rời rạc với `val_10k` và các panel 3k cũ nhưng vẫn trích từ `public 100K` từng xuất hiện trong chuỗi R86/P1 (không gọi là "fresh blind holdout tuyệt đối").
6. **Cụm 2 và Cụm 3 dừng ở mức khảo sát (`SURVEY COMPLETE`):** Nếu báo cáo bao trùm cả 3 cụm, cần trình bày rõ Cụm 2 (sau PipeANN baseline) và Cụm 3 (GPU) là nền tảng khảo sát & định vị khoảng trống, còn đóng góp thực nghiệm sâu tập trung ở Cụm 1 (multi-core traversal) và tích hợp Task A × Task D.
