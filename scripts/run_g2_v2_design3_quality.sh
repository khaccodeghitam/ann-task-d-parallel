#!/usr/bin/env bash
# Orchestrator wrapper (OUTSIDE frozen design-3 package) for owner-approved
# G2 v2 design-3 QUALITY_ONLY execution (18 sequential ON processes, beam=432, p=2, S=16).
#
# Usage:
#   ./scripts/run_g2_v2_design3_quality.sh            # full preflight + B4 materialize + 18 ON
#   ./scripts/run_g2_v2_design3_quality.sh --dry-run  # read-only preflight + in-memory B4 only (0 writes, 0 ANN)
#
# Safety guarantees:
# - NEVER calls sudo, NEVER stops gdm.service, NEVER edits kernel/GRUB/governor/frozen files.
# - NEVER bypasses any frozen runner, guard, preflight, schema, or checksum check.
# - NEVER overwrites/resumes an existing output directory or retries on HOLD/failure.
# - NEVER opens 144 G2 OFF (strictly pinned to --phase quality and scope=QUALITY_ONLY).
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
APPROVAL_JSON="$EVIDENCE_ROOT/axd-g2-v2-approvals/design3_quality_only_approval.json"
QUAL_JSON="$EVIDENCE_ROOT/axd-g2-v2-design3-qualification-20261124T094602Z/qualification_result.json"
OUT_DIR="$EVIDENCE_ROOT/axd-g2-v2-quality-design3"
CONSOLE_LOG="$EVIDENCE_ROOT/axd-g2-v2-quality-design3.console.log"
EXPECTED_APPROVAL_SHA256="bb482f042a226c14bc163efde6bebe8b865351cfd69dfa45c34298d802ce2002"
EXPECTED_KERNEL="7.0.0-43-generic"

if [[ ! -x "$VENV_PY" ]]; then
  echo "ERROR: Pinned Python venv not found at $VENV_PY" >&2
  exit 1
fi

cd "$REPO_ROOT"

echo "=== [Stage A] Read-Only Preflight: Freeze, Approval, Qualification, Kernel & Quiet TTY ==="
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

# Quiet-host check (READ-ONLY — never stops services itself; NEVER stop gdm.service from TTY!)
QUIET_FAIL=0
for unit in gdm.service cups-browsed.service avahi-daemon.socket avahi-daemon.service; do
  st="$(systemctl is-active "$unit" 2>/dev/null || true)"
  if [[ "$st" == "active" || "$st" == "activating" || "$st" == "reloading" ]]; then
    echo "QUIET_HOST_BLOCKER: unit '$unit' is '$st' (must be inactive)" >&2
    QUIET_FAIL=1
  else
    echo "UNIT_INACTIVE=OK ($unit: ${st:-inactive})"
  fi
done
if pgrep -af 'avahi-daemon|gnome-shell|gdm3|cups-browsed' >/dev/null 2>&1; then
  echo "QUIET_HOST_BLOCKER: competing desktop/mDNS process still running:" >&2
  pgrep -af 'avahi-daemon|gnome-shell|gdm3|cups-browsed' >&2 || true
  QUIET_FAIL=1
else
  echo "COMPETING_DAEMONS_ABSENT=OK (no avahi-daemon/gnome-shell/gdm3/cups-browsed)"
fi

for timer in sysstat-collect.timer fwupd-refresh.timer; do
  tst="$(systemctl is-active "$timer" 2>/dev/null || true)"
  echo "OPTIONAL_TIMER_STATUS: $timer=${tst:-inactive}"
done

# Full Python contract, approval, qualification, provenance & in-memory B4 verification
env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT "$VENV_PY" - \
  "$ARTIFACTS_JSON" "$APPROVAL_JSON" "$QUAL_JSON" "$OUT_DIR" "$EXPECTED_APPROVAL_SHA256" "$DRY_RUN" "$QUIET_FAIL" <<'PY'
import hashlib
import json
import os
import sys
from pathlib import Path

from research.task_da.g2_v2_design3_contract import (
    FREEZE, GRAPHS, authorize, load_freeze, require, require_default_loader, sha, validate_schema,
)
from research.task_da.g2_v2_design3_guard import host_contract
from research.task_da.g2_v2_design3_runner import plan, verify_qualification

artifacts_path = Path(sys.argv[1])
approval_path = Path(sys.argv[2])
qual_path = Path(sys.argv[3])
out_dir = Path(sys.argv[4])
expected_approval_sha = sys.argv[5]
dry_run = sys.argv[6] == "1"
quiet_fail = sys.argv[7] == "1"

require_default_loader(os.environ)
freeze = load_freeze(environment=True)
hc = host_contract()
qual = verify_qualification(qual_path)

actual_approval_sha = sha(approval_path)
require(actual_approval_sha == expected_approval_sha,
        f"approval SHA mismatch: got {actual_approval_sha}, expected {expected_approval_sha}")
approval = json.loads(approval_path.read_text())
scope = authorize(
    approval,
    sha(FREEZE),
    sha(artifacts_path),
    "quality",
    out_dir,
    qualification_digest=sha(qual_path),
)
require(scope == "QUALITY_ONLY" and approval["quota_s"] == 3600 and approval["quiet_host_confirmed"] is True,
        "unexpected approval scope/quota")
require(not out_dir.exists(), f"output directory already exists (never overwrite/resume): {out_dir}")

artifacts = json.loads(artifacts_path.read_text())
validate_schema(artifacts, "artifacts")
tasks = plan(artifacts, "quality", out_dir.resolve())
require(len(tasks) == 18, f"expected 18 quality tasks, got {len(tasks)}")

# Verify immutable native runtime, compiler, binary, dataset, graphs, Stage 5 validation baselines
for p, digest in freeze["native_runtime_sha256"].items():
    require(sha(p) == digest, f"native runtime changed: {p}")
require(sha(freeze["compiler"]["executable"]) == freeze["compiler"]["sha256"], "compiler changed")
for k in ("binary", "base", "queries", "gt", "val", "warmup"):
    require(sha(artifacts[k]) == freeze["artifact_sha256"][k], f"artifact mismatch: {k}")
require(set(artifacts["graphs"]) == set(GRAPHS), "graph cohort mismatch")
for g, digest in freeze["graph_sha256"].items():
    require(sha(artifacts["graphs"][g]) == digest, f"graph mismatch: {g}")
for g, item in freeze["validation_baseline"].items():
    require(sha(Path(artifacts["validation_root"]) / item["path"]) == item["sha256"],
            f"validation baseline mismatch: {g}")

# B4 deterministic test-panel verification (in-memory first; write ONLY when not dry-run and quiet_host OK)
ev_root = Path("/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence")
id_pins = {
    "val_10k": (ev_root / "p1-full-validation-20261117T225717+0700/split/val_10k.ids",
                "a3c948e9aac4f40c1fb818a6f784c4fbb56473a0769affe3344493ed4eb87f57", 10000),
    "test_90k": (ev_root / "p1-full-validation-20261117T225717+0700/split/test_90k.ids",
                 "af871517d88aaad90549ba2fde0d4ed745f59400037a757f17bc93fa479bbfa3", 90000),
    "pilot_3k": (ev_root / "p2-exploratory-0990-20261118/pilot_r1/pilot_test_3000.ids",
                 "18d8b901e925d71c0ddb2d043bf2cba12edab4061859da833bd1ccc37790c1b0", 3000),
    "disjoint_3k": (ev_root / "p2-pivot-b1-a1-20261119/disjoint_test_3000.ids",
                    "c91dcae377afc8161856377842930c691b2ea19e337d1361576538b5ab39abfc", 3000),
    "narrow_3k": (ev_root / "p2-b1-a1-narrow-20261119/narrow_test_3000.ids",
                  "77fda0316a8bb559c75e113ec3d750de0cf93403a11be474fc375c94c927c90b", 3000),
    "warmup_100": (ev_root / "p2-exploratory-0990-20261118/pilot_r1/warmup_val_100.ids",
                   "199ca6066269641347280d6ef4eaab39efee3397b87c23cd74d38ee85bcd4783", 100),
}
loaded = {}
for label, (p, exp_sha, exp_n) in id_pins.items():
    require(sha(p) == exp_sha, f"B4 source ID SHA mismatch: {label}")
    vals = [int(x) for x in p.read_text().split()]
    require(len(vals) == exp_n and len(set(vals)) == exp_n, f"B4 source ID invalid: {label}")
    loaded[label] = vals

pool = set(loaded["test_90k"]) - (set(loaded["pilot_3k"]) | set(loaded["disjoint_3k"]) | set(loaded["narrow_3k"]))
require(len(pool) == 81_000, f"unexpected pool size: {len(pool)}")
pool_sha = hashlib.sha256("".join(f"{q}\n" for q in sorted(pool)).encode("ascii")).hexdigest()
require(pool_sha == "ab1de8ef151cc0fffce9b859d3f6f674bdf81581afe592a633aa605e3f4acef1", "pool SHA mismatch")

prefix = "axd-g2-v2-3a-test10k-20261123/"
ordered = sorted(pool, key=lambda q: (hashlib.sha256((prefix + str(q)).encode("ascii")).digest(), q))
panel = ordered[:10_000]
serialized = "".join(f"{q}\n" for q in panel).encode("ascii")
expected_test_sha = freeze["artifact_sha256"]["test"]
require(hashlib.sha256(serialized).hexdigest() == expected_test_sha, "computed B4 test panel SHA mismatch")
require(panel[:10] == [32792, 20400, 17878, 72872, 61505, 35404, 40783, 34564, 23435, 79120],
        "B4 first-10 ID order mismatch")
pset = set(panel)
require(len(pset) == 10_000 and all(0 <= q < 100_000 for q in panel), "B4 count/bounds invalid")
for k in ("val_10k", "pilot_3k", "disjoint_3k", "narrow_3k", "warmup_100"):
    require(pset.isdisjoint(loaded[k]), f"B4 overlap with {k}")

print(f"CONTRACT_AND_PROVENANCE=PASS scope={scope} approval_sha={actual_approval_sha[:12]}... qual={qual['verdict']}")
print(f"HOST_CONTRACT=PASS cpu={hc['cpu_model']} kernel={hc['kernel']} cpus={hc['cpus']}")
print(f"B4_IN_MEMORY_VERIFIED=PASS count=10000 overlap=0 sha256={expected_test_sha}")

test_path = Path(artifacts["test"])
if dry_run:
    print(f"DRY_RUN_COMPLETE: test_panel_exists={test_path.exists()} quiet_host_ok={not quiet_fail}")
    if quiet_fail:
        print("NOTE: Quiet-host blockers present (expected on GUI desktop); real execution is blocked until multi-user.target + Avahi/cups-browsed stopped.", file=sys.stderr)
        sys.exit(3)
    sys.exit(0)

if quiet_fail:
    print("ABORT: Quiet-host blockers detected. Boot GRUB once with systemd.unit=multi-user.target (NEVER stop gdm.service from TTY!), then stop cups-browsed.service, avahi-daemon.socket, avahi-daemon.service.", file=sys.stderr)
    sys.exit(2)

# Stage B: Materialize B4 test panel once (exclusive create; never overwrite)
if not test_path.exists():
    test_path.parent.mkdir(parents=True, exist_ok=True)
    with test_path.open("xb") as fh:
        fh.write(serialized)
    on_disk_sha = sha(test_path)
    require(on_disk_sha == expected_test_sha, f"on-disk B4 SHA mismatch: {on_disk_sha}")
    sha_note = test_path.with_suffix(".sha256")
    if not sha_note.exists():
        sha_note.write_text(f"{on_disk_sha}  {test_path.name}\n")
    print(f"B4_MATERIALIZED_ONCE=OK path={test_path} sha256={on_disk_sha}")
else:
    on_disk_sha = sha(test_path)
    require(on_disk_sha == expected_test_sha, f"existing test panel SHA mismatch: {on_disk_sha}")
    existing_ids = [int(x) for x in test_path.read_text().split()]
    require(existing_ids == panel, "existing test panel content/order mismatch")
    print(f"B4_EXISTING_VERIFIED=OK path={test_path} sha256={on_disk_sha}")
PY

if [[ "$DRY_RUN" -eq 1 ]]; then
  exit 0
fi

echo "=== [Stage C] Executing 18 Sequential QUALITY_ONLY ON Processes via Frozen design-3 Runner ==="
echo "Output directory : $OUT_DIR"
echo "Console log      : $CONSOLE_LOG"
echo "Quota / Timeout  : 3600s phase quota / 180s per process / 0 auto-retries"

set +e
env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT \
  "$VENV_PY" -m research.task_da.g2_v2_design3_runner execute \
  --phase quality \
  --artifacts "$ARTIFACTS_JSON" \
  --approval "$APPROVAL_JSON" \
  --qualification "$QUAL_JSON" \
  --output "$OUT_DIR" 2>&1 | tee "$CONSOLE_LOG"
RUNNER_RC=${PIPESTATUS[0]}
set -e

echo "=== [Stage D] Post-Run Evidence Seal & Audit Summary (runner_rc=$RUNNER_RC) ==="
if [[ -d "$OUT_DIR" ]]; then
  (
    cd "$OUT_DIR"
    find . -type f ! -name 'BUNDLE.sha256' | LC_ALL=C sort | sed 's|^\./||' | xargs -d '\n' sha256sum > BUNDLE.sha256
    sha256sum -c BUNDLE.sha256 >/dev/null
  )
  echo "BUNDLE_SHA256_SEALED=OK ($OUT_DIR/BUNDLE.sha256)"
fi

env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT "$VENV_PY" - "$OUT_DIR" "$RUNNER_RC" <<'PY'
import json
import sys
from pathlib import Path
from research.task_da.g2_v2_design3_contract import sha
from research.task_da.g2_v2_design3_runner import quality_context

out_dir = Path(sys.argv[1])
rc = int(sys.argv[2])
hold_path = out_dir / "HOLD.json"
qual_path = out_dir / "quality.json"
comp_path = out_dir / "complete.json"

if hold_path.exists() or rc != 0:
    print("VERDICT=QUALITY_EXECUTION_HOLD (evidence preserved; NEVER overwrite or retry into this directory)")
    if hold_path.exists():
        print(hold_path.read_text())
    sys.exit(rc if rc != 0 else 2)

quality_context(qual_path)
q = json.loads(qual_path.read_text())
c = json.loads(comp_path.read_text())
summary = {
    "verdict": "QUALITY_GATE_PASS" if (q["A_pass"] and q["parity"] and q["duplicate_reduction"]) else "QUALITY_HOLD",
    "A_pass": q["A_pass"],
    "B_pass": q["B_pass"],
    "parity": q["parity"],
    "duplicate_reduction": q["duplicate_reduction"],
    "recall": [round(x, 6) for x in q["recall"]],
    "lcb95": [round(x, 6) for x in q["lcb95"]],
    "arm_difference": round(q["arm_difference"], 6),
    "arm_ci95": [round(x, 6) for x in q["arm_ci95"]],
    "elapsed_s": round(c["elapsed_s"], 2),
    "quality_json_sha256": sha(qual_path),
    "complete_json_sha256": sha(comp_path),
    "next_step": "STOP HERE (144 OFF remains NOT_OPEN). Reboot normally (sudo reboot) to restore Ubuntu Desktop and share quality.json + BUNDLE.sha256 for audit.",
}
print(json.dumps(summary, indent=2))
PY
