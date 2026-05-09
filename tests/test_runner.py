"""Tests for experiment runner."""

import json
from pathlib import Path

import pytest

from replaylab.backend.runner import normalize_command, find_command_output_dir, copy_demo_outputs


def test_normalize_string_command():
    parts, original = normalize_command("python demo.py --batch 8")
    assert len(parts) >= 3
    assert original == "python demo.py --batch 8"


def test_normalize_list_command():
    parts, original = normalize_command(["python", "demo.py", "--batch", "8"])
    assert parts[1] == "demo.py"


def test_normalize_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        normalize_command("")


def test_find_command_output_dir_flag():
    parts = ["python", "demo.py", "--output", "/tmp/runs"]
    result = find_command_output_dir(parts)
    assert result == Path("/tmp/runs")


def test_find_command_output_dir_equals():
    parts = ["python", "demo.py", "--output=/tmp/runs"]
    result = find_command_output_dir(parts)
    assert result == Path("/tmp/runs")


def test_find_command_output_dir_missing():
    parts = ["python", "demo.py", "--batch", "8"]
    result = find_command_output_dir(parts)
    assert result is None


def test_copy_demo_outputs_copies_files(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "metrics.json").write_text('{"status": "ok"}')
    (src / "artifact.json").write_text('{"name": "test"}')

    dst = tmp_path / "dst"
    dst.mkdir()

    copied = copy_demo_outputs(src, dst)
    assert "metrics.json" in copied
    assert "artifact.json" in copied
    assert (dst / "metrics.json").exists()


def test_copy_demo_outputs_no_source():
    copied = copy_demo_outputs(None, Path("/tmp"))
    assert copied == []


def test_copy_demo_outputs_missing_dir(tmp_path):
    copied = copy_demo_outputs(tmp_path / "nonexistent", tmp_path)
    assert copied == []
