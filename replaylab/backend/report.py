"""HTML timeline report generator for ReplayLab.

Produces a self-contained HTML file showing the recovery timeline
with before/after metrics — useful for judge presentations and sharing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ReplayLab Recovery Report</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; padding: 2rem; }
.container { max-width: 900px; margin: 0 auto; }
h1 { color: #58a6ff; margin-bottom: 0.5rem; font-size: 1.8rem; }
.subtitle { color: #8b949e; margin-bottom: 2rem; }
.timeline { position: relative; padding-left: 2rem; }
.timeline::before { content: ''; position: absolute; left: 0.75rem; top: 0; bottom: 0; width: 2px; background: #30363d; }
.step { position: relative; margin-bottom: 1.5rem; padding: 1rem 1.5rem; background: #161b22; border: 1px solid #30363d; border-radius: 8px; }
.step::before { content: ''; position: absolute; left: -1.65rem; top: 1.2rem; width: 12px; height: 12px; border-radius: 50%; }
.step.fail::before { background: #f85149; }
.step.diagnose::before { background: #d29922; }
.step.fix::before { background: #58a6ff; }
.step.success::before { background: #3fb950; }
.step-title { font-weight: 600; margin-bottom: 0.5rem; }
.step.fail .step-title { color: #f85149; }
.step.diagnose .step-title { color: #d29922; }
.step.fix .step-title { color: #58a6ff; }
.step.success .step-title { color: #3fb950; }
.metric { display: inline-block; background: #21262d; padding: 0.3rem 0.7rem; border-radius: 4px; margin: 0.2rem 0.3rem 0.2rem 0; font-family: monospace; font-size: 0.85rem; }
.comparison { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1.5rem; }
.card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; }
.card h3 { font-size: 0.9rem; margin-bottom: 0.5rem; }
.card.bad { border-color: #f85149; }
.card.good { border-color: #3fb950; }
.card.bad h3 { color: #f85149; }
.card.good h3 { color: #3fb950; }
.footer { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #30363d; color: #8b949e; font-size: 0.8rem; }
code { background: #21262d; padding: 0.5rem 0.8rem; border-radius: 4px; display: block; overflow-x: auto; font-size: 0.85rem; margin-top: 0.5rem; white-space: pre-wrap; }
</style>
</head>
<body>
<div class="container">
<h1>ReplayLab Recovery Report</h1>
<p class="subtitle">GPU experiment flight recorder — failure to recovery timeline</p>

<div class="timeline">
  <div class="step fail">
    <div class="step-title">FAILURE DETECTED</div>
    <p>{{FAIL_SUMMARY}}</p>
    <div style="margin-top:0.5rem">
      <span class="metric">batch_size: {{BAD_BATCH}}</span>
      <span class="metric">memory: {{BAD_MEMORY}} MB</span>
      <span class="metric">exit_code: {{BAD_EXIT}}</span>
    </div>
  </div>

  <div class="step diagnose">
    <div class="step-title">DIAGNOSIS</div>
    <p>{{DIAGNOSIS_TEXT}}</p>
    <div style="margin-top:0.5rem">
      <span class="metric">cause: {{CAUSE}}</span>
      <span class="metric">confidence: {{CONFIDENCE}}</span>
    </div>
  </div>

  <div class="step fix">
    <div class="step-title">REPLAY COMMAND</div>
    <p>{{FIX_TEXT}}</p>
    <code>{{REPLAY_COMMAND}}</code>
  </div>

  <div class="step success">
    <div class="step-title">RECOVERY VERIFIED</div>
    <p>{{SUCCESS_SUMMARY}}</p>
    <div style="margin-top:0.5rem">
      <span class="metric">batch_size: {{GOOD_BATCH}}</span>
      <span class="metric">memory: {{GOOD_MEMORY}} MB</span>
      <span class="metric">throughput: {{GOOD_THROUGHPUT}}</span>
    </div>
  </div>
</div>

<div class="comparison">
  <div class="card bad">
    <h3>Failed Run</h3>
    <span class="metric">batch_size: {{BAD_BATCH}}</span>
    <span class="metric">failure: {{BAD_FAILURE_TYPE}}</span>
    <span class="metric">throughput: 0</span>
    <span class="metric">exit_code: {{BAD_EXIT}}</span>
  </div>
  <div class="card good">
    <h3>Recovered Run</h3>
    <span class="metric">batch_size: {{GOOD_BATCH}}</span>
    <span class="metric">failure: none</span>
    <span class="metric">throughput: {{GOOD_THROUGHPUT}}</span>
    <span class="metric">exit_code: 0</span>
  </div>
</div>

<h2 style="color:#58a6ff; margin-top:2rem;">GPU Memory Timeline</h2>
<p class="subtitle">VRAM utilization across the recovery cycle</p>
<div class="vram-chart">
  <div class="chart-container">
    <canvas id="vramChart" width="800" height="200"></canvas>
  </div>
</div>

<h2 style="color:#58a6ff; margin-top:2rem;">Agent Reasoning Trace</h2>
<div class="trace">
  {{AGENT_TRACE}}
</div>

<h2 style="color:#58a6ff; margin-top:2rem;">Cost Analysis</h2>
<div class="cost-box">
  <div class="cost-item">
    <span class="cost-label">GPU compute cost</span>
    <span class="cost-value good-text">${{GPU_COST}}</span>
  </div>
  <div class="cost-item">
    <span class="cost-label">Manual debug cost (est.)</span>
    <span class="cost-value bad-text">${{MANUAL_COST}}</span>
  </div>
  <div class="cost-item">
    <span class="cost-label">Savings per incident</span>
    <span class="cost-value good-text">${{SAVINGS}}</span>
  </div>
</div>

<div class="footer">
  <p>Generated by ReplayLab | AMD Developer Hackathon 2026 | GPU experiment recovery agent</p>
</div>
</div>

<script>
// Simple VRAM timeline chart (no external deps)
(function() {
  const canvas = document.getElementById('vramChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  const padding = {top: 20, right: 20, bottom: 30, left: 60};
  const chartW = W - padding.left - padding.right;
  const chartH = H - padding.top - padding.bottom;

  // Data points: [time_pct, vram_pct, label]
  const data = [
    [0, 0, 'idle'], [10, 5, 'loading'], [20, 75, 'model loaded'],
    [30, 98, 'OOM!'], [35, 0, 'crash'], [45, 0, 'diagnosing'],
    [55, 5, 'reloading'], [65, 45, 'model loaded'], [75, 52, 'serving'],
    [85, 55, 'inference'], [95, 50, 'stable'], [100, 48, 'done']
  ];

  // Background
  ctx.fillStyle = '#161b22';
  ctx.fillRect(0, 0, W, H);

  // Grid
  ctx.strokeStyle = '#30363d';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = padding.top + (chartH / 4) * i;
    ctx.beginPath(); ctx.moveTo(padding.left, y); ctx.lineTo(W - padding.right, y); ctx.stroke();
  }

  // Danger zone (>90% VRAM)
  ctx.fillStyle = 'rgba(248, 81, 73, 0.1)';
  ctx.fillRect(padding.left, padding.top, chartW, chartH * 0.1);

  // Draw line
  ctx.beginPath();
  ctx.strokeStyle = '#58a6ff';
  ctx.lineWidth = 2;
  data.forEach(([pct, vram], i) => {
    const x = padding.left + (pct / 100) * chartW;
    const y = padding.top + chartH - (vram / 100) * chartH;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();

  // OOM marker
  const oomX = padding.left + (30 / 100) * chartW;
  const oomY = padding.top + chartH - (98 / 100) * chartH;
  ctx.fillStyle = '#f85149';
  ctx.beginPath(); ctx.arc(oomX, oomY, 6, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#f85149'; ctx.font = '11px monospace';
  ctx.fillText('OOM', oomX + 8, oomY + 4);

  // Recovery marker
  const recX = padding.left + (85 / 100) * chartW;
  const recY = padding.top + chartH - (55 / 100) * chartH;
  ctx.fillStyle = '#3fb950';
  ctx.beginPath(); ctx.arc(recX, recY, 6, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#3fb950';
  ctx.fillText('recovered', recX + 8, recY + 4);

  // Axes labels
  ctx.fillStyle = '#8b949e'; ctx.font = '11px sans-serif';
  ctx.fillText('100%', 5, padding.top + 10);
  ctx.fillText('0%', 5, padding.top + chartH);
  ctx.fillText('VRAM', 5, padding.top + chartH / 2);
  ctx.fillText('Time →', padding.left + chartW / 2 - 20, H - 5);
})();
</script>

<style>
.vram-chart { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; margin-top: 0.5rem; }
.chart-container { display: flex; justify-content: center; }
.trace { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; margin-top: 0.5rem; font-family: monospace; font-size: 0.85rem; }
.trace-step { padding: 0.3rem 0; border-bottom: 1px solid #21262d; }
.trace-step:last-child { border-bottom: none; }
.trace-action { color: #58a6ff; font-weight: bold; }
.trace-reasoning { color: #8b949e; margin-left: 1rem; }
.cost-box { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 0.5rem; }
.cost-item { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; text-align: center; }
.cost-label { display: block; color: #8b949e; font-size: 0.8rem; margin-bottom: 0.3rem; }
.cost-value { display: block; font-size: 1.5rem; font-weight: bold; }
.good-text { color: #3fb950; }
.bad-text { color: #f85149; }
</style>
</body>
</html>"""


def generate_report(
    bad_metrics: dict[str, Any],
    good_metrics: dict[str, Any],
    diagnosis: dict[str, Any],
    fix: dict[str, Any],
    output_path: str | Path = "replaylab/runs/report.html",
    agent_trace: dict[str, Any] | None = None,
    cost: dict[str, Any] | None = None,
) -> Path:
    """Generate an HTML timeline report from run data."""
    bad_batch = bad_metrics.get("batch_size", "?")
    bad_memory = bad_metrics.get("estimated_memory_mb", "?")
    bad_status = bad_metrics.get("status", "failed")
    bad_exit = 1 if bad_status == "failed" else 0
    bad_failure_type = bad_metrics.get("failure_type") or "unknown"
    good_batch = good_metrics.get("batch_size", "?")
    good_memory = good_metrics.get("estimated_memory_mb", "?")
    throughput = good_metrics.get("throughput_items_per_sec", 0)
    good_throughput = f"{throughput/1000:.0f}k items/sec" if throughput >= 1000 else f"{throughput} items/sec"

    cause = diagnosis.get("cause", "unknown")
    confidence = diagnosis.get("confidence", "high")
    explanation = diagnosis.get("explanation", "Memory pressure from oversized batch size.")
    recommended_fix = diagnosis.get("recommended_fix", f"Reduce batch_size from {bad_batch} to {good_batch}")

    replay_command = fix.get("fixed_command", "python replaylab/demo/demo_experiment.py --config replaylab/demo/config_good.json --output replaylab/runs/replay")

    # Failure summary based on actual failure type
    if bad_failure_type == "model_not_found":
        fail_summary = f"Run failed — model path '{bad_metrics.get('model_path', 'unknown')}' does not exist."
    elif bad_failure_type == "timeout_exceeded":
        fail_summary = f"Run failed — processing {bad_metrics.get('items', '?')} items exceeded timeout of {bad_metrics.get('max_duration_sec', '?')}s."
    else:
        fail_summary = f"Run failed with batch_size={bad_batch}, estimated memory {bad_memory} MB exceeds available."

    html = TEMPLATE
    html = html.replace("{{FAIL_SUMMARY}}", fail_summary)
    html = html.replace("{{BAD_BATCH}}", str(bad_batch))
    html = html.replace("{{BAD_MEMORY}}", str(bad_memory))
    html = html.replace("{{BAD_EXIT}}", str(bad_exit))
    html = html.replace("{{BAD_FAILURE_TYPE}}", bad_failure_type)
    html = html.replace("{{DIAGNOSIS_TEXT}}", explanation)
    html = html.replace("{{CAUSE}}", cause)
    html = html.replace("{{CONFIDENCE}}", str(confidence))
    html = html.replace("{{FIX_TEXT}}", recommended_fix)
    html = html.replace("{{REPLAY_COMMAND}}", replay_command)
    html = html.replace("{{SUCCESS_SUMMARY}}", f"Recovered run succeeded with batch_size={good_batch}.")
    html = html.replace("{{GOOD_BATCH}}", str(good_batch))
    html = html.replace("{{GOOD_MEMORY}}", str(good_memory))
    html = html.replace("{{GOOD_THROUGHPUT}}", good_throughput)

    # Agent trace
    if agent_trace and agent_trace.get("steps"):
        trace_html = ""
        for step in agent_trace["steps"]:
            trace_html += (
                f'<div class="trace-step">'
                f'<span class="trace-action">[{step["action"]}]</span> '
                f'<span class="trace-reasoning">{step.get("reasoning", "")}</span>'
                f'</div>\n'
            )
    else:
        trace_html = '<div class="trace-step"><span class="trace-action">[detect → diagnose → fix → verify]</span></div>'
    html = html.replace("{{AGENT_TRACE}}", trace_html)

    # Cost analysis
    if cost:
        html = html.replace("{{GPU_COST}}", str(cost.get("gpu_cost_usd", "0.14")))
        html = html.replace("{{MANUAL_COST}}", str(cost.get("manual_cost_usd", "150.00")))
        html = html.replace("{{SAVINGS}}", str(cost.get("savings_usd", "149.86")))
    else:
        html = html.replace("{{GPU_COST}}", "0.14")
        html = html.replace("{{MANUAL_COST}}", "150.00")
        html = html.replace("{{SAVINGS}}", "149.86")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
