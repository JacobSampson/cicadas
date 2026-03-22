
---
next_section: 'Design Goals & Constraints'
---

# UX Design: Git Worktree Support

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

**Primary goal:** The user should feel that worktree and remote storage support "just works" — no mental overhead, no special commands for day-to-day use. Setup is a one-time operation; after that, Cicadas behaves identically whether in a worktree or the main repo.

**Design constraints:**
- **CLI-only** — All interaction is via terminal commands and script output.
- **Existing CLI patterns** — Must follow established Cicadas script conventions (argparse, consistent exit codes, colored output via existing utils).
- **Transparent operation** — Scripts should not require `--worktree` flags for normal use; worktree detection is automatic.
- **Backward compatible** — Existing `.cicadas` directories (non-symlinked) must continue to work unchanged.

**Skip condition:** N/A — While this is infrastructure, it has CLI touchpoints (`init.py --link`, status output, error messages).

---

## User Journeys & Touchpoints

### Solo Builder — Setting Up Worktree Workflow

**Entry point:** User has an existing Cicadas project and wants to work on multiple partitions in parallel.
**First touchpoint:** `python scripts/init.py --link ~/shared-cicadas` (or symlink manually)
**Key moment:** Running `status.py` from a new worktree and seeing the same registry as the main repo — "it just works."
**Exit state:** Multiple worktrees, each on a different feature branch, all sharing state.
**Pain points to design around:**
- Confusion about whether `.cicadas` is "here" or "somewhere else"
- Accidentally running `init.py` without `--link` and creating a duplicate `.cicadas`

---

### Distributed Team — Remote Shared Memory

**Entry point:** Team wants to share Cicadas state across machines (Post-MVP, but UX designed now).
**First touchpoint:** `python scripts/init.py --link /path/to/submodule` after setting up the submodule externally.
**Key moment:** Running `status.py` on Machine B and seeing the branch registered on Machine A.
**Exit state:** Team members see consistent state; conflicts are surfaced, not silently lost.
**Pain points to design around:**
- Sync failures that leave state inconsistent
- Unclear error messages when hooks fail
- Not knowing if state is "fresh" or stale

---

## Information Architecture

### Command Structure

```
scripts/
├── init.py              # Extended: --link <path> option
├── status.py            # Extended: worktree indicator in output
├── branch.py            # Unchanged (path resolution handles worktrees)
├── kickoff.py           # Unchanged
├── check.py             # Unchanged
├── signal.py            # Unchanged
├── archive.py           # Unchanged
├── update_index.py      # Unchanged
└── ... (other scripts)  # Unchanged
```

### Navigation Model

**Primary nav:** Direct script invocation (`python scripts/<name>.py`)
**Secondary nav:** `--help` flags on each script
**Key entry points:**
- `init.py --link` — One-time setup for symlink mode
- `status.py` — Primary state inspection (shows worktree indicator)

---

## Key User Flows

### Flow 1: Initialize with Symlink (Happy Path)

1. User runs `python scripts/init.py --link ~/shared-cicadas`
2. Script checks if `~/shared-cicadas` exists; if not, creates it
3. Script creates `.cicadas` as symlink → `~/shared-cicadas`
4. Script initializes standard structure inside the target (if empty)
5. Script adds `.cicadas` to `.gitignore` (if not already present)
6. Output: `Initialized .cicadas → ~/shared-cicadas`

**Alternate path A:** `.cicadas` already exists as a directory
- Output: `Error: .cicadas already exists. Remove it first or use --force to replace.`

**Alternate path B:** `.cicadas` already exists as a symlink
- Output: `Error: .cicadas is already a symlink → /current/target. Use --force to replace.`

---

### Flow 2: Run Status from Worktree

1. User is in a Git worktree (e.g., `~/proj-worktree-auth`)
2. User runs `python scripts/status.py`
3. Script detects worktree, resolves `.cicadas` (follows symlink if present)
4. Script displays normal status output
5. If in worktree, append indicator: `(worktree: ~/proj-worktree-auth)`

**Alternate path:** `.cicadas` not found
- Script walks up to main repo root, checks there
- If still not found: `Error: .cicadas not found. Run init.py first.`

---

### Flow 3: Sync Hook Failure (Post-MVP)

1. User runs `branch.py` to register a new branch
2. Pre-write hook is configured; script runs it
3. Hook exits non-zero (e.g., `git pull` conflict)
4. Script aborts write, displays hook stderr
5. Output: `Error: Pre-write hook failed. Resolve the conflict and retry.`

**Alternate path:** Hook succeeds but file changed during sync
- Output: `Warning: registry.json changed during sync. Overwrite local changes? [y/N]`

---

## UI States

### `init.py --link` Output

| State | Trigger | What the User Sees |
|-------|---------|-------------------|
| **Success** | Symlink created | `✓ Initialized .cicadas → /path/to/target` |
| **Target created** | Target dir didn't exist | `Created /path/to/target\n✓ Initialized .cicadas → /path/to/target` |
| **Already exists (dir)** | `.cicadas` is a directory | `✗ Error: .cicadas already exists as a directory. Remove it or use --force.` |
| **Already exists (link)** | `.cicadas` is a symlink | `✗ Error: .cicadas already linked → /other/path. Use --force to replace.` |
| **Force replace** | `--force` flag used | `Removed existing .cicadas\n✓ Initialized .cicadas → /path/to/target` |

---

### `status.py` Output (Worktree Indicator)

| State | Trigger | What the User Sees |
|-------|---------|-------------------|
| **Main repo** | Running from main repo | Normal output (no indicator) |
| **Worktree** | Running from a worktree | Normal output + `(worktree)` suffix on first line |
| **Symlinked .cicadas** | `.cicadas` is a symlink | Normal output + `(.cicadas → /path/to/target)` in header |

---

### Sync Hook States (Post-MVP)

| State | Trigger | What the User Sees |
|-------|---------|-------------------|
| **Hook running** | Pre-write hook executing | `Running pre-write hook...` |
| **Hook success** | Exit 0 | (silent, proceed to write) |
| **Hook failure** | Exit non-zero | `✗ Pre-write hook failed:\n{stderr}\nAborted.` |
| **Conflict detected** | File changed during sync | `⚠ registry.json changed during sync. Overwrite? [y/N]` |

---

## Copy & Tone

**Voice:** Direct, technical, minimal. Cicadas is a developer tool; users expect terse, actionable output.

**Key principles:**
- Use `✓` for success, `✗` for errors, `⚠` for warnings
- Error messages state what happened and what to do next
- No chatty explanations; link to docs for details
- Use absolute paths in output for clarity

**Critical copy samples:**

| Context | Copy |
|---------|------|
| Success (init --link) | `✓ Initialized .cicadas → {path}` |
| Error (already exists) | `✗ Error: .cicadas already exists. Remove it or use --force.` |
| Warning (sync conflict) | `⚠ {file} changed during sync. Overwrite? [y/N]` |
| Hook failure | `✗ Pre-write hook failed:\n{stderr}\nAborted.` |
| Worktree indicator | `(worktree)` or `(.cicadas → {path})` |

---

## Visual Design Direction

**Style:** Terminal / CLI — monospace text, ANSI colors for status indicators.

**Color palette:**
- Green (`\033[32m`) — Success messages, checkmarks
- Red (`\033[31m`) — Errors, X marks
- Yellow (`\033[33m`) — Warnings
- Cyan (`\033[36m`) — Informational (paths, hints)
- Default — Normal output

**Typography:** System monospace (terminal default)

**Spacing & density:** Compact — one message per line, no blank lines except to separate sections.

**Existing design system:** Follow existing Cicadas CLI output patterns (see `status.py`, `branch.py` for examples).

---

## UX Consistency Patterns

### Exit Codes
- `0` — Success
- `1` — Error (user-actionable)
- `2` — Error (system/unexpected)

### Flag Patterns
- `--link <path>` — Specify symlink target
- `--force` — Overwrite existing state (destructive, requires explicit opt-in)
- `--help` — Standard argparse help

### Confirmation Patterns
- Destructive operations (e.g., `--force`) do not prompt; the flag itself is the confirmation
- Sync conflicts prompt interactively: `[y/N]` (default No)

### Error Message Pattern
```
✗ Error: {what happened}.
{what to do next, if actionable}
```

### Success Message Pattern
```
✓ {action completed} → {result or path}
```

---

## Responsive & Accessibility

**Breakpoints:** N/A — CLI only, terminal width handled by user's terminal emulator.

**Accessibility standards:** N/A for WCAG (no GUI).

**Key requirements:**
- **Screen reader support:** Output is plain text; no special requirements.
- **Color:** All status indicators have text equivalents (`✓`, `✗`, `⚠`) so color is not the only signal.
- **No animations:** No spinners or progress bars that would confuse screen readers.

