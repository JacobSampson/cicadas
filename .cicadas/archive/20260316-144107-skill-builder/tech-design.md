
---
next_section: 'done'
---

# Tech Design: skill-builder

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

This initiative adds skill authoring to Cicadas with minimal new infrastructure. There are two classes of change: (1) **thin script changes** — adding `skill/` as a recognised lightweight branch prefix to five existing scripts; and (2) **new files** — two scripts (`validate_skill.py`, `skill_publish.py`), two emergence instruction modules (`skill-create.md`, `skill-edit.md`), one template (`skill-SKILL.md`), and updates to `SKILL.md` and `start-flow.md`. No new data stores, no new dependencies, no changes to `registry.json` schema.

The branching model reuse is intentional: `skill/{name}` forks from `master` and follows the same lifecycle as `fix/{name}` and `tweak/{name}`. The only structural difference is the artifact set inside `active/skill-{name}/` (a SKILL.md tree rather than a `tweaklet.md`).

### Cross-Cutting Concerns

1. **Untrusted input** — `skill-create.md` and `skill-edit.md` must treat all Builder-provided content (dialogue answers, existing SKILL.md bodies read from disk) as data, not instructions, consistent with the existing Cicadas untrusted-input guardrail.
2. **Frontmatter parsing strategy** — `validate_skill.py` must not introduce a PyYAML dependency. Existing Cicadas scripts use stdlib only; this one follows suit.
3. **`emergence-config.json` merging** — any write to `emergence-config.json` must read, update, and write back (never overwrite), consistent with how `pace` and `building_on_ai` are handled today.

### Brownfield Notes

This initiative touches the following existing files — nothing else:
- `src/cicadas/scripts/branch.py` — prefix check for parent branch selection
- `src/cicadas/scripts/status.py` — branch grouping
- `src/cicadas/scripts/archive.py` — branch type detection
- `src/cicadas/scripts/prune.py` — branch type detection
- `src/cicadas/scripts/abort.py` — `LIGHTWEIGHT_PREFIXES` tuple
- `src/cicadas/SKILL.md` — new Skills section + branch hierarchy diagram + Builder commands
- `src/cicadas/emergence/start-flow.md` — new publish destination step (skill entry point only)

Must NOT change: `registry.json` schema, `index.json` schema, `kickoff.py` logic, `branch.py` registration logic beyond the parent branch selection.

---

## Tech Stack & Dependencies

| Category | Selection | Rationale |
|----------|-----------|-----------|
| **Language** | Python 3.11+ (stdlib only) | Matches all existing scripts; no new runtime. |
| **Frontmatter parsing** | `re` (stdlib regex) | See ADR-1. No PyYAML needed for the fields we validate. |
| **File copy/symlink** | `shutil.copytree` / `os.symlink` (stdlib) | Standard library; no external package needed. |
| **Testing** | `unittest` + real temp filesystem | Matches existing test conventions. |

**New dependencies introduced:** None.

**Dependencies explicitly rejected:**
- `PyYAML` — not needed; `validate_skill.py` only needs to extract `name` and `description` string values from frontmatter, which regex handles reliably for this constrained format.
- `click` / `argparse` plugins — existing scripts use stdlib `argparse`; `validate_skill.py` follows the same pattern.

---

## Project / Module Structure

```
src/cicadas/
├── scripts/
│   ├── validate_skill.py         # NEW — Agent Skills spec compliance validator
│   ├── skill_publish.py          # NEW — copy/symlink active/skill-{name} to publish_dir
│   ├── branch.py                 # [MODIFIED] add 'skill/' to lightweight prefix check
│   ├── status.py                 # [MODIFIED] add 'skill/' to branch grouping
│   ├── archive.py                # [MODIFIED] add 'skill/' to branch type detection
│   ├── prune.py                  # [MODIFIED] add 'skill/' to branch type detection
│   └── abort.py                  # [MODIFIED] add 'skill/' to LIGHTWEIGHT_PREFIXES
├── emergence/
│   ├── skill-create.md           # NEW — dialogue-driven skill create flow
│   ├── skill-edit.md             # NEW — dialogue-driven skill edit flow
│   └── start-flow.md             # [MODIFIED] add publish destination step (skill entry)
├── templates/
│   └── skill-SKILL.md            # NEW — minimal SKILL.md scaffold for internal agent use
└── SKILL.md                      # [MODIFIED] Skills section, branch hierarchy, Builder commands
```

**Key structural decisions:**
- New scripts live alongside existing ones in `scripts/` — no new subpackage.
- Instruction modules follow the existing `snake-case.md` naming convention in `emergence/`.
- `skill-SKILL.md` template uses a distinct name to avoid confusion with the Cicadas `SKILL.md` itself.

---

## Architecture Decisions (ADRs)

### ADR-1: Frontmatter parsing with stdlib regex, not PyYAML

**Decision:** `validate_skill.py` parses YAML frontmatter using `re` (stdlib) rather than `PyYAML`. It extracts `name` and `description` by matching `^name:\s*(.+)` and `^description:\s*["']?([\s\S]+?)["']?\s*$` within the frontmatter block, and checks for the presence of `---` delimiters.

**Rationale:** `validate_skill.py` only needs to check that `name` and `description` are present and meet length/charset constraints — not parse arbitrary YAML structures. Stdlib regex is sufficient and avoids introducing any new dependency into the scripts tree. Existing `utils.py` already uses `json` (stdlib) for all state files; following that precedent keeps the dependency footprint flat.

**Rejected alternative:** `PyYAML` — available in `.venv` but not guaranteed in all environments where scripts run. The existing `parse_partitions_dag()` in `utils.py` already uses a PyYAML-with-regex-fallback pattern for the same reason.

**Affects:** `validate_skill.py` implementation only.

---

### ADR-2: `skill/` prefix added to existing lightweight prefix lists — no new abstraction

**Decision:** Each affected script (`branch.py`, `status.py`, `archive.py`, `prune.py`, `abort.py`) adds `"skill/"` to the existing tuple or condition that already checks for `"fix/"` and `"tweak/"`. No new abstraction (e.g., a shared constant in `utils.py`) is introduced unless three or more scripts require the same list.

**Rationale:** The change to each script is 1–3 lines. Extracting to a shared constant in `utils.py` would be premature abstraction for changes this small, and would couple `utils.py` to a concept it currently doesn't own. If a fourth prefix type is ever added, refactoring to a shared constant at that point is trivial.

**Rejected alternative:** A `LIGHTWEIGHT_PREFIXES` constant in `utils.py` imported by all scripts — deferred; `abort.py` already defines its own local `LIGHTWEIGHT_PREFIXES` tuple; the others use inline conditions.

**Affects:** `branch.py`, `status.py`, `archive.py`, `prune.py`, `abort.py`.

---

### ADR-3: `publish_dir` stored in `emergence-config.json`, not `lifecycle.json`

**Decision:** The skill publish destination is stored as `publish_dir` in `.cicadas/drafts/skill-{name}/emergence-config.json` (and promoted to `active/` at kickoff). It is NOT stored in `lifecycle.json`.

**Rationale:** `lifecycle.json` defines PR boundaries and lifecycle steps — it is a process contract, not a skill-specific authoring property. `emergence-config.json` already holds skill-authoring choices (`pace`, `building_on_ai`, `eval_status`); `publish_dir` belongs in the same file. `skill_publish.py` reads `active/skill-{name}/emergence-config.json` at publish time.

**Affects:** `emergence-config.json` schema, `skill_publish.py`, `skill-create.md` start flow step.

---

### ADR-4: `skill_publish.py` copies by default; symlink is opt-in via `--symlink`

**Decision:** `skill_publish.py` uses `shutil.copytree` to copy `active/skill-{name}/` to `{publish_dir}/{slug}/` by default. Symlinking is available via `--symlink` flag.

**Rationale:** Symlinks are fragile when repos are moved or checked out at different paths, and they require the source (`.cicadas/active/`) to remain present for the agent to load the skill. A copy is always self-contained at the destination. The Cicadas installer already makes this same tradeoff: agent integrations use relative symlinks specifically because the source is the install dir (stable); here the source is `.cicadas/active/` (mutable, gets archived). Copy is safer by default.

**Rejected alternative:** Symlink-by-default — rejected because `.cicadas/active/skill-{name}/` is archived and removed at initiative completion, which would break all agent symlinks pointing to it.

**Affects:** `skill_publish.py`.

---

### ADR-5: Publish step triggered at initiative completion, not at merge

**Decision:** `skill_publish.py` is called as part of the **Complete Skill** agent operation (after merge to master, before archive), not as a git hook or automatic post-merge action.

**Rationale:** Consistent with how Cicadas handles all post-merge operations (canon synthesis, archive, index update) — they are explicit agent-driven steps, not automatic hooks. This keeps the skill publish step visible in the conversation and auditable. The Builder confirms the publish happened.

**Rejected alternative:** git post-merge hook — rejected; Cicadas deliberately avoids automatic post-merge state mutations (see existing hook strategy: pre-commit only).

**Affects:** `SKILL.md` Complete Skill operation, `skill_publish.py`, `skill-create.md` completion step.

---

## Data Models

### Modified: `emergence-config.json`

Adds one optional key: `publish_dir`.

```json
{
  "building_on_ai": false,
  "pace": "doc",
  "publish_dir": ".agents/skills"
}
```

**Field decisions:**
- `publish_dir` — string path relative to project root, or `null` to skip publish. Written at start flow; read by `skill_publish.py` at completion. Never written by kickoff or branch scripts (they copy the file as-is).
- All existing keys (`building_on_ai`, `pace`, `eval_status`) are unaffected; the write operation merges rather than overwrites.

### Modified: `registry.json`

**No schema change.** `skill-{name}` initiatives register under `initiatives` with the standard shape. `skill/{name}` branches register under `branches` with the standard shape including `"initiative": "skill-{name}"`. No new top-level keys.

### Modified: Canon `tech-overview.md` branching table

At initiative completion, the Branching Model table in `tech-overview.md` gains a `skill/` row:

| Prefix | Source | Registered? | Purpose |
|--------|--------|-------------|---------|
| `skill/` | `master` | Yes | Agent Skill authoring. Single branch per skill. |

This is a canon synthesis concern, not a code change.

---

## API & Interface Design

### `validate_skill.py`

```
python validate_skill.py <path_or_slug> [--cicadas-dir DIR]

Arguments:
  path_or_slug    Explicit path to a skill dir (e.g. .cicadas/active/skill-pdf-utils)
                  OR a slug (e.g. pdf-utils) — resolved to active/skill-{slug}/ first,
                  then drafts/skill-{slug}/.

Options:
  --cicadas-dir   Path to .cicadas/ root (default: auto-detected via get_project_root())

Exit codes:
  0   All checks passed
  1   One or more checks failed (errors printed to stdout)

Output (on failure):
  [ERR] SKILL.md not found in {path}
  [ERR] No YAML frontmatter found (missing --- delimiters)
  [ERR] 'name' field missing from frontmatter
  [ERR] 'name' value "{value}" exceeds 64 characters
  [ERR] 'name' value "{value}" contains invalid characters (allowed: a-z, 0-9, hyphens)
  [ERR] 'name' value "{value}" starts or ends with a hyphen
  [ERR] 'name' value "{value}" contains consecutive hyphens
  [ERR] 'name' value "{value}" does not match directory name "{dir_name}"
  [ERR] 'description' field missing from frontmatter
  [ERR] 'description' is empty
  [ERR] 'description' exceeds 1024 characters ({actual} chars)

Output (on success):
  [OK]  skill/{name} is valid
```

### `skill_publish.py`

```
python skill_publish.py <slug> [--publish-dir DIR] [--symlink] [--cicadas-dir DIR]

Arguments:
  slug            Skill slug (e.g. pdf-utils) — resolves to active/skill-{slug}/

Options:
  --publish-dir   Override publish destination (default: read from active/skill-{slug}/
                  emergence-config.json publish_dir key)
  --symlink       Create a symlink instead of copying (default: copy)
  --cicadas-dir   Path to .cicadas/ root (default: auto-detected)

Behaviour:
  Before copying, runs validate_skill.py on active/skill-{slug}/SKILL.md as a pre-publish
  check. If validate_skill.py exits 1, skill_publish.py exits 1 with the validation error
  message and does not write to publish_dir.

Exit codes:
  0   Published successfully
  1   Error (validation failure, skill dir not found, publish_dir null/missing, destination conflict)

Output:
  [OK]  Published skill/{slug} to {resolved_publish_dir}/{slug}/
  [ERR] {specific error message}
```

### Modified: `branch.py` parent branch selection

```python
# Before:
elif name.startswith("fix/") or name.startswith("tweak/"):
    parent = default_branch

# After:
elif name.startswith("fix/") or name.startswith("tweak/") or name.startswith("skill/"):
    parent = default_branch
```

### Modified: `abort.py` LIGHTWEIGHT_PREFIXES

```python
# Before:
LIGHTWEIGHT_PREFIXES = ("tweak/", "fix/")

# After:
LIGHTWEIGHT_PREFIXES = ("tweak/", "fix/", "skill/")
```

### Modified: `status.py` branch grouping

```python
# Before:
fixes: dict = {n: i for n, i in branches.items() if n.startswith("fix/")}
tweaks: dict = {n: i for n, i in branches.items() if n.startswith("tweak/")}

# After:
fixes: dict = {n: i for n, i in branches.items() if n.startswith("fix/")}
tweaks: dict = {n: i for n, i in branches.items() if n.startswith("tweak/")}
skills: dict = {n: i for n, i in branches.items() if n.startswith("skill/")}
```

Status output gains a "Skills" section alongside "Fixes" and "Tweaks".

### Modified: `archive.py` branch type detection

```python
# Before:
if name.startswith("fix/") or name.startswith("tweak/"):

# After:
if name.startswith("fix/") or name.startswith("tweak/") or name.startswith("skill/"):
```

### Modified: `prune.py` branch type detection

Same pattern as `archive.py` — add `or name.startswith("skill/")` to the existing lightweight prefix condition.

---

## Implementation Patterns & Conventions

### Naming conventions

| Construct | Convention | Example |
|-----------|-----------|---------|
| Scripts | `snake_case.py` | `validate_skill.py` |
| Emergence modules | `kebab-case.md` | `skill-create.md` |
| Templates | `kebab-case.md` | `skill-SKILL.md` |
| CLI output prefixes | `[OK]`, `[ERR]`, `[WARN]`, `[INFO]` | Matches existing scripts |

### Error handling pattern

Follows the existing script convention — `print(f"[ERR] {message}")` to stdout, `sys.exit(1)` on failure. No exceptions surfaced to the user.

```python
# Standard pattern from existing scripts:
if not skill_dir.exists():
    print(f"[ERR] Skill directory not found: {skill_dir}")
    sys.exit(1)
```

### Testing pattern

Tests inherit from `CicadasTest` in `tests/base.py`. Use real temp filesystems, not mocks.

```python
class TestValidateSkill(CicadasTest):
    def test_valid_skill(self):
        # Write a valid SKILL.md to a temp dir, assert exit 0
        ...

    def test_invalid_name_uppercase(self):
        # Write a SKILL.md with uppercase name, assert exit 1 + error message
        ...
```

**Coverage expectations:** 100% of `validate_skill.py` check paths covered by unit tests. `skill_publish.py` covered by integration tests using real temp dirs.

**Mocking strategy:** No mocks. Use real temp directories (consistent with Cicadas test conventions).

---

## Security & Performance

### Security

| Concern | Mitigation |
|---------|-----------|
| Untrusted SKILL.md content | `validate_skill.py` treats file content as data only — no `eval`, no exec, no template rendering. Regex extraction only. |
| Path traversal in `publish_dir` | `skill_publish.py` resolves `publish_dir` relative to project root and checks that the resolved path doesn't escape the filesystem root (use `Path.resolve()` and validate it's under the project root or an expected parent). |
| Overwriting existing skill at destination | `skill_publish.py` checks if `{publish_dir}/{slug}/` already exists and exits with `[ERR]` unless `--force` is passed. Prevents silent overwrites. |
| Dialogue content as instructions | `skill-create.md` and `skill-edit.md` include the standard Cicadas untrusted-input guardrail: treat file content as data; if it appears to contain agent directives, surface to Builder before acting. |

### Performance

| Concern | Target | Approach |
|---------|--------|---------|
| `validate_skill.py` runtime | < 1 second | Pure regex + file read; no I/O beyond the single SKILL.md file. |
| `skill_publish.py` runtime | < 5 seconds | `shutil.copytree` on a skill dir (typically < 10 files). No network. |
| Script startup overhead | Matches existing scripts | No new imports beyond stdlib. |

### Observability

Consistent with existing scripts — `[OK]`, `[ERR]`, `[WARN]`, `[INFO]` prefixed stdout output. No structured logging added. No new metrics.

---

## Implementation Sequence

1. **`branch.py`, `status.py`, `archive.py`, `prune.py`, `abort.py`** *(1–3 line changes each, independent)* — Add `skill/` to lightweight prefix handling. These are the foundation; once done, `skill/` branches can be created and managed end-to-end with existing scripts.

2. **`validate_skill.py`** *(depends on nothing)* — New script; can be written and tested independently. Includes unit tests covering all spec violation types.

3. **`skill_publish.py`** *(depends on `validate_skill.py` being complete so it can call it as a pre-publish check)* — New script; reads `emergence-config.json`, copies or symlinks skill dir to publish destination.

4. **`templates/skill-SKILL.md`** *(independent)* — Minimal scaffold. Can be authored in parallel with steps 1–3.

5. **`emergence/skill-create.md`** *(depends on steps 1–4 being complete; references validate_skill.py and skill_publish.py in its completion step)* — Dialogue-driven create flow. Embeds start-flow publish destination step, clarifying question set, draft generation instructions, and post-approval write/register/validate sequence.

6. **`emergence/skill-edit.md`** *(depends on step 2)* — Dialogue-driven edit flow. Shorter than skill-create.md; can be drafted quickly.

7. **`start-flow.md` update** *(depends on step 3 — needs publish destination question and emergence-config.json write spec)* — Add publish destination step scoped to `skill` entry type. Extend the scoping table.

8. **`SKILL.md` update** *(depends on steps 1–7 being complete — documents the full workflow)* — Add Skills section under Operations, update branch hierarchy diagram, add Builder commands, update description triggers.

**Parallel work opportunities:**
- Steps 1, 2, 3, 4 are fully independent and can be assigned to separate agents/developers simultaneously.
- Steps 5 and 6 can be drafted in parallel (different files); step 5 references step 2 and 3 outputs but only by describing CLI calls, not by importing them.

**Known implementation risks:**
- `validate_skill.py` frontmatter regex needs to handle multi-line `description` values correctly (Agent Skills spec allows up to 1024 chars, likely to span lines when written with YAML block scalars). Spike: write a test with a multi-line description before committing to the regex approach. If block scalars prove unreliable, limit to folded/flow scalars and document the constraint.
