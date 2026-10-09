#!/usr/bin/env python3
"""Replay five finalized P0 campaigns without writing inside historical evidence.

This checks canonical JSON equivalence, not byte-identical whitespace. It adds no
readiness inference and never converts PANTRC01/02 into candidate observations.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path

CAMPAIGNS = (
    ("E0B_SIFT10M_20261008T151707400337Z", "analyze_e0b", "analysis"),
    ("E0C_SIFT10M_20261009T055255739318Z", "analyze_e0c", "analysis"),
    ("G0B_SIFT10M_20261009T063743710720Z", "analyze_g0b_light", "analysis_final"),
    ("G0C1_SIFT10M_20261009T073827804239Z", "analyze_g0c1", "analysis"),
    ("G0C2_SIFT10M_20261009T090432438598Z", "analyze_g0c2_d6", "analysis_verified"),
)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Non-finite JSON value: {value}")


def read_json(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def canonical_json(value):
    # JSON round trip normalizes historical numeric histogram keys. Reject
    # collisions rather than silently losing one of an int/string key pair.
    normalized = json.loads(json.dumps(value, allow_nan=False),
                            object_pairs_hook=unique_object)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), allow_nan=False)


def compare_result(result, baseline):
    expected = canonical_json(read_json(baseline))
    actual = canonical_json(result)
    if actual != expected:
        raise ValueError(f"Historical replay differs: {baseline}")
    return {"exact_json_equality": True,
            "canonical_json_sha256": hashlib.sha256(actual.encode()).hexdigest(),
            "baseline": str(baseline),
            "baseline_file_sha256": hashlib.sha256(Path(baseline).read_bytes()).hexdigest()}


def prepare_output(campaign_root, output):
    campaign_root, output = Path(campaign_root).resolve(), Path(output).resolve()
    if output == campaign_root or campaign_root in output.parents:
        raise ValueError("Replay output must be outside historical campaigns")
    output.mkdir(parents=True, exist_ok=False)
    return campaign_root, output


def replay(campaign_root, output):
    campaign_root, output = prepare_output(campaign_root, output)
    report = {"source": "Local finalized evidence", "replays": {}, "all_equal": False}
    # On failure preserve the new diagnostic result; never modify a baseline.
    try:
        for name, module_name, analysis_dir in CAMPAIGNS:
            campaign = campaign_root / name
            result = importlib.import_module(module_name).analyze_campaign(campaign)
            (output / (name + ".json")).write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
            report["replays"][name] = compare_result(result, campaign / analysis_dir / "analysis.json")
        report["all_equal"] = True
    except (ValueError, OSError, KeyError, TypeError) as error:
        report["error"] = str(error)
        raise
    finally:
        (output / "REPLAY.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = replay(args.campaign_root, args.output)
    print(json.dumps({"all_equal": result["all_equal"], "campaigns": len(result["replays"])}))


if __name__ == "__main__":
    main()
