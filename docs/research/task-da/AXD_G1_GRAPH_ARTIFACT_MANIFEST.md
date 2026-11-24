# A×D G1 · Manifest graph đã nhận

**Ngày 22/11/2026, đã nhận đủ 6/6 graph gốc và Stage 1 integrity PASS.** Sáu SHA khớp audit G1 của D, TRANSFER_MANIFEST.json, SHA256SUMS.txt, manifest BUILD và manifest Search R90 v1.3 tại checkout A. Tổng graph payload là 1.292.447.108 byte. [Audit danh tính lần nhận](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/artifact_identity.json) · [Audit G1 gốc](AXD_G1_COMPATIBILITY_AND_READINESS_AUDIT.md)

Gói owner cung cấp đã được xác nhận tồn tại ở Downloads/ và bản sao trong [thư mục artifact workspace](../../../.local/artifacts/task-a-r90-v13-six-original-graphs/). Archive chứa đúng tám regular file, gồm sáu graph và hai metadata, tên member nằm trong một thư mục package, không có đường dẫn thoát ra ngoài. Bản đã giải nén được dùng trực tiếp trong lượt G1.

| Payload | SHA-256 đã kiểm |
|---|---|
| Archive TAR | `e59f5889f1271a801ff350866bfdffdf7764c372aac65e06d93c2d6a3c48029d` |
| TRANSFER_MANIFEST.json | `df092d838b717430e75148bc2c47ab4611af95eed8f014646f5520a3273e2d52` |
| SHA256SUMS.txt | `62b0db1a07336840fecb083c1235e608e75937d74f5db6e9a7ffc9a9c99a6e75` |

Đường dẫn nhận của các graph tính tương đối từ gốc checkout D là `.local/artifacts/task-a-r90-v13-six-original-graphs/TASK_A_R90_V13_MST1M_SIX_ORIGINAL_GRAPHS/`. Git ignore thư mục .local/. SHA sau smoke khớp SHA lúc nhận.

| File | Expected = actual SHA-256 | Actual bytes | Directed arcs | Identity |
|---|---|---:|---:|---|
| `MS-Turing1M_stock_off_r1.graph` | `db4f5257f06d7ca6df0a040d19590d201bc3e9b1eab7bf0f36265732969716cc` | 215,313,724 | 52,828,429 | PASS |
| `MS-Turing1M_stock_off_r2.graph` | `5de325e9bbb0b46208c4878b3af77ae79c7c1821096eb11064efab5c15d0ae84` | 215,413,516 | 52,853,377 | PASS |
| `MS-Turing1M_stock_off_r3.graph` | `a7eb1ad15ff31130ce8411169f19b41d9bde75577ad5b5416e1b53a90ecbd010` | 215,432,108 | 52,858,025 | PASS |
| `MS-Turing1M_fast_off_r1.graph` | `104a1bc69711e494dbf562772b867752dd915e53ff7ed4142763cdc98fb354e9` | 215,398,220 | 52,849,553 | PASS |
| `MS-Turing1M_fast_off_r2.graph` | `4b69a53c548cdb47714902c2201fe732daf668683056aae9efa724982e11731a` | 215,429,104 | 52,857,274 | PASS |
| `MS-Turing1M_fast_off_r3.graph` | `7c80157e8165e2792151e4934078fd7bd2fa2deebad2ad9864ba6aaf24da0462` | 215,460,436 | 52,865,107 | PASS |

Cả sáu graph có n=1.000.000, declared/observed max degree 64, zero invalid ID, self-loop và hàng chứa neighbor trùng. Đọc độc lập từng hàng từ file so với CSR của frozen common loader cho changed_rows=0 trên toàn bộ 6.000.000 hàng. Direction, multiplicity và edge ordering đều được so ở từng vị trí. Entry được truyền bằng 0, directed reachability đạt đủ 1.000.000 đỉnh/graph. [Receipt cấu trúc và loader](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/stage1_stage2.json) · [Digest ordered adjacency](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/canonical_adjacency.json)

Source Task A trong TRANSFER_MANIFEST là main tại `f5e48bb681812ce51aed7272f30ecefc85ed427b`. Đã kiểm 10 checksum manifest nguồn. BUILD manifest SHA `0c76f3e5bc3dc0d82f70aa1aadac9b26c5b0e8f4607f31d9aa6d8b0b0a4121c3`, structural audit SHA `9550858dcb763349ed5180b3b65577e48a600e54becc0ecb9c755970a4d4bbfb`, Search manifest SHA `767c8b95dcf9f2e91bb06612b1c0d82ee9814ea3e6b220cd755601705a1738ed`.

Cohort là MS-Turing-1M, H85 Highway `6bc2d47793bae9c521fb4150936669647700765d`, Stock/Fast OFF × ba BUILD, C160/K1024/N2, prune degree 64, hash bits 12, alpha 1.1. ID bằng hàng base, squared L2 trên vector FP32 gốc. [Hợp đồng graph](graph_format_contract.md)

| Workload tại D, đường dẫn từ gốc checkout | SHA-256 đã băm lại |
|---|---|
| ../../graph/data/MSTuring_1M_v1/base.1M.fbin | `44e83e1dd4c65999b75873101adc5ac06ca900d259a2befd05c2c3aa28ff4042` |
| ../../graph/data/MSTuring_1M_v1/query.public.100K.fbin | `48d087a17bec15a5ec9ea526fe9bd14ac31bbbb5cd200817b341adbb77695644` |
| ../../graph/data/MSTuring_1M_v1/groundtruth.public.100K.ibin | `fa5acf5ab262b42355296e99f920e6aa863f48820ca6f70fa37ca7966634c344` |

Header base/query/GT lần lượt là 1M×100, 100K×100 và 100K×100. FBIN dùng float32 row-major. IBIN có toàn bộ ID uint32 rồi toàn bộ auxiliary distance float32. Đã kiểm đúng bytes theo header và pins. Recall của D dùng 10 ID đầu theo query ID. [23 pin frozen](../../../../artifact-evidence/axd-g1-runtime-20261122-Ik1dBvXi/frozen_pins.json) · [Kết quả runtime](AXD_G1_RUNTIME_PARITY_REPORT.md)
