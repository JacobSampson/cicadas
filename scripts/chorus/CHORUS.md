# Chorus: Cicadas Orchestrator

Chorus orchestrates the Cicadas methodology — sustainable spec-driven development where forward docs (PRDs, specs, tasks) are transient inputs that expire after implementation, and canonical documentation is reverse-engineered from the code.

## Operations

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
