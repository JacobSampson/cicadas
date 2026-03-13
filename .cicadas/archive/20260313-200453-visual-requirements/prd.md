
---
next_section: ''
---

# PRD: visual-requirements

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

Allow Builders to kickstart or replace the PRD (Clarify) process using a Loom video transcript or a requirements doc, instead of text Q&A only. As the first step of Clarify, Cicadas asks whether the user wants to clarify via **text Q&A**, **a doc**, or **Loom**. If Loom: provide instructions for recording and then copying the transcript to `drafts/{initiative}/loom.md`; then fill the PRD from that transcript. This initiative covers the intake choice, Loom path (instructions + loom.md → PRD), and doc path.

### What Makes This Special

- **Flexible intake** — Clarify adapts to how the Builder prefers to express requirements (conversation, document, or video).
- **Loom-native** — Video + transcript can replace or seed the PRD without re-typing; transcript becomes the source for PRD sections.
- **Doc-native** — A pre-written requirements doc in `drafts/{initiative}/` can be used to populate the PRD.

## Project Classification

**Technical Type:** Developer Tool / Methodology Orchestrator
**Domain:** Spec-driven development (Cicadas)
**Complexity:** Low–Medium — New intake branch in Clarify subagent + file conventions; no new scripts in MVP.
**Project Context:** Brownfield — Cicadas already has Emergence, Clarify subagent, and drafts layout.

---

## Success Criteria

### User Success

A Builder achieves success when they can:

1. **Choose their preferred intake** — At the start of Clarify, see a clear choice (Q&A, Doc, or Loom) and select one without ambiguity.
2. **Use Loom without re-typing** — Record a Loom, paste the transcript into the designated file, and get a PRD draft derived from it.
3. **Use a doc without re-typing** — Place an existing requirements doc in the designated path and get a PRD draft derived from it.

### Technical Success

- Clarify subagent instructions (emergence/clarify.md) include the intake step and both Doc and Loom paths.
- File convention is documented: `drafts/{initiative}/loom.md` for Loom transcript, `drafts/{initiative}/requirements.md` (or agreed path) for doc.

### Measurable Outcomes

- One round of Emergence (Clarify → UX → Tech → Approach → Tasks) completes with the new intake options exercised and PRD produced from at least one non-Q&A source in test or dogfood.

---

## User Journeys

### Journey 1: Builder who prefers video — "I think out loud"

Pat is kicking off a new initiative and finds it easier to talk through the problem than to type. They start Emergence and run the Clarify subagent. The agent asks how they want to clarify; Pat chooses Loom. The agent shows short instructions: record in Loom, then save the transcript to `drafts/{initiative}/loom.md`. Pat records a 5-minute Loom covering the problem, users, and success criteria, copies the transcript from Loom into loom.md, and tells the agent. The agent reads loom.md, maps the content to PRD sections, and presents a draft PRD. Pat reviews and iterates. Success is a complete PRD without having to type the initial requirements in Q&A form.

**Requirements Revealed:** Intake choice, Loom instructions, loom.md convention, PRD fill-from-transcript.

---

### Journey 2: Builder with an existing doc — "I already wrote it down"

Sam has a requirements brief or one-pager from a stakeholder. They start Clarify; the agent asks intake. Sam chooses Doc. The agent tells them to put the file at `drafts/{initiative}/requirements.md`. Sam copies the doc there and confirms. The agent reads it, infers PRD structure, and fills the PRD. Sam reviews and refines. Success is reusing existing prose instead of re-entering it via Q&A.

**Requirements Revealed:** Intake choice, doc path convention, PRD fill-from-doc.

---

### Journey 3: Builder who prefers conversation — "I want to be asked"

Jordan prefers the current flow: the agent asks questions, they answer, and the PRD is built interactively. At Clarify start they choose Q&A. The flow is unchanged from today (Ingest → Canon Check → Initialize → Iterative Drafting). Success is no regression for the existing Q&A path.

**Requirements Revealed:** Intake choice defaults; Q&A path unchanged.

---

### Journey Requirements Summary

| User Type | Key Requirements |
|-----------|------------------|
| **Video-first Builder** | Intake choice, Loom instructions, loom.md, fill PRD from transcript |
| **Doc-first Builder** | Intake choice, requirements doc path, fill PRD from doc |
| **Q&A Builder** | Intake choice, Q&A path preserved |

---

## Scope & Phasing

### MVP — Minimum Viable Product (v1)

**Core Deliverables:**
- Clarify step 0.5: ask intake (Q / D / L) before Ingest.
- Q&A path: behavior unchanged when [Q] selected.
- Doc path: instructions to put doc in `drafts/{initiative}/requirements.md` (or stated path); read file and fill PRD; present for review.
- Loom path: instructions for recording Loom and saving transcript to `drafts/{initiative}/loom.md`; read loom.md and fill PRD; present for review.
- Document file conventions in Clarify (and optionally in SKILL or canon) so Builders and agents know where to put loom.md / requirements doc.

**Quality Gates:**
- Emergence doc (e.g. EMERGENCE.md or clarify.md) or SKILL references the intake options and file paths.
- No change to kickoff, branch, or other scripts for MVP (instructions and agent behavior only).

### Growth Features (Post-MVP)

**v2: Optional transcript ingestion**
- Script or agent helper to fetch Loom transcript via API if Builder provides a Loom URL (out of scope for v1).

**v3: Other media**
- Support for other video/audio sources or formats (out of scope for v1).

### Vision (Future)

- Canon or product-overview could mention "requirements via Loom or doc" as a first-class intake option.

---

## Functional Requirements

### 1. Intake choice

**FR-1.1:** At the start of Clarify (after Process Preview & Pace), the agent MUST ask the Builder how they want to provide requirements: Q&A, Doc, or Loom.
- Options presented as [Q] Q&A, [D] Doc, [L] Loom with short descriptions.

**FR-1.2:** If the Builder chooses Q&A, the agent MUST proceed to the existing Ingest step and iterative drafting without further intake steps.

### 2. Doc path

**FR-2.1:** If the Builder chooses Doc, the agent MUST instruct them to place the requirements document in `.cicadas/drafts/{initiative}/requirements.md` (or an agreed path).
- Agent MUST wait for Builder confirmation that the file is in place before reading.

**FR-2.2:** The agent MUST read the document and populate the PRD sections (Executive Summary through Risk Mitigation) by inferring structure from the content.
- Agent MUST still run Canon Check and Initialize (create prd.md from template) before filling.
- Agent MUST present the draft PRD for review according to the chosen emergence pace.

### 3. Loom path

**FR-3.1:** If the Builder chooses Loom, the agent MUST display instructions that cover: (1) opening/starting a Loom recording, (2) what to say (problem, users, success, scope, constraints), (3) copying the transcript from Loom, (4) saving the transcript to `.cicadas/drafts/{initiative}/loom.md`, (5) replying to the agent when done.
- Agent MUST stop and wait until the Builder indicates loom.md is in place.

**FR-3.2:** Once loom.md exists, the agent MUST read it and populate the PRD by mapping transcript content to PRD sections.
- Agent MUST still run Canon Check and Initialize before filling.
- Agent MUST present the draft PRD for review according to the chosen emergence pace.

### 4. Conventions and docs

**FR-4.1:** The file paths `drafts/{initiative}/loom.md` and `drafts/{initiative}/requirements.md` (or equivalent) MUST be documented in the Clarify subagent instructions so that Builders and agents know where to read/write.
- Optional: mention in EMERGENCE.md or SKILL so the convention is discoverable.

---

## Non-Functional Requirements

- **Performance:** N/A for MVP (no new scripts; agent reads one file).
- **Reliability:** If loom.md or requirements.md is missing when the agent tries to read it, the agent MUST prompt the Builder to add the file and not assume content.
- **Security:** No new credentials or external APIs in MVP; Loom transcript is user-pasted content only.
- **Maintainability:** Intake logic lives in a single place (clarify.md); Doc/Loom fill behavior should be described clearly so future agents or scripted steps can replicate.

---

## Open Questions

- **OQ-1:** Should we support an alternate doc filename (e.g. `brief.md`, `context.md`) by default, or always require `requirements.md`? *Owner: Builder/agent; resolve during Approach or implementation.*
- **OQ-2:** For Loom, should we ever auto-fetch transcript from a URL in a later version? *Deferred to v2.*

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Transcript quality varies | Medium | Medium | Agent guidance in instructions on what to say in the Loom; PRD review step catches gaps. |
| Doc structure doesn't match PRD | Medium | Low | Agent infers mapping; Builder reviews and corrects in Finalize. |
| Builder forgets to add loom.md | Low | Low | Agent waits for confirmation; clear instructions reduce confusion. |
| Regression in Q&A path | Low | High | Keep Q&A as explicit branch; no shared logic change for step 1–5 when Q selected. |
