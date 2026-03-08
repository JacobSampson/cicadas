
# Tasks: Token Usage Logging

## Partition 1: feat/token-core

### Feature: Core Token Logger
- [x] Create `src/cicadas/scripts/tokens.py`: implement `init_log(log_path)` — creates `{"entries": []}` if file absent <!-- id: 1 -->
- [x] `tokens.py`: implement `load_log(log_path)` — returns entries list; returns `[]` on missing/corrupt file, never raises <!-- id: 2 -->
- [x] `tokens.py`: implement `append_entry(log_path, initiative, phase, source, *, subphase, input_tokens, output_tokens, cached_tokens, model, notes)` — validates required fields and source enum, appends timestamped entry, wraps I/O in try/except with `[WARN]` on failure <!-- id: 3 -->
- [x] `tokens.py`: define `VALID_SOURCES = {"agent-reported", "unavailable", "estimated"}` and validate in `append_entry()` <!-- id: 4 -->

### Feature: Core Tests
- [x] Create `tests/test_tokens.py`: test `init_log()` creates file with empty entries list <!-- id: 5 -->
- [x] `test_tokens.py`: test `append_entry()` creates file on first write and entry has correct fields <!-- id: 6 -->
- [x] `test_tokens.py`: test multiple `append_entry()` calls grow the entries list <!-- id: 7 -->
- [x] `test_tokens.py`: test `append_entry()` raises `ValueError` on invalid source <!-- id: 8 -->
- [x] `test_tokens.py`: test `append_entry()` raises `ValueError` when required fields missing <!-- id: 9 -->
- [x] `test_tokens.py`: test `load_log()` returns `[]` when file absent <!-- id: 10 -->
- [x] `test_tokens.py`: test `load_log()` returns `[]` when file contains invalid JSON <!-- id: 11 -->
- [x] `test_tokens.py`: test `append_entry()` with all optional fields set to None succeeds <!-- id: 12 -->
- [x] `test_tokens.py`: test timestamp is ISO 8601 UTC format <!-- id: 13 -->

---

## Partition 2: feat/token-integration

### Feature: Kickoff Integration
- [x] Update `src/cicadas/scripts/kickoff.py`: import `append_entry` from `tokens` <!-- id: 20 -->
- [x] `kickoff.py`: after `active_dir` is set and initiative is registered, call `append_entry(active_dir / "tokens.json", initiative=name, phase="lifecycle", subphase="kickoff", source="unavailable")` <!-- id: 21 -->
- [x] `test_kickoff.py` or `test_tokens.py`: add integration test — after `kickoff()`, `tokens.json` exists in active dir with one entry having `phase="lifecycle"` and `subphase="kickoff"` <!-- id: 22 -->

### Feature: Branch Integration
- [x] Update `src/cicadas/scripts/branch.py`: import `append_entry` from `tokens` <!-- id: 23 -->
- [x] `branch.py`: after branch is registered, call `append_entry(active_dir / "tokens.json", initiative=active_name, phase="implementation", subphase=name, source="unavailable")` <!-- id: 24 -->
- [x] `test_branch.py` or `test_tokens.py`: add integration test — after `create_branch()`, `tokens.json` in active dir has an entry with `phase="implementation"` and `subphase` matching branch name <!-- id: 25 -->

### Feature: History Rollup
- [x] Update `src/cicadas/scripts/history.py`: add `load_token_summary(folder)` — reads `tokens.json` from archive folder; returns dict with `total_input`, `total_output`, `total_cached`, `by_phase`; returns `None` if file absent, corrupt, or all counts are null <!-- id: 26 -->
- [x] `history.py`: update `parse_archive_entry()` to include token summary in the entry dict <!-- id: 27 -->
- [x] `history.py`: update `render_html()` card template — add conditional token block: shows per-phase breakdown table only when token summary is non-None and at least one phase has non-null counts <!-- id: 28 -->
- [x] Add tests for `load_token_summary()`: returns None when file absent, returns None when all counts null, returns correct totals when counts present <!-- id: 29 -->
- [x] Add test for `render_html()`: card renders without error when token summary is None <!-- id: 30 -->
- [x] Add test for `render_html()`: card includes token block when summary has real counts <!-- id: 31 -->

---

## Partition 3: feat/emergence-pace

### Feature: Clarify Pace Question
- [x] Update `src/cicadas/emergence/clarify.md` step 0: present three-level pace menu (`[S] Section / [D] Doc / [A] All`) before any drafting begins <!-- id: 40 -->
- [x] `clarify.md`: write chosen pace to `.cicadas/drafts/{name}/emergence-config.json` with key `"pace"`; default to `"doc"` if Builder skips <!-- id: 41 -->

### Feature: Pace Enforcement in Subsequent Agents
- [x] Update `src/cicadas/emergence/ux.md`: add step 0 — read `emergence-config.json`, state active stop rule, enforce accordingly <!-- id: 42 -->
- [x] Update `src/cicadas/emergence/tech-design.md`: same step 0 pace check <!-- id: 43 -->
- [x] Update `src/cicadas/emergence/approach.md`: same step 0 pace check <!-- id: 44 -->
- [x] Update `src/cicadas/emergence/tasks.md`: same step 0 pace check <!-- id: 45 -->

### Feature: Clarify Process Preview
- [x] Update `src/cicadas/emergence/clarify.md` step 0 Process Preview: add a note that Approach will ask about PR boundaries before drafting and that `lifecycle.json` is created at that step <!-- id: 47 -->

### Feature: EMERGENCE.md Documentation
- [x] Update `src/cicadas/emergence/EMERGENCE.md`: add pace option to workflow overview — note that `clarify.md` step 0 sets the pace for the entire emergence phase <!-- id: 46 -->
