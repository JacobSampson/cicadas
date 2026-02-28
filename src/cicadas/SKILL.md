---
name: cicadas
description: Use when the user says "kickoff", "start feature", "complete initiative", "check status", "signal", "prune", "bootstrap", "reflect", or any other Cicadas lifecycle command. Orchestrates the Cicadas spec-driven development methodology.
argument-hint: "[command] [name]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Cicadas: Orchestrator

## Overview

The Cicadas methodology is a sustainable spec-driven development approach where:
- **Active Specs** (PRDs, designs, tasks) are disposable inputs that expire after implementation.
- **Code is the single source of truth** — always authoritative.
- **Canon** is reverse-engineered from code + expiring specs, not maintained in parallel.
- **Work is partitioned** — large initiatives are sliced into independent feature branches.
- **Specs stay current during development** — a "Reflect" operation keeps active specs in sync with code.
- **Teams coordinate asynchronously** — a "Signal" operation broadcasts breaking changes to peer branches.

Cicadas is the orchestrator — a set of portable CLI scripts and agent instructions that manages the Cicadas lifecycle: initiative kickoff, branch registration, conflict detection, spec reflection, signaling, synthesis, merging, and queries.

## Directory Structure

Cicadas logic resides in its skill directory, and manages the `.cicadas/` folder in the project root:

> **Note**: `{cicadas-dir}` refers to the directory containing this skill file (e.g., `src/cicadas/` or wherever Cicadas is installed in the target project).

```
project-root/
├── {cicadas-dir}/                    # Cicadas orchestrator (wherever installed)
│   ├── SKILL.md                      # Agent skill definition (this file)
│   ├── implementation.md             # Agent guardrails
│   ├── scripts/                      # CLI tools
│   │   ├── utils.py                  # Shared utilities (root detection, JSON I/O)
│   │   ├── init.py                   # Bootstrap .cicadas/ structure
│   │   ├── kickoff.py                # Promote drafts → active, register initiative
│   │   ├── branch.py                 # Register a feature branch
│   │   ├── status.py                 # Show initiatives, branches, signals
│   │   ├── check.py                  # Check for conflicts & master updates
│   │   ├── signalboard.py            # Broadcast a change to peer branches
│   │   ├── archive.py                # Move active specs → archive, deregister
│   │   ├── update_index.py           # Append to change ledger
│   │   └── prune.py                  # Rollback branch or initiative → restore to drafts
│   ├── templates/                    # Markdown templates
│   │   ├── synthesis-prompt.md       # LLM prompt for canon synthesis
│   │   ├── product-overview.md       # Canon template
│   │   ├── ux-overview.md            # Canon template
│   │   ├── tech-overview.md          # Canon template
│   │   ├── module-snapshot.md        # Canon template (per module)
│   │   ├── prd.md                    # Active spec template
│   │   ├── ux.md                     # Active spec template
│   │   ├── tech-design.md            # Active spec template
│   │   ├── approach.md               # Active spec template
│   │   ├── tasks.md                  # Active spec template
│   │   ├── buglet.md                 # Lightweight bug spec template
│   │   └── tweaklet.md               # Lightweight tweak spec template
│   └── emergence/                    # Subagent instructions for spec authoring
│       ├── EMERGENCE.md              # Emergence phase overview
│       ├── bootstrap.md              # Reverse Engineering subagent
│       ├── clarify.md                # PRD refinement subagent
│       ├── ux.md                     # UX design subagent
│       ├── tech-design.md            # Architecture subagent
│       ├── approach.md               # Partitioning & sequencing subagent
│       ├── tasks.md                  # Task breakdown subagent
│       ├── bug-fix.md                # Bug clarification drafting subagent
│       └── tweak.md                  # Minor tweak drafting subagent
└── .cicadas/                         # Cicadas artifacts (managed by scripts)
    ├── config.json                   # Local configuration
    ├── registry.json                 # Global registry (initiatives + feature branches)
    ├── index.json                    # Change ledger (append-only)
    ├── canon/                        # Canon (authoritative, generated)
    │   ├── product-overview.md
    │   ├── ux-overview.md
    │   ├── tech-overview.md
    │   └── modules/
    │       └── {module-name}.md
    ├── drafts/                       # Pre-kickoff staging area
    │   └── {initiative-name}/
    │       ├── prd.md
    │       ├── ux.md
    │       ├── tech-design.md
    │       ├── approach.md
    │       └── tasks.md
    ├── active/                       # Live specs for in-flight work
    │   └── {initiative-name}/
    └── archive/                      # Expired specs (timestamped)
        └── {timestamp}-{name}/
```

## Process

### Outer Loop — Initiative Lifecycle

1. **Emergence**: Draft specs in `.cicadas/drafts/{initiative}/` using subagents or manual authoring.
2. **Kickoff**: Promote drafts to active, register initiative, create initiative branch.
3. **Feature Branches**: For each partition defined in `approach.md`, start a registered feature branch.
4. **Task Branches**: For each task, create ephemeral unregistered task branches off the feature branch.
5. **Complete Feature**: Merge feature branch into initiative branch. No synthesis yet.
6. **Complete Initiative**: Merge initiative branch to `master`, synthesize canon on `master`, archive specs.

### Inner Loop — Daily Coding

1. Create task branch from feature branch: `git checkout -b task/{feature}/{task-name}`
2. Implement code.
3. **Reflect**: Keep active specs current as code diverges from plan.
4. Open a **PR** against the feature branch. Include Reflect findings in the PR description.
5. Builder reviews and approves the PR.
6. Merge the PR, delete the task branch.

### Branch Hierarchy

```
main (default branch)
├── initiative/{name}              ← created at kickoff, merges to main (default branch) once
│   ├── feat/{partition-1}         ← registered, forks from initiative
│   │   ├── task/.../task-a        ← ephemeral, unregistered
│   │   └── task/.../task-b        ← ephemeral, unregistered
│   ├── feat/{partition-2}         ← registered, forks from initiative
│   └── feat/{partition-3}         ← registered, forks from initiative
├── fix/{name}                     ← [NEW] lightweight, forks from main (default branch)
└── tweak/{name}                   ← [NEW] lightweight, forks from main (default branch)
```

---

## Operations

### Bootstrap (Legacy Migration)

Use the **Bootstrap Subagent** to bring an existing codebase into Cicadas.

1.  **Discovery**: Scan the repository to understand product goals and architecture.
2.  **Canonization**: Synthesize a full suite of authoritative docs (PRD, UX, Tech, Modules) using templates.
3.  **Validation**: Verify the documentation correctly reflects the code.
4.  **Genesis**: Record the baseline in the index.

### Emergence (Drafting Specs)
Progressive spec authoring in `.cicadas/drafts/{initiative-name}/`, using subagents in `emergence/` or manual drafting. See `emergence/emergence.md` for the full workflow.

| Step | Artifact | Focus |
|------|----------|-------|
| 1. Clarify | `prd.md` | **What & Why**. Problem, users, success criteria. |
| 2. UX | `ux.md` | **Experience**. Interaction flow, UI states, copy. |
| 3. Tech | `tech-design.md` | **Architecture**. Components, data flow, schemas. |
| 4. Approach | `approach.md` | **Strategy & Partitioning**. Sequencing, dependencies, and logical partitions that become feature branches. |
| 5. Tasks | `tasks.md` | **Execution**. Ordered, testable checklist grouped by partition. |

**Critical**: `approach.md` MUST define logical partitions with declared module scopes. These become feature branches.

Human review is required after each step. The Agent MUST NOT proceed without Builder approval.

### Kickoff (Initiative Start)
**Trigger**: Drafts reviewed and approved.
```
python {cicadas-dir}/scripts/kickoff.py {initiative-name} --intent "description"
```
**Effect**:
1. Promotes docs from `.cicadas/drafts/{name}/` to `.cicadas/active/{name}/`.
2. Registers the initiative in `registry.json` under `initiatives`.
3. Creates the initiative branch: `git checkout -b initiative/{name}`.
4. Pushes the initiative branch to remote: `git push -u origin initiative/{name}` (done by script).

### Start a Feature Branch (Registered)
**When**: Starting a partition of work defined in `approach.md`.

**Steps**:
1. **Semantic Intent Check (Agent)**: Read `registry.json`. Analyze new intent against all active feature intents for logical conflicts.
2. **Checkout initiative branch**: `git checkout initiative/{name}`
3. **Script**: `python {cicadas-dir}/scripts/branch.py {branch-name} --intent "description" --modules "mod1,mod2" --initiative {initiative-name}`
4. Review warnings from both the Agent (intent conflicts) and the Script (module overlaps).
5. Branch is automatically pushed to remote by the script (`git push -u origin {branch-name}`), making it visible to collaborators.

### Complete a Feature Branch
**When**: All task branches merged into the feature branch.

**Steps**:
1. **Update index**: `python {cicadas-dir}/scripts/update_index.py --branch {name} --summary "..."`
2. **Merge to initiative**: `git checkout initiative/{name} && git merge {branch-name}`
3. **Push initiative branch**: `git push origin initiative/{name}`

**Key**: No synthesis, no archiving at this step. Active specs stay active — they are the living document for the rest of the initiative, continuously updated by Reflect.

### Complete an Initiative
**When**: All feature branches merged into the initiative branch.

**Step 1 — Merge to main (default branch)**:
```
git checkout main (default branch) && git merge initiative/{name}
git push origin main (default branch)
git branch -d initiative/{name}
git push origin --delete initiative/{name}
```

**Step 2 — Synthesize canon on main (default branch)** (Agent Operation):
- Read: codebase on `main (default branch)`, active specs, existing canon, change ledger
- Synthesize: create (greenfield) or update (brownfield) canon files
- **Extract Key Decisions** from active specs and embed in canon
- Present to Builder for review

Use the prompt in `{cicadas-dir}/templates/synthesis-prompt.md` to guide synthesis.

**Step 3 — Archive & commit**:
```
python {cicadas-dir}/scripts/archive.py {initiative-name} --type initiative
python {cicadas-dir}/scripts/update_index.py --branch {initiative-name} --summary "..."
git commit -m "chore(cicadas): synthesize canon and archive {initiative-name}"
git push origin main (default branch)
```

### Check Status & Signals
```
python {cicadas-dir}/scripts/status.py
python {cicadas-dir}/scripts/check.py
```
The Agent should check for signals when performing a Check Status operation and assess their relevance.

### Broadcast: Signal
**Trigger**: A change that affects other feature branches.
```
python {cicadas-dir}/scripts/signal.py "Changed API: renamed login() to authenticate()"
```
Appends a timestamped signal to the initiative's signal board in `registry.json`.

### Prune / Rollback
```
python {cicadas-dir}/scripts/prune.py {name} --type {branch|initiative}
```
Deletes the git branch, removes from registry, and restores specs to `drafts/`.

### Lightweight Paths (Bug Fixes & Tweaks)

For trivial changes, Cicadas supports a "fast path" that reduces documentation overhead and simplifies the branch hierarchy.

**Thresholds**:
- **Fix**: An isolated defect with no architectural impact.
- **Tweak**: A small enhancement (e.g., UI polish, new utility function) requiring < 100 lines of code and no new dependencies.

**The Workflow**:
1. **Emergence**: Draft a single `buglet.md` or `tweaklet.md` in `.cicadas/drafts/{name}/`.
2. **Kickoff**: `python {cicadas-dir}/scripts/kickoff.py {name}`. Promotes the single spec to `active/`.
3. **Branch**: `python {cicadas-dir}/scripts/branch.py {fix|tweak}/{name} --initiative {name}`. Forks directly from `main (default branch)`.
4. **Implement**: Work directly on the fix/tweak branch.
5. **Significance Check**: Before completion, the Agent evaluates if the change warrants a Canon update.
6. **Complete**: Merge to `main (default branch)`, optionally Reflect/Synthesize to Canon, and Archive.

**Escalation Criteria**:
If a lightweight path discovers new complexity (e.g., "this fix requires a database migration"), the Agent MUST:
1. Halt execution.
2. Upgrade to a full initiative: Draft `tech-design.md`, `approach.md`, and `tasks.md`.
3. Move the work to an `initiative/` and `feat/` branch hierarchy.

---

## Agent Operations (LLM)

These are reasoning + editing operations performed by the Agent, NOT scripts.

### Semantic Intent Check
**Trigger**: Before starting a feature branch.
**Action**: Read `registry.json`, analyze the new intent against all active feature intents for logical conflicts. Module overlap alone is insufficient — this is an LLM reasoning step.

### Reflect
**Trigger**: After significant code changes; before merging a task branch to the feature branch.
**Action**:
1. Analyze `git diff` against the active specs.
2. Update relevant docs in `.cicadas/active/` (e.g., `tech-design.md`, `approach.md`, `tasks.md`) to match code reality.
3. If the change is significant enough to impact other feature branches, proceed to Signal.
4. Include Reflect findings in the PR description.

### Signal Assessment
**Trigger**: After Reflect discovers a cross-branch impact.
**Action**: The Agent evaluates whether a change affects peer branches and runs `signal.py` autonomously if needed.

### Bootstrap (Agent Operation)
**Trigger**: Migrating a legacy project or initializing with existing code.
**Action**:
1.  Initialize `.cicadas/` structure.
2.  Perform comprehensive code discovery.
3.  Synthesize authoritative Canon (PRD, UX, Tech, Modules) using templates.
4.  Validate documentation against code.
5.  Set Genesis point in index.

---

## Guardrails

1. **No Unplanned Work**: Never start writing code until you have a reviewed `tasks.md`.
2. **Branch Only**: Only implement code on a registered feature branch or a task branch off of one. Never on `main (default branch)` or the initiative branch.
3. **Hard Stop**: After drafting specs, STOP and wait for the Builder to approve. After synthesis, STOP and wait for review.
4. **Tool Mandate**: NEVER manually edit `registry.json`. ALWAYS use the scripts.
5. **Reflect Before PR**: Always run the Reflect operation before opening a PR for a task branch.
6. **No Canon on Branches**: Never write to `.cicadas/canon/` on any branch. Canon is only synthesized on `main (default branch)` at initiative completion.

## Agent Autonomy Boundaries

| Action | Autonomy | Rationale |
|--------|----------|-----------|
| **Reflect** | Autonomous | Keeping specs current is mechanical. |
| **Signal** | Autonomous | Agent assesses cross-branch impact. |
| **Semantic Intent Check** | Autonomous | Conflict detection is informational. |
| **PR creation** | Autonomous | Agent opens PRs with summaries and Reflect findings. |
| **PR merge** | **Builder approval** | Code review is a human gate. |
| **Synthesis** | Autonomous (execution) | Agent produces canon, but... |
| **Canon commit** | **Builder approval** | ...canon must be reviewed before committing. |
| **Archive** | **Builder approval** | Archiving is irreversible. |

## Builder Commands

The Builder interacts via natural-language commands. The Agent handles all scripts, git operations, and agentic operations behind the scenes.

- **"Initialize cicadas"** → Runs `init.py`. Sets up `.cicadas/` structure.
- **"Kickoff {name}"** → Runs `kickoff.py`. Promotes drafts, registers initiative, creates initiative branch.
- **"Start feature {name}"** → Semantic check + `branch.py`. Creates feature branch from initiative, registers, checks conflicts.
- **"Implement task {X}"** → Creates task branch, implements, Reflects, opens PR with findings.
- **"Signal {message}"** → Runs `signal.py`. Broadcasts change to initiative.
- **"Complete feature {name}"** → Runs `update_index.py`. Merges feature branch into initiative branch.
- **"Complete initiative {name}"** → Merges initiative to `master`, synthesizes canon, archives specs, commits.
- **"Check status"** → Runs `status.py` and `check.py`. Surfaces state, conflicts, signals.
- **"Prune {name}"** → Runs `prune.py`. Rollback and restore to drafts.

---

## CLI Quick Reference

### Scripts (Deterministic)

| Phase | Command | Action |
|-------|---------|--------|
| **Init** | `python {cicadas-dir}/scripts/init.py` | Bootstrap project structure |
| **Kickoff** | `python {cicadas-dir}/scripts/kickoff.py {name} --intent "..."` | Promote drafts, register initiative, create branch |
| **Feature** | `python {cicadas-dir}/scripts/branch.py {name} --intent "..." --modules "..." --initiative {name}` | Register feature branch |
| **Status** | `python {cicadas-dir}/scripts/status.py` | Show global state & signals |
| **Check** | `python {cicadas-dir}/scripts/check.py` | Check for conflicts & updates |
| **Signal** | `python {cicadas-dir}/scripts/signal.py "{message}"` | Broadcast to initiative |
| **Archive** | `python {cicadas-dir}/scripts/archive.py {name} --type {branch\|initiative}` | Expire active specs |
| **Log** | `python {cicadas-dir}/scripts/update_index.py --branch {name} --summary "..."` | Record history |
| **Prune** | `python {cicadas-dir}/scripts/prune.py {name} --type {branch\|initiative}` | Rollback & restore to drafts |

### Agent Operations (LLM)

| Operation | Trigger | Action |
|-----------|---------|--------|
| **Semantic Intent Check** | Before starting a feature branch | Analyze registry intents for logical conflicts |
| **Reflect** | After significant code changes, before PR | Update active specs to match code reality. Include findings in PR. |
| **Signal Assessment** | After Reflect, during status check | Evaluate cross-branch impact. Signal autonomously if needed. |
| **Synthesis** | At initiative completion, on `main` | Generate canon from code + active specs. Requires Builder review. |

## Templates

Use templates in `{cicadas-dir}/templates/` directory:
- `product-overview.md`, `ux-overview.md`, `tech-overview.md`, `module-snapshot.md`: Canon templates
- `prd.md`, `ux.md`, `tech-design.md`, `approach.md`, `tasks.md`: Active spec templates
- `synthesis-prompt.md`: System prompt for canon synthesis

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
