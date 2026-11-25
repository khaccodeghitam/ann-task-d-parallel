#!/usr/bin/env bash
# Orchestrator wrapper (OUTSIDE frozen design-3.1 package) for owner-approved
# G2 v2 design-3.1 Performance OFF execution — RUN 2 (scope=OFF_AB, 144 sequential OFF
# processes, 12 balanced blocks x 6 R90 v1.3 graphs x 2 policies, beam=432, p=2, S=16).
#
# Usage:
#   ./scripts/run_g2_v2_design3_1_off_run2.sh            # full preflight + 144 OFF + BUNDLE.sha256 seal
#   ./scripts/run_g2_v2_design3_1_off_run2.sh --dry-run  # read-only preflight only (0 disk writes, 0 ANN)
#
# Safety guarantees:
# - Uses frozen design-3.1 runner/contract/analyzer UNCHANGED (freeze SHA bc897419...).
# - Reuses audited Qualification PASS (20261124T094602Z) and Quality ON 18/18 (axd-g2-v2-quality-design3).
# - Preserves BOTH prior HOLD bundles (axd-g2-v2-off-design3 & axd-g2-v2-off-design3_1) untouched.
# - NEVER calls sudo, NEVER stops gdm.service, NEVER edits kernel/GRUB/governor/IRQ/frozen files.
# - NEVER overwrites/resumes an existing output directory, NEVER auto-retries on HOLD/failure.
# - Checks ALL audited quiet-host blockers including user timers, cron.service, snapd, and all 15 system timers.
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
APPROVAL_JSON="$EVIDENCE_ROOT/axd-g2-v2-approvals/design3_1_off_approval_run2.json"
QUAL_JSON="$EVIDENCE_ROOT/axd-g2-v2-design3-qualification-20261124T094602Z/qualification_result.json"
QUALITY_JSON="$EVIDENCE_ROOT/axd-g2-v2-quality-design3/quality.json"
HOLD_D3_DIR="$EVIDENCE_ROOT/axd-g2-v2-off-design3"
HOLD_D31_DIR="$EVIDENCE_ROOT/axd-g2-v2-off-design3_1"
OUT_DIR="$EVIDENCE_ROOT/axd-g2-v2-off-design3_1_run2"
CONSOLE_LOG="$EVIDENCE_ROOT/axd-g2-v2-off-design3_1_run2.console.log"
ANALYSIS_OUT="$EVIDENCE_ROOT/axd-g2-v2-off-design3_1_run2-analysis.json"

EXPECTED_DESIGN3_1_FREEZE_SHA256="bc8974193970b1663a53e08bc7de16b91013f11866965f872a78d775b7b28f5e"
EXPECTED_QUAL_SHA256="f64b9f9af6d230f320c2539c201079cbda42614c0a8b28f881b875fcf67c49cb"
EXPECTED_QUALITY_SHA256="360e1d29fc3c8f3c03e381ce57dea2e826459f7534577d6d24ec6ac81a54c59f"
EXPECTED_APPROVAL_SHA256="${EXPECTED_APPROVAL_SHA256:-}"
EXPECTED_KERNEL="7.0.0-43-generic"

if [[ ! -x "$VENV_PY" ]]; then
  echo "ERROR: Pinned Python venv not found at $VENV_PY" >&2
  exit 1
fi

cd "$REPO_ROOT"

echo "=== [Stage A] Read-Only Preflight (RUN 2): Freezes, HOLD Preservation, Approval OFF_AB, Qualification, Quality & Full Quiet TTY ==="
ACTUAL_KERNEL="$(uname -r)"
if [[ "$ACTUAL_KERNEL" != "$EXPECTED_KERNEL" ]]; then
  echo "ERROR: Kernel mismatch: got '$ACTUAL_KERNEL', expected '$EXPECTED_KERNEL'." >&2
  exit 2
fi
echo "KERNEL_CHECK=OK ($ACTUAL_KERNEL)"

# Verify all 3 frozen packages remain intact
sha256sum -c "$REPO_ROOT/docs/research/task-da/AXD_G2_V2_DESIGN3_1_FREEZE.sha256" >/dev/null
echo "DESIGN3_1_FREEZE_29_29=OK"
sha256sum -c "$REPO_ROOT/docs/research/task-da/AXD_G2_V2_DESIGN3_FREEZE.sha256" >/dev/null
echo "DESIGN3_FREEZE_26_26=OK"
sha256sum -c "$REPO_ROOT/docs/research/task-da/AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256" >/dev/null
echo "DESIGN2_FREEZE_24_24=OK"

# Verify BOTH prior HOLD bundles remain untouched
(cd "$HOLD_D3_DIR" && sha256sum -c BUNDLE.sha256 >/dev/null)
echo "PRESERVED_HOLD_DESIGN3_11_11=OK"
(cd "$HOLD_D31_DIR" && sha256sum -c BUNDLE.sha256 >/dev/null)
echo "PRESERVED_HOLD_DESIGN3_1_1080_1080=OK"

# Verify AC power online
AC_ONLINE="$(cat /sys/class/power_supply/AC/online 2>/dev/null || echo missing)"
if [[ "$AC_ONLINE" != "1" ]]; then
  echo "ERROR: AC power is not online (/sys/class/power_supply/AC/online='$AC_ONLINE')." >&2
  exit 2
fi
echo "AC_POWER=OK (online=1)"

# Full Quiet-Host check via dedicated read-only checker (covers GDM, Avahi, cups-browsed, cron,
# snapd, all 15 system timers + companion services, BOTH user timers + companion services, and catch-all timers)
QUIET_FAIL=0
set +e
"$REPO_ROOT/scripts/prepare_quiet_tty_env.sh" --check-only
QUIET_CHECK_RC=$?
set -e
if [[ "$QUIET_CHECK_RC" -ne 0 ]]; then
  QUIET_FAIL=1
fi

# Full Python design-3.1 contract, RUN2 OFF_AB approval, Qualification PASS, Quality ON 18/18, provenance & 144-plan check
env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT "$VENV_PY" - \
  "$ARTIFACTS_JSON" "$APPROVAL_JSON" "$QUAL_JSON" "$QUALITY_JSON" "$OUT_DIR" \
  "$EXPECTED_APPROVAL_SHA256" "$EXPECTED_DESIGN3_1_FREEZE_SHA256" \
  "$EXPECTED_QUAL_SHA256" "$EXPECTED_QUALITY_SHA256" "$DRY_RUN" "$QUIET_FAIL" <<'PY'
import json
import os
import shutil
import sys
from pathlib import Path

from research.task_da.g2_v2_design3_1_contract import (
    FREEZE, authorize, load_freeze, require, require_default_loader, sha, validate_schema,
)
from research.task_da.g2_v2_design3_guard import host_contract
from research.task_da.g2_v2_design3_1_runner import (
    plan, quality_context, verify_artifacts, verify_qualification,
)

artifacts_path = Path(sys.argv[1])
approval_path = Path(sys.argv[2])
qual_path = Path(sys.argv[3])
quality_path = Path(sys.argv[4])
out_dir = Path(sys.argv[5])
expected_approval_sha = sys.argv[6]
expected_freeze_sha = sys.argv[7]
expected_qual_sha = sys.argv[8]
expected_quality_sha = sys.argv[9]
dry_run = sys.argv[10] == "1"
quiet_fail = sys.argv[11] == "1"

require_default_loader(os.environ)
actual_freeze_sha = sha(FREEZE)
require(actual_freeze_sha == expected_freeze_sha,
        f"design-3.1 freeze SHA mismatch: got {actual_freeze_sha}, expected {expected_freeze_sha}")
freeze = load_freeze(environment=True)
hc = host_contract()

actual_qual_sha = sha(qual_path)
require(actual_qual_sha == expected_qual_sha,
        f"qualification SHA mismatch: got {actual_qual_sha}, expected {expected_qual_sha}")
qual = verify_qualification(qual_path, freeze=freeze)

actual_quality_sha = sha(quality_path)
require(actual_quality_sha == expected_quality_sha,
        f"quality.json SHA mismatch: got {actual_quality_sha}, expected {expected_quality_sha}")
quality = quality_context(
    quality_path,
    expected_artifacts_sha256=sha(artifacts_path),
    expected_qualification_sha256=actual_qual_sha,
)
require(quality.get("A_pass") is True and quality.get("B_pass") is True
        and quality.get("parity") is True and quality.get("duplicate_reduction") is True,
        "Quality Gate A/B/parity/duplicate_reduction not all PASS")

require(not out_dir.exists(), f"OFF run2 output directory already exists (never overwrite/resume): {out_dir}")

artifacts = json.loads(artifacts_path.read_text())
validate_schema(artifacts, "artifacts")
verify_artifacts(freeze, artifacts)

frozen_d3_plan = json.loads(
    Path(".local/artifacts/axd-g2-v2-design3-freeze-20261124/off_plan_design3_final.json").read_text()
)["commands"]
live_plan = plan(artifacts, "off", out_dir.resolve())
require(len(live_plan) == 144 and len(frozen_d3_plan) == 144, "144-OFF plan length mismatch")
for a, b in zip(frozen_d3_plan, live_plan):
    for k in ("block", "graph", "policy", "panel", "mode", "name"):
        require(a[k] == b[k], f"144-OFF schedule drift on key {k}")
    require(a["argv"][:-1] == b["argv"][:-1], "144-OFF argv drift")
    require(b["argv"][-1] == str(out_dir.resolve() / b["name"]), "144-OFF out-dir drift")

free_gib = shutil.disk_usage(out_dir.parent).free / (2**30)
require(free_gib > 25.0, f"insufficient free disk ({free_gib:.2f} GiB <= 25 GiB floor)")

print(f"HOST_CONTRACT=PASS cpu={hc['cpu_model']} kernel={hc['kernel']} cpus={hc['cpus']} free_disk={free_gib:.2f}GiB")
print("OFF_144_PLAN_VERIFIED=EXACT_EQUIVALENCE (12 balanced blocks x 6 R90 v1.3 graphs x 2 policies, beam=432, p=2, S=16, output=axd-g2-v2-off-design3_1_run2)")

if not approval_path.exists():
    print(f"APPROVAL_BLOCKER: signed run2 approval not found yet at {approval_path}", file=sys.stderr)
    sys.exit(4 if dry_run else 2)

actual_approval_sha = sha(approval_path)
if expected_approval_sha:
    require(actual_approval_sha == expected_approval_sha,
            f"approval SHA mismatch: got {actual_approval_sha}, expected {expected_approval_sha}")

approval = json.loads(approval_path.read_text())
scope = authorize(
    approval,
    actual_freeze_sha,
    sha(artifacts_path),
    "off",
    out_dir,
    qualification_digest=actual_qual_sha,
    quality_digest=actual_quality_sha,
)
require(scope == "OFF_AB" and approval["quota_s"] == 10800 and approval["quiet_host_confirmed"] is True,
        "unexpected OFF_AB approval scope/quota/confirmation")

print(f"CONTRACT_AND_PROVENANCE=PASS revision=design-3.1 scope={scope} quota_s={approval['quota_s']} approval_sha={actual_approval_sha} freeze_sha={actual_freeze_sha[:12]}... qual={qual['verdict']} quality_sha={actual_quality_sha[:12]}...")

if dry_run:
    print(f"DRY_RUN_COMPLETE: approval_ok=True off_output_exists={out_dir.exists()} quiet_host_ok={not quiet_fail}")
    if quiet_fail:
        print("NOTE: Quiet-host blockers present (expected on GUI desktop); real execution is blocked until multi-user.target + ./scripts/prepare_quiet_tty_env.sh passes.", file=sys.stderr)
        sys.exit(3)
    sys.exit(0)

if quiet_fail:
    print(
        "ABORT: Quiet-host blockers detected. Boot GRUB once with systemd.unit=multi-user.target "
        "(NEVER stop gdm.service from TTY!), then run ./scripts/prepare_quiet_tty_env.sh before running this script.",
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

APPROVAL_SHA_LIVE="$(sha256sum "$APPROVAL_JSON" | awk '{print $1}')"
{
  echo "=== [Stage B] Executing 144 Sequential OFF_AB Processes via Frozen design-3.1 Runner (RUN 2) ==="
  echo "Started UTC      : $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "Approval path    : $APPROVAL_JSON"
  echo "Approval SHA-256 : $APPROVAL_SHA_LIVE"
  echo "Output directory : $OUT_DIR"
  echo "Console log      : $CONSOLE_LOG"
  echo "Quota / Timeout  : 10800s (3h) phase quota / 180s per process / >=15s preflight / 0 auto-retries"
} | tee "$CONSOLE_LOG"

set +e
env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT \
  "$VENV_PY" -m research.task_da.g2_v2_design3_1_runner execute \
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
from research.task_da.g2_v2_design3_1_contract import schedule, sha, validate_schema
from research.task_da.g2_v2_design3_1_runner import name as task_name

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
    "revision": "design-3.1",
    "campaign": "run2",
    "phase": comp["phase"],
    "elapsed_s": round(comp["elapsed_s"], 2),
    "receipts_count": len(comp["receipts"]),
    "preflights_count": len(comp["preflight_sha256"]),
    "complete_json_sha256": sha(comp_path),
    "bundle_sha256": sha(out_dir / "BUNDLE.sha256"),
    "next_steps": [
        "1. Reboot normally (sudo reboot) to restore standard Ubuntu Desktop and all paused timers/services.",
        "2. Verify restoration: ./scripts/prepare_quiet_tty_env.sh --verify-restored",
        f'3. Run offline frozen design-3.1 analyzer separately (absolute paths required): env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT /home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python -m research.task_da.g2_v2_design3_1_analyzer --campaign "{out_dir}" --output "{analysis_out}"',
    ],
}
print(json.dumps(summary, indent=2))
PY
