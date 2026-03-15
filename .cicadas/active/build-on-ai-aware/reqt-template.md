

Problem Statement: What problem are we solving and why now? 




Use Case: One concrete scenario; easy to swap later. 




Objective / Intended Impact: Measurable business/user impact. 




2) Hypothesis / Success Specification

Primary Hypothesis:

The system should <do X> with <primary metric> ≥ <threshold> under constraints of <latency/cost/safety>. 




Scope: In vs out, to prevent scope creep. 




Success Criteria (numeric): Hard gates only. 




3) Metrics

Define what “good” means and how it’s measured. Keep gates explicit.

|   |   |   |   |
|---|---|---|---|
|**Metric**|**Target / Constraint**|**Type (Hard Gate/Monitor)**|**Bucket (Task/Safety/Format/Latency/Cost)**|
|||||
|||||
|||||









Metric definitions: Briefly define computation and source of truth.




4) Data

Dataset Description: Name, size, representativeness, edge cases. 




Sources & Privacy: Origin, consent, PII handling, access control. 




Labels & Guidelines: What labels exist and how to apply them. 




Storage & Manifest: Exact location and owner. 




5) Methodology

Experiment Approach: Baseline, single-variable changes, eval loop.




Graders & Rubrics: Deterministic checks + LLM judge + optional human loop.




6) Model & Resource Requirements

Model Configuration: Model(s), temperature, max tokens, system prompt, output schema. 



Human & Technical Resources: People, environments, credits/budget. 




7) Experiment Harness / Framework

Tooling: Harness/framework, evaluation style (lab vs in-situ), logging. 




Assets Location: Where prompts, datasets, runs live. 





8) Timeline

Milestones & Decision Date: High-level schedule and ship/no-ship decision date.


9) Results & Experiment Snapshots

Record variants and best-run snapshot for reproducibility.

|   |   |   |   |   |
|---|---|---|---|---|
|**Variant ID**|**Change Description**|**Primary Metric (Task F1)**|**Δ vs Baseline**|**Notes**|
||||||
||||||
||||||




Best Run Snapshot:




10) Exit Criteria

Ship when all hard gates are met on the eval set and human audit agrees with LLM judge at acceptable levels.

Abort/Pivot: After N serious variants if quality remains below targets or constraints infeasible.

11) Wrap-Up & Peer Review

Summary: What was tried, dataset used, metrics achieved, decision made.



Reviewers: 

[Add Product Manager]

[Add Engineering Manager]

[Add AI/ML Partner]