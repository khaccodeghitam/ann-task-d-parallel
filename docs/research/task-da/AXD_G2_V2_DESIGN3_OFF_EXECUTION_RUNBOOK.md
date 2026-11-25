# A×D G2 v2 (`design-3`) · Performance `OFF_AB` Pre-Execution Audit & TTY Runbook

- **Official Preparation Verdict:** **`READY_FOR_OFF_EXECUTION`** *(toàn bộ preflight read-only, approval `OFF_AB`, Quality Gate A/B PASS, Qualification PASS và kế hoạch 144 OFF đã **PASS 100%**; chưa chạy OFF trong phiên này).*
- **Signed Owner Approval Receipt (`OFF_AB`):** `../../../../artifact-evidence/axd-g2-v2-approvals/design3_off_approval.json`
  - **SHA-256:** **`aa9a98d4fbda63b57fb6257c781fdd67c98c904c3390a2b9d16d1d83fb9b33e3`**
  - **Owner / Timestamp / Scope / Quota:** `owner = "thinhbui"` · `approved_at = "2026-11-24T23:16:21+07:00"` · `scope = "OFF_AB"` · `quota_s = 10800` (`3 giờ`) · `quiet_host_confirmed = true`
- **Pinned Upstream Receipts (tái sử dụng hợp lệ theo contract `design-3`, KHÔNG cần `design-4` hay chạy lại qualification/quality):**
  - **Qualification PASS:** `../../../../artifact-evidence/axd-g2-v2-design3-qualification-20261124T094602Z/qualification_result.json` (`f64b9f9a...c49cb`, `853/853` 10s, `848/848` 15s, `0` hard fails)
  - **Quality Gate A/B PASS:** `../../../../artifact-evidence/axd-g2-v2-quality-design3/quality.json` (`360e1d29...a54c59f`, `18/18` ON, `A_pass=true`, `B_pass=true`, `parity=true`, `duplicate_reduction=true`, `166/166` `BUNDLE.sha256` OK)
- **Orchestrator Script (ngoài frozen package):** [run_g2_v2_design3_off.sh](../../../scripts/run_g2_v2_design3_off.sh)

---

## 1. Xác minh Pre-Execution: Approval `OFF_AB`, Freeze, Provenance & Kế hoạch 144 OFF

| Hạng mục kiểm toán | Kết quả xác minh trực tiếp | Trạng thái |
|---|---|---|
| Approval `OFF_AB` & 8 trường pinned | `SHA-256 = aa9a98d4...b9b33e3`; 8 trường pinned khớp 100% `DRAFT_UNSIGNED` & freeze; `authorize(..., "off", ...)` trả `scope = "OFF_AB"`, `quota_s = 10800`, `quiet_host_confirmed = true` | **`PASS`** |
| Qualification PASS & Quality Gate A/B PASS | `verify_qualification()` PASS (`20261124T094602Z`, `2/2 OK`; `HOLD 20261124T082344Z` giữ nguyên `2/2 OK`); `quality_context()` PASS (`360e1d29...`, `A_pass=true`, `B_pass=true`, `166/166 OK`) | **`PASS`** |
| Toàn vẹn Frozen Package `design-3` & `design-2` | [AXD_G2_V2_DESIGN3_FREEZE.sha256](AXD_G2_V2_DESIGN3_FREEZE.sha256) **`26/26 OK`**; freeze bundle **`4/4 OK`**; `design-2` **`24/24 OK`**; `git diff` trống | **`PASS`** |
| Provenance đầu vào, 6 đồ thị & test panel | `load_freeze(environment=True)` PASS (`Python 3.12.3`, `e50d468e...`, `7/7` wheels); `host_contract()` PASS (`Ryzen 5 PRO 4650U`, kernel `7.0.0-43-generic`, `cpus=[0,2]`); `verify_artifacts()` PASS (gồm `5/5` `.so`, ELF `7a2685e5...`, `6/6` R90 v1.3 graphs, `6/6` Stage 5 baselines, và `v2_test_10000.ids` đã materialize `457abdc1...`) | **`PASS`** |
| Kế hoạch 144 OFF (`off_plan_design3_final.json`) | Khớp từng byte (`SHA-256 = 1bf54315...780d95e`): **144 tiến trình `--mode OFF`**, `12` balanced blocks × `6` graph (`3` Stock + `3` Fast R90 v1.3) × `2` policy (`base/opt`), `beam=432`, `p=2`, `S=16`, `jobs=1`, `warmup=100`, `N=10,000`, mỗi graph `2×`/vị trí (`1 AB + 1 BA`, tổng `6 AB / 6 BA`), cặp luôn liền kề; thư mục đích `axd-g2-v2-off-design3` **chưa tồn tại** | **`EXACT MATCH`** |

---

## 2. Xác nhận Môi trường Ubuntu & Danh mục Dịch vụ / Timer Cần Tạm Dừng Cho Pha OFF (2–3 giờ)

Khác với pha `QUALITY_ONLY`, pha **`OFF`** kích hoạt **đủ 3 tầng noise guard nghiêm ngặt** (`worker-cores [0..3] <= 0.01 (10s)`, `CCX0 [0..5] <= 0.02 (10s)`, `host [0..11] <= 0.025 (15s)`, `single <= 0.10 (10s)`, `preflight >= 15s`) trong suốt **`~2.0–2.3 giờ`**. Kiểm tra trực tiếp `systemctl list-timers --all` cho thấy ngoài các tiến trình đã tắt khi PASS qualification & Quality ON, có các timer định kỳ (đặc biệt qua mốc `00:00` đêm) có thể tự chạy giữa chiến dịch OFF:

| Nhóm đơn vị systemd | Tên unit chính xác | Lý do tạm dừng trong phiên OFF 2–3 giờ | Cách xử lý an toàn & hoàn nguyên |
|---|---|---|---|
| **Display Manager** | `gdm.service` | Từng giữ `gnome-shell` sống qua `gdm-autologin`. **TUYỆT ĐỐI KHÔNG chạy `systemctl stop gdm.service` từ TTY** (từng gây treo máy). | **Boot GRUB 1 lần `systemd.unit=multi-user.target`** (kernel `7.0.0-43-generic`) → `gdm.service` tự `inactive`; reboot tự khôi phục. |
| **mDNS / In ấn** *(đã kiểm chứng ở Qual PASS & Quality ON)* | `cups-browsed.service`, `avahi-daemon.socket`, `avahi-daemon.service` | `avahi-daemon` là nguồn nhiễu #1 gây 92/93 FAIL trước đây; `cups-browsed` & `.socket` có thể kích hoạt lại `avahi-daemon`. | `sudo systemctl stop ...` tạm thời (KHÔNG `disable`); reboot tự khôi phục. |
| **Timer định kỳ trong cửa sổ 2–3 giờ** *(từ `systemctl list-timers --all`)* | `sysstat-collect.timer`, `sysstat-summary.timer`, `fwupd-refresh.timer`, `anacron.timer`, `dpkg-db-backup.timer`, `logrotate.timer`, `motd-news.timer`, `apt-daily.timer`, `apt-daily-upgrade.timer` | Tránh `sysstat` (mỗi 10 phút), `anacron` (mỗi giờ / cron ngày), `dpkg-db-backup` + `logrotate` (`00:00`), `sysstat-summary` (`00:07`), `fwupd-refresh`, `motd-news`, `apt-daily*` nổ giữa 144 lượt OFF gây `HOLD.json`. | `sudo systemctl stop ...` tạm thời (KHÔNG `disable`); reboot tự khôi phục. |

*(Không thay đổi `/etc/default/grub`, kernel, BIOS, IRQ, CPU governor hay bất kỳ cấu hình hệ thống vĩnh viễn nào.)*

---

## 3. Hướng dẫn Thực thi Ngắn gọn Trên TTY (Cho Owner Tự Chạy)

### Bước 1 — Boot GRUB một lần vào `multi-user.target` (kernel `7.0.0-43-generic`)
1. Cắm nguồn **AC**, lưu công việc, `sudo reboot`.
2. Tại GRUB chọn dòng Ubuntu mặc định (`7.0.0-43-generic`), nhấn **`e`**, thêm **`systemd.unit=multi-user.target`** vào cuối dòng `linux`, nhấn **`Ctrl+X`** (hoặc `F10`), đăng nhập `thinhbui`.

### Bước 2 — Xác minh GDM `inactive` & tạm dừng mDNS + timer định kỳ
```bash
uname -r                                            # phải là 7.0.0-43-generic
systemctl is-active gdm.service || true             # phải là inactive
cat /sys/class/power_supply/AC/online               # phải là 1

sudo systemctl stop \
  cups-browsed.service avahi-daemon.socket avahi-daemon.service \
  sysstat-collect.timer sysstat-summary.timer fwupd-refresh.timer \
  anacron.timer dpkg-db-backup.timer logrotate.timer \
  motd-news.timer apt-daily.timer apt-daily-upgrade.timer

pgrep -af 'avahi-daemon|gnome-shell|gdm3|cups-browsed' || echo "CLEAN"
```

### Bước 3 — Chạy 1 lệnh duy nhất để thu thập 144 lượt `OFF_AB` (ước tính ~2.0–2.3 giờ, trần 3 giờ)
```bash
cd "/home/thinhbui/Documents/ChatGPT/Research ANN/task-d"
./scripts/run_g2_v2_design3_off.sh
```
*(Muốn kiểm tra khô trước khi chạy thật: `./scripts/run_g2_v2_design3_off.sh --dry-run` — không ghi đĩa, không chạy ANN.)*

### Bước 4 — Sau khi kết thúc (dù đủ 144/144 hay gặp `HOLD.json`), reboot bình thường về Ubuntu Desktop
```bash
sudo reboot
```

---

## 4. Vị trí Evidence, Kiểm tra Kết quả & Quy trình Phân tích Offline `OFF_AB`

### 4.1 Đường dẫn Output & Kiểm tra Toàn vẹn Sau Khi Về Desktop (Read-Only)
- **Thư mục chiến dịch 144 OFF:** `/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-off-design3/`
  - `artifacts.json`, `start.json`, `complete.json`, `BUNDLE.sha256` (hoặc `HOLD.json` nếu dừng sớm)
  - `144` tệp `b<0..11>_<graph>_<base|opt>_test_preflight.jsonl`
  - `144` thư mục tiến trình (`manifest.json`, `command.sh`, `stdout.log`, `stderr.log`, `host.jsonl`, `p2_eval_summary.json`, `beam_432_p2_OFF.jsonl`, `metrics.json`)
- **Console log (bên ngoài thư mục output):** `/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-off-design3.console.log`
- **Kiểm tra nhanh sau khi reboot:**
  ```bash
  OUT="/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-off-design3"
  ls -la "$OUT/HOLD.json" 2>/dev/null || echo "NO_HOLD_JSON"
  (cd "$OUT" && wc -l BUNDLE.sha256 && sha256sum -c BUNDLE.sha256 >/dev/null && echo "OFF_BUNDLE_ALL=OK")
  cat "$OUT/complete.json" | tail -n 10
  ```

### 4.2 Phân tích Offline `OFF_AB` Qua Frozen Analyzer (Chạy Riêng Sau Khi Đủ 144/144 & `NO_HOLD_JSON`)
```bash
cd "/home/thinhbui/Documents/ChatGPT/Research ANN/task-d"
env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT \
  /home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python -m research.task_da.g2_v2_design3_analyzer \
  --campaign "/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-off-design3" \
  --output "/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-off-design3-analysis.json"
```
Frozen [g2_v2_design3_analyzer.py](../../../research/task_da/g2_v2_design3_analyzer.py) sẽ tự động gọi `load_campaign()` (replay đủ 144 `host.jsonl` qua guard pha `off`, re-verify toàn bộ parity ON/OFF, preflight, RAM hard gate, monotonic order, `quality_context`, `verify_qualification`, `authorize`) và xuất đầy đủ theo phạm vi `OFF_AB` (`B_authorized = True`, quota phân tích riêng `10800 s`, schema `axd_g2_v2.3` `#/$defs/analysis`):
1. **Hiệu năng & tốc độ:** `mean_us`, `p50_us`, `p95_us`, `p99_us`, `qps_wall`, `primary_reduction` (`1 - exp(-mean(x_b))`), `speedup` (`exp(mean(x_b))`), cùng `arithmetic_base_us`, `arithmetic_opt_us`, `arithmetic_reduction`.
2. **Tài nguyên:** `cpu_percent`, `cpu_capacity_percent`, `rss_kib` (`p2_eval_summary.vm_hwm_kib`), `ram_hard_pass` (`10(C-B) <= max(655360, B)` cho từng cặp trong 72 cặp), `ram_max_by_graph`, `ram_mean_upper` & `tail_log_upper` (`18` simultaneous upper bounds $t_{1-0.05/18,\,11}$).
3. **Paired Effect, CI & Noise Balance:** `primary_log_ci95` (`df=11`), `drift_log_ci95` (`6` cặp block, `df=5`), `query_bootstrap` & `joint_bootstrap` (`10,000` replicates, `query_block=100`, `seed=20261123`), `graph_log_ci95` (6 graph), `leave_one_out_log_effects` (6 LOO), và `noise_balance` (`paired Δforeign = opt - base` trên `all`/`workers`/`ccx0`, CI95 `df=11`, Spearman với `x_gb`, `imbalance_warning` — chỉ chẩn đoán).
4. **Tác động riêng B1+A1 trên Stock vs Fast:** `arm_log_ci95["stock"]`, `arm_log_ci95["fast"]`, cùng `metrics_by_graph_policy` cho toàn bộ `6 graph × 2 policy`.
5. **Tương tác BUILD–SEARCH & `ΔT(Q)` (`OFF_AB`):** `build_search.contrasts` gồm 4 đối chiếu (`fast_base_vs_stock_base`, `fast_opt_vs_stock_opt`, `fast_opt_vs_stock_base`, `fast_opt_vs_fast_base`), `log_latency_ratio_ci95`, `mean_search_delta_us`, `positive_break_even_queries`, và `ΔT(Q)` (`saved_s`, `ci95_s`, `joint_ci95_s`) tại **`Q = 1`, `100,000`, `1,000,000`** *(có điều kiện trên 6 BUILD receipts lịch sử; `independent-root population CI = NOT_ESTIMABLE`)*.
6. **Quyết định khóa trước:**
   - **Primary A (`verdict`):** `GO_A_FIXED_COHORT` *(khi `min(primary_lo, drift_lo, joint_lo) > θ + 1e-12`, `stability_pass=true`, `safety_pass=true`, `duplicate_reduction=true`)* · `PIVOT_TO_TASK_A` *(khi cận trên primary & fast arm `< θ - 1e-12`, hoặc lower simultaneous bound tail/RAM vượt ngân sách)* · ngược lại `HOLD`.
   - **Secondary B (`build_search.status`):** `GO_B_SYSTEM_FIXED_COHORT` *(khi `fast_opt_vs_stock_base` tại `Q=100,000` có `min(ci95_lo, joint_ci95_lo) > 1e-12` và `saved_s > 0` trước cả `fast_base` và `stock_opt`, cùng `safety_pass=true`)* · ngược lại `HOLD_B_SYSTEM_UNCERTAINTY` / `HOLD_B_RESOURCES`.

### 4.3 Quy tắc Dừng & Bảo toàn Evidence (0 Auto-Retry, 0 Partial Resume)
- Mọi lỗi safety/thermal/AC/RAM/disk/swap/contention/timeout `180 s`/quota `10800 s`/ON-OFF parity/RAM hard gate trong lúc chạy đều kích hoạt dừng tức thời, ghi `HOLD.json`, niêm phong `BUNDLE.sha256` và kết thúc với mã lỗi. **Tuyệt đối không xóa, không ghi đè, không chạy bù một phần và không kiểm tra hiệu năng giữa chừng để chỉnh thiết kế.**
