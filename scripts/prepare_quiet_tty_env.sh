#!/usr/bin/env bash
# Targeted, reversible quiet-host preparation script (OUTSIDE frozen design-3.1 package)
# for G2 v2 design-3.1 OFF_AB run2 on Linux multi-user.target TTY.
#
# Usage:
#   ./scripts/prepare_quiet_tty_env.sh --check-only       # read-only audit (0 sudo, 0 mutations)
#   ./scripts/prepare_quiet_tty_env.sh                    # temporarily stop audited non-essential noise sources on TTY
#   ./scripts/prepare_quiet_tty_env.sh --verify-restored  # read-only check AFTER rebooting back to Ubuntu Desktop
#
# Safety guarantees:
# - NEVER calls 'systemctl stop gdm.service' (hard-aborts if gdm.service or gnome-shell is active!).
# - NEVER uses disable, mask, uninstall, or modifies /etc, /boot, GRUB, BIOS, CPU governor, or IRQ.
# - NEVER stops power, thermal/hwmon, kernel, watchdog, udev, dbus, or systemd-logind services.
# - ONLY issues temporary 'stop' on verified non-essential background noise sources; a normal
#   'sudo reboot' restores every service and timer automatically.
set -euo pipefail

MODE="apply"
if [[ "${1:-}" == "--check-only" ]]; then
  MODE="check"
  shift
elif [[ "${1:-}" == "--verify-restored" ]]; then
  MODE="restored"
  shift
fi
if [[ $# -gt 0 ]]; then
  echo "Usage: $0 [--check-only | --verify-restored]" >&2
  exit 2
fi

EXPECTED_KERNEL="7.0.0-43-generic"

# Audited non-essential user timers & companion services (culprit of run1 HOLD at 03:00:54 +07)
USER_TIMERS=(
  snap.firmware-updater.firmware-notifier.timer
  launchpadlib-cache-clean.timer
)
USER_COMPANION_SERVICES=(
  snap.firmware-updater.firmware-notifier.service
  launchpadlib-cache-clean.service
)

# Audited non-essential system daemons/sockets (mDNS, printing, cron, snapd auto-refresh)
SYSTEM_NOISE_SERVICES=(
  cups-browsed.service
  avahi-daemon.socket
  avahi-daemon.service
  cron.service
  snapd.socket
  snapd.service
)

# Audited periodic system timers (9 original + 6 newly audited)
SYSTEM_TIMERS=(
  sysstat-collect.timer
  sysstat-summary.timer
  fwupd-refresh.timer
  anacron.timer
  dpkg-db-backup.timer
  logrotate.timer
  motd-news.timer
  apt-daily.timer
  apt-daily-upgrade.timer
  systemd-tmpfiles-clean.timer
  man-db.timer
  update-notifier-download.timer
  update-notifier-motd.timer
  e2scrub_all.timer
  fstrim.timer
)

# Companion oneshot/D-Bus services triggered by the timers above
SYSTEM_COMPANION_SERVICES=(
  sysstat-collect.service
  sysstat-summary.service
  fwupd-refresh.service
  fwupd.service
  anacron.service
  dpkg-db-backup.service
  logrotate.service
  motd-news.service
  apt-daily.service
  apt-daily-upgrade.service
  systemd-tmpfiles-clean.service
  man-db.service
  update-notifier-download.service
  update-notifier-motd.service
  e2scrub_all.service
  fstrim.service
)

unit_loaded() {
  local scope="$1" unit="$2" state
  if [[ "$scope" == "user" ]]; then
    state="$(systemctl --user show -p LoadState --value "$unit" 2>/dev/null || true)"
  else
    state="$(systemctl show -p LoadState --value "$unit" 2>/dev/null || true)"
  fi
  [[ "$state" == "loaded" ]]
}

unit_active() {
  local scope="$1" unit="$2" st
  if [[ "$scope" == "user" ]]; then
    st="$(systemctl --user is-active "$unit" 2>/dev/null || true)"
  else
    st="$(systemctl is-active "$unit" 2>/dev/null || true)"
  fi
  [[ "$st" == "active" || "$st" == "activating" || "$st" == "reloading" ]]
}

if [[ "$MODE" == "restored" ]]; then
  echo "=== [Post-Reboot Restoration Verification] Read-Only ==="
  echo "kernel=$(uname -r)  AC=$(cat /sys/class/power_supply/AC/online 2>/dev/null || echo missing)"
  RESTORE_FAIL=0
  for u in gdm.service cups-browsed.service avahi-daemon.socket avahi-daemon.service cron.service snapd.socket snapd.service "${SYSTEM_TIMERS[@]}"; do
    if unit_loaded system "$u"; then
      st="$(systemctl is-active "$u" 2>/dev/null || true)"
      echo "  [system] $u : ${st:-inactive}"
      if [[ "$st" != "active" ]]; then
        RESTORE_FAIL=1
      fi
    fi
  done
  for u in "${USER_TIMERS[@]}"; do
    if unit_loaded user "$u"; then
      st="$(systemctl --user is-active "$u" 2>/dev/null || true)"
      echo "  [user]   $u : ${st:-inactive}"
      if [[ "$st" != "active" ]]; then
        RESTORE_FAIL=1
      fi
    fi
  done
  if [[ "$RESTORE_FAIL" -eq 0 ]]; then
    echo "POST_REBOOT_RESTORATION=OK (all checked desktop/system/user units active)"
    exit 0
  else
    echo "POST_REBOOT_RESTORATION=INCOMPLETE (some unit not active yet; re-check after login settles)" >&2
    exit 1
  fi
fi

echo "=== [Quiet TTY Environment] Mode: $MODE ==="
ACTUAL_KERNEL="$(uname -r)"
if [[ "$ACTUAL_KERNEL" != "$EXPECTED_KERNEL" ]]; then
  echo "ERROR: Kernel mismatch: got '$ACTUAL_KERNEL', expected '$EXPECTED_KERNEL'." >&2
  exit 2
fi
echo "KERNEL=OK ($ACTUAL_KERNEL)"

AC_ONLINE="$(cat /sys/class/power_supply/AC/online 2>/dev/null || echo missing)"
if [[ "$AC_ONLINE" != "1" ]]; then
  echo "ERROR: AC power is not online (/sys/class/power_supply/AC/online='$AC_ONLINE')." >&2
  exit 2
fi
echo "AC_POWER=OK (online=1)"

GDM_STATE="$(systemctl is-active gdm.service 2>/dev/null || true)"
if [[ "$GDM_STATE" == "active" || "$GDM_STATE" == "activating" || "$GDM_STATE" == "reloading" ]]; then
  echo "BLOCKER: gdm.service is '$GDM_STATE'. Boot GRUB once with systemd.unit=multi-user.target (NEVER stop gdm.service from TTY!)." >&2
  if [[ "$MODE" == "apply" ]]; then
    echo "ABORT: Refusing to modify services while gdm.service is active." >&2
    exit 2
  fi
else
  echo "GDM_SERVICE=OK (${GDM_STATE:-inactive})"
fi

if [[ "$MODE" == "apply" ]]; then
  # Extra safety check: ensure no GNOME Shell / GDM3 processes are running
  if pgrep -af 'gnome-shell|gdm3' >/dev/null 2>&1; then
    echo "ABORT: gnome-shell/gdm3 process detected; boot cleanly into multi-user.target first." >&2
    exit 2
  fi

  # 1. Stop audited user timers & companion services (no sudo needed)
  ACTIVE_USER=()
  for u in "${USER_TIMERS[@]}" "${USER_COMPANION_SERVICES[@]}"; do
    if unit_loaded user "$u" && unit_active user "$u"; then
      ACTIVE_USER+=("$u")
    fi
  done
  if [[ ${#ACTIVE_USER[@]} -gt 0 ]]; then
    echo "Stopping user units: ${ACTIVE_USER[*]}"
    systemctl --user stop "${ACTIVE_USER[@]}"
  else
    echo "USER_NOISE_UNITS=ALREADY_INACTIVE"
  fi

  # 2. Stop audited non-essential system services, timers, and any already-triggered companion services
  ACTIVE_SYS=()
  for u in "${SYSTEM_NOISE_SERVICES[@]}" "${SYSTEM_TIMERS[@]}" "${SYSTEM_COMPANION_SERVICES[@]}"; do
    if unit_loaded system "$u" && unit_active system "$u"; then
      ACTIVE_SYS+=("$u")
    fi
  done
  if [[ ${#ACTIVE_SYS[@]} -gt 0 ]]; then
    echo "Stopping system units (temporary until reboot): ${ACTIVE_SYS[*]}"
    sudo systemctl stop "${ACTIVE_SYS[@]}"
  else
    echo "SYSTEM_NOISE_UNITS=ALREADY_INACTIVE"
  fi
fi

# Read-only verification pass (runs in BOTH --check-only and apply modes)
BLOCKERS=0
if unit_active system gdm.service; then
  echo "QUIET_BLOCKER: gdm.service is active" >&2
  BLOCKERS=1
fi
for u in "${USER_TIMERS[@]}" "${USER_COMPANION_SERVICES[@]}"; do
  if unit_loaded user "$u" && unit_active user "$u"; then
    echo "QUIET_BLOCKER: [user] $u is active" >&2
    BLOCKERS=1
  fi
done
for u in "${SYSTEM_NOISE_SERVICES[@]}" "${SYSTEM_TIMERS[@]}" "${SYSTEM_COMPANION_SERVICES[@]}"; do
  if unit_loaded system "$u" && unit_active system "$u"; then
    echo "QUIET_BLOCKER: [system] $u is active" >&2
    BLOCKERS=1
  fi
done

# Catch-all check for ANY remaining active timers in system or user scope
REM_SYS_TIMERS="$(systemctl list-timers --no-pager --no-legend 2>/dev/null || true)"
REM_USR_TIMERS="$(systemctl --user list-timers --no-pager --no-legend 2>/dev/null || true)"
if [[ -n "$REM_SYS_TIMERS" ]]; then
  echo "QUIET_BLOCKER: active system timer(s) remain:" >&2
  echo "$REM_SYS_TIMERS" >&2
  BLOCKERS=1
else
  echo "ACTIVE_SYSTEM_TIMERS=0 (CLEAN)"
fi
if [[ -n "$REM_USR_TIMERS" ]]; then
  echo "QUIET_BLOCKER: active user timer(s) remain:" >&2
  echo "$REM_USR_TIMERS" >&2
  BLOCKERS=1
else
  echo "ACTIVE_USER_TIMERS=0 (CLEAN)"
fi

if pgrep -af 'avahi-daemon|gnome-shell|gdm3|cups-browsed|firmware-notifier|/usr/libexec/fwupd/fwupd' >/dev/null 2>&1; then
  echo "QUIET_BLOCKER: competing process(es) still running:" >&2
  pgrep -af 'avahi-daemon|gnome-shell|gdm3|cups-browsed|firmware-notifier|/usr/libexec/fwupd/fwupd' >&2 || true
  BLOCKERS=1
else
  echo "COMPETING_PROCESSES=0 (CLEAN)"
fi

if [[ "$BLOCKERS" -ne 0 ]]; then
  if [[ "$MODE" == "check" ]]; then
    echo "QUIET_ENV_CHECK=BLOCKED (expected on Ubuntu Desktop; run on multi-user.target TTY without --check-only)" >&2
    exit 3
  fi
  echo "QUIET_ENV_PREP=INCOMPLETE (resolve blockers above before launching OFF)" >&2
  exit 2
fi

echo "QUIET_ENV_READY=OK (kernel=$ACTUAL_KERNEL, AC=1, GDM=inactive, 0 active system/user timers, 0 competing daemons)"
