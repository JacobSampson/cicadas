---
name: chorus
description: Orchestrates Cicadas methodology for spec-driven development. Use this skill when performing project lifecycle operations.
---

# Overview

## Cicadas Methodology

The Cicadas methodology is a spec-driven development approach where forward docs
(PRDs, specs, tasks) are transient inputs that expire after implementation, and canonical
documentation is reverse-engineered from the code. It also provides a framework for managing
concurrent work across multiple contributors so teams can work together.

Chorus is the orchestrator of the Cicadas methodology. It provides the tools and processes
for managing the lifecycle of a project, including:

- Creating and managing branches and broods
- Tracking work in progress
- Generating and updating documentation
- Merging changes to main
- Checking for conflicts
- Resetting and pruning branches and broods
- Updating the artifact index

## Structure

### Working Directories
```
.cicadas/
├── registry.json # Tracks active branches and their status
├── index.json # Append-only ledger of all changes
├── canon/ # Canonical documentation
│   ├── product-overview.md # Comprehensive product requirements
│   ├── ux-overview.md # Comprehensive user experience
│   ├── tech-overview.md # Comprehensive technical approach
├── incubator/ # docs for an early stage change before it's hatched to a brood for implementation
└── forward/ # Forward-facing documentation that is consumed during implementation and then archived
    ├── broods/ # docs for a change that may be implemented by multiple agents
    │   ├── prd.md # Product requirements
    │   ├── ux.md # User experience
    │   ├── tech-design.md # Technical approach
    │   ├── approach.md # Implementation approach
    │   └── tasks.md # Tasks to be implemented
    └── ...

```

## Process
A typical Cicadas workflow looks like this:

### "Outer Loop" (Brood Initiation)
- Draft a PRD, UX, and Tech Design in the incubator
- Tell the Agent: **"Hatch the {name} brood."**
- The agent promotes the docs and initializes the initiative context.
- Ask Chorus to **"Create an approach"**
- Ask Chorus to **"Create tasks"**

### "Inner Loop"
- Ask Chorus to **"Implement task X"**
- Write the code and tests in the branch (AI or human)
- Ask Chorus to **"Check for brood changes"** to see if anything has changed that affects you
- When complete, ask Chorus to **"PR"** to create a pull request
- When PR is approved, ask Chorus to **"Merge"** to:
  - Merge the branch into main 
  - Update the registry
  - Update the brood specs (if needed)

### "Outer Loop" (Brood Completion)
Once all tasks are complete...
- Ask Chorus to **"Retire the brood"** to:
  - Update the registry
  - Archive the brood docs
  - Re-generate the canon docs



# Operations

### Bootstrap (first-time setup)
- Create the `.cicadas/` working directory structure:
```python
python scripts/chorus/scripts/init.py
```
- If the project already has existing code, execute ./reverse_engineering.md to create an initial canon.

### Hatch a Brood (Initiative Start)
Use when an idea involves multiple synchronized branches.
1. Draft shared docs (PRD, UX, Tech, Approach) in `.cicadas/incubator/{name}/`.
  - **Critical**: `approach.md` must define sequencing, dependencies, and logical partitions (which become Feature Branches).
  - The docs can be created manually or with ./emergence/
2. Tell the Agent: **"Hatch the {name} brood."**
3. The agent promotes the docs and initializes the initiative context.


### Start a Feature Branch (Registered)
Use when starting a major partition of work defined in the Brood's `approach.md`.
1. Ensure forward docs exist in `.cicadas/forward/broods/{brood_name}/`.
2. **Semantic Check**: Agent must check `registry.json` to ensure the new *intent* does not logically conflict with active work (LLM check).
3. **Run**: `python scripts/chorus/scripts/branch.py {branch_name} --intent "description" --modules "mod1,mod2" --brood {brood_name}`
4. Review any conflict warnings from Chorus (Modules) and the Agent (Intent).

### Start a Task Branch (Unregistered)
Use for the daily inner loop of coding. These are ephemeral and **do not** touch the registry.
1. Checkout from the Feature Branch: `git checkout -b task/{feature}/{task-name}`
2. Implement code.
3. **Reflect**: Keep the Feature Branch specs updated (see below).
4. Merge back to Feature Branch when done.

### Check Status & Signals
Use to see current state, potential conflicts, and broadcasts from other branches.
1. Run: `python scripts/chorus/scripts/status.py`
2. **Signal Check**: The Agent must check `registry.json` for any new `signal` messages from other branches in the Brood.
3. **Semantic Check**: The Agent must analyze the returned list of active intents for any logical conflicts or overlaps (using LLM reasoning).

### Inner Loop: Reflect
Use to keep specs in sync with code *during* development.
1. **Trigger**: After significant code changes or before merging a Task Branch.
2. **Action**: Agent analyzes the `git diff` and updates the local `forward/` docs (e.g., `tech-design.md`, `approach.md`) to match the reality of the code.
3. **Command**: (Agent Action) "Update the forward docs to reflect the code changes."

### Broadcast: Signal
Use to notify other branches of significant changes (e.g., API shift).
1. **Trigger**: You made a change that affects other Feature Branches in the Brood.
2. **Command**: `python scripts/chorus/scripts/signal.py "{message}"`
3. **Effect**: Appends a timestamped signal to the **Brood** entry in `registry.json`.

### Reset / Prune

Use to rollback a branch or brood and restore its docs to the incubator for iteration.

Run: `python scripts/chorus/scripts/prune.py {name} --type {branch|brood}`

### Check for Changes

Use during work to see if anything has changed that affects you.

Run: `python scripts/chorus/scripts/check.py`

### Synthesize Snapshot

Use when implementation is complete, before merging.

This is LLM work. Inputs:
- Current code (read the actual implementation)
- Forward docs from `.cicadas/forward/{branch}/`
- Previous Cicadas snapshot from `.cicadas/canon/`
- Artifact index from `.cicadas/index.json`

Output:
- Updated `canon/product-overview.md` (Goals, Personas, Metrics)
- Updated `canon/ux-overview.md` (Design Principles, Patterns, Flows)
- Updated `canon/tech-overview.md` (Architecture, Components, API, Schema)
- Updated module-level snapshot(s)

Use the prompt in `scripts/chorus/templates/synthesis-prompt.md` to guide this process.

**Agent Action**:
1.  Generate the plan and content using the prompt.
2.  **Execute**: Write the file contents to the `canon/` directory using your file writing tools.

### Merge

Use when synthesis is complete and reviewed.

1. Ensure snapshot is synthesized and reviewed
2. Run: `python scripts/chorus/scripts/archive.py {branch_name}`
3. Run: `python scripts/chorus/scripts/update_index.py --branch {branch} --summary "..."`
4. Execute `git merge {branch_name}` (Manual or Agent action required)
5. Push to remote

### Query System State

Use to answer questions about the system.

For questions about current state: consult `.cicadas/canon/`
For questions about history: consult `.cicadas/index.json`
For questions about in-flight work: consult `.cicadas/registry.json`

## Core Guardrails

1. **No Unplanned Work**: Never start writing code until you have a reviewed `tasks.md`.
2. **Branch Only**: Only implement code on a registered git branch (not `main`).
3. **Hard Stop**: After drafting `tasks.md` in the incubator, you MUST STOP and wait for the user to "Hatch" or "Branch".
4. **Tool Mandate**: NEVER manually edit `registry.json`. ALWAYS use `scripts/chorus/scripts/branch.py` (and friends) to manage state.

## Agent Procedures

Use these high-level procedures to orchestrate the lifecycle of a phase.

### Procedural: "Implement Phase {N}"
When asked to implement a specific phase:
1. **Setup**: Run `branch.py` if not already on a registered feature branch.
2. **Context**: Read `tasks.md` from the Brood or Local branch.
3. **Execution**: Implement **only** the tasks assigned to Phase {N}.
4. **Checkpoint**: After the last task in the phase, **STOP** and notify the user for code review. Do not proceed to Phase N+1 without approval.

### Procedural: "Complete Phase {N}"
When asked to complete/finalize a phase:
1. **Synthesis**: Update the `canon/` documentation to reflect the new code state.
2. **Archive**: Run `archive.py {branch_name}`.
3. **Log**: Run `update_index.py` with a summary of the phase's impact.
4. **Handoff**: Notify the user that the phase is archived and the canon is updated.

## Templates

Use templates in `scripts/chorus/templates/` directory:
- `product-overview.md`, `ux-overview.md`, `tech-overview.md`: Rich Canon templates
- `synthesis-prompt.md`: System prompt for synthesis agent
- `module-snapshot.md`: Structure for module-level Cicadas snapshots
- `forward-docs/`: Templates for PRD, approach, tasks

## Scripts

All scripts are in `scripts/chorus/scripts/` directory. Run with Python 3.

### Bootstrap (Reverse Engineering)
Use when initializing Cicadas on an existing (non-Cicadas) project.
1. Run: `python scripts/chorus/scripts/init.py`
2. Follow the [Reverse Engineering Workflow](./REVERSE_ENGINEERING.md) to establish your baseline **Canon**.
3. Create the `app.md` and key module snapshots from code discovery.

### Hatch a Brood (Initiative Start)
Use when an idea involves multiple synchronized branches.
1. Draft shared docs (PRD, UX, Tech) in `.cicadas/incubator/{name}/`.
2. Tell the Agent: **"Hatch the {name} brood."**
3. The agent promotes the docs and initializes the initiative context.

### Start a Branch
Use when beginning work on a feature, fix, or change.
1. Tell the Agent: **"Start a new branch called {branch_name} [linked to brood {name}]."**
2. The agent creates the git branch and associates it with the correct shared context.

### Check Status
Run: `python scripts/chorus/scripts/status.py`
Shows active branches, potential overlaps, and snapshot state.

### Prune / Rollback
Use when you want to **undo** a branch or brood (e.g., during experimentation).
Run: `python scripts/chorus/scripts/prune.py {name} --type {branch|brood}`
Effect: Deletes the git branch (if applicable), removes from registry, and restores forward docs to `incubator/` so you can try again.

### Synthesize Snapshot
This is LLM work. Before merging:
1. Read current code + forward docs + previous snapshots.
2. Update `.cicadas/canon/` files using the templates in `scripts/chorus/templates/`.
3. Example: extract rationale from `forward/my-feature/approach.md` and add to `canon/modules/my-module.md`.

### Merge & Archive
When synthesis is reviewed:
1. Run: `python scripts/chorus/scripts/archive.py {branch_name}`
2. Run: `python scripts/chorus/scripts/update_index.py --branch {branch} --summary "..."`
3. Execute standard git merge.

## Reference Guides

### Guide 1: Bootstrapping / Reverse Engineering
When bringing Cicadas to an existing codebase:
1. **Initialize**: Run `python scripts/chorus/scripts/init.py`.
2. **Reverse Engineer**: Follow [REVERSE_ENGINEERING.md](./REVERSE_ENGINEERING.md) for disciplined code discovery.
3. **Analyze**: Identify core modules and architectural patterns.
3. **Draft Snapshots**:
    - Create `.cicadas/canon/app.md` using the template.
    - Create module snapshots in `.cicadas/canon/modules/` for key components.
4. **Seed Index**:
    - Run `python scripts/chorus/scripts/update_index.py --branch "bootstrap" --summary "Initial bootstrap"`.

### Guide 2: Snapshot Synthesis (The LLM's Core Task)
**When to run**: Before merging any branch.
**Goal**: Update canonical docs to reflect the *new reality* of the code.

**Protocol**:
1. **Read**:
    - The *actual* code changes (git diff or file reads).
    - The forward docs in `.cicadas/forward/{branch}/` (for intent/rationale).
    - The existing snapshots in `.cicadas/canon/`.
2. **Synthesize**:
    - Update `app.md` if high-level architecture changed.
    - Update relevant `modules/{name}.md` files.
    - **Crucial**: Extract "Key Decisions" from the forward docs and append them to the snapshots. This preserves the "why" before the forward docs are archived.
3. **Verify**: Ensure the new snapshots accurately describe the code as it exists *now*.

### Guide 4: Implementation Rules (Guardrails)
To prevent agents from starting work before the plan is ready:
1. **Wait for Hatching**: Never start implementing tasks until the incubator is hatched into a brood or branch.
2. **Branch Check**: Verify you are on a dedicated git branch from the `registry.json`.
3. **Protocol**: Follow the strict rules in [implementation.md](./implementation.md).

### Guide 5: Agent Procedures (Simplified Flow)
Use these high-level natural language commands in the TUI:
- **"Implement Phase {N}"**: Orchestrates branch creation, task identification, and autonomous implementation of a phase.
- **"Complete Phase {N}"**: Orchestrates synthesis, archiving, and indexing once review is approved.

### Guide 6: Conflict Resolution
Run: `python scripts/chorus/scripts/check.py`

**Interpreting Output**:
- **Module Overlap**: Warning that another branch is touching the same modules. *Action*: Check their forward docs, maybe coordinate.
- **Main Updates**: New commits on main. *Action*: Rebase your branch to ensure you're building on the latest state.
- **Registry Desync**: Branch not registered. *Action*: Run `branch.py` to register it.

---

## CLI Workflow Quick Reference

| Phase | Command | Action |
|-------|---------|--------|
| **Start** | `python scripts/chorus/scripts/branch.py {name} --intent "..." --modules "..."` | Join the brood |
| **Check** | `python scripts/chorus/scripts/status.py` | See global state |
| **Verify**| `python scripts/chorus/scripts/check.py` | Check for conflicts |
| **Prune** | `python scripts/chorus/scripts/prune.py {name} --type {branch|brood}` | Rollback & restore docs |
| **Finish**| `python scripts/chorus/scripts/archive.py {name}` | Husk forward docs |
| **Log** | `python scripts/chorus/scripts/update_index.py --branch {name} --summary "..."` | Record history |
