# Tasks: visual-requirements

## Partition: feat/clarify-intake

**Branch:** `feat/clarify-intake` (from `initiative/visual-requirements`)  
**Modules:** `src/cicadas/emergence/`

### Clarify instructions

- [x] Confirm `emergence/clarify.md` step 0.5 Intake: intake question with [Q] [D] [L], Loom instructions block (record → copy transcript → save to `drafts/{initiative}/loom.md` → reply when done), Doc path (`requirements.md`), and explicit wait-for-file behavior; fill-from-doc and fill-from-loom behavior. Align copy with UX doc. <!-- id: 1 -->
- [ ] Dry-run or manual test: run Clarify for a test initiative; choose [Q] and confirm existing flow unchanged. <!-- id: 2 -->
- [ ] Dry-run or manual test: choose [D], place a sample `drafts/{test-initiative}/requirements.md`, confirm; verify agent waits then fills PRD and presents for review. <!-- id: 3 -->
- [ ] Dry-run or manual test: choose [L], place a sample `drafts/{test-initiative}/loom.md` (transcript text), confirm; verify agent waits then fills PRD and presents for review. <!-- id: 4 -->

### Optional discoverability

- [x] Add short mention of intake options and file paths (`loom.md`, `requirements.md`) to `EMERGENCE.md` and/or `SKILL.md` so Builders and agents can discover them without reading clarify.md. <!-- id: 5 -->

### Optional regression guard

- [x] Add test that parses `emergence/clarify.md` and asserts presence of "Intake", "loom.md", and "requirements.md" (or equivalent strings) to guard against instruction regressions. <!-- id: 6 -->

### Feature boundary (lifecycle: PR at features)

- [ ] Open PR: feat/clarify-intake → initiative/visual-requirements and await merge approval before continuing <!-- id: PR-feature -->

---

## Initiative boundary (lifecycle: PR at initiatives)

- [ ] Open PR: initiative/visual-requirements → master and await merge approval before continuing <!-- id: PR-initiative -->
