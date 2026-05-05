"""LLM-powered diagnosis agent for ReplayLab.

Uses Qwen model (via vLLM on AMD GPU or Hugging Face Inference) to provide
intelligent failure analysis beyond rule-based pattern matching.
Falls back to rule-based diagnosis if LLM is unavailable.
"""

from __future__ import annotations

import json
import os
from typing import Any


def _build_diagnosis_prompt(failed_run: dict[str, Any], good_run: dict[str, Any] | None) -> str:
    """Build a structured prompt for LLM diagnosis."""
    prompt = """You are ReplayLab's GPU experiment diagnosis agent. Analyze this failed run and identify the root cause.

## Failed Run Evidence
"""
    prompt += f"- Exit code: {failed_run.get('exit_code', 'unknown')}\n"
    prompt += f"- Status: {failed_run.get('metrics', {}).get('status', 'unknown')}\n"
    prompt += f"- Batch size: {failed_run.get('metrics', {}).get('batch_size', 'unknown')}\n"
    prompt += f"- Estimated memory: {failed_run.get('metrics', {}).get('estimated_memory_mb', 'unknown')} MB\n"
    prompt += f"- Available memory: {failed_run.get('metrics', {}).get('available_memory_mb', 'unknown')} MB\n"
    prompt += f"- Memory pressure: {failed_run.get('metrics', {}).get('memory_pressure', 'unknown')}\n"
    prompt += f"- Runtime: {failed_run.get('metrics', {}).get('runtime_kind', 'unknown')}\n"

    if failed_run.get("stderr"):
        prompt += f"\n## Stderr (last 500 chars)\n```\n{failed_run['stderr'][-500:]}\n```\n"

    if good_run:
        prompt += "\n## Successful Run (for comparison)\n"
        prompt += f"- Batch size: {good_run.get('metrics', {}).get('batch_size', 'unknown')}\n"
        prompt += f"- Estimated memory: {good_run.get('metrics', {}).get('estimated_memory_mb', 'unknown')} MB\n"
        prompt += f"- Memory pressure: {good_run.get('metrics', {}).get('memory_pressure', 'unknown')}\n"
        prompt += f"- Throughput: {good_run.get('metrics', {}).get('throughput_items_per_sec', 'unknown')}\n"

    prompt += """
## Instructions
Respond in JSON with these fields:
- "cause": one-line root cause
- "explanation": 2-3 sentence technical explanation
- "fix": specific parameter change recommendation
- "confidence": float 0-1
- "gpu_relevant": boolean, whether this is a GPU-specific failure
"""
    return prompt


def _try_vllm_diagnosis(prompt: str) -> dict[str, Any] | None:
    """Try to get diagnosis from a local vLLM server (AMD GPU)."""
    try:
        import urllib.request

        vllm_url = os.environ.get("REPLAYLAB_VLLM_URL", "http://localhost:8000/v1/chat/completions")
        model = os.environ.get("REPLAYLAB_MODEL", "Qwen/Qwen2.5-7B-Instruct")

        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0.1,
        }).encode("utf-8")

        req = urllib.request.Request(
            vllm_url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        content = result["choices"][0]["message"]["content"]
        # Try to parse JSON from the response
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
    except Exception:
        pass
    return None


def _try_hf_inference(prompt: str) -> dict[str, Any] | None:
    """Try to get diagnosis from Hugging Face Inference API."""
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        return None

    try:
        import urllib.request

        model = os.environ.get("REPLAYLAB_HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")
        url = f"https://api-inference.huggingface.co/models/{model}/v1/chat/completions"

        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0.1,
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {hf_token}",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        content = result["choices"][0]["message"]["content"]
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
    except Exception:
        pass
    return None


def llm_diagnose(failed_run: dict[str, Any], good_run: dict[str, Any] | None = None) -> dict[str, Any]:
    """Attempt LLM-powered diagnosis. Returns diagnosis dict or None if unavailable.

    Tries in order:
    1. Local vLLM server (AMD GPU with Qwen model)
    2. Hugging Face Inference API
    3. Returns None (caller should fall back to rule-based)
    """
    prompt = _build_diagnosis_prompt(failed_run, good_run)

    # Try vLLM first (AMD GPU local inference)
    result = _try_vllm_diagnosis(prompt)
    if result:
        result["diagnosis_source"] = "vllm_amd_gpu"
        return result

    # Try HF Inference API
    result = _try_hf_inference(prompt)
    if result:
        result["diagnosis_source"] = "huggingface_api"
        return result

    # No LLM available
    return {
        "cause": None,
        "diagnosis_source": "unavailable",
        "note": "LLM diagnosis unavailable. Using rule-based fallback.",
    }
