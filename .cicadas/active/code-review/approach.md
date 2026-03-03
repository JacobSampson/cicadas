
# Approach: Code Review

## Strategy

Single partition, sequential. There is one logical unit of work — the Code Review subagent prompt and its registration in SKILL.md. No parallelism needed; SKILL.md changes must reference the finalized prompt to stay accurate.

## Partitions (Feature Branches)

### Partition 1: Code Review Subagent → `feat/code-review-subagent`

**Modules**: `src/cicadas/emergence/`, `src/cicadas/SKILL.md`

**Scope**: Write `emergence/code-review.md` (the subagent prompt with full reasoning algorithm and output format), then make additive changes to `SKILL.md` (new operation, autonomy row, Builder commands, quick reference entry).

**Dependencies**: None

#### Implementation Steps

1. Write `src/cicadas/emergence/code-review.md` following the structure and conventions of existing emergence subagents (Role, Process, Algorithm, Output Format, Key Considerations, copyright footer)
2. Update `src/cicadas/SKILL.md`:
   - Add `### Code Review` under `## Agent Operations (LLM)`
   - Add row to Agent Autonomy Boundaries table
   - Add Builder commands to Builder Commands section
   - Add row to Agent Operations quick reference table
   - Update directory listing to include `code-review.md`
3. Run lint/format check on any modified files

## Sequencing

```mermaid
graph LR
    A[Write code-review.md] --> B[Update SKILL.md]
    B --> C[Lint & verify]
```

## Migrations & Compat

No migration required. SKILL.md changes are purely additive. Projects not invoking Code Review are unaffected. No registry, lifecycle, or schema changes.

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| SKILL.md additions drift from the actual prompt behavior | Write `code-review.md` first; use it as the source of truth when writing SKILL.md summaries |
| Subagent prompt produces inconsistent output structure | Enforce literal section headings and verdict strings in the prompt; include a worked example of the report format |
| Correctness scan produces too many false-positive advisories | Keep Advisory threshold explicit (must cite a specific line/pattern); vague findings are not permitted |

## Alternatives Considered

- **Two partitions (prompt + SKILL.md separately)**: Unnecessary overhead for two files that take less than a day to write and have a clear linear dependency.
- **Helper script partition**: Evaluated and rejected — pure LLM is sufficient for the actual branch types in use (feature, fix, tweak); complexity not warranted.

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
