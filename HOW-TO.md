# Chorus & Cicadas: The Definitive Guide

Welcome to the Cicadas methodology. This guide explains the core concepts, directory structure, and conversational workflows managed by the **Chorus Agent**.

---

## 🧠 Core Concepts

| Term | Definition |
| :--- | :--- |
| **Incubator** | The "pre-natal" phase. Rough drafts (PRDs, tech designs) live here before work starts. |
| **Hatch** | Promoting incubator docs into a shared **Brood** or a specific **Branch**. |
| **Brood** | A collection of synchronized branches sharing a "**Provisional Canon**" (shared initiative spec). |
| **Branch** | An individual line of development linked to specific modules and tasks. |
| **Forward Docs** | Transient requirements (PRDs, Approach, Tasks) that expire after implementation. |
| **Canon** | The permanent, authoritative documentation reverse-engineered from the code + rationale. |
| **Synthesis** | The process where the Agent updates the Canon after reading code changes and forward docs. |

---

## 📁 Directory Structure (`.cicadas/`)

```text
.cicadas/
├── registry.json      # Global state of branches, broods, and module owners.
├── index.json         # Historical log of every merge and synthesis.
├── incubator/         # [PHASE 0] Unrefined specs and ideas.
├── forward/           # [PHASE 1] Active requirements guiding branches.
│   └── broods/        # Shared "provisional canon" for initiatives.
├── canon/             # [PHASE 2] Permanent architectural snapshots.
│   └── modules/       # Per-module deep dives.
└── archive/           # [CLOSED] The "husks" of completed work.
```

---

## 🤖 Agents & Skills

You don't run scripts; you talk to the **Chorus Agent** in your TUI. It uses specialized skills:

1.  **Emergence Agent**: Helps you clarify requirements and design UX/Tech. Uses the section-by-section drafting protocol.
2.  **Implementation Agent**: The actual developer. Focuses on `tasks.md` and writing code.
3.  **Synthesis Agent**: The architect. Reads code and forward docs to update the permanent Canon.

---

## 🚀 The Three Paths

### 🟢 1. Greenfield: Initial Launch
- **Incubate**: Talk to the agent to draft your MVP specs in the incubator.
- **Hatch**: Tell the agent: *"Hatch the 'mvp' brood."*
- **Branch**: *"Start an 'api' branch linked to the 'mvp' brood."*

### 🟠 2. Brownfield: New Release / Large Feature
- **Context**: The agent reads the existing **Canon** to understand the baseline.
- **Cycle**: Follow the same Incubate -> Hatch -> Branch flow for the new release delta.

### 🔵 3. Bootstrap: Migrating a Legacy Project
- **Initialize**: `python scripts/chorus/scripts/init.py`.
- **Lexical Discovery**: *"Scan this legacy project and tell me what the architecture looks like."*
- **Canonize**: *"Synthesize a baseline Canon from these files."*
- **Reference**: See [REVERSE_ENGINEERING.md](./scripts/chorus/REVERSE_ENGINEERING.md) for deeper details.

---

## 🚀 Sample Flow: Building a "Social Feed"

1.  **Drafting**: *"Clarify the requirements for a Social Feed."* (Agent drafts in `incubator/` section-by-section).
2.  **Hatching**: *"Hatch this as the 'v1-feed' brood."* (Docs move to `forward/broods/v1-feed/`).
3.  **Branching**: *"Start a branch called 'feed-db' linked to 'v1-feed'."* (Agent creates branch + local task list).
4.  **Coding**: Agent implements the schema based on the brood's Tech Design.
5.  **Synthesizing**: *"Done. Update the canon."* (Agent updates `canon/modules/feed.md` and archives the branch).

> [!IMPORTANT]
> Always initialize a new project with `python scripts/chorus/scripts/init.py` before starting your first interaction.
