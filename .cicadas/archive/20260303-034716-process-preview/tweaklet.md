
# Tweaklet: Process Preview

## Intent
Orient the user at two key moments in the Cicadas workflow:
1. **At the start of emergence** (initiative, tweak, or bug fix): show what the spec phase steps are before diving in.
2. **After spec finalization**: show what the path from kickoff through implementation looks like.

This reduces confusion about "what happens next" and gives users a mental model of the process before they're in it.

## Proposed Change

### 1. Add a "Process Preview" step at the top of each emergence subagent

In `src/cicadas/emergence/tweak.md`, `bug-fix.md`, and `clarify.md`, add a **step 0** that instructs the agent to show the user a brief, formatted preview of the spec phase steps before starting.

- **Tweak**: `Define intent → Draft tweaklet.md → [Review] → Kickoff`
- **Bug Fix**: `Clarify bug → Analyze → Draft buglet.md → [Review] → Kickoff`
- **Initiative**: `Clarify (PRD) → UX → Tech Design → Approach → Tasks → [Review each] → Kickoff`

### 2. Add a "What's Next" step at the end of each emergence subagent

After the spec is approved (final review step), instruct the agent to show the user what happens next — the post-kickoff path through implementation.

- **Tweak / Bug Fix**: `Kickoff → Branch → Implement → (Significance check) → Merge → Archive`
- **Initiative**: `Kickoff → Feature branch(es) → Task branches → Reflect → PR per task → Merge feature → Merge initiative → Synthesize canon → Archive`

### Files to edit
- `src/cicadas/emergence/tweak.md`
- `src/cicadas/emergence/bug-fix.md`
- `src/cicadas/emergence/clarify.md`

## Tasks
- [ ] Add Process Preview (step 0) to `tweak.md` <!-- id: 10 -->
- [ ] Add Process Preview (step 0) to `bug-fix.md` <!-- id: 11 -->
- [ ] Add Process Preview (step 0) to `clarify.md` <!-- id: 12 -->
- [ ] Add What's Next message after spec approval in `tweak.md` <!-- id: 13 -->
- [ ] Add What's Next message after spec approval in `bug-fix.md` <!-- id: 14 -->
- [ ] Add What's Next message after spec approval in `clarify.md` <!-- id: 15 -->
- [ ] Significance Check: Does this warrant a Canon update? <!-- id: 16 -->

---
_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
