"""ReplayLab FastAPI web application.

Serves the timeline UI and exposes API endpoints for running experiments,
diagnosing failures, and viewing recovery timelines.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure package imports work when running directly
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from replaylab.backend.diagnoser import compare_runs
from replaylab.backend.gpu_telemetry import collect_gpu_snapshot
from replaylab.backend.llm_diagnoser import llm_diagnose
from replaylab.backend.planner import generate_fix, load_run
from replaylab.backend.report import generate_report
from replaylab.backend.runner import run_command
from replaylab.backend.verifier import verify_replay

app = FastAPI(
    title="ReplayLab",
    description="GPU experiment flight recorder — failure to recovery in seconds",
    version="0.1.0",
)

RUNS_DIR = Path("replaylab/runs")
DEMO_DIR = Path("replaylab/demo")

# --- Scenarios available ---
SCENARIOS = {
    "memory_pressure": {
        "name": "Memory Pressure (OOM)",
        "description": "Batch size too large for available GPU VRAM",
        "bad_config": "config_bad.json",
        "good_config": "config_good.json",
    },
    "model_not_found": {
        "name": "Model Path Error",
        "description": "Model checkpoint path does not exist",
        "bad_config": "config_bad_model_path.json",
        "good_config": "config_good_model_path.json",
    },
    "timeout": {
        "name": "Processing Timeout",
        "description": "Too many items to process within time limit",
        "bad_config": "config_bad_timeout.json",
        "good_config": "config_good_timeout.json",
    },
}


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main timeline UI."""
    ui_path = Path("replaylab/frontend/index.html")
    if ui_path.exists():
        return HTMLResponse(ui_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>ReplayLab</h1><p>Frontend not built yet. Use /docs for API.</p>")


@app.get("/api/scenarios")
async def list_scenarios():
    """List available failure scenarios."""
    return JSONResponse(SCENARIOS)


@app.get("/api/gpu")
async def gpu_status():
    """Get current GPU telemetry snapshot."""
    return JSONResponse(collect_gpu_snapshot())


@app.post("/api/run/{scenario}")
async def run_scenario(scenario: str):
    """Run a full failure-to-recovery demo for a given scenario."""
    if scenario not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Unknown scenario: {scenario}")

    sc = SCENARIOS[scenario]
    bad_config = f"replaylab/demo/{sc['bad_config']}"
    good_config = f"replaylab/demo/{sc['good_config']}"

    bad_cmd = f"python replaylab/demo/demo_experiment.py --config {bad_config} --output replaylab/runs/api_bad_{scenario}"
    good_cmd = f"python replaylab/demo/demo_experiment.py --config {good_config} --output replaylab/runs/api_good_{scenario}"

    # Step 1: Run bad experiment
    bad_record = run_command(bad_cmd, f"api_bad_{scenario}", "replaylab/runs")

    # Step 2: Run good baseline
    good_record = run_command(good_cmd, f"api_good_{scenario}", "replaylab/runs")

    # Step 3: Diagnose
    bad_run_dir = f"replaylab/runs/api_bad_{scenario}"
    good_run_dir = f"replaylab/runs/api_good_{scenario}"
    diagnosis = compare_runs(bad_run_dir, good_run_dir)

    # Step 4: Generate fix
    bad_run = load_run(bad_run_dir)
    fix = generate_fix(diagnosis, bad_run)

    # Step 5: Replay & verify
    replay_cmd = fix["fixed_command"].replace(f"api_bad_{scenario}", f"api_replay_{scenario}")
    replay_result = verify_replay(replay_cmd, f"api_replay_{scenario}")

    # Step 6: Try LLM diagnosis
    llm_result = llm_diagnose(bad_run, load_run(good_run_dir))

    # Step 7: Generate HTML report
    bad_metrics_data = json.loads((Path(bad_run_dir) / "metrics.json").read_text(encoding="utf-8"))
    good_metrics_data = replay_result["metrics"]
    report_path = generate_report(
        bad_metrics=bad_metrics_data,
        good_metrics=good_metrics_data,
        diagnosis=diagnosis,
        fix=fix,
        output_path=f"replaylab/runs/report_{scenario}.html",
    )

    # Step 8: GPU snapshot
    gpu = collect_gpu_snapshot()

    return JSONResponse({
        "scenario": scenario,
        "scenario_name": sc["name"],
        "success": replay_result["success"],
        "timeline": [
            {"step": "FAIL", "status": "failed", "detail": diagnosis.get("explanation", "")[:200]},
            {"step": "DIAGNOSE", "status": "diagnosed", "cause": diagnosis["cause"], "confidence": diagnosis["confidence"]},
            {"step": "FIX", "status": "fixed", "command": fix["fixed_command"], "changes": fix["changes"]},
            {"step": "REPLAY", "status": "replayed", "exit_code": replay_result["exit_code"]},
            {"step": "VERIFY", "status": "verified" if replay_result["success"] else "failed"},
        ],
        "diagnosis": diagnosis,
        "fix": fix,
        "replay_result": {
            "success": replay_result["success"],
            "exit_code": replay_result["exit_code"],
            "throughput": replay_result["metrics"].get("throughput_items_per_sec", 0),
        },
        "llm_diagnosis": llm_result if llm_result.get("cause") else None,
        "gpu_telemetry": gpu,
        "report_url": f"/reports/{Path(report_path).name}",
    })


@app.get("/api/runs")
async def list_runs():
    """List all stored run directories."""
    if not RUNS_DIR.exists():
        return JSONResponse([])
    runs = []
    for d in sorted(RUNS_DIR.iterdir()):
        if d.is_dir() and (d / "metrics.json").exists():
            metrics = json.loads((d / "metrics.json").read_text(encoding="utf-8"))
            runs.append({
                "run_id": d.name,
                "status": metrics.get("status"),
                "failure_type": metrics.get("failure_type"),
                "batch_size": metrics.get("batch_size"),
                "throughput": metrics.get("throughput_items_per_sec", 0),
            })
    return JSONResponse(runs)


@app.get("/reports/{filename}", response_class=HTMLResponse)
async def get_report(filename: str):
    """Serve a generated HTML report."""
    # Sanitize filename to prevent path traversal
    safe_name = Path(filename).name
    report_path = RUNS_DIR / safe_name
    if not report_path.exists() or not safe_name.endswith(".html"):
        raise HTTPException(status_code=404, detail="Report not found")
    return HTMLResponse(report_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
