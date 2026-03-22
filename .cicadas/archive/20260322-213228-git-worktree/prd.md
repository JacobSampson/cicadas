---

## next_section: 'Executive Summary'

# PRD: Git Worktree Support

## Progress

- Executive Summary
- Project Classification
- Success Criteria
- User Journeys
- Scope & Phasing
- Functional Requirements
- Non-Functional Requirements
- Open Questions
- Risk Mitigation

## Executive Summary

Enable Cicadas to operate across Git worktrees and shared/remote `.cicadas` storage, allowing parallel development workflows where each feature branch runs in its own worktree while sharing a single source of truth for registry, specs, and signals. This unlocks true parallel implementation for human-AI teams working on multiple partitions simultaneously.

### What Makes This Special

- **True Parallelism** — Multiple agents or developers can work on different partitions concurrently, each in their own worktree, without stepping on each other.
- **Shared State, Local Speed** — A single `.cicadas` directory (symlinked or submoduled) keeps all worktrees in sync without requiring network calls for every operation.
- **Transparent to Agents** — Agents continue to work on "a branch" without needing to understand worktree mechanics; the infrastructure handles coordination.

## Project Classification

**Technical Type:** Developer Tool / Infrastructure
**Domain:** Infrastructure
**Complexity:** Medium — Requires changes to path resolution, write coordination, and optional sync hooks, but no fundamental architectural changes.
**Project Context:** Brownfield — Extending the existing Cicadas orchestrator to support worktree-based workflows.

---

## Success Criteria

### User Success

A user achieves success when they can:

1. **Run multiple feature branches in parallel** — Each branch in its own worktree, all sharing the same `.cicadas` state.
2. **Set up shared storage with one command** — Point `.cicadas` to a symlink/submodule and have everything "just work."
3. **Avoid data loss from concurrent writes** — Sync-before-write ensures no silent overwrites.

### Technical Success

The system is successful when:

1. **All existing scripts work unchanged in worktree environments** — `status.py`, `branch.py`, `kickoff.py`, etc. resolve paths correctly whether in main repo or worktree.
2. **Write operations are safe** — Sync hook (when configured) runs before writes; conflicts are surfaced, not silently lost.

### Measurable Outcomes

- 100% of existing tests pass when run from a worktree (not just the main repo).
- Zero data loss in concurrent write scenarios when sync hook is configured.

---

## User Journeys

### Journey 1: Solo Builder — Parallel Partition Development

A solo developer is working on a large initiative with three partitions. They want to context-switch between partitions without stashing or losing flow state. They run `git worktree add ../proj-feat-auth feat/auth` and open that directory in a second IDE window. Both windows share the same `.cicadas` — when they run `status.py` in either, they see the same registry and signals. They implement `feat/auth` in one window while keeping `feat/api` open in another. When `feat/auth` is ready, they merge it; the worktree can be removed. The shared `.cicadas` reflects the completed work immediately.

**Requirements Revealed:** Worktree-aware path resolution, shared `.cicadas` via symlink, transparent operation of existing scripts.

---

### Journey 2: Distributed Team — Remote Shared Memory

A team of three developers works on the same initiative from different machines. They configure `.cicadas` as a Git submodule pointing to a shared repo (or an S3-synced directory). Before any Cicadas script writes to `.cicadas`, a sync hook pulls the latest state. After the write, another hook pushes. If two developers try to register branches simultaneously, the second one sees a conflict and is prompted to resolve it. The team never loses work, and the registry stays consistent.

**Requirements Revealed:** Remote storage support (symlink/submodule detection), sync hooks (pre-write, post-write), conflict detection and prompting.

---

### Journey Requirements Summary


| User Type            | Key Requirements                                                                  |
| -------------------- | --------------------------------------------------------------------------------- |
| **Solo Builder**     | Worktree path resolution, symlink support, transparent script operation           |
| **Distributed Team** | Remote storage detection, sync hooks, conflict detection, sequential write safety |


---

## Scope

### MVP — Minimum Viable Product (v1)

**Core Deliverables:**

- Worktree-aware path resolution in all scripts (detect `.cicadas` correctly from any worktree)
- Symlink support for `.cicadas` (scripts follow symlinks transparently)
- Optional `worktree: true` flag in `emergence-config.json` or `config.json` to hint concurrent operation
- Documentation for setting up worktree-based workflows

**Quality Gates:**

- All existing tests pass when run from a worktree
- New tests covering symlinked `.cicadas` scenarios

### Growth Features (Post-MVP)

**v2: Remote Sync Hooks**

- Configurable pre-write and post-write hooks (shell commands)
- Hook configuration in `.cicadas/config.json`
- Conflict detection: if sync pulls changes that conflict with pending write, prompt user

**v3: First-Class Submodule Support**

- `init.py --remote <repo-url>` to set up `.cicadas` as a submodule
- Auto-commit to submodule after writes (default behavior); future enhancement to synchronize commits with base branch PR workflow
- S3/rsync backend examples in documentation

### Vision (Future)

- Real-time sync via file watchers (inotify/fsevents)
- Lock-based coordination for high-contention scenarios
- Dashboard showing all active worktrees and their branch status

---

## Functional Requirements

### 1. Path Resolution

**FR-1.1:** All scripts must resolve `.cicadas` correctly when run from a Git worktree.

- Use `git rev-parse --show-toplevel` or equivalent to find the main repo root.
- If `.cicadas` is a symlink, follow it transparently.
- `get_project_root()` in `utils.py` must handle worktree scenarios.

**FR-1.2:** Scripts must detect when running in a worktree vs. main repo.

- Provide a utility function `is_worktree()` that returns `True` if current directory is a worktree.
- This is informational; scripts should behave identically in both cases.

---

### 2. Symlink/Remote Storage Support

**FR-2.1:** `.cicadas` may be a symlink pointing to an external directory.

- All file operations must follow the symlink.
- `init.py` should support `--link <path>` to create `.cicadas` as a symlink to an external directory.
- If the target directory does not exist, create it.

**FR-2.2:** Scripts must not assume `.cicadas` is inside the Git working tree.

- Avoid `git add .cicadas` or similar commands that assume `.cicadas` is tracked.
- Gitignore `.cicadas` by default when using symlink mode.

---

### 3. Sync Hooks (Post-MVP)

**FR-3.1:** Support configurable pre-write and post-write hooks.

- Configuration in `.cicadas/config.json`: `{ "hooks": { "pre_write": "cmd", "post_write": "cmd" } }`
- Pre-write hook runs before any JSON write (`registry.json`, `index.json`, etc.).
- Post-write hook runs after successful write.

**FR-3.2:** If pre-write hook fails (non-zero exit), abort the write and surface the error.

- Do not silently proceed; prompt the user with the hook's stderr.

**FR-3.3:** Conflict detection: if pre-write sync pulls changes, detect if the file being written has changed since it was read.

- Compare file mtime or content hash before write.
- If conflict detected, prompt user: "File changed during sync. Overwrite? [y/N]"

---

### 4. Worktree Awareness

**FR-4.1:** Scripts must not record local worktree paths in shared state.
- Since `.cicadas` may be synced remotely, local paths would leak environment details and be meaningless to other machines.
- `registry.json` entries remain path-agnostic.

**FR-4.2:** `status.py` may indicate when running from a worktree (informational, local display only).
- No worktree metadata is persisted to shared state.

---

## Non-Functional Requirements

- **Performance:** Path resolution overhead must be < 50ms. Sync hooks are external and their latency is out of scope.
- **Reliability:** No data loss in concurrent write scenarios when sync hooks are configured. Without hooks, last-write-wins is acceptable (documented behavior).
- **Security:** Sync hooks execute arbitrary shell commands; document the trust implications. Do not execute hooks from untrusted `.cicadas` directories.
- **Maintainability:** All worktree-related logic should be isolated in `utils.py` to minimize changes across scripts.

---

## Open Questions

_All resolved during Clarify._

### Resolved

- **OQ-1:** Should `init.py --link` create the target directory if it doesn't exist? **Yes** — create it if missing.
- **OQ-2:** For submodule mode (Post-MVP), should Cicadas auto-commit to the submodule? **Yes** — auto-commit on writes for now. Future enhancement: synchronize submodule commits with the base branch PR workflow.
- **OQ-3:** Should worktree path be recorded in `registry.json`? **No** — since `.cicadas` may be synced remotely, we avoid exposing local path details.

---

## Risk Mitigation


| Risk                                                          | Likelihood | Impact | Mitigation                                                                 |
| ------------------------------------------------------------- | ---------- | ------ | -------------------------------------------------------------------------- |
| Path resolution breaks on edge-case Git configurations        | Medium     | High   | Comprehensive test suite covering worktrees, symlinks, and nested repos    |
| Sync hooks introduce latency that frustrates users            | Medium     | Medium | Hooks are optional and off by default; document performance implications   |
| Concurrent writes cause data loss before hooks are configured | Medium     | Medium | Document that without hooks, last-write-wins; recommend hooks for team use |
| Symlinked `.cicadas` confuses Git (tries to track it)         | Low        | Medium | Default `.gitignore` entry for `.cicadas` when symlink mode is used        |


