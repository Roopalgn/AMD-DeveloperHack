---
title: ReplayLab
emoji: 🔬
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: true
license: mit
short_description: GPU experiment flight recorder — failure to recovery agent
tags:
  - amd
  - gpu
  - agents
  - rocm
  - experiment-tracking
  - debugging
---

# ReplayLab

**GPU experiment flight recorder that autonomously detects failures, diagnoses root causes, and replays corrected experiments — in a single closed-loop cycle costing $0.14.**

Built for the [AMD Developer Hackathon 2026](https://lablab.ai/event/amd-developer-hackathon-2026) · Track 1: AI Agents & Agentic Workflows

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![AMD MI300X](https://img.shields.io/badge/AMD-MI300X-ED1C24)](https://www.amd.com/)
[![ROCm](https://img.shields.io/badge/ROCm-7.2.0-orange)](https://rocm.docs.amd.com/)
[![vLLM](https://img.shields.io/badge/vLLM-0.17.1-blue)](https://github.com/vllm-project/vllm)
[![Tests](https://img.shields.io/badge/tests-38_passing-brightgreen)]()

## The Problem

Every ML engineer running GPU workloads hits the same wall: experiments fail silently (OOM, bad configs, timeouts), debugging takes hours of manual log-diving, and there's no reproducible trail from failure to recovery. Existing tools alert you that something broke — **none of them fix it**.

## The Solution

ReplayLab is the **black box flight recorder** for GPU experiments. It:

1. **Records** the failed experiment (command, config, metrics, GPU telemetry, stderr)
2. **Diagnoses** the root cause using a 10-pattern vLLM/ROCm failure taxonomy + optional LLM reasoning via Qwen2.5-7B
3. **Generates** a minimum-parameter fix (e.g., reduce batch_size from 64→8)
4. **Replays** the corrected experiment automatically
5. **Verifies** recovery with before/after evidence

This is a **closed-loop agentic system** — not a dashboard, not a log viewer.

## Architecture

```
User runs experiment
        ↓
┌──────────────────────────────────────────────────┐
│              REPLAYLAB AGENT LOOP                │
│                                                  │
│  [Runner]         Record command, stdout/stderr, │
│                   exit code, metrics, artifacts  │
│       ↓                                          │
│  [Taxonomy]       Match stderr against 10 known  │
│                   vLLM/ROCm failure patterns     │
│       ↓                                          │
│  [Diagnoser]      Rule-based comparison of       │
│                   failed vs baseline run          │
│       ↓                                          │
│  [LLM Diagnoser]  Qwen2.5-7B via vLLM provides  │
│                   natural-language explanation    │
│       ↓                                          │
│  [Planner]        Generate minimum fix           │
│       ↓                                          │
│  [Verifier]       Execute fix, confirm recovery  │
│       ↓                                          │
│  [Reporter]       HTML timeline + cost analysis  │
└──────────────────────────────────────────────────┘
        ↓
Recovered experiment with full evidence trail
```

## Three Failure Scenarios

ReplayLab handles three distinct GPU failure patterns:

| Scenario | Cause | Fix Applied | Recovery |
|----------|-------|-------------|----------|
| **GPU OOM** | `batch_size=64` exceeds VRAM | Reduce to `batch_size=8` | ✅ 648k items/sec |
| **Model Not Found** | Invalid model path `/nonexistent/...` | Correct path to `./models/qwen2.5-7b` | ✅ Model loads successfully |
| **Processing Timeout** | 100k items exceeds 2s limit | Reduce to 512 items | ✅ Completes within limit |

## vLLM Failure Taxonomy (Domain Knowledge)

10 expert-level patterns modeled from real MI300X failure modes:

| Pattern ID | Severity | Cause |
|-----------|----------|-------|
| `kv_cache_oom` | critical | KV cache memory exhaustion |
| `model_too_large` | critical | Model weights exceed GPU VRAM |
| `context_length_exceeded` | high | Context exceeds max_model_len |
| `rocm_version_mismatch` | critical | ROCm version incompatible |
| `triton_attention_fallback` | warning | FlashAttention unavailable |
| `tokenizer_timeout` | medium | HF tokenizer download failed |
| `port_in_use` | medium | Server port already occupied |
| `engine_dead_after_warmup` | critical | vLLM engine init failed |
| `batch_too_large_runtime` | high | Runtime batch exceeds capacity |
| `gpu_not_detected` | critical | No AMD GPU found by ROCm |

## Why Qwen2.5-7B (Not 70B+)

ReplayLab's LLM agent is a **diagnostic sidecar**, not the main workload. The experiment being debugged is the main GPU consumer. A 7B model:
- Loads in 8.42s cold / 2.58s warm (14.35 GiB)
- Leaves 155+ GiB free for the experiment's model + KV cache
- Provides sufficient reasoning for structured diagnosis prompts
- Costs $0.14 per full recovery cycle vs $150+ manual debugging

## Performance (Verified on AMD MI300X)

| Metric | Value |
|--------|-------|
| GPU | AMD Instinct MI300X (192 GB HBM3) |
| ROCm | 7.2.0 |
| vLLM | 0.17.1 |
| Model load (cold) | 14.35 GiB in 8.42s |
| Model load (warm) | 14.35 GiB in 2.58s |
| torch.compile (cold) | 16.28s |
| torch.compile (warm) | 5.95s |
| KV cache allocation | 155.31 GiB / 2,908,128 tokens |
| Max concurrency (32K ctx) | 88 sequences |
| Inference throughput | 230.17 tok/sec |
| TTFT | ~180ms |
| Full recovery cycle | ~4 min |
| Cost per recovery | **$0.14** |
| Manual debug cost (est.) | **$150.00** |
| Speedup | **1,071×** cost reduction |

## Agent Reasoning Trace

Each recovery produces a full reasoning chain:

```
[detect_failure]    Check exit code and run status → confirmed failure
[taxonomy_match]    Matched stderr against 10 known vLLM/ROCm patterns
[diagnose]          Compared failed vs baseline run metrics
[llm_diagnosis]     Qwen model provides NL explanation (if available)
[plan_fix]          Generated minimum parameter change
[verify_success]    Fix succeeded — recovery confirmed
[cost_estimate]     $0.14 GPU vs $150 manual (1,071× faster)
```

## Quickstart

```bash
# Clone and install
git clone https://github.com/Roopalgn/AMD-DeveloperHack
cd AMD-DeveloperHack
pip install -r requirements.txt

# Run full recovery demo (no GPU required)
python replaylab/backend/full_demo.py

# Run tests
pytest tests/ -v

# Launch Gradio interactive demo
python replaylab/frontend/gradio_app.py
```

## Repo Layout

```
AMD-DeveloperHack/
├── README.md                          This file (HF Space + GitHub)
├── SUBMISSION.md                      Hackathon submission details
├── requirements.txt
├── Dockerfile                         HF Space deployment
├── tests/                             38 tests, all passing
│   ├── test_diagnoser.py              Rule-based diagnosis tests
│   ├── test_planner.py                Fix generation tests
│   ├── test_report.py                 HTML report generation tests
│   ├── test_agent_loop.py             Multi-step agent tests
│   ├── test_vllm_taxonomy.py          10-pattern taxonomy tests
│   ├── test_llm_diagnoser.py          LLM fallback tests
│   ├── test_gpu_telemetry.py          GPU metrics collection tests
│   ├── test_runner.py                 Experiment runner tests
│   └── test_verifier.py              Replay verifier tests
├── replaylab/
│   ├── backend/
│   │   ├── agent.py                   Multi-step reasoning loop
│   │   ├── diagnoser.py               Rule-based failure diagnosis
│   │   ├── planner.py                 Fix generation engine
│   │   ├── runner.py                  Experiment runner/recorder
│   │   ├── verifier.py                Replay verification
│   │   ├── report.py                  HTML timeline report generator
│   │   ├── vllm_taxonomy.py           10 vLLM/ROCm failure patterns
│   │   ├── llm_diagnoser.py           Qwen-powered diagnosis agent
│   │   ├── gpu_telemetry.py           AMD GPU metrics (rocm-smi/amd-smi)
│   │   ├── app.py                     FastAPI web application
│   │   └── full_demo.py               End-to-end demo script
│   ├── frontend/
│   │   ├── gradio_app.py              Interactive Gradio demo
│   │   └── index.html                 Timeline UI
│   ├── demo/                          3 failure scenario configs
│   │   ├── config_bad.json            OOM trigger (batch_size=64)
│   │   ├── config_good.json           Recovered (batch_size=8)
│   │   ├── config_bad_model_path.json Model path error
│   │   ├── config_good_model_path.json Fixed model path
│   │   ├── config_bad_timeout.json    Timeout trigger (100k items)
│   │   ├── config_good_timeout.json   Fixed timeout (512 items)
│   │   └── demo_experiment.py         Controlled experiment simulator
│   └── runs/                          Pre-recorded GPU evidence
│       ├── gpu_oom/                   Real MI300X OOM crash data
│       ├── gpu_recovered/             Real MI300X recovery data
│       └── gpu_evidence/              vLLM startup, model, throughput
```

## Submission Checklist

- [x] Public GitHub repository
- [x] HF Space deployed (Gradio interactive demo)
- [x] MIT License
- [x] 3 failure scenarios (OOM, model path, timeout)
- [x] 10-pattern vLLM/ROCm failure taxonomy
- [x] LLM-powered diagnosis agent (Qwen2.5-7B)
- [x] Multi-step agent reasoning loop with traces
- [x] HTML timeline report with VRAM chart
- [x] Cost analysis ($0.14 vs $150 per incident)
- [x] GPU telemetry collection (rocm-smi/amd-smi)
- [x] Real AMD MI300X evidence files committed
- [x] 38 tests passing
- [x] SUBMISSION.md with market sizing

## Links & Team

| | |
|---|---|
| **GitHub** | https://github.com/Roopalgn/AMD-DeveloperHack |
| **HF Space** | https://huggingface.co/spaces/lablab-ai-amd-developer-hackathon/ReplayLab |
| **Hackathon** | [lablab.ai AMD Developer Hackathon 2026](https://lablab.ai/event/amd-developer-hackathon-2026) |
| **Team** | Latency Locksmith |
| **Track** | Track 1: AI Agents & Agentic Workflows |

Built for the [AMD Developer Hackathon 2026](https://lablab.ai/ai-hackathons/amd-developer).
