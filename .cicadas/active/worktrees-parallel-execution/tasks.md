
# Tasks: Worktrees for Parallel Execution

> Tasks are grouped by partition / feature branch. Each partition maps to one `feat/` branch.
> Partitions 1 & 4 can start immediately (parallel). Partitions 2 & 3 begin after Partition 1 merges.

---

## Partition 1: Foundation Utilities (`feat/worktree-utils`)

### Setup
- [x] Add `pyyaml` to `pyproject.toml` dependencies <!-- id: 1 -->

### `utils.py` — New Functions
- [x] Implement `git_version_check()`: run `git --version`, parse major.minor, raise `RuntimeError` with install guidance if < 2.5 <!-- id: 2 -->
- [x] Implement `worktree_path(repo_root: Path, branch_name: str) -> Path`: replace `/` with `-` in branch slug, return `repo_root.parent / f"{repo_root.name}-{slug}"` <!-- id: 3 -->
- [x] Implement `parse_partitions_dag(approach_path: Path) -> list[dict]`: regex-extract fenced ` ```yaml partitions ` block, parse with PyYAML, return `[]` on any error/absence; never raise <!-- id: 4 -->
- [x] Define `WorktreeDirtyError(Exception)` <!-- id: 5 -->
- [x] Implement `create_worktree(repo_root, branch_name, worktree_dir) -> Path`: check if `worktree_dir` already exists and is a valid worktree (idempotent); run `git worktree add {worktree_dir} {branch_name}`; return absolute path; raise `subprocess.CalledProcessError` on failure without touching registry <!-- id: 6 -->
- [x] Implement `remove_worktree(repo_root, worktree_dir, force=False)`: if directory missing, print `[WARN]` and return; if dirty and not force, raise `WorktreeDirtyError`; run `git worktree remove [--force] {worktree_dir}` <!-- id: 7 -->

### Tests (`tests/`)
- [x] Test `git_version_check()`: passes on current git; mock version string < 2.5 raises `RuntimeError` <!-- id: 8 -->
- [x] Test `worktree_path()`: `feat/api` → `../reponame-feat-api`; verify with various slug patterns <!-- id: 9 -->
- [x] Test `parse_partitions_dag()`: returns correct list from valid block; returns `[]` for missing file; returns `[]` for missing block; returns `[]` for invalid YAML; use this initiative's own `approach.md` as a real fixture <!-- id: 10 -->
- [x] Test `create_worktree()` in real temp git repo: creates worktree dir; idempotent on re-call; raises on invalid branch <!-- id: 11 -->
- [x] Test `remove_worktree()` in real temp git repo: removes clean worktree; raises `WorktreeDirtyError` on dirty without force; removes dirty with force; warns and returns on missing dir <!-- id: 12 -->

---

## Partition 2: Core Script Integration (`feat/worktree-scripts`)

> Starts after `feat/worktree-utils` merges to `initiative/worktrees-parallel-execution`.

### `branch.py`
- [ ] Import `parse_partitions_dag`, `create_worktree`, `worktree_path`, `git_version_check`, `WorktreeDirtyError` from `utils` <!-- id: 20 -->
- [ ] Add `--worktree-dir` optional arg (override default worktree path) <!-- id: 21 -->
- [ ] Add `--no-worktree` flag (force plain branch even if `depends_on: []`) <!-- id: 22 -->
- [ ] In `create_branch()`: resolve `approach.md` path from `.cicadas/active/{initiative}/approach.md`; call `parse_partitions_dag()`; look up current branch name in DAG; if `depends_on: []` and not `--no-worktree`, call `create_worktree()` with computed or overridden path <!-- id: 23 -->
- [ ] On successful worktree creation: write `worktree_path` to branch's registry entry; print `[OK]   Worktree created: {abs_path}` <!-- id: 24 -->
- [ ] Write `context.md` to worktree root: assemble from `canon/summary.md` (if present), module snapshots for declared modules, `approach.md`, `tasks.md`; print `[INFO] context.md written to worktree root` <!-- id: 25 -->
- [ ] Print `[INFO] Point your agent at: {abs_path}` after successful worktree creation <!-- id: 26 -->
- [ ] On DAG lookup miss (branch not in partitions block): print `[WARN] Partition not found in approach.md — treating as sequential` and create plain branch <!-- id: 27 -->

### `kickoff.py`
- [ ] After draft promotion: resolve promoted `approach.md` path; call `parse_partitions_dag()` <!-- id: 30 -->
- [ ] Collect names of partitions with `depends_on: []`; if any: print `[INFO] Parallel partitions detected: {list}`; call `check_conflicts(initiative_name=name)` <!-- id: 31 -->
- [ ] If `check_conflicts` returns `True` (conflicts): print `[WARN]` lines from check output; printing continues but warn Builder to resolve before starting parallel branches <!-- id: 32 -->

### `check.py`
- [ ] Refactor `check_conflicts()` to accept `initiative_name: str | None = None` param <!-- id: 40 -->
- [ ] When `initiative_name` provided: scope module-overlap check to all branches registered under that initiative (not just current git branch); return `bool` indicating conflicts found <!-- id: 41 -->
- [ ] Add stale-worktree detection: iterate all registry branches; for any with `worktree_path` set, check if directory exists; print `[WARN] Stale worktree: {path} (branch: {name}). Run 'git worktree repair' or re-run branch.py.` <!-- id: 42 -->
- [ ] Existing CLI invocation (no args) preserves current-branch behavior unchanged <!-- id: 43 -->

### Tests
- [ ] Test `branch.py` with parallel partition: worktree created at expected path; `worktree_path` in registry; `context.md` present in worktree dir <!-- id: 50 -->
- [ ] Test `branch.py` with sequential partition (`depends_on` non-empty): plain branch only; no `worktree_path` in registry <!-- id: 51 -->
- [ ] Test `branch.py` idempotent: second call with same branch name reports existing worktree, doesn't duplicate <!-- id: 52 -->
- [ ] Test `branch.py` git failure: no registry write; exits non-zero <!-- id: 53 -->
- [ ] Test `kickoff.py`: parallel partitions detected → `check_conflicts` called; all sequential → no check called <!-- id: 54 -->
- [ ] Test `check.py` initiative-scoped mode: conflict across initiative branches flagged; no conflict = returns `False` <!-- id: 55 -->
- [ ] Test `check.py` stale-worktree detection: recorded path that doesn't exist → warning printed <!-- id: 56 -->

---

## Partition 3: Teardown & Status (`feat/worktree-teardown`)

> Starts after `feat/worktree-utils` merges to `initiative/worktrees-parallel-execution`. Parallel to Partition 2.

### `archive.py`
- [ ] Import `remove_worktree`, `WorktreeDirtyError` from `utils` <!-- id: 60 -->
- [ ] Add `--force` flag to CLI args <!-- id: 61 -->
- [ ] Before deregistering branch: check `registry["branches"][name].get("worktree_path")`; if set, call `remove_worktree(root, Path(wt_path), force=args.force)` <!-- id: 62 -->
- [ ] Handle `WorktreeDirtyError`: print `[WARN] Worktree has uncommitted changes: {path}` + `[WARN] Use --force to remove anyway...`; exit non-zero <!-- id: 63 -->
- [ ] On successful removal: print `[OK]   Worktree removed: {path}`; clear `worktree_path` from registry entry before save <!-- id: 64 -->
- [ ] Missing dir path: `remove_worktree` already handles (`[WARN]` + continue); `worktree_path` still cleared from registry <!-- id: 65 -->

### `prune.py`
- [ ] Same `--force` flag and `remove_worktree` integration as `archive.py` — apply to branch pruning path only <!-- id: 70 -->
- [ ] Clear `worktree_path` from registry on successful removal <!-- id: 71 -->

### `abort.py`
- [ ] Same `--force` flag and `remove_worktree` integration as `archive.py` <!-- id: 75 -->

### `status.py`
- [ ] Collect all branches in registry with a non-null `worktree_path` <!-- id: 80 -->
- [ ] If none: skip Worktrees section entirely <!-- id: 81 -->
- [ ] If any: print `\nWorktrees ({n}):` section after existing Branches output <!-- id: 82 -->
- [ ] For each worktree: run `git -C {path} status --porcelain`; if output empty → `[clean]`, else → `[dirty]`; run `git -C {path} log -1 --oneline` for HEAD summary <!-- id: 83 -->
- [ ] If `worktree_path` dir does not exist: print `[MISSING]` instead of status/HEAD <!-- id: 84 -->
- [ ] Format: `  {branch-name}  →  {abs-path}  [{clean|dirty|MISSING}]  {HEAD or ""}` <!-- id: 85 -->

### Tests
- [ ] Test `archive.py` clean worktree: worktree removed; `worktree_path` cleared in registry <!-- id: 90 -->
- [ ] Test `archive.py` dirty worktree without `--force`: exits non-zero; worktree not removed; registry intact <!-- id: 91 -->
- [ ] Test `archive.py` dirty worktree with `--force`: worktree removed <!-- id: 92 -->
- [ ] Test `archive.py` missing worktree dir: warns; continues; registry cleared <!-- id: 93 -->
- [ ] Test `prune.py` worktree teardown: same scenarios as archive <!-- id: 94 -->
- [ ] Test `status.py` no worktrees: Worktrees section absent from output <!-- id: 95 -->
- [ ] Test `status.py` one clean + one missing worktree: both render correctly with correct labels <!-- id: 96 -->

---

## Partition 4: Templates & Emergence Instructions (`feat/worktree-templates`)

> Fully independent — can run at any time, in parallel with all other partitions.

### `src/cicadas/templates/approach.md`
- [ ] Add `partitions` YAML block to template with schema documentation comment and a worked 2-partition example (one parallel, one sequential) <!-- id: 100 -->
- [ ] Add a note in the template that `depends_on: []` signals parallelism and triggers worktree creation <!-- id: 101 -->

### `src/cicadas/emergence/approach.md`
- [ ] Update subagent instructions: add step to populate the `partitions` block for each partition declared <!-- id: 102 -->
- [ ] Document `depends_on` semantics: empty list = parallel (gets worktree), non-empty = sequential (plain branch) <!-- id: 103 -->
- [ ] Include the exact YAML fence format and a worked example <!-- id: 104 -->

### `.gitignore`
- [ ] Add `context.md` to root `.gitignore` <!-- id: 110 -->

---

## Cross-Partition: Reflect Checkpoints

Before merging each feature branch to the initiative branch:
- [ ] Run Reflect: compare implementation against `tasks.md` and `tech-design.md`; update this file with `- [x]` for completed items; adjust any tasks that diverged <!-- id: 200 -->
- [ ] Confirm `git worktree list` shows zero orphans after teardown tests pass <!-- id: 201 -->
- [ ] Confirm all existing tests in `tests/` still pass: `python -m pytest tests/` <!-- id: 202 -->
