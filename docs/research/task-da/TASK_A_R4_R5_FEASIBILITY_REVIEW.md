# Task A — R4/R5 feasibility review

Ngày: **2026-11-20**. **R4/R5 replication = OWNER DECISION REQUIRED.** Historical provenance đủ mạnh để định danh recipe A3; khả năng compile/run tương đương trên Ryzen chưa được chứng nhận. Local recovery package chưa đủ dependency/source để dựng offline từ chính package. Hai cohort “cùng root 555” và “independent RNG roots” là hai lựa chọn nghiên cứu khác nhau; preregistration hiện tại chỉ cho lựa chọn đầu và vẫn HOLD.

Lượt này chỉ đọc receipts/source, băm file và phân tích tĩnh ELF; không thực thi builder, biên dịch builder mới, tạo graph, thay seed/binary hoặc chạy benchmark. Chỉ host quan sát là **AMD Ryzen 5 PRO 4650U**, AVX2/FMA/POPCNT có, AVX512F/AVX512VL không có. Không dùng i5-14600KF.

## 1. “Xác minh với Task A” đã đạt đến đâu

Đối chiếu trực tiếp bản bàn giao do Task A lập: [recovery report 2026-11-17](../../../../artifact-evidence/TaskA_R86_Artifact_Recovery_20261117/TASK_A_R86_ARTIFACT_RECOVERY_REPORT.md), [manifest V3](experiment_manifest_v3_reconciled.json), `jvYREW` compile/source metadata và `build_command.json`/`build_result.json` của A3-R1/R2/R3 trong raw receipts. Report Task A có SHA `ed39671dac4e70cc382b5a2f919c4f17cf4573d7db4122182a7c59a9f869b08b`.

**Không có xác nhận mới từ Task A về portable rebuild hoặc independent-seed design trong evidence đã đọc.** Không gán kết quả audit này thành sự chấp thuận của Task A. Mục 7 là nội dung bàn giao cụ thể còn cần Task A trả lời; chưa gửi thông điệp tới một người/phiên Task A không được định danh. Các điểm đã khép provenance không bị mở lại chỉ vì thiếu xác nhận mới về một recipe tương lai.

## 2. Source → binary lịch sử

| Danh tính | Giá trị được receipt khóa và kiểm lại |
| --- | --- |
| Git base source lịch sử | `443a328dc71a3b7be753d52ca2b3c9a4ba77f3fd` (H70) |
| H70 dirty patch SHA-256 | `d6bcbe9aaae95c0916fa58599355cc93040a19ff41b89bb6109a7b3be5739121` |
| R86 counter/staging patch SHA-256 | `70c9088092f58c16be6835cddad6710003216723164bd74fff81510c909e0a8c` |
| Staged source | `r86_v1_2_source`, không có `.git`; phải dùng reconstruction chain, không gán snapshot commit làm build commit |
| A3 builder | H17 OFF `neighbors-pipnn_FLOAT_T_EUCLIDEAN` |
| ELF SHA-256 kiểm lại | `5f673586210f93b424fc81791ec7873cb74600843b5004c0a4aaaf32bf936297` |
| ELF size / BuildID | 2.840.040 byte / `930b31acc375459f7a02723312e1b7620ae45ba9` theo receipt |
| Toolchain lịch sử | GCC 13.3.0, CMake 3.28.3, GNU++17, Release |
| Flags thực tế | `-march=native -ffast-math -O3 -DNDEBUG -std=gnu++17 -fPIE` |
| H17/tier/counters | `R71_USE_H17=ON` → `R71_H17_TOP2=1`; `R70_USE_TIER=OFF`; `R86_USE_COUNTERS=OFF` |

Bốn tệp core đã băm lại khớp `jvYREW/source_sha256.txt`: root CMake `198badc698ebd5a87fe10e854dca124ac94825535931f20265b86c5d6643c2f9`, PipNN CMake `19d5eb89771343c90ee21c98b8ed3628cfab1a1daf2d5549d37123bfa10d2a95`, `pipnn.h` `77a9b97e593e82037b6f801fb23b5f5bbeab5a5e0c8e112b6386f55488ca9f7d`, `pipnn_utils.h` `33b09c3cb85d70f0a11d86c481dc2a6e398b9e162fe1d42b2b1bd1314a0bd3db`. Hai patch cũng khớp SHA trên bytes local.

Dependency revisions phải giữ theo **compile provenance**, không resolve lại `master` trong CMake:

| Dependency | Revision lịch sử |
| --- | --- |
| Highway | `6bc2d47793bae9c521fb4150936669647700765d` |
| Parlaylib | `51017699dcc421f80479cdb238d3092233ad0d26` |
| Eigen | `3147391d946bb4b6c68edd901f2add6ac1f31f8c` |
| Abseil | `bc257a88f7c1939f24e0379f14a3589e926c950c` |

Receipt/compiler depfile chứng minh header paths lịch sử. Nó không có nghĩa recovery package chứa toàn bộ header bytes. Trong `recovered_artifacts/provenance/source/r86_v1_2_source` local, không có `external/Parallel-KMeans/seeding`; trong recovery tree không có các `_deps/{highway,parlaylib,eigen,abseil-cpp}-src` đầy đủ. Vì vậy **self-contained offline rebuild từ package hiện có = BLOCKED bởi dependency/source completeness**, không phải bằng chứng thuật toán không portable. Không tự fetch revision mới hay dùng checkout source-only `2558e018...` để thay thế source chain.

## 3. Recipe A3 phải được giữ nguyên

Cả ba `build_command.json` ghi cùng H17 OFF ELF, cùng SHA input và `PARLAY_NUM_THREADS=4`; chỉ path output/replicate khác. Lệnh wrapper lịch sử có `taskset -c 0,2,4,6` và `/usr/bin/time`. Không thực thi lại wrapper trong lượt này; mapping core trên Ryzen nếu sau này cần phải được owner chấp thuận theo host protocol riêng, không đổi affinity hệ thống.

| Tham số | A3 lịch sử |
| --- | --- |
| Input | MSTuring_1M_v1, `base.1M.fbin`, 1.000.000 × 100 float32 |
| Input SHA-256 | `44e83e1dd4c65999b75873101adc5ac06ca900d259a2befd05c2c3aa28ff4042` |
| num_clusters / cluster_size | 2 / 512 |
| top_level_leaders / fanout_scheme | 100 / `10,3,1` |
| mst_deg | 2 |
| prune / prune_all / prune_degree | 1 / 1 / 64 |
| table_size / hash_bits | 64 / 12 |
| alpha / k | 1.1 / 0 |
| Parallelism / root policy | Parlay 4 threads / hardcoded SEED 555, hash64 evolution |
| Selection / reservoir / partition | H17 packed top-2; cùng source/flags của reservoir, clustering và pruning, không chỉ cùng argv |

**Graph arm A1/A3 của Task A khác toggle A1 frontier optimization của Task D.** A3 là graph được xây H17 OFF theo recipe trên. Toggle B1/A1 chỉ thuộc evaluator/search; không được nhập nó vào builder semantics.

Đã băm lại đủ A0/A1/A3 × R1–R3 và ba input theo manifest V3. Với A3, header đọc trực tiếp là `n=1.000.000`, max-degree 64:

| Slot | SHA-256 graph | Byte size | Số cạnh suy từ format/size |
| --- | --- | ---: | ---: |
| R1 | `0fff20ec47502c675c4905787d319390e49fa5bee856ac16c814c74697c5fbb2` | 157.419.636 | 38.354.907 |
| R2 | `3d6113e721fa26c8a82f77d2e5bcbc60b6e55352532814694afb146c9c5f9c6c` | 157.417.780 | 38.354.443 |
| R3 | `11f7a5059af309db0a08c4a9e0484d194c8ea5c6f17d8c8f9f67ceb299d85829` | 157.418.376 | 38.354.592 |

Size/cạnh khác nhau loại trừ giải thích chỉ hoán vị thứ tự serialize của cùng multiset cạnh. Không chứng minh độc lập RNG hoặc trao đổi được thống kê. Thư mục formal A3 local chỉ có `r1/r2/r3`, chưa có `r4/r5` trong inventory này; không kết luận R4/R5 không tồn tại ở mọi host khác.

Format giữ [PiPNN contract](graph_format_contract.md): LE uint32 `n,max_degree`, n degree rồi các adjacency rows; vectors không nằm trong graph; entry 0 là policy search ngoài serialization. Giữ directed edges, ID order, self/duplicate arcs nếu có; không chuyển thành NSG hoặc tự repair. Future graph audit phải kiểm exact format, n/degree/length/range và directed reachability từ entry 0; quality chỉ là gate bổ sung, không chứng minh build semantics.

## 4. Ryzen không AVX-512: điều gì được biết

**Quan sát:** `lscpu` và `/proc/cpuinfo` trong lượt này cho Ryzen 4650U, AVX2/FMA có, AVX-512 không có. `objdump -d` tìm thấy lệnh ZMM trong ELF H17 OFF, ví dụ trong symbol Highway `hwy::N_AVX3_SPR::...MaybePartitionTwoValue...`.

**Giới hạn suy luận:** Highway có các target-specific symbols; riêng một lệnh ZMM trong target như trên chưa chứng minh nó nằm trên đường thực thi vô điều kiện. Không được dùng “có ZMM” để khẳng định chắc chắn ELF không thể chạy. Ngược lại, root source có `-march=native -ffast-math` và Eigen dist-matrix nên cũng không được chứng nhận an toàn AVX2 chỉ vì Highway có dispatch. Chưa kiểm toàn bộ reachable ISA/call paths; không chạy ELF để thử SIGILL.

Điểm này làm rõ nhận xét AVX-512 của [preregistration R4/R5](B1_A1_R4_R5_CONFIRMATION_PREREG_20261119.md), giữ preregistration gốc bất biến. **Historical ELF-on-Ryzen compatibility = NOT VERIFIED. Portable source compile = PLAUSIBLE, NOT COMPILED/VALIDATED.** Không có kết quả compile mới để đánh dấu FEASIBLE.

H17 top-2 tại `pipnn_utils.h` dùng scan so sánh packed double cho `mst_deg==2`; riêng đoạn đó không đòi AVX-512 intrinsic. Tuy nhiên distance matrix dùng Eigen float norms/rankUpdate và công thức norm-dot; pruning gọi metric của Points; sorting/selection có Highway. Khác ISA/compiler/FMA/reduction order dưới fast-math có thể đổi tie/decision và adjacency. Đọc một đoạn top-2 portable hoặc thấy Recall gần nhau không đủ chứng nhận toàn builder.

Portable rebuild tương lai cần source/dependency đúng pins, compiler/flags được ghi đầy đủ, build trong output mới, ISA target AVX2 phù hợp Ryzen và kiểm toàn đường build. Không âm thầm tắt fast-math, đổi precision/distance, dùng Task D double-distance evaluator thay builder float/SIMD hoặc đổi H17 implementation. Nếu cần patch build flags để chọn ISA rõ ràng, phải ghi patch/hash và owner chấp thuận đây là cohort/binary mới. Không yêu cầu byte-identical graph giữa hai ISA, nhưng phải giải thích numeric semantics và mọi sai khác ảnh hưởng phương pháp.

## 5. R1–R3 và ý nghĩa “độc lập”

Source `pipnn.h` dòng 498 khởi tạo `size_t SEED = 555`; dòng 429 cập nhật bằng `parlay::hash64(SEED)`. Một số luồng con dùng seed dẫn xuất theo depth/cluster. `std::random_device`/`mt19937`/`parlay::random rnd` ở wrapper dòng 373–376 không chứng minh graph dùng independent root; theo audit Task A đây là local RNG không đi vào seed path chính. `hash.h` có các constructor default seed 0 riêng. Receipt argv không có runtime seed.

R1–R3 là **ba invocation riêng cùng root và recipe, build bốn luồng**. Biến thiên adjacency phù hợp với parallel build nondeterminism được Task A ghi nhận; chưa cô lập nguyên nhân scheduler/race/order bằng thí nghiệm. Không dùng nhãn `FORMAL_INDEPENDENT_NATIVE_OFF_BUILD...` trong receipt làm bằng chứng độc lập xác suất. Không xem graph SHA khác như chứng chỉ independence.

| Loại replicate | Có thể claim | Không thể claim |
| --- | --- | --- |
| Invocation mới, cùng 555/recipe | Build replicate có điều kiện; cần giả định exchangeability | Independent RNG draw hoặc tái lập distribution graph construction toàn bộ |
| Root RNG được lấy độc lập, streams được audit/khóa | Independent-root cohort theo policy công bố | Vẫn cùng historical build subject nếu đổi seed interface/semantics mà không ghi |
| Search process/query folds trên cùng graph | Nhiễu đo/query uncertainty bên trong graph | Tăng số graph outer replicates |

Independent roots cần audit **mọi** randomness stream: SEED/hash64, cluster/leader shuffle, hash-family seed 0, RNG có trạng thái và tác động thứ tự build. Task A phải nói rõ policy nào là shared fixed randomness và policy nào thay theo master seed. Nếu giữ hash-family 0, claim độc lập được điều kiện trên hash-family cố định đó; nếu chuyển mọi stream sang master root, đó là thay đổi phương pháp cần cohort riêng. Root khác nhau cần được lấy/khóa trước, không chọn sau Recall/latency. Cố định root khác không tự chữa nondeterministic concurrency.

Không tự thêm seed CLI, sửa `555`, đổi thread count, thử nhiều seed rồi chọn hai graph hoặc coi `r4/r5` là seed values. Builder hiện tại **chưa có giao diện runtime seed được chứng minh** trong receipts/source audit này. Việc tạo independent-root replicates thực sự vẫn cần thiết kế và phê duyệt riêng.

## 6. Hai đường đi, không trộn cohort

**A — Giữ conditional preregistration hiện tại.** R4/R5 là invocation mới cùng root 555, Parlay 4, recipe A3. Chỉ tiếp tục nếu Task A chứng nhận source/dependency package và phương pháp portable; owner chấp thuận binary/cohort Ryzen mới cùng giới hạn suy luận. Ghi binary SHA mới, host/ISA/numeric policy, mọi graph kể cả trùng adjacency hoặc quality fail. Không pooling R1–R3 lịch sử với R4/R5 Ryzen để tăng df khi builder/ISA khác; primary outer R4/R5 có n=2 theo plan, CI có điều kiện và rất rộng.

**B — Mục tiêu là independent RNG roots.** Preregistration 2026-11-19 không bao phủ. Cần Task A đặc tả seed stream contract và owner chấp thuận source patch/binary, root list, cohort name, compile semantics và protocol mới trước tạo graph. Không sửa preregistration cũ; tạo addendum/version riêng. Nếu chọn B thì không gọi kết quả là confirmation đúng thiết kế A.

Nếu yêu cầu là dùng **đúng historical ELF và semantics byte-level** trên Ryzen, điều kiện ISA chưa được chứng minh; đánh dấu technical blocker cho đường đó, không đề nghị chạy thử builder thật. Khả năng portable bằng source là một câu hỏi khác.

## 7. Nội dung bàn giao cho Task A, chưa gửi

Yêu cầu phản hồi bằng receipt/manifest có nguồn và SHA, không chỉ “có thể build”:

1. Cung cấp full source reconstruction + dirty patches + submodule/external seeding + bốn dependency revisions thực tế, cùng clean/dirty status. Xác nhận package đủ offline build, không resolve `master` mới.
2. Xác nhận historical H17 OFF ELF/source/argv ở mục 2–3. Đánh giá đường ISA bắt buộc so với Highway dispatch. Chọn recipe compile trên Ryzen AVX2, ghi compiler/link/flags/PCH, numeric semantics, macros và output identity mới; không biên dịch hoặc chạy graph trong bước trả lời kiểm tra này.
3. Xác nhận giữ top-2, reservoir, clustering/fanout, pruning, metric, ID mapping và PiPNN format. Liệt kê chỗ fast-math/Eigen/SIMD có thể đổi thứ hạng; đề xuất bounded semantic checks cho một authorization sau, không thay bằng Recall-only equivalence.
4. Xác nhận R1–R3 cùng 555 và không có root seed CLI; audit randomness streams, giải thích phạm vi invocation independence. Nêu rõ hỗ trợ independent master seeds có cần source change không và shared fixed hash-family được xử lý thế nào.
5. Khuyến nghị rõ chọn A hay B, giới hạn suy luận/cross-ISA, tài nguyên/guard và receipt cần có trước khi owner quyết định tạo R4/R5. Không tạo graph hoặc benchmark kèm câu trả lời feasibility.

## 8. Quyết định và validation của lượt tài liệu

| Câu hỏi | Trạng thái |
| --- | --- |
| Historical recipe/source/binary có truy nguyên được không? | VERIFIED theo receipts; core source/ELF/patch SHA được kiểm lại |
| Package local tự đủ portable build offline? | BLOCKED: thiếu full external/dependency trees trong recovery package đã kiểm |
| Historical ELF chắc chắn không chạy trên Ryzen vì có ZMM? | Không đủ chứng cứ kết luận; compatibility NOT VERIFIED |
| Có chứng minh compile portable và giữ semantics? | Chưa; chưa compile, cần Task A xác nhận |
| R1–R3 là independent RNG roots? | Không; cùng root 555 |
| Tạo R4/R5 cùng-root theo plan có được kích hoạt? | Chưa; plan HOLD, owner chưa duyệt tạo graph/calibration/timing |
| Tạo independent-root cohort theo plan hiện có? | Ngoài phạm vi; cần quyết định và preregistration mới |

**Overall: OWNER DECISION REQUIRED**, với technical prerequisites chưa khép; không đánh dấu FEASIBLE và không khẳng định bất khả thi. [Novelty audit](H3_NOVELTY_AND_PRIOR_ART_AUDIT.md) và [screening plan](H3_OVERLAP_SIGNAL_SCREENING_PLAN.md) không phụ thuộc vào việc tạo graph mới.

Lượt này chỉ thêm ba báo cáo Markdown, đề xuất commit bảo toàn hai tài liệu có sẵn; không commit hoặc thay baseline. Kiểm toàn bộ local Markdown links của ba báo cáo không có link hỏng; `git diff --check` sạch; SHA của hai tài liệu có sẵn giữ nguyên. Không chạy Linux integration opt-in hoặc ANN benchmark.

Dataset-free verification cuối: **516 tests, 505 pass, 11 skip** bằng virtualenv có sẵn qua alias `/tmp/h3-screening-audit/venv-no-spaces/bin/python -m unittest discover -s tests/research -v` với `PYTHONDONTWRITEBYTECODE=1`. Giữ log các lần kiểm tra ở `/tmp/h3-screening-audit/`. Các lần thử trước được ghi rõ: shell không có `python`; system `python3` thiếu numpy nên ba module test không import được; virtualenv dưới đường dẫn có dấu cách làm test fake collector shebang lỗi ENOENT. Probe synthetic tái hiện lỗi shebang và alias không dấu cách khắc phục mà không sửa code. Một lần gọi focused test ban đầu còn thiếu `tools/research` trong PYTHONPATH; focused sau đó tái hiện đúng lỗi shebang. Full suite cuối qua với cùng dependencies, alias path hợp lệ. Đây là kiểm thử synthetic, không đo ANN.

Original TP-CG dynamic scheduling = **PIVOT**. Overlap-aware frontier assignment = **MORE EVIDENCE**. R4/R5 replication = **OWNER DECISION REQUIRED**. Historical P0 / Full P1 / t0998 **HOLD**, V4 D1–D5 **UNAPPROVED**, P3 Official **CLOSED**, H3/TP-CG **NOT_OPENED**; D1 **UNTESTED**, D4 **NOT TESTED**, D6 **INCONCLUSIVE**. Các frozen subjects và lane nghiên cứu giữ nguyên ranh giới.
