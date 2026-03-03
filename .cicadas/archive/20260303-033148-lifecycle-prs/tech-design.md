# Tech Design: Lifecycle and Pull Requests

## Progress

- [x] Overview & Context
- [x] Tech Stack & Dependencies
- [x] Project / Module Structure
- [x] Architecture Decisions (ADRs)
- [x] Data Models
- [x] API & Interface Design
- [x] Implementation Patterns & Conventions
- [x] Security & Performance
- [x] Implementation Sequence

---

## Overview & Context

**Summary:** This initiative adds a per-initiative **lifecycle** artifact (timeline + optional PR boundaries) and host-agnostic mechanics for opening PRs and detecting merge completion. The lifecycle is an ordered list of steps (e.g. kickoff initiative → kickoff features → test → reflect → commit → push → PR → merge) that agents and builders share; PR-at-boundary choices are captured during the approach phase and stored with the initiative (lifecycle file or approach), not in global config. Opening PRs uses host CLI (gh/glab) when available, else URL or fallback; completion is detected via git only (merge-base check; no fetch in status.py — user may run `git fetch` before status if needed).

### Cross-Cutting Concerns

1. **Per-initiative only** — lifecycle and PR boundaries live under drafts/{name}/ and active/{name}/; never in .cicadas/config.json.
2. **Git-only completion** — No dependency on GitHub/GitLab/Bitbucket APIs for detecting “PR merged”; use git fetch and merge reachability.
3. **Optional helper** — Any script that opens PRs is best-effort; fallback is always documented (push + open in UI, or merge locally).

### Brownfield Notes

- Existing scripts (kickoff, branch, archive, update_index, status) remain; we add or extend behavior (e.g. kickoff copies lifecycle.json; status can report merge state and next step).
- SKILL and docs are updated to describe lifecycle and PR boundaries; no breaking change to registry schema.
- .cicadas/config.json is unchanged for this initiative; it stays project-wide config only.

---

## Tech Stack & Dependencies

| Category        | Selection | Rationale |
|----------------|-----------|-----------|
| Language/Runtime | Python 3.x (existing) | No change. |
| New dependencies | None required | Optional: subprocess to call `gh`/`glab` if present; no PyPI host API clients. |
| File format      | JSON for lifecycle | Already used for registry, config, index; scripts have load_json/save_json. |

**New dependencies introduced:** None.

**Dependencies explicitly rejected:** PyGitHub, GitLab API, Bitbucket API — keep Cicadas host-agnostic and avoid API keys.

---

## Project / Module Structure

```
.cicadas/
├── drafts/
│   └── {initiative-name}/
│       ├── prd.md
│       ├── ux.md
│       ├── tech-design.md
│       ├── approach.md
│       ├── tasks.md
│       └── lifecycle.json          # [NEW] per-initiative lifecycle + PR boundaries
├── active/
│   └── {initiative-name}/
│       ├── ... (existing specs)
│       └── lifecycle.json          # [NEW] promoted at kickoff
└── archive/
    └── {timestamp}-{name}/
        └── lifecycle.json         # [NEW] archived with initiative

src/cicadas/scripts/
├── utils.py                        # (existing) load_json, save_json, get_project_root, get_default_branch
├── kickoff.py                      # (unchanged) existing move-all-drafts already moves lifecycle.json
├── archive.py                      # (unchanged) existing move-active-to-archive already includes lifecycle.json
├── status.py                       # [EXTENDED] report merge state + next step when lifecycle.json present
├── create_lifecycle.py             # [NEW] write lifecycle.json to drafts/ or active/
└── open_pr.py                      # [NEW] host-agnostic open PR (gh/glab/URL/fallback)
```

**Key structural decisions:**
- lifecycle.json lives alongside other initiative specs; same promote/archive rules.
- No new top-level .cicadas files; all new artifacts are per-initiative.

---

## Architecture Decisions (ADRs)

### ADR-1: Lifecycle and PR boundaries per initiative, not in config.json

**Decision:** Store lifecycle (ordered steps) and PR boundary choices in a per-initiative file (lifecycle.json) or at top of approach.md; do not add these to .cicadas/config.json.

**Rationale:** config.json is shared by all initiatives; PR and lifecycle policy can differ per initiative (e.g. one heavy with PRs, one lightweight). Keeping them with the initiative also ensures they are archived with the initiative.

**Affects:** Where lifecycle and PR flags are read/written; kickoff and archive behavior.

### ADR-2: Completion detection is git-only

**Decision:** Determine “branch A merged into B” using only git: fetch origin (if remote), then check whether A’s tip is reachable from B (or A is deleted on remote). No calls to GitHub/GitLab/Bitbucket APIs.

**Rationale:** Works with any host and local repos; no API keys or rate limits; same code path everywhere.

**Affects:** status.py or a small dedicated script that reports “merged” and next step.

### ADR-3: Open-PR helper is optional and best-effort

**Decision:** If we add open_pr.py (or equivalent), it tries gh → glab → Bitbucket URL → fallback message. It does not fail the workflow if no CLI is available; docs always describe manual “push and open in UI.”

**Rationale:** Teams use different hosts and may not have gh/glab installed; Cicadas must not assume one environment.

**Affects:** open_pr.py (if implemented), SKILL and HOW-TO wording.

### ADR-4: Lifecycle v1 is a flat list of steps

**Decision:** lifecycle.json contains an ordered array of steps; each step has id, name, optional description, optional attributes (e.g. opens_pr, reflect_before). We do not introduce nested “repeat” or sub-sequences in v1; a single “feature work (per feature)” step can describe the loop in text.

**Rationale:** Simpler to generate, parse, and document; sufficient for “next step” inference. Can extend later with repeat/sub-steps if needed.

**Affects:** lifecycle schema, default template, and any script that reads lifecycle.

---

## Data Models

### lifecycle.json (new)

```json
{
  "initiative": "initiative-name",
  "pr_boundaries": {
    "specs": false,
    "initiatives": true,
    "features": true,
    "tasks": false
  },
  "steps": [
    { "id": "kickoff_initiative", "name": "Kickoff initiative", "description": "Promote drafts to active, create initiative branch" },
    { "id": "kickoff_features", "name": "Kickoff feature branches", "description": "For each partition, run branch.py" },
    { "id": "feature_work", "name": "Feature work (per feature)", "description": "Task branches → implement → test → reflect → commit → push → PR (if enabled) → merge to feature", "opens_pr": true },
    { "id": "complete_feature", "name": "Complete each feature", "description": "Update index, push, open PR to initiative (if enabled), merge", "opens_pr": true },
    { "id": "complete_initiative", "name": "Complete initiative", "description": "Open PR to main (if enabled), merge, synthesize canon, archive", "opens_pr": true }
  ]
}
```

**Key field decisions:**
- `pr_boundaries` — mirrors the four questions (specs, initiatives, features, tasks); used when generating steps (e.g. only add “open PR” semantics where true) and by docs/agents.
- `steps[].opens_pr` — optional; when true, this step implies “open a PR” at that boundary. Omitted or false = merge directly.
- No `completed` array in v1; “next step” inferred from git/registry.

### No changes to registry.json or config.json

Existing schema unchanged. No new top-level keys.

---

## API & Interface Design

### Scripts

- **kickoff.py**  
  - **Change:** When copying drafts → active, if `lifecycle.json` exists in drafts/{name}/, copy it to active/{name}/.  
  - No new CLI arguments required; existing `--intent` etc. unchanged.

- **archive.py**  
  - **Change:** When archiving active/{name}/, include lifecycle.json in the timestamped archive directory if present.  
  - No new CLI arguments.

- **status.py** (or new/optional behavior)  
  - **Input:** Current branch, registry (initiatives + branches), optional path to active lifecycle.  
  - **Behavior:** Optionally run `git fetch`; for each registered feature branch, check if it is merged into its initiative branch; for initiative branch, check if merged into default branch.  
  - **Output:** Existing status output + optional lines: “feat/X → initiative/Y: merged”, “Next: [lifecycle step name].”  
  - **Interface:** Could be a flag (e.g. `--lifecycle`) or always-on when lifecycle.json exists in active.

- **open_pr.py** (optional new script)  
  - **Input:** Current branch, target base branch (e.g. initiative/name or main), optional body file.  
  - **Behavior:** If `gh` in PATH, run `gh pr create --base <target> --head <current> ...`. Else if `glab` in PATH, run `glab mr create ...`. Else if remote URL looks like Bitbucket, print URL for “new PR” with source=current. Else print fallback: “Push your branch and open a Pull Request in your host’s UI.”  
  - **Output:** PR URL if created, or printed URL or message.  
  - **Exit:** 0 if PR created or URL printed; non-zero only on hard failure (e.g. not in a git repo).

### Agent operations (no new script)

- **Approach phase:** After approach.md is drafted, agent (or builder) is prompted: “Will you be doing PRs?” If yes, “At which boundaries?” with defaults. Result is written into lifecycle.json (and optionally a one-line note in approach.md).  
- **Reading lifecycle:** Agents read `.cicadas/active/{initiative}/lifecycle.json` (or drafts) to know steps and PR boundaries; “next step” inferred from status + lifecycle.

---

## Implementation Patterns & Conventions

- Use existing `load_json` / `save_json` from utils.py for lifecycle.json; same path handling as other .cicadas files (get_project_root()).
- For merge detection: use `subprocess` to run `git fetch` and `git branch -r --merged <target>` or equivalent (e.g. `git merge-base --is-ancestor <source> <target>` after fetch). Prefer one implementation that works for local and remote refs.
- open_pr.py: use `shutil.which("gh")` / `shutil.which("glab")` to detect CLIs; no hardcoded paths. For Bitbucket, parse `git remote get-url origin` to build PR URL if possible.

---

## Security & Performance

- **Secrets:** No API keys or tokens in Cicadas; gh/glab use their own auth (e.g. gh auth login). Safe.
- **Performance:** git fetch and merge check are cheap; status may add one fetch per run when lifecycle reporting is enabled. Acceptable.
- **Observability:** No new logging required beyond existing script behavior; optional “next step” line in status is user-facing only.

---

## Implementation Sequence

1. **Lifecycle schema and default template** — Define lifecycle.json schema and a default template (standard initiative steps with optional opens_pr). No scripts yet; used by approach-phase flow and docs.
2. **Draft lifecycle in approach phase** — When approach is finalized, prompt for “use PRs?” and four boundaries; write lifecycle.json into drafts/{name}/ (and optionally a line in approach.md). May be agent-driven or a small helper.
3. **Kickoff and archive** — Update kickoff.py to copy lifecycle.json drafts → active; update archive.py to include lifecycle.json in archive. Tests for both.
4. **Status / merge detection** — Extend status.py (or add a small script) to: fetch, compute “branch X merged into Y” for registered branches, read active lifecycle if present, output “Next: …” step. Prefer minimal change to status.py.
5. **Docs and SKILL** — Update SKILL.md, HOW-TO, CLAUDE.md to describe lifecycle, PR boundaries, host-agnostic open PR, and git-based completion. Reference lifecycle in “Complete feature” and “Complete initiative.”
6. **Optional open_pr.py** — If desired, add open_pr.py with gh/glab/URL/fallback; document in SKILL and HOW-TO.

**Parallel work:** (2) and (1) can be done together; (3) and (4) after (1)–(2); (5) can run alongside (3)–(4). (6) is optional and last.

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
