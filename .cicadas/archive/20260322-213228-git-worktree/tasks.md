
# Tasks: Git Worktree Support

**Mode**: Feature (Vertical Slices)

---

## Partition 1: Foundation → `feat/worktree-utils`

### 1.1 Core Path Resolution

- [ ] Add `_get_main_repo_root()` helper to `utils.py`: Uses `git rev-parse --git-common-dir` to find main repo root from a worktree. Returns `Path | None`. <!-- id: 1 -->
  - **Acceptance**: Function returns correct path when called from worktree; returns `None` when called from main repo or non-git directory.

- [ ] Add `is_worktree()` function to `utils.py`: Returns `True` if current directory is a Git worktree (not main repo). <!-- id: 2 -->
  - **Acceptance**: Returns `True` from worktree, `False` from main repo, `False` from non-git directory.

- [ ] Add `is_cicadas_symlinked()` function to `utils.py`: Returns `True` if `.cicadas` is a symlink. <!-- id: 3 -->
  - **Acceptance**: Returns `True` when `.cicadas` is symlink, `False` when regular directory or missing.

- [ ] Add `get_cicadas_symlink_target()` function to `utils.py`: Returns symlink target path if `.cicadas` is a symlink, else `None`. <!-- id: 4 -->
  - **Acceptance**: Returns resolved `Path` for symlinked `.cicadas`, `None` otherwise.

- [ ] Add `get_cicadas_root()` function to `utils.py`: Returns resolved path to `.cicadas`, following symlinks and handling worktrees. <!-- id: 5 -->
  - **Acceptance**: Returns correct path for: local `.cicadas`, symlinked `.cicadas`, running from worktree. Raises `FileNotFoundError` with clear message if `.cicadas` not found.

### 1.2 Tests for Foundation

- [ ] Create `tests/test_utils_worktree.py` with test class `TestWorktreeUtils`. <!-- id: 6 -->
  - **Acceptance**: File exists, imports pass, inherits from `CicadasTest`.

- [ ] Add test `test_is_worktree_from_main_repo`: Verify `is_worktree()` returns `False` from main repo. <!-- id: 7 -->
  - **Acceptance**: Test passes.

- [ ] Add test `test_is_worktree_from_worktree`: Create a worktree, verify `is_worktree()` returns `True` from it. <!-- id: 8 -->
  - **Acceptance**: Test passes using real git worktree.

- [ ] Add test `test_get_cicadas_root_local`: Verify returns local `.cicadas` path when not symlinked. <!-- id: 9 -->
  - **Acceptance**: Test passes.

- [ ] Add test `test_get_cicadas_root_symlinked`: Create symlinked `.cicadas`, verify returns resolved target. <!-- id: 10 -->
  - **Acceptance**: Test passes using real symlink.

- [ ] Add test `test_get_cicadas_root_from_worktree`: Create worktree, verify `.cicadas` resolves correctly from worktree. <!-- id: 11 -->
  - **Acceptance**: Test passes.

- [ ] Add test `test_get_cicadas_root_not_found`: Verify raises `FileNotFoundError` when `.cicadas` missing. <!-- id: 12 -->
  - **Acceptance**: Test passes, error message is actionable.

- [ ] Run full test suite, verify all tests pass and no regressions. <!-- id: 13 -->
  - **Acceptance**: `python3 -m unittest discover -s tests/` exits 0.

---

## Partition 2: CLI Integration → `feat/worktree-cli`

### 2.1 init.py --link

- [ ] Add `--link <path>` argument to `init.py` argparse. <!-- id: 20 -->
  - **Acceptance**: `python init.py --help` shows `--link` option with description.

- [ ] Add `--force` argument to `init.py` argparse. <!-- id: 21 -->
  - **Acceptance**: `python init.py --help` shows `--force` option.

- [ ] Implement `init_cicadas_link()` function: Creates target dir if missing, initializes structure, creates symlink. <!-- id: 22 -->
  - **Acceptance**: Running `init.py --link /tmp/test-cicadas` creates symlink and initializes target.

- [ ] Add error handling for existing `.cicadas` directory (without `--force`). <!-- id: 23 -->
  - **Acceptance**: Prints error message with `✗` prefix, exits with code 1.

- [ ] Add error handling for existing `.cicadas` symlink (without `--force`). <!-- id: 24 -->
  - **Acceptance**: Prints error showing current target, exits with code 1.

- [ ] Implement `--force` behavior: Remove existing `.cicadas` before creating new symlink. <!-- id: 25 -->
  - **Acceptance**: `init.py --link /new/path --force` replaces existing `.cicadas`.

- [ ] Add `_ensure_gitignore()` helper: Adds `.cicadas` to `.gitignore` if not present. <!-- id: 26 -->
  - **Acceptance**: After `init.py --link`, `.gitignore` contains `.cicadas` entry.

- [ ] Update `config.json` with optional `cicadas_storage` field after `--link`. <!-- id: 27 -->
  - **Acceptance**: `config.json` contains `cicadas_storage: { type: "symlink", target: "..." }`.

### 2.2 status.py Indicators

- [ ] Update `status.py` to detect and display worktree indicator. <!-- id: 30 -->
  - **Acceptance**: Running from worktree shows `(worktree)` in status header.

- [ ] Update `status.py` to detect and display symlink indicator. <!-- id: 31 -->
  - **Acceptance**: When `.cicadas` is symlinked, shows `(.cicadas → /path/to/target)` in header.

- [ ] Handle combined case: worktree + symlinked `.cicadas`. <!-- id: 32 -->
  - **Acceptance**: Shows both indicators: `(worktree, .cicadas → /path)`.

### 2.3 Tests for CLI Integration

- [ ] Create `tests/test_init_link.py` with test class `TestInitLink`. <!-- id: 40 -->
  - **Acceptance**: File exists, imports pass, inherits from `CicadasTest`.

- [ ] Add test `test_init_link_creates_target`: Verify `--link` creates target directory if missing. <!-- id: 41 -->
  - **Acceptance**: Test passes.

- [ ] Add test `test_init_link_creates_symlink`: Verify `.cicadas` is a symlink to target. <!-- id: 42 -->
  - **Acceptance**: Test passes.

- [ ] Add test `test_init_link_initializes_structure`: Verify target contains registry.json, index.json, etc. <!-- id: 43 -->
  - **Acceptance**: Test passes.

- [ ] Add test `test_init_link_adds_gitignore`: Verify `.cicadas` added to `.gitignore`. <!-- id: 44 -->
  - **Acceptance**: Test passes.

- [ ] Add test `test_init_link_error_existing_dir`: Verify error when `.cicadas` dir exists. <!-- id: 45 -->
  - **Acceptance**: Test passes, exit code is 1.

- [ ] Add test `test_init_link_force_replaces`: Verify `--force` replaces existing `.cicadas`. <!-- id: 46 -->
  - **Acceptance**: Test passes.

- [ ] Add test `test_status_worktree_indicator`: Verify status shows worktree indicator. <!-- id: 47 -->
  - **Acceptance**: Test passes.

- [ ] Add test `test_status_symlink_indicator`: Verify status shows symlink indicator. <!-- id: 48 -->
  - **Acceptance**: Test passes.

### 2.4 Integration Test

- [ ] Add integration test: Full workflow — init with --link, create worktree, run status from worktree, verify shared state. <!-- id: 50 -->
  - **Acceptance**: Test creates symlinked `.cicadas`, creates git worktree, runs `status.py` from worktree, verifies registry is shared.

- [ ] Run full test suite, verify all tests pass and no regressions. <!-- id: 51 -->
  - **Acceptance**: `python3 -m unittest discover -s tests/` exits 0.

---

## Final Steps

- [ ] Update documentation: Add worktree setup instructions to HOW-TO.md. <!-- id: 60 -->
  - **Acceptance**: HOW-TO.md contains section on worktree/symlink setup.

- [ ] Run linter and fix any issues: `ruff check src/ tests/`. <!-- id: 61 -->
  - **Acceptance**: Linter passes with no errors.

- [ ] Run coverage report, verify 80%+ on new code. <!-- id: 62 -->
  - **Acceptance**: `python3 -m coverage report` shows ≥80% for `utils.py` and `init.py`.

