# Release Notes

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

