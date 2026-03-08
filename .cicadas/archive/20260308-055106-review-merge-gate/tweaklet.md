
# Tweaklet: Code Review as Merge Gate

## Intent

Make code review a persistent, machine-readable artifact and a real merge gate. The review agent writes `review.md` to `.cicadas/active/{initiative}/` with a structured verdict (`PASS`, `PASS WITH NOTES`, or `BLOCK`). A new `review.py` script reads the verdict and returns an appropriate exit code. `open_pr.py` checks for a `BLOCK` verdict and refuses to proceed.

## Proposed Change

**`templates/review.md`** — New template. Mirrors the output format defined in `emergence/code-review.md` so the agent has a concrete fill-in-the-blanks target when writing to disk.

**`emergence/code-review.md`** — Two changes:
1. Add a step 0.5 (before Process Preview) to write the final report to `.cicadas/active/{initiative}/review.md` once the review is complete (overwriting any prior run).
2. Update verdict strings from `MERGE-READY` / `NEEDS-WORK` to `PASS` / `PASS WITH NOTES` / `BLOCK` to align with roadmap-next.md §3.

**`scripts/review.py`** — New script (~60 LOC). Detects the current branch's initiative, reads `.cicadas/active/{initiative}/review.md`, parses the verdict line (`**Verdict: PASS**` etc.), prints a summary, and exits with:
- `0` — PASS or PASS WITH NOTES
- `1` — BLOCK
- `2` — review.md not found (with instructions to run Code Review first)

**`scripts/open_pr.py`** — Add a pre-flight check: if `review.md` exists for the current initiative and its verdict is `BLOCK`, print the verdict summary and return exit code `1` without opening the PR. If `PASS WITH NOTES`, print an advisory and proceed. If no `review.md`, proceed with a warning.

## Tasks

- [x] Create `templates/review.md` <!-- id: 10 -->
- [x] Update `emergence/code-review.md`: add write-to-disk step and update verdict strings <!-- id: 11 -->
- [x] Create `scripts/review.py` with verdict detection and exit codes <!-- id: 12 -->
- [x] Update `scripts/open_pr.py` to check `review.md` verdict before proceeding <!-- id: 13 -->
- [x] Add tests for `review.py` verdict parsing and exit code behavior <!-- id: 14 -->
- [x] Significance Check: Yes — Canon update needed at completion (tech-overview.md, module snapshot for scripts) <!-- id: 15 -->
