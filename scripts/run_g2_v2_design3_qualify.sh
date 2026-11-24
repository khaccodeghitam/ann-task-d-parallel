#!/usr/bin/env bash
# One-command 900-second read-only host qualification for G2 v2 design-3.
# Run on a minimal Linux TTY (Ctrl+Alt+F3) after logging out of Ubuntu Desktop.
# Never executes ANN binaries, never opens test panels, never modifies thresholds.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PY="${G2_V2_VENV_PY:-/home/thinhbui/.local/share/axd-g2-v2-design2/venv/bin/python}"

if [[ ! -x "$VENV_PY" ]]; then
  echo "ERROR: Pinned Python venv not found at $VENV_PY" >&2
  exit 1
fi

cd "$REPO_ROOT"
exec env -u LD_PRELOAD -u LD_LIBRARY_PATH -u LD_AUDIT \
  "$VENV_PY" -m research.task_da.g2_v2_design3_qualify "$@"
