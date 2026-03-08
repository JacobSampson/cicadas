
---
next_section: 'Design Goals & Constraints'
---

# UX Design: Worktrees for Parallel Execution

## Progress

- [x] Design Goals & Constraints
- [x] User Journeys & Touchpoints
- [x] Information Architecture
- [x] Key User Flows
- [x] UI States
- [x] Copy & Tone
- [x] Visual Design Direction
- [x] UX Consistency Patterns
- [x] Responsive & Accessibility

---

## Design Goals & Constraints

**Primary goal:** The Builder should feel that parallel execution *just works* — worktrees appear when the plan calls for parallelism and disappear when the work is done, without adding new commands or concepts to learn. First-use should feel like a natural extension of today's `branch.py` workflow, not a new mode.

**Design constraints:**
- Platform: Terminal / CLI only. No web UI, no TUI (rich formatting is fine as decoration, not required).
- Existing design system: Cicadas CLI conventions — plain text output with prefixes (`[OK]`, `[WARN]`, `[ERR]`) indicating status; paths printed in full. New output follows these same conventions.
- Technical constraints: All worktree state is emitted at the moment of command execution; no real-time updates or watchers. `context.md` is written to the filesystem, not streamed.

---

## User Journeys & Touchpoints

### Parallel Builder — From Emergence to Parallel Execution

**Entry point:** Finishes `approach.md` with the emergence agent, which has populated the `partitions` block. Runs `kickoff.py`.

**First touchpoint:** `kickoff.py` output — sees a new message: `[INFO] Parallel partitions detected: feat/api, feat/ui. Running conflict check...` followed by `check.py` output. No prompt required; this is automatic.

**Key moment:** Running `branch.py feat/api` and seeing `[OK] Worktree created: ../cicadas-feat-api` — immediately recognizes that the right directory exists and an agent can be pointed at it, with no extra commands needed.

**Exit state:** `archive.py` on `feat/api` prints `[OK] Worktree removed: ../cicadas-feat-api` — clean completion with no manual cleanup needed.

**Pain points to design around:**
- Confusion about where the worktree lives (mitigate: always print the full path).
- Fear of "what happens if I run this twice" (mitigate: idempotent with a clear `[INFO] Worktree already exists` message).
- Missing context on what `context.md` is for (mitigate: print a one-line note on creation).

---

### Solo Builder — Sequential Work, Unchanged Experience

**Entry point:** `approach.md` has `partitions` with all `depends_on` non-empty (strict sequence). Runs `kickoff.py`.

**First touchpoint:** `kickoff.py` output — no mention of worktrees, no new messages. Identical to today.

**Key moment:** Running `branch.py feat/partition-a` — output unchanged from today. Builder never encounters worktree concepts.

**Exit state:** `archive.py` — unchanged. No reference to worktrees.

**Pain points to design around:**
- Accidental confusion if the Builder adds `depends_on: []` without intending parallelism — mitigate with a clear `kickoff.py` warning that lists which partitions will be parallelized.

---

## Information Architecture

This initiative adds no new commands or navigation paths. The CLI "IA" is extended in-place:

```
Cicadas CLI
├── kickoff.py          ← [MODIFIED] prints parallel partition summary + auto-runs check.py
├── branch.py           ← [MODIFIED] creates worktree (parallel) or plain branch (sequential)
├── status.py           ← [MODIFIED] new "Worktrees" section in output
├── check.py            ← [MODIFIED] new stale-worktree detection in output
├── archive.py          ← [MODIFIED] prints worktree removal on completion
├── prune.py            ← [MODIFIED] prints worktree removal on rollback
└── abort.py            ← [MODIFIED] prints worktree removal on abort
```

**New filesystem artifact (per worktree):**
```
{worktree-root}/
└── context.md          ← injected by branch.py; ephemeral, not committed
```

**Navigation model:** N/A — CLI only. Discovery is via `status.py` output and printed paths.

---

## Key User Flows

### Flow 1: Kickoff with Parallel Partitions (Happy Path)

1. Builder runs: `python cicadas/scripts/kickoff.py worktrees-parallel-execution --intent "..."`
2. Script detects `depends_on: []` on ≥1 partition in `approach.md`.
3. Output:
   ```
   [OK]   Initiative registered: worktrees-parallel-execution
   [INFO] Parallel partitions detected: feat/api, feat/ui
   [INFO] Running conflict check before parallel execution...
   [OK]   No module conflicts detected.
   [OK]   Initiative branch created: initiative/worktrees-parallel-execution
   ```
4. Builder proceeds to start feature branches.

**Alternate path — conflict detected:**
```
[OK]   Initiative registered: worktrees-parallel-execution
[INFO] Parallel partitions detected: feat/api, feat/ui
[INFO] Running conflict check before parallel execution...
[WARN] Module conflict: feat/api and feat/ui both declare ownership of 'core/engine'
[WARN] Resolve conflict in approach.md before starting parallel branches.
```
- `kickoff.py` still completes registration and creates the initiative branch, but clearly flags the conflict before the Builder proceeds.

---

### Flow 2: Starting a Parallel Feature Branch (Happy Path)

1. Builder runs: `python cicadas/scripts/branch.py feat/api --intent "..." --modules "api,gateway" --initiative worktrees-parallel-execution`
2. `branch.py` reads `approach.md`, finds `feat/api` has `depends_on: []`.
3. Creates worktree at `../cicadas-feat-api`.
4. Writes `context.md` to worktree root.
5. Output:
   ```
   [OK]   Branch registered: feat/api
   [OK]   Worktree created: /Users/dan/dev/code/ai/cicadas-feat-api
   [INFO] context.md written to worktree root (canon summary + module snapshots + tasks)
   [INFO] Point your agent at: /Users/dan/dev/code/ai/cicadas-feat-api
   ```

**Alternate path — sequential branch (depends_on non-empty):**
```
[OK]   Branch registered: feat/integration
[OK]   Branch created: feat/integration
```
*(No worktree lines — identical to today's output.)*

**Alternate path — worktree already exists:**
```
[INFO] Worktree already exists at: /Users/dan/dev/code/ai/cicadas-feat-api
[OK]   Branch registered: feat/api
```

**Alternate path — path conflict:**
```
[ERR]  Worktree path already in use: /Users/dan/dev/code/ai/cicadas-feat-api
[ERR]  Remove the existing directory or use a different branch slug.
```
*(Exits non-zero. No registry write.)*

---

### Flow 3: Status Check with Active Worktrees (Happy Path)

1. Builder runs: `python cicadas/scripts/status.py`
2. Output (new Worktrees section appended after Branches):
   ```
   Project: cicadas

   Active Initiatives (1):
     initiative/worktrees-parallel-execution

   Feature Branches (2):
     feat/api         [registered]
     feat/integration [registered]

   Worktrees (1):
     feat/api  →  /Users/dan/dev/code/ai/cicadas-feat-api  [clean]  abc1234 add auth middleware
   ```

**Alternate path — worktree path missing:**
```
   Worktrees (1):
     feat/api  →  /Users/dan/dev/code/ai/cicadas-feat-api  [MISSING]
```

---

### Flow 4: Archiving a Branch with a Worktree (Happy Path)

1. Builder runs: `python cicadas/scripts/archive.py feat/api --type branch`
2. Output:
   ```
   [OK]   Worktree removed: /Users/dan/dev/code/ai/cicadas-feat-api
   [OK]   Branch deregistered: feat/api
   [OK]   Specs archived.
   ```

**Alternate path — dirty worktree:**
```
[WARN] Worktree has uncommitted changes: /Users/dan/dev/code/ai/cicadas-feat-api
[WARN] Use --force to remove anyway, or commit/stash changes first.
```
*(Exits non-zero without `--force`.)*

**Alternate path — worktree directory already gone:**
```
[WARN] Worktree directory not found (already removed): /Users/dan/dev/code/ai/cicadas-feat-api
[OK]   Branch deregistered: feat/api
[OK]   Specs archived.
```

---

## UI States

### `branch.py` — Feature Branch Creation

| State | Trigger | Output |
|-------|---------|--------|
| **Parallel branch** | `depends_on: []` in `approach.md` | `[OK] Worktree created: {path}` + `[INFO] context.md written...` |
| **Sequential branch** | `depends_on` non-empty | `[OK] Branch created: {name}` (unchanged) |
| **Already exists** | Worktree path already present on disk | `[INFO] Worktree already exists at: {path}` |
| **Git failure** | `git worktree add` fails | `[ERR] git worktree add failed: {message}` — exits non-zero, no registry write |
| **Path conflict** | Target path exists but isn't a git worktree | `[ERR] Worktree path already in use: {path}` |
| **No partitions block** | `approach.md` has no `partitions` block | Creates plain branch (backward-compatible fallback) |
| **Unknown partition** | Branch name not in `partitions` block | `[WARN] Partition not found in approach.md — treating as sequential` |

---

### `status.py` — Worktrees Section

| State | Trigger | Output |
|-------|---------|--------|
| **No worktrees** | No branches have `worktree_path` | Worktrees section omitted entirely |
| **Clean worktree** | No uncommitted changes | `[clean]  {HEAD commit summary}` |
| **Dirty worktree** | Uncommitted changes present | `[dirty]  {HEAD commit summary}` |
| **Missing worktree** | Path recorded but directory gone | `[MISSING]` |

---

### `kickoff.py` — Parallel Detection

| State | Trigger | Output |
|-------|---------|--------|
| **All sequential** | All partitions have `depends_on` non-empty | No extra lines — identical to today |
| **Parallel detected, no conflicts** | ≥1 `depends_on: []`, clean `check.py` | `[INFO] Parallel partitions: {list}` + `[OK] No module conflicts` |
| **Parallel detected, conflicts** | ≥1 `depends_on: []`, `check.py` finds overlap | `[WARN] Module conflict: {details}` — registration completes, execution blocked by warning |

---

## Copy & Tone

**Voice:** Direct, informative, and terse. Cicadas speaks like a reliable senior engineer — it tells you exactly what happened, what it did, and what you should do next. No exclamation points. No filler.

**Key principles:**
- Always print the full path when a worktree is created or removed (never just the branch name).
- Never leave the Builder guessing what happened — every significant state change has a printed line.
- Error messages name the thing that failed and what to do about it.
- Warnings don't block; errors do.

**Critical copy samples:**

| Context | Copy |
|---------|------|
| Worktree created | `[OK]   Worktree created: {absolute-path}` |
| context.md written | `[INFO] context.md written to worktree root (canon summary + module snapshots + tasks)` |
| Point agent here | `[INFO] Point your agent at: {absolute-path}` |
| Worktree already exists | `[INFO] Worktree already exists at: {absolute-path}` |
| Worktree removed | `[OK]   Worktree removed: {absolute-path}` |
| Dirty worktree on teardown | `[WARN] Worktree has uncommitted changes: {path}` |
| Dirty teardown recovery | `[WARN] Use --force to remove anyway, or commit/stash changes first.` |
| Path conflict error | `[ERR]  Worktree path already in use: {path}` |
| Missing worktree (status) | `[MISSING]` |
| Parallel partitions detected | `[INFO] Parallel partitions detected: {comma-list}` |
| Conflict at kickoff | `[WARN] Module conflict: {branch-a} and {branch-b} both declare ownership of '{module}'` |

---

## Visual Design Direction

**Style:** Terminal monospace — no color requirements (ANSI color is optional decoration, not required for comprehension).
**Existing design system:** Extend Cicadas' existing `[OK]` / `[INFO]` / `[WARN]` / `[ERR]` prefix convention. No new visual language.
**Density:** Compact — one line per event. Multi-line output only when listing multiple items (e.g. `status.py` Worktrees section).
**Mood reference:** "A tool that respects your time."

---

## UX Consistency Patterns

### Output Prefix Hierarchy
Extends the existing Cicadas convention:
- `[OK]  ` — operation succeeded, something changed.
- `[INFO]` — informational, no action required.
- `[WARN]` — something unexpected but recoverable; execution continues.
- `[ERR] ` — operation failed; exits non-zero.

All prefixes are padded to 6 characters so output columns align.

### Path Display
- Always print absolute paths for worktree locations.
- Never truncate paths, even if long.
- Print path immediately after `[OK] Worktree created:` — no line-wrap.

### Idempotency Signaling
- Already-exists states use `[INFO]`, not `[OK]` — `[OK]` implies something changed.
- Already-gone state (worktree directory missing at teardown) uses `[WARN]` + continues.

### Backward Compatibility Signaling
- If `approach.md` has no `partitions` block, no extra output. Silent fallback to existing behavior.
- Sequential branches (`depends_on` non-empty) produce no new output lines.

---

## Responsive & Accessibility

**Breakpoints:** N/A — CLI only.
**Accessibility standards:** N/A — terminal output; no WCAG target.
**Key requirements:**
- No color-only signaling — all states are communicated by the `[prefix]` text, not color alone.
- Screen reader: N/A.
- `context.md` is plain Markdown — readable in any terminal editor without special tooling.
