"""Post-run conversion of fixed numeric PANTRC01 traces into local readable evidence."""
import csv
import json
from pathlib import Path
import struct
import sys

from check_causal_trace import check_events, EVENTS

NA = (1 << 64) - 1
EVENT_FIELDS = ("type", "timestamp_ns", "query_id", "worker_id", "linux_tid", "ring_id",
    "request_seq", "request_key", "node_id", "page_id", "location", "offset", "length",
    "width", "wcap", "old_width", "cur_n_in", "cur_tot", "n_in", "n_out", "max_marker",
    "inflight_count", "poll_cqes", "submitted", "cqe_seen", "published", "expanded",
    "completed_hidden", "cache_ready", "cache_published", "events_dropped",
    "ordering_violations", "outstanding_correlations", "cqe_result")
COUNTER_FIELDS = ("query_id", "worker_id", "linux_tid", "is_sampled", "selected", "submitted",
    "cqe_seen", "published", "expanded", "poll_calls", "cqe_count", "max_completed_hidden",
    "initial_width", "final_width", "width_change_count", "max_inflight", "events_dropped",
    "unmatched_submit", "unmatched_cqe", "unmatched_publish", "ordering_violations",
    "negative_hidden_count", "outstanding_at_query_end", "cache_ready", "cache_published",
    "latency_ns", "table_overflows", "events_written")
QUERY_COLUMNS = ("schema_version", "run_id", "trace_mode", *COUNTER_FIELDS, "latency_us")
HEADER = struct.Struct("<8s10Q")
MODES = ("OFF", "LIGHT", "DETAIL")
FAILURE_COUNTERS = ("events_dropped", "unmatched_submit", "unmatched_cqe", "unmatched_publish",
                    "ordering_violations", "negative_hidden_count", "outstanding_at_query_end", "table_overflows")


def read_raw(path):
    raw = Path(path).read_bytes()
    if len(raw) < HEADER.size:
        raise ValueError("Missing/truncated raw trace header")
    magic, version, mode, workers, capacity, first_n, queries, nevents, nrows, ef, cf = HEADER.unpack_from(raw)
    if magic != b"PANTRC01" or version != 1 or mode >= len(MODES) or ef != len(EVENT_FIELDS) or cf != len(COUNTER_FIELDS):
        raise ValueError("Unknown raw trace protocol/layout")
    if not workers or not capacity or nevents > workers * capacity or nrows != (0 if mode == 0 else queries):
        raise ValueError("Invalid raw trace dimensions")
    event_size, row_size = ef * 8, cf * 8
    expected = HEADER.size + nevents * event_size + nrows * row_size
    if len(raw) != expected:
        raise ValueError("Truncated/trailing raw trace data")
    events = []
    for offset in range(HEADER.size, HEADER.size + nevents * event_size, event_size):
        values = struct.unpack_from(f"<{ef}Q", raw, offset)
        kind = values[0]
        if not 1 <= kind <= len(EVENTS): raise ValueError("Unknown event code")
        event = {field: None if value == NA else value for field, value in zip(EVENT_FIELDS, values)}
        event.pop("type")
        event.update(schema_version=2, source="ann", event=EVENTS[kind - 1])
        if kind == 7:  # CQE result is signed, including -1 (otherwise NA in unused fields).
            result = values[-1]
            event["cqe_result"] = result - (1 << 64) if result >= (1 << 63) else result
        events.append(event)
    rows = []
    begin = HEADER.size + nevents * event_size
    for offset in range(begin, len(raw), row_size):
        values = struct.unpack_from(f"<{cf}Q", raw, offset)
        rows.append({field: None if value == NA else value for field, value in zip(COUNTER_FIELDS, values)})
    return {"trace_mode": MODES[mode], "workers": workers, "buffer_capacity": capacity,
            "first_n": first_n, "queries": queries}, events, rows


def export_trace(directory, manifest):
    directory = Path(directory)
    base = {"schema_version": 2, "trace_mode": manifest["trace_mode"],
            "sample_policy": {"kind": "first_n", "first_n": manifest["trace_config"]["detail_first_n"]},
            "sample_requested": 0, "sample_observed": 0,
            "buffer_capacity": manifest["trace_config"]["event_capacity"],
            "events_written": 0, "trace_valid": False, "ann_events_available": False,
            **dict.fromkeys((*FAILURE_COUNTERS, "submitted", "cqe_seen", "published", "expanded"), 0)}
    try:
        config, events, rows = read_raw(directory / "ann_trace.bin")
        if config["trace_mode"] != manifest["trace_mode"] or config["queries"] != manifest["query_count"] or config["workers"] != manifest["threads"]:
            raise ValueError("Raw trace mode/query/worker count disagrees with manifest")
        if config["first_n"] != manifest["trace_config"]["detail_first_n"] or config["buffer_capacity"] != manifest["trace_config"]["event_capacity"]:
            raise ValueError("Raw trace sampling/capacity disagrees with manifest")
        requested = min(config["first_n"], config["queries"]) if config["trace_mode"] == "DETAIL" else 0
        if len({r["query_id"] for r in rows}) != len(rows) or any(r["query_id"] != i for i, r in enumerate(rows)):
            raise ValueError("Missing/duplicate query counter rows")
        if any(r["worker_id"] >= config["workers"] or r["linux_tid"] <= 0 or
               r["is_sampled"] != int(config["trace_mode"] == "DETAIL" and r["query_id"] < config["first_n"]) for r in rows):
            raise ValueError("Invalid worker/sample query counters")
        with (directory / "events.jsonl").open("w") as stream:
            for event in events:
                event["run_id"] = manifest["run_id"]
                stream.write(json.dumps(event, allow_nan=False) + "\n")
        with (directory / "query_metrics.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, QUERY_COLUMNS); writer.writeheader()
            for row in rows:
                writer.writerow({"schema_version": 2, "run_id": manifest["run_id"],
                                 "trace_mode": manifest["trace_mode"], **row,
                                 "latency_us": row["latency_ns"] / 1000 if row["latency_ns"] is not None else None})
        checked = check_events(events)
        sums = {field: sum(r[field] or 0 for r in rows) for field in COUNTER_FIELDS if field not in
                ("query_id", "worker_id", "linux_tid", "initial_width", "final_width", "latency_ns")}
        if sums["events_written"] != len(events):
            raise ValueError("Event count disagrees with query counters")
        health = {**base, **sums,
                  **{key: max((r[key] for r in rows), default=0) for key in ("max_completed_hidden", "max_inflight")},
                  "sample_requested": requested, "sample_observed": sums["is_sampled"],
                  "events_written": len(events), "ann_events_available": bool(events),
                  "query_rows": len(rows), "event_counts": checked["event_counts"],
                  "invariant_errors": checked["errors"], "invariant_error_count": checked["error_count"]}
        counter_ok = all(not sums[key] for key in FAILURE_COUNTERS)
        counter_ok &= sums["submitted"] == sums["cqe_seen"] == sums["published"]
        counter_ok &= sums["selected"] == sums["submitted"] + sums["cache_ready"]
        counter_ok &= sums["cache_ready"] == sums["cache_published"]
        counter_ok &= sums["cqe_count"] == sums["cqe_seen"]
        counter_ok &= all(r["initial_width"] == min(4, manifest["wcap"]) and
                          r["initial_width"] <= r["final_width"] <= manifest["wcap"] for r in rows)
        counter_ok &= all(r["submitted"] == r["cqe_seen"] == r["published"] and
                          r["selected"] == r["submitted"] + r["cache_ready"] and
                          r["cache_ready"] == r["cache_published"] and r["cqe_count"] == r["cqe_seen"] for r in rows)
        # Sampled event histories must agree with their separately stored query summaries.
        sampled = {r["query_id"]: r for r in rows if r["is_sampled"]}
        grouped = {qid: [] for qid in sampled}
        for event in events:
            if event["query_id"] not in grouped:
                counter_ok = False
            else:
                grouped[event["query_id"]].append(event)
        for qid, row in sampled.items():
            query_events = grouped[qid]
            ends = [e for e in query_events if e["event"] == "QUERY_END"]
            counter_ok &= len(ends) == 1 and len(query_events) == row["events_written"]
            if len(ends) == 1:
                end = ends[0]
                counter_ok &= all(end[k] == row[k] for k in
                    ("submitted", "cqe_seen", "published", "expanded", "cache_ready", "cache_published"))
                counter_ok &= end["width"] == row["final_width"]
            counter_ok &= sum(e["event"] == "IO_SELECT" for e in query_events) == row["selected"]
            counter_ok &= sum(e["event"] == "WIDTH_CHANGE" for e in query_events) == row["width_change_count"]
        health["trace_valid"] = bool(counter_ok and checked["trace_valid"] and
            sums["is_sampled"] == requested and checked["queries_checked"] == requested and
            (config["trace_mode"] == "DETAIL" or not events))
        checked["trace_valid"] = health["trace_valid"]
        if not counter_ok:
            health["health_error"] = "Aggregate counter/width invariants failed"
            checked["errors"].append(health["health_error"])
            checked["error_count"] += 1
        if sums["is_sampled"] != requested or checked["queries_checked"] != requested:
            checked["errors"].append("Incomplete deterministic sample")
            checked["error_count"] += 1
    except (OSError, ValueError, TypeError, KeyError) as error:
        health = {**base, "health_error": f"{type(error).__name__}: {error}"}
        checked = {"schema_version": 1, "trace_valid": False, "errors": [health["health_error"]]}
    for name, value in (("trace_health.json", health), ("trace_check.json", checked)):
        (directory / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    return health


if __name__ == "__main__":
    directory = Path(sys.argv[1])
    health = export_trace(directory, json.loads((directory / "manifest.json").read_text()))
    print(json.dumps(health))
    sys.exit(0 if health["trace_valid"] else 1)
