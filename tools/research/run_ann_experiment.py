#!/usr/bin/env python3
"""P0 external-process experiment harness. Local artifacts are authoritative."""

import argparse
import csv
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import time
import uuid

REPO = Path(__file__).resolve().parents[2]
METRICS = ("qps", "recall", "mean_latency_us", "p50_latency_us",
           "p95_latency_us", "p99_latency_us", "p999_latency_us", "mean_hops", "mean_ios")
QUERY_COLUMNS = ("schema_version", "run_id", "query_id", "latency_us", "hops",
                 "ios", "recall", "trace_mode")
SYSTEM_COLUMNS = ("schema_version", "run_id", "collector", "sample_time_local",
                  "entity", "metric", "value", "unit")
V1_INDEX_COLUMNS = ("run_id", "timestamp_start", "timestamp_end", "git_commit",
                 "git_dirty", "dataset_id", "index_id", "threads", "wcap", "k",
                 "l_search", "mem_l", "trace_mode", "repetition", *METRICS,
                 "wall_time_s", "exit_code", "run_status", "mlflow_status", "mlflow_run_id")
PROVENANCE_COLUMNS = tuple(f"{namespace}_{field}" for namespace in ("harness", "subject")
                           for field in ("repo_root", "repo_remote", "git_commit", "git_branch", "git_dirty"))
PROFILE_COLUMNS = ("benchmark_profile", "benchmark_profile_version", "parser_version",
                   "printed_latency_percentile")
INDEX_COLUMNS = (*V1_INDEX_COLUMNS, *PROFILE_COLUMNS, *PROVENANCE_COLUMNS)

# Source-audited contracts; the shared output label cannot identify its percentile.
BENCHMARK_PROFILES = {
    "legacy-research": {
        "version": "legacy-research/v1", "parser_version": "search-table/v1",
        "neighbor_types": None, "percentile": 0.999, "latency_metric": "p999_latency_us",
        "memory_suffixes": ("_mem.index", "_mem.index.data", "_mem.index.tags"),
        "argv_fields": ("data_type", "index_prefix", "threads", "wcap", "query", "ground_truth",
                        "k", "distance_metric", "search_mode", "mem_l", "l_search"),
    },
    "pipeann-b9ec4ba": {
        "version": "pipeann-b9ec4ba/v1", "parser_version": "search-table/v1",
        "neighbor_types": ("pq", "rabitq", "rabitq3", "rabitq4", "rabitq5", "dummy"),
        "percentile": 0.99, "latency_metric": "p99_latency_us",
        "memory_suffixes": ("_mem.index",),  # Upstream loads vectors/graph from this disk-format file.
        "argv_fields": ("data_type", "index_prefix", "threads", "wcap", "query", "ground_truth",
                        "k", "distance_metric", "neighbor_type", "search_mode", "mem_l", "l_search"),
    },
}


def profile_metadata(name):
    profile = BENCHMARK_PROFILES[name]
    return {"benchmark_profile": name, "benchmark_profile_version": profile["version"],
            "parser_version": profile["parser_version"],
            "printed_latency_percentile": profile["percentile"]}


def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_json(path, value):
    """Replace only this run's owned metadata; never replace a run directory."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_id(dataset, threads, wcap, trace_mode, repetition):
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", dataset)[:40]
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"P0_{safe}_T{threads}_W{wcap}_{trace_mode}_R{repetition:03d}_{timestamp}_{uuid.uuid4().hex}"


def git_value(*args, repo=REPO):
    try:
        result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                                text=True, timeout=5, check=True)
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def git_provenance(repo, namespace):
    result = {f"{namespace}_{field}": None for field in
              ("repo_root", "repo_remote", "git_commit", "git_branch", "git_dirty")}
    if repo is None or git_value("rev-parse", "--is-inside-work-tree", repo=repo) != "true":
        return result
    root = git_value("rev-parse", "--show-toplevel", repo=repo)
    if root is None:
        return result
    dirty = git_value("status", "--porcelain", repo=root)
    result.update({f"{namespace}_repo_root": str(Path(root).resolve()),
                   f"{namespace}_repo_remote": git_value("remote", "get-url", "origin", repo=root),
                   f"{namespace}_git_commit": git_value("rev-parse", "HEAD", repo=root),
                   f"{namespace}_git_branch": git_value("branch", "--show-current", repo=root) or None,
                   f"{namespace}_git_dirty": None if dirty is None else bool(dirty)})
    return result


def host_info():
    cpu_model = ram = cores = None
    try:
        cpu_text = Path("/proc/cpuinfo").read_text()
        cpu_model = re.search(r"^model name\s*:\s*(.+)$", cpu_text, re.M)[1]
        pairs = set()
        for block in cpu_text.split("\n\n"):
            physical = re.search(r"^physical id\s*:\s*(\d+)$", block, re.M)
            core = re.search(r"^core id\s*:\s*(\d+)$", block, re.M)
            if physical and core:
                pairs.add((physical[1], core[1]))
        cores = len(pairs) or None
    except (OSError, TypeError):
        pass
    try:
        ram = int(re.search(r"^MemTotal:\s+(\d+)", Path("/proc/meminfo").read_text(), re.M)[1]) * 1024
    except (OSError, TypeError):
        pass
    return {"hostname": socket.gethostname(), "kernel": platform.release(),
            "cpu_model": cpu_model, "logical_cpu_count": os.cpu_count(),
            "physical_core_count": cores, "total_ram_bytes": ram}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--executable", required=True)
    p.add_argument("--benchmark-profile", required=True, choices=BENCHMARK_PROFILES)
    p.add_argument("--subject-repo", help="Git worktree that produced the ANN executable; overrides discovery")
    p.add_argument("--dataset-id", default="sift1m")
    p.add_argument("--dataset-path", required=True, help="Existing dataset directory or file")
    p.add_argument("--query", required=True)
    p.add_argument("--ground-truth", required=True, help="Existing truthset, or literal null")
    p.add_argument("--index-id", default="sift1m")
    p.add_argument("--index-prefix", required=True)
    p.add_argument("--data-type", choices=("float", "int8", "uint8"), default="float")
    p.add_argument("--search-mode", type=int, choices=(0, 1, 2, 3), default=2)
    p.add_argument("--threads", type=int, default=8)
    p.add_argument("--wcap", type=int, default=32)
    p.add_argument("--k", type=int, default=10)
    p.add_argument("--l-search", type=int, default=20, help="Exactly one L per experiment")
    p.add_argument("--mem-l", type=int, default=10, help="Legacy OVERLAP_INIT needs mem_L>0; canonical supports 0")
    p.add_argument("--distance-metric", choices=("l2", "cosine"), default="l2")
    p.add_argument("--neighbor-type", help="Required positional nbr_type for pipeann-b9ec4ba; legacy annotation only")
    p.add_argument("--trace-mode", choices=("OFF", "LIGHT", "DETAIL"), default="OFF")
    p.add_argument("--repetition", type=int, default=1)
    p.add_argument("--evidence-root", default=os.environ.get("ANN_EVIDENCE_ROOT", "~/ann-research/research-v3"))
    p.add_argument("--mlflow", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument("--telemetry-interval", type=int, default=1)
    p.add_argument("--timeout", type=float, default=300, help="Benchmark wall timeout in seconds")
    p.add_argument("--mlflow-timeout", type=float, default=60)
    p.add_argument("--dry-run", action="store_true")
    return p


def resolve(args):
    profile = BENCHMARK_PROFILES[args.benchmark_profile]
    if profile["neighbor_types"] is not None and args.neighbor_type not in profile["neighbor_types"]:
        raise ValueError("pipeann-b9ec4ba requires --neighbor-type from: " + ", ".join(profile["neighbor_types"]))
    for name in ("threads", "wcap", "k", "l_search", "repetition", "telemetry_interval", "timeout", "mlflow_timeout"):
        value = getattr(args, name)
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be positive and finite")
    if args.mem_l < 0 or args.l_search < args.k:
        raise ValueError("mem_l must be nonnegative and l_search must be at least k")
    for name in ("executable", "dataset_path", "query", "index_prefix", "evidence_root"):
        setattr(args, name, Path(getattr(args, name)).expanduser().resolve())
    if not args.executable.is_file() or not os.access(args.executable, os.X_OK):
        raise ValueError(f"Not an executable: {args.executable}")
    if args.subject_repo is not None:
        args.subject_repo = Path(args.subject_repo).expanduser().resolve()
        if not args.subject_repo.is_dir() or git_value(
                "rev-parse", "--is-inside-work-tree", repo=args.subject_repo) != "true":
            raise ValueError(f"--subject-repo must be an existing Git worktree: {args.subject_repo}")
    args.subject_provenance = git_provenance(
        args.subject_repo if args.subject_repo is not None else args.executable.parent, "subject")
    if not args.dataset_path.exists():
        raise ValueError(f"Dataset path missing: {args.dataset_path}")
    if not args.query.is_file():
        raise ValueError(f"Query file missing: {args.query}")
    args.ground_truth = (None if args.ground_truth == "null"
                         else Path(args.ground_truth).expanduser().resolve())
    if args.ground_truth is not None and not args.ground_truth.is_file():
        raise ValueError(f"Ground truth missing: {args.ground_truth}")
    suffixes = ["_disk.index", "_disk.index.tags"]
    if profile["neighbor_types"] is None or args.neighbor_type == "pq":
        suffixes.extend(("_pq_compressed.bin", "_pq_pivots.bin"))
    elif args.neighbor_type.startswith("rabitq"):
        suffixes.extend("_rabitq_" + part + ".bin" for part in
                        ("metadata", "rotator", "pivots", "compressed"))
    if args.mem_l:
        suffixes.extend(profile["memory_suffixes"])
        if args.benchmark_profile == "pipeann-b9ec4ba":
            # Upstream accepts absent tags (identity mapping); record them when present.
            tag_path = Path(str(args.index_prefix) + "_mem.index.tags")
            if tag_path.is_file():
                suffixes.append("_mem.index.tags")
    args.index_files = []
    for suffix in suffixes:
        path = Path(str(args.index_prefix) + suffix)
        if not path.is_file():
            raise ValueError(f"Index component missing: {path}")
        args.index_files.append(path)
    # Validate the native binary input headers without rewriting any input files.
    with args.query.open("rb") as stream:
        header = stream.read(8)
    if len(header) != 8:
        raise ValueError("Query header is truncated")
    count, dimension = struct.unpack("<II", header)
    item_size = 4 if args.data_type == "float" else 1
    if not count or not dimension or args.query.stat().st_size != 8 + count * dimension * item_size:
        raise ValueError("Query shape/type does not match file size")
    if args.ground_truth:
        with args.ground_truth.open("rb") as stream:
            truth_header = stream.read(8)
        if len(truth_header) != 8:
            raise ValueError("Ground truth header is truncated")
        truth_count, truth_k = struct.unpack("<II", truth_header)
        if truth_count != count or truth_k < args.k:
            raise ValueError("Ground truth query count/K does not match")
        size = args.ground_truth.stat().st_size
        if size not in (8 + truth_count * truth_k * 4, 8 + truth_count * truth_k * 8):
            raise ValueError("Unsupported/truncated ground truth format")
    args.query_count, args.query_dimension = count, dimension
    return args


def benchmark_argv(args):
    profile = BENCHMARK_PROFILES[args.benchmark_profile]
    if profile["neighbor_types"] is not None and args.neighbor_type not in profile["neighbor_types"]:
        raise ValueError("Canonical profile requires a valid --neighbor-type")
    return [str(args.executable), *(str(getattr(args, field)) if getattr(args, field) is not None
                                    else "null" for field in profile["argv_fields"])]


def collector_availability(trace_mode):
    return {name: {"executable": shutil.which(name),
                   "status": "disabled" if trace_mode == "OFF" else
                   "available" if shutil.which(name) else "unavailable"}
            for name in ("mpstat", "pidstat", "iostat")}


def make_manifest(args, identity, argv, collectors):
    harness = git_provenance(REPO, "harness")
    build_directory = args.executable.parent.parent
    build_metadata = {}
    for relative in ("CMakeCache.txt", "compile_commands.json", "src/CMakeFiles/diskann.dir/flags.make",
                     "src/CMakeFiles/pipeann.dir/flags.make"):
        path = build_directory / relative
        if path.is_file():
            build_metadata[relative] = {"path": str(path), "sha256": sha256(path)}
            if relative.endswith("flags.make"):
                build_metadata[relative]["flags"] = [line for line in path.read_text().splitlines()
                                                     if line.startswith(("CXX_DEFINES", "CXX_FLAGS", "CXX_INCLUDES"))]
    return {"schema_version": 2, "run_id": identity, "timestamp_start": utc_now(),
            "timestamp_end": None, **harness, **args.subject_provenance,
            **profile_metadata(args.benchmark_profile),
            # Deprecated v1 aliases identify the harness ONLY, never the ANN subject.
            "git_commit": harness["harness_git_commit"], "git_dirty": harness["harness_git_dirty"],
            "git_branch": harness["harness_git_branch"], "repo_remote": harness["harness_repo_remote"],
            "executable": str(args.executable), "executable_sha256": sha256(args.executable),
            "build_metadata": build_metadata,
            "argv": argv, "exact_command": shlex.join(argv), "cwd": str(REPO),
            "environment": {key: os.environ.get(key) for key in
                            ("OMP_NUM_THREADS", "OMP_PROC_BIND", "OMP_PLACES", "MKL_NUM_THREADS")},
            **host_info(), "dataset_id": args.dataset_id, "dataset_path": str(args.dataset_path),
            "dataset_hash": sha256(args.dataset_path) if args.dataset_path.is_file() and
                            args.dataset_path.stat().st_size <= 64 * 1024 * 1024 else None,
            "query_path": str(args.query), "query_sha256": sha256(args.query),
            "query_count": args.query_count, "query_dimension": args.query_dimension,
            "ground_truth_path": str(args.ground_truth) if args.ground_truth else None,
            "ground_truth_sha256": sha256(args.ground_truth) if args.ground_truth else None,
            "index_id": args.index_id, "index_path": str(args.index_prefix),
            "index_files": [{"path": str(path), "resolved_path": str(path.resolve()),
                             "size_bytes": path.stat().st_size,
                             "sha256": sha256(path) if path.stat().st_size <= 64 * 1024 * 1024 else None}
                            for path in args.index_files],
            "data_type": args.data_type, "search_mode": args.search_mode, "threads": args.threads,
            "wcap": args.wcap, "k": args.k, "l_search": args.l_search, "mem_l": args.mem_l,
            "distance_metric": args.distance_metric, "neighbor_type": args.neighbor_type,
            "trace_mode": args.trace_mode, "repetition": args.repetition,
            "host_telemetry_collectors": collectors, "telemetry_interval_s": args.telemetry_interval,
            "mlflow_enabled": args.mlflow, "mlflow_run_id": None,
            "mlflow_status": "pending" if args.mlflow else "disabled",
            "mlflow_error": None, "status": "running", "error": None}


def parse_benchmark_output(text, l_search, wcap, k, has_truth, benchmark_profile):
    """Accept only the audited benchmark table and a single matching result row.

    The explicit source-audited profile determines the printed latency semantics.
    """
    profile = BENCHMARK_PROFILES[benchmark_profile]
    metrics = dict.fromkeys(METRICS)
    header_seen = False
    rows = []
    for line in text.splitlines():
        if re.fullmatch(r"\s*L\s+I/O Width\s+QPS\s+AvgLat\(us\)\s+P99 Lat\s+Mean Hops\s+Mean IOs(?:\s+Recall@\d+)?\s*", line):
            header_seen = True
            recall_header = re.search(r"Recall@(\d+)", line)
            if bool(recall_header) != has_truth or (recall_header and int(recall_header[1]) != k):
                return metrics, "Recall header disagrees with requested truthset/K"
            continue
        fields = line.split()
        if not header_seen or len(fields) != (8 if has_truth else 7):
            continue
        try:
            values = [float(field) for field in fields]
        except ValueError:
            continue
        if values[0] != l_search or values[1] != wcap:
            continue
        if not all(math.isfinite(v) and v >= 0 for v in values):
            continue
        if values[2] <= 0 or (has_truth and values[7] > 100):
            continue
        rows.append(values)
    if len(rows) != 1:
        return metrics, f"Expected one benchmark row, found {len(rows)}"
    values = rows[0]
    metrics[profile["latency_metric"]] = values[4]
    metrics.update(qps=values[2], mean_latency_us=values[3],
                   mean_hops=values[5], mean_ios=values[6], recall=values[7] if has_truth else None)
    return metrics, None


def make_summary(identity, metrics, wall_time, exit_code, status, parse_error, benchmark_profile):
    profile = BENCHMARK_PROFILES[benchmark_profile]
    return {"schema_version": 2, "run_id": identity, **metrics, "wall_time_s": wall_time,
            **profile_metadata(benchmark_profile), "printed_latency_metric": profile["latency_metric"],
            "exit_code": exit_code, "run_status": status, "parse_error": parse_error,
            "recall_unit": "percent", "latency_note":
            f"Printed P99 Lat maps to {profile['latency_metric']} at percentile {profile['percentile']}; "
            "all other unreported percentiles remain null"}


def stop_process(process):
    if process is not None and process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()


class Telemetry:
    def __init__(self, directory, collectors, interval):
        self.directory, self.collectors, self.interval = directory, collectors, interval
        self.processes = []

    def start(self, benchmark_pid):
        commands = {"mpstat": ["-P", "ALL", str(self.interval)],
                    "pidstat": ["-h", "-u", "-r", "-d", "-p", str(benchmark_pid), str(self.interval)],
                    "iostat": ["-y", "-t", "-x", "-d", str(self.interval)]}
        env = {**os.environ, "LC_ALL": "C", "S_TIME_FORMAT": "ISO"}
        for name, info in self.collectors.items():
            if info["status"] != "available":
                continue
            info["argv"] = [info["executable"], *commands[name]]
            stream = None
            try:
                self.directory.mkdir(exist_ok=True)
                stream = (self.directory / f"{name}.log").open("w")
                process = subprocess.Popen(info["argv"], stdout=stream, stderr=subprocess.STDOUT,
                                           env=env, start_new_session=True)
                self.processes.append((process, stream, info))
                info["status"] = "running"
                info["timestamp_start"] = utc_now()
            except OSError as error:
                if stream is not None:
                    stream.close()
                info.update(status="failed", error=str(error))

    def stop(self):
        for process, stream, info in self.processes:
            already_exited = process.poll() is not None
            stop_process(process)
            stream.close()
            info.update(status="failed" if already_exited and process.returncode else "stopped",
                        exit_code=process.returncode, timestamp_end=utc_now())


def metric_unit(metric):
    if metric.startswith("%"):
        return "percent"
    if "await" in metric:
        return "ms"
    if metric in ("RSS", "VSZ") or metric.endswith("-sz") and metric != "aqu-sz":
        return "KiB"
    if "kB" in metric:
        return "KiB/s" if metric.endswith("/s") else "KiB"
    if metric.endswith("/s"):
        return "1/s"
    return None


def telemetry_rows(text, collector, identity):
    """Normalize numeric columns while retaining raw sysstat output for auditing."""
    header = None
    sample_time = None
    for line in text.splitlines():
        fields = line.lstrip("# ").split()
        if not fields or line.startswith("Average:") or fields[0] == "Linux":
            continue
        if collector == "iostat" and re.match(r"^\d{4}-\d{2}-\d{2}T", fields[0]):
            sample_time = fields[0]
            continue
        entity_key = {"mpstat": "CPU", "pidstat": "PID", "iostat": "Device"}[collector]
        if entity_key in fields:
            header = fields
            # mpstat has a literal time as the first header token.
            if collector == "mpstat":
                header = ["Time", *header[1:]]
            continue
        if header is None or len(fields) != len(header):
            continue
        row = dict(zip(header, fields))
        if entity_key not in row:
            continue
        sample_time_row = row.get("Time", sample_time)
        for metric, raw in row.items():
            if metric in ("Time", "UID", "PID", "CPU", "Device", "Command"):
                continue
            try:
                value = float(raw)
            except ValueError:
                continue
            if math.isfinite(value):
                yield {"schema_version": 1, "run_id": identity, "collector": collector,
                       "sample_time_local": sample_time_row, "entity": row[entity_key],
                       "metric": metric, "value": value, "unit": metric_unit(metric)}


def write_trace_artifacts(directory, manifest):
    with (directory / "query_metrics.csv").open("w", newline="") as stream:
        csv.writer(stream).writerow(QUERY_COLUMNS)  # No per-query export exists yet.
    count = 0
    with (directory / "system_metrics.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, SYSTEM_COLUMNS)
        writer.writeheader()
        for name, info in manifest["host_telemetry_collectors"].items():
            path = directory / "telemetry" / f"{name}.log"
            rows = list(telemetry_rows(path.read_text(errors="replace"), name, manifest["run_id"])) if path.exists() else []
            writer.writerows(rows)
            count += len(rows)
            info["metric_rows"] = len(rows)
    health = {"schema_version": 1, "trace_mode": manifest["trace_mode"], "query_rows": 0,
              "system_metric_rows": count, "ann_events_available": False,
              "d1_d4_d6_implemented": False, "reason": "Current benchmark exports run summaries only",
              "collectors": manifest["host_telemetry_collectors"]}
    write_json(directory / "trace_health.json", health)
    if manifest["trace_mode"] == "DETAIL":
        # Harness lifecycle only. This interface is not an ANN causal trace.
        with (directory / "events.jsonl").open("w") as stream:
            for kind, timestamp in (("benchmark_start", manifest["timestamp_start"]),
                                    ("benchmark_end", manifest["timestamp_end"])):
                stream.write(json.dumps({"schema_version": 1, "run_id": manifest["run_id"],
                                         "source": "harness", "event": kind, "timestamp": timestamp}) + "\n")


def update_run_index(root, manifest, summary):
    directory = root / "summaries"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "run_index.csv"
    row = {key: {**manifest, **summary}.get(key) for key in INDEX_COLUMNS}
    with (directory / ".run_index.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        rows = []
        if path.exists():
            with path.open(newline="") as stream:
                reader = csv.DictReader(stream)
                if reader.fieldnames not in (list(INDEX_COLUMNS), list(V1_INDEX_COLUMNS)):
                    raise ValueError("Existing run_index.csv schema differs; preserved without overwriting")
                rows = [old for old in reader if old["run_id"] != row["run_id"]]
        rows.append(row)
        with tempfile.NamedTemporaryFile(mode="w", newline="", dir=directory, delete=False) as stream:
            temporary = Path(stream.name)
            try:
                writer = csv.DictWriter(stream, INDEX_COLUMNS)
                writer.writeheader()
                writer.writerows(rows)
                stream.flush()
                os.fsync(stream.fileno())
            except BaseException:
                temporary.unlink(missing_ok=True)
                raise
        os.replace(temporary, path)


def checksums(directory):
    paths = sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    with (directory / "SHA256SUMS").open("w") as stream:
        for path in paths:
            stream.write(f"{sha256(path)}  {path.relative_to(directory).as_posix()}\n")


def mirror_mlflow(directory, root, timeout, cancelled=lambda: False):
    """Isolate optional dependency failures/timeouts from benchmark and local evidence."""
    result_path = directory / "mlflow_result.json"
    with (directory / "mlflow.log").open("w") as stream:
        worker = subprocess.Popen([sys.executable, str(Path(__file__).with_name("mlflow_mirror.py")),
                                   str(directory), str(root)], stdout=stream,
                                  stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + timeout
            while worker.poll() is None:
                if cancelled() or time.monotonic() > deadline:
                    reason = "MLflow mirror interrupted" if cancelled() else "MLflow mirror timed out"
                    return {"status": "failed", "run_id": None, "error": reason}
                try:
                    worker.wait(timeout=0.2)
                except subprocess.TimeoutExpired:
                    pass
        finally:
            stop_process(worker)
    if result_path.exists():
        return json.loads(result_path.read_text())
    return {"status": "failed", "run_id": None, "error": f"MLflow worker exited {worker.returncode}; see mlflow.log"}


def run(args):
    args = resolve(args)
    argv = benchmark_argv(args)
    identity = run_id(args.dataset_id, args.threads, args.wcap, args.trace_mode, args.repetition)
    directory = args.evidence_root / "runs" / identity
    collectors = collector_availability(args.trace_mode)
    preview = {"run_id": identity, "executable": str(args.executable),
               **profile_metadata(args.benchmark_profile),
               **git_provenance(REPO, "harness"), **args.subject_provenance,
               "dataset": str(args.dataset_path), "query": str(args.query),
               "index": str(args.index_prefix), "exact_command": shlex.join(argv),
               "run_directory": str(directory), "trace_mode": args.trace_mode,
               "mlflow_enabled": args.mlflow, "telemetry_collectors": collectors}
    if args.dry_run:
        print(json.dumps(preview, indent=2))
        return 0  # No directories, telemetry, MLflow import or benchmark process.
    directory.mkdir(parents=True, exist_ok=False)
    manifest = make_manifest(args, identity, argv, collectors)
    write_json(directory / "manifest.json", manifest)
    command = ["#!/bin/sh", "set -eu", "cd " + shlex.quote(str(REPO))]
    for key, value in manifest["environment"].items():
        command.append(f"export {key}={shlex.quote(value)}" if value is not None else f"unset {key}")
    command.append("exec " + shlex.join(argv))
    (directory / "command.sh").write_text("\n".join(command) + "\n")
    telemetry = Telemetry(directory / "telemetry", collectors, args.telemetry_interval)
    process = None
    received_signal = None
    status = "failed"
    exit_code = None
    def handle_signal(number, _frame):
        nonlocal received_signal
        received_signal = number  # Cleanup happens in normal control flow.
    handlers = {number: signal.signal(number, handle_signal) for number in (signal.SIGINT, signal.SIGTERM)}
    start = time.monotonic()
    try:
        with (directory / "stdout.log").open("w") as stream:
            if received_signal is None:
                process = subprocess.Popen(argv, cwd=REPO, stdout=stream, stderr=subprocess.STDOUT,
                                           start_new_session=True)
                telemetry.start(process.pid)
            while process is not None and process.poll() is None:
                if received_signal is not None:
                    status = "interrupted"
                    break
                if time.monotonic() - start > args.timeout:
                    status = "timed_out"
                    break
                try:
                    process.wait(timeout=0.2)
                except subprocess.TimeoutExpired:
                    pass
            if received_signal is not None:
                status = "interrupted"
    except Exception as error:
        manifest["error"] = f"{type(error).__name__}: {error}"
    finally:
        stop_process(process)
        wall = time.monotonic() - start
        exit_code = process.returncode if process is not None else None
        telemetry.stop()
        manifest["timestamp_end"] = utc_now()
    try:
        output_path = directory / "stdout.log"
        metrics, parse_error = parse_benchmark_output(
            output_path.read_text(errors="replace") if output_path.exists() else "",
            args.l_search, args.wcap, args.k, args.ground_truth is not None, args.benchmark_profile)
        if status not in ("interrupted", "timed_out"):
            status = "success" if exit_code == 0 and parse_error is None and manifest["error"] is None else "failed"
        manifest.update(status=status, termination_signal=received_signal)
        summary = make_summary(identity, metrics, wall, exit_code, status, parse_error, args.benchmark_profile)
        write_json(directory / "summary.json", summary)
        if args.trace_mode != "OFF":
            write_trace_artifacts(directory, manifest)
        write_json(directory / "manifest.json", manifest)
        if args.mlflow and received_signal is None:
            try:
                mirrored = mirror_mlflow(directory, args.evidence_root, args.mlflow_timeout,
                                         cancelled=lambda: received_signal is not None)
            except Exception as error:
                mirrored = {"status": "failed", "run_id": None, "error": str(error)}
            manifest.update(mlflow_status=mirrored["status"], mlflow_run_id=mirrored["run_id"],
                            mlflow_error=mirrored["error"])
        elif args.mlflow:
            manifest.update(mlflow_status="skipped", mlflow_error="Run interrupted")
        try:
            update_run_index(args.evidence_root, manifest, summary)
            manifest["run_index_status"] = "updated"
        except Exception as error:
            manifest.update(run_index_status="failed", run_index_error=str(error))
        manifest["termination_signal"] = received_signal
        write_json(directory / "manifest.json", manifest)
        checksums(directory)
        print(json.dumps({**preview, "run_status": status, "summary": summary,
                          "mlflow_status": manifest["mlflow_status"], "mlflow_run_id": manifest["mlflow_run_id"]}, indent=2))
        return 128 + received_signal if received_signal else 0 if status == "success" else 1
    finally:
        for number, handler in handlers.items():
            signal.signal(number, handler)


def main():
    try:
        return run(parser().parse_args())
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
