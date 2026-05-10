# ReplayLab — Submission Details

## Short Description

ReplayLab is a GPU experiment flight recorder with an autonomous recovery agent for AMD Instinct GPUs. It captures failures, diagnoses root causes using a vLLM taxonomy + LLM reasoning, generates fixes, reruns experiments, and verifies recovery — all in a single closed-loop cycle costing $0.14.

## Long Description

ReplayLab helps ML engineers recover from failed GPU experiments without losing reproducibility.

In the demo, a GPU experiment fails because `max_model_len=65536` — double the model's 32K context limit — causes vLLM to crash on startup on an AMD Instinct MI300X. ReplayLab records the command, logs, exit code, metrics, and GPU telemetry via rocm-smi; classifies the failure against a 10-pattern vLLM/ROCm taxonomy (`context_length_exceeded`); runs LLM-powered diagnosis using Qwen2.5-7B in 604ms; generates a fix (`max_model_len=32768`, `gpu_memory_utilization=0.9`); reruns the experiment; and verifies success at 227 tokens/sec (4/4 prompts completed) — all validated on real AMD hardware.

The project is designed for AMD GPU workflows where runtime behavior matters: memory pressure, throughput, batch sizing, and failed model execution. Instead of being another log viewer or monitoring dashboard, ReplayLab connects failure to recovery and produces a replayable evidence trail that engineers can trust.

## Target Customers

1. **ML Engineers at GPU-intensive startups** — Running inference/training on AMD GPUs who encounter OOM, throughput regression, and config issues daily
2. **MLOps/Platform teams** — Need automated incident response for GPU workloads in production; can't afford 2-hour manual debug cycles
3. **Research labs** — Running large-scale experiments where reproducibility and fast recovery matter more than cost
4. **AMD Developer Cloud users** — Teams already invested in AMD ecosystem (ROCm, MI300X) who need tooling purpose-built for their stack

## Market Sizing

| Segment | Estimate | Source |
|---------|----------|--------|
| GPU cloud market (2025) | $65B | Gartner |
| MLOps tooling market (2025) | $4.2B | MarketsAndMarkets |
| GPU debugging/observability (TAM) | ~$800M | 20% of MLOps spend is failure-related |
| AMD GPU workloads (SAM) | ~$120M | AMD's ~15% accelerator share × debugging spend |
| Early adopters reachable (SOM) | ~$5M | Teams actively on AMD Developer Cloud |

## Differentiation

| ReplayLab | Alternatives |
|-----------|-------------|
| Closed-loop (detect → diagnose → fix → verify) | Open-loop (alert only, human fixes) |
| GPU-native taxonomy (10 vLLM/ROCm patterns) | Generic log parsers |
| Sub-second diagnosis at $0.14/cycle | Manual debugging at $150/incident |
| Full evidence trail (before/after) | Dashboard metrics without context |
| Works with AMD ROCm stack | Mostly NVIDIA-focused tooling |

## Hackathon Context

- **Track**: Track 1 — AI Agents & Agentic Workflows
- **Event**: AMD Developer Hackathon 2026
- **Platform**: lablab.ai
- **Hardware**: AMD Instinct MI300X (192 GB HBM3) via AMD Developer Cloud
- **Team**: Latency Locksmith

## Technical Highlights

| Metric | Value |
|--------|-------|
| Model load (cold) | 14.35 GiB in 8.42s |
| Model load (warm) | 14.35 GiB in 2.58s |
| torch.compile (cold) | 16.28s |
| torch.compile (warm) | 5.95s |
| KV cache allocation | 155.31 GiB / 2,908,128 tokens |
| Max concurrency (32K ctx) | 88 sequences |
| Inference throughput | 227 tok/sec |
| Time to first token | 283ms |
| Full recovery cycle | ~4 min, $0.14 |
| Tests | 38 passing |

## Links

- **GitHub**: https://github.com/Roopalgn/AMD-DeveloperHack
- **HF Space**: https://huggingface.co/spaces/lablab-ai-amd-developer-hackathon/ReplayLab
- **Hackathon**: [lablab.ai AMD Developer Hackathon 2026](https://lablab.ai/event/amd-developer-hackathon-2026)
