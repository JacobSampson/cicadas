# PRD — Installer

## Problem

Cicadas has no installation story. Users must:
1. Manually copy `src/cicadas/` files into their project
2. Discover Python 3.13+ is required only after setup fails
3. Manually create agent symlinks/configs for Claude Code, Cursor, etc.

This friction prevents adoption and is especially punishing for developers whose primary stack is not Python.

## Users

Developers using AI coding agents (Claude Code, Cursor, Antigravity, etc.) on any tech stack (React, Java, Go, etc.) who want to adopt spec-driven development with Cicadas.

## Goals

- Zero-friction install: one command puts Cicadas into any project
- Fast: under 60 seconds from nothing to first `cicadas status`
- Transparent: print what's happening; no silent failures
- Agent-aware: set up agent integrations automatically

## Non-Goals

- Package manager distribution (npm, pip, homebrew) — not yet
- Windows native support (only WSL) — not yet
- Auto-upgrading background daemon

## Success Criteria

- `curl -fsSL https://raw.githubusercontent.com/ecodan/cicadas/master/install.sh | bash` works in a fresh git repo
- Under 60 seconds on a normal connection
- Works regardless of project stack (no node/npm/java required)
- Python 3.13+ missing → helpful, OS-specific install guidance printed; installer exits cleanly
- Agent integrations created correctly when `--agent` flag provided
