# AI-Assisted Development Methods: Multi-Framework Comparison

> Research compiled March 2026. Star counts verified at time of writing.  
> Scope: BMAD, Cicadas, GitHub Spec Kit, GSD, TaskMaster, OpenSpec, AWS Kiro.

---

## At a Glance

| | BMAD | Cicadas | Spec Kit | GSD | TaskMaster | OpenSpec | Kiro |
|---|---|---|---|---|---|---|---|
| **GitHub Stars** | 35k | 5 | 76.7k | 29.9k | 25.9k | 23.8k | N/A (IDE) |
| **License** | MIT | Apache 2.0 | MIT | MIT | MIT | MIT | Free preview |
| **Runtime** | Node 20+ | Python 3.11+ | Node (npx) | Node (npx) | Node (npx) | Node (npx) | Hosted IDE |
| **Maturity** | Production (v6 beta) | Early (v0.5) | Production | Production | Stable | Stable | Preview |
| **Core metaphor** | Full agile team of AI agents | Code-authoritative SDD | Constitution + spec phases | Context isolation + wave execution | PRD → dependency-driven tasks | Delta-spec change management | Spec-native IDE |
| **Best for** | Enterprise greenfield, governance | Experienced teams, parallel initiatives | Individual devs, clean greenfield | Solo devs, context rot, fast shipping | Task decomposition layer | Brownfield, incremental change | AWS-native, all-in-one IDE |
| **Complementary with** | TaskMaster (task management) | Spec Kit (Emergence inputs) | BMAD (planning layer) | Spec Kit (spec inputs) | BMAD, GSD, Spec Kit | Any method | BMAD, TaskMaster |

---

## Spec Creation

| Method | Approach | Artifact Set | Depth | Quality Gates |
|---|---|---|---|---|
| **BMAD** | Full agent chain: Analyst → PM → Architect → PO with guided elicitation, templates, probing questions | project-brief.md, prd.md, architecture.md, sharded epics, story files | Product-level, 15–25 page PRDs, 10–20 page architecture docs | PO alignment checklist between PRD and architecture before sharding |
| **Cicadas** | Subagent ensemble (Clarify, UX, Tech, Approach, Tasks) in staging area; supports Q&A, requirements doc, or Loom transcript as inputs | prd.md, tech-design.md, approach.md, tasks.md — per initiative | Initiative-level; equivalent rigor to BMAD within scope | Reflect loop + structured Code Review (PASS/BLOCK) pre-PR |
| **Spec Kit** | Four-phase CLI: `/constitution` → `/specify` → `/plan` → `/tasks`; constitution establishes non-negotiable project rules | constitution.md, spec.md, implementation-plan.md, tasks.md | Feature-level; concise and actionable over comprehensive | Cross-check step before implementation to catch over-engineering |
| **GSD** | Discuss phase (Q&A until fully understood) → parallel research agents → requirements extraction → roadmap; spawns specialized subagents | PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md, per-phase plans | Phase-level; emphasis on scope clarity (v1 vs v2 vs out-of-scope) | Nyquist validation layer catches quality issues before execution; plan-checker agent reviews plans before execution starts |
| **TaskMaster** | Not a spec creation tool; consumes an existing PRD as input | tasks.json with dependencies, complexity scores, and implementation sequence (generated from input PRD) | N/A — downstream consumer only | Dependency validation; complexity assessment per task |
| **OpenSpec** | Delta-based: tracks ADDED, MODIFIED, REMOVED requirements per change; minimal upfront ceremony | specs/ directory with feature specs; changes/ directory for incremental deltas | Change-level; designed for incremental clarity, not upfront comprehensiveness | Diff-based validation against existing specs |
| **Kiro** | IDE-native: describing a feature automatically generates requirements, design doc, and task list in-editor | requirements.md, design.md, tasks.md (auto-generated in-IDE) | Feature-level; structured but IDE-assisted rather than agent-deep | In-IDE spec review before agent hooks execute implementation |

**Summary:** BMAD offers the deepest upfront spec creation. Cicadas matches it within initiative scope. Spec Kit, GSD, and Kiro produce clean feature-level specs. OpenSpec is delta-first. TaskMaster doesn't create specs.

---

## Work Size Flexibility

| Method | Bugs / Hotfixes | Minor Features / Refactors | Major Features | 0→1 Greenfield | Brownfield |
|---|---|---|---|---|---|
| **BMAD** | Quick flow (`/quick-spec` → `/dev-story` → `/code-review`); still slightly ceremonious | Skippable phases 1–3; quick flow handles it | Full planning path | ★★★★★ Best-in-class; scale-adaptive intelligence | Explicit brownfield workflow with Analyst + Architect review of existing code |
| **Cicadas** | First-class "tweak" path: minimal draft → branch; cleanest for tiny work | Initiative vs. tweak distinction built into start flow | Full initiative path with partitioned approach.md | ★★★★ Solid; Emergence phase lighter than BMAD upfront | Naturally supported via existing canon snapshot; less scaffolding than BMAD |
| **Spec Kit** | Not optimized; minimum is a `spec.md`; overkill for a 5-line fix | Works well; `/specify` → `/tasks` is fast | Good fit; constitution governs consistency across features | ★★★★ Strong with constitution-first governance | Gaps in brownfield documentation; manual customization needed |
| **GSD** | Not explicitly lightweight; minimum is discuss + plan phases | Good fit; discuss phase scopes quickly | ★★★★ Strong; wave-based parallel execution handles complex features | ★★★★ Strong; codebase mapping via parallel agents before planning | `/gsd:map-codebase` analyzes existing stack before planning; good brownfield support |
| **TaskMaster** | Overkill for bugs; adds overhead without benefit | Reasonable if a PRD already exists | Good fit as orchestration layer on top of another method | Not standalone; requires a PRD from another tool | Works with existing PRDs describing brownfield changes |
| **OpenSpec** | ★★★★★ Purpose-built for this; delta-spec per change is minimal overhead | ★★★★★ Best fit; ADDED/MODIFIED/REMOVED tracking is natural here | Works; less structured than dedicated planning tools | Weak; no upfront planning scaffold | ★★★★★ Best-in-class; designed specifically for incremental changes to existing systems |
| **Kiro** | Can open a fix as a feature in-IDE; moderate overhead | Good fit in-IDE | Good fit; spec → design → tasks flow handles it well | ★★★★ Strong with IDE integration | Weak; generic initialization templates for existing projects require manual customization |

**Summary:** OpenSpec for brownfield/incremental. BMAD for greenfield. Cicadas and GSD are the most versatile across the range. TaskMaster is a layer, not a standalone.

---

## Round-Trip Process (Spec ↔ Code Sync)

| Method | Spec-Code Sync Mechanism | Feedback to Planning Docs | Post-Initiative Cleanup | Human Checkpoints |
|---|---|---|---|---|
| **BMAD** | Manual. Story files carry context; divergence handled by re-doing or editing the doc. No automated enforcement. | Not structurally built in. Artifacts stay static post-creation unless humans update them. | None. Docs persist in place, may drift or conflict with newer decisions. | Explicit review steps between phases; agents prompt for approval. Very deliberate. |
| **Cicadas** | **Reflect**: mandatory spec update when code diverges from plan, enforced before every commit on feat/task branches via pre-commit hook. | Reflect loop + post-merge Synthesis generates permanent record of intent vs. what was built. | Archive step moves active specs to `.cicadas/archive/`. Canon synthesized fresh. Registry updated. Clean slate. | Configurable PR preference at kickoff. Code Review verdict automated. Human review optional. |
| **Spec Kit** | No built-in sync mechanism. Spec is static once written; implementation may diverge silently. | No feedback loop back to spec. | No formal process. | Cross-check prompt before implementation; human reviews output before PR. |
| **GSD** | STATE.md tracks completion and phase status. Verify-work agent checks output against goals. No spec-update enforcement. | ROADMAP.md and STATE.md updated through phases; no spec-code diff tracking. | Milestone squash merge or merge with history; no formal archive. | Plan-checker reviews plan before execution; verify-work reviews output after. |
| **TaskMaster** | Task status updated as implementation proceeds. No spec-code sync beyond task completion flags. | No feedback to source PRD; task status only. | No formal cleanup; task file persists. | Human reviews task breakdown before implementation begins. |
| **OpenSpec** | Delta specs are inherently change-scoped; new delta = new spec. Less drift risk by design. | Each change produces a new delta spec; history of changes tracks evolution. | Specs accumulate as change history (intentional audit trail). | Human authors each delta spec; review at delta level. |
| **Kiro** | Agent hooks execute against tasks; no explicit spec update step when code diverges. | No automated feedback to design.md. | No formal post-initiative cleanup. | In-IDE review of generated spec and tasks before agent proceeds. |

**Summary:** Cicadas is the clear winner with the Reflect loop + Canon synthesis. Everything else is manual or absent. OpenSpec's delta model reduces drift risk structurally but differently — by scoping specs to changes, not by syncing them.

---

## Spec Management

| Method | Storage Model | Lifecycle Tracking | Multi-Initiative Awareness | Spec Expiry |
|---|---|---|---|---|
| **BMAD** | Flat files in git (project-brief.md, prd.md, arch.md, story files). Human-navigated. | No formal state machine; progress tracked by which files exist and story status within them. | None built in. Parallel work coordinated via standard git practices. | Never; docs persist indefinitely and may become stale. |
| **Cicadas** | Structured `.cicadas/` directory: `drafts/` → `active/` → `archive/` + `canon/`. `registry.json` tracks all in-flight initiatives programmatically. | Explicit lifecycle: Emergence → Kickoff → Execution → Completion. `status.py` shows live state. | Registry tracks all concurrent initiatives. `check.py` detects conflicts. Signal broadcasts breaking changes to peer branches. | Designed in: specs expire after initiative completes; canon synthesized from code. |
| **Spec Kit** | `specs/` directory per project. Constitution at root. Per-feature spec files. Convention-based. | No formal state tracking. Phase progression is conversational (CLI commands), not recorded. | No multi-initiative tracking. Each feature spec is independent. | No expiry. Specs persist as static documents. |
| **GSD** | `.planning/` directory with config.json, STATE.md, ROADMAP.md, per-milestone plan files. | STATE.md tracks current phase and milestone; roadmap tracks completion. `roadmap_complete` flag signals done. | Single-project focus; no registry for parallel initiatives. | No expiry. Planning files persist. |
| **TaskMaster** | `.taskmaster/tasks/tasks.json` with all tasks, dependencies, and status. Single task graph per project. | Task status per item (pending/in-progress/done/blocked). Dependency graph tracks sequencing. | No multi-initiative concept; single task graph per codebase. | No expiry; task file is the persistent record. |
| **OpenSpec** | `specs/` for feature specs, `changes/` for deltas. Lightweight, flat structure. | No formal lifecycle; deltas accumulate as a change log. Status tracked per spec file. | No multi-initiative tracking. | No expiry; delta specs accumulate as an audit trail. |
| **Kiro** | IDE-native; specs live as project files in-editor. In-IDE navigation. | IDE manages file state; no separate tracking infrastructure. | No multi-initiative coordination. | No expiry; spec files persist in project. |

**Summary:** Cicadas is the only framework with programmatic spec lifecycle management. Everything else is file-based convention. BMAD at least has a clear folder taxonomy; GSD has STATE.md; Spec Kit and OpenSpec are flat.

---

## Token Management

| Method | Context Injection Strategy | Context Window Discipline | Stale Context Risk |
|---|---|---|---|
| **BMAD** | "Hyper-detailed" story files — full context embedded per story. PO shards PRD into per-epic focused units to limit scope. | No explicit token budget enforcement. Risk of large story files + full arch docs filling context in long sessions. | High. Planning docs don't expire. Old PRD sections can silently conflict with newer implementation decisions. |
| **Cicadas** | Canon summary (300–500 tokens) injected at branch start. Active spec for current initiative only. Detail lives in the code itself. | Architecture is token-aware by design: small snapshot + initiative spec + branch diff fits comfortably in a single agent session. | Low structurally. Specs expire. Canon regenerated after each initiative. Stale context impossible at initiative boundaries. |
| **Spec Kit** | Constitution + current spec file loaded at session start. Compact by design — spec files are meant to be concise. | Implicit; spec files are short but no explicit monitoring or budgeting. | Moderate. Specs persist statically; may drift from implementation without detection. |
| **GSD** | Each execution phase gets a fresh context window built from project artifacts (PROJECT.md, REQUIREMENTS.md, current plan) — not accumulated chat history. Context window monitor hook with WARNING/CRITICAL alerts. | Explicit context isolation architecture: fresh 200k token window per execution unit. Most aggressive token management of any framework. | Low. Fresh context per phase means no accumulation of stale conversation. STATE.md and ROADMAP.md are the persistent state, kept concise. |
| **TaskMaster** | Injects the current task + its dependencies from tasks.json per agent call. Only the relevant task subtree loaded, not the full task graph. | MCP-based injection keeps context tight per task; no full-file loading. | Low per-task. No accumulated conversation state; each task call is fresh. |
| **OpenSpec** | Current spec file + relevant delta for the change being made. Minimal injection surface. | Very light footprint by design; delta specs are small and targeted. | Low. Delta model means each change has its own scoped spec; no monolithic doc to drift. |
| **Kiro** | IDE manages context injection natively via agent hooks; spec files and task context injected automatically per step. | IDE-managed; not directly configurable by user. | Moderate. No explicit expiry or canon synthesis; specs can drift from implementation. |

**Summary:** GSD has the most aggressive token management (fresh context window per execution unit). Cicadas is the most architecturally elegant (compact canon + scoped initiative spec). TaskMaster is efficient per-task via MCP. BMAD is the weakest — hyper-detailed files are a foot-gun at scale.

---

## Git Branch Management

| Method | Branch Model | PR Automation | Cross-Branch Coordination |
|---|---|---|---|
| **BMAD** | Implicit. Stories map to branches by convention; no tooling to enforce or track the binding. | None built in. Developers open PRs via normal git / IDE workflow. | None. Standard git practices and team coordination. |
| **Cicadas** | Explicit and programmatic: Initiative branch → Feature branches (registered) → Task branches (ephemeral). `cicadas kickoff` creates initiative branch; `cicadas branch` registers features. | `cicadas open-pr` supports gh / glab / Bitbucket / fallback. Blocks on BLOCK verdict from `review.md`. | `cicadas signal` broadcasts breaking changes to registered peer branches. `cicadas check` surfaces conflicts proactively. `registry.json` is the live map. |
| **Spec Kit** | No branch management. Spec Kit is branch-agnostic; developers use their own git workflow. | CLI prompt to create a PR via GitHub CLI at end of implementation; optional. | None. |
| **GSD** | Configurable: branch-per-milestone or branch-per-phase options via `/gsd:settings`. Squash merge or merge-with-history at milestone completion. | No native PR creation; relies on git / IDE workflow. Milestone merge is a GSD-managed step. | None beyond milestone merges. |
| **TaskMaster** | No branch management. TaskMaster operates at the task level independent of git workflow. | None. | None. |
| **OpenSpec** | No branch management. Assumes developer uses their own git workflow alongside delta specs. | None. | None. |
| **Kiro** | IDE manages git integration natively; branch creation and PR opening available in-IDE. | In-IDE PR workflow; Kiro can open PRs directly from the IDE. | None beyond IDE git tooling. |

**Summary:** Cicadas is the only framework with a full, programmatic branch lifecycle model. GSD has minimal branch options. Everything else defers entirely to the developer's git workflow.

---

## Builder / Agent Parallelization

| Method | Parallel Execution Model | Planning Parallelism | Orchestration |
|---|---|---|---|
| **BMAD** | Architecturally possible per story (each story is self-contained) but not formally supported. No coordination mechanism across parallel agent runs. | Party Mode: multiple agent personas in one session for multi-perspective collaborative planning. Unique capability. | Orchestrator agent coordinates phase transitions; human drives. `/bmad-help` is interactive guide. |
| **Cicadas** | `approach.md` defines partitions (feature branches) as the explicit unit of parallel work. Multiple builders on independent features simultaneously. Registry prevents overlap. | Subagents (Clarify, UX, Tech, Approach, Tasks) during Emergence — sequential assembly-line, not collaborative. | Chorus manages branch lifecycles and parallel agent coordination. Python scripts as programmable orchestration layer. |
| **Spec Kit** | No parallelization model. Single-feature, sequential implementation. | No multi-agent planning. Single-agent per feature. | No orchestrator; developer sequences commands. |
| **GSD** | Wave-based parallel execution: plans grouped by dependency into waves. Independent plans within a wave run simultaneously; waves are sequential. Four parallel research agents during discuss phase. | Four parallel research agents during discuss/research phase. Plan-checker agent reviews planner output. | Dedicated agents: gsd-planner, plan-checker, wave executors, verifiers, debuggers. Sophisticated multi-agent pipeline within a single session. |
| **TaskMaster** | Dependency-aware task sequencing; independent tasks can be assigned to parallel agent sessions. Dependency graph prevents conflicting work. | Not applicable (consumes PRD, doesn't plan). | MCP server coordinates task assignment across agent sessions. |
| **OpenSpec** | No parallelization model. Single-developer, single-change focus. | No multi-agent planning. | No orchestrator. |
| **Kiro** | No explicit parallelization model. Single-agent per feature in-IDE. | Agent hooks execute sequentially per task. | IDE manages agent hook execution sequence. |

**Summary:** GSD has the most sophisticated intra-session parallelism (wave-based dependency-aware execution). Cicadas has the best cross-session parallelism (registered parallel feature branches). BMAD's Party Mode is uniquely useful for planning. Everything else is sequential.

---

## Tool Use & Ecosystem

| Method | Agent Integrations | Installation | Extensibility | Community & Docs | Maturity |
|---|---|---|---|---|---|
| **BMAD** | Claude Code, Cursor, Windsurf, Augment. IDE-agnostic; works in web UI too. | `npx bmad-method install`. Node 20+. Zero custom code required. | Module system (TEA for testing, Game Dev Studio, Creative Intelligence Suite). BMad Builder for custom agents and workflows. | Docs site, Discord (19k+ members), YouTube, 35k stars, 111 contributors. Best-in-class. | Production (v6 beta). Actively maintained with large community. |
| **Cicadas** | Claude Code, Cursor, Rovodev, Antigravity. Symlink-based agent skill injection. | `curl .../install.sh \| bash --agent claude-code`. Python 3.11+. | Python scripts as orchestration layer; fully extensible. No module ecosystem yet. | README + HOW-TO + dry-run walkthrough. Single author. 5 stars — very early. | v0.5.0. Actively developed. Expect API churn. |
| **Spec Kit** | Claude Code, Gemini CLI, Copilot, Cursor, Windsurf, Kiro CLI, Amp, and 15+ others. Widest agent coverage of any framework. | `npx specify init <project> --ai claude`. Node. One command. | Pluggable preset system; extensions directory; community presets catalog. Actively growing. | GitHub (github org), 76.7k stars, 6.5k forks, 536 open issues. Good docs site. Most momentum in ecosystem. | Production. Rapid release cadence. GitHub-backed. |
| **GSD** | Claude Code (primary), OpenCode, Gemini CLI, Codex. Cross-runtime via community ports. | `npx get-shit-done-cc --global`. Node. | Agent-level model overrides (Opus/Sonnet/Haiku per agent). Config-driven feature toggles. 11 installer domain modules. | 29.9k stars, 2.5k forks, 164 open PRs, very active. Medium/blog coverage. | Production. Very active release cadence (daily/weekly releases). |
| **TaskMaster** | Cursor, Lovable, Windsurf, Roo, Claude Code. MCP server as integration point — works with any MCP-capable agent. | `npx task-master-ai` or MCP server config. Node. | Task rules and complexity profiles are configurable. MCP integration means any tool can connect. | 25.9k stars, 2.5k forks. Docs at tryhamster.com. Active community. | Stable. Slower release cadence than GSD/Spec Kit; deliberate API. |
| **OpenSpec** | Claude Code, Cursor, Copilot, Gemini, and others. Tool-agnostic by design — no integration requirements. | `npx openspec init`. Node. Lightest footprint of any option. | Delta spec schema is extensible. Minimal core — easy to wrap with custom tooling. | 23.8k stars, 2k forks. openspec.dev docs site. Moderate community activity. | Stable. Active but measured pace. |
| **Kiro** | Native to Kiro IDE (VS Code base). Agent hooks system for any language/framework. | Download Kiro IDE. No additional install. | Agent hooks are extensible via YAML config. Steering documents customize agent behavior. | AWS-backed. No public star count (hosted IDE). Docs at kiro.dev. Preview-stage community. | Free preview. AWS-backed suggests long-term investment but also platform dependency risk. |

**Summary:** Spec Kit has the widest ecosystem momentum (76.7k stars, GitHub-backed, 15+ agent integrations). BMAD has the deepest community and documentation. GSD is the most actively developed. Cicadas is very early but uniquely architectured. Kiro has AWS backing but IDE lock-in.

---

## Decision Matrix

### Choose by primary pain point

| Pain Point | Best Fit | Runner-Up |
|---|---|---|
| "We start building before we know what we're building" | BMAD | Spec Kit |
| "Our specs drift from reality within days" | Cicadas | GSD |
| "Context rot kills quality in long agent sessions" | GSD | Cicadas |
| "I need something I can learn in an hour and ship today" | Spec Kit | GSD |
| "We're adding features to a legacy codebase" | OpenSpec | Cicadas |
| "I need to coordinate multiple parallel feature initiatives" | Cicadas | GSD |
| "My team needs governance, audit trail, and traceability" | BMAD | Spec Kit |
| "I want a task management layer on top of my existing method" | TaskMaster | — |
| "I want everything in one box and I'm AWS-native" | Kiro | — |

### Choose by team profile

| Profile | Recommendation |
|---|---|
| Solo dev, ship fast, experienced | GSD |
| Solo dev, organized, brownfield | OpenSpec |
| Small team (2–5), feature work | Spec Kit + TaskMaster |
| Experienced principal / tech lead | Cicadas |
| Enterprise team, greenfield product | BMAD |
| Enterprise team, ongoing product | BMAD (planning) + Cicadas or GSD (execution) |
| AWS shop, wants all-in-one | Kiro |

### Composable combinations that work well

- **BMAD + TaskMaster**: BMAD for methodology and planning depth; TaskMaster for dependency-aware task orchestration during implementation. Popular combination.
- **BMAD + Spec Kit**: BMAD planning artifacts (PRD, architecture) as input to Spec Kit's `/specify` command for feature-level implementation. Hybrid approach.
- **Cicadas + Spec Kit**: Spec Kit for quick Emergence-phase spec generation; Cicadas for execution machinery (branch management, Reflect, canon synthesis).
- **GSD + Spec Kit**: Spec Kit spec files as input to GSD's discuss phase. GSD handles context-isolated execution; Spec Kit handles spec structure.
- **Any method + TaskMaster**: TaskMaster's MCP server slots in as a task management layer alongside any planning framework.

---

## Quick Reference

| | BMAD | Cicadas | Spec Kit | GSD | TaskMaster | OpenSpec | Kiro |
|---|---|---|---|---|---|---|---|
| **Stars** | 35k | 5 | 76.7k | 29.9k | 25.9k | 23.8k | — |
| **Runtime** | Node 20+ | Python 3.11+ | Node | Node | Node | Node | Hosted IDE |
| **Spec philosophy** | Living product docs | Disposable scaffolding | Feature spec + constitution | Phase plans + state | PRD → task graph | Delta-per-change | IDE-generated spec |
| **Token strategy** | Hyper-detailed story files | Compact canon snapshot | Short feature specs | Fresh context per phase | Task-scoped MCP injection | Delta-scoped specs | IDE-managed |
| **Spec-code sync** | Manual | Automated (Reflect) | None | STATE.md tracking | Task completion flags | Delta model (structural) | None |
| **Branch management** | Convention | Programmatic + Signal | None | Configurable milestones | None | None | IDE-native |
| **Parallelism** | Ad hoc | Registered feature branches | None | Wave-based + dependency graph | Dependency-sequenced tasks | None | None |
| **Best spec depth** | Product-level | Initiative-level | Feature-level | Phase-level | Task-level | Change-level | Feature-level |
| **Ecosystem** | ★★★★★ | ★ | ★★★★★ | ★★★★ | ★★★★ | ★★★ | ★★ (preview) |
| **Brownfield** | ★★★★ | ★★★★ | ★★ | ★★★★ | ★★★ | ★★★★★ | ★★ |
| **Greenfield 0→1** | ★★★★★ | ★★★★ | ★★★★ | ★★★★ | ★ (not standalone) | ★★ | ★★★★ |
| **Learning curve** | Steep | Moderate | Flat | Flat–moderate | Low | Flat | Flat |

---

*Sources: GitHub repos (BMAD-METHOD, ecodan/cicadas, github/spec-kit, gsd-build/get-shit-done, eyaltoledano/claude-task-master, Fission-AI/OpenSpec), Kiro documentation, and secondary analysis from Augment Code, Obvious Works, DEV Community, and Medium. Star counts as of March 2026.*