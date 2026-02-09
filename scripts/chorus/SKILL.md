---
name: chorus
description: >
  Orchestrates Cicadas methodology for sustainable spec-driven development. Use this skill when:
  starting work on a new feature or change, checking for conflicts with other work in progress,
  completing work and merging to main, querying the current state of the system, bootstrapping
  Cicadas on an existing project, or any mention of "Cicadas", "Chorus", "branch registry", 
  "canonical snapshot", or spec-driven development workflows. This skill handles the full lifecycle
  of concurrent development with transient forward docs and reverse-engineered canonical snapshots.
---

# Chorus

Orchestrates the Cicadas methodology — sustainable spec-driven development where forward docs
(PRDs, specs, tasks) are transient inputs that expire after implementation, and canonical
documentation is reverse-engineered from the code.

## Why "Cicadas"?

Cicadas emerge in synchronized broods, do their work, leave their husks behind, and repeat.
This mirrors the methodology: forward docs emerge to drive implementation, then expire (leave 
husks), while the living system continues. Multiple contributors work in synchronized parallel,
like a brood. Chorus is the synchronized sound they make together — the orchestration layer.

## Core Concepts

**Forward docs**: Created to drive a change, consumed during implementation, then archived (husks).
Never maintained after use.

**Cicadas snapshots**: Generated from code + expiring forward docs. The authoritative
description of what the system does and why. Never manually edited — regenerated on each merge.

**Branch registry**: Tracks who's working on what. Enables conflict detection across
concurrent work.

**Artifact index**: Append-only ledger of changes. Captures what/when/why for history.

## Operations

### Bootstrap (first-time setup)

Use when initializing Cicadas on an existing project.

1. Run: `python scripts/chorus/scripts/init.py`
2. This creates the `.cicadas/` directory structure
3. Read `docs/cicadas-method.md` for how to generate the initial Cicadas snapshot from existing code

### Start a Branch

Use when beginning work on a feature, fix, or change.

1. Ensure forward docs exist (PRD, approach, tasks) — author them or use BMAD
2. Run: `python scripts/chorus/scripts/branch.py {branch_name} --intent "description" --modules "mod1,mod2"`
3. Review any conflict warnings from Chorus

The script will:
- Check registry for overlapping work
- Create git branch
- Register intent in registry.json
- Create `.cicadas/forward/{branch_name}/` directory

### Check Status

Use to see current state and potential conflicts.

Run: `python scripts/chorus/scripts/status.py`

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
- Updated app-level snapshot (if scope warrants)
- Updated module-level snapshot(s)

### Merge

Use when synthesis is complete and reviewed.

1. Ensure snapshot is synthesized and reviewed
2. Run: `python scripts/chorus/scripts/archive.py {branch_name}`
3. Run: `python scripts/chorus/scripts/update_index.py --branch {branch} --summary "..."`
4. Execute git merge

### Query System State

Use to answer questions about the system.

For questions about current state: consult `.cicadas/canon/`
For questions about history: consult `.cicadas/index.json`
For questions about in-flight work: consult `.cicadas/registry.json`

## Core Guardrails

1. **No Unplanned Work**: Never start writing code until you have a reviewed `tasks.md`.
2. **Branch Only**: Only implement code on a registered git branch (not `main`).
3. **Hard Stop**: After drafting `tasks.md` in the incubator, you MUST STOP and wait for the user to "Hatch" or "Branch".

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
- `app-snapshot.md`: Structure for app-level Cicadas snapshot
- `module-snapshot.md`: Structure for module-level Cicadas snapshots
- `forward-docs/`: Templates for PRD, approach, tasks

## Scripts

All scripts are in `scripts/chorus/scripts/` directory. Run with Python 3.
