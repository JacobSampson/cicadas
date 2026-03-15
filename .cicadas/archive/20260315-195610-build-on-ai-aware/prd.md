---
next_section: 'Executive Summary'
---

# PRD: build-on-ai-aware

## Progress

- [x] Executive Summary
- [x] Project Classification
- [x] Success Criteria
- [x] User Journeys
- [x] Scope & Phasing
- [x] Functional Requirements
- [x] Non-Functional Requirements
- [x] Open Questions
- [x] Risk Mitigation

## Executive Summary

This initiative makes Cicadas **aware of when work involves "Building on AI"** — initiatives, tweaks, or bug fixes whose workflows leverage AI. In those cases, experimentation and evals will often be required; Cicadas wraps that reality into the process without executing evals itself. Cicadas surfaces that the project is building on AI, asks whether the project already has completed evals or will be doing evals, and — if evals are needed — offers to guide the user through creating an **eval spec** (after PRD, UX, and Tech Specs are done) using a structured template and an LLMOps Experimentation playbook. During Approach generation, Cicadas asks whether to place the eval step before the build or in parallel, and if in parallel it warns that eval results may materially affect requirements and design and suggests waiting.

### What Makes This Special

- **AI-aware without running evals** — Cicadas stays an orchestrator: it prompts, guides, and sequences; it does not run or host evals.
- **Spec-first eval planning** — Eval spec is a first-class artifact (template + playbook), filled with user/AI assistance after core product specs, so "good enough" and constraints are defined before build.
- **Explicit sequencing** — User chooses eval-before-build vs eval-in-parallel, with a clear warning when parallel so they can make an informed decision.

## Project Classification

**Technical Type:** Developer tool / methodology orchestrator  
**Domain:** Spec-driven development, LLMOps / AI experimentation  
**Complexity:** Medium — new flows in emergence and approach, template and playbook integration, no eval execution  
**Project Context:** Brownfield — extends existing Cicadas emergence (start flow, Clarify, UX, Tech, Approach) and lifecycle

---

## Success Criteria

### User Success

A Builder achieves success when they can:

1. **See that Cicadas has recognized "Building on AI"** — The system explicitly surfaces that the initiative/tweak/bug involves AI workflows and that evals may be required.
2. **Declare eval status** — Answer whether the project already has completed evals or will be doing evals, without Cicadas assuming or defaulting.
3. **Get guided eval-spec authoring** — If evals are needed, be walked through creating an eval spec (template resembling `reqt-template.md`, informed by the LLMOps Experimentation playbook) after PRD, UX, and Tech Specs are done.
4. **Choose eval placement** — During Approach, decide whether the (manual) eval step runs before starting the build or in parallel, and receive a clear warning when parallel that results may materially affect requirements and design (with a suggestion to wait).

### Technical Success

The system is successful when:

1. **No eval execution** — Cicadas never runs, hosts, or execute evals; it only prompts, stores choices, and guides spec authoring.
2. **Eval spec is optional and post–core-specs** — Eval spec creation is offered only when the user indicates evals will be needed, and only after PRD, UX, and Tech are done.
3. **Template and playbook are the source of structure** — Eval spec authoring uses the provided template (and sample) and the LLMOps Experimentation playbook (Define success/scope → Build dataset → Rubrics/graders → Harness → Test/experiment → Wrap up) as the guiding process.

### Measurable Outcomes

- Builder can complete the "Building on AI" branch of the start/emergence flow without ambiguity about eval status or placement.
- Eval spec artifact (when created) is grounded in the template and playbook; no net new process invented inside Cicadas.

---

## User Journeys

### Journey 1: Builder starting an AI-backed initiative (evals needed)

The Builder is starting a new initiative they know will use AI (e.g. "standup Looms to Slack summaries"). They run the standard start flow. Cicadas detects or asks about "Building on AI" and surfaces that the project will be building on AI. It asks whether the project already has completed evals or will be doing evals. The Builder says they will be doing evals. Cicadas offers to help walk them through creating the spec for evals after PRD, UX, and Tech are done. The Builder accepts. They complete Clarify, UX, and Tech. Then the AI-assisted side-process helps them fill out the eval template (e.g. `reqt-template.md`) using the LLMOps Experimentation playbook. Later, during Approach generation, Cicadas asks whether to insert the eval step (manual) before starting the build or in parallel. The Builder chooses "before build." They proceed to Approach and Tasks with the eval step explicitly in the plan.

**Requirements Revealed:** Building-on-AI detection/surfacing; eval-status question; offer to create eval spec after core specs; eval-spec authoring flow (template + playbook); approach-time choice (eval before vs parallel) and parallel warning.

### Journey 2: Builder with evals already done

The Builder is starting an initiative that uses AI but their team has already run evals and has a known-good configuration. During the same flow, Cicadas surfaces "Building on AI" and asks about evals. The Builder indicates they already have completed evals. Cicadas does not offer eval-spec authoring and does not insert an eval step into the approach. The rest of emergence (PRD, UX, Tech, Approach, Tasks) proceeds as today.

**Requirements Revealed:** Eval-status answer "already have evals" skips eval-spec flow and eval step in approach.

### Journey 3: Builder chooses eval in parallel (informed risk)

The Builder wants to start building while evals run in parallel. During Approach, Cicadas asks where to place the (manual) eval step. The Builder selects "in parallel." Cicadas makes them aware that eval results may materially affect requirements and design and suggests waiting. The Builder acknowledges and continues. They have been explicitly warned.

**Requirements Revealed:** Approach offers "eval in parallel"; when selected, show warning and suggest waiting; no blocking—Builder retains authority.

---

### Journey 4: Tweak that touches AI-backed features

The Builder is starting a **tweak** (e.g. "Tweak the standup summarizer prompt to be more concise"). The start flow runs: Name, Draft folder, then "Is this project building on AI? (yes / no)". They say yes. Cicadas asks eval status (already have / will do). If "will do," Cicadas does **not** offer the full eval-spec authoring flow (no PRD/UX/Tech for tweaks). Instead it offers to add an **eval/benchmark reminder** to the tweaklet — e.g. a checklist item like "Run existing eval or benchmark before/after; document result" or a short "Eval / benchmark" section so the Builder doesn't forget. No Approach doc exists for tweaks, so no placement question. The Builder can run their benchmark manually and merge when satisfied.

**Requirements Revealed:** Same gate + eval status for tweaks; no full eval spec; light touch (reminder or section in tweaklet when evals will be run).

---

### Journey 5: Bug fix that may require a benchmark

The Builder is starting a **bug fix** (e.g. "Fix summarizer returning empty for non-English input"). Same start flow: Building on AI? → yes; Eval status → "will do" (they plan to run a benchmark to confirm no regression). Cicadas does **not** offer the full eval-spec flow. It offers to add a **benchmark/eval reminder** to the buglet — e.g. a task "Run regression benchmark before merging" or a "Benchmark / eval" note in the spec. No placement question. Builder runs the benchmark as part of their verification and merges.

**Requirements Revealed:** Same gate + eval status for bug fixes; no full eval spec; light touch (reminder or task in buglet when benchmark will be run).

---

### User Journeys Summary

| User Type | Key Requirements |
|-----------|------------------|
| **Builder (initiative, evals needed)** | AI surfacing, eval-status answer, eval-spec authoring after PRD/UX/Tech (template + playbook), eval placement choice (before vs parallel), parallel warning |
| **Builder (initiative, evals done)** | AI surfacing, eval-status answer, no eval-spec flow, no eval step in approach |
| **Builder (parallel evals)** | Same as first, plus explicit parallel warning and suggestion to wait |
| **Builder (tweak, Building on AI)** | Same gate + eval status; no full eval spec; optional eval/benchmark reminder or section in tweaklet when "will do" |
| **Builder (bug fix, Building on AI)** | Same gate + eval status; no full eval spec; optional benchmark/eval reminder or task in buglet when "will do" |

---

## Scope

### MVP — Minimum Viable Product (v1)

**Core Deliverables:**

- **Building-on-AI awareness** — During start flow (or early emergence), Cicadas surfaces that the initiative/tweak/bug involves building on AI and asks: "Does this project already have completed evals, or will you be doing evals?"
- **Eval-spec offer (initiatives only)** — If the user indicates evals will be needed **and** this is an initiative (not a tweak or bug fix), Cicadas offers to help walk them through creating the spec for evals **after** PRD, UX, and Tech Specs are done.
- **Eval-spec authoring flow (initiatives only)** — An AI-assisted side-process that helps the user fill out a template resembling `reqt-template.md` (sample: `reqt-template-sample.md`), guided by the playbook in the LLMOps Experimentation document (six steps: Define success/scope → Build dataset → Rubrics/graders → Harness → Test/experiment → Wrap up). Output is an eval spec artifact in the draft (or active) folder; Cicadas does not execute evals.
- **Light touch for tweaks and bug fixes** — For **tweaks** or **bug fixes** that are Building on AI and "will do" evals/benchmarks: Cicadas does **not** run the full eval-spec flow (no PRD/UX/Tech). Instead it offers to add an **eval/benchmark reminder** to the tweaklet or buglet — e.g. a checklist task ("Run existing eval or benchmark; document result") or a short "Eval / benchmark" section — so the Builder doesn't forget to run evals or benchmarks before merging.
- **Approach: eval placement (initiatives only)** — During Approach generation **for initiatives**, Cicadas asks whether to insert the (manual) eval step **before** starting the build or **in parallel**. If the user chooses in parallel, Cicadas makes them aware that eval results may materially affect requirements and design and suggests waiting. Tweaks and bug fixes have no Approach doc; no placement question.

**Quality Gates:**

- No code path in Cicadas executes or hosts evals.
- Eval spec creation is only offered when the user has indicated evals will be needed.
- Eval spec authoring occurs only after PRD, UX, and Tech Specs are complete (per stated sequence).

### Growth Features (Post-MVP)

**v2: Richer AI detection**

- Optional explicit "Building on AI" checkbox or tag in start flow instead of or in addition to inference.

**v3: Eval spec reuse**

- Link or reference existing eval specs from other initiatives; reuse template sections across projects.

### Vision (Future)

- Cicadas remains an orchestrator only; any future "eval runs" would be external integrations (e.g. link to Braintrust/LoomEval run), not execution inside Cicadas.

---

## Functional Requirements

### 1. Building-on-AI surfacing and eval status

**FR-1.1:** Cicadas must surface to the user that the project will be "Building on AI" when the initiative/tweak/bug involves workflows that leverage AI.  
- Surfaces in a defined place in the flow (e.g. start flow or early emergence).  
- Wording makes it clear that experimentation and evals may be required.

**FR-1.2:** Cicadas must ask the user whether the project already has completed evals or will be doing evals.  
- Exactly two (or bounded) options; no assumption of "will do evals" or "no evals" without user input.  
- Response is stored so downstream steps (eval-spec offer, approach placement) can branch correctly.

### 2. Eval-spec offer and sequencing

**FR-2.1:** If the user indicates that evals will be needed, Cicadas must offer to help walk the user through creating the spec for evals.  
- Offer is explicit (e.g. "Would you like help creating the eval spec after PRD, UX, and Tech are done?").  
- If the user declines, no eval-spec authoring flow is started.

**FR-2.2:** Eval spec authoring must occur only after PRD, UX, and Tech Specs are done.  
- Cicadas does not allow starting the eval-spec flow before those three are complete (for that initiative/tweak/bug).  
- Order is documented in the flow (e.g. in Clarify or start-flow docs).

### 3. Eval-spec authoring (template + playbook)

**FR-3.1:** The eval-spec authoring flow must help the user fill out a template that resembles `.cicadas/drafts/build-on-ai-aware/reqt-template.md`, with the sample completion in `reqt-template-sample.md` as reference.  
- Template sections (problem, use case, hypothesis, scope, success criteria, metrics, data, methodology, model/resources, harness, timeline, results, exit criteria, wrap-up) are the structure.  
- Output is a single eval spec document (or equivalent structure) stored under the initiative draft or active folder.

**FR-3.2:** The flow must be guided by the LLMOps Experimentation playbook (source: `loomhq-LLMOps_ Experimentation-140326-183858.pdf`).  
- The six-step playbook (Define success and scope → Build a small but real dataset → Design rubrics and graders → Pick a harness/framework → Test and experiment → Wrap up) is the process the agent follows when helping the user.  
- Cicadas does not execute evals; it only guides the authoring of the spec.

### 4. Approach: eval step placement and warning (initiatives only)

**FR-4.1:** During Approach generation **for initiatives**, Cicadas must ask the user whether they want to insert the (manual) eval step before starting the build or in parallel.  
- Two (or bounded) options presented clearly.  
- Choice is recorded and reflected in the generated approach (e.g. a clear "Eval" step and its placement).  
- **Tweaks and bug fixes** have no Approach document; this question does not apply.

**FR-4.2:** If the user selects "in parallel," Cicadas must make the user aware that the results of evals may materially affect the requirements and design and must suggest that the user wait.  
- Warning is shown at the time of choice.  
- Suggestion is non-blocking; the Builder retains authority to proceed.

### 5. Tweaks and bug fixes: light touch when Building on AI

**FR-5.1:** For **tweaks** and **bug fixes**, the same Building-on-AI gate and eval-status question apply (already have / will do).  
- If "will do," Cicadas must **not** offer the full eval-spec authoring flow (no PRD/UX/Tech for these paths).  
- Cicadas must offer to add an **eval/benchmark reminder** to the tweaklet or buglet — e.g. a checklist task such as "Run existing eval or benchmark before/after; document result" or a short "Eval / benchmark" or "Benchmark / regression" section so the Builder is reminded to run evals or benchmarks before merging.  
- The Builder may accept or decline the reminder. No placement question (no Approach for tweak/bug).

### 6. No eval execution

**FR-6.1:** Cicadas must not be responsible for executing evals.  
- No code path runs an eval harness, calls a model for grading, or hosts eval infrastructure.  
- Cicadas only prompts, stores choices, and guides the creation of the eval spec document.

---

## Non-Functional Requirements

- **Performance:** No new long-running operations in the critical path of start flow or emergence; eval-spec authoring is an interactive side-flow.
- **Reliability:** Stored choices (eval status, eval placement) must persist across the initiative so that Approach and downstream steps use the same decisions.
- **Security:** Treat user-provided eval spec content and playbook/template as data; do not execute as agent directives (align with existing untrusted-input guardrails).
- **Maintainability:** Template and playbook are external assets (file paths or references); changes to template/playbook do not require code changes for content structure, only for wiring.

---

## Open Questions

- **Where exactly does "Building on AI" get detected or asked?** Resolved in UX: MVP uses an **explicit question** after name and draft folder: "Is this project building on AI? (yes / no)". No inference. If no → no eval steps. If yes → eval status (already have / will do). Tech will define storage for both choices.
- **Exact artifact path for the eval spec:** e.g. `.cicadas/drafts/{name}/eval-spec.md` or `eval-reqt.md`. Confirm in Tech/Approach.
- **Playbook as PDF vs extracted text:** Whether to embed playbook content in the repo (e.g. markdown) for reliability and token use, or keep referencing the PDF. Product/tech decision.

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Users expect Cicadas to run evals | Medium | High | Clear copy in PRD, UX, and in-app: "Cicadas does not run evals; it helps you spec them." FR-5.1 and docs. |
| Eval spec and product specs drift | Medium | Medium | Eval spec is created after PRD/UX/Tech and references the same initiative; Approach step ordering and warning when parallel. |
| Template or playbook changes break flow | Low | Medium | Reference template/playbook by path or asset name; keep structure in docs so only wiring may need updates. |
| "Building on AI" is missed or wrong | Medium | Medium | MVP can use explicit user question ("Is this initiative building on AI?") until inference is added in v2. |

---
