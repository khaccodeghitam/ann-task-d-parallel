import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools/research"))
import replay_research_history as replay


class ReplayTests(unittest.TestCase):
    def test_numeric_histogram_keys_match_historical_json(self):
        self.assertEqual(replay.canonical_json({32: 5}), replay.canonical_json({"32": 5}))

    def test_key_order_is_not_a_change(self):
        self.assertEqual(replay.canonical_json({"a": 1, "b": 2}),
                         replay.canonical_json({"b": 2, "a": 1}))

    def test_numeric_key_collision_rejected(self):
        with self.assertRaises(ValueError):
            replay.canonical_json({32: 5, "32": 7})

    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):
            replay.canonical_json({"qps": float("nan")})

    def test_boolean_is_not_numeric_equivalence(self):
        self.assertNotEqual(replay.canonical_json({"valid": True}), replay.canonical_json({"valid": 1}))

    def test_run_order_preserved(self):
        self.assertNotEqual(replay.canonical_json(["OFF", "LIGHT"]), replay.canonical_json(["LIGHT", "OFF"]))

    def test_duplicate_file_keys_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "baseline.json"
            p.write_text('{"valid":true,"valid":false}')
            with self.assertRaises(ValueError):
                replay.read_json(p)

    def test_equivalent_result_preserves_baseline_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "baseline.json"
            raw = '{"32": 5}\n'
            p.write_text(raw)
            self.assertTrue(replay.compare_result({32: 5}, p)["exact_json_equality"])
            self.assertEqual(p.read_text(), raw)

    def test_changed_result_rejected_without_rewrite(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "baseline.json"
            p.write_text('{"valid":true}')
            with self.assertRaises(ValueError):
                replay.compare_result({"valid": False}, p)
            self.assertEqual(p.read_text(), '{"valid":true}')

    def test_output_inside_history_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                replay.prepare_output(Path(d), Path(d) / "new")

    def test_existing_output_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "campaigns"
            out = Path(d) / "existing"
            out.mkdir()
            with self.assertRaises(FileExistsError):
                replay.prepare_output(root, out)

    def test_failed_replay_preserves_diagnostic(self):
        with tempfile.TemporaryDirectory() as d:
            root, out = Path(d) / "campaigns", Path(d) / "new"
            with patch.object(replay.importlib, "import_module", side_effect=ValueError("bad evidence")):
                with self.assertRaises(ValueError):
                    replay.replay(root, out)
            self.assertFalse(json.loads((out / "REPLAY.json").read_text())["all_equal"])

    def test_all_five_replays_write_only_new_output(self):
        with tempfile.TemporaryDirectory() as d:
            root, out = Path(d) / "campaigns", Path(d) / "new"
            result = {"classification": "unchanged", "histogram": {32: 5}}
            for name, _, analysis in replay.CAMPAIGNS:
                baseline = root / name / analysis / "analysis.json"
                baseline.parent.mkdir(parents=True)
                baseline.write_text(json.dumps(result))
            before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            module = SimpleNamespace(analyze_campaign=lambda _: result)
            with patch.object(replay.importlib, "import_module", return_value=module):
                report = replay.replay(root, out)
            self.assertTrue(report["all_equal"])
            self.assertEqual(len(report["replays"]), 5)
            self.assertEqual(before, {p: p.read_bytes() for p in root.rglob("*") if p.is_file()})


if __name__ == "__main__":
    unittest.main()
