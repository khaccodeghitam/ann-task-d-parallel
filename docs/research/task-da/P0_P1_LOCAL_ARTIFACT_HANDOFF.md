# Task D × Task A — Bàn giao kiểm kê artifact P0/P1 tại máy Linux

**Ngày:** 2026-11-15. **Phạm vi:** thu hồi bằng chứng và smoke correctness, **không** phải benchmark, không thay main. Tham chiếu: [manifest](experiment_manifest.yaml), [tiền đăng ký](PRE_REGISTRATION.md), [format](graph_format_contract.md), [P1 report](GRAPH_COMPATIBILITY_REPORT.md), [hướng dẫn](README.md).

## Những gì đã xác minh từ xa

- Draft PR #57, nhánh `research/task-d-a-p0-p1-20261115`, commit gốc `7c8cb0aab8832ef780f96c8522681663691d8068` vẫn chưa merge tại thời điểm kiểm tra.
- GitHub Actions workflow **Research synthetic checks** cho commit gốc đã báo `success`. Kết quả này **không** chứng nhận real-artifact P0/P1.
- Snapshot `nuyntai19/ann-task-a-research` ref `2558e018c71f412b4e4e4eddb79264c7ce6ac730` là *source-only*. Kiểm tra cây Git trên ref này không tìm thấy 9 graph OFF hay base/query/GT MS-Turing-1M.
- Bản DOCX người dùng mới đính kèm với hậu tố `(2)` có SHA-256 `a7aef4ba2ed867ed8799f72baec463ab5bd59c6fbdd190327d38b6953b260b45`, trùng bản đề xuất đã ghim trong manifest. **Không suy ra bản `(1)` tồn tại hay trùng byte.**
- Thư mục `/home/thinhbui/Documents/ChatGPT` trên host người dùng **không truy cập được từ phiên ChatGPT hiện tại**. Kết quả tìm kiếm Drive chưa xác nhận sự hiện diện của graph binaries. Tình trạng host phải được kiểm tra độc lập.

## Prompt giao agent chạy trên máy Linux

> Bạn là research-reproducibility agent cho Task D × Task A, thực thi **ngay trên máy Linux của người dùng**, có quyền đọc `/home/thinhbui/Documents/ChatGPT`. Mục tiêu duy nhất: khôi phục và **xác minh read-only** artifact để có thể đóng các điều kiện P0/P1; không tự triển khai multi-walker, không chạy P3 benchmark.
>
> 1. Xác định repo Task D bằng cách tìm trong `/home/thinhbui/Documents/ChatGPT`; đường dẫn dự kiến là `/home/thinhbui/Documents/ChatGPT/Research ANN/task-d`. Kiểm tra `git status`, branch, HEAD, PR #57 trước khi thao tác. **Không checkout đè file, không reset/clean/merge, không commit lên main và không sửa branch nếu có uncommitted work của người khác.** Nếu cần lưu tài liệu, làm trên nhánh nghiên cứu của PR và báo rõ commit.
> 2. Đọc **nguyên bản** `docs/research/task-da/experiment_manifest.yaml`, `README.md`, `PRE_REGISTRATION.md`, `graph_format_contract.md`, `SOURCE_AUDIT.md`, `NEXT_STEPS.md`. Manifest thực tế là JSON hợp lệ. Không bịa đường dẫn/seed/source revision.
> 3. Kiểm kê an toàn các candidate files trên `/home/thinhbui/Documents/ChatGPT` và trong mounts được người dùng cho phép: `*.pipnn`, `*.nsg`, `*.fbin`, `*.ibin`, receipts/logs, binary/source build provenance. Ghi **đường dẫn thật**, kích thước, mtime, SHA-256 và bằng chứng nguồn. Không sửa, đổi tên, di chuyển, reserialize hay rebuild input. Tránh rehash nhiều lần tập dữ liệu lớn. Nếu không truy cập được directory hoặc thiếu dung lượng/RAM, dừng và báo.
> 4. Đối chiếu SHA-256 với **3 dữ liệu base/query/GT và 9 OFF graph A0/A1/A3 × R1–R3** đúng theo manifest. Phân loại mỗi file: `AVAILABLE_HASH_MATCH`, `MISSING`, `HASH_MISMATCH`, `NOT_VERIFIED`; cùng hash ghi nhận đường dẫn nhưng không suy diễn seed/build provenance. Không lấy graph ON, SIFT1M, BIGANN1M hoặc graph mới dựng để giả mạo OFF R86.
> 5. Nếu đủ bytes và hash khớp, kiểm tra header, kích thước, row mapping, dtypes, format `.fbin` và split-GT `.ibin`; kiểm tra vector finite và GT exact-distance trên mẫu theo tài liệu, không giả định GT distances là squared L2. Dùng cấu hình rõ ràng `n=1000000,d=100,nq=100000,GT width=100`; báo sai khác thay vì sửa input.
> 6. Tạo **bản copy cục bộ** của manifest với relative paths trỏ tới artifact root (không chỉnh file manifest gốc để che HOLD); chạy `python3 -m research.task_da.preflight <manifest-local> --artifact-root <artifact-root>` tại repo root. Exit **1** là HOLD theo thiết kế, **2** là lỗi integrity/structure; tuyệt đối không coi preflight là P0/P1 PASS. Lưu stdout/stderr và bản inventory trong evidence directory **ngoài Git**, không ghi đè receipts hiện hữu.
> 7. Với graph thật SHA-matched, chạy tuần tự structural audit bằng `python3 -m research.task_da.graph_audit <file.pipnn> --format pipnn --entry 0 --expected-n 1000000`. Ghi n, arcs, degree, self-loop, duplicate, reachability, file SHA và ordered adjacency SHA. Không tự sửa self-loop/edge order/direction. Nếu làm conversion chỉ khi cần, dùng output mới, per-node before/after SHA và entry parity; direct loader được ưu tiên.
> 8. **Chỉ sau** khi graph + vectors + GT đã xác minh, chạy bounded p=1 correctness smoke tối đa 32 queries theo `README.md` (beam 384 chỉ là ví dụ, phải ghi đúng cấu hình đã dùng), cả ON và OFF trên A0/A3, đánh giá Recall bằng `evaluate_smoke.py`. Nếu làm representation comparison, kiểm tra IDs, distances và node digests. Smoke không đo latency/QPS, không đạt Recall floor nghiên cứu chỉ nhờ 32 queries.
> 9. Truy nguyên raw receipts, builder/search binary SHA, source commit, uncommitted diff hash, build flags, seed hoặc randomness mechanism, host details (CPU, SMT/NUMA, affinity, governor, memory residency, temperature/frequency protocol). Nếu nguồn không có, đánh dấu `NOT_VERIFIED`; không gắn snapshot `backup/r86-source-only` làm provenance lịch sử khi chưa có bằng chứng.
> 10. Tạo `P0_P1_REAL_ARTIFACT_INVENTORY.md` (và máy-đọc được JSON) có các cột run_id / arm / replicate / candidate relative path / expected SHA / actual SHA / status / receipt / provenance / blockers; **không** commit raw graph, data, binaries, secrets hoặc logs lớn. Ghi evidence paths riêng và SHA-256 logs. Ghi chép kết quả thực tế vào report mới, không sửa preregistration v1 theo kết quả.
> 11. Gate: **P0 vẫn HOLD** nếu thiếu provenance, artifacts, môi trường host; **P1 vẫn HOLD** nếu chưa kiểm toán A0/A3 thật và smoke cùng engine/GT. Một file sai hash là lỗi integrity có phạm vi, không phải bác bỏ H1/H2. Nếu thiếu evidence, dừng ở inventory và yêu cầu Task A handoff; không triển khai P2/P3.
>
> **Trả lại:** (a) inventory 12 assets, (b) receipts và checksum minh chứng, (c) báo cáo kiểm tra graph/GT/smoke nếu thực thi được, (d) các blocker có tên người cần cung cấp, (e) GO/HOLD/NO-GO **theo phạm vi** kèm command/exit logs, (f) commit/PR link **chỉ nếu** tài liệu mới đã được commit trên đúng nhánh.
>
> Nếu cần viết code mới hoặc sửa engine phức tạp, **không tự suy diễn**. Trình bày API/semantics, tests cần thiết và một prompt tách riêng cho coding agent; chờ P1 real-data evidence trước khi khởi động multi-walker 1/2/4.

## Artifact handoff cần yêu cầu Task A nếu kiểm kê không tìm thấy

- **Dataset**: MS-Turing-1M base, queries và GT đúng 3 SHA trong manifest; n/d/nq/GT width đã nêu.
- **Graphs**: đúng 9 `A0/A1/A3 × R1/R2/R3` thuộc **OFF formal** (không thay bằng các graph ON hoặc SIFT).
- **Build/source receipts**: source commit/diff, builder binary SHA, toolchain/compiler flags, seeds hoặc nguồn randomness, build/search process logs, mapping run_id→file và provenance graph bytes.
- **Host**: benchmark host và guard được ghi thành phiên bản protocol mới trước mọi đo P3.

Không có artifact thật thì **dừng ở P0/P1 HOLD**. Chạy một graph mới với SHA khác là một campaign khác có run_id mới, không được dùng để lấp dữ liệu lịch sử.
