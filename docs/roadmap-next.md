# Cicadas: Next Evolution — Roadmap Notes

_Discussion notes from March 2026. These are directional proposals, not finalized specs._

---

## 1. Worktrees for Parallel Execution

**What:** Use `git worktree` for parallel feature branch execution; plain branches for sequential work.

**Why:** Worktrees give each agent an isolated filesystem checkout without requiring a separate clone. Agents can build, test, and commit independently without fighting over the working directory. For sequential work, the overhead isn't justified — `git switch` is sufficient.

**Key design decisions:**

- `approach.md` must explicitly encode a dependency DAG between partitions — which can run in parallel, which must wait. The emergence agent is responsible for declaring this during spec authoring.
- `kickoff.py` / `branch.py` read the DAG and decide: parallel → create worktree, sequential → create plain branch.
- `check.py` should run *before* parallel execution starts (not just on-demand) to catch module ownership conflicts early.
- Cleanup is explicit: `archive.py` and `abort.py` must tear down worktrees, not just delete branch references.

**Approach.md addition needed:** A `partitions` block declaring each partition's name, module scope, and dependencies (e.g. `depends_on: [partition-a]`). Empty `depends_on` means it can run immediately.

---

## 2. Spec Development Stays Human-Paced

**What:** No compression of the emergence phase. Each subagent phase (Clarify → UX → Tech → Approach → Tasks) remains a sparring opportunity between human and agent.

**Why:** This is where Cicadas earns its keep. The spec pipeline eliminates ambiguity that would otherwise cause agent failures downstream. Compressing it to save time trades the wrong thing.

**One addition worth considering:** A cross-phase consistency check at the end of emergence — after Tasks is drafted, an agent reviews the full draft set for internal contradictions. Examples: tasks.md implying more scope than approach.md's partitions can contain; tech-design.md dependencies not reflected in the partition DAG; UX flows referencing features not in the PRD. This surfaces as a structured list of questions for the human, not autonomous resolution.

---

## 3. Automated Code Review as Merge Gate

**What:** After each feature branch completes, an independent code review agent runs before any merge proceeds. It produces a structured `review.md` artifact and issues a verdict.

**Why:** Removes a manual review step without removing quality assurance. The agent catches spec drift, test gaps, and code quality issues. Human only intervenes if the agent flags a block.

**Report structure (proposed `review.md`):**

- **Spec conformance** — did the implementation match tasks.md? List any gaps or deviations.
- **Reflect status** — are the active specs current with the code? Flag if Reflect was skipped.
- **Test coverage delta** — coverage before/after. Flag regressions.
- **Lint/format** — ruff clean, any warnings.
- **Merge verdict** — one of: `PASS`, `PASS WITH NOTES` (human should read but can proceed), `BLOCK` (human must resolve before merge).

**Placement:** `review.md` lives alongside `tasks.md` in `.cicadas/active/{initiative}/`. It is generated fresh on each review run — not manually edited.

**Merge gate:** PRs to initiative branch (and initiative to main) should not proceed with a `BLOCK` verdict. `PASS WITH NOTES` can proceed at human discretion.

---

## 4. Context Injection at Branch Start

**What:** When `branch.py` starts a feature branch, automatically inject relevant canon context into the agent's starting context.

**Why:** Research finding: token usage explains 80% of multi-agent performance variance. Agents that start with the right context make better decisions and deviate less from the plan.

**What gets injected:**

- `canon/summary.md` — a compressed, high-signal overview of the full codebase (target: 300–500 tokens). New artifact produced during canon synthesis, alongside the full canon docs.
- Full module snapshots (`canon/modules/{module}.md`) for each module declared in the feature branch's scope.
- The feature's own `tasks.md` and the parent initiative's `approach.md`.

**Canon synthesis addition:** The synthesis step adds one more output: `canon/summary.md`. Concise, high-signal. Purpose is branch-start injection, not human reading.

**Implementation:** `branch.py` assembles this context bundle and either writes it to a temp file the agent reads, or passes it as the agent's initial prompt prefix, depending on the agent integration.

---

## 5. Token Usage Logging

**What:** An append-only `tokens.json` log per initiative, created at the start of the draft phase and accumulating through archive. Captures token usage at each phase and subphase, giving a cradle-to-grave picture of initiative cost.

**Why:** Visibility into where tokens are actually going — across emergence subagents, implementation per partition, code review, and canon synthesis. Useful for catching runaway phases, validating that context injection compression is working, and building intuition about cost patterns across initiatives.

**Log lifecycle:**
- Created at: `.cicadas/drafts/{name}/tokens.json` (start of emergence)
- Moves to: `.cicadas/active/{name}/tokens.json` (on kickoff)
- Archives with: `.cicadas/archive/{timestamp}-{name}/tokens.json` (on completion)
- Rolled up by: `history.py` for cross-initiative cost summaries

**Entry schema:**

```json
{
  "timestamp": "2026-03-08T14:23:00Z",
  "initiative": "auth-revamp",
  "phase": "emergence",
  "subphase": "clarify",
  "input_tokens": 12400,
  "output_tokens": 3200,
  "cached_tokens": 8100,
  "model": "claude-sonnet-4-6",
  "source": "agent-reported",
  "notes": "Two rounds of human feedback"
}
```

**Phases to capture:**

| Phase | Subphase examples |
|---|---|
| `emergence` | `clarify`, `ux`, `tech-design`, `approach`, `tasks`, `consistency-check` |
| `implementation` | per partition name (e.g. `feat-auth`, `feat-api`) |
| `code-review` | per feature branch reviewed |
| `synthesis` | `canon`, `summary` |
| `cleanup` | `archive`, `prune` |

**Implementation strategy — Claude-native first:**

Token counts are runtime-dependent. The implementation approach is best-effort and incremental:

- **Claude Code / Claude Agent SDK** — full instrumentation. Token usage is available in API response metadata (`usage.input_tokens`, `usage.output_tokens`, `usage.cache_read_input_tokens`). Agent self-reports at end of each phase; scripts write phase-boundary entries. `"source": "agent-reported"`.
- **Other runtimes (Cursor, Windsurf, etc.)** — write the entry with `"tokens": null` and `"source": "unavailable"`. Schema is consistent; data quality varies. Document which runtimes give real numbers.
- **Estimation fallback** — for runtimes that expose text but not counts, estimate from character length (~4 chars/token for prose, less for code). Flag clearly with `"source": "estimated"`.

**Who writes the log:**
- Scripts write phase-boundary entries (kickoff, branch start, archive).
- Agents self-append within a phase when they can (emergence subagents, code review agent).
- Both patterns coexist — scripts handle the envelope, agents handle the interior.

**`history.py` addition:** Roll up `tokens.json` entries across archived initiatives into a summary table — total tokens per initiative, breakdown by phase, cost estimate (if model pricing is configured).

---

## 6. YOLO Mode — Autonomous Initiative Execution

**What:** A `--yolo` flag on `kickoff.py` (or a standalone `run.py`) that takes over after spec approval and drives the full initiative to a PR autonomously — no human checkpoints in between.

**Why:** The human already sparred during emergence and approved the specs. Everything after that is mechanical: spin up partitions, implement, review, merge, synthesize, open PR. YOLO mode removes the "proceed?" prompts and makes wave execution explicit.

**What YOLO mode does:**

1. Reads the partition DAG from `approach.md`
2. Runs `check.py` for pre-execution conflict validation
3. Executes partitions in waves (parallel where DAG allows, sequential where dependencies exist)
4. On each partition completion: runs `review.py` → auto-proceeds on `PASS` / `PASS WITH NOTES`, halts and surfaces to human on `BLOCK`
5. After all waves complete: synthesizes canon, runs `open_pr.py`, stops
6. Human reviews the PR — that's the only required touchpoint

**The `BLOCK` escape hatch is critical.** YOLO doesn't mean unattended forever — it means the human only intervenes when something genuinely unexpected happened, not as a routine step.

### New script: `run.py`

A thin orchestration wrapper (~100 lines) that manages wave execution. Not a new methodology — just removes the human from the "proceed?" prompts between existing steps.

```
wave 1: spawn agents on all partitions with no dependencies
wait for wave 1 completion
wave 2: spawn agents on partitions depending on wave 1
wait...
on each completion: review.py → merge or halt
after all waves: synthesize canon → open_pr.py
```

### Persistent orchestrator state: `run-state.json`

The orchestrator is **stateless between waves** — it never accumulates partition content in its context. After each wave it writes:

```json
{
  "initiative": "auth-revamp",
  "current_wave": 2,
  "completed_partitions": ["feat-auth"],
  "pending_partitions": ["feat-api"],
  "blocked_partitions": [],
  "review_verdicts": {"feat-auth": "PASS"},
  "started_at": "2026-03-08T10:00:00Z"
}
```

A `--resume` flag on `run.py` reads this file and continues from where it left off. Survives crashes, timeouts, and overnight runs.

### Runtime tiers for agent spawning

YOLO mode requires spawning sub-agents with fresh context. Not all runtimes support this:

**Tier 1 — Full YOLO (true parallel sub-agent spawning):**
- Claude Code via `claude --print` subprocess per worktree
- Claude Agent SDK (programmatic API)
- Raw Anthropic API (custom tool loop)

**Tier 2 — Sequential YOLO (context-disciplined, single agent):**
- Cursor, Windsurf, Copilot, IDE-embedded agents
- `run.py` detects no spawn capability, falls back to sequential partition execution with explicit context resets between partitions
- YOLO flag still means "don't stop and ask between steps" — just not parallel

**Tier 3 — Manual (script generates execution plan):**
- Unknown/unsupported runtime
- `run.py` outputs a human-readable checklist of commands to run

### New module: `runtime.py`

Shared detection and spawning abstraction imported by `run.py` and `branch.py`:

```python
class Runtime:
    CLAUDE_CODE = "claude-code"
    CLAUDE_SDK = "claude-sdk"
    ANTHROPIC_API = "anthropic-api"
    UNSUPPORTED = "unsupported"

    @staticmethod
    def detect() -> str: ...

    @staticmethod
    def can_spawn_agents() -> bool: ...

    @staticmethod
    def spawn_agent(worktree_path, prompt, context) -> AgentResult: ...
```

Detection checks: `claude` CLI in PATH, `ANTHROPIC_API_KEY` env var, `CURSOR_*` env vars, etc. Adding a new Tier 1 runtime later is just implementing the `spawn_agent()` interface — not a redesign.

### Context management for long-running YOLO

Long initiatives can run for hours. Two distinct problems:

**Worker agent context bloat:**
- Context bundle at branch start is intentionally minimal (canon summary + scoped modules + tasks.md only)
- Workers instructed to **reflect-before-compact** — write current state to disk before any compaction, so the filesystem is the memory, not the context window
- Compact proactively at task item boundaries, not reactively at 92% utilization

**Orchestrator context bloat:**
- Orchestrator never holds partition content — only verdicts and state references
- Workers return one line to the orchestrator (verdict + artifact paths), never full output
- Full detail goes to disk: `review.md`, `tokens.json`, reflected specs
- This is the **observation masking** pattern from JetBrains/NeurIPS 2025 — replace completed tool outputs with lightweight placeholders, don't summarize everything

**The principle:** Disk is cheap and persistent. Context is expensive and ephemeral. Anything that needs to outlive a context window goes to disk immediately, retrieved on demand via file reads rather than held in memory.

---

## 7. Coordination and Collision Prevention (Deferred)

**Status:** Parked. The problem (parallel agents on separate machines or repos need a shared coordination primitive) points toward git-native solutions — signals as commits to a shared ref, or a dedicated `cicadas/state` branch. Local filesystem watching doesn't survive multi-machine or multi-repo scenarios. Revisit once items 1–5 are in place.

---

## Summary of Script/Skill Changes Required

| Component | Change |
|---|---|
| `approach.md` template | Add `partitions` block with dependency DAG |
| `branch.py` | Read DAG, create worktree vs. plain branch accordingly |
| `kickoff.py` | Run `check.py` before parallel execution starts |
| `archive.py` / `abort.py` | Tear down worktrees on cleanup |
| `check.py` | Support pre-execution conflict validation mode |
| Canon synthesis | Add `summary.md` output (300–500 tokens) |
| `branch.py` | Inject canon summary + scoped module snapshots at branch start |
| New: `review.py` | Code review agent runner, produces `review.md` |
| `open_pr.py` | Check for `BLOCK` verdict in `review.md` before proceeding |
| `emergence/code-review.md` | Update with new report structure and verdict format |
| `templates/review.md` | New template for code review output |
| New: `tokens.json` | Append-only log, created in drafts, moves with initiative |
| All scripts | Write phase-boundary token entries where runtime allows |
| Emergence subagent prompts | Instruct agent to self-append token usage at phase end |
| `history.py` | Roll up token logs across archived initiatives |
| New: `run.py` | YOLO mode orchestrator; reads partition DAG, executes waves, calls review.py, merges, opens PR |
| New: `run-state.json` | Persistent orchestrator checkpoint; enables `--resume` after crash or timeout |
| New: `runtime.py` | Runtime detection and agent spawning abstraction (Tier 1/2/3) |
| `kickoff.py` | Accept `--yolo` flag; write mode to initiative config |
| Worker agent prompts | Instruct reflect-before-compact; proactive compaction at task boundaries |
