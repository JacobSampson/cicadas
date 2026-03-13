
---
next_section: ''
---

# UX Design: visual-requirements

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

**Primary goal:** The Builder feels in control of *how* they provide requirements (talk, doc, or video) and never feels stuck — the agent’s question and instructions are clear, and the next step is always obvious.

**Design constraints:**
- **Channel:** Conversational (agent chat); no new GUI or CLI commands in MVP.
- **Existing pattern:** Cicadas Emergence is already doc-by-doc with pace choice; this adds one earlier choice (intake) and two new flows (Doc, Loom).
- **Technical:** Agent-only behavior; Builder may use Loom in browser/app and paste transcript into a file in the repo.

**Skip condition:** Not applicable — this initiative is entirely about the Builder’s experience of the Clarify conversation and instructions.

---

## User Journeys & Touchpoints

### Video-first Builder — "I’ll say it in a Loom"

**Entry point:** Starts Emergence, runs Clarify for initiative `{name}`.
**First touchpoint:** Sees Process Preview & Pace, then the intake question (Q / D / L).
**Key moment:** Chooses [L], reads the Loom instructions in the agent response, records, pastes transcript to `drafts/{name}/loom.md`, and replies "done". Agent then returns a draft PRD.
**Exit state:** PRD draft in hand, ready to review and iterate.
**Pain points to design around:** Unclear where to paste the transcript; not knowing what to say in the Loom; agent proceeding before file exists.

---

### Doc-first Builder — "I have a brief already"

**Entry point:** Same as above.
**First touchpoint:** Intake question; chooses [D].
**Key moment:** Agent tells them exactly where to put the file (`drafts/{name}/requirements.md`); they put it there and confirm. Agent returns draft PRD.
**Exit state:** PRD derived from their doc, ready for review.
**Pain points to design around:** Wrong path or filename; agent reading before file is there.

---

### Q&A Builder — "Just ask me"

**Entry point:** Same as above.
**First touchpoint:** Intake question; chooses [Q].
**Key moment:** Flow continues as today — no extra steps, first question from Ingest.
**Exit state:** Same as current Clarify (iterative PRD building).
**Pain points to design around:** None new; avoid making the extra question feel like friction.

---

## Information Architecture

No app/site map — this is a single conversational flow with one branching point (intake).

**Flow structure:**
```
Clarify start
├── Process Preview & Pace (existing)
├── Intake choice: [Q] [D] [L]
├── [Q] → Ingest → … (existing)
├── [D] → Instructions → Wait for file → Read → Fill PRD → Review
└── [L] → Instructions → Wait for loom.md → Read → Fill PRD → Review
```

**Navigation model:** Linear within the conversation; the only "nav" is the Builder’s reply (Q, D, or L, or "done" / "file is there").

---

## Key User Flows

### Flow 1: Loom path (happy path)

1. Builder runs Clarify; sees pace question, then intake question.
2. Builder replies with [L] (or "Loom", "L").
3. Agent responds with the Loom instructions block (record → copy transcript → save to `drafts/{initiative}/loom.md` → reply when done). Agent stops.
4. Builder records Loom, copies transcript, creates/edits `drafts/{initiative}/loom.md`, replies e.g. "loom.md is in place" or "done".
5. Agent reads `loom.md`, runs Canon Check + Initialize, fills PRD from transcript, presents draft. Agent stops for review per pace.
6. Builder reviews, requests changes or continues to next doc.

**Alternate:** Builder says they don’t have transcript yet — agent can remind them of the path and wait.

---

### Flow 2: Doc path (happy path)

1. Builder runs Clarify; sees pace, then intake; replies [D].
2. Agent instructs: put requirements in `drafts/{initiative}/requirements.md` and confirm when ready. Agent stops.
3. Builder adds file, replies "done" or "it’s there".
4. Agent reads file, Canon Check + Initialize, fills PRD, presents draft. Stops for review.
5. Builder reviews and continues.

**Alternate:** Builder asks for a different path (e.g. `brief.md`) — agent accepts and reads from that path.

---

### Flow 3: Q&A path (unchanged)

1. Builder runs Clarify; sees pace, then intake; replies [Q].
2. Agent proceeds to Ingest (initial request), then Canon Check, Initialize, Iterative Drafting as today.
3. No additional steps or waiting for files.

---

## UI States

The "UI" here is the agent’s messages and the Builder’s replies. States to design for:

| State | Trigger | What the Builder Sees |
|-------|---------|----------------------|
| **Intake choice** | After pace | Clear prompt with [Q] [D] [L] and one-line descriptions. |
| **Waiting for Loom** | Chose [L] | Instructions block; agent explicitly waiting for confirmation that loom.md is in place. |
| **Waiting for Doc** | Chose [D] | Path and instruction; agent explicitly waiting for confirmation. |
| **File missing** | Agent tries to read loom.md or requirements.md and file absent | Agent does not assume content; asks Builder to add the file and confirm. |
| **PRD draft ready** | Agent finished fill-from-doc/loom | Full or section-wise PRD draft plus reminder of remaining spec steps. |

---

## Copy & Tone

**Voice:** Same as current Cicadas Emergence — clear, procedural, minimal. Options are terse ([Q] [D] [L]); instructions are step-by-step.

**Key principles:**
- One clear question at a time for the intake choice.
- Instructions must name the exact path (`drafts/{initiative}/loom.md`) so there’s no guesswork.
- When waiting for a file, say so explicitly ("Reply here once loom.md is in place") so the Builder knows the agent won’t proceed until they confirm.

**Critical copy (to be used in clarify.md):**

| Context | Copy |
|---------|------|
| Intake question | `How do you want to clarify requirements? [Q] Q&A / [D] Doc / [L] Loom` plus one line each. |
| Loom step 4 | `Save the transcript to: .cicadas/drafts/{initiative}/loom.md` |
| Loom step 5 | `Reply here once loom.md is in place; I'll read it and fill the PRD from it.` |
| Doc instruction | `Place your requirements document in .cicadas/drafts/{initiative}/requirements.md` (or agreed path). |
| File missing | Ask Builder to add the file and confirm; do not assume or invent content. |

---

## Visual Design Direction

**N/A for MVP.** No visual UI; all interaction is text in the agent conversation. Any "visual" is the formatting of the instructions block (numbered steps, code path) for scanability.

---

## UX Consistency Patterns

- **Choice presentation:** Same pattern as pace ( [S] [D] [A] ): short labels and one-line descriptions.
- **Waiting for user:** When the agent needs a file, state exactly what’s needed and that the agent will wait for confirmation before proceeding.
- **Error / missing file:** Do not proceed; prompt once for the correct file and path.

---

## Responsive & Accessibility

**N/A for MVP.** No layout or breakpoints. Accessibility is the same as for the rest of the agent chat (readable copy, clear structure in instructions). If the Builder uses Loom, that’s their tool; we only specify transcript placement and agent behavior.

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
