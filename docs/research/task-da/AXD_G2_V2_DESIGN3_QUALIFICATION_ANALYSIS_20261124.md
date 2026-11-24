# G2 v2 design-3 — Read-Only Forensic Analysis of 900s Host Qualification (`20261124T082344Z`)

- **Date:** 2026-11-24
- **Scope:** Strictly read-only forensic audit of the completed 900-second `design-3` host qualification bundle (`axd-g2-v2-design3-qualification-20261124T082344Z`).
- **Evidence location (external, immutable):** `../../../../artifact-evidence/axd-g2-v2-design3-qualification-20261124T082344Z/`
- **Recorded qualification verdict:** **`QUALIFICATION_HOLD`** (`qualification_pass = false`)
- **Action taken during this review:** None (zero services stopped, zero source files edited, zero thresholds changed, zero freeze manifests modified, `0/18` G2 Quality ON, `0/144` G2 OFF, test panel `v2_test_10000.ids` NOT materialized, Task A Google Sheets untouched).

---

## 1. Evidence Integrity & Freeze Provenance Audit

All integrity, schema, freeze-manifest, and independent-replay checks passed **100%**:

| Check | Scope / Target | Result |
|---|---|---|
| `BUNDLE.sha256` verification | `qualification_result.json` (`c597e572b9d5fd4b6f4e614b52e3071503fe3caf3fe5e2b3514d1813a7243a28`) + `qualification_telemetry.jsonl` (`7d92649d5d3e9065aea7d0cfc741a75e6ef53c71936279c9eb606c5e35bf1a79`) | **2/2 OK** |
| JSON schema validation | `schema = "axd_g2_v2.3"` (`qualification_result.json`) | **PASS** |
| Frozen `design-3` manifest SHA match | `freeze_sha256 = 425c748329292ffe15db2c52bdf53f5d219b47d1ecf95ac3c76a5429814159ae` matches [`AXD_G2_V2_DESIGN3_FREEZE_MANIFEST.json`](AXD_G2_V2_DESIGN3_FREEZE_MANIFEST.json) | **EXACT MATCH** |
| Frozen `design-3` package integrity | [`AXD_G2_V2_DESIGN3_FREEZE.sha256`](AXD_G2_V2_DESIGN3_FREEZE.sha256) | **26/26 OK** |
| Frozen `design-2` package integrity | [`AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256`](AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256) | **24/24 OK** |
| Independent telemetry replay | Replaying all `860` snapshots from `qualification_telemetry.jsonl` through [`g2_v2_design3_guard.py`](../../../research/task_da/g2_v2_design3_guard.py) (`ContentionV3(phase="qualification")` + `CoolingGuard`) | **EXACT MATCH** (`fail10 = 93`, `fail15 = 0`, `hard = 0`) |

Run identity confirmed from `qualification_result.json`:
- **Host:** `AMD Ryzen 5 PRO 4650U`, kernel `7.0.0-43-generic`, `CLK_TCK = 100`, `allowed_cpus = [0..11]`, worker CPUs `[0, 2]`, worker cores+SMT `[0, 1, 2, 3]`, CCX0/L3 `[0..5]`, CCX1/L3 `[6..11]`.
- **Window:** `2026-11-24T08:23:44.645331Z` → `2026-11-24T08:38:44.760617Z` (`observed_wall_s = 900.089 s`, `samples = 860`, mean 10s rolling window width `10.473 s`).

---

## 2. Quantitative Analysis of `qualification_result.json` & `qualification_telemetry.jsonl`

### 2.1 Gate-by-Gate Outcome — What Passed 100% vs What Failed

A key result of this run is that **every `design-3` engineering improvement and 4 of the 5 guard gates passed 100% across the entire 15-minute window**; only the tightest tier (`worker-cores [0..3] <= 0.01`) drove `QUALIFICATION_HOLD`:

| Gate / Metric | Frozen `design-3` Limit | Observed Value | Status |
|---|---|---|---|
| **15s whole-host `[0..11]` foreign CPU** | `<= 0.0250` (`p2` fraction) | `mean 0.01233`, `p95 0.01566`, **`max 0.01851`** (`845 PASS / 0 FAIL`) | **100% PASS** |
| **10s single foreign process rate** | `<= 0.1000` (1-core fraction) | `mean 0.00891`, `p95 0.01426`, **`max 0.01620`** (`0 FAIL`) | **100% PASS** |
| **Hard hardware / thermal / resource guards** | `Tctl < 85°C`, AC online, RAM/disk/swap | `Tctl 37.75–56.625°C`, `AC=1`, `min MemAvailable = 13.47 GiB`, `min free disk = 138.07 GiB`, `swap = 0 B` | **0 FAIL** |
| **Monitor self-overhead (`design-3` single-pass fix)** | Informative (target `<< design-2`) | `14.00 s / 900.09 s` = **`1.555%` of 1 core** (`0.778%` of `p2`), `observer_cpu_s` mean `14.9 ms`, p95 `16.2 ms` | **VALIDATED (`~4×` lower than `design-2`)** |
| **10s CCX0/L3 `[0..5]` foreign CPU** | `<= 0.0200` (`p2` fraction) | `mean 0.00973`, `p95 0.01390`, **`max 0.02006`** (**`1 / 850 FAIL`**, step 20 only) | **FAIL (1 window, +0.00006 over cap)** |
| **10s worker-cores `[0..3]` foreign CPU** | `<= 0.0100` (`p2` fraction) | `mean 0.00663`, `p50 0.00620`, `p95 0.01100`, **`max 0.01435`** (**`93 / 850 FAIL`**, `757 PASS`) | **FAIL (primary cause of HOLD)** |

Additional structural properties of the **93 failing 10-second windows**:
- **Contiguous episodes:** `93` overlapping 10s windows grouped into **47 short episodes** (1–5 consecutive windows each), distributed steadily across the entire 15-minute run rather than concentrated in a single cron/timer burst:
  - Per-minute fail counts (minutes `0..14`): `6, 8, 0, 2, 5, 7, 7, 10, 10, 9, 4, 4, 10, 6, 5` (total `93`).
- **Narrow exceedance margin:** `40 / 93` failing windows fell between `0.0100` and `0.0109`; overall mean across the 93 failing windows was `0.01113`, and worst peak was `0.01435` (Episode 33, `t = 626–629 s`).
- **Exact tier & attribution mechanism:**
  - `93 / 93` failed `worker-cores [0..3] > 0.0100` (`1 / 93` simultaneously tripped `CCX0 [0..5] = 0.02006 > 0.02000` at Episode 2, step 20).
  - **`92 / 93` were driven by `procs_workers_s`** (directly tracked foreign PIDs attributed to CPUs `[0..3]`), and only **`1 / 93`** (Episode 30, step 554, `t = 580.3 s`) was driven by the per-CPU conservation lower bound (`per_cpu_lb = 0.01008`, when `avahi-daemon` ended on `cpu4` while `gnome-shell` ran `0.04 s` on `cpu1`).
  - Across all 93 failing windows, `per_cpu_lb` averaged only `0.00558` (max `0.01008`), confirming that **untracked kernel/IRQ bursts were NOT the dominant driver**.

### 2.2 Top Processes Contributing to the 93 Failing 10s Windows and Full 900s Run

#### Table A — Top Contributors Inside the 93 Failing 10s Windows (Overlapping Window Sums on CPUs `0..3`)

*(Values below sum `window_accounting()` 10s PID deltas attributed to `WORKER_CORES_CPUS = {0,1,2,3}` across the 93 overlapping failing 10s windows; because windows overlap at 1s steps, summed seconds exceed wall time.)*

| Rank | Process (`comm`) | PID (`start`) | Sum on `[0..3]` across 93 fail wins | Mean per fail win on `[0..3]` | Seen in fail wins | Share of `foreign_workers_s` in fail wins |
|---|---|---|---:|---:|---:|---:|
| **1** | **`avahi-daemon`** | `907` (`812`) | **`10.970 s`** | **`0.1180 s`** | **`93 / 93`** (`92/93` end-CPU on `0..3`) | **mean `50.6%`**, median `50.0%`, max **`69.6%`** |
| **2** | **`gnome-shell`** | `1624` (`1030`) | **`1.980 s`** | **`0.0213 s`** | **`86 / 93`** (`76/93` end-CPU on `0..3`) | **mean `9.1%`**, max **`26.1%`** |
| 3 | `irq/9-acpi` | `107` (`31`) | `1.350 s` | `0.0145 s` | `93 / 93` | OS hardware IRQ (pinned `cpu1`) |
| 4 | `NetworkManager` | `966` (`819`) | `0.880 s` | `0.0095 s` | `79 / 93` | Network management daemon |
| 5 | `irq/96-iwlwifi:default_queue` | `586` (`385`) | `0.830 s` | `0.0089 s` | `83 / 93` | Wi-Fi driver IRQ (`cpu0`) |
| 6 | `kworker/u48:2-dm_vblank_control_workqueue` | `137` (`60`) | `0.700 s` | `0.0075 s` | `93 / 93` | AMD display vblank workqueue |
| 7–15 | `kworker/*-events`, `irq/97..99-iwlwifi`, `rcu_preempt` | various | `0.25–0.48 s` each | `0.0027–0.0052 s` each | `12–93 / 93` | Routine kernel/Wi-Fi background |

#### Table B — Top Foreign Processes Across the Entire 900.09s Run (Non-Overlapping 1s-Step Totals by CPU Zone)

| Rank | Process (`comm`) | PID (`start`) | 900s Total CPU | % of 1 core | `w[0..3]` (1s sum) | `ccx0[4..5]` (1s sum) | `ccx1[6..11]` (1s sum) | Sample share on `w[0..3]` |
|---|---|---|---:|---:|---:|---:|---:|---:|
| **1** | **`avahi-daemon`** | `907` (`812`) | **`8.000 s`** | **`0.889%`** | `2.570 s` | `1.390 s` | `4.040 s` | `276/860` (`32.1%`) |
| **2** | **`gnome-shell`** | `1624` (`1030`) | **`1.950 s`** | **`0.217%`** | `1.420 s` | `0.530 s` | **`0.000 s`** | `678/860` (`78.8%`) |
| 3 | `kworker/u48:2-dm_vblank_control_workqueue` | `137` (`60`) | `1.460 s` | `0.162%` | `0.720 s` | `0.240 s` | `0.500 s` | `414/860` (`48.1%`) |
| 4 | `irq/9-acpi` | `107` (`31`) | `1.180 s` | `0.131%` | `1.180 s` | `0.000 s` | `0.000 s` | `860/860` (`100.0%`, `cpu1`) |
| 5 | `rcu_preempt` | `15` (`23`) | `1.170 s` | `0.130%` | `0.090 s` | `0.170 s` | `0.910 s` | mostly CCX1 |
| 6 | `kworker/4:1-events` | `139` (`61`) | `1.000 s` | `0.111%` | `0.000 s` | `1.000 s` | `0.000 s` | `0%` (`cpu4`) |
| 7 | `kworker/5:3-events` | `2436` (`1525`) | `0.930 s` | `0.103%` | `0.000 s` | `0.930 s` | `0.000 s` | `0%` (`cpu5`) |
| 8 | `NetworkManager` | `966` (`819`) | `0.860 s` | `0.096%` | `0.630 s` | `0.200 s` | `0.030 s` | `612/860` (`71.2%`) |
| 9 | `irq/96-iwlwifi:default_queue` | `586` (`385`) | `0.650 s` | `0.072%` | `0.650 s` | `0.000 s` | `0.000 s` | `100%` (`cpu0`) |
| 10 | `systemd-oomd` | `841` (`466`) | `0.390 s` | `0.043%` | `0.080 s` | `0.220 s` | `0.090 s` | mixed |

**Notable non-contributors during this 900s window:**
- Periodic maintenance timers/daemons (`sysstat`/`sa1`/`sadc`, `fwupd`, `apt`, `dpkg`, `unattended-upgrades`, `updatedb`) recorded **`0.000 s`** of CPU in `qualification_telemetry.jsonl` during this run.
- Minor active desktop-session companions alongside `gnome-shell` (`1.950 s`) were `tracker-miner-f` (`0.130 s`), `dbus-daemon` (`0.120 s`), `gsd-sharing` (`0.090 s`), `snapd` (`0.060 s`), `xdg-desktop-por` (`0.030 s`), `gsd-housekeepin` (`0.020 s`), `evolution-alarm` (`0.010 s`), and `gjs` (`0.010 s`).

---

## 3. Role of `avahi-daemon`, `gnome-shell`, and Background Processes — Evidence vs. Hypotheses

To keep forensic conclusions strictly rigorous, directly verified findings are separated from unverified hypotheses below.

### 3.1 Directly Evidenced Causes (Proven by Telemetry, Guard Code, `ps`, `systemctl`, and `/etc/gdm3/custom.conf`)

1. **`avahi-daemon` (PID `907`, `start = 812`) is the #1 direct cause of the 93 failing windows — via both real continuous CPU load and `design-3` endpoint-CPU attribution:**
   - **Continuous background load:** `avahi-daemon` burned `8.000 s` in `900.09 s` (`0.889%` of 1 core continuously — **4.1× higher than the #2 process**), matching its steady post-boot consumption reported by `systemctl status avahi-daemon.service` (`25.092 s` over 47 minutes = `0.890%` of 1 core).
   - **Frequent migration onto worker cores `[0..3]`:** Across 860 snapshots, the kernel scheduled `avahi-daemon` on `cpu0` (96×), `cpu1` (6×), `cpu2` (164×), `cpu3` (10×) — i.e., **`32.1%` of samples** (`2.570 s` of direct 1s-step CPU on `[0..3]`, plus `1.390 s` on `[4..5]` and `4.040 s` on `[6..11]`).
   - **Exact mechanism inside frozen `design-3` (`g2_v2_design3_guard.py` lines 370–409):** `window_accounting()` computes each PID's net 10-second `dticks` and assigns **all** of that 10s `dticks` to `procs_workers_s` if the PID's `processor` at the **window endpoint** lies in `{0, 1, 2, 3}`. Whenever `avahi-daemon` (`0.07–0.16 s` per 10s window, mean `0.1196 s`) ended a 10s window on `cpu0..3` — which occurred in **`92 / 93` failing windows** (`cpu0: 32`, `cpu1: 2`, `cpu2: 54`, `cpu3: 4`) — `avahi-daemon` alone consumed **~50% (max `69.6%`) of the entire `0.209 s` (`0.01 × 2 × 10.47 s`) worker-core budget**.
   - **Socket & reverse-dependency coupling (verified via `systemctl`):** `avahi-daemon.service` has `TriggeredBy: avahi-daemon.socket` and is a reverse dependency of `cups-browsed.service`. Stopping `avahi-daemon.service` alone without stopping `avahi-daemon.socket` (and `cups-browsed.service`) risks immediate socket re-activation.

2. **`gnome-shell` (PID `1624`, `start = 1030`) proves the user's Ubuntu Wayland desktop session remained running throughout the entire 900s TTY qualification:**
   - **Why it remained running despite using TTY (`Ctrl+Alt+F3`):** `/etc/gdm3/custom.conf` explicitly sets:
     ```ini
     AutomaticLoginEnable=true
     AutomaticLogin=thinhbui
     ```
   - Live `ps` and `systemctl status gdm.service` confirm that `gdm.service` started at `15:18:25 +07` (`08:18:25 UTC`, 5 minutes before qualification), spawned `gdm-session-worker [pam/gdm-autologin]` (PID `1409`) → `gdm-wayland-session` (PID `1472`) → `/usr/bin/gnome-shell` (PID `1624`, `start = 1030` — the exact same PID and starttime logged in `qualification_telemetry.jsonl`), along with `gnome-shell-calendar-server`, `gjs`, `tracker-miner-f`, `gsd-sharing`, and `gsd-housekeepin`.
   - **Direct impact in telemetry:** `gnome-shell` spent **`100%` of its `1.950 s` CPU inside CCX0 `[0..5]`** (`1.420 s` on `w[0..3]`, `0.530 s` on `ccx0[4..5]`, `0.000 s` on `ccx1[6..11]`). It appeared in `86 / 93` failing 10s windows (mean `9.1%`, max `26.1%` of `foreign_workers_s`), directly caused the sole `CCX0 [0..5]` failure at Episode 2 (`0.02006 > 0.02000` with `0.08 s` on `cpu5`), and was the #1 tracked worker-core process (`0.04 s` on `cpu1`) in the sole conservation-LB failure at Episode 30 (`0.01008`).

3. **Kernel/network baseline floor is small and directly quantified:**
   - `irq/9-acpi` (`1.180 s`, always `cpu1`), `NetworkManager` (`0.860 s`, `71.2%` on `[0..3]`), `irq/96..99-iwlwifi` (`~0.65 s` default queue + minor queues on `[0..3]`), `kworker/u48:2-dm_vblank_control_workqueue` (`1.460 s`, `0.720 s` on `[0..3]`), and per-CPU `kworker` threads form a steady low-level floor well below `0.0100` on their own (`net_total_workers_fraction = 0.00449` even *with* `avahi-daemon` and `gnome-shell` included!).

### 3.2 Hypotheses (Plausible, NOT Directly Proven by Telemetry Alone)

| Hypothesis | Basis / Clues Observed | Why Not Proven Yet |
|---|---|---|
| **H1:** `avahi-daemon`'s steady `~0.89%` 1-core load is driven by LAN/Wi-Fi mDNS multicast traffic on `wlp*`. | `systemctl status` shows `avahi-daemon` joined mDNS multicast on `wlp*`; `iwlwifi` IRQs and `NetworkManager` were active continuously. | No packet capture (`tcpdump`/mDNS counter) was collected; could also include local mDNS clients or multicast chatter. |
| **H2:** Stopping `gdm.service` will also reduce `kworker/u48:2-dm_vblank_control_workqueue` (`1.460 s`, `0.720 s` on `[0..3]`). | `dm_vblank_control_workqueue` is part of the `amdgpu` display manager driven by display vblank interrupts while Wayland/GNOME holds DRM scanout. | Linux framebuffer console (`tty3`) can still maintain panel scanout; actual reduction must be observed in a clean rerun. |
| **H3:** `sysstat-collect.timer` (10-minute cadence) and `fwupd-refresh.timer` could fire during a future 900s run even though they did not register `> 0 s` here. | Both timers are `active (waiting)` and scheduled within minutes (`systemctl status`). | Did not impact the `08:23:44Z` run, so their exact 10s impact on `[0..3]` is untested here. |

---

## 4. Safe, Temporary, 100% Reversible Procedure to Reduce CPU Noise (For Owner Review)

> [!IMPORTANT]
> **Nothing below has been executed by the agent.** All commands use **`systemctl stop`** (temporary runtime stop only) — **never** `systemctl disable`, `systemctl mask`, `/etc/gdm3/custom.conf` edits, CPU governor/affinity/fan changes, or `design-3` edits. Either running the **Restore** block below or rebooting returns the machine to its exact prior state.

### Step 1 — Save work & switch to Linux text console (`tty3`)
1. Save and close open desktop applications first (stopping `gdm.service` cleanly terminates the graphical GNOME Wayland session).
2. Switch to a Linux text TTY with **`Ctrl+Alt+F3`** and log in as `thinhbui`.

### Step 2 — Temporarily stop the evidenced noise sources (from `tty3`)
Primary pair (directly evidenced to eliminate `93/93` failures analytically):
```bash
sudo systemctl stop gdm.service
sudo systemctl stop cups-browsed.service avahi-daemon.socket avahi-daemon.service
```

Optional defensive pause of periodic timers (prevents an unlucky 10-minute `sysstat` or `fwupd` trigger mid-run):
```bash
sudo systemctl stop sysstat-collect.timer fwupd-refresh.timer
```

### Step 3 — Verify clean stop BEFORE running qualification (read-only)
```bash
systemctl is-active gdm.service avahi-daemon.socket avahi-daemon.service cups-browsed.service sysstat-collect.timer fwupd-refresh.timer || true
pgrep -af 'avahi-daemon|gnome-shell|gdm3' || echo "CLEAN: no avahi/gnome-shell/gdm3 processes"
```
Expected result: all checked units report `inactive`, and `pgrep` prints `CLEAN: no avahi/gnome-shell/gdm3 processes`. *(Do NOT proceed if `avahi-daemon` or `gnome-shell` is still alive.)*

### Step 4 — Run one fresh 900s qualification under UNCHANGED frozen `design-3`
```bash
cd "/home/thinhbui/Documents/ChatGPT/Research ANN/task-d"
./scripts/run_g2_v2_design3_qualify.sh
```
- Writes a **new** timestamped immutable bundle under `../../../../artifact-evidence/axd-g2-v2-design3-qualification-<UTC>/` without touching `20261124T082344Z`.
- Does **not** execute ANN binaries, does **not** materialize `v2_test_10000.ids`, and uses the exact frozen `design-3` code and thresholds.

### Step 5 — Immediately restore all services after the 900s run completes
```bash
sudo systemctl start avahi-daemon.socket avahi-daemon.service cups-browsed.service sysstat-collect.timer fwupd-refresh.timer
sudo systemctl start gdm.service
systemctl is-active gdm.service avahi-daemon.socket avahi-daemon.service cups-browsed.service sysstat-collect.timer fwupd-refresh.timer
```
*(Because `AutomaticLoginEnable=true` was never altered, starting `gdm.service` immediately brings back the normal Ubuntu Desktop; alternatively, `sudo reboot` also restores 100% of defaults.)*

---

## 5. Assessment: Is a New Qualification Run Under Unchanged Frozen `design-3` Reasonable?

### 5.1 Analytical Counterfactual Replay (Zero Threshold Changes)

Replaying the exact `860` snapshots from `qualification_telemetry.jsonl` under **unchanged frozen `design-3`** thresholds (`worker-cores [0..3] <= 0.01`, `CCX0 [0..5] <= 0.02`, `host [0..11] <= 0.025`, `single <= 0.10`) while subtracting only the directly observed process contributions yields:

| Analytical Counterfactual (Exact Replay of `20261124T082344Z`) | Est. Remaining Failing 10s Windows | Est. Peak `worker-cores [0..3]` Fraction (Cap `0.01000`) |
|---|---:|---:|
| Baseline observed (with `avahi-daemon` + active GNOME session) | **`93 / 850`** | `0.01435` |
| Subtract `gnome-shell` only | `47 / 850` | `0.01289` |
| Subtract `avahi-daemon` only | **`1 / 850`** | `0.01008` |
| **Subtract `avahi-daemon` + `gnome-shell`** | **`0 / 850` (`100% PASS`)** | **`0.00816`** (`~18.4%` headroom below `0.01000`) |
| Subtract `avahi-daemon` + `gnome-shell` + desktop helpers (`pipewire`/`gsd`/`xdg`) | `0 / 850` (`100% PASS`) | `0.00816` |

### 5.2 Recommendation & Strict Stop Rule

- **Verdict on rerunning qualification under UNCHANGED frozen `design-3`: YES — HIGHLY REASONABLE AND SCIENTIFICALLY CLEAN.**
  1. **Zero scientific compromise:** Every frozen `design-3` threshold, attribution rule, and artifact remains untouched (`425c7483...`). Temporarily stopping `gdm.service` (which `AutomaticLoginEnable=true` kept running despite TTY login) and `avahi-daemon` (`mDNS` discovery daemon) is standard quiet-host hygiene — not post-hoc rule relaxation.
  2. **Strong empirical foundation:** Four of five `design-3` criteria already passed **100%** even *with* `avahi-daemon` and `gnome-shell` running (`15s` whole-host `845/845 PASS` with `max 0.01851 <= 0.025`; `single-proc 0 FAIL`; `hard guards 0 FAIL`; monitor overhead `1.56%` of 1 core). Analytically removing just `avahi-daemon` + `gnome-shell` eliminates **`93/93` failures** (`est_max_fw = 0.00816 <= 0.01000`).
  3. **Honest residual-risk disclosure:** `est_max_fw = 0.00816` leaves a real but modest `~0.00184` margin against `0.01000` on `[0..3]`. If `irq/9-acpi` (`cpu1`) + `NetworkManager` + `iwlwifi` IRQs (`cpu0`) + `kworker` happen to burst simultaneously on `[0..3]`, an occasional 10s window could still edge near `0.0100` (and conversely, if `H2` holds and `dm_vblank_control_workqueue` drops once `gdm.service` is stopped, headroom improves further).
- **Pre-committed Stop Rule for the rerun:**
  - **If the clean rerun passes (`qualification_pass = true`, `0` 10s/15s/hard failures):** record the bundle as `QUALIFICATION_PASS` for `design-3` and return to owner review before any `QUALITY_ONLY` approval.
  - **If the clean rerun STILL fails on `worker-cores [0..3]`** despite `gdm.service` and `avahi-daemon` being verified inactive: **keep `DESIGN3_HOLD`**, inspect the new residual culprit (e.g., `iwlwifi`/`NetworkManager` vs `dm_vblank`), and do **not** blindly repeat runs or silently relax thresholds.
