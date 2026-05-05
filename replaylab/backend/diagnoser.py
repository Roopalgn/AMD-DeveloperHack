"""Rule-based failure diagnoser for ReplayLab MVP."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def load_metrics(run_dir: str | Path) -> dict[str, Any]:
    return load_json(Path(run_dir) / "metrics.json")


def load_artifact(run_dir: str | Path) -> dict[str, Any]:
    return load_json(Path(run_dir) / "artifact.json")


def load_run(run_dir: str | Path) -> dict[str, Any]:
    return load_json(Path(run_dir) / "run.json")


def _diff_value(bad: dict[str, Any], good: dict[str, Any], key: str) -> dict[str, Any] | None:
    bad_value = bad.get(key)
    good_value = good.get(key)
    if bad_value == good_value:
        return None
    return {"bad": bad_value, "good": good_value}


def compare_runs(bad_run_dir: str | Path, good_run_dir: str | Path) -> dict[str, Any]:
    bad_metrics = load_metrics(bad_run_dir)
    good_metrics = load_metrics(good_run_dir)
    bad_artifact = load_artifact(bad_run_dir)
    good_artifact = load_artifact(good_run_dir)
    bad_run = load_run(bad_run_dir)
    good_run = load_run(good_run_dir)

    compared_fields = {
        "batch_size": {
            "bad": bad_metrics.get("batch_size"),
            "good": good_metrics.get("batch_size"),
        },
        "estimated_memory_mb": {
            "bad": bad_metrics.get("estimated_memory_mb"),
            "good": good_metrics.get("estimated_memory_mb"),
        },
        "memory_pressure": {
            "bad": bad_metrics.get("memory_pressure"),
            "good": good_metrics.get("memory_pressure"),
        },
        "throughput_items_per_sec": {
            "bad": bad_metrics.get("throughput_items_per_sec"),
            "good": good_metrics.get("throughput_items_per_sec"),
        },
        "exit_code": {
            "bad": bad_run.get("exit_code"),
            "good": good_run.get("exit_code"),
        },
    }

    key_difference: dict[str, dict[str, Any]] = {}
    for key in ("batch_size", "estimated_memory_mb", "memory_pressure", "throughput_items_per_sec"):
        diff = _diff_value(bad_metrics, good_metrics, key)
        if diff is not None:
            key_difference[key] = diff

    exit_code_diff = _diff_value(bad_run, good_run, "exit_code")
    if exit_code_diff is not None:
        key_difference["exit_code"] = exit_code_diff

    bad_memory_pressure = bool(bad_metrics.get("memory_pressure"))
    good_memory_pressure = bool(good_metrics.get("memory_pressure"))
    bad_batch = bad_metrics.get("batch_size")
    good_batch = good_metrics.get("batch_size")
    bad_failure_type = bad_metrics.get("failure_type")

    # Pattern 1: Memory pressure from oversized batch
    if bad_memory_pressure and not good_memory_pressure:
        cause = "memory pressure due to oversized batch size"
        confidence = "high"
        explanation = (
            f"The failed run used batch size {bad_batch}, which pushed estimated memory to "
            f"{bad_metrics.get('estimated_memory_mb')} MB against "
            f"{bad_metrics.get('available_memory_mb')} MB available. The recovered run used "
            f"batch size {good_batch}, lowering estimated memory to "
            f"{good_metrics.get('estimated_memory_mb')} MB and clearing memory pressure."
        )
        recommended_fix = f"Reduce batch size from {bad_batch} to {good_batch}"

    # Pattern 2: Model path not found
    elif bad_failure_type == "model_not_found" or (not bad_metrics.get("model_path_valid", True)):
        bad_path = bad_metrics.get("model_path", "unknown")
        good_path = good_metrics.get("model_path", "unknown")
        cause = "model path does not exist"
        confidence = "high"
        explanation = (
            f"The failed run tried to load from '{bad_path}' which does not exist. "
            f"The recovered run uses '{good_path}' which is a valid path."
        )
        recommended_fix = f"Change model_path from '{bad_path}' to '{good_path}'"
        key_difference["model_path"] = {"bad": bad_path, "good": good_path}

    # Pattern 3: Timeout exceeded
    elif bad_failure_type == "timeout_exceeded" or bad_metrics.get("timed_out"):
        bad_items = bad_metrics.get("items", "?")
        good_items = good_metrics.get("items", "?")
        bad_max_dur = bad_metrics.get("max_duration_sec", "?")
        cause = "processing timeout exceeded"
        confidence = "high"
        explanation = (
            f"The failed run attempted to process {bad_items} items within {bad_max_dur}s timeout. "
            f"The recovered run uses {good_items} items which completes within the time limit."
        )
        recommended_fix = f"Reduce items from {bad_items} to {good_items}"
        key_difference["items"] = {"bad": bad_items, "good": good_items}
        key_difference["timed_out"] = {"bad": True, "good": False}

    else:
        cause = bad_artifact.get("cause") or "unknown failure pattern"
        confidence = "low"
        explanation = "No high-confidence ReplayLab MVP rule matched this failed/recovered pair."
        recommended_fix = good_artifact.get("recommendation") or "Inspect logs and configuration differences."

    return {
        "cause": cause,
        "confidence": confidence,
        "key_difference": key_difference,
        "compared_fields": compared_fields,
        "explanation": explanation,
        "recommended_fix": recommended_fix,
        "bad_run_id": bad_run.get("run_id"),
        "good_run_id": good_run.get("run_id"),
    }
