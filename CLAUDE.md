# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run all tests:**
```bash
python -m pytest tests/
```

**Run a single test file:**
```bash
python -m pytest tests/test_kickoff.py
```

**Run a single test:**
```bash
python -m pytest tests/test_kickoff.py::TestKickoff::test_basic_kickoff
```

**Lint:**
```bash
ruff check src/ tests/
```

**Format:**
```bash
ruff format src/ tests/
```

**CLI scripts** (run from project root; scripts use `sys.path` to find `utils.py`):
```bash
python src/cicadas/scripts/init.py
python src/cicadas/scripts/status.py
python src/cicadas/scripts/check.py
python src/cicadas/scripts/kickoff.py {name} --intent "..."
python src/cicadas/scripts/branch.py {name} --intent "..." --modules "mod1,mod2" --initiative {name}
python src/cicadas/scripts/signal.py "message"
python src/cicadas/scripts/archive.py {name} --type {branch|initiative}
python src/cicadas/scripts/update_index.py --branch {name} --summary "..."
python src/cicadas/scripts/prune.py {name} --type {branch|initiative}
python src/cicadas/scripts/history.py [--output path]
```

## Architecture

Cicadas is a **spec-driven development methodology toolset** for human-AI teams. It consists of two parts:

1. **The Skill** (`src/cicadas/`) — portable CLI scripts and agent instructions that can be dropped into any project.
2. **The State** (`.cicadas/`) — filesystem-based state managed by the scripts, living in the project root.

### `src/cicadas/` Structure

- `scripts/` — CLI tools for the full initiative lifecycle. All share `utils.py` for root detection (`get_project_root()`), branch detection (`get_default_branch()`), and JSON I/O (`load_json`/`save_json`).
- `emergence/` — Markdown instructions for subagents (Clarify, UX, Tech, Approach, Tasks, Bootstrap, Bug-fix, Tweak). These are **agent prompts**, not code.
- `templates/` — Markdown templates for specs (`prd.md`, `ux.md`, `tech-design.md`, `approach.md`, `tasks.md`, `buglet.md`, `tweaklet.md`) and Canon docs (`product-overview.md`, `ux-overview.md`, `tech-overview.md`, `module-snapshot.md`).
- `skill.md` — The master agent skill definition (read this for full operational detail).
- `implementation.md` — Guardrails for implementation agents.

### `.cicadas/` State Directory

```
.cicadas/
├── registry.json     # Source of truth for all active initiatives + feature branches + signals
├── index.json        # Append-only ledger of completed work
├── canon/            # Authoritative docs synthesized from code (NEVER edited manually; NEVER on feature branches)
├── drafts/           # Staging area for new initiatives before kickoff
├── active/           # Live specs driving current work
└── archive/          # Timestamped expired specs from completed initiatives
```

### Branching Model

| Prefix | Forks From | Registered | Purpose |
|--------|-----------|------------|---------|
| `initiative/` | `master` | Yes | Integration branch for a full initiative |
| `feat/` | `initiative/` | Yes | One partition of an initiative |
| `fix/` | `master` | Yes | Lightweight bug fix |
| `tweak/` | `master` | Yes | Lightweight enhancement (<100 LOC) |
| `task/` | `feat/` | No | Ephemeral; never registered |

### Initiative Lifecycle

1. **Emergence** — Draft specs in `.cicadas/drafts/{name}/` using subagent prompts in `emergence/`.
2. **Kickoff** — `kickoff.py` promotes drafts → `active/`, registers in `registry.json`, creates `initiative/{name}` branch.
3. **Feature Branches** — `branch.py` creates `feat/{name}`, declares module scope to detect overlaps.
4. **Inner Loop** — Task branches → Reflect (update active specs to match code) → PR to feature branch.
5. **Complete Initiative** — Merge initiative → `master`, Synthesize Canon on `master`, Archive specs.

### Key Invariants (Guardrails)

- **Never manually edit `registry.json`** — always use the scripts.
- **Never write to `.cicadas/canon/` on any branch** — Canon is only synthesized on `master` at initiative completion.
- **No code without a reviewed `tasks.md`** — agents must stop after Emergence and wait for Builder approval.
- **Reflect before every PR** — active specs must match code before merging any task branch.

### Test Conventions

Tests live in `tests/` and inherit from `CicadasTest` in `tests/base.py`. The base class:
- Creates a temp directory and `chdir`s into it.
- Sets up a minimal `.cicadas/` structure with empty `registry.json` and `index.json`.
- Provides `init_git()` for tests that need a real git repo.
- Cleans up in `tearDown`.

Scripts are imported directly by inserting `src/cicadas/scripts/` into `sys.path` at the top of `base.py`.
