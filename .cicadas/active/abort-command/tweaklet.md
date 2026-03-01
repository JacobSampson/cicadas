
# Tweaklet: abort-command

## Intent
Add a context-aware `abort` command that acts as an escape hatch — detecting the current git branch type and rolling back the appropriate scope, with a prompt for how to handle any promoted specs.

## Proposed Change

### 1. New script `src/cicadas/scripts/abort.py`
- Reads the current git branch and detects its type (`tweak/`, `fix/`, `feat/`, `initiative/`)
- **For `tweak/` or `fix/`**:
  - Deletes the branch and deregisters from `registry.json` (delegates to `prune.py` logic)
  - If specs exist in `.cicadas/active/{name}/`, prompts the user:
    - `[D] Move docs back to drafts`
    - `[X] Delete docs entirely`
- **For `feat/`**:
  - Prompts the user for scope:
    - `[F] Abort just this feature branch`
    - `[I] Abort the entire initiative`
  - **(F) Abort feature**: prunes the feature branch; prompts on docs for that feature's active specs
  - **(I) Abort initiative**: prunes the feature branch, then the initiative branch; prompts on docs for the full initiative's active specs
- **For any other branch** (e.g., `master`, `task/`): prints "Nothing to abort from this branch." and exits cleanly

### 2. Update `src/cicadas/skill.md`
- Add `abort` to the Builder Commands table
- Add `abort.py` to the CLI Quick Reference table

### 3. Update `CLAUDE.md`
- Add `abort.py` to the CLI scripts list

## Tasks
- [x] Implement `src/cicadas/scripts/abort.py` <!-- id: 10 -->
- [x] Update `src/cicadas/skill.md` <!-- id: 11 -->
- [x] Update `CLAUDE.md` <!-- id: 12 -->
- [x] Significance Check: No Canon update warranted — additive script only <!-- id: 13 -->

---
_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
