#!/usr/bin/env bash
# Orchestrator wrapper (OUTSIDE frozen design-3 package) for owner-approved
# G2 v2 design-3 Performance OFF execution (scope=OFF_AB, 144 sequential OFF processes,
# 12 balanced blocks x 6 R90 v1.3 graphs x 2 policies, beam=432, p=2, S=16).
#
# Usage:
#   ./scripts/run_g2_v2_design3_off.sh            # full preflight + 144 OFF + BUNDLE.sha256 seal
#   ./scripts/run_g2_v2_design3_off.sh --dry-run  # read-only preflight only (0 disk writes, 0 ANN)
#
# Safety guarantees:
# - NEVER calls sudo, NEVER stops gdm.service, NEVER edits kernel/GRUB/governor/frozen files.
# - NEVER bypasses any frozen runner, guard, preflight, schema, or checksum check.
# - NEVER overwrites/resumes an existing output directory, NEVER auto-retries on HOLD/failure.
# - NEVER runs offline bootstrap analysis concurrently with OFF collection.
set -euo pipefail

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
  shift
fi
if [[ $# -gt 0 ]]; then
  echo "Usage: $0 [--dry-run]" >&2
  exit 2
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE_ROOT="/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence"
VENV_PY="${G2_V2_VENV_PY:-/home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python}"

ARTIFACTS_JSON="$REPO_ROOT/configs/axd_g2_v2_design3_artifacts.proposed.json"
APPROVAL_JSON="$EVIDENCE_ROOT/axd-g2-v2-approvals/design3_off_approval.json"
QUAL_JSON="$EVIDENCE_ROOT/axd-g2-v2-design3-qualification-20261124T094602Z/qualification_result.json"
QUALITY_JSON="$EVIDENCE_ROOT/axd-g2-v2-quality-design3/quality.json"
OUT_DIR="$EVIDENCE_ROOT/axd-g2-v2-off-design3"
CONSOLE_LOG="$EVIDENCE_ROOT/axd-g2-v2-off-design3.console.log"
ANALYSIS_OUT="$EVIDENCE_ROOT/axd-g2-v2-off-design3-analysis.json"

EXPECTED_APPROVAL_SHA256="aa9a98d4fbda63b57fb6257c781fdd67c98c904c3390a2b9d16d1d83fb9b33e3"
EXPECTED_QUALITY_SHA256="360e1d29fc3c8f3c03e381ce57dea2e826459f7534577d6d24ec6ac81a54c59f"
EXPECTED_KERNEL="7.0.0-43-generic"

if [[ ! -x "$VENV_PY" ]]; then
  echo "ERROR: Pinned Python venv not found at $VENV_PY" >&2
  exit 1
fi

cd "$REPO_ROOT"

echo "=== [Stage A] Read-Only Preflight: Freeze, Approval OFF_AB, Qualification, Quality Gate, Kernel & Quiet TTY ==="
ACTUAL_KERNEL="$(uname -r)"
if [[ "$ACTUAL_KERNEL" != "$EXPECTED_KERNEL" ]]; then
  echo "ERROR: Kernel mismatch: got '$ACTUAL_KERNEL', expected '$EXPECTED_KERNEL'." >&2
  echo "       Reboot and select '$EXPECTED_KERNEL' in GRUB with systemd.unit=multi-user.target." >&2
  exit 2
fi
echo "KERNEL_CHECK=OK ($ACTUAL_KERNEL)"

# Verify frozen design-3 package integrity (26/26)
sha256sum -c "$REPO_ROOT/docs/research/task-da/AXD_G2_V2_DESIGN3_FREEZE.sha256" >/dev/null
echo "DESIGN3_FREEZE_26_26=OK"

# Verify AC power online
AC_ONLINE="$(cat /sys/class/power_supply/AC/online 2>/dev/null || echo missing)"
if [[ "$AC_ONLINE" != "1" ]]; then
  echo "ERROR: AC power is not online (/sys/class/power_supply/AC/online='$AC_ONLINE')." >&2
  exit 2
fi
echo "AC_POWER=OK (online=1)"

# Quiet-host check (READ-ONLY — NEVER calls sudo or systemctl stop; NEVER stop gdm.service from TTY!)
QUIET_FAIL=0
REQUIRED_INACTIVE_SERVICES=(
  gdm.service
  cups-browsed.service
  avahi-daemon.socket
  avahi-daemon.service
)
for unit in "${REQUIRED_INACTIVE_SERVICES[@]}"; do
  st="$(systemctl is-active "$unit" 2>/dev/null || true)"
  if [[ "$st" == "active" || "$st" == "activating" || "$st" == "reloading" ]]; then
    echo "QUIET_HOST_BLOCKER: service/socket '$unit' is '$st' (must be inactive)" >&2
    QUIET_FAIL=1
  else
    echo "UNIT_INACTIVE=OK ($unit: ${st:-inactive})"
  fi
done

# Periodic timers that can fire during a 2-3 hour OFF window (incl. midnight backups/logrotate/anacron/apt)
REQUIRED_INACTIVE_TIMERS=(
  sysstat-collect.timer
  sysstat-summary.timer
  fwupd-refresh.timer
  anacron.timer
  dpkg-db-backup.timer
  logrotate.timer
  motd-news.timer
  apt-daily.timer
  apt-daily-upgrade.timer
)
ACTIVE_TIMERS=()
for timer in "${REQUIRED_INACTIVE_TIMERS[@]}"; do
  tst="$(systemctl is-active "$timer" 2>/dev/null || true)"
  if [[ "$tst" == "active" || "$tst" == "activating" || "$tst" == "reloading" ]]; then
    echo "QUIET_HOST_BLOCKER: periodic timer '$timer' is '$tst' (pause temporarily before 2-3h OFF run)" >&2
    ACTIVE_TIMERS+=("$timer")
    QUIET_FAIL=1
  else
    echo "TIMER_INACTIVE=OK ($timer: ${tst:-inactive})"
  fi
done

if pgrep -af 'avahi-daemon|gnome-shell|gdm3|cups-browsed' >/dev/null 2>&1; then
  echo "QUIET_HOST_BLOCKER: competing desktop/mDNS process still running:" >&2
  pgrep -af 'avahi-daemon|gnome-shell|gdm3|cups-browsed' >&2 || true
  QUIET_FAIL=1
else
  echo "COMPETING_DAEMONS_ABSENT=OK (no avahi-daemon/gnome-shell/gdm3/cups-browsed)"
fi

# Full Python contract, OFF_AB approval, qualification PASS, Quality Gate A/B PASS, provenance & 144-plan check
env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT "$VENV_PY" - \
  "$ARTIFACTS_JSON" "$APPROVAL_JSON" "$QUAL_JSON" "$QUALITY_JSON" "$OUT_DIR" \
  "$EXPECTED_APPROVAL_SHA256" "$EXPECTED_QUALITY_SHA256" "$DRY_RUN" "$QUIET_FAIL" <<'PY'
import json
import os
import shutil
import sys
from pathlib import Path

from research.task_da.g2_v2_design3_contract import (
    FREEZE, authorize, load_freeze, require, require_default_loader, sha, validate_schema,
)
from research.task_da.g2_v2_design3_guard import host_contract
from research.task_da.g2_v2_design3_runner import (
    plan, quality_context, verify_artifacts, verify_qualification,
)

artifacts_path = Path(sys.argv[1])
approval_path = Path(sys.argv[2])
qual_path = Path(sys.argv[3])
quality_path = Path(sys.argv[4])
out_dir = Path(sys.argv[5])
expected_approval_sha = sys.argv[6]
expected_quality_sha = sys.argv[7]
dry_run = sys.argv[8] == "1"
quiet_fail = sys.argv[9] == "1"

require_default_loader(os.environ)
freeze = load_freeze(environment=True)
hc = host_contract()
qual = verify_qualification(qual_path)
quality_context(quality_path)

actual_quality_sha = sha(quality_path)
require(actual_quality_sha == expected_quality_sha,
        f"quality.json SHA mismatch: got {actual_quality_sha}, expected {expected_quality_sha}")
quality = json.loads(quality_path.read_text())
require(quality.get("A_pass") is True and quality.get("B_pass") is True
        and quality.get("parity") is True and quality.get("duplicate_reduction") is True,
        "Quality Gate A/B/parity/duplicate_reduction not all PASS")

actual_approval_sha = sha(approval_path)
require(actual_approval_sha == expected_approval_sha,
        f"approval SHA mismatch: got {actual_approval_sha}, expected {expected_approval_sha}")
approval = json.loads(approval_path.read_text())
scope = authorize(
    approval,
    sha(FREEZE),
    sha(artifacts_path),
    "off",
    out_dir,
    qualification_digest=sha(qual_path),
    quality_digest=actual_quality_sha,
)
require(scope == "OFF_AB" and approval["quota_s"] == 10800 and approval["quiet_host_confirmed"] is True,
        "unexpected OFF_AB approval scope/quota/confirmation")
require(not out_dir.exists(), f"OFF output directory already exists (never overwrite/resume): {out_dir}")

artifacts = json.loads(artifacts_path.read_text())
validate_schema(artifacts, "artifacts")
verify_artifacts(freeze, artifacts)

frozen_off_plan = json.loads(
    Path(".local/artifacts/axd-g2-v2-design3-freeze-20261124/off_plan_design3_final.json").read_text()
)["commands"]
live_plan = plan(artifacts, "off", out_dir.resolve())
require(live_plan == frozen_off_plan and len(live_plan) == 144,
        "live 144-OFF plan mismatch against frozen off_plan_design3_final.json")

free_gib = shutil.disk_usage(out_dir.parent).free / (2**30)
require(free_gib > 25.0, f"insufficient free disk ({free_gib:.2f} GiB <= 25 GiB floor)")

print(f"CONTRACT_AND_PROVENANCE=PASS scope={scope} quota_s={approval['quota_s']} approval_sha={actual_approval_sha[:12]}... quality_sha={actual_quality_sha[:12]}... qual={qual['verdict']}")
print(f"HOST_CONTRACT=PASS cpu={hc['cpu_model']} kernel={hc['kernel']} cpus={hc['cpus']} free_disk={free_gib:.2f}GiB")
print("OFF_144_PLAN_VERIFIED=EXACT_MATCH (12 balanced blocks x 6 R90 v1.3 graphs x 2 policies, beam=432, p=2, S=16)")

if dry_run:
    print(f"DRY_RUN_COMPLETE: off_output_exists={out_dir.exists()} quiet_host_ok={not quiet_fail}")
    if quiet_fail:
        print("NOTE: Quiet-host blockers present (expected on GUI desktop); real execution is blocked until multi-user.target + Avahi/cups-browsed/timers paused.", file=sys.stderr)
        sys.exit(3)
    sys.exit(0)

if quiet_fail:
    print(
        "ABORT: Quiet-host blockers detected. Boot GRUB once with systemd.unit=multi-user.target "
        "(NEVER run systemctl stop gdm.service from TTY!), then temporarily stop cups-browsed, "
        "avahi-daemon.{socket,service}, and periodic timers before running this script.",
        file=sys.stderr,
    )
    sys.exit(2)
PY

if [[ "$DRY_RUN" -eq 1 ]]; then
  exit 0
fi

if [[ -e "$CONSOLE_LOG" ]]; then
  echo "ERROR: Console log already exists ($CONSOLE_LOG); refusing to overwrite prior evidence." >&2
  exit 2
fi

{
  echo "=== [Stage B] Executing 144 Sequential OFF_AB Processes via Frozen design-3 Runner ==="
  echo "Started UTC      : $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "Output directory : $OUT_DIR"
  echo "Console log      : $CONSOLE_LOG"
  echo "Quota / Timeout  : 10800s (3h) phase quota / 180s per process / >=15s preflight / 0 auto-retries"
} | tee "$CONSOLE_LOG"

set +e
env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT \
  "$VENV_PY" -m research.task_da.g2_v2_design3_runner execute \
  --phase off \
  --artifacts "$ARTIFACTS_JSON" \
  --approval "$APPROVAL_JSON" \
  --qualification "$QUAL_JSON" \
  --quality "$QUALITY_JSON" \
  --output "$OUT_DIR" 2>&1 | tee -a "$CONSOLE_LOG"
RUNNER_RC=${PIPESTATUS[0]}
set -e

{
  echo "Finished UTC     : $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "=== [Stage C] Post-Run Evidence Seal & Completion Audit (runner_rc=$RUNNER_RC) ==="
} | tee -a "$CONSOLE_LOG"

if [[ -d "$OUT_DIR" ]]; then
  (
    cd "$OUT_DIR"
    find . -type f ! -name 'BUNDLE.sha256' | LC_ALL=C sort | sed 's|^\./||' | xargs -d '\n' sha256sum > BUNDLE.sha256
    sha256sum -c BUNDLE.sha256 >/dev/null
  )
  BUNDLE_COUNT="$(wc -l < "$OUT_DIR/BUNDLE.sha256")"
  echo "BUNDLE_SHA256_SEALED=OK ($OUT_DIR/BUNDLE.sha256, entries=$BUNDLE_COUNT)" | tee -a "$CONSOLE_LOG"
fi

env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT "$VENV_PY" - "$OUT_DIR" "$RUNNER_RC" "$ANALYSIS_OUT" <<'PY' | tee -a "$CONSOLE_LOG"
import json
import sys
from pathlib import Path
from research.task_da.g2_v2_design3_contract import schedule, sha, validate_schema
from research.task_da.g2_v2_design3_runner import name as task_name

out_dir = Path(sys.argv[1])
rc = int(sys.argv[2])
analysis_out = sys.argv[3]
hold_path = out_dir / "HOLD.json"
comp_path = out_dir / "complete.json"

if hold_path.exists() or rc != 0 or not comp_path.exists():
    print("VERDICT=OFF_EXECUTION_HOLD (all raw evidence preserved & sealed; NEVER overwrite, resume, or auto-retry)")
    if hold_path.exists():
        print(hold_path.read_text())
    sys.exit(rc if rc != 0 else 2)

comp = json.loads(comp_path.read_text())
validate_schema(comp, "complete")
wanted = {task_name(item) for item in schedule()}
assert set(comp["receipts"]) == wanted and set(comp["preflight_sha256"]) == wanted, "incomplete 144-OFF receipts"
summary = {
    "status": "OFF_COLLECTION_COMPLETE_144_OF_144",
    "phase": comp["phase"],
    "elapsed_s": round(comp["elapsed_s"], 2),
    "receipts_count": len(comp["receipts"]),
    "preflights_count": len(comp["preflight_sha256"]),
    "complete_json_sha256": sha(comp_path),
    "bundle_sha256": sha(out_dir / "BUNDLE.sha256"),
    "next_steps": [
        "1. Reboot normally (sudo reboot) to restore standard Ubuntu Desktop and all paused timers/services.",
        f"2. Run offline frozen analyzer separately: /home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python -m research.task_da.g2_v2_design3_analyzer --campaign \"{out_dir}\" --output \"{analysis_out}\"",
    ],
}
print(json.dumps(summary, indent=2))
PY
