"""Dataset-free scheduling/accounting checks, not tests of ANN behavior."""
import importlib.util
from itertools import product
from pathlib import Path
import sys
import unittest

FILE = Path(__file__).resolve().parents[2] / "research" / "queue_role_e0.py"
spec = importlib.util.spec_from_file_location("queue_role_e0", FILE)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def static_oracle(n, p, m, a, b):
    """Independent continuous event recurrence for identical FIFO jobs."""
    producers, consumers = [0] * m, [0] * (p - m)
    finishes = []
    for _ in range(n):
        i = min(range(m), key=producers.__getitem__)
        producers[i] += a
        finishes.append(producers[i])
    for release in sorted(finishes):
        i = min(range(p - m), key=consumers.__getitem__)
        consumers[i] = max(consumers[i], release) + b
    return max(consumers)


class E0ModelTests(unittest.TestCase):
    def test_static_matches_independent_event_oracle(self):
        for n, p, m, a, b in product(range(9), (3, 4, 6), (1, 2), (1, 3, 7), (1, 2, 5)):
            with self.subTest(n=n, p=p, m=m, a=a, b=b):
                r = module.run_model(n_jobs=n, n_cores=p, initial_maintainers=m,
                                     maintain_ticks=a, distance_ticks=b)
                self.assertEqual(r["ticks"], static_oracle(n, p, m, a, b))

    def test_last_inflight_maintenance_counts_as_starvation(self):
        r = module.run_model(n_jobs=1, maintain_ticks=6, distance_ticks=1)
        self.assertEqual(r["ticks"], 7)
        self.assertEqual(r["worker_ticks"], dict(maintenance=6, distance=1, monitoring=0,
            switching=0, idle_maintenance=1, starved_distance=18, drain_idle_distance=2))

    def test_publication_not_visible_to_later_worker_in_same_tick(self):
        r = module.run_model(n_jobs=5, maintain_ticks=1, distance_ticks=1, trace=True)
        finish = {e["job"]: e["tick"] for e in r["events"]
                  if e["kind"] == "finish" and e["role"] == "maint"}
        for e in r["events"]:
            if e["kind"] == "start" and e["role"] == "dist":
                self.assertGreater(e["tick"], finish[e["job"]])

    def test_monitoring_then_switch_cost_delays_helper(self):
        r = module.run_model(policy="responsive", n_jobs=20, maintain_ticks=6,
                             monitor_ticks=2, switch_ticks=3, trace=True)
        events = [e for e in r["events"] if e["worker"] == 1]
        self.assertEqual([(e["kind"], e["tick"]) for e in events[:3]],
                         [("sample", 0), ("switch", 2), ("start", 5)])

    def test_decisions_at_idle_epochs_and_no_preemption(self):
        r = module.run_model(policy="responsive", n_jobs=51, maintain_ticks=3,
                             distance_ticks=7, monitor_ticks=2, switch_ticks=5, epoch=4, trace=True)
        busy = {}
        for e in r["events"]:
            i = e["worker"]
            if e["kind"] in ("sample", "switch"):
                self.assertNotIn(i, busy)
            if e["kind"] == "sample":
                self.assertEqual(e["tick"] % 4, 0)
            if e["kind"] == "start":
                self.assertNotIn(i, busy)
                busy[i] = e
            if e["kind"] == "finish":
                start = busy.pop(i)
                cost = 3 if e["role"] == "maint" else 7
                self.assertEqual(e["tick"] - start["tick"] + 1, cost)
                self.assertEqual(e["job"], start["job"])
        self.assertFalse(busy)

    def test_empty_input_and_zero_ratio(self):
        r = module.compare(n_jobs=0)
        for name in ("fixed", "fixed_two", "observe", "responsive"):
            self.assertEqual(r[name]["ticks"], 0)
            self.assertEqual(sum(r[name]["worker_ticks"].values()), 0)
            self.assertEqual(r[name]["decisions"], 0)
        self.assertIsNone(r["fixed_over_responsive"])

    def test_terminal_overhead_is_charged_only_until_job_completion(self):
        r = module.run_model(policy="responsive", n_jobs=1, maintain_ticks=1,
                             distance_ticks=1, monitor_ticks=10, switch_ticks=40)
        self.assertEqual(r["ticks"], 2)
        self.assertEqual(r["worker_ticks"]["monitoring"], 2)
        self.assertEqual(r["worker_ticks"]["switching"], 0)
        self.assertEqual(r["unfinished_helper_overhead_ticks"], 8)

    def test_static_better_control_for_maintenance_bottleneck(self):
        r = module.compare(n_jobs=120, maintain_ticks=6, distance_ticks=1,
                           switch_ticks=1, monitor_ticks=1)
        self.assertLess(r["responsive"]["ticks"], r["fixed"]["ticks"])
        self.assertLessEqual(r["fixed_two"]["ticks"], r["responsive"]["ticks"])

    def test_costly_adaptation_can_lose(self):
        r = module.compare(n_jobs=16, maintain_ticks=1, distance_ticks=5,
                           switch_ticks=40, monitor_ticks=1)
        self.assertGreater(r["responsive"]["ticks"], r["fixed"]["ticks"])

    def test_zero_cost_observer_is_identical_work_schedule(self):
        args = dict(n_jobs=37, maintain_ticks=2, distance_ticks=5, monitor_ticks=0)
        a, b = (module.run_model(policy=p, **args) for p in ("fixed", "observe"))
        self.assertEqual(a["ticks"], b["ticks"])
        self.assertEqual(a["worker_ticks"], b["worker_ticks"])
        self.assertEqual(b["role_switches"], 0)

    def test_monitor_cost_is_measured_without_role_changes(self):
        r = module.run_model(policy="observe", n_jobs=120, maintain_ticks=1,
                             distance_ticks=5, monitor_ticks=4)
        self.assertGreater(r["worker_ticks"]["monitoring"], 0)
        self.assertEqual(r["role_switches"], 0)

    def test_hysteresis_and_terminal_signal(self):
        f = module.choose_role
        self.assertEqual(f("dist", 3, 1, 1, 5), "maint")
        self.assertEqual(f("maint", 3, 5, 1, 5), "dist")
        for role in ("maint", "dist"):
            self.assertEqual(f(role, 3, 3, 1, 5), role)
            self.assertEqual(f(role, 0, 0, 1, 5), "dist")

    def test_large_epoch_does_not_deadlock(self):
        r = module.run_model(policy="responsive", n_jobs=3, n_cores=3,
                             epoch=10000, monitor_ticks=1000, switch_ticks=1000)
        self.assertEqual(r["job_ids"], [0, 1, 2])
        self.assertEqual(r["decisions"], 1)

    def test_same_work_time_partition_and_determinism(self):
        for policy, n, p, m, d, o, s in product(("fixed", "observe", "responsive"),
                (1, 7), (3, 5), (1, 4), (1, 5), (0, 2), (0, 9)):
            args = dict(policy=policy, n_jobs=n, n_cores=p, maintain_ticks=m,
                        distance_ticks=d, monitor_ticks=o, switch_ticks=s)
            r = module.run_model(**args)
            self.assertEqual(r, module.run_model(**args))
            self.assertEqual(r["job_ids"], list(range(n)))
            self.assertEqual(sum(r["worker_ticks"].values()), p * r["ticks"])
            self.assertEqual(r["worker_ticks"]["maintenance"], n * m)
            self.assertEqual(r["worker_ticks"]["distance"], n * d)

    def test_strict_integer_validation(self):
        names = ("n_jobs", "n_cores", "maintain_ticks", "distance_ticks", "epoch",
                 "switch_ticks", "monitor_ticks", "ready_low", "ready_high", "initial_maintainers")
        for name, value in product(names, (True, False, 1.0, "1", None, float("nan"), -1)):
            with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                module.run_model(**{name: value})
        for args in (dict(n_cores=2), dict(maintain_ticks=0), dict(distance_ticks=0),
                     dict(epoch=0), dict(ready_low=5), dict(initial_maintainers=3),
                     dict(policy="unknown"), dict(trace=1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                module.run_model(**args)


if __name__ == "__main__":
    unittest.main()
