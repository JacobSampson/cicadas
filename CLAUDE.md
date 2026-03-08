# CLAUDE.md

This file provides guidance to **Claude Code** (claude.ai/code) when working with code in this repository. It is not used by Cursor, Antigravity, Rovodev, or other agents — those environments use the Cicadas skill file (`SKILL.md` / `cicadas.mdc`) alone, which includes the same implementation guardrails.

## Python / Environment

Tests use **stdlib `unittest` + `coverage.py`** via the system `python3` (miniconda, 3.12). The `.venv` has Python 3.13 for running the scripts themselves but does **not** have pytest/coverage installed. Do **not** use `uv run` — the Atlassian PyPI mirror blocks package downloads.

## Commands

**Run all tests:**
```bash
PYTHONPATH=src/cicadas/scripts:tests python3 -m unittest discover -s tests/
```

**Run a single test file:**
```bash
PYTHONPATH=src/cicadas/scripts:tests python3 -m unittest tests.test_kickoff
```

**Run a single test:**
```bash
PYTHONPATH=src/cicadas/scripts:tests python3 -m unittest tests.test_kickoff.TestKickoff.test_basic_kickoff
```

**Run with coverage:**
```bash
PYTHONPATH=src/cicadas/scripts:tests python3 -m coverage run -m unittest discover -s tests/
python3 -m coverage report --include="src/cicadas/scripts/*" -m
```

**Lint:**
```bash
source .venv/bin/activate && ruff check src/ tests/
```

**Format:**
```bash
source .venv/bin/activate && ruff format src/ tests/
```

**CLI scripts** (activate venv first; scripts use `sys.path` to find `utils.py`):
```bash
source .venv/bin/activate
python src/cicadas/scripts/init.py
python src/cicadas/scripts/status.py
python src/cicadas/scripts/check.py
python src/cicadas/scripts/kickoff.py {name} --intent "..."
python src/cicadas/scripts/branch.py {name} --intent "..." --modules "mod1,mod2" --initiative {name}
python src/cicadas/scripts/signal.py "message"
python src/cicadas/scripts/archive.py {name} --type {branch|initiative}
python src/cicadas/scripts/update_index.py --branch {name} --summary "..."
python src/cicadas/scripts/create_lifecycle.py {name}  # optional: --pr-specs, --no-pr-initiatives, etc.
python src/cicadas/scripts/open_pr.py [--base branch]   # open PR from current branch (gh/glab/URL/fallback); blocks on BLOCK verdict
python src/cicadas/scripts/review.py [--initiative name]  # check review.md verdict (exit 0=PASS, 1=BLOCK, 2=not found)
python src/cicadas/scripts/prune.py {name} --type {branch|initiative}
python src/cicadas/scripts/abort.py
python src/cicadas/scripts/history.py [--output path]
```

## Architecture

Cicadas is a **spec-driven development methodology toolset** for human-AI teams. It consists of two parts:

1. **The Skill** (`src/cicadas/`) — portable CLI scripts and agent instructions that can be dropped into any project.
2. **The State** (`.cicadas/`) — filesystem-based state managed by the scripts, living in the project root.

### `src/cicadas/` Structure

- `scripts/` — CLI tools for the full initiative lifecycle. All share `utils.py` for root detection (`get_project_root()`), branch detection (`get_default_branch()`), and JSON I/O (`load_json`/`save_json`). `tokens.py` provides the append-only token usage log API (`init_log`, `append_entry`, `load_log`) used by `kickoff.py` and `branch.py`. `review.py` reads `review.md` verdict and returns exit codes; imported by `open_pr.py` for the merge gate check.
- `emergence/` — Markdown instructions for subagents (Clarify, UX, Tech, Approach, Tasks, Bootstrap, Bug-fix, Tweak, Code Review). These are **agent prompts**, not code.
- `templates/` — Markdown templates for specs (`prd.md`, `ux.md`, `tech-design.md`, `approach.md`, `tasks.md`, `buglet.md`, `tweaklet.md`, `review.md`) and Canon docs (`product-overview.md`, `ux-overview.md`, `tech-overview.md`, `module-snapshot.md`, `canon-summary.md`).
- `SKILL.md` — The master agent skill definition (read this for full operational detail).
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
4. **Inner Loop** — Task branches → Reflect (update active specs to match code) → PR to feature branch (if lifecycle has PR at tasks).
5. **Complete Initiative** — Merge initiative → `master` (open PR if lifecycle has PR at initiatives), Synthesize Canon on `master`, Archive specs.
6. **Lifecycle** — Per-initiative `lifecycle.json` (drafts/active) sets PR boundaries and steps; `status.py` reports Merged/Next (git-based).

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

Tests are run directly with `unittest` (not pytest); `PYTHONPATH=src/cicadas/scripts:tests` is set explicitly on the command line so all scripts are importable. `tests/conftest.py` exists for legacy pytest compatibility but is not used by the primary test runner.

**Testing bias — real filesystems over mocks:** Prefer tests that operate on real temporary filesystems and real git repositories over mocks. Cicadas scripts touch the filesystem and git directly; mocking these layers hides the integration bugs that matter. Mocks are acceptable only for pure logic with no I/O side-effects (e.g., string parsing, slug computation).
