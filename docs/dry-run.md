# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

# Cicadas Method — Dry Run

Pressure-testing the v2 methodology by walking through a fictional project end-to-end.

**Format**: The dry-run is written as a **dialog** between the Builder (human) and the Agent (AI with the Chorus skill). The Builder gives natural-language commands. The Agent handles all ceremony — script execution, agentic operations, git commands — behind the scenes.

> **Open Question — Chorus Installation**: How does the Chorus orchestrator get into a new project? The v2 doc assumes `scripts/chorus/` exists but doesn't prescribe an install mechanism. For now, assume copy-and-paste (`cp -r /path/to/chorus scripts/chorus`). TBD.

---

## Greenfield (v1)

### The Fake Project: **PlateMate**

A web app where users create, share, and discover recipes. Key features:
- Browse/search recipes by ingredient, cuisine, dietary tag
- Create and publish recipes with structured fields (ingredients, steps, photos)
- Meal planning: drag recipes into a weekly calendar
- Social feed: follow cooks, like/comment on recipes

**Stack**: Python (FastAPI) backend, PostgreSQL, React frontend, deployed on Fly.io.

**Team**: One human developer ("the Builder") using an AI coding agent with the Chorus skill installed.

---

### Phase 0: Bootstrap

> **Builder**: "Initialize cicadas for this project."

**Agent performs**:
1. **Script**: `python scripts/chorus/scripts/init.py`
2. Reports: "Initialized `.cicadas/` with registry, index, config, and empty `canon/`, `drafts/`, `active/`, `archive/` directories."

**Result**:
```
platemate/
├── .git/
├── scripts/chorus/          # Pre-installed
└── .cicadas/
    ├── config.json          # {"project_name": "platemate"}
    ├── registry.json        # Empty initiatives & branches
    ├── index.json           # Empty entries
    ├── canon/modules/       # Empty — greenfield, nothing to reverse-engineer
    ├── drafts/              # Empty
    ├── active/              # Empty
    └── archive/             # Empty
```

---

### Phase 1: Emergence (Drafting)

#### Step 1.1: Clarify → `prd.md`

> **Builder**: "I want to build a recipe sharing app. Help me clarify the requirements."

**Agent performs**:
1. **Agentic Op**: Activates the **Clarify** subagent (`emergence/clarify`).
2. Creates `.cicadas/drafts/platemate-v1/` directory.
3. Begins a multi-turn elicitation dialog:

> **Agent**: "Who are the target users? What's the MVP scope vs. future? What does success look like?"
>
> **Builder**: "Home cooks, 25-45. MVP = recipe CRUD + search + social feed. Meal planning is v1 stretch. Success = 100 recipes shared in first month."
>
> **Agent**: "Got it. I've drafted the PRD. Key points: problem is recipe-sharing clutter, two personas (creator and discoverer), MVP includes account creation, recipe CRUD, ingredient search, social feed. Meal planning, grocery lists, and video are non-goals for v1. Please review."

**Agent produces**: `.cicadas/drafts/platemate-v1/prd.md`

> **Builder**: *Reviews. Cuts meal planning from MVP scope. Adjusts success criteria.* "Looks good with my edits."

**Gate**: Builder approval. Agent does NOT proceed to UX until the Builder says go.

**Observation**: The Clarify subagent *elicits* — it doesn't invent requirements. The Builder's review gate is where scope is locked.

#### Step 1.2: UX → `ux.md`

> **Builder**: "Draft the UX."

**Agent performs**:
1. **Agentic Op**: Activates the **UX** subagent (`emergence/ux`).
2. Reads `prd.md` as input.
3. Produces `.cicadas/drafts/platemate-v1/ux.md` — screens, flows, key states.

> **Agent**: "I've designed 7 screens (Landing, Sign Up/In, Feed, Recipe Detail, Recipe Editor, Profile, Search). The recipe creation flow is a wizard with 3 steps. Key empty states and error states are defined. Please review."
>
> **Builder**: "Make recipe creation a single long-form page, not a wizard. Otherwise good."

**Agent**: Updates `ux.md`, confirms the change.

#### Step 1.3: Tech → `tech-design.md`

> **Builder**: "Draft the tech design."

**Agent performs**:
1. **Agentic Op**: Activates the **Tech Design** subagent (`emergence/tech-design`).
2. Reads `prd.md` + `ux.md` as inputs.
3. Produces `.cicadas/drafts/platemate-v1/tech-design.md`.

> **Agent**: "Architecture: FastAPI monolith, SQLite, React SPA. Data models: User, Recipe (ingredients as JSONB), Follow, Like, Comment. Auth via JWT. Search via SQLite FTS5."
>
> **Builder**: "Swap SQLite for PostgreSQL. Use S3-compatible storage for recipe images from day 1. Use tsvector for search."

**Agent**: Updates `tech-design.md` with PostgreSQL, S3, tsvector. Records these as key decisions.

#### Step 1.4: Approach → `approach.md`

This is the **critical** step — it defines the partitions that become feature branches.

> **Builder**: "Draft the approach."

**Agent performs**:
1. **Agentic Op**: Activates the **Approach** subagent (`emergence/approach`).
2. Reads `prd.md` + `ux.md` + `tech-design.md`.
3. Produces `.cicadas/drafts/platemate-v1/approach.md`.

> **Agent**: "I've identified 4 partitions:
> 1. **`feat/data-and-auth`** — DB schema, migrations, user model, JWT auth. *Modules*: `db`, `auth`
> 2. **`feat/recipe-engine`** — Recipe CRUD API, ingredient parsing, search. *Modules*: `recipes`, `search`
> 3. **`feat/frontend-shell`** — React scaffold, routing, auth UI, layout. *Modules*: `frontend`
> 4. **`feat/social-feed`** — Follow/like/comment, feed API, feed UI. *Modules*: `social`, `frontend`
>
> Sequencing: data-and-auth first (everything depends on it), then recipe-engine and frontend-shell in parallel, then social-feed last (depends on both).
>
> ⚠️ Note: `feat/social-feed` and `feat/frontend-shell` both touch `frontend`. I recommend tightening the boundary — shell owns `frontend/core/`, social owns `frontend/social/`."
>
> **Builder**: "Good call on the boundary. Let's keep it at 4 partitions even though I'm solo — the clean merge boundaries are worth the overhead."

**Observation**: The approach creates *named* partitions with declared module scopes. Everything downstream — branch names, conflict detection, registry — flows from this document.

#### Step 1.5: Tasks → `tasks.md`

> **Builder**: "Draft the tasks."

**Agent performs**:
1. **Agentic Op**: Activates the **Tasks** subagent (`emergence/tasks`).
2. Reads all prior docs.
3. Produces `.cicadas/drafts/platemate-v1/tasks.md` — ordered checklist grouped by partition.

> **Agent**: "18 tasks across 4 partitions. Each has an ID and is testable. Please review for granularity."
>
> **Builder**: *Reviews. Splits "Set up database" into migrate + seed steps. Adds acceptance criteria.* "Good to go."

**Gate**: Builder has now reviewed all 5 Emergence artifacts. The drafts are complete.

---

### Phase 2: Kickoff + Initiative Branch

> **Builder**: "Kickoff platemate-v1."

**Agent performs**:
1. **Script**: `python scripts/chorus/scripts/brood.py platemate-v1 --intent "Recipe sharing app MVP: recipe CRUD, search, social feed"`
   - Moves all files from `.cicadas/drafts/platemate-v1/` → `.cicadas/active/platemate-v1/`
   - Registers `platemate-v1` in `registry.json` under `initiatives`
2. **Git**: `git checkout -b initiative/platemate-v1`
   - Creates the long-lived **initiative integration branch**
3. Reports: "Initiative `platemate-v1` is active. Created integration branch `initiative/platemate-v1`. All feature branches will fork from here."

**Branch hierarchy** (the full picture for the entire initiative):
```
main
└── initiative/platemate-v1          ← long-lived, created at kickoff
    ├── feat/data-and-auth           ← registered, forks from initiative
    │   ├── task/.../schema          ← ephemeral, unregistered
    │   └── task/.../jwt-auth        ← ephemeral, unregistered
    ├── feat/recipe-engine           ← registered, forks from initiative
    ├── feat/frontend-shell          ← registered, forks from initiative
    └── feat/social-feed             ← registered, forks from initiative
```

**Observation**: Kickoff is one command from the Builder's perspective. Behind the scenes, the Agent runs a script (spec promotion + registration) and a git command (integration branch). The v2 doc hints at this hierarchy but doesn't mandate it — the dry-run makes it explicit.

**Pressure-test**: `brood.py` should probably create the initiative branch automatically, mirroring how `branch.py` creates the git branch for features. One command, one ceremony.

---

### Phase 3: Execution — Feature Branch 1: `feat/data-and-auth`

#### 3.1: Start the Feature Branch

> **Builder**: "Start feature data-and-auth."

**Agent performs**:
1. **Agentic Op — Semantic Intent Check**: Reads `registry.json`. No other branches exist. No semantic conflicts.
2. **Git**: `git checkout initiative/platemate-v1` (ensure correct parent)
3. **Script**: `python scripts/chorus/scripts/branch.py feat/data-and-auth --intent "Database schema, user model, JWT auth" --modules "db,auth" --initiative platemate-v1`
   - Creates git branch `feat/data-and-auth` (forking from `initiative/platemate-v1`)
   - Registers in `registry.json` under `branches`
   - Creates `.cicadas/active/feat/data-and-auth/`
4. Reports: "Feature branch `feat/data-and-auth` created and registered. No conflicts detected. You're on the branch and ready to work on tasks 1-4."

**Observation**: The semantic check is trivial here (no peers). It matters more when `feat/social-feed` starts later and the `frontend` module overlap needs assessment.

**Pressure-test**: `branch.py` implicitly forks from current HEAD. A `--from` flag (defaulting to the linked initiative branch) would make this explicit and prevent mistakes.

#### 3.2: Inner Loop — Task Branches

**Task 1: Database Schema + Migrations**

> **Builder**: "Implement task 1 — set up PostgreSQL schema and Alembic migrations."

**Agent performs**:
1. **Git**: `git checkout -b task/data-and-auth/schema` (from `feat/data-and-auth`)
2. **Implementation**: Creates `alembic.ini`, initial migration, `db/models/user.py`, `db/session.py`
3. **Verification**: Runs `alembic upgrade head` — confirms migration applies cleanly
4. **Agentic Op — Reflect**: Diffs task branch against feature branch. This is all new code — no existing specs to diverge from. Updates `tasks.md` → marks task 1 as `[x]`.
5. **Git**: Pushes task branch and opens a **PR** against `feat/data-and-auth`.
   - PR description includes: what was implemented, Reflect summary (no drift this time), test results.
6. Reports: "Task 1 complete. Schema and migrations are set up. No spec drift — this is new code. PR is open for review."

> **Builder**: *Reviews the PR. Checks the diff, confirms migrations look correct.* "Approved."

**Agent performs**:
1. **Git**: Merges the PR into `feat/data-and-auth`.
2. **Git**: Deletes task branch.
3. Reports: "PR merged. Task branch cleaned up."

**Observation**: On a greenfield v1, the first few Reflect operations are uneventful — there's no "drift" because nothing existed before. Reflect becomes valuable when reality diverges from the plan. The PR process here is lightweight (solo Builder), but the structure is in place for team review.

---

**Task 3: JWT Auth — Where Reflect Gets Interesting**

> **Builder**: "Implement task 3 — JWT auth with login, register, and refresh."

**Agent performs**:
1. **Git**: `git checkout -b task/data-and-auth/jwt-auth`
2. **Implementation**: Builds `/api/auth/login`, `/api/auth/register`, `/api/auth/refresh`.
   - Discovery: refresh tokens need a DB table (`RefreshToken`) — this wasn't in the tech design.
   - Decision: uses `python-jose` instead of `PyJWT` (library choice wasn't spec'd).
3. **Verification**: Auth endpoints pass tests.
4. **Agentic Op — Reflect**:
   - Analyzes git diff against active specs
   - Finds divergence from `tech-design.md`: new `RefreshToken` model, library choice
   - **Updates** `.cicadas/active/platemate-v1/tech-design.md` — adds `RefreshToken` to data model section, notes `python-jose`
   - **Updates** `tasks.md` → marks task 3 as `[x]`
5. **Agentic Op — Signal Assessment**: Is this change significant enough to broadcast? `RefreshToken` is internal to auth — no cross-branch impact. No signal needed.
6. **Git**: Pushes task branch and opens a **PR** against `feat/data-and-auth`.
   - PR description includes: what was implemented, **Reflect findings** (new `RefreshToken` table, `python-jose` choice — both diverge from tech design), test results.
   - The Reflect findings in the PR give the reviewer visibility into *why* the specs were updated.
7. Reports: "Task 3 complete. I discovered we needed a `RefreshToken` table and chose `python-jose` — both diverge from the original tech design. I've updated the active specs and the PR includes the Reflect summary."

> **Builder**: *Reviews the PR. The Reflect summary makes the divergences immediately visible — no need to diff specs manually.* "The RefreshToken approach is sound. Approved."

**Agent performs**:
1. **Git**: Merges the PR into `feat/data-and-auth`.
2. **Git**: Deletes task branch.

**This is the method working as designed**: code reality diverged from the plan, Reflect caught it, updated the specs, and the PR surfaced the divergence to the reviewer. The active specs stay honest — *during* development, not after.

---

#### 3.3: Complete the Feature Branch

All four tasks (1-4) are done.

> **Builder**: "Complete feature data-and-auth."

**Agent performs**:
1. **Script**: `python scripts/chorus/scripts/update_index.py --branch feat/data-and-auth --summary "Database schema, user model, JWT auth with refresh tokens" --modules "db,auth"` — logs to change ledger
2. **Git**: `git checkout initiative/platemate-v1 && git merge feat/data-and-auth` — merges into the **initiative branch**, not `main`
3. Reports: "Feature `data-and-auth` merged into `initiative/platemate-v1`. Index updated. Ready for the next feature."

**Key**: No synthesis, no archiving here. The active specs stay active — they're the living document for the rest of the initiative, continuously updated by Reflect. Canon is an *output* of the completed initiative, not a running log. The next feature branch will fork from the initiative branch and have auth code available.

---

### Phase 3 (continued): Feature Branch 2: `feat/recipe-engine`

#### 3.4: Start the Feature Branch

> **Builder**: "Start feature recipe-engine."

**Agent performs**:
1. **Agentic Op — Semantic Intent Check**: Reads `registry.json`. No active feature branches (data-and-auth was completed). No conflicts.
2. **Git**: `git checkout initiative/platemate-v1`
3. **Script**: `python scripts/chorus/scripts/branch.py feat/recipe-engine --intent "Recipe CRUD, ingredient parsing, search" --modules "recipes,search" --initiative platemate-v1`
4. Reports: "Feature branch `feat/recipe-engine` created from `initiative/platemate-v1`. Auth code is available. No conflicts. Working on tasks 5-9."

#### 3.5: A Signal Scenario

Midway through implementation, the Agent discovers the Recipe model needs a `slug` field for SEO-friendly URLs. This wasn't in the tech design.

> **Agent** (during Reflect after a task): "I've added a `slug` field to the Recipe model for SEO-friendly URLs (`/recipes/{slug}` instead of `/recipes/{id}`). This diverges from the tech design — I've updated it. **This affects other branches**: `feat/frontend-shell` will need slug-based routes, and `feat/social-feed` links to recipes in the feed. I'm going to signal this."

**Agent performs**:
1. **Agentic Op — Reflect**: Updates `tech-design.md` with the slug field
2. **Script**: `python scripts/chorus/scripts/signal.py "Recipe URLs changed to slug-based: /recipes/{slug} instead of /recipes/{id}. Frontend routes and feed links must use slugs."`
   - Appends timestamped signal to initiative's signal board in `registry.json`
3. Reports: "Signal sent to initiative `platemate-v1`. When you start the next feature branch, I'll surface this."

> **Builder**: "Good. Keep going."

**Observation**: The Agent assessed cross-branch impact and signaled autonomously. The Builder didn't have to remember to do it. In a multi-agent scenario, this is how Agent A tells Agent B about breaking changes without blocking.

---

### Phase 3 (continued): Feature Branches 3 & 4

Each feature branch forks from `initiative/platemate-v1` and merges back into it. Same dialog pattern:

**`feat/frontend-shell`** (tasks 10-14):

> **Builder**: "Start feature frontend-shell."

**Agent performs**:
1. Semantic intent check + branch creation from initiative.
2. **Script**: `python scripts/chorus/scripts/check.py` — surfaces the slug signal.
3. Reports: "📡 Signal from `feat/recipe-engine`: Recipe URLs changed to slug-based. I'll use `/recipes/{slug}` in all frontend routing."

The Agent incorporates the signal into its implementation from the start. During Reflect, it updates `ux.md` with actual component names. At completion, merges back to the initiative branch (same pattern as 3.3 — index update + merge, no synthesis).

**`feat/social-feed`** (tasks 15-18):

> **Builder**: "Start feature social-feed."

**Agent performs**:
1. Semantic intent check — notes `frontend` module overlap with completed `feat/frontend-shell`. Since that branch is already merged, no active conflict.
2. During implementation, discovers the feed query is slow without a denormalized `feed_events` table.

> **Agent**: "The chronological feed query is O(n) on follows × recipes. I need to add a `feed_events` denormalized table. This is an architectural change — updating tech design and signaling."

**Agent performs**:
1. **Agentic Op — Reflect**: Updates `tech-design.md` with the new table.
2. **Script**: `python scripts/chorus/scripts/signal.py "Added feed_events denormalized table for feed performance. No API changes, but DB schema is larger than planned."`

At completion, merges back to `initiative/platemate-v1` (index update + merge). Active specs have been continuously updated by Reflect across all four branches — they now reflect the *actual* state of the complete system.

---

### Phase 5: Initiative Completion (Outer Loop: Synthesis & Archive)

All four feature branches have been merged into `initiative/platemate-v1`. The initiative branch contains the complete v1 codebase. Active specs have been kept honest by Reflect throughout. Now — and only now — we close the outer loop.

> **Builder**: "Complete initiative platemate-v1."

**Step 1: Merge code to main**

**Agent performs**:
1. **Git**: `git checkout main && git merge initiative/platemate-v1` — **code merge only**. The initiative branch never touched canon, so there are no documentation conflicts. Active specs (in `.cicadas/active/`) come along with the merge.
2. **Git**: `git branch -d initiative/platemate-v1` — cleanup.
3. Reports: "Code merged to `main`. Initiative branch deleted. Now synthesizing canon."

**Why merge first, then synthesize**: Canon is meant to *replace*, not *merge*. If synthesis happened on the initiative branch, merging canon files to main would use git's 3-way merge — which could conflict with previous canon versions. By synthesizing directly on main, canon is a simple file write (overwrite old, create new). No merge strategy needed, ever. On a second initiative, the same pattern works: merge code, then overwrite canon on main.

**Step 2: Synthesize canon on main**

**Agent performs**:
4. **Agentic Op — Synthesis**:
   - Reads *all* code on `main` (now contains the complete v1)
   - Reads the active specs in `.cicadas/active/platemate-v1/` (`prd.md`, `ux.md`, `tech-design.md`, `approach.md`, `tasks.md`) — these have been continuously updated by Reflect across all four feature branches and now reflect the *actual* system, not the original plan
   - Reads `index.json` for the change ledger (4 entries, one per feature branch)
   - Canon is empty (greenfield) — creating from scratch
   - **Produces canon**:
     - `canon/product-overview.md` — full product description, goals, personas
     - `canon/ux-overview.md` — actual UX as built (reflecting Reflect updates from `feat/frontend-shell`)
     - `canon/tech-overview.md` — actual architecture including discoveries (RefreshToken, slug routing, feed_events)
     - `canon/modules/db.md`, `auth.md`, `recipes.md`, `search.md`, `social.md`, `frontend.md`
   - **Extracts key decisions** from the active specs and embeds them in canon — this preserves the "why" before specs are archived
5. Reports: "Canon synthesized on `main` from the complete v1 codebase. This captures everything as actually built — including all discoveries and divergences from the original plan. Key decisions are preserved. Please review before I archive and commit."

> **Builder**: *Reviews canon. The tech-overview accurately reflects the RefreshToken table, slug-based URLs, and feed_events — all things that emerged during implementation. The "why" for each is captured in Key Decisions.* "Ship it."

**Step 3: Archive and commit**

**Agent performs**:
6. **Script**: `python scripts/chorus/scripts/archive.py platemate-v1` — moves all active specs from `.cicadas/active/` to `.cicadas/archive/`
7. Removes `platemate-v1` from `registry.json` initiatives
8. **Git**: Commits canon + archive as a follow-up commit on `main`: `"chore(cicadas): synthesize canon and archive platemate-v1"`
9. Reports: "Initiative `platemate-v1` complete. Canon is authoritative, specs are archived, all on `main`. Registry is clean."

**Key design choice**: The initiative branch is a *pure code integration branch*. It never touches canon. Synthesis and archiving happen on `main` after the code merge. This means:
- Canon is always synthesized *from* main, *on* main — it truthfully reflects what's deployed
- No merge conflicts on documentation files, ever
- A second initiative just overwrites canon on main after its code merges — same simple pattern
- There's a brief commit window where code is updated but canon is stale, but the synthesis commit follows immediately

`main` receives two commits: the code merge, then the synthesis/archive commit. The hierarchy: task branches (ephemeral) → feature branches (registered) → initiative branch (integration) → `main` (production) → synthesis commit.

**Final state**:
```
.cicadas/
├── canon/                          ← Authoritative, synthesized on main from complete v1
│   ├── product-overview.md
│   ├── ux-overview.md
│   ├── tech-overview.md
│   └── modules/
│       ├── db.md
│       ├── auth.md
│       ├── recipes.md
│       ├── search.md
│       ├── social.md
│       └── frontend.md
├── archive/                        ← Expired specs, for archaeology
│   └── 20260216-...-platemate-v1/  ← All active specs from the initiative
├── index.json                      ← 4 entries, one per feature branch
├── registry.json                   ← Empty (no active work)
└── config.json
```

---

### Observations & Pressure Points

#### What Worked Well

1. **Agent as the interface**: The Builder never typed a script path. They said "Start feature", "Implement task", "Complete feature" — the Agent handled all ceremony. This collapses the mental overhead of the method into natural dialog.

2. **Reflect is invisible until it matters**: On task 1 (new code, no drift), Reflect is a no-op the Builder barely notices. On task 3 (RefreshToken divergence), it catches a real problem and the Builder sees it surface naturally in the Agent's report.

3. **Signals are Agent-initiated**: The Agent assessed cross-branch impact and signaled autonomously during the slug change. The Builder didn't have to remember — the Agent's judgment drove it.

4. **Approach as the pivot point**: The `approach.md` step in Emergence is the single most important artifact. Every downstream decision (branch names, module scopes, conflict detection) flows from it.

5. **Canon as a product, not an input**: The Builder never "maintained documentation." Canon was synthesized *once* at initiative completion from what was actually built. During development, the active specs + Reflect served as the living document. The "why" was preserved by extracting key decisions before archiving.

6. **Synthesis and archiving at the outer loop**: No per-feature-branch synthesis ceremony. The active specs accumulated Reflect updates across all four branches, so by initiative completion they accurately described the full system. One synthesis, one archive, one merge to main.

#### Gaps and Questions

1. **First synthesis on greenfield is special**: Canon starts empty. The synthesis prompt needs a "bootstrap" mode that creates canon from scratch rather than updating existing docs.

2. **Shared `tasks.md` conflict risk**: `tasks.md` lives at the initiative level, organized by partition. Two parallel branches Reflecting simultaneously could create merge conflicts. **Possible fix**: Split tasks into per-branch files at kickoff.

3. **Overhead for solo builders**: The full ceremony (4 branch registrations, 4 semantic checks, Reflect on every task branch, PRs) is significant for one person. Guidance on "light mode" (fewer partitions, combined steps) would help.

4. **Intermediate spec snapshots are lost**: Active specs mutate via Reflect across all branches. By initiative completion, they reflect the *final* state only. Intermediate states (e.g., tech design after `feat/data-and-auth` vs. after `feat/social-feed` added `feed_events`) aren't preserved as snapshots — though git history of `.cicadas/active/` provides this if needed.

5. **Synthesis is the highest-skill LLM task**: It needs to read code, understand intent from specs, produce accurate canon, and extract key decisions. For v1, the code surface is manageable. For mature projects, this is a context-window challenge.

6. **No explicit test phase**: The method doesn't prescribe where testing fits. Recommendation: tasks should include acceptance criteria; task branches aren't merge-ready until tests pass.

7. **`archive.py` needs initiative-level support**: The current script archives branches (removes from `registry.json["branches"]`). Initiative completion needs to archive initiative specs and remove from `registry.json["initiatives"]` — likely needs a `--type` flag.

8. **`brood.py` should create the initiative branch**: Currently the Agent must manually run `git checkout -b initiative/{name}` after kickoff. The script should do this automatically.

9. **`branch.py` should enforce parent branch**: The script forks from current HEAD. A `--from` flag (defaulting to the linked initiative branch) would prevent mistakes.

10. **Agent autonomy boundaries**: The dry-run shows the Agent signaling autonomously and making Reflect decisions without explicit Builder approval. The method should clarify: which Agent actions require Builder confirmation, and which can proceed autonomously? Reflect seems safe to auto-run. Signaling seems safe. But synthesis — which produces authoritative canon — clearly needs Builder review before archiving.

---
---

## Brownfield (v1.1)

Picking up where the greenfield left off. PlateMate v1 is deployed. Canon exists. The codebase has ~15k lines across `db`, `auth`, `recipes`, `search`, `social`, and `frontend`. Now we're adding a **new feature** and **updating an existing feature**.

### Starting State

```
main (deployed v1)
├── src/                              # ~15k lines of working code
└── .cicadas/
    ├── canon/                        # Authoritative — synthesized from v1
    │   ├── product-overview.md       # Goals, personas, metrics
    │   ├── ux-overview.md            # 7 screens, recipe creation flow
    │   ├── tech-overview.md          # FastAPI + PostgreSQL, JWT auth, tsvector search
    │   └── modules/
    │       ├── db.md                 # Schema: User, Recipe, RefreshToken, Follow, Like, Comment
    │       ├── auth.md               # JWT + refresh tokens (python-jose)
    │       ├── recipes.md            # CRUD, slug-based URLs, ingredient JSONB
    │       ├── search.md             # tsvector FTS, ingredient-based search
    │       ├── social.md             # Follow/like/comment, feed_events denormalized table
    │       └── frontend.md           # React SPA, routing, auth UI
    ├── archive/
    │   └── 20260216-...-platemate-v1/
    ├── index.json                    # 4 entries from v1
    ├── registry.json                 # Empty — no active work
    └── config.json
```

**Key difference from greenfield**: Canon is populated. The Agent now has authoritative context about the existing system *before* Emergence begins. This changes everything downstream — the Agent draft specs that are aware of existing architecture, data models, and design decisions.

### The v1.1 Initiative

Two features for this release:
1. **NEW — Meal Planning**: Drag recipes into a weekly calendar. This was explicitly cut from v1 scope. *New modules*: `planner`, `frontend/planner`
2. **UPDATE — Advanced Search**: Add filtering by dietary tags, cuisine type, and cooking time. Extends the existing `search` and `recipes` modules. *Touches*: `recipes`, `search`, `frontend/search`

---

### Phase 1: Emergence (Canon-Aware Drafting)

#### Step 1.1: Clarify → `prd.md`

> **Builder**: "I want to add meal planning and improve search. Help me clarify requirements."

**Agent performs**:
1. **Agentic Op**: Activates the **Clarify** subagent.
2. **Reads existing canon**: `product-overview.md`, `ux-overview.md`, `tech-overview.md` — understands what PlateMate already does.
3. Creates `.cicadas/drafts/platemate-v1.1/`
4. Multi-turn elicitation:

> **Agent**: "I see from the canon that meal planning was a v1 non-goal. I also see search currently supports ingredient-based tsvector FTS. Let me clarify the scope for both:
> - Meal planning: weekly or monthly view? Can users share meal plans? Grocery list generation?
> - Search: what dietary tags? Should filters combine with text search or replace it?"
>
> **Builder**: "Weekly view only. No sharing, no grocery lists — just drag-and-drop. For search: dietary tags (vegan, gluten-free, etc.), cuisine type (Italian, Thai, etc.), and cooking time ranges. Filters combine with text search — AND logic."
>
> **Agent**: "Got it. I've drafted the PRD. Meal planning is a new feature area; advanced search extends the existing search module. Both are scoped tightly."

**Agent produces**: `.cicadas/drafts/platemate-v1.1/prd.md`

**Observation**: The Agent's first question referenced existing canon. On greenfield, the Clarify subagent started from zero. Here, it starts from *knowledge* — the canon tells it what exists, what was deferred, and what the architecture looks like. This makes elicitation sharper.

#### Step 1.2–1.3: UX and Tech Design

> **Builder**: "Draft UX and tech design."

**Agent performs**:
1. **UX subagent**: Reads `prd.md` + existing `canon/ux-overview.md`. Designs 2 new screens (Meal Planner, Search Filters panel) and updates to the existing Search screen. Notes: "The existing recipe card component in `frontend.md` can be reused for the planner's drag source."
2. **Tech Design subagent**: Reads all prior docs + existing `canon/tech-overview.md` + `canon/modules/db.md`, `recipes.md`, `search.md`. Designs:
   - New `MealPlan` and `MealPlanEntry` tables
   - New `DietaryTag` enum + `recipe_tags` join table on existing `Recipe` model
   - Extended search query combining tsvector with tag/cuisine/time filters
   - API: `GET/POST/PUT /api/meal-plans/`, `GET /api/recipes/?tags=...&cuisine=...&time_max=...`

> **Agent**: "The tech design extends the existing schema. Key decisions: dietary tags are a many-to-many on Recipe (not free-text), cuisine is an enum field on Recipe, and the search endpoint gets new query parameters — backward compatible, no breaking changes."
>
> **Builder**: "Good. Adding fields to Recipe means a migration — make sure existing recipes get `cuisine=null` and empty tags as defaults."

**Observation**: The tech design subagent knew about `RefreshToken`, `feed_events`, slug-based URLs — all discoveries from v1 that were captured in canon. Without canon, it might have designed something that conflicted with the existing schema.

#### Step 1.4: Approach → `approach.md`

> **Builder**: "Draft the approach."

**Agent performs**:
1. **Approach subagent**: Reads all prior docs + canon. Designs partitions:

> **Agent**: "Two partitions:
> 1. **`feat/advanced-search`** — Extends Recipe model (tags, cuisine, time), updates search queries, search UI filters. *Modules*: `recipes`, `search`, `frontend/search`
> 2. **`feat/meal-planner`** — New MealPlan tables, planner API, planner UI with drag-and-drop. *Modules*: `planner`, `frontend/planner`
>
> Sequencing: `feat/advanced-search` first — it modifies the Recipe model, and the planner needs to display recipe cards that include the new tag/cuisine data. Then `feat/meal-planner`.
>
> ⚠️ Module boundary: `feat/advanced-search` touches `recipes` (adding fields) and `search` (query changes). `feat/meal-planner` reads from `recipes` but doesn't modify it. Clean boundary.
>
> Risk: The Recipe model migration in `advanced-search` changes a high-traffic table. Migration should be backward compatible."
>
> **Builder**: "Two partitions is right for this scope. Go."

#### Step 1.5: Tasks → `tasks.md`

> **Builder**: "Draft the tasks."

**Agent**: Produces 10 tasks across 2 partitions. Builder reviews and approves.

**Gate**: All 5 Emergence artifacts reviewed. Ready for kickoff.

---

### Phase 2: Kickoff + Initiative Branch

> **Builder**: "Kickoff platemate-v1.1."

**Agent performs**:
1. **Script**: `python scripts/chorus/scripts/brood.py platemate-v1.1 --intent "Meal planning + advanced search"`
   - Promotes `.cicadas/drafts/platemate-v1.1/` → `.cicadas/active/platemate-v1.1/`
   - Registers initiative in `registry.json`
2. **Git**: `git checkout -b initiative/platemate-v1.1` (from `main`)
3. Reports: "Initiative `platemate-v1.1` is active. Integration branch `initiative/platemate-v1.1` created from `main`."

---

### Phase 3: Feature Branch 1 — `feat/advanced-search`

#### 3.1: Start the Feature Branch

> **Builder**: "Start feature advanced-search."

**Agent performs**:
1. **Agentic Op — Semantic Intent Check**: Registry is clean. No conflicts.
2. **Git**: `git checkout initiative/platemate-v1.1`
3. **Script**: `python scripts/chorus/scripts/branch.py feat/advanced-search --intent "Dietary tags, cuisine filter, time filter on recipes and search" --modules "recipes,search,frontend/search" --initiative platemate-v1.1`
4. Reports: "Feature branch created. Working on tasks 1–6."

#### 3.2: Task — Add Tags and Cuisine to Recipe Model

> **Builder**: "Implement task 1 — add dietary tags, cuisine type, and cooking time to the Recipe model."

**Agent performs**:
1. **Git**: `git checkout -b task/advanced-search/recipe-model-extension`
2. **Implementation**:
   - Migration: adds `cuisine` (nullable enum), `cooking_time_minutes` (nullable int) to `Recipe`
   - New `DietaryTag` table + `recipe_tags` many-to-many join table
   - Backfill: existing recipes get `cuisine=null`, `cooking_time_minutes=null`, empty tags
3. **Verification**: Migration applies and rolls back cleanly. Existing tests pass.
4. **Agentic Op — Reflect**:
   - Diffs task branch against active specs.
   - `tech-design.md` accurately described this — no divergence.
   - However, the Agent also checks against **canon**: the existing `canon/modules/recipes.md` describes Recipe without these fields. The active spec is the authority during development, but the Agent notes: "Canon will need updating at synthesis time — Recipe's schema is now larger than what canon describes."
   - Updates `tasks.md` → marks task 1 as `[x]`
5. **Git**: Opens PR. PR description includes implementation summary + Reflect finding (no spec drift, but canon is now stale for `recipes` module — expected, will be resolved at synthesis).

> **Builder**: *Reviews PR. Migration looks clean, backward compatible.* "Approved."

**Agent**: Merges PR, deletes task branch.

**Observation — Reflect against canon vs. active specs**: During v1, Reflect only compared against active specs (there was no prior canon). Now Reflect can *also* compare against canon to flag where the codebase is diverging from the *previously authoritative* snapshot. This is informational — canon staleness is expected during an initiative — but it helps the Builder understand the growing delta.

#### 3.3: Task — Extend Search with Filters

> **Builder**: "Implement task 3 — add filter parameters to the search endpoint."

**Agent performs**:
1. **Git**: `git checkout -b task/advanced-search/search-filters`
2. **Implementation**:
   - Updates `GET /api/recipes/search` with query params: `?tags=vegan,gluten-free&cuisine=italian&time_max=30`
   - Combines tsvector FTS with filter predicates using AND logic
   - Discovery: the existing search endpoint used a simple `SELECT` with `ts_rank`. Adding filters required refactoring to a query builder pattern — cleaner but structurally different from what was spec'd.
3. **Verification**: Search with and without filters passes tests.
4. **Agentic Op — Reflect**:
   - Finds divergence: `tech-design.md` described the search extension as "add WHERE clauses." Reality: refactored to a query builder.
   - **Updates** `.cicadas/active/platemate-v1.1/tech-design.md` — documents query builder pattern, notes it replaces the simple SELECT approach.
   - **Signal Assessment**: Does the query builder pattern affect the meal planner? No — the planner uses recipe CRUD, not search. No signal needed.
5. **Git**: Opens PR. Reflect findings in the PR: "Refactored search from simple SELECT to query builder pattern. Tech design updated."

> **Builder**: "Good refactor. Approved."

#### 3.4: Complete Feature Branch

All tasks for `feat/advanced-search` are done.

> **Builder**: "Complete feature advanced-search."

**Agent performs**:
1. **Script**: `python scripts/chorus/scripts/update_index.py --branch feat/advanced-search --summary "Added dietary tags, cuisine, cooking time to Recipe model. Refactored search to query builder with combined FTS + filter support." --modules "recipes,search,frontend/search"`
2. **Git**: `git checkout initiative/platemate-v1.1 && git merge feat/advanced-search`
3. Reports: "Feature `advanced-search` merged into initiative branch. Index updated."

No synthesis, no archiving. Active specs stay active.

---

### Phase 3 (continued): Feature Branch 2 — `feat/meal-planner`

#### 3.5: Start the Feature Branch

> **Builder**: "Start feature meal-planner."

**Agent performs**:
1. **Agentic Op — Semantic Intent Check**: Reads registry. `feat/advanced-search` is completed (no longer active). No conflicts.
2. **Git**: `git checkout initiative/platemate-v1.1`
3. **Script**: `python scripts/chorus/scripts/branch.py feat/meal-planner --intent "Weekly meal calendar with recipe drag-and-drop" --modules "planner,frontend/planner" --initiative platemate-v1.1`
4. Reports: "Feature branch created from initiative. Recipe model now includes tags, cuisine, and cooking time (from advanced-search). Working on tasks 7–10."

**Observation**: Because `feat/advanced-search` already merged into the initiative branch, `feat/meal-planner` gets those schema changes automatically. The new dietary tag data is available for display on recipe cards in the planner.

#### 3.6: Task — Planner API

> **Builder**: "Implement task 7 — MealPlan model and API."

**Agent performs**:
1. **Git**: `git checkout -b task/meal-planner/api`
2. **Implementation**:
   - New models: `MealPlan` (user_id, week_start_date), `MealPlanEntry` (meal_plan_id, recipe_id, day_of_week, meal_slot)
   - API: `POST /api/meal-plans/`, `GET /api/meal-plans/{week}`, `PUT /api/meal-plans/{id}/entries`
   - Discovery: needed a `meal_slot` enum (`breakfast`, `lunch`, `dinner`, `snack`) — not in the tech design.
3. **Agentic Op — Reflect**:
   - Finds divergence: `meal_slot` enum wasn't spec'd. Updates `tech-design.md`.
   - **Signal Assessment**: Does `meal_slot` affect other modules? No — this is internal to `planner`. No signal.
4. **Git**: Opens PR. Reflect: "Added `meal_slot` enum (breakfast/lunch/dinner/snack). Tech design updated."

> **Builder**: "Approved."

#### 3.7: Task — Planner Frontend (Where a Signal Is Received)

> **Builder**: "Implement task 9 — planner UI with drag-and-drop."

**Agent performs**:
1. **Git**: `git checkout -b task/meal-planner/ui`
2. **Agentic Op — Check Status**: `python scripts/chorus/scripts/check.py`
   - No new signals. (The search refactor didn't warrant one.)
3. **Implementation**:
   - Weekly calendar grid component
   - Recipe card drag source (reuses existing recipe card component — as the UX subagent suggested)
   - Discovery: the existing recipe card component doesn't expose dietary tags in its props. Needs a minor update to `frontend/core/RecipeCard.tsx`.
   - This touches `frontend/core/` — which was in `frontend-shell`'s scope during v1, not the planner's scope.
4. **Agentic Op — Reflect**:
   - Updates `ux.md` with actual component hierarchy.
   - **Signal Assessment**: The change to `RecipeCard.tsx` is in `frontend/core/`, outside the planner's declared modules. But since there's no active feature branch owning `frontend/core/`, this is safe. If there *were* a concurrent `feat/frontend-redesign`, this would be a conflict.
   - Reflect notes: "Modified shared component `RecipeCard.tsx` to expose `dietaryTags` prop. No active branches conflict, but this module boundary crossing should be documented."
5. **Git**: Opens PR. Reflect: "Extended shared `RecipeCard` component with tags — boundary crossing into `frontend/core/`, no active conflicts."

> **Builder**: *Reviews. The RecipeCard change is minimal — one new optional prop.* "Approved. Good call flagging the boundary crossing."

**Observation — Module boundary crossing on brownfield**: During v1, module boundaries were clean because we defined them from scratch. On brownfield, the existing code has implicit ownership. The planner needed to modify a shared component. On a team, this is exactly where the semantic intent check + signal system pays off. Solo, it's informational but still useful for tracking.

#### 3.8: Complete Feature Branch

> **Builder**: "Complete feature meal-planner."

**Agent performs**:
1. **Script**: `python scripts/chorus/scripts/update_index.py --branch feat/meal-planner --summary "Weekly meal planner with drag-and-drop. New MealPlan/MealPlanEntry models, meal_slot enum. Extended RecipeCard component." --modules "planner,frontend/planner"`
2. **Git**: `git checkout initiative/platemate-v1.1 && git merge feat/meal-planner`
3. Reports: "Feature `meal-planner` merged. Both features are on the initiative branch. Ready for initiative completion."

---

### Phase 5: Initiative Completion — Canon Update (Not Creation)

Both features are merged into `initiative/platemate-v1.1`. Time to close the outer loop.

> **Builder**: "Complete initiative platemate-v1.1."

**Step 1: Merge code to main**

**Agent performs**:
1. **Git**: `git checkout main && git merge initiative/platemate-v1.1`
2. **Git**: `git branch -d initiative/platemate-v1.1`
3. Reports: "Code merged to `main`. Now synthesizing canon."

**Step 2: Synthesize canon on main — UPDATE mode**

This is where brownfield synthesis differs from greenfield:

**Agent performs**:
4. **Agentic Op — Synthesis**:
   - Reads the codebase on `main` (now ~18k lines, including new planner code and search extensions)
   - Reads active specs in `.cicadas/active/platemate-v1.1/` (updated by Reflect — includes query builder refactor, meal_slot enum)
   - Reads **existing canon** in `.cicadas/canon/` — this is the v1 snapshot. Synthesis must *update* it, not create from scratch.
   - Reads `index.json` (now 6 entries — 4 from v1, 2 from v1.1)
   - **Updates existing canon** (not replaces entirely):
     - `canon/product-overview.md` — adds Meal Planning to feature list, updates success metrics
     - `canon/ux-overview.md` — adds 2 new screens (Planner, Search Filters), updates search screen description
     - `canon/tech-overview.md` — adds MealPlan/MealPlanEntry to data model, documents query builder pattern, adds dietary tags to Recipe
     - `canon/modules/recipes.md` — **updates** with new fields (cuisine, cooking_time, tags), documents the Recipe→DietaryTag join
     - `canon/modules/search.md` — **updates** with query builder pattern, filter parameters
     - `canon/modules/planner.md` — **new** module snapshot
     - `canon/modules/frontend.md` — **updates** with planner UI, RecipeCard tag prop, search filter panel
   - **Extracts key decisions**: query builder refactor rationale, meal_slot enum, RecipeCard boundary crossing
5. Reports: "Canon updated on `main`. Changes: product-overview expanded, tech-overview updated with new schema and query builder, 5 module snapshots updated, 1 new module created. Key decisions from this initiative preserved. Please review."

> **Builder**: *Reviews. Compares the diff between old canon and new canon:*
> - *`recipes.md` now includes tags, cuisine, cooking_time — accurate*
> - *`search.md` documents the query builder — accurate, and the rationale for the refactor is in Key Decisions*
> - *`planner.md` is new and comprehensive*
> - *`product-overview.md` correctly lists meal planning as a feature*
>
> "Ship it."

**Step 3: Archive and commit**

**Agent performs**:
6. **Script**: `python scripts/chorus/scripts/archive.py platemate-v1.1`
7. Removes `platemate-v1.1` from `registry.json`
8. **Git**: Commits: `"chore(cicadas): synthesize canon v1.1 and archive platemate-v1.1"`
9. Reports: "Initiative `platemate-v1.1` complete."

**Observation — Update synthesis vs. creation synthesis**: On v1 (greenfield), synthesis created canon from nothing. On v1.1 (brownfield), synthesis *updated* existing canon — adding new sections, modifying existing module snapshots, creating new module files. This is the harder task. The LLM must:
- Understand what changed vs. what stayed the same
- Preserve existing canon content that wasn't affected by this initiative
- Merge new key decisions with existing ones (not replace them)
- Create new module snapshots for entirely new modules (`planner.md`)

**Final state**:
```
.cicadas/
├── canon/                          ← Updated to reflect v1.1
│   ├── product-overview.md         ← Updated: now includes meal planning
│   ├── ux-overview.md              ← Updated: 2 new screens
│   ├── tech-overview.md            ← Updated: new tables, query builder
│   └── modules/
│       ├── db.md                   ← Updated: 3 new tables
│       ├── auth.md                 ← Unchanged from v1
│       ├── recipes.md              ← Updated: tags, cuisine, cooking_time
│       ├── search.md               ← Updated: query builder, filters
│       ├── social.md               ← Unchanged from v1
│       ├── frontend.md             ← Updated: planner UI, RecipeCard tags
│       └── planner.md              ← NEW module
├── archive/
│   ├── 20260216-...-platemate-v1/  ← v1 specs
│   └── 20260217-...-platemate-v1.1/ ← v1.1 specs
├── index.json                      ← 6 entries (4 from v1, 2 from v1.1)
├── registry.json                   ← Empty
└── config.json
```

---

### Brownfield Observations & Pressure Points

#### What the Brownfield Run Validated

1. **Canon as input to Emergence**: The Clarify and Tech Design subagents produced sharper specs because they read existing canon. On greenfield, elicitation starts from zero. On brownfield, the Agent already knows the schema, architecture, and UX — it asks *targeted* questions instead of open-ended ones.

2. **Update synthesis works**: Canon was updated, not replaced. Existing content for unchanged modules (`auth`, `social`) was preserved. New module (`planner`) was created. Modified modules (`recipes`, `search`) were updated with deltas. Key decisions accumulated across initiatives.

3. **Module boundary crossings are real**: The `RecipeCard.tsx` modification was a boundary crossing that the method caught. On a team with concurrent work, this would be a signal or a conflict. Solo, it's informational and still useful for tracking.

4. **Reflect against existing canon**: On greenfield, Reflect only compared against active specs. On brownfield, the Agent can also flag where the codebase diverges from *existing canon*. This is informational (canon staleness during an initiative is expected) but useful for gauging the growing delta.

5. **Sequencing matters more on brownfield**: `feat/advanced-search` extended the Recipe model. `feat/meal-planner` needed those extensions. The approach's sequencing recommendation was critical — reversing the order would have caused rework.

#### New Gaps from Brownfield

1. **Canon diff review**: The Builder reviewed synthesis output as full files. A *diff view* (what changed in canon from v1 → v1.1) would make review dramatically faster and more reliable.

2. **Update synthesis is harder than creation**: The LLM must distinguish between "preserve this existing content" and "update this section." On large codebases with extensive canon, the risk of accidentally dropping existing canon content during synthesis is real. **Possible fix**: Synthesis should explicitly output a change plan before writing, listing which sections are added, modified, or untouched.

3. **Cross-initiative key decisions**: v1 decisions (RefreshToken, slug-based URLs, feed_events) are in canon. v1.1 decisions (query builder refactor, meal_slot enum) are now added. Over many initiatives, the Key Decisions section could grow unwieldy. **Possible fix**: Age-based pruning or tagging decisions with the initiative that produced them.

4. **Unchanged module canon verification**: Synthesis should verify that modules it claims are "unchanged" truly are — by diffing the relevant source code against what's described in those module snapshots. Otherwise, a subtle change could slip through unnoticed.

5. **Migration ordering**: The method doesn't prescribe how database migrations are coordinated across feature branches. In v1.1, both features added migrations. If they had run in parallel, migration ordering could conflict. The initiative branch handles this via merge order, but it's worth documenting as a pattern.

---
---

## Parallel Initiatives (v1.1 + Calorie Counter)

**Setup**: Builder A is midway through `initiative/platemate-v1.1` (meal planning + advanced search). `feat/advanced-search` has already merged into the initiative branch — the Recipe model now has `cuisine`, `cooking_time_minutes`, and `DietaryTag`. Builder A is about to start `feat/meal-planner`.

Builder B arrives and wants to add a **Calorie Counter** feature: per-ingredient calorie data, recipe-level nutritional breakdown, and daily intake tracking. This is a separate initiative with its own timeline.

Two initiatives. Two developers. Overlapping modules. This is the scenario the registry, signals, and semantic intent checks were designed for.

### Timeline

```
Week 1:   A: advanced-search done, starting meal-planner
          B: starts calorie-counter initiative (Emergence → Kickoff)
Week 2:   A: meal-planner in progress
          B: feat/nutrition-model in progress ← MODULE OVERLAP with Recipe
Week 3:   A: completes v1.1, merges to main, synthesizes
          B: feat/calorie-ui in progress, working against stale main
Week 4:   B: completes calorie-counter, merges to main, synthesizes (must update A's canon)
```

### State When Builder B Begins

```
main (deployed v1 — unchanged, v1.1 code is on its initiative branch)
├── .cicadas/
│   ├── canon/                        ← v1 canon (does NOT include v1.1 changes yet)
│   ├── registry.json
│   │   └── initiatives: { "platemate-v1.1": { ... } }
│   │   └── branches: { "feat/meal-planner": { modules: ["planner","frontend/planner"], initiative: "platemate-v1.1" } }
│   └── ...
```

**Critical detail**: Canon on `main` is **v1 canon**. Builder A's v1.1 work (dietary tags, cuisine, query builder) exists only on `initiative/platemate-v1.1`. Builder B's Emergence will read v1 canon — which describes Recipe *without* the fields A is adding. This is the first problem.

---

### Phase 1: Builder B — Emergence (Against Stale Canon)

#### Step 1.1: Clarify

> **Builder B**: "I want to add calorie tracking to PlateMate."

**Agent performs**:
1. Reads **v1 canon**: `product-overview.md`, `tech-overview.md`, `canon/modules/recipes.md`
2. Reads **registry**: Sees `platemate-v1.1` is active with branches touching `recipes`, `search`, `frontend/search` and `planner`, `frontend/planner`
3. Multi-turn elicitation:

> **Agent**: "I see from canon that Recipe has `ingredients` (JSONB) but no nutritional data. I also see there's an active initiative `platemate-v1.1` that's modifying the Recipe model — specifically adding dietary tags, cuisine, and cooking time. Your calorie feature will also need to modify Recipe.
>
> ⚠️ **Cross-initiative module overlap detected**: Both initiatives touch `recipes`. Builder A has already added fields. Your changes will need to coexist with theirs.
>
> Questions:
> - Calorie data: per-ingredient or per-recipe? Or both?
> - Daily tracking: simple log or goal-based (target calories)?
> - How do you want to handle the overlap with v1.1's Recipe changes?"
>
> **Builder B**: "Per-ingredient calories, with recipe-level rollup calculated from ingredient quantities. Daily tracking with a target goal. For the overlap — I'll coordinate with Builder A. Let's design against current main and rebase when v1.1 merges."

**Agent produces**: `.cicadas/drafts/calorie-counter/prd.md`

**Observation — The Agent surfaced the overlap during Emergence, not during branch registration.** The registry gave it enough information to warn Builder B *before any code was written*. This is the first real payoff of the initiative + branch registration system in a multi-developer context.

#### Step 1.2–1.5: Full Emergence

**Agent produces** all 5 artifacts based on v1 canon + awareness of v1.1's overlap:
- `tech-design.md` designs a `NutritionInfo` table (per-ingredient) and `RecipeNutrition` view/materialized query. Adds `calorie_target` to User model.
- `approach.md` defines 2 partitions:
  1. **`feat/nutrition-model`** — `NutritionInfo` table, recipe calorie rollup, nutrition API. *Modules*: `recipes`, `nutrition`, `db`
  2. **`feat/calorie-ui`** — Daily intake log, calorie tracking UI, recipe nutrition display. *Modules*: `frontend/nutrition`, `nutrition`

> **Agent**: "⚠️ `feat/nutrition-model` declares module `recipes` — same module claimed by `feat/advanced-search` in v1.1. When you register this branch, the registry will flag the overlap. Since `feat/advanced-search` has already merged into its initiative branch, the conflict risk is lower — but your branch will fork from `main`, which doesn't have those changes yet."
>
> **Builder B**: "Understood. I'll rebase onto main after v1.1 merges."

---

### Phase 2: Builder B — Kickoff

> **Builder B**: "Kickoff calorie-counter."

**Agent performs**:
1. **Script**: `python scripts/chorus/scripts/brood.py calorie-counter --intent "Per-ingredient calorie data, recipe nutrition rollup, daily intake tracking"`
   - Promotes drafts → active
   - Registers `calorie-counter` in `registry.json`
2. **Git**: `git checkout -b initiative/calorie-counter` (from `main`)
3. Reports: "Initiative `calorie-counter` is active."

**Registry state** (two active initiatives):
```json
{
  "initiatives": {
    "platemate-v1.1": { "intent": "Meal planning + advanced search", ... },
    "calorie-counter": { "intent": "Per-ingredient calorie data, recipe nutrition rollup, daily intake tracking", ... }
  },
  "branches": {
    "feat/meal-planner": { "modules": ["planner","frontend/planner"], "initiative": "platemate-v1.1" }
  }
}
```

---

### Phase 3: Builder B — `feat/nutrition-model` (Module Overlap)

> **Builder B**: "Start feature nutrition-model."

**Agent performs**:
1. **Agentic Op — Semantic Intent Check**:
   - Reads registry. Sees `feat/meal-planner` (initiative: `platemate-v1.1`).
   - Analyzes: `nutrition-model` intent ("recipe calorie data, nutrition table") vs. `meal-planner` intent ("weekly calendar, drag-and-drop"). **No semantic conflict** — different goals.
   - But notes: "The `platemate-v1.1` initiative also has a completed branch `feat/advanced-search` that touched `recipes` — it added dietary tags, cuisine, and cooking time to Recipe. Your branch also touches `recipes`. The code changes from that branch exist on `initiative/platemate-v1.1` but not yet on `main`."
2. **Git**: `git checkout initiative/calorie-counter`
3. **Script**: `python scripts/chorus/scripts/branch.py feat/nutrition-model --intent "NutritionInfo table, recipe calorie rollup" --modules "recipes,nutrition,db" --initiative calorie-counter`

> **Script output**: `⚠️ WARNING: Module overlaps detected: feat/meal-planner (Overlaps: — none directly)`
>
> **Agent**: "No active branch overlap on `recipes` — `feat/advanced-search` has already merged and is deregistered. However, the initiative `platemate-v1.1` modified `recipes` and those changes aren't on `main` yet. When v1.1 completes and merges to main, you'll need to rebase `initiative/calorie-counter` to pick up those Recipe model changes. Proceeding."

4. Reports: "Feature branch created."

#### Task: Add NutritionInfo Table

> **Builder B**: "Implement task 1 — NutritionInfo model and recipe calorie rollup."

**Agent performs**:
1. **Git**: `git checkout -b task/nutrition-model/nutrition-table`
2. **Implementation**:
   - New `NutritionInfo` table: `ingredient_name` (text), `calories_per_100g`, `protein`, `carbs`, `fat`
   - Recipe calorie rollup: SQL view joining `Recipe.ingredients` JSONB → `NutritionInfo` → sum by quantity
   - API: `GET /api/recipes/{slug}/nutrition`, `GET/POST /api/nutrition-info/`
   - Discovery: The `ingredients` JSONB field in Recipe stores ingredients as `[{"name": "flour", "amount": "2 cups"}]`. To calculate calories, we need to parse the `amount` string into grams. This is harder than expected — need a unit conversion layer.
3. **Agentic Op — Reflect**:
   - Divergence: tech-design didn't anticipate the unit conversion complexity. Updates `tech-design.md` with a `UnitConverter` utility and the parsing logic.
   - **Signal Assessment**: The unit conversion is internal to `nutrition`. No cross-branch impact. No signal.
4. **Git**: Opens PR. Reflect: "Added UnitConverter for ingredient amount parsing. Tech design updated."

> **Builder B**: "Approved."

#### Meanwhile — Builder A completes v1.1

While Builder B is implementing the nutrition model, Builder A finishes `feat/meal-planner`, completes `initiative/platemate-v1.1`, and merges to `main`. Canon is now v1.1 on `main`.

**The world shifts under Builder B**:
- `main` now has dietary tags, cuisine, cooking_time on Recipe
- `main` now has `MealPlan`, `MealPlanEntry` tables
- Canon now describes all of this
- Builder B's initiative branch forked from the *old* `main`

> **Builder B**: "I see v1.1 landed on main. Do I need to rebase?"

**Agent performs**:
1. **Agentic Op — Check Status**: `python scripts/chorus/scripts/check.py`
   - Output: "📥 12 new commits on main since you branched."
2. **Agent**: "Yes, `main` has 12 new commits from `platemate-v1.1`. This includes Recipe model changes (dietary tags, cuisine, cooking_time), MealPlan tables, and updated canon. I recommend rebasing the initiative branch now before starting `feat/calorie-ui`. Here's what I'll do:
   - Rebase `initiative/calorie-counter` onto new `main`
   - Check for merge conflicts — likely in Recipe model migration ordering
   - Re-verify that your `NutritionInfo` table and rollup still work with the expanded Recipe model"
>
> **Builder B**: "Do it."

**Agent performs**:
3. **Git**: `git checkout initiative/calorie-counter && git rebase main`
4. **Conflict**: Migration ordering conflict — v1.1's migrations and calorie-counter's `NutritionInfo` migration have overlapping sequence numbers.
5. **Resolution**: Agent re-sequences the migration. `NutritionInfo` migration now comes after v1.1's migrations.
6. **Verification**: Existing tests pass. The `NutritionInfo` table works alongside the new dietary tags. The recipe calorie rollup query still works — the ingredient JSONB structure didn't change, so the `UnitConverter` is unaffected.
7. Reports: "Rebased successfully. One migration conflict resolved (re-sequenced). All tests pass. Your initiative branch now includes v1.1's Recipe model extensions. Notably, Recipe now has `cuisine`, `cooking_time_minutes`, and a `DietaryTag` relation — these don't affect your calorie rollup, but the nutrition display UI might want to show them."

**Observation — Rebase timing**: The method doesn't prescribe *when* to rebase an initiative branch against main. Builder B chose to rebase between feature branches — a natural pause point. Alternatives: rebase continuously (more disruptive), or only at initiative completion (more conflict risk). The right answer depends on how much `main` is changing.

---

### Phase 3 (continued): Builder B — `feat/calorie-ui`

> **Builder B**: "Start feature calorie-ui."

**Agent performs**:
1. **Semantic Intent Check**: Registry now shows `calorie-counter` as the only active initiative (v1.1 is complete). No conflicts.
2. **Git**: `git checkout initiative/calorie-counter`
3. **Script**: `python scripts/chorus/scripts/branch.py feat/calorie-ui --intent "Daily intake tracking, calorie goals, recipe nutrition display" --modules "frontend/nutrition,nutrition" --initiative calorie-counter`
4. Reports: "Feature branch created. The initiative branch now includes v1.1's code (rebased)."

#### Task: Recipe Nutrition Display

> **Builder B**: "Implement task 4 — show calorie breakdown on recipe detail page."

**Agent performs**:
1. **Git**: `git checkout -b task/calorie-ui/recipe-nutrition`
2. **Implementation**:
   - Adds a `NutritionPanel` component to the recipe detail page
   - Discovery: after the rebase, the recipe detail page now shows dietary tags (from v1.1's `RecipeCard` changes). The `NutritionPanel` should display *alongside* the tags, not replace them. The UX spec didn't account for this because it was drafted against v1 canon.
3. **Agentic Op — Reflect**:
   - Divergence: `ux.md` doesn't mention dietary tags on the recipe page (those came from v1.1). Updates `ux.md` to reflect the actual recipe detail layout including both tags and the new nutrition panel.
   - Notes: "The rebase brought v1.1's UI changes. Active specs have been updated to reflect the combined state."
4. **Git**: Opens PR. Reflect: "Updated UX spec to account for v1.1's dietary tag display on recipe page. NutritionPanel positioned alongside."

> **Builder B**: "Good catch on the layout coexistence. Approved."

**Observation — Reflect after rebase**: When Builder B rebased, the codebase gained v1.1's changes. But the active specs for `calorie-counter` were drafted against v1 canon. Reflect naturally catches this — it compares code against specs and updates specs. The rebase effectively made parts of Builder B's specs stale, and Reflect corrected them. This wasn't an explicit feature of the method — it fell out of Reflect doing its job.

#### Complete Feature Branch

> **Builder B**: "Complete feature calorie-ui."

**Agent performs**:
1. **Script**: `python scripts/chorus/scripts/update_index.py --branch feat/calorie-ui --summary "Recipe nutrition display, daily intake tracker, calorie goals UI" --modules "frontend/nutrition,nutrition"`
2. **Git**: `git checkout initiative/calorie-counter && git merge feat/calorie-ui`
3. Reports: "Both features merged into initiative branch. Ready for completion."

---

### Phase 5: Builder B — Initiative Completion (Second Synthesis on Main)

> **Builder B**: "Complete initiative calorie-counter."

**Step 1: Merge code to main**

**Agent performs**:
1. **Git**: `git checkout main && git merge initiative/calorie-counter`
   - Because Builder B rebased earlier, this is a clean fast-forward-able merge. No conflicts.
2. **Git**: `git branch -d initiative/calorie-counter`
3. Reports: "Code merged to `main`. Now synthesizing canon."

**Step 2: Synthesize canon on main — Second initiative (v1.1 canon exists)**

**This is the critical test**: Canon on `main` was synthesized by Builder A's v1.1 completion. It already includes dietary tags, query builder, meal planner, etc. Now Builder B's synthesis must update *that* canon — not v1 canon.

**Agent performs**:
4. **Agentic Op — Synthesis**:
   - Reads the codebase on `main` (now ~21k lines — v1 + v1.1 + calorie counter)
   - Reads active specs in `.cicadas/active/calorie-counter/` (updated by Reflect after rebase — includes awareness of v1.1's Recipe changes)
   - Reads **existing canon** — this is **v1.1 canon**, not v1. Builder A already updated it.
   - Reads `index.json` (now 8 entries — 4 from v1, 2 from v1.1, 2 from calorie-counter)
   - **Updates existing v1.1 canon**:
     - `canon/product-overview.md` — adds calorie tracking to features, adds health-conscious persona
     - `canon/ux-overview.md` — adds NutritionPanel, daily intake tracker screens
     - `canon/tech-overview.md` — adds NutritionInfo table, UnitConverter, recipe nutrition rollup
     - `canon/modules/recipes.md` — **updates** to document nutrition rollup relationship (Recipe → NutritionInfo via ingredients)
     - `canon/modules/nutrition.md` — **new** module snapshot (NutritionInfo, UnitConverter, calorie rollup)
     - `canon/modules/frontend.md` — **updates** with NutritionPanel, intake tracker
     - `canon/modules/db.md` — adds NutritionInfo table
     - All other modules (`auth`, `social`, `search`, `planner`) — **unchanged**
   - Key decisions: UnitConverter for ingredient parsing, NutritionPanel alongside dietary tags
5. Reports: "Canon updated on `main`. Builds on top of v1.1 canon — v1.1 content preserved, calorie counter content added. Please review."

> **Builder B**: *Reviews. v1.1 content (dietary tags, query builder, planner) is intact. New nutrition module is documented. The recipe module now describes both v1.1's tags AND calorie rollup. Key decisions from all three initiatives (v1, v1.1, calorie-counter) are present.*
>
> "Ship it."

**Step 3: Archive and commit**

**Agent performs**:
6. **Script**: `python scripts/chorus/scripts/archive.py calorie-counter`
7. Removes `calorie-counter` from `registry.json`
8. **Git**: Commits: `"chore(cicadas): synthesize canon v1.1+nutrition and archive calorie-counter"`
9. Reports: "Initiative `calorie-counter` complete."

**Final state**:
```
.cicadas/
├── canon/                          ← v1 + v1.1 + calorie-counter
│   ├── product-overview.md         ← 3 initiatives of content
│   ├── ux-overview.md              ← 11+ screens documented
│   ├── tech-overview.md            ← Full architecture
│   └── modules/
│       ├── db.md                   ← Updated: NutritionInfo table added
│       ├── auth.md                 ← Unchanged since v1
│       ├── recipes.md              ← Updated: nutrition rollup added (on top of v1.1 tags)
│       ├── search.md               ← Unchanged since v1.1
│       ├── social.md               ← Unchanged since v1
│       ├── frontend.md             ← Updated: NutritionPanel, intake tracker
│       ├── planner.md              ← Unchanged since v1.1
│       └── nutrition.md            ← NEW: NutritionInfo, UnitConverter
├── archive/
│   ├── 20260216-...-platemate-v1/
│   ├── 20260217-...-platemate-v1.1/
│   └── 20260218-...-calorie-counter/
├── index.json                      ← 8 entries across 3 initiatives
├── registry.json                   ← Empty
└── config.json
```

---

### Parallel Initiatives: Observations & Pressure Points

#### What Parallel Execution Validated

1. **Registry catches overlap early**: The Agent surfaced the Recipe module overlap *during Emergence*, before any code was written. Builder B could make an informed decision about coordination strategy (rebase later) instead of discovering conflicts at merge time.

2. **Initiatives are truly independent branches**: Builder A's v1.1 and Builder B's calorie-counter had separate initiative branches, separate active specs, separate feature branches. They didn't block each other. Builder B chose when to rebase.

3. **Serial synthesis on main works**: v1.1 synthesized first (canon v1→v1.1). Calorie-counter synthesized second (canon v1.1→v1.1+nutrition). Each synthesis updated the previous canon, not v1 canon. The overwrite-on-main pattern handles this cleanly — no merge conflicts on canon files.

4. **Reflect corrects post-rebase drift**: When Builder B rebased, the codebase changed beneath the active specs. Reflect naturally caught the divergence (v1.1's dietary tags appearing on recipe pages). No special "post-rebase" operation needed — Reflect just works™.

5. **Signals work across initiatives**: If Builder A's Recipe changes had happened *during* Builder B's active coding (rather than before B started), A's Agent would have signaled. The signal appears in the initiative's signal board, and B's Agent would surface it during status checks.

#### New Gaps from Parallel Execution

1. **Canon is stale for the second initiative's Emergence**: Builder B's specs were drafted against v1 canon, but by the time B finishes, main is on v1.1 canon. Reflect corrected this during implementation, but the *drafting* phase used outdated context. **Possible fix**: During Emergence, the Agent should read not just canon but also the active specs of other in-flight initiatives — surfacing planned (but not yet merged) changes to shared modules.

2. **No cross-initiative signal mechanism**: The current signal system is *intra-initiative* — signals are scoped to one initiative's signal board. Builder A's Recipe changes couldn't directly signal Builder B's initiative. The Agent caught the overlap via the registry, but there's no formal notification channel between initiatives. **Possible fix**: Initiative-level signals or a global signal board in `registry.json`.

3. **Rebase timing is undefined**: The method doesn't prescribe when an initiative branch should rebase against main. Builder B rebased between feature branches — a good heuristic. But on a larger team with many initiatives merging frequently, this becomes a strategic decision. **Possible approaches**: rebase before each new feature branch, rebase only at initiative completion, or continuous rebase.

4. **Initiative merge ordering**: Builder A finished first, so v1.1 merged first. But what if both finished simultaneously? The merge order determines which synthesis is "first" (creating/updating) vs. "second" (updating the first's output). With the overwrite-on-main pattern, order doesn't create *conflicts*, but it does affect which initiative's synthesis sees which canon. **Rule of thumb**: merge initiatives in the order they completed. If truly simultaneous, the team needs to coordinate.

5. **Active specs from different initiatives don't know about each other**: Builder B's active specs described the calorie feature against v1 state. Builder A's active specs described v1.1 features. Neither set references the other. At synthesis time, the LLM synthesizes from *one initiative's* specs + the full codebase. It works, but the synthesis for initiative B doesn't have A's "why" (key decisions) from A's specs — it only has them if they were already embedded in canon by A's prior synthesis. If B merges before A, B's synthesis would miss A's rationale entirely (since A hasn't synthesized yet). **Possible fix**: The synthesis prompt should instruct the LLM to read active specs from *all* in-flight initiatives, not just its own.

6. **Migration coordination across initiatives**: Builder B's rebase resolved migration conflicts manually. On a larger team, multiple initiatives adding database migrations creates a combinatorial conflict surface. The initiative branch isolates this somewhat (conflicts appear at rebase, not at merge), but it's still a pain point. **Possible fix**: Use a central migration sequence counter in `registry.json`, or adopt timestamp-based migration naming.

7. **Canon accumulation over many initiatives**: After 3 initiatives, the Key Decisions section spans v1, v1.1, and calorie-counter. After 10 initiatives, this becomes a chapter. The canon is getting *bigger* each cycle, but never *smaller*. Synthesis is additive — it doesn't cull obsolete documentation. Over time, canon drifts toward comprehensive reference docs rather than concise snapshots. **Possible fix**: Add a "prune" pass to synthesis — asking the LLM to identify and remove canon sections that are no longer accurate or relevant. Or, version the Key Decisions (each tagged with its initiative) so they can be archived when they become historical.
