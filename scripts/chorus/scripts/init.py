import argparse
import json
from pathlib import Path
from utils import save_json, get_project_root

def init_cicadas(root):
    cicadas = root / ".cicadas"
    cicadas.mkdir(exist_ok=True)
    (cicadas / "canon/modules").mkdir(parents=True, exist_ok=True)
    (cicadas / "forward").mkdir(exist_ok=True)
    (cicadas / "forward/broods").mkdir(parents=True, exist_ok=True)
    (cicadas / "incubator").mkdir(exist_ok=True)
    (cicadas / "archive").mkdir(exist_ok=True)
    
    save_json(cicadas / "registry.json", {
        "schema_version": "1.1", 
        "branches": {},
        "broods": {}
    })
    save_json(cicadas / "index.json", {"schema_version": "1.0", "entries": []})
    save_json(cicadas / "config.json", {"project_name": root.name})
    
    # Create empty app.md
    app_md = (cicadas / "canon/app.md")
    if not app_md.exists():
        app_md.write_text("# App Snapshot\n\n[Pending Synthesis]")
    print(f"Initialized Cicadas in {cicadas}")

if __name__ == "__main__":
    init_cicadas(get_project_root())
