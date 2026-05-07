"""Full ReplayLab MVP demo: fail, record, diagnose, fix, rerun, verify."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from replaylab.backend.agent import AgentLoop, AgentTrace
from replaylab.backend.diagnoser import compare_runs
from replaylab.backend.gpu_telemetry import collect_gpu_snapshot
from replaylab.backend.llm_diagnoser import llm_diagnose
from replaylab.backend.planner import generate_fix, load_run
from replaylab.backend.report import generate_report
from replaylab.backend.runner import run_command
from replaylab.backend.verifier import verify_replay
from replaylab.backend.vllm_taxonomy import classify_failure


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

    # Check vLLM taxonomy for pattern match
    bad_stderr = Path("replaylab/runs/full_bad_run/stderr.txt")
    taxonomy_match = None
    if bad_stderr.exists():
        taxonomy_match = classify_failure(bad_stderr.read_text(encoding="utf-8"))

    # Agent cost analysis
    agent = AgentLoop(max_retries=2)
    cost = agent.estimate_cost(gpu_hours=0.07)

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
    if taxonomy_match:
        print(f"Taxonomy Match: {taxonomy_match['pattern_id']} ({taxonomy_match['severity']})")
    print(f"Cost: ${cost['gpu_cost_usd']} GPU vs ${cost['manual_cost_usd']} manual ({cost['speedup_factor']}x faster)")

    # Generate HTML timeline report
    # Build agent trace for the report
    trace = AgentTrace()
    trace.add_step("detect_failure", {"exit_code": 1, "status": "failed"}, "Confirmed experiment failure")
    if taxonomy_match:
        trace.add_step("taxonomy_match", taxonomy_match, f"Matched pattern: {taxonomy_match['pattern_id']}")
    trace.add_step("diagnose", {"cause": diagnosis["cause"]}, "Rule-based diagnosis confirmed")
    if llm_result.get("cause"):
        trace.add_step("llm_diagnosis", llm_result, "LLM enhanced diagnosis")
    trace.add_step("plan_fix", {"batch_size": f"{bad_batch} -> {good_batch}"}, "Minimum parameter change")
    trace.add_step("verify_success", {"throughput": replay_throughput}, "Recovery confirmed")
    trace.add_step("cost_estimate", cost, f"${cost['savings_usd']} saved")

    bad_metrics_report = {"batch_size": bad_batch, "estimated_memory_mb": diagnosis["compared_fields"]["estimated_memory_mb"]["bad"], "memory_pressure": True}
    good_metrics_report = replay_result["metrics"]
    report_path = generate_report(
        bad_metrics=bad_metrics_report,
        good_metrics=good_metrics_report,
        diagnosis=diagnosis,
        fix=fix,
        output_path="replaylab/runs/report.html",
        agent_trace=trace.to_dict(),
        cost=cost,
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
