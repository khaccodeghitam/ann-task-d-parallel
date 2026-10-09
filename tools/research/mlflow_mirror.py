"""Optional post-benchmark local MLflow worker; never imported in ANN hot loops."""

import json
import os
from pathlib import Path
import sys


def mirror(directory, root):
    run_id = None
    client = None
    try:
        # Ignore ambient cloud tracking configuration. Both client stores are local.
        os.environ["MLFLOW_TRACKING_URI"] = "sqlite:///" + str(root / "mlflow" / "mlflow.db")
        os.environ["MLFLOW_REGISTRY_URI"] = os.environ["MLFLOW_TRACKING_URI"]
        from mlflow import MlflowClient
        manifest = json.loads((directory / "manifest.json").read_text())
        summary = json.loads((directory / "summary.json").read_text())
        artifacts = root / "mlflow" / "artifacts"
        artifacts.mkdir(parents=True, exist_ok=True)
        uri = os.environ["MLFLOW_TRACKING_URI"]
        client = MlflowClient(tracking_uri=uri, registry_uri=uri)
        name = "Parallel_ANN_P0"
        experiment = client.get_experiment_by_name(name)
        experiment_id = experiment.experiment_id if experiment else client.create_experiment(
            name, artifact_location=artifacts.as_uri())
        # Existing experiments must also point inside this evidence root.
        experiment = client.get_experiment(experiment_id)
        if not experiment.artifact_location.startswith(artifacts.as_uri() + "/") and experiment.artifact_location != artifacts.as_uri():
            raise ValueError("Existing MLflow experiment artifact location is outside the local artifact root")
        provenance = ("harness_git_commit", "subject_git_commit", "harness_git_dirty", "subject_git_dirty")
        profiles = ("benchmark_profile", "benchmark_profile_version", "parser_version")
        packages = tuple(f"{kind}_package_manifest_sha256" for kind in ("input", "index"))
        package_tags = {key: str(manifest[key]) for key in packages if manifest.get(key) is not None}
        run_id = client.create_run(experiment_id, tags={
            "mlflow.runName": manifest["run_id"], "phase": "P0", "dataset": manifest["dataset_id"],
            "variant": "baseline", "trace_mode": manifest["trace_mode"],
            "local_run_dir": str(directory), "local_run_id": manifest["run_id"],
            "ann_run_status": summary.get("benchmark_status", "unknown"),
            "benchmark_status": summary.get("benchmark_status", "unknown"),
            "trace_valid": json.dumps(summary.get("trace_valid")),
            "run_status": summary["run_status"],
            "host_telemetry_requested": json.dumps(manifest.get("host_telemetry_requested")),
            **package_tags,
            **{key: "unknown" if manifest.get(key) is None else str(manifest[key])
               for key in (*provenance, *profiles)}}).info.run_id
        keys = {"dataset": "dataset_id", "threads": "threads", "wcap": "wcap", "L": "l_search",
                "K": "k", "mem_L": "mem_l", "metric": "distance_metric", "neighbor_type": "neighbor_type",
                "trace_mode": "trace_mode", "search_mode": "search_mode",
                **{key: key for key in (*provenance, *profiles, "printed_latency_percentile")}}
        for target, source in keys.items():
            value = manifest.get(source)
            client.log_param(run_id, target, "unknown" if value is None else value)
        if "host_telemetry_requested" in manifest:
            client.log_param(run_id, "host_telemetry_requested", manifest["host_telemetry_requested"])
        for key, value in package_tags.items():
            client.log_param(run_id, key, value)
        if manifest.get("causal_trace_enabled"):
            client.log_param(run_id, "trace_protocol", manifest["trace_config"]["protocol"])
            client.log_param(run_id, "trace_detail_first_n", manifest["trace_config"]["detail_first_n"])
            client.log_param(run_id, "trace_event_capacity", manifest["trace_config"]["event_capacity"])
        for key in ("trace_sample_policy", "trace_sample_sha256", "trace_sample_count"):
            if manifest.get(key) is not None:
                client.log_param(run_id, key, manifest[key])
                client.set_tag(run_id, key, str(manifest[key]))
        for metric in ("qps", "recall", "mean_latency_us", "p99_latency_us", "p999_latency_us",
                       "mean_hops", "mean_ios", "wall_time_s"):
            if summary[metric] is not None:
                client.log_metric(run_id, metric, summary[metric])
        client.set_tag(run_id, "recall_unit", "percent")
        client.set_tag(run_id, "latency_note", summary["latency_note"])
        # Small stable artifacts only; local manifest remains authoritative.
        for name in ("summary.json", "command.sh"):
            client.log_artifact(run_id, str(directory / name))
        client.set_terminated(run_id, status="FINISHED" if summary["run_status"] == "success" else "FAILED")
        return {"status": "success", "run_id": run_id, "error": None}
    except Exception as error:
        if client is not None and run_id is not None:
            try:
                client.set_terminated(run_id, status="FAILED")
            except Exception:
                pass
        return {"status": "failed", "run_id": run_id, "error": f"{type(error).__name__}: {error}"}


if __name__ == "__main__":
    directory, root = (Path(value).resolve() for value in sys.argv[1:])
    result = mirror(directory, root)
    temporary = directory / "mlflow_result.json.tmp"
    temporary.write_text(json.dumps(result, indent=2) + "\n")
    temporary.replace(directory / "mlflow_result.json")
    sys.exit(0 if result["status"] == "success" else 1)
