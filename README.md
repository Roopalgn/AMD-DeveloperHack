# ReplayLab — The Black Box for GPU Experiments

**AMD Developer Hackathon 2026 | Track 1: AI Agents & Agentic Workflows**

ReplayLab is an autonomous GPU experiment flight recorder. It watches a real AMD GPU workload fail, diagnoses the root cause using AI, generates a corrected replay command, and verifies the recovery — all without human intervention.

> Failed runs aren't bugs to hide. They're evidence to learn from.

---

## The Problem

GPU experiments fail in expensive, messy ways: bad batch sizes cause OOM, configs drift between runs, model paths break, and serving parameters silently degrade performance. Engineers fix these quickly — but later can't prove *what* failed, *what* changed, or *how* to reproduce the working result.

For ML teams shipping under deadline, this makes GPU development fragile and hard to trust.

## How ReplayLab Solves It

```
FAIL → RECORD → DIAGNOSE → FIX → REPLAY → VERIFY
```

1. **FAIL** — A GPU experiment fails or degrades (real AMD GPU workload)
2. **RECORD** — ReplayLab captures command, config, logs, exit code, GPU telemetry, and artifacts
3. **DIAGNOSE** — AI agent identifies the root cause (LLM-powered via Qwen on AMD GPU + rule-based fallback)
4. **FIX** — Generates a corrected replay command with the minimum parameter change
5. **REPLAY** — Executes the fixed command automatically
6. **VERIFY** — Proves recovery with before/after metrics and GPU evidence

## Real GPU Evidence (AMD Instinct MI300X)

We ran ReplayLab on an AMD Instinct MI300X (192 GB HBM3) via AMD Developer Cloud with vLLM 0.17.1 / ROCm 7.2.0 and Qwen2.5-7B-Instruct.

| Metric | OOM Run (bad) | Recovered Run (good) |
|--------|--------------|---------------------|
| `gpu_memory_utilization` | 0.08 (deliberately constrained) | 0.9 |
| `max_model_len` | 32768 | 4096 |
| Available KV cache | **-1.84 GiB** (negative → OOM) | 172.5 GiB |
| Status | `ValueError: No available memory` | 8/8 prompts completed |
| Throughput | 0 tokens/sec | **230.17 tokens/sec** |

Evidence files: [`replaylab/runs/gpu_oom/`](replaylab/runs/gpu_oom/) and [`replaylab/runs/gpu_recovered/`](replaylab/runs/gpu_recovered/)

## Demo (30 seconds)

```bash
python replaylab/backend/full_demo.py
```

```
[GPU] source: rocm-smi
========================
ReplayLab Live Recovery
========================
❌ failure   batch_size=64, memory_pressure=True
🔍 diagnosis memory pressure from oversized batch
🤖 LLM says: OOM caused by batch_size exceeding VRAM capacity
🔧 fix       batch_size 64 -> 8
🚀 replay    running corrected config...
✅ success   memory_pressure=False, throughput=230 tok/sec
========================
📄 Timeline report: replaylab/runs/report.html
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ReplayLab Agent Loop                   │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│  Runner  │  GPU     │ Diagnoser│ Planner  │  Verifier   │
│ /Recorder│ Telemetry│ (AI+Rule)│          │             │
├──────────┼──────────┼──────────┼──────────┼─────────────┤
│ Execute  │ rocm-smi │ Qwen LLM │ Config   │ Re-execute  │
│ Capture  │ amd-smi  │ Pattern  │ Patch    │ Compare     │
│ Store    │ vLLM     │ Match    │ Command  │ Validate    │
└──────────┴──────────┴──────────┴──────────┴─────────────┘
                           │
                    AMD Instinct MI300X
                    (ROCm / vLLM / PyTorch)
```

## Why AMD GPU Matters Here

- The **observed workload** runs on AMD Instinct MI300X via AMD Developer Cloud
- **GPU telemetry** is collected via `rocm-smi` / `amd-smi` (memory, utilization, throughput)
- **LLM diagnosis** uses Qwen model served by vLLM on AMD GPU with ROCm
- **Before/after proof** shows GPU memory pressure → recovery with real hardware metrics
- CPU-only alternatives cannot reproduce hardware-bound failures or demonstrate recovery

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Compute | AMD Instinct MI300X, AMD Developer Cloud |
| GPU Platform | ROCm, rocm-smi, amd-smi |
| LLM Inference | Qwen2.5-7B-Instruct via vLLM on AMD GPU |
| Language | Python (stdlib for core, optional deps for full features) |
| Model Hub | Hugging Face (model hosting + Space deployment) |
| Telemetry | rocm-smi JSON output, runtime metrics |
| Report | Self-contained HTML timeline |

## Project Structure

```
replaylab/
  backend/
    runner.py           # Experiment execution and evidence capture
    gpu_telemetry.py    # AMD GPU metrics (rocm-smi/amd-smi)
    diagnoser.py        # Rule-based failure diagnosis
    llm_diagnoser.py    # LLM-powered diagnosis (Qwen on AMD GPU)
    planner.py          # Replay command generator
    verifier.py         # Recovery verification
    report.py           # HTML timeline report generator
    full_demo.py        # One-click demo flow
  demo/
    demo_experiment.py  # Controlled GPU experiment (fail/succeed)
    config_bad.json     # Intentionally broken config (OOM)
    config_good.json    # Corrected config (recovered)
  runs/                 # Captured run evidence (auto-generated)
    gpu_oom/            # Real MI300X OOM evidence (vLLM crash)
    gpu_recovered/      # Real MI300X recovery (230 tok/sec)
    gpu_evidence/       # Inference results + rocm-smi baseline
```

## Quick Start

```bash
# Clone and run (no dependencies needed for basic demo)
git clone <repo-url>
cd AMD-DeveloperHack
python replaylab/backend/full_demo.py

# On AMD Developer Cloud (full features)
pip install -r requirements.txt
export REPLAYLAB_VLLM_URL=http://localhost:8000/v1/chat/completions
python replaylab/backend/full_demo.py
```

## What Makes This Agentic

ReplayLab makes **autonomous decisions under uncertainty**:

- Decides whether a run failed, degraded, or succeeded
- Classifies the root cause from logs, configs, and GPU metrics
- Chooses the minimum fix (not a generic suggestion — a specific parameter change)
- Executes the fix and validates recovery without human approval
- Revises its diagnosis if the first fix fails

This is not a log viewer or a dashboard. It's a closed-loop recovery agent.

## Judging Criteria Alignment

| Criteria | Evidence |
|----------|----------|
| **Application of Technology** | AMD Instinct MI300X, ROCm 7.2.0, rocm-smi, vLLM 0.17.1, Qwen2.5-7B-Instruct, Hugging Face |
| **Originality** | GPU experiment flight recorder with autonomous recovery — not a chatbot or RAG |
| **Business Value** | Saves ML engineers hours of debugging; makes GPU experiments reproducible |
| **Presentation** | Live demo: real OOM → AI diagnosis → fix → verified recovery at 230 tok/sec |

---

*Built for the AMD Developer Hackathon 2026*

## Impact

ReplayLab is built for ML engineers who need to move fast without losing reproducibility.

It helps teams answer the questions that matter after a failed GPU run:

- What failed?
- Why did it fail?
- What changed?
- What command fixed it?
- Did performance improve?
- Can someone else reproduce the result?

For startups and hackathon teams, that means fewer fragile demos, clearer engineering evidence, and faster recovery when GPU experiments break.

## Long Description

ReplayLab helps ML engineers recover from failed GPU experiments without losing reproducibility.

In the demo, a GPU experiment fails because `gpu_memory_utilization=0.08` starves vLLM of VRAM on an AMD Instinct MI300X — the model loads at 14.35 GiB but leaves -1.84 GiB for KV cache, crashing with `ValueError: No available memory`. ReplayLab records the command, logs, exit code, metrics, and GPU telemetry; identifies the constrained memory setting as the cause; generates a fixed config using `gpu_memory_utilization=0.9`; reruns the experiment; and verifies success at 230.17 tokens/sec (8/8 prompts completed) — all validated on real AMD hardware.

The project is designed for AMD GPU workflows where runtime behavior matters: memory pressure, throughput, batch sizing, and failed model execution. Instead of being another log viewer or monitoring dashboard, ReplayLab connects failure to recovery and produces a replayable evidence trail that engineers can trust.
