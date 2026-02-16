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
