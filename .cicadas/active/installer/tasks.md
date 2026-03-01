# Tasks — Installer

## feat/install-core

- [x] Write `install.sh` scaffold: arg parsing (`--dir`, `--agent`, `--update`), `log()` helper
- [x] Git repo check: fail with helpful message if not in a git repo
- [x] Python 3.13+ check with OS-specific install guidance (brew / apt / winget)
- [x] `unzip` availability check with install guidance
- [x] Download + extract from GitHub archive URL to temp dir
- [x] Copy extracted skill files to `--dir` target (default: `src/cicadas/`)
- [x] Call `init.py` to create `.cicadas/` structure
- [x] `--update` flag: re-download + overwrite `scripts/`, `emergence/`, `templates/`, `skill.md`; skip init and agent setup
- [x] Smoke test: run `bash install.sh` in a clean temp git repo → `.cicadas/` created, `src/cicadas/` populated

**Reflect notes**: `install.sh` was written with agent integration logic inline (the `setup_agents()` function and interactive prompt). This means `agent-integrations` branch only needs to add doc updates (README.md, HOW-TO.md). Python 3.13 lives in `.venv`; CLAUDE.md updated accordingly.

## feat/agent-integrations

- [x] Merge `feat/install-core` as base (via initiative/installer)
- [x] `--agent claude-code`: create `.claude/skills/cicadas` relative symlink
- [x] `--agent antigravity`: create `.agents/skills/cicadas` relative symlink
- [x] `--agent cursor`: copy `skill.md` → `.cursor/rules/cicadas.mdc`
- [x] `--agent none`: skip agent setup silently
- [x] Interactive agent prompt when no `--agent` flag and stdin is a tty
- [x] Skip interactive prompt when `curl | bash` (non-tty stdin); print manual setup instructions instead
- [x] Update `README.md`: replace manual install section with one-liner
- [x] Update `HOW-TO.md`: add Install section and Update workflow
- [x] Smoke test: `bash install.sh --agent claude-code` → `.claude/skills/cicadas` symlink points to `src/cicadas/`
- [x] Smoke test: `bash install.sh --agent cursor` → `.cursor/rules/cicadas.mdc` exists with skill content

**Reflect notes**: All agent integration logic (setup_agents, interactive prompt, tty detection) was implemented inline in install.sh on install-core. This branch delivers the doc layer: README.md one-liner and HOW-TO.md Install & Update sections.
