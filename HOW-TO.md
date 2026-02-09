# Chorus & Cicadas: The Definitive Guide

Welcome to the Cicadas methodology. This guide explains the core concepts, directory structure, and conversational workflows managed by the **Chorus Agent**.

---

## 🧠 Core Concepts

| Term | Definition |
| :--- | :--- |
| **Incubator** | The "pre-natal" phase. Rough drafts (PRDs, tech designs) live here before work starts. |
| **Hatch** | The act of promoting incubator docs into a shared **Brood** or a specific **Branch**. |
| **Brood** | A collection of synchronized branches sharing a "Provisional Canon" (like a shared MVP spec). |
| **Branch** | An individual line of development linked to specific modules and tasks. |
| **Forward Docs** | Transient requirements (PRDs, Approach, Tasks) that guide development but *expire* after implementation. |
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
3.  **Synthesis Agent**: The architect. Reads your code and forward docs to update the permanent Canon.

---

## 💬 How to Invoke the Agent

Simply tell the agent your **intent** in the console.

- **To start an idea**: *"Help me clarify the requirements for a new [Feature Name]."*
- **To start an initiative**: *"Everything looks good. Hatch the [Initiative Name] brood from the incubator."*
- **To start a feature**: *"Start a branch for [Member-Feature] and link it to the [Initiative Name] brood."*
- **To merge work**: *"I'm done with these changes. Synthesize the docs and archive the branch."*

---

## 🚀 Sample Flow: Building a "Social Feed"

1.  **Drafting**: 
    - You: *"Clarify the requirements for a Social Feed."*
    - Agent: Drafts a PRD in `incubator/social-feed/` one section at a time, asking you for feedback.
2.  **Hatching**: 
    - You: *"Hatch this as the 'v1-feed' brood."*
    - Agent: Moves docs to `forward/broods/v1-feed/`.
3.  **Branching**: 
    - You: *"Start a branch called 'feed-db' linked to 'v1-feed'."*
    - Agent: Creates git branch and a local `forward/feed-db/tasks.md`.
4.  **Coding**: 
    - Agent: Implements the database schema based on the brood's Tech Design.
5.  **Synthesizing**:
    - You: *"Done. Update the canon."*
    - Agent: Reads the code, updates `canon/modules/feed.md`, and archives the `feed-db` folder.

> [!IMPORTANT]
> Always initialize a new project with `python scripts/chorus/scripts/init.py` before starting your first interaction.
