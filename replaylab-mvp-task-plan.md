# ReplayLab MVP Task Plan

This plan breaks the ReplayLab MVP into atomic build tasks for a hackathon demo.

Core demo promise:

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

## Task List

| ID | Status | Task Name | Input | Output | Files To Create | Dependencies | Complexity |
|---|---|---|---|---|---|---|---|
| T1 | MUST BUILD | Define MVP project structure | Existing repo | Backend/frontend/demo folders | `replaylab/`, `replaylab/backend/`, `replaylab/frontend/`, `replaylab/demo/`, `replaylab/runs/` | None | Low |
| T2 | MUST BUILD | Create controlled demo experiment | Desired failure scenario | Script that can fail and succeed based on parameter | `replaylab/demo/demo_experiment.py`, `replaylab/demo/config_bad.json`, `replaylab/demo/config_good.json` | T1 | Medium |
| T3 | MUST BUILD | Implement experiment runner | Demo command/config | Run process, capture stdout/stderr, exit code, duration | `replaylab/backend/runner.py` | T1, T2 | Medium |
| T4 | MUST BUILD | Implement run record storage | Runner output | Persisted run JSON + log file | `replaylab/backend/store.py`, `replaylab/runs/.gitkeep` | T3 | Low |
| T5 | MUST BUILD | Implement metric collector | Running process/system info | Runtime metrics; GPU metrics when available | `replaylab/backend/metrics.py` | T3 | Medium |
| T6 | MUST BUILD | Implement failure detector | Run record, logs, metrics | `failed`, `degraded`, or `succeeded` classification | `replaylab/backend/detector.py` | T4, T5 | Medium |
| T7 | MUST BUILD | Implement cause diagnoser | Failed run record, config, logs | Cause label, evidence, confidence | `replaylab/backend/diagnoser.py` | T6 | Medium |
| T8 | MUST BUILD | Implement replay command generator | Diagnosis + failed command/config | Corrected command | `replaylab/backend/planner.py` | T7 | Medium |
| T9 | MUST BUILD | Implement rerun verifier | Replay command | Successful rerun record + before/after comparison | `replaylab/backend/verifier.py` | T8, T3, T4 | Medium |
| T10 | MUST BUILD | Build backend API | Runner/diagnoser/planner/verifier modules | HTTP endpoints for UI/demo | `replaylab/backend/app.py`, `replaylab/backend/schemas.py` | T3-T9 | Medium |
| T11 | MUST BUILD | Build timeline UI | Backend API | Visual timeline with failed/diagnosed/replay/recovered states | `replaylab/frontend/*` | T10 | Medium |
| T12 | MUST BUILD | Add demo one-click flow | Backend + UI | Button/endpoint to run full broken-to-recovered demo | `replaylab/backend/demo_flow.py` or endpoint in `app.py` | T2-T11 | Medium |
| T13 | MUST BUILD | Create demo README | MVP behavior | Clear run instructions | `replaylab/README.md` | T1-T12 | Low |
| T14 | MUST BUILD | Local dry-run test | Complete MVP | Verified demo-critical path | No new file required, optional `replaylab/demo/transcript.md` | T1-T13 | Medium |
| T15 | NICE TO HAVE | Add simulated AMD telemetry fallback | Metrics collector | Demo-safe telemetry if AMD tools unavailable | Update `replaylab/backend/metrics.py` | T5 | Low |
| T16 | NICE TO HAVE | Add LLM-generated diagnosis text | Cause/evidence | Better explanation copy | Update `replaylab/backend/diagnoser.py` | T7 | Low/Medium |
| T17 | NICE TO HAVE | Add artifact preview | Successful run artifacts | UI artifact panel | Update frontend files | T9, T11 | Low |
| T18 | NICE TO HAVE | Add benchmark before/after chart | Run comparison | Simple latency/throughput chart | Update frontend files | T9, T11 | Low |
| T19 | NICE TO HAVE | Add export replay capsule | Final run records | Downloadable JSON/Markdown capsule | `replaylab/backend/exporter.py` | T9 | Medium |
| T20 | NICE TO HAVE | Add polished pitch screen | Demo data | Judge-friendly summary panel | Update frontend files | T11 | Low |

## Execution Order

## Phase 1: Skeleton And Controlled Failure

1. T1: Define MVP project structure.
2. T2: Create controlled demo experiment.
3. T3: Implement experiment runner.
4. T4: Implement run record storage.

Goal: We can execute a broken run and store evidence.

## Phase 2: Intelligence Loop

1. T5: Implement metric collector.
2. T6: Implement failure detector.
3. T7: Implement cause diagnoser.
4. T8: Implement replay command generator.
5. T9: Implement rerun verifier.

Goal: We can go from failure to corrected rerun.

## Phase 3: Demo Surface

1. T10: Build backend API.
2. T11: Build timeline UI.
3. T12: Add demo one-click flow.
4. T13: Create demo README.
5. T14: Local dry-run test.

Goal: Judges can see the full magic moment.

## Phase 4: Optional Polish

1. T15: Simulated AMD telemetry fallback.
2. T16: LLM-generated diagnosis text.
3. T17: Artifact preview.
4. T18: Before/after chart.
5. T19: Export replay capsule.
6. T20: Pitch summary panel.

Goal: Improve resilience and presentation if time remains.

## Parallel Plan

## Can Run In Parallel

- **T2 and T5:** Demo experiment and metric collector can be developed separately after project structure exists.
- **T6, T7, T8:** Detector, diagnoser, and planner can be stubbed against sample run records before the runner is fully finished.
- **T10 and T11:** Backend API shape and frontend timeline can be built in parallel once schemas are agreed.
- **T15, T17, T18, T20:** Optional polish tasks can run independently after the core data model is stable.

## Should Not Run In Parallel

- T3 before T2 is stable enough to execute.
- T9 before T8 generates a real replay command.
- T12 before T10 and T11 expose the required API/UI flow.
- T14 before T12 exists.

## Critical Path

The critical path is:

```text
T1 Project structure
  -> T2 Controlled demo experiment
  -> T3 Runner
  -> T4 Run storage
  -> T6 Failure detector
  -> T7 Cause diagnoser
  -> T8 Replay command generator
  -> T9 Rerun verifier
  -> T10 Backend API
  -> T11 Timeline UI
  -> T12 One-click demo flow
  -> T14 Dry-run test
```

T5 metric collection is also demo-critical if we want AMD GPU proof. If AMD access is delayed, use T15 telemetry fallback while keeping the GPU metric slot visible in the UI.

## Demo Blockers

## MUST BUILD

- T1: Project structure.
- T2: Controlled demo experiment.
- T3: Experiment runner.
- T4: Run record storage.
- T5: Metric collector.
- T6: Failure detector.
- T7: Cause diagnoser.
- T8: Replay command generator.
- T9: Rerun verifier.
- T10: Backend API.
- T11: Timeline UI.
- T12: One-click demo flow.
- T13: Demo README.
- T14: Local dry-run test.

## NICE TO HAVE

- T15: Simulated AMD telemetry fallback.
- T16: LLM-generated diagnosis text.
- T17: Artifact preview.
- T18: Benchmark before/after chart.
- T19: Export replay capsule.
- T20: Pitch summary panel.

## Minimal Demo Acceptance Criteria

The MVP is acceptable if:

- The broken experiment runs from the UI or one endpoint.
- The failed run record includes command, config, log path, exit code, and metric data.
- The system detects the failure without manual selection.
- The system identifies one concrete cause.
- The replay command is generated and shown.
- The replay command succeeds.
- The UI shows a clear before/after timeline.

## Recommended Build Strategy

Build the backend first using sample JSON records, then wire the real runner, then add the UI.

The fastest credible order:

1. Create the controlled experiment.
2. Build runner and storage.
3. Hard-code one robust failure pattern.
4. Generate a real replay command.
5. Verify the rerun.
6. Put the timeline UI on top.
7. Add GPU telemetry and charts after the core loop works.
