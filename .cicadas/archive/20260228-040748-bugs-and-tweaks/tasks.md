# Tasks: bugs-and-tweaks

## Mode A: Foundation (Strict Phases)

### Phase 1: Definitions (Blocking)
- [ ] Update `src/cicadas/skill.md`: Add lightweight path definitions and rules <!-- id: 100 -->
- [ ] Create `src/cicadas/templates/buglet.md`: Minimal spec template <!-- id: 101 -->
- [ ] Create `src/cicadas/templates/tweaklet.md`: Minimal spec template <!-- id: 102 -->
- [ ] Create `src/cicadas/emergence/bug-fix.md`: Subagent for buglets <!-- id: 103 -->
- [ ] Create `src/cicadas/emergence/tweak.md`: Subagent for tweaklets <!-- id: 104 -->

### Phase 2: Orchestration (Sequential)
- [ ] Modify `src/cicadas/scripts/kickoff.py`: Support relaxed validation for fix/tweak <!-- id: 200 -->
- [ ] Modify `src/cicadas/scripts/branch.py`: Support direct-from-main branching for fix/tweak <!-- id: 201 -->
- [ ] Modify `src/cicadas/scripts/update_index.py`: Update branch tracking for fix/tweak <!-- id: 202 -->
- [ ] Modify `src/cicadas/scripts/status.py`: Update status reporting for fix/tweak <!-- id: 203 -->
- [ ] Modify `src/cicadas/scripts/archive.py`: Implement significance check and Reflect flow <!-- id: 204 -->

### Phase 3: Verification
- [ ] Run end-to-end dry run of a `fix/` task <!-- id: 300 -->
- [ ] Run end-to-end dry run of a `tweak/` task with Canon update <!-- id: 301 -->

---
_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
