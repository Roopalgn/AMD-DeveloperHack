"""Experiment runner/recorder for ReplayLab."""

from __future__ import annotations

import json
import os
import shutil
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_command(command: str | Sequence[str]) -> tuple[list[str], str]:
    if isinstance(command, str):
        original = command
        parts = shlex.split(command, posix=os.name != "nt")
    else:
        parts = [str(part) for part in command]
        original = " ".join(shlex.quote(part) for part in parts)

    if not parts:
        raise ValueError("command cannot be empty")

    if parts[0].lower() in {"python", "python.exe", "py"}:
        parts[0] = sys.executable

    return parts, original


def find_command_output_dir(command_parts: Sequence[str]) -> Path | None:
    for index, part in enumerate(command_parts):
        if part == "--output" and index + 1 < len(command_parts):
            return Path(command_parts[index + 1])
        if part.startswith("--output="):
            return Path(part.split("=", 1)[1])
    return None


def copy_demo_outputs(source_dir: Path | None, run_dir: Path) -> list[str]:
    copied: list[str] = []
    if source_dir is None or not source_dir.exists():
        return copied

    for name in ("metrics.json", "artifact.json"):
        source = source_dir / name
        destination = run_dir / name
        if source.exists() and source.resolve() != destination.resolve():
            shutil.copy2(source, destination)
            copied.append(name)
    return copied


def run_command(command: str | Sequence[str], run_id: str, output_dir: str | Path) -> dict:
    command_parts, original_command = normalize_command(command)
    runs_root = Path(output_dir)
    run_dir = runs_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    start_time = _utc_now()
    timer_start = time.perf_counter()
    completed = subprocess.run(command_parts, capture_output=True, text=True)
    duration_sec = round(time.perf_counter() - timer_start, 6)
    end_time = _utc_now()

    (run_dir / "stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (run_dir / "stderr.txt").write_text(completed.stderr, encoding="utf-8")

    source_output_dir = find_command_output_dir(command_parts)
    copied_outputs = copy_demo_outputs(source_output_dir, run_dir)

    run_record = {
        "command": original_command,
        "resolved_command": command_parts,
        "run_id": run_id,
        "exit_code": completed.returncode,
        "duration_sec": duration_sec,
        "start_time": start_time,
        "end_time": end_time,
        "run_dir": str(run_dir),
        "source_output_dir": str(source_output_dir) if source_output_dir else None,
        "copied_outputs": copied_outputs,
    }

    (run_dir / "run.json").write_text(
        json.dumps(run_record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return run_record
