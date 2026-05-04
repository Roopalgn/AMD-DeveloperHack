# ReplayLab: The Black Box for GPU Experiments

ReplayLab turns failed GPU runs into reproducible recovery evidence by recording what happened, diagnosing why it failed, and replaying the fix.

## Short Description

ReplayLab is a black box for GPU experiments. It records a failed run, diagnoses the cause, generates a corrected replay command, and verifies the recovered run with before/after evidence.

## Problem

GPU experiments fail in messy ways.

A model run might crash because the batch size is too large, memory pressure spikes, a config changes, or a serving parameter breaks under load. The engineer usually fixes it quickly, reruns, and moves on.

The problem comes later: nobody can clearly answer what failed, what changed, which command fixed it, or whether the recovered run actually performed better.

For hackathon teams, startups, and ML engineers working under deadline, this makes GPU development hard to trust and hard to reproduce.

## Solution: ReplayLab

ReplayLab records a GPU experiment as it runs, captures the failure evidence, diagnoses the cause, generates a corrected replay command, and verifies the recovered run.

Instead of hiding failure, ReplayLab makes failure useful. It turns the broken run into a clear timeline: what failed, why it failed, what changed, and how to reproduce the successful result.

## How It Works

ReplayLab follows a simple recovery loop:

```text
FAIL -> RECORD -> DIAGNOSE -> FIX -> RERUN -> SUCCESS
```

1. **FAIL:** A GPU experiment fails or degrades.
2. **RECORD:** ReplayLab captures command, logs, exit code, config, metrics, and artifacts.
3. **DIAGNOSE:** It compares failed and recovered run evidence to identify the cause.
4. **FIX:** It generates a corrected replay command.
5. **RERUN:** It executes the fixed command and records the result.
6. **SUCCESS:** It verifies the recovered run and shows before/after evidence.

## Why It Is Different

ReplayLab is not just logging.

Logs tell you what happened. Monitoring tells you something went wrong. ReplayLab connects the failure to the fix.

For the MVP demo, ReplayLab detects memory pressure caused by an oversized batch size. It identifies the parameter change, replaces the bad config with the corrected config, reruns the experiment, and verifies success.

That makes it closer to a GPU experiment flight recorder than a dashboard.

## Demo

Run the full demo:

```powershell
python replaylab/backend/full_demo.py
```

The demo shows one complete recovery loop:

1. A GPU-style experiment starts with `batch_size=64`.
2. The run fails because estimated memory exceeds available memory.
3. ReplayLab records the failed command, logs, metrics, and artifacts.
4. ReplayLab diagnoses memory pressure and recommends `batch_size=8`.
5. ReplayLab replays the fixed config and verifies a successful recovered run.

Example output:

```text
========================
ReplayLab Live Recovery
========================
❌ failure   batch_size=64, memory_pressure=True
🔍 diagnosis memory pressure from oversized batch
🔧 fix       batch_size 64 -> 8
🚀 replay    running corrected config...
✅ success   memory_pressure=False, throughput=648k items/sec
========================
ReplayLab Summary
========================
Failure Cause: Memory pressure
Parameter Fixed: batch_size 64 -> 8
Outcome: Successful recovery
Performance: 0.0 -> 648k items/sec
```

## Tech Stack

- **Python:** Standard-library MVP for deterministic demo execution.
- **Agentic workflow:** Logical agents for recording, diagnosis, planning, replay, and verification.
- **AMD GPU relevance:** The system is designed around GPU runtime behavior such as memory pressure, batch size, throughput, and failed model execution.
- **Replay evidence:** Each run stores `run.json`, `stdout.txt`, `stderr.txt`, `metrics.json`, and `artifact.json`.

## Project Structure

```text
replaylab/
  backend/
    runner.py
    diagnoser.py
    planner.py
    verifier.py
    full_demo.py
  demo/
    demo_experiment.py
    config_bad.json
    config_good.json
  runs/
```

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
