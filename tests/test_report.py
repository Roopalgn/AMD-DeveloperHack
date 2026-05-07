"""Tests for HTML report generation."""

from pathlib import Path

from replaylab.backend.report import generate_report


def test_generate_report_creates_html(tmp_path):
    out = tmp_path / "report.html"
    result = generate_report(
        bad_metrics={"batch_size": 64, "estimated_memory_mb": 16384, "memory_pressure": True},
        good_metrics={"batch_size": 8, "estimated_memory_mb": 2048, "throughput_items_per_sec": 648000},
        diagnosis={"cause": "memory pressure", "confidence": "high", "explanation": "Batch too large"},
        fix={"fixed_command": "python demo.py --config config_good.json"},
        output_path=str(out),
    )
    assert result.exists()
    html = result.read_text()
    assert "ReplayLab" in html
    assert "batch_size: 64" in html
    assert "batch_size: 8" in html
    assert "648k items/sec" in html


def test_generate_report_creates_parent_dirs(tmp_path):
    out = tmp_path / "nested" / "deep" / "report.html"
    result = generate_report(
        bad_metrics={"batch_size": 32, "estimated_memory_mb": 8000, "memory_pressure": True},
        good_metrics={"batch_size": 4, "estimated_memory_mb": 1000, "throughput_items_per_sec": 500},
        diagnosis={"cause": "oom", "confidence": "high"},
        fix={"fixed_command": "run"},
        output_path=str(out),
    )
    assert result.exists()
