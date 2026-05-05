"""AMD GPU telemetry collector for ReplayLab.

Collects real GPU metrics from rocm-smi/amd-smi when available on AMD Developer Cloud.
Falls back gracefully to simulated telemetry for local development.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from typing import Any


def _run_tool(cmd: list[str], timeout: float = 5.0) -> str | None:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None


def detect_amd_tools() -> dict[str, bool]:
    """Check which AMD GPU tools are available on the system."""
    return {
        "rocm_smi": shutil.which("rocm-smi") is not None,
        "amd_smi": shutil.which("amd-smi") is not None,
    }


def collect_rocm_smi() -> dict[str, Any] | None:
    """Collect GPU metrics via rocm-smi --showmeminfo vram --showuse --json."""
    output = _run_tool(["rocm-smi", "--showmeminfo", "vram", "--showuse", "--json"])
    if output is None:
        return None
    try:
        return json.loads(output)
    except (json.JSONDecodeError, ValueError):
        return {"raw_output": output[:2000]}


def collect_amd_smi() -> dict[str, Any] | None:
    """Collect GPU metrics via amd-smi monitor."""
    output = _run_tool(["amd-smi", "monitor", "--json", "-e", "1"])
    if output is None:
        return None
    try:
        return json.loads(output)
    except (json.JSONDecodeError, ValueError):
        return {"raw_output": output[:2000]}


def collect_gpu_snapshot() -> dict[str, Any]:
    """Collect a single GPU telemetry snapshot. Uses real tools if available."""
    tools = detect_amd_tools()
    snapshot: dict[str, Any] = {
        "timestamp": time.time(),
        "source": "none",
        "tools_available": tools,
    }

    if tools["amd_smi"]:
        data = collect_amd_smi()
        if data is not None:
            snapshot["source"] = "amd-smi"
            snapshot["data"] = data
            return snapshot

    if tools["rocm_smi"]:
        data = collect_rocm_smi()
        if data is not None:
            snapshot["source"] = "rocm-smi"
            snapshot["data"] = data
            return snapshot

    # Fallback: no AMD tools available (local dev / non-AMD machine)
    snapshot["source"] = "simulated"
    snapshot["data"] = {
        "note": "No AMD GPU tools detected. Using simulated telemetry.",
        "gpu_memory_used_mb": 0,
        "gpu_memory_total_mb": 0,
        "gpu_utilization_pct": 0,
    }
    return snapshot


def collect_during_run(duration_sec: float, interval_sec: float = 1.0) -> list[dict[str, Any]]:
    """Collect GPU telemetry snapshots over a time window."""
    snapshots: list[dict[str, Any]] = []
    end_time = time.time() + duration_sec
    while time.time() < end_time:
        snapshots.append(collect_gpu_snapshot())
        remaining = end_time - time.time()
        if remaining > interval_sec:
            time.sleep(interval_sec)
        else:
            break
    return snapshots
