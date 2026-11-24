# A×D G1 · Kết quả runtime parity

**G1_RUNTIME_PASS trong scope sáu original graph R90 v1.3, 500 validation query, beam 384, p=2, S=16.** Hoàn tất ngày 22/11/2026. Có 6/6 SHA identity PASS, 6/6 structure/direct-load PASS và 24/24 invocation correctness PASS. **Stock r3 đạt Recall@10 0,9896 ở smoke, thấp hơn floor 0,990. G2 quality còn HOLD và G2 NOT_OPEN.** [Kết quả máy đọc được](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/result.json) · [Prereg G1 trước chạy](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/preregistered.json)

| Kiểm tra | Kết quả |
|---|---|
| Identity | 6 SHA bằng expected qua TRANSFER → BUILD → structural → Search, rehash sau chạy khớp |
| Structural + direct loader | 6 graph, 6.000.000 ordered row, 317,111,765 ordered arcs khớp từng vị trí |
| Header/IDs/entry | n=1M, max_degree=64, toàn bộ ID trong miền, entry=0 |
| Directed reachability | Đủ 1M đỉnh ở từng graph |
| Query coverage | 500 ID duy nhất/graph, 3.000 graph-query pair, 12.000 query execution qua 4 cấu hình |
| Ordered top-10 và L2² | 24/24 output đủ 10 ID duy nhất, cùng query order, exact parity base/opt và ON/OFF |
| Oracle độc lập | 30.000 returned-distance được tính lại từ base/query FP32, max absolute error quan sát 0 |
| Logical counters | ON internal accounting và frozen B1/A1 invariants PASS trên mọi query |
| Guard và termination | 30/30 process exit 0, gồm 6 loader audit và 24 evaluator, zero guard failure |
| Frozen preservation | 23/23 pin khớp trước/sau, SHA graph và binary khớp sau chạy |

Đường nạp là PiPNN trực tiếp bằng frozen load_graph trong engine.hpp của commit `f2cd634b837a70735c3e31e5956f0524bfc26675`. Một verifier C++ riêng gọi loader này rồi đọc độc lập toàn bộ bytes theo LE-u32, so từng degree và neighbor trong CSR, kiểm EOF, loops/duplicates và BFS có hướng. Verifier là công cụ kiểm tra riêng, có source, compile argv và ELF SHA trong evidence. [Verifier source](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/verify_direct_loader.cpp) · [Frozen loader header](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/engine.hpp) · [Runtime identities](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/runtime_identities.json)

Search dùng nguyên ELF B1+A1 Release `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1`. Hai policy là baseline/full và barrier_all_evaled/incremental, cùng flat, p=2, S=16, jobs=1, K=10, beam=384, entry=0. Mỗi policy có một lượt ON và một lượt OFF phục vụ correctness. Mỗi process warmup đúng 100 validation query đã freeze. Raw giữ nguyên fields do ELF phát ra. Các endpoint của G1 là correctness, parity, counters và Recall. [Lệnh và receipts từng lượt](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/runs/)

500 query là đúng smoke_val_500.ids, SHA `54f9eae4c2039f613fe63e2a27a40fadd7b498ab31f195f54fe7340d845ae9a6`, bằng 500 ID đầu của val_10k. Oracle tính double loop trên 100 chiều cho toàn bộ top-10 của 500 query/graph, đặt trước abs_tol=rel_tol=1e-12. Giá trị GT distance không tham gia phép kiểm khoảng cách. Recall dùng giao với 10 GT ID đầu của chính hàng query. [Runner và validator](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/run_g1.py)

| Graph | Recall@10, cả bốn output | LCB95, 500 query | Point ≥0,990 | Exact parity |
|---|---:|---:|---|---|
| stock_off_r1 | 0.991000 | 0.987649 | PASS | PASS |
| stock_off_r2 | 0.991400 | 0.988535 | PASS | PASS |
| stock_off_r3 | 0.989600 | 0.986303 | BELOW_FLOOR | PASS |
| fast_off_r1 | 0.990600 | 0.987398 | PASS | PASS |
| fast_off_r2 | 0.991400 | 0.988378 | PASS | PASS |
| fast_off_r3 | 0.990800 | 0.987667 | PASS | PASS |

LCB95 dùng mean − 1,96×SE trên 500 query. Cả sáu LCB đều dưới 0,990. Span point giữa graph là 0,0018, vượt biên matching 0,0001 trong kế hoạch G2. Điểm smoke phản ánh operating point đã khóa, mọi policy trên cùng graph có ΔRecall=0. G1 được đăng ký để kiểm tương đương output và tính đúng đắn. Calibration val_10k và test 3k của G2 vẫn chưa thực hiện. [Kế hoạch quality](AXD_JOINT_BUILD_SEARCH_GO_NO_GO_PLAN.md)

Counters ON thỏa total L2=unique+duplicate, expansions=unique+duplicate và total L2+already_seen=neighbor_attempts+1. So combo với base bằng invariant frozen mark=True giữ toàn bộ logical counters ngoài các trường tổng/duplicate L2, already_seen và per-worker L2 được phép thay đổi. Mỗi L2 trùng được loại tương ứng một already_seen tăng. Các trường timer được loại khỏi phép equality theo định nghĩa frozen.

| Graph | Duplicate L2/query base | Duplicate L2/query combo |
|---|---:|---:|
| stock_off_r1 | 3231.700 | 893.630 |
| stock_off_r2 | 3240.342 | 902.012 |
| stock_off_r3 | 3256.834 | 915.610 |
| fast_off_r1 | 3234.712 | 890.522 |
| fast_off_r2 | 3243.198 | 902.306 |
| fast_off_r3 | 3237.692 | 895.316 |

Host là AMD Ryzen 5 PRO 4650U, CPU quan sát [0,2], hai core vật lý trong L3 chung 0–5. Guard Ryzen lịch sử từ chối start ≥85°C, dừng ≥95°C, kiểm AC, RAM, disk, swap, foreign ANN và heartbeat watchdog. Có 145 mẫu trong evaluator, Tctl 74.875–88.125°C. Mẫu thiếu sensor và mẫu 95°C được kiểm fail-closed trước chạy. PID 1 của môi trường hiện tại là codex. [Host ban đầu](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/initial_host.json) · [Topology](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/topology.txt) · [Tóm tắt guard](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/verification_summary.json)

Git D ở branch research/task-da-pivot-b1-a1-20261119, HEAD `f54b1bb653652dd13e760cc00c9fb46d0e643c1c`. Trước lượt có tám tài liệu untracked, tracked/staged diff rỗng. Đã lưu snapshot ba báo cáo trước khi cập nhật, kiểm 61 tài liệu cũ giống bytes trước edit. Historical P0/Full P1/t0998/B1+A1 HOLD, V4 D1–D5 UNAPPROVED, P3 official CLOSED, H3/TP-CG NOT_OPENED. [Trạng thái Git ban đầu](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/initial_git.json) · [Báo cáo trước lượt](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/prior_reports/)

Raw đã niêm phong tại thư mục artifact ngoài Git. Receipts giữ absolute capture paths /tmp của thời điểm chạy, file kết quả cùng basename nằm trong từng thư mục run của bundle. [Checksum payload](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/BUNDLE.sha256)

**G2 đủ điều kiện trình duyệt protocol có quality gate. Timing còn chờ calibration/matched quality PASS và owner phê duyệt.** [Readiness](AXD_G2_PREREG_READINESS.md) · [Prereg tối thiểu](AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md)
