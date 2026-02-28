---
next_section: 'Done'
steps_completed:
  - Overview & Context
  - Tech Stack & Dependencies
  - Project / Module Structure
  - Architecture Decisions (ADRs)
  - Data Models
  - API & Interface Design
  - Implementation Patterns & Conventions
  - Security & Performance
  - Implementation Sequence
---

# Tech Design: bugs-and-tweaks

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

**Summary:** This initiative introduces "lightweight paths" for handling bugs and minor tweaks within the Cicadas methodology. It preserves the strict state machine (`drafts` -> `active` -> `archive`) and registry tracking, but relaxes the documentation requirements (using `buglet.md` and `tweaklet.md` instead of the full 5-document suite) and uses a single-branch workflow. Architecturally, the Chorus scripts must be updated to tolerate missing spec files for these paths, to bypass the `initiative/{name}` parent branch requirement, and to enforce "significance checks" before archiving.

### Cross-Cutting Concerns

1. **State Machine Integrity** — The core `drafts` -> `active` -> `archive` flow and `registry.json` tracking must remain unbroken.
2. **Backward Compatibility** — Existing (standard) initiatives must not be impacted by the relaxed validation rules for lightweight paths.
3. **Escalation** — The system must be able to gracefully upgrade a `buglet`/`tweaklet` into a full initiative if complexity demands it.

### Brownfield Notes

This modifies the core Chorus orchestration scripts (`scripts/chorus/scripts/`). The existing registry structure (`registry.json`) and index (`index.json`) must be maintained, though their parsing logic may need to accommodate the new branch naming conventions (`fix/` and `tweak/`).

---

## Tech Stack & Dependencies

| Category | Selection | Rationale |
|----------|-----------|-----------|
| **Language/Runtime** | Python 3.x | Existing codebase for Chorus scripts. |
| **Testing** | pytest (assuming existing) | To verify script modifications. |

**New dependencies introduced:** None

---

## Project / Module Structure

```
project-root/
├── <agent-skills-dir>/
│   └── cicadas/
│       ├── SKILL.md                  # [MODIFIED] Define lightweight paths & rules
│       ├── templates/
│       │   ├── buglet.md             # [NEW] Template for bug fixes
│       │   └── tweaklet.md           # [NEW] Template for tweaks
│       └── emergence/
│           ├── bug-fix.md            # [NEW] Subagent for drafting buglets
│           └── tweak.md              # [NEW] Subagent for drafting tweaklets
└── scripts/
    └── chorus/
        └── scripts/
            ├── kickoff.py            # [MODIFIED] Relax doc checks for fast paths
            ├── branch.py             # [MODIFIED] Allow direct main branching for fast paths
            ├── update_index.py       # [MODIFIED] Handle fix/tweak branch prefixes
            ├── archive.py            # [MODIFIED] Add significance check logic
            └── status.py             # [MODIFIED] Display lightweight paths correctly
```

---

## Architecture Decisions (ADRs)

### ADR-1: Single Branch vs. Feature Branches for Fast Paths

**Decision:** Lightweight paths (`fix/*` and `tweak/*`) will use a single branch derived directly from `main`, bypassing the `initiative/{name}` parent branch structure.

**Rationale:** The primary goal is velocity for trivial changes. Mandating an initiative branch that only ever holds one feature branch is pure overhead.

**Affects:** `branch.py`, `update_index.py`, `SKILL.md`.

---

### ADR-2: Specification Storage

**Decision:** Lightweight specs (`buglet.md` and `tweaklet.md`) will be stored in the standard `.cicadas/active/{name}/` directories, rather than a separate lightweight folder structure.

**Rationale:** This maintains the simplicity of the existing state machine and allows `status.py` and `archive.py` to function with minimal modification.

**Affects:** `kickoff.py`, `archive.py`.

---

## Data Models

### Modified Models

The `registry.json` structure remains the same, but the expected values for branch schemas must be updated to accept `fix/*` and `tweak/*` prefixes natively without throwing validation errors.

---

## API & Interface Design

### Command Modifications

`branch.py` must support a `--fast-path` flag (or infer it from the branch prefix) to bypass the `initiative` parent check.

```
python scripts/chorus/scripts/branch.py fix/typo-fix --intent "Fixing a typo" --fast-path
```

`archive.py` must enforce the "significance check" for fast paths before proceeding.

---

## Implementation Patterns & Conventions

### Validation Relaxation Pattern

When modifying scripts (e.g., `kickoff.py`), use explicit branch prefix checking to selectively bypass strict validation:

```python
def validate_artifacts(initiative_name, branch_type):
    if branch_type in ['fix', 'tweak']:
        # Only check for buglet.md or tweaklet.md
        pass
    else:
        # Check for full suite (PRD, UX, Tech, etc.)
        pass
```

---

## Security & Performance

**Security:** N/A (Internal developer tooling)
**Performance:** The significance check in `archive.py` will require LLM invocation (to determine if Canon needs updating). This adds latency to the archiving step, but it is an asynchronous/infrequent operation, so the impact is acceptable.

---

## Implementation Sequence

1. **Artifact Foundation** — Create `buglet.md` and `tweaklet.md` templates and their corresponding emergence sub-skills (`bug-fix.md`, `tweak.md`).
2. **SKILL Definition** — Update `SKILL.md` to formally document the lightweight paths, boundaries, and the emergence escalation path.
3. **Script Updates: Lifecycle** — Modify `kickoff.py` and `branch.py` to allow the lightweight workflow and relaxed validations.
4. **Script Updates: Conclusion** — Modify `update_index.py`, `status.py`, and `archive.py` (adding the significance check).
5. **Validation Run** — Execute a dummy `fix/` through the entire pipeline to verify functionality.
