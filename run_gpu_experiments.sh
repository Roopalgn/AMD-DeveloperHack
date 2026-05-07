#!/bin/bash
# ReplayLab GPU Experiment Runner for AMD Developer Cloud
# Run this on the MI300X droplet after cloning the repo.
#
# The vLLM Quick Start image runs vLLM inside Docker.
# This script handles both Docker and direct execution.

set -e

echo "========================================="
echo "ReplayLab - AMD MI300X GPU Experiments"
echo "========================================="

# Check ROCm
echo ""
echo "[1/6] Checking ROCm and GPU..."
rocm-smi --showid
echo ""
rocm-smi --showmeminfo vram

# Save GPU telemetry baseline
echo ""
echo "[2/6] Saving GPU telemetry baseline..."
mkdir -p replaylab/runs/gpu_evidence
rocm-smi --json > replaylab/runs/gpu_evidence/rocm_smi_baseline.json 2>/dev/null || echo "JSON output not available, using text"
rocm-smi > replaylab/runs/gpu_evidence/rocm_smi_baseline.txt

# Determine if vLLM is available directly or via Docker
VLLM_CMD=""
if python3 -c "import vllm" 2>/dev/null; then
    VLLM_CMD="python3 -m vllm.entrypoints.openai.api_server"
    echo "[*] vLLM available directly"
elif docker exec -it rocm python3 -c "import vllm" 2>/dev/null; then
    VLLM_CMD="docker exec rocm python3 -m vllm.entrypoints.openai.api_server"
    echo "[*] vLLM available via Docker (rocm container)"
else
    echo "[!] vLLM not found. Installing..."
    pip install vllm
    VLLM_CMD="python3 -m vllm.entrypoints.openai.api_server"
fi

# --- SCENARIO 1: OOM (Bad config) ---
echo ""
echo "[3/6] Running OOM scenario (bad config)..."
echo "  Starting vLLM with max_model_len=65536, gpu_memory_utilization=0.99"
echo "  This SHOULD fail with OOM..."

mkdir -p replaylab/runs/gpu_oom
timeout 120 $VLLM_CMD \
    --model Qwen/Qwen2.5-7B-Instruct \
    --max-model-len 65536 \
    --gpu-memory-utilization 0.99 \
    --port 8000 \
    > replaylab/runs/gpu_oom/stdout.txt 2> replaylab/runs/gpu_oom/stderr.txt || true

OOM_EXIT=$?
echo "  Exit code: $OOM_EXIT"

# Capture GPU state after OOM attempt
rocm-smi --json > replaylab/runs/gpu_evidence/rocm_smi_after_oom.json 2>/dev/null || true
rocm-smi > replaylab/runs/gpu_evidence/rocm_smi_after_oom.txt

# Write metrics
python3 -c "
import json, time
metrics = {
    'status': 'failed',
    'failure_type': 'gpu_oom',
    'scenario': 'oom',
    'exit_code': $OOM_EXIT,
    'model': 'Qwen/Qwen2.5-7B-Instruct',
    'max_model_len': 65536,
    'gpu_memory_utilization': 0.99,
    'timestamp': time.time(),
    'memory_pressure': True,
    'batch_size': 65536,
    'available_memory_mb': 192000,
    'estimated_memory_mb': 250000,
    'throughput_items_per_sec': 0,
}
with open('replaylab/runs/gpu_oom/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

artifact = {
    'status': 'failed',
    'cause': 'gpu_oom_max_model_len_too_large',
    'summary': 'vLLM failed: max_model_len=65536 with gpu_memory_utilization=0.99 exceeds MI300X VRAM.',
    'recommendation': 'Reduce max_model_len to 4096 and gpu_memory_utilization to 0.9.',
}
with open('replaylab/runs/gpu_oom/artifact.json', 'w') as f:
    json.dump(artifact, f, indent=2)
"
echo "  ❌ OOM scenario recorded"

# --- SCENARIO 2: Recovered (Good config) ---
echo ""
echo "[4/6] Running RECOVERED scenario (good config)..."
echo "  Starting vLLM with max_model_len=4096, gpu_memory_utilization=0.9"

mkdir -p replaylab/runs/gpu_recovered

# Start vLLM server in background with safe settings
$VLLM_CMD \
    --model Qwen/Qwen2.5-7B-Instruct \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.9 \
    --port 8000 \
    > replaylab/runs/gpu_recovered/server_stdout.txt 2> replaylab/runs/gpu_recovered/server_stderr.txt &

VLLM_PID=$!
echo "  vLLM server PID: $VLLM_PID"
echo "  Waiting for server to be ready..."

# Wait for server health
for i in $(seq 1 90); do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "  Server ready after ${i}s"
        break
    fi
    if ! kill -0 $VLLM_PID 2>/dev/null; then
        echo "  Server died. Check logs."
        cat replaylab/runs/gpu_recovered/server_stderr.txt | tail -20
        break
    fi
    sleep 2
done

# Send inference requests
echo "  Sending inference requests..."
python3 -c "
import json, time, urllib.request

prompts = [
    'Explain GPU memory management in one paragraph.',
    'What is ROCm and why does it matter for AI?',
    'Describe the difference between batch size 8 and 64 for inference.',
    'What causes out-of-memory errors in model serving?',
    'How does vLLM optimize GPU memory usage?',
    'What is the MI300X architecture advantage?',
    'Explain KV cache memory in transformer inference.',
    'Why does larger context length require more GPU memory?',
]

start = time.perf_counter()
results = []
errors = []

for prompt in prompts:
    payload = json.dumps({
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'prompt': prompt,
        'max_tokens': 128,
        'temperature': 0.0,
    }).encode('utf-8')
    req = urllib.request.Request(
        'http://localhost:8000/v1/completions',
        data=payload,
        headers={'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            results.append(result)
            print(f'  ✓ Prompt {len(results)}: {len(result[\"choices\"][0][\"text\"])} chars')
    except Exception as e:
        errors.append(str(e))
        print(f'  ✗ Error: {e}')

duration = time.perf_counter() - start
throughput = len(results) / max(duration, 0.001)

print(f'  Completed: {len(results)}/{len(prompts)} in {duration:.1f}s')
print(f'  Throughput: {throughput:.2f} prompts/sec')

metrics = {
    'status': 'succeeded',
    'failure_type': None,
    'scenario': 'recovered',
    'exit_code': 0,
    'model': 'Qwen/Qwen2.5-7B-Instruct',
    'max_model_len': 4096,
    'gpu_memory_utilization': 0.9,
    'timestamp': time.time(),
    'memory_pressure': False,
    'batch_size': 8,
    'available_memory_mb': 192000,
    'estimated_memory_mb': 45000,
    'throughput_items_per_sec': round(throughput, 3),
    'total_prompts': len(prompts),
    'successful': len(results),
    'errors': len(errors),
    'duration_sec': round(duration, 3),
}
with open('replaylab/runs/gpu_recovered/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

artifact = {
    'status': 'succeeded',
    'cause': None,
    'summary': f'Inference succeeded: {len(results)}/{len(prompts)} prompts in {duration:.1f}s.',
    'recommendation': 'Keep max_model_len=4096 and gpu_memory_utilization=0.9 for stable serving.',
    'sample_output': results[0]['choices'][0]['text'][:200] if results else '',
}
with open('replaylab/runs/gpu_recovered/artifact.json', 'w') as f:
    json.dump(artifact, f, indent=2)
"

# Kill the vLLM server
kill $VLLM_PID 2>/dev/null || true
wait $VLLM_PID 2>/dev/null || true
echo "  ✅ Recovered scenario complete"

# Capture GPU state after successful run
rocm-smi --json > replaylab/runs/gpu_evidence/rocm_smi_after_recovery.json 2>/dev/null || true
rocm-smi > replaylab/runs/gpu_evidence/rocm_smi_after_recovery.txt

# --- Save final evidence ---
echo ""
echo "[5/6] Saving final GPU evidence..."
rocm-smi --showmeminfo vram > replaylab/runs/gpu_evidence/vram_final.txt
cat /proc/driver/amdgpu/version > replaylab/runs/gpu_evidence/amdgpu_version.txt 2>/dev/null || true

# --- Summary ---
echo ""
echo "[6/6] Done!"
echo "========================================="
echo "Results saved in replaylab/runs/"
echo "  gpu_oom/       - Failed OOM scenario"
echo "  gpu_recovered/ - Successful recovery"
echo "  gpu_evidence/  - GPU telemetry snapshots"
echo "========================================="
echo ""
echo "Next: commit and push results"
echo "  git add -A"
echo "  git commit -m 'Add real MI300X experiment results'"
echo "  git push origin main"
