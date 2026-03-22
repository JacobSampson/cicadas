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

**Cicadas CLI** (unified entry point; activate venv if using editable install):
```bash
source .venv/bin/activate   # optional
cicadas init
cicadas status
cicadas check
cicadas kickoff {name} --intent "..."
cicadas branch {name} --intent "..." --modules "mod1,mod2" --initiative {name}
cicadas signal "message"
cicadas archive {name} --type branch   # or initiative
cicadas update-index --branch {name} --summary "..."
cicadas lifecycle {name}   # optional: --pr-specs, --no-pr-initiatives, etc.
cicadas open-pr [--base branch]   # gh/glab/URL/fallback; blocks on BLOCK verdict
cicadas review [--initiative name]   # review.md verdict: 0=PASS, 1=BLOCK, 2=not found
cicadas prune {name} --type branch   # or initiative
cicadas abort
cicadas history [--output path]
cicadas validate-skill {slug-or-path}
cicadas publish-skill {slug} [--publish-dir DIR] [--symlink] [--force]
cicadas refresh-wiki
```

From a repo checkout **without** installing the package: `PYTHONPATH=src python -m cicadas.scripts.cli <subcommand> [...]` (same flags as `cicadas`). Individual `scripts/*.py` files remain for tests and backward compatibility but are not the documented interface.

## Architecture

Cicadas is a **spec-driven development methodology toolset** for human-AI teams. It consists of two parts:

1. **The Skill** (`src/cicadas/`) — portable **`cicadas` CLI** (`scripts/cli.py` + modules) and agent instructions that can be dropped into any project.
2. **The State** (`.cicadas/`) — filesystem-based state managed by the CLI, living in the project root.

### `src/cicadas/` Structure

- `scripts/` — Implementation of the **`cicadas`** CLI (`cli.py` dispatches to the same modules). All share `utils.py` for root detection (`get_project_root()`), branch detection (`get_default_branch()`), and JSON I/O (`load_json`/`save_json`). `tokens.py` provides the append-only token usage log API (`init_log`, `append_entry`, `load_log`) used by kickoff and branch. `review.py` reads `review.md` verdict and returns exit codes; used by `open_pr` for the merge gate check. `validate_skill.py` checks an Agent Skill directory against the spec (name charset/length/dir-match, description ≤1024 chars, frontmatter delimiters) using stdlib regex. `skill_publish.py` copies or symlinks an active skill to its `publish_dir` with a pre-publish validation gate.
- `emergence/` — Markdown instruction modules (Clarify, UX, Tech, Approach, Tasks, Bootstrap, Bug-fix, Tweak, Eval Spec, Code Review, Skill Create, Skill Edit) — inline role files read in the current context window; no separate agent process is spawned. **start-flow.md** defines the standard start flow (name → draft folder → **Building on AI?** → requirements source/pace → publish destination for skills → PR preference) run first for initiative, tweak, bug, or skill. Building on AI and eval status are stored in `emergence-config.json` (skills skip the eval-status follow-up — Post-MVP). **skill-create.md** drives dialogue-driven Agent Skill authoring: clarifying dialogue, SKILL.md + bundled files generation, `eval_queries.json` draft, kickoff + validate. **skill-edit.md** handles targeted edits: one diagnostic question, minimum-change before/after proposal, validate. For initiatives building on AI with "will do" evals, **eval-spec.md** guides creation of `eval-spec.md` in drafts/active after PRD/UX/Tech; Approach asks eval placement (before build / in parallel). For tweaks/bugs, a light-touch reminder can be added to the tweaklet/buglet. Cicadas does not run evals. Clarify supports intake via Q&A, a requirements doc (`drafts/{initiative}/requirements.md`), or a Loom transcript (`drafts/{initiative}/loom.md`). These are **agent prompts**, not code.
- `templates/` — Markdown templates for specs (`prd.md`, `ux.md`, `tech-design.md`, `approach.md`, `tasks.md`, `buglet.md`, `tweaklet.md`, `eval-spec.md`, `review.md`, `skill-SKILL.md`) and Canon docs (`product-overview.md`, `ux-overview.md`, `tech-overview.md`, `module-snapshot.md`, `canon-summary.md`).
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
| `skill/` | `master` | Yes | Agent Skill authoring |
| `task/` | `feat/` | No | Ephemeral; never registered |

### Initiative Lifecycle

1. **Emergence** — Draft specs in `.cicadas/drafts/{name}/` using instruction modules in `emergence/`.
2. **Kickoff** — `cicadas kickoff` promotes drafts → `active/`, registers in `registry.json`, creates `initiative/{name}` branch.
3. **Feature Branches** — `cicadas branch` creates `feat/{name}`, declares module scope to detect overlaps.
4. **Inner Loop** — Task branches → Reflect (update active specs to match code) → PR to feature branch (if lifecycle has PR at tasks).
5. **Complete Initiative** — Merge initiative → `master` (open PR if lifecycle has PR at initiatives), Synthesize Canon on `master`, Archive specs.
6. **Lifecycle** — Per-initiative `lifecycle.json` (drafts/active) sets PR boundaries and steps; `cicadas status` reports Merged/Next (git-based).

### Key Invariants (Guardrails)

- **Never manually edit `registry.json`** — always use the `cicadas` CLI.
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
