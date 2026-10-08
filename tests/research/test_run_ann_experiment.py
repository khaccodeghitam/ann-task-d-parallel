"""P0 tests use synthetic files/processes; no SIFT dataset or ANN build required."""

import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import multiprocessing
import os
from pathlib import Path
import signal
import struct
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from jsonschema import Draft202012Validator, ValidationError

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools/research/run_ann_experiment.py"
spec = importlib.util.spec_from_file_location("p0runner", SCRIPT)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
TABLE = """unrelated startup log 20 32 1 2 3 4 5 6
     L   I/O Width         QPS  AvgLat(us)     P99 Lat   Mean Hops    Mean IOs   Recall@10
=========================================================================================
    20          32     1234.50      789.00     1500.25       12.00       13.00       90.50
"""


def append_index(root, number):
    runner.update_run_index(Path(root), {"run_id": f"worker-{number}"}, {"run_status": "success"})


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="p0-test-")
        self.root = Path(self.temp.name)
        self.executable = self.root / "fake benchmark"
        self.executable.write_text("#!/usr/bin/env python3\nprint(" + repr(TABLE) + ")\n")
        self.executable.chmod(0o755)
        self.query = self.root / "query.bin"
        self.query.write_bytes(struct.pack("<IIff", 1, 2, 1.0, 2.0))
        self.truth = self.root / "truth.bin"
        self.truth.write_bytes(struct.pack("<II", 1, 10) + bytes(10 * 8))
        self.prefix = self.root / "index"
        for suffix in ("_disk.index", "_disk.index.tags", "_pq_compressed.bin", "_pq_pivots.bin",
                       "_mem.index", "_mem.index.data", "_mem.index.tags"):
            Path(str(self.prefix) + suffix).write_bytes(b"synthetic index, never searched")
        self.evidence = self.root / "evidence"

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, *extra):
        return ["--executable", str(self.executable), "--dataset-path", str(self.root),
                "--query", str(self.query), "--ground-truth", str(self.truth),
                "--index-prefix", str(self.prefix), "--evidence-root", str(self.evidence), *extra]

    def execute(self, *extra):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = runner.run(runner.parser().parse_args(self.cli(*extra)))
        return code, json.loads(output.getvalue())

    def test_run_ids_are_unique_and_safe(self):
        ids = {runner.run_id("../sift 1m", 8, 32, "OFF", 1) for _ in range(1000)}
        self.assertEqual(len(ids), 1000)
        for identity in ids:
            self.assertRegex(identity, r"^P0_[A-Za-z0-9_-]+$")
            self.assertIn("_T8_W32_OFF_R001_", identity)

    def test_manifest_and_summary_schemas(self):
        code, result = self.execute()
        self.assertEqual(code, 0)
        directory = Path(result["run_directory"])
        for name in ("manifest", "summary"):
            schema = json.loads((REPO / f"schemas/research/{name}.schema.json").read_text())
            Draft202012Validator.check_schema(schema)
            validator = Draft202012Validator(schema)
            data = json.loads((directory / f"{name}.json").read_text())
            validator.validate(data)
            del data["run_id"]
            with self.assertRaises(ValidationError):
                validator.validate(data)
        manifest = json.loads((directory / "manifest.json").read_text())
        self.assertIsNone(manifest["neighbor_type"])
        self.assertEqual(manifest["argv"][0], str(self.executable))
        self.assertEqual(manifest["status"], "success")

    def test_parser_preserves_true_percentile(self):
        metrics, error = runner.parse_benchmark_output(TABLE, 20, 32, 10, True)
        self.assertIsNone(error)
        self.assertEqual(metrics["qps"], 1234.5)
        self.assertEqual(metrics["recall"], 90.5)
        self.assertEqual(metrics["p999_latency_us"], 1500.25)
        for key in ("p50_latency_us", "p95_latency_us", "p99_latency_us"):
            self.assertIsNone(metrics[key])

    def test_parser_rejects_ambiguous_unavailable_or_invalid_results(self):
        for text in ("20 32 1 2 3 4 5 6", TABLE + TABLE, TABLE.replace("1234.50", "nan"),
                     TABLE.replace("90.50", "101.00"), TABLE.replace("Recall@10", "Recall@1")):
            with self.subTest(text=text):
                metrics, error = runner.parse_benchmark_output(text, 20, 32, 10, True)
                self.assertIsNotNone(error)
                self.assertTrue(all(value is None for value in metrics.values()))

    def test_parser_without_ground_truth(self):
        text = TABLE.replace("   Recall@10", "").replace("       90.50", "")
        metrics, error = runner.parse_benchmark_output(text, 20, 32, 10, False)
        self.assertIsNone(error)
        self.assertIsNone(metrics["recall"])
        self.assertEqual(metrics["mean_ios"], 13)

    def test_dry_run_has_no_side_effects(self):
        with mock.patch.object(runner.subprocess, "Popen", side_effect=AssertionError("process launched")):
            code, result = self.execute("--dry-run", "--mlflow", "--trace-mode", "LIGHT")
        self.assertEqual(code, 0)
        self.assertFalse(self.evidence.exists())
        self.assertEqual(result["executable"], str(self.executable))
        self.assertIn("'" + str(self.executable) + "'", result["exact_command"])
        self.assertTrue(result["mlflow_enabled"])
        self.assertEqual(result["trace_mode"], "LIGHT")
        self.assertEqual(set(result["telemetry_collectors"]), {"mpstat", "pidstat", "iostat"})

    def test_mlflow_disabled_and_off_minimal_artifacts(self):
        with mock.patch.object(runner, "mirror_mlflow", side_effect=AssertionError("MLflow called")):
            code, result = self.execute("--no-mlflow")
        self.assertEqual(code, 0)
        self.assertEqual(result["mlflow_status"], "disabled")
        names = {p.name for p in Path(result["run_directory"]).iterdir()}
        self.assertEqual(names, {"manifest.json", "summary.json", "command.sh", "stdout.log", "SHA256SUMS"})
        self.assertFalse((self.evidence / "mlflow").exists())

    def test_mlflow_failure_keeps_local_success(self):
        with mock.patch.object(runner, "mirror_mlflow", return_value={"status": "failed", "run_id": None, "error": "missing dependency"}):
            code, result = self.execute("--mlflow")
        self.assertEqual(code, 0)
        self.assertEqual(result["run_status"], "success")
        manifest = json.loads((Path(result["run_directory"]) / "manifest.json").read_text())
        self.assertEqual(manifest["mlflow_status"], "failed")
        self.assertEqual(manifest["mlflow_error"], "missing dependency")

    def test_failed_benchmark_diagnostics_and_checksums(self):
        self.executable.write_text("#!/bin/sh\necho 'diagnostic error' >&2\nexit 7\n")
        code, result = self.execute()
        self.assertEqual(code, 1)
        self.assertEqual(result["summary"]["exit_code"], 7)
        directory = Path(result["run_directory"])
        self.assertIn("diagnostic error", (directory / "stdout.log").read_text())
        self.check_checksums(directory)

    def check_checksums(self, directory):
        lines = (directory / "SHA256SUMS").read_text().splitlines()
        self.assertEqual(len(lines), len([p for p in directory.rglob("*") if p.is_file()]) - 1)
        for line in lines:
            digest, name = line.split("  ", 1)
            self.assertEqual(digest, hashlib.sha256((directory / name).read_bytes()).hexdigest())

    def test_zero_exit_without_benchmark_row_is_failed(self):
        self.executable.write_text("#!/bin/sh\necho 'load failed but main returns zero'\n")
        code, result = self.execute()
        self.assertEqual(code, 1)
        self.assertEqual(result["summary"]["exit_code"], 0)
        self.assertEqual(result["run_status"], "failed")

    def test_missing_collectors_and_detail_scaffold(self):
        with mock.patch.object(runner.shutil, "which", return_value=None):
            code, result = self.execute("--trace-mode", "DETAIL")
        self.assertEqual(code, 0)
        directory = Path(result["run_directory"])
        health = json.loads((directory / "trace_health.json").read_text())
        self.assertEqual(health["query_rows"], 0)
        self.assertEqual(health["system_metric_rows"], 0)
        self.assertFalse(health["ann_events_available"])
        for info in health["collectors"].values():
            self.assertEqual(info["status"], "unavailable")
        schema = json.loads((REPO / "schemas/research/events.schema.json").read_text())
        events = [json.loads(line) for line in (directory / "events.jsonl").read_text().splitlines()]
        self.assertEqual(len(events), 2)
        for event in events:
            Draft202012Validator(schema).validate(event)
        self.assertEqual(len((directory / "query_metrics.csv").read_text().splitlines()), 1)
        self.check_checksums(directory)

    def test_telemetry_normalization(self):
        examples = {
            "mpstat": "12:00:00 CPU %usr %idle\n12:00:01 all 10.0 90.0\nAverage: all 10.0 90.0\n",
            "pidstat": "# Time UID PID %CPU RSS Command\n12:00:01 1000 123 10.0 1024 ann\n",
            "iostat": "2026-10-08T12:00:01+0700\nDevice r/s r_await %util\nnvme0n1 2.0 1.5 3.0\n"}
        for name, text in examples.items():
            with self.subTest(name=name):
                rows = list(runner.telemetry_rows(text, name, "test"))
                self.assertTrue(rows)
                self.assertTrue(all(row["sample_time_local"] is not None for row in rows))
                self.assertTrue(all(row["value"] >= 0 for row in rows))
        self.assertEqual(len(list(runner.telemetry_rows(examples["mpstat"], "mpstat", "test"))), 2)

    def test_csv_schema_columns(self):
        schemas = json.loads((REPO / "schemas/research/csv_schemas.json").read_text())
        for filename, columns in (("query_metrics.csv", runner.QUERY_COLUMNS),
                                  ("system_metrics.csv", runner.SYSTEM_COLUMNS),
                                  ("run_index.csv", runner.INDEX_COLUMNS)):
            self.assertEqual(schemas[filename]["columns"], list(columns))

    def test_mlflow_worker_timeout_and_cancellation_cleanup(self):
        pid_path = self.root / "mirror.pid"
        worker_path = self.root / "mlflow_mirror.py"
        worker_path.write_text(f"import os,time\nopen({str(pid_path)!r},'w').write(str(os.getpid()))\ntime.sleep(30)\n")
        with mock.patch.object(runner, "__file__", str(self.root / "runner.py")):
            for cancelled in (lambda: False, lambda: pid_path.exists()):
                pid_path.unlink(missing_ok=True)
                result = runner.mirror_mlflow(self.root, self.evidence, 0.3, cancelled=cancelled)
                self.assertEqual(result["status"], "failed")
                self.assertTrue(pid_path.exists())
                with self.assertRaises(ProcessLookupError):
                    os.kill(int(pid_path.read_text()), 0)

    def test_run_index_upsert_and_preserves_other_rows(self):
        runner.update_run_index(self.evidence, {"run_id": "one"}, {"qps": 1})
        runner.update_run_index(self.evidence, {"run_id": "two"}, {"qps": 2})
        runner.update_run_index(self.evidence, {"run_id": "one"}, {"qps": 3})
        with (self.evidence / "summaries/run_index.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 2)
        self.assertEqual({row["run_id"]: row["qps"] for row in rows}, {"one": "3", "two": "2"})

    def test_run_index_concurrent_writers(self):
        workers = [multiprocessing.Process(target=append_index, args=(str(self.evidence), i)) for i in range(6)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(timeout=10)
            self.assertEqual(worker.exitcode, 0)
        with (self.evidence / "summaries/run_index.csv").open() as stream:
            self.assertEqual(len(list(csv.DictReader(stream))), 6)

    def test_preserve_incompatible_run_index(self):
        directory = self.evidence / "summaries"
        directory.mkdir(parents=True)
        path = directory / "run_index.csv"
        path.write_text("legacy,header\nimportant,evidence\n")
        code, result = self.execute()
        self.assertEqual(code, 0)
        self.assertEqual(path.read_text(), "legacy,header\nimportant,evidence\n")
        manifest = json.loads((Path(result["run_directory"]) / "manifest.json").read_text())
        self.assertEqual(manifest["run_index_status"], "failed")

    def test_existing_run_directory_is_not_overwritten(self):
        directory = self.evidence / "runs/fixed"
        directory.mkdir(parents=True)
        (directory / "keep").write_text("prior evidence")
        with mock.patch.object(runner, "run_id", return_value="fixed"), self.assertRaises(FileExistsError):
            self.execute()
        self.assertEqual((directory / "keep").read_text(), "prior evidence")

    def test_rebuild_run_index_from_canonical_run(self):
        code, result = self.execute()
        self.assertEqual(code, 0)
        (self.evidence / "summaries/run_index.csv").unlink()
        process = subprocess.run([sys.executable, str(REPO / "tools/research/rebuild_run_index.py"),
                                  "--evidence-root", str(self.evidence)], capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        with (self.evidence / "summaries/run_index.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["run_id"], result["run_id"])
        self.check_checksums(Path(result["run_directory"]))

    def test_timeout_stops_process_and_finalizes(self):
        self.executable.write_text("#!/usr/bin/env python3\nimport time\ntime.sleep(30)\n")
        code, result = self.execute("--timeout", "0.05")
        self.assertEqual(code, 1)
        self.assertEqual(result["run_status"], "timed_out")
        self.assertLess(result["summary"]["wall_time_s"], 5)
        self.check_checksums(Path(result["run_directory"]))

    def test_sigterm_stops_benchmark_and_collectors(self):
        benchmark_pid = self.root / "benchmark.pid"
        collector_pid = self.root / "collector.pid"
        self.executable.write_text(f"#!/usr/bin/env python3\nimport os,time\nopen({str(benchmark_pid)!r},'w').write(str(os.getpid()))\ntime.sleep(30)\n")
        # A local fake mpstat records its PID; no dependency on installed collectors.
        bin_directory = self.root / "bin"
        bin_directory.mkdir()
        collector = bin_directory / "mpstat"
        collector.write_text(f"#!{sys.executable}\nimport os,time\nopen({str(collector_pid)!r},'w').write(str(os.getpid()))\ntime.sleep(30)\n")
        collector.chmod(0o755)
        process = subprocess.Popen([sys.executable, str(SCRIPT), *self.cli("--trace-mode", "LIGHT")],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                   env={**os.environ, "PATH": str(bin_directory) + os.pathsep + os.environ["PATH"]})
        try:
            deadline = time.monotonic() + 10
            while not collector_pid.exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue(collector_pid.exists())
            process.send_signal(signal.SIGTERM)
            output, error = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 143, error)
            result = json.loads(output)
            self.assertEqual(result["run_status"], "interrupted")
            for path in (benchmark_pid, collector_pid):
                with self.assertRaises(ProcessLookupError):
                    os.kill(int(path.read_text()), 0)
            self.check_checksums(Path(result["run_directory"]))
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()

    def test_invalid_input_rejected_before_artifacts(self):
        self.truth.write_bytes(struct.pack("<II", 2, 10) + bytes(20 * 8))
        with self.assertRaisesRegex(ValueError, "Ground truth query count"):
            self.execute()
        self.assertFalse(self.evidence.exists())


if __name__ == "__main__":
    unittest.main()
