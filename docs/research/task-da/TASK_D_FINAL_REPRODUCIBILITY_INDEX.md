# Task D · Chỉ mục tái lập và biên bản freeze

**Mốc dữ liệu 20/11/2026.** Có thể kiểm tra các checksum, tính lại quyết định validity và tra lại interaction H1 bằng Python chuẩn trên bản lưu của owner. Raw nằm ngoài Git. Chạy các khối lệnh dưới đây từ **thư mục gốc checkout Task D**, với Python 3.11+ và các thư mục sibling `../artifact-evidence/`, `../source-evidence/` như trong bàn giao. Mọi lệnh ở mục 3 chỉ đọc evidence gốc. Bản sao phân tích dùng thư mục tạm mới.

## 1. Trạng thái đã khóa

| Đối tượng | Định danh / kiểm tra |
|---|---|
| Branch khi bàn giao | `research/task-da-pivot-b1-a1-20261119`. Trước freeze chỉ có các tệp untracked. Tracked source diff và staged diff rỗng |
| Stage D/E | Tag `task-da-p2-stage-de-freeze-20261119` peel về `87d4a8149416b22ccf8854f72c7c72f09197cfa3`. Binary Stage D SHA-256 `ff46d6ac8895d519054548575c3187544716c0fdf2bbdad83db8a0a8cc7f8759` |
| B1+A1 | Tag `task-da-b1-a1-pilot-freeze-20261119` peel về `f2cd634b837a70735c3e31e5956f0524bfc26675`. Frozen OFF SHA-256 `7a2685e5760b1e03c040684b3144a7f454086761e2d25ff147d11d33df8727d1`. Narrow plan `5744207`, report `40bb7c5` |
| H3 screening | Feasibility docs `1d38389`, trace/tools/NO-GO `6bdf65f`. Trace Release SHA-256 `4903d4262876eb928b4a61c5461d306bdfd94337b830505d4a9f75c8c094887c` |
| Final validity | Hai tiền đề ở `32160b6`. Freeze riêng **`467f03021139af3d4facb46bd26d4e7c90ca8324`** chứa hai báo cáo final, ba observer/analysis tools và một synthetic contract. Bốn tệp Python khớp từng byte với archived source. Observer ELF SHA-256 `3e59c909c4f70d1f2a4ad18e986c275754c00d5aacac5de941b9bfd76b295f67` |
| Hồ sơ B1 có sẵn | Freeze riêng `8223d4af4044bd62852644984e971258e0015e9e`. SHA của review ngày 19/11 là `59b8774fa17de6c34010d13d95fdb602b10e053f5dd06dffb176e1c3bb565920`, prereg R4/R5 là `ab06155c90a3daab175bac804922a2e95479716afca2deea2a844bf9e4aca205`. Prereg ở trạng thái chờ |
| Package và proposal | Manifest V3 SHA-256 `9094fb348269918077b37e901b887eae7ac1662c74a45aa43a237cd227e57d16` chứa định danh graph, base/query/GT và builder. DOCX gốc `a7aef4ba2ed867ed8799f72baec463ab5bd59c6fbdd190327d38b6953b260b45`. [V3](experiment_manifest_v3_reconciled.json) · [DOCX](../../../../source-evidence/TASK_D_A_GRAPH_TOPOLOGY_PARALLEL_TRAVERSAL_PROPOSAL_20261115.docx) |

**Kiểm tra bản lưu.** Thư mục bền vững `../artifact-evidence/task-d-final-measurement-validity-20261120/` chứa 74 payload và một manifest. Digest của manifest bằng giá trị đã công bố ở final audit. Danh sách đường dẫn tương đối và digest của **tất cả 74 payload** trong `/tmp/task-d-final-measurement-20261120` khớp bản bền vững. Vì bản sao đã hoàn chỉnh, lượt freeze này chỉ đọc và kiểm, không cần copy lại. Các absolute path và đường dẫn tương đối theo vị trí capture trong receipts vẫn mô tả nơi chạy ban đầu. Dùng cây thư mục bền vững và source trong checkout khi phân tích trên máy hiện tại. [Manifest](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/CHECKSUMS.sha256) · [Identity lúc capture](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/final_identities.json)

## 2. Tra từ kết luận về raw

| Câu hỏi | Điểm vào và cách truy sâu |
|---|---|
| Proposal, P0, P1 | [Đề xuất có thể đọc dạng text](../../../../source-evidence/proposal_drive_extract.txt), [provenance reconciliation](P0_P1_FINAL_RECONCILIATION_REPORT.md), [P1 calibration matrix](P1_CALIBRATION_MATRIX.csv) và [P1 sealed test records](../../../../artifact-evidence/p1-full-validation-20261117T225717+0700/EVIDENCE_CHECKSUMS.csv). Matrix ghi SHA JSONL cho từng graph/beam |
| H1/H2 pilot và Stage D/E | [Pilot OFF](../../../../artifact-evidence/p2-exploratory-0990-20261118/pilot_r1/h1_off_summary.json), [pilot ON](../../../../artifact-evidence/p2-exploratory-0990-20261118/pilot_r1/h2_on_summary.json), [45 validation points](../../../../artifact-evidence/p2-followup-20261118/stage_d_val10k_r2_r3/stage_d_val10k_45cells_manifest.json), [63 ô Stage D](../../../../artifact-evidence/p2-followup-20261118/stage_d_replication/stage_d_replication_summary.json). [Budget JSON](../../../../artifact-evidence/task-d-latency-audit-20261120/budget.json) liệt kê process summary ON/OFF theo ô, mỗi process có result JSONL |
| B1+A1 | [Pilot R1](B1_A1_PILOT_HANDOFF_20261119.md), [narrow raw bundle](../../../../artifact-evidence/p2-b1-a1-narrow-20261119/BUNDLE.sha256), [process latency](../../../../artifact-evidence/p2-b1-a1-narrow-analysis-20261119/process_latency.csv), [quality](../../../../artifact-evidence/p2-b1-a1-narrow-analysis-20261119/quality.csv), [CI và ablations](../../../../artifact-evidence/p2-b1-a1-narrow-analysis-20261119/analysis.json). So theo graph và block. R1 có hai đối chứng pilot riêng |
| Negative H3 | [Panel đã khóa](../../../../artifact-evidence/h3-overlap-screening-20261120/preregistered.json), [capture parity](../../../../artifact-evidence/h3-overlap-screening-20261120/capture_checks.json), [R1 trace thực](../../../../artifact-evidence/h3-overlap-screening-20261120/A3_r1/trace_on/beam_970_p2_ON.jsonl), [per-query assignment proxy](../../../../artifact-evidence/h3-overlap-screening-20261120/offline_analysis/query_metrics.csv), [cost/quality](../../../../artifact-evidence/h3-overlap-screening-20261120/offline_analysis/cost_quality.json). Giữ thứ tự 32 development / 32 held. Hai graph còn lại dùng beam 986, 966 |
| Final audit | [Thứ tự và tiêu chí trước đo](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/preregistered.json), [6 process và mapping đến raw](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/capture_checks.json), [build/flags](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/observer/build_identity.json), [analysis JSON](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/analysis.json), [perf permission probe](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/profiler_permission_probe.json). Từng thư mục process có argv, PID, guard, host samples và per-query results |
| Kiểm thử tại mốc đo | [Dataset-free log](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/unittest.log) có 521 tests, 507 pass, 14 skip. [Native synthetic observer](../../../../artifact-evidence/task-d-final-measurement-validity-20261120/observer_synthetic_tests.log) pass 1/1. Đây là log tại thời điểm freeze |

## 3. Lệnh kiểm lại đã chạy trong lượt bàn giao

**Kiểm tra manifest và payload.** Chín bundle từ H1 đến final audit có 4.075 entry. Thêm 9 entry của P0 reconciliation và 261 entry P1, tổng là **4.345 entry trong 11 manifest**. Số đếm có thể gồm các tệp được giữ ở nhiều tầng evidence. Kiểm tra riêng 23 input/tool pins của narrow study trên máy có package. Dùng Python chạy ở chế độ bình thường, không bật `-O`.

~~~bash
python3 - <<'PY'
import csv, hashlib, json
from pathlib import Path

root = Path("../artifact-evidence")
def digest(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

# folder / manifest / manifest SHA256
pins = """
p0-p1-final-reconciliation-20261117T223637+0700 EVIDENCE_CHECKSUMS.csv 37b81ce490b69fb5c66f3739092b5c56be5cb18a63c6c959c6a2678e054d6f63
p1-full-validation-20261117T225717+0700 EVIDENCE_CHECKSUMS.csv ef0236f0ef50bcdbba1f0e299468845bb8a1c46615c89c1d4ab62d8c7880b66a
p2-exploratory-0990-20261118 EVIDENCE_CHECKSUMS.csv 8b4ae99ae0424540be1b606f50138be4279d71f1539a176b223b9d0fb77528b8
p2-followup-20261118 EVIDENCE_CHECKSUMS.csv 4e3298e92352e4718b729024d41ab48fbd7a7503770ee24231bfdf3a5e2480eb
p2-pivot-b1-a1-20261119 EVIDENCE_CHECKSUMS.csv eda452166aa05eb6bd3934e45f2aaf6aecfb57122ff54d3f9340b2b99c725067
p2-pivot-b1-a1-resume-20261119 BUNDLE.sha256 1c0df3150aafaf5fae6aee26018a6309201e0376e41ccb016c380e3ed6c1c173
p2-b1-a1-narrow-20261119 BUNDLE.sha256 2b6677895dce4a274fd288f71e31e57b3051313e19b05f8cd12ce7022fae4ffe
p2-b1-a1-narrow-analysis-20261119 CHECKSUMS.sha256 483804c96aefbe954693f615537aaebe8d059d59f4790ff8ae5f808331e52fb8
h3-overlap-screening-20261120 BUNDLE.sha256 fb6b1c81dee38ed78eb5de23f589668638097faf60e4d395f6e6cc5f67ac8f15
task-d-latency-audit-20261120 CHECKSUMS.sha256 003a3ad68f287904c23ac8254f7deac86cff2696c65fa66fc408efcadbb7d685
task-d-final-measurement-validity-20261120 CHECKSUMS.sha256 1af5626e530bf0bd37e4977c3dae18b1e0860f3c29d1205dce4679e95694098f
"""
assert __debug__
total = 0
for line in pins.strip().splitlines():
    folder, name, expected = line.split()
    manifest = root / folder / name
    assert digest(manifest) == expected, manifest
    if name.endswith(".csv"):
        with manifest.open() as f:
            entries = [(r["sha256"], r["relative_path"]) for r in csv.DictReader(f)]
    else:
        entries = [line.split(None, 1) for line in manifest.read_text().splitlines() if line]
    for expected_hash, rel in entries:
        path = manifest.parent / rel.lstrip("*")
        assert digest(path) == expected_hash, path
    total += len(entries)
assert total == 4345
narrow = root / "p2-b1-a1-narrow-20261119"
files = json.loads((narrow / "frozen.json").read_text())["files_sha256"]
assert len(files) == 23
for rel, pin in files.items():
    assert digest(narrow / rel) == pin, rel
print(total, "manifest entries,", len(files), "narrow pins OK")
PY
~~~

**Tính lại final validity từ sáu raw processes.** Analyzer ghi derived JSON/CSV vào thư mục truyền vào, đồng thời đọc historical H3 modes qua đường dẫn sibling của repo. Lệnh sau chỉ cho analyzer ghi vào một thư mục tạm mới. Kết quả mong đợi là hai phép so sánh byte thành công và trạng thái `NOT_VALIDATED_OUTSIDE_EQUIVALENCE_BUDGET`.

~~~bash
set -eu
audit=../artifact-evidence/task-d-final-measurement-validity-20261120
replay=$(mktemp -d)
cp -r "$audit/runs" "$audit/capture_checks.json" "$replay/"
python3 research/task_da/analyze_measurement_validity.py "$replay" > "$replay/replay.log"
cmp "$replay/analysis.json" "$audit/analysis.json"
cmp "$replay/query_summary.csv" "$audit/query_summary.csv"
python3 -c 'import json, sys; a=json.load(open(sys.argv[1])); print(a["observed_off_mean_ns"], a["observer_CI95_pct"], a["observer_gate"])' "$replay/analysis.json"
~~~

**Tái tính H1 theo đúng log-interaction của đề xuất.** Mỗi tỷ số p1/p đã dùng mean của 5 process trong cùng build. Ba dòng xuất ra là ba đối chứng khác nhau ở mục 4 của bản thảo.

~~~bash
python3 - <<'PY'
import json, math, statistics
from pathlib import Path
p = Path("../artifact-evidence/p2-followup-20261118/stage_d_replication/stage_d_replication_summary.json")
cells = json.loads(p.read_text())["cells"]
for a0_config, a3_config in [("p2_S16_flat","p2_S16_flat"), ("p4_S8_flat","p4_S16_flat"), ("p4_S16_flat","p4_S16_flat")]:
    deltas = []
    for r in (1, 2, 3):
        a0 = cells[f"A0_r{r}_{a0_config}"]["ratio_of_agg_means"]
        a3 = cells[f"A3_r{r}_{a3_config}"]["ratio_of_agg_means"]
        deltas.append(math.log(a0 / a3))
    print(a0_config, a3_config, round(statistics.mean(deltas), 4))
PY
~~~

## 4. Phạm vi tái lập và vấn đề còn mở

Replay khôi phục đúng số đã xuất từ raw hiện có. Tái lập phép đo native còn cần đúng graph/vector package, binary, hardware, guard và quyền sử dụng dữ liệu. Git chỉ chứa công cụ và tài liệu. Một checkout độc lập thiếu artifact sibling sẽ không mở được các liên kết raw. Những lệnh capture trong receipts ghi lại dòng lệnh lịch sử. Lượt bàn giao chỉ kiểm checksum và tái tính offline.

Owner và giảng viên cần chọn phạm vi case study và mục tiêu nghiệm thu. Nếu yêu cầu generalization, cần thống nhất baseline tác giả, workload và cách bảo đảm matched Recall. Với independent-root replication, Task A cần xác nhận đầy đủ dependency, ISA/build semantics và seed contract. P4 attribution còn thiếu phép đo hợp lệ trên OFF. Đây là các vấn đề mở. [Brief quyết định](TASK_D_SUPERVISOR_DECISION_BRIEF_VI.md) · [Feasibility R4/R5](TASK_A_R4_R5_FEASIBILITY_REVIEW.md)
