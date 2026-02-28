# Release Notes

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

