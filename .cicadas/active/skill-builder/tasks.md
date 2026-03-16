# Tasks: skill-builder

## Partition 1: feat/script-infrastructure

### Spike: multi-line YAML description parsing

- [x] Write spike test cases in `tests/test_validate_skill.py` covering single-line, YAML folded scalar (`>`), and block scalar (`|`) description values to confirm stdlib regex handles all formats reliably. Document the constraint if block scalars are unreliable. <!-- id: 1 -->

### Plumbing changes (5 existing scripts)

- [x] `src/cicadas/scripts/branch.py`: add `or name.startswith("skill/")` to the lightweight parent-branch selection condition. Verify: `branch.py skill/xyz --initiative skill-xyz` creates `skill/xyz` from the default branch, not from `initiative/skill-xyz`. <!-- id: 2 -->
- [x] `src/cicadas/scripts/status.py`: add `skills` dict comprehension (`n.startswith("skill/")`); add a "Skills" display section to the output alongside "Fixes" and "Tweaks". <!-- id: 3 -->
- [x] `src/cicadas/scripts/archive.py`: add `or name.startswith("skill/")` to the branch-type detection condition. <!-- id: 4 -->
- [x] `src/cicadas/scripts/prune.py`: add `or name.startswith("skill/")` to the branch-type detection condition. <!-- id: 5 -->
- [x] `src/cicadas/scripts/abort.py`: add `"skill/"` to the `LIGHTWEIGHT_PREFIXES` tuple. <!-- id: 6 -->

### New scripts

- [x] `src/cicadas/scripts/validate_skill.py`: implement slug-or-path resolution (slug → `active/skill-{slug}/` first, then `drafts/skill-{slug}/`); parse YAML frontmatter with stdlib regex (using approach confirmed in spike); check all FR-4.2 conditions (SKILL.md exists, frontmatter present, `name` charset/length/dir-match, `description` present/non-empty/≤1024 chars); print `[ERR] {message}` per violation and exit 1, or print `[OK] skill/{name} is valid` and exit 0. <!-- id: 7 -->
- [x] `src/cicadas/scripts/skill_publish.py`: implement slug resolution (`active/skill-{slug}/`); read `publish_dir` from `active/skill-{slug}/emergence-config.json` (fall back to `--publish-dir` CLI arg; exit `[ERR]` if neither present or `null`); **run `validate_skill.py` on `active/skill-{slug}/SKILL.md` as a pre-publish check — exit `[ERR]` with the validation message if it fails**; check destination `{publish_dir}/{slug}/` doesn't already exist (exit `[ERR]` unless `--force`); copy with `shutil.copytree` (default) or symlink with `os.symlink` (`--symlink` flag); report `[OK] Published skill/{slug} to {dest}/`. <!-- id: 8 -->

### Template

- [x] `src/cicadas/templates/skill-SKILL.md`: write minimal SKILL.md scaffold — YAML frontmatter with `name` and `description` placeholders, `license` comment, and body section stubs (`## Instructions`, optional `## Scripts`, `## References`). Confirm it passes `validate_skill.py` after substituting a valid slug. <!-- id: 9 -->

### Tests

- [x] `tests/test_branch.py`: add regression assertions for `skill/` — verify parent branch is default branch (not initiative), verify registration in `branches` with correct `initiative` key. <!-- id: 10 -->
- [x] `tests/test_archive_status.py`: add assertions for `skill/` branches in status output (appears in Skills section) and archive of `skill-{name}` initiatives (correct archive dir name). <!-- id: 11 -->
- [x] `tests/test_prune.py`: add assertions for pruning `skill/{name}` branch and `skill-{name}` initiative. <!-- id: 12 -->
- [x] `tests/test_abort.py`: add assertions for abort from a `skill/` branch (recognised as lightweight, correctly deregisters branch and initiative). <!-- id: 13 -->
- [x] `tests/test_validate_skill.py`: full path coverage — one test per `[ERR]` violation type (missing SKILL.md, missing frontmatter, name missing, name too long, name bad charset, name starts with hyphen, name ends with hyphen, name consecutive hyphens, name/dir mismatch, description missing, description empty, description >1024 chars); one `[OK]` test for a valid skill; one test for slug resolution (active/ preferred over drafts/). <!-- id: 14 -->
- [x] `tests/test_skill_publish.py`: test copy (default), symlink (`--symlink`), destination already exists without `--force` (exits 1), destination exists with `--force` (succeeds), `publish_dir` null in config (exits 1), `--publish-dir` CLI override, **invalid SKILL.md fails pre-publish validate and exits 1 without writing to destination**. Use real temp dirs. <!-- id: 15 -->
- [x] Run full test suite; confirm all existing tests pass and all new tests pass. <!-- id: 16 -->

---

## Partition 2: feat/emergence-and-docs

### Instruction modules

- [x] `src/cicadas/emergence/skill-create.md`: draft the full dialogue-driven create flow — (1) pace check + start flow (publish destination detection and question, write `publish_dir` to `emergence-config.json`); (2) clarifying dialogue (4 intent questions + bundling signal probe for scripts/references/assets); (3) draft generation instructions (complete SKILL.md + proposed bundled files with rationale, shown separately); (4) review/iteration loop; (5) write/register sequence (write to `drafts/skill-{slug}/`, `kickoff.py`, `branch.py`, `validate_skill.py`, draft `eval_queries.json` with 8–10 should-trigger + 8–10 should-not-trigger); (6) completion note (call `skill_publish.py` when `skill/{slug}` is merged). Embed spec constraints inline (name rules, description ≤1024, progressive disclosure). <!-- id: 17 -->
- [x] `src/cicadas/emergence/skill-edit.md`: draft the dialogue-driven edit flow — (1) resolve skill path (`active/skill-{name}/` on branch `skill/{name}`, or `drafts/` if not yet kicked off); (2) one diagnostic question (under-triggering / over-triggering / wrong output); (3) read SKILL.md and affected files; (4) propose minimum targeted change as before/after, with rationale; (5) apply on Builder approval; (6) run `validate_skill.py`; (7) report outcome. <!-- id: 18 -->

### Updated files

- [x] `src/cicadas/emergence/start-flow.md`: insert new **Publish destination** step (after Building on AI?, scoped to skill entry type only); add detection order (`.cicadas/config.json skill_publish_dir` → `.agents/skills/` → `.claude/skills/` → `src/` → `skills/` → prompt with "Other" and "Don't publish" options); write chosen path to `emergence-config.json` as `publish_dir`; extend the scoping table with a `skill` column. <!-- id: 19 -->
- [x] `src/cicadas/SKILL.md`: (a) add `skill/` to the branch hierarchy diagram alongside `fix/` and `tweak/`; (b) add **Skills** section under Operations with triggers (`"create a skill"`, `"start a skill"`, `"build a skill for X"`, `"edit skill X"`, `"tune skill X"`), create/edit/validate/complete-skill operations, and a note that `skill-evaluate.md` / `skill-tune.md` are Post-MVP; (c) add Builder commands (`"Create skill {name}"`, `"Edit skill {name}"`, `"Complete skill {name}"`); (d) update the SKILL.md frontmatter description to include skill trigger phrases. <!-- id: 20 -->

### Final check

- [x] Re-read all five draft docs (`prd.md`, `ux.md`, `tech-design.md`, `approach.md`, `tasks.md`) and the two new emergence modules against each other. Confirm: all FR numbers referenced in tasks map to correct PRD FRs; `validate_skill.py` CLI in `skill-create.md` and `skill-edit.md` matches the implemented interface from Partition 1; `publish_dir` detection order in `start-flow.md` matches `skill_publish.py` behaviour; no contradictions. <!-- id: 21 -->
