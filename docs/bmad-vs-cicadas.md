# BMAD Method vs Cicadas: A Deep Comparison

> Research compiled March 2026. Sources: BMAD-METHOD repo (bmad-code-org/BMAD-METHOD, v6 beta), Cicadas repo (ecodan/cicadas, v0.5.0), archived initiative specs, dry-run walkthrough, and BMAD documentation site.

---

## Overview

Both frameworks address the same core problem: agentic AI coding tools produce inconsistent results without structured context and process. They diverge sharply on *where* that structure lives and what happens to it after the work is done.

**BMAD** (Breakthrough Method for Agile AI-Driven Development) is a comprehensive planning and process framework built around a team of specialized AI agents (PM, Architect, Scrum Master, Developer, QA, etc.) that guide humans through a structured, document-heavy development lifecycle. Specs are living artifacts that persist alongside code.

**Cicadas** (Sustainable Spec-Driven Development) inverts this. Forward-looking specs — PRDs, designs, task lists — are treated as *disposable scaffolding* that drives implementation and then expires. After each initiative, authoritative documentation is reverse-engineered from the code itself. Code is truth; specs are fuel.

Neither philosophy is wrong. They solve different problems and optimize for different failure modes.

---

## Philosophy Comparison

| | BMAD | Cicadas |
|---|---|---|
| **Core belief** | Specs are living truth alongside code | Specs are disposable inputs; code is truth |
| **Failure mode addressed** | "We don't know what we're building before we build it" | "Specs drift from reality and become lies" |
| **Optimized for** | Upfront clarity, stakeholder alignment, governance | Execution discipline, spec-code sync, parallel work coordination |
| **Relationship to code** | Specs inform code; humans keep them in sync | Code informs canon; AI synthesizes docs post-merge |

---

## Feature-by-Feature Comparison

### Spec Creation

| Dimension | BMAD | Cicadas |
|---|---|---|
| **Process depth** | Full agent chain: Analyst → PM → Architect → PO, with guided elicitation and probing questions. PRDs run 15–25 pages, architecture 10–20 pages. | Subagent ensemble (Clarify, UX, Tech, Approach, Tasks) drafts in `.cicadas/drafts/`. Supports Q&A, requirements doc, or Loom transcript as inputs. |
| **Spec artifact set** | project-brief.md, prd.md, architecture.md, sharded epics, per-story files | prd.md, tech-design.md, approach.md, tasks.md — per initiative |
| **Spec scope** | Product-level (covers the whole thing) | Initiative-level (scoped tightly to what's being built now) |
| **Spec quality** | Deep and comprehensive, but padded — AI generates a lot of ceremony alongside the signal | Equally rigorous within its scope — same intellectual content (exec summary, user journeys, FRs, NFRs, ADRs, implementation sequence), tighter surface area |
| **Quality gates** | PO runs alignment checklists between PRD and architecture before sharding | Reflect enforces spec-code sync during execution; Code Review produces structured PASS/BLOCK verdict pre-PR |
| **Canon / living docs** | PRD + arch docs maintained throughout; human curates updates | Canon auto-synthesized from code + expired spec intent post-merge; 300–500 token summary injected at branch start. Never manually maintained. |

**Edge** Split. The difference is scope, not rigor. BMAD PRDs cover the product; Cicadas PRDs cover the initiative. For a focused feature, Cicadas spec quality is equivalent.

---

### Flexibility Across Work Size

| Work Type | BMAD | Cicadas |
|---|---|---|
| **Bugs / hotfixes** | Quick flow: `/quick-spec` → `/dev-story` → `/code-review`. Still somewhat ceremonious for a 5-line fix. | First-class "tweak" path in the standard start flow. Name → minimal draft → branch. Cleaner for tiny work. |
| **Minor features / refactors** | Quick flow handles it; phases 1–3 explicitly skippable | Initiative vs. tweak distinction built into start flow. Same toolchain, lighter artifact set. |
| **0→1 / greenfield** | Best-in-class: Brief → PRD → Architecture → Epics → Stories. Scale-adaptive intelligence adjusts planning depth per domain type (SaaS vs. medical system, etc.). | Emergence phase with subagents drafts approach.md defining partitions. Less prescriptive upfront — works but requires more self-direction from the builder. |
| **Brownfield / enhancement** | Explicit brownfield workflow: Analyst reviews existing code → Architect designs enhancement fitting current patterns → SM creates migration-aware stories. | Naturally supported via existing canon snapshot for context. Signal handles cross-branch impact. Less scaffolding for the "don't break things" problem. |

**Edge:** BMAD for greenfield and brownfield due to explicit workflow scaffolding. Cicadas for bugs and tweaks due to first-class lightweight paths.

---

### Round-Trip Process

| Dimension | BMAD | Cicadas |
|---|---|---|
| **Spec ↔ code sync** | Human-driven. Story files carry context; divergence handled by editing docs or re-doing the story. No automated enforcement. | **Reflect** is a first-class, mandatory step: when code diverges from plan, active specs update immediately — enforced before every commit on feat/task branches. |
| **Feedback to planning docs** | Not structurally built in. Artifacts stay static post-creation unless humans update them (they don't). | Reflect loop + post-merge Synthesis creates a permanent record of intent vs. what was actually built. Future branches start from canon, not stale planning docs. |
| **Human-in-loop checkpoints** | Explicit review steps between major phases. Agents prompt for approval before proceeding. Very deliberate. | PR preference configurable at kickoff. Code Review verdict (PASS/BLOCK) is automated. Human review is optional; system functions without it. |
| **Post-initiative cleanup** | No formal process. Docs persist in place and may drift. | Archive step moves active specs to `.cicadas/archive/`. Canon synthesized fresh. Registry updated. Clean slate for next initiative. |

**Edge:** Cicadas wins decisively on round-trip discipline. The Reflect loop is the most important missing feature in BMAD.

---

### Spec Management

| Dimension | BMAD | Cicadas |
|---|---|---|
| **Storage model** | Docs in git (project-brief.md, prd.md, arch.md, story files). Flat structure, human-navigated. | Structured `.cicadas/` directory: `drafts/` → `active/` → `archive/` + `canon/`. `registry.json` tracks all in-flight initiatives. Programmatic, not just convention. |
| **Lifecycle tracking** | No formal state machine. Progress tracked by which files exist and story status within files. | Explicit lifecycle: Emergence → Kickoff → Execution → Completion. `status.py` shows Merged/Next. `registry.json` is the system of record. |
| **Multi-initiative awareness** | Not structurally addressed. Parallel work coordinated via standard git practices. | Registry tracks all concurrent initiatives. `check.py` detects cross-branch conflicts. `signal.py` broadcasts breaking changes to peer branches explicitly. |

**Edge:** Cicadas wins on spec management infrastructure. BMAD relies on convention; Cicadas relies on structure.

---

### Token Management

| Dimension | BMAD | Cicadas |
|---|---|---|
| **Context injection strategy** | "Hyper-detailed" story files — full context embedded. PO shards PRD and architecture into per-epic focused units. | Canon summary (300–500 tokens) injected at branch start. Active spec for current initiative only. Detail lives in the code itself. |
| **Context window discipline** | No explicit token budget enforcement. Risk of large story files + full arch docs filling context early in long sessions. | Architecture: small canon snapshot + initiative spec + current branch diff. Designed to fit comfortably in a single coding agent session. Token-aware by design. |
| **Stale context risk** | Planning docs don't expire. Old PRD sections can silently conflict with newer implementation decisions. | Specs expire. Canon regenerated after each initiative. Stale context is structurally impossible at initiative boundaries. |

**Edge:** Cicadas wins on token management. This is a meaningful practical advantage at scale — BMAD's "hyper-detailed story files" approach is a foot-gun in long sessions.

---

### Git Branch Management

| Dimension | BMAD | Cicadas |
|---|---|---|
| **Branch model** | Implicit. Stories map to branches by convention. No tooling to enforce or track the binding. | Explicit: Initiative branch → Feature branches (registered) → Task branches (ephemeral). `kickoff.py` creates initiative branch. `branch.py` registers feature branches. Fully programmatic. |
| **PR automation** | Not built in. Developers open PRs via normal git / IDE workflow. | `open_pr.py` supports gh / glab / Bitbucket / fallback. Blocks on BLOCK verdict from `review.md`. PR creation is a first-class workflow step. |
| **Cross-branch coordination** | None built in. Teams use standard PR review and merge conflict resolution. | Signal broadcasts breaking changes to registered peer branches. `check.py` surfaces conflicts proactively. Registry provides a live map of what's in flight. |

**Edge:** Cicadas wins decisively on branch management. BMAD's model is "trust git and the team." Cicadas' model is enforceable infrastructure.

---

### Builder / Agent Parallelization

| Dimension | BMAD | Cicadas |
|---|---|---|
| **Parallel story execution** | Architecturally possible (each story is self-contained) but not formally supported. No coordination mechanism across parallel agent runs. | `approach.md` explicitly defines partitions / feature-branches as the unit of parallelization. Multiple agents can work on independent features simultaneously. Registry prevents overlap. |
| **Multi-agent planning** | **Party Mode**: multiple agent personas in one session for collaborative planning, troubleshooting, multi-perspective discussion. Unique and genuinely useful for complex design decisions. | Subagents (Clarify, UX, Tech, Approach, Tasks) operate during Emergence. More assembly-line than party — each contributes their artifact in sequence. |
| **Orchestration model** | Orchestrator agent coordinates phase transitions. Human drives; agents advise. `/bmad-help` is the interactive guide. | Cicadas manages branch lifecycles and parallel agent coordination. Python scripts are the orchestration layer — programmable, not just conversational. |

**Edge:** Split. BMAD's Party Mode is genuinely novel for planning. Cicadas' parallel execution model is more robust for actual build parallelism.

---

### Tool Use & Ecosystem

| Dimension | BMAD | Cicadas |
|---|---|---|
| **Agent integrations** | Claude Code, Cursor, Windsurf, Augment. npm-installed. Works in web UI or IDE. | Claude Code, Cursor, Rovodev, Antigravity. Bash-installed. Symlink-based agent skill injection. |
| **Tooling footprint** | Node.js 20+. Markdown + YAML. Zero custom code required. | Python 3.11+. Python scripts as the orchestration layer. More programmable surface area; users can extend scripts. |
| **Extensibility** | Module system (TEA for testing, Game Dev Studio, Creative Intelligence Suite). BMad Builder for custom agents and workflows. | Small, focused, single-author. Open Apache 2.0. Extensible via Python scripts. No module ecosystem yet. |
| **Community & docs** | Extensive: full docs site, Discord, YouTube, 35k stars, 111 contributors. Mature ecosystem. | README + HOW-TO + dry-run walkthrough. Good for a solo project. No community infrastructure yet. (5 stars — early.) |
| **Maturity** | Production-ready. v6 beta actively developed with large community. | v0.5.0. Actively developed, single-author. Expect API churn. |

**Edge:** BMAD wins on ecosystem and maturity. Not close.

---

## Strengths & Gaps Summary

### BMAD: Strengths

- **Best-in-class upfront planning.** The full greenfield path (Brief → PRD → Architecture → Epics → Stories) with guided agent elicitation is genuinely good at surfacing what you're building before you build it. Scale-adaptive intelligence adjusts depth per domain type.
- **Explicit brownfield workflow.** Dedicated scaffolding for adding features to existing systems without breaking things.
- **Party Mode.** Running multiple agent personas in one planning session surfaces contradictions and competing perspectives in a way that mirrors good design reviews.
- **Ecosystem.** Documentation, community, modules, and tooling are mature. BMAD has 35k stars for a reason — it's approachable and well-explained.
- **Zero custom code.** Markdown + YAML + npm. Lower barrier to entry.

### BMAD: Gaps

- **Spec drift is structurally inevitable.** There's no automated mechanism to keep specs honest as implementation evolves. By sprint 2, the PRD is already lying to you.
- **Token management is an afterthought.** "Hyper-detailed story files" is a marketing term for "we put everything in one place and hope it fits." For complex, long-running sessions, this is a real problem.
- **No branch management infrastructure.** Branch-to-story binding is convention, not enforcement. Parallel initiative coordination doesn't exist.
- **Spec weight vs. signal ratio.** A 20-page BMAD PRD contains maybe 3–5 pages of actual signal for an experienced engineer. The rest is AI-generated ceremony.
- **Post-initiative cleanup.** No formal process. Docs persist in place, may conflict with newer decisions, and nobody updates them.

---

### Cicadas: Strengths

- **Reflect loop is the killer feature.** Mandatory spec-code sync at every commit boundary, enforced pre-commit. This is the single most important operational discipline BMAD is missing.
- **Canon synthesis.** Post-merge, an AI agent reads the code + expired spec intent and generates authoritative documentation. Never manually maintained. Stale context is structurally impossible at initiative boundaries.
- **Token-aware architecture.** 300–500 token canon snapshot at branch start. Initiative-scoped active specs. Designed for real coding agent session constraints.
- **Branch management as infrastructure.** `kickoff.py`, `branch.py`, `open_pr.py`, `signal.py`, `check.py`, `registry.json` — the entire branch lifecycle is programmatic and coordinated.
- **Parallelization by design.** `approach.md` explicitly defines partitions as the unit of parallel work. Registry prevents overlap. Multiple agents on multiple features is a first-class pattern.
- **Spec rigor at initiative scope.** Despite the "specs are disposable" philosophy, actual Cicadas specs are rigorous — prd.md, tech-design.md, approach.md, tasks.md — just scoped to the initiative rather than the product. Same intellectual content, smaller surface area.
- **Code review as a first-class operation.** Structured PASS/BLOCK verdict from a spec-anchored review, not just a generic lint pass.

### Cicadas: Gaps

- **Greenfield planning scaffold is thinner.** The Emergence phase doesn't give you as much structured guidance for 0→1 work as BMAD's full agent chain. You need to bring more self-direction.
- **Brownfield workflow is implicit.** The existing canon provides context, but there's no explicit scaffolding for "here's how to add a feature without breaking things."
- **Ecosystem is nascent.** Single-author, v0.5.0, 5 stars. Expect API churn. No community, no modules, no YouTube tutorials.
- **Python runtime dependency.** Requires Python 3.11+. For teams not already Python-native, this adds friction.
- **No Party Mode / multi-perspective planning.** Emergence subagents are sequential, not collaborative. No mechanism for running multiple agent personas to surface design contradictions.

---

## When to Choose Each

### Choose BMAD when:

- You're building something **genuinely net-new** (0→1) with significant domain uncertainty — you need the upfront elicitation discipline
- You have **multiple stakeholders** who need to align on requirements before a line of code is written
- You're working with **junior engineers or agents that need heavy guardrails** — BMAD's story file verbosity is a feature in this context
- You want **comprehensive module support** — test strategy (TEA), game development, creative workflows
- You need something **approachable and well-documented** with community support
- You're an individual contributor who wants a guide through the process, not infrastructure to deploy

### Choose Cicadas when:

- You're an **experienced engineer with clear domain knowledge** — you don't need 20 pages of guided elicitation to know what you're building
- You're running **multiple parallel initiatives** and need coordination infrastructure
- **Spec drift is your primary pain point** — the Reflect loop directly addresses this
- You want **token-efficient agent sessions** — canon snapshots and initiative-scoped specs fit comfortably in context windows
- You're comfortable with **Python and CLI tooling** and want programmable orchestration over conversational guidance
- You care about **long-term codebase health** — canon synthesis ensures docs reflect what was actually built, not what was planned

### The synthesis option:

These frameworks are not architecturally incompatible. The dream move is:

1. Use **BMAD's Emergence/planning depth** for greenfield 0→1 work — let the PM and Architect agents do the upfront heavy lifting
2. Use **Cicadas' execution machinery** from Kickoff onward — branch model, Reflect loop, canon synthesis, Signal, PR automation

Cicadas has a `requirements.md` input path in Emergence that could trivially accept a BMAD-generated PRD as input. The planning artifacts from BMAD become the requirements source that drives Cicadas' Emergence phase, and then Cicadas takes over for everything operational.

For ongoing brownfield work (adding features, fixing bugs, refactoring) on an established codebase, Cicadas alone is the better fit. The canon already exists; you don't need BMAD's upfront planning infrastructure.

---

## Quick Reference

| | BMAD | Cicadas |
|---|---|---|
| **Install** | `npx bmad-method install` | `curl -fsSL .../install.sh \| bash --agent claude-code` |
| **Runtime** | Node.js 20+ | Python 3.11+ |
| **License** | MIT | Apache 2.0 |
| **Stars** | 35k | 5 |
| **Maturity** | Production (v6 beta) | Early (v0.5.0) |
| **Spec philosophy** | Living documents | Disposable scaffolding |
| **Spec scope** | Product-level | Initiative-level |
| **Branch management** | Convention | Programmatic infrastructure |
| **Spec-code sync** | Manual | Automated (Reflect) |
| **Post-initiative docs** | Manual | Auto-synthesized (Canon) |
| **Token strategy** | Hyper-detailed story files | Compact canon snapshot |
| **Parallelization** | Ad hoc | First-class (approach.md partitions) |
| **Best for** | Greenfield, stakeholder alignment, guided process | Experienced teams, brownfield, parallel execution, spec discipline |

---

*Report compiled from: BMAD-METHOD v6 beta GitHub repo, BMAD documentation site (docs.bmad-method.org), Cicadas v0.5.0 GitHub repo, archived initiative specs (`.cicadas/archive/`), dry-run walkthrough, and secondary analysis articles.*