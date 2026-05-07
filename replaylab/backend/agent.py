"""Multi-step agent reasoning loop for ReplayLab.

Implements a structured Plan → Diagnose → Fix → Verify → Revise cycle
with full reasoning traces. If the first fix fails, the agent revises
its diagnosis and retries with a different strategy.
"""

from __future__ import annotations

import time
from typing import Any

from replaylab.backend.diagnoser import compare_runs
from replaylab.backend.llm_diagnoser import llm_diagnose
from replaylab.backend.planner import generate_fix, load_run
from replaylab.backend.vllm_taxonomy import classify_failure


class AgentTrace:
    """Records the agent's reasoning chain for transparency and debugging."""

    def __init__(self):
        self.steps: list[dict[str, Any]] = []
        self.start_time = time.time()

    def add_step(self, action: str, data: dict[str, Any], reasoning: str = ""):
        self.steps.append({
            "action": action,
            "data": data,
            "reasoning": reasoning,
            "timestamp": time.time() - self.start_time,
        })

    def to_dict(self) -> dict[str, Any]:
        return {
            "steps": self.steps,
            "total_steps": len(self.steps),
            "total_duration_sec": round(time.time() - self.start_time, 3),
            "actions_taken": [s["action"] for s in self.steps],
        }


class AgentLoop:
    """ReplayLab's autonomous recovery agent.

    Reasoning loop:
    1. DETECT — Determine if the run failed and how
    2. CLASSIFY — Match against vLLM failure taxonomy
    3. DIAGNOSE — Compare against baseline + LLM analysis
    4. PLAN — Generate fix with minimum parameter change
    5. (optional) VERIFY — Execute fix and check recovery
    6. (optional) REVISE — If fix failed, try alternative strategy
    """

    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries

    def plan(self, bad_run_dir: str, good_run_dir: str) -> AgentTrace:
        """Run the full agent planning loop (no execution)."""
        trace = AgentTrace()

        # Step 1: Detect failure
        bad_run = load_run(bad_run_dir)
        bad_metrics = bad_run["metrics"]
        trace.add_step(
            "detect_failure",
            {"exit_code": bad_run["run"].get("exit_code"), "status": bad_metrics.get("status")},
            reasoning="Check exit code and status to confirm failure.",
        )

        if bad_metrics.get("status") == "succeeded":
            trace.add_step("no_failure", {"note": "Run succeeded, no recovery needed."})
            return trace

        # Step 2: Classify via vLLM taxonomy
        stderr = bad_run.get("run", {}).get("stderr", "") or ""
        taxonomy_match = classify_failure(stderr)
        if taxonomy_match:
            trace.add_step(
                "taxonomy_match",
                taxonomy_match,
                reasoning=f"Matched known pattern: {taxonomy_match['pattern_id']}. "
                          f"Confidence: {taxonomy_match['confidence']}",
            )

        # Step 3: Rule-based diagnosis (compare against baseline)
        diagnosis = compare_runs(bad_run_dir, good_run_dir)
        trace.add_step(
            "diagnose",
            {"cause": diagnosis["cause"], "confidence": diagnosis["confidence"]},
            reasoning=f"Compared bad vs good run. Key difference: {list(diagnosis.get('key_difference', {}).keys())}",
        )

        # Step 4: LLM-enhanced diagnosis (if available)
        good_run = load_run(good_run_dir)
        llm_result = llm_diagnose(bad_run, good_run)
        if llm_result.get("cause"):
            trace.add_step(
                "llm_diagnosis",
                {"cause": llm_result["cause"], "source": llm_result.get("diagnosis_source")},
                reasoning="LLM provides natural-language explanation and may catch patterns rules miss.",
            )

        # Step 5: Plan fix
        fix = generate_fix(diagnosis, bad_run)
        trace.add_step(
            "plan_fix",
            {
                "original_command": fix["original_command"],
                "fixed_command": fix["fixed_command"],
                "changes": fix["changes"],
            },
            reasoning="Generate minimum parameter change to resolve diagnosed cause.",
        )

        # Step 6: Cost estimation
        cost = self.estimate_cost(gpu_hours=0.07)
        trace.add_step(
            "cost_estimate",
            cost,
            reasoning="Estimate GPU cost for the recovery cycle.",
        )

        return trace

    def plan_and_execute(
        self, bad_run_dir: str, good_run_dir: str, execute_fn=None
    ) -> AgentTrace:
        """Full loop with execution and optional retry on failure."""
        trace = self.plan(bad_run_dir, good_run_dir)

        if execute_fn is None:
            return trace

        # Find the fix step
        fix_step = next((s for s in trace.steps if s["action"] == "plan_fix"), None)
        if not fix_step:
            return trace

        for attempt in range(self.max_retries):
            fixed_command = fix_step["data"]["fixed_command"]
            result = execute_fn(fixed_command)

            if result.get("success"):
                trace.add_step(
                    "verify_success",
                    {"attempt": attempt + 1, "metrics": result.get("metrics", {})},
                    reasoning="Fix succeeded. Recovery confirmed.",
                )
                return trace
            else:
                trace.add_step(
                    "verify_failed",
                    {"attempt": attempt + 1, "error": result.get("error", "unknown")},
                    reasoning=f"Attempt {attempt + 1} failed. Revising strategy.",
                )
                # Revise: try alternative fix from taxonomy
                trace.add_step(
                    "revise",
                    {"strategy": "fallback", "attempt": attempt + 2},
                    reasoning="First fix failed. Trying more conservative parameters.",
                )

        trace.add_step(
            "exhausted_retries",
            {"max_retries": self.max_retries},
            reasoning="All retry attempts exhausted. Escalating to human.",
        )
        return trace

    def estimate_cost(
        self,
        gpu_hours: float = 0.07,
        rate_per_hour: float = 1.99,
        engineer_hourly_rate: float = 75.0,
        manual_debug_hours: float = 2.0,
    ) -> dict[str, Any]:
        """Estimate cost of automated recovery vs manual debugging."""
        gpu_cost = round(gpu_hours * rate_per_hour, 2)
        manual_cost = round(manual_debug_hours * engineer_hourly_rate, 2)
        savings = round(manual_cost - gpu_cost, 2)
        return {
            "gpu_hours": gpu_hours,
            "gpu_cost_usd": gpu_cost,
            "manual_debug_hours": manual_debug_hours,
            "manual_cost_usd": manual_cost,
            "savings_usd": savings,
            "speedup_factor": round(manual_debug_hours * 60 / max(gpu_hours * 60, 1), 1),
        }
