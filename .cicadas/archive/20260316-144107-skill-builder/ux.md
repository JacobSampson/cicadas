
---
next_section: 'done'
---

# UX Design: skill-builder

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

**Primary goal:** The Builder should feel like they're talking to a knowledgeable colleague who happens to know the Agent Skills spec by heart — not filling in a form or running a wizard. The experience should feel like the agent already understands what the Builder wants and is asking the minimum number of questions needed to get it right. The output (the generated SKILL.md) should feel considered and complete, not mechanically assembled.

**Design constraints:**
- **CLI / agent conversation only** — all interaction is through the agent's chat interface (Cursor, Claude Code, etc.). No visual UI.
- **Extends existing Cicadas conversation patterns** — the start flow, Q&A pace, elicitation menu, and "stop for Builder review" gates are already established conventions. Skill Builder follows them rather than inventing new ones.
- **Agent writes files; Builder reviews** — the agent produces all artifacts; the Builder's job is to read, react, and approve. No manual file editing by the Builder.

---

## User Journeys & Touchpoints

### The Builder — "I want to create a new skill"

**Entry point:** Types a natural-language trigger: "create a skill for X," "I want an agent skill that does Y," "start a skill," etc.

**First touchpoint:** The standard Cicadas start flow — name, draft folder, publish destination. These questions are quick and familiar; the Builder recognises the pattern from starting tweaks and bugs.

**Key moment:** The agent presents the first complete draft of SKILL.md — description + body — in a single response. The Builder reads it and immediately knows whether the agent understood their intent. This is the moment of first value.

**Exit state:** The Builder has an approved, validated skill in `.cicadas/active/skill-{name}/` on branch `skill/{name}`, and knows exactly where it will be published when the branch is merged.

**Pain points to design around:**
- Builder describes a vague intent → agent asks too many questions → conversation feels like a form. Mitigation: ask 3–4 targeted questions max, then commit to a draft and iterate.
- Agent produces a generic, best-practice description that doesn't match the project's actual trigger cases. Mitigation: the clarifying questions specifically target project-specific knowledge and near-miss exclusions.
- Builder doesn't know what "near-miss" means. Mitigation: the agent explains by example ("e.g., queries that mention CSV but are actually asking about database ETL — those should NOT trigger this skill").

---

### The Builder — "My skill isn't triggering reliably" _(Post-MVP)_

> **Post-MVP (v2).** Requires `skill-evaluate.md` and `skill-tune.md`, which are out of scope for this initiative. Documented here as the intended future experience.

**Entry point:** Types "tune skill X," "the skill isn't triggering," or similar.

**First touchpoint:** Agent asks one diagnostic question (under-triggering / over-triggering / wrong output).

**Key moment:** Agent proposes a specific, rationale-backed revision to the description.

**Exit state:** Updated description, validated, with reasoning visible in conversation.

**Pain points to design around:** Builder doesn't know Agent Skills vocabulary; agent over-rewrites when only the description needs tweaking.

---

## Information Architecture

This initiative is entirely conversational — there is no nav structure. The "architecture" is the sequence of conversation states the Builder passes through.

```
Skill Builder conversation states
├── Start flow
│   ├── Name confirmation
│   ├── Draft folder creation
│   ├── Publish destination (NEW)
│   └── [Standard: building_on_ai, PR preference]
├── Create flow (skill-create.md)
│   ├── Clarifying questions (3–4 max)
│   ├── Draft generation
│   ├── Review & iteration loop
│   └── Write + register + validate
├── Edit flow (skill-edit.md)
│   ├── Diagnostic question
│   ├── Targeted edit
│   └── Validate + present
├── Evaluate flow (skill-evaluate.md) [Post-MVP]
│   ├── Draft eval_queries.json
│   ├── Run / interpret results
│   └── Report pass/fail
└── Tune flow (skill-tune.md) [Post-MVP]
    ├── Diagnostic (under / over / wrong output)
    ├── Train/val split
    ├── Revision loop
    └── Select by validation pass rate
```

The Builder never navigates this structure manually — the agent drives transitions between states.

---

## Key User Flows

### Flow 1: Create a new skill (happy path)

1. Builder: "create a skill that handles our database migration runbook"
2. Agent: confirms name (`db-migrations`), creates draft folder. Asks publish destination — detects `.agents/skills/` exists, offers it as default.
3. Builder: confirms publish destination.
4. Agent: asks 3–4 clarifying questions in a single message:
   - "What does the agent currently get wrong without this skill?"
   - "Any project-specific commands, conventions, or schema details the agent wouldn't know on its own?"
   - "What should this skill NOT do? (e.g., are there similar-sounding tasks that shouldn't trigger it?)"
5. Builder: answers in natural language.
6. Agent: drafts complete SKILL.md — description + body — and presents it in full. If bundled `scripts/`, `references/`, or `assets/` were identified during the questions, presents each one separately with a one-sentence rationale ("Since you mentioned running `migrate.sh`, here's a bundled wrapper:"). Asks: "Does this capture what you meant?"
7. Builder: "The description looks right but add a note about the `--dry-run` flag in the migration step."
8. Agent: revises the body, re-presents the affected section. Asks for approval.
9. Builder: "Approved."
10. Agent: writes skill tree to `drafts/skill-db-migrations/`, runs kickoff, runs branch, runs validate. Reports: "✓ skill/db-migrations created and validated. Will publish to `.agents/skills/db-migrations` when the branch is merged."

**Alternate path — validation failure:**
After step 10, `validate_skill.py` reports a name violation (e.g. slug derived contains uppercase). Agent fixes the slug, re-runs validate, reports success.

**Alternate path — Builder rejects draft entirely:**
At step 7, Builder says "this isn't right at all — it should be about X not Y." Agent acknowledges, asks one follow-up question to reorient, re-drafts from scratch.

---

### Flow 2: Edit an existing skill

1. Builder: "edit skill db-migrations — it's triggering too often"
2. Agent: "Got it — over-triggering. I'll look at the description's scope." Reads `active/skill-db-migrations/SKILL.md`.
3. Agent: "The description currently includes 'even if they mention database scripts generally.' That's likely catching too much. Proposed change: [shows before/after of description only]."
4. Builder: "Yes, do that."
5. Agent: edits SKILL.md, runs validate, reports: "✓ Updated and valid."

---

### Flow 3: Start flow — publish destination question

This question is inserted into the existing start flow after "Building on AI?" (or after draft folder for skills, since there's no "requirements source" or "pace" question).

1. Agent detects `.agents/skills/` exists in project root.
2. Agent: "Where should the finished skill be published when the branch is merged?
   1. `.agents/skills/db-migrations` ← detected
   2. `.claude/skills/db-migrations`
   3. Enter a custom path
   4. Don't publish (I'll install manually)"
3. Builder: "1"
4. Agent: writes `publish_dir: ".agents/skills"` to `emergence-config.json`. Continues start flow.

---

## UI States

This is a conversational interface. "States" are the distinct phases of the conversation with their expected agent behaviour.

### Create flow states

| State | Trigger | Agent behaviour |
|-------|---------|----------------|
| **Waiting for intent** | Create trigger phrase received | Confirms name, creates draft folder, asks publish destination |
| **Clarifying** | Draft folder created, publish set | Asks 3–4 questions in a single message; waits for Builder response |
| **Drafting** | Builder answered questions | Generates complete SKILL.md; presents in full with any proposed bundled files (scripts/references/assets) shown separately with rationale; asks for approval |
| **Iterating** | Builder requests changes | Applies targeted changes; re-presents affected sections; asks for approval |
| **Writing** | Builder approves draft | Writes files, runs kickoff + branch + validate; reports outcome |
| **Validation error** | `validate_skill.py` exits 1 | Reports specific violation(s), fixes autonomously if unambiguous (e.g. slug casing), re-validates, reports |
| **Done** | Validate exits 0 | Summarises: skill name, branch, publish destination, next step ("merge `skill/{name}` to publish") |

### Edit flow states

| State | Trigger | Agent behaviour |
|-------|---------|----------------|
| **Diagnosing** | Edit trigger received | Asks: under-triggering / over-triggering / wrong output — one question only |
| **Proposing** | Diagnosis given | Reads SKILL.md, proposes minimum change with before/after; asks for approval |
| **Applying** | Builder approves | Edits file, runs validate, reports |
| **Done** | Validate exits 0 | Confirms change applied; offers to draft updated eval queries if they exist |

---

## Copy & Tone

**Voice:** Direct, technically precise, and collegial — like a senior engineer who knows the spec and gets to the point. No cheerfulness or filler ("Great!", "Sure thing!"). No hedging ("I think maybe"). Confidence without arrogance — state what the agent is doing, then do it.

**Key principles:**
- Never ask the Builder to fill in a field — the agent fills fields, the Builder approves them.
- Frame clarifying questions as "things the agent needs to know to get this right," not "form fields."
- Use concrete examples to illustrate abstract concepts (near-miss, under-triggering).
- Report outcomes with specific paths and next steps, not vague confirmations.

**Critical copy samples:**

| Context | Copy |
|---------|------|
| Clarifying questions opener | `"A few things that will help me get this right:"` |
| Near-miss explanation | `"Are there similar-sounding tasks that should NOT trigger this skill? (e.g., queries about CSV that are actually asking about database ETL)"` |
| Draft presentation opener | `"Here's the complete skill draft. Read through the description and instructions — I'll revise anything that doesn't match your intent."` |
| Approval prompt | `"Does this capture what you meant? Anything to adjust?"` |
| Bundled file proposal | `"Since you mentioned {signal}, I'd bundle a {scripts\|references\|assets} file: [shows content]. Does this match what you meant?"` |
| Validation success | `"✓ skill/{name} created and validated. Will publish to {publish_dir}/{name}/ when skill/{name} is merged."` |
| Validation error | `"✗ Validation failed: {specific error}. Fixing now…"` |
| Publish destination prompt | `"Where should the finished skill be published when the branch is merged?"` |
| Edit diagnostic | `"Is the problem: (a) the skill isn't triggering when it should, (b) it's triggering when it shouldn't, or (c) it triggers but produces wrong output?"` |

---

## Visual Design Direction

**N/A — agent conversation interface only.** No visual design decisions are in scope. The rendered output is plain Markdown in whatever chat UI the agent is running in (Cursor, Claude Code, etc.).

The one "visual" consideration: SKILL.md drafts should be presented as code-fenced Markdown so the Builder can read the exact file content, not a prose summary of it.

---

## UX Consistency Patterns

### Question patterns
- **Single-message multi-question:** When multiple clarifying questions are needed, ask them all in one message as a numbered list. Do not drip questions one at a time — it elongates the conversation unnecessarily.
- **Binary diagnostic:** For edit/tune entry, ask one diagnostic question with lettered options. Never open-ended at this stage.
- **Numbered options for choices:** Publish destination, PR preference, etc. — always numbered so the Builder can reply with just a digit.

### Output presentation patterns
- **Show the whole artifact:** When presenting a SKILL.md draft, show the complete file (frontmatter + body), not a summary. The Builder needs to see exactly what will be written.
- **Before/after for edits:** When proposing a change to an existing skill, show the before/after of the specific section being changed, not a full re-print of the file.
- **Structured outcome report:** At completion, always report: artifact created, branch name, publish destination, and the one next action the Builder needs to take.

### Iteration patterns
- **Targeted revision, not full rewrite:** When the Builder requests changes, change only what they asked for. Re-present only the affected section.
- **Hard stop at approval gates:** After presenting a draft or a revision, always wait for explicit Builder approval before writing any files. Never auto-proceed.

### Error patterns
- **Self-correct on unambiguous errors:** Validation errors that have one obvious fix (e.g., slug contains uppercase → lowercase it) should be fixed autonomously and reported, not escalated to the Builder.
- **Escalate ambiguous errors:** If the fix requires a judgment call (e.g., the name conflicts with an existing skill), surface it to the Builder with the specific tradeoff.

---

## Responsive & Accessibility

**N/A — CLI / agent conversation only.** No breakpoints or accessibility standards apply to the agent conversation interface itself. SKILL.md output files are plain text and are inherently accessible.

