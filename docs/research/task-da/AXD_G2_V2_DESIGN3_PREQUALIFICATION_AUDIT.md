# A×D G2 v2 · `design-3` Pre-Qualification Scientific & Implementation Audit

- **Audit Verdict:** **`DESIGN3_READY_FOR_QUALIFICATION`** *(Stage 1–3 **PASS 100%**; Stage 4 `900 s` minimal-TTY qualification bàn giao qua 1 lệnh ngắn cho owner thực thi).*
- **Frozen Package Under Audit:** [AXD_G2_V2_DESIGN3_FREEZE_MANIFEST.json](AXD_G2_V2_DESIGN3_FREEZE_MANIFEST.json) (`SHA-256: 425c748329292ffe15db2c52bdf53f5d219b47d1ecf95ac3c76a5429814159ae`, `25` components) · [AXD_G2_V2_DESIGN3_FREEZE.sha256](AXD_G2_V2_DESIGN3_FREEZE.sha256) (`26/26 OK`) · [audit_design3.json](../../../.local/artifacts/axd-g2-v2-design3-freeze-20261124/audit_design3.json) · [BUNDLE.sha256](../../../.local/artifacts/axd-g2-v2-design3-freeze-20261124/BUNDLE.sha256) (`69c1951b...`).
- **Scope & Execution Accounting:** `EXPLORATORY_HOST_SPECIFIC` · `Quality ON = 0/18` · `G2 OFF = 0/144` (`NOT_OPEN`) · `Profiler = 0` · `v2_test_10000.ids materialized = false`.

---

## 1. Ma trận Kiểm toán Khoa học & Triển khai (Stage 2)

Toàn bộ kiểm chứng thực hiện trên môi trường Python bền vững `/home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python` (`Python 3.12.3`, SHA `e50d468e...`, `7/7` locked packages từ `requirements-g2-v2-design3.lock`) bằng dataset-free fixtures, synthetic telemetry và frozen receipts (tắt toàn bộ 5 biến native opt-in):

| Hạng mục kiểm toán Stage 2 | Cơ chế / Test xác minh | Kết quả |
|---|---|---|
| **1. Counter conservation & CPU time accounting** | `parse_proc_stat()` kiểm `0 <= agg - sum(cpu0..11) <= 6×12` (đúng toán học `nsec_to_clock_t` floor division của Linux `fs/proc/stat.c`, từ chối `< 0` và `> 72`); `test_topology_hierarchy_conservation_always_holds` kiểm 50 kịch bản ngẫu nhiên xác nhận `0 <= f_workers <= f_ccx0 <= f_all` luôn đúng. | **`PASS`** |
| **2. PID identity / reuse & cadence gaps** | `validate_step()` kiểm `0.5 s <= dt <= 2.0 s`, `CLK_TCK == 100`, `start_ticks` cố định cho cả `owned`, `monitor` và `watchdog`, và tính đơn điệu của từng per-CPU counter (`test_pid_reuse_gap_and_counter_regression_fail_closed`). | **`PASS`** |
| **3. Worker-core / CCX / L3 topology** | `host_contract()` xác minh trực tiếp trên Ryzen 5 PRO 4650U: `cpus=[0,2]`, `worker_cores_cpus=[0,1,2,3]`, `ccx0_cpus=[0,1,2,3,4,5]` (`L3 0-5`), `ccx1_l3_shared_list='6-11'`; `test_topology_ccx1_os_pulse_allowed_while_worker_cores_and_ccx0_strictly_guarded` kiểm đủ 4 kịch bản (`CCX1` pulse PASS; `CPU 1` SMT FAIL; `CPU 4` CCX0 L3 FAIL; `CPU 0` untracked hard-IRQ storm FAIL). | **`PASS`** |
| **4. Known CPU jobs & foreign contention** | `test_single_process_cap_and_known_cpu_jobs_instant_rejection` kiểm chặn tức thời `stress-ng` (không chờ cửa sổ 10s) ở cả `quality` và `off`, và chặn single foreign process ẩn danh `12%` core trên `CCX1` ở `off`; `test_quality_phase_allows_small_ccx1_os_load_but_blocks_overload_and_thermal` kiểm tách sạch `quality` (`<= 10%` host / `<= 25%` single) vs `off`. | **`PASS`** |
| **5. Missing telemetry, malformed records, thermal & RAM failure** | Kiểm fail-closed cho `/proc/<pid>/stat` cụt, `cpu11` bị thiếu, `Tctl >= 95°C` / `85°C`, `MemAvailable <= 1 GiB`, `free_disk <= 20 GiB`, `AC = 0`, `vm_hwm_kib <= 0/NaN/fractional/bool/str`, biên integer hard gate RAM `10(C-B) <= max(655360, B)` (`165536` PASS vs `165537` FAIL; `1100000` PASS vs `1100001` FAIL). | **`PASS`** |
| **6. False-abort do monitor / watchdog / quantization** | `test_watchdog_and_monitor_excluded_zero_false_abort` (monitor `2%` p2 + watchdog `1%` p2 -> `0` false abort); `test_net_window_subtraction_eliminates_quantization_rectification_false_abort` (`±2` tick jitter mỗi giây trong `20 s` -> `0` false abort); đo sống `10 s` cho thấy self-overhead `host_snapshot_v3` giảm từ `5.67%–6.84%` xuống **`1.62%` của 1 core (`0.81%` p2)**. | **`PASS`** |
| **7. Per-block paired noise balance** | `test_paired_noise_balance_detects_systematic_imbalance_without_altering_verdict` kiểm `imbalance_warning = False` khi cân bằng (`Spearman = null` khi hằng số, không `NaN`), `imbalance_warning = True` + `CI95 > 0` + Spearman hữu hạn khi `opt` chịu nhiễu cao hơn `base`, và từ chối process receipt vi phạm thứ tự topology. | **`PASS`** |
| **8. Không làm thay đổi quality/performance estimands** | `test_estimands_are_mathematically_identical_to_design2` chạy song song `g2_v2_analyzer.analyze` (`design-2`) và `g2_v2_design3_analyzer.analyze` (`design-3`) trên cùng fixture và kiểm **bằng nhau tuyệt đối** trên toàn bộ 20 trường đầu ra (`verdict`, `primary_reduction`, `speedup`, `primary_log_ci95`, `drift_log_ci95`, `query_bootstrap`, `joint_bootstrap`, `build_search`, `ram_hard_pass`, `safety_pass`, `stability_pass`, ...). | **`PASS`** |
| **9. Từ chối approval receipt `design-2` & mẫu `UNAPPROVED`** | Kiểm trực tiếp trên tệp approval `design-2` thật [quality_only_approval.json](../../../../artifact-evidence/axd-g2-v2-approvals/quality_only_approval.json) (`ad6f60cb...`) -> **BỊ TỪ CHỐI** (`design-2 or mismatched revision approval rejected; design-3 approval required`); cả hai template `UNAPPROVED` (`design-2` và `design-3`) đều bị từ chối; `design-3` bắt buộc khớp `qualification_sha256` của biên nhận `900 s` `QUALIFICATION_PASS`. | **`PASS`** |
| **10. Full repository dataset-free test suite** | `env -u TASK_DA_SMOKE ... /home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python -m unittest discover -s tests/research -v`: **`Ran 568 tests in 19.688s — OK (skipped=14)`** (`554` executed PASS gồm `17/17` `design-3` + `30/30` `design-2`, `14` native opt-in skipped, `0` errors, `0` failures). | **`PASS`** |

---

## 2. Xác minh Bảo toàn Bất biến (`design-2`, Historical v1 & Ràng buộc Không Đổi)

| Đối tượng bảo toàn | Đường dẫn / SHA-256 xác minh | Trạng thái |
|---|---|---|
| `24/24` protected `design-2` files | `sha256sum -c docs/research/task-da/AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256` -> `24/24 OK` | **`UNCHANGED`** |
| `design-2` freeze manifest | `configs/axd_g2_v2_freeze.json` = `91186d57e5992e1df70f86a55ba928ad4d6613bb0b67ccbee0f485cc380d1749` | **`UNCHANGED`** |
| `design-2` `UNAPPROVED` template | `configs/axd_g2_v2_approval.UNAPPROVED.json` = `0f76abc61992312e7e3fb5d447b0d0b4a3210c62958bb62065581efa37bb69ab` | **`UNCHANGED`** |
| Historical v1 prereg (`QUALITY_HOLD`) | `docs/research/task-da/AXD_G2_MINIMAL_PAIRED_PILOT_PREREG.md` = `cb6433cb2c04108653cca7e8d63ed9688f3b19fa68a0b236acccc28d766393eb` | **`UNCHANGED`** |
| Stage 5 / Stage 6 / Preflight 1 & 2 bundles | `82e740bc...`, `cd65a8ac...`, `cc079410...`, `02027ca0...` khớp 100% | **`UNCHANGED`** |
| Các tham số khoa học khóa | `6` graphs R90 v1.3, ELF `7a2685e5...`, `p=2`, `S=16`, `beam=432`, `v2_test_10000.ids` (`457abdc1...`), `LCB95 >= 0.990`, `±0.0005`, `3%` geometric, `12` blocks, RAM hard gate, `EXPLORATORY_HOST_SPECIFIC` | **`IDENTICAL`** |
| Thư mục output & split chưa mở | `axd-g2-v2-quality-design{2,3}`, `axd-g2-v2-off-design3`, `v2_test_10000.ids` đều không tồn tại | **`NOT_CREATED`** |
| Git & ngoài phạm vi | `git diff` rỗng (`0` tracked modifications), `0` commit, `Task A Google Sheets` không sửa | **`CLEAN`** |

---

## 3. Giới hạn Còn Mở & Điều kiện Chuyển Bước (Không Tự Chuyển Stage)

1. **Unknown còn lại duy nhất trước khi lập checklist ký approval `design-3`:** Kết quả thực tế của phiên qualification **`900 s` (`15 phút`)** trên minimal Linux TTY bằng lệnh ngắn `./scripts/run_g2_v2_design3_qualify.sh` (xem hướng dẫn tại [AXD_G2_V2_DESIGN3_IMPLEMENTATION_REPORT.md](AXD_G2_V2_DESIGN3_IMPLEMENTATION_REPORT.md) §3).
2. **Kiểm toàn vẹn độc lập cho `design-3` từ repo root:** `sha256sum -c docs/research/task-da/AXD_G2_V2_DESIGN3_FREEZE.sha256` (`26/26 OK`).
3. **Kết luận chính thức Stage 5:** **`DESIGN3_READY_FOR_QUALIFICATION`**. Chỉ sau khi owner chạy `./scripts/run_g2_v2_design3_qualify.sh` trên minimal TTY và đạt **`QUALIFICATION_PASS`** mới lập checklist để owner ký approval receipt mới cho `design-3`; nếu qualification thất bại thì giữ **`DESIGN3_HOLD`**, không tự sửa ngưỡng rồi chạy lại.
