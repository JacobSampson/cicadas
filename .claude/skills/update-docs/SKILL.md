---
name: update-docs
description: Use before committing or pushing to update project documentation. Updates README.md, HOW-TO.md, src/cicadas/README.md, release-notes.md, agents.md, and CLAUDE.md to reflect recent code and structural changes.
argument-hint: "[optional: brief description of what changed]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Update Docs

Update the six canonical documentation files to reflect recent changes before a commit or push.

## Files to Update

| File | Purpose | Update Trigger |
|------|---------|----------------|
| `README.md` | High-level intro, version, installation, quick-start | Script changes, workflow changes, version bump |
| `HOW-TO.md` | Full user guide (install, greenfield, brownfield, skills) | Workflow changes, new features, installation changes |
| `src/cicadas/README.md` | Technical breakdown of the orchestrator | Script changes, directory structure changes |
| `release-notes.md` | Changelog — one entry per release | Always: add a new entry describing what changed |
| `agents.md` | Project overview for agents | Structural or architectural changes |
| `CLAUDE.md` | Claude Code guidance: commands, architecture, conventions | Script changes, new files, test convention changes |

## Process

### 1. Understand What Changed
```bash
git diff HEAD
git status
```
If the user provided arguments (`$ARGUMENTS`), treat them as additional context about the nature of the change.

### 2. Read Each Doc File
Read all six files before making any edits. Understand their current state.

### 3. Determine What Needs Updating
For each file, ask: *does the diff reveal something this doc now misrepresents or omits?*

- **README.md**: Update installation commands, version string, or workflow description if affected.
- **HOW-TO.md**: Update the relevant section if a workflow step, command, or skill registration process changed.
- **src/cicadas/README.md**: Update script listings, directory structure, or operational formulas if scripts were added/renamed/removed.
- **release-notes.md**: **Always** add a new entry at the top (under `# Release Notes`) in the format:
  ```
  ## Version X.Y.Z
  - **Category**: Description of change.
  ```
  Infer the version bump: patch for fixes/docs, minor for new features, major for breaking changes.
- **agents.md**: Update if the top-level project structure, key directories, or agent roles changed.
- **CLAUDE.md**: Update commands, architecture description, or test conventions if scripts, tests, or project structure changed.

### 4. Make Targeted Edits
Edit only the sections that are out of date. Do not rewrite content that is still accurate. Preserve the existing tone and formatting of each file.

### 5. Stage the Updated Files
```bash
git add README.md HOW-TO.md src/cicadas/README.md release-notes.md agents.md CLAUDE.md
```

### 6. Report
List which files were updated and briefly describe what changed in each. If a file needed no changes, say so.

## Guardrails

- Do not bump the version in `README.md` or `release-notes.md` unless the user has indicated this is a release commit. If unsure, ask.
- Do not alter the structure or heading hierarchy of any file unless it is clearly wrong.
- Do not add filler content — only update what the diff actually warrants.
