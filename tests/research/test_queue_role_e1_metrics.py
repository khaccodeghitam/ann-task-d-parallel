"""Artificial exported rows only; no native ANN measurements."""
import copy
import importlib.util
from pathlib import Path
import unittest

FILE = Path(__file__).resolve().parents[2] / "research/queue_role_e1_metrics.py"
spec = importlib.util.spec_from_file_location("queue_role_e1_metrics", FILE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ExportMetricTests(unittest.TestCase):
    def setUp(self):
        self.truth = dict(base_count=200, queries=[dict(query_id=i, ids=list(range(100))) for i in range(2)])
        self.run = dict(base_count=200, search_wall_ns=1000, queries=[
            dict(query_id=0, ids=list(range(100)), latency_ns=100),
            dict(query_id=1, ids=list(range(50, 150)), latency_ns=300)])

    def test_recall_and_percentiles_against_hand_calculation(self):
        r = module.summarize(self.run, self.truth)
        self.assertEqual(r["recall_at_100"], 0.75)
        self.assertEqual(r["qps"], 2_000_000)
        self.assertEqual(r["latency_ns"], dict(p50=200, p95=290, p99=298))
        self.assertEqual(r["scope"], "OFFLINE_EXPORT_METRICS_ONLY")

    def test_query_order_is_not_alignment(self):
        a = module.summarize(self.run, self.truth)
        self.run["queries"].reverse()
        self.assertEqual(a, module.summarize(self.run, self.truth))

    def test_reject_missing_duplicate_and_mismatched_query_ids(self):
        for rows in ([self.run["queries"][0]], [self.run["queries"][0]] * 2,
                     [dict(self.run["queries"][0], query_id=99), self.run["queries"][1]]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                module.summarize(dict(self.run, queries=rows), self.truth)

    def test_reject_bad_ids_and_topk_in_both_inputs(self):
        for which in ("run", "truth"):
            for ids in (list(range(99)), list(range(101)), [0] * 100,
                        [-1] + list(range(99)), [200] + list(range(99)),
                        [True] + list(range(1, 100)), [0.0] + list(range(1, 100))):
                run, truth = copy.deepcopy(self.run), copy.deepcopy(self.truth)
                (run if which == "run" else truth)["queries"][0]["ids"] = ids
                with self.subTest(which=which, ids=ids[:2]), self.assertRaises(ValueError):
                    module.summarize(run, truth)

    def test_reject_nonfinite_or_inconsistent_timing(self):
        for value in (0, -1, True, None, float("nan"), float("inf"), 1001):
            run = copy.deepcopy(self.run)
            run["queries"][0]["latency_ns"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.summarize(run, self.truth)
        for value in (0, -1, True, None, float("nan"), float("inf"), 200):
            with self.subTest(wall=value), self.assertRaises(ValueError):
                module.summarize(dict(self.run, search_wall_ns=value), self.truth)

    def test_reject_mismatched_base_and_empty_input(self):
        for run in (dict(self.run, base_count=201), dict(self.run, queries=[]),
                    dict(self.run, base_count=True), []):
            with self.subTest(run=run), self.assertRaises(ValueError):
                module.summarize(run, self.truth)


if __name__ == "__main__":
    unittest.main()
