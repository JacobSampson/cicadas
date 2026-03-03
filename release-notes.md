# Release Notes

## Unreleased

## Version 0.5.1
- **Code Review**: New optional agent operation (`emergence/code-review.md`) for spec-anchored evaluation of code diffs. Covers task completeness, acceptance criteria, architectural conformance, module scope, Reflect completeness, security (OWASP patterns), correctness (9 named bug patterns with explicit blocking thresholds), and code quality. Produces an ephemeral advisory report with tiered findings (Blocking / Advisory) and a `MERGE-READY` / `NEEDS-WORK` verdict. Supports feature branches (Full mode) and fix/tweak branches (Lightweight mode).
- **SKILL.md**: Added Code Review to Agent Operations, Agent Autonomy Boundaries table, Builder Commands (`"Code review"`, `"Review feature"`, `"Review fix"`, `"Review tweak"`), and quick reference table.
- **Lint fixes**: Resolved pre-existing `ruff` errors in `history.py` (`timezone.utc` → `UTC`, two long CSS lines) and `tests/test_init.py` (unused import).

## Version 0.5.0
- **Lifecycle & PRs**: Per-initiative `lifecycle.json` (in drafts/active) defines PR boundaries (specs, initiatives, features, tasks) and an ordered step list. Created during Approach via `create_lifecycle.py`; promoted at kickoff and archived with the initiative.
- **Status merge detection**: When `lifecycle.json` exists, `status.py` reports which branches are merged (git-based) and suggests the next lifecycle step (Merged/Next).
- **open_pr.py**: New script to open a PR from the current branch (tries `gh` → `glab` → Bitbucket URL → fallback). Host-agnostic; no API keys.
- **SKILL/HOW-TO/CLAUDE**: Updated Complete feature/initiative for PR-at-boundary wording, lifecycle step 5b, and create_lifecycle/open_pr in CLI references.
- **Requirement change**: Cicadas now requires **Python 3.11+** (was 3.13+). The scripts use stdlib only (e.g. `datetime.UTC`); the installer and docs have been updated accordingly.

## Version 0.4.0
- **New Feature**: Added `install.sh` — a single-command bash installer that checks for Python 3.12+, downloads Cicadas from the GitHub archive URL, extracts to `src/cicadas/` (configurable via `--dir`), and calls `init.py` to bootstrap `.cicadas/`.
- **Agent Integrations**: `--agent` flag supports `claude-code` (symlink at `.claude/skills/cicadas`), `antigravity` (symlink at `.agents/skills/cicadas`), and `cursor` (copies `SKILL.md` to `.cursor/rules/cicadas.mdc`). Interactive agent prompt when stdin is a tty; skipped gracefully in `curl | bash` context.
- **Update Workflow**: `--update` flag re-downloads and overwrites skill files without touching `.cicadas/` state or re-running init.
- **Docs**: `README.md` and `HOW-TO.md` updated with one-liner install, agent integration table, and update workflow.
- **Tests**: Added 2 tests to `test_init.py` covering hook installation loop and `__main__` entry point; `init.py` coverage 74% → 97%. Overall test coverage 83% → 84% (54 tests).
- **Canon**: Updated `product-overview.md` and `tech-overview.md` with installer feature, distribution architecture, and agent integration conventions.

## Version 0.3.5
- **Bug Fix**: Fixed `archive.py` leaving orphaned branch entries in `registry.json` after archiving an initiative; associated branches (matching `initiative` field) are now deregistered automatically.
- **Tests**: Added regression test `test_archive_initiative_deregisters_associated_branches` in `test_archive_status.py`.

## Version 0.3.4
- **New Script**: Added `src/cicadas/scripts/abort.py` — context-aware escape hatch that detects the current branch type (`tweak/`, `fix/`, `feat/`, `initiative/`) and rolls back the appropriate scope, prompting whether to move promoted active specs back to drafts or delete them entirely.
- **Skill Update**: Added `"Abort"` builder command and `abort.py` entry to the CLI Quick Reference in `SKILL.md`.
- **Docs**: Updated `README.md`, `HOW-TO.md`, `src/cicadas/README.md`, and `CLAUDE.md` to document the new command.
- **Tests**: Added `tests/test_abort.py` with 14 tests at 86% coverage.
- **Dev Dependencies**: Added `pytest` and `pytest-cov` to `pyproject.toml`.

## Version 0.3.3
- **Bug Fix**: Fixed `branch.py` creating orphaned nested active directories (e.g. `active/tweak/X`) for lightweight fix/tweak branches; active dirs now consistently use the initiative name (`active/{name}/`).
- **Test Infrastructure**: Added `tests/conftest.py` to ensure scripts dir is in `sys.path` before test collection, fixing test isolation failure.
- **Tests**: Added two regression tests for the active dir convention in `test_branch.py`.

## Version 0.3.2
- **New Script**: Added `src/cicadas/scripts/history.py` — generates a self-contained HTML timeline (`.cicadas/canon/history.html`) from archived specs and the index ledger.
- **Skill Update**: Added `"Project history"` / `"Generate history"` builder command and `history.py` entry to the CLI quick reference in `SKILL.md`.

## Version 0.3.1
- **Claude Code Integration**: Added `CLAUDE.md` with build/test/lint commands and codebase architecture overview.
- **Skill Registration**: Created `.claude/skills/` directory with a symlink to `src/cicadas/`, registering Cicadas as a native Claude Code skill.
- **SKILL.md Compliance**: Renamed `skill.md` to `SKILL.md` per Anthropic convention; fixed missing opening `---` frontmatter fence.
- **SKILL.md Improvements**: Added `allowed-tools`, `argument-hint`, and trigger-keyword-style `description` for reliable auto-invocation.
- **SKILL.md Bug Fixes**: Corrected duplicate `emergence/` directory tree (scripts were misplaced), removed orphaned Bootstrap/Synthesis block, and added `{cicadas-dir}` definition note.

## Version 0.3.0
- **Lightweight Paths (Bugs & Tweaks)**: Introduced streamlined workflows for simple bug fixes and small tweaks: `fix/` and `tweak/` branches (fork from main), minimal specs (`buglet.md`, `tweaklet.md`), and emergence subagents (Bug-fix, Tweak). Scripts updated to support relaxed validation, direct-from-main branching, and status/history for fix/tweak.
- **Test Coverage**: Achieved >75% code coverage (83% overall) for all core scripts.
- **Mock-Free Testing**: Refactored the test suite to use real file system operations and Git scaffolding instead of mocks.
- **Linting & Formatting**: Integrated `ruff` and `pre-commit` hooks for automated code quality checks.
- **Refactoring**: Renamed `signal.py` to `signalboard.py` to resolve Python standard library collisions.
- **Reliability**: Fixed internal bugs in `update_index.py` and improved JSON serialization for `Path` objects.

## Version 0.2.1
- Renamed the core skill directory from `scripts/chorus/` to `src/cicadas/`.
- Created an Antigravity skill symlink in `.agents/skills/cicadas` pointing to the new `src/cicadas/` location.
- Updated documentation (`README.md`) to reflect the new paths and branding changes from Chorus to Cicadas.
- Updated all skill files to use relative paths within the skill.
- Created a comprehensive README instruction file

