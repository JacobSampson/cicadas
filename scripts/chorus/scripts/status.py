import json
from pathlib import Path
from utils import get_project_root, load_json

def show_status():
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")
    
    print(f"Project: {root.name}")
    
    broods = registry.get("broods", {})
    if broods:
        print(f"\nActive Broods ({len(broods)}):")
        for name, info in broods.items():
            branch_count = len(info.get("branches", []))
            print(f"  - [Brood] {name}: {info['intent']} ({branch_count} branches active)")

    branches = registry.get("branches", {})
    if branches:
        print(f"\nActive Branches ({len(branches)}):")
        for name, info in branches.items():
            brood_tag = f" [Brood: {info['brood']}]" if info.get("brood") else ""
            print(f"  - {name}: {info['intent']}{brood_tag}")

if __name__ == "__main__":
    show_status()
