---
next_section: 'Done'
steps_completed:
  - Executive Summary
  - Project Classification
  - Success Criteria
  - User Journeys
  - Scope & Phasing
  - Functional Requirements
  - Non-Functional Requirements
  - Open Questions
  - Risk Mitigation
---

# PRD: bugs-and-tweaks

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

Cicadas currently mandates a rigorous, multi-branch, documentation-heavy process for all initiatives. This PRD defines two new "lightweight paths" through the Cicadas methodology (and by extension, Antigravity) designed specifically for **Simple Bug Fixes** and **Small Tweaks/Improvements**. These paths still follow the standard `drafts/` -> `active/` -> `archive/` lifecycle, but require significantly less documentation and utilize a single branch instead of a complex tree of initiative and feature branches.

### What Makes This Special

- **Right-Sized Documentation** — Reduces the required artifacts (e.g., just a PRD and Tasks) while strictly maintaining the standard folder lifecycle.
- **Velocity** — Developers can fix bugs and ship tweaks faster via a streamlined, single-branch workflow.
- **Process Flexibility** — Preserves the rigor of the main Cicadas path for complex features, with built-in escape hatches to upgrade lightweight paths to full initiatives if complexity grows mid-flight.

## Project Classification

**Technical Type:** Developer Tool (Process/Methodology Extension)
**Domain:** Software Engineering / Productivity
**Complexity:** Low — This is an intentional reduction in complexity for specific, bounded use cases.
**Project Context:** Brownfield — Extending the existing Cicadas methodology defined in `SKILL.md` and related scripts.

---

## Success Criteria

### User Success

A user achieves success when they can:

1. **Fix a simple bug directly** — A developer can address an isolated defect drafting only lightweight specs (e.g., `buglet.md`) and using a single branch hierarchy, while still flowing through `drafts` -> `active` -> `archive`.
2. **Ship a minor tweak quickly** — A developer can implement a small enhancement drafting only lightweight specs (e.g., `tweaklet.md`) using the same lightweight process.
3. **Understand and Upgrade** — The methodology clearly defines the boundary for a lightweight path, and can seamlessly "upgrade" a lightweight fix/tweak into a full initiative if complexity increases mid-flight.

### Technical Success

The system is successful when:

1. **The Scripts Support It** — The Chorus scripts (`init.py`, `branch.py`, `update_index.py`, etc.) can handle these lightweight branches without erroring due to missing initiative context or required artifacts.
2. **The Agent Understands It** — The `SKILL.md` clearly outlines when and how the AI agent should use these paths vs. the standard path.

### Measurable Outcomes

- Time from idea/bug discovery to raised PR is significantly reduced for changes qualifying for the lightweight paths.
- Zero "process violations" logged by the Chorus scripts when legitimately using these new paths.

---

## User Journeys

### Journey 1: The AI Developer — The Quick Bug Fix

Dan the Developer is working in a Cicadas-managed project and notices a typo in an error message that is confusing users. Under the standard process, Dan would write 5 highly detailed spec documents. With the lightweight path, Dan uses the `bug-fix` subagent to draft a very brief `buglet.md` in `drafts/`, kicks it off to `active/`, uses a single branch to make the change, and merges it back to `main`, at which point the spec is archived. Success is fixing the bug rapidly while still maintaining the standard state machine.

**Requirements Revealed:** Single-branch workflow, `buglet.md` documentation, `bug-fix.md` subagent, standard folder lifecycle.

---

### Journey 2: The AI Developer — The Expanding Tweak

Dan starts a lightweight "tweak" to update a button component. Mid-flight, he discovers the button is tightly coupled to a legacy state machine that needs a full rewrite. The agent recognizes modifying the state machine exceeds the "tweak" threshold and halts. It helps Dan upgrade the active tweak into a full initiative, generating a Tech Design and Approach document before work continues on properly partitioned feature branches. Success is moving fast initially, but catching scope creep safely.

**Requirements Revealed:** Mid-flight complexity recognition, upgrade path to full initiative.

---

### Journey Requirements Summary

| User Type | Key Requirements |
|-----------|-----------------|
| **AI Developer** | Single-branch workflow, Documentation bypass, Clear boundary thresholds for paths, Script tolerance for missing initiative structure |

---

## Scope

**Core Deliverables:**
- Define the two lightweight paths (Bug Fix, Tweak) in `SKILL.md`, detailing single-branch conventions.
- Create new markdown templates for these paths: `<agent-skills-dir>/cicadas/templates/buglet.md` and `<agent-skills-dir>/cicadas/templates/tweaklet.md`. These templates should combine minimal context with actionable tasks.
- Create two new emergence sub-skills (`<agent-skills-dir>/cicadas/emergence/bug-fix.md` and `<agent-skills-dir>/cicadas/emergence/tweak.md`) to guide the agent in drafting these specific "let" documents using the new templates.
- Provide explicit guidelines and agent instructions on what qualifies for a lightweight path vs. the standard initiative path.
- Implement mid-flight complexity recognition: Prompt the agent to monitor scope and upgrade a fix/tweak to a full initiative (requiring UX, Tech Design, Approach) if it breaches complexity thresholds.
- Implement Canon update logic for tweaks/fixes: Ensure the agent performs a significance check upon completion. If the change warrants it, the agent must perform a Reflect operation to update the Canon documents (e.g., `ux-overview.md` or `tech-overview.md`) before archiving the `buglet`/`tweaklet`.
- Update Chorus scripts (e.g., `kickoff.py`, `update_index.py`, `archive.py`) to flawlessly handle the lifecycle (`drafts` -> `active` -> `archive`) and registry updates for single-branch lightweight paths alongside traditional nested initiatives.

**Quality Gates:**
- The updated strategy must be successfully applied to fix a real bug or make a real tweak in the current Cicadas repo.
- A test scenario demonstrating a "tweak" expanding in scope and successfully upgrading to a full initiative.

---

## Functional Requirements

### 1. Fast Path Routing

**FR-1.1:** The methodology must formally define two lightweight branch types: `fix/*` and `tweak/*`.
- `fix/*`: Used exclusively for defect remediation.
- `tweak/*`: Used for minor, non-structural enhancements.

**FR-1.2:** The methodology must establish a threshold for when a change must use the standard initiative path.
- The threshold should be qualitative (e.g., "introduces a new module or dependency", "alters cross-system data flow").

### 2. Documentation Bypass

**FR-2.1:** Branches matching `fix/*` or `tweak/*` must still utilize the `.cicadas/active/` specification folder, but use specific lightweight artifacts (`buglet.md` or `tweaklet.md`) instead of the standard 5-document suite.

**FR-2.2:** The emergence phase must include specific sub-skills (`emergence/bug-fix.md` and `emergence/tweak.md`) designed to elicit and draft these lightweight documents.

**FR-2.2:** Branches matching `fix/*` or `tweak/*` must be allowed to branch directly from `main`, bypassing the `initiative/*` parent branch requirement.

**FR-2.3 (Complexity Upgrade):** The agent must be instructed to monitor the scope of active lightweight branches. If complexity increases (e.g., modifying architectural patterns, adding new modules), the agent must halt, prompt the user, and facilitate upgrading the lightweight path into a full initiative by generating the missing spec documents.

### 3. Registry and Ledger Compatibility

**FR-3.1:** The Chorus scripts (`kickoff.py`, `update_index.py`, `archive.py`) must natively support registering, indexing, and archiving these lightweight paths through the standard `drafts` -> `active` -> `archive` folders without expecting child feature branches.

---

## Non-Functional Requirements

- **Maintainability:** The addition of these paths must not over-complicate `SKILL.md` or make the core Cicadas philosophy ambiguous. They should be presented clearly as exceptions for minor work.
- **Reliability:** The existing scripts (`archive.py`, `prune.py`, `synthesize.py`) must gracefully ignore `fix/` and `tweak/` branches if they encounter them during initiative-level operations.

---

## Open Questions

- *Resolved: Fixes and tweaks will use the standard `drafts` -> `active` -> `archive` process and will be tracked in the `registry.json`, but they will use specific lightweight documentation (`buglet.md` or `tweaklet.md`).*

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Scope Creep (Tweaks turning into features without design docs) | High | Medium | Provide very strict, objective criteria in `SKILL.md` for what qualifies as a tweak vs. a feature. |
| Code Drift (Canon docs become outdated because changes bypass standard Reflect) | Medium | Medium | Require a "significance check" upon completion of a bug or tweak. If the change is significant, the agent must perform a Reflect and Canon update before merging and archiving. |
