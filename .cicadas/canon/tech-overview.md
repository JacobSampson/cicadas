# Tech Overview

> Canon document. Updated by the Synthesis agent at the close of each initiative.

## Architecture Summary

Cicadas is a filesystem-based state machine that orchestrates development via Git and JSON-based registries. It separates logic (the "Skill") from state (the `.cicadas/` directory). Distribution and installation is managed by a standalone bash script (`install.sh`) that requires only `bash`, `curl`, and `unzip`.

### Key Decisions

- **Expiring Specs** — Active specs live in `.cicadas/active/` and are moved to `.cicadas/archive/` upon completion. This prevents developers from relying on outdated documents.
- **Hierarchical Branching** — Complex work uses `initiative/{name}` and `feat/{name}` branches. Lightweight work forks directly from `master` using `fix/` or `tweak/`.
- **Registry Source of Truth** — `registry.json` is the definitive map of all in-flight work and cross-branch signals.
- **Distribution-First Design** — `install.sh` is the primary entry point; uses GitHub archive URL for zero-friction distribution without requiring a release pipeline.
- **Universal Installation** — Installer works on any project stack (Go, Java, React, etc.); only requires Python 3.11+ and `git` at runtime.
- **Lifecycle & PR Boundaries** — Per-initiative `lifecycle.json` (in drafts/active) defines at which boundaries to open PRs (specs, initiatives, features, tasks) and an ordered step list; completion is detected via git only (no host API).

---

## Directory Schema

```
.cicadas/
├── registry.json                 # Global state (initiatives + feature branches)
├── index.json                    # Change ledger (append-only)
├── canon/                        # Authoritative documentation (synthesized)
├── drafts/                       # Pre-kickoff staging area (may include lifecycle.json)
├── active/                       # Live specs for in-flight work (may include lifecycle.json)
└── archive/                      # Expired spec trail
```

---

## Branching Model

| Prefix | Source | registered? | Purpose |
|--------|--------|-------------|---------|
| `initiative/` | `master` | Yes | Parent branch for multi-partition work. |
| `feat/` | `initiative/` | Yes | Vertical slice of an initiative. |
| `fix/` | `master` | Yes | Lightweight bug fix. |
| `tweak/` | `master` | Yes | Lightweight enhancement. |
| `task/` | `feat/` | No | Ephemeral implementation branch. |

---

## Installation & Distribution

### `install.sh` — Entry Point

A portable bash script in the project root that handles installation, setup, and updates. Requires only `bash`, `curl`, `unzip`, and `git`.

**Key features:**
- **Python 3.11+ Check**: Validates version; prints OS-specific install guidance if missing.
- **GitHub Archive Distribution**: Downloads `master.zip`, extracts to `.cicadas-skill/cicadas/` (configurable via `--dir`).
- **Workspace Initialization**: Calls `init.py` to initialize the `.cicadas/` directory structure.
- **Agent Integration Setup**: Optionally creates symlinks/configs for `claude-code` (`.claude/skills/cicadas`), `antigravity` (`.agents/skills/cicadas`), `cursor` (`.cursor/rules/cicadas.mdc`), and `rovodev` (`.rovodev/skills/cicadas`).
- **Update Workflow**: `--update` flag re-downloads skill files without touching `.cicadas/` state or re-running init.

```bash
curl -fsSL https://raw.githubusercontent.com/ecodan/cicadas/master/install.sh | bash
bash install.sh --dir tools/cicadas --agent claude-code,cursor
bash install.sh --update
```

---

## CLI Orchestration

The system uses a set of Python scripts in `src/cicadas/scripts/`:
- `init.py`: Initializes `.cicadas/` directory on fresh install (idempotent; called by `install.sh`).
- `kickoff.py`: Promotes drafts (including `lifecycle.json` when present) and registers initiatives.
- `branch.py`: Creates and registers feature/fix/tweak branches.
- `status.py`: Reports global project state; when `lifecycle.json` exists for an initiative, reports Merged (branch pairs) and Next (suggested step) via git-based merge detection.
- `create_lifecycle.py`: Creates `lifecycle.json` in drafts or active with PR boundaries and default steps.
- `open_pr.py`: Opens a PR from current branch (tries `gh` → `glab` → Bitbucket URL → fallback); host-agnostic.
- `update_index.py`: Logs changes to the ledger.
- `archive.py`: Concludes work, deregisters branches, and expires specs (includes `lifecycle.json` when present).
- `abort.py`: Context-aware rollback for any branch type.
- `signal.py`: Broadcasts breaking changes across peer branches.
- `history.py`: Generates HTML timeline of completed initiatives.
- `check.py`: Validates for module conflicts across active branches.

---

## Implementation Conventions

- **Module-Awareness**: Feature branches declare their module scope in the registry to prevent silent merge conflicts.
- **Reflect Operation**: Agents MUST update active specs before merging any code change.
- **Code Review Operation**: Optional agent operation invoked after Reflect, before opening a PR or merging. Runs a structured algorithm (task completeness, acceptance criteria, arch conformance, module scope, Reflect completeness, security scan, correctness scan, code quality) against the branch diff and active specs. Output is ephemeral and always advisory. Defined in `emergence/code-review.md`.
- **Significance Check**: Lightweight paths must be evaluated for Canon updates before archiving.
- **Relative Symlinks**: Agent integrations use relative symlinks for portability across machines with different mount paths.
- **Non-Interactive Pipe Support**: Installer detects `curl | bash` context (`[ -t 0 ]`) and skips interactive prompts, printing manual setup guidance instead.

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
