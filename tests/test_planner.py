"""Tests for ReplayLab planner."""

import json
from pathlib import Path

import pytest

from replaylab.backend.planner import generate_fix, load_run


@pytest.fixture
def run_dir_memory(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    (d / "run.json").write_text(json.dumps({
        "command": "python replaylab/demo/demo_experiment.py --config replaylab/demo/config_bad.json --output replaylab/runs/tmp",
        "exit_code": 1,
    }))
    (d / "metrics.json").write_text(json.dumps({"status": "failed", "batch_size": 64}))
    (d / "artifact.json").write_text(json.dumps({"status": "failed"}))
    return d


def test_generate_fix_memory_pressure(run_dir_memory):
    diagnosis = {
        "cause": "memory pressure due to oversized batch size",
        "key_difference": {"batch_size": {"bad": 64, "good": 8}},
    }
    bad_run = load_run(str(run_dir_memory))
    fix = generate_fix(diagnosis, bad_run)
    assert "config_good.json" in fix["fixed_command"]
    assert "config_bad.json" not in fix["fixed_command"]
    assert fix["changes"]["batch_size"]["bad"] == 64
    assert fix["changes"]["batch_size"]["good"] == 8


def test_generate_fix_model_path(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    (d / "run.json").write_text(json.dumps({
        "command": "python replaylab/demo/demo_experiment.py --config replaylab/demo/config_bad_model_path.json --output out",
        "exit_code": 1,
    }))
    (d / "metrics.json").write_text(json.dumps({"status": "failed"}))
    (d / "artifact.json").write_text(json.dumps({"status": "failed"}))

    diagnosis = {
        "cause": "model path does not exist",
        "key_difference": {"model_path": {"bad": "/bad/path", "good": "./models/qwen"}},
    }
    bad_run = load_run(str(d))
    fix = generate_fix(diagnosis, bad_run)
    assert "config_good_model_path.json" in fix["fixed_command"]


def test_generate_fix_timeout(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    (d / "run.json").write_text(json.dumps({
        "command": "python replaylab/demo/demo_experiment.py --config replaylab/demo/config_bad_timeout.json --output out",
        "exit_code": 1,
    }))
    (d / "metrics.json").write_text(json.dumps({"status": "failed"}))
    (d / "artifact.json").write_text(json.dumps({"status": "failed"}))

    diagnosis = {
        "cause": "processing timeout exceeded",
        "key_difference": {"items": {"bad": 100000, "good": 512}},
    }
    bad_run = load_run(str(d))
    fix = generate_fix(diagnosis, bad_run)
    assert "config_good_timeout.json" in fix["fixed_command"]
