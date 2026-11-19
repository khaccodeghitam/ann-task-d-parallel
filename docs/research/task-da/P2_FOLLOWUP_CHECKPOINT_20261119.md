# Task D — P2 Follow-Up Checkpoint (`2026-11-19`)

- **Checkpoint Status:** **`COMPLETE_AT_STAGE_E_H3_PIVOT`** *(Hoàn tất toàn bộ Giai đoạn A -> E trên binary thống nhất `ff46d6ac...`; `0` tiến trình nền còn chạy; toàn bộ `1,777` tệp evidence `2,491.26 MiB` đã băm SHA-256 trong `../artifact-evidence/p2-followup-20261118/EVIDENCE_CHECKSUMS.csv` và `18/18` tệp bất biến xác minh nguyên vẹn.)*
- **Preserved Gates (Không thay đổi):** `Historical P0 = HOLD`, `Full P1 Gate = HOLD`, `t0998 = HOLD`, `Protocol V4 D1–D5 = UNAPPROVED`, `P3 Official = CLOSED`, `TP-CG / H3 = NOT_OPENED` *(quyết định Giai đoạn E: **`PIVOT`**; máy `i5-14600KF`: **`NOT_AVAILABLE_ON_THIS_HOST_NOT_RUN`**)*.
- **Host:** `thinhbui-linux` (`AMD Ryzen 5 PRO 4650U`, 6 cores / 12 threads, pinned `0 / 0,2 / 0,2,4,6`).

---

## 1. Trạng thái hoàn thành từng Giai đoạn (`OBSERVED`)

| Giai đoạn | Trạng thái | Đường dẫn & Kết quả chính |
|---|---|---|
| **Giai đoạn A — Evidence Audit** | **`COMPLETE`** | `../artifact-evidence/p2-followup-20261118/stage_a_audit_report.json`: `227/227` tệp khớp SHA-256 trong `EVIDENCE_CHECKSUMS.csv`; `45/45` `OFF` và `18/18` `ON` hợp lệ; xác nhận `duplicate_expansions != already_seen_attempts`; tái tính `paired_mean` vs `ratio_of_aggregate_means` (giải thích bất đẳng thức Jensen + pairing nhiệt). |
| **Giai đoạn B — Strict Matched Recall (`val_10k` ONLY)** | **`COMPLETE`** | Chứng minh **step-32 lattice có `0` bộ ba hợp lệ** đạt `\|ΔRecall\| <= 0.0001`. Hiệu chỉnh lưới tinh trên `val_10k` chọn `A0_r1` (`420/416/408`), `A1_r1` (`426/424/416`), `A3_r1` (`976/970/960`) (`global span = 0.000090`). Chạy lại Pilot H1 (`45` OFF + `18` ON): `stage_b_h1_off_summary.json`. |
| **Giai đoạn C1 — Ablation `sync_interval = {4,8,16,32}` (`std::set` nguyên bản)** | **`COMPLETE`** | Hiệu chỉnh `val_10k` (`sync_val10k_calibration.json`) + `22` nhánh (`110` lượt `OFF` + `22` lượt `ON` đối chứng parity): `stage_c_sync_ablation_summary.json`. Xác nhận `S=16` tối ưu nhưng `std::set` gặp sàn `~1.13 ms` trên `A3_r1`; `S=32` làm `dup_exp` tăng vọt (`134.8`) khiến `p=4` chậm lại. |
| **Giai đoạn C2 — Ablation `--merge-impl set\|flat`** | **`COMPLETE`** | Mã nguồn [p2_engine.hpp](../../../research/task_da/search_common/p2_engine.hpp) & [p2_eval.cpp](../../../research/task_da/search_common/p2_eval.cpp) (`task_da_p2_eval` SHA-256 `ff46d6ac8895d519054548575c3187544716c0fdf2bbdad83db8a0a8cc7f8759`), Release CTest `24/24 OK`, ASan+UBSan+LSan CTest `24/24 OK`, **`14/14` smoke parity `flat == set` từng bit + ASan `100q A3 p=4` PASS**, hoàn tất trọn vẹn `110/110` `OFF` + `22/22` `ON`: `stage_c_merge_ablation_summary.json`. |
| **Giai đoạn D — Replication (`A0/A1/A3 × R1/R2/R3 × p={1,2,4}`)** | **`COMPLETE`** | Hiệu chỉnh `45` ô `val_10k` (`stage_d_val10k_45cells_manifest.json`, `global_recall_span = 0.000090 <= 0.0001`, tất cả `LCB95 >= 0.990`). Chạy ma trận `63` ô × (`5 OFF + 1 ON` = `378` lượt) đồng nhất trên `ff46d6ac...`: `63/63` exact `ON/OFF` parity & invariants PASS, `0` incomplete top-10, `test3k_recall` `63/63 >= 0.990` (`stage_d_replication_summary.json`, `STAGE_D_REPLICATION_SUMMARY.csv`, `stage_d_decomposition.json`). |
| **Giai đoạn E — Decision Report (`H3: TP-CG`)** | **`COMPLETE` (`PIVOT`)** | Báo cáo tổng hợp & luận chứng định lượng tại [STAGE_D_E_REPLICATION_AND_H3_DECISION.md](STAGE_D_E_REPLICATION_AND_H3_DECISION.md) và [P2_MULTIWALKER_IMPLEMENTATION_STATUS.md](P2_MULTIWALKER_IMPLEMENTATION_STATUS.md). Khuyến nghị **`PIVOT`** (không mở `TP-CG`); xem 3 hướng ưu tiên kế tiếp (chạy lại ma trận trên `i5-14600KF` khi có máy, loại quét tuyến tự `merge/frontier` `407–719 us`, và giảm `3.8k–6.2k` L2 eval trùng). |

---

## 2. Chỉ mục Verification & Evidence

- **Checksums toàn chiến dịch:** `../artifact-evidence/p2-followup-20261118/EVIDENCE_CHECKSUMS.csv` (`1,777` tệp, `2,491.26 MiB`, `18/18` immutable files verified).
- **Báo cáo chính:** [STAGE_D_E_REPLICATION_AND_H3_DECISION.md](STAGE_D_E_REPLICATION_AND_H3_DECISION.md) & bảng tổng hợp CSV `../artifact-evidence/p2-followup-20261118/stage_d_replication/STAGE_D_REPLICATION_SUMMARY.csv`.
