# ReplayLab

ReplayLab is the black box for GPU experiments. It records a failed run, diagnoses why it failed, generates a corrected replay command, and verifies the recovered run.

Run the full demo:

```powershell
python replaylab/backend/full_demo.py
```

Run the failing experiment:

```powershell
python replaylab/demo/demo_experiment.py --config replaylab/demo/config_bad.json --output replaylab/runs/manual_bad
```

Run the recovered experiment:

```powershell
python replaylab/demo/demo_experiment.py --config replaylab/demo/config_good.json --output replaylab/runs/manual_good
```

Each run writes:

- `metrics.json`
- `artifact.json`

The bad config exits non-zero and records a memory-pressure cause. The good config exits `0` and records a successful recovered run.

Each recorded run can include:

- `run.json`
- `stdout.txt`
- `stderr.txt`
- `metrics.json`
- `artifact.json`
