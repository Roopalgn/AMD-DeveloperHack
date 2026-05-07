"""Tests for ReplayLab rule-based diagnoser."""

import json
import tempfile
from pathlib import Path

import pytest

from replaylab.backend.diagnoser import compare_runs, load_metrics, load_artifact


@pytest.fixture
def bad_run_dir(tmp_path):
    d = tmp_path / "bad"
    d.mkdir()
    (d / "metrics.json").write_text(json.dumps({
        "status": "failed",
        "batch_size": 64,
        "estimated_memory_mb": 16384,
        "available_memory_mb": 8192,
        "memory_pressure": True,
        "throughput_items_per_sec": 0,
        "failure_type": "memory_pressure",
    }))
    (d / "artifact.json").write_text(json.dumps({
        "status": "failed",
        "cause": "memory_pressure",
    }))
    (d / "run.json").write_text(json.dumps({
        "command": "python demo.py --config config_bad.json --output out",
        "exit_code": 1,
        "run_id": "bad_001",
    }))
    return d


@pytest.fixture
def good_run_dir(tmp_path):
    d = tmp_path / "good"
    d.mkdir()
    (d / "metrics.json").write_text(json.dumps({
        "status": "succeeded",
        "batch_size": 8,
        "estimated_memory_mb": 2048,
        "available_memory_mb": 8192,
        "memory_pressure": False,
        "throughput_items_per_sec": 648000,
        "failure_type": None,
    }))
    (d / "artifact.json").write_text(json.dumps({
        "status": "succeeded",
        "cause": None,
    }))
    (d / "run.json").write_text(json.dumps({
        "command": "python demo.py --config config_good.json --output out",
        "exit_code": 0,
        "run_id": "good_001",
    }))
    return d


def test_compare_runs_memory_pressure(bad_run_dir, good_run_dir):
    result = compare_runs(str(bad_run_dir), str(good_run_dir))
    assert result["cause"] == "memory pressure due to oversized batch size"
    assert result["confidence"] == "high"
    assert result["key_difference"]["batch_size"]["bad"] == 64
    assert result["key_difference"]["batch_size"]["good"] == 8


def test_compare_runs_model_not_found(tmp_path):
    bad = tmp_path / "bad_model"
    bad.mkdir()
    (bad / "metrics.json").write_text(json.dumps({
        "status": "failed",
        "batch_size": 8,
        "estimated_memory_mb": 2048,
        "available_memory_mb": 8192,
        "memory_pressure": False,
        "throughput_items_per_sec": 0,
        "failure_type": "model_not_found",
        "model_path": "/bad/path/model.bin",
        "model_path_valid": False,
    }))
    (bad / "artifact.json").write_text(json.dumps({"status": "failed", "cause": "model_not_found"}))
    (bad / "run.json").write_text(json.dumps({"command": "python demo.py", "exit_code": 1, "run_id": "bad_m"}))

    good = tmp_path / "good_model"
    good.mkdir()
    (good / "metrics.json").write_text(json.dumps({
        "status": "succeeded",
        "batch_size": 8,
        "estimated_memory_mb": 2048,
        "available_memory_mb": 8192,
        "memory_pressure": False,
        "throughput_items_per_sec": 648000,
        "failure_type": None,
        "model_path": "./models/qwen.bin",
        "model_path_valid": True,
    }))
    (good / "artifact.json").write_text(json.dumps({"status": "succeeded", "cause": None}))
    (good / "run.json").write_text(json.dumps({"command": "python demo.py", "exit_code": 0, "run_id": "good_m"}))

    result = compare_runs(str(bad), str(good))
    assert "model path" in result["cause"]
    assert result["confidence"] == "high"


def test_compare_runs_timeout(tmp_path):
    bad = tmp_path / "bad_timeout"
    bad.mkdir()
    (bad / "metrics.json").write_text(json.dumps({
        "status": "failed",
        "batch_size": 100000,
        "estimated_memory_mb": 1024,
        "available_memory_mb": 8192,
        "memory_pressure": False,
        "throughput_items_per_sec": 0,
        "failure_type": "timeout_exceeded",
        "timed_out": True,
        "items": 100000,
        "max_duration_sec": 10,
    }))
    (bad / "artifact.json").write_text(json.dumps({"status": "failed", "cause": "timeout_exceeded"}))
    (bad / "run.json").write_text(json.dumps({"command": "python demo.py", "exit_code": 1, "run_id": "bad_t"}))

    good = tmp_path / "good_timeout"
    good.mkdir()
    (good / "metrics.json").write_text(json.dumps({
        "status": "succeeded",
        "batch_size": 512,
        "estimated_memory_mb": 1024,
        "available_memory_mb": 8192,
        "memory_pressure": False,
        "throughput_items_per_sec": 51200,
        "failure_type": None,
        "timed_out": False,
        "items": 512,
        "max_duration_sec": 10,
    }))
    (good / "artifact.json").write_text(json.dumps({"status": "succeeded", "cause": None}))
    (good / "run.json").write_text(json.dumps({"command": "python demo.py", "exit_code": 0, "run_id": "good_t"}))

    result = compare_runs(str(bad), str(good))
    assert "timeout" in result["cause"]
    assert result["confidence"] == "high"


def test_load_metrics_invalid_json(tmp_path):
    f = tmp_path / "metrics.json"
    f.write_text("not json")
    with pytest.raises(json.JSONDecodeError):
        load_metrics(tmp_path)
