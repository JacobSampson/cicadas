import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add current directory to path to allow importing utils if run from same dir
# Or assume run from project root and use scripts.chorus.scripts.utils?
# The other scripts use 'from utils import ...' which implies they are run with PYTHONPATH set or from the dir?
# Actually 'init.py' uses 'from utils import ...'.
# Let's adjust sys.path to be safe.
sys.path.append(str(Path(__file__).parent))
from utils import load_json, save_json

def register_existing(root_path, branch_name, intent, brood=None, modules=""):
    root = Path(root_path).resolve()
    cicadas = root / ".cicadas"
    registry_path = cicadas / "registry.json"
    
    if not registry_path.exists():
        print(f"Error: Registry not found at {registry_path}")
        sys.exit(1)

    registry = load_json(registry_path)
    
    if branch_name in registry.get("branches", {}):
        print(f"Branch {branch_name} already registered.")
        return

    print(f"Registering existing branch '{branch_name}' in {registry_path}...")
    
    my_mods = set(m.strip() for m in modules.split(",") if m.strip())
    
    branch_info = {
        "intent": intent,
        "modules": list(my_mods),
        "owner": "unknown",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    if brood:
         if brood not in registry.get("broods", {}):
            print(f"Warning: Brood '{brood}' not found in registry.")
            # Proceed anyway? Or fail? The original branch.py warns but proceeds.
         else:
            branch_info["brood"] = brood
    registry.setdefault("branches", {})[branch_name] = branch_info
    save_json(registry_path, registry)
    print(f"Successfully registered branch '{branch_name}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Register an existing git branch in the Chorus registry.")
    parser.add_argument("--root", required=True, help="Path to project root")
    parser.add_argument("--branch", required=True, help="Name of the existing branch")
    parser.add_argument("--intent", required=True, help="Description of the branch intent")
    parser.add_argument("--brood", help="Name of the brood to associate with")
    parser.add_argument("--modules", default="", help="Comma-separated list of modules")
    
    args = parser.parse_args()
    register_existing(args.root, args.branch, args.intent, args.brood, args.modules)
