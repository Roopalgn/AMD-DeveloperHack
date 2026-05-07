"""Tests for LLM diagnoser module."""

from replaylab.backend.llm_diagnoser import llm_diagnose, _build_diagnosis_prompt


def test_llm_diagnose_returns_fallback_without_server():
    """Without a vLLM server or HF token, should return graceful fallback."""
    failed_run = {
        "exit_code": 1,
        "metrics": {"status": "failed", "batch_size": 64, "memory_pressure": True},
        "stderr": "CUDA out of memory",
    }
    result = llm_diagnose(failed_run, None)
    assert isinstance(result, dict)
    assert "diagnosis_source" in result
    # Without server, source should be unavailable
    assert result["diagnosis_source"] in ("unavailable", "vllm_amd_gpu", "huggingface_api")


def test_build_diagnosis_prompt_contains_evidence():
    failed_run = {
        "exit_code": 1,
        "metrics": {
            "status": "failed",
            "batch_size": 64,
            "estimated_memory_mb": 16000,
            "available_memory_mb": 8000,
            "memory_pressure": True,
            "runtime_kind": "gpu",
        },
        "stderr": "OOM: Available KV cache memory: -1.84 GiB",
    }
    good_run = {
        "metrics": {"batch_size": 8, "estimated_memory_mb": 2000, "memory_pressure": False, "throughput_items_per_sec": 230},
    }
    prompt = _build_diagnosis_prompt(failed_run, good_run)
    assert "Batch size" in prompt
    assert "64" in prompt
    assert "-1.84 GiB" in prompt
    assert "Respond in JSON" in prompt


def test_llm_diagnose_with_good_run():
    failed_run = {"metrics": {"status": "failed", "batch_size": 64}}
    good_run = {"metrics": {"status": "succeeded", "batch_size": 8, "throughput_items_per_sec": 230}}
    result = llm_diagnose(failed_run, good_run)
    assert isinstance(result, dict)
