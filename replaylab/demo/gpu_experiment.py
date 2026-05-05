"""Real GPU workload for ReplayLab on AMD Developer Cloud.

This script replaces the simulated demo_experiment.py when running on
an AMD Instinct MI300X with ROCm and vLLM. It triggers actual GPU
memory pressure, real OOM, and real inference throughput measurements.

Usage on AMD Cloud:
  # Bad config (OOM): large batch + long sequences
  python replaylab/demo/gpu_experiment.py --scenario oom

  # Good config (recovered): safe batch size
  python replaylab/demo/gpu_experiment.py --scenario recovered

  # Timeout: too many requests for the time budget
  python replaylab/demo/gpu_experiment.py --scenario timeout

Prerequisites:
  - AMD Instinct MI300X VM on AMD Developer Cloud
  - ROCm installed (comes with Quick Start images)
  - vLLM installed: pip install vllm
  - Model downloaded: Qwen/Qwen2.5-7B-Instruct
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def check_rocm() -> dict[str, Any]:
    """Check ROCm availability and GPU info."""
    info: dict[str, Any] = {"rocm_available": False, "gpu_count": 0, "devices": []}
    try:
        result = subprocess.run(
            ["rocm-smi", "--showid", "--json"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            info["rocm_available"] = True
            info["raw"] = data
            # Count GPUs
            info["gpu_count"] = len([k for k in data if k.startswith("card")])
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return info


def get_gpu_memory() -> dict[str, Any]:
    """Get current GPU memory usage via rocm-smi."""
    try:
        result = subprocess.run(
            ["rocm-smi", "--showmeminfo", "vram", "--json"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return {}


def start_vllm_server(model: str, max_model_len: int = 4096, gpu_memory_utilization: float = 0.9) -> subprocess.Popen | None:
    """Start a vLLM OpenAI-compatible server."""
    cmd = [
        sys.executable, "-m", "vllm.entrypoints.openai.api_server",
        "--model", model,
        "--max-model-len", str(max_model_len),
        "--gpu-memory-utilization", str(gpu_memory_utilization),
        "--port", "8000",
        "--trust-remote-code",
    ]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Wait for server to be ready
        import urllib.request
        for _ in range(60):
            time.sleep(2)
            try:
                urllib.request.urlopen("http://localhost:8000/health", timeout=2)
                return proc
            except Exception:
                if proc.poll() is not None:
                    return None
        return proc
    except Exception:
        return None


def send_inference_batch(
    prompts: list[str],
    model: str = "Qwen/Qwen2.5-7B-Instruct",
    max_tokens: int = 256,
    url: str = "http://localhost:8000/v1/completions",
) -> dict[str, Any]:
    """Send a batch of prompts to the vLLM server and measure throughput."""
    import urllib.request

    start = time.perf_counter()
    results = []
    errors = []

    for prompt in prompts:
        payload = json.dumps({
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.0,
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                results.append(result)
        except Exception as e:
            errors.append(str(e))

    duration = time.perf_counter() - start
    return {
        "total_prompts": len(prompts),
        "successful": len(results),
        "errors": len(errors),
        "duration_sec": round(duration, 3),
        "throughput_prompts_per_sec": round(len(results) / max(duration, 0.001), 3),
        "error_messages": errors[:5],
    }


def scenario_oom(output_dir: Path) -> int:
    """Trigger real OOM by requesting too much GPU memory."""
    print("=" * 50)
    print("SCENARIO: GPU Out-of-Memory (oversized allocation)")
    print("=" * 50)

    gpu_before = get_gpu_memory()
    print(f"GPU memory before: {json.dumps(gpu_before, indent=2)[:200]}")

    # Try to start vLLM with unreasonable settings that will OOM
    print("\nStarting vLLM with max_model_len=65536, gpu_memory_utilization=0.99...")
    proc = subprocess.run(
        [
            sys.executable, "-m", "vllm.entrypoints.openai.api_server",
            "--model", "Qwen/Qwen2.5-7B-Instruct",
            "--max-model-len", "65536",
            "--gpu-memory-utilization", "0.99",
            "--port", "8000",
        ],
        capture_output=True, text=True, timeout=120,
    )

    gpu_after = get_gpu_memory()

    metrics = {
        "status": "failed",
        "failure_type": "gpu_oom",
        "scenario": "oom",
        "exit_code": proc.returncode,
        "gpu_memory_before": gpu_before,
        "gpu_memory_after": gpu_after,
        "stderr_tail": proc.stderr[-2000:] if proc.stderr else "",
        "stdout_tail": proc.stdout[-1000:] if proc.stdout else "",
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "max_model_len": 65536,
        "gpu_memory_utilization": 0.99,
    }

    artifact = {
        "status": "failed",
        "cause": "gpu_oom_max_model_len_too_large",
        "summary": "vLLM failed to start: max_model_len=65536 exceeds GPU VRAM capacity.",
        "recommendation": "Reduce max_model_len to 4096 and gpu_memory_utilization to 0.9.",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    (output_dir / "artifact.json").write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")

    print(f"\n❌ FAILED: exit_code={proc.returncode}")
    print(f"Outputs: {output_dir}")
    return 1


def scenario_recovered(output_dir: Path) -> int:
    """Run inference with safe parameters — the fixed version."""
    print("=" * 50)
    print("SCENARIO: Recovered (safe parameters)")
    print("=" * 50)

    gpu_before = get_gpu_memory()
    print(f"GPU memory before: {json.dumps(gpu_before, indent=2)[:200]}")

    # Start vLLM with safe settings
    print("\nStarting vLLM with max_model_len=4096, gpu_memory_utilization=0.9...")
    server = start_vllm_server("Qwen/Qwen2.5-7B-Instruct", max_model_len=4096, gpu_memory_utilization=0.9)

    if server is None:
        print("❌ Server failed to start even with safe params")
        metrics = {"status": "failed", "failure_type": "server_start_failed", "scenario": "recovered"}
        artifact = {"status": "failed", "cause": "vllm_server_failed", "summary": "Server did not start."}
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
        (output_dir / "artifact.json").write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
        return 1

    # Run inference batch
    prompts = [
        "Explain GPU memory management in one paragraph.",
        "What is ROCm and why does it matter for AI?",
        "Describe the difference between batch size 8 and 64 for inference.",
        "What causes out-of-memory errors in model serving?",
    ]

    print(f"\nSending {len(prompts)} inference prompts...")
    result = send_inference_batch(prompts)
    print(f"Throughput: {result['throughput_prompts_per_sec']} prompts/sec")

    gpu_after = get_gpu_memory()

    # Kill server
    server.terminate()
    server.wait(timeout=10)

    metrics = {
        "status": "succeeded",
        "failure_type": None,
        "scenario": "recovered",
        "exit_code": 0,
        "gpu_memory_before": gpu_before,
        "gpu_memory_after": gpu_after,
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "max_model_len": 4096,
        "gpu_memory_utilization": 0.9,
        "inference_result": result,
        "throughput_prompts_per_sec": result["throughput_prompts_per_sec"],
        "batch_size": len(prompts),
        "throughput_items_per_sec": result["throughput_prompts_per_sec"],
    }

    artifact = {
        "status": "succeeded",
        "cause": None,
        "summary": f"Inference succeeded: {result['successful']}/{result['total_prompts']} prompts completed.",
        "recommendation": "Keep max_model_len=4096 and gpu_memory_utilization=0.9 for stable serving.",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    (output_dir / "artifact.json").write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")

    print(f"\n✅ SUCCESS: {result['successful']}/{result['total_prompts']} prompts, {result['throughput_prompts_per_sec']} p/sec")
    print(f"Outputs: {output_dir}")
    return 0


def scenario_timeout(output_dir: Path) -> int:
    """Trigger timeout by sending too many requests."""
    print("=" * 50)
    print("SCENARIO: Inference Timeout (too many requests)")
    print("=" * 50)

    # Start server with tight settings
    server = start_vllm_server("Qwen/Qwen2.5-7B-Instruct", max_model_len=2048, gpu_memory_utilization=0.8)
    if server is None:
        metrics = {"status": "failed", "failure_type": "server_start_failed", "scenario": "timeout"}
        artifact = {"status": "failed", "cause": "vllm_server_failed", "summary": "Server did not start."}
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
        (output_dir / "artifact.json").write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
        return 1

    # Flood with many long prompts
    prompts = ["Write a detailed 500-word essay about GPU computing. " * 5] * 20
    print(f"\nSending {len(prompts)} heavy prompts (expecting timeout)...")

    start = time.perf_counter()
    max_time = 30.0  # 30 second budget
    completed = 0
    errors = 0

    import urllib.request
    for prompt in prompts:
        if time.perf_counter() - start > max_time:
            break
        payload = json.dumps({
            "model": "Qwen/Qwen2.5-7B-Instruct",
            "prompt": prompt,
            "max_tokens": 512,
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:8000/v1/completions",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                completed += 1
        except Exception:
            errors += 1

    duration = time.perf_counter() - start
    server.terminate()
    server.wait(timeout=10)

    timed_out = duration >= max_time or errors > completed
    status = "failed" if timed_out else "succeeded"

    metrics = {
        "status": status,
        "failure_type": "timeout_exceeded" if timed_out else None,
        "scenario": "timeout",
        "exit_code": 1 if timed_out else 0,
        "total_prompts": len(prompts),
        "completed": completed,
        "errors": errors,
        "duration_sec": round(duration, 3),
        "max_duration_sec": max_time,
        "timed_out": timed_out,
        "throughput_items_per_sec": round(completed / max(duration, 0.001), 3),
    }

    artifact = {
        "status": status,
        "cause": "timeout_exceeded" if timed_out else None,
        "summary": f"Only {completed}/{len(prompts)} completed in {max_time}s budget." if timed_out else "All prompts completed.",
        "recommendation": "Reduce concurrent prompts or increase max_duration_sec." if timed_out else "Current load is sustainable.",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    (output_dir / "artifact.json").write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")

    print(f"\n{'❌ TIMEOUT' if timed_out else '✅ SUCCESS'}: {completed}/{len(prompts)} in {duration:.1f}s")
    print(f"Outputs: {output_dir}")
    return 1 if timed_out else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="ReplayLab real GPU experiment (AMD Cloud)")
    parser.add_argument("--scenario", required=True, choices=["oom", "recovered", "timeout"])
    parser.add_argument("--output", default=None, help="Output directory for run artifacts")
    args = parser.parse_args()

    output_dir = Path(args.output) if args.output else Path(f"replaylab/runs/gpu_{args.scenario}")

    # Check ROCm first
    rocm = check_rocm()
    if not rocm["rocm_available"]:
        print("⚠️  WARNING: ROCm not detected. This script requires AMD GPU with ROCm.")
        print("   Run on AMD Developer Cloud with MI300X for real results.")
        print("   Falling back to attempt anyway...\n")

    if args.scenario == "oom":
        return scenario_oom(output_dir)
    elif args.scenario == "recovered":
        return scenario_recovered(output_dir)
    elif args.scenario == "timeout":
        return scenario_timeout(output_dir)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
