
---
next_section: 'COMPLETE'
---

# PRD: Code Review

## Progress

- [x] Executive Summary
- [x] Project Classification
- [x] Success Criteria
- [x] User Journeys
- [x] Scope & Phasing
- [x] Functional Requirements
- [x] Non-Functional Requirements
- [x] Open Questions
- [x] Risk Mitigation

## Executive Summary

A **Code Review** operation for Cicadas that performs a rigorous, agent-driven evaluation of implemented code against active specifications and quality standards. It runs optionally at the end of a task branch (pre-PR) or feature branch (pre-merge), and also on lightweight fix/tweak branches, producing a structured, actionable review report with advisory findings and a merge verdict. It fills the gap between Reflect (spec sync) and the Builder's human PR review — catching spec drift, missing tasks, architectural violations, security issues, and quality gaps *before* the Builder ever looks at the code.

### What Makes This Special

- **Spec-Anchored** — Unlike generic linters, the review is grounded in *this* initiative's tasks.md, tech-design.md, and approach.md (or buglet.md / tweaklet.md for lightweight paths)
- **Tiered Findings** — Blocking vs. advisory findings give clear merge/no-merge signal; verdict is always advisory (Builder retains merge authority)
- **Universal** — Applies to full initiatives (task + feature branches) and lightweight paths (fix/, tweak/) alike

## Project Classification

**Technical Type:** Developer Tool / Agent Prompt
**Domain:** Infrastructure / Methodology
**Complexity:** Medium — New emergence subagent + SKILL.md operation; no new CLI scripts or registry schema changes
**Project Context:** Brownfield — adds to existing `emergence/` directory and SKILL.md operation table

---

## Success Criteria

### User Success

A user achieves success when they can:

1. **Catch gaps before PR** — Running code review before opening a PR surfaces spec gaps, missed tasks, or quality issues in >50% of runs where a gap actually exists
2. **Get clear signal** — The review report gives an unambiguous `MERGE-READY` / `NEEDS-WORK` verdict with categorized findings, always advisory
3. **Fast feedback** — Review completes in one agent turn without back-and-forth clarification

### Technical Success

The system is successful when:

1. The subagent prompt produces consistently structured output (no hallucinated findings, no missed spec items)
2. Integration is backwards-compatible — projects not using code review are unaffected

### Measurable Outcomes

- Review reports have < 5% false positives (findings that turn out to be non-issues after Builder review)
- Builders opt-in on >70% of feature branches after first use

---

## User Journeys

### Journey 1: The Builder — "Trust but Verify Before PR" (Task Branch)

After implementing two tasks on `task/feat/api-refactor/add-auth-middleware`, the Builder has already run Reflect. Before opening a PR, they run Code Review. The agent reads the full per-task diff, the active tasks.md, tech-design.md, and approach.md, then produces a structured report. It catches that one acceptance criterion in tasks.md (error handling for 401 responses) has no corresponding test, that the middleware order deviates from the sequence diagram in tech-design.md, and that a new helper function lacks input validation (security advisory). Both spec findings are fixable before PR — saving a round-trip review cycle.

**Requirements Revealed:** per-task diff analysis, spec-anchored evaluation, security checking, finding categorization, merge verdict, actionable output.

---

### Journey 2: The Builder — "Feature Branch Completeness Check" (Feature Branch)

All task branches for `feat/api-layer` are merged. Before merging into the initiative branch, the Builder asks for a feature-level code review. The agent reviews the full detail of all task-branch diffs (not just the accumulated feature diff), cross-checks against the partition's declared module scope in approach.md, and verifies all partition tasks are checked off. It finds two tasks marked "in progress" with no corresponding code, and a new utility module not captured in tech-design.md (a Reflect gap). It also flags an unguarded dict access as an advisory security note.

**Requirements Revealed:** per-task diff detail at feature scope, module scope verification, task completeness, Reflect-completeness check, security scan.

---

### Journey 3: The Builder — "Quick Fix Review" (Lightweight Path)

A bug fix on `fix/null-pointer-login` is nearly done. The Builder runs Code Review against the buglet.md spec. The agent checks that the fix addresses the root cause described in buglet.md, that the reproduction steps are now resolved, that no new surface area was introduced, and scans for related security issues. Output is a simpler report (no approach.md or tech-design.md to cross-reference), focused on: fix correctness, test coverage, and security.

**Requirements Revealed:** lightweight spec support (buglet.md / tweaklet.md), simplified review mode, fix correctness evaluation.

---

### Journey Requirements Summary

| User Type | Key Requirements |
|-----------|-----------------|
| **Builder (task-level)** | per-task diff, spec cross-reference, security check, tiered findings, merge verdict |
| **Builder (feature-level)** | full per-task diff detail, module scope check, task completeness, Reflect-completeness check, security scan |
| **Builder (fix/tweak)** | buglet/tweaklet spec support, simplified review mode, fix correctness, security |

---

## Scope

### MVP — v1

**Core Deliverables:**
- New emergence subagent: `src/cicadas/emergence/code-review.md`
- New SKILL.md operation: **Code Review** (autonomous execution, findings presented to Builder, always advisory)
- New Builder commands: `"Code review"`, `"Review task"`, `"Review feature"`, `"Review fix"`, `"Review tweak"`
- Runs at: (a) task branch pre-PR, (b) feature branch pre-merge, (c) fix/tweak branch pre-merge
- Output: ephemeral structured markdown report in agent response (not persisted to disk)
- Full path: task.md + tech-design.md + approach.md cross-reference; per-task diff detail at all scopes
- Lightweight path: buglet.md / tweaklet.md cross-reference; simplified report structure
- Security: advisory scan for common issues (input validation gaps, unguarded access, exposed secrets, basic OWASP patterns)
- Backwards-compatible: zero impact on projects not using code review

**Quality Gates:**
- Subagent prompt produces identical output structure across all invocations
- No changes to registry.json, lifecycle.json schema, or existing scripts

### Growth (v2) — Lifecycle Integration

- Optional step in `lifecycle.json`: `"code_review": true` at task or feature boundary
- Agent automatically runs code review as part of the inner loop when enabled

### Vision (v3)

- Configurable review depth (quick / standard / deep)
- Custom review checklists in tasks.md frontmatter

---

## Functional Requirements

### 1. Code Review Operation

**FR-1.1:** The agent MUST support code review at three scopes: task branch (diff vs. parent feature branch), feature branch (full per-task diff detail across all merged task branches), and lightweight branches (fix/, tweak/).

**FR-1.2:** At task-branch scope, the review MUST analyze the diff of the current branch against its parent and cross-reference against tasks.md, tech-design.md, and approach.md.

**FR-1.3:** At feature-branch scope, the review MUST analyze the per-task diffs in full detail (not just the accumulated feature diff) and cross-reference against the full partition's task list, module scope in approach.md, and tech-design.md.

**FR-1.4:** At lightweight scope (fix/tweak), the review MUST cross-reference against buglet.md or tweaklet.md. No tech-design.md or approach.md cross-reference is required.

### 2. Finding Tiers & Verdict

**FR-2.1:** All findings MUST be categorized as **Blocking** (must fix before merge) or **Advisory** (recommended improvement).

**FR-2.2:** The report MUST include a **Pass** section listing items explicitly verified as correct.

**FR-2.3:** The report MUST conclude with a verdict: `MERGE-READY` or `NEEDS-WORK`.

**FR-2.4:** The verdict is ALWAYS advisory — the Builder retains merge authority regardless of verdict.

### 3. Security Scan

**FR-3.1:** The review MUST include a security scan of the diff, checking for: unguarded input, exposed secrets or credentials, unvalidated user input at system boundaries, unguarded collection access, and basic OWASP Top 10 patterns relevant to the changed code.

**FR-3.2:** Security findings MUST be Advisory unless they represent a clear, critical vulnerability (e.g., exposed secret committed to code), in which case they are Blocking.

**FR-3.3:** The review MUST include a correctness scan of the diff for logic bugs detectable without execution: off-by-one errors, loop/collection mutation while iterating, swallowed exceptions, concurrency risks (deadlocks, unsynchronized shared state), null/None dereference, resource leaks, boolean logic errors, wrong comparison operators, and mutable default arguments.

**FR-3.4:** Correctness findings MUST be Advisory by default. Findings where the bug is unambiguous from reading the code (e.g., bare `except: pass`, clear resource leak with no `finally`) MUST be Blocking.

### 4. Reflect Completeness Check

**FR-4.1:** As part of code review, the agent MUST check whether the prior Reflect operation captured all significant code changes in the active specs. Incomplete Reflect is a Blocking finding.

### 5. Invocation

**FR-5.1:** The operation MUST be invocable via Builder natural-language commands: `"Code review"`, `"Review task"`, `"Review feature"`, `"Review fix"`, `"Review tweak"`.

**FR-5.2:** The output is ephemeral — presented in the agent response only, not persisted to `.cicadas/`.

### 6. Backwards Compatibility

**FR-6.1:** Projects that do not invoke code review MUST be unaffected. No schema changes, no new required fields.

---

## Non-Functional Requirements

- **Performance:** Review completes in a single agent turn (< 2 min) for typical diffs (< 500 lines changed)
- **Consistency:** Structured output format is identical across all runs — same sections, same verdict labels — enforced by the subagent prompt
- **Reliability:** Finding false positive rate < 5% (verified by Builder during PR review)
- **Maintainability:** Subagent prompt must be self-contained and follow existing emergence subagent conventions exactly
- **Backwards Compatibility:** Zero impact on projects not invoking code review; no registry or lifecycle schema changes

---

## Open Questions

_All resolved:_

1. ~~Blocking vs. Advisory Gate~~ → **Always advisory.** Builder retains merge authority.
2. ~~Scope at feature level~~ → **Full per-task diff detail**, not just accumulated feature diff.
3. ~~Persist or ephemeral?~~ → **Ephemeral.** Output in agent response only; not saved to `.cicadas/`.
4. ~~Merge with Reflect or separate?~~ → **Orthogonal.** Reflect = sync specs to code. Code Review = evaluate code against specs + quality. Distinct operations with distinct triggers.
5. ~~Security/quality scope~~ → **Yes, include security.** Advisory scan for common issues (OWASP patterns, input validation, exposed secrets, unguarded access).
6. ~~Lightweight paths~~ → **Yes, supported.** Fix and tweak branches use buglet.md / tweaklet.md as the spec anchor; simplified report structure.

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Agent produces low-quality reviews (hallucinated findings, misread diffs) | Med | High | Structured output format + precise reasoning steps in prompt; Builder always reviews before acting |
| Code Review slows inner loop | Med | Med | Always optional; v2 lifecycle opt-in only |
| Reflect + Code Review redundancy confuses Builder | Med | Med | Clear distinction in SKILL.md: Reflect = sync; Code Review = evaluate |
| Security scan produces noisy false positives | Med | Med | Advisory-by-default for security; only Blocking for clear critical issues (e.g., committed secrets) |
| Review scope creep (agent over-reviews unrelated code) | Low | Med | Scope anchored to diff only, not full codebase |

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
