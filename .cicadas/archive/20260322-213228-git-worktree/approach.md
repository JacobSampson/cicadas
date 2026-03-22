
# Approach: Git Worktree Support

## Strategy

**Sequential implementation** with two partitions. The foundation (utils.py changes) must be complete before the CLI changes can be built, as both `init.py` and `status.py` depend on the new utility functions.

This is a small, focused initiative — parallelism isn't beneficial here because:
1. The utils.py changes are a prerequisite for everything else.
2. The init.py and status.py changes are small enough to implement sequentially without bottleneck.

## Partitions (Feature Branches)

### Partition 1: Foundation → `feat/worktree-utils`

**Modules**: `scripts/utils.py`, `tests/`
**Scope**: Core path resolution and worktree detection utilities.
**Dependencies**: None

#### Implementation Steps
1. Add `get_cicadas_root()` function — resolves `.cicadas` path following symlinks and handling worktrees.
2. Add `is_worktree()` function — detects if running from a Git worktree.
3. Add `is_cicadas_symlinked()` function — checks if `.cicadas` is a symlink.
4. Add `get_cicadas_symlink_target()` function — returns symlink target if applicable.
5. Add `_get_main_repo_root()` helper — finds main repo root from a worktree.
6. Write comprehensive tests for all new functions covering:
   - Local `.cicadas` (not symlinked)
   - Symlinked `.cicadas`
   - Running from a worktree
   - Running from main repo
   - Edge cases (missing `.cicadas`, broken symlinks)

---

### Partition 2: CLI Integration → `feat/worktree-cli`

**Modules**: `scripts/init.py`, `scripts/status.py`, `tests/`
**Scope**: User-facing CLI changes for symlink setup and status display.
**Dependencies**: Requires Partition 1 (`feat/worktree-utils`)

#### Implementation Steps
1. Extend `init.py` with `--link <path>` argument:
   - Create target directory if missing
   - Initialize `.cicadas` structure in target
   - Create symlink from `.cicadas` to target
   - Add `.cicadas` to `.gitignore`
2. Add `--force` flag to `init.py` for replacing existing `.cicadas`.
3. Update `status.py` to display worktree indicator when running from a worktree.
4. Update `status.py` to display symlink target when `.cicadas` is symlinked.
5. Write tests for init.py --link (success, already exists, force replace).
6. Write tests for status.py indicators.
7. Integration test: init with --link, create worktree, run status from worktree.

---

## Sequencing

Strictly sequential — Partition 2 depends on Partition 1.

```mermaid
graph LR
    P1[feat/worktree-utils] --> P2[feat/worktree-cli]
```

### Partitions DAG

> This block is machine-readable. It drives automatic worktree creation in `branch.py`.
> - `depends_on: []` → partition runs in parallel (gets its own git worktree)
> - `depends_on: [feat/other]` → partition is sequential (plain branch, waits for dependency)

```yaml partitions
- name: feat/worktree-utils
  modules: [scripts/utils.py, tests/]
  depends_on: []

- name: feat/worktree-cli
  modules: [scripts/init.py, scripts/status.py, tests/]
  depends_on: [feat/worktree-utils]
```

## Migrations & Compat

**No migration required.** Existing projects with a regular `.cicadas` directory continue to work unchanged. The new symlink mode is opt-in via `init.py --link`.

**Backward compatibility:**
- All existing scripts continue to work — they use `get_project_root() / ".cicadas"` which follows symlinks automatically via pathlib.
- The new `get_cicadas_root()` function is additive; existing code paths are not modified.
- `registry.json` schema is unchanged.

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Git version incompatibility | `git rev-parse --git-common-dir` requires Git 2.5+. Extend existing `git_version_check()` to cover this; fail fast with clear error message. |
| Windows symlink limitations | Creating symlinks on Windows requires elevated privileges or Developer Mode. Document this limitation; test on macOS/Linux for MVP. |
| Broken symlinks | If symlink target is deleted, scripts will fail. `get_cicadas_root()` should raise clear `FileNotFoundError` with actionable message. |
| Race condition in concurrent writes | Without locking, last-write-wins. Document this as known limitation for MVP; recommend sync hooks (Post-MVP) for team use. |

## Alternatives Considered

**Alternative 1: Git submodule for `.cicadas`**
- Rejected for MVP: Adds complexity (submodule init, update, commit workflow). Symlinks are simpler and cover the primary use case. Submodule support is Post-MVP.

**Alternative 2: Environment variable for `.cicadas` location**
- Rejected: Less discoverable than symlinks; would require setting env var in every terminal. Symlinks are self-documenting (visible in filesystem).

**Alternative 3: Config file pointing to remote storage**
- Rejected: Would require all scripts to read config before accessing `.cicadas`. Symlinks are transparent — no script changes needed for basic operation.

