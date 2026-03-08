
---
next_section: 'Overview & Context'
---

# Tech Design: Worktrees for Parallel Execution

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

This initiative extends the Cicadas Python CLI scripts to support `git worktree` as the execution substrate for parallel feature partitions. The design is purely additive: existing sequential workflows are unchanged, and all new logic is introduced behind the DAG check (`depends_on: []` in `approach.md`). No new commands are introduced; the worktree lifecycle is embedded inside existing scripts (`branch.py`, `archive.py`, `prune.py`, `abort.py`) via shared utility functions added to `utils.py`.

The central design pattern is: **parse intent, then act**. `branch.py` reads the `partitions` block from the active `approach.md`, decides worktree vs. plain branch based on `depends_on`, acts, and writes result to `registry.json`. All downstream scripts (`archive.py`, `prune.py`, `abort.py`) read `worktree_path` from the registry and remove the worktree if present before deregistering. `kickoff.py` reads the same `partitions` block after promotion to detect parallelism and invoke `check.py` proactively.

### Cross-Cutting Concerns

1. **Atomicity of registry writes** — `registry.json` must only be written after all git operations succeed. If `git worktree add` fails, `registry.json` must not be modified. Follow the existing pattern: all git ops first, then `save_json`.
2. **Graceful degradation** — Missing `approach.md`, missing `partitions` block, or missing `worktree_path` in registry must all result in silent fallback to current behavior (plain branches), never a crash.
3. **Idempotency** — All worktree operations must be safe to re-run: already-exists is `[INFO]`, already-gone is `[WARN]` + continue.
4. **Path portability** — All path construction uses `pathlib.Path` throughout (existing convention). Absolute paths are used for worktree directories.
5. **Git version guard** — Check `git worktree` availability (git ≥ 2.5) once, in `utils.py`, before any worktree operation.

### Brownfield Notes

- **Must not change**: `registry.json` schema for fields other than the new `worktree_path` on branch entries. `utils.py` functions (`get_project_root`, `load_json`, `save_json`, `get_default_branch`) are extended, not replaced.
- **Existing patterns to follow**: All scripts use `get_project_root()` for root detection, `load_json`/`save_json` for registry I/O, and `subprocess.run`/`check_output` for git. New code follows the same pattern.
- **`check.py` is context-sensitive** — currently reads `git branch --show-current` to scope its check. The new pre-execution mode (called by `kickoff.py`) must work with a supplied initiative name rather than the current branch, requiring a `check_conflicts(initiative_name=None)` signature change.

---

## Tech Stack & Dependencies

| Category | Selection | Rationale |
|----------|-----------|-----------|
| **Language/Runtime** | Python 3.11+ | Existing codebase requirement |
| **Git interface** | `subprocess` + `git` CLI | Existing convention; avoids `gitpython` dependency |
| **Markdown parsing** | `re` (regex, stdlib) | DAG block is a fenced YAML block; `re` is sufficient and adds no dependency |
| **YAML parsing** | `tomllib` / `PyYAML` / `re` | See ADR-3 |
| **Testing** | `unittest` + real temp git repos | Existing test convention (no mocks, real filesystem) |

**New dependencies introduced:** None (stdlib only, or PyYAML if ADR-3 resolves to it — see ADR-3).

**Dependencies explicitly rejected:**
- `gitpython` — not in existing stack; heavy dependency for what is purely subprocess calls.
- `rich` — terminal formatting library; not required for this initiative's output (plain prefix-based format).

---

## Project / Module Structure

Only changed/new files shown:

```
src/cicadas/
├── scripts/
│   ├── utils.py            # [MODIFIED] add: worktree_path(), create_worktree(), remove_worktree(),
│   │                       #            parse_partitions_dag(), git_version_check()
│   ├── branch.py           # [MODIFIED] DAG lookup → decide worktree vs plain; write worktree_path to registry;
│   │                       #            write context.md to worktree root
│   ├── kickoff.py          # [MODIFIED] after draft promotion: parse partitions, if any parallel → call check_conflicts()
│   ├── check.py            # [MODIFIED] accept optional initiative_name arg for pre-execution mode;
│   │                       #            add stale-worktree detection
│   ├── archive.py          # [MODIFIED] before deregistering: call remove_worktree() if worktree_path set
│   ├── prune.py            # [MODIFIED] same as archive.py
│   └── abort.py            # [MODIFIED] same as archive.py
└── templates/
    └── approach.md         # [MODIFIED] add partitions block schema + example

.cicadas/
└── active/{initiative}/
    └── approach.md         # [MODIFIED at runtime] populated with partitions block by emergence agent

{worktree-root}/
└── context.md              # [NEW, ephemeral] written by branch.py; not committed
```

**Key structural decisions:**
- Worktree logic is not a new script — it lives in `utils.py` as shared functions and is called from existing scripts. This keeps the CLI surface identical.
- DAG parsing is isolated in `parse_partitions_dag(approach_path)` in `utils.py` — all scripts that need the DAG call this one function.
- `context.md` is written to the worktree root (not inside `.cicadas/`) so agents landing in the worktree directory see it immediately.

---

## Architecture Decisions (ADRs)

### ADR-1: Embed worktree logic in existing scripts, not a new `worktree.py`

**Decision:** Worktree creation is triggered by `branch.py`, not a dedicated script. Teardown is triggered by `archive.py`, `prune.py`, and `abort.py`. Shared low-level functions live in `utils.py`.

**Rationale:** The Builder already knows `branch.py` is the command to start a feature. Introducing `worktree.py` as a separate command requires learning a new invocation order and risks the registry falling out of sync (someone runs `branch.py` without `worktree.py`). Embedding the decision inside `branch.py` is the only way to guarantee consistency.

**Alternatives rejected:** Standalone `worktree.py` — requires the Builder to run two commands per parallel partition; violates "zero new concepts" goal.

**Affects:** `branch.py`, `archive.py`, `prune.py`, `abort.py`, `utils.py`

---

### ADR-2: DAG stored as fenced YAML block in `approach.md`

**Decision:** The `partitions` block in `approach.md` is a fenced code block with language tag `yaml`:

~~~markdown
```yaml partitions
- name: feat/api
  modules: [api, gateway]
  depends_on: []
- name: feat/integration
  modules: [integration]
  depends_on: [feat/api, feat/ui]
```
~~~

Parsed by `parse_partitions_dag()` using `re` to extract the block, then `PyYAML` (or stdlib `tomllib` equivalent — see ADR-3) to parse the YAML.

**Rationale:** Fenced code block is human-readable (renders on GitHub), machine-parseable with a simple regex extraction, and fits the existing `approach.md` markdown convention. A pure markdown table would require a bespoke parser for no benefit.

**Alternatives rejected:** JSON block — less human-readable; TOML — unfamiliar to most Markdown authors; pure prose — unparseable.

**Consequences:** The `approach.md` template must document the exact format with an example. The emergence agent instructions (`emergence/approach.md`) must be updated to instruct the agent to populate this block.

**Affects:** `utils.py` (`parse_partitions_dag`), `approach.md` template, `emergence/approach.md` subagent prompt

---

### ADR-3: Use PyYAML for YAML parsing (accept the dependency)

**Decision:** Add `PyYAML` as a dependency for parsing the `partitions` block. Do not use `re`-only parsing for the YAML content (only `re` for block extraction).

**Rationale:** The `partitions` block contains nested structures (lists of objects). Hand-rolling a parser for YAML lists-of-dicts is fragile and untestable. `PyYAML` is a near-universal Python dependency with no transitive deps. The risk of adding it is extremely low; the risk of not adding it (bespoke parser bugs) is real.

**Alternatives rejected:** `tomllib` (stdlib in 3.11+) — TOML syntax is not YAML; we'd need to change the format. Regex-only — works for simple cases but fails on multiline strings, quoted values, etc.

**Affects:** `utils.py`, `pyproject.toml` (add `pyyaml`)

---

### ADR-4: Worktree path convention — sibling of repo root

**Decision:** Worktree path = `{repo_root.parent}/{repo_root.name}-{branch_slug}` where `branch_slug` replaces `/` with `-` and `_` with `-`.

Example: repo at `/home/dan/cicadas`, branch `feat/api` → worktree at `/home/dan/cicadas-feat-api`.

**Rationale:** Sibling placement keeps all work near the main repo without polluting the repo tree itself. The slug transformation is deterministic and reversible. Using the repo name as a prefix prevents collisions with unrelated sibling directories.

**Override:** `branch.py` accepts `--worktree-dir {path}` to override the default. This is recorded as-is in `registry.json`.

**Affects:** `utils.py` (`worktree_path()`), `branch.py`

---

### ADR-5: `check.py` gains an initiative-scoped pre-execution mode

**Decision:** `check_conflicts()` signature changes to `check_conflicts(initiative_name: str | None = None) -> bool`. When `initiative_name` is provided, the function checks conflicts across all branches registered to that initiative (not just the current git branch). It returns `True` if conflicts exist.

**Rationale:** `kickoff.py` needs to call `check.py` before any branch exists — it can't rely on `git branch --show-current`. The cleanest approach is to parameterize the scope rather than duplicate logic.

**Backward compatibility:** Called with no arguments from the CLI (`check.py` as before), behavior is identical to today.

**Affects:** `check.py`, `kickoff.py`

---

### ADR-6: `context.md` is ephemeral and not committed

**Decision:** `context.md` is written to the worktree root by `branch.py` but added to `.gitignore` in the worktree (or already covered by the repo's `.gitignore`). It is never committed. It is regenerated fresh each time `branch.py` creates the worktree.

**Rationale:** `context.md` is a runtime artifact for agent consumption. Committing it would create a permanent, stale document that diverges from canon. Fresh generation on worktree creation ensures the context reflects the current canon state.

**Consequence:** If a developer manually deletes `context.md`, re-running `branch.py` (idempotent) will regenerate it.

**Affects:** `branch.py`, `.gitignore` (add `context.md` rule if not already excluded)

---

## Data Models

### Modified Models

The only data model change is additive to `registry.json`'s branch entries:

**Before:**
```json
{
  "branches": {
    "feat/api": {
      "intent": "...",
      "modules": ["api", "gateway"],
      "owner": "unknown",
      "initiative": "worktrees-parallel-execution",
      "created_at": "2026-03-07T19:00:00Z"
    }
  }
}
```

**After (additive):**
```json
{
  "branches": {
    "feat/api": {
      "intent": "...",
      "modules": ["api", "gateway"],
      "owner": "unknown",
      "initiative": "worktrees-parallel-execution",
      "created_at": "2026-03-07T19:00:00Z",
      "worktree_path": "/home/dan/cicadas-feat-api"
    }
  }
}
```

| Field | Type | Change | Notes |
|-------|------|--------|-------|
| `worktree_path` | `str \| null` | Added | Absent = no worktree. Set by `branch.py`, cleared on teardown. |

**Migration required?** No. Existing entries without `worktree_path` are treated as `null` (no worktree) by all scripts.

---

## API & Interface Design

### New utility functions in `utils.py`

```python
def git_version_check() -> None:
    """Raise RuntimeError if git < 2.5 (worktree support requires 2.5+)."""

def worktree_path(repo_root: Path, branch_name: str) -> Path:
    """Compute default worktree path: sibling dir named {repo}-{branch-slug}."""

def parse_partitions_dag(approach_path: Path) -> list[dict]:
    """
    Parse the ```yaml partitions block from approach.md.
    Returns list of dicts: [{name, modules, depends_on}, ...].
    Returns [] if block is absent or approach.md doesn't exist.
    Never raises — graceful degradation to empty list.
    """

def create_worktree(repo_root: Path, branch_name: str, worktree_dir: Path) -> Path:
    """
    Run `git worktree add {worktree_dir} {branch_name}`.
    Returns the absolute worktree path.
    Raises subprocess.CalledProcessError on git failure (caller handles; does NOT write registry).
    Idempotent: if worktree_dir already exists and is a valid worktree, returns path without re-creating.
    """

def remove_worktree(repo_root: Path, worktree_dir: Path, force: bool = False) -> None:
    """
    Run `git worktree remove [--force] {worktree_dir}`.
    If worktree_dir does not exist: logs [WARN] and returns (does not raise).
    If uncommitted changes and not force: raises WorktreeDirtyError (caller handles).
    """

class WorktreeDirtyError(Exception):
    """Raised when remove_worktree finds uncommitted changes without --force."""
```

### Modified CLI signatures

**`branch.py`** — no new required args; one new optional arg:
```
python branch.py {branch-name} --intent "..." --modules "..." --initiative {name}
                 [--worktree-dir {path}]   # override default worktree location
                 [--no-worktree]           # force plain branch even if depends_on is empty
```

**`check.py`** — no change to CLI; internal signature changes:
```python
# Internal: check_conflicts(initiative_name: str | None = None) -> bool
# CLI: python check.py  (unchanged — initiative_name=None = current-branch mode)
```

**`archive.py`, `prune.py`, `abort.py`** — new `--force` flag for dirty-worktree teardown:
```
python archive.py {name} --type branch [--force]
python prune.py {name} --type branch [--force]
python abort.py [--force]
```

### Backward Compatibility

All existing CLI invocations remain valid. No arguments are removed or made newly required. Scripts that receive no `worktree_path` in registry simply skip the worktree teardown path.

---

## Implementation Patterns & Conventions

### Naming Conventions

Follows existing Cicadas conventions:

| Construct | Convention | Example |
|-----------|-----------|---------|
| Functions | `snake_case` | `create_worktree()`, `parse_partitions_dag()` |
| Classes | `PascalCase` | `WorktreeDirtyError` |
| CLI args | `--kebab-case` | `--worktree-dir`, `--no-worktree` |
| Output prefixes | `[OK]`, `[INFO]`, `[WARN]`, `[ERR]` padded to 6 chars | `[OK]   Worktree created: ...` |

### Error Handling Pattern

```python
# Worktree operations: git failure → print [ERR], exit non-zero, no registry write
try:
    wt_path = create_worktree(root, name, target_dir)
except subprocess.CalledProcessError as e:
    print(f"[ERR]  git worktree add failed: {e}")
    sys.exit(1)

# Teardown: dirty worktree → warn, exit non-zero unless --force
try:
    remove_worktree(root, Path(worktree_path), force=args.force)
except WorktreeDirtyError:
    print(f"[WARN] Worktree has uncommitted changes: {worktree_path}")
    print("[WARN] Use --force to remove anyway, or commit/stash changes first.")
    sys.exit(1)
```

**Rules:**
- Git operations always come before registry writes. If git fails, no registry state is mutated.
- `remove_worktree()` never raises on missing directory — it warns and continues.
- `parse_partitions_dag()` never raises — returns `[]` on any parse failure.

### Testing Pattern

Follows existing test convention: real temp git repos, no mocks, `unittest.TestCase`.

```python
class TestWorktreeCreation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        # init git repo, create branch, etc.

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_parallel_partition_gets_worktree(self):
        # write approach.md with depends_on: []
        # call create_branch(...)
        # assert worktree dir exists
        # assert registry has worktree_path
```

**Coverage expectations:** All new utility functions in `utils.py` are unit-tested. `branch.py`, `archive.py` integration paths tested end-to-end with real git repos.
**Mocking strategy:** No mocks. Real subprocess calls against temp git repos.

---

## Security & Performance

### Security

| Concern | Mitigation |
|---------|-----------|
| Path traversal via branch name | `worktree_path()` uses `pathlib.Path` construction — no shell interpolation; branch slug is sanitized (only alphanum + `-`) |
| Shell injection in branch names | All subprocess calls use list form `[cmd, arg, ...]`, never `shell=True` |
| Uncommitted changes silently lost | `remove_worktree` requires `--force` if dirty; never silent data loss |

### Performance

| Concern | Target | Approach |
|---------|--------|---------|
| `branch.py` end-to-end (with worktree) | < 5 seconds | `git worktree add` is local-only; no network |
| `status.py` with 3 worktrees | < 3 seconds | 2 subprocess calls per worktree (`status --porcelain`, `log -1`); synchronous is fine at this scale |
| `parse_partitions_dag()` | < 50ms | Single file read + regex + YAML parse; no I/O beyond `approach.md` |

### Observability

- **Logs (printed):** Every worktree creation/removal prints `[OK]`/`[WARN]`/`[ERR]` lines with the absolute path.
- **No new metrics or traces** — this is a local CLI tool.

---

## Implementation Sequence

1. **Foundation — `utils.py` extensions** *(blocking all other work)*
   - `git_version_check()`
   - `worktree_path()`
   - `parse_partitions_dag()` + unit tests
   - `create_worktree()` + `remove_worktree()` + `WorktreeDirtyError` + unit tests

2. **Registry data model** *(depends on 1, blocking branch.py)*
   - Confirm `worktree_path` field is read/write via `load_json`/`save_json` (no schema migration needed — additive)

3. **`branch.py` worktree integration** *(depends on 1–2)*
   - Read `partitions` block, decide worktree vs plain
   - Call `create_worktree()`, write `worktree_path` to registry
   - Write `context.md` to worktree root
   - Add `--worktree-dir` and `--no-worktree` args
   - Tests: parallel partition → worktree created; sequential → plain branch; already-exists → idempotent; git failure → no registry write

4. **`kickoff.py` pre-execution check** *(depends on 1)*
   - Parse `partitions` from promoted `approach.md`
   - If any `depends_on: []`, call `check_conflicts(initiative_name=name)`
   - Tests: parallel detected → check runs; all sequential → check skipped

5. **`check.py` initiative-scoped mode** *(depends on 1, parallel with 3–4)*
   - Add `initiative_name` param, stale-worktree detection
   - Tests: initiative-scoped check finds conflicts; stale worktree flagged

6. **Teardown — `archive.py`, `prune.py`, `abort.py`** *(depends on 1–2)*
   - Call `remove_worktree()` before deregistering if `worktree_path` is set
   - Add `--force` arg
   - Tests: clean worktree → removed; dirty worktree → blocked without --force; missing path → warn + continue

7. **`status.py` Worktrees section** *(depends on 1–2, parallel with 6)*
   - Render worktrees table; `[MISSING]` for gone paths
   - Tests: 0 worktrees → section absent; 1 clean + 1 missing → both render correctly

8. **Templates & emergence instructions** *(parallel with 3–7)*
   - Update `approach.md` template with `partitions` block and example
   - Update `emergence/approach.md` subagent instructions to populate the block
   - Add `pyyaml` to `pyproject.toml`

9. **`.gitignore` update** *(parallel with all)*
   - Add `context.md` to root `.gitignore`

**Parallel work opportunities:**
- Steps 3, 5, 6, 7 can all proceed in parallel once step 1 is complete.
- Step 8 is independent of all code changes — can be authored any time.

**Known implementation risks:**
- `parse_partitions_dag()`: the regex must handle the exact fence syntax the emergence agent produces. A spike to validate the regex against a real emergence output is recommended before finalizing the implementation.
