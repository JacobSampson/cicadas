# Tweaklet: Agent guardrails and CR before commit (features)

## Intent
Tighten implementation agent behavior across all environments: require Reflect + task updates before every commit on feat/task branches, require Code Review before committing on feature branches, and ensure Cursor and other non–Claude Code envs get the same guardrails from the skill file. Fix Cursor install to use SKILL.md; document that CLAUDE.md is Claude Code–only.

## Proposed Change
- **implementation.md**: Pause before commit (Reflect + tasks); add Code Review before committing on feature branches.
- **SKILL.md**: Guardrails and new "Implementation agent rules (all environments)" section with same rules; Reflect trigger includes before every commit; CR before commit on feat/; fix Cursor install reference.
- **install.sh**: Copy SKILL.md (not skill.md) for Cursor integration.
- **CLAUDE.md**: Note that this file is Claude Code–only; other envs use the skill.
- **HOW-TO.md**, **README.md**: Agent table SKILL.md + note on where guardrails come from per env.

## Tasks
- [x] implementation.md: Reflect + tasks + CR (feat) before commit
- [x] SKILL.md: guardrails, Implementation agent rules, CR before commit on feat/
- [x] install.sh: use SKILL.md for Cursor
- [x] CLAUDE.md, HOW-TO, README: env-specific docs
- [ ] Verify: run status, confirm on tweak branch
- [ ] Significance check: Does this warrant a Canon update? (Doc/spec only — likely no.)
