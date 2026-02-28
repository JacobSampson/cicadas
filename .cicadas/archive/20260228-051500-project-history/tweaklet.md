
# Tweaklet: project-history

## Intent

Generate a self-contained HTML timeline at `.cicadas/canon/history.html` by reading the archive folder (spec files) and `index.json` (ledger entries) to produce a comprehensive visual history of completed initiatives, tweaks, and bug fixes.

## Proposed Change

New script: `src/cicadas/scripts/history.py`

- Scans `.cicadas/archive/` — each `{timestamp}-{name}/` folder becomes a timeline entry
- Reads `prd.md` (or `tweaklet.md` / `buglet.md`) to extract executive summary / intent
- Reads `approach.md` for partition/feature branch info (initiatives only)
- Reads `tasks.md` for task count and completion status
- Cross-references `.cicadas/index.json` entries by branch name for logged summaries
- Classifies entries: name contains `fix/` or starts with `fix-` → bug fix; `tweak/` or `tweak-` → tweak; else → initiative
- Outputs a single self-contained `history.html` (inline CSS + JS, no external deps) to `.cicadas/canon/`
- CLI: `python src/cicadas/scripts/history.py [--output path]`

## Tasks

- [ ] Write `src/cicadas/scripts/history.py` <!-- id: 10 -->
- [ ] Verify output renders correctly against existing archive data <!-- id: 11 -->
- [ ] Significance Check: Does this warrant a Canon update? <!-- id: 12 -->

---
_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
