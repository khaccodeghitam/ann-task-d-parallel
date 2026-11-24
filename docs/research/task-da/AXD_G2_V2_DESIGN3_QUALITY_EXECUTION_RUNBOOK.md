# A×D G2 v2 (`design-3`) · `QUALITY_ONLY` Pre-Execution Audit & TTY Runbook

- **Official Preparation Verdict:** **`READY_FOR_QUALITY_EXECUTION`** *(chuẩn bị & preflight read-only đã **PASS 100%**; chưa materialize `v2_test_10000.ids`, chưa chạy `18` Quality ON, và **`144 G2 OFF` tiếp tục ở trạng thái `NOT_OPEN`**).*
- **Signed Owner Approval Receipt:** `../../../../artifact-evidence/axd-g2-v2-approvals/design3_quality_only_approval.json`
  - **SHA-256:** `bb482f042a226c14bc163efde6bebe8b865351cfd69dfa45c34298d802ce2002` *(đã khớp 100%, giữ nguyên bản sao lưu `.bak`)*
  - **Owner / Timestamp / Scope / Quota:** `owner = "thinhbui"` · `approved_at = "2026-11-24T17:49:30+07:00"` · `scope = "QUALITY_ONLY"` · `quota_s = 3600` · `quiet_host_confirmed = true`
- **Qualification PASS Receipt:** `../../../../artifact-evidence/axd-g2-v2-design3-qualification-20261124T094602Z/qualification_result.json` (`f64b9f9af6d230f320c2539c201079cbda42614c0a8b28f881b875fcf67c49cb`, `853/853` 10s, `848/848` 15s, `0` hard fails)
- **Orchestrator Script (ngoài frozen package):** [run_g2_v2_design3_quality.sh](../../../scripts/run_g2_v2_design3_quality.sh)

---

## 1. Kiểm toán Approval Đã Ký, Qualification PASS, Freeze & Provenance

| Hạng mục kiểm toán | Bằng chứng kiểm tra trực tiếp | Trạng thái |
|---|---|---|
| Signed Approval SHA-256 & 7 trường pinned | `bb482f042a226c14bc163efde6bebe8b865351cfd69dfa45c34298d802ce2002`; cả 7 trường (`schema`, `protocol`, `revision`, `freeze_sha256`, `artifacts_sha256`, `qualification_sha256`, `output_directory`) khớp 100% `DRAFT_UNSIGNED` & freeze manifest; 5 trường owner không bị sửa | **`PASS`** |
| Contract Verifier `authorize(..., "quality")` | `scope = "QUALITY_ONLY"`, `quota_s = 3600`, `quiet_host_confirmed = true`, timezone `+07:00` hợp lệ | **`PASS`** |
| Khóa cứng `144 OFF = NOT_OPEN` | Kiểm trực tiếp `authorize(..., "off")` trên cùng tệp approval -> **BỊ TỪ CHỐI** (`output_directory`, `scope`, `quota_s`, thiếu `quality_sha256`) | **`VERIFIED BLOCKED`** |
| Qualification PASS (`20261124T094602Z`) & HOLD lịch sử (`20261124T082344Z`) | `BUNDLE.sha256`: PASS `2/2 OK`, HOLD `2/2 OK`; `verify_qualification()` PASS | **`PASS`** |
| Toàn vẹn Frozen Package `design-3` & `design-2` | [AXD_G2_V2_DESIGN3_FREEZE.sha256](AXD_G2_V2_DESIGN3_FREEZE.sha256) **`26/26 OK`**; [.local/artifacts/axd-g2-v2-design3-freeze-20261124/BUNDLE.sha256](../../../.local/artifacts/axd-g2-v2-design3-freeze-20261124/BUNDLE.sha256) **`4/4 OK`**; `design-2` **`24/24 OK`**; `git diff` trống | **`PASS`** |
| Provenance đầu vào, đồ thị & runtime | `load_freeze(environment=True)` PASS (`Python 3.12.3`, `e50d468e...`, `7/7` wheels); `host_contract()` PASS (`7.0.0-43-generic`, Ryzen 5 PRO 4650U); `native_runtime` `5/5`, `/usr/bin/c++`, `binary/base/queries/gt/val/warmup` `6/6`, `6/6` R90 v1.3 graphs, `6/6` Stage 5 baselines đều **EXACT MATCH** | **`PASS`** |
| Kế hoạch 18 lệnh ON | `plan(artifacts, "quality", out_dir)` khớp từng byte với `quality_plan_design3_final.json`: **6 validation `opt` ON + 12 test `base/opt` ON** trên 6 graph R90 v1.3, `beam=432`, `p=2`, `S=16` | **`EXACT MATCH`** |

---

## 2. Xác minh Khả năng Hiệu lực Qua Lần Boot Kế Tiếp (`systemd.unit=multi-user.target`)

Đã kiểm toán từng dòng mã của [g2_v2_design3_contract.py](../../../research/task_da/g2_v2_design3_contract.py), [g2_v2_design3_runner.py](../../../research/task_da/g2_v2_design3_runner.py) và [g2_v2_design3_guard.py](../../../research/task_da/g2_v2_design3_guard.py):

- **Qualification PASS (`20261124T094602Z`) và Approval đã ký (`bb482f04...`) HOÀN TOÀN CÒN HIỆU LỰC sau khi reboot sang `systemd.unit=multi-user.target`.**
  - `verify_qualification()` và `authorize()` **KHÔNG** gắn với `boot_id`, `uptime`, hay tính liên tục `monotonic_s` từ phiên qualification trước. Chúng kiểm tra schema, `freeze_sha256`, `artifacts_sha256`, `qualification_sha256`, `verdict == "QUALIFICATION_PASS"`, `853/0` & `848/0` & `hard == 0`, và SHA của `qualification_telemetry.jsonl`.
  - Toàn bộ đường dẫn bền vững đều nằm ngoài `/tmp`: venv Python tại `/home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python`, evidence/approval tại `/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/`, repo tại `/home/thinhbui/Documents/ChatGPT/Research ANN/task-d/`. Lock `/tmp/task-da-pivot-4650u.lock` được runner tự tạo mới sạch sau reboot.
- **Hai điều kiện duy nhất cần giữ nguyên khi boot lại:**
  1. **Chọn đúng kernel `7.0.0-43-generic`** *(hiện là bản mới nhất mặc định trong `/boot/vmlinuz-7.0.0-43-generic`; nếu chọn nhầm `7.0.0-42-generic` hoặc chạy `apt upgrade` lên kernel mới trước khi đo, `host_contract()` sẽ tự từ chối fail-closed vì lệch `kernel`).*
  2. **Không chạy `apt upgrade` nâng cấp `glibc`/`libstdc++`/`python3.12` trước khi hoàn tất pha `QUALITY_ONLY`** *(vì `verify_artifacts()` kiểm exact SHA-256 của 5 thư viện `.so` và `python_executable_sha256`).*

---

## 3. Kiểm tra Điều kiện B4 & Chống Test Leakage (Chưa Materialize)

- **Trạng thái trên đĩa hiện tại:** `axd-g2-v2-inputs-design3/v2_test_10000.ids` **CHƯA TỒN TẠI**; thư mục đích `axd-g2-v2-quality-design3` **CHƯA TỒN TẠI**.
- **Kiểm tra tái lập trong bộ nhớ (0 byte ghi ra đĩa):**
  - `6/6` tệp nguồn bất biến (`val_10k.ids`, `test_90k.ids`, `pilot_test_3000.ids`, `disjoint_test_3000.ids`, `narrow_test_3000.ids`, `warmup_val_100.ids`) khớp 100% SHA-256 từ [AXD_G2_V2_QUERY_SPLIT_AUDIT.md](AXD_G2_V2_QUERY_SPLIT_AUDIT.md).
  - Pool `test_90k \ (pilot3k ∪ disjoint3k ∪ narrow3k)` có đúng `81.000` ID (`sorted SHA = ab1de8ef151cc0fffce9b859d3f6f674bdf81581afe592a633aa605e3f4acef1`).
  - Xếp hạng theo `(SHA256("axd-g2-v2-3a-test10k-20261123/" + id), id)` và lấy `10.000` ID đầu cho kết quả khớp tuyệt đối:
    - **`count = 10,000`**, **`unique = 10,000`**, biên `[0, 99999]`.
    - **`overlap = 0`** với `val_10k`, `pilot_test_3000`, `disjoint_test_3000`, `narrow_test_3000`, và `warmup_val_100`.
    - 10 ID đầu: `32792, 20400, 17878, 72872, 61505, 35404, 40783, 34564, 23435, 79120`.
    - **Expected `SHA-256`:** **`457abdc13abc95d8d0f48ff32919a6013f5ed4bca469f9075312ae80dfe44b0d`**.
- **Bảo vệ chống test leakage:** Script `run_g2_v2_design3_quality.sh` chỉ ghi `v2_test_10000.ids` **một lần duy nhất (`open("xb")`)** *sau khi* toàn bộ preflight (freeze 26/26, kernel `7.0.0-43-generic`, AC=1, GDM/Avahi/cups-browsed đều `inactive`, approval `bb482f04...`, qualification PASS) đều PASS. 71.000 ID còn lại trong pool không bao giờ được mở.

---

## 4. Hướng dẫn Thực thi An toàn Trên Ubuntu TTY (Cho Owner Tự Chạy)

> [!CAUTION]
> **TUYỆT ĐỐI KHÔNG CHẠY `sudo systemctl stop gdm.service` từ TTY** *(đã từng gây treo máy phải tắt nguồn cứng)*. Luôn dùng phương pháp **boot GRUB một lần với `systemd.unit=multi-user.target`** đã kiểm chứng PASS (`20261124T094602Z`) — không chỉnh `/etc/default/grub`, không đổi kernel/BIOS/IRQ/CPU governor vĩnh viễn.

### Bước 1 — Boot một lần vào `multi-user.target` từ GRUB
1. Lưu mọi công việc, cắm nguồn **AC**, rồi khởi động lại máy (`sudo reboot`).
2. Tại màn hình **GRUB**, chọn đúng dòng Ubuntu mặc định (kernel `7.0.0-43-generic`), nhấn **`e`**.
3. Tìm dòng bắt đầu bằng `linux ...`, thêm vào cuối dòng (sau một dấu cách):
   ```text
   systemd.unit=multi-user.target
   ```
4. Nhấn **`Ctrl+X`** (hoặc **`F10`**) để boot một lần vào text console (`tty1`), sau đó đăng nhập `thinhbui`.

### Bước 2 — Xác minh GDM không chạy & tạm dừng `cups-browsed` + `Avahi`
```bash
uname -r                                            # phải là 7.0.0-43-generic
systemctl is-active gdm.service || true             # phải là inactive
sudo systemctl stop cups-browsed.service avahi-daemon.socket avahi-daemon.service
# Tùy chọn phòng ngừa timer định kỳ:
sudo systemctl stop sysstat-collect.timer fwupd-refresh.timer

# Kiểm tra sạch hoàn toàn trước khi chạy:
systemctl is-active gdm.service cups-browsed.service avahi-daemon.socket avahi-daemon.service || true
pgrep -af 'avahi-daemon|gnome-shell|gdm3|cups-browsed' || echo "CLEAN"
cat /sys/class/power_supply/AC/online               # phải là 1
```

### Bước 3 — Chạy đúng 1 lệnh điều phối `QUALITY_ONLY` (18 tiến trình ON tuần tự)
```bash
cd "/home/thinhbui/Documents/ChatGPT/Research ANN/task-d"
./scripts/run_g2_v2_design3_quality.sh
```
*(Nếu muốn kiểm tra khô không ghi file nào trước khi chạy thật: `./scripts/run_g2_v2_design3_quality.sh --dry-run`.)*

### Bước 4 — Sau khi lệnh kết thúc, reboot bình thường về Ubuntu Desktop
```bash
sudo reboot
```
*(Vì tham số GRUB chỉ áp dụng một lần và không có dịch vụ nào bị `disable`, máy sẽ tự khởi động lại bình thường vào `graphical.target` với nguyên trạng mặc định.)*

---

## 5. Đầu ra Kỳ vọng, Vị trí Evidence, Quy tắc Dừng & Cách Kiểm tra Kết quả

### 5.1 Vị trí Evidence & Expected Output
- **Test panel (tạo 1 lần sau preflight):** `/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-inputs-design3/v2_test_10000.ids` (`SHA-256 = 457abdc1...44b0d`) + `v2_test_10000.sha256`.
- **Thư mục chiến dịch Quality ON:** `/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-quality-design3/`
  - `artifacts.json`, `start.json`, `complete.json`, `quality.json`, `BUNDLE.sha256`
  - `18` file preflight `b-1_*_preflight.jsonl`
  - `18` thư mục tiến trình (`6` `b-1_<graph>_opt_validation` + `12` `b-1_<graph>_{base,opt}_test`), mỗi thư mục gồm `manifest.json`, `command.sh`, `stdout.log`, `stderr.log`, `host.jsonl`, `p2_eval_summary.json`, `beam_432_p2_ON.jsonl`, `metrics.json`.
- **Log console bên ngoài thư mục output:** `/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-quality-design3.console.log`.
- **Thời lượng ước tính:** 18 tiến trình tuần tự × (~10s preflight + ~30–60s thực thi ON/tiến trình) ≈ **12–22 phút**, nằm gọn trong trần cứng `quota_s = 3600 s`.

### 5.2 Quy tắc Dừng Nghiêm ngặt (Fail-Closed, 0 Auto-Retry)
- **Runtime / Safety / Guard / Timeout / Quota:** bất kỳ lỗi nào (`exit_code != 0`, `Tctl >= 95°C` hoặc timeout hạ nhiệt `>= 85°C`, `AC != 1`, `MemAvailable <= 1 GiB`, `free_disk <= 20 GiB` / `<= 25 GiB` đầu phiên, `swap > 64 MiB`, `KNOWN_CPU_JOBS`, `host > 0.10 (15s)`, `single > 0.25 (10s)`, `> 180 s/process`, `> 3600 s` tổng pha) đều kích hoạt `terminate_group()`, ghi `HOLD.json`, bảo toàn nguyên trạng các tiến trình đã hoàn tất, niêm phong `BUNDLE.sha256`, và thoát mã lỗi. **Tuyệt đối không xóa, không ghi đè, không tự chạy lại vào cùng thư mục để ép PASS.**
- **Quality Gate (`quality.json`):**
  - `parity != true` (lệch bất kỳ Top-10 ID hoặc `squared_l2` nào trên 180.000 truy vấn) hoặc `duplicate_reduction != true` -> **`QUALITY_HOLD`**.
  - **Gate A (`A_pass == false`):** bất kỳ graph nào trong 6 graph có simultaneous one-sided `LCB95 < 0.990` -> **`QUALITY_HOLD`** (`144 OFF` giữ nguyên `NOT_OPEN`, cấm retune beam hoặc mở 71.000 ID còn lại).
  - **Gate A PASS (`A_pass == true`):** ghi nhận `B_pass` (arm equivalence `CI95 ∈ (-0.0005, +0.0005)`), **DỪNG TẠI ĐÂY** để kiểm toán độc lập báo cáo quality trước khi xét biên nhận phê duyệt riêng cho `OFF_A` / `OFF_AB`.

### 5.3 Lệnh Kiểm tra Kết quả Sau Khi Boot Lại Desktop (Read-Only)
```bash
OUT="/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-quality-design3"
(cd "$OUT" && sha256sum -c BUNDLE.sha256 | tail -n 5)
ls -la "$OUT/HOLD.json" 2>/dev/null || echo "NO_HOLD_JSON"
cat "$OUT/complete.json"
cat "$OUT/quality.json"
```
