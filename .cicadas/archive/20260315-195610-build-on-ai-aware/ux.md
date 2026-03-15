---
next_section: 'Design Goals & Constraints'
---

# UX Design: build-on-ai-aware

## Progress

- [x] Design Goals & Constraints
- [x] User Journeys & Touchpoints
- [x] Information Architecture
- [x] Key User Flows
- [x] UI States
- [x] Copy & Tone
- [x] Visual Design Direction
- [x] UX Consistency Patterns
- [x] Responsive & Accessibility

---

## Design Goals & Constraints

**Primary goal:** The Builder should feel **informed and in control** when their work involves AI. They should never wonder whether Cicadas "ran evals" for them or assume evals are someone else's problem. Every decision (eval status, eval placement) is explicit and reversible in intent.

**Design constraints:**
- **Platform:** Terminal + agent conversation (Cursor, Claude Code, or other agent host). No graphical UI; all interaction is conversational (agent messages + user replies) and file-based (drafts, active specs).
- **Existing design:** Cicadas already uses a standard start flow (name → draft folder → requirements source → pace → PR preference) and emergence docs (PRD, UX, Tech, Approach, Tasks). This initiative adds **conversation turns and branches**, not new apps or screens.
- **Technical:** No real-time UI; prompts are inline in the agent response. Stored choices (e.g. "evals needed", "eval before build") must persist in config or registry so Approach and downstream steps see them.

**Skip condition:** Not applicable — this initiative is entirely user-facing (Builder-facing) through prompts, choices, and guided flows.

---

## User Journeys & Touchpoints

Cicadas has one primary persona for this initiative: **the Builder** (human driving the agent). The "user" is the Builder; the "product" is the sequence of agent prompts and the resulting artifacts.

### Builder — Realizing this work is Building on AI

**Entry point:** Builder has started an initiative/tweak/bug (standard start flow: name, draft folder). The flow explicitly asks about AI (MVP: no inference).

**First touchpoint:** Agent asks: "Is this project building on AI? (yes / no)". If Builder says yes, the next touchpoint is the eval-status question: "Does this project already have completed evals, or will you be doing evals?"

**Key moment:** Builder answers "already have evals" or "will do evals" and (if the latter) later sees the offer to create an eval spec after PRD/UX/Tech. They feel they've been asked, not assumed.

**Exit state:** Either (a) no eval flow (evals done), or (b) eval spec created and placement chosen (before build or in parallel, with warning if parallel). Builder proceeds to Approach/Tasks with no ambiguity.

**Pain points to design around:** Builders who assume Cicadas runs evals; Builders who forget to do evals because the process didn't ask; Builders who choose "parallel" without understanding impact — hence explicit warning and suggestion to wait.

---

### Builder — Creating the eval spec (evals needed)

**Entry point:** PRD, UX, and Tech Specs are done; Builder previously said "will do evals" and accepted the offer to create an eval spec.

**First touchpoint:** Agent offers to walk the user through the eval spec using the template and playbook. First question or section of the template is presented.

**Key moment:** Builder completes the eval spec (or a first draft) with agent assistance, grounded in the template and the six-step playbook. They have a concrete artifact (e.g. `eval-spec.md` or `eval-reqt.md`) in the draft folder.

**Exit state:** Eval spec file exists; Builder can hand it to the team that runs evals. Cicadas does not run evals.

**Pain points to design around:** Template feeling like busywork; playbook feeling disconnected from the template — agent should weave playbook steps into the template sections. Long playbook (PDF) — consider extracted summary or structured prompts so the conversation stays focused.

---

### Builder — Choosing eval placement (Approach)

**Entry point:** Approach generation; Builder has indicated evals will be needed (and may or may not have already created the eval spec).

**First touchpoint:** Agent asks: "Do you want to insert the (manual) eval step before starting the build, or in parallel?"

**Key moment:** Builder chooses. If they choose "in parallel," they immediately see the warning that eval results may materially affect requirements and design, and the suggestion to wait. They can still proceed; the warning is not a block.

**Exit state:** Approach document reflects the chosen placement (eval before build vs in parallel). Builder is informed.

**Pain points to design around:** Builder not understanding "in parallel" — copy must spell out that building and evals happen at the same time and results might change requirements. Avoid legalistic tone; stay helpful.

---

### Builder — Tweak that touches AI-backed features

**Entry point:** Builder starts a **tweak** (e.g. prompt change to an existing AI feature). Start flow: Name, Draft folder, then "Is this project building on AI? (yes / no)". They say yes; agent asks eval status.

**First touchpoint:** Same gate + eval status as initiatives. If "will do" evals/benchmarks, agent does **not** offer the full eval-spec flow (no PRD/UX/Tech for tweaks). Instead: "I can add an eval/benchmark reminder to your tweaklet — e.g. a task to run your existing eval or benchmark and document the result. Add it? (yes / no)"

**Key moment:** Builder accepts or declines. If accepted, tweaklet gets an extra checklist item or short "Eval / benchmark" section. No Approach, no placement question.

**Exit state:** Tweaklet (and optional reminder) is ready; Builder implements and runs benchmark as they see fit before merging.

**Pain points to design around:** Builder expecting full eval spec for a small tweak — make it clear the full spec is for initiatives only; the light touch is a reminder so they don't forget to run evals.

---

### Builder — Bug fix that may require a benchmark

**Entry point:** Builder starts a **bug fix** (e.g. fix that might affect model behavior or require regression checking). Same gate + eval status. If "will do" benchmarks, agent does **not** offer full eval spec.

**First touchpoint:** "I can add a benchmark/eval reminder to your buglet — e.g. a task 'Run regression benchmark before merging' or a short 'Benchmark / eval' note. Add it? (yes / no)"

**Key moment:** Builder accepts or declines. If accepted, buglet gets an extra task or section. No Approach, no placement question.

**Exit state:** Buglet (and optional reminder) is ready; Builder implements and runs benchmark as part of verification before merging.

**Pain points to design around:** Same as tweak — clarify that full eval spec is initiative-only; this is a reminder so benchmarks aren't forgotten.

---

## Information Architecture

This initiative does not introduce a new app or site. The "IA" is the **sequence and branching of the emergence flow**.

### Flow structure (high level)

**How Cicadas knows "Building on AI":** For MVP, Cicadas **asks explicitly**. It does not infer. After name and draft folder, the agent asks: "Is this project building on AI? (yes / no)". If **no** → the rest of the start flow and emergence run as today (no eval status, no eval-spec offer, no placement question). If **yes** → the agent then asks eval status and branches as below. (A future v2 could add inference from keywords or a tag; that is out of scope for MVP.)

```
Standard Start Flow (existing + new gate)
├── Name
├── Draft folder
├── [NEW] Building on AI? (yes / no)  ← explicit question; no inference in MVP
│       ├── No  → continue to Requirements source (or Pace / PR preference); no eval steps anywhere
│       └── Yes → Eval status (already have / will do) → then Requirements source, Pace, PR preference
        ↓
Emergence (existing + new branches)
├── Clarify (PRD)
├── UX
├── Tech
├── [NEW] Eval spec authoring only if "Building on AI"=yes AND "evals"=will do; after PRD/UX/Tech
├── Approach ← [NEW] Eval placement question only if "Building on AI"=yes AND "evals"=will do
└── Tasks
```

### Navigation model

**Primary "nav":** Linear progression through the emergence steps, with one branch: "evals needed" triggers the eval-spec authoring step after Tech. No tabs or menus — conversation and file artifacts only.

**Key entry points:** (1) Start flow (where "Building on AI?" is asked; if yes, then eval status) — **all types** (initiative, tweak, bug). (2) Post-Tech (where eval-spec offer is fulfilled, **initiatives only**, when Building on AI = yes and evals = will do). (2b) When drafting **tweaklet/buglet** (if Building on AI = yes and evals = will do): offer to add eval/benchmark reminder. (3) Approach (where eval placement is asked, **initiatives only**, same condition).

---

## Key User Flows

### Flow 0: Non–Building-on-AI (no eval steps)

1. Builder starts an initiative (or tweak/bug); standard start flow runs: Name, Draft folder.
2. Agent asks: "Is this project building on AI? (yes / no)".
3. Builder replies: "No."
4. Agent stores "Building on AI = no" (or equivalent). No eval-status question is asked. No eval-spec offer or placement question will appear later.
5. Flow continues with requirements source (initiatives), pace, and PR preference exactly as today. Emergence runs as today: Clarify → UX → Tech → Approach → Tasks. No eval steps, no eval spec, no placement question.

**Outcome:** Experience is unchanged from current Cicadas for projects that do not build on AI.

---

### Flow 1: Building on AI = yes, then eval status (happy path)

1. Builder starts an initiative (or tweak/bug); standard start flow runs: Name, Draft folder.
2. Agent asks: "Is this project building on AI? (yes / no)".
3. Builder replies: "Yes."
4. Agent then asks: "This project involves Building on AI. Experimentation and evals may be required. Does this project already have completed evals, or will you be doing evals? (already have / will do)" (Exact copy in Copy & Tone.)
5. Builder replies: "Already have evals" or "Will do evals."
6. Agent stores both choices (Building on AI = yes; eval status = already have | will do). Flow continues to requirements source / pace / PR preference.
7. **If "already have evals":** No eval-spec offer after PRD/UX/Tech; no eval placement question in Approach. **If "will do evals":** Agent will offer eval-spec authoring after PRD/UX/Tech and will ask placement in Approach.

**Alternate path A:** Builder says "Will do evals" → later, when PRD/UX/Tech are done, agent offers: "Would you like help creating the eval spec now? I'll use the [template] and the LLMOps Experimentation playbook." Builder says yes → eval-spec authoring flow runs.  
**Alternate path B:** Builder says "Will do evals" but later declines the eval-spec offer → no eval spec artifact; Approach still asks placement (eval step can be "manual, no spec in Cicadas").

### Flow 2: Eval-spec authoring (initiatives only; evals needed, offer accepted)

1. PRD, UX, and Tech are complete. Agent checks stored choice: evals will be needed **and** this is an initiative (not a tweak or bug fix).
2. Agent offers: "Would you like help creating the eval spec? I'll walk you through the template [path] using the LLMOps Experimentation playbook (define success, dataset, rubrics, harness, experiment, wrap-up)."
3. Builder accepts.
4. Agent guides the user section-by-section through the template (problem, use case, hypothesis, scope, success criteria, metrics, data, methodology, model/resources, harness, timeline, results, exit criteria, wrap-up), referencing the playbook where relevant. User can answer in prose or bullets; agent fills the template.
5. Agent writes the result to the draft folder (e.g. `.cicadas/drafts/{name}/eval-spec.md`). Builder reviews; no separate "submit" — the artifact is the deliverable.
6. Agent confirms: "Eval spec is saved at [path]. Cicadas does not run evals; use this spec with your team or eval harness."

**Alternate path:** Builder skips or defers → agent does not create the file; Builder can run the flow again later or create the spec manually.

---

### Flow 2b: Tweak or bug fix — eval/benchmark reminder (no full eval spec)

1. Builder is drafting a **tweaklet** or **buglet**. Agent has already stored building_on_ai = true and eval_status = will_do from the start flow.
2. Agent offers: "This work touches AI and you said you'll run evals/benchmarks. I can add a reminder to your [tweaklet/buglet] — e.g. a task 'Run existing eval or benchmark; document result' [or for buglet: 'Run regression benchmark before merging'] — so you don't forget. Add it? (yes / no)"
3. Builder says yes or no.
4. If yes: Agent adds one checklist task or a short "Eval / benchmark" (or "Benchmark / regression") section to the draft tweaklet/buglet. No full eval spec; no placement question.
5. Builder continues to implement as usual.

**Note:** For initiatives, the full eval-spec flow (Flow 2) is used instead; this light touch applies only to tweaks and bug fixes.

---

### Flow 3: Eval placement in Approach (initiatives only; before vs parallel + warning)

1. Agent is generating Approach (or has generated a draft). Agent asks: "Do you want to insert the (manual) eval step before starting the build, or run evals in parallel with the build?"
2. Builder chooses "before build" → Agent adds an explicit step in the approach (e.g. "Run evals per eval spec; proceed to implementation when gates are met.") and continues.
3. **Or** Builder chooses "in parallel" → Agent shows: "Heads up: if evals run in parallel, their results may materially affect requirements and design. We suggest waiting for eval results before locking the build plan." Then Agent still records "in parallel" and adds a step that reflects that (e.g. "Evals run in parallel; be prepared to update requirements/design if results change."). Builder can proceed.
4. Approach is finalized with the chosen placement visible in the doc.

**Alternate path A:** Builder already said "already have evals" → Agent does not ask placement; no eval step is inserted (or an optional "Evals already complete" note only).  
**Alternate path B:** Builder said "Building on AI = no" at start flow → Agent never asks placement; Approach has no eval step.  
**Alternate path C:** This is a **tweak** or **bug fix** → No Approach doc; placement question is never asked. Only the light-touch reminder (Flow 2b) applies when Building on AI + will do evals.

---

## UI States

There is no graphical UI. "States" apply to **conversation turns** and **file artifacts**.

### Building-on-AI gate and eval-status prompt

| State | Trigger | What the Builder Sees |
|-------|---------|------------------------|
| **Gate: Ready** | Start flow has reached the Building-on-AI step | Agent asks: "Is this project building on AI? (yes / no)" |
| **Gate: No** | User replied "no" | Agent continues to requirements source (or pace / PR preference). No eval steps later. Stored: Building on AI = no. |
| **Gate: Yes** | User replied "yes" | Agent asks eval status: "Does this project already have completed evals, or will you be doing evals? (already have / will do)". |
| **Eval status: Answered** | User replied "already have" or "will do" | Agent acknowledges and continues. Stored: eval status. If "already have," no eval-spec offer or placement question later. |
| **Unclear** | User reply is ambiguous (gate or eval status) | Agent re-asks with same options in parentheses (yes/no or already have/will do). |
| **Error** | Persistence of choice failed | Agent states: "I couldn't save that choice. Please try again or set it manually in [path]." |

### Eval-spec authoring

| State | Trigger | What the Builder Sees |
|-------|---------|------------------------|
| **Offer** | PRD/UX/Tech done, evals = will do | Agent offers to create eval spec with template + playbook. |
| **In progress** | Builder accepted; agent is guiding | Agent presents each template section, asks for input, fills content. |
| **Success** | Agent wrote the file | Agent confirms path and reminds: "Cicadas does not run evals." |
| **Skipped** | Builder declined or deferred | Agent continues to Approach without creating eval spec. |
| **Error** | File write failed (e.g. permissions) | Agent reports the error and suggests saving content elsewhere or retrying. |

### Eval placement (Approach, initiatives only)

| State | Trigger | What the Builder Sees |
|-------|---------|------------------------|
| **Ask** | Approach generation, evals = will do | Agent asks: before build or in parallel? |
| **Chose before** | User chose "before build" | Agent adds the step; no warning. |
| **Chose parallel** | User chose "in parallel" | Agent shows warning + suggestion to wait; then records "in parallel" and adds step. |
| **N/A** | Evals = already have, or **tweak/bug** (no Approach) | No question; no eval step (or optional note only). |

### Eval/benchmark reminder (tweaklet / buglet only)

| State | Trigger | What the Builder Sees |
|-------|---------|------------------------|
| **Offer** | Drafting tweaklet/buglet, building_on_ai = yes, eval_status = will do | Agent offers to add reminder task or section. |
| **Accepted** | Builder said yes | Agent adds one task or section to the spec. |
| **Declined** | Builder said no | Agent continues without adding. |
| **N/A** | Initiative (full eval spec offered instead) or evals = already have | No offer. |

---

## Copy & Tone

**Voice:** Direct, concise, and procedural. Same as existing Cicadas prompts: no marketing speak, no humor. Helpful but neutral. When warning (e.g. parallel evals), be clear and suggestive, not alarming.

**Key principles:**
- State "Building on AI" and "Cicadas does not run evals" explicitly so there is no ambiguity.
- Every choice is a short, scannable question with bounded options where possible (e.g. "already have / will do").
- Warnings are one short paragraph: what could happen + what we suggest; then move on.

**Critical copy samples:**

| Context | Copy |
|---------|------|
| Building on AI gate (MVP: explicit ask) | `Is this project building on AI? (yes / no)` |
| Eval status (only when gate = yes) | `This project involves Building on AI. Experimentation and evals may be required. Does this project already have completed evals, or will you be doing evals? (already have / will do)` |
| Eval-spec offer (initiatives only) | `Would you like help creating the eval spec? I'll walk you through the template using the LLMOps Experimentation playbook (define success, dataset, rubrics, harness, experiment, wrap-up).` |
| Eval/benchmark reminder (tweak) | `This work touches AI and you said you'll run evals/benchmarks. I can add a reminder to your tweaklet — e.g. a task "Run existing eval or benchmark; document result." Add it? (yes / no)` |
| Eval/benchmark reminder (bug fix) | `This work touches AI and you said you'll run evals/benchmarks. I can add a reminder to your buglet — e.g. a task "Run regression benchmark before merging." Add it? (yes / no)` |
| Eval placement question (initiatives only) | `Do you want to insert the (manual) eval step before starting the build, or run evals in parallel with the build? (before / parallel)` |
| Parallel warning | `Heads up: if evals run in parallel, their results may materially affect requirements and design. We suggest waiting for eval results before locking the build plan. You can still proceed now if you prefer.` |
| After eval spec saved | `Eval spec saved at [path]. Cicadas does not run evals — use this spec with your team or eval harness.` |
| Clarify eval status | `Do you already have completed evals for this project, or will you be doing evals? Reply "already have" or "will do".` |

---

## Visual Design Direction

**Style:** N/A for this initiative. All interaction is terminal/chat text. No visual design system is introduced. If a future initiative adds a UI (e.g. a small web status page), it would follow Cicadas' existing direction (minimal, terminal-friendly, dark if any).

**Color palette / Typography / Spacing:** Not applicable — CLI and agent messages only.

**Existing design system:** Cicadas is CLI- and file-based; no GUI design system. Copy and flow structure are the "design."

---

## UX Consistency Patterns

### Prompt pattern

- **One decision per turn where possible:** Ask one clear question (eval status, placement) with bounded options. Avoid stacking multiple yes/no questions in one block.
- **Confirm and persist:** After the user answers, briefly confirm and state what was stored (e.g. "Recorded: evals will be needed. I'll offer the eval spec after PRD, UX, and Tech.").
- **Recovery:** If the user's reply is ambiguous, re-ask with the same options in parentheses: "(already have / will do)".

### Offer pattern

- **Explicit offer, explicit decline:** "Would you like X?" — user can say yes or no. If no, do not repeat the offer in the same flow; they can ask later.
- **No auto-assumption:** Never assume "will do evals" or "already have evals" without asking. Never assume "before build" vs "parallel" without asking when evals are needed.

### Warning pattern

- **One block, then proceed:** Warning = one short paragraph. Then "You can still proceed if you prefer" (or equivalent). No second-guessing the user.
- **Same structure for all warnings:** (1) What could happen. (2) What we suggest. (3) That it's their call.

### File artifact pattern

- **Name and path:** Eval spec has a single canonical name/path (e.g. `eval-spec.md` in the draft folder). Document it in Tech and in the prompt after save.
- **Template + playbook:** When guiding, refer to "the template" and "the playbook" by name so the Builder can open them if they want.

---

## Responsive & Accessibility

**Breakpoints:** Not applicable — no responsive layout. All interaction is text (terminal or chat).

**Accessibility standards:** For the **conversation** itself: copy must be readable in plain text (no information conveyed only by color or images). For any future GUI: WCAG 2.1 AA would apply; this initiative does not add GUI.

**Key requirements:**
- **Keyboard navigation:** N/A (user types replies).
- **Screen reader:** All content is text; no charts or images required for the flow. If the playbook or template is ever presented as an image, provide a text alternative or link to the source file.
- **Copy clarity:** Avoid jargon in the main prompts; "evals," "eval spec," and "Building on AI" are acceptable as they are defined in context. Use consistent terms (e.g. "eval spec" not "eval doc" / "eval spec" interchangeably in the same flow).
- **Reduced motion:** N/A.

---
