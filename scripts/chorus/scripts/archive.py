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
