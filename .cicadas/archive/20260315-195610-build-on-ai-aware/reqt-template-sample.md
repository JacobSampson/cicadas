Problem Statement: _What problem are we solving and why now?_

Async standup Looms are long; teams need concise Slack summaries.

Use Case: _One concrete scenario; easy to swap later._

Standup Looms to Slack summaries.

Objective / Intended Impact: _Measurable business/user impact._

Reduce manual note-taking time by 50% with equal usefulness.

## 2) Hypothesis / Success Specification

Primary Hypothesis:

The system should **<do X>** with **<primary metric> ≥ <threshold>** under constraints of **<latency/cost/safety>**.

Generate standup summaries from Loom transcripts with usefulness ≥ 4.0/5 and task F1 ≥ 0.80, under p95 latency ≤ 3s and cost ≤ $0.02/request.

Scope: _In vs out, to prevent scope creep._

In: English, Looms tagged “standup”, ≤5 speakers.

Out: non-English, heavy visual reasoning.

Success Criteria (numeric): _Hard gates only._

Task F1 ≥ 0.80; usefulness ≥ 4.0/5

JSON correctness ≥ 99.5%

policy violations ≤ 0.5%

p95 latency ≤ 3s; cost ≤ $0.02.

## 3) Metrics

Define what “good” means and how it’s measured. Keep gates explicit.

|   |   |   |   |
|---|---|---|---|
|**Metric**|**Target / Constraint**|**Type (Hard Gate/Monitor)**|**Bucket (Task/Safety/Format/Latency/Cost)**|
|||||
|||||
|||||

Metric definitions: _Briefly define computation and source of truth._

- Task F1: code-computed vs gold labels; macro F1 across fields.
    
- Usefulness: LLM-as-judge rubric + small human audit set.
    
- JSON correctness: strict validator over output schema.
    

## 4) Data

Dataset Description: _Name, size, representativeness, edge cases._

Standup-Summaries-Eval-v1

20 Looms:

- Duration: 5 <5 mins, 10 5-20 min, 5 >30 min
    
- Artifacts: 5 noisy
    
- Content: 10 with task board, 10 with code demos
    

Sources & Privacy: _Origin, consent, PII handling, access control._

Opt-in internal workspace; PII redacted; restricted access.

Labels & Guidelines: _What labels exist and how to apply them._

None currently; will hand label.

Storage & Manifest: _Exact location and owner._

loom://datasets/standup-summaries/manifest-v1.json; Owner: [Add Product Manager].

## 5) Methodology

Experiment Approach: _Baseline, single-variable changes, eval loop._

- Baseline: simple prompt + base model; no retrieval/tools.
    
- Variants: prompt tweaks, few-shot, alternative models, decoding params.
    
- Evaluation: run over dataset; compute task/safety/format/latency/cost.
    

Graders & Rubrics: _Deterministic checks + LLM judge + optional human loop._

- Code checks: JSON schema validation; required fields present; limits.
    
- LLM judge: usefulness and tone/style 0–5 with examples per bucket.
    
- Human audit: 20–40 items for agreement and drift checks.
    

## 6) Model & Resource Requirements

Model Configuration: _Model(s), temperature, max tokens, system prompt, output schema._

- AIGateway use case ID X
    
- OpenAI, Gemini, Claude model families
    

Human & Technical Resources: _People, environments, credits/budget._

- [Add Engineer]
    
- [Add Designer]
    
- staging env
    
- AI gateway access.
    

## 7) Experiment Harness / Framework

Tooling: _Harness/framework, evaluation style (lab vs in-situ), logging._

- Eval tool: X
    
- AIGateway for LLM
    
- System under test (SuT) for in-situ testing
    

Assets Location: _Where prompts, datasets, runs live._

Prompts:  
- System under test git repo

Configs:

- System under test git repo
    

Test Datasets:

- Google Drive (location X)
    

## 8) Timeline

Milestones & Decision Date: _High-level schedule and ship/no-ship decision date._

- 1 week: Finalize success spec + dataset; run baseline.
    
- 2 weeks: Iterate 2–4 variants; select candidate snapshot.
    
- 1 week: Human audit + peer review; ship decision.
    

Target decision date:

## 9) Results & Experiment Snapshots

Record variants and best-run snapshot for reproducibility.

|   |   |   |   |   |
|---|---|---|---|---|
|**Variant ID**|**Change Description**|**Primary Metric (Task F1)**|**Δ vs Baseline**|**Notes**|
||||||
||||||
||||||

Best Run Snapshot:

- Name: standup-summary-v3-2026-03-28
    
- Dataset: Standup-Summaries-Eval-v1; Prompt: prompt-standup-v2; Judge: judge-standup-usefulness-v1
    
- Model: pro; temp 0.3; max_tokens 512; Output: strict JSON
    
- Key Metrics: F1 0.83; usefulness 4.4/5; policy 0.3%; JSON 99.8%; p95 2.7s; cost $0.019
    
- Run link:
    

## 10) Exit Criteria

Ship when all hard gates are met on the eval set and human audit agrees with LLM judge at acceptable levels.

Abort/Pivot: After N serious variants if quality remains below targets or constraints infeasible.

## 11) Wrap-Up & Peer Review

Summary: _What was tried, dataset used, metrics achieved, decision made._

Reviewers:

[Add Product Manager]

[Add Engineering Manager]

[Add AI/ML Partner]