# Buglet: unit-tests

## Intent

Address gaps and critical missing coverage identified in the test coverage review:
- `history.py` has zero test coverage (2 CRITICAL findings)
- `status.py` lifecycle merge detection paths are untested
- Vacuous assertion in `test_signalboard.py`
- Thin coverage in `test_update_index.py`, `test_create_lifecycle.py`, `test_synthesize.py`, `test_kickoff.py`
- Mock violation in `test_open_pr.py`
- Missing end-to-end test in `test_orchestration.py`
- Incomplete assertion in `test_archive_significance_check`

## Tasks

- [x] Create tests/test_history.py covering classify, extract_summary, count_tasks, load_token_summary, render_html, generate
- [x] Add lifecycle merge detection tests to test_archive_status.py (_is_merged_into, _ref_exists, _lifecycle_merge_status branches)
- [x] Fix vacuous assertion in test_signalboard.py::test_send_signal_no_initiative_unregistered_branch
- [x] Add accumulation, decisions, modules-whitespace tests to test_update_index.py
- [x] Add overwrite and step-content tests to test_create_lifecycle.py
- [x] Add gather_context and apply_response edge cases to test_synthesize.py
- [x] Remove shutil.which mock from test_open_pr.py
- [x] Add multi-file promotion and tokens.json init tests to test_kickoff.py
- [x] Add end-to-end kickoff→branch→archive→update_index test to test_orchestration.py
- [x] Complete test_archive_significance_check to assert archive still succeeds
