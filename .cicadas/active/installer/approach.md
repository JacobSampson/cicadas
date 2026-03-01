# Approach — Installer

## Feature Branches

| Branch | Scope | Description |
|--------|-------|-------------|
| `feat/install-core` | `install.sh` | Python check, download, extract, init, `--update` flag |
| `feat/agent-integrations` | Agent setup + docs | Symlink/config creation per agent type; README + HOW-TO updates |

## Sequencing

Both branches fork from `initiative/installer`. They can be worked independently since they touch different files:
- `feat/install-core`: creates `install.sh`
- `feat/agent-integrations`: adds agent logic to `install.sh` (via merge or coordinated edit), updates `README.md` and `HOW-TO.md`

Recommended order: complete `feat/install-core` first, then `feat/agent-integrations` merges it and adds agent logic on top.

## Key Decisions

1. **Single shell script** — no build pipeline, no dependencies, universally runnable
2. **GitHub archive URL** — avoids needing a release workflow; master is always current
3. **Relative symlinks** — portable; work regardless of where the repo is cloned
4. **`curl | bash` aware** — detect non-interactive stdin, skip interactive prompts
5. **`--update` stays in shell** — YAGNI; no `self_update.py` for now
6. **`init.py` is idempotent** — safe to call on update; never destroys `.cicadas/` state

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| `unzip` not present | Check for `unzip`; suggest `sudo apt install unzip` |
| Symlinks not supported (rare filesystems) | Detect failure, fall back to copy for agent integration |
| `curl \| bash` breaks interactive prompts | Detect `[ -t 0 ]`; if not tty, skip prompt and print guidance |
| Archive URL changes if we rename branch | Document in tech-design; easy to update the one URL |
