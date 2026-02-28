
# Buglet: branch-active-dir

## Bug Description

`branch.py` unconditionally creates `.cicadas/active/{branch-name}/` using the full branch name, including any prefix (e.g. `tweak/`, `fix/`). For lightweight branches this produces an orphaned nested directory (e.g. `.cicadas/active/tweak/project-history/`) because `kickoff.py` already created the correct active dir at `.cicadas/active/{initiative-name}/`.

## Root Cause

`branch.py` line 65:
```python
(cicadas / "active" / name).mkdir(parents=True, exist_ok=True)
```
`name` for a lightweight branch is `tweak/project-history`, so `parents=True` silently creates the nested path `.cicadas/active/tweak/project-history/`.

## Fix

In `branch.py`, replace `name` with `initiative` (already available as a parameter) when resolving the active dir path. If no initiative is provided, fall back to stripping the type prefix from the branch name. This makes all branch types use the same convention: `active/{initiative-name}/`.

Also clean up the existing orphaned directories in `.cicadas/active/`.

## Tasks

- [ ] Fix `branch.py`: skip `active/` dir creation for `fix/` and `tweak/` branches <!-- id: 10 -->
- [ ] Remove orphaned dirs: `.cicadas/active/tweak/`, `.cicadas/active/fix/`, `.cicadas/active/definitions/`, `.cicadas/active/orchestration/` <!-- id: 11 -->
- [ ] Add/update test covering lightweight branch active dir behaviour <!-- id: 12 -->
- [ ] Significance Check: Does this warrant a Canon update? <!-- id: 13 -->

---
_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
