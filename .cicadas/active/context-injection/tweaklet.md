
# Tweaklet: Context Injection at Branch Start

## Intent

Complete roadmap item 4: ensure every registered branch (worktree or sequential) receives a
`context.md` bundle at start, and that `canon/summary.md` is produced during synthesis so
the bundle has something meaningful to inject.

## Current State

`branch.py` already has `_write_context_md()` which assembles canon summary + scoped module
snapshots + `approach.md` + `tasks.md` and writes `context.md` to the worktree root.
This runs **only for worktree (parallel) branches**.

Two gaps remain:
1. `canon/summary.md` is never created — synthesis prompt doesn't mention it, no template exists.
2. Sequential branches get no `context.md` — `_write_context_md` is skipped in that path.

## Proposed Change

### 1. Add `canon/summary.md` to synthesis

Update `src/cicadas/templates/synthesis-prompt.md` to add a final step:
> After the four standard canon files, produce `canon/summary.md` — a concise, high-signal
> overview of the entire codebase targeting 300–500 tokens. Sections: one-liner product
> purpose, key architectural decisions (bullet list), module index (name → one-line purpose),
> active conventions (naming, patterns, constraints). Purpose is agent bootstrapping at
> branch start, not human reading. Optimize for token density, not readability.

Add a minimal template file at `src/cicadas/templates/canon-summary.md`.

### 2. Inject context for sequential branches

In `branch.py`, after the `git checkout -b` / `git push` block in the sequential path, call
`_write_context_md(root, cicadas, list(my_mods), initiative)` so sequential branches also
get a `context.md` at the project root.

### 3. Gitignore `context.md` at project root

Ensure `context.md` is added to `.gitignore` so a sequential branch's injected file is
never accidentally committed (worktrees are already isolated).

### 4. Update `SKILL.md` synthesis step

Add a note in the "Synthesize canon on main" step that the agent also produces
`canon/summary.md` as part of synthesis.

## Tasks

- [x] Update `src/cicadas/templates/synthesis-prompt.md` to add `canon/summary.md` step <!-- id: 10 -->
- [x] Create `src/cicadas/templates/canon-summary.md` template <!-- id: 11 -->
- [x] Call `_write_context_md` in sequential branch path of `branch.py` <!-- id: 12 -->
- [x] Add `context.md` to `.gitignore` <!-- id: 13 (already present) -->
- [x] Update `SKILL.md` synthesis section to mention `canon/summary.md` <!-- id: 14 -->
- [x] Verify functionality (manual walkthrough: create a tweak branch, confirm context.md appears) <!-- id: 15 -->
- [ ] Significance Check: Does this warrant a Canon update? <!-- id: 16 -->
