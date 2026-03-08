
---
next_section: 'Overview & Context'
---

# Tech Design: Token Usage Logging

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

**Summary:** A new `tokens.py` module provides the core append-only log API. It reads the current `tokens.json` (creating it if absent), appends the validated entry, and writes back atomically. Existing scripts (`kickoff.py`, `branch.py`, `history.py`) import and call this module at natural phase boundaries. No new external dependencies. The log file travels with initiative specs through the existing `shutil.move` lifecycle — no special handling required.

### Cross-Cutting Concerns

1. **Null-safety everywhere** — token counts are optional integers; all arithmetic in `history.py` must guard against `None`.
2. **Never crash a script** — all `tokens.py` I/O is wrapped to degrade gracefully on corrupt/missing files.
3. **Consistent schema** — entry validation in `append_entry()` is the single enforcement point; downstream consumers trust the schema.

### Brownfield Notes

- Existing scripts (`kickoff.py`, `branch.py`) gain one call at the end of their main function — no other logic changes.
- `history.py` gains a new `load_token_summary()` helper and adds a token block to `render_html()`.
- `archive.py` requires **no changes** — `tokens.json` moves automatically with the initiative folder via `shutil.move`.
- `utils.py` requires **no changes** — `tokens.py` is a separate module, no circular imports.

---

## Tech Stack & Dependencies

| Category | Selection | Rationale |
|----------|-----------|-----------|
| **Language/Runtime** | Python 3.12+ | Existing project standard |
| **Serialization** | stdlib `json` | Existing pattern; no new deps |
| **Time** | stdlib `datetime` with UTC | Existing pattern in scripts |
| **Testing** | stdlib `unittest` | Existing test framework |

**New dependencies introduced:** None.

---

## Project / Module Structure

```
src/cicadas/scripts/
├── tokens.py                 # NEW: token log API (init_log, append_entry, load_log)
├── kickoff.py                # [MODIFIED] append lifecycle/kickoff entry
├── branch.py                 # [MODIFIED] append implementation/branch-start entry
└── history.py                # [MODIFIED] load_token_summary() + token block in render_html()

src/cicadas/emergence/
├── EMERGENCE.md              # [MODIFIED] document pace option in workflow table
├── clarify.md                # [MODIFIED] step 0: ask pace, write emergence-config.json
├── ux.md                     # [MODIFIED] step 0: read pace, enforce stop behavior
├── tech-design.md            # [MODIFIED] step 0: read pace, enforce stop behavior
├── approach.md               # [MODIFIED] step 0: read pace, enforce stop behavior
└── tasks.md                  # [MODIFIED] step 0: read pace, enforce stop behavior

tests/
└── test_tokens.py            # NEW: unit tests for tokens.py + script integration
```

**Key structural decisions:**
- `tokens.py` is a standalone module with no imports from `utils.py` beyond what's needed; uses `pathlib.Path` and `json` directly. This avoids any future circular import risk.
- The log file path is always `{initiative_dir}/tokens.json` — caller passes the path; `tokens.py` has no path-discovery logic.

---

## Architecture Decisions (ADRs)

### ADR-1: Caller passes file path, not initiative name

**Decision:** `append_entry()` takes a `log_path: Path` argument. It does not discover the path from the registry or project root.

**Rationale:** Keeps `tokens.py` stateless and easily testable. Scripts already know the initiative dir (they've just resolved it). Avoids tying `tokens.py` to the Cicadas directory structure, making it reusable in other contexts.

**Affects:** `kickoff.py`, `branch.py`, test setup.

---

### ADR-2: Append-only with read-modify-write (no streaming append)

**Decision:** `append_entry()` reads the full file, appends to the `entries` list, and rewrites the file with `json.dump`. No line-by-line JSONL.

**Rationale:** Initiative token logs will have at most a few dozen entries. Full rewrite is simpler and produces pretty-printed JSON that humans can inspect. JSONL would require separate parsing. The file never exceeds a few KB.

**Affects:** `tokens.py` implementation; history rollup reads standard JSON.

---

### ADR-3: Scripts write boundary entries with null counts

**Decision:** Phase-boundary entries written by scripts (`kickoff`, `branch-start`) always have `input_tokens=None`, `output_tokens=None`, `cached_tokens=None`, `source="unavailable"`.

**Rationale:** Scripts are Python processes — they have no access to their own LLM context costs. Null entries with a clear source flag are more honest and useful than omitting the entry entirely. They also serve as phase markers even when counts are absent, helping history.py identify phase boundaries in the timeline.

**Affects:** `kickoff.py`, `branch.py`; `history.py` rollup must filter nulls from sums.

---

### ADR-5: Emergence pace stored in a sidecar file, not in prd.md frontmatter

**Decision:** Pace preference is written to a separate `emergence-config.json` file rather than embedded in `prd.md` frontmatter or passed only via agent memory.

**Rationale:** A sidecar file is readable by every subsequent emergence agent regardless of which agent wrote the PRD. It survives context resets, is auditable, and doesn't pollute the PRD template. Agent memory alone is unreliable across multi-turn sessions.

**Affects:** `clarify.md` (writer), all other emergence agents (readers).

---

### ADR-4: Token summary in history.py is per-initiative only

**Decision:** `history.py` renders a per-initiative token summary (total input/output/cached by phase) but does NOT add a cross-initiative summary table in the MVP.

**Rationale:** Cross-initiative aggregation requires all archive entries to have consistent initiative names and model IDs — a constraint that breaks during migration. Per-initiative summary is safe, immediately useful, and doesn't require structural changes to the HTML layout.

**Affects:** `history.py` render_html(); cross-initiative table is deferred to v3.

---

## Data Models

### `tokens.json` File Schema

```json
{
  "entries": [
    {
      "timestamp": "2026-03-08T14:23:00Z",
      "initiative": "auth-revamp",
      "phase": "lifecycle",
      "subphase": "kickoff",
      "input_tokens": null,
      "output_tokens": null,
      "cached_tokens": null,
      "model": null,
      "source": "unavailable",
      "notes": null
    }
  ]
}
```

### Python type (for documentation)

```python
from typing import Literal

TokenEntry = {
    "timestamp": str,                         # ISO 8601 UTC, required
    "initiative": str,                        # required
    "phase": str,                             # required
    "subphase": str | None,                   # optional
    "input_tokens": int | None,
    "output_tokens": int | None,
    "cached_tokens": int | None,
    "model": str | None,
    "source": Literal["agent-reported", "unavailable", "estimated"],  # required
    "notes": str | None,
}
```

**Key field decisions:**
- `phase` is free-form string (not an enum) — new phases can be added without schema changes.
- `source` is a required string enum — prevents ambiguity between "I forgot to log" and "runtime can't report".
- All count fields are `int | None` — never `0` when unavailable; `0` means truly zero tokens.

---

## API & Interface Design

### `tokens.py` Public API

```python
def init_log(log_path: Path) -> None:
    """Create tokens.json with empty entries list if it doesn't exist."""

def append_entry(
    log_path: Path,
    initiative: str,
    phase: str,
    source: str,
    *,
    subphase: str | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    cached_tokens: int | None = None,
    model: str | None = None,
    notes: str | None = None,
) -> None:
    """Append a validated token entry to the log. Creates file if absent."""

def load_log(log_path: Path) -> list[dict]:
    """Return entries list. Returns [] if file absent or corrupt."""
```

### Usage in `kickoff.py`

```python
from tokens import append_entry

# After registering initiative and creating active_dir:
log_path = active_dir / "tokens.json"
append_entry(log_path, initiative=name, phase="lifecycle", subphase="kickoff", source="unavailable")
```

### Usage in `branch.py`

```python
from tokens import append_entry

# After registering branch:
active_dir = cicadas / "active" / active_name
log_path = active_dir / "tokens.json"
append_entry(log_path, initiative=active_name, phase="implementation", subphase=name, source="unavailable")
```

### `history.py` token rollup

```python
def load_token_summary(folder: Path) -> dict | None:
    """
    Read tokens.json from archive folder.
    Returns {total_input, total_output, total_cached, by_phase: {phase: {input, output, cached}}}
    or None if file absent, corrupt, or all entries have null counts.
    """
```

---

## Implementation Patterns & Conventions

### Naming Conventions

| Construct | Convention | Example |
|-----------|-----------|---------|
| Functions | snake_case | `append_entry()` |
| Constants | UPPER_SNAKE | `VALID_SOURCES` |
| Files | snake_case | `tokens.py` |

### Error Handling Pattern

```python
def load_log(log_path: Path) -> list[dict]:
    try:
        if not log_path.exists():
            return []
        with open(log_path) as f:
            data = json.load(f)
        return data.get("entries", [])
    except (json.JSONDecodeError, OSError):
        return []  # Never crash a script
```

**Rules:**
- `load_log()` and `load_token_summary()` never raise — they return empty/None on any I/O or parse error.
- `append_entry()` raises `ValueError` on schema violations (bad source, missing required fields) so callers know immediately if they pass invalid data.
- `append_entry()` wraps file I/O in try/except and prints a `[WARN]` rather than crashing the calling script.

### Testing Pattern

```python
class TestAppendEntry(CicadasTest):
    def test_creates_file_on_first_write(self):
        log = self.tmp / "tokens.json"
        append_entry(log, initiative="test", phase="lifecycle", subphase="kickoff", source="unavailable")
        entries = load_log(log)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["phase"], "lifecycle")
```

**Coverage expectations:** 90%+ on `tokens.py`; integration tests for kickoff and branch boundary writes.
**Mocking strategy:** No mocks — use real temp filesystem (project convention).

---

## Security & Performance

### Security

| Concern | Mitigation |
|---------|-----------|
| Sensitive data in notes | Documentation: notes is for human-readable context, not credentials. No enforcement at MVP. |
| File permissions | Inherits existing `.cicadas/` file permissions; no special handling needed. |

### Performance

| Concern | Target | Approach |
|---------|--------|---------|
| File I/O per script call | < 5ms | Read-modify-write on a < 10KB file; acceptable. |
| History rendering | No regression | Token summary added per card; no new O(n²) work. |

### Observability

- **Logs:** `append_entry()` prints `[WARN]` on I/O failure (consistent with other scripts).
- **Metrics:** None — `tokens.json` itself is the observability artifact.

---

## Implementation Sequence

1. **`tokens.py`** *(blocking)* — Core module: `init_log()`, `append_entry()`, `load_log()`. Schema validation. Tests.
2. **Script integration** *(depends on 1)* — Wire `append_entry()` into `kickoff.py` and `branch.py`. Tests confirm entries are written.
3. **History rollup** *(depends on 1)* — Add `load_token_summary()` to `history.py`; render token block in HTML cards. Tests confirm null-safe rendering.

**Parallel work opportunities:** Steps 2 and 3 both depend on `tokens.py` but are independent of each other — they can be implemented in parallel partitions.

**Known implementation risks:**
- History HTML rendering is string-templated; adding a conditional block for tokens must not break existing cards that lack token data.
