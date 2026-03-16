
---
next_section: 'done'
---

# PRD: skill-builder

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

Cicadas Skill Builder adds a first-class, dialogue-driven workflow for creating, editing, evaluating, and tuning **Agent Skills** (compliant with the [agentskills.io specification](https://agentskills.io/specification)) directly within the Cicadas lifecycle. A Builder describes what they want a skill to do in plain language; Cicadas conducts a short clarifying conversation, generates the complete `SKILL.md` (frontmatter, body, optional scripts/references), and presents it for review — no form-filling required. The workflow reuses the existing draft → active → branch → archive infrastructure so skills are first-class tracked artifacts alongside initiatives, tweaks, and bug fixes.

### What Makes This Special

- **Dialogue-first authoring** — the Builder speaks plain language; the agent produces spec-compliant SKILL.md bodies with trigger-optimised descriptions, not the user.
- **Unified lifecycle** — skills live in `.cicadas/drafts/skill-{name}/` and `.cicadas/active/skill-{name}/` on `skill/{name}` branches, reusing every existing Cicadas script and convention without special-casing.
- **First-class publish destination** — the start flow asks where the finished skill should live (detected from existing project conventions; stored in `emergence-config.json`); the skill is published automatically at completion.
- **Built-in trigger evaluation and tuning** — `eval_queries.json` + instruction modules for testing whether a skill's description fires reliably, with a train/validation split to avoid overfitting.

---

## Project Classification

**Technical Type:** Developer Tool / Methodology Extension
**Domain:** Developer Productivity / AI-Augmented Engineering
**Complexity:** Medium — new emergence instruction modules + minor CLI changes + one new script; no new data stores or external dependencies.
**Project Context:** Brownfield — extends an existing Cicadas installation. Reuses all existing scripts, directory layout, and registry conventions.

---

## Success Criteria

### User Success

A user achieves success when they can:

1. **Describe a skill in plain language and receive a complete, spec-compliant SKILL.md draft** — measured by: draft is produced in a single conversation with no form-filling, passes `validate_skill.py`, and is approved by the Builder without structural rewrites.
2. **Edit or tune an existing skill with a plain-language request** — measured by: the agent understands the change, edits the right files, validates, and re-presents for approval without the Builder having to open SKILL.md directly.
3. **Know where the skill will be published before starting work** — measured by: publish destination is confirmed in the start flow and stored in `emergence-config.json`; `skill_publish.py` copies/symlinks to that path at completion with no manual steps.
4. **Know that `eval_queries.json` was drafted as part of skill creation so trigger behaviour can be spot-checked** — measured by: `eval_queries.json` with ~20 labelled queries (should-trigger + should-not-trigger) exists in `active/skill-{name}/` after the create flow completes. Evaluation and tuning workflows (`skill-evaluate.md`, `skill-tune.md`) are Post-MVP.

### Technical Success

The system is successful when:

1. `branch.py`, `status.py`, `archive.py`, `prune.py`, and `abort.py` handle `skill/` branches without errors using the same code paths as `fix/` and `tweak/`.
2. `validate_skill.py` correctly catches all name and description violations from the Agent Skills spec (bad charset, name mismatch, description > 1024 chars, missing frontmatter) and exits 0/1 cleanly.

### Measurable Outcomes

- A new skill (from conversation to valid `SKILL.md` in `drafts/skill-{name}/`) is produced in a single Cicadas session with no manual file editing by the Builder.
- `validate_skill.py` catches 100% of spec violations in unit tests covering name rules, description length, and missing frontmatter.
- `status.py` lists `skill/` branches in output alongside `fix/` and `tweak/` with no code changes to the caller.

---

## User Journeys

### Journey 1: The Builder — "I need an Agent Skill for my project"

A Builder is working on a project and finds themselves repeatedly correcting their AI agent on a specific task — say, how to run database migrations for their schema. They want to package that knowledge as a reusable skill so the agent gets it right automatically. They type "create a skill for running database migrations" into Cicadas. The agent asks a handful of targeted questions: what does the agent currently do wrong, what should it never do, what commands or conventions are project-specific? The agent then generates a complete `SKILL.md` with a well-phrased description and step-by-step instructions, presents it, and the Builder approves with minor tweaks. The skill is written to `.cicadas/drafts/skill-db-migrations/`, kicked off, and tracked like any other piece of work.

**Requirements Revealed:** dialogue-driven create flow, clarifying questions, complete SKILL.md generation, draft folder creation, kickoff + branch registration.

---

### Journey 2: The Builder — "My skill isn't triggering reliably" _(Post-MVP)_

> **Post-MVP (v2).** Requires `skill-evaluate.md` and `skill-tune.md`, which are out of scope for this initiative. Documented here as the intended future experience.

A Builder published a skill a week ago and notices it only fires about half the time on relevant queries. They tell Cicadas "tune skill db-migrations." The agent asks whether it's under-triggering, over-triggering, or producing wrong output. The Builder says "under-triggering." The agent opens the `eval_queries.json` in `active/skill-db-migrations/`, splits it into train and validation sets, identifies the failing should-trigger queries, and proposes a revised description that broadens the coverage without keyword-stuffing. It re-runs the mental evaluation and presents both the revised description and the rationale. The Builder approves, the file is updated, and the session ends with a measurably better description.

**Requirements Revealed (Post-MVP):** tune instruction module, train/validation split, description revision loop, guided dialogue for diagnosing mismatch type.

---

### Journey Requirements Summary

| User Type | Key Requirements |
|-----------|-----------------|
| **Builder (create)** | Dialogue intake, complete SKILL.md generation, draft folder, kickoff + branch, validate, eval_queries.json |
| **Builder (tune)** | _(Post-MVP)_ eval_queries.json, tune loop, train/val split, description revision, mismatch diagnosis |

---

## Scope

### MVP — Minimum Viable Product (v1)

**Core Deliverables:**
- `emergence/skill-create.md` — dialogue-driven create flow (understand intent → clarify scope → draft full skill → review → iterate → write + register). Includes publish-destination step and initial `eval_queries.json` draft.
- `templates/skill-SKILL.md` — minimal SKILL.md scaffold used internally by the agent.
- `scripts/validate_skill.py` — spec-compliance validator (frontmatter, name charset/length/dir-match, description ≤ 1024 chars). Exit 0/1.
- `scripts/skill_publish.py` — copy or symlink `active/skill-{name}` to the `publish_dir` stored in `emergence-config.json`. Called at skill completion. Skipped if `publish_dir` is null.
- `branch.py` change — treat `skill/` like `fix/` and `tweak/`: parent = default branch when `name.startswith("skill/")`.
- `status.py`, `archive.py`, `prune.py`, `abort.py` changes — include `skill/` in the same handling as `fix/` and `tweak/`.
- `emergence/skill-edit.md` — dialogue-driven edit: understand change → edit `active/skill-{name}/` on `skill/{name}` branch → validate.
- Cicadas `SKILL.md` updates — add **Skills** section under Operations with triggers: "create a skill," "start a skill," "build a skill for X," "edit skill X."

**Quality Gates:**
- `validate_skill.py` has unit tests covering all spec violation types (missing frontmatter, name mismatch, name charset, description over limit).
- `branch.py` integration test: `skill/xyz` forks from default branch (not `initiative/`).
- `skill-create.md` reviewed and approved by Builder before kickoff.

### Growth Features (Post-MVP)

**v2: Eval & Tune**
- `emergence/skill-evaluate.md` — draft `eval_queries.json`, run trigger-rate evals, interpret results, apply train/validation split.
- `emergence/skill-tune.md` — tune loop with mismatch-type diagnosis, description revision, validation pass-rate selection.
- `eval_queries.json` format documented in `templates/` or `emergence/skill-evaluate.md`.

**v3: Automation**
- Trigger-rate testing harness integrated with the host agent (Cursor, Claude Code) — current design leaves "run agent and detect trigger" host-specific; future work could provide a test harness.

### Vision (Future)

- Automated trigger-rate testing integrated with the host agent (Cursor, Claude Code) — current design leaves "run agent and detect trigger" host-specific; future work could provide a test harness.
- Skill versioning and changelog in the index.

---

## Functional Requirements

### 1. Skill Lifecycle (Branch & Registry)

**FR-1.1:** `branch.py` MUST treat `skill/` as a lightweight branch prefix. When `name.startswith("skill/")`, the parent branch MUST be the default branch (same behaviour as `fix/` and `tweak/`), not an initiative branch.
- Acceptance: `branch.py skill/xyz --intent "..." --initiative skill-xyz` creates `skill/xyz` from master/main without requiring `git checkout initiative/skill-xyz` first.

**FR-1.2:** `status.py` MUST list `skill/` branches in its output. They MUST appear grouped alongside or near `fix/` and `tweak/` branches, not under "feature branches."

**FR-1.3:** `archive.py` MUST archive a `skill-{name}` initiative using the same logic as `fix/` and `tweak/` initiatives. The archive dir name follows the same `{timestamp}-{name}` convention.

**FR-1.4:** `prune.py` MUST support pruning `skill-{name}` initiatives and `skill/{name}` branches with `--type initiative` and `--type branch` respectively.

**FR-1.5:** `abort.py` MUST recognise `skill/` as a lightweight branch prefix and handle abort from a `skill/` branch analogously to `fix/` and `tweak/`.

---

### 2. Skill Create — Dialogue Flow (`skill-create.md`)

**FR-2.1:** The `skill-create.md` instruction module MUST conduct a dialogue-driven intake. The agent MUST ask clarifying questions before generating any SKILL.md content — it MUST NOT present a form or ask the user to fill in fields directly.
- Minimum questions: (a) what task or class of tasks the skill should handle, (b) what the agent currently gets wrong without it, (c) any project-specific conventions, tools, or knowledge the agent wouldn't know on its own, (d) what the skill should NOT do / near-miss exclusions.

**FR-2.2:** After the dialogue, the agent MUST generate a **complete, spec-compliant SKILL.md** in a single pass:
- Frontmatter with `name` (slug derived from intent, lowercase hyphens, 1–64 chars, matching dir name), `description` (1–1024 chars, imperative, user-intent framing, near-miss exclusions), and optional fields if relevant (`license`, `compatibility`, `metadata`, `allowed-tools`).
- Body: stepwise instructions grounded in what the agent wouldn't know on its own; concrete examples; edge cases. No generic best-practice filler.
- During the clarifying dialogue, the agent MUST actively probe for bundling needs by recognising these signals:
  - **`scripts/`**: the skill needs the agent to *run* a command or executable (e.g. "the agent needs to run our validate script with specific flags") → propose a bundled script wrapper.
  - **`references/`**: there is a lookup table, schema, error code list, or internal doc the agent needs to consult (e.g. "there's an internal error code reference the agent always forgets") → propose a bundled reference file.
  - **`assets/`**: the skill uses a static template, data file, or config stub the agent should fill in (e.g. "there's a standard migration config template") → propose a bundled asset.
- When a bundling signal is detected, the agent MUST **propose the bundled content alongside the SKILL.md draft** — not add it silently. The proposal must show the file contents and ask "Does this match what you meant?" The Builder must explicitly approve any bundled files before they are written.
- If no bundling signals are detected, omit `scripts/`, `references/`, and `assets/` entirely.

**FR-2.3:** The agent MUST present the full draft to the Builder and ask for approval. It MUST iterate on feedback until the Builder explicitly approves.

**FR-2.4:** After approval, the agent MUST:
1. Write the skill tree to `.cicadas/drafts/skill-{slug}/`.
2. Run `kickoff.py skill-{slug} --intent "..."`.
3. Run `branch.py skill/{slug} --intent "..." --initiative skill-{slug}`.
4. Run `validate_skill.py skill-{slug}` and surface any violations to the Builder.

**FR-2.5:** The agent MUST also draft an initial `eval_queries.json` (8–10 should-trigger, 8–10 should-not-trigger including near-misses) as part of the create flow, using the intent and scope boundaries established in the dialogue. This file is written alongside SKILL.md at step FR-2.4.1.

**FR-2.6 — Publish destination (skill start flow step):** During the skill start flow, BEFORE the dialogue begins, the agent MUST ask where the finished skill should be published. Detection order:
1. Check `.cicadas/config.json` for an existing `skill_publish_dir` key — if present, offer it as the default.
2. Otherwise, detect existing skill dirs in the project root in this priority order: `.agents/skills/`, `.claude/skills/`, `src/`, `skills/`. Offer the first found as option 1.
3. Always include "Other (enter a path)" and "Don't publish (keep in `.cicadas/active/` only)" as options.

The chosen path is written to `.cicadas/drafts/skill-{slug}/emergence-config.json` as `publish_dir`. At completion (merge to default branch), the agent copies/symlinks `active/skill-{slug}/` to `{publish_dir}/{slug}/`. If `publish_dir` is `null` / "don't publish," this step is skipped.

---

### 3. Skill Edit (`skill-edit.md`)

**FR-3.1:** The `skill-edit.md` instruction module MUST resolve the skill path: `active/skill-{name}/` when on branch `skill/{name}`, or `drafts/skill-{name}/` if not yet kicked off.

**FR-3.2:** The agent MUST ask what the Builder wants changed and why before making any edits. For description changes, it MUST surface whether the issue is under-triggering or over-triggering and explain the revision strategy.

**FR-3.3:** After edits, the agent MUST run `validate_skill.py` and surface any violations before declaring the edit complete.

---

### 4. Skill Validation (`validate_skill.py`)

**FR-4.1:** `validate_skill.py` MUST accept either a slug (`pdf-utils` → resolves to `active/skill-pdf-utils/` or `drafts/skill-pdf-utils/`) or an explicit path.

**FR-4.2:** `validate_skill.py` MUST check and report on all of the following, exiting 1 if any fail:
- `SKILL.md` exists in the target dir.
- YAML frontmatter block is present (delimited by `---`).
- `name` field is present, non-empty, 1–64 chars, matches `[a-z0-9-]+`, does not start or end with `-`, contains no `--`.
- `name` field matches the directory name (for `active/skill-{name}/` → name must equal the part after `skill-`; for an explicit path → name must equal basename).
- `description` field is present, non-empty, ≤ 1024 chars.
- Exit 0 if all checks pass; exit 1 if any fail, with a human-readable error per violation.

---

### 5. SKILL.md and Docs Updates

**FR-5.1:** Cicadas `SKILL.md` MUST have a **Skills** section under Operations documenting: create, edit, validate, evaluate (post-MVP), tune (post-MVP). Triggers in the SKILL.md description or body MUST include: "create a skill," "start a skill," "build a skill for X," "edit skill X," "tune skill X," "skill isn't triggering."

**FR-5.2:** The branch hierarchy diagram in `SKILL.md` MUST include `skill/{name}` alongside `fix/{name}` and `tweak/{name}`.

**FR-5.3:** `templates/skill-SKILL.md` MUST be a minimal, valid SKILL.md scaffold (frontmatter placeholders + section stubs for Instructions, and optionally Scripts/References/Assets). It is used only as a writing aid by `skill-create.md`, not presented to the Builder.

---

## Non-Functional Requirements

- **Performance:** `validate_skill.py` MUST complete in < 1 second on any SKILL.md. No external network calls in the validator.
- **Reliability:** `validate_skill.py` MUST exit with a non-zero code and a clear error message for every spec violation; it MUST NOT silently pass an invalid skill. `skill-create.md` MUST call the validator after every write — a skill is never left in an unvalidated state.
- **Security:** `skill-create.md` and `skill-edit.md` MUST treat all user-provided content (dialogue answers, existing SKILL.md bodies) as data, not instructions, consistent with the existing Cicadas untrusted-input guardrail.
- **Maintainability:** New `skill/` handling in `branch.py`, `status.py`, etc. MUST be added by extending the existing `fix/tweak` prefix lists/conditionals, not duplicating logic. Target: each affected script requires ≤ 5 lines changed.

---

## Open Questions

- **`eval_queries.json` in create flow — opt-in or default?** FR-2.5 drafts eval queries as part of every create. Risk: bloats the conversation for simple skills. Proposal: default on, but the Builder can say "skip eval queries" to defer.
- **`skill/` in SKILL.md docs — separate subsection or extend Lightweight Paths?** Leaning towards extending Lightweight Paths with a note that `skill/` follows the same pattern; avoids a third parallel section for a closely related concept.

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `skill-create.md` dialogue generates poor descriptions that under-trigger | Med | Med | FR-2.1 mandates near-miss exclusion questions; FR-2.5 requires initial eval_queries.json so the Builder can immediately spot-check triggering. |
| Changes to `branch.py` / `status.py` break existing `fix/` and `tweak/` behaviour | Low | High | Each change adds `skill/` to an existing prefix check — minimal diff, covered by existing `test_branch.py` and `test_status.py` test files; add regression assertions for `skill/` in the same tests. |
| Agent Skills spec changes invalidate `validate_skill.py` | Low | Low | Spec constraints (name charset, description limit) are stable fundamentals; validator is a thin script that's easy to update. |
| Scope creep: Builder wants eval in MVP | Med | Med | Explicit Post-MVP classification in this PRD; defer if raised during implementation. |
| Publish destination detection finds no existing skill dirs, leaving Builder confused | Low | Med | FR-2.6 always offers "Other (enter a path)" and "Don't publish" as options; detection failure gracefully falls back to the options menu. |
