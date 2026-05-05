# ReplayLab MVP Architecture

The MVP exists to demonstrate one magic moment:

**A GPU run fails, ReplayLab detects the failure, identifies the cause, generates a replay command, and shows a successful rerun.**

Everything else is secondary.

## Minimum System

## Components List

| Component | Purpose | Keep / Remove |
|---|---|---|
| Experiment Runner + Recorder | Launches controlled GPU run and captures command, logs, config, artifacts, and metrics | Keep |
| GPU Metric Collector | Captures at least one AMD GPU/runtime signal | Keep |
| Failure Detector | Determines whether the run failed or degraded | Keep |
| Cause Diagnoser | Identifies the likely cause from logs/config/metrics | Keep |
| Replay Command Generator | Produces corrected rerun command | Keep |
| Rerun Verifier | Runs corrected command or validates successful rerun evidence | Keep |
| Timeline UI | Shows failed run, cause, replay command, and recovered run | Keep |
| Long-term memory | Stores historical failures across projects | Remove |
| Multi-hypothesis diagnosis | Runs competing explanations in parallel | Remove for MVP |
| Full agent orchestration | General task delegation framework | Remove for MVP |
| General notebook tracking | Support all notebooks and arbitrary workflows | Remove |
| Team collaboration | Sharing, comments, org features | Remove |
| Model tournament / benchmark arena | Broader model selection system | Remove |

## MVP Architecture

## 1. Runner/Recorder

Combines the original Run Observer and GPU Telemetry roles.

Responsibilities:

- Execute a controlled GPU-bound experiment command.
- Capture command string.
- Capture config file before each run.
- Capture stdout/stderr logs.
- Capture runtime status.
- Capture simple metrics such as duration, throughput, memory estimate, or GPU utilization.
- Write all run evidence into a local `runs/` directory or SQLite database.

MVP decision:

- It decides whether a run record is complete enough to diagnose.

## 2. Diagnoser/Planner

Combines Failure Diagnoser and Replay Planner.

Responsibilities:

- Detect failure from exit code, log patterns, and/or degraded metric threshold.
- Compare failed config vs corrected config.
- Identify one likely cause.
- Generate one corrected replay command.
- Produce concise explanation for the UI.

MVP decision:

- It decides which known failure pattern applies.
- It decides which parameter should change in the replay command.

## 3. Rerun Verifier

Keeps the original Verification Agent role, but simplified.

Responsibilities:

- Execute the generated replay command.
- Capture rerun logs and metrics.
- Mark recovery as successful only if exit code is clean and expected output appears.
- Compare failed vs successful run evidence.

MVP decision:

- It decides whether the recovered run is demo-worthy.

## 4. Demo Timeline UI

Responsibilities:

- Show run states: `Failed -> Diagnosed -> Replay Generated -> Recovered`.
- Highlight the cause.
- Show the replay command.
- Show before/after evidence.
- Show AMD GPU/runtime signal so judges see why GPU execution mattered.

## Exact MVP Flow

1. User clicks **Run Broken Experiment**.
2. Runner/Recorder launches a controlled GPU-bound script with a known bad parameter.
3. Script fails or degrades in a real way.
4. Runner/Recorder captures command, config, logs, exit code, runtime metrics, and artifact path.
5. Diagnoser/Planner detects failure.
6. Diagnoser/Planner identifies the cause.
7. Diagnoser/Planner generates corrected replay command.
8. User clicks **Replay Fix** or verifier runs it automatically.
9. Rerun Verifier executes corrected command.
10. Successful rerun produces expected artifact/metric.
11. UI displays the timeline and before/after evidence.

## Demo-Critical Path

The demo must work on this path:

```text
Bad config/command
  -> GPU-bound run fails or degrades
  -> logs + metrics captured
  -> failure detected
  -> cause identified
  -> replay command generated
  -> rerun succeeds
  -> timeline shows evidence
```

If this path works, the MVP works.

## Recommended Controlled Failure

Use one predictable failure that is real but easy to recover.

Best choices:

- **Bad batch size / memory pressure**
  - Broken command uses too-large batch/concurrency.
  - Fixed command uses smaller batch/concurrency.
  - Strongest AMD GPU story, but depends on real GPU behavior.

- **Missing or wrong model/config path**
  - Broken command points to wrong config/model path.
  - Fixed command points to correct path.
  - Easier to guarantee, but weaker GPU-specific story.

- **Bad serving parameter**
  - Broken command launches model server with invalid context/batch/concurrency setting.
  - Fixed command changes one serving parameter.
  - Good compromise if using vLLM or similar runtime.

MVP recommendation:

- Use **bad batch size / memory pressure** if AMD GPU access is stable.
- Fall back to **bad serving parameter** if memory failure is unreliable.

## What Is Real vs Mocked

## Must Be Real

- A run command is executed.
- Logs are captured.
- Failure/degradation is detected from actual evidence.
- A corrected replay command is generated.
- A successful rerun is executed or validated.
- The UI shows the actual failed and successful run records.

## Should Be Real If AMD Access Works

- AMD GPU workload execution.
- AMD GPU telemetry from `rocm-smi` or `amd-smi`.
- Before/after runtime metric such as latency, throughput, memory use, or duration.

## Acceptable To Mock For Demo Backup

- GPU telemetry values, if cloud telemetry access is blocked.
- Natural-language diagnosis text, as long as it is based on real captured logs/configs.
- Fancy agent reasoning traces.
- Long-term memory of previous runs.
- Parallel analysis details.
- Artifact previews.

## Should Not Be Faked

- The failed run.
- The generated replay command.
- The successful rerun.
- The before/after state transition.

These are the credibility core of ReplayLab.

## Removed From MVP

- Long-term memory.
- Multi-project experiment tracking.
- Full notebook integration.
- Agent marketplace or plugin system.
- General cluster scheduling.
- Model comparison tournament.
- Autonomous multi-step repair beyond one replay attempt.
- Complex UI dashboards.
- Fine-tuning support unless it is the simplest available demo workload.

## MVP Data Model

Minimal run record:

```json
{
  "run_id": "run_001",
  "status": "failed",
  "command": "python demo_experiment.py --batch-size 999",
  "config_path": "configs/bad.json",
  "started_at": "timestamp",
  "ended_at": "timestamp",
  "exit_code": 1,
  "logs_path": "runs/run_001/log.txt",
  "metrics": {
    "duration_sec": 8.2,
    "gpu_memory_mb": 188000,
    "throughput": 0
  },
  "diagnosis": {
    "cause": "batch_size_too_large",
    "evidence": "Out of memory / memory pressure detected",
    "confidence": 0.87
  },
  "replay_command": "python demo_experiment.py --batch-size 8"
}
```

## MVP Agentic Claim

The MVP is still agentic because the Diagnoser/Planner makes autonomous decisions:

- It decides whether failure happened.
- It classifies the cause.
- It chooses the corrected command.
- It asks the Verifier to test recovery.
- It marks the recovered run as valid or invalid.

It is intentionally not a broad autonomous lab system yet. It is one agentic recovery loop built to survive a hackathon demo.

## 60-Second Demo Script

1. **0-10s:** Start broken GPU run. It fails or degrades.
2. **10-20s:** ReplayLab captures logs and metrics.
3. **20-30s:** ReplayLab identifies cause and highlights exact parameter.
4. **30-40s:** Replay command appears.
5. **40-55s:** Rerun succeeds.
6. **55-60s:** Timeline shows failed run, fix, recovered run, and before/after evidence.

## Success Criteria

- Judges see a real failed run.
- Judges see automatic failure detection.
- Judges see a specific cause, not vague summarization.
- Judges see a replay command.
- Judges see a successful rerun.
- Judges see at least one GPU/runtime metric.
- Judges understand why failure became useful evidence.
