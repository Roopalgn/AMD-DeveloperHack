"""Controlled ReplayLab demo experiment.

This script intentionally behaves like a tiny GPU experiment: a bad config
triggers deterministic memory pressure, while a corrected config succeeds.
It uses only the Python standard library so the MVP works before cloud setup.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


MEMORY_PER_BATCH_ITEM_MB = 128
RUNTIME_OVERHEAD_MB = 512


def load_config(path: str) -> dict:
    """Load JSON config for a demo experiment."""
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    if not isinstance(config, dict):
        raise ValueError(f"Config must be a JSON object: {path}")
    return config


def detect_runtime() -> dict:
    """Detect whether torch/ROCm/CUDA appears available, with stdlib fallback."""
    runtime = {
        "runtime_kind": "cpu_fallback",
        "gpu_available": False,
        "torch_available": False,
        "rocm_available": False,
        "cuda_available": False,
        "details": "torch not installed; using deterministic simulated telemetry",
    }

    if importlib.util.find_spec("torch") is None:
        return runtime

    runtime["torch_available"] = True
    try:
        import torch  # type: ignore

        hip_version = getattr(getattr(torch, "version", None), "hip", None)
        cuda_version = getattr(getattr(torch, "version", None), "cuda", None)
        cuda_available = bool(torch.cuda.is_available())
        rocm_available = bool(hip_version)

        runtime.update(
            {
                "runtime_kind": "rocm" if rocm_available else ("cuda" if cuda_available else "torch_cpu"),
                "gpu_available": cuda_available,
                "rocm_available": rocm_available,
                "cuda_available": bool(cuda_version or cuda_available),
                "details": f"torch={torch.__version__}, hip={hip_version}, cuda={cuda_version}",
            }
        )
    except Exception as exc:  # pragma: no cover - environment-specific guardrail
        runtime["details"] = f"torch detected but runtime probe failed: {exc}"

    return runtime


def estimate_memory_pressure(batch_size: int, model_size_mb: int, available_memory_mb: int) -> dict:
    """Return estimated memory demand and whether the run should fail."""
    activation_memory_mb = batch_size * MEMORY_PER_BATCH_ITEM_MB
    estimated_memory_mb = model_size_mb + activation_memory_mb + RUNTIME_OVERHEAD_MB
    headroom_mb = available_memory_mb - estimated_memory_mb
    return {
        "estimated_memory_mb": estimated_memory_mb,
        "activation_memory_mb": activation_memory_mb,
        "runtime_overhead_mb": RUNTIME_OVERHEAD_MB,
        "available_memory_mb": available_memory_mb,
        "headroom_mb": headroom_mb,
        "memory_pressure": estimated_memory_mb > available_memory_mb,
    }


def run_experiment(config: dict) -> tuple[int, dict]:
    """Run the controlled experiment and return exit code plus metrics/artifact data."""
    started_at = time.time()
    timer_start = time.perf_counter()

    batch_size = int(config.get("batch_size", 1))
    model_size_mb = int(config.get("model_size_mb", 1024))
    available_memory_mb = int(config.get("available_memory_mb", 8192))
    items = int(config.get("items", batch_size))
    recommended_batch_size = int(config.get("recommended_batch_size", max(1, batch_size // 8)))
    model_path = config.get("model_path")
    max_duration_sec = config.get("max_duration_sec")

    runtime = detect_runtime()
    memory = estimate_memory_pressure(batch_size, model_size_mb, available_memory_mb)

    # --- Failure pattern: model path not found ---
    model_path_error = False
    if model_path and not Path(model_path).exists():
        # Check if it looks intentionally bad (absolute path to nonexistent dir)
        if model_path.startswith("/") or model_path.startswith("C:\\"):
            model_path_error = True

    # Keep the demo deterministic while still doing a tiny amount of work.
    synthetic_work_units = min(items, 2048)
    checksum = 0
    for index in range(synthetic_work_units):
        checksum = (checksum + ((index + 1) * max(batch_size, 1))) % 1_000_003

    duration_sec = round(time.perf_counter() - timer_start, 6)
    if duration_sec == 0:
        duration_sec = 0.000001

    # --- Failure pattern: timeout ---
    timed_out = False
    if max_duration_sec and items > 10000:
        # Simulate that processing 100k items would exceed the timeout
        estimated_total_time = (duration_sec / synthetic_work_units) * items
        if estimated_total_time > max_duration_sec or items > 50000:
            timed_out = True
            duration_sec = max_duration_sec

    # Determine failure mode
    memory_failed = bool(memory["memory_pressure"])
    failed = memory_failed or model_path_error or timed_out

    if model_path_error:
        failure_cause = "model_not_found"
        failure_summary = f"Model path '{model_path}' does not exist. Cannot load model."
        recommendation = f"Fix model_path to a valid location (e.g., './models/qwen2.5-7b')."
    elif timed_out:
        failure_cause = "timeout_exceeded"
        failure_summary = f"Run exceeded max_duration_sec={max_duration_sec}s processing {items} items."
        recommendation = f"Reduce items from {items} to {recommended_batch_size * 64} or increase max_duration_sec."
    elif memory_failed:
        failure_cause = "batch_size_too_large_memory_pressure"
        failure_summary = "Run failed because estimated memory demand exceeded available memory."
        recommendation = f"Reduce batch_size from {batch_size} to {recommended_batch_size} and rerun."
    else:
        failure_cause = None
        failure_summary = "Run completed successfully."
        recommendation = "Keep this config as the replayable recovered run."

    status = "failed" if failed else "succeeded"
    throughput = 0.0 if failed else round(items / duration_sec, 3)

    metrics = {
        "status": status,
        "failure_type": failure_cause,
        "duration_sec": duration_sec,
        "started_at": started_at,
        "ended_at": time.time(),
        "batch_size": batch_size,
        "model_size_mb": model_size_mb,
        "available_memory_mb": available_memory_mb,
        "estimated_memory_mb": memory["estimated_memory_mb"],
        "activation_memory_mb": memory["activation_memory_mb"],
        "runtime_overhead_mb": memory["runtime_overhead_mb"],
        "headroom_mb": memory["headroom_mb"],
        "memory_pressure": memory["memory_pressure"],
        "model_path": model_path,
        "model_path_valid": not model_path_error,
        "timed_out": timed_out,
        "max_duration_sec": max_duration_sec,
        "runtime_kind": runtime["runtime_kind"],
        "gpu_available": runtime["gpu_available"],
        "torch_available": runtime["torch_available"],
        "rocm_available": runtime["rocm_available"],
        "cuda_available": runtime["cuda_available"],
        "runtime_details": runtime["details"],
        "throughput_items_per_sec": throughput,
        "items": items,
        "checksum": checksum,
    }

    replay_hint = (
        "python replaylab/demo/demo_experiment.py "
        "--config replaylab/demo/config_good.json "
        "--output replaylab/runs/manual_good"
    )
    artifact = {
        "status": status,
        "experiment_name": config.get("experiment_name", "replaylab_demo"),
        "task": config.get("task", "simulated_gpu_inference"),
        "model_name": config.get("model_name", "unknown"),
        "summary": failure_summary if failed else "Run completed successfully with a safe batch size.",
        "cause": failure_cause,
        "recommendation": recommendation,
        "replay_hint_command": replay_hint,
        "expected_failure": config.get("expected_failure"),
        "recommended_batch_size": recommended_batch_size,
        "deterministic_checksum": checksum,
    }

    return (1 if failed else 0), {"metrics": metrics, "artifact": artifact}


def write_outputs(output_dir: str, metrics: dict, artifact: dict) -> None:
    """Write metrics.json and artifact.json."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    with (output_path / "metrics.json").open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_path / "artifact.json").open("w", encoding="utf-8") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main() -> int:
    """Parse CLI args and execute the demo experiment."""
    parser = argparse.ArgumentParser(description="Run the controlled ReplayLab demo experiment.")
    parser.add_argument("--config", required=True, help="Path to the JSON experiment config.")
    parser.add_argument("--output", required=True, help="Directory where run outputs should be written.")
    args = parser.parse_args()

    try:
        config = load_config(args.config)
        exit_code, payload = run_experiment(config)
        write_outputs(args.output, payload["metrics"], payload["artifact"])
    except Exception as exc:
        print(f"ReplayLab demo experiment crashed before outputs were written: {exc}", file=sys.stderr)
        return 2

    metrics = payload["metrics"]
    artifact = payload["artifact"]
    output_dir = os.path.abspath(args.output)

    if exit_code:
        print("ReplayLab demo run: FAILED")
        print(f"Cause: {artifact['cause']}")
        print(f"Recommendation: {artifact['recommendation']}")
    else:
        print("ReplayLab demo run: SUCCEEDED")
        print(f"Throughput: {metrics['throughput_items_per_sec']} items/sec")
    print(f"Estimated memory: {metrics['estimated_memory_mb']} MB")
    print(f"Available memory: {metrics['available_memory_mb']} MB")
    print(f"Outputs: {output_dir}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
