# A×D G2 v2 (`design-3`) · Pre-Approval Review & Owner Approval Checklist (`QUALITY_ONLY`)

- **Official Readiness Verdict:** **`READY_FOR_OWNER_APPROVAL`** *(chỉ xét phê duyệt pha **`QUALITY_ONLY` — 18 tiến trình ON** theo `design-3`; pha **`G2 OFF` (144 tiến trình)** tiếp tục ở trạng thái **`NOT_OPEN`**).*
- **Protocol & Revision:** `AXD-G2-V2-3A-20261123` · revision **`design-3`** · schema **`axd_g2_v2.3`** · **`EXPLORATORY_HOST_SPECIFIC`** · `p=2`, `S=16`, `common beam = 432`.
- **Execution & Gate Accounting:** `Qualification #1 (20261124T082344Z) = QUALIFICATION_HOLD` *(giữ nguyên)* · `Qualification #2 (20261124T094602Z) = QUALIFICATION_PASS` *(853/853 10s, 848/848 15s, 0 hard fails)* · `Quality ON = 0/18` · `G2 OFF = 0/144` · `v2_test_10000.ids materialized = false`.
- **Unsigned Draft Location (ngoài frozen package):** `../../../../artifact-evidence/axd-g2-v2-approvals/design3_quality_only_approval.DRAFT_UNSIGNED.json` *(cố ý chưa ký, chưa điền `owner`/`approved_at`, giữ `scope: "UNAPPROVED"`, `quota_s: 0`, `quiet_host_confirmed: false` — bị verifier từ chối cho tới khi owner tự sao chép và ký).*
- **Strict Non-Mutation Disclosure:** Tài liệu này chỉ tổng hợp kiểm toán read-only và chuẩn bị bản nháp chưa ký; **không** chạy ANN, **không** materialize `v2_test_10000.ids`, **không** tự ký approval, **không** dùng approval `design-2`, **không** sửa frozen package/guard/protocol, **không** dừng dịch vụ hệ thống, và **không** sửa Task A / Google Sheets.

---

## 1. Kiểm toán Bằng chứng Qualification PASS (`20261124T094602Z`) & Toàn vẹn Freeze `design-3`

### 1.1 Xác minh Qualification PASS Bundle (`20261124T094602Z`)

Bằng chứng ngoài repo: `../../../../artifact-evidence/axd-g2-v2-design3-qualification-20261124T094602Z/`.

| Hạng mục xác minh | Kết quả đo / SHA-256 kiểm chứng | Trạng thái |
|---|---|---|
| `BUNDLE.sha256` (`qualification_result.json`) | `f64b9f9af6d230f320c2539c201079cbda42614c0a8b28f881b875fcf67c49cb` | **`OK`** |
| `BUNDLE.sha256` (`qualification_telemetry.jsonl`) | `832515669974e23eea0d615af07433f97cd0a23061567523bd931dcdf8d2ec47` | **`OK`** |
| `verify_qualification()` ([g2_v2_design3_runner.py](../../../research/task_da/g2_v2_design3_runner.py)) | `schema = "axd_g2_v2.3"`, `protocol = "AXD-G2-V2-3A-20261123"`, `revision = "design-3"`, `verdict = "QUALIFICATION_PASS"`, `qualification_pass = true` | **`PASS`** |
| Khớp `freeze_sha256` | `425c748329292ffe15db2c52bdf53f5d219b47d1ecf95ac3c76a5429814159ae` khớp nguyên bản [AXD_G2_V2_DESIGN3_FREEZE_MANIFEST.json](AXD_G2_V2_DESIGN3_FREEZE_MANIFEST.json) | **`EXACT MATCH`** |
| Thời lượng & số mẫu | `2026-11-24T09:46:02.975647Z` → `10:01:03.071933Z` (`observed_wall_s = 900.065 s >= 899 s`, `samples = 863`) | **`PASS`** |
| Cửa sổ `10s` (`worker-cores <= 0.01`, `CCX0 <= 0.02`, `single <= 0.10`) | **`853 PASS / 0 FAIL`** (`rolling_10s_workers max = 0.00817`; `rolling_10s_ccx0 max = 0.00962`; `rolling_10s_single_rate max = 0.01152`) | **`100% PASS`** |
| Cửa sổ `15s` (toàn host `[0..11] <= 0.025`) | **`848 PASS / 0 FAIL`** (`rolling_15s_all mean = 0.00766`, `p95 = 0.00897`, `max = 0.01141`) | **`100% PASS`** |
| Hard guard / nhiệt / tài nguyên | `hard_guard_failures = 0`; `Tctl = 37.25–56.375°C`; `AC = 1`; `min MemAvailable = 14.11 GiB`; `min free disk = 138.33 GiB`; `swap = 0 B` | **`0 FAIL`** |
| Monitor self-overhead | `11.37 s / 900.065 s` = **`1.263%`** của 1 core (`0.632%` công suất `p2`) | **`PASS`** |
| Independent telemetry replay (`863` snapshots) | Replay qua `make_guard(rows[0], phase="qualification")`: **`w10 = 853/0`, `w15 = 848/0`, `hard = 0`**; `avahi`/`gnome-shell`/`gdm`/`cups-browsed` đều **`0` xuất hiện** | **`EXACT MATCH`** |
| Bảo toàn lịch sử Qualification HOLD (`20261124T082344Z`) | `sha256sum -c BUNDLE.sha256` -> `2/2 OK` | **`UNCHANGED`** |

*(Ghi chú kiểm chứng khoa học: đỉnh `rolling_10s_workers.max` đo thực tế là **`0.00817`**, khớp gần như tuyệt đối với dự báo đối chứng phân tích `0.00816` trong [AXD_G2_V2_DESIGN3_QUALIFICATION_ANALYSIS_20261124.md](AXD_G2_V2_DESIGN3_QUALIFICATION_ANALYSIS_20261124.md).)*

### 1.2 Xác minh Tất cả Điều kiện Tiên quyết Mở `QUALITY_ONLY`

| # | Điều kiện mở `QUALITY_ONLY` | Bằng chứng kiểm tra trực tiếp | Trạng thái |
|---:|---|---|---|
| 1 | **900s Host Qualification `design-3`** | `20261124T094602Z` đạt `QUALIFICATION_PASS` (`853/853` 10s, `848/848` 15s, `0` hard fails, replay khớp 100%) | **`PASS`** |
| 2 | **Toàn vẹn frozen package `design-3`** | [AXD_G2_V2_DESIGN3_FREEZE.sha256](AXD_G2_V2_DESIGN3_FREEZE.sha256) **`26/26 OK`**; freeze bundle [.local/artifacts/axd-g2-v2-design3-freeze-20261124/BUNDLE.sha256](../../../.local/artifacts/axd-g2-v2-design3-freeze-20261124/BUNDLE.sha256) **`4/4 OK`** (gồm `quality_plan_design3_final.json` `c501f752...`, 18 lệnh ON) | **`PASS`** |
| 3 | **Bảo toàn `design-2` & lịch sử** | [AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256](AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256) **`24/24 OK`**; `git diff` trống (`0` file tracked bị sửa) | **`PASS`** |
| 4 | **Môi trường Python & loader** | `/home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python` (`Python 3.12.3`, SHA `e50d468e...`, `7/7` wheels): `load_freeze(environment=True)` **`PASS`**; `require_default_loader()` **`PASS`** | **`PASS`** |
| 5 | **Topology host Ryzen 5 PRO 4650U** | `host_contract()` **`PASS`**: `cpus=[0,2]`, `worker_cores=[0..3]`, `CCX0=[0..5]`, `CCX1=[6..11]`, `allowed_cpus=12`, `kernel=7.0.0-43-generic`, `CLK_TCK=100` | **`PASS`** |
| 6 | **Dataset, 6 graphs R90 v1.3, ELF, compiler, `.so`, Stage 5 baselines** | `configs/axd_g2_v2_design3_artifacts.proposed.json` (`6b49cce5...`) hợp schema; `native_runtime` **`5/5 OK`**; `/usr/bin/c++` **`OK`**; `binary/base/queries/gt/val/warmup` **`6/6 OK`**; `6` graphs gốc R90 v1.3 **`6/6 OK`**; `6` Stage 5 `beam_432_p2_ON.jsonl` baselines **`6/6 OK`** | **`PASS`** |
| 7 | **Test panel gate (`v2_test_10000.ids`)** | Đã xác minh đường dẫn `axd-g2-v2-inputs-design3/v2_test_10000.ids` **CHƯA TỒN TẠI** (chỉ được materialize một lần *sau khi* owner ký approval) | **`PASS (GATED)`** |
| 8 | **Output directory chưa tồn tại** | Đã xác minh `axd-g2-v2-quality-design3` **CHƯA TỒN TẠI** (`execute()` cấm ghi đè/resume) | **`PASS`** |
| 9 | **Cách ly approval `design-2` & template** | `g2_v2_design3_contract.authorize()` từ chối trực tiếp approval `design-2` đã ký (`quality_only_approval.json`), từ chối `configs/axd_g2_v2_design3_approval.UNAPPROVED.json`, và từ chối bản nháp `DRAFT_UNSIGNED.json` | **`PASS`** |
| 10 | **Dataset-free test suite** | `python -m unittest discover -s tests/research -v`: **`Ran 568 tests — OK (skipped=14)`** (`554 PASS`, `0` failures/errors) | **`PASS`** |
| 11 | **Owner ký approval receipt `design-3`** | Đang chờ **owner** tự rà soát, điền 5 trường xác nhận và lưu tệp đã ký ngoài frozen package | **`WAITING_OWNER`** |

---

## 2. Đặc tả Schema `axd_g2_v2.3` (`#/$defs/approval`) & Danh mục Trường Owner Phải Tự Xác nhận

Đối chiếu nguyên văn [axd_g2_v2_design3.schema.json](../../../configs/axd_g2_v2_design3.schema.json) (`#/$defs/approval`, lines 904–976, `additionalProperties: false`) và [g2_v2_design3_contract.py](../../../research/task_da/g2_v2_design3_contract.py) (`authorize()`, lines 125–151):
- Schema bắt buộc đúng **12 trường** cho pha `QUALITY_ONLY` (trường thứ 13 `quality_sha256` **bị cấm** trong `QUALITY_ONLY` và chỉ dùng cho phê duyệt pha `OFF` riêng về sau).
- **Tuyệt đối không** dùng approval của `design-2` và **không** chỉnh sửa [axd_g2_v2_design3_approval.UNAPPROVED.json](../../../configs/axd_g2_v2_design3_approval.UNAPPROVED.json).

### 2.1 Nhóm A — 5 Trường Owner BẮT BUỘC Tự Điền & Xác nhận Trong Tệp Ký

*(Trong bản nháp `design3_quality_only_approval.DRAFT_UNSIGNED.json`, toàn bộ 5 trường này cố ý để trống / chưa xác nhận để tránh ký thay.)*

| Trường JSON | Giá trị trong bản nháp chưa ký | Quy tắc verifier & giá trị Owner cần điền khi ký | Ý nghĩa pháp lý / khoa học của trường |
|---|---|---|---|
| **`owner`** | `""` *(trống)* | Chuỗi không rỗng (`minLength: 1`), ví dụ tên/định danh owner thật của bạn | Xác nhận danh tính người sở hữu dự án chịu trách nhiệm mở pha `QUALITY_ONLY`. |
| **`approved_at`** | `""` *(trống)* | ISO-8601 **bắt buộc có múi giờ** (`tzinfo is not None`), ví dụ `"2026-11-24T17:45:00+07:00"` | Đóng dấu thời điểm phê duyệt thực tế sau khi đã xem kết quả qualification PASS (`10:01:03Z` / `17:01:03+07`). |
| **`scope`** | `"UNAPPROVED"` | Đổi chính xác thành **`"QUALITY_ONLY"`** *(không dùng `"OFF_A"` hay `"OFF_AB"`)* | Giới hạn cứng phạm vi ủy quyền chỉ gồm `18` tiến trình ON kiểm tra chất lượng; tiếp tục khóa hoàn toàn `144` tiến trình OFF. |
| **`quota_s`** | `0` | Đổi chính xác thành **`3600`** *(số nguyên)* | Giới hạn tổng thời gian wall-clock tối đa cho cả pha `QUALITY_ONLY` là đúng 3600 giây (1 giờ); pha OFF là `10800` và bị từ chối ở pha quality. |
| **`quiet_host_confirmed`** | `false` | Đổi thành **`true`** *(boolean)* | Xác nhận của owner rằng bằng chứng `900s` qualification PASS đã được kiểm duyệt và lượt chạy 18 ON sẽ thực hiện trên cùng điều kiện quiet-host an toàn. |

### 2.2 Nhóm B — 7 Trường Khóa Cố định Đã Điền Sẵn Trong Bản Nháp (Owner Cần Đối Chiếu Trước Khi Ký)

| Trường JSON | Giá trị đã điền sẵn trong `DRAFT_UNSIGNED.json` | Nguồn đối chiếu độc lập |
|---|---|---|
| `schema` | `"axd_g2_v2.3"` | Hằng số schema `design-3` (`configs/axd_g2_v2_design3.schema.json`) |
| `protocol` | `"AXD-G2-V2-3A-20261123"` | Mã preregistration khóa |
| `revision` | `"design-3"` | Bản tu chính B1 guard (từ chối `design-2`) |
| `freeze_sha256` | `"425c748329292ffe15db2c52bdf53f5d219b47d1ecf95ac3c76a5429814159ae"` | `sha256sum docs/research/task-da/AXD_G2_V2_DESIGN3_FREEZE_MANIFEST.json` |
| `artifacts_sha256` | `"6b49cce57a9520ef650dafda0ffd1deb735d6546569d7bbc5b1cdf2a3045f068"` | `sha256sum configs/axd_g2_v2_design3_artifacts.proposed.json` |
| `qualification_sha256` | `"f64b9f9af6d230f320c2539c201079cbda42614c0a8b28f881b875fcf67c49cb"` | `sha256sum ../artifact-evidence/axd-g2-v2-design3-qualification-20261124T094602Z/qualification_result.json` |
| `output_directory` | `"/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-quality-design3"` | Khớp đường dẫn tuyệt đối `resolve()` trong `quality_plan_design3_final.json` (chưa tồn tại) |

---

## 3. Cách Owner Tạo Tệp Ký & Kiểm tra Receipt Trước Khi Chạy (Read-Only, 0 ANN)

### Bước 1 — Tạo bản sao để Owner tự điền 5 trường tại Mục 2.1
```bash
cp "/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-approvals/design3_quality_only_approval.DRAFT_UNSIGNED.json" \
   "/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-approvals/design3_quality_only_approval.json"
```
Sau đó owner mở tệp mới `design3_quality_only_approval.json`, đối chiếu 7 trường Nhóm B và tự điền 5 trường Nhóm A (`owner`, `approved_at`, `scope: "QUALITY_ONLY"`, `quota_s: 3600`, `quiet_host_confirmed: true`). Không thêm bất kỳ khóa JSON phụ nào.

### Bước 2 — Xác minh Receipt bằng chính Contract Verifier của `design-3` (Read-Only)
```bash
cd "/home/thinhbui/Documents/ChatGPT/Research ANN/task-d"
APPROVAL="/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-approvals/design3_quality_only_approval.json"
QUAL="/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-design3-qualification-20261124T094602Z/qualification_result.json"

env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT \
  /home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python - "$APPROVAL" "$QUAL" <<'PY'
import json, sys
from pathlib import Path
from research.task_da.g2_v2_design3_contract import FREEZE, authorize, load_freeze, sha
from research.task_da.g2_v2_design3_runner import verify_qualification

approval_path = Path(sys.argv[1])
qual_path = Path(sys.argv[2])
load_freeze(environment=True)
verify_qualification(qual_path)
approval = json.loads(approval_path.read_text())
scope = authorize(
    approval,
    sha(FREEZE),
    sha("configs/axd_g2_v2_design3_artifacts.proposed.json"),
    "quality",
    "/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-quality-design3",
    qualification_digest=sha(qual_path),
)
print("DESIGN3_APPROVAL_CHECK=PASS", "scope=", scope, "approval_sha256=", sha(approval_path))
PY
```
- **Kỳ vọng:** in `DESIGN3_APPROVAL_CHECK=PASS scope= QUALITY_ONLY approval_sha256= <64-hex>`.
- **Nếu thiếu/sai bất kỳ trường nào** (hoặc dùng nhầm receipt `design-2` / bản nháp `DRAFT_UNSIGNED.json`): lệnh dừng lỗi `ValueError` và tuyệt đối không được tiến sang bước chạy.

---

## 4. Kế hoạch Thực hiện 18 Lượt `QUALITY_ONLY` Sau Khi Owner Ký Phê duyệt (Chưa Thực Thi)

### 4.1 Cấu trúc 18 tiến trình ON tuần tự (theo `quality_plan_design3_final.json`)
- Cấu hình cố định: `task_da_p2_eval` (`7a2685e5...`), `pipnn`, `p=2`, `CPU [0,2]`, `S=16`, `flat`, `jobs=1`, `K=10`, `entry=0`, `common beam = 432`, `warmup = 100`, `N = 10,000`, `mode = ON`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OMP_DYNAMIC=FALSE`.
- **6 tiến trình đầu (`validation` panel `val_10k.ids`, `opt = barrier_all_evaled + incremental`):** chạy trên 6 graph R90 v1.3 (`stock_off_r1..r3`, `fast_off_r1..r3`), đối chiếu bit-exact ordered Top-10 & `squared_l2` với 6 baseline `beam_432_p2_ON.jsonl` đóng băng từ Stage 5 và kiểm `duplicate_l2_saved > 0`.
- **12 tiến trình sau (`test` panel `v2_test_10000.ids`, cả `base` và `opt`):** 2 policy × 6 graph, đối chiếu parity từng cặp query (tổng 120.000 lượt truy vấn test ON), kiểm `duplicate_l2_saved > 0`, tính **Gate A** (`simultaneous one-sided LCB95 >= 0.990`, `z = 2.39397980`) và **Gate B** (`arm CI95 ∈ (-0.0005, +0.0005)`).

### 4.2 Chuẩn bị Môi trường Quiet Host Phù hợp (Phương án GRUB `multi-user.target` Đã Đạt PASS)
- **Lưu ý chính sách pha `quality` trong `design-3`:** `PHASE_POLICIES['quality']` giữ toàn bộ hard safety/thermal (`Tctl < 85°C` start / `>= 95°C` abort, `AC = 1`, `MemAvailable > 1 GiB`, `free_disk > 25 GiB` start / `> 20 GiB` running, `swap growth <= 64 MiB`, instant reject `KNOWN_CPU_JOBS`) và ghi đầy đủ telemetry phân tầng; áp trần chống quá tải `host [0..11] <= 0.10 (15s)`, `single foreign process <= 0.25 (10s)`, `preflight >= 10s`.
- **Tuyệt đối KHÔNG chạy `sudo systemctl stop gdm.service` từ TTY** *(từng gây mất phản hồi máy phải tắt nguồn cứng)*. Tái lập đúng môi trường đã đạt `QUALIFICATION_PASS` (`20261124T094602Z`):
  1. Cắm nguồn AC, reboot và tại GRUB nhấn `e`, thêm **`systemd.unit=multi-user.target`** vào cuối dòng `linux` (chỉ áp dụng 1 lần, không sửa cấu hình hệ thống), nhấn `Ctrl+X`.
  2. Trên text console, xác minh `uname -r` = `7.0.0-43-generic` và `systemctl is-active gdm.service` = `inactive`.
  3. Tạm dừng các dịch vụ mDNS/in ấn (và tùy chọn timer định kỳ):
     ```bash
     sudo systemctl stop cups-browsed.service avahi-daemon.socket avahi-daemon.service
     sudo systemctl stop sysstat-collect.timer fwupd-refresh.timer
     ```
  4. Kiểm tra `systemctl is-active gdm.service cups-browsed.service avahi-daemon.socket avahi-daemon.service` đều `inactive` và `pgrep -af 'avahi-daemon|gnome-shell|gdm3|cups-browsed'` trống. *(Sau khi chạy xong chỉ cần `sudo reboot` để quay về Ubuntu Desktop bình thường.)*

### 4.3 Trình tự Thực thi Sau Approval (Chỉ Chạy Sau Khi Owner Ký & Verifier PASS)
1. **Materialize một lần duy nhất `v2_test_10000.ids`** tại `/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-inputs-design3/v2_test_10000.ids` theo đúng công thức khóa [AXD_G2_V2_QUERY_SPLIT_AUDIT.md](AXD_G2_V2_QUERY_SPLIT_AUDIT.md) §4 (`prefix = "axd-g2-v2-3a-test10k-20261123/"`); xác minh `count == 10000`, `unique == 10000`, `overlap == 0` với `val_10k` / `pilot3k` / `disjoint3k` / `narrow3k`, 10 ID đầu `32792,20400,17878,72872,61505,35404,40783,34564,23435,79120`, và **`SHA-256 == 457abdc13abc95d8d0f48ff32919a6013f5ed4bca469f9075312ae80dfe44b0d`**.
2. **Chạy đúng 18 tiến trình `QUALITY_ONLY` qua runner `design-3` đóng băng:**
   ```bash
   cd "/home/thinhbui/Documents/ChatGPT/Research ANN/task-d"
   env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT \
     /home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python -m research.task_da.g2_v2_design3_runner execute \
     --phase quality \
     --artifacts configs/axd_g2_v2_design3_artifacts.proposed.json \
     --approval "/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-approvals/design3_quality_only_approval.json" \
     --qualification "/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-design3-qualification-20261124T094602Z/qualification_result.json" \
     --output "/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-quality-design3"
   ```
3. **Khôi phục về Ubuntu Desktop bình thường sau khi runner kết thúc:**
   ```bash
   sudo reboot
   ```
   *(Do tham số GRUB `systemd.unit=multi-user.target` chỉ áp dụng 1 lần và không có dịch vụ nào bị `disable`, khởi động lại sẽ tự khôi phục nguyên trạng `graphical.target` cùng toàn bộ dịch vụ mặc định.)*
4. **Hậu kiểm độc lập & niêm phong `BUNDLE.sha256`** cho thư mục `axd-g2-v2-quality-design3` (`start.json`, `18` `*_preflight.jsonl`, `18` thư mục process gồm `metrics.json`/`manifest.json`/`host.jsonl`/`p2_eval_summary.json`/`beam_432_p2_ON.jsonl`, `quality.json`, `complete.json`).

### 4.4 Điều kiện Dừng Bắt buộc (Fail-Closed Stop Rules)
- **Dừng runtime ngay lập tức (`HOLD.json`):** bất kỳ lỗi `exit_code != 0`, `guard_failure`, `Tctl >= 95°C` (hoặc timeout hạ nhiệt `>= 85°C`), mất nguồn AC (`AC != 1`), `MemAvailable <= 1 GiB`, `free_disk <= 20 GiB` (`<= 25 GiB` lúc khởi động), `swap` tăng `> 64 MiB`, `KNOWN_CPU_JOBS`, tải quá mức (`host > 0.10` / `single > 0.25`), timeout `> 180 s/process`, hoặc vượt `quota_s = 3600 s`. Tuyệt đối không ghi đè hoặc resume đè vào thư mục đã tạo `HOLD.json`.
- **Dừng tại Quality Gate (`QUALITY_HOLD`):** nếu bất kỳ cặp nào sai parity Top-10 / `squared_l2`, hoặc `duplicate_l2_saved <= 0`, hoặc **Gate A FAIL** (`A_pass == false`, tức tồn tại graph có `LCB95 < 0.990`) -> đóng ở `QUALITY_HOLD`, giữ `144 OFF = NOT_OPEN`, cấm retune beam hoặc mở 71.000 query còn lại.
- **Dừng theo phạm vi ủy quyền sau khi hoàn tất 18 ON:** ngay cả khi `A_pass == true` (và `B_pass == true/false`), **DỪNG** để báo cáo owner thẩm định `quality.json`. Pha `144 OFF` đòi hỏi một biên nhận phê duyệt mới tách biệt (`scope: "OFF_A"` hoặc `"OFF_AB"`, `quota_s: 10800`, kèm `quality_sha256 = sha256(quality.json)`).

---

## 5. Kết luận Trạng thái

- **Verdict:** **`READY_FOR_OWNER_APPROVAL`** (`design-3` · `QUALITY_ONLY` · `18 ON`).
- **Điều kiện duy nhất còn lại để mở thực thi:** Owner tự kiểm tra bản nháp `design3_quality_only_approval.DRAFT_UNSIGNED.json`, tạo tệp ký `design3_quality_only_approval.json` với đầy đủ 5 trường Nhóm A và chạy lệnh kiểm chứng ở Mục 3.
