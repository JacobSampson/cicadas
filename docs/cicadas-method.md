# Cicadas

## A Methodology for Sustainable Spec-Driven Development

### Implementation Manual

---

## Part 1: Summary of the Approach

### The Problem

Traditional Spec-Driven Development (SDD) works well on the first pass but degrades over time:

1. **Documentation entropy**: Every code change must back-propagate to specs, creating exponential maintenance burden
2. **Waterfall assumptions**: SDD assumes requirements are known before implementation, but real design is emergent
3. **Single-threaded model**: SDD doesn't address concurrent work by multiple humans and AI agents
4. **Stale context**: LLMs confidently generate from outdated specs, producing incorrect code

### The Cicadas Solution

**Why "Cicadas"?** Cicadas emerge in synchronized broods, do their work, leave their husks behind, and repeat on a cycle. This mirrors the methodology: forward docs emerge to drive implementation, then expire (leave husks), while the living system continues. Multiple contributors work in synchronized parallel, like a brood.

**Core principles:**

1. **Forward docs are disposable inputs** — PRDs, specs, and tasks expire after implementation
2. **Code is the single source of truth** — always authoritative
3. **Canonical snapshots are reverse-engineered** — derived from code + expiring docs, not maintained in parallel
4. **Clear bounded context** — scoped to a single VCS repo
5. **Concurrent work via intent registry** — branch registration with advisory conflict detection

**Key innovation:** Instead of fighting to keep docs in sync with code, we let forward docs expire and synthesize a canonical snapshot from what was actually built. The snapshot captures both the "what" (from code) and the "why" (from the expiring forward docs).

### System Components

| Component | Purpose | Lifecycle |
|-----------|---------|-----------|
| Forward docs | Drive implementation (PRD, approach, tasks) | Created → consumed → archived |
| Cicadas snapshots | Authoritative system documentation | Generated at merge, never manually edited |
| Artifact index | Lightweight change ledger | Append-only, accumulates history |
| Branch registry | Track concurrent work-in-progress | Entries added/removed with branches |
| Archive | Historical forward docs (husks) | Append-only, for archaeology |

**Chorus** is the orchestrator — the skill and scripts that manage the Cicadas lifecycle: branch registration, conflict detection, synthesis, merging, and queries.

**Canon hierarchy** (conflict resolution order, highest to lowest):
```
code (main) → snapshot docs → branch registry → branch code → branch docs → archive
```

### Workflow Overview

**Starting work:**
1. Author forward docs (PRD, approach, tasks) — possibly via BMAD
2. Ask Chorus to check branch registry for conflicts
3. Create branch via Chorus, register intent
4. Receive context from relevant Cicadas snapshots

**During work:**
- Work directly on files/git (fast path)
- Optionally ask Chorus to check for changes that affect your work
- For emergent design: shorter cycles, revise forward docs as understanding evolves

**Completing work:**
1. Chorus synthesizes: code + forward docs + index → updated Cicadas snapshot
2. Human reviews snapshot
3. Chorus executes merge to main
4. Chorus archives forward docs (they become husks)
5. Chorus updates artifact index
6. Chorus deregisters branch, notifies affected branches

---

## Part 2: Implementation Architecture

### Directory Structure

Chorus creates and manages this structure in the target project:

```
project-root/
├── src/                          # Existing source code
├── tests/                        # Existing tests
└── .cicadas/                     # Cicadas artifacts
    ├── canon/                    # Canonical snapshots (authoritative)
    │   ├── app.md                # App-level snapshot
    │   └── modules/              # Module-level snapshots
    │       ├── {module-name}.md
    │       └── ...
    ├── index.json                # Artifact index (append-only ledger)
    ├── registry.json             # Branch registry (active work)
    ├── forward/                  # Active forward docs (transient)
    │   └── {branch-name}/
    │       ├── prd.md
    │       ├── approach.md
    │       └── tasks.md
    └── archive/                  # Expired forward docs (husks)
        └── {timestamp}-{branch}/
            └── ...
```

### Skill Structure

```
chorus/
├── SKILL.md                      # Main entry point
├── templates/
│   ├── app-snapshot.md           # Template for app-level snapshot
│   ├── module-snapshot.md        # Template for module snapshot
│   ├── forward-docs/
│   │   ├── prd.md
│   │   ├── approach.md
│   │   └── tasks.md
│   └── schemas/
│       ├── registry.schema.json
│       └── index.schema.json
├── scripts/
│   ├── init.py                   # Initialize .cicadas structure
│   ├── branch.py                 # Create branch, register intent
│   ├── status.py                 # Show current state
│   ├── check.py                  # Check for conflicts/changes
│   ├── archive.py                # Archive forward docs
│   ├── update_index.py           # Append to artifact index
│   └── utils.py                  # Shared utilities
└── references/
    ├── bootstrap.md              # How to bootstrap existing project
    ├── branch-workflow.md        # Detailed branching procedure
    ├── synthesis.md              # How to synthesize snapshots
    ├── merge-workflow.md         # Detailed merge procedure
    └── conflict-detection.md     # How conflict detection works
```

---

## Part 3: Skill Specification

### SKILL.md

```markdown
---
name: chorus
description: >
  Orchestrates Cicadas methodology for sustainable spec-driven development. Use this skill when:
  starting work on a new feature or change, checking for conflicts with other work in progress,
  completing work and merging to main, querying the current state of the system, bootstrapping
  Cicadas on an existing project, or any mention of "Cicadas", "Chorus", "branch registry", 
  "canonical snapshot", or spec-driven development workflows. This skill handles the full lifecycle
  of concurrent development with transient forward docs and reverse-engineered canonical snapshots.
---

# Chorus

Orchestrates the Cicadas methodology — sustainable spec-driven development where forward docs
(PRDs, specs, tasks) are transient inputs that expire after implementation, and canonical
documentation is reverse-engineered from the code.

## Why "Cicadas"?

Cicadas emerge in synchronized broods, do their work, leave their husks behind, and repeat.
This mirrors the methodology: forward docs emerge to drive implementation, then expire (leave 
husks), while the living system continues. Multiple contributors work in synchronized parallel,
like a brood. Chorus is the synchronized sound they make together — the orchestration layer.

## Core Concepts

**Forward docs**: Created to drive a change, consumed during implementation, then archived (husks).
Never maintained after use.

**Cicadas snapshots**: Generated from code + expiring forward docs. The authoritative
description of what the system does and why. Never manually edited — regenerated on each merge.

**Branch registry**: Tracks who's working on what. Enables conflict detection across
concurrent work.

**Artifact index**: Append-only ledger of changes. Captures what/when/why for history.

## Operations

### Bootstrap (first-time setup)

Use when initializing Cicadas on an existing project.

1. Run: `python {skill_path}/scripts/init.py {project_root}`
2. This creates the `.cicadas/` directory structure
3. Read `references/bootstrap.md` for how to generate the initial Cicadas snapshot from existing code

### Start a Branch

Use when beginning work on a feature, fix, or change.

1. Ensure forward docs exist (PRD, approach, tasks) — author them or use BMAD
2. Run: `python {skill_path}/scripts/branch.py {branch_name} --intent "description" --modules "mod1,mod2"`
3. Review any conflict warnings from Chorus
4. Read `references/branch-workflow.md` for detailed procedure

The script will:
- Check registry for overlapping work
- Create git branch
- Register intent in registry.json
- Create `.cicadas/forward/{branch_name}/` directory

### Check Status

Use to see current state and potential conflicts.

Run: `python {skill_path}/scripts/status.py {project_root}`

Shows:
- Current branch and its registration
- Other active branches (the brood)
- Potential overlaps
- Staleness of Cicadas snapshots

### Check for Changes

Use during work to see if anything has changed that affects you.

Run: `python {skill_path}/scripts/check.py {project_root}`

### Synthesize Snapshot

Use when implementation is complete, before merging.

This is LLM work — read `references/synthesis.md` for the detailed procedure.

Inputs:
- Current code (read the actual implementation)
- Forward docs from `.cicadas/forward/{branch}/`
- Previous Cicadas snapshot from `.cicadas/canon/`
- Artifact index from `.cicadas/index.json`

Output:
- Updated app-level snapshot (if scope warrants)
- Updated module-level snapshot(s)
- Use templates from `templates/app-snapshot.md` and `templates/module-snapshot.md`

### Merge

Use when synthesis is complete and reviewed.

Read `references/merge-workflow.md` for detailed procedure.

Steps:
1. Ensure snapshot is synthesized and reviewed
2. Run: `python {skill_path}/scripts/archive.py {project_root} {branch_name}`
3. Run: `python {skill_path}/scripts/update_index.py {project_root} --branch {branch} --summary "..." --decisions "..."`
4. Execute git merge
5. Branch is automatically deregistered by archive.py

### Query System State

Use to answer questions about the system.

Read the relevant Cicadas snapshots and artifact index. Cite sources in your response.

For questions about current state: consult `.cicadas/canon/`
For questions about history: consult `.cicadas/index.json`
For questions about in-flight work: consult `.cicadas/registry.json`

## Templates

Use templates in `templates/` directory:
- `app-snapshot.md`: Structure for app-level Cicadas snapshot
- `module-snapshot.md`: Structure for module-level Cicadas snapshots
- `forward-docs/`: Templates for PRD, approach, tasks

## Scripts

All scripts are in `scripts/` directory. Run with Python 3.

Scripts handle deterministic operations (file manipulation, JSON updates, git commands).
LLM handles synthesis, conflict analysis, and queries.
```

---

## Part 4: Script Specifications

### scripts/init.py

```python
#!/usr/bin/env python3
"""
Initialize Cicadas structure in a project.

Usage:
    python init.py <project_root>

Creates:
    .cicadas/
    ├── canon/
    │   ├── app.md (empty template)
    │   └── modules/
    ├── index.json (empty array)
    ├── registry.json (empty object)
    ├── forward/
    └── archive/
"""

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

def init_cicadas(project_root: Path) -> dict:
    """Initialize .cicadas directory structure."""
    cicadas = project_root / ".cicadas"
    
    if cicadas.exists():
        return {"success": False, "error": ".cicadas already exists", "path": str(cicadas)}
    
    # Create directories
    (cicadas / "canon" / "modules").mkdir(parents=True)
    (cicadas / "forward").mkdir()
    (cicadas / "archive").mkdir()
    
    # Initialize empty registry
    registry = {
        "schema_version": "1.0",
        "branches": {}
    }
    (cicadas / "registry.json").write_text(json.dumps(registry, indent=2))
    
    # Initialize empty index
    index = {
        "schema_version": "1.0",
        "entries": []
    }
    (cicadas / "index.json").write_text(json.dumps(index, indent=2))
    
    # Create placeholder app snapshot
    app_snapshot = """# Application Snapshot

> Generated by Cicadas. Do not edit manually.

## Overview

[To be generated during bootstrap or first merge]

## Modules

[To be generated]

## Key Decisions

[To be generated]

## External Dependencies

[To be generated]
"""
    (cicadas / "canon" / "app.md").write_text(app_snapshot)
    
    return {
        "success": True,
        "path": str(cicadas),
        "created": [
            "canon/",
            "canon/app.md",
            "canon/modules/",
            "forward/",
            "archive/",
            "registry.json",
            "index.json"
        ]
    }

def main():
    parser = argparse.ArgumentParser(description="Initialize Cicadas structure")
    parser.add_argument("project_root", type=Path, help="Path to project root")
    args = parser.parse_args()
    
    result = init_cicadas(args.project_root.resolve())
    print(json.dumps(result, indent=2))
    return 0 if result["success"] else 1

if __name__ == "__main__":
    exit(main())
```

### scripts/branch.py

```python
#!/usr/bin/env python3
"""
Create a branch and register intent with Chorus.

Usage:
    python branch.py <branch_name> --intent "description" [--modules "mod1,mod2"] [--project-root <path>]

Returns:
    JSON with registration details and any conflict warnings
"""

import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

def load_registry(project_root: Path) -> dict:
    registry_path = project_root / ".cicadas" / "registry.json"
    if not registry_path.exists():
        raise FileNotFoundError(f"Registry not found: {registry_path}")
    return json.loads(registry_path.read_text())

def save_registry(project_root: Path, registry: dict):
    registry_path = project_root / ".cicadas" / "registry.json"
    registry_path.write_text(json.dumps(registry, indent=2))

def check_conflicts(registry: dict, modules: list[str]) -> list[dict]:
    """Check for potential conflicts with existing branches."""
    conflicts = []
    for branch_name, branch_info in registry.get("branches", {}).items():
        branch_modules = set(branch_info.get("modules", []))
        overlap = branch_modules.intersection(set(modules))
        if overlap:
            conflicts.append({
                "branch": branch_name,
                "owner": branch_info.get("owner", "unknown"),
                "intent": branch_info.get("intent", ""),
                "overlapping_modules": list(overlap)
            })
    return conflicts

def create_branch(
    project_root: Path,
    branch_name: str,
    intent: str,
    modules: list[str],
    owner: str = "unknown"
) -> dict:
    """Create git branch and register with Chorus."""
    
    registry = load_registry(project_root)
    
    # Check if branch already registered
    if branch_name in registry.get("branches", {}):
        return {
            "success": False,
            "error": f"Branch '{branch_name}' already registered in Chorus"
        }
    
    # Check for conflicts
    conflicts = check_conflicts(registry, modules)
    
    # Create git branch
    try:
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=project_root,
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"Git branch creation failed: {e.stderr.decode()}"
        }
    
    # Register branch
    registry.setdefault("branches", {})[branch_name] = {
        "intent": intent,
        "modules": modules,
        "owner": owner,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    save_registry(project_root, registry)
    
    # Create forward docs directory
    forward_dir = project_root / ".cicadas" / "forward" / branch_name
    forward_dir.mkdir(parents=True, exist_ok=True)
    
    return {
        "success": True,
        "branch": branch_name,
        "registered": registry["branches"][branch_name],
        "forward_docs_path": str(forward_dir),
        "conflicts": conflicts if conflicts else None,
        "conflict_warning": f"⚠️  Chorus detected potential conflicts with {len(conflicts)} branch(es)" if conflicts else None
    }

def main():
    parser = argparse.ArgumentParser(description="Create and register Cicadas branch")
    parser.add_argument("branch_name", help="Name of the branch to create")
    parser.add_argument("--intent", required=True, help="Description of what this branch will do")
    parser.add_argument("--modules", default="", help="Comma-separated list of modules affected")
    parser.add_argument("--owner", default="unknown", help="Owner of the branch (human or agent name)")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root path")
    args = parser.parse_args()
    
    modules = [m.strip() for m in args.modules.split(",") if m.strip()]
    
    result = create_branch(
        project_root=args.project_root.resolve(),
        branch_name=args.branch_name,
        intent=args.intent,
        modules=modules,
        owner=args.owner
    )
    
    print(json.dumps(result, indent=2))
    return 0 if result["success"] else 1

if __name__ == "__main__":
    exit(main())
```

### scripts/status.py

```python
#!/usr/bin/env python3
"""
Show Cicadas status for a project via Chorus.

Usage:
    python status.py [project_root]

Returns:
    JSON with current branch, registry state, and snapshot info
"""

import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

def get_current_branch(project_root: Path) -> str:
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_root,
            capture_output=True,
            check=True
        )
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError:
        return "unknown"

def get_status(project_root: Path) -> dict:
    """Get full Cicadas status."""
    cicadas = project_root / ".cicadas"
    
    if not cicadas.exists():
        return {
            "initialized": False,
            "error": "Cicadas not initialized. Run init.py first."
        }
    
    # Load registry
    registry = json.loads((cicadas / "registry.json").read_text())
    
    # Load index
    index = json.loads((cicadas / "index.json").read_text())
    
    # Get current branch
    current_branch = get_current_branch(project_root)
    
    # Check if current branch is registered
    current_registration = registry.get("branches", {}).get(current_branch)
    
    # Get snapshot info
    app_snapshot = cicadas / "canon" / "app.md"
    module_snapshots = list((cicadas / "canon" / "modules").glob("*.md"))
    
    # Get active forward docs
    forward_dirs = [d.name for d in (cicadas / "forward").iterdir() if d.is_dir()]
    
    # Count archived husks
    archive_count = len(list((cicadas / "archive").iterdir()))
    
    return {
        "initialized": True,
        "project_root": str(project_root),
        "current_branch": current_branch,
        "current_registration": current_registration,
        "brood": {
            "active_branches": list(registry.get("branches", {}).keys()),
            "count": len(registry.get("branches", {}))
        },
        "registry": registry.get("branches", {}),
        "index_entries": len(index.get("entries", [])),
        "last_change": index["entries"][-1] if index.get("entries") else None,
        "snapshots": {
            "app": str(app_snapshot) if app_snapshot.exists() else None,
            "modules": [str(m) for m in module_snapshots]
        },
        "active_forward_docs": forward_dirs,
        "archived_husks": archive_count
    }

def main():
    parser = argparse.ArgumentParser(description="Show Cicadas status")
    parser.add_argument("project_root", type=Path, nargs="?", default=Path.cwd())
    args = parser.parse_args()
    
    result = get_status(args.project_root.resolve())
    print(json.dumps(result, indent=2))
    return 0 if result.get("initialized") else 1

if __name__ == "__main__":
    exit(main())
```

### scripts/check.py

```python
#!/usr/bin/env python3
"""
Check for changes that might affect current branch via Chorus.

Usage:
    python check.py [project_root]

Returns:
    JSON with conflict analysis and recent changes
"""

import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

def get_current_branch(project_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_root,
            capture_output=True,
            check=True
        )
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError:
        return "unknown"

def get_main_commits_since_branch(project_root: Path, branch_name: str) -> list[str]:
    """Get commits on main since this branch diverged."""
    try:
        result = subprocess.run(
            ["git", "log", f"{branch_name}..main", "--oneline"],
            cwd=project_root,
            capture_output=True,
            check=True
        )
        return result.stdout.decode().strip().split("\n") if result.stdout else []
    except subprocess.CalledProcessError:
        return []

def check_conflicts(project_root: Path) -> dict:
    """Check for potential conflicts and changes."""
    cicadas = project_root / ".cicadas"
    
    if not cicadas.exists():
        return {"error": "Cicadas not initialized"}
    
    registry = json.loads((cicadas / "registry.json").read_text())
    index = json.loads((cicadas / "index.json").read_text())
    
    current_branch = get_current_branch(project_root)
    current_reg = registry.get("branches", {}).get(current_branch)
    
    if not current_reg:
        return {
            "warning": f"Current branch '{current_branch}' is not registered with Chorus",
            "suggestion": "Register with branch.py or switch to a registered branch"
        }
    
    my_modules = set(current_reg.get("modules", []))
    
    # Check other branches in the brood for overlap
    other_branches = []
    for branch_name, branch_info in registry.get("branches", {}).items():
        if branch_name == current_branch:
            continue
        their_modules = set(branch_info.get("modules", []))
        overlap = my_modules.intersection(their_modules)
        if overlap:
            other_branches.append({
                "branch": branch_name,
                "owner": branch_info.get("owner"),
                "intent": branch_info.get("intent"),
                "status": branch_info.get("status"),
                "overlapping_modules": list(overlap)
            })
    
    # Check for new commits on main
    main_commits = get_main_commits_since_branch(project_root, current_branch)
    
    # Check for recent index entries (merged after this branch started)
    branch_created = current_reg.get("created_at")
    recent_changes = []
    if branch_created:
        for entry in index.get("entries", []):
            if entry.get("timestamp", "") > branch_created:
                recent_changes.append(entry)
    
    return {
        "current_branch": current_branch,
        "my_modules": list(my_modules),
        "brood_conflicts": other_branches if other_branches else None,
        "main_commits_since_branch": main_commits if main_commits else None,
        "changes_since_branch_created": recent_changes if recent_changes else None,
        "chorus_recommendation": _get_recommendation(other_branches, main_commits, recent_changes)
    }

def _get_recommendation(conflicts, commits, changes) -> str:
    if not conflicts and not commits and not changes:
        return "✓ No conflicts or changes detected. Safe to continue."
    
    parts = []
    if conflicts:
        parts.append(f"⚠️  {len(conflicts)} branch(es) in the brood working on overlapping modules")
    if commits:
        parts.append(f"📥 {len(commits)} commit(s) on main since you branched")
    if changes:
        parts.append(f"📝 {len(changes)} change(s) merged since you started")
    
    parts.append("Consider rebasing or coordinating with other contributors.")
    return " | ".join(parts)

def main():
    parser = argparse.ArgumentParser(description="Check for Cicadas conflicts via Chorus")
    parser.add_argument("project_root", type=Path, nargs="?", default=Path.cwd())
    args = parser.parse_args()
    
    result = check_conflicts(args.project_root.resolve())
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    exit(main())
```

### scripts/archive.py

```python
#!/usr/bin/env python3
"""
Archive forward docs (create husks) and deregister branch via Chorus.

Usage:
    python archive.py <project_root> <branch_name>

Archives:
    .cicadas/forward/{branch}/ → .cicadas/archive/{timestamp}-{branch}/
    
Also removes branch from registry.json
"""

import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

def archive_branch(project_root: Path, branch_name: str) -> dict:
    """Archive forward docs (create husk) and deregister branch."""
    cicadas = project_root / ".cicadas"
    
    if not cicadas.exists():
        return {"success": False, "error": "Cicadas not initialized"}
    
    # Load and update registry
    registry_path = cicadas / "registry.json"
    registry = json.loads(registry_path.read_text())
    
    if branch_name not in registry.get("branches", {}):
        return {
            "success": False,
            "error": f"Branch '{branch_name}' not found in Chorus registry"
        }
    
    # Archive forward docs (create husk)
    forward_dir = cicadas / "forward" / branch_name
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    archive_name = f"{timestamp}-{branch_name}"
    archive_dir = cicadas / "archive" / archive_name
    
    archived_files = []
    if forward_dir.exists():
        shutil.move(str(forward_dir), str(archive_dir))
        archived_files = [f.name for f in archive_dir.iterdir() if f.is_file()]
    else:
        # Create empty archive marker
        archive_dir.mkdir(parents=True)
        (archive_dir / ".empty").write_text("No forward docs were present")
    
    # Remove from registry
    branch_info = registry["branches"].pop(branch_name)
    registry_path.write_text(json.dumps(registry, indent=2))
    
    return {
        "success": True,
        "branch": branch_name,
        "husk_location": str(archive_dir),
        "archived_files": archived_files,
        "deregistered": branch_info
    }

def main():
    parser = argparse.ArgumentParser(description="Archive Cicadas branch (create husk)")
    parser.add_argument("project_root", type=Path)
    parser.add_argument("branch_name")
    args = parser.parse_args()
    
    result = archive_branch(args.project_root.resolve(), args.branch_name)
    print(json.dumps(result, indent=2))
    return 0 if result["success"] else 1

if __name__ == "__main__":
    exit(main())
```

### scripts/update_index.py

```python
#!/usr/bin/env python3
"""
Append entry to Cicadas artifact index via Chorus.

Usage:
    python update_index.py <project_root> --branch <name> --summary "what changed" [--decisions "key decisions"] [--modules "mod1,mod2"]
"""

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

def update_index(
    project_root: Path,
    branch: str,
    summary: str,
    decisions: str = "",
    modules: list[str] = None
) -> dict:
    """Append entry to Cicadas artifact index."""
    cicadas = project_root / ".cicadas"
    index_path = cicadas / "index.json"
    
    if not index_path.exists():
        return {"success": False, "error": "Index not found. Run init.py first."}
    
    index = json.loads(index_path.read_text())
    
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "branch": branch,
        "summary": summary,
        "decisions": decisions if decisions else None,
        "modules_affected": modules if modules else []
    }
    
    # Remove None values
    entry = {k: v for k, v in entry.items() if v is not None}
    
    index.setdefault("entries", []).append(entry)
    index_path.write_text(json.dumps(index, indent=2))
    
    return {
        "success": True,
        "entry_number": len(index["entries"]),
        "entry": entry
    }

def main():
    parser = argparse.ArgumentParser(description="Update Cicadas artifact index")
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--branch", required=True, help="Branch name")
    parser.add_argument("--summary", required=True, help="What changed")
    parser.add_argument("--decisions", default="", help="Key decisions made")
    parser.add_argument("--modules", default="", help="Comma-separated modules affected")
    args = parser.parse_args()
    
    modules = [m.strip() for m in args.modules.split(",") if m.strip()]
    
    result = update_index(
        project_root=args.project_root.resolve(),
        branch=args.branch,
        summary=args.summary,
        decisions=args.decisions,
        modules=modules
    )
    
    print(json.dumps(result, indent=2))
    return 0 if result["success"] else 1

if __name__ == "__main__":
    exit(main())
```

### scripts/utils.py

```python
#!/usr/bin/env python3
"""
Shared utilities for Chorus scripts.
"""

import json
from pathlib import Path

def load_json(path: Path) -> dict:
    """Load JSON file."""
    return json.loads(path.read_text())

def save_json(path: Path, data: dict):
    """Save JSON file with formatting."""
    path.write_text(json.dumps(data, indent=2))

def get_cicadas_root(project_root: Path) -> Path:
    """Get .cicadas directory path."""
    return project_root / ".cicadas"

def ensure_cicadas_exists(project_root: Path) -> bool:
    """Check if Cicadas is initialized."""
    return (project_root / ".cicadas").exists()
```

---

## Part 5: Templates

### templates/app-snapshot.md

```markdown
# {Project Name} — Cicadas Snapshot

> Generated by Chorus on {timestamp}. Do not edit manually.
> Regenerated from code on each merge.

## Overview

{2-3 paragraph description of what this application does, its purpose, and primary users}

## Architecture

{High-level architecture description — key patterns, data flow, deployment model}

## Modules

| Module | Purpose | Key Files |
|--------|---------|-----------|
| {name} | {one-line purpose} | {main files} |

## Key Decisions

{Accumulated architectural decisions with rationale}

### {Decision Title}
- **Decision**: {what was decided}
- **Rationale**: {why}
- **Date**: {when}
- **Alternatives considered**: {what else was evaluated}

## External Dependencies

| Dependency | Purpose | Notes |
|------------|---------|-------|
| {name} | {why it's used} | {version constraints, etc.} |

## Configuration

{Key configuration options and environment variables}

## Entry Points

{Main entry points — CLI commands, API endpoints, etc.}
```

### templates/module-snapshot.md

```markdown
# Module: {Module Name}

> Generated by Chorus on {timestamp}. Do not edit manually.

## Purpose

{What this module does and why it exists}

## Key Abstractions

{Main classes, functions, or concepts and their roles}

## Patterns Used

{Design patterns, architectural patterns employed}

## Internal Structure

{How the module is organized — submodules, key files}

## Interfaces

### Exports (public API)
{What this module exposes to others}

### Dependencies (imports from other modules)
{What this module depends on}

## Key Decisions

{Module-specific decisions with rationale}

## Gotchas

{Non-obvious behaviors, edge cases, things to watch out for}
```

### templates/forward-docs/prd.md

```markdown
# PRD: {Feature Name}

## Problem Statement

{What user problem are we solving? Why now?}

## Success Criteria

{How will we know this succeeded?}

## User Stories

{Key user stories — who, what, why}

## Scope

### In Scope
{What's included}

### Out of Scope
{What's explicitly excluded}

## Requirements

### Functional
{What the system must do}

### Non-Functional
{Performance, security, etc.}

## Open Questions

{Unresolved questions to address during implementation}
```

### templates/forward-docs/approach.md

```markdown
# Technical Approach: {Feature Name}

## Summary

{One paragraph overview of the approach}

## Modules Affected

{List of modules this will touch and how}

## Design

{Technical design — new components, changes to existing, data models}

## Alternatives Considered

{What else was evaluated and why this approach was chosen}

## Risks

{Technical risks and mitigations}

## Dependencies

{External dependencies, prerequisites, sequencing}
```

### templates/forward-docs/tasks.md

```markdown
# Tasks: {Feature Name}

## Task Breakdown

### 1. {Task Title}
- **Description**: {what needs to be done}
- **Acceptance criteria**: {how we know it's done}
- **Estimated effort**: {small/medium/large}

### 2. {Task Title}
...

## Sequencing

{Which tasks depend on others, suggested order}

## Testing Strategy

{How this will be tested}
```

---

## Part 6: Reference Documents

### references/bootstrap.md

```markdown
# Bootstrapping Cicadas on an Existing Project

When initializing Cicadas on a project with existing code, you need to generate
the initial snapshot without any forward docs to draw from.

## Process

1. **Initialize structure**: Run `scripts/init.py {project_root}`

2. **Analyze the codebase**:
   - Read the main entry points
   - Identify module boundaries
   - Understand key patterns and decisions
   - Note external dependencies

3. **Generate app-level snapshot**:
   - Use `templates/app-snapshot.md` as structure
   - Fill in based on code analysis
   - For "Key Decisions" section, infer from code patterns or mark as "inherited"
   - Write to `.cicadas/canon/app.md`

4. **Generate module snapshots**:
   - Create one snapshot per logical module
   - Use `templates/module-snapshot.md` as structure
   - Write to `.cicadas/canon/modules/{module-name}.md`

5. **Seed the artifact index**:
   ```bash
   python scripts/update_index.py {project_root} \
     --branch "bootstrap" \
     --summary "Initial Cicadas bootstrap from existing codebase" \
     --decisions "Snapshots generated from code analysis"
   ```

## Tips

- Don't try to document everything — focus on what a new contributor would need
- It's okay if the initial snapshot is incomplete; it will improve with each merge
- If existing docs exist (README, architecture docs), use them as input
- Mark uncertain information with "[inferred]" or "[needs verification]"
```

### references/branch-workflow.md

```markdown
# Branch Workflow

## Starting a Branch

### Prerequisites
- Forward docs prepared (PRD, approach, tasks)
- Clear understanding of scope and affected modules

### Steps

1. **Check current state**:
   ```bash
   python {skill_path}/scripts/status.py
   ```

2. **Create and register branch with Chorus**:
   ```bash
   python {skill_path}/scripts/branch.py feature-xyz \
     --intent "Add caching layer for API responses" \
     --modules "api,cache,config" \
     --owner "claude-agent-1"
   ```

3. **Review conflict warnings** — if Chorus detects conflicts, coordinate with the brood

4. **Place forward docs**:
   - Copy or create PRD, approach, tasks in `.cicadas/forward/{branch}/`
   - These will be consumed during synthesis and then become husks

5. **Load context**:
   - Read relevant Cicadas snapshots from `.cicadas/canon/`
   - Review artifact index for recent history
   - Understand the current state before making changes

## During Implementation

- Work normally on code
- If design changes significantly, update forward docs (don't maintain old versions)
- Periodically ask Chorus to check for changes via `check.py`
- For emergent design: embrace short cycles, revise forward docs as understanding evolves
```

### references/synthesis.md

```markdown
# Snapshot Synthesis

Synthesis is the process of generating/updating Cicadas snapshots from:
- The actual implementation (code)
- The expiring forward docs (intent and rationale)
- The artifact index (historical context)
- The previous snapshot (continuity)

## When to Synthesize

- Before merging a branch to main
- After significant implementation milestones (optional checkpoints)

## Process

### 1. Gather Inputs

Read:
- Current code changes (git diff or full module read)
- Forward docs from `.cicadas/forward/{branch}/`
- Current Cicadas snapshot(s) being affected
- Recent artifact index entries

### 2. Determine Scope

What snapshots need updating?
- App-level: if architectural changes, new modules, or cross-cutting concerns
- Module-level: for each module with significant changes

### 3. Synthesize Updates

For each snapshot being updated:

**Preserve**:
- Existing content that's still accurate
- Historical decisions (append, don't replace)
- Information not affected by this change

**Update**:
- Sections affected by the implementation
- Module interfaces if they changed
- Dependencies if they changed

**Add**:
- New decisions with rationale (pull from forward docs before they become husks)
- New patterns or abstractions introduced
- New gotchas discovered during implementation

**Remove**:
- Information that's no longer true
- Deprecated patterns or interfaces

### 4. Capture Rationale

The forward docs contain the "why" — extract key decisions before they expire:
- Why was this approach chosen?
- What alternatives were considered?
- What tradeoffs were made?

Add these to the "Key Decisions" section of the appropriate snapshot.

### 5. Review

Before finalizing:
- Does the snapshot accurately reflect the implementation?
- Would a new contributor understand the system from this?
- Are the decisions documented with sufficient rationale?

## Output

- Updated `.cicadas/canon/app.md` (if scope warrants)
- Updated `.cicadas/canon/modules/{name}.md` for affected modules
- These are written directly — no intermediate format
```

### references/merge-workflow.md

```markdown
# Merge Workflow

## Prerequisites

- Implementation complete
- Synthesis complete (snapshots updated)
- Human has reviewed synthesized snapshots

## Steps

### 1. Final Conflict Check

```bash
python {skill_path}/scripts/check.py
```

Address any conflicts Chorus identifies before proceeding.

### 2. Archive Forward Docs (Create Husks)

```bash
python {skill_path}/scripts/archive.py {project_root} {branch_name}
```

This:
- Moves `.cicadas/forward/{branch}/` to `.cicadas/archive/{timestamp}-{branch}/`
- Removes branch from Chorus registry

### 3. Update Artifact Index

```bash
python {skill_path}/scripts/update_index.py {project_root} \
  --branch {branch_name} \
  --summary "Brief description of what changed" \
  --decisions "Key decisions: chose X over Y because Z" \
  --modules "mod1,mod2"
```

### 4. Git Merge

```bash
git checkout main
git merge {branch_name}
```

Handle any code conflicts through normal git workflow.

### 5. Push and Notify

- Push to remote
- Other active branches in the brood should run `check.py` to see what changed

## Post-Merge

The artifact index now contains a record of this change.
The Cicadas snapshots reflect the current state.
The forward docs are now husks in the archive.
Next iteration starts fresh with new forward docs.
```

### references/conflict-detection.md

```markdown
# Conflict Detection

Chorus uses advisory conflict detection — warnings, not blocks.

## Types of Conflicts

### Module Overlap
Two branches in the brood registered with overlapping modules.

Detection: Compare `modules` arrays in registry entries.

Response: Warning with details of who's working on what.

### Semantic Conflict
Two branches with related intent even if modules don't overlap.

Detection: Not automated — requires human judgment or LLM analysis.

Response: Flag for human review if intents seem related.

### Stale Branch
Branch working against outdated understanding of main.

Detection: Compare branch creation time against recent index entries.

Response: Suggest rebase or review of recent changes.

## Running Conflict Checks

```bash
# Check current branch against the brood
python {skill_path}/scripts/check.py

# View all active branches in the brood
python {skill_path}/scripts/status.py
```

## Responding to Conflicts

Conflicts are advisory — options include:

1. **Coordinate**: Talk to the other branch owner, divide work
2. **Proceed carefully**: Be aware of overlap, plan to reconcile at merge
3. **Wait**: Let the other branch merge first, then rebase
4. **Merge scopes**: Combine into a single branch if overlap is significant

The goal is awareness, not prevention. Sometimes parallel work on the same area is intentional and fine.
```

---

## Part 7: Development Workflow

### Setting Up for Development

```bash
# In your project directory (e.g., loom-eval)
mkdir -p _dev/chorus/{templates,scripts,references}
mkdir -p _dev/chorus/templates/{forward-docs,schemas}

# Create the files from this manual
# SKILL.md, all scripts, all templates, all references
```

### Testing the Skill Locally

```bash
# From your project root, tell Claude:
"Read the skill at _dev/chorus/SKILL.md and use it to initialize Cicadas for this project"

# Or test scripts directly:
python _dev/chorus/scripts/init.py .
python _dev/chorus/scripts/status.py .
```

### Iteration Cycle

1. Edit skill files in `_dev/chorus/`
2. Test by asking Claude to use the skill
3. Observe behavior, note issues
4. Revise skill files
5. Repeat

### Packaging for Distribution

When stable:
```bash
python /mnt/skills/examples/skill-creator/scripts/package_skill.py _dev/chorus/
# Upload chorus.skill to Claude.ai
```

---

## Part 8: PoC Test Plan

### Phase 1: Single Lifecycle

**Goal**: Validate full Cicadas cycle on one feature.

1. Bootstrap Cicadas on Loom Eval
2. Create forward docs for a small feature
3. `chorus branch` → implement → `synthesize` → `merge`
4. Verify:
   - Cicadas snapshot is accurate
   - Forward docs are archived as husks
   - Artifact index has entry
   - Fresh agent can understand system from snapshot alone

### Phase 2: Parallel Work (Brood Test)

**Goal**: Test conflict detection with two agents.

1. Create two features with overlapping scope
2. Agent A: branch and start work
3. Agent B: branch, observe Chorus conflict warning
4. Agent A: complete and merge
5. Agent B: run check, see notification from Chorus
6. Agent B: adapt and merge
7. Verify:
   - Both features in snapshot
   - No orphaned artifacts
   - Brood conflicts were surfaced

### Success Criteria

- Cicadas snapshot accurate enough for fresh agent to work from
- Forward docs successfully expire (become husks) without losing critical context
- Chorus catches at least one synthetic collision in the brood
- Workflow feels lighter than traditional SDD maintenance

---

## Quick Reference

### Chorus Commands

```bash
# Initialize Cicadas
python {skill}/scripts/init.py {project}

# Create branch (join the brood)
python {skill}/scripts/branch.py {name} --intent "..." --modules "..."

# Check status
python {skill}/scripts/status.py {project}

# Check for brood conflicts
python {skill}/scripts/check.py {project}

# Archive forward docs (create husk)
python {skill}/scripts/archive.py {project} {branch}

# Update artifact index
python {skill}/scripts/update_index.py {project} --branch {name} --summary "..."
```

### File Locations

```
.cicadas/canon/app.md           # App-level Cicadas snapshot
.cicadas/canon/modules/*.md     # Module snapshots
.cicadas/registry.json          # Active brood (branches)
.cicadas/index.json             # Change history
.cicadas/forward/{branch}/      # Active forward docs
.cicadas/archive/               # Husks (expired forward docs)
```

### Canon Hierarchy

```
code (main)          ← highest authority
Cicadas snapshots
branch registry
branch code
branch docs
archive (husks)      ← lowest authority
```

### Terminology

| Term | Meaning |
|------|---------|
| **Cicadas** | The methodology |
| **Chorus** | The orchestrator (skill + scripts) |
| **Brood** | Active branches / concurrent workers |
| **Husk** | Archived forward docs |
| **Snapshot** | Canonical documentation |

---

*End of manual. Use this to build the Chorus skill and test Cicadas on your project.*