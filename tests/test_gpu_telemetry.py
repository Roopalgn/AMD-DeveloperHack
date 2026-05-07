"""Tests for GPU telemetry collector."""

from replaylab.backend.gpu_telemetry import collect_gpu_snapshot, detect_amd_tools


def test_collect_gpu_snapshot_returns_dict():
    snapshot = collect_gpu_snapshot()
    assert isinstance(snapshot, dict)
    assert "source" in snapshot
    assert "timestamp" in snapshot
    assert snapshot["source"] in ("amd-smi", "rocm-smi", "simulated")


def test_detect_amd_tools_returns_booleans():
    tools = detect_amd_tools()
    assert isinstance(tools["rocm_smi"], bool)
    assert isinstance(tools["amd_smi"], bool)
