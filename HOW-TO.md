# Cicadas: The Definitive Guide (v2.1)

Welcome to the Cicadas methodology. This guide explains how to install Cicadas, initialize your project, and follow the Cicadas workflow for both new and existing codebases.

---

## 🚀 Installation & Setup

### 1. Install Cicadas

**One-liner** (requires Python 3.11+, `curl`, `unzip`, and a `git` repo):

```bash
curl -fsSL https://raw.githubusercontent.com/ecodan/cicadas/master/install.sh | bash
```

This will:
1. Check for Python 3.11+ (and print OS-specific guidance if missing)
2. Download and extract Cicadas into `.cicadas-skill/cicadas/` (configurable with `--dir`)
3. Initialize the `.cicadas/` workspace
4. Optionally set up your AI coding agent integration

**With agent integration** (skips interactive prompt):
```bash
# Claude Code
curl -fsSL https://raw.githubusercontent.com/ecodan/cicadas/master/install.sh | bash -s -- --agent claude-code

# Cursor
curl -fsSL https://raw.githubusercontent.com/ecodan/cicadas/master/install.sh | bash -s -- --agent cursor
```

**All flags:**
```
--dir <path>     Install location (default: .cicadas-skill/cicadas/)
--agent <list>   Agent integrations: claude-code, antigravity, cursor, none (comma-separated)
--update         Re-download skill files only; never touches .cicadas/
```

**Supported agent integrations:**

| Agent | What gets created |
|-------|------------------|
| `claude-code` | `.claude/skills/cicadas` → symlink to install dir |
| `antigravity` | `.agents/skills/cicadas` → symlink to install dir |
| `cursor` | `.cursor/rules/cicadas.mdc` (copy of `skill.md`) |

### 2. Update Cicadas

To refresh the Cicadas skill files without touching your `.cicadas/` workspace:

```bash
bash install.sh --update
```

Or re-run the one-liner with `--update`:
```bash
curl -fsSL https://raw.githubusercontent.com/ecodan/cicadas/master/install.sh | bash -s -- --update
```

---

## 🧠 Core Concepts & Hierarchy

### Branching Model

Cicadas uses a two-layer branching hierarchy to manage concurrent work and ensure documentation integrity:

1.  **Initiative Branch (`initiative/{name}`)**: A long-lived branch created at **Kickoff**. It serves as the integration point for all code in a release. No documentation is synthesized here.
2.  **Feature Branch (`feat/{name}`)**: A registered branch for a specific **Partition** (defined in the Approach). It forks from the Initiative branch and merges back when the partition is complete.
3.  **Task Branch (`task/{feat}/{name}`)**: (Optional) Ephemeral, unregistered branches for individual PRs into a feature branch.

### Terminology

| Term | Definition |
| :--- | :--- |
| **Canon** | Authoritative documentation reverse-engineered from code + rationale. Lives in `.cicadas/canon/`. |
| **Drafts** | Staging area for new requirements before work starts (`.cicadas/drafts/`). |
| **Active Specs** | The living requirements driving current work (`.cicadas/active/`). |
| **Approach** | The strategy doc where you define the **Initiative** and its **Partitions**. |
| **Reflect** | Keeping active specs in sync with code *during* development. |
| **Signal** | Broadcasting breaking changes to other peer branches. |
| **Synthesis** | Overwriting Canon on `main` at the end of an initiative. |

---

## 📁 Directory Structure (`.cicadas/`)

```text
.cicadas/
├── config.json        # Local configuration.
├── registry.json      # Global state of active initiatives and feature branches.
├── index.json         # Append-only history of all completed feature branches.
├── canon/             # Authoritative snapshots of the system.
├── drafts/            # Staging area for upcoming initiatives.
├── active/            # Living specs for in-flight work.
└── archive/           # Expired specs from completed initiatives.
```

---

## 🟢 Greenfield: Starting a New Project

1.  **Initialize**: *"Initialize cicadas for this project."*
2.  **Clarify**: *"I want to build [Product Name]. Help me clarify the requirements."*
3.  **Draft Appearance**: Use prompts like *"Draft the UX"* and *"Draft the tech design"*.
4.  **Define Strategy (Approach)**: *"Draft the approach."*
    - **Note**: This is where you define the **Partitions** (future Feature Branches).
5.  **Draft Tasks**: *"Draft the tasks."*
6.  **Kickoff**: *"Kickoff [initiative-name]."*
    - Agent promotes drafts to active and creates the **Initiative Branch**.
7.  **Implementation Loop**:
    - **Start Feature**: *"Start feature [partition-name]."* (Forks from Initiative Branch).
    - **Reflect**: The Agent keeps specs current as you build.
    - **Complete Feature**: Merges back to the Initiative Branch.
8.  **Complete Initiative**: *"Complete initiative [initiative-name]."*
    - Merges Initiative Branch to `main`, **Synthesizes** the Canon on `main`, and **Archives** the specs.

---

## 🔵 Bootstrap: Migrating a Legacy Project

If you are starting with an existing codebase that lacks Cicadas documentation, use the Bootstrap workflow to bring it into the methodology.

1.  **Initialize**: *"Initialize cicadas for this project."*
2.  **Bootstrap**: *"Bootstrap the baseline Canon."*
    - The Agent autonomously performs code discovery, synthesizes a full suite of docs (PRD, UX, Tech, Modules) using templates, and validates them against the code.
3.  **Reference**: See the **Bootstrap Subagent** instructions in `{cicadas root}/emergence/bootstrap.md` for a deep-dive on legacy migration.

---

## 🟠 Brownfield: New Features (Canon-Aware)

1.  **Read Canon**: The Agent uses existing `.cicadas/canon/` as context automatically.
2.  **Draft Delta**: *"I want to add [Feature X]."* (Agent authors specs aware of the existing system).
3.  **Standard Cycle**: Follow the Approach -> Kickoff -> Feature loop.
4.  **Update Canon**: Synthesis on `main` **updates** the existing Canon with the new reality.

---

## 🟡 Lightweight Paths (Fixes & Tweaks)

For trivial changes, Cicadas supports a "fast path" that reduces documentation overhead.

-   **Fix**: An isolated defect with no architectural impact.
-   **Tweak**: A small enhancement requiring < 100 lines of code.

**Workflow**:
1.  **Draft**: *"Draft the buglet"* or *"Draft the tweaklet"*.
2.  **Kickoff**: Promotes the single spec to active.
3.  **Branch**: Forks directly from `main`.
4.  **Complete**: Merge to `main`, optionally update Canon, and Archive.

**Aborting a Lightweight Path**: Say *"Abort"* at any point. The agent runs `abort.py` from the current branch, rolls back the branch and registry entry, and prompts whether to move the promoted spec back to drafts or delete it entirely.

---

## 🤖 Agents & Skills

- **Emergence Agent**: Authors specs (PRD, UX, Tech, Approach, Tasks).
- **Implementation Agent**: Focuses on `tasks.md` and writing code.
- **Synthesis Agent**: Operates on `main` to update the authoritative Canon.

### Registering Cicadas as a Claude Code Skill

To use Cicadas as a native Claude Code skill (enabling auto-invocation and the `/cicadas` slash command), register it by symlinking the skill directory into `.claude/skills/`:

```bash
mkdir -p .claude/skills
ln -s ../../{cicadas-dir} .claude/skills/cicadas
```

Where `{cicadas-dir}` is the relative path from `.claude/skills/` to wherever you installed the Cicadas scripts (e.g., `../../.cicadas-skill/cicadas`).

Alternatively, copy or symlink the directory directly:

```bash
# If installed at the default location:
mkdir -p .claude/skills
ln -s ../../.cicadas-skill/cicadas .claude/skills/cicadas
```

Once registered, Claude Code will automatically load the skill and recognize Cicadas lifecycle commands like "kickoff", "start feature", and "check status".

> [!IMPORTANT]
> The **Code is the single source of truth**. Specs are active inputs that expire once implemented, while Canon is the permanent record synthesized from reality.

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
