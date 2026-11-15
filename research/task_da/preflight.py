"""Verify supplied immutable artifacts; never download, build, or benchmark."""
import argparse
import json
from pathlib import Path
import re

from .graph_audit import Graph, audit, sha256


def check_artifact(item, root):
    expected = item.get("reported_sha256")
    if not isinstance(expected, str) or not re.fullmatch("[0-9a-f]{64}", expected):
        return {"status": "NOT_VERIFIED", "reason": "missing/invalid expected SHA256"}
    if not item.get("path"):
        return {"status": "MISSING", "reason": "artifact path not supplied"}
    path = root / item["path"]
    if not path.is_file():
        return {"status": "MISSING", "reason": "file not available"}
    actual = sha256(path)
    return {"status": "AVAILABLE" if actual == expected else "NO-GO",
            "reason": "SHA256 matched" if actual == expected else "SHA256 mismatch",
            "actual_sha256": actual}


def preflight(manifest, root):
    records, blockers = {}, []
    for name, item in manifest["dataset"]["artifacts"].items():
        records[name] = check_artifact(item, root)
    for item in manifest["graphs"]:
        key = item["run_id"]
        records[key] = check_artifact(item, root)
        if records[key]["status"] == "AVAILABLE":
            try:
                with Graph(root / item["path"], "pipnn", entry=manifest["search_policy"]["entry_point"],
                           expected_n=manifest["dataset"]["n"]) as graph:
                    records[key]["structure"] = audit(graph)
            except (ValueError, OSError) as error:
                records[key] = {"status": "NO-GO", "reason": str(error)}
        for field in ("build_source_commit", "build_source_diff_sha256", "seed", "raw_receipt_path"):
            if item.get(field) is None:
                blockers.append(key + ": " + field + " not verified")
    blockers.extend(name + ": " + row["status"] for name, row in records.items() if row["status"] != "AVAILABLE")
    # An availability tool cannot certify host stability, provenance or recall.
    blockers.append("benchmark host stability and raw build provenance require independent review")
    return dict(scope="ARTIFACT_PREFLIGHT_ONLY", P0="HOLD", P1="HOLD", artifacts=records,
                blockers=blockers, benchmark_executed=False,
                no_go_scope="artifact integrity only, not refutation of topology hypothesis")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args()
    result = preflight(json.loads(args.manifest.read_text()), args.artifact_root)
    print(json.dumps(result, indent=2))
    return 2 if any(x["status"] == "NO-GO" for x in result["artifacts"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
