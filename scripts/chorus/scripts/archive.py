import argparse
import shutil
from pathlib import Path
from datetime import datetime, timezone
from utils import get_project_root, load_json, save_json

def archive_item(name, is_brood=False):
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")
    
    registry_key = "broods" if is_brood else "branches"
    if name not in registry.get(registry_key, {}):
        print(f"Error: {registry_key.capitalize()} {name} not found.")
        return

    # Move docs to archive
    if is_brood:
        source = cicadas / "forward" / "broods" / name
    else:
        source = cicadas / "forward" / name

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    prefix = "brood-" if is_brood else "branch-"
    husk = cicadas / "archive" / f"{ts}-{prefix}{name}"
    
    if source.exists():
        shutil.move(str(source), str(husk))
        print(f"Archived docs to {husk.name}")

    # Remove from registry
    del registry[registry_key][name]
    save_json(cicadas / "registry.json", registry)
    print(f"Deregistered {registry_key} {name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--brood", action="store_true", help="Archive an entire brood")
    args = parser.parse_args()
    archive_item(args.name, is_brood=args.brood)
