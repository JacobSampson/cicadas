# PRD: Lifecycle and Pull Requests

## Progress

- [x] Executive Summary
- [x] Project Classification
- [x] Success Criteria
- [x] User Journeys
- [x] Scope & Phasing
- [x] Functional Requirements
- [x] Non-Functional Requirements
- [x] Open Questions
- [x] Risk Mitigation

## Executive Summary

Make **pull requests** and a **per-initiative lifecycle** first-class in Cicadas. Today PRs are only explicit at the task→feature boundary; feature→initiative and initiative→main are described as direct merges. We will add: (1) configurable PR boundaries (specs, initiatives, features, tasks) chosen during the approach phase; (2) a per-initiative **lifecycle.json** that defines a timeline and task list (kickoff → features → test → reflect → commit → push → PR → merge…) so agents and builders share one process script; (3) host-agnostic mechanics for opening PRs (GitHub/GitLab/Bitbucket/CLI or URL fallback) and git-based detection of PR completion so the agent knows “what’s next” without host APIs.

### What Makes This Special

- **Lifecycle as contract** — One ordered list of steps per initiative; agents refer to it and can infer “next step” from git/registry state.
- **PR policy per initiative** — Stored with the approach (or lifecycle), not in global config; supports teams that want PRs at initiative/feature (default) and optional at task/specs.
- **Host-agnostic** — Works with GitHub, GitLab, Bitbucket, or local git; open via CLI when available, else URL or “push and open in UI”; completion detected via git only.

## Project Classification

**Technical Type:** Developer tool / methodology orchestrator  
**Domain:** DevOps / workflow / spec-driven development  
**Complexity:** Medium — new artifact (lifecycle.json), approach-phase prompts, optional helper script, status/merge detection.  
**Project Context:** Brownfield — Cicadas already has SKILL, scripts, registry, drafts/active/archive.

## Success Criteria

### User Success

A builder or agent achieves success when:

1. **PR boundaries are explicit** — They can answer “will we use PRs?” and “at which boundaries?” during approach; that choice is persisted and used by the workflow.
2. **Lifecycle is actionable** — They see an ordered list of steps (kickoff initiative, kickoff features, test, reflect, commit, push, PR, merge…) and can follow or check off; the agent can infer “next step” from current state.
3. **PR open works everywhere** — On GitHub/GitLab they can open a PR via CLI or documented URL; on Bitbucket or local they get a clear fallback (URL or “push and open in UI” / “merge locally”).
4. **Completion is discoverable** — The agent finds out a PR was merged when it next runs status (or a dedicated check), via git fetch + merge detection, with no host API dependency.

### Technical Success

- lifecycle.json exists per initiative (drafts and active), promoted at kickoff and archived with the initiative.
- Approach-phase flow captures PR boundary choices and produces or updates lifecycle (and optionally a short note in approach).
- SKILL and docs describe PR-at-boundary behavior and lifecycle-driven “what’s next”; agents use lifecycle + git state.
- Optional open-PR helper: best-effort gh/glab, Bitbucket URL, or fallback message; no API keys in Cicadas.
- Status (or a small script) can report “branch X merged into Y” and suggest next lifecycle step.

### Measurable Outcomes

- All PR boundaries (specs, initiatives, features, tasks) documented and configurable per initiative.
- At least one default lifecycle template (standard initiative flow) that includes optional PR steps.
- Completion detection works with only git (fetch + merge check) against any remote or local.

## User Journeys

### Journey 1: Builder — Configuring PRs and lifecycle for an initiative

Builder is drafting the approach for a new initiative. They are asked “Will you be doing PRs?” If yes, they are asked at which boundaries (specs: no, initiatives: yes, features: yes, tasks: no by default). That is stored with the initiative (lifecycle or approach). They get a lifecycle timeline (e.g. kickoff initiative → kickoff features → … → PR → merge) they can follow; the agent uses it to suggest “next step” and to know when to open a PR vs merge directly.

**Requirements Revealed:** Approach-phase PR questions; lifecycle.json (or equivalent) per initiative; lifecycle as timeline/task list; docs/skill reference lifecycle and PR boundaries.

### Journey 2: Agent — Opening a PR and learning it’s merged

Agent is on a feature branch and the lifecycle says “open PR to initiative.” It runs the open-PR helper (or follows docs): if `gh`/`glab` exists, use it; else Bitbucket URL or “push and open in UI.” Later, the agent runs status (or “what’s next”); the script does git fetch and checks if the feature branch is merged into the initiative branch. It reports “PR merged” and suggests the next lifecycle step (e.g. complete initiative or next feature).

**Requirements Revealed:** Host-agnostic open-PR (CLI/URL/fallback); git-only merge detection; status or dedicated command that reports merged state and next step.

### Journey 3: Builder on Bitbucket or local git

Builder uses Bitbucket or a local-only repo. They still get lifecycle and PR boundary choices. “Open PR” means: open a Merge Request in Bitbucket (URL or UI), or “merge locally / use your team’s review process.” Completion is still detected via git (branch merged); no webhooks or API required.

**Requirements Revealed:** No dependency on GitHub/GitLab APIs; URL or instructions for Bitbucket; local = “merge locally” or “request merge” with clear messaging.

## Scope

### MVP — Minimum Viable Product (v1)

**Core Deliverables:**

- lifecycle.json (or equivalent) per initiative: schema (ordered steps; optional attributes e.g. opens_pr, reflect_before); lives in drafts/{name}/ and active/{name}/; promoted at kickoff, archived with initiative.
- Approach-phase: ask “use PRs?” and, if yes, PR at specs (default no), initiatives (default yes), features (default yes), tasks (default no); persist in lifecycle or top of approach.
- Default lifecycle template: standard initiative flow (kickoff initiative → kickoff features → feature work loop → complete feature → complete initiative) with PR steps when enabled.
- SKILL and docs updated: PR boundaries, lifecycle as process script, “what’s next” from lifecycle + git; open PR = host-agnostic (CLI/URL/fallback); completion = git-based detection.
- Status (or small script): ability to report “branch X merged into Y” and suggest next lifecycle step (git fetch + merge check only).

**Quality Gates:**

- No new dependency on GitHub/GitLab/Bitbucket APIs for core behavior.
- lifecycle and PR choices are per-initiative, not in global config.

### Growth Features (Post-MVP)

- Optional open_pr helper script: `gh` / `glab` / Bitbucket URL / fallback.
- Persisted “completed steps” in lifecycle (e.g. completed: []) or minimal state for checkoffs; v1 can rely on inference from git/registry only.
- fix/tweak lifecycle: optional fifth boundary or doc rule.

### Vision (Future)

- Webhook-driven “PR merged” event writing state file for real-time agent awareness (optional, infra-dependent).

## Functional Requirements

### 1. Lifecycle artifact

**FR-1.1:** Per-initiative lifecycle file (e.g. lifecycle.json) exists in `.cicadas/drafts/{name}/` and `.cicadas/active/{name}/`; created/updated during or after approach; promoted to active at kickoff; archived with the initiative.  
- Format: ordered list of steps; each step has id, name, optional description, optional attributes (e.g. opens_pr, reflect_before).

**FR-1.2:** A default lifecycle template exists that models the standard initiative flow (kickoff initiative, kickoff features, feature work, complete feature, complete initiative) and can include PR steps when PRs are enabled at those boundaries.

**FR-1.3:** Agents and docs refer to the lifecycle as the process script for “what to do next”; “next step” can be inferred from current git/registry state (no mandatory persisted checkoffs in v1).

### 2. PR boundaries (approach phase)

**FR-2.1:** During the approach phase (or when finalizing approach), the user is asked: “Will you be doing PRs?” If yes, ask at which boundaries: specs (default no), initiatives (default yes), features (default yes), tasks (default no).

**FR-2.2:** These choices are stored per initiative (in lifecycle file or at top of approach), not in `.cicadas/config.json`.

**FR-2.3:** SKILL and docs describe that PRs can be required or optional at each boundary and that the lifecycle reflects these choices (e.g. “open PR” step only when that boundary has PR enabled).

### 3. Opening PRs (host-agnostic)

**FR-3.1:** Documentation describes how to open a PR after push: use host CLI (e.g. gh, glab) if available; otherwise open in host UI or, for Bitbucket, use a documented URL pattern; for local-only, “merge locally” or “request review” per team process.

**FR-3.2:** Optional helper (script or doc step): if gh/glab in PATH, run it with sensible defaults; else if Bitbucket remote/context, print “new PR” URL; else print fallback message. No API keys or secrets in Cicadas.

### 4. Detecting PR completion

**FR-4.1:** Completion of a PR (merge of source branch into target) is detectable using only git: fetch (if remote), then check whether source is merged into target (e.g. commit reachable or branch deleted). Works for GitHub, GitLab, Bitbucket, and local.

**FR-4.2:** status.py or a dedicated command reports “branch X merged into Y” when applicable and suggests the next lifecycle step (e.g. “Complete initiative” or “Next: complete next feature”).

## Non-Functional Requirements

- **Compatibility:** Works with existing kickoff, branch, archive, update_index scripts; no breaking change to registry or config schema for existing users.
- **Portability:** No hard dependency on GitHub or GitLab; Bitbucket and local git are supported via URL/instructions and git-only detection.
- **Maintainability:** lifecycle schema is simple (list of steps + optional attributes); easy to extend later (e.g. repeat, sub-steps, completed array).

## Open Questions

- Exact lifecycle.json schema (flat steps vs nested “feature_loop”) — v1 can use flat list with one “feature work (per feature)” step and describe the loop in text.
- Whether to add a “lifecycle” subsection in approach.md that references or embeds the PR boundaries — or keep only in lifecycle.json.

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep (full state machine for lifecycle) | Medium | High | Ship v1 with ordered list + inference; no mandatory persisted checkoffs. |
| Host-specific bugs in open-PR helper | Medium | Low | Helper is optional; fallback is always “push and open in UI” or URL. |
| Approach-phase flow becomes heavy | Low | Medium | Keep questions to 4 boundaries + one “use PRs?”; defaults reduce friction. |

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
