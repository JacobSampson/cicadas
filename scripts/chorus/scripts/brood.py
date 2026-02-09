import argparse
import shutil
import json
from pathlib import Path
from datetime import datetime, timezone
from utils import get_project_root, load_json, save_json

def hatch_brood(name, intent, owner="unknown"):
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")
    
    if name in registry.get("broods", {}):
        print(f"Error: Brood {name} already exists.")
        return

    brood_dir = cicadas / "forward" / "broods" / name
    brood_dir.mkdir(parents=True, exist_ok=True)

    # Promote incubator content
    incubator_dir = cicadas / "incubator" / name
    if incubator_dir.exists():
        print(f"🐣 Hatching brood from incubator: {name}...")
        for item in incubator_dir.iterdir():
            if item.name.startswith("."): continue
            shutil.move(str(item), str(brood_dir / item.name))
        
        try:
            incubator_dir.rmdir()
        except OSError:
            pass
    else:
        print(f"Warning: No incubator content found for {name}. Creating empty brood.")

    # Register
    registry.setdefault("broods", {})[name] = {
        "intent": intent,
        "owner": owner,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "branches": []
    }
    save_json(cicadas / "registry.json", registry)
    print(f"Hatched brood: {name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--intent", required=True)
    args = parser.parse_args()
    hatch_brood(args.name, args.intent)
