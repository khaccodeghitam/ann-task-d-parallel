#!/usr/bin/env python3
"""MODEL_ONLY: deterministic open two-stage pipeline, NOT AverSearch or ANN.

Jobs are all available at t=0; maintenance precedes distance service. There is
no graph, feedback, pruning, redundancy, memory contention or Recall. All times
are integer model ticks. See docs/research/AVERSEARCH_QUEUE_ROLE_E0.md.
"""
import argparse
from collections import Counter, deque
from dataclasses import dataclass
from itertools import product
import json


@dataclass
class Worker:
    role: str
    job: int | None = None
    left: int = 0
    monitoring: int = 0
    switching: int = 0
    target: str | None = None


ACTIVITIES = ("maintenance", "distance", "monitoring", "switching",
              "idle_maintenance", "starved_distance", "drain_idle_distance")


def choose_role(role, pending, ready, low, high):
    """Only current queue counts; no job durations, GT or future information."""
    if pending and ready <= low:
        return "maint"
    if not pending or ready >= high:
        return "dist"
    return role


def _integer(name, value, minimum):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def run_model(*, policy="fixed", n_jobs=120, n_cores=4,
              maintain_ticks=4, distance_ticks=1, switch_ticks=2,
              monitor_ticks=1, epoch=4, ready_low=1, ready_high=5,
              initial_maintainers=1, trace=False):
    """Fixed, observation-only, or responsive roles; one optional helper.

    Worker 0 is always maintenance, workers 2..P-1 always distance. Only worker
    1 may change role. A decision is sampled at an epoch AND an idle boundary.
    Sampling occupies that helper for monitor_ticks; a changed role then pays
    switch_ticks. The snapshot is intentionally stale after these delays.
    Busy jobs are never preempted. Publications at t+1 cannot be consumed at t.
    """
    if policy not in {"fixed", "observe", "responsive"}:
        raise ValueError("Unknown policy")
    for name, value, minimum in (
        ("n_jobs", n_jobs, 0), ("n_cores", n_cores, 3),
        ("maintain_ticks", maintain_ticks, 1), ("distance_ticks", distance_ticks, 1),
        ("switch_ticks", switch_ticks, 0), ("monitor_ticks", monitor_ticks, 0),
        ("epoch", epoch, 1), ("ready_low", ready_low, 0),
        ("ready_high", ready_high, 1), ("initial_maintainers", initial_maintainers, 1),
    ):
        _integer(name, value, minimum)
    if ready_low >= ready_high or initial_maintainers not in (1, 2):
        raise ValueError("Require ready_low < ready_high and 1 or 2 initial maintainers")
    if type(trace) is not bool:
        raise ValueError("trace must be boolean")

    workers = [Worker("maint" if i < initial_maintainers else "dist")
               for i in range(n_cores)]
    helper = workers[1]
    pending, ready = deque(range(n_jobs)), deque()
    completed, maintained, events = [], [], []
    activity = Counter({key: 0 for key in ACTIVITIES})
    decisions = switches = tick = 0

    def event(kind, worker, **data):
        if trace:
            events.append(dict(tick=tick, kind=kind, worker=worker, **data))

    # Permanent producer and consumer ensure progress. Even if the helper never
    # serves a job, each job can traverse both stages in this conservative bound.
    limit = n_jobs * (maintain_ticks + distance_ticks) + 1
    while len(completed) < n_jobs:
        if tick >= limit:
            raise RuntimeError("Model violated its permanent-worker progress bound")
        # Apply a previously sampled decision only AFTER monitoring has elapsed.
        # Do not immediately resample on a decision's application boundary.
        applying = helper.target is not None
        if (policy != "fixed" and tick % epoch == 0 and not applying
                and helper.job is None and not helper.switching):
            target = choose_role(helper.role, len(pending), len(ready), ready_low, ready_high)
            helper.target = target if policy == "responsive" else helper.role
            helper.monitoring = monitor_ticks
            decisions += 1
            event("sample", 1, pending=len(pending), ready=len(ready), target=helper.target)
        if helper.target is not None and not helper.monitoring:
            if helper.role != helper.target:
                helper.role = helper.target
                helper.switching = switch_ticks
                switches += 1
                event("switch", 1, role=helper.role)
            helper.target = None

        # Snapshot before dispatch/service: last in-flight maintenance still
        # starves an empty distance queue, independently of worker loop order.
        upstream_live = bool(pending) or any(
            w.role == "maint" and w.job is not None for w in workers)
        produced, results = [], []
        for i, worker in enumerate(workers):
            if worker.monitoring:
                worker.monitoring -= 1
                activity["monitoring"] += 1
                continue
            if worker.switching:
                worker.switching -= 1
                activity["switching"] += 1
                continue
            if worker.job is None:
                queue = pending if worker.role == "maint" else ready
                if queue:
                    worker.job = queue.popleft()
                    worker.left = maintain_ticks if worker.role == "maint" else distance_ticks
                    event("start", i, role=worker.role, job=worker.job)
                else:
                    key = ("idle_maintenance" if worker.role == "maint" else
                           "starved_distance" if upstream_live else "drain_idle_distance")
                    activity[key] += 1
                    continue
            activity["maintenance" if worker.role == "maint" else "distance"] += 1
            worker.left -= 1
            if worker.left == 0:
                (produced if worker.role == "maint" else results).append(worker.job)
                event("finish", i, role=worker.role, job=worker.job)
                worker.job = None
        ready.extend(produced)
        maintained.extend(produced)
        completed.extend(results)
        tick += 1

    expected = list(range(n_jobs))
    if (sorted(maintained) != expected or sorted(completed) != expected
            or pending or ready or any(w.job is not None for w in workers)
            or activity["maintenance"] != n_jobs * maintain_ticks
            or activity["distance"] != n_jobs * distance_ticks
            or sum(activity.values()) != n_cores * tick):
        raise AssertionError("Job conservation or worker-time accounting failed")
    result = dict(
        evidence="MODEL_ONLY", model_version=2, policy=policy,
        config=dict(n_jobs=n_jobs, n_cores=n_cores, maintain_ticks=maintain_ticks,
                    distance_ticks=distance_ticks, switch_ticks=switch_ticks,
                    monitor_ticks=monitor_ticks, epoch=epoch, ready_low=ready_low,
                    ready_high=ready_high, initial_maintainers=initial_maintainers),
        ticks=tick, worker_ticks=dict(activity), decisions=decisions,
        role_switches=switches, all_jobs_completed=True, job_ids=sorted(completed),
        # A job-completion horizon may truncate an irrelevant helper transition.
        unfinished_helper_overhead_ticks=helper.monitoring + helper.switching,
    )
    if trace:
        result["events"] = events
    return result


def compare(**kwargs):
    """Same work against BOTH static allocations and a monitoring-only control."""
    outputs = {}
    for name, policy, count in (("fixed", "fixed", 1), ("fixed_two", "fixed", 2),
                                ("observe", "observe", 1), ("responsive", "responsive", 1)):
        outputs[name] = run_model(policy=policy, initial_maintainers=count, **kwargs)
    if any(r["job_ids"] != outputs["fixed"]["job_ids"] for r in outputs.values()):
        raise AssertionError("Policies did not complete identical work")
    for result in outputs.values():
        del result["job_ids"]
    ticks = outputs["responsive"]["ticks"]
    return dict(evidence="MODEL_ONLY", **outputs, same_frozen_work=True,
                fixed_over_responsive=outputs["fixed"]["ticks"] / ticks if ticks else None,
                best_static_over_responsive=min(outputs["fixed"]["ticks"],
                                               outputs["fixed_two"]["ticks"]) / ticks if ticks else None,
                caveat="Open pipeline makespan only; no ANN, Recall or hardware speedup")


def suite():
    """108 prespecified homogeneous cases; no fitted thresholds or random seeds."""
    return [dict(parameters=dict(n_jobs=n, maintain_ticks=m, distance_ticks=d,
                                 switch_ticks=s, monitor_ticks=o),
                 comparison=compare(n_jobs=n, maintain_ticks=m, distance_ticks=d,
                                    switch_ticks=s, monitor_ticks=o))
            for n, m, d, s, o in product((16, 120), (1, 2, 6), (1, 5), (0, 1, 40), (0, 1, 4))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", action="store_true", help="emit the full fixed sensitivity matrix")
    for name, default in (("jobs", 120), ("cores", 4), ("maintain-ticks", 4),
                          ("distance-ticks", 1), ("switch-ticks", 2), ("monitor-ticks", 1),
                          ("epoch", 4), ("ready-low", 1), ("ready-high", 5)):
        parser.add_argument("--" + name, type=int, default=default)
    args = parser.parse_args()
    result = suite() if args.suite else compare(
        n_jobs=args.jobs, n_cores=args.cores, maintain_ticks=args.maintain_ticks,
        distance_ticks=args.distance_ticks, switch_ticks=args.switch_ticks,
        monitor_ticks=args.monitor_ticks, epoch=args.epoch,
        ready_low=args.ready_low, ready_high=args.ready_high)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
