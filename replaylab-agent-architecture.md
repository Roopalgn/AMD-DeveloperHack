# ReplayLab Multi-Agent Architecture

ReplayLab should be built as a shared **run graph** with agents writing evidence, hypotheses, decisions, and verification results into the same state store.

The system is not "logs in, summary out." It watches a live AMD GPU experiment, branches when things go wrong, and iterates until it can explain or reproduce the run.

## Agent Architecture

| Agent | Role | Independent Decisions | Tools / Models |
|---|---|---|---|
| Run Observer Agent | Captures experiment commands, configs, logs, environment, artifacts, and run boundaries | What counts as a run, which files changed, which artifacts matter | Shell wrapper, file watcher, config parser, git diff, artifact store |
| GPU Telemetry Agent | Tracks AMD GPU behavior during the run | Whether the run is healthy, degraded, memory-bound, idle, or unstable | `rocm-smi` / `amd-smi`, runtime metrics, vLLM/server stats, benchmark probes |
| Failure Diagnoser Agent | Explains why the run failed or degraded | Which error signal matters, likely root cause, confidence score, whether more evidence is needed | LLM reasoning, error-pattern retrieval, log parser, config diff analyzer |
| Replay Planner Agent | Builds the minimum reproducible recovery path | Which command/config should be replayed, what fix to apply, what evidence to preserve | Command generator, config patch generator, dependency/environment resolver |
| Verification Agent | Tests whether the replay plan actually works | Accept/reject recovery, compare before/after metrics, decide if run is demo-worthy | AMD GPU runner, eval script, benchmark script, metric scorer |

## Roles And Responsibilities

## Run Observer Agent

- Acts as the flight recorder.
- Captures evidence before the system knows whether the run will matter.
- Tracks commands, configs, logs, artifacts, environment details, and run boundaries.

## GPU Telemetry Agent

- Acts as the hardware witness.
- Proves that failure or improvement happened under real AMD GPU constraints.
- Tracks GPU memory, utilization, latency, throughput, runtime duration, and degraded execution.

## Failure Diagnoser Agent

- Acts as the causal reasoner.
- Compares logs, configs, metrics, and artifacts.
- Produces ranked explanations with confidence and asks for more evidence when needed.

## Replay Planner Agent

- Acts as the recovery operator.
- Turns diagnosis into an executable rerun plan.
- Generates the minimum reproducible command, config change, and replay capsule.

## Verification Agent

- Acts as the skeptic.
- Reruns or checks the recovery path.
- Refuses to mark success without evidence.

## Interaction Flow

1. User launches an experiment through ReplayLab.
2. Run Observer and GPU Telemetry start simultaneously.
3. Run Observer streams logs, command metadata, config snapshots, and artifact paths into the run graph.
4. GPU Telemetry streams GPU memory, utilization, latency, throughput, and runtime state into the same graph.
5. If the run succeeds cleanly, Replay Planner creates a reproducible capsule.
6. If the run fails or degrades, Failure Diagnoser generates ranked hypotheses.
7. Replay Planner selects the smallest credible fix and creates a rerun command.
8. Verification Agent executes or validates the replay.
9. If verification fails, Diagnoser revises the hypothesis and Planner tries another recovery path.
10. If verification succeeds, ReplayLab produces the final timeline: failed run, cause, fix, recovered run, before/after metrics.

## Dynamic Branching

ReplayLab should branch based on what happens during the run.

| Situation | System Behavior |
|---|---|
| Run succeeds | Build replay capsule and score reproducibility |
| GPU memory spikes | Diagnose batch, concurrency, or model-size issue |
| Logs show missing artifact | Check paths, configs, model cache, and dependency state |
| Metrics degrade but logs look clean | Compare telemetry windows and benchmark behavior |
| Cause is ambiguous | Run competing diagnosis hypotheses |
| Fix fails | Loop back, revise diagnosis, and generate alternate replay |
| Recovery succeeds | Freeze evidence and produce final reproducible path |

## Memory Layers

## Short-Term Memory

- Active run graph.
- Commands, configs, logs, metrics, artifacts, hypotheses, decisions, and verification status.

## Long-Term Memory

- Known failure patterns.
- Previous successful configs.
- Common ROCm/model-serving errors.
- Benchmark baselines.
- Reusable replay templates.

## Tool Memory

- Every agent action is recorded.
- Judges can inspect not only the final answer but also why the system chose that path.

## Tool Usage

- Shell wrapper for launching experiments.
- File watcher for configs/artifacts.
- Log parser for structured evidence extraction.
- Config diff analyzer.
- `rocm-smi` or `amd-smi` for AMD GPU telemetry.
- vLLM/server metrics when applicable.
- Benchmark/eval script for before/after comparison.
- LLM or local model for diagnosis, summarization, and recovery planning.

## Parallelism

## During Observation

- Run Observer streams logs and config changes.
- GPU Telemetry samples AMD GPU metrics.
- Failure Diagnoser can begin early anomaly detection before the run ends.

## During Diagnosis

- Multiple diagnosis hypotheses can run simultaneously.
- One agent can inspect logs while another compares configs and another reviews GPU metric windows.
- LLM-based analysis can run in parallel over log chunks, config diffs, and benchmark summaries.

## GPU-Relevant Workloads

- The target experiment runs on AMD GPU.
- Replay verification reruns the corrected workload on AMD GPU.
- Optional batched log/config analysis or local model inference can run as parallel inference.
- Before/after metrics prove GPU memory, latency, throughput, or runtime behavior changed.

## Feedback Loop

1. Detect failure or degradation.
2. Generate ranked diagnosis hypotheses.
3. Choose the smallest recovery action.
4. Generate replay command/config.
5. Verify the rerun.
6. If verification fails, revise diagnosis and try again.
7. If verification succeeds, freeze replay capsule and final timeline.

## Why This Is Truly Agentic

ReplayLab is agentic because it makes decisions under uncertainty.

It does not just collect logs. It decides what evidence matters, detects whether the run is healthy, forms competing explanations, asks for more evidence when needed, generates a recovery plan, tests that plan, and revises itself if the plan fails.

The core intelligence is **experiment causality**: understanding what changed, why it mattered, and how to reproduce the successful path on AMD GPU infrastructure.
