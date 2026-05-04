"""Replay verifier for ReplayLab MVP."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from replaylab.backend.runner import run_command


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def verify_replay(command: str, run_id: str) -> dict[str, Any]:
    record = run_command(command, run_id, "replaylab/runs")
    run_dir = Path("replaylab/runs") / run_id
    metrics = _load_json(run_dir / "metrics.json")
    success = record["exit_code"] == 0 and metrics.get("status") == "succeeded"
    return {
        "success": success,
        "exit_code": record["exit_code"],
        "metrics": metrics,
        "run": record,
    }
