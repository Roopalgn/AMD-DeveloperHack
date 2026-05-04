"""Replay planner for ReplayLab MVP."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def load_run(run_dir: str) -> dict[str, Any]:
    path = Path(run_dir)
    return {
        "run": _load_json(path / "run.json"),
        "metrics": _load_json(path / "metrics.json"),
        "artifact": _load_json(path / "artifact.json"),
    }


def generate_fix(diagnosis: dict, bad_run: dict) -> dict[str, Any]:
    original_command = str(bad_run["run"]["command"])
    fixed_command = original_command
    changes: dict[str, Any] = {}

    cause = str(diagnosis.get("cause", "")).lower()
    if "batch size" in cause:
        fixed_command = fixed_command.replace("config_bad.json", "config_good.json")
        batch_diff = diagnosis.get("key_difference", {}).get("batch_size", {})
        changes["config"] = {
            "bad": "config_bad.json",
            "good": "config_good.json",
        }
        changes["batch_size"] = {
            "bad": batch_diff.get("bad"),
            "good": batch_diff.get("good"),
        }

    return {
        "original_command": original_command,
        "fixed_command": fixed_command,
        "changes": changes,
    }
