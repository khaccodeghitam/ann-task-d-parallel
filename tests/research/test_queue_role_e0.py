"""Dataset-free checks for the E0 scheduling model, not ANN behavior."""
import importlib.util
from pathlib import Path
import sys
import unittest

FILE = Path(__file__).resolve().parents[2] / "research" / "queue_role_e0.py"
spec = importlib.util.spec_from_file_location("queue_role_e0", FILE)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class E0ModelTests(unittest.TestCase):
    def test_same_frozen_work_and_fixed_is_reproducible(self):
        p = dict(n_jobs=31, n_cores=4, maintain_ticks=3, distance_ticks=2)
        a = module.run_model(policy="fixed", **p)
        b = module.run_model(policy="responsive", **p)
        self.assertEqual(a["job_ids"], b["job_ids"])
        self.assertEqual(a, module.run_model(policy="fixed", **p))
        self.assertTrue(a["all_jobs_completed"] and b["all_jobs_completed"])

    def test_maintenance_bottleneck_can_benefit(self):
        r = module.compare(n_jobs=120, n_cores=4, maintain_ticks=6,
                           distance_ticks=1, switch_ticks=1)
        self.assertLess(r["responsive"]["ticks"], r["fixed"]["ticks"])

    def test_responsive_not_guaranteed_to_win(self):
        r = module.compare(n_jobs=16, n_cores=4, maintain_ticks=1,
                           distance_ticks=5, switch_ticks=40)
        self.assertGreaterEqual(r["responsive"]["ticks"], r["fixed"]["ticks"])

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            module.run_model(n_cores=2)
        with self.assertRaises(ValueError):
            module.run_model(switch_ticks=-1)


if __name__ == "__main__":
    unittest.main()
