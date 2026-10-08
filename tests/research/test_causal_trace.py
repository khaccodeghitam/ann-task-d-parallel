"""Synthetic causal protocol tests; no dataset, root, or ANN executable required."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools/research"))
import causal_trace as trace
from check_causal_trace import check_events
import run_ann_experiment as runner


def valid_events(cache=False):
    kinds = ["QUERY_START", "WIDTH_INIT", "IO_SELECT"]
    kinds += ["IO_CACHE_READY"] if cache else ["IO_SUBMIT", "IO_CQE_SEEN"]
    kinds += ["IO_PUBLISH", "NODE_EXPAND", "WIDTH_CHANGE", "QUERY_END", "TRACE_HEALTH"]
    counts = dict(submitted=0, cqe_seen=0, published=0, expanded=0, cache_ready=0, cache_published=0)
    events = []
    for i, kind in enumerate(kinds):
        field = {"IO_SUBMIT": "submitted", "IO_CQE_SEEN": "cqe_seen", "IO_CACHE_READY": "cache_ready",
                 "IO_PUBLISH": "cache_published" if cache else "published", "NODE_EXPAND": "expanded"}.get(kind)
        if field: counts[field] += 1
        event = dict.fromkeys(trace.EVENT_FIELDS)
        event.pop("type")
        event.update(schema_version=2, source="ann", run_id="synthetic", event=kind,
                     timestamp_ns=100 + i, query_id=0, worker_id=0, linux_tid=123,
                     ring_id=16, **counts, completed_hidden=counts["cqe_seen"] - counts["published"],
                     events_dropped=0, ordering_violations=0, outstanding_correlations=0)
        if kind != "QUERY_START":
            event.update(width=5 if i >= kinds.index("WIDTH_CHANGE") else 4, wcap=32)
        if kind.startswith("IO_"):
            event.update(request_seq=1, request_key=64, node_id=7, page_id=1, location=7, offset=4096, length=4096)
            event["outstanding_correlations"] = int(kind != "IO_PUBLISH")
        if kind == "IO_CQE_SEEN": event.update(poll_cqes=1, cqe_result=4096)
        if kind == "NODE_EXPAND": event["node_id"] = 7
        if kind == "WIDTH_CHANGE":
            event.update(old_width=4, cur_n_in=10, cur_tot=10, n_in=1, n_out=0, max_marker=8, inflight_count=0)
        events.append(event)
    return events


def raw_trace(events=None, mode="DETAIL", dropped=0):
    events = valid_events() if events is None else events
    counters = dict.fromkeys(trace.COUNTER_FIELDS, 0)
    counters.update(query_id=0, worker_id=0, linux_tid=123, is_sampled=int(mode == "DETAIL"), selected=1,
                    submitted=1, cqe_seen=1, published=1, expanded=1, poll_calls=1, cqe_count=1,
                    max_completed_hidden=1, initial_width=4, final_width=5, width_change_count=1,
                    max_inflight=1, events_dropped=dropped, latency_ns=123456,
                    events_written=len(events) if mode == "DETAIL" else 0)
    output = trace.HEADER.pack(b"PANTRC01", 1, trace.MODES.index(mode), 1, 32, 1, 1,
                               len(events) if mode == "DETAIL" else 0, 0 if mode == "OFF" else 1,
                               len(trace.EVENT_FIELDS), len(trace.COUNTER_FIELDS))
    if mode == "DETAIL":
        for event in events:
            values = {**event, "type": trace.EVENTS.index(event["event"]) + 1}
            output += struct.pack(f"<{len(trace.EVENT_FIELDS)}Q", *(trace.NA if values[k] is None else values[k]
                                                                    for k in trace.EVENT_FIELDS))
    if mode != "OFF":
        output += struct.pack(f"<{len(trace.COUNTER_FIELDS)}Q", *(counters[k] for k in trace.COUNTER_FIELDS))
    return output


class CausalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="causal-test-")
        self.root = Path(self.temp.name)
        self.manifest = {"run_id": "synthetic", "trace_mode": "DETAIL", "query_count": 1, "threads": 1,
                         "wcap": 32, "trace_config": {"detail_first_n": 1, "event_capacity": 32}}

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_physical_and_cache_lifecycles(self):
        for cache in (False, True):
            with self.subTest(cache=cache):
                result = check_events(valid_events(cache))
                self.assertTrue(result["trace_valid"], result)

    def test_all_required_malformed_traces_fail(self):
        original = valid_events()
        variants = {}
        rows = copy.deepcopy(original); rows[3], rows[4] = rows[4], rows[3]; variants["CQE before submit"] = rows
        rows = copy.deepcopy(original); rows[4], rows[5] = rows[5], rows[4]; variants["publish before CQE"] = rows
        rows = copy.deepcopy(original); rows.insert(3, copy.deepcopy(rows[2])); variants["duplicate request_seq"] = rows
        rows = copy.deepcopy(original); rows[5]["completed_hidden"] = -1; variants["negative hidden"] = rows
        rows = copy.deepcopy(original); rows[7]["width"] = 3; variants["width decrease"] = rows
        rows = copy.deepcopy(original); rows[7]["width"] = 6; variants["width jump"] = rows
        rows = copy.deepcopy(original); rows.pop(5); variants["unfinished request"] = rows
        rows = copy.deepcopy(original); rows.pop(3); variants["CQE without submit"] = rows
        rows = copy.deepcopy(original); rows[1]["width"] = 5; variants["width init"] = rows
        rows = copy.deepcopy(original); rows[7]["width"] = 33; variants["width bounds"] = rows
        rows = copy.deepcopy(original); rows.pop(); variants["missing TRACE_HEALTH"] = rows
        for label, rows in variants.items():
            with self.subTest(label=label):
                self.assertFalse(check_events(rows)["trace_valid"])

    def test_published_request_need_not_expand(self):
        rows = [r for r in valid_events() if r["event"] != "NODE_EXPAND"]
        for row in rows: row["expanded"] = 0
        self.assertTrue(check_events(rows)["trace_valid"])

    def test_publication_fifo_with_out_of_order_completions(self):
        base = valid_events()
        second = []
        for event in base:
            if event["event"] in ("IO_SELECT", "IO_SUBMIT", "IO_CQE_SEEN", "IO_PUBLISH"):
                copy_event = copy.deepcopy(event)
                copy_event.update(request_seq=2, request_key=128, node_id=8)
                second.append(copy_event)
        rows = base[:4] + second[:2] + [second[2], base[4], base[5], second[3]] + base[6:]
        counts = dict(submitted=0, cqe_seen=0, published=0, expanded=0, cache_ready=0, cache_published=0)
        outstanding = 0
        for i, event in enumerate(rows):
            kind = event["event"]
            field = {"IO_SUBMIT": "submitted", "IO_CQE_SEEN": "cqe_seen", "IO_PUBLISH": "published",
                     "NODE_EXPAND": "expanded"}.get(kind)
            if field: counts[field] += 1
            outstanding += int(kind == "IO_SELECT") - int(kind == "IO_PUBLISH")
            event.update(**counts, completed_hidden=counts["cqe_seen"] - counts["published"],
                         outstanding_correlations=outstanding, timestamp_ns=100 + i)
        self.assertTrue(check_events(rows)["trace_valid"])
        rows[8]["request_seq"], rows[9]["request_seq"] = rows[9]["request_seq"], rows[8]["request_seq"]
        result = check_events(rows)
        self.assertFalse(result["trace_valid"])
        self.assertTrue(any("FIFO" in error for error in result["errors"]))

    def test_summary_counters_cannot_disagree_with_sampled_events(self):
        raw = bytearray(raw_trace())
        offset = trace.HEADER.size + 10 * len(trace.EVENT_FIELDS) * 8
        for field in ("selected", "submitted", "cqe_seen", "published", "cqe_count"):
            struct.pack_into("<Q", raw, offset + trace.COUNTER_FIELDS.index(field) * 8, 2)
        (self.root / "ann_trace.bin").write_bytes(raw)
        health = trace.export_trace(self.root, self.manifest)
        self.assertFalse(health["trace_valid"])

    def test_checker_cli_machine_readable_failure(self):
        path = self.root / "events.jsonl"
        path.write_text(json.dumps({"event": "IO_CQE_SEEN", "query_id": 0}) + "\n")
        process = subprocess.run([sys.executable, str(REPO / "tools/research/check_causal_trace.py"), str(path)],
                                 text=True, capture_output=True)
        self.assertEqual(process.returncode, 1)
        self.assertFalse(json.loads(process.stdout)["trace_valid"])

    def test_exporter_schemas_and_health(self):
        (self.root / "ann_trace.bin").write_bytes(raw_trace())
        health = trace.export_trace(self.root, self.manifest)
        self.assertTrue(health["trace_valid"], health)
        self.assertEqual(health["sample_requested"], 1)
        self.assertEqual(health["sample_observed"], 1)
        self.assertEqual(health["events_written"], 10)
        for key in trace.FAILURE_COUNTERS: self.assertEqual(health[key], 0)
        events = [json.loads(row) for row in (self.root / "events.jsonl").read_text().splitlines()]
        validator = Draft202012Validator(json.loads((REPO / "schemas/research/causal_events.schema.json").read_text()))
        for event in events: validator.validate(event)
        Draft202012Validator(json.loads((REPO / "schemas/research/causal_trace_health.schema.json").read_text())).validate(health)
        self.assertIn("123.456", (self.root / "query_metrics.csv").read_text())

    def test_off_and_light_exports(self):
        for mode in ("OFF", "LIGHT"):
            with self.subTest(mode=mode):
                (self.root / "ann_trace.bin").write_bytes(raw_trace(mode=mode))
                self.manifest["trace_mode"] = mode
                health = trace.export_trace(self.root, self.manifest)
                self.assertTrue(health["trace_valid"], health)
                self.assertEqual(health["events_written"], 0)
                self.assertEqual((self.root / "events.jsonl").read_text(), "")
                self.assertEqual(health["query_rows"], 0 if mode == "OFF" else 1)

    def test_dropped_events_invalidate_trace(self):
        (self.root / "ann_trace.bin").write_bytes(raw_trace(dropped=1))
        health = trace.export_trace(self.root, self.manifest)
        self.assertFalse(health["trace_valid"])
        self.assertEqual(health["events_dropped"], 1)

    def test_missing_or_corrupt_raw_trace_fails_health(self):
        health = trace.export_trace(self.root, self.manifest)
        self.assertFalse(health["trace_valid"])
        raw = raw_trace()
        for value in (raw[:8], raw[:-1], raw + b"x", b"INVALID!" + raw[8:]):
            with self.subTest(size=len(value)):
                (self.root / "ann_trace.bin").write_bytes(value)
                self.assertFalse(trace.export_trace(self.root, self.manifest)["trace_valid"])

    def test_sampling_or_mode_mismatch_rejected(self):
        (self.root / "ann_trace.bin").write_bytes(raw_trace())
        for key, value in (("detail_first_n", 2), ("event_capacity", 64)):
            with self.subTest(key=key):
                manifest = copy.deepcopy(self.manifest); manifest["trace_config"][key] = value
                self.assertFalse(trace.export_trace(self.root, manifest)["trace_valid"])

    def test_trace_config_and_env_preserve_canonical_argv(self):
        from test_run_ann_experiment import RunnerTests
        fixture = RunnerTests(); fixture.setUp()
        try:
            options = fixture.cli("--benchmark-profile", "pipeann-b9ec4ba", "--neighbor-type", "pq",
                                  "--causal-trace", "--trace-mode", "DETAIL", "--trace-detail-first-n", "4")
            args = runner.resolve(runner.parser().parse_args(options))
            argv = runner.benchmark_argv(args)
            environment = runner.trace_environment(args, self.root)
            self.assertEqual(environment["PIPEANN_TRACE_DETAIL_FIRST_N"], "4")
            self.assertEqual(environment["PIPEANN_TRACE_OUTPUT"], str(self.root / "ann_trace.bin"))
            self.assertEqual(len(argv), 13)
            self.assertNotIn("DETAIL", argv)
            for extra in (("--trace-detail-first-n", "0"), ("--trace-event-capacity", "0"),
                          ("--benchmark-profile", "legacy-research"), ("--search-mode", "1")):
                with self.assertRaises(ValueError): runner.resolve(runner.parser().parse_args([*options, *extra]))
        finally:
            fixture.tearDown()

    def test_causal_dry_run_and_missing_output_are_explicit(self):
        from test_run_ann_experiment import RunnerTests
        fixture = RunnerTests(); fixture.setUp()
        try:
            code, preview = fixture.execute("--benchmark-profile", "pipeann-b9ec4ba", "--neighbor-type", "pq",
                                            "--causal-trace", "--trace-mode", "DETAIL", "--dry-run")
            self.assertEqual(code, 0)
            self.assertTrue(preview["causal_trace_enabled"])
            self.assertFalse(fixture.evidence.exists())
            code, result = fixture.execute("--benchmark-profile", "pipeann-b9ec4ba", "--neighbor-type", "pq", "--causal-trace")
            self.assertEqual(code, 1)
            self.assertEqual(result["run_status"], "success")  # ANN succeeded; tracing is separately invalid.
            health = json.loads((Path(result["run_directory"]) / "trace_health.json").read_text())
            self.assertFalse(health["trace_valid"])
        finally:
            fixture.tearDown()


if __name__ == "__main__":
    unittest.main()
