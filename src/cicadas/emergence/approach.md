
# Emergence: Approach

**Goal**: Define the implementation strategy, including logical partitions that become feature branches.

**Role**: You are a Lead Developer. Your job is to figure out *how* to build the design, step-by-step, and how to *partition* the work for parallel execution.

## Process

1.  **Ingest**: Read `prd.md`, `ux.md`, and `tech-design.md` from `.cicadas/drafts/{initiative}/`.
2.  **Plan**:
    -   **Define Partitions**: Identify logical partitions of work. Each partition becomes a **Feature Branch**. For each partition, declare:
        - A name (e.g., `feat/data-and-auth`, `feat/frontend-shell`)
        - The modules it touches (e.g., `db`, `auth`, `frontend/core`)
        - Its scope and boundaries
    -   **Sequence**: Determine ordering and dependencies between partitions. Which must go first? Which can run in parallel?
    -   **Author the Partitions DAG**: In the `## Sequencing` section, add a `yaml partitions` fenced block (see template). For every partition:
        - Set `depends_on: []` if it can run in parallel (no prerequisites). This partition **will get its own git worktree** when `branch.py` is run.
        - Set `depends_on: [feat/other-partition]` if it must wait for another partition to merge first. This partition will be a plain branch.
        - If no partition is parallel (all have non-empty `depends_on`), the block is still valid — all branches will be plain. Omit the block entirely only if the concept of parallelism is irrelevant to the initiative.
    -   **Identify Risks**: Module overlaps between partitions, migration concerns, shared component boundaries.
    -   **Plan for backward compatibility and migration** (brownfield).
3.  **Draft**: Create `.cicadas/drafts/{initiative}/approach.md`.
4.  **Refine**: Builder review.
5.  **Lifecycle (PR boundaries)**: Ask the Builder: *"Will you be doing PRs for this initiative?"* If yes, ask at which boundaries (defaults: specs **no**, initiatives **yes**, features **yes**, tasks **no**). Create `lifecycle.json` in `.cicadas/drafts/{initiative}/` with those choices and the standard steps. Use `python {cicadas-dir}/scripts/create_lifecycle.py {initiative}` with flags `--pr-specs`, `--no-pr-initiatives`, `--no-pr-features`, `--pr-tasks` to override defaults, or run with no flags for defaults.

## Output Artifacts

- **approach.md**: Use the template at `{cicadas-dir}/templates/approach.md`.
- **lifecycle.json** (after step 5): In `.cicadas/drafts/{initiative}/lifecycle.json`; created by `create_lifecycle.py` with the Builder's PR boundary choices. Promoted to active at kickoff.

**The approach document is the single most important artifact in Emergence.** Every downstream decision — branch names, module scopes, conflict detection, registry entries — flows from the partitions defined here.

## Key Considerations

-   **Partitions are mandatory**: The approach MUST define named partitions with declared module scopes. Without partitions, feature branches cannot be created.
-   **Author the Partitions DAG**: Every approach.md MUST include the `yaml partitions` fenced block in `## Sequencing`. This block is machine-read by `branch.py` to decide whether to create a git worktree (parallel) or a plain branch (sequential). Use the exact format from the template.
-   **`depends_on` semantics**:
    - `depends_on: []` → parallel partition — gets its own isolated git worktree directory so agents can work on it simultaneously.
    - `depends_on: [feat/x]` → sequential — plain branch created from the initiative branch, waits for `feat/x` to merge first.
-   **Module boundary clarity**: If two partitions touch the same module, tighten the boundaries (e.g., `frontend/core/` vs. `frontend/social/`).
-   **Testability**: How will we test this?
-   **Incremental Delivery**: Can we ship this in pieces?
-   **Risks**: What could go wrong?

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
