# Bảng thống nhất kết quả Task A × Task D

Dùng bảng dưới trong cả hai phần của báo cáo. [JSON chuẩn dùng chung](tables/table14_axd_canonical_integration.json) giữ số chưa làm tròn, phạm vi phép đo và phiên bản. G2 kết hợp hai quyết định trên cùng cohort R90 P0A v1.3: **GO_A_FIXED_COHORT** cho SEARCH và **GO_B_SYSTEM_FIXED_COHORT** cho so sánh hệ thống theo mô hình.

## Bốn cấu hình trên MS-Turing-1M

| Graph × policy | BUILD Host A (s/index) | Recall@10 | SEARCH OFF Host D (µs/query) | P50 / P95 / P99 (µs/query) | QPS wall, jobs=1 | Duplicate / total L2 ON (lần/query) |
|---|---:|---:|---:|---|---:|---:|
| Stock × baseline | 42.257 | 0.992050 | 3619.875 | 3735.78 / 4100.25 / 4229.57 | 276.236 | 3712.00 / 22775.42 |
| Stock × B1+A1 | 42.257 | 0.992050 | 3401.511 | 3511.46 / 3926.75 / 4057.93 | 293.969 | 928.26 / 19991.68 |
| Fast v2 × baseline | 33.793 | 0.992167 | 3619.545 | 3736.64 / 4097.79 / 4226.94 | 276.262 | 3713.62 / 22778.52 |
| Fast v2 × B1+A1 | 33.793 | 0.992167 | 3401.144 | 3511.66 / 3925.58 / 4052.84 | 294.001 | 929.29 / 19994.18 |

BUILD dùng cùng ba biên nhận cho cả hai hàng của một loại graph. Mỗi ô SEARCH là 3 graph × 12 block = 36 process OFF. Quantile báo ở đây là trung bình các quantile cấp process. SEARCH chạy trên Ryzen 5 PRO 4650U, p=2, S=16, beam=432, jobs=1. [Dữ liệu theo arm](tables/table05_g2_2x2_arms_summary.csv)

**Task A — measured BUILD.** Stock và Fast v2 cùng recipe C160/K1024/N2, source Task A `f5e48bb`, Highway `6bc2d477`. Ba build OFF 4 thread trên Host A cho từng arm, cùng SEED=555. Stock mất 42.57/41.99/42.21 s, Fast v2 mất 33.84/33.74/33.80 s. Chênh 8.46333 s/index, giảm 20.03%. Sáu graph có tổng 1 292 447 108 byte. G1 xác nhận đúng danh tính và thứ tự cạnh trước khi Task D chạy SEARCH. Mỗi hàng Bảng 11 nối tên graph với SHA của graph, builder ELF và receipt. [Manifest G1](../../task-da/AXD_G1_GRAPH_ARTIFACT_MANIFEST.md) · [Bảng 11](tables/table11_measured_build_host_a.csv) · [Biên nhận BUILD ghim theo commit](../../../../configs/axd_g2_v2_build_reference.json)

**Task D — measured SEARCH.** So baseline với B1+A1 trên từng graph. Hai panel rời gồm 10 000 query validation và 10 000 test. Gate A dùng cận dưới đồng thời Recall@10 theo graph, nhỏ nhất 0.991188 vượt 0.990. Gate B cho Fast trừ Stock +0.000117, CI95 [−0.000051, +0.000284], nằm trong biên đăng ký ±0.0005. Hai policy khớp bit-exact trong từng graph. Điểm mean latency reduction 6.033151% dùng log-ratio ghép cặp, CI95 block-t [5.976580%, 6.089687%]. Cả sáu graph giảm latency; nguồn biến thiên khi build bằng seed mới vẫn chưa định lượng được. [Kiểm tra chất lượng](../../task-da/AXD_G2_V2_QUALITY_RESULTS.md) · [Kết quả theo graph](tables/table10_per_graph_r90.csv)

**Interaction.** Tính gain SEARCH bằng baseline trừ optimized trong cùng arm. Stock tiết kiệm 218.364 µs/q, Fast tiết kiệm 218.401 µs/q. Hiệu Fast gain trừ Stock gain là **+0.037 µs/q**, CI95 **[−2.582, +2.655]**. Số dương là chiều Fast có lợi hơn. Khoảng này cho biết những mức tương tác còn phù hợp với dữ liệu. Không có bằng chứng về cộng hưởng hay độc lập tuyệt đối. Khi giữ cùng policy, Fast trừ Stock là −0.330 µs/q (baseline) và −0.367 µs/q (optimized); chưa thiết lập biên tương đương latency. [Kiểm định và thống kê](../../task-da/TASK_D_FINAL_EXPERIMENT_RESULTS.md)

## Chi phí mô hình hóa trên hai máy

Với mỗi arm, T(Q) = BUILD_HostA (s) + Q × SEARCH_HostD (µs/query) / 1 000 000. So hai đầu mút Stock+baseline và Fast+B1+A1, tổng chênh mỗi truy vấn là 218.730 µs, gồm cả chênh quan sát giữa hai arm graph. Con số này khác gain B1+A1 trong từng graph. Thành phần BUILD cố định ở 8.46333 s. Phép cộng loại toàn bộ transfer/load. Cửa sổ process ngoài batch khoảng 3.91–3.93 s bao gồm các công việc khác; chi phí toàn tuyến truyền và nạp chưa được đo.

| Q (query) | Tổng Stock+baseline (s) | Tổng Fast+B1+A1 (s) | Tiết kiệm BUILD (s) | Tiết kiệm SEARCH (s) | Tổng tiết kiệm (s) | CI95 block-t của tiết kiệm (s) |
|---:|---:|---:|---:|---:|---:|---|
| 100 000 | 404.244 | 373.908 | 8.463 | 21.873 | **30.336** | [30.071, 30.602] |
| 1 000 000 | 3662.131 | 3434.938 | 8.463 | 218.730 | **227.194** | [224.537, 229.850] |

CI cố định các biên nhận BUILD lịch sử. Tại Q=100k, joint bootstrap cho [30.005, 30.667] s. Trên các hệ số đã đo, cả intercept lẫn slope đều thấp hơn ở Fast+B1+A1, nên mô hình không có giao điểm tại Q dương. Kết quả của G2 mang nhãn **EXPLORATORY_HOST_SPECIFIC**, **graph_population_ci = NOT_ESTIMABLE**. R86 thuộc pilot dùng để phát hiện vấn đề; R91 ngoài cohort tích hợp. [Các workload mô hình hóa](tables/table12_modeled_two_host_build_search.csv) · [Ma trận claim C1–C3, M1](../../task-da/TASK_D_FINAL_CLAIM_EVIDENCE_MATRIX.md)
