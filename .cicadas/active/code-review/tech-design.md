
---
next_section: 'COMPLETE'
---

# Tech Design: Code Review

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

**Summary:** Code Review is a new **agent operation** (LLM reasoning step, no new scripts) that performs a structured evaluation of a code diff against the active specifications for that branch. It operates orthogonally to Reflect: while Reflect syncs specs *to* code (code wins), Code Review evaluates code *against* specs (spec is authoritative). The operation produces an ephemeral structured report with tiered findings and a merge verdict, always advisory.

The implementation has two parts: (1) a new emergence subagent prompt (`emergence/code-review.md`) that defines the reasoning algorithm and output format, and (2) additions to `SKILL.md` registering Code Review as a named operation with defined trigger, autonomy boundary, and Builder commands.

### Cross-Cutting Concerns

1. **Consistency over creativity** — The subagent prompt must enforce identical report structure across every invocation. Sections, finding labels, and verdict strings must be literal constants, not paraphrased. The agent must follow the algorithm deterministically.
2. **Diff scope precision** — The correct diff command depends on branch type. Wrong diff = wrong review. The prompt must specify exact `git diff` commands per scope.
3. **Spec file resolution** — The agent must read the correct spec files for the branch type. Full paths must be resolvable from `.cicadas/active/{initiative}/`. The prompt must handle the case where a spec file doesn't exist (lightweight paths have no tech-design.md).
4. **Advisory-only enforcement** — The verdict must never imply the agent can block a merge. The language in the prompt and SKILL.md must reinforce that Builder retains merge authority.

### Brownfield Notes

This initiative touches:
- `src/cicadas/emergence/` — new file added, existing files unmodified
- `src/cicadas/SKILL.md` — additive changes only (new operation section, new rows in existing tables, new Builder commands)
- Nothing else. No scripts, no registry schema, no lifecycle schema, no templates.

The existing Reflect operation, Builder commands, and lifecycle flow are unchanged.

---

## Tech Stack & Dependencies

| Category | Selection | Rationale |
|----------|-----------|-----------|
| **Implementation** | Markdown prompt file | All other emergence subagents are markdown; no code required |
| **Runtime** | LLM agent (Claude) | Reasoning step, not a script |
| **Git** | `git diff`, `git log`, `git merge-base` | Standard; already used throughout Cicadas |
| **No new dependencies** | — | Zero new packages, CLIs, or schema fields |

**New dependencies introduced:** None.

---

## Project / Module Structure

```
src/cicadas/
├── emergence/
│   ├── code-review.md          # [NEW] Code Review subagent prompt
│   └── (all existing files unchanged)
└── SKILL.md                    # [MODIFIED] New operation, commands, autonomy row
```

**Key structural decisions:**
- Code Review lives in `emergence/` alongside other subagent prompts — consistent with existing conventions.
- SKILL.md additions are purely additive — new `### Code Review` section under Agent Operations, new row in autonomy table, new Builder commands.
- No new template file needed — output format is fully defined within the subagent prompt itself (ephemeral, not persisted).

---

## Architecture Decisions (ADRs)

### ADR-1: Agent Operation, Not a Script

**Decision:** Code Review is implemented as an LLM reasoning operation (a markdown prompt) rather than a CLI script.

**Rationale:** The review requires reading and reasoning over prose specifications, git diffs, and code simultaneously — tasks that require LLM capabilities. A deterministic script cannot do this. All other comparable operations in Cicadas (Reflect, Synthesis, Semantic Intent Check) are agent operations, not scripts.

**Affects:** `emergence/code-review.md`, `SKILL.md`

---

### ADR-2: Orthogonal to Reflect — Not a Superset

**Decision:** Code Review is a separate, distinct operation from Reflect. It does not subsume or replace Reflect.

**Rationale:** They have opposite directions of authority: Reflect treats code as authoritative and updates specs to match. Code Review treats specs as authoritative and evaluates code against them. Merging them would create conflicting authority, unclear semantics, and confuse the Builder about which direction changes flow. They compose: run Reflect first (sync specs), then Code Review (evaluate code against synced specs). A Reflect-completeness check is included *within* Code Review as one finding category, making the composition explicit.

**Affects:** `SKILL.md` (both operations documented side by side)

---

### ADR-3: Scope-Parametric Reasoning Algorithm

**Decision:** The subagent prompt defines three distinct review modes — Full (task or feature branch), Lightweight (fix/tweak) — with different spec files, diff commands, and report sections for each. The agent detects which mode to use from the current branch name prefix.

**Rationale:** A single one-size-fits-all review algorithm would either over-specify lightweight paths (no approach.md to check) or under-specify full initiative paths (no module scope check). Separate modes with shared output format gives precision without redundancy.

**Affects:** `emergence/code-review.md`

---

### ADR-4: Ephemeral Output — No Artifact Persisted

**Decision:** Review output is presented in the agent response only. Nothing is written to `.cicadas/`.

**Rationale:** Persisting reviews adds state that must be managed (cleanup, stale detection, naming collisions). The Builder reads the review in context and acts on it immediately. PR descriptions (written during Reflect/PR-open) already capture the gist of findings. Persisted reviews would be rarely re-read and add friction without value at this stage (v2 may revisit via lifecycle.json).

**Affects:** `emergence/code-review.md`, `SKILL.md` (autonomy table — execution is autonomous, no artifact to approve)

---

### ADR-5: Security Findings are Advisory by Default

**Decision:** Security scan findings are Advisory unless the finding is a clear, critical vulnerability committed to code (e.g., hardcoded API key, SQL string concatenation with user input). In that case it is Blocking.

**Rationale:** Security scanning by an LLM without static analysis tools will produce false positives. Advisory-by-default ensures findings are surfaced without false alarms blocking merges. The narrow Blocking threshold (only unambiguous, critical issues) prevents noise from becoming friction. The Builder, as a security-aware developer, uses advisory findings as prompts for their own judgment.

**Affects:** `emergence/code-review.md` (security scan section of algorithm)

---

### ADR-6: Accumulated Diff at Feature Scope (Pure LLM)

**Decision:** At feature-branch scope, the review uses a single accumulated diff (`git diff $(git merge-base HEAD initiative/{name}) HEAD`) rather than per-task diff reconstruction.

**Rationale:** Per-task diff reconstruction via `git log` was evaluated and rejected. Reconstructing individual task-branch commit ranges requires the agent to interpret git history shape (merge commits, rebased history, squash merges) — fragile and error-prone without a helper script. Since task branches are not a required part of the workflow in practice, the accumulated diff is sufficient: it captures all changes on the feature branch relative to the initiative branch and can be cross-referenced against the full task list. Pure LLM data gathering keeps the implementation consistent with how Reflect works and avoids a new script dependency.

**Affects:** `emergence/code-review.md` (feature-scope diff command)

---

## Data Models

### No New Models

No changes to `registry.json`, `index.json`, `lifecycle.json`, or any existing schema. Code Review produces no persistent artifacts.

---

## API & Interface Design

### Builder Commands (Natural Language)

```
"Code review"         → Review current branch (auto-detect scope)
"Review task"         → Explicit task-branch review
"Review feature"      → Explicit feature-branch review
"Review fix"          → Explicit fix-branch review (lightweight mode)
"Review tweak"        → Explicit tweak-branch review (lightweight mode)
```

### Review Report Format (Output Contract)

The subagent MUST produce output in this exact structure every time. Section headings and verdict strings are literal constants:

```markdown
## Code Review: {branch-name}

**Scope:** Task Branch | Feature Branch | Fix Branch | Tweak Branch
**Spec files:** {comma-separated list of spec files read}
**Diff:** {N files changed, +X −Y lines}

---

### ✅ Verified

- {Item explicitly checked and confirmed correct}
- {Item explicitly checked and confirmed correct}

### 🔶 Advisory

- **[Category]** {Finding — specific, actionable, with file/line reference where possible}

### 🔴 Blocking

- **[Category]** {Finding — specific, actionable, with file/line reference where possible}

### 🔒 Security

- **[Advisory|Blocking]** {Finding — file:line, pattern, recommended fix}

### 🐛 Correctness

- **[Advisory|Blocking]** {Finding — file:line, pattern, recommended fix}

---

**Verdict: MERGE-READY** ← if zero Blocking findings
**Verdict: NEEDS-WORK** ← if one or more Blocking findings

*Blocking findings: {N}. Advisory findings: {N}. This verdict is advisory — Builder retains merge authority.*
```

### Finding Categories (used in `[Category]` labels)

| Label | Meaning |
|-------|---------|
| `Task Gap` | A task in tasks.md has no corresponding code change |
| `Acceptance Criteria` | A stated acceptance criterion is not satisfied by the code |
| `Arch Violation` | Code deviates from a pattern, structure, or sequence in tech-design.md |
| `Module Scope` | Code touches a module not declared in approach.md partition scope |
| `Reflect Gap` | A code change not captured in active specs (incomplete Reflect) |
| `Test Coverage` | Missing test for a non-trivial behavior change |
| `Fix Incomplete` | For buglet: the root cause described is not addressed by the change |
| `Security` | Security scan finding (OWASP patterns, exposed secrets, unvalidated input) |
| `Correctness` | Logic bug visible in the diff: off-by-one, swallowed exception, deadlock risk, null dereference, resource leak, wrong comparison, etc. |
| `Quality` | Code style issue that doesn't rise to Correctness: missing test for non-trivial logic, unclear naming, etc. |

### Review Algorithm (Full Mode — Task or Feature Branch)

```
1. DETECT SCOPE
   - Branch name starts with "task/" → Task scope
   - Branch name starts with "feat/" → Feature scope

2. READ SPECS
   - .cicadas/active/{initiative}/tasks.md
   - .cicadas/active/{initiative}/tech-design.md
   - .cicadas/active/{initiative}/approach.md

3. GATHER DIFF
   Task scope:    git diff $(git merge-base HEAD {parent-feat-branch}) HEAD
   Feature scope: git log --oneline {initiative-branch}..HEAD  → identify task commits
                  for each task commit range: git diff {range}

4. REASON — for each check, produce a finding or a pass:
   a. TASK COMPLETENESS
      For each task in tasks.md partition:
      - Is it marked done? If yes, is there a corresponding diff chunk?
      - If no diff found for a "done" task → Blocking [Task Gap]
   b. ACCEPTANCE CRITERIA
      For each task with stated acceptance criteria:
      - Does the diff satisfy the criteria? If no → Blocking [Acceptance Criteria]
   c. ARCHITECTURAL CONFORMANCE
      - Does the diff follow patterns, naming, and structure in tech-design.md?
      - Any deviation → Advisory or Blocking [Arch Violation] based on severity
   d. MODULE SCOPE (Feature scope only)
      - Does the diff touch only modules declared in approach.md for this partition?
      - Any out-of-scope module touched → Advisory [Module Scope]
   e. REFLECT COMPLETENESS
      - Are there code changes (new files, renamed functions, new modules, schema changes)
        NOT reflected in active specs?
      - If yes → Blocking [Reflect Gap] (run Reflect first, then re-review)
   f. SECURITY SCAN
      - Scan diff for: hardcoded secrets/credentials, SQL string concatenation with
        user input, unvalidated user input at system boundaries, unguarded collection
        access on external data, obvious OWASP Top 10 patterns
      - Clear critical issue → Blocking [Security]
      - Pattern of concern → Advisory [Security]
   g. CORRECTNESS SCAN
      Scan the diff for logic bugs detectable without running the code:
      - Off-by-one errors (< vs <=, range bounds, slice indices, fence-post)
      - Loop or collection mutation while iterating
      - Swallowed exceptions (bare `except: pass`, broad catch with no log/rethrow)
      - Concurrency risks (shared mutable state without locks, deadlock-prone lock ordering)
      - Null/None dereference on values that could be absent (unchecked return values, optional fields)
      - Resource leaks (files, connections, sockets opened without `with`/`finally`)
      - Incorrect boolean logic (and/or precedence errors, double negation, wrong short-circuit)
      - Wrong comparison operator (`is` vs `==`, identity vs equality on non-singletons)
      - Mutable default arguments in function signatures
      Advisory by default (agent cannot prove a bug without execution). Blocking if the
      pattern is unambiguous (e.g., exception handler with bare `pass`, clear file handle leak).
   h. CODE QUALITY
      - Non-trivial logic changes without a test → Advisory [Test Coverage]
      - Unhandled edge cases visible in diff that don't rise to Correctness → Advisory [Quality]

5. COMPILE REPORT in prescribed format
6. EMIT VERDICT: NEEDS-WORK if any Blocking findings, else MERGE-READY
```

### Review Algorithm (Lightweight Mode — Fix or Tweak Branch)

```
1. DETECT SCOPE
   - Branch starts with "fix/" → read buglet.md
   - Branch starts with "tweak/" → read tweaklet.md

2. READ SPECS
   - .cicadas/active/{initiative}/buglet.md  OR  tweaklet.md
   (No tech-design.md or approach.md — skip those checks)

3. GATHER DIFF
   git diff $(git merge-base HEAD master) HEAD

4. REASON:
   a. FIX/TWEAK COMPLETENESS
      Fix:   Does the diff address the root cause described in buglet.md? If no → Blocking [Fix Incomplete]
      Tweak: Does the diff implement the change described in tweaklet.md? If no → Blocking [Task Gap]
   b. SCOPE CONTAINMENT
      - Does the diff stay within the scope described in the spec?
      - Any out-of-scope changes → Advisory [Module Scope]
   c. REGRESSION RISK
      - Does the fix introduce any new surface area beyond the described fix? → Advisory [Quality]
   d. SECURITY SCAN (same as Full mode)
   e. CORRECTNESS SCAN (same as Full mode)
   f. CODE QUALITY (same as Full mode)

5. COMPILE REPORT (same format, omit sections not applicable: Arch Violation, Module Scope if not relevant)
6. EMIT VERDICT
```

---

## Implementation Patterns & Conventions

### Subagent Prompt Conventions

The `emergence/code-review.md` prompt MUST follow the same structural conventions as all other emergence subagents:

| Element | Convention |
|---------|-----------|
| File name | `kebab-case.md` |
| Header | `# Subagent: Code Review` |
| Sections | Role, Process, Algorithm (new section for this subagent), Output Format, Key Considerations |
| Process Preview | Show the Builder where Code Review fits in the full workflow |
| Copyright footer | Required |

The prompt is **imperative** — it tells the agent what to do step by step. It does not describe what code review *is*; it instructs the agent *how to perform* code review. This prevents the agent from improvising its own method.

### SKILL.md Change Conventions

- New operation is added under `## Agent Operations (LLM)` as `### Code Review`
- New row added to Agent Autonomy Boundaries table
- New Builder commands added to Builder Commands section
- New row added to Agent Operations quick reference table
- All additions are purely additive — no existing content is removed or modified

---

## Security & Performance

### Security

| Concern | Mitigation |
|---------|-----------|
| LLM hallucinating findings | Structured algorithm — each finding must reference a specific diff line or spec citation; vague findings are not permitted by the prompt |
| Security scan false positives | Advisory-by-default; Blocking threshold is narrow and explicitly defined |
| Agent reading wrong spec files | Prompt specifies exact file paths with `.cicadas/active/{initiative}/` prefix; missing files are noted explicitly in the report |

### Performance

| Concern | Target | Approach |
|---------|--------|---------|
| Review latency | Single agent turn < 2 min | Scoped diff (not full codebase); read only required spec files |
| Context window | Fit within model context | Large diffs (>500 LOC) get a warning in the report noting that review may be incomplete; Builder should break tasks smaller |

### Observability

No new logging or metrics. The review report itself is the observable artifact.

---

## Implementation Sequence

1. **`emergence/code-review.md`** — Write the subagent prompt with the full algorithm, output format, and lightweight mode. This is the primary deliverable.
2. **`SKILL.md` additions** — Add Code Review to Agent Operations, autonomy table, Builder commands, and quick reference. Depends on (1) being finalized so descriptions are accurate.

**Parallel work opportunities:** Both files can be drafted in the same task since neither depends on the other at implementation time (they're both docs). However, finalize the algorithm in `code-review.md` before updating SKILL.md summaries to ensure consistency.

**Known implementation risks:**
- The feature-scope per-task diff algorithm (step 3 in Full mode) requires the agent to reconstruct task branch commit ranges from `git log`. This is feasible but requires careful prompt wording — if the agent reads the accumulated feature diff instead, it misses per-task granularity. The prompt must include exact `git` command sequences.

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
