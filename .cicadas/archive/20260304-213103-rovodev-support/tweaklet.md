
# Tweaklet: rovodev-support

## Intent
Add an install target for rovodev that creates a symlink under `.rovodev/skills/` on install, so the Cicadas skill can be used by rovodev without copying files.

## Proposed Change
- Add an install target (e.g. in Makefile, or a small script invoked by `make install-rovodev` / similar) that:
  - Resolves the project root (or cicadas skill location).
  - Ensures `.rovodev/skills/` exists (in repo root or user's chosen prefix).
  - Creates a symlink from `.rovodev/skills/cicadas` (or similar name) to the cicadas skill directory (e.g. `src/cicadas` or the skill path rovodev expects).
- Document the target in README or HOW-TO (one line).
- Keep change under 100 LOC; no new dependencies.

## Tasks
- [x] Implement tweak <!-- id: 10 -->
- [x] Verify functionality <!-- id: 11 -->
- [ ] Significance Check: Does this warrant a Canon update? <!-- id: 12 -->
