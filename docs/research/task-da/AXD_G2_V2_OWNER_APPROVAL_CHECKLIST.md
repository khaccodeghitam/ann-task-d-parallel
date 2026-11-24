# A×D G2 v2 · Owner Approval Checklist (`QUALITY_ONLY`, `design-2`)

- **Mục đích:** Hướng dẫn từng bước để **owner** hoàn tất kiểm tra quiet host (**B1**) và tự tạo/ký tệp approval receipt (**B2**) bên ngoài frozen package theo đúng schema `axd_g2_v2.2` ([axd_g2_v2.schema.json](../../../configs/axd_g2_v2.schema.json)) và contract [g2_v2_contract.py](../../../research/task_da/g2_v2_contract.py).
- **Trạng thái hiện tại:** **B3 = `PASS`** · **B1 = `HOLD`** · **B2 = `WAITING_OWNER`** · **B4 = `NOT_EXECUTED`** · **Quality ON = `0/18`** · **G2 OFF = `0/144` (`NOT_OPEN`)**.
- **Cam kết tuân thủ:** Tài liệu này **KHÔNG** ký thay owner, **KHÔNG** tạo tệp approval đã ký, **KHÔNG** sửa [axd_g2_v2_approval.UNAPPROVED.json](../../../configs/axd_g2_v2_approval.UNAPPROVED.json), **KHÔNG** giả mạo timestamp/trạng thái quiet, và **KHÔNG** materialize `v2_test_10000.ids`.

---

## 1. Xác nhận Điều kiện Tiền đề Trước khi Ký

- [x] **B3 (`PASS`):** Môi trường Python bền vững đã sẵn sàng tại `/home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python` (`load_freeze(environment=True) = PASS`, `551` tests / `537 PASS` / `14 skipped` / `0 FAIL`; xem [AXD_G2_V2_PREFLIGHT_RECOVERY_REPORT.md](AXD_G2_V2_PREFLIGHT_RECOVERY_REPORT.md)).
- [x] **Frozen Package (`PASS`):** `24/24` checksums [AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256](AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256), `22/22` components, `6/6` graphs R90 v1.3, `6/6` Stage 5 b432 baselines, Release ELF `7a2685e5...`, `5/5` thư viện native `.so` và `host_contract()` đều khớp 100%.
- [ ] **B1 (`HOLD` — Owner phải tự xác nhận trên minimal TTY trước khi ký `quiet_host_confirmed: true`):** Đưa máy về trạng thái quiet đạt liên tiếp `foreign_busy_s / (wall_s × 2) <= 0.01` (xem Mục 2).

---

## 2. Bước Owner Kiểm tra Quiet Host (Gỡ B1)

1. Chủ động lưu công việc và đóng an toàn: `msedge`, `ChatGPT`/Codex, trình phát media/chat/IDE và phiên `agy` tương tác.
2. Chuyển sang text console tối giản **`Ctrl+Alt+F3`** (hoặc SSH từ máy khác khi màn hình desktop đã khóa/rỗi), đảm bảo cắm nguồn AC (`AC/online == 1`) và `Tctl < 85°C`.
3. Từ thư mục repo `/home/thinhbui/Documents/ChatGPT/Research ANN/task-d`, chạy kiểm tra đọc-chỉ `30 s` bằng đúng guard đóng băng:

```sh
cd "/home/thinhbui/Documents/ChatGPT/Research ANN/task-d"
/home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python - <<'EOF'
import sys, time
from pathlib import Path
sys.path.insert(0, ".")
from research.task_da.g2_v2_guard import guard_module, host_contract

print("HOST_CONTRACT:", host_contract())
mod = guard_module()
first = mod.host_snapshot(Path("."))
g = mod.CoolingGuard(first)
passed_windows = 0
failed_windows = 0
for i in range(1, 31):
    time.sleep(1.0)
    s = mod.host_snapshot(Path("."))
    reasons = g.check(s)
    iv = g.noise.intervals[-1]
    frac = iv.get("foreign_capacity_fraction")
    tctl = [v["value_C"] for v in s["sensors"].values() if v["name"] == "k10temp" and v["label"] == "Tctl"]
    if g.noise.ready:
        if reasons:
            failed_windows += 1
        else:
            passed_windows += 1
    top3 = [(p["comm"], round(p["cpu_seconds"], 3)) for p in iv["competing_processes"][:3]]
    print(f"t+{i:02d}s Tctl={tctl} frac={None if frac is None else round(frac, 5)} reasons={reasons} top3={top3}")
print(f"SUMMARY: passed_windows={passed_windows} failed_windows={failed_windows} B1_QUIET_PASS={failed_windows == 0 and passed_windows >= 20}")
EOF
```

- **Nếu `B1_QUIET_PASS=True`** (và không có xung `reasons` nào): Owner có cơ sở thực tế để ký `quiet_host_confirmed: true` tại Mục 3.
- **Nếu `B1_QUIET_PASS=False`** ngay cả trên minimal TTY sạch (không GUI/browser/agent): **DỪNG và KHÔNG ký `quiet_host_confirmed: true`**; ghi nhận `B1_HOLD_NOISE_THRESHOLD_INFEASIBLE` cùng log 30 s để xét controlled revision `design-3` riêng theo [AXD_G2_V2_PREFLIGHT_RECOVERY_REPORT.md](AXD_G2_V2_PREFLIGHT_RECOVERY_REPORT.md) §2.3.

---

## 3. Đặc tả Chính xác các Trường của Approval Receipt (`axd_g2_v2.2`)

Đối chiếu `configs/axd_g2_v2.schema.json` (`#/$defs/approval`, `additionalProperties: false`) và `g2_v2_contract.authorize()`:

| Trường JSON | Kiểu / Quy tắc khóa | Giá trị chính xác cho `QUALITY_ONLY` |
|---|---|---|
| `schema` | `const` | `"axd_g2_v2.2"` |
| `protocol` | `const` | `"AXD-G2-V2-3A-20261123"` |
| `revision` | `const` | `"design-2"` |
| `owner` | `string`, `minLength: 1` | **Owner tự điền** tên/định danh owner |
| `approved_at` | `string`, ISO-8601 **bắt buộc có timezone** (`tzinfo is not None`) | **Owner tự điền** thời điểm ký thực tế, ví dụ `"2026-11-24T00:45:00+07:00"` |
| `freeze_sha256` | `^[0-9a-f]{64}$` khớp `sha256(configs/axd_g2_v2_freeze.json)` | `"91186d57e5992e1df70f86a55ba928ad4d6613bb0b67ccbee0f485cc380d1749"` |
| `artifacts_sha256` | `^[0-9a-f]{64}$` khớp `sha256(configs/axd_g2_v2_artifacts.proposed.json)` | `"da448149a01c3027cd928c23c10eb2725555f4ced4328a105d185bb4d4aa75e3"` |
| `output_directory` | Đường dẫn tuyệt đối đã `resolve()`, khớp `quality_plan_final.json` | `"/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-quality-design2"` |
| `scope` | `enum` cho pha quality | `"QUALITY_ONLY"` *(tuyệt đối không dùng `"OFF_A"` hay `"OFF_AB"`)* |
| `quota_s` | Khóa cứng theo phase `quality` | `3600` *(đúng 1 giờ; pha OFF là 10800 và bị từ chối ở đây)* |
| `quiet_host_confirmed` | `const: true` | `true` *(chỉ điền `true` sau khi bước Mục 2 thực sự đạt `B1_QUIET_PASS=True`)* |

*(Lưu ý: Không thêm khóa phụ nào khác vì schema đặt `additionalProperties: false`; trường tùy chọn `quality_sha256` chỉ dùng cho pha `off` sau này, bỏ trống/không khai báo trong `QUALITY_ONLY`.)*

### Mẫu JSON để Owner Tự Lưu Ngoài Frozen Package
Lưu ra một đường dẫn riêng ngoài Git repo (ví dụ `/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-approvals/quality_only_approval.json`); **tuyệt đối không chỉnh sửa `configs/axd_g2_v2_approval.UNAPPROVED.json`**:

```json
{
  "schema": "axd_g2_v2.2",
  "protocol": "AXD-G2-V2-3A-20261123",
  "revision": "design-2",
  "owner": "<OWNER_TU_DIEN>",
  "approved_at": "<YYYY-MM-DDTHH:MM:SS+07:00>",
  "freeze_sha256": "91186d57e5992e1df70f86a55ba928ad4d6613bb0b67ccbee0f485cc380d1749",
  "artifacts_sha256": "da448149a01c3027cd928c23c10eb2725555f4ced4328a105d185bb4d4aa75e3",
  "output_directory": "/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-quality-design2",
  "scope": "QUALITY_ONLY",
  "quota_s": 3600,
  "quiet_host_confirmed": true
}
```

---

## 4. Cách Xác minh Approval Receipt (Read-Only Dry-Run, 0 ANN Execution)

Sau khi owner tự tạo và lưu tệp approval receipt tại `$APPROVAL`, xác minh hợp lệ bằng chính `g2_v2_contract.authorize()` và `load_freeze(environment=True)`:

```sh
cd "/home/thinhbui/Documents/ChatGPT/Research ANN/task-d"
APPROVAL="/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-approvals/quality_only_approval.json"
/home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python - "$APPROVAL" <<'EOF'
import json, sys
from pathlib import Path
sys.path.insert(0, ".")
from research.task_da.g2_v2_contract import FREEZE, authorize, load_freeze, sha

approval_path = Path(sys.argv[1])
load_freeze(environment=True)
approval = json.loads(approval_path.read_text())
scope = authorize(
    approval,
    sha(FREEZE),
    sha("configs/axd_g2_v2_artifacts.proposed.json"),
    "quality",
    "/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-quality-design2",
)
print("APPROVAL_CONTRACT_CHECK=PASS scope=", scope, "approval_sha256=", sha(approval_path))
EOF
```

---

## 5. Bước Tiếp theo Chỉ Khi B1, B2 và B3 Đều PASS (Không Tự Chạy Lúc Này)

1. **B4 — Materialize một lần `v2_test_10000.ids`:** Tạo đúng tệp `/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-inputs-design2/v2_test_10000.ids` theo pseudocode khóa trong [AXD_G2_V2_QUERY_SPLIT_AUDIT.md](AXD_G2_V2_QUERY_SPLIT_AUDIT.md) §4, xác minh count = `10,000`, unique = `10,000`, overlap = `0` với `val_10k` / `pilot3k` / `disjoint3k` / `narrow3k`, và SHA-256 = **`457abdc13abc95d8d0f48ff32919a6013f5ed4bca469f9075312ae80dfe44b0d`**.
2. **Stage 1 (`QUALITY_ONLY` — đúng 18 tiến trình ON trong minimal TTY):**
   ```sh
   cd "/home/thinhbui/Documents/ChatGPT/Research ANN/task-d"
   /home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python -m research.task_da.g2_v2_runner execute \
     --phase quality \
     --artifacts configs/axd_g2_v2_artifacts.proposed.json \
     --approval "$APPROVAL" \
     --output "/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-quality-design2"
   ```
3. **Dừng sau Quality Gate:** Phân tích kết quả 18 tiến trình ON từ raw, xuất kết luận `QUALITY_GATE_PASS` hoặc `QUALITY_HOLD`. **Pha `144 OFF` vẫn giữ `NOT_OPEN` và đòi hỏi một tệp approval riêng biệt (`scope: "OFF_A"` hoặc `"OFF_AB"`, `quota_s: 10800`, kèm `quality_sha256`) do owner ký sau khi đọc báo cáo quality thực tế.**
