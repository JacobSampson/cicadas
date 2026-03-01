
# Buglet: archive-branch-cleanup

## Bug Description

`archive.py` deregisters an initiative from `registry["initiatives"]` but does not remove associated branches from `registry["branches"]`. After archiving an initiative, its linked `fix/` or `tweak/` (or `feat/`) branches remain as orphaned entries in the registry, showing up as false-active in `status.py`.

## Root Cause

`archive.py` line 38 only deletes from the targeted `registry_key` (`initiatives` or `branches`). When archiving an initiative, branches whose `initiative` field matches the archived name are not cleaned up.

## Fix

In `archive.py`, when `type_ == "initiative"`, after deregistering the initiative also remove all entries from `registry["branches"]` where `branch["initiative"] == name`.

Also remove the two currently orphaned entries (`tweak/project-history`, `fix/branch-active-dir`) from `.cicadas/registry.json`.

## Tasks

- [ ] Fix `archive.py`: deregister associated branches when archiving an initiative <!-- id: 10 -->
- [ ] Clean up orphaned registry entries for `tweak/project-history` and `fix/branch-active-dir` <!-- id: 11 -->
- [ ] Add/update test covering branch cleanup on initiative archive <!-- id: 12 -->
- [ ] Significance Check: Does this warrant a Canon update? <!-- id: 13 -->

---
_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
