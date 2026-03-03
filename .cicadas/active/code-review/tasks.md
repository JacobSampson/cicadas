
# Tasks: Code Review

## Partition 1: Code Review Subagent → `feat/code-review-subagent`

Mode: Foundation (strict phases — SKILL.md must reference the finalized prompt)

---

### Phase 1: Subagent Prompt (Blocking)

- [x] Create `src/cicadas/emergence/code-review.md`: Write Role, Process Preview, and scope-detection logic (auto-detect branch type from prefix: `feat/`, `fix/`, `tweak/`) <!-- id: 1 -->
  - Acceptance: File exists; header is `# Subagent: Code Review`; Process Preview shows where Code Review fits in the inner loop; scope detection table covers all three modes

- [x] `code-review.md`: Write Full Mode algorithm (feature branch scope) — steps 1–6: detect scope, read specs, gather diff (`git diff $(git merge-base HEAD initiative/*)  HEAD`), run all checks (task completeness, acceptance criteria, arch conformance, module scope, Reflect completeness, security scan, correctness scan, code quality), compile report, emit verdict <!-- id: 2 -->
  - Acceptance: All 8 check types are present with explicit pass/fail criteria; git diff command is correct for feature scope; finding category labels match the defined set exactly

- [x] `code-review.md`: Write Lightweight Mode algorithm (fix/tweak branch scope) — reads buglet.md or tweaklet.md, single diff command, runs fix completeness, scope containment, regression risk, security scan, correctness scan, code quality checks <!-- id: 3 -->
  - Acceptance: Correctly omits arch-conformance and module-scope checks (no tech-design.md/approach.md for lightweight paths); all remaining checks present

- [x] `code-review.md`: Write Output Format section — define the exact report template (section headings, emoji markers, finding category labels, verdict strings as literal constants) and a worked example showing a `NEEDS-WORK` report with one finding per category <!-- id: 4 -->
  - Acceptance: Report template is reproduced verbatim; worked example includes ✅ Verified, 🔶 Advisory, 🔴 Blocking, 🔒 Security, 🐛 Correctness sections and a `NEEDS-WORK` verdict; advisory caveat line is present

- [x] `code-review.md`: Write Key Considerations section — consistency enforcement (no paraphrased headings), diff-scope precision (wrong diff = wrong review), spec file resolution (handle missing files gracefully), advisory-only enforcement, false-positive discipline (findings must cite specific line/pattern) <!-- id: 5 -->
  - Acceptance: All five considerations present; copyright footer present

---

### Phase 2: SKILL.md Integration (Depends on Phase 1)

- [x] `src/cicadas/SKILL.md`: Add `code-review.md` to the directory listing under `emergence/` <!-- id: 6 -->
  - Acceptance: Entry reads `├── code-review.md  # Code Review subagent`

- [x] `src/cicadas/SKILL.md`: Add `### Code Review` section under `## Agent Operations (LLM)` — trigger, action summary (auto-detect scope, read specs, run algorithm, emit report), and note that output is ephemeral <!-- id: 7 -->
  - Acceptance: Section is consistent with the Reflect and Signal Assessment sections in structure; scope auto-detection and advisory-only verdict mentioned

- [x] `src/cicadas/SKILL.md`: Add Code Review row to Agent Autonomy Boundaries table <!-- id: 8 -->
  - Acceptance: Row reads `| **Code Review** | Autonomous | Agent runs review and presents findings; Builder retains merge authority. |`

- [x] `src/cicadas/SKILL.md`: Add Code Review Builder commands to Builder Commands section <!-- id: 9 -->
  - Acceptance: Commands listed: `"Code review"`, `"Review feature"`, `"Review fix"`, `"Review tweak"` with brief descriptions

- [x] `src/cicadas/SKILL.md`: Add Code Review row to Agent Operations quick reference table <!-- id: 10 -->
  - Acceptance: Row includes trigger (`End of feature/fix/tweak branch, before merge`) and action summary

---

### Phase 3: Verify

- [x] Manually read `code-review.md` end-to-end and verify: no section references a file that doesn't exist (e.g., no `approach.md` reference in Lightweight Mode), all finding category labels match the defined set, report format template is internally consistent <!-- id: 11 -->
  - Acceptance: Zero cross-reference errors; all category labels in algorithm match labels in Output Format section

- [x] Lint: `source .venv/bin/activate && ruff check src/ tests/` — confirm zero new errors <!-- id: 12 -->
  - Acceptance: Clean lint output (markdown files are not linted; this is a sanity check that no adjacent Python was accidentally touched)

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
