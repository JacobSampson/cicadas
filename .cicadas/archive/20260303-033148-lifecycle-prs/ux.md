# UX Design: Lifecycle and Pull Requests

## Progress

- [x] Design Goals & Constraints
- [x] User Journeys & Touchpoints
- [x] Information Architecture
- [x] Key User Flows
- [x] UI States
- [x] Copy & Tone
- N/A Visual Design Direction (CLI/docs only)
- [x] UX Consistency Patterns
- N/A Responsive & Accessibility (CLI/docs only)

---

## Design Goals & Constraints

**Primary goal:** Builders and agents have a single, clear process script (lifecycle) per initiative and know when to open PRs vs merge directly; opening a PR and discovering completion work the same way regardless of host (GitHub, GitLab, Bitbucket, local).

**Design constraints:**
- CLI and markdown/docs only; no new UI application.
- Must work without GitHub/GitLab/Bitbucket APIs (git-only completion detection).
- Per-initiative configuration only; no PR/lifecycle policy in global config.

**Skip condition:** N/A — This initiative is methodology/CLI; “UX” here means builder and agent experience (flows, clarity, messaging).

---

## User Journeys & Touchpoints

### Builder — Setting up PR and lifecycle for an initiative

**Entry point:** During or after drafting approach (Emergence phase).  
**First touchpoint:** Prompt or step: “Will you be doing PRs?” → if yes, “At which boundaries?” with defaults (specs: no, initiatives: yes, features: yes, tasks: no).  
**Key moment:** Builder sees the resulting lifecycle (ordered steps) and knows the agent will follow it; they can hand off “complete feature” / “complete initiative” with confidence that PR will be opened when configured.  
**Exit state:** lifecycle.json (and optional approach note) stored in drafts; at kickoff, lifecycle is promoted to active.  
**Pain points to design around:** Don’t make approach phase feel like a long form; keep to one “use PRs?” and four boundary toggles with clear defaults.

### Agent — Following lifecycle and opening PRs

**Entry point:** Agent reads active specs and lifecycle for current initiative.  
**First touchpoint:** Lifecycle lists next step (e.g. “open PR to initiative”). Agent runs helper or follows docs (gh/glab/URL/fallback).  
**Key moment:** Agent runs status (or “what’s next”); script reports “branch X merged into Y” and “Next: complete initiative.”  
**Exit state:** Agent proceeds to next lifecycle step without needing host API or human to say “I merged.”  
**Pain points to design around:** Clear fallback when no CLI (e.g. “Push your branch and open a Merge Request in your host’s UI”); no assumption of GitHub.

### Builder on Bitbucket or local git

**Entry point:** Same as first journey; PR boundaries and lifecycle are still configured.  
**First touchpoint:** “Open PR” step results in Bitbucket URL or “merge locally / use your team’s process.”  
**Key moment:** Completion is still detected via git; status shows “merged” and next step.  
**Exit state:** Same as other hosts — no second-class experience.

---

## Information Architecture

- **Lifecycle file:** Single source of truth for “what steps, in what order” for the initiative. Referenced by SKILL, status, and any helper.
- **PR boundaries:** Stored in lifecycle (or top of approach); not in config.json. Read when generating default lifecycle and when deciding “open PR” vs “merge directly.”
- **Docs:** SKILL describes PR-at-boundary and lifecycle-driven flow; HOW-TO/CLAUDE mention lifecycle and host-agnostic PR/open/merge detection.

---

## Key User Flows

1. **Approach → lifecycle**
   - Finish approach (partitions, etc.).
   - Ask: “Use PRs?” → if yes, ask four boundaries (defaults: no, yes, yes, no).
   - Create/update lifecycle.json with ordered steps and PR steps where enabled.
   - Optional: short note at top of approach (“Lifecycle: see lifecycle.json” or “PRs at initiatives and features”).

2. **Kickoff**
   - kickoff.py promotes drafts → active; lifecycle.json is promoted with other specs.
   - No change to builder flow except lifecycle is now in active.

3. **During initiative — “What’s next?”**
   - Builder or agent runs status (or dedicated command).
   - Script: git fetch; for each known branch pair (e.g. feat/X → initiative/Y), check if source merged into target.
   - If merged, report “feat/X → initiative/Y: merged” and “Next: [next lifecycle step].”
   - Agent uses this to continue without human saying “I merged.”

4. **Opening a PR**
   - Lifecycle step says “open PR.”
   - If helper exists: try gh, then glab, then Bitbucket URL, else fallback message.
   - If no helper: docs say “push, then open PR in your host’s UI” or “merge locally” for local repos.

---

## UI States

- **No lifecycle yet:** Approach not finalized; no lifecycle.json. After approach + PR questions, lifecycle appears in drafts.
- **Lifecycle in drafts:** Visible in drafts/{name}/; at kickoff, copied to active.
- **Lifecycle in active:** Agent and status use it for “next step” and PR vs merge.
- **After archive:** Lifecycle archived with initiative specs; historical record only.

(No graphical UI; “states” are presence/absence of lifecycle and branch merge state.)

---

## Copy & Tone

- **Approach-phase prompts:** Short and clear. “Will you be doing PRs for this initiative?” “At which boundaries? (defaults: initiatives and features only)”
- **Fallback when no PR CLI:** “Push your branch and open a Pull Request in your host’s UI (GitHub, GitLab, Bitbucket), or merge locally if you’re not using PRs.”
- **Status when merged:** “feat/foo → initiative/bar: merged. Next: Complete initiative” (or next step from lifecycle).
- **Tone:** Instructional, host-agnostic, no jargon beyond “PR,” “merge,” “lifecycle.”

---

## UX Consistency Patterns

- All “open PR” behavior respects the per-initiative PR boundaries stored in lifecycle (or approach).
- All “is it merged?” behavior uses git only; same message shape regardless of host.
- Lifecycle step names and ids are stable so agents and docs can refer to them consistently.

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
