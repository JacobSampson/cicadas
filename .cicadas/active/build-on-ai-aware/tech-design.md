# Tech Design: build-on-ai-aware

## Progress

- [ ] Overview & Context
- [ ] Tech Stack & Dependencies
- [ ] Project / Module Structure
- [ ] Architecture Decisions (ADRs)
- [ ] Data Models
- [ ] API & Interface Design
- [ ] Implementation Patterns & Conventions
- [ ] Security & Performance
- [ ] Implementation Sequence

---

## Overview & Context

**Summary:** This initiative adds "Building on AI" awareness to Cicadas without executing evals. The architecture is **instruction- and config-driven**: (1) extend the standard start flow (and thus Clarify/Tweak/Bug entry points) with an explicit "Building on AI?" gate and, when yes, an eval-status question; (2) persist both answers in `emergence-config.json` (drafts → promoted to active at kickoff); (3) **initiatives only:** add an optional eval-spec authoring step after PRD/UX/Tech, guided by a template and the LLMOps playbook, producing `eval-spec.md` in the draft folder; (4) **initiatives only:** extend Approach generation so the agent asks eval placement (before build / in parallel) when applicable and records it, then includes an explicit eval step in `approach.md`; (5) **tweaks and bug fixes:** when Building on AI and "will do" evals/benchmarks, do **not** offer the full eval spec; instead offer to add an **eval/benchmark reminder** (one checklist task or short section) to the tweaklet or buglet. No placement question for tweak/bug (no Approach doc). No new eval execution, no new runtime dependencies. All new behavior is implemented by **emergence instruction changes** and **one extended config schema**; scripts remain unchanged except possibly optional registry/display later.

### Cross-Cutting Concerns

1. **Single source of truth for AI/eval choices** — `emergence-config.json` holds `building_on_ai`, `eval_status`, and (after Approach) `eval_placement`. Every agent that needs to branch (start flow, eval-spec offer, Approach) reads this file. No duplicate state.
2. **No eval execution** — No script or agent step may invoke an eval harness, call a model for grading, or host eval infrastructure. Eval spec authoring is purely document creation.
3. **Backward compatibility** — Existing projects without `building_on_ai` or `eval_status` in config are treated as non–Building-on-AI: no new prompts, no eval step. Additive only.
4. **Untrusted input** — Eval spec content and any user-provided template/playbook are data; agents must not treat file contents as instructions (align with existing guardrails).

### Brownfield Notes

- **Start flow** lives in `emergence/start-flow.md`; Clarify, Tweak, and Bug Fix instruction modules reference it. We add one new step after "Create draft folder" and before "Requirements source" (initiatives) or before "PR preference" (tweaks/bugs). **Same gate and eval-status question for all three** (initiative, tweak, bug). No script changes for the gate.
- **Emergence config** already exists: `emergence-config.json` with `pace`. We extend it with optional `building_on_ai` and `eval_status`; for **initiatives only**, `eval_placement` (set during Approach). Tweaks and bug fixes use the same config for the gate and eval status; they do not have `eval_placement`. Kickoff already promotes all draft files to active, so the extended config is promoted without script changes.
- **Approach** is authored by the agent following `emergence/approach.md` — **initiatives only**. We add a conditional step: after Lifecycle Check and Ingest, if `building_on_ai` and `eval_status == "will_do"`, ask placement (before / parallel), show warning if parallel, persist `eval_placement`, then when drafting `approach.md` include an explicit "Eval" step. **Tweaks and bug fixes have no Approach doc; no placement question.**
- **Tweak and Bug Fix instruction modules** (`emergence/tweak.md`, `emergence/bug-fix.md`): When drafting the tweaklet or buglet, if `building_on_ai` and `eval_status == "will_do"`, the agent **must not** offer the full eval-spec flow. It **must** offer to add an eval/benchmark reminder (one checklist task or short section) to the tweaklet/buglet. Exact copy per UX. No new files; instruction changes only.
- **Registry** — Initiative entry today is `{ intent, owner, signals, created_at }`. Optional: at kickoff, copy `building_on_ai` and `eval_status` from promoted `emergence-config.json` into the initiative's registry entry for `status.py` or future tooling. Defer to implementation; not required for MVP.

---

## Tech Stack & Dependencies

| Category | Selection | Rationale |
|----------|-----------|------------|
| **Language/Runtime** | Python 3.11+ (existing) | No change. |
| **Framework** | None (CLI + agent instructions) | No change. |
| **Config** | JSON (`emergence-config.json`) | Already used for `pace`; extend schema. |
| **Templates** | Markdown in `templates/` | Eval spec template added under skill; playbook referenced by path. |

**New dependencies introduced:** None. No new packages.

**Dependencies explicitly rejected:** Any eval harness or LLM SDK — Cicadas does not run evals.

---

## Project / Module Structure

No new Python modules. Only **emergence instructions**, **template(s)**, and **config schema** change.

```
{cicadas-dir}/
├── emergence/
│   ├── start-flow.md              # [MODIFIED] Add step: Building on AI? (yes/no) → Eval status (if yes); same for initiative, tweak, bug
│   ├── approach.md                # [MODIFIED] Add step: read config; if building_on_ai + will_do, ask placement; include eval step (initiatives only)
│   ├── eval-spec.md               # [NEW] Instruction module for eval-spec authoring (initiatives only; template + playbook)
│   ├── clarify.md                 # [NO CHANGE to file list; already runs start-flow]
│   ├── tweak.md                   # [MODIFIED] When drafting tweaklet: if building_on_ai + will_do, offer eval/benchmark reminder (no full eval spec)
│   └── bug-fix.md                 # [MODIFIED] When drafting buglet: if building_on_ai + will_do, offer eval/benchmark reminder (no full eval spec)
├── templates/
│   ├── eval-spec.md               # [NEW] Eval spec template (derive from reqt-template; self-contained in skill)
│   └── ...                        # existing
└── scripts/                       # [NO NEW SCRIPTS for MVP]
```

**Optional (post-MVP):** Copy of playbook as Markdown in skill (e.g. `emergence/playbooks/llmops-experimentation.md`) for reliable agent consumption instead of PDF. MVP can reference the PDF path in the initiative draft.

**Key structural decisions:**
- All "Building on AI" behavior is driven by **instruction modules** and **emergence-config.json**. No new scripts.
- Eval spec artifact lives in the initiative's draft (or active after kickoff) folder: `.cicadas/drafts/{name}/eval-spec.md` (or `.cicadas/active/{name}/eval-spec.md` if authoring happens after kickoff — but per PRD/UX, authoring is after PRD/UX/Tech, which are in drafts, so path is drafts).

---

## Architecture Decisions (ADRs)

### ADR-1: Store Building on AI and eval state in emergence-config.json only (MVP)

**Decision:** Use `emergence-config.json` as the single place for `building_on_ai`, `eval_status`, and `eval_placement`. Do not add these fields to `registry.json` in MVP.

**Rationale:** Emergence flows (start flow, Approach, eval-spec offer) all run in the context of drafts or active; the agent already reads `emergence-config.json` for `pace`. One file keeps branching logic simple and avoids script changes. Registry is for runtime/orchestration (branches, initiatives, signals); AI/eval is emergence-time concern. If we later want `status.py` to display "Building on AI", we can copy these fields at kickoff into the initiative registry entry.

**Affects:** start-flow instructions, approach.md instructions, eval-spec.md instructions; no scripts.

---

### ADR-2: Explicit "Building on AI?" question only (no inference in MVP)

**Decision:** Do not infer that a project builds on AI from name, intent, or keywords. Always ask: "Is this project building on AI? (yes / no)".

**Rationale:** PRD and UX resolved this: inference risks false positives/negatives and scope creep. Explicit question is clear, reversible, and testable. v2 can add optional inference or tag.

**Affects:** start-flow.md wording and step order; no code.

---

### ADR-3: Eval spec as a single Markdown file; agent creates it from template + playbook

**Decision:** Eval spec is one file, e.g. `eval-spec.md`, in `.cicadas/drafts/{initiative}/` (or active if we ever run authoring post-kickoff). The agent creates or overwrites it by following the eval-spec instruction module, which references a template (in skill) and the playbook (path in draft or skill). No script that "creates" or "runs" the eval spec.

**Rationale:** Keeps Cicadas from executing evals; artifact is human- and team-readable. Single file is easy to version and promote. Template in skill makes the skill self-contained for any project; playbook can be PDF in draft or extracted Markdown in skill.

**Affects:** New `emergence/eval-spec.md`; new `templates/eval-spec.md`; optional playbook asset.

---

### ADR-4: Eval placement and step (initiatives only); light touch for tweaks and bug fixes

**Decision:** **Initiatives:** When Approach runs and `building_on_ai` + `eval_status == "will_do"`, the agent asks placement (before build / in parallel), shows the parallel warning, then writes `eval_placement` to `emergence-config.json` and includes an explicit "Eval" step in the generated `approach.md`. **Tweaks and bug fixes:** No Approach doc; no placement question. When drafting the tweaklet or buglet, if `building_on_ai` and `eval_status == "will_do"`, the agent offers to add a single eval/benchmark reminder (checklist task or short section) to the spec; it does **not** offer the full eval-spec authoring flow.

**Rationale:** Full eval spec and placement sequencing are appropriate for initiatives (multi-doc, partitions). For small tweaks and bug fixes, a reminder in the single-spec doc keeps the process light and avoids overkill while still surfacing the need to run evals/benchmarks.

**Affects:** approach.md (initiatives); tweak.md and bug-fix.md (offer reminder when Building on AI + will do); emergence-config.json (eval_placement only for initiatives).

---

### ADR-5: Playbook as referenced asset (PDF or Markdown); recommend extraction for reliability

**Decision:** The LLMOps Experimentation playbook is referenced by path (e.g. initiative draft `loomhq-LLMOps_ Experimentation-....pdf` or a Markdown copy in the skill). Agents are instructed to use it when guiding eval-spec authoring. Recommend extracting the playbook to Markdown (e.g. in `emergence/playbooks/`) for token efficiency and stability; MVP can still reference a PDF in the draft folder.

**Rationale:** PDF is large and not ideal for full context; extracted Markdown gives consistent structure and lower token cost. Skill-owned playbook allows any project to use the same process without copying the file.

**Affects:** emergence/eval-spec.md (instructions for where to find playbook); optional new file emergence/playbooks/llmops-experimentation.md.

---

## Data Models

### Extended: emergence-config.json

**Current (existing):**
```json
{ "pace": "doc" }
```

**After this initiative (additive):**
```json
{
  "pace": "doc",
  "building_on_ai": true,
  "eval_status": "already_have | will_do",
  "eval_placement": "before_build | parallel"
}
```

- `building_on_ai`: `true` | `false`. Present only after the start-flow gate has been answered. If absent, treat as non–Building-on-AI (backward compatible).
- `eval_status`: `"already_have"` | `"will_do"`. Present only when `building_on_ai === true`. Omitted when `building_on_ai === false`.
- `eval_placement`: `"before_build"` | `"parallel"`. Present only for **initiatives** when `building_on_ai === true` and `eval_status === "will_do"`, and only after the Approach step has asked and the user answered. **Omitted for tweaks and bug fixes** (no Approach doc).

**Key field decisions:**
- String literals for `eval_status` and `eval_placement` to avoid boolean ambiguity and to allow future values (e.g. "defer") without schema change.
- No migration: existing files without these keys are valid; readers treat absent as "no Building on AI" / "no placement".

### New artifact: eval-spec.md

No formal schema. Content follows the structure of the eval spec template (problem, use case, hypothesis, scope, success criteria, metrics, data, methodology, model/resources, harness, timeline, results, exit criteria, wrap-up). Stored at:

- `.cicadas/drafts/{initiative}/eval-spec.md` (during emergence, before kickoff)
- If authoring were ever run after kickoff: `.cicadas/active/{initiative}/eval-spec.md` (promoted with other specs)

### Registry (optional, post-MVP)

If we later add display in `status.py` or elsewhere:

| Field | Type | When set |
|-------|------|----------|
| `building_on_ai` | boolean | At kickoff, from promoted emergence-config.json |
| `eval_status` | string | At kickoff, from promoted emergence-config.json |

No migration of existing registry entries; new fields optional.

---

## API & Interface Design

No new CLI commands or HTTP APIs. The only "contracts" are:

### Agent–config contract

- **Read:** Agents implementing start flow, Approach, or eval-spec authoring MUST read `emergence-config.json` from `.cicadas/drafts/{initiative}/` (or `.cicadas/active/{initiative}/` if running after kickoff). Path: `{project_root}/.cicadas/drafts/{initiative}/emergence-config.json`.
- **Write:** Start flow (or Clarify/Tweak/Bug entry) writes `building_on_ai` and, when true, `eval_status`. Approach step writes `eval_placement` when applicable. Use `load_json` / `save_json` pattern if a script is added later; for MVP, agents instruct the Builder to "ensure emergence-config.json contains …" or the agent edits the file (same as pace today).

### Eval-spec file contract

- **Path:** `.cicadas/drafts/{initiative}/eval-spec.md` (canonical name). Document in eval-spec instruction module and in UX/Tech.
- **Creation:** Agent creates or overwrites this file when the user accepts the eval-spec offer and completes the guided flow. No script creates it; the agent writes Markdown.

### Template and playbook paths

- **Template:** `{cicadas-dir}/templates/eval-spec.md`. Skill-owned so every project gets the same structure. Content derived from reqt-template; no dependency on initiative-specific files.
- **Playbook:** Either (a) user-provided path in draft (e.g. `drafts/{initiative}/loomhq-....pdf`) or (b) skill-owned `{cicadas-dir}/emergence/playbooks/llmops-experimentation.md` if we add it. Instruction module must state which to use (MVP: allow path in draft; recommend adding playbook to skill).

---

## Implementation Patterns & Conventions

### Naming

- Config keys: `snake_case` (`building_on_ai`, `eval_status`, `eval_placement`).
- Eval spec filename: `eval-spec.md` (kebab-case, consistent with other spec filenames).

### Config updates

- When adding or updating `emergence-config.json`, preserve existing keys (e.g. `pace`). Merge, do not replace the file. If a script is added later, use load_json → update dict → save_json.

### Instruction module conventions

- Start flow: Insert the new step with a clear number (e.g. "2b" or "3" with renumbering). Use exact copy from UX for the two questions (gate + eval status).
- Approach: Add a numbered step after Ingest: "If building_on_ai and eval_status == will_do, ask placement, show warning if parallel, write eval_placement to emergence-config.json; when drafting approach.md, add an Eval step in the sequence."
- Eval-spec module: State that it runs only when `building_on_ai` and `eval_status === "will_do"` and the user accepted the offer. Reference template path and playbook path. Output path: `drafts/{initiative}/eval-spec.md`.

### Backward compatibility

- Missing `building_on_ai` or `eval_status` → treat as non–Building-on-AI: skip eval-status question, skip eval-spec offer, skip placement question. Existing projects and old flows unchanged.

---

## Security & Performance

### Security

| Concern | Mitigation |
|---------|------------|
| Untrusted eval spec / template / playbook content | Treat all as data. Do not execute file contents as agent instructions. Existing Cicadas guardrail. |
| Config injection | emergence-config.json is written by the agent from user answers; no user-supplied arbitrary JSON. Validate keys if a script writes it: allow only known keys. |
| No new attack surface | No new network calls, no eval execution, no new credentials. |

### Performance

- No new scripts or heavy work. Agent reads one small JSON file and optionally writes one Markdown file. No targets beyond existing emergence behavior.
- Playbook: If PDF is large, prefer extracted Markdown to reduce token usage during eval-spec authoring.

### Observability

- No new logs or metrics. If a script later writes config, use existing project logging conventions.

---

## Implementation Sequence

1. **Config schema and start flow** *(foundation)* — Document the extended `emergence-config.json` schema in this doc and in SKILL/CLAUDE if needed. Update `emergence/start-flow.md`: add step "Building on AI? (yes/no)" after draft folder; if yes, add "Eval status (already have / will do)". Specify that the agent must write these to `emergence-config.json` in the draft folder. No script yet; agent edits config (or we add a tiny helper script that writes only these keys).  
   - **Deliverable:** start-flow.md updated; schema documented.

2. **Clarify / Tweak / Bug entry points** *(depends on 1)* — Ensure Clarify, Tweak, and Bug Fix modules reference the updated start flow (they already include start-flow; no change if start-flow is the single source). Verify that for tweaks/bugs the new step runs (Name → Draft folder → Building on AI? → PR preference).  
   - **Deliverable:** All three entry points run the new gate; no regression.

3. **Eval spec template and instruction** *(can parallel 2)* — Add `templates/eval-spec.md` (content from reqt-template or equivalent). Add `emergence/eval-spec.md` instruction module: when to run (after PRD/UX/Tech, when eval_status === "will_do", user accepted offer), template path, playbook path, output path, and the six-step playbook summary. Optionally add `emergence/playbooks/llmops-experimentation.md` (extract from PDF).  
   - **Deliverable:** Eval spec can be created by the agent; template and playbook referenced.

4. **Approach: placement question and eval step (initiatives only)** *(depends on 1)* — Update `emergence/approach.md`: after Lifecycle Check and Ingest, read `emergence-config.json`; if `building_on_ai` and `eval_status === "will_do"`, ask placement (before / parallel), show parallel warning, write `eval_placement` to config; when drafting `approach.md`, add an explicit "Eval" step in the sequence with wording that reflects before_build vs parallel. Update approach template if there is a standard place for this step.  
   - **Deliverable:** Approach includes eval step when applicable; placement and warning in place. Tweaks and bug fixes never run this step (no Approach doc).

5. **Tweak and Bug Fix: eval/benchmark reminder** *(depends on 1)* — Update `emergence/tweak.md` and `emergence/bug-fix.md`: when drafting the tweaklet or buglet, if `building_on_ai` and `eval_status === "will_do"`, offer to add an eval/benchmark reminder (one checklist task or short section) per UX copy. Do not offer the full eval-spec flow.  
   - **Deliverable:** Tweaks and bug fixes get the light touch only; no full eval spec, no placement question.

6. **Integration and docs** *(depends on 2, 3, 4, 5)* — Update SKILL.md (and any HOW-TO or README) to describe the Building on AI flow for initiatives (eval spec, placement) and for tweaks/bug fixes (reminder only). Ensure consistency check (if any) is aware of optional eval-spec.md.  
   - **Deliverable:** Docs and flow coherent; no script changes unless we add optional config writer.

**Parallel work:** (2) and (3) can proceed in parallel after (1). (4) depends on (1) only for config read/write. (5) can proceed in parallel with (2)–(4) once (1) is done.

**Known implementation risks:**
- **Playbook in PDF:** Large token cost and possible parsing issues. Mitigation: extract to Markdown in skill and reference that in the instruction module; MVP can still support PDF path in draft for this initiative.
- **Config write from agent:** If the agent edits JSON by hand, risk of broken JSON or overwriting `pace`. Mitigation: document merge semantics; consider a small script `write_emergence_config.py --building-on-ai true --eval-status will_do` that only sets these keys (optional for MVP).
