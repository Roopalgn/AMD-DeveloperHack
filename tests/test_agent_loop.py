"""Tests for the multi-step agent reasoning loop."""

import json
from pathlib import Path

from replaylab.backend.agent import AgentLoop, AgentTrace


def test_agent_trace_records_steps():
    trace = AgentTrace()
    trace.add_step("detect", {"status": "failed", "exit_code": 1})
    trace.add_step("diagnose", {"cause": "memory_pressure"})
    assert len(trace.steps) == 2
    assert trace.steps[0]["action"] == "detect"
    assert trace.steps[1]["data"]["cause"] == "memory_pressure"


def test_agent_trace_to_dict():
    trace = AgentTrace()
    trace.add_step("detect", {"status": "failed"})
    d = trace.to_dict()
    assert "steps" in d
    assert "total_duration_sec" in d


def test_agent_loop_plans_from_metrics(tmp_path):
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "metrics.json").write_text(json.dumps({
        "status": "failed", "batch_size": 64,
        "estimated_memory_mb": 16384, "available_memory_mb": 8192,
        "memory_pressure": True, "throughput_items_per_sec": 0,
        "failure_type": "memory_pressure",
    }))
    (bad / "artifact.json").write_text(json.dumps({"status": "failed", "cause": "memory_pressure"}))
    (bad / "run.json").write_text(json.dumps({"command": "python demo.py --config config_bad.json", "exit_code": 1, "run_id": "test"}))

    good = tmp_path / "good"
    good.mkdir()
    (good / "metrics.json").write_text(json.dumps({
        "status": "succeeded", "batch_size": 8,
        "estimated_memory_mb": 2048, "available_memory_mb": 8192,
        "memory_pressure": False, "throughput_items_per_sec": 648000,
        "failure_type": None,
    }))
    (good / "artifact.json").write_text(json.dumps({"status": "succeeded", "cause": None}))
    (good / "run.json").write_text(json.dumps({"command": "python demo.py --config config_good.json", "exit_code": 0, "run_id": "test_good"}))

    agent = AgentLoop(max_retries=2)
    trace = agent.plan(str(bad), str(good))
    assert trace.steps[0]["action"] == "detect_failure"
    assert any(s["action"] == "diagnose" for s in trace.steps)
    assert any(s["action"] == "plan_fix" for s in trace.steps)


def test_agent_loop_cost_estimate():
    agent = AgentLoop()
    cost = agent.estimate_cost(gpu_hours=0.07, rate_per_hour=1.99)
    assert cost["gpu_cost_usd"] == pytest.approx(0.14, abs=0.01)


# Need pytest import for approx
import pytest
