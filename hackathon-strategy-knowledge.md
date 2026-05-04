# AMD Developer Hackathon Strategy Knowledge Base

This document consolidates the strategy, judging analysis, idea evaluation, and selected project direction developed from the AMD Developer Hackathon brief in `info.md`.

## 1. True Judging Priorities

The official judging criteria are application of technology, presentation, business value, and originality. The real priorities underneath those are sharper:

1. **Technical depth**
   - Judges will reward meaningful AMD Developer Cloud, ROCm, AMD Instinct MI300X, inference, fine-tuning, benchmarking, or GPU-aware execution.
   - A project should do more than wrap an API or run a generic model.

2. **Demo quality**
   - A working end-to-end demo beats an ambitious slide-only idea.
   - The demo must be reliable, legible, and quick to understand.

3. **Practicality**
   - The project should solve a real workflow, domain problem, or developer pain point.
   - Strong projects make the value obvious within seconds.

4. **Innovation**
   - Novel agent design, simulation, multimodal processing, benchmarking, infrastructure intelligence, or reproducibility work will stand out.

5. **Storytelling**
   - Judges need to understand why the problem matters, why AMD matters, what was hard, and what changed because of the system.

6. **UI/UX**
   - Important for usability, but secondary to technical proof and working execution.
   - Clean and clear beats flashy.

## 2. What Top, Mid, and Weak Projects Feel Like

## Top 1% Traits

- AMD Developer Cloud, ROCm, or MI300X usage is central to the project.
- The project shows measurable technical evidence: latency, throughput, evals, GPU utilization, model comparisons, before/after metrics, or deployment tradeoffs.
- The app feels complete: live demo, public repo, hosted interface, clear architecture, and believable data flow.
- The system goes beyond basic document chat into multi-step reasoning, tool use, multimodal processing, domain adaptation, or autonomous recovery.
- The problem statement is narrow and valuable.
- Hugging Face, Qwen, and AMD tooling are used coherently, not as sponsor-name decoration.

## Mid-Tier Traits

- Working app with decent UI and a recognizable use case.
- Uses open-source models or agent frameworks, but novelty is light.
- Demo works for happy paths but lacks evals, edge cases, or proof of impact.
- AMD is present mainly as cloud hosting rather than as a technical differentiator.
- Presentation is understandable but not memorable.

## Low-Effort Traits

- Thin chatbot wrapper around an LLM.
- Generic RAG over PDFs with no evaluation or unique workflow.
- Multi-agent system where agents are just labeled prompts.
- No live app, broken demo, private repo, or missing deployment.
- Fine-tuning claims with no before/after comparison.
- Sponsor names appear in slides but not in the actual system design.

## 3. Scoring Rubric

Total: **100 points**

| Category | Weight | What Judges Need to See |
|---|---:|---|
| Technical depth and AMD stack usage | 25 | Meaningful AMD Developer Cloud, ROCm, MI300X, GPU workload, fine-tuning, inference, benchmarking, or deployment evidence |
| Demo quality and completeness | 20 | Working live app/demo, reliable end-to-end flow, hosted app or runnable repo, reproducible setup |
| Practicality and business value | 18 | Real user pain, clear impact, believable adoption path, useful workflow |
| Innovation and originality | 15 | Fresh architecture, non-obvious agent design, multimodal/fine-tuning/eval/infrastructure angle |
| Model/application quality | 10 | Accuracy, robustness, latency, reliability, appropriate model choice, evaluation evidence |
| Storytelling and presentation | 7 | Clear framing, memorable pitch, tradeoffs, lessons learned |
| UI/UX | 5 | Usable interface, clean flow, understandable outputs |

## 4. Common Submissions to Avoid

## Common Ideas

- PDF/document Q&A bot.
- IT helpdesk support agent.
- Customer support chatbot.
- Legal document assistant.
- Medical report explainer.
- Finance advisor or stock insight bot.
- Resume analyzer or job matcher.
- Meeting summarizer and action tracker.
- Multi-agent research assistant.
- Code review or repo analysis bot.
- AI project manager or task planner.
- Healthcare triage chatbot.
- Cybersecurity log analyzer.
- Fraud detection model.
- Sentiment analysis dashboard.
- Image classification for defects.
- Medical image diagnosis assistant.
- Multimodal shopping assistant.
- Education tutor chatbot.
- Social media content generator.

## Overused Templates

- **AI chatbot for [domain]**
  - Examples: healthcare chatbot, finance chatbot, legal chatbot, education chatbot.

- **Upload documents and ask questions**
  - Examples: PDF Q&A, policy assistant, contract explainer, company knowledge bot.

- **Multi-agent system where agents are roles**
  - Examples: researcher agent, planner agent, writer agent, reviewer agent.

- **Dashboard for [data source]**
  - Examples: sentiment dashboard, security dashboard, finance dashboard, support dashboard.

- **Predictive model for [business metric]**
  - Examples: fraud prediction, churn prediction, demand forecasting, risk scoring.

- **Image classifier for [industry]**
  - Examples: defect detection, medical scan classifier, product recognition.

- **Personal assistant that automates everything**
  - Examples: calendar helper, email assistant, task planner, meeting summarizer.

- **Fine-tune a model for [domain]**
  - Examples: legal LLM, healthcare LLM, finance LLM, code LLM, often without strong evals.

## Judge Fatigue Patterns

- RAG chatbot for enterprise documents with no twist.
- Agents that only call search and summarize.
- Beautiful slides hiding a weak or non-working demo.
- AMD mentions with no performance insight, GPU-aware design, or ROCm-specific learning.
- Fine-tuning projects that do not compare base vs tuned model.
- Multimodal demos that are just image upload plus caption.
- Broad claims like "revolutionizes healthcare" without a concrete workflow.

## 5. Contrarian Problem Spaces Considered

These problem spaces were generated to avoid common hackathon templates and push toward systems, simulations, autonomous behavior, and GPU-dependent workloads.

| Problem Space | Core Idea | Best Attribute | Main Risk |
|---|---|---|---|
| GPU Crisis Autopilot | Autonomous rescue for bad GPU inference runs | Most AMD-native | Depends on live telemetry and environment stability |
| Autonomous Model Survival Arena | Models compete under latency, cost, quality, and memory constraints | Best metrics story | Model setup and benchmarking can be slow |
| Disaster Swarm Command | Multi-agent disaster response under cascading failures | Strong visual wow | Simulation realism and GPU need may be questioned |
| Synthetic Factory Under Attack | Industrial multimodal agents prevent failure cascades | Business value | Synthetic data may feel fake |
| Climate Microgrid War Room | Autonomous energy negotiation during outages | Social value | Could become a dashboard |
| Autonomous Lab Reproducer | GPU experiment recorder and recovery system | Best feasibility-to-win ratio | Must avoid looking like logging |
| Multimodal Search-and-Rescue Simulator | Drone imagery plus agentic crew coordination | Emotional visual impact | Asset-heavy and risky |
| Biosecurity Mutation Triage Arena | Sequence variant triage under uncertainty | Original and technical | Domain/safety complexity |
| Autonomous Data Center Fire Drill | AI infrastructure stress simulation | Strong AMD relevance | Too broad for 24-48 hours |
| Robotic Policy Sandbox Without Robots | Simulated robot policy stress testing | Futuristic | Robotics scaffolding is heavy |

## 6. Ruthless Evaluation Scorecard

Scores are 0-10.

| Idea | Originality | Technical Depth | GPU Relevance | Demo Wow | Feasibility | Judge Appeal | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| GPU Crisis Autopilot | 9 | 9 | 10 | 8 | 6 | 10 | Top 3 |
| Autonomous Model Survival Arena | 8 | 9 | 10 | 8 | 6 | 10 | Top 3 |
| Disaster Swarm Command | 8 | 8 | 7 | 9 | 5 | 8 | Eliminate |
| Synthetic Factory Under Attack | 8 | 8 | 8 | 8 | 5 | 8 | Eliminate |
| Climate Microgrid War Room | 8 | 7 | 7 | 8 | 5 | 7 | Eliminate |
| Autonomous Lab Reproducer | 8 | 8 | 9 | 7 | 8 | 9 | Top 3 |
| Multimodal Search-and-Rescue Simulator | 8 | 8 | 8 | 9 | 5 | 8 | Eliminate |
| Biosecurity Mutation Triage Arena | 9 | 8 | 9 | 7 | 4 | 7 | Eliminate |
| Autonomous Data Center Fire Drill | 8 | 9 | 10 | 7 | 5 | 9 | Eliminate |
| Robotic Policy Sandbox Without Robots | 8 | 8 | 8 | 8 | 4 | 7 | Eliminate |

## 7. Top 3 Refined Ideas

## 1. GPU Crisis Autopilot

**Final refined version:** A closed-loop rescue agent for bad AMD GPU inference runs.

**Core capability:** Automatically detect and fix one bad GPU inference configuration.

**Simplified scope:**

- Observe latency, throughput, memory usage, and error signals.
- Decide whether the run is unhealthy.
- Apply one corrective action.
- Prove the run improved.

**GPU dependency:**

- Requires a real AMD GPU inference run.
- Uses memory pressure, utilization, throughput, latency, and failed request signals.
- CPU/API-only alternatives cannot show hardware saturation or recovery.

**Demo hook:**

- The demo opens with an unhealthy GPU run.
- Latency spikes, throughput drops, or memory is nearly full.
- The agent selects an intervention such as reducing batch size and restarting the worker.
- Within seconds, the graph flips from red to green.

**Twist:** The agent intentionally chooses a less aggressive configuration and gets better performance. Bigger batch is not always better.

**Why it could win:**

- Most AMD-native.
- Strong metric proof.
- Infrastructure intelligence rather than app-layer AI.

**Failure risks:**

- Telemetry may be unavailable.
- Improvement may be too small.
- Live intervention may fail if serving setup is brittle.

## 2. Model Survival Arena

**Final refined version:** A GPU-powered elimination tournament where models compete under real deployment constraints.

**Core capability:** Automatically select the best deployable model under a constraint.

**Simplified scope:**

- Use one task.
- Compare 2-3 models or configs.
- Run adversarial eval cases.
- Score quality, latency, memory, and throughput.
- Crown a winner with evidence.

**GPU dependency:**

- Runs high-throughput inference across candidates.
- Captures AMD GPU memory, latency, and throughput.
- Parallel evals make GPU acceleration visible.

**Demo hook:**

- Judges see three models enter a tournament.
- An adversarial eval case appears.
- One model gives a confident wrong answer.
- Another passes quality but fails latency.
- The system crowns the survivor.

**Twist:** The largest model does not win. The best model is the one that survives real constraints.

**Why it could win:**

- Strong fit for Hugging Face, AMD Cloud, and real deployment decisions.
- Gives judges numbers, tradeoffs, and a clear winner.
- More original than another domain app.

**Failure risks:**

- Model downloads and setup can burn time.
- Quality scoring may look subjective.
- Without real benchmarking, it becomes a dressed-up leaderboard.

## 3. ReplayLab

**Final refined version:** A GPU experiment flight recorder that reconstructs the exact path from failed run to reproducible success.

**Core capability:** Turn a failed GPU experiment into a reproducible successful run.

**Simplified scope:**

- Track one controlled GPU-bound script or inference job.
- Capture command, config, logs, metrics, and artifact path.
- Detect failure.
- Compare failed and successful run states.
- Identify the critical change.
- Generate a replay command.

**GPU dependency:**

- The observed workload must run on AMD GPU.
- Captures memory, latency, throughput, runtime status, and failure symptoms.
- The failure should be GPU-relevant: batch size, memory pressure, model loading, or serving config.

**Demo hook:**

- A run fails live.
- ReplayLab immediately detects the failure.
- It highlights the exact changed parameter.
- It produces a rerun command and reconstructs the successful timeline.

**Twist:** The failed run becomes the strongest part of the demo. Instead of hiding failure, ReplayLab turns it into reproducible evidence.

**Why it could win:**

- Practical, technical, and emotionally relatable to builders.
- Feasible in 24-48 hours.
- Proves AMD GPU usage through real experiment traces.
- Best feasibility-to-winning ratio.

**Failure risks:**

- Could be perceived as an experiment tracker unless diagnosis is clear.
- Log parsing may be messy.
- Replay command must be credible and executable.

## Strategic Read

- **Highest ceiling:** GPU Crisis Autopilot.
- **Best metrics story:** Model Survival Arena.
- **Best feasibility-to-win ratio:** ReplayLab.

Recommendation:

- Build **ReplayLab** if reliability, speed, and shipping probability matter most.
- Borrow GPU health metrics from **GPU Crisis Autopilot**.
- Borrow before/after score comparison from **Model Survival Arena**.

## 8. Selected Direction: ReplayLab

## Final Problem Statement

GPU experiments fail in messy, expensive ways: bad configs, memory pressure, missing artifacts, unstable serving commands, and unclear recovery steps.

For overloaded ML engineers, the real problem is not only fixing a failed run; it is proving exactly what changed and reproducing the successful path under deadline.

ReplayLab is an AMD-powered experiment flight recorder that observes a real GPU workflow, diagnoses failure, and generates a replayable recovery path.

## Persona

- **User:** Solo ML infrastructure engineer at a 6-person AI startup preparing a customer-facing model demo.
- **Context:** They are running open-source model inference or lightweight fine-tuning on AMD Developer Cloud using ROCm, Hugging Face models, shell scripts, notebooks, and ad hoc config files.
- **Pressure:** They need a working model demo, reproducible setup, and credible performance evidence before a review with investors, customers, or hackathon judges.
- **Technical profile:** Strong engineer, but overloaded. Comfortable with Python, model serving, logs, and cloud GPUs, but has no time to manually reconstruct every failed attempt.

## Pain Scenario

The engineer launches a GPU-bound inference or fine-tuning run. It fails because of batch size, memory pressure, model path, missing dependency, bad serving command, or config drift.

They patch the issue quickly, rerun, and get a better result. Later, they cannot answer:

- What exactly changed?
- Which run produced the good result?
- What command should reproduce it?
- Did the GPU actually behave better?
- Can someone else rerun the same experiment?

In a judging or customer setting, that makes the project look fragile even if the final model works.

## Current Broken Workflow

1. Start an AMD cloud GPU VM.
2. Install dependencies or use a prebuilt ROCm image.
3. Download model/data artifacts.
4. Run an inference, benchmark, or fine-tuning script.
5. Watch terminal logs manually.
6. Check GPU state separately.
7. Patch configs after failure.
8. Rerun commands from shell history.
9. Copy useful logs into README or slides.
10. Hope the final command still works later.

## Where It Breaks

- Commands, configs, logs, artifacts, and GPU metrics are scattered.
- Failed attempts are discarded even though they contain the most useful debugging signal.
- Shell history has commands but no context.
- Experiment trackers capture clean metrics but often miss messy recovery decisions.
- Notebook history does not reliably capture shell actions, environment drift, or GPU runtime behavior.
- The UX assumes disciplined logging, while real hackathon/startup work is chaotic.

## Technical Necessity

ReplayLab requires both agentic workflows and GPU compute.

**Agentic workflow is required because the system must:**

- Observe the run.
- Capture commands, configs, logs, artifacts, and metrics.
- Detect failure or degradation.
- Compare failed and successful states.
- Infer the likely causal change.
- Generate a replay command.
- Decide whether the recovered run is submission-worthy.

**GPU compute is required because the system evidence depends on:**

- GPU memory pressure.
- Inference latency.
- Throughput.
- Runtime duration.
- Failed or degraded model execution.
- Before/after performance comparison.

CPU-only or basic API approaches fail because they cannot reproduce hardware-bound model execution under real runtime constraints.

## Core Intelligence

ReplayLab is thinking about **experiment causality**.

It autonomously decides:

- Whether a run failed, degraded, improved, or succeeded.
- Which logs and metrics are relevant.
- Which config or command change likely caused recovery.
- What minimum sequence of steps reproduces the successful run.
- Whether the final run is credible enough for demo or submission.

The non-trivial reasoning is correlating command history, config diffs, log errors, artifacts, and GPU metrics into one causal timeline.

It feels like a system, not a script, because it maintains memory across runs, compares states, interprets failures, and outputs an actionable replay plan.

## Magic Moment

In the most impressive 5-10 seconds:

- A GPU run fails live.
- ReplayLab reports: **Failure detected: memory pressure from oversized batch.**
- It highlights the exact changed parameter.
- It generates the corrected rerun command.
- The timeline updates from failed run to recovered run with before/after GPU metrics.

Under the hood, ReplayLab parses logs, reads run metadata, compares configs, checks GPU/runtime metrics, classifies the failure, and builds a reproducible run graph.

## Constraints

**Key assumptions:**

- AMD GPU access is available early enough.
- The demo workload is small and controlled.
- Commands, configs, logs, and output artifacts are observable.
- At least one GPU/runtime metric can be captured reliably.
- The failure scenario is real but recoverable.

**Failure points:**

- AMD Cloud setup takes too long.
- ROCm telemetry is hard to access in the environment.
- Model downloads are slow.
- Failure cause is ambiguous.
- Rerun command does not actually reproduce success.
- The product looks like a log viewer instead of autonomous diagnosis.

**Technical challenges:**

- Correlating logs, commands, configs, and metrics.
- Detecting meaningful differences between failed and successful runs.
- Generating an executable replay command.
- Showing GPU-specific evidence clearly.
- Keeping the demo narrow enough to work while still feeling powerful.

## Hypothesis

If we build **ReplayLab**, an autonomous GPU experiment flight recorder, using **AMD Developer Cloud, ROCm-aware runtime metrics, and parallel log/config analysis agents**, then ML engineers will recover and reproduce failed GPU experiments faster because the system captures causal evidence during execution instead of forcing humans to reconstruct it afterward.

## Demo Success Criteria

The demo must prove in under 60 seconds:

- A real GPU-bound experiment or inference run executes.
- ReplayLab captures command, config, logs, artifacts, and GPU/runtime metrics.
- A failed or degraded run is detected automatically.
- The system identifies the likely cause or exact changed parameter.
- A corrected replay/rerun command is generated.
- A successful or improved run appears in the timeline.
- Judges understand why AMD GPU execution mattered.

## Winning Positioning

ReplayLab should be pitched as:

**The black box flight recorder for GPU experiments.**

The story is strongest when failure is not hidden. The failed run becomes the proof that the system is useful.

## 9. Build Guidance Going Forward

- Create focused Markdown files whenever the output captures durable strategy, architecture, implementation, or judging decisions.
- Keep this document as the main strategy knowledge base, but do not force every future artifact into one file.
- Keep `info.md` as the raw hackathon brief.
- Future planning can update this document or create dedicated files when that makes the work easier to reuse.
