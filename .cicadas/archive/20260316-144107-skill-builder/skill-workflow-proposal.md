# Proposal: Agent Skills workflow in Cicadas

This document proposes a **top-level workflow** in Cicadas for creating, editing, evaluating, and tuning **Anthropic-compliant Agent Skills** from specs. The target format is the [Agent Skills specification](https://agentskills.io/specification); guidance is taken from [best practices](https://agentskills.io/skill-creation/best-practices), [optimizing descriptions](https://agentskills.io/skill-creation/optimizing-descriptions), and [using scripts](https://agentskills.io/skill-creation/using-scripts).

---

## 1. Scope and principles

- **Cicadas does not define the skill format.** We adopt the Agent Skills spec (SKILL.md with YAML frontmatter, optional `scripts/`, `references/`, `assets/`) as the single target format.
- **Same process as initiatives/tweaks/bugs.** Skills use the **same** draft → active flow and branch model: draft in `.cicadas/drafts/skill-{name}/`, kickoff promotes to `.cicadas/active/skill-{name}/` and creates `initiative/skill-{name}`, then `branch.py skill/{name} --initiative skill-{name}` creates the working branch `skill/{name}` (forking from default branch, like fix/ and tweak/). Work happens on `skill/{name}`; completion = merge to default branch, archive, no canon synthesis.
- **Dialogue-first, not form-fill.** The user describes what they want in plain language. The agent conducts a short clarifying conversation, then generates the complete skill — including the SKILL.md body, description, and any scripts — and presents it for review. The user never fills in a form.
- **Workflow follows Cicadas patterns:** instruction modules (emergence) for authoring, same CLI (kickoff, branch, status, archive, prune), templates for skill artifacts.
- **Evaluation and tuning** are part of the workflow: trigger-rate evals and (optionally) output-quality evals, with a train/validation split to avoid overfitting descriptions.

---

## 2. Where skills live (unified with initiatives/tweaks/bugs)

Skills use the **same** folders and flow as other work; the only difference is the branch prefix `skill/` and the artifact set (Agent Skill tree instead of prd/ux/tech/approach/tasks).

| Phase | Path | Branch |
|-------|------|--------|
| **Draft** | `.cicadas/drafts/skill-{name}/` | — |
| **Active** | `.cicadas/active/skill-{name}/` | `initiative/skill-{name}` (kickoff), then `skill/{name}` (branch.py; work done here) |

- **Naming:** Use a `skill-` prefix in the initiative name so draft/active dirs are `drafts/skill-xyz` and `active/skill-xyz`. The working branch is `skill/xyz` (slug only). Same idea as lightweight paths: the "initiative" is the container (e.g. `tweak-foo` → branch `tweak/foo`).
- **Registry:** Register the initiative as `skill-xyz` in `registry.json` under `initiatives`. The branch `skill/xyz` is registered under `branches` with `initiative: skill-xyz`. Treat `skill/` like `fix/` and `tweak/` in status, archive, prune, and abort.
- **No separate `skill-drafts/`.** One `drafts/` and one `active/` for all types.

---

## 3. Create

- **Trigger:** User says "create a skill," "start a new skill," "I want an Agent Skill for X," or simply describes what they want the skill to do in plain language.

### The dialogue-first model

The agent does **not** ask the user to fill in a form (name, description, fields, body). Instead it conducts a short conversation to understand intent, then **generates the complete skill** — SKILL.md frontmatter, body instructions, and any scripts or reference files — and presents it for review. The user only needs to describe what they want in plain language.

**Conversation shape (in `emergence/skill-create.md`):**

1. **Understand intent** — Ask a small number of open questions to understand:
   - What task or class of tasks should the skill handle?
   - What does the agent currently get wrong or miss without the skill?
   - Who/what is the target agent (Cursor, Claude Code, etc.)?
   - Are there special tools, APIs, project conventions, or domain knowledge the agent wouldn't know on its own?

2. **Clarify scope** — Based on the answers, surface boundaries:
   - What should the skill *not* do?
   - Are there near-miss cases that look similar but shouldn't trigger the skill?

3. **Draft the full skill** — Generate a complete, spec-compliant SKILL.md:
   - Derive a slug from the intent (lowercase, hyphens, 1–64 chars, matches dir name).
   - Write a `description` that is trigger-optimised: imperative phrasing, user-intent framing, explicit "even if they don't say X" coverage, and precise near-miss exclusions so it doesn't over-trigger.
   - Write the body: stepwise instructions, concrete examples, edge cases — grounded in what the agent *wouldn't know on its own*, not generic best-practice prose.
   - Add `scripts/`, `references/`, or `assets/` if the intent clearly needs bundled logic or reference docs; otherwise omit them.

4. **Present for review** — Show the full draft to the Builder. Walk through the description and the body instructions. Ask: "Does this capture what you meant? Anything missing or over-specified?"

5. **Iterate** — Revise based on feedback. Repeat until the Builder approves.

6. **Write and register:**
   - Write the approved skill tree to `.cicadas/drafts/skill-{slug}/`.
   - Run `kickoff.py skill-{slug} --intent "..."` → promotes to `active/skill-{slug}/`, creates `initiative/skill-{slug}`.
   - Run `branch.py skill/{slug} --intent "..." --initiative skill-{slug}` → creates working branch `skill/{slug}` (parent = default branch, like fix/tweak).
   - Validate: `validate_skill.py skill-{slug}`.

**Template:** `templates/skill-SKILL.md` is a minimal scaffold (frontmatter + section stubs) used only as a writing aid, not exposed to the user.

---

## 4. Edit

- **Trigger:** "Edit skill X," "Update the skill description," "Add a script to skill X," or any plain-language change request against an existing skill.
- **Process:**
  1. Resolve skill: `.cicadas/active/skill-{name}/` (or `drafts/skill-{name}/` if not yet kicked off), with work on branch `skill/{name}` when active.
  2. **Dialogue:** Understand what the user wants changed and why. For description changes, surface whether the issue is under-triggering (too narrow) or over-triggering (too broad) and revise accordingly.
  3. Agent edits SKILL.md and/or files under scripts/, references/, assets/ following best practices (progressive disclosure, procedures over declarations, etc.).
  4. **Validate** after edits (see §7).

---

## 5. Evaluate

Two evaluation modes, both optional but recommended before publishing or tuning.

### 5.1 Trigger-rate evaluation (description tuning)

- **Purpose:** Ensure the skill's `description` triggers when it should and does not trigger when it shouldn't ([optimizing descriptions](https://agentskills.io/skill-creation/optimizing-descriptions)).
- **Artifact:** `eval_queries.json` in the skill dir (e.g. `.cicadas/active/skill-{name}/eval_queries.json`):
  - Array of `{ "query": "...", "should_trigger": true|false }`.
  - ~20 queries: ~8–10 should-trigger, ~8–10 should-not-trigger (including near-misses).
  - The agent can **draft these queries** as part of the create or tune conversation — it already knows the intended trigger cases and the near-miss exclusions from the dialogue in §3.
- **Process:**
  - Run each query through the agent N times (e.g. 3), record whether the skill was invoked.
  - Compute trigger rate per query. Pass = should-trigger rate > 0.5; should-not-trigger rate < 0.5.
- **Train/validation split:** For tuning, split queries into train (~60%) and validation (~40%); use train to guide description revisions, validation to select the best iteration.

Cicadas provides the workflow and `eval_queries.json` format. The actual "run agent and detect trigger" step is host-specific (Cursor, Claude Code, etc.).

### 5.2 Output-quality evaluation

- **Purpose:** Grade that the skill's instructions produce good outputs.
- **Artifact:** Test cases in `.cicadas/active/skill-{name}/eval_cases.json` or `references/eval_cases.md` — input prompts + expected criteria or rubrics.
- **Process:** Host-dependent execution; Cicadas defines the structure and the `skill-evaluate.md` instruction module guides the agent through interpreting results and iterating.

---

## 6. Tune

- **Trigger:** "Tune skill X," "The skill isn't triggering," "It's triggering too often," or any plain-language description of a mismatch.
- **Dialogue:** Before running the eval loop, the agent asks: Is the problem under-triggering, over-triggering, or wrong output? Uses the answer to focus the iteration.
- **Description tuning loop:**
  1. **Evaluate** trigger rates on train and validation sets.
  2. **Identify failures** on the **train** set only.
  3. **Revise** the `description` — broaden if missing triggers, narrow if false triggers; generalise rather than keyword-stuff.
  4. **Re-run evaluation** on both sets.
  5. **Repeat** until train set passes or improvement plateaus; **select best by validation pass rate** (not necessarily the last iteration).
- **Output-quality tuning:** Same loop: run output evals → identify failures → revise instructions/scripts → re-run.

The `emergence/skill-tune.md` instruction module encapsulates this loop with the optimizing-descriptions guidance embedded so the agent doesn't need to fetch external URLs.

---

## 7. Scripts and CLI surface

Skills use the **same** scripts as initiatives/tweaks: `kickoff.py`, `branch.py`, `status.py`, `archive.py`, `prune.py`, `abort.py`. The only additions are validation and optional publish.

| Script | Purpose |
|--------|---------|
| `kickoff.py` | Same as today. Use name `skill-{slug}`; creates `initiative/skill-{slug}` and promotes `drafts/skill-{slug}` → `active/skill-{slug}`. |
| `branch.py` | **Change:** Treat `skill/` like `fix/` and `tweak/`: when `name.startswith("skill/")`, parent = default branch. |
| `validate_skill.py` | Validate a skill dir against the Agent Skills spec (frontmatter present, `name` matches dir and charset/length, `description` ≤ 1024 chars). Exit 0/1. |
| (Optional) `skill_publish.py` | Copy or symlink `active/skill-{name}` to configured output dir (e.g. `.agents/skills/{name}`) for agent consumption. |

**CLI examples:**

```bash
# After create dialogue: draft written, now register
python scripts/kickoff.py skill-pdf-utils --intent "PDF text extraction and form fill"
python scripts/branch.py skill/pdf-utils --intent "..." --initiative skill-pdf-utils

# Validate active skill
python scripts/validate_skill.py pdf-utils
# or by path
python scripts/validate_skill.py .cicadas/active/skill-pdf-utils

# Publish to agent dir (if implemented)
python scripts/skill_publish.py pdf-utils
```

---

## 8. Emergence / instruction modules

| Module | Purpose |
|--------|---------|
| **skill-create.md** | Full dialogue-driven create flow: understand intent → clarify scope → draft complete skill (frontmatter + body + scripts/references) → review → iterate → write and register. Embeds Agent Skills spec constraints and best-practice writing guidance so the agent produces well-calibrated descriptions and clear instructions without re-fetching external docs. |
| **skill-edit.md** | Dialogue-driven edit: understand the change request → edit `active/skill-{name}/` on branch `skill/{name}` → validate. |
| **skill-evaluate.md** | How to draft `eval_queries.json`, run trigger-rate and output evals, interpret results, and apply the train/validation split. |
| **skill-tune.md** | Tune loop: dialogue to identify the mismatch type → evaluate on train set → revise description/instructions → re-evaluate → select best by validation pass rate. |

All modules inline the key spec constraints (name rules, description ≤ 1024 chars, progressive disclosure) and best-practice bullets so the agent doesn't need to fetch external URLs during a session.

---

## 9. SKILL.md and docs updates

- **Cicadas SKILL.md:** Add a **Skills** section under Operations. Triggers: "create a skill," "start a skill," "build a skill for X," "edit skill X," "tune skill X," "skill isn't triggering." Entry point = read `emergence/skill-create.md`.
- **README / HOW-TO / CLAUDE.md:** Short mention that Cicadas can generate and tune Agent Skills via a dialogue-driven workflow, and link to the skill-create emergence module.

---

## 10. Implementation order (suggested)

1. **branch.py** — Add `skill/` to lightweight prefixes so `name.startswith("skill/")` uses parent = default branch (like fix/tweak). No new dirs needed.
2. **status.py, archive.py, prune.py, abort.py** — Treat `skill/` like `fix/` and `tweak/` where relevant.
3. **`emergence/skill-create.md`** and **`templates/skill-SKILL.md`** — The dialogue-driven create flow; update Cicadas SKILL.md triggers.
4. **`validate_skill.py`** — Spec checks (frontmatter, name, description); wire into skill-create.md end step and skill-edit.md.
5. **`skill_publish.py`** (optional) — Publish active skill to configurable output dir.
6. **`emergence/skill-evaluate.md`** and **`emergence/skill-tune.md`** — Eval and tune flows with `eval_queries.json` format defined.

---

## 11. References

- [Agent Skills specification](https://agentskills.io/specification)
- [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices)
- [Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions)
- [Using scripts in skills](https://agentskills.io/skill-creation/using-scripts)
- [skills-ref validate](https://github.com/agentskills/agentskills/tree/main/skills-ref) (optional validator)

---

_Copyright 2026 Cicadas Contributors_  
_SPDX-License-Identifier: Apache-2.0_
