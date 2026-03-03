# Cicadas 
**Version 0.5.0**

**Sustainable, Spec-Driven Development (SDD) for human-AI teams.**

Cicadas reverses the traditional relationship between code and documentation. Instead of fighting to keep specifications in sync with code, **Cicadas treats forward-looking docs (PRDs, plans) as disposable inputs** that drive implementation and then expire. Authoritative system documentation is then **reverse-engineered from the code itself** into canonical snapshots.

---

## The Core Concept

1.  **Active Specs are Disposable**: PRDs, designs, and task lists drive implementation but expire when the initiative completes.
2.  **Code is Truth**: The codebase is the only source of truth.
3.  **Work is Coordinated**: Parallel initiatives and features are registered in a registry, allowing parallel work efforts to minimize overlap and clashes.
4.  **Canon is Synthesized**: Authoritative documentation (`canon/`) is generated from the code + the intent of expired specs. It is never manually maintained.
5.  **Reflect & Signal**: During development, we keep specs honest via **Reflect** (updating active specs to match code reality) and coordinate via **Signal** (broadcasting breaking changes to peer branches).

### See It In Action

For a complete end-to-end walkthrough of the method (Greenfield creation + Brownfield update), see:

👉 **[Cicadas Method — Dry Run](docs/dry-run.md)**

For the full methodology specification, see:

📘 **[Cicadas Method (v2) Specification](docs/cicadas-method-general-02.md)**

---

## The Workflow

### Phase 1: Emergence (Drafting)
We draft specifications in `.cicadas/drafts/` using specialized subagents (Clarify, UX, Tech, Approach, Tasks).
*   **Key Artifact**: `approach.md` defines the partitions (feature branches).

### Phase 2: Kickoff
We promote drafts to **Active Specs** and register the initiative.
*   **Command**: `python src/cicadas/scripts/kickoff.py {name} --intent "..."`
*   **Result**: Creates `initiative/{name}` branch and `.cicadas/active/{name}/`.

### Phase 3: Execution (The Dual Loop)
Work happens in **Feature Branches** (registered) and **Task Branches** (ephemeral).

*   **Start Feature**: `python src/cicadas/scripts/branch.py {feature} --intent "..."`
*   **Reflect**: When code implementation diverges from the plan, we update the active specs *immediately*.
*   **Code Review** (optional): After Reflect, the agent evaluates the diff against specs, security, correctness, and quality — producing an advisory report with a merge verdict.
*   **Signal**: If a change affects other branches, we broadcast it: `python src/cicadas/scripts/signal.py "..."`

### Phase 4: Completion (Synthesis)
When all features are merged into the initiative branch, we merge to `main` and then:
1.  **Synthesize Canon**: An AI agent reads the code on `main` + the active specs and generates fresh documentation in `.cicadas/canon/`.
2.  **Archive**: Active specs are moved to `.cicadas/archive/`.

---

## Project Structure

The **Cicadas** toolset manages the `.cicadas/` directory:

```text
.
├── src/
│   └── cicadas/                # The Cicadas orchestrator (scripts & agents)
└── .cicadas/
    ├── canon/                  # Authoritative, generated checks
    │   ├── product-overview.md
    │   ├── tech-overview.md
    │   └── modules/            # Module-level snapshots
    ├── active/                 # Live specs for in-flight initiatives
    ├── drafts/                 # Staging area for new initiatives
    ├── archive/                # Expired specs (historical record)
    └── registry.json           # Active initiatives & branch registry
```

---

## Getting Started

### Installation

**One-liner** (requires Python 3.11+ and `git`):

```bash
curl -fsSL https://raw.githubusercontent.com/ecodan/cicadas/master/install.sh | bash
```

This downloads Cicadas into `.cicadas-skill/cicadas/`, initializes the `.cicadas/` workspace, and optionally sets up agent integrations.

**With agent integration:**
```bash
# Claude Code
curl -fsSL https://raw.githubusercontent.com/ecodan/cicadas/master/install.sh | bash -s -- --agent claude-code

# Cursor
curl -fsSL https://raw.githubusercontent.com/ecodan/cicadas/master/install.sh | bash -s -- --agent cursor

# Multiple agents
curl -fsSL https://raw.githubusercontent.com/ecodan/cicadas/master/install.sh | bash -s -- --agent claude-code,cursor
```

**Custom install directory:**
```bash
bash install.sh --dir tools/cicadas --agent claude-code
```

**Update Cicadas files** (preserves your `.cicadas/` workspace):
```bash
bash install.sh --update
```

**Supported agents:**

| Agent | Integration |
|-------|------------|
| `claude-code` | `.claude/skills/cicadas` symlink |
| `antigravity` | `.agents/skills/cicadas` symlink |
| `cursor` | `.cursor/rules/cicadas.mdc` (copy of `skill.md`) |
| `none` | Skip; configure manually |

**Requirements:** Python 3.11+, `curl`, `unzip`, `git`

### Quick Command Reference
All scripts are in `src/cicadas/scripts/`.

| Action | Command |
| :--- | :--- |
| **Kickoff Initiative** | `python src/cicadas/scripts/kickoff.py {name} --intent "..."` |
| **Start Feature** | `python src/cicadas/scripts/branch.py {name} --intent "..."` |
| **Check Status** | `python src/cicadas/scripts/status.py` (shows Merged/Next when lifecycle exists) |
| **Check Conflicts** | `python src/cicadas/scripts/check.py` |
| **Send Signal** | `python src/cicadas/scripts/signal.py "Message..."` |
| **Log Work** | `python src/cicadas/scripts/update_index.py --branch {name} ...` |
| **Lifecycle** | `python src/cicadas/scripts/create_lifecycle.py {name}` (PR boundaries + steps in drafts/active) |
| **Open PR** | `python src/cicadas/scripts/open_pr.py [--base branch]` (gh/glab/Bitbucket/fallback) |
| **Archive** | `python src/cicadas/scripts/archive.py {name}` |
| **Abort** | `python src/cicadas/scripts/abort.py` |
| **Project History** | `python src/cicadas/scripts/history.py` |


## License

Cicadas is licensed under the [Apache License 2.0](LICENSE).
```

**Optional: Add a NOTICE file** (recommended for Apache 2.0 projects):
```
Cicadas
Copyright 2026 Cicadas Contributors

This product includes software developed by Dan and contributors.
---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
