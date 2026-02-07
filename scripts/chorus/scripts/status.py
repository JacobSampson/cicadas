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
