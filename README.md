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
✅ success   memory_pressure=False, throughput=648k items/sec
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
| **Application of Technology** | AMD Instinct MI300X, ROCm, rocm-smi, vLLM, Qwen, Hugging Face |
| **Originality** | GPU experiment flight recorder with autonomous recovery — not a chatbot or RAG |
| **Business Value** | Saves ML engineers hours of debugging; makes GPU experiments reproducible |
| **Presentation** | Live demo: failure → AI diagnosis → fix → verified recovery in 30 seconds |

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

In the demo, a GPU-style experiment fails because `batch_size=64` creates memory pressure. ReplayLab records the command, logs, exit code, metrics, and artifacts; identifies the oversized batch as the cause; generates a fixed replay command using `batch_size=8`; reruns the experiment; and verifies success with improved throughput.

The project is designed for AMD GPU workflows where runtime behavior matters: memory pressure, throughput, batch sizing, and failed model execution. Instead of being another log viewer or monitoring dashboard, ReplayLab connects failure to recovery and produces a replayable evidence trail that engineers can trust.
