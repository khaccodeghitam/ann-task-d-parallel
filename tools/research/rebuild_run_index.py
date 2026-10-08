#!/usr/bin/env python3
"""Upsert finalized local runs into the derived CSV index; preserve other rows."""

import argparse
import json
import os
from pathlib import Path

from run_ann_experiment import update_run_index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-root", default=os.environ.get("ANN_EVIDENCE_ROOT", "~/ann-research/research-v3"))
    root = Path(parser.parse_args().evidence_root).expanduser().resolve()
    updated = 0
    for path in sorted((root / "runs").glob("*/manifest.json")):
        summary_path = path.with_name("summary.json")
        if not summary_path.is_file():
            continue
        manifest = json.loads(path.read_text())
        summary = json.loads(summary_path.read_text())
        if manifest.get("schema_version") != 1 or manifest.get("status") == "running":
            continue
        if manifest["run_id"] != summary["run_id"]:
            raise ValueError(f"Run ID mismatch: {path.parent}")
        update_run_index(root, manifest, summary)
        updated += 1
    print(f"Upserted {updated} finalized runs into {root / 'summaries/run_index.csv'}")


if __name__ == "__main__":
    main()
