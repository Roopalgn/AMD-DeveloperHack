"""Tests for vLLM failure taxonomy."""

from replaylab.backend.vllm_taxonomy import classify_failure, get_all_patterns, suggest_vllm_config


def test_classify_kv_cache_oom():
    stderr = """(EngineCore_DP0 pid=1034) INFO 05-07 03:20:52 [gpu_worker.py:424] Available KV cache memory: -1.84 GiB
(EngineCore_DP0 pid=1034) ERROR 05-07 03:20:52 [core.py:1100] ValueError: No available memory for the cache blocks."""
    result = classify_failure(stderr)
    assert result is not None
    assert result["pattern_id"] == "kv_cache_oom"
    assert result["severity"] == "critical"
    assert result["confidence"] == 0.95
    assert "gpu_memory_utilization" in result["fix_params"]


def test_classify_engine_failed():
    stderr = "Engine core initialization failed. See root cause above."
    result = classify_failure(stderr)
    assert result is not None
    assert result["pattern_id"] == "engine_dead_after_warmup"


def test_classify_port_in_use():
    stderr = "OSError: [Errno 98] Address already in use"
    result = classify_failure(stderr)
    assert result is not None
    assert result["pattern_id"] == "port_in_use"
    assert result["severity"] == "medium"


def test_classify_no_match():
    stderr = "Some random unrelated error"
    result = classify_failure(stderr)
    assert result is None


def test_classify_empty_stderr():
    assert classify_failure("") is None
    assert classify_failure(None, exit_code=1) is None


def test_get_all_patterns():
    patterns = get_all_patterns()
    assert len(patterns) == 10
    assert all("id" in p and "cause" in p and "severity" in p for p in patterns)


def test_suggest_vllm_config_7b():
    config = suggest_vllm_config(model_size_gb=14.35, gpu_vram_gb=192.0)
    assert config["gpu_memory_utilization"] >= 0.5
    assert config["gpu_memory_utilization"] <= 0.95
    assert config["estimated_kv_cache_gb"] > 0
    assert config["max_model_len"] > 0


def test_suggest_vllm_config_70b():
    config = suggest_vllm_config(model_size_gb=140.0, gpu_vram_gb=192.0)
    assert config["gpu_memory_utilization"] >= 0.75
    assert config["estimated_kv_cache_gb"] > 0
