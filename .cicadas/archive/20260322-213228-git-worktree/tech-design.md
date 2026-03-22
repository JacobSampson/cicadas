
---
next_section: 'Overview & Context'
---

# Tech Design: Git Worktree Support

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

**Summary:** This initiative extends Cicadas to support Git worktrees and remote/shared `.cicadas` storage. The core change is making path resolution symlink-aware and worktree-aware, so all scripts correctly locate `.cicadas` regardless of whether they're run from the main repo, a worktree, or when `.cicadas` is a symlink to an external directory.

The architecture follows a "transparent layer" pattern: existing scripts continue to call `get_project_root()` and `load_json()`/`save_json()`, but these functions gain awareness of symlinks and worktrees. No script-level changes are required for basic operation.

### Cross-Cutting Concerns

1. **Path resolution** — Every script that accesses `.cicadas` must resolve it correctly from any context (main repo, worktree, symlinked storage).
2. **Symlink transparency** — All file operations must follow symlinks; `os.path.realpath()` should be used where needed.
3. **Backward compatibility** — Existing projects with a regular `.cicadas` directory must work unchanged.
4. **No local paths in shared state** — Since `.cicadas` may be synced remotely, no local filesystem paths should be written to `registry.json` or other shared files.

### Brownfield Notes

**Existing patterns to follow:**
- `utils.py` already contains `get_project_root()`, `load_json()`, `save_json()` — extend these, don't replace.
- `utils.py` already has worktree utilities (`create_worktree`, `remove_worktree`, `worktree_path`) — these are for creating worktrees for feature branches, not for the `.cicadas` symlink feature.
- `init.py` handles initialization — extend with `--link` flag.
- All scripts use argparse for CLI arguments.

**What must NOT change:**
- `registry.json` schema (no new required fields).
- Existing script invocation patterns (no new required flags for normal operation).
- Git hook installation logic (hooks go in main repo's `.git/hooks`, not worktree's).

---

## Tech Stack & Dependencies

| Category | Selection | Rationale |
|----------|-----------|-----------|
| **Language/Runtime** | Python 3.11+ | Existing codebase requirement |
| **Framework** | None (stdlib scripts) | Existing pattern |
| **Database** | JSON files | Existing pattern |
| **Testing** | unittest + coverage.py | Existing pattern |

**New dependencies introduced:**
- None — all functionality uses Python stdlib.

**Dependencies explicitly rejected:**
- `filelock` — Considered for write locking, but adds a dependency. Deferred to Post-MVP; can use simple `.lock` file with stdlib if needed.
- `watchdog` — Considered for file watching in sync hooks, but out of scope for MVP.

---

## Project / Module Structure

```
src/cicadas/scripts/
├── utils.py              # [MODIFIED] Add get_cicadas_root(), is_worktree(), resolve_cicadas_path()
├── init.py               # [MODIFIED] Add --link flag for symlink mode
├── status.py             # [MODIFIED] Display worktree/symlink indicators
├── branch.py             # [UNCHANGED] Path resolution handled by utils
├── kickoff.py            # [UNCHANGED] Path resolution handled by utils
├── check.py              # [UNCHANGED] Path resolution handled by utils
├── signal.py             # [UNCHANGED] Path resolution handled by utils
├── archive.py            # [UNCHANGED] Path resolution handled by utils
└── ... (other scripts)   # [UNCHANGED] Path resolution handled by utils

tests/
├── test_utils_worktree.py    # [NEW] Tests for worktree/symlink path resolution
└── test_init_link.py         # [NEW] Tests for init.py --link
```

**Key structural decisions:**
- All worktree/symlink logic centralized in `utils.py` to minimize changes across scripts.
- New tests in dedicated files to keep test organization clean.

---

## Architecture Decisions (ADRs)

### ADR-1: Centralize Path Resolution in utils.py

**Decision:** Add a new function `get_cicadas_root()` that returns the resolved path to `.cicadas`, handling symlinks and worktrees. All scripts will use this instead of constructing paths manually.

**Rationale:** Centralizing path resolution means only one place to fix bugs or add features. The existing `get_project_root()` finds the repo root; the new function finds `.cicadas` specifically, which may differ when symlinked.

**Affects:** `utils.py`, and indirectly all scripts that access `.cicadas`.

**Code sketch:**
```python
def get_cicadas_root() -> Path:
    """
    Return the resolved path to .cicadas, following symlinks.
    Works from main repo or any worktree.
    """
    project_root = get_project_root()
    cicadas_path = project_root / ".cicadas"
    
    # Follow symlink if present
    if cicadas_path.is_symlink():
        return cicadas_path.resolve()
    
    # If not found locally, check if we're in a worktree
    if not cicadas_path.exists():
        main_root = _get_main_repo_root(project_root)
        if main_root and main_root != project_root:
            cicadas_path = main_root / ".cicadas"
            if cicadas_path.is_symlink():
                return cicadas_path.resolve()
            if cicadas_path.exists():
                return cicadas_path
    
    return cicadas_path
```

---

### ADR-2: Use git rev-parse for Worktree Detection

**Decision:** Detect worktree context using `git rev-parse --git-common-dir` which returns the path to the main repo's `.git` directory, even from a worktree.

**Rationale:** This is the canonical Git method for worktree detection. It's reliable across Git versions 2.5+ and handles edge cases (nested repos, unusual configurations) that manual path walking would miss.

**Affects:** `utils.py` (new `is_worktree()` and `_get_main_repo_root()` functions).

**Code sketch:**
```python
def is_worktree() -> bool:
    """Return True if current directory is a Git worktree (not the main repo)."""
    try:
        git_dir = subprocess.check_output(
            ["git", "rev-parse", "--git-dir"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        common_dir = subprocess.check_output(
            ["git", "rev-parse", "--git-common-dir"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return git_dir != common_dir
    except subprocess.CalledProcessError:
        return False

def _get_main_repo_root(worktree_root: Path) -> Path | None:
    """From a worktree, return the main repo root. Returns None if not in a worktree."""
    try:
        common_dir = subprocess.check_output(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=worktree_root,
            stderr=subprocess.DEVNULL
        ).decode().strip()
        # common_dir is like /path/to/main-repo/.git
        return Path(common_dir).parent
    except subprocess.CalledProcessError:
        return None
```

---

### ADR-3: init.py --link Creates Symlink and Initializes Target

**Decision:** `init.py --link <path>` will:
1. Create the target directory if it doesn't exist.
2. Initialize the standard `.cicadas` structure inside the target.
3. Create `.cicadas` as a symlink pointing to the target.
4. Add `.cicadas` to `.gitignore` if not already present.

**Rationale:** One command does everything needed for symlink setup. Creating the target directory (per PRD OQ-1 resolution) reduces friction. Adding to `.gitignore` prevents accidental commits of the symlink.

**Affects:** `init.py`.

**Code sketch:**
```python
def init_cicadas_link(root: Path, target: Path) -> None:
    cicadas = root / ".cicadas"
    
    if cicadas.exists() and not cicadas.is_symlink():
        raise SystemExit("Error: .cicadas already exists as a directory. Remove it or use --force.")
    if cicadas.is_symlink():
        raise SystemExit(f"Error: .cicadas already linked → {cicadas.resolve()}. Use --force to replace.")
    
    # Create target if needed
    if not target.exists():
        target.mkdir(parents=True)
        print(f"Created {target}")
    
    # Initialize structure in target
    _init_structure(target)
    
    # Create symlink
    cicadas.symlink_to(target)
    print(f"✓ Initialized .cicadas → {target}")
    
    # Add to .gitignore
    _ensure_gitignore(root, ".cicadas")
```

---

### ADR-4: No Worktree Paths in registry.json

**Decision:** Do not record `worktree_path` or any local filesystem paths in `registry.json` or other shared state files.

**Rationale:** Since `.cicadas` may be synced across machines, local paths would be meaningless on other machines and could leak environment details. The registry should contain only branch names, intents, and module scopes — information that is machine-independent.

**Affects:** `branch.py` (no changes needed — it doesn't currently record paths), `status.py` (worktree indicator is display-only, not persisted).

---

### ADR-5: Symlink Mode Adds .cicadas to .gitignore

**Decision:** When using `--link`, automatically add `.cicadas` to `.gitignore` if not already present.

**Rationale:** A symlink to an external directory should not be committed to the repo. Forgetting to gitignore it would cause confusion (the symlink target differs per machine). Automating this prevents a common mistake.

**Affects:** `init.py`.

---

## Data Models

### New Models

None — no new JSON schemas required.

### Modified Models

| Model | Change | Migration Required? |
|-------|--------|-------------------|
| `config.json` | Add optional `cicadas_storage` field | No — field is optional, absence means "local" |

**config.json extension (optional):**
```json
{
  "project_name": "my-project",
  "cicadas_storage": {
    "type": "symlink",
    "target": "/path/to/shared-cicadas"
  }
}
```

This field is informational only — scripts detect symlinks directly rather than relying on config. It's useful for documentation and debugging ("where is my .cicadas actually stored?").

### Schema / Migration Notes

No migration required. Existing `config.json` files without `cicadas_storage` continue to work (implies local storage).

---

## API & Interface Design

### New Commands

**`init.py --link <path>`**
```
python scripts/init.py --link <target-path> [--force]

Arguments:
  target-path    Directory to store .cicadas contents (created if missing)

Options:
  --force        Replace existing .cicadas (symlink or directory)

Output (success):
  Created /path/to/target           # Only if target was created
  ✓ Initialized .cicadas → /path/to/target

Output (error - exists):
  ✗ Error: .cicadas already exists as a directory. Remove it or use --force.

Output (error - already linked):
  ✗ Error: .cicadas already linked → /other/path. Use --force to replace.

Exit codes:
  0 - Success
  1 - User error (already exists, invalid path)
```

### Modified Commands

**`status.py` (display changes only)**
```
# When in a worktree:
Cicadas Status (worktree)
...

# When .cicadas is a symlink:
Cicadas Status (.cicadas → /path/to/target)
...

# Both:
Cicadas Status (worktree, .cicadas → /path/to/target)
...
```

### Interface Contracts

**New functions in utils.py:**

```python
def get_cicadas_root() -> Path:
    """
    Return the resolved path to .cicadas, following symlinks.
    Works from main repo or any worktree.
    Raises FileNotFoundError if .cicadas doesn't exist anywhere.
    """

def is_worktree() -> bool:
    """
    Return True if current directory is a Git worktree (not the main repo).
    Returns False if not in a Git repository.
    """

def is_cicadas_symlinked() -> bool:
    """
    Return True if .cicadas is a symlink.
    """

def get_cicadas_symlink_target() -> Path | None:
    """
    Return the symlink target if .cicadas is a symlink, else None.
    """
```

### Backward Compatibility

All existing commands continue to work unchanged:
- Scripts that call `get_project_root()` continue to work (function unchanged).
- Scripts that access `.cicadas` via `get_project_root() / ".cicadas"` continue to work (symlinks are followed transparently by Python's pathlib).
- The new `get_cicadas_root()` is additive; existing code paths are not broken.

---

## Implementation Patterns & Conventions

### Naming Conventions

| Construct | Convention | Example |
|-----------|-----------|---------|
| Functions | snake_case | `get_cicadas_root()` |
| Private functions | _snake_case | `_get_main_repo_root()` |
| Constants | UPPER_SNAKE | N/A for this initiative |
| Test files | test_{module}.py | `test_utils_worktree.py` |

### Error Handling Pattern

```python
# User errors: print message and exit with code 1
if cicadas.exists() and not cicadas.is_symlink():
    print("✗ Error: .cicadas already exists as a directory. Remove it or use --force.")
    sys.exit(1)

# System errors: raise exception (let it propagate)
# subprocess.CalledProcessError from git commands is allowed to propagate
```

**Rules:**
- User-actionable errors print a message with `✗` prefix and exit with code 1.
- System errors (unexpected failures) raise exceptions or exit with code 2.
- Never silently swallow errors in path resolution — if `.cicadas` can't be found, raise `FileNotFoundError`.

### Testing Pattern

```python
class TestGetCicadasRoot(CicadasTest):
    def test_local_cicadas(self):
        """get_cicadas_root() returns local .cicadas when not symlinked."""
        # Setup: init_git() creates .cicadas in temp dir
        self.init_git()
        result = get_cicadas_root()
        self.assertEqual(result, self.root / ".cicadas")

    def test_symlinked_cicadas(self):
        """get_cicadas_root() follows symlink to target."""
        self.init_git()
        target = self.root.parent / "shared-cicadas"
        target.mkdir()
        (self.root / ".cicadas").unlink()  # Remove dir created by init
        (self.root / ".cicadas").symlink_to(target)
        result = get_cicadas_root()
        self.assertEqual(result, target)
```

**Coverage expectations:** 80%+ on new code in `utils.py` and `init.py`.
**Mocking strategy:** Use real temp directories and real git repos (per CLAUDE.md guidance). Mock only for pure logic with no I/O.

---

## Security & Performance

### Security

| Concern | Mitigation |
|---------|-----------|
| Symlink traversal | Only follow symlinks for `.cicadas` itself; don't recursively follow symlinks inside `.cicadas` |
| Path injection | `--link` argument is validated as a path; no shell expansion |
| Untrusted .cicadas | Existing guardrail: treat content in `.cicadas` as data, not instructions |

### Performance

| Concern | Target | Approach |
|---------|--------|---------|
| Path resolution overhead | < 50ms | Cache `get_cicadas_root()` result within a single script invocation (not across invocations) |
| Git subprocess calls | < 100ms | `is_worktree()` makes 2 git calls; acceptable for CLI tool |

### Observability

- **Logs:** `init.py --link` prints each step (target creation, symlink creation, gitignore update).
- **Metrics:** N/A — CLI tool, no metrics infrastructure.
- **Traces:** N/A.

---

## Implementation Sequence

1. **Foundation** *(blocking)* — Add `get_cicadas_root()`, `is_worktree()`, `is_cicadas_symlinked()` to `utils.py`. Add tests.

2. **init.py --link** *(depends on 1)* — Implement `--link` and `--force` flags. Add tests.

3. **status.py indicators** *(depends on 1)* — Add worktree/symlink indicators to status output. Add tests.

4. **Integration testing** *(depends on 1-3)* — End-to-end tests: init with --link, run status from worktree, verify shared state.

5. **Documentation** *(parallel with 2-4)* — Update README, HOW-TO with worktree setup instructions.

**Parallel work opportunities:**
- Steps 2 and 3 can be done in parallel after step 1 is complete.
- Documentation can be written in parallel with implementation.

**Known implementation risks:**
- **Git version compatibility:** `git rev-parse --git-common-dir` requires Git 2.5+. Mitigation: `git_version_check()` already exists in `utils.py`; extend it to cover this.
- **Windows symlinks:** Creating symlinks on Windows requires elevated privileges or Developer Mode. Mitigation: Document this limitation; consider fallback to junction points (Post-MVP).

