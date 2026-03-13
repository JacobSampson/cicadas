# Buglet: Clarify Standardization

## Problem Description
Starting an initiative, tweak, or bug currently has no single repeatable flow. Agents and Builders get inconsistent prompts (what to ask first, whether to create lifecycle, when to draft). That leads to skipped steps, wrong order, or missing PR preference—making the "start" experience unpredictable.

## Reproduction Steps
1. Ask an agent to "start an initiative" (or "start a tweak" / "start a bug").
2. Observe which questions are asked and in what order.
3. Compare across sessions or agents—flow and checklist differ; lifecycle/PR preference may be omitted.

## Proposed Fix
Define and document a **standard start flow** used for all three entry points (initiative, tweak, bug): same sequence of questions (name, intent/description, PR preference), same creation order (lifecycle when applicable, then draft specs), and a single checklist so agents and docs (e.g. HOW-TO, emergence) reference one flow. Implement in agent instructions and/or scripts so the flow is repeatable.

The flow should ALWAYS be:
1. Name the initiative / tweak / bug
2. Create the draft folder with initial files (e.g. emergence-config.json)
3. Determine source of requirements (Q&A, doc, Loom)
4. Determine pace (for initiatives) - Section, Doc, All
5. Determine PRs - Feature, Initiative, None

Then start collecting requirements via Q&A, doc or Loom. 

No matter how it's entered, this flow should be run.

If the user provides information up front, you can pre-populate their input but still verify. For example, if the user says "Start a tweak called XYZ", still do step 1 and ask "What is the name of this tweak? 1. XYZ, 2. Other (enter the name)"

## Tasks
- [x] Implement fix <!-- id: 1 -->
- [x] Verify fix with the test case <!-- id: 2 -->
- [x] Significance Check: Does this warrant a Canon update? <!-- id: 3 --> No — process/agent instructions only; canon remains product/tech/UX from code.
