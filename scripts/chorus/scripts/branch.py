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
