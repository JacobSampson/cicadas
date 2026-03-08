
---
next_section: 'Executive Summary'
---

# PRD: Token Usage Logging

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

Token usage logging adds an append-only `tokens.json` file to every Cicadas initiative, capturing input/output/cached token counts at each phase and subphase across the full lifecycle — from emergence drafting through archiving. It gives teams cradle-to-grave visibility into where AI costs are going so they can catch runaway phases, validate that context injection is working, and build intuition about cost patterns across initiatives.

### What Makes This Special

- **Lifecycle-native** — the log is created in drafts, promoted by kickoff, and archived alongside specs; no separate tracking infrastructure needed.
- **Best-effort and incremental** — runtimes that can't report token counts write `null` entries with a source flag; schema is consistent regardless of data quality.
- **Dual write model** — scripts write phase-boundary envelope entries; agents self-append interior usage within a phase; both patterns coexist cleanly.

## Project Classification

**Technical Type:** Developer Tool / Framework
**Domain:** Infrastructure / Observability
**Complexity:** Low — append-only JSON, no new dependencies, no external services
**Project Context:** Brownfield — adds a new artifact and wires it into existing scripts

---

## Success Criteria

### User Success

A user achieves success when they can:

1. **See total token cost per initiative** — after archiving, `history.py` shows a token summary table per initiative in the HTML output.
2. **Drill into phase breakdown** — `tokens.json` in the archive shows per-phase and per-subphase entries with input/output/cached counts and source attribution.
3. **See partial data without errors** — initiatives on runtimes that don't expose token counts produce valid `tokens.json` with `"source": "unavailable"` entries rather than missing or broken files.

### Technical Success

The system is successful when:

1. **Every kickoff creates `tokens.json`** — the file is present in `.cicadas/active/{name}/tokens.json` after every kickoff, even if the runtime can't report real counts.
2. **Archive preserves the log** — `tokens.json` moves with specs to `.cicadas/archive/{timestamp}-{name}/tokens.json` automatically.
3. **`history.py` renders a token summary** — the HTML timeline includes a per-initiative token rollup table when token data is available.

### Measurable Outcomes

- `tokens.json` present in 100% of initiated initiatives.
- `history.py` renders token table without crashing even when some entries have `null` counts.

---

## User Journeys

### Journey 1: Builder — "Where did all the tokens go?"

A builder has been running Cicadas for several initiatives and wants to understand which phases are most expensive. After completing an initiative, they run `python history.py` and see an HTML timeline that now includes a token cost section beneath each initiative card — total tokens, breakdown by phase, and a `(source: agent-reported)` attribution on entries where real counts are available. They immediately notice the synthesis phase is unexpectedly expensive and investigate.

**Requirements Revealed:** Phase-labeled entries, rollup by initiative, model attribution, source flag.

---

### Journey 2: Agent — "Log tokens at phase end"

An emergence subagent finishes drafting `tasks.md`. The subagent reads its runtime's token usage from the API response metadata and calls `append_entry()` with `phase="emergence"`, `subphase="tasks"`, and the actual counts. The entry is appended to `tokens.json` in the drafts folder. Later, kickoff promotes the entire drafts folder (including `tokens.json`) to active.

**Requirements Revealed:** `append_entry()` function accessible from scripts; entry schema including phase/subphase/model/source; graceful no-op when counts are unavailable.

---

### Journey Requirements Summary

| User Type | Key Requirements |
|-----------|-----------------|
| **Builder** | history.py token table, per-phase breakdown, archive preservation |
| **Agent** | append_entry() helper, schema validation, null-safe, source attribution |

---

## Scope

### MVP — Minimum Viable Product (v1)

**Core Deliverables:**
- New `tokens.py` utility with `init_log()`, `append_entry()`, `load_log()` functions
- `kickoff.py` writes a `kickoff` phase-boundary entry to `tokens.json` on initiative start
- `branch.py` writes a `branch-start` phase-boundary entry when a feature branch is registered
- `history.py` rolls up `tokens.json` entries from archived initiatives into a summary table appended to each initiative card
- Entry schema validated on write (no silent corruption)
- Source attribution: `agent-reported`, `unavailable`, `estimated`

**Quality Gates:**
- Unit tests for `tokens.py` (append, load, schema validation, null-safe rollup)
- Tests for kickoff and branch writing boundary entries
- `history.py` renders without error when `tokens.json` is absent, partial, or has null counts

### Growth Features (Post-MVP)

**v2: Archive and Prune Integration**
- `archive.py` writes a final `archive` boundary entry before moving the folder
- `prune.py` writes a `prune` entry before deletion

**v3: Cross-Initiative Reporting**
- Separate `tokens` CLI command that prints a summary table across all archived initiatives without generating HTML

### Vision (Future)

- Cost estimate column in the rollup (model pricing config per model ID)
- Token budget alerts: warn when a phase exceeds a configured threshold

---

## Functional Requirements

### 1. Token Log File Management

**FR-1.1:** A `tokens.json` file is created at `.cicadas/drafts/{name}/tokens.json` at the earliest opportunity — on kickoff if not already present.
- Kickoff creates the file if it doesn't exist in drafts.

**FR-1.2:** The log is a JSON object with a single `"entries"` array; entries are appended, never rewritten.

**FR-1.3:** The log file moves with the initiative folder: drafts → active (kickoff) → archive (archive.py). No special handling needed — it moves as part of the existing `shutil.move` calls.

---

### 2. Entry Schema

**FR-2.1:** Each entry must conform to:
```json
{
  "timestamp": "<ISO 8601 UTC>",
  "initiative": "<name>",
  "phase": "<phase-name>",
  "subphase": "<subphase-name | null>",
  "input_tokens": <int | null>,
  "output_tokens": <int | null>,
  "cached_tokens": <int | null>,
  "model": "<model-id | null>",
  "source": "<agent-reported | unavailable | estimated>",
  "notes": "<string | null>"
}
```

**FR-2.2:** `append_entry()` validates required fields (`timestamp`, `initiative`, `phase`, `source`) and raises `ValueError` on violation.

**FR-2.3:** `source` must be one of `agent-reported`, `unavailable`, `estimated`.

---

### 3. Script Phase-Boundary Writes

**FR-3.1:** `kickoff.py` appends an entry with `phase="lifecycle"`, `subphase="kickoff"` after registering the initiative. Token counts are `null`, source is `unavailable` (scripts can't introspect their own LLM call costs).

**FR-3.2:** `branch.py` appends an entry with `phase="implementation"`, `subphase=<branch-name>` after registering a feature branch. Token counts are `null`, source is `unavailable`.

---

### 4. History Rollup

**FR-4.1:** `history.py` reads `tokens.json` from each archive folder (if present).

**FR-4.2:** For each initiative, the HTML card includes a token summary: total input_tokens, total output_tokens, total cached_tokens, and count of entries by phase — summing only non-null values.

**FR-4.3:** If `tokens.json` is absent or all entries have null counts, the card omits the token section gracefully (no error, no "0 tokens" confusion).

---

### 5. Emergence Pace Selection

**FR-5.1:** At the start of the Clarify step (before drafting any content), the agent asks the Builder their preferred review pace:
```
Emergence pace — how often do you want to review?
  [S] Section  — pause after each section within a doc
  [D] Doc      — pause after each complete doc  (default)
  [A] All      — draft all docs, then present together
```

**FR-5.2:** The chosen pace is written to `.cicadas/drafts/{name}/emergence-config.json`:
```json
{ "pace": "doc" }
```

**FR-5.3:** Every subsequent emergence agent (UX, Tech Design, Approach, Tasks) reads `emergence-config.json` at the start and enforces the pace:
- `section` — pause after each section within the doc (existing per-section elicitation behavior)
- `doc` — complete the full doc, then hard stop for Builder review before proceeding
- `all` — complete the full doc and continue to the next without stopping

**FR-5.4:** Default pace is `doc` if the Builder skips the question or the file is absent.

---

## Non-Functional Requirements

- **Performance:** `append_entry()` is a simple file read-modify-write; no performance constraint beyond "fast enough not to block a script".
- **Reliability:** Corrupt or missing `tokens.json` must never crash a script. All reads are wrapped with graceful fallback to empty log.
- **Security:** `tokens.json` may contain model IDs and token counts; no secrets are logged. Notes field is free text — agents must not put API keys in notes.
- **Maintainability:** `tokens.py` is a standalone utility importable by any script; no circular imports with `utils.py`.

---

## Open Questions

- Should `init.py` create an empty `tokens.json` template in new projects? (Probably not — only created per-initiative, not globally.)
- Should the history rollup include a cost estimate? Deferred to v3; pricing tables change frequently.

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Corrupt tokens.json causes history.py crash | Low | Med | Wrap all reads in try/except; treat corrupt file as absent |
| Agents put sensitive data in notes field | Low | High | Document notes field as non-sensitive; no enforcement needed at MVP |
| Token counts unavailable on most runtimes at first | High | Low | Source attribution makes null entries expected and visible, not confusing |
