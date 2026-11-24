# A×D G2 v2 · Pre-approval remediation và re-audit

**Kết luận: `READY_FOR_OWNER_APPROVAL` — package design-2, chỉ p=2/S=16.**  
`EXPLORATORY_HOST_SPECIFIC` · protocol `AXD-G2-V2-3A-20261123` · ngày 23/11/2026.

F1/RAM, F2/CPU-contention và F3/runner-analyzer của [audit design-1](AXD_G2_V2_PRE_APPROVAL_AUDIT.md) đã được xử lý bằng executable contract, schema, version/content pins và dataset-free verification. Đây là trạng thái **sẵn sàng cho owner review/ký duyệt**, không phải quyền thực nghiệm hoặc kết luận hiệu năng. **Owner approval chưa có; quality v2 chưa chạy; G2 OFF vẫn NOT_OPEN.**

Không ANN benchmark, profiler, G2 OFF, test-panel/GT exposure, materialize/đổi split, retune beam432, build graph, i5-14600KF experiment, Google Sheets write hoặc commit. Chỉ bốn prereg v2 được cập nhật có giải thích; v1, Stage 5/6 và audit design-1 giữ nguyên.

## 1. Thay đổi và kết quả đóng blocker

| Finding | Remediation design-2 | Re-audit |
|---|---|---|
| **F1: per-process RAM bị che bởi mean** | Hard gate cho **mọi cặp**, cộng aggregate CI; pinned ELF HWM; invalid data fail-closed; dừng/HOLD và giữ raw | **PASS** |
| **F2: CPU utilization/contention chưa đủ định nghĩa** | /proc ticks/window/normalization; fixed affinity/profile; named jobs và aggregate foreign CPU; preflight/telemetry logs; no retry/drop | **PASS_SPEC_AND_FIXTURES** |
| **F3: chưa freeze runner/analyzer** | Code thực thi có owner authorization gate, separate plan command, schema, exact packages, binary/compiler/flags/native runtime pins, full argv plans | **PASS_PREPARATION** |
| **C1: 3% geometric vs arithmetic** | Giữ geometric paired estimator làm primary duy nhất; arithmetic means và T(Q) tách rõ | **PASS** |
| **C2: worker strata confounding** | **P2-only**; p1/p4 không được hỗ trợ hoặc cấp quyền bởi package này | **CLOSED_BY_SCOPE**, không phải đã đo/giải quyết scaling thực nghiệm |
| **C3: Markdown table** | Sửa header absolute gap, không đổi số liệu | **PASS** |
| **C4: power/cost assumptions** | Giữ cảnh báo underpower, nominal/model-based CIs, host/graph limits và budget chưa đo | **DISCLOSED**, không giả định đã được kiểm chứng |

Phạm vi p2-only là quyết định thiết kế cụ thể để đóng C2. Nếu muốn p1/p4 cần extension prereg riêng, cân bằng worker order và quality/calibration riêng trước dữ liệu extension; không bật bằng một flag sau khi thấy p2.

## 2. RAM: hard acceptance khác aggregate uncertainty

Nguồn duy nhất cho primary RAM là `p2_eval_summary.vm_hwm_kib`: **integer KiB dương** do frozen ELF capture sau search/output serialization, trước final summary/exit. Wrapper polling RSS chỉ diagnostic; không đổi nguồn cho kết quả thuận lợi. Đây là reported process high-water đến capture, không phải RAM riêng lõi search hoặc kernel-enforced allocation cap.

Với cùng graph/block, B=baseline HWM, C=B1+A1 HWM:

`C−B ≤ max(65536 KiB,0.10B)`.

So sánh hard gate bằng integer: **`10(C−B) ≤ max(655360,B)`**. Equality PASS; vượt dù 1 KiB không PASS. Mọi cặp phải đạt. Aggregate normalized mean/CI qua 12 block là điều kiện bổ sung; không thể thay hard gate. Không cộng 144 RSS tuần tự thành peak memory đồng thời; host MemAvailable/swap guard là tầng bảo vệ riêng.

- Missing/zero/negative/nonfinite/fractional HWM: **INVALID**, dừng campaign, giữ raw và HOLD; không thay bằng zero hoặc wrapper fallback.
- Hard RAM exceedance là dữ liệu regression được giữ: **HOLD_RAM**, dừng sau khi cặp đủ. Nếu opt chạy trước base, relative cap chỉ quyết định được sau base; live absolute RAM guard vẫn áp trong lúc chạy.
- Thiếu bất kỳ process/cặp nào không được tính GO bằng số repeat còn lại, không impute hoặc chạy bù.

Fixture tái hiện phản ví dụ audit `v=[2,0,…,0]`: aggregate upper bound≈0.73947 vẫn dưới1, nhưng hard gate nay FAIL. Các biên 64MiB,10%, equality,+1KiB và invalid fields đều được kiểm.

## 3. CPU, affinity, contention và abort

Owned CPU time dùng `/proc/<pid>/stat` utime+stime/CLK_TCK, kiểm PID/start_ticks. Window **first-to-last alive samples**, gồm một phần load/warmup/output; không gọi là CPU time thuần search. CPU%=100ΔCPU_s/Δwall_s; capacity%=CPU%/2; có thể vượt100% và không clamp. Không cộng process aggregate với thread counters lần nữa; monitor CPU được tách. Nguồn units được đối chiếu với [Linux proc_pid_stat](https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html).

Profile đã khóa để owner duyệt: Ryzen5 PRO4650U, worker CPUs **[0,2]**, core IDs0/1, sibling lists0-1/2-3, cùng L3 list0-5; inherited parent/monitor allowed mask0..11; Linux kernel7.0.0-43-generic, CLK_TCK100. Frozen evaluator pin worker threads; mỗi summary requested=observed=[0,2]. Wrapper **không sửa global/parent affinity, fan, power hoặc security**. Mismatch phải HOLD, không tự tune host để ép PASS.

Cadence1Hz; valid interval0.5–2s, observation window≥5s. Missing/reset/PID reuse/gap>2s hoặc window thiếu: INVALID/ABORT. Trước mỗi process có ≥5s quiet preflight, lưu toàn bộ JSONL kể cả khi fail. CPU/profile/sensor/AC actual readiness **chưa được đo ở task này**, chỉ kiểm bằng fixtures/static source.

Foreign work lấy host busy ticks từ `/proc/stat`, trừ owned+monitor CPU, không double-count guest, không tính idle/iowait; phần dư âm do rounding được clamp0. Named CPU/ANN job bị chặn ngay. Unknown-name sustained job vẫn bị chặn khi rolling ≥5s:

**`foreign_busy_seconds / (wall_seconds×2) >0.01`**.

1% capacity là **engineering noise budget bằng1/3 minimum effect3%**, được đề xuất trước dữ liệu; không phải threshold empirical hoặc bảo đảm latency noise≤1%. Owner phải nhận tính bảo thủ/false HOLD có thể cao và xác nhận không có CPU-heavy benchmark khác. Không dò threshold từ quiet samples/test để lấy PASS. Không có detector bảo đảm nhận diện mọi transient workload; raw/CI uncertainty vẫn cần báo.

MemAvailable>1GiB, disk>20GiB, swap growth>64MiB trong≥10s, AC available/unchanged, start Tctl<85°C, abort≥95°C/critical trip và watchdog được giữ. Initial disk mỗi phase phải >25GiB =floor20+reserve5; không nới guard. Timeout≤180s/process và phase quota được kiểm cả trong preflight/run/postchecks. Chỉ start-temperature có cooldown≤180s; contention không tự retry.

**Không loại bỏ raw lượt đo:** contention/invalid/guard/timeout/quota giữ logs/partial outputs, ghi HOLD với process đang xét và dừng toàn campaign. Run chậm nhưng hợp lệ vẫn giữ trong phân tích. Không kill process ngoài owned group, lọc outlier, đổi order hoặc thêm repeat. Analyzer cũng từ chối campaign/quality phase có HOLD hoặc thiếu completion/receipts.

## 4. Primary estimand và điều kiện 3%

Giữ nguyên định nghĩa đã công bố ở design-1 và làm rõ nhãn:

`x_gb=log(mean_base_gb/mean_opt_gb)`; `x_b=mean_six_graphs(x_gb)`; `x̄=mean_12_blocks(x_b)`.

**Primary:** geometric speedup `exp(x̄)`, reduction `1−exp(−x̄)`. Mỗi process trước tiên tính **arithmetic mean latency theo query**; không lấy geometric mean của individual query latencies. CI95 chính là t-CI trên 12 block log-effects, df11. GO cần cận dưới CI12, adjacent-block CI6 và joint query×process bootstrap vượt **θ=−log(.97)**, cùng stability/tail/RAM gates.

**Arithmetic cohort latency** là mean đồng trọng số process/graph; `1−mean(opt)/mean(base)` báo riêng. Đây không phải primary 3% và không được đổi vai sau kết quả. T(Q) và saved seconds dùng arithmetic means; source/reference BUILD receipts cố định, conditional CI, không population-root BUILD CI. Numerical strict comparisons có tie rule bảo thủ1e-12 trên scale đang xét; equality/near equality giữ HOLD. Fixture đúng3% không thành GO/PIVOT do floating-point roundoff.

Ngưỡng3%, floor.990, equivalence±.0005, p95+5%, p99+10% và RAM budget không được retune. Tail gates là CI của typical process quantile ratios; raw max từng process được báo, không tuyên bố worst-process tail SLA. Root independence chưa xác minh; query reuse/validation post-selection, m12/power và nominal CI assumptions vẫn tồn tại.

## 5. Package freeze và exact plans

[Freeze manifest](../../../configs/axd_g2_v2_freeze.json) SHA-256:

**`91186d57e5992e1df70f86a55ba928ad4d6613bb0b67ccbee0f485cc380d1749`**.

Manifest khóa22 component files, schema, dependency lock, bốn prereg và stable helper dependencies. Source identity không giả mạo commit:

- Search source: **f2cd634b837a70735c3e31e5956f0524bfc26675**; ELF vẫn **7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1**.
- Repository base: **f54b1bb653652dd13e760cc00c9fb46d0e643c1c**; wrappers mới là **uncommitted overlay với content SHA**, không tự commit.
- GCC13.3.0 frontend SHA **1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769**; compile flags `-O3 -DNDEBUG -std=c++17 -Wall -Wextra -Wpedantic -Werror`; link `-O3 -DNDEBUG`. Recovered CMake flags phù hợp frozen source/ELF .comment; **không rebuild hoặc claim bit-reproduction**.
- Python3.12.3 và executable SHA; bảy packages exact +wheel hashes trong [requirements-g2-v2.lock](../../../requirements-g2-v2.lock): numpy2.5.5, jsonschema4.26.0 và năm transitive packages. Năm native runtime libraries có byte pins; kiểm lại sau authorization. LD_PRELOAD/LD_LIBRARY_PATH/LD_AUDIT bị từ chối, không silent dependency substitution.
- [Output schema](../../../configs/axd_g2_v2.schema.json): **axd_g2_v2.2**, 10 definitions cho task/plan/artifacts/approval/start/process/quality/complete/HOLD/analysis; own outputs được validate, nonfinite JSON không được chấp nhận.

| Component | SHA-256 |
|---|---|
| [Runner](../../../research/task_da/g2_v2_runner.py) | `d1de7a0c1a02e6bcbdc8e651dc7d2b71fb8f5f531362e380e86d8bd6f03eab24` |
| [Analyzer](../../../research/task_da/g2_v2_analyzer.py) | `97178bbab33844bf6eda2ed7e22f3d57be471bcd671c62f665078cc72a39bb64` |
| [Guard extension](../../../research/task_da/g2_v2_guard.py) | `86ce14eda8de96889d97828f7281504b6afb4dd1bfb8c9e530b108be1d1298a2` |
| [Contract](../../../research/task_da/g2_v2_contract.py) | `565f7c3cc4ab5eb45044f2fc95f0fa8078e0329384182d77c9926e2e64778994` |

Frozen base guard SHA232ed904… và existing helpers không bị sửa; extension mới áp AMD/CPU rules và tái sử dụng owned-process/watchdog termination. Exact Python environment và compiler/native identity được ghi trong [evidence directory](../../../.local/artifacts/axd-g2-v2-remediation-20261123-a3df2che/).

Hai **final** command plans, chỉ là JSON metadata, chưa thực thi:

- [quality_plan_final.json](../../../.local/artifacts/axd-g2-v2-remediation-20261123-a3df2che/quality_plan_final.json): 6 opt validation ON432 +12 test ON =18 process dự kiến.
- [off_plan_final.json](../../../.local/artifacts/axd-g2-v2-remediation-20261123-a3df2che/off_plan_final.json): 12×6×2=144 OFF dự kiến; mỗi graph có một AB và BA tại mỗi vị trí, tổng6/6; toàn10k và100 validation warmup/process.

Plans có full argv, proposed absolute artifact/output paths và freeze/artifact-map hashes. Planner không đọc ANN inputs hoặc tạo split/output campaign. Proposed test-ID path vẫn chưa tồn tại. Initial plans/freeze candidates trong evidence là lịch sử chuẩn bị; **chỉ `_final` plans và freeze SHA ở trên là package đưa duyệt**.

[Approval template](../../../configs/axd_g2_v2_approval.UNAPPROVED.json) cố ý invalid: owner/date trống, scope UNAPPROVED, quiet-host=false. Runner từ chối. Owner phải copy template thành receipt mới **ngoài frozen package**, ký scope/path/hashes/quota cụ thể; không sửa template in-place. Quality-only authorization không cấp OFF; OFF cần actual quality completion/parity/floor, B equivalence nếu scope OFF_AB và approval riêng. A-only không được tự xuất B system GO dù B quality tình cờ đạt.

## 6. Dataset-free verification và re-audit

Môi trường tạm đã giải quyết dependency failures ở task trước được dùng lại; không sửa `.venv` cũ hoặc Python hệ thống. Chạy đầy đủ:

```sh
env -u TASK_DA_SMOKE -u TASK_DA_P1_EVAL -u TASK_DA_P2_EVAL \
    -u TASK_DA_PHASE_EVAL -u TASK_DA_P2_TRACE_EVAL \
    /tmp/axd-g2-v2-preapproval-20261123-ge85t3xl/venv/bin/python \
    -m unittest discover -s tests/research -v
```

**551 tests, 537 executed PASS, 14 native opt-in skipped, 0 errors/failures.** Không thêm skip decorators hoặc bỏ failing tests. [Final suite log](../../../.local/artifacts/axd-g2-v2-remediation-20261123-a3df2che/verification-suite.log); intermediate implementation/fixture test logs cũng giữ trong evidence, không phải ANN measurements.

[30 remediation checks](../../../tests/research/test_g2_v2.py) bao gồm hard RAM counterexample/boundaries/invalids; CPU ticks vs monitor, >100% utilization, noise boundary, unknown/named competitors, PID/counter/gap errors; AMD/resource guard inheritance; logged quiet preflight; balanced argv; owner scope/template/component/native dependency tamper; incomplete campaign rejection; exact IDs/double digest/counter invariants; separate floor/equivalence; weighted percentiles khớp explicit samples; deterministic paired bootstrap; production10k resamples trên tensor tổng hợp; 3% boundary HOLD; schema và BUILD–SEARCH arithmetic fixtures. Không native evaluator/benchmark/profiler được gọi.

Đã chạy lại [re_audit.py](../../../.local/artifacts/axd-g2-v2-remediation-20261123-a3df2che/re_audit.py), kết quả [re_audit.json](../../../.local/artifacts/axd-g2-v2-remediation-20261123-a3df2che/re_audit.json): **READY_FOR_OWNER_APPROVAL**. Re-audit kiểm component/env/plan/schema/unsigned-approval rejection, hard RAM counterexample, preserved files, source/binary/runtime pins và tests; không mở ANN/test artifacts. Không gọi đây là peer review từ agent/người thứ hai hoặc hardware qualification.

**Preservation:** 96 protected files ngoài bốn prereg v2 không đổi, gồm **92 research docs**. V1 SHA `cb6433cb2c04108653cca7e8d63ed9688f3b19fa68a0b236acccc28d766393eb` và Stage5/6 decisions giữ nguyên. Audit design-1 và 10 payload trong bundle của nó còn nguyên. Bản design-1 của bốn prereg được lưu nguyên bytes trong evidence mới; old/new SHA nằm trong re_audit.json. Không commit, không staged changes.

Sáu BUILD receipts +sáu `.time` logs được **đọc từ đúng Task A commit f5e48bb…** và lưu thành bản sao mới; cả12 SHA khớp pins trong transfer/receipts. Không chạy lại BUILD. [Compact BUILD reference](../../../configs/axd_g2_v2_build_reference.json) giữ wall times Stock42.57/41.99/42.21 và Fast33.84/33.74/33.80s, graph bytes/ELF/receipt identities. Chúng vẫn là bằng chứng lịch sử host A; không phải BUILD trên Ryzen D. Raw mới ở ignored evidence directory, không chèn vào historical bundles.

## 7. Giới hạn còn lại và owner checklist

Các unknown sau là điều kiện bước thực nghiệm kế tiếp, **không được giả vờ PASS ở preparation**: actual Ryzen/profile/sensors/AC/quiet feasibility, v2 validation-opt/test quality và parity tại432, OFF latency/tails/RAM, process variance/dependence, CI coverage, all-gates power, cost bootstrap trên nonconstant ANN tails. m12/N10k không bảo đảm80% power mọi effect. CPU1% feasibility/noise bound chưa được chứng minh. Runtime/budget dự trù p2 2,5–3,5h thu thập +0,5–2h hậu kỳ vẫn là planning, không phải Search result.

Public100K/Task A và test90k/R86/P1 reuse, post-v1 redesign, reused validation, một host và root independence NOT_VERIFIED vẫn giữ nhãn EXPLORATORY_HOST_SPECIFIC; population graph CI NOT_ESTIMABLE. Không chuyển thành fresh independent holdout. Threshold3% là engineering choice cần owner nhận, không SLA hoặc evidence novelty.

| Quyết định | State sau remediation |
|---|---|
| READY_FOR_OWNER_APPROVAL | **Đạt về package preparation design-2 p2-only** |
| Owner design/quality authorization | **Chưa có**, cần ký scope/hashes/profile/budget |
| Quality gate A/B v2 | NOT_RUN, không giả định PASS |
| G2 OFF / GO_RESEARCH | NOT_OPEN / chưa đánh giá |
| PIVOT nghiên cứu | Chưa có cơ sở OFF mới; không suy từ code/fixtures |

- [x] F1/F2/F3 closed bằng code/schema/pins và dataset-free tests; C1/C3 sửa rõ; C2 khóa p2-only; C4 công bố giới hạn.
- [x] Beam432, panel SHA/order, six-graph cohort, p2/S16/K10/jobs1/entry0 và m12 không retune.
- [x] Bốn prereg design-2, source/package/checksums và exact command plans reviewable; historical v1/Stage5/6 giữ nguyên.
- [ ] Owner nhận các unknown/power/noise/host limits và ký **QUALITY_ONLY** cho đúng freeze/artifact-map/output/quota3600s; không gồm OFF hoặc p1/p4.
- [ ] Sau actual quality report, owner review A/B/parity/provenance/guard/completion và ký OFF_A hoặc OFF_AB riêng, quota10800s, external output đủ disk; không có auto-approval.

Kiểm checksum từ repository root: `sha256sum -c docs/research/task-da/AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256`. [Checksum file](AXD_G2_V2_PRE_APPROVAL_REMEDIATION.sha256) khóa report, freeze và component files; [evidence BUNDLE](../../../.local/artifacts/axd-g2-v2-remediation-20261123-a3df2che/BUNDLE.sha256) khóa logs/snapshots/raw receipt copies riêng. Bundle ignored cần được bàn giao riêng khi review ở máy khác; dataset-free tests không phụ thuộc private ANN artifacts.

**READY_FOR_OWNER_APPROVAL**
