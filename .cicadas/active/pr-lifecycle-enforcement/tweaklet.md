# Tweaklet: PR Lifecycle Enforcement

## Intent

Three gaps in the PR lifecycle flow need to be closed:

1. **Approach asks too late**: The lifecycle/PR question currently comes at step 5 of the Approach emergence phase — after the approach doc is already drafted. The Builder should be asked about PRs *upfront* (step 1), so the answer can inform partitioning and sequencing decisions.

2. **Implementation agents ignore `Open PR` tasks**: `emergence/tasks.md` injects `- [ ] Open PR: ...` tasks at PR boundaries, but `implementation.md` has no rule saying "stop when you hit one." Agents treat them as ordinary checkboxes and merge without pausing.

3. **`SKILL.md` guardrails don't mention the pause rule**: The agent skill definition has no enforcement language for `Open PR` tasks either.

## Proposed Changes

### `src/cicadas/emergence/approach.md`
- Move the lifecycle/PR question to **step 1** (before any drafting), not step 5.
- Reframe: "Before we plan, how do you want to handle PRs for this initiative?" with the three options:
  - No PRs (merge directly at every boundary)
  - PRs at the final initiative merge only
  - PRs at every feature boundary + the initiative merge (default)
- After getting the answer, immediately run `create_lifecycle.py` with the appropriate flags, then proceed to plan the approach.

### `src/cicadas/implementation.md`
- Add **Rule 4b: Pause at `Open PR` Tasks**:
  - When executing a `tasks.md` checklist and the next task is `- [ ] Open PR: ...`, STOP.
  - Do NOT mark it complete. Do NOT merge. Do NOT proceed.
  - Open the PR using `open_pr.py`, present the PR URL to the Builder, and explicitly wait for confirmation that the PR has been merged before continuing.
  - Only after the Builder confirms the merge should the agent mark the task `- [x]` and continue.

### `src/cicadas/SKILL.md`
- In the **Guardrails** section: add a bullet for the `Open PR` task pause rule (mirrors `implementation.md`).
- In the **Inner Loop** description: note that `Open PR` tasks are hard stops, not automatic steps.

## Tasks
- [x] Move PR/lifecycle question to step 1 of `emergence/approach.md` <!-- id: 1 -->
- [x] Add Rule 4b (pause at Open PR tasks) to `implementation.md` <!-- id: 2 -->
- [x] Update `SKILL.md` guardrails and inner loop description <!-- id: 3 -->
- [ ] Significance Check: Does this warrant a Canon update? <!-- id: 4 -->
