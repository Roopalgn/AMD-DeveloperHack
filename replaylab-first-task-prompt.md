# ReplayLab First Implementation Task

## Top 5 MUST BUILD Tasks

1. **Controlled demo experiment**
   - Creates the real broken/successful run target.
   - Unlocks runner, detector, diagnoser, planner, verifier, and UI.

2. **Experiment runner/recorder**
   - Executes the experiment and captures logs, exit code, duration, command, config, and artifacts.

3. **Run record storage**
   - Persists run evidence in a stable shape for diagnosis and UI.

4. **Failure detection + diagnosis + replay planning**
   - Detects failure, identifies cause, and generates corrected command.

5. **Rerun verification**
   - Executes or validates the corrected command and proves recovery.

## First Task To Implement

**Task:** Controlled demo experiment with minimal project skeleton.

Why this first:

- It unlocks the rest of the system.
- It can be implemented independently.
- It produces visible output immediately.
- It gives later agents something real to observe, diagnose, and replay.

## Exact File Structure

Create this structure:

```text
replaylab/
  README.md
  __init__.py
  backend/
    __init__.py
  demo/
    __init__.py
    demo_experiment.py
    config_bad.json
    config_good.json
  frontend/
    .gitkeep
  runs/
    .gitkeep
```

## Required CLI Entry Point

The first visible command should work:

```powershell
python replaylab/demo/demo_experiment.py --config replaylab/demo/config_bad.json --output replaylab/runs/manual_bad
```

Expected result:

- Exits non-zero.
- Prints a clear failure message.
- Writes `metrics.json`.
- Writes `artifact.json`.
- Indicates the failure cause is oversized batch / memory pressure.

The success command should also work:

```powershell
python replaylab/demo/demo_experiment.py --config replaylab/demo/config_good.json --output replaylab/runs/manual_good
```

Expected result:

- Exits `0`.
- Prints a success message.
- Writes `metrics.json`.
- Writes `artifact.json`.
- Includes throughput/duration/runtime evidence.

## Function Definitions

Implement these functions in `replaylab/demo/demo_experiment.py`:

```python
def load_config(path: str) -> dict:
    """Load JSON config for a demo experiment."""

def detect_runtime() -> dict:
    """Detect whether torch/ROCm/CUDA appears available, with stdlib fallback."""

def estimate_memory_pressure(batch_size: int, model_size_mb: int, available_memory_mb: int) -> dict:
    """Return estimated memory demand and whether the run should fail."""

def run_experiment(config: dict) -> tuple[int, dict]:
    """Run the controlled experiment and return exit code plus metrics/artifact data."""

def write_outputs(output_dir: str, metrics: dict, artifact: dict) -> None:
    """Write metrics.json and artifact.json."""

def main() -> int:
    """Parse CLI args and execute the demo experiment."""
```

## Minimal Behavior

`config_bad.json` should intentionally fail:

- `batch_size` large enough to exceed estimated memory.
- `expected_failure` set to `memory_pressure`.

`config_good.json` should pass:

- Smaller `batch_size`.
- Same task/model settings where possible.

The script should be deterministic and hackathon-demo-safe:

- No network calls.
- No required paid APIs.
- No mandatory GPU dependency on the developer laptop.
- If AMD/ROCm/GPU runtime is unavailable, still run using simulated telemetry fields.
- If GPU is available later, include runtime detection fields in the output.

## Copy-Paste Coding Prompt

```text
You are Codex implementing the first ReplayLab MVP task.

Goal:
Create the minimal project skeleton and a controlled demo experiment that can intentionally fail and then succeed. This task unlocks the rest of ReplayLab by producing real failed/successful run evidence for later runner, detector, diagnoser, planner, verifier, and UI work.

Repository:
C:\Users\roopa\OneDrive\Desktop\AMD-DeveloperHack

Create exactly this structure:

replaylab/
  README.md
  __init__.py
  backend/
    __init__.py
  demo/
    __init__.py
    demo_experiment.py
    config_bad.json
    config_good.json
  frontend/
    .gitkeep
  runs/
    .gitkeep

Implement replaylab/demo/demo_experiment.py with only Python standard library dependencies.

Required functions:

def load_config(path: str) -> dict:
    Load JSON config for a demo experiment.

def detect_runtime() -> dict:
    Detect whether torch/ROCm/CUDA appears available, with stdlib fallback. Do not require torch. If torch is missing, return a clear fallback runtime object.

def estimate_memory_pressure(batch_size: int, model_size_mb: int, available_memory_mb: int) -> dict:
    Estimate memory demand and return whether the run should fail. Keep this deterministic.

def run_experiment(config: dict) -> tuple[int, dict]:
    Run the controlled experiment and return exit code plus a payload containing metrics and artifact data.

def write_outputs(output_dir: str, metrics: dict, artifact: dict) -> None:
    Create output_dir and write metrics.json and artifact.json.

def main() -> int:
    Parse --config and --output, execute the experiment, print a human-readable status, write outputs, and return the correct process exit code.

Behavior:
- config_bad.json should fail because batch_size is too large for available_memory_mb.
- config_good.json should succeed with a smaller batch_size.
- Both runs must write metrics.json and artifact.json.
- Bad run must exit non-zero.
- Good run must exit 0.
- Metrics should include status, duration_sec, batch_size, model_size_mb, available_memory_mb, estimated_memory_mb, memory_pressure, runtime_kind, gpu_available, and throughput_items_per_sec.
- Artifact should include status, summary, cause if failed, recommendation if failed, and replay_hint_command showing the likely corrected command.
- No network calls.
- No paid APIs.
- No external dependencies.
- Keep the code readable, typed where useful, and friendly to later imports by backend modules.

README:
Create replaylab/README.md with short instructions for running:

python replaylab/demo/demo_experiment.py --config replaylab/demo/config_bad.json --output replaylab/runs/manual_bad
python replaylab/demo/demo_experiment.py --config replaylab/demo/config_good.json --output replaylab/runs/manual_good

Verification:
After implementation, run both commands from the repo root.
Confirm the bad command exits non-zero and writes outputs.
Confirm the good command exits 0 and writes outputs.
Report the created files and the key outputs.

Constraints:
- Do not modify info.md or existing strategy markdown files unless necessary.
- Do not add package dependencies.
- Do not create a frontend yet.
- Do not implement runner/detector/diagnoser/planner yet.
```
