
# Cicadas (General/Skill-Agnostic Version)

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

### The Cicadas Solution

**Why "Cicadas"?** Cicadas emerge in synchronized broods, do their work, leave their husks behind, and repeat on a cycle. This mirrors the methodology: forward docs emerge to drive implementation, then expire (leave husks), while the living system continues. Multiple contributors work in synchronized parallel.

**Core principles:**

1. **Forward docs are disposable inputs** — PRDs, specs, and tasks expire after implementation.
2. **Code is the single source of truth** — always authoritative.
3. **Canonical snapshots are reverse-engineered** — derived from code + expiring docs, not maintained in parallel.
4. **Clear bounded context** — scoped to a single VCS repo.
5. **Concurrent work via intent registry** — branch registration with advisory conflict detection.

**Key innovation:** Instead of fighting to keep docs in sync with code, we let forward docs expire and synthesize a canonical snapshot from what was actually built. The snapshot captures both the "what" (from code) and the "why" (from the expiring forward docs).

### System Components

| Component | Purpose | Lifecycle |
|-----------|---------|-----------|
| Forward docs | Drive implementation (PRD, approach, tasks) | Created → consumed → archived |
| Cicadas snapshots | Authoritative system documentation | Generated at merge, never manually edited |
| Artifact index | Lightweight change ledger | Append-only, accumulates history |
| Branch registry | Track concurrent work-in-progress | Entries added/removed with branches |
| Archive | Historical forward docs (husks) | Append-only, for archaeology |

**Chorus** is the orchestrator — a set of portable CLI tools and a manual that manages the Cicadas lifecycle: branch registration, conflict detection, synthesis instructions, merging, and queries.

---

## Part 2: Implementation Architecture

### Directory Structure

Chorus logic resides in a centralized location (e.g., `scripts/chorus/`), and it manages the `.cicadas/` folder in the project root:

```
project-root/
├── src/                          # Existing source code
├── scripts/
│   └── chorus/                   # Chorus CLI tools & manual
│       ├── CHORUS.md             # The Agent Manual
│       ├── scripts/              # Python orchestration scripts
│       └── templates/            # Markdown templates
└── .cicadas/                     # Cicadas artifacts (Managed)
    ├── config.json               # Local configuration
    ├── canon/                    # Canonical snapshots (authoritative)
    │   ├── app.md                # App-level snapshot
    │   └── modules/              # Module-level snapshots
    ├── index.json                # Artifact index (append-only ledger)
    ├── registry.json             # Branch registry (active work)
    ├── forward/                  # Active forward docs (transient)
    └── archive/                  # Expired forward docs (husks)
```

### Portability Principle

All scripts should be platform-agnostic, using standard Python libraries. They avoid hardcoded platform-specific paths (like Anthropic Skill directories) and instead rely on the project structure and the `CHORUS.md` guide.

---

## Part 3: Agent Manual (CHORUS.md)

This file replaces platform-specific "Skill" manifests. It provides instructions to any AI agent on how to use the methodology.

```markdown
# Chorus: Cicadas Orchestrator

Chorus orchestrates the Cicadas methodology — sustainable spec-driven development where forward docs (PRDs, specs, tasks) are transient inputs that expire after implementation, and canonical documentation is reverse-engineered from the code.

## Operations

### Bootstrap (first-time setup)
Use when initializing Cicadas on an existing project.
1. Run: `python scripts/chorus/scripts/init.py [project_root]`
2. This creates the `.cicadas/` structure and `config.json`.

### Start a Branch
Use when beginning work on a feature, fix, or change.
1. Author forward docs (PRD, approach, tasks) in `.cicadas/forward/{branch_name}/`.
2. Run: `python scripts/chorus/scripts/branch.py {branch_name} --intent "description" --modules "mod1,mod2"`
3. Review conflict warnings from the output.

### Check Status
Run: `python scripts/chorus/scripts/status.py`
Shows active branches, potential overlaps, and snapshot state.

### Synthesize Snapshot
This is LLM work. Before merging:
1. Read current code + forward docs + previous snapshots.
2. Update `.cicadas/canon/` files using the templates in `scripts/chorus/templates/`.
3. captured rationale from the expiring forward docs.

### Merge & Archive
When synthesis is reviewed:
1. Run: `python scripts/chorus/scripts/archive.py {branch_name}`
2. Run: `python scripts/chorus/scripts/update_index.py --branch {branch} --summary "..."`
3. Execute standard git merge.
```

---

## Part 4: Script Specifications

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
Initializes the structure.

```python
import argparse
import json
from pathlib import Path
from utils import save_json, get_project_root

def init_cicadas(root):
    cicadas = root / ".cicadas"
    cicadas.mkdir(exist_ok=True)
    (cicadas / "canon/modules").mkdir(parents=True, exist_ok=True)
    (cicadas / "forward").mkdir(exist_ok=True)
    (cicadas / "archive").mkdir(exist_ok=True)
    
    save_json(cicadas / "registry.json", {"schema_version": "1.0", "branches": {}})
    save_json(cicadas / "index.json", {"schema_version": "1.0", "entries": []})
    save_json(cicadas / "config.json", {"project_name": root.name})
    
    # Create empty app.md
    app_md = (cicadas / "canon/app.md")
    if not app_md.exists():
        app_md.write_text("# App Snapshot\n\n[Pending Synthesis]")
    print(f"Initialized Cicadas in {cicadas}")

if __name__ == "__main__":
    init_cicadas(get_project_root())
```

### scripts/branch.py
Registers a branch and checks for conflicts.

```python
import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from utils import get_project_root, load_json, save_json

def create_branch(name, intent, modules, owner="unknown"):
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")
    
    if name in registry.get("branches", {}):
        print(f"Error: Branch {name} already registered.")
        return

    # Check for overlaps
    my_mods = set(m.strip() for m in modules.split(",") if m.strip())
    conflicts = []
    for b_name, b_info in registry.get("branches", {}).items():
        overlap = my_mods.intersection(set(b_info.get("modules", [])))
        if overlap:
            conflicts.append(f"{b_name} (Overlaps: {', '.join(overlap)})")

    # Git branch creation
    subprocess.run(["git", "checkout", "-b", name], check=True)

    # Register
    registry.setdefault("branches", {})[name] = {
        "intent": intent,
        "modules": list(my_mods),
        "owner": owner,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    save_json(cicadas / "registry.json", registry)
    
    (cicadas / "forward" / name).mkdir(parents=True, exist_ok=True)
    
    print(f"Registered branch {name}.")
    if conflicts:
        print(f"WARNING: Potential overlaps detected: {'; '.join(conflicts)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--intent", required=True)
    parser.add_argument("--modules", default="")
    args = parser.parse_args()
    create_branch(args.name, args.intent, args.modules)
```

### scripts/status.py
Status overview.

```python
import json
from pathlib import Path
from utils import get_project_root, load_json

def show_status():
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")
    
    print(f"Project: {root.name}")
    print(f"Active Brood ({len(registry.get('branches', {}))} branches):")
    for name, info in registry.get("branches", {}).items():
        print(f"  - {name}: {info['intent']} (Modules: {', '.join(info['modules'])})")

if __name__ == "__main__":
    show_status()
```

### scripts/archive.py
Expires forward docs (husks).

```python
import argparse
import shutil
from pathlib import Path
from datetime import datetime, timezone
from utils import get_project_root, load_json, save_json

def archive_branch(name):
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")
    
    if name not in registry.get("branches", {}):
        print(f"Error: Branch {name} not found.")
        return

    # Move forward docs to archive
    forward = cicadas / "forward" / name
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    husk = cicadas / "archive" / f"{ts}-{name}"
    
    if forward.exists():
        shutil.move(str(forward), str(husk))
        print(f"Archived forward docs to {husk.name}")

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

---

## Part 5: Templates

Templates remain standard Markdown, located in `scripts/chorus/templates/`.

### scripts/check.py
Check for conflicts and changes.

```python
import argparse
import json
import subprocess
from pathlib import Path
from utils import get_project_root, load_json

def check_conflicts():
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")
    
    # Get current branch
    try:
        curr = subprocess.check_output(["git", "branch", "--show-current"], cwd=root).decode().strip()
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
    else:
        print(f"ℹ️  Current branch '{curr}' is not registered in Chorus.")

    # Check for main updates
    try:
        log = subprocess.check_output(["git", "log", f"{curr}..main", "--oneline"], cwd=root).decode()
        if log:
            count = len(log.strip().split('\n'))
            print(f"📥 {count} new commits on main since you branched.")
    except:
        pass

if __name__ == "__main__":
    check_conflicts()
```

### scripts/update_index.py
Appends to the artifact ledger.

```python
import argparse
import json
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
    print(f"Added entry {len(index['entries'])} to artifact index.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--decisions", default="")
    parser.add_argument("--modules", default="")
    args = parser.parse_args()
    update_index(args.branch, args.summary, args.decisions, args.modules)
```

---

## Part 5: Templates

Templates remain standard Markdown, located in `scripts/chorus/templates/`.

### app-snapshot.md
```markdown
# {Project Name} — Cicadas Snapshot

> Generated by Chorus on {timestamp}. Do not edit manually.

## Overview
{Detailed summary of application}

## Architecture
{High-level architecture description}

## Modules
| Module | Purpose | Key Files |
|--------|---------|-----------|
| {name} | {purpose} | {files} |

## Key Decisions
- **{Decision}**: {Rationale} ({Date})
```

### module-snapshot.md
```markdown
# Module: {Module Name}

> Generated by Chorus on {timestamp}.

## Purpose
{What this module does}

## Interfaces
- **Exports**: {Public API}
- **Dependencies**: {Imports}

## Key Decisions
{Module-specific decisions}
```

### forward-docs/prd.md
```markdown
# PRD: {Feature Name}

## Problem Statement
{What are we solving?}

## User Stories
- As a {user}, I want {action}, so that {benefit}.

## Requirements
- [ ] {Requirement 1}
```

### forward-docs/approach.md
```markdown
# Technical Approach: {Feature Name}

## Design
{Description of changes}

## Modules Affected
{List of modules}

## Risks
{Potential issues}
```

### forward-docs/tasks.md
```markdown
# Tasks: {Feature Name}

- [ ] {Task 1} <!-- id: 1 -->
- [ ] {Task 2} <!-- id: 2 -->
```

---

---

## Part 6: Reference Guides

### Guide 1: Bootstrapping a New Project
When starting Cicadas on an existing codebase:
1. **Initialize**: Run `python scripts/chorus/scripts/init.py`.
2. **Analyze**: Read the codebase to understand architecture and modules.
3. **Draft Snapshots**:
    - Create `.cicadas/canon/app.md` using the template.
    - Create module snapshots in `.cicadas/canon/modules/` for key components.
4. **Seed Index**:
    - Run `python scripts/chorus/scripts/update_index.py --branch "bootstrap" --summary "Initial bootstrap"`.

### Guide 2: Snapshot Synthesis (The LLM's Core Task)
**When to run**: Before merging any branch.
**Goal**: Update canonical docs to reflect the *new reality* of the code.

**Protocol**:
1. **Read**:
    - The *actual* code changes (git diff or file reads).
    - The forward docs in `.cicadas/forward/{branch}/` (for intent/rationale).
    - The existing snapshots in `.cicadas/canon/`.
2. **Synthesize**:
    - Update `app.md` if high-level architecture changed.
    - Update relevant `modules/{name}.md` files.
    - **Crucial**: Extract "Key Decisions" from the forward docs and append them to the snapshots. This preserves the "why" before the forward docs are archived.
3. **Verify**: Ensure the new snapshots accurately describe the code as it exists *now*.

### Guide 3: Conflict Resolution
Run: `python scripts/chorus/scripts/check.py`

**Interpreting Output**:
- **Module Overlap**: Warning that another branch is touching the same modules. *Action*: Check their forward docs, maybe coordinate.
- **Main Updates**: New commits on main. *Action*: Rebase your branch to ensure you're building on the latest state.
- **Registry Desync**: Branch not registered. *Action*: Run `branch.py` to register it.

---

## Part 7: CLI Workflow Quick Reference

| Phase | Command | Action |
|-------|---------|--------|
| **Start** | `python scripts/chorus/scripts/branch.py {name} --intent "..." --modules "..."` | Join the brood |
| **Check** | `python scripts/chorus/scripts/status.py` | See global state |
| **Verify**| `python scripts/chorus/scripts/check.py` | Check for conflicts |
| **Finish**| `python scripts/chorus/scripts/archive.py {name}` | Husk forward docs |
| **Log** | `python scripts/chorus/scripts/update_index.py --branch {name} --summary "..."` | Record history |

**File Locations**:
- Core logic: `scripts/chorus/scripts/`
- Artifacts: `.cicadas/`
- Manual: `scripts/chorus/CHORUS.md` (This file's deployed location)

---

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
