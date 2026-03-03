# Tasks: Lifecycle and Pull Requests

## Mode B: Feature (Vertical Slices)

### Partition 1: Lifecycle artifact → `feat/lifecycle-artifact`

- [x] Define lifecycle.json schema (pr_boundaries, steps array with id, name, description, optional opens_pr) and document in tech-design or a short schema doc <!-- id: 1 -->
- [x] Add default lifecycle template (JSON or generator) for standard initiative flow with optional PR steps <!-- id: 2 -->
- [x] Add approach-phase flow: prompt “use PRs?” and four boundaries (specs, initiatives, features, tasks); write lifecycle.json to drafts/{name}/ <!-- id: 3 -->
- [x] kickoff.py: copy lifecycle.json from drafts to active when present <!-- id: 4 -->
- [x] archive.py: include lifecycle.json in archive directory when archiving active/{name} <!-- id: 5 -->
- [x] Tests: kickoff with lifecycle.json in drafts → lifecycle in active <!-- id: 6 -->
- [x] Tests: archive active with lifecycle.json → lifecycle in timestamped archive <!-- id: 7 -->

### Partition 2: Status, merge detection, and docs → `feat/status-and-docs`

- [x] Implement merge detection: given branch pair (source, target), run git fetch and determine if source is merged into target <!-- id: 10 -->
- [x] status.py: when active lifecycle.json exists for current initiative, compute merged branches and next lifecycle step; append to output <!-- id: 11 -->
- [x] SKILL.md: add lifecycle and PR boundaries (approach-phase questions, lifecycle as process script); update Complete feature / Complete initiative for PR and lifecycle <!-- id: 12 -->
- [x] SKILL.md: document host-agnostic open PR and git-based completion detection <!-- id: 13 -->
- [x] HOW-TO.md and CLAUDE.md: mention lifecycle.json, PR boundaries, “next step” and merge status <!-- id: 14 -->
- [x] Tests: status with lifecycle and merged-branch detection (mock or real git) <!-- id: 15 -->

### Partition 3: Optional open-PR helper → `feat/open-pr-helper`

- [x] Add open_pr.py: try gh, then glab, then Bitbucket URL from remote, else fallback message <!-- id: 20 -->
- [x] SKILL and HOW-TO: document when and how to use open_pr, behavior per host, fallback <!-- id: 21 -->
- [x] Tests: open_pr fallback when no gh/glab; optional test for Bitbucket URL when remote is Bitbucket <!-- id: 22 -->

---

## Reflect (post-implementation)

**As-built vs spec:**
- **kickoff/archive**: No script changes; existing behavior (move all draft files to active, move entire active dir to archive) already includes lifecycle.json.
- **Merge detection**: Uses local refs only (`git merge-base --is-ancestor`); no `git fetch` in status.py. User may run `git fetch` before status if remote merge state is needed.
- **open_pr.py**: Implements gh → glab → Bitbucket URL → fallback; supports `--base` and `--body-file`. All three partitions merged to initiative/lifecycle-prs.

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
