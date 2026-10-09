#!/usr/bin/env python3
"""Check source-audited PipeANN causal invariants; no performance/hypothesis verdict."""
import argparse
from collections import defaultdict, deque
import json
from pathlib import Path
import sys

EVENTS = ("QUERY_START", "QUERY_END", "WIDTH_INIT", "WIDTH_CHANGE", "IO_SELECT",
          "IO_SUBMIT", "IO_CQE_SEEN", "IO_PUBLISH", "NODE_EXPAND", "TRACE_HEALTH", "IO_CACHE_READY")


def check_events(events, expected_qids=None):
    groups = defaultdict(list)
    errors = []
    counts = defaultdict(int)
    for position, event in enumerate(events):
        qid = event.get("query_id")
        if not isinstance(qid, int) or isinstance(qid, bool) or qid < 0:
            errors.append(f"event {position}: invalid query_id")
            continue
        groups[qid].append(event)
        counts[event.get("event")] += 1
    if expected_qids is not None and (len(expected_qids) != len(set(expected_qids)) or set(groups) != set(expected_qids)):
        errors.append("Exact requested/observed sample membership mismatch")
    for qid, rows in groups.items():
        requests, queue, published_nodes = {}, deque(), set()
        started = ended = health = initialized = False
        width = wcap = None
        previous_time = -1
        cumulative = dict(submitted=0, cqe_seen=0, published=0, expanded=0, cache_ready=0, cache_published=0)
        identity = None
        def fail(reason):
            errors.append(f"query {qid}: {reason}")
        for event in rows:
            kind = event.get("event")
            timestamp = event.get("timestamp_ns")
            if kind not in EVENTS:
                fail(f"unknown event {kind}")
                continue
            if not isinstance(timestamp, int) or timestamp < previous_time:
                fail("invalid/nonmonotonic timestamp")
            else:
                previous_time = timestamp
            current_identity = (event.get("worker_id"), event.get("linux_tid"))
            if (not isinstance(current_identity[0], int) or current_identity[0] < 0 or
                    not isinstance(current_identity[1], int) or current_identity[1] <= 0):
                fail("invalid worker/thread identity")
            if identity is None:
                identity = current_identity
            if current_identity != identity:
                fail("worker/thread changed within query")
            if kind == "QUERY_START":
                if started: fail("duplicate QUERY_START")
                started = True
            elif not started:
                fail("event before QUERY_START")
            if ended and kind != "TRACE_HEALTH":
                fail("event after QUERY_END")
            if kind == "WIDTH_INIT":
                if initialized: fail("duplicate WIDTH_INIT")
                initialized = True
                width, wcap = event.get("width"), event.get("wcap")
                if not isinstance(wcap, int) or wcap < 1 or width != min(4, wcap):
                    fail("width init must equal min(4,Wcap)")
            elif kind == "WIDTH_CHANGE":
                new = event.get("width")
                if width is None or event.get("old_width") != width or not isinstance(new, int):
                    fail("width change has no matching old width")
                elif new < width:
                    fail("width decrease")
                elif new > width + 1:
                    fail("width jump greater than 1")
                width = new
            if event.get("width") is not None:
                actual = event["width"]
                if not initialized or not isinstance(actual, int) or not isinstance(wcap, int) or not 1 <= actual <= wcap:
                    fail("width out of bounds/uninitialized")
                elif actual != width or event.get("wcap") != wcap:
                    fail("width snapshot inconsistent")
            seq = event.get("request_seq")
            if kind == "IO_SELECT":
                if not isinstance(seq, int) or seq < 1 or seq in requests:
                    fail("duplicate/invalid request_seq")
                elif seq != len(requests) + 1:
                    fail("request_seq not monotonic")
                else:
                    if not isinstance(event.get("request_key"), int) or event["request_key"] <= 1:
                        fail("invalid request correlation key")
                    requests[seq] = {"state": "selected", "key": event.get("request_key"), "node": event.get("node_id")}
                    queue.append(seq)
            elif kind in ("IO_SUBMIT", "IO_CQE_SEEN", "IO_CACHE_READY", "IO_PUBLISH"):
                request = requests.get(seq)
                if request is None:
                    fail(f"{kind} without selected request/submit")
                else:
                    if event.get("request_key") != request["key"] or event.get("node_id") != request["node"]:
                        fail("correlation identity changed")
                    expected = {"IO_SUBMIT": ("selected",), "IO_CQE_SEEN": ("submitted",),
                                "IO_CACHE_READY": ("selected",), "IO_PUBLISH": ("cqe", "cache")}[kind]
                    if request["state"] not in expected:
                        fail(f"{kind} violates submit/CQE/publish order")
                    if kind == "IO_SUBMIT":
                        request["state"] = "submitted"; cumulative["submitted"] += 1
                    elif kind == "IO_CQE_SEEN":
                        request["state"] = "cqe"; cumulative["cqe_seen"] += 1
                        if event.get("cqe_result") is not None and event["cqe_result"] < 0:
                            fail("CQE error")
                        if not isinstance(event.get("poll_cqes"), int) or event["poll_cqes"] < 1:
                            fail("invalid CQE poll batch size")
                    elif kind == "IO_CACHE_READY":
                        request["state"] = "cache"; cumulative["cache_ready"] += 1
                    else:
                        if not queue or queue[0] != seq: fail("publication is not FIFO")
                        if seq in queue: queue.remove(seq)
                        cumulative["cache_published" if request["state"] == "cache" else "published"] += 1
                        request["state"] = "published"
                        published_nodes.add(request["node"])
            elif kind == "NODE_EXPAND":
                cumulative["expanded"] += 1
                if event.get("node_id") not in published_nodes:
                    fail("expanded node not previously published")
                if seq is not None:
                    request = requests.get(seq)
                    if request is None or request["state"] != "published": fail("expand before publish")
            elif kind == "QUERY_END":
                ended = True
                if queue or any(r["state"] != "published" for r in requests.values()):
                    fail("unfinished request at query end")
                if event.get("outstanding_correlations") != 0:
                    fail("nonzero outstanding at query end")
            elif kind == "TRACE_HEALTH":
                if health or not ended: fail("TRACE_HEALTH must follow QUERY_END exactly once")
                health = True
            hidden = cumulative["cqe_seen"] - cumulative["published"]
            if hidden < 0 or event.get("completed_hidden") != hidden:
                fail("negative/inconsistent completed_hidden")
            for key, value in cumulative.items():
                if event.get(key) != value: fail(f"inconsistent {key} counter")
            if event.get("outstanding_correlations") != sum(r["state"] != "published" for r in requests.values()):
                fail("inconsistent outstanding correlations")
            if event.get("events_dropped", 0) or event.get("ordering_violations", 0):
                fail("runtime drops/ordering violations")
        if not (started and ended and initialized and health):
            fail("missing query boundary/width init/health")
    return {"schema_version": 1, "trace_valid": not errors, "queries_checked": len(groups),
            "events_checked": sum(counts.values()), "event_counts": dict(counts),
            "errors": errors[:100], "error_count": len(errors)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events", type=Path)
    parser.add_argument("--health", type=Path, help="Also require zero loss/unmatched and valid sampling")
    args = parser.parse_args()
    try:
        events = [json.loads(line) for line in args.events.read_text().splitlines() if line.strip()]
        health = json.loads(args.health.read_text()) if args.health else None
        expected = health.get("requested_sample_qids") if health else None
        result = check_events(events, expected_qids=expected)
        if args.health:
            health = json.loads(args.health.read_text())
            if health.get("schema_version") == 3:
                from trace_sampling import explicit_policy
                policy = health["sample_policy"]
                validated = explicit_policy(policy["qids"], health["query_rows"])
                if policy != validated or health["sampling_sha256"] != validated["sha256"] or expected != policy["qids"] or health["observed_sample_qids"] != expected:
                    raise ValueError("Sample health identity/digest mismatch")
                origin, end = health["benchmark_origin_ns"], health["benchmark_end_ns"]
                if not 0 < origin <= end or health["benchmark_duration_ns"] != end-origin:
                    raise ValueError("Invalid benchmark phase bounds")
                if any(e.get("benchmark_relative_ns") != e["timestamp_ns"]-origin or not origin <= e["timestamp_ns"] <= end for e in events):
                    raise ValueError("Invalid benchmark-relative event time")
                if any(health.get(k, 0) for k in ("events_dropped", "table_overflows", "unmatched_submit", "unmatched_cqe", "unmatched_publish", "ordering_violations", "negative_hidden_count", "outstanding_at_query_end")):
                    raise ValueError("Nonzero trace failure counter")
            if not health.get("trace_valid") or health.get("sample_observed") != health.get("sample_requested"):
                result["trace_valid"] = False
                result["errors"].append("trace health invalid/incomplete sampling")
                result["error_count"] += 1
            if health.get("trace_mode") == "DETAIL" and result["queries_checked"] != health.get("sample_observed"):
                result["trace_valid"] = False
                result["errors"].append("sample events missing")
                result["error_count"] += 1
    except (OSError, ValueError, TypeError, KeyError) as error:
        result = {"trace_valid": False, "errors": [str(error)], "error_count": 1}
    print(json.dumps(result, indent=2))
    return 0 if result["trace_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
