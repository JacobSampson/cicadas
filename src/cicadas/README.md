# Cicadas Orchestrator

Cicadas is a sustainable **spec-driven development** methodology designed for high-velocity, high-quality engineering. It treats specifications as disposable inputs and the codebase as the single source of truth.

## The Cicadas Philosophy

1.  **Disposable Active Specs**: PRDs, Tech Designs, and Task lists are "active" only during development. Once code is merged, they expire.
2.  **Code is Truth**: Documentation is reverse-engineered (synthesized) from the code, not maintained manually in parallel.
3.  **Partitioned Work**: Complex initiatives are sliced into independent, registered feature branches to minimize conflicts.
4.  **Continuous Reflection**: "Reflect" operations keep specs in sync with code reality during the inner loop of development.

---

## Directory Architecture

The system is split between the **Skill** (logic) and the **Institutional Memory** (data).

### 0. The Installer (`install.sh` — project root)
A portable bash script for zero-friction setup. Run once to download Cicadas, check Python 3.11+, initialize `.cicadas/`, and optionally wire up agent integrations (`claude-code`, `antigravity`, `cursor`, `rovodev`).

```bash
curl -fsSL https://raw.githubusercontent.com/ecodan/cicadas/master/install.sh | bash
bash install.sh --update   # refresh skill files without touching .cicadas/
```

### 1. The Skill Directory (`src/cicadas/`)
This is the orchestrator itself. It contains:
- `SKILL.md`: The agent manual and technical definition (includes "Implementation agent rules" so the same guardrails apply in Cursor, Claude Code, and other envs).
- `implementation.md`: Guardrails for implementation agents (pause before commit, Reflect, tasks, Code Review on feat/).
- `scripts/`: CLI tools for project lifecycle operations (kickoff, branch, status, create_lifecycle, open_pr, review, tokens, etc.).
- `emergence/`: Subagent instructions for the drafting phase. Includes `start-flow.md` — the mandatory sequence (name, draft folder, requirements source/pace, PR preference) run first for initiative, tweak, and bug.
- `templates/`: Standardized markdown templates for specs, canon, and per-initiative lifecycle (`lifecycle-default.json`, `lifecycle-schema.md`). `canon-summary.md` is the template for the 300–500 token agent-optimized codebase snapshot produced during synthesis.

### 2. The `.cicadas/` Directory
Located at your project root, this folder stores all project-specific state:
- `canon/`: The authoritative, synthesized documentation (Product, UX, and Tech overviews).
- `drafts/`: Staging area for new initiatives before they are officially "kicked off".
- `active/`: Live specs for work currently in progress.
- `archive/`: Evidence trail of expired specs from completed initiatives.
- `registry.json`: Global state tracking all active initiatives and branches.
- `index.json`: An append-only ledger of every significant change.

---

## The End-to-End Process

### 1. Emergence (Planning)
When starting an initiative, tweak, or bug, the agent runs the **standard start flow** first (see `emergence/start-flow.md`): name, draft folder, then (for initiatives) requirements source and pace, then PR preference. Vague ideas are refined into structured drafts in `.cicadas/drafts/{initiative}/`.
- **Clarify**: Define the "What & Why" (PRD). At Clarify start, the Builder can choose **Q&A** (interactive), **Doc** (place a file at `drafts/{initiative}/requirements.md`), or **Loom** (save transcript to `drafts/{initiative}/loom.md`); the agent fills the PRD from the doc or transcript.
- **UX**: Map the interaction and UI.
- **Tech**: Design the architecture.
- **Approach**: Slice the work into logical partitions (Feature Branches).
- **Tasks**: Create a testable checklist.
- **Lifecycle** (optional): Run `create_lifecycle.py` to add `lifecycle.json` with PR boundaries and steps; promoted to active at kickoff.

### 2. Kickoff
Promote drafts to `active`, register the initiative, and create the `initiative/{name}` branch.

### 3. Execution (The Inner Loop)
- **Start Feature**: Create a registered feature branch for a partition.
- **Implement Task**: Work on ephemeral task branches.
- **Reflect**: Periodically update active specs to match code changes.
- **Code Review** (optional): After Reflect, run *"Code review"* to evaluate the diff against specs, security, correctness, and quality. Writes `review.md` to `.cicadas/active/{initiative}/` with a `PASS` / `PASS WITH NOTES` / `BLOCK` verdict. `open_pr.py` reads the verdict and blocks on `BLOCK`. Check verdict anytime via `review.py`.
- **Signal**: Broadcast breaking changes to other active branches.

### 4. Completion & Synthesis
Merge back to `main`. The agent then **synthesizes** new Canon docs from the code and active specs (including `canon/summary.md` — a 300–500 token agent-optimized snapshot used for context injection at branch start), then archives the specs.

---

## Operational Formulas

### Greenfield Formula (New Feature)
**Flow**: `Idea -> Clarify -> Tech -> Approach -> Tasks -> Kickoff`
> **Prompt**: "Initialize a new initiative for [IDEA]. Run the Emergence subagents to draft the PRD and Tech Design."

### Brownfield Formula (Legacy/Existing Code)
**Flow**: `Code -> Bootstrap -> Clarify -> Approach -> Tasks -> Kickoff`
> **Prompt**: "Bootstrap cicadas for this project. Reverse-engineer the current architecture into Canon, then draft an initiative to [CHANGE]."

---

## Builder Command Quick Reference

| Action | Builder Command |
| :--- | :--- |
| **Setup** | "Initialize cicadas" |
| **Start Initiative** | "Kickoff {initiative-name}" |
| **Start Work** | "Start feature {partition-name}" |
| **Do Coding** | "Implement task {X}" |
| **Code Review** | "Code review" / "Review feature" / "Review fix" / "Review tweak" |
| **Review** | "Check status" |
| **Broadcast** | "Signal: {your message}" |
| **Finish Feature** | "Complete feature {name}" |
| **Finish Initiative** | "Complete initiative {name}" |
| **Abort** | "Abort" |
| **Project History** | "Project history" or "Generate history" |

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
