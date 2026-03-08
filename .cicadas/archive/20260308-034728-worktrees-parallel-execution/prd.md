
---
next_section: 'Executive Summary'
---

# PRD: Worktrees for Parallel Execution

## Progress

- [x] Executive Summary
- [x] Project Classification
- [ ] Success Criteria
- [ ] User Journeys
- [ ] Scope & Phasing
- [ ] Functional Requirements
- [ ] Non-Functional Requirements
- [ ] Open Questions
- [ ] Risk Mitigation

## Executive Summary

Cicadas manages multi-partition initiatives by registering feature branches — but today all branches are plain git branches requiring sequential checkout, even when their work is logically independent. This initiative adds **git worktree** support so that partitions with no declared dependencies are automatically checked out into isolated filesystem directories, enabling true parallel execution by multiple agents or terminals simultaneously. Sequential partitions continue to use plain branches — worktrees are used only where the dependency DAG in `approach.md` allows it.

### What Makes This Special

- **DAG-Driven Parallelism** — The dependency graph declared in `approach.md` determines which partitions get worktrees automatically; the orchestrator doesn't guess, it reads the plan.
- **First-Class Cicadas Integration** — Worktrees are created by `branch.py`, tracked in `registry.json`, and torn down by `archive.py`/`abort.py` — no new CLI surface for the Builder to learn.
- **Zero New Concepts for Builders** — The Builder declares partition dependencies during Emergence; the runtime outcome (worktree vs. plain branch) follows automatically.

## Project Classification

**Technical Type:** Developer Tool / CLI Enhancement
**Domain:** Developer Infrastructure / Workflow
**Complexity:** Medium — Git worktree API is well-defined; the main complexity is the dependency DAG schema in `approach.md`, the `branch.py` decision logic, and cross-worktree status reporting.
**Project Context:** Brownfield — extends `branch.py`, `kickoff.py`, `check.py`, `archive.py`, `abort.py`, and the `approach.md` template. Adds a `partitions` block to `approach.md`. No changes to the methodology or spec pipeline as experienced by the Builder.

---

## Success Criteria

### User Success

A user achieves success when they can:

1. **Declare parallelism in `approach.md`** — The emergence agent populates a `partitions` block with `depends_on` lists; partitions with empty `depends_on` are flagged as parallelizable.
2. **Start a parallel partition with `branch.py` and get a worktree automatically** — The Builder runs the same `branch.py` command as always; when the partition's `depends_on` is empty, a worktree is created transparently.
3. **See all worktree states in `status.py`** — A single `status.py` invocation shows path, dirty/clean, and HEAD summary for each registered worktree.
4. **Have worktrees cleaned up automatically on completion** — `archive.py`, `prune.py`, and `abort.py` remove worktrees without requiring manual `git worktree remove` calls.

### Technical Success

The system is successful when:

1. **`approach.md` has a machine-readable `partitions` block** — `branch.py` and `kickoff.py` can parse it to determine DAG order and parallelizability.
2. **Registry tracks worktree paths** — `registry.json` records `worktree_path` per feature branch entry (null when no worktree).
3. **`check.py` runs before parallel execution** — `kickoff.py` invokes `check.py` proactively to catch module ownership conflicts before any parallel branch starts.
4. **No orphaned worktrees** — Every worktree created by Cicadas is removed by the same tool that deregisters the branch.

### Measurable Outcomes

- `branch.py` creates a worktree (or plain branch) in < 5 seconds based on the DAG.
- `status.py` lists all worktree states without crashing if a path is missing.
- Zero orphaned `git worktree list` entries after any `archive.py`, `prune.py`, or `abort.py` run.
- `check.py` conflict detection runs automatically at kickoff when parallel partitions are present.

---

## User Journeys

### Journey 1: The Parallel Builder — Multi-Agent Initiative

A senior engineer is mid-Emergence on a three-partition refactor. During the Approach phase, the emergence agent populates the `partitions` block in `approach.md`, declaring that `feat/api` and `feat/ui` have no dependencies (parallel), while `feat/integration` depends on both. At kickoff, `kickoff.py` detects parallel partitions and runs `check.py` proactively. The Builder starts `feat/api` and `feat/ui` via the normal `branch.py` command; each gets a sibling worktree directory automatically. The Builder assigns one agent to each directory. Both agents work simultaneously; `status.py` shows both worktrees' health in one table. When `feat/api` completes, `archive.py` tears down its worktree. The Builder then starts `feat/integration` as a plain branch (sequential, no worktree needed).

**Requirements Revealed:** DAG-based worktree/branch decision in `branch.py`, `kickoff.py` pre-flight conflict check, registry `worktree_path` tracking, `status.py` cross-worktree view, auto-teardown in archive.

---

### Journey 2: The Solo Builder — Sequential Work, No Change

A solo developer is working on a simple two-partition initiative where partition B depends on partition A (a strict sequence). They run `branch.py` to start `feat/partition-a`. Because `depends_on` is non-empty for B (it depends on A), no worktrees are created — just plain branches as before. The Builder works sequentially, never encounters worktree concepts, and the experience is identical to today. This confirms worktrees are invisible to sequential workflows.

**Requirements Revealed:** Backward compatibility — plain branch creation unchanged when `depends_on` is non-empty; no worktree overhead for sequential partitions.

---

### Journey Requirements Summary

| User Type | Key Requirements |
|-----------|-----------------|
| **Parallel Builder** | DAG in `approach.md`, auto worktree on `branch.py`, pre-flight `check.py`, cross-worktree `status.py`, auto-teardown |
| **Solo Builder** | Zero behavior change for sequential (depends_on non-empty) partitions |

---

## Scope

### This Release

**Core Deliverables:**
- `approach.md` template update: add `partitions` YAML/markdown block with `name`, `modules`, `depends_on` per partition
- `branch.py` update: read `partitions` block from `approach.md`, create worktree if `depends_on` is empty, plain branch otherwise; record `worktree_path` in registry
- `kickoff.py` update: detect parallel partitions (any with `depends_on: []`) and run `check.py` proactively before execution begins
- `check.py` update: support a "pre-execution" validation mode invocable by `kickoff.py`; detect stale/missing worktrees and suggest `git worktree repair`
- Registry extension: `worktree_path` field (optional, null/absent by default) on feature branch entries
- `status.py` enhancement: show worktree path, dirty/clean, HEAD commit for branches with a `worktree_path`; flag `[MISSING]` when path is recorded but directory is gone
- Teardown: `archive.py`, `prune.py`, `abort.py` call `git worktree remove` and clear `worktree_path` from registry
- Context injection: when `branch.py` creates a worktree, assemble and write a context bundle (`context.md`) into the worktree root containing canon summary + scoped module snapshots + `tasks.md` + `approach.md`

**Worktree naming convention:** `{sibling-of-repo-root}/{repo-name}-{branch-slug}` (e.g. `../cicadas-feat-api`)

**Quality Gates:**
- All existing unit tests pass unmodified.
- New tests cover DAG parsing, worktree creation decision logic, registry mutation, teardown, and context bundle assembly.
- `git worktree list` reports zero orphans after any Cicadas teardown operation.

### Vision (Future)

- Agent launcher: from the initiative branch, spawn one agent per parallel worktree with pre-loaded context (tasks.md + approach.md + scoped module snapshots)

---

## Functional Requirements

### 1. Dependency DAG in `approach.md`

**FR-1.1:** The `approach.md` template MUST include a `partitions` block declaring each partition's `name`, `modules` list, and `depends_on` list.
- `depends_on: []` (empty) signals the partition can begin immediately (parallel).
- `depends_on: [partition-name]` signals a sequential dependency.
- The emergence agent is responsible for populating this block during spec authoring.

**FR-1.2:** `branch.py` MUST parse the `partitions` block to determine the dependency status of the target partition before creating its branch.

---

### 2. Worktree Lifecycle (via `branch.py`)

**FR-2.1:** When `branch.py` starts a partition whose `depends_on` is empty, it MUST create a git worktree instead of a plain branch checkout.
- Worktree path: `{parent-dir-of-repo}/{repo-name}-{branch-slug}` where `branch-slug` replaces `/` with `-`.
- On creation, records `worktree_path` in `registry.json` under the feature branch entry.
- Prints the created worktree path on success.

**FR-2.2:** When `branch.py` starts a partition whose `depends_on` is non-empty, it MUST create a plain git branch as today — no worktree, no registry `worktree_path`.

**FR-2.3:** `branch.py` MUST be idempotent: if a worktree already exists for the branch, it reports the path and exits cleanly without duplicating it.

**FR-2.4:** If `git worktree add` fails (e.g. path conflict, branch not found), `branch.py` MUST exit non-zero with a clear message and NOT write to `registry.json`.

---

### 3. Pre-Execution Conflict Check

**FR-3.1:** `kickoff.py` MUST invoke `check.py` when the initiative has any partition with `depends_on: []` (i.e., parallel partitions exist), before returning control to the Builder.
- This is a proactive guard, not on-demand: conflicts are caught before any parallel branch starts.
- If `check.py` reports module ownership conflicts, `kickoff.py` MUST surface the warnings and prompt the Builder to resolve before proceeding.

---

### 4. Registry Integration

**FR-4.1:** `registry.json` feature branch entries MUST support an optional `worktree_path` field (null or absent = no worktree).
- Set by `branch.py`; cleared by `archive.py`, `prune.py`, `abort.py`.
- Never manually editable.

---

### 5. Status Reporting

**FR-5.1:** `status.py` MUST display, for each registered feature branch with a `worktree_path`, the worktree's path, dirty/clean status, and HEAD commit summary.
- Implementation: `git -C {worktree_path} status --porcelain` and `git -C {worktree_path} log -1 --oneline`.
- Graceful degradation: if path is recorded but directory is missing, display `[MISSING]` rather than crashing.

---

### 6. Worktree Teardown

**FR-6.1:** `archive.py`, `prune.py`, and `abort.py` MUST remove the worktree (via `git worktree remove`) when deregistering a branch that has a `worktree_path`.
- If the worktree has uncommitted changes, the script MUST warn and require an explicit `--force` flag to proceed.
- After removal, clears `worktree_path` from the registry entry.
- If the worktree directory is already missing (manually deleted), the script logs a warning and continues cleanly.

---

### 7. Worktree Health & Repair

**FR-7.1:** `check.py` MUST detect worktrees recorded in `registry.json` whose `worktree_path` no longer exists on disk.
- Report these as `[MISSING]` in `check.py` output alongside a suggested repair command (`git worktree repair` or re-running `branch.py`).

**FR-7.2:** `status.py` MUST display `[MISSING]` (not an error/crash) for any branch whose recorded `worktree_path` does not exist.

---

### 8. Context Injection at Branch Start

**FR-8.1:** When `branch.py` creates a worktree for a parallel partition, it MUST assemble a `context.md` file and write it to the worktree root.
- Contents: canon summary (`canon/summary.md` if present), full module snapshots for each module declared in the partition's `modules` list, the initiative's `approach.md`, and the partition's `tasks.md`.
- If `canon/summary.md` does not exist (e.g. greenfield project), that section is omitted without error.

**FR-8.2:** `context.md` is ephemeral — it is NOT committed to the branch. It is written fresh each time the worktree is created.

---

## Non-Functional Requirements

- **Performance:** Worktree creation via `branch.py` completes in < 5 seconds; `status.py` with 3 worktrees completes in < 3 seconds.
- **Reliability:** Any `git worktree` failure exits non-zero with a clear error; no partial state is written to `registry.json` on failure.
- **Security:** No external network calls; all operations are local git commands and filesystem reads.
- **Maintainability:** Worktree creation/removal logic is isolated in a shared utility function in `utils.py` (`create_worktree`, `remove_worktree`) imported by `branch.py`, `archive.py`, `prune.py`, and `abort.py`. DAG parsing is a separate utility function.

---

## Open Questions

- **Q1 (Owner: Builder, Urgency: Before Tech Design):** Should the DAG be encoded as a fenced YAML block in `approach.md` (machine-parseable) or as a structured markdown table (human-readable, but harder to parse)? Leaning toward fenced YAML for reliability.
- **Q2 (Owner: Builder, Urgency: Before Tech Design):** If a partition's `depends_on` references a name that doesn't match any other partition, should `branch.py` error hard or warn and treat it as sequential?
- **Q3 (Owner: Builder, Urgency: MVP):** On teardown with uncommitted changes: warn + require `--force`, or hard-stop by default? Roadmap says "explicit" — confirming this means `--force` required.
- **Q4 (Owner: Builder, Urgency: Before Tech Design):** The approach.md template change affects the emergence agent instructions. Should the `approach.md` subagent prompt (`emergence/approach.md`) be updated in this initiative, or as a follow-on?

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Orphaned worktrees if a teardown script crashes mid-execution | Medium | Medium | Wrap teardown in try/finally; `check.py` detects orphans via `git worktree list` comparison |
| DAG parsing fails on malformed `approach.md` | Medium | Medium | Validate `partitions` block schema at parse time; clear error message pointing to the block |
| Path conflict: two partitions resolve to same worktree directory | Low | High | `branch.py` checks path existence before `git worktree add`; exits with actionable error |
| Backward compatibility break (existing `approach.md` without `partitions` block) | Medium | Low | `partitions` block is optional; absence = all partitions treated as sequential (plain branches) |
| Git version incompatibility (worktree API < 2.5) | Low | Low | Add `git --version` check in worktree utility; print install guidance if < 2.5 |
