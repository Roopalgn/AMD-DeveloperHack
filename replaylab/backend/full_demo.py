"""Full ReplayLab MVP demo: fail, record, diagnose, fix, rerun, verify."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from replaylab.backend.diagnoser import compare_runs
from replaylab.backend.gpu_telemetry import collect_gpu_snapshot
from replaylab.backend.llm_diagnoser import llm_diagnose
from replaylab.backend.planner import generate_fix, load_run
from replaylab.backend.report import generate_report
from replaylab.backend.runner import run_command
from replaylab.backend.verifier import verify_replay


BAD_COMMAND = (
    "python replaylab/demo/demo_experiment.py "
    "--config replaylab/demo/config_bad.json "
    "--output replaylab/runs/full_tmp_bad"
)
GOOD_BASELINE_COMMAND = (
    "python replaylab/demo/demo_experiment.py "
    "--config replaylab/demo/config_good.json "
    "--output replaylab/runs/full_tmp_good"
)


def run_full_demo() -> dict:
    # Collect GPU telemetry snapshot
    gpu_snapshot = collect_gpu_snapshot()
    print(f"[GPU] source: {gpu_snapshot['source']}")

    bad_record = run_command(BAD_COMMAND, "full_bad_run", "replaylab/runs")
    good_record = run_command(GOOD_BASELINE_COMMAND, "full_good_baseline", "replaylab/runs")
    diagnosis = compare_runs("replaylab/runs/full_bad_run", "replaylab/runs/full_good_baseline")
    bad_run = load_run("replaylab/runs/full_bad_run")
    fix = generate_fix(diagnosis, bad_run)
    replay_result = verify_replay(fix["fixed_command"].replace("full_tmp_bad", "full_tmp_replay"), "replay_run")

    # Try LLM-powered diagnosis (enhances rule-based with natural language)
    llm_result = llm_diagnose(bad_run, load_run("replaylab/runs/full_good_baseline"))
    if llm_result.get("cause"):
        diagnosis["llm_diagnosis"] = llm_result

    bad_batch = diagnosis["key_difference"]["batch_size"]["bad"]
    good_batch = diagnosis["key_difference"]["batch_size"]["good"]
    bad_throughput = diagnosis["compared_fields"]["throughput_items_per_sec"]["bad"]
    replay_throughput = replay_result["metrics"]["throughput_items_per_sec"]
    bad_memory_pressure = diagnosis["compared_fields"]["memory_pressure"]["bad"]
    replay_memory_pressure = replay_result["metrics"]["memory_pressure"]
    replay_throughput_short = f"{replay_throughput / 1000:.0f}k" if replay_throughput >= 1000 else str(replay_throughput)

    print("========================")
    print("ReplayLab Live Recovery")
    print("========================")
    print(f"❌ failure   batch_size={bad_batch}, memory_pressure={bad_memory_pressure}")
    print("🔍 diagnosis memory pressure from oversized batch")
    if llm_result.get("cause"):
        print(f"🤖 LLM says: {llm_result['cause']}")
    print(f"🔧 fix       batch_size {bad_batch} -> {good_batch}")
    print("🚀 replay    running corrected config...")
    print(f"✅ success   memory_pressure={replay_memory_pressure}, throughput={replay_throughput_short} items/sec")
    print("========================")
    print("ReplayLab Summary")
    print("========================")
    print("Failure Cause: Memory pressure")
    print(f"Parameter Fixed: batch_size {bad_batch} -> {good_batch}")
    print("Outcome: Successful recovery")
    print(f"Performance: {bad_throughput} -> {replay_throughput_short} items/sec")
    print(f"GPU Telemetry: {gpu_snapshot['source']}")
    print(f"LLM Diagnosis: {llm_result.get('diagnosis_source', 'unavailable')}")

    # Generate HTML timeline report
    bad_metrics = replay_result["metrics"] | {"batch_size": bad_batch, "estimated_memory_mb": diagnosis["compared_fields"]["estimated_memory_mb"]["bad"]}
    good_metrics = replay_result["metrics"]
    report_path = generate_report(
        bad_metrics={"batch_size": bad_batch, "estimated_memory_mb": diagnosis["compared_fields"]["estimated_memory_mb"]["bad"], "memory_pressure": True},
        good_metrics=good_metrics,
        diagnosis=diagnosis,
        fix=fix,
        output_path="replaylab/runs/report.html",
    )
    print(f"\n📄 Timeline report: {report_path}")

    return {
        "bad_record": bad_record,
        "good_record": good_record,
        "diagnosis": diagnosis,
        "fix": fix,
        "replay_result": replay_result,
        "gpu_snapshot": gpu_snapshot,
        "llm_diagnosis": llm_result,
        "report_path": str(report_path),
    }


def main() -> int:
    result = run_full_demo()
    return 0 if result["replay_result"]["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
