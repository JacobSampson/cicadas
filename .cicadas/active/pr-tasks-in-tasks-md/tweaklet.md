
# Tweaklet: PR Tasks in tasks.md

## Intent
When a builder says "yes, do PRs at feature/initiative boundaries" during the Approach phase, that decision lives in `lifecycle.json`. But the implementation agent executing tasks.md never sees a task that says "open a PR here" — so it merges silently without pausing.

The fix: the Tasks emergence agent reads `lifecycle.json` and appends explicit `[ ] Open PR` tasks at each configured boundary, making the PR step a visible, pauseable task in the builder-approved checklist.

## Proposed Change

**`src/cicadas/emergence/tasks.md`** — Add step 6 to the Process section:
- After drafting all implementation tasks, read `lifecycle.json` from `drafts/{initiative}/`.
- For each step with `opens_pr: true` (i.e., `complete_feature` when `pr_boundaries.features: true`, and `complete_initiative` when `pr_boundaries.initiatives: true`), append a PR task at the end of the relevant partition group or at the end of tasks.md.
- Format: `- [ ] Open PR: {branch} → {target} and await merge approval before continuing <!-- id: PR-{step_id} -->`

## Tasks
- [x] Kick off tweak branch <!-- id: 10 -->
- [ ] Update `emergence/tasks.md` with lifecycle.json PR task step <!-- id: 11 -->
- [ ] Verify against lifecycle.json schema (both `pr_boundaries` flags and `opens_pr` on steps) <!-- id: 12 -->
- [ ] Significance Check: Does this warrant a Canon update? <!-- id: 13 -->
