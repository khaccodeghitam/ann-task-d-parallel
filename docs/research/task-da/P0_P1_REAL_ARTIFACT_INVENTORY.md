# P0/P1 real-artifact recovery — kiểm tra tại máy Linux

Ngày kiểm tra: 2026-11-17T15:25:45.304078+07:00. **Thu hồi bytes: 12/12 khớp hash. Bước khôi phục P0/P1 chưa hoàn tất: P0 HOLD, P1 HOLD.**

## Kết luận và phạm vi

- Ba file MS-Turing-1M và chín OFF formal graph A0/A1/A3 × R1–R3 đều tồn tại, đọc được và khớp SHA-256 trong manifest đã commit. Không có HASH_MISMATCH trong 12 asset.
- Kiểm tra cấu trúc cả chín graph thành công. A3–R2 có một node không thể đi tới từ entry 0. Điều này được giữ nguyên, không sửa graph.
- Base/query đúng shape, size, float32 little-endian và hữu hạn trên toàn bộ dữ liệu. GT đúng split layout, IDs hợp lệ; phát hiện **ba auxiliary distances âm**. Năm query exact spot-check khớp top-100 IDs và thứ tự.
- **Chưa có raw receipts, builder/search binaries lịch sử, source/diff/build-toolchain linkage, seed/randomness theo từng build, hoặc qualified host protocol.** Snapshot source có sẵn không thay được provenance lịch sử.
- Native p=1 ON/OFF smoke **NOT_RUN**: provenance chưa đủ và GT chưa được chấp nhận theo contract. Không có Recall smoke, latency hay QPS mới. Không triển khai P2, không chạy P3, không rebuild/conversion.

Đây là PASS cho byte identity và scoped structural checks, không phải P0/P1 PASS hay kết luận bác bỏ H1/H2. Raw recovery, GT semantics và smoke vẫn là các công việc còn thiếu.

## Repository và GitHub

Repo: `/home/thinhbui/Documents/ChatGPT/Research ANN/task-d`. Nhánh giữ nguyên `research/task-d-a-p0-p1-20261115`, HEAD `b0a95f4d4a8c0a5e9d100caa18c57ef448fe8251`. Working tree sạch trước audit. Không checkout/reset/clean/merge/fetch/pull, không đổi ref và không tạo commit/push. File mới được lưu chưa commit trên nhánh nghiên cứu hiện tại.

Đã đọc GitHub bằng integration kết nối: PR #57 **closed, draft=true, merged=false**, `merged_at=null`, đóng lúc **18:11:03 ngày 16/11/2026 (UTC+7)**. Mô tả cũ nói PR đang mở đã lỗi thời. Live research ref và PR head đều là HEAD cục bộ. Remote `main` quan sát được là `c2542bdc163ff298ca8ac19bb39bc909bcad3cf7`; không thay đổi `main`. Giá trị `merge_commit_sha` trên PR không được dùng làm bằng chứng merge.

Hai workflow “Research synthetic checks” tại HEAD này đều completed/success: run 43695891481 (pull_request) và 43695888087 (push). Chúng chỉ chứng nhận synthetic CI. Raw responses ở `github-snapshot.json`, commit readback ở `github-followup.json`, live ref ở `github-live-ref.json` trong evidence root. Branch URL có encoded slash từng bị connector từ chối; đã xác minh thay thế bằng GET git/ref. PR commits response chỉ là trang đầu và không dùng để suy luận toàn bộ ancestry.

## Artifact roots, phương pháp và giới hạn tìm kiếm

- Artifact root: `/home/thinhbui/Documents/ChatGPT/graph`.
- Evidence mới, ngoài mọi Git repository: `/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/p0-p1-20261117T151056+0700`. `git rev-parse --show-toplevel` tại đây exit 128 như dự kiến.
- Kiểm kê 11.106 file trong `/home/thinhbui/Documents/ChatGPT`, gồm hidden/ignored files; bỏ `.git`, `node_modules`, `.venv`, `__pycache__` và evidence mới. Không có lỗi truy cập từ discovery hoặc lỗi stat; không thấy archive để giải nén. Không dò host/mount khác hoặc `~/ann-task-a` nằm ngoài phạm vi yêu cầu.
- 16 graph/data candidates gồm 12 asset thật và 4 fixture; các fixture bị loại khỏi inventory lịch sử. 45 ELF candidates được hash (file không suffix hoặc suffix `.so/.bin/.exe`), không trùng hai builder hay hai Search pins lịch sử.
- Hash mong đợi chỉ lấy từ manifest đã commit và source/receipt có pin. Cả chín graph pins được đối chiếu thêm với bản `E_PROTOCOL.json` đã lưu cục bộ; đây là snapshot của sheet, không phải raw native receipts. Không suy seed từ tên R1–R3 hoặc mtime.
- Manifest gốc SHA-256 `f73fe3b062eb2205ad31593210c125c6c081510d948968490fe207811c363790` giữ nguyên. `manifest-local.json` chỉ điền relative artifact paths; các trường provenance và gates cũ được giữ nguyên.
- Hash được lưu/cache cho inventory. Các CLI handoff bắt buộc tự tính lại hash trong preflight/audit; không sửa chúng để bỏ verification. Size/mtime của 12 input giữ nguyên khi hoàn tất kiểm tra; graph hash nhất quán giữa inventory, preflight và standalone audit.

## Inventory 12 asset

Full paths, relative paths, mtime, expected/actual SHA, authoritative source, checks và blockers nằm trong `P0_P1_REAL_ARTIFACT_INVENTORY.csv` và `.json` cùng thư mục. Bảng dưới dùng actual SHA; mỗi actual SHA bằng expected SHA tương ứng trong manifest.

| Run / asset | Bytes | SHA-256 | Tình trạng byte identity |
|---|---:|---|---|
| `base` | 400,000,008 | `44e83e1dd4c65999b75873101adc5ac06ca900d259a2befd05c2c3aa28ff4042` | AVAILABLE_HASH_MATCH |
| `queries` | 40,000,008 | `48d087a17bec15a5ec9ea526fe9bd14ac31bbbb5cd200817b341adbb77695644` | AVAILABLE_HASH_MATCH |
| `ground_truth` | 80,000,008 | `fa5acf5ab262b42355296e99f920e6aa863f48820ca6f70fa37ca7966634c344` | AVAILABLE_HASH_MATCH |
| `R86_MST1M_A0_OFF_FORMAL_R1` | 215,424,180 | `55df31ac9b7716f779dca332ce9360c9e21a065f9298ec1c92c8ccdd37d72522` | AVAILABLE_HASH_MATCH |
| `R86_MST1M_A1_OFF_FORMAL_R1` | 215,506,900 | `7da34f1c3e0ff8a67092a2c9f96bc35122b88fdbe36c59347d1f213b55c46979` | AVAILABLE_HASH_MATCH |
| `R86_MST1M_A3_OFF_FORMAL_R1` | 157,419,636 | `0fff20ec47502c675c4905787d319390e49fa5bee856ac16c814c74697c5fbb2` | AVAILABLE_HASH_MATCH |
| `R86_MST1M_A3_OFF_FORMAL_R2` | 157,417,780 | `3d6113e721fa26c8a82f77d2e5bcbc60b6e55352532814694afb146c9c5f9c6c` | AVAILABLE_HASH_MATCH |
| `R86_MST1M_A1_OFF_FORMAL_R2` | 215,403,280 | `b08ef703f162b75f6c2512d29d58113212c185030dc5b230a7488c8244c82ede` | AVAILABLE_HASH_MATCH |
| `R86_MST1M_A0_OFF_FORMAL_R2` | 215,468,020 | `e0e0be004e6b3bd9cf55c4f620863e2d002aa5798a9e258f5330ee2f1d1ee6b9` | AVAILABLE_HASH_MATCH |
| `R86_MST1M_A3_OFF_FORMAL_R3` | 157,418,376 | `11f7a5059af309db0a08c4a9e0484d194c8ea5c6f17d8c8f9f67ceb299d85829` | AVAILABLE_HASH_MATCH |
| `R86_MST1M_A0_OFF_FORMAL_R3` | 215,384,040 | `a4ad500421b95700f34d1d2e267640decffbf3f54a88fdb2b3708cf33448405b` | AVAILABLE_HASH_MATCH |
| `R86_MST1M_A1_OFF_FORMAL_R3` | 215,420,692 | `1b51bf7115450c208bc209d9419fd42425c8393e75f712ec1fabdd7fb69787b1` | AVAILABLE_HASH_MATCH |

Dataset paths dưới artifact root: `data/MSTuring_1M_v1/base.1M.fbin`, `query.public.100K.fbin`, `groundtruth.public.100K.ibin`. Graph path template: `experiments/R86/msturing_1m_sixarm/formal_mst1m_v1/{A0,A1,A3}/r{1,2,3}/index.graph`. Suffix `.graph` được đọc với **format pipnn chỉ định rõ**, không đổi tên hay đoán format từ suffix.

## Dữ liệu và GT

Base: n=1.000.000, d=100, 400.000.008 bytes. Query: nq=100.000, d=100, 40.000.008 bytes. Đã scan cả 110 triệu giá trị vector/query; không có NaN/Inf. Row index được giữ nguyên. Historical builder-to-base row mapping vẫn cần raw build receipt xác nhận.

GT: nq=100.000, width=100, 80.000.008 bytes, header rồi toàn bộ uint32 IDs, rồi toàn bộ float32 distances. Đã kiểm tra tất cả 100.000 rows: không có ID ngoài range, ID trùng trong row, nonfinite distance hoặc thứ tự distance giảm. **Có ba giá trị âm ở rank 0:**

| Query ID (0-based) | Base ID | Stored auxiliary distance | Squared L2 tính độc lập |
|---:|---:|---:|---:|
| 45219 | 467759 | -3.576278686523438e-07 | 9.642754869869548e-14 |
| 48571 | 938845 | -2.384185791015625e-07 | 0 |
| 95033 | 905634 | -2.384185791015625e-07 | 0 |

Độ lớn nhỏ và cặp vector trùng/gần trùng phù hợp với khả năng sai số số học, nhưng nguyên nhân và policy chấp nhận **chưa được chứng minh**. Không clamp, normalize, sort lại hoặc ghi lại GT. `evaluate_smoke.py` hiện từ chối distance âm trên những GT rows được đánh giá; ba query lỗi nằm ngoài first-32 smoke, nên một smoke first-32 thành công cũng sẽ không giải quyết lỗi này.

Exact diagnostic độc lập: query IDs `[0,1,31,50000,99999]`, mỗi query scan toàn bộ 1 triệu base rows, float64 accumulation trên float32 gốc, tie bằng base ID tăng dần. Top-10 và top-100 sets/order đều khớp GT trên năm query này. Stored distances phù hợp **squared L2 trên mẫu**, không phù hợp L2; max absolute error trên mẫu ≤ 6.576e-7 (rtol=1e-4, atol=1e-5). Không mặc định convention trước khi kiểm tra, không chứng nhận exact GT cho toàn bộ 100.000 queries. Q50000 được bổ sung theo mẫu trong Task A diagnostic source; sample không dùng để tune search.

Diagnostic lần đầu dừng với assertion (exit 1) khi phát hiện distance âm. Giữ nguyên stderr và bản script v1; lần hai chỉ mở rộng ghi diagnostics, process exit 0 nhưng **data status HOLD**. Không diễn giải exit 0 này thành GT PASS.

## Graph audit chỉ đọc

Chạy preflight theo handoff: exit **1**, 12 artifacts AVAILABLE, 37 blocker entries; P0/P1 vẫn HOLD theo thiết kế. Sau đó chạy riêng chín `graph_audit` tuần tự, tất cả exit 0; toàn bộ kết quả trùng structural records của preflight.

Tất cả graph có 1.000.000 vertices, declared max degree=64, không có neighbor ngoài range, trailing/truncated bytes, self-loops, duplicate arcs hoặc zero-outdegree nodes. File SHA và ordered adjacency SHA được giữ trong JSON/CSV. Directed BFS từ entry 0 không phải chứng minh strong connectivity.

| Arm | Replicate | Directed arcs | Degree mean | Degree p95 | Degree max | Reachable từ 0 |
|---|---|---:|---:|---:|---:|---:|
| A0 | R1 | 52,856,043 | 52.856043 | 64 | 64 | 1,000,000 |
| A0 | R2 | 52,867,003 | 52.867003 | 64 | 64 | 1,000,000 |
| A0 | R3 | 52,846,008 | 52.846008 | 64 | 64 | 1,000,000 |
| A1 | R1 | 52,876,723 | 52.876723 | 64 | 64 | 1,000,000 |
| A1 | R2 | 52,850,818 | 52.850818 | 64 | 64 | 1,000,000 |
| A1 | R3 | 52,855,171 | 52.855171 | 64 | 64 | 1,000,000 |
| A3 | R1 | 38,354,907 | 38.354907 | 51 | 64 | 1,000,000 |
| A3 | R2 | 38,354,443 | 38.354443 | 51 | 64 | 999,999 |
| A3 | R3 | 38,354,592 | 38.354592 | 51 | 64 | 1,000,000 |

**A3–R2:** node **840923**, outdegree=29, incoming arcs=0, không reachable từ 0. Node này xuất hiện 13 lần trong GT top-100 và 4 lần trong top-10, ở query IDs `[23741,47069,66279,89193]`. Với entry-only traversal hiện tại, node này không thể được trả về. Đây là giới hạn topology có phạm vi, không phải graph-format failure; giữ nguyên edges/entry/order và không suy thành NO-GO cho nghiên cứu. Xem `reachability-detail.stdout` để có adjacency và phép đếm.

## Provenance còn thiếu

`P0_P1_PROVENANCE_INVENTORY.csv` liệt kê từng missing path và trách nhiệm. Raw files cần lấy từ **Task A owner/agent**:

1. `campaign_manifest.json` ở formal root; với từng A0/A1/A3 × r1/r2/r3: `build_command.json`, `build_result.json`, `native.build.log` — **28 file cụ thể không có trong bản copy**. Phải nối run_id → graph SHA → base SHA → binary SHA → log SHA, không tạo receipt hồi tố từ tên thư mục.
2. Historical stock OFF builder SHA `aa2d174ed063070045f1fbbc8051b1d97b851168b2f3bf53ee32215a867583be`; H17 OFF builder SHA `5f673586210f93b424fc81791ec7873cb74600843b5004c0a4aaaf32bf936297`. Cả hai MISSING trong phạm vi tìm kiếm.
3. Historical Search v3 SHA `ea6c757b47b1267b7009ff0a1a80a3fdeaaf59740c4c2036712accf9ba0d0af5` và v4 SHA `bb6576ad3e1e0cc770535aa06355c664993ca70bd1170d6dd4d202ab5767e144` được ghim trong source runners đã match SOURCE_SHA256SUMS; cả hai MISSING. Cần compile/link manifests và các `calibrated_*.json`, `calib_*` và `measure_*` JSON/logs tương ứng. Không suy beam từ ví dụ README.
4. Source commit thực tế, source dirty diff hoặc xác nhận clean có bằng chứng, toolchain/compiler version, full compile/link flags/dependency pins. `E_PROTOCOL` cả chín rows để trống source_commit, source_diff_sha và seed. Runtime build CLI được báo cáo trong manifest **không phải compiler flags đã xác minh**.
5. Seed hoặc cơ chế randomness thực tế cho từng build. Snapshot `pipnn.h` lines 373–376 có `std::random_device → std::mt19937 → parlay::random`, nhưng chưa nối được source này với historical binaries. Không dùng cơ chế trong snapshot làm provenance thay thế, không suy ba builds độc lập chỉ từ ba hash khác nhau.
6. Raw GT acquisition/diagnostic evidence, giải thích ba auxiliary distances âm và policy đánh giá được ghi thành protocol mới. Không sửa preregistration v1 hay dữ liệu gốc.

Task A checkout hiện sạch, detached HEAD `2558e018c71f412b4e4e4eddb79264c7ce6ac730`; README_SOURCE_SNAPSHOT xác nhận source-only. Năm source files quan trọng khớp SOURCE_SHA256SUMS, nhưng commit snapshot không được gán làm build_source_commit. Hai Task D smoke binaries cũ khớp `validation_receipt.json`; chúng thuộc synthetic P1 baseline, không phải builder/Search Task A, và không được chạy trong phiên này.

Host hiện tại: AMD Ryzen 5 PRO 4650U, 6 cores/12 logical CPUs, SMT on, 1 NUMA node; affinity của audit process 0–11, governor `schedutil` trên 12 CPUs, tổng RAM khoảng 14 GiB, ban đầu available khoảng 7.6 GiB và disk free 154 GiB. Chỉ quan sát, không đổi host settings. Historical host match, memory residency và qualified thermal/frequency guard **NOT_VERIFIED**. User/Task D host owner cần cung cấp protocol host riêng trước mọi P3.

## Logs, exit codes và tái kiểm tra

Toàn bộ command argv/cwd/exit code được lưu trong `*.command.json`; stdout/stderr và SHA ở `command-index.json` cùng evidence root. CSV `P0_P1_EVIDENCE_CHECKSUMS.csv` liệt kê checksum của evidence/supporting files; các file này không commit vào Git. Bảng dưới chỉ hiển thị stdout SHA, stderr SHA vẫn có trong index.

| Check | Exit | stdout SHA-256 |
|---|---:|---|
| `graph-audit-R86_MST1M_A0_OFF_FORMAL_R1` | 0 | `8c8adc0fc4895e58ee0e35863f89b089686e0b9ae775dbf1a727fc5611d7b230` |
| `graph-audit-R86_MST1M_A0_OFF_FORMAL_R2` | 0 | `785b9eb2360c5a66fff5a652c44d48bb8d177641b9efc812b09d0708ba63523e` |
| `graph-audit-R86_MST1M_A0_OFF_FORMAL_R3` | 0 | `33803c5b7437ecc7ca38d7b40ad9a2a85f6ac58b8d161dc9f04f421a28a1dace` |
| `graph-audit-R86_MST1M_A1_OFF_FORMAL_R1` | 0 | `05d6e3c9faddb2e44718b0055d7b50216dbefd02560ab65f776bbb4fbb978f0c` |
| `graph-audit-R86_MST1M_A1_OFF_FORMAL_R2` | 0 | `b39431d186ea128142f2a4c60f5fa66947047f27b7505232a3384be3d77a5bcd` |
| `graph-audit-R86_MST1M_A1_OFF_FORMAL_R3` | 0 | `e8435c85d9ab68aaef6153dc04f6ba8fd8ad323b7625a60e22d6c854b3018af5` |
| `graph-audit-R86_MST1M_A3_OFF_FORMAL_R1` | 0 | `744e1ac1aca52cbc665f3e2c85d5cfbf9b3559f5655fb7b0c2ac90a3068292f1` |
| `graph-audit-R86_MST1M_A3_OFF_FORMAL_R2` | 0 | `1310da1056e9d1fa996a37c8aa77406a94732f5366ddc812509a26183b588286` |
| `graph-audit-R86_MST1M_A3_OFF_FORMAL_R3` | 0 | `391b48b19d31df1c09c89597c8c077a6b33a543657fff45185803d91cc7a2583` |
| `preflight` | 1 | `4773bd7e19371680c7de577795d2ff97b6d3d5ae3c16afd490f1b6bbd7451d6a` |
| `reachability-detail` | 0 | `dc429753d5d3369cf1e7bcdbc06ffd1befc58901e544d557ef49f6ae3517d078` |
| `vector-gt-check-v2` | 0 | `b92bf1f9530aa8fb7f653cf51b0cdc93bbb1b557601dd5fb6ab057585a4d0352` |
| `vector-gt-check` | 1 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Lệnh thực tế được lưu đầy đủ, ví dụ (run mới phải dùng evidence/output names chưa tồn tại):

```sh
python3 -m research.task_da.preflight '<evidence>/manifest-local.json' --artifact-root '/home/thinhbui/Documents/ChatGPT/graph'
python3 -m research.task_da.graph_audit '<artifact-root>/experiments/R86/msturing_1m_sixarm/formal_mst1m_v1/A0/r1/index.graph' --format pipnn --entry 0 --expected-n 1000000
```

## Bước tiếp theo an toàn

Gửi prompt trong `TASK_A_PROVENANCE_HANDOFF_VI_20261117.md` cho Task A owner để **khôi phục receipts/binaries/provenance và xử lý GT contract bằng bằng chứng**, không dựng lại historical graphs. Sau khi các điều kiện được giải quyết, mới chạy bounded p=1 ON/OFF ≤32 queries trên A0/A3 cùng engine/GT, ghi beam thực tế, đánh giá bằng `evaluate_smoke.py` và so sánh IDs/distances; conversion chỉ khi thật sự cần. Không mở P2 cho tới khi P0/P1 được ghi PASS một cách tường minh. Không có scientific NO-GO hoặc kết quả hiệu năng mới từ audit này.
