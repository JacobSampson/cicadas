# Tweaklet: Emergence Consistency Check

## Intent
Add a cross-phase consistency check as the final step of emergence, after `tasks.md` is approved.
A subagent reads all five draft docs and surfaces internal contradictions as a structured list of
questions for the human — no autonomous resolution.

## Proposed Change

**New file: `src/cicadas/emergence/consistency-check.md`**
A subagent prompt that reads `.cicadas/drafts/{initiative}/` (all five docs) and checks for:
- tasks.md implying more scope than approach.md's partitions can contain
- tech-design.md dependencies not reflected in the partition DAG
- UX flows referencing features not in the PRD
- Any other cross-doc contradiction

Output is a numbered list of questions. If no issues found, confirm "all clear" and defer to kickoff.

**Edit: `src/cicadas/emergence/EMERGENCE.md`**
- Add step 5b "Consistency Check" to the workflow table
- Add node to mermaid diagram between Tasks and Kickoff

**Edit: `src/cicadas/emergence/tasks.md`**
- Add a note after the "Refine" step: once Builder approves tasks.md, run the Consistency Check
  subagent before proceeding to kickoff.

## Tasks
- [x] Write `src/cicadas/emergence/consistency-check.md` <!-- id: 10 -->
- [x] Edit `src/cicadas/emergence/EMERGENCE.md` to add step 5b <!-- id: 11 -->
- [x] Edit `src/cicadas/emergence/tasks.md` to reference the consistency check <!-- id: 12 -->
- [x] Significance Check: Does this warrant a Canon update? <!-- id: 13 --> No canon update needed.
