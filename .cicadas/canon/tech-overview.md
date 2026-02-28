# Tech Overview

> Canon document. Updated by the Synthesis agent at the close of each initiative.

## Architecture Summary

Cicadas is a filesystem-based state machine that orchestrates development via Git and JSON-based registries. It separates logic (the "Skill") from state (the `.cicadas/` directory).

### Key Decisions

- **Expiring Specs** — Active specs live in `.cicadas/active/` and are moved to `.cicadas/archive/` upon completion. This prevents developers from relying on outdated documents.
- **Hierarchical Branching** — Complex work uses `initiative/{name}` and `feat/{name}` branches. Lightweight work forks directly from `master` using `fix/` or `tweak/`.
- **Registry Source of Truth** — `registry.json` is the definitive map of all in-flight work and cross-branch signals.

---

## Directory Schema

```
.cicadas/
├── registry.json                 # Global state (initiatives + feature branches)
├── index.json                    # Change ledger (append-only)
├── canon/                        # Authoritative documentation (synthesized)
├── drafts/                       # Pre-kickoff staging area
├── active/                       # Live specs for in-flight work
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

## CLI Orchestration

The system uses a set of Python scripts in `src/cicadas/scripts/`:
- `kickoff.py`: Promotes drafts and registers initiatives.
- `branch.py`: Creates and registers feature/fix/tweak branches.
- `status.py`: Reports global project state.
- `update_index.py`: Logs changes to the ledger.
- `archive.py`: Concludes work and expires specs.

---

## Implementation Conventions

- **Module-Awareness**: Feature branches declare their module scope in the registry to prevent silent merge conflicts.
- **Reflect Operation**: Agents MUST update active specs before merging any code change.
- **Significance Check**: Lightweight paths must be evaluated for Canon updates before archiving.

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
