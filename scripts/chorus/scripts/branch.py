import argparse
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime, timezone
from utils import get_project_root, load_json, save_json

def create_branch(name, intent, modules, brood=None, owner="unknown"):
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
    branch_info = {
        "intent": intent,
        "modules": list(my_mods),
        "owner": owner,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    if brood:
        if brood not in registry.get("broods", {}):
            print(f"Warning: Brood {brood} not found. Branch registered without brood association.")
        else:
            branch_info["brood"] = brood
            registry["broods"][brood].setdefault("branches", []).append(name)

    registry.setdefault("branches", {})[name] = branch_info
    save_json(cicadas / "registry.json", registry)
    
    forward_dir = cicadas / "forward" / name
    forward_dir.mkdir(parents=True, exist_ok=True)

    # Check for incubator content and promote it
    incubator_dir = cicadas / "incubator" / name
    if incubator_dir.exists():
        print(f"🐣 Promoting incubator content from {incubator_dir} to {forward_dir}...")
        for item in incubator_dir.iterdir():
            if item.name.startswith("."): continue
            
            # If part of a brood, only promote branch-specific docs
            if brood and item.name in ["prd.md", "tech-design.md", "ux.md"]:
                print(f"  - Keeping shared doc {item.name} in incubator (Brood path handles it)")
                continue

            shutil.move(str(item), str(forward_dir / item.name))
        
        # Clean up incubator if empty
        try:
            incubator_dir.rmdir()
        except OSError:
            pass
    
    print(f"Registered branch {name}.")
    if conflicts:
        print(f"WARNING: Potential overlaps detected: {'; '.join(conflicts)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--intent", required=True)
    parser.add_argument("--modules", default="")
    parser.add_argument("--brood", help="Associate branch with an active brood")
    args = parser.parse_args()
    create_branch(args.name, args.intent, args.modules, brood=args.brood)
