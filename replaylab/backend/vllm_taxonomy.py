"""vLLM failure taxonomy for ReplayLab.

Domain-specific knowledge layer that maps vLLM/ROCm error patterns to
structured diagnoses. This gives ReplayLab expert knowledge beyond generic
pattern matching — modeled after real MI300X failure modes.
"""

from __future__ import annotations

import re
from typing import Any


# Taxonomy of known vLLM failure patterns on AMD GPUs
VLLM_FAILURE_PATTERNS: list[dict[str, Any]] = [
    {
        "id": "kv_cache_oom",
        "pattern": r"Available KV cache memory:\s*(-[\d.]+)\s*GiB",
        "cause": "KV cache memory exhaustion",
        "severity": "critical",
        "explanation": (
            "vLLM pre-allocates KV cache at startup. When gpu_memory_utilization is too low "
            "or max_model_len is too high, model weights consume all available VRAM, leaving "
            "negative space for KV cache blocks."
        ),
        "fix_strategy": "increase_gpu_memory_utilization",
        "fix_params": {"gpu_memory_utilization": 0.9, "max_model_len": 4096},
    },
    {
        "id": "model_too_large",
        "pattern": r"torch\.OutOfMemoryError|torch\.cuda\.OutOfMemoryError|HIP out of memory",
        "cause": "Model weights exceed GPU VRAM",
        "severity": "critical",
        "explanation": (
            "Model parameters in bfloat16/float16 exceed available GPU memory. "
            "For 7B models: ~14 GiB, for 70B models: ~140 GiB. "
            "MI300X has 192 GiB so this typically means quantization is needed for 70B+ or "
            "tensor parallelism for multi-GPU setups."
        ),
        "fix_strategy": "reduce_model_or_quantize",
        "fix_params": {"dtype": "auto", "quantization": "awq"},
    },
    {
        "id": "context_length_exceeded",
        "pattern": r"maximum context length|max_model_len.*(?:exceeds|greater than).*(?:max_seq_len|derived max_model_len|max_position_embeddings)|This model's maximum context length",
        "cause": "Requested context exceeds model or engine limits",
        "severity": "high",
        "explanation": (
            "The input + max_tokens exceeds the configured max_model_len or the model's "
            "native context window. VRAM usage for KV cache scales linearly with context length."
        ),
        "fix_strategy": "reduce_max_model_len",
        "fix_params": {"max_model_len": 4096},
    },
    {
        "id": "rocm_version_mismatch",
        "pattern": r"ROCm.*not supported|hipErrorNoBinaryForGpu|amdgpu.*error",
        "cause": "ROCm version incompatible with GPU or vLLM build",
        "severity": "critical",
        "explanation": (
            "The vLLM ROCm wheel was built against a different ROCm version than what's "
            "installed. MI300X requires ROCm 6.0+ and recent vLLM builds target ROCm 6.2/7.x."
        ),
        "fix_strategy": "match_rocm_version",
        "fix_params": {"rocm_version": "7.2.0"},
    },
    {
        "id": "triton_attention_fallback",
        "pattern": r"Using Triton Attention backend|FlashAttention.*not available",
        "cause": "FlashAttention unavailable, using Triton fallback",
        "severity": "warning",
        "explanation": (
            "FlashAttention is not available for this GPU/ROCm combo. Triton attention "
            "backend works but may be slower. This is informational on MI300X with ROCm 7.x."
        ),
        "fix_strategy": "none",
        "fix_params": {},
    },
    {
        "id": "tokenizer_timeout",
        "pattern": r"Tokenizer.*timed out|tokenizer.*connection.*refused",
        "cause": "HuggingFace tokenizer download failed or timed out",
        "severity": "medium",
        "explanation": (
            "Model tokenizer couldn't be downloaded. This happens with network issues "
            "or private models without authentication."
        ),
        "fix_strategy": "set_hf_token_or_cache",
        "fix_params": {"HF_TOKEN": "required", "HF_HOME": "/root/.cache/huggingface"},
    },
    {
        "id": "port_in_use",
        "pattern": r"Address already in use|bind.*failed|port.*already.*allocated",
        "cause": "vLLM server port already occupied",
        "severity": "medium",
        "explanation": (
            "Another vLLM instance or process is already using the target port. "
            "Common when restarting servers without proper shutdown."
        ),
        "fix_strategy": "change_port_or_kill",
        "fix_params": {"port": 8001},
    },
    {
        "id": "engine_dead_after_warmup",
        "pattern": r"EngineCore failed to start|Engine core initialization failed",
        "cause": "vLLM engine failed during initialization",
        "severity": "critical",
        "explanation": (
            "The vLLM engine process crashed after loading model weights but before "
            "completing initialization. Usually a KV cache allocation failure or "
            "GPU memory fragmentation issue."
        ),
        "fix_strategy": "increase_gpu_memory_utilization",
        "fix_params": {"gpu_memory_utilization": 0.9},
    },
    {
        "id": "batch_too_large_runtime",
        "pattern": r"Request.*too large|Batch.*exceeds.*memory|num_seqs.*exceeds.*max",
        "cause": "Runtime batch size exceeds serving capacity",
        "severity": "high",
        "explanation": (
            "Too many concurrent requests or sequences are batched together, "
            "exceeding the available KV cache blocks allocated at startup."
        ),
        "fix_strategy": "reduce_max_num_seqs",
        "fix_params": {"max_num_seqs": 32},
    },
    {
        "id": "gpu_not_detected",
        "pattern": r"No (AMD|ROCm|HIP) GPU.*detected|RuntimeError.*No GPU|hip.*device.*not found",
        "cause": "No AMD GPU detected by ROCm/HIP runtime",
        "severity": "critical",
        "explanation": (
            "The ROCm runtime cannot find any AMD GPU. Check that the Docker container "
            "has --device=/dev/kfd --device=/dev/dri and that ROCm drivers are loaded."
        ),
        "fix_strategy": "fix_docker_gpu_passthrough",
        "fix_params": {"docker_flags": "--device=/dev/kfd --device=/dev/dri --group-add video"},
    },
]


def classify_failure(stderr: str, exit_code: int = 1) -> dict[str, Any] | None:
    """Match stderr against known vLLM/ROCm failure patterns.

    Returns the first matching pattern with diagnosis details, or None.
    """
    if not stderr:
        return None

    for pattern in VLLM_FAILURE_PATTERNS:
        match = re.search(pattern["pattern"], stderr, re.IGNORECASE | re.MULTILINE)
        if match:
            return {
                "pattern_id": pattern["id"],
                "cause": pattern["cause"],
                "severity": pattern["severity"],
                "explanation": pattern["explanation"],
                "fix_strategy": pattern["fix_strategy"],
                "fix_params": pattern["fix_params"],
                "matched_text": match.group(0),
                "confidence": 0.95 if pattern["severity"] == "critical" else 0.80,
            }

    return None


def get_all_patterns() -> list[dict[str, str]]:
    """Return summary of all known patterns (for UI/documentation)."""
    return [
        {"id": p["id"], "cause": p["cause"], "severity": p["severity"]}
        for p in VLLM_FAILURE_PATTERNS
    ]


def suggest_vllm_config(
    model_size_gb: float,
    gpu_vram_gb: float = 192.0,
    target_context_len: int = 4096,
) -> dict[str, Any]:
    """Suggest safe vLLM config based on model size and available VRAM.

    Uses the formula: usable_vram = gpu_vram * gpu_memory_utilization - model_size
    KV cache must be positive for the engine to start.
    """
    # Leave 10% headroom for runtime allocations
    safe_utilization = min(0.95, (model_size_gb + 5.0) / gpu_vram_gb + 0.1)
    safe_utilization = max(0.5, safe_utilization)

    usable_vram = gpu_vram_gb * safe_utilization - model_size_gb
    # Each token in KV cache uses ~0.5MB for 7B model (rough estimate)
    max_safe_context = int(usable_vram * 1024 / 0.5) if usable_vram > 0 else 2048
    max_safe_context = min(max_safe_context, target_context_len)

    return {
        "gpu_memory_utilization": round(safe_utilization, 2),
        "max_model_len": max_safe_context,
        "estimated_kv_cache_gb": round(usable_vram, 1),
        "model_size_gb": model_size_gb,
        "gpu_vram_gb": gpu_vram_gb,
    }
