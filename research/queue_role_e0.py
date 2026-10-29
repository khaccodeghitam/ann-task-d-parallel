#!/usr/bin/env python3
"""E0 deterministic *synthetic* two-stage queue-role scheduling model.

NOT an implementation or replay of Speed-ANN, iQAN, AverSearch, or PipeANN.
All jobs are frozen in advance, so candidate selection and Recall cannot change.
Only scheduling and queue starvation are modeled. Time is model ticks, NOT ms.
"""
import argparse
from collections import deque
from dataclasses import dataclass
import json


@dataclass
class Worker:
    role: str
    job: int | None = None
    left: int = 0
    switching: int = 0


def run_model(*, policy="fixed", n_jobs=120, n_cores=4,
              maintain_ticks=4, distance_ticks=1, switch_ticks=2,
              epoch=4, ready_low=1, ready_high=5):
    """Compare fixed (1 maintainer) vs queue-responsive (1 or 2).

    One frozen list of jobs: each job must be maintained then distance-evaluated.
    All model policies finish the SAME work. No graph or ANN Recall is evaluated.
    Role changes occur only while idle; no job is preempted or duplicated.
    """
    if policy not in {"fixed", "responsive"}:
        raise ValueError("Unknown policy")
    vals = (n_jobs, n_cores, maintain_ticks, distance_ticks, epoch)
    if any(not isinstance(x, int) or x < 1 for x in vals) or n_cores < 3:
        raise ValueError("n_jobs, n_cores >= 3, costs and epoch must be positive integers")
    if not isinstance(switch_ticks, int) or switch_ticks < 0:
        raise ValueError("switch_ticks must be nonnegative integer")
    if not 0 <= ready_low < ready_high:
        raise ValueError("Expected 0 <= ready_low < ready_high")

    pending = deque(range(n_jobs))
    ready = deque()
    completed = []
    workers = [Worker("maint")] + [Worker("dist") for _ in range(n_cores - 1)]
    switches = 0
    idle_distance = 0
    desired_maintainers = 1
    max_ticks = n_jobs * (maintain_ticks + distance_ticks + switch_ticks + 5) * 3
    for tick in range(max_ticks):
        if policy == "responsive" and tick % epoch == 0:
            if pending and len(ready) <= ready_low:
                desired_maintainers = 2
            elif len(ready) >= ready_high or not pending:
                desired_maintainers = 1

        if policy == "responsive":
            n_maintainers = sum(w.role == "maint" for w in workers)
            if n_maintainers < desired_maintainers:
                # Move one *idle* distance worker; do not preempt its task.
                for w in workers:
                    if w.role == "dist" and w.job is None and w.switching == 0:
                        w.role, w.switching = "maint", switch_ticks
                        switches += 1
                        break
            elif n_maintainers > desired_maintainers:
                for w in workers:
                    if w.role == "maint" and w.job is None and w.switching == 0:
                        w.role, w.switching = "dist", switch_ticks
                        switches += 1
                        break

        produced = []
        results = []
        for w in workers:
            if w.switching:
                w.switching -= 1
                continue
            if w.job is None:
                queue = pending if w.role == "maint" else ready
                if queue:
                    w.job = queue.popleft()
                    w.left = maintain_ticks if w.role == "maint" else distance_ticks
                elif w.role == "dist" and pending:
                    idle_distance += 1
            if w.job is not None:
                w.left -= 1
                if w.left == 0:
                    (produced if w.role == "maint" else results).append(w.job)
                    w.job = None
        # Results published on next tick, not instantaneously to later workers.
        ready.extend(produced)
        completed.extend(results)
        if len(completed) == n_jobs:
            if len(set(completed)) != n_jobs or pending or ready or any(w.job is not None for w in workers):
                raise AssertionError("Model duplicated or dropped jobs")
            return dict(policy=policy, n_jobs=n_jobs, n_cores=n_cores,
                        maintain_ticks=maintain_ticks, distance_ticks=distance_ticks,
                        switch_ticks=switch_ticks, epoch=epoch,
                        ticks=tick + 1, idle_distance_worker_ticks=idle_distance,
                        role_switches=switches, all_jobs_completed=True,
                        job_ids=sorted(completed),
                        evidence="SYNTHETIC_MODEL_ONLY_NOT_ANN_LATENCY_OR_RECALL")
    raise RuntimeError("Model did not finish within its bounded tick budget")


def compare(**kwargs):
    original = run_model(policy="fixed", **kwargs)
    proposed = run_model(policy="responsive", **kwargs)
    assert original["job_ids"] == proposed["job_ids"] == list(range(original["n_jobs"]))
    return dict(fixed={k:v for k,v in original.items() if k != "job_ids"},
                responsive={k:v for k,v in proposed.items() if k != "job_ids"},
                model_speed_ratio=round(original["ticks"] / proposed["ticks"], 6),
                same_frozen_work=True,
                caveat="No ANN search or Recall; ratio refers only to synthetic model ticks")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--jobs", type=int, default=120)
    ap.add_argument("--cores", type=int, default=4)
    ap.add_argument("--maintain-ticks", type=int, default=4)
    ap.add_argument("--distance-ticks", type=int, default=1)
    ap.add_argument("--switch-ticks", type=int, default=2)
    ap.add_argument("--epoch", type=int, default=4)
    args=ap.parse_args()
    result=compare(n_jobs=args.jobs,n_cores=args.cores,maintain_ticks=args.maintain_ticks,
                   distance_ticks=args.distance_ticks,switch_ticks=args.switch_ticks,epoch=args.epoch)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
