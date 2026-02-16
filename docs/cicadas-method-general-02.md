# Cicadas Method (v2)

## A Methodology for Sustainable Spec-Driven Development

### Implementation Manual

---

## Part 1: Summary of the Approach

### The Problem

Traditional Spec-Driven Development (SDD) works well on the first pass but degrades over time:

1. **Documentation entropy**: Every code change must back-propagate to specs, creating exponential maintenance burden.
2. **Waterfall assumptions**: SDD assumes requirements are known before implementation, but real design is emergent.
3. **Single-threaded model**: SDD doesn't address concurrent work by multiple humans and AI agents.
4. **Stale context**: LLMs confidently generate from outdated specs, producing incorrect code.
5. **Spec drift during implementation**: As engineers discover reality, the specs they were given become stale, but there is no mechanism to keep them current during the inner loop of coding.

### The Cicadas Solution

**Why "Cicadas"?** Cicadas emerge in synchronized broods, do their work, leave their husks behind, and repeat on a cycle. This mirrors the methodology: active specs emerge to drive implementation, then expire (leave husks), while the living system continues. Multiple contributors work in synchronized parallel.

**Core principles:**

1. **Active Specs are disposable inputs** — PRDs, designs, and tasks expire after implementation.
2. **Code is the single source of truth** — always authoritative.
3. **Canon are reverse-engineered** — derived from code + expiring specs, not maintained in parallel.
4. **Work is partitioned** — large initiatives are sliced into independent feature branches via an explicit approach doc.
5. **Concurrent work via intent registry** — feature branch registration with both module-level and semantic intent conflict detection.
6. **Specs stay current during development** — a "Reflect" mechanism keeps active specs in sync with code as implementation progresses.
7. **Teams coordinate asynchronously** — a "Signal" mechanism broadcasts breaking changes to peer branches without blocking.

**Key innovation:** Instead of fighting to keep docs in sync with code, we let active specs expire and synthesize canon from what was actually built. The canon capture both the "what" (from code) and the "why" (from the expiring active specs). During development, the "Reflect" operation keeps specs honest, and "Signal" keeps teams informed.

### Terminology

| Concept | Term | Definition |
| :--- | :--- | :--- |
| **Coordination Unit** | **Initiative** | A set of related features with shared context (PRD, UX, Architecture). |
| **Drafting Area** | **Drafts** | Where specs are authored before work begins (`.cicadas/drafts/`). |
| **Live Requirements** | **Active Specs** | The living requirements driving current work (`.cicadas/active/`). Updated by Reflect during development. |
| **Generated Docs** | **Canon** | Authoritative canon, reverse-engineered from code on `main` (`.cicadas/canon/`). |
| **Activation** | **Kickoff** | Promoting drafts to active status, registering the initiative, and creating the initiative branch. |
| **Outer Integration** | **Initiative Branch** | A long-lived git branch (`initiative/{name}`) that integrates all feature branches. Pure code — never touches canon. Merges to `main` once at initiative completion. |
| **Inner Integration** | **Feature Branch** | A registered git branch for a partition of the initiative. Forks from and merges back to the initiative branch. |
| **Work Branch** | **Task Branch** | An ephemeral, private git branch for a single task. Unregistered. Merges to feature branch via PR. |
| **Change Ledger** | **Index** | Append-only history of all completed work (`.cicadas/index.json`). |
| **Expired Specs** | **Archive** | Completed active specs, preserved for archaeology (`.cicadas/archive/`). |

### System Components

| Component | Purpose | Lifecycle |
|-----------|---------|-----------|
| Active Specs | Drive implementation (PRD, approach, tasks) | Created at kickoff → updated by Reflect → archived at initiative completion |
| Canon | Authoritative canon | Synthesized on `main` at initiative completion, never manually edited |
| Index | Lightweight change ledger | Append-only, one entry per feature branch |
| Registry | Track concurrent work-in-progress | Entries added/removed with initiatives and feature branches |
| Archive | Historical active specs | Append-only, one entry per initiative |

**Chorus** is the orchestrator — a set of portable CLI scripts and agent instructions that manages the Cicadas lifecycle: initiative kickoff, branch registration, conflict detection, spec reflection, signaling, synthesis, merging, and queries.

---

## Part 2: Implementation Architecture

### Directory Structure

Chorus logic resides in `scripts/chorus/`, and it manages the `.cicadas/` folder in the project root:

```
project-root/
├── src/                              # Existing source code
├── scripts/
│   └── chorus/                       # Chorus orchestrator
│       ├── SKILL.md                  # Agent skill definition (entry point)
│       ├── implementation.md         # Guardrails for agent implementation
│       ├── reverse-engineering.md    # Bootstrapping guide for existing codebases
│       ├── scripts/                  # Python orchestration scripts
│       │   ├── utils.py              # Shared utilities (path resolution, JSON I/O)
│       │   ├── init.py               # Bootstrap .cicadas/ structure
│       │   ├── kickoff.py            # Promote drafts → active, register initiative
│       │   ├── branch.py             # Register a feature branch, check module overlaps
│       │   ├── status.py             # Show initiatives, branches, signals
│       │   ├── check.py              # Check for conflicts & main updates
│       │   ├── signal.py             # Broadcast a change to peer branches
│       │   ├── archive.py            # Move active specs → archive, deregister branch
│       │   ├── update_index.py       # Append to change ledger
│       │   └── prune.py              # Rollback branch or initiative → restore to drafts
│       ├── templates/                # Markdown templates
│       │   ├── synthesis-prompt.md   # LLM prompt for canon synthesis
│       │   ├── product-overview.md   # Canon template
│       │   ├── ux-overview.md        # Canon template
│       │   ├── tech-overview.md      # Canon template
│       │   ├── module-snapshot.md    # Canon template (per module)
│       │   ├── prd.md                # Active spec template
│       │   ├── ux.md                 # Active spec template
│       │   ├── tech-design.md        # Active spec template
│       │   ├── approach.md           # Active spec template
│       │   └── tasks.md              # Active spec template
│       └── emergence/                # Subagent definitions for spec authoring
│           ├── emergence.md          # Emergence phase overview
│           ├── clarify.md            # PRD refinement subagent
│           ├── ux.md                 # UX design subagent
│           ├── tech-design.md        # Architecture subagent
│           ├── approach.md           # Partitioning & sequencing subagent
│           └── tasks.md              # Task breakdown subagent
└── .cicadas/                         # Cicadas artifacts (managed by scripts)
    ├── config.json                   # Local configuration
    ├── registry.json                 # Global registry (initiatives + feature branches)
    ├── index.json                    # Change ledger (append-only)
    ├── canon/                        # Canon (authoritative, generated)
    │   ├── product-overview.md       # What the product does, goals, personas
    │   ├── ux-overview.md            # Design principles, patterns, flows
    │   ├── tech-overview.md          # Architecture, components, API, schema
    │   └── modules/                  # Module-level snapshots
    │       └── {module-name}.md
    ├── drafts/                       # Pre-kickoff staging area
    │   └── {initiative-name}/
    │       ├── prd.md
    │       ├── ux.md
    │       ├── tech-design.md
    │       ├── approach.md           # MUST define partitions → feature branches
    │       └── tasks.md
    ├── active/                       # Live specs for in-flight work
    │   └── {initiative-name}/
    │       ├── prd.md
    │       ├── ux.md
    │       ├── tech-design.md
    │       ├── approach.md
    │       └── tasks.md
    └── archive/                      # Expired specs (timestamped)
        └── {timestamp}-{name}/
```

### Portability Principle

All scripts are platform-agnostic, using standard Python 3 libraries. They avoid hardcoded platform-specific paths and instead rely on the project structure and convention.

---

## Part 3: The Workflow

### Phase 1: Emergence (Drafting)

**Location**: `.cicadas/drafts/{initiative-name}/`

Progressive spec authoring using subagents or manual drafting:

| Step | Artifact | Focus |
|------|----------|-------|
| 1. Clarify | `prd.md` | **What & Why**. Problem, users, success criteria. |
| 2. UX | `ux.md` | **Experience**. Interaction flow, UI states, copy. |
| 3. Tech | `tech-design.md` | **Architecture**. Components, data flow, schemas. |
| 4. Approach | `approach.md` | **Strategy & Partitioning**. Implementation plan, sequencing, dependencies, and logical partitions. |
| 5. Tasks | `tasks.md` | **Execution**. Ordered, testable checklist. |

**Critical**: `approach.md` MUST define logical partitions (e.g., "Auth Module", "Frontend Shell", "Data Layer"). These partitions become **Feature Branches**.

Each step consumes the artifacts from previous steps. Human review is required after each step.

**Mechanism**: Subagents in `scripts/chorus/emergence/` or manual authoring. See `EMERGENCE.md` for details.

### Phase 2: Kickoff

**Trigger**: Drafts are reviewed and approved.

**Action (Script)**: `python scripts/chorus/scripts/brood.py {initiative-name} --intent "description"`

**Effect**:
1. Promotes docs from `.cicadas/drafts/{name}/` to `.cicadas/active/{name}/`.
2. Registers the initiative in `registry.json` under `initiatives`.
3. Creates the **initiative branch**: `git checkout -b initiative/{name}` — a long-lived integration branch where all feature branches merge.
4. The shared specs become the "constitution" for all feature branches.

**Branch hierarchy**:
```
main
└── initiative/{name}              ← created at kickoff, merges to main once
    ├── feat/{partition-1}         ← registered, forks from initiative
    │   ├── task/.../task-a        ← ephemeral, unregistered
    │   └── task/.../task-b        ← ephemeral, unregistered
    ├── feat/{partition-2}         ← registered, forks from initiative
    └── feat/{partition-3}         ← registered, forks from initiative
```

**Key**: The initiative branch is a *pure code integration branch*. It never touches canon. Canon is synthesized on `main` after the initiative branch merges (see Phase 5).

### Phase 3: Execution (The Dual Loop)

#### Outer Loop: Start a Feature Branch (Registered)

**When**: Starting a major partition of work defined in `approach.md`.

**Steps**:
1. **Semantic Check (Agent)**: Read `registry.json`. Analyze the new intent against all active feature intents for logical conflicts. This is an LLM reasoning step — module overlap alone is insufficient.
2. **Checkout initiative branch**: `git checkout initiative/{name}` — ensure branching from the correct parent.
3. **Module Check (Script)**: `python scripts/chorus/scripts/branch.py {branch-name} --intent "description" --modules "mod1,mod2" --initiative {initiative-name}`
4. Review warnings from both the Agent (intent conflicts) and the Script (module overlaps).

**Script effect**:
- Creates git branch (forking from the initiative branch).
- Registers the branch in `registry.json` under `branches`, linked to the initiative.
- Creates `.cicadas/active/{branch-name}/` for branch-specific specs.

#### Outer Loop: Complete a Feature Branch

**When**: All task branches for this feature are merged.

**Steps**:
1. **Update index (Script)**: `python scripts/chorus/scripts/update_index.py --branch {name} --summary "..."` — logs to the change ledger.
2. **Merge to initiative**: `git checkout initiative/{name} && git merge {branch-name}` — merges into the initiative branch, **not** `main`.

**Key**: No synthesis, no archiving at this step. Active specs stay active — they're the living document for the rest of the initiative, continuously updated by Reflect. Canon is produced only at initiative completion (Phase 5).

#### Inner Loop: Task Branches (Unregistered)

**When**: Daily coding work. These are ephemeral and do NOT touch the registry.

**Steps**:
1. Checkout from Feature Branch: `git checkout -b task/{feature}/{task-name}`
2. Implement code.
3. **Reflect** (see below): Keep active specs current as code reality diverges from plan.
4. Open a **PR** against the feature branch. Include in the PR description:
   - What was implemented
   - **Reflect findings**: any spec divergences discovered and updated
   - Test results
5. Builder reviews and approves the PR.
6. Merge the PR into the feature branch. Delete the task branch.

#### Inner Loop: Reflect (Agent Operation)

**Purpose**: Keep active specs in sync with code *during* development, not just at the end.

**Trigger**: After significant code changes; before merging a Task Branch to the Feature Branch.

**Action (Agent)**:
1. Analyze `git diff` against the active specs.
2. Update the relevant docs in `.cicadas/active/` (e.g., `tech-design.md`, `approach.md`, `tasks.md`) to match code reality.
3. If the change is significant enough to impact other feature branches, proceed to **Signal**.

**This is NOT a script** — it is an LLM reasoning + file editing operation performed by the agent.

### Phase 4: Coordination (Signals)

**Problem**: Feature A changes an API signature that Feature B depends on. Feature B's developer needs to know.

**Action (Script)**: `python scripts/chorus/scripts/signal.py "Changed Auth API: renamed login() to authenticate()"`

**Effect**:
- Appends a timestamped signal to the Initiative entry in `registry.json`.

**Reception**:
- `python scripts/chorus/scripts/status.py` surfaces unacknowledged signals.
- The Agent should check for signals when performing a **Check Status** operation and assess their relevance.

### Phase 5: Initiative Completion (Outer Loop: Synthesis & Archive)

**Trigger**: All feature branches for the initiative are merged into the initiative branch.

Synthesis and archiving are **outer loop functions** — they happen once, when all inner loops are done. During development, the active specs + Reflect serve as the living document.

#### Step 1: Merge Code to Main

1. `git checkout main && git merge initiative/{name}` — **code merge only**. The initiative branch never touched canon, so there are no documentation conflicts.
2. `git branch -d initiative/{name}` — delete the initiative branch.

**Why merge first, then synthesize**: Canon is meant to *replace*, not *merge*. If synthesis happened on the initiative branch, merging canon files to `main` would use git's 3-way merge — which could conflict with previous canon versions. By synthesizing directly on `main`, canon is a simple file write (overwrite old, create new). No merge strategy needed, ever.

#### Step 2: Synthesize Canon on Main (Agent Operation)

**Inputs**:
- The complete codebase on `main` (now includes all initiative code)
- Active specs from `.cicadas/active/{initiative}/` (continuously updated by Reflect — they reflect the *actual* system, not the original plan)
- Existing canon from `.cicadas/canon/` (may be empty on greenfield)
- Change ledger from `.cicadas/index.json`

**Outputs**:
- `canon/product-overview.md` (Goals, Personas, Metrics)
- `canon/ux-overview.md` (Design Principles, Patterns, Flows)
- `canon/tech-overview.md` (Architecture, Components, API, Schema)
- Module-level snapshots in `canon/modules/`

**Protocol**:
1. **Read**: Code on `main`, active specs, existing canon, change ledger.
2. **Synthesize**: Write canon to reflect the *new reality* of the code. On greenfield, create from scratch. On subsequent initiatives, update existing canon.
3. **Crucial**: Extract "Key Decisions" from the active specs and embed them in canon. This preserves the "why" before the specs are archived.
4. **Verify**: Ensure the new canon accurately describes the code as it exists *now* on `main`.

Use the prompt in `scripts/chorus/templates/synthesis-prompt.md` to guide this process.

**Builder review**: The Builder reviews the synthesized canon before proceeding.

#### Step 3: Archive & Commit

1. Run: `python scripts/chorus/scripts/archive.py {initiative-name}` — moves all active specs to `archive/`.
2. Remove the initiative from `registry.json`.
3. Commit canon + archive as a follow-up commit on `main`.
4. Push to remote.

**Result**: `main` receives two commits — the code merge, then the synthesis/archive commit. Canon is always synthesized *from* main, *on* main.

---

## Part 4: Script Specifications

All scripts reside in `scripts/chorus/scripts/`. Run with Python 3.

### scripts/utils.py
Portable utilities for JSON handling and path resolution.

```python
import json
import os
from pathlib import Path

def get_project_root():
    """Detect .cicadas folder or .git folder to find root."""
    curr = Path.cwd()
    for parent in [curr] + list(curr.parents):
        if (parent / ".cicadas").exists() or (parent / ".git").exists():
            return parent
    return curr

def load_json(path):
    if not path.exists(): return {}
    with open(path, 'r') as f: return json.load(f)

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f: json.dump(data, f, indent=2)
```

### scripts/init.py
Initializes the `.cicadas/` directory structure.

```python
import argparse
from pathlib import Path
from utils import save_json, get_project_root

def init_cicadas(root):
    cicadas = root / ".cicadas"
    cicadas.mkdir(exist_ok=True)
    (cicadas / "canon/modules").mkdir(parents=True, exist_ok=True)
    (cicadas / "active").mkdir(exist_ok=True)
    (cicadas / "drafts").mkdir(exist_ok=True)
    (cicadas / "archive").mkdir(exist_ok=True)

    save_json(cicadas / "registry.json", {
        "schema_version": "2.0",
        "initiatives": {},
        "branches": {}
    })
    save_json(cicadas / "index.json", {"schema_version": "2.0", "entries": []})
    save_json(cicadas / "config.json", {"project_name": root.name})

    app_md = cicadas / "system" / "product-overview.md"
    if not app_md.exists():
        app_md.write_text("# Product Overview\n\n[Pending Synthesis]")
    print(f"Initialized Cicadas in {cicadas}")

if __name__ == "__main__":
    init_cicadas(get_project_root())
```

### scripts/brood.py (Kickoff)
Promotes drafts to active specs and registers the initiative.

```python
import argparse
import shutil
from pathlib import Path
from datetime import datetime, timezone
from utils import get_project_root, load_json, save_json

def kickoff(name, intent, owner="unknown"):
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")

    if name in registry.get("initiatives", {}):
        print(f"Error: Initiative {name} already exists.")
        return

    active_dir = cicadas / "active" / name
    active_dir.mkdir(parents=True, exist_ok=True)

    # Promote drafts
    drafts_dir = cicadas / "drafts" / name
    if drafts_dir.exists():
        print(f"Promoting drafts for initiative: {name}...")
        for item in drafts_dir.iterdir():
            if item.name.startswith("."): continue
            shutil.move(str(item), str(active_dir / item.name))
        try:
            drafts_dir.rmdir()
        except OSError:
            pass
    else:
        print(f"Warning: No drafts found for {name}. Creating empty initiative.")

    # Register
    registry.setdefault("initiatives", {})[name] = {
        "intent": intent,
        "owner": owner,
        "signals": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    save_json(cicadas / "registry.json", registry)
    print(f"Initiative kicked off: {name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--intent", required=True)
    args = parser.parse_args()
    kickoff(args.name, args.intent)
```

### scripts/branch.py
Registers a feature branch, checks for module overlaps, and links to an initiative.

```python
import argparse
import subprocess
import shutil
from pathlib import Path
from datetime import datetime, timezone
from utils import get_project_root, load_json, save_json

def create_branch(name, intent, modules, initiative=None, owner="unknown"):
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")

    if name in registry.get("branches", {}):
        print(f"Error: Branch {name} already registered.")
        return

    # Check for module overlaps
    my_mods = set(m.strip() for m in modules.split(",") if m.strip())
    conflicts = []
    for b_name, b_info in registry.get("branches", {}).items():
        overlap = my_mods.intersection(set(b_info.get("modules", [])))
        if overlap:
            conflicts.append(f"{b_name} (Overlaps: {', '.join(overlap)})")

    # Git branch creation
    subprocess.run(["git", "checkout", "-b", name], check=True)

    # Register
    branch_info = {
        "intent": intent,
        "modules": list(my_mods),
        "owner": owner,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    if initiative:
        if initiative not in registry.get("initiatives", {}):
            print(f"Warning: Initiative {initiative} not found.")
        else:
            branch_info["initiative"] = initiative

    registry.setdefault("branches", {})[name] = branch_info
    save_json(cicadas / "registry.json", registry)

    (cicadas / "active" / name).mkdir(parents=True, exist_ok=True)

    print(f"Registered feature branch: {name}")
    if conflicts:
        print(f"WARNING: Module overlaps detected: {'; '.join(conflicts)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--intent", required=True)
    parser.add_argument("--modules", default="")
    parser.add_argument("--initiative", help="Link to an active initiative")
    args = parser.parse_args()
    create_branch(args.name, args.intent, args.modules, initiative=args.initiative)
```

### scripts/status.py
Shows global state: active initiatives, branches, signals, and potential overlaps.

```python
from utils import get_project_root, load_json

def show_status():
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")

    print(f"Project: {root.name}\n")

    initiatives = registry.get("initiatives", {})
    print(f"Active Initiatives ({len(initiatives)}):")
    for name, info in initiatives.items():
        signals = info.get("signals", [])
        print(f"  - {name}: {info['intent']}")
        if signals:
            print(f"    Signals ({len(signals)}):")
            for s in signals[-3:]:  # Show last 3
                print(f"      [{s['timestamp']}] {s['message']}")

    branches = registry.get("branches", {})
    print(f"\nActive Feature Branches ({len(branches)}):")
    for name, info in branches.items():
        initiative = info.get("initiative", "standalone")
        print(f"  - {name}: {info['intent']} (Initiative: {initiative}, Modules: {', '.join(info.get('modules', []))})")

if __name__ == "__main__":
    show_status()
```

### scripts/signal.py (NEW)
Broadcasts a signal to the initiative's signal board.

```python
import argparse
import subprocess
from datetime import datetime, timezone
from utils import get_project_root, load_json, save_json

def send_signal(message, initiative=None):
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")

    # Auto-detect initiative from current branch
    if not initiative:
        try:
            curr = subprocess.check_output(
                ["git", "branch", "--show-current"], cwd=root
            ).decode().strip()
            branch_info = registry.get("branches", {}).get(curr, {})
            initiative = branch_info.get("initiative")
        except:
            pass

    if not initiative or initiative not in registry.get("initiatives", {}):
        print("Error: Could not determine initiative. Use --initiative flag.")
        return

    signal = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": message,
        "from_branch": subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=root
        ).decode().strip()
    }
    registry["initiatives"][initiative].setdefault("signals", []).append(signal)
    save_json(cicadas / "registry.json", registry)
    print(f"Signal sent to initiative '{initiative}': {message}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("message")
    parser.add_argument("--initiative", help="Target initiative (auto-detected if omitted)")
    args = parser.parse_args()
    send_signal(args.message, args.initiative)
```

### scripts/check.py
Checks for conflicts, main updates, and signals.

```python
import subprocess
from utils import get_project_root, load_json

def check_conflicts():
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")

    # Get current branch
    try:
        curr = subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=root
        ).decode().strip()
    except:
        curr = "unknown"

    print(f"Checking status for branch: {curr}")

    # Check registry overlaps
    curr_info = registry.get("branches", {}).get(curr)
    if curr_info:
        my_mods = set(curr_info.get("modules", []))
        for name, info in registry.get("branches", {}).items():
            if name == curr: continue
            overlap = my_mods.intersection(set(info.get("modules", [])))
            if overlap:
                print(f"⚠️  CONFLICT: Branch '{name}' overlaps on modules: {', '.join(overlap)}")

        # Check for signals in linked initiative
        initiative = curr_info.get("initiative")
        if initiative:
            init_info = registry.get("initiatives", {}).get(initiative, {})
            signals = init_info.get("signals", [])
            if signals:
                print(f"\n📡 Signals from initiative '{initiative}':")
                for s in signals:
                    print(f"  [{s['timestamp']}] ({s.get('from_branch', '?')}): {s['message']}")
    else:
        print(f"ℹ️  Current branch '{curr}' is not registered.")

    # Check for main updates
    try:
        log = subprocess.check_output(
            ["git", "log", f"{curr}..main", "--oneline"], cwd=root
        ).decode()
        if log:
            count = len(log.strip().split('\n'))
            print(f"\n📥 {count} new commits on main since you branched.")
    except:
        pass

if __name__ == "__main__":
    check_conflicts()
```

### scripts/archive.py
Expires active specs by moving them to `archive/`.

```python
import argparse
import shutil
from datetime import datetime, timezone
from utils import get_project_root, load_json, save_json

def archive_branch(name):
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")

    if name not in registry.get("branches", {}):
        print(f"Error: Branch {name} not found in registry.")
        return

    # Move active specs to archive
    active = cicadas / "active" / name
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    husk = cicadas / "archive" / f"{ts}-{name}"

    if active.exists():
        shutil.move(str(active), str(husk))
        print(f"Archived active specs to {husk.name}")

    # Remove from registry
    del registry["branches"][name]
    save_json(cicadas / "registry.json", registry)
    print(f"Deregistered branch {name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    args = parser.parse_args()
    archive_branch(args.name)
```

### scripts/update_index.py
Appends to the change ledger.

```python
import argparse
from datetime import datetime, timezone
from utils import get_project_root, load_json, save_json

def update_index(branch, summary, decisions="", modules=""):
    root = get_project_root()
    index_path = root / ".cicadas" / "index.json"
    index = load_json(index_path)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "branch": branch,
        "summary": summary,
        "decisions": decisions,
        "modules": [m.strip() for m in modules.split(",") if m.strip()]
    }

    index.setdefault("entries", []).append(entry)
    save_json(index_path, index)
    print(f"Added entry {len(index['entries'])} to index.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--decisions", default="")
    parser.add_argument("--modules", default="")
    args = parser.parse_args()
    update_index(args.branch, args.summary, args.decisions, args.modules)
```

### scripts/prune.py
Rolls back a branch or initiative and restores specs to drafts.

```python
import argparse
import shutil
import subprocess
from utils import get_project_root, load_json, save_json

def prune(name, type_):
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")

    if type_ == "branch":
        if name not in registry.get("branches", {}):
            print(f"Error: Branch {name} not found.")
            return
        # Restore active specs to drafts
        active = cicadas / "active" / name
        drafts = cicadas / "drafts" / name
        if active.exists():
            shutil.move(str(active), str(drafts))
            print(f"Restored specs to drafts/{name}")
        # Delete git branch
        try:
            subprocess.run(["git", "checkout", "main"], check=True, cwd=root)
            subprocess.run(["git", "branch", "-D", name], check=True, cwd=root)
        except:
            print(f"Warning: Could not delete git branch {name}")
        del registry["branches"][name]
        save_json(cicadas / "registry.json", registry)
        print(f"Pruned branch: {name}")

    elif type_ == "initiative":
        if name not in registry.get("initiatives", {}):
            print(f"Error: Initiative {name} not found.")
            return
        # Restore specs
        active = cicadas / "active" / name
        drafts = cicadas / "drafts" / name
        if active.exists():
            shutil.move(str(active), str(drafts))
            print(f"Restored specs to drafts/{name}")
        del registry["initiatives"][name]
        save_json(cicadas / "registry.json", registry)
        print(f"Pruned initiative: {name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--type", required=True, choices=["branch", "initiative"])
    args = parser.parse_args()
    prune(args.name, args.type)
```

---

## Part 5: Templates

Templates reside in `scripts/chorus/templates/`. They provide structure for canon and active specs.

### Canon: product-overview.md
```markdown
# {Project Name} — Product Overview

> Generated by Chorus on {timestamp}. Do not edit manually.

## Overview
{Detailed summary of the product}

## Goals & Metrics
{Key business goals and how success is measured}

## Personas
{User types and their needs}

## Key Decisions
- **{Decision}**: {Rationale} ({Date})
```

### Canon: module-snapshot.md
```markdown
# Module: {Module Name}

> Generated by Chorus on {timestamp}.

## Purpose
{What this module does}

## Interfaces
- **Exports**: {Public API}
- **Dependencies**: {Imports}

## Key Decisions
{Module-specific decisions and rationale}
```

### Active Spec: prd.md
```markdown
# PRD: {Feature Name}

## Problem Statement
{What are we solving?}

## User Stories
- As a {user}, I want {action}, so that {benefit}.

## Requirements
- [ ] {Requirement 1}
```

### Active Spec: approach.md
```markdown
# Approach: {Feature / Initiative Name}

## Design
{Description of changes}

## Partitions
Each partition becomes a Feature Branch:
- **{Partition 1}**: {scope, modules affected}
- **{Partition 2}**: {scope, modules affected}

## Sequencing & Dependencies
{Which partitions must go first, what depends on what}

## Risks
{Potential issues}
```

### Active Spec: tasks.md
```markdown
# Tasks: {Feature Name}

- [ ] {Task 1} <!-- id: 1 -->
- [ ] {Task 2} <!-- id: 2 -->
```

---

## Part 6: Reference Guides

### Guide 1: Bootstrapping an Existing Project
When starting Cicadas on a codebase that already has code:
1. **Initialize**: Run `python scripts/chorus/scripts/init.py`.
2. **Reverse Engineer**: Follow `scripts/chorus/REVERSE_ENGINEERING.md` for disciplined code discovery.
3. **Analyze**: Identify core modules and architectural patterns.
4. **Draft Canon**:
    - Create `.cicadas/canon/product-overview.md` using the template.
    - Create module snapshots in `.cicadas/canon/modules/` for key components.
5. **Seed Index**:
    - Run `python scripts/chorus/scripts/update_index.py --branch "bootstrap" --summary "Initial bootstrap"`.

### Guide 2: Canon Synthesis (The LLM's Core Task)
**When to run**: At initiative completion, on `main`, after the code merge. NOT per-feature-branch.
**Goal**: Produce canon that reflects the *complete reality* of the code on `main`.

**Protocol**:
1. **Read**:
    - The codebase on `main` (now includes all initiative code).
    - The active specs in `.cicadas/active/{initiative}/` (updated by Reflect throughout development).
    - The existing canon in `.cicadas/canon/` (may be empty on greenfield).
    - The change ledger in `.cicadas/index.json` (for feature branch summaries).
2. **Synthesize**:
    - On greenfield: create canon from scratch.
    - On subsequent initiatives: update existing canon — overwrite, don't merge.
    - Update `product-overview.md` if product scope changed.
    - Update `tech-overview.md` if architecture changed.
    - Update relevant `modules/{name}.md` files.
    - **Crucial**: Extract "Key Decisions" from the active specs and embed them in canon. This preserves the "why" before the specs are archived.
3. **Verify**: Ensure the new canon accurately describes the code as it exists *now* on `main`.
4. **Builder review**: Present canon for review before archiving and committing.

### Guide 3: Conflict Resolution
Run: `python scripts/chorus/scripts/check.py`

**Interpreting Output**:
- **Module Overlap**: Another branch is touching the same modules. *Action*: Check their active specs, coordinate.
- **Signals**: Another branch broadcast a change. *Action*: Assess relevance and update your approach.
- **Main Updates**: New commits on main. *Action*: Rebase your branch.
- **Registry Desync**: Branch not registered. *Action*: Run `branch.py` to register it.

### Guide 4: Agent Guardrails
1. **No Unplanned Work**: Never start writing code until you have a reviewed `tasks.md`.
2. **Branch Only**: Only implement code on a registered feature branch or a task branch off of one (not `main` or the initiative branch).
3. **Hard Stop**: After drafting specs, STOP and wait for the Builder to approve. After synthesis, STOP and wait for the Builder to review canon.
4. **Tool Mandate**: NEVER manually edit `registry.json`. ALWAYS use the scripts.
5. **Reflect Before PR**: Always run the Reflect operation before opening a PR for a task branch. Include Reflect findings in the PR description.
6. **No Canon on Branches**: Never write to `.cicadas/canon/` on any branch. Canon is only synthesized on `main` at initiative completion.

### Guide 5: Agent Autonomy Boundaries
The Agent handles all ceremony behind natural-language commands from the Builder. Some actions are autonomous; others require Builder confirmation.

| Action | Autonomy | Rationale |
|--------|----------|----------|
| **Reflect** | Autonomous | Keeping specs current is mechanical — the Agent diffs and updates. |
| **Signal** | Autonomous | The Agent assesses cross-branch impact and signals when needed. |
| **Semantic Intent Check** | Autonomous | Conflict detection is informational. |
| **PR creation** | Autonomous | The Agent opens PRs with summaries and Reflect findings. |
| **PR merge** | **Builder approval** | Code review is a human gate. |
| **Synthesis** | Autonomous (execution) | The Agent produces canon, but... |
| **Canon commit** | **Builder approval** | ...canon must be reviewed before committing to `main`. |
| **Archive** | **Builder approval** | Archiving is irreversible — specs move to archive after Builder confirms canon. |

### Guide 6: Builder Commands
The Builder interacts via natural-language commands. The Agent handles all scripts, git operations, and agentic operations behind the scenes.

- **"Initialize cicadas"**: Runs `init.py`. Sets up `.cicadas/` structure.
- **"Kickoff {name}"**: Runs `brood.py`. Promotes drafts, registers initiative, creates initiative branch.
- **"Start feature {name}"**: Semantic check + `branch.py`. Creates feature branch from initiative branch, registers, checks conflicts.
- **"Implement task {X}"**: Creates task branch, implements, Reflects, opens PR with findings.
- **"Signal {message}"**: Runs `signal.py`. Broadcasts change to initiative.
- **"Complete feature {name}"**: Runs `update_index.py`. Merges feature branch into initiative branch.
- **"Complete initiative {name}"**: Merges initiative to `main`, synthesizes canon on `main`, archives specs, commits.

---

## Part 7: Workflow Quick Reference

### Scripts (Deterministic)

| Phase | Command | Action |
|-------|---------|--------|
| **Init** | `python scripts/chorus/scripts/init.py` | Bootstrap project structure |
| **Kickoff** | `python scripts/chorus/scripts/brood.py {name} --intent "..."` | Promote drafts, register initiative |
| **Feature** | `python scripts/chorus/scripts/branch.py {name} --intent "..." --modules "..." --initiative {name}` | Register feature branch |
| **Status** | `python scripts/chorus/scripts/status.py` | Show global state & signals |
| **Check** | `python scripts/chorus/scripts/check.py` | Check for conflicts & updates |
| **Signal** | `python scripts/chorus/scripts/signal.py "{message}"` | Broadcast to initiative |
| **Archive** | `python scripts/chorus/scripts/archive.py {name}` | Expire active specs |
| **Log** | `python scripts/chorus/scripts/update_index.py --branch {name} --summary "..."` | Record history |
| **Prune** | `python scripts/chorus/scripts/prune.py {name} --type {branch\|initiative}` | Rollback & restore to drafts |

### Agent Operations (LLM)

| Operation | Trigger | Action |
|-----------|---------|--------|
| **Semantic Intent Check** | Before starting a feature branch | Analyze registry intents for logical conflicts |
| **Reflect** | After significant code changes, before PR | Update active specs to match code reality. Include findings in PR. |
| **Signal Assessment** | After Reflect, during status check | Evaluate cross-branch impact. Signal autonomously if needed. |
| **Synthesis** | At initiative completion, on `main` | Generate canon from code + active specs. Requires Builder review. |

### File Locations
- Orchestrator: `scripts/chorus/`
- Artifacts: `.cicadas/`
- Agent Manual: `scripts/chorus/SKILL.md`
