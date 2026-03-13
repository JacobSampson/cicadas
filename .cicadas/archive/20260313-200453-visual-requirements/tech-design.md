
---
next_section: ''
---

# Tech Design: visual-requirements

## Progress

- [x] Overview & Context
- [x] Tech Stack & Dependencies
- [x] Project / Module Structure
- [x] Architecture Decisions (ADRs)
- [x] Data Models
- [x] API & Interface Design
- [x] Implementation Patterns & Conventions
- [x] Security & Performance
- [x] Implementation Sequence

---

## Overview & Context

**Summary:** This initiative is implemented entirely as changes to **agent instructions** (Emergence subagent prompts). There are no new CLI scripts, no new Python modules, and no new runtime dependencies. The Clarify subagent (`emergence/clarify.md`) gains a single new step (Intake) that branches on Builder choice (Q&A / Doc / Loom). For Doc and Loom, the agent reads from well-defined file paths under `.cicadas/drafts/{initiative}/` and fills the PRD from that content. The only "architecture" is: (1) one place for intake logic (clarify.md), (2) two optional, convention-based file names in drafts (loom.md, requirements.md), (3) optional documentation of those conventions in EMERGENCE.md or SKILL so they are discoverable.

### Cross-Cutting Concerns

1. **Single source of truth for intake** — All intake behavior (prompt text, options, instructions, file paths) lives in `clarify.md`. No duplicate logic in scripts or other emergence docs.
2. **Drafts are user-owned** — `drafts/{initiative}/` is already a staging area; loom.md and requirements.md are optional user-provided files. No schema or validation; content is opaque to the system and only consumed by the agent when filling the PRD.
3. **No script dependency** — Scripts (kickoff, branch, init, etc.) do not read or validate loom.md or requirements.md. They continue to operate on the same drafts/active/archive layout; the new files are simply additional optional files that may appear in a draft folder.

### Brownfield Notes

- **Touch:** `src/cicadas/emergence/clarify.md` only (required). Optionally: `src/cicadas/emergence/EMERGENCE.md` or `src/cicadas/SKILL.md` for discoverability of file conventions.
- **Do not change:** Any script in `scripts/`, registry schema, or canon layout. Existing emergence flow (pace, Process Preview, Ingest, Canon Check, Initialize, Iterative Drafting, Finalize) remains; we only insert step 0.5 and branch the subsequent behavior.
- **Follow:** Existing pattern of step-by-step instructions in clarify.md and use of `{initiative}` placeholder where the agent substitutes the actual initiative name.

---

## Tech Stack & Dependencies

| Category | Selection | Rationale |
|----------|-----------|-----------|
| **Language/Runtime** | N/A (no new code) | Implementation is markdown instructions only. |
| **Framework** | N/A | — |
| **Key Libraries** | None | — |

**New dependencies introduced:** None.

**Dependencies explicitly rejected:** N/A.

---

## Project / Module Structure

No new modules or files are required beyond editing existing ones. Only the following are modified or referenced:

```
src/cicadas/
├── emergence/
│   ├── clarify.md          # [MODIFIED] Add step 0.5 Intake; Q/D/L branches; Loom instructions; Doc/Loom fill behavior
│   └── EMERGENCE.md        # [OPTIONAL] Add one line or short subsection referencing intake options and file paths (loom.md, requirements.md)
└── SKILL.md                # [OPTIONAL] Mention "requirements via Loom or doc" and paths in Emergence or CLI Quick Reference context
```

**.cicadas/drafts/{initiative}/** (existing directory; no script changes):

- **loom.md** — Optional. Present only when Builder chooses Loom and pastes transcript. Agent reads once to fill PRD.
- **requirements.md** — Optional. Present only when Builder chooses Doc and places their doc here. Agent reads once to fill PRD.

**Key structural decisions:**

- Intake logic lives only in `clarify.md` so that any agent or environment running Clarify has one place to look.
- File names are fixed in the instructions (loom.md, requirements.md) to avoid ambiguity; alternate paths can be "agreed" in conversation (e.g. brief.md) but the default is documented.

---

## Architecture Decisions (ADRs)

### ADR-1: Intake implemented in Clarify instructions only (no new script)

**Decision:** All intake behavior — the question, the three branches, the Loom instructions text, and the "read file and fill PRD" behavior — is specified in `emergence/clarify.md`. No new Python (or other) script is added to read loom.md or requirements.md or to perform the intake prompt.

**Rationale:** The actor that runs Clarify is an LLM agent; the natural place for "ask this, then do that" is the subagent prompt. A script would not improve the flow (the agent still has to show instructions and wait for the user); it would add a second place to maintain and a dependency from agent to script for no clear benefit. Keeping everything in clarify.md preserves single-source truth and matches how other emergence steps (e.g. pace, Process Preview) already work.

**Affects:** `emergence/clarify.md` only.

---

### ADR-2: Convention-based file names in drafts; no schema or validation

**Decision:** The paths `drafts/{initiative}/loom.md` and `drafts/{initiative}/requirements.md` are conventions documented in the Clarify instructions. There is no schema, no validation, and no script that reads or writes these files. The agent reads the file when the Builder confirms it is in place; content is free-form text used to populate the PRD.

**Rationale:** Loom transcripts and stakeholder docs vary widely in format. Defining a schema would be brittle and would not add value for the MVP. The agent's job is to infer PRD structure from the content. Validation would require either a script (rejected per ADR-1) or agent-side checks that duplicate the "fill and present for review" step. Keeping these as opaque user files minimizes scope and matches the existing drafts model (user-owned staging).

**Affects:** `clarify.md` (documentation of paths and behavior); optional EMERGENCE.md/SKILL.md mention.

---

### ADR-3: No Loom API or transcript fetch in MVP

**Decision:** We do not call any Loom API or automatically fetch a transcript from a URL. The Builder records in Loom, copies the transcript manually, and pastes it into loom.md.

**Rationale:** MVP scope is "instructions + file convention + agent fills PRD." Adding an API dependency (Loom or similar) would introduce auth, rate limits, and failure modes. Manual copy-paste is sufficient for v1 and keeps the implementation agent-only.

**Affects:** Clarify instructions (they direct the user to copy transcript and save to loom.md); no code.

---

## Data Models

No new data models. The files `loom.md` and `requirements.md` are plain text (typically markdown); they are not parsed into structured JSON or any internal schema. They are read as a single blob by the agent for the purpose of drafting PRD sections.

**Schema / Migration Notes:** N/A.

---

## API & Interface Design

No new API, CLI, or programmatic interface. The only "contract" is between the Builder and the agent:

- **Intake choice:** Builder replies with one of Q, D, or L (or equivalent phrasing).
- **Doc path:** Builder places a file at the path specified by the agent (default `drafts/{initiative}/requirements.md`) and confirms.
- **Loom path:** Builder places the transcript at `drafts/{initiative}/loom.md` and confirms.

**Backward compatibility:** Existing users who never run Clarify with the new instructions see no change. Users who run Clarify see one additional question (intake) before the existing flow; choosing [Q] preserves previous behavior.

---

## Implementation Patterns & Conventions

### Naming Conventions

| Construct | Convention | Example |
|-----------|-----------|---------|
| File paths in instructions | Literal, with `{initiative}` placeholder | `.cicadas/drafts/{initiative}/loom.md` |
| Option labels in prompt | Short letter + word | `[Q] Q&A`, `[D] Doc`, `[L] Loom` |

### Instruction Text

- Use the exact copy specified in the UX doc (and PRD) for the intake question and Loom steps 4–5 so that Builder-facing text is consistent and testable.
- When the agent waits for a file, the instructions must explicitly say to "reply when done" or "confirm when the file is in place" so the agent does not proceed until the Builder confirms.

### Testing

- No new unit tests for scripts (no script changes). Manual or agent-driven test: run Clarify for a test initiative, choose each of Q/D/L, and for D/L verify the agent waits for the file and then fills the PRD from it. Optionally add a test that parses clarify.md and asserts the presence of "Intake", "loom.md", and "requirements.md" so regressions in the instructions are caught.

---

## Security & Performance

### Security

| Concern | Mitigation |
|---------|------------|
| User content in drafts | loom.md and requirements.md are under .cicadas/drafts/; same trust model as existing draft specs. No execution of content; agent only reads as text. |
| Secrets in transcript/doc | No special handling. Builder is responsible for not pasting secrets; drafts are typically not committed or are in a private repo. |
| Path traversal | Agent and scripts use fixed path patterns (`drafts/{initiative}/loom.md`). Initiative name is already validated by existing flows (e.g. kickoff). |

### Performance

No new runtime behavior; agent reads one file when Doc or Loom is chosen. File size is assumed to be reasonable (transcript or short doc). No targets added.

### Observability

None. No new logging or metrics.

---

## Implementation Sequence

1. **Clarify instructions** *(done)* — Step 0.5 Intake and Q/D/L branches with Loom instructions and Doc/Loom fill behavior are already in `clarify.md`. No further code change required for MVP.
2. **Optional documentation** — Add a short mention of intake options and file conventions to `EMERGENCE.md` and/or `SKILL.md` so Builders and agents discover loom.md and requirements.md without reading clarify.md. Order: after verifying the clarify.md flow in a dry run or test.
3. **Verification** — Run through Clarify once for a test initiative with [Q], [D], and [L] (e.g. create test drafts with sample loom.md and requirements.md) to confirm behavior and copy.

**Parallel work:** N/A; single-doc change.

**Known implementation risks:** None. The only risk is instruction ambiguity (e.g. agent not waiting for file); the UX doc and clarify.md text are written to make the wait explicit.
