import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from utils import get_project_root, load_json, save_json

def prune(name, item_type, no_restore=False, force=False):
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry_path = cicadas / "registry.json"
    registry = load_json(registry_path)
    
    # Paths
    if item_type == "branch":
        # 1. Validate Branch
        if name not in registry.get("branches", {}):
            print(f"Error: Branch '{name}' not found in registry.")
            return
        
        forward_dir = cicadas / "forward" / name
        incubator_dir = cicadas / "incubator" / name
        
        # 2. Delete Git Branch
        try:
            # Check if branch exists in git first
            subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{name}"], check=True)
            print(f"🗑️  Deleting git branch '{name}'...")
            subprocess.run(["git", "branch", "-D", name], check=True)
        except subprocess.CalledProcessError:
            print(f"Warning: Git branch '{name}' not found or could not be deleted.")

        # 3. Restore to Incubator (unless no_restore)
        if not no_restore and forward_dir.exists():
            print(f"♻️  Restoring forward docs to incubator: {incubator_dir}...")
            incubator_dir.mkdir(parents=True, exist_ok=True)
            for item in forward_dir.iterdir():
                if item.name.startswith("."): continue
                shutil.move(str(item), str(incubator_dir / item.name))
        
        # 4. Cleanup Forward Dir
        if forward_dir.exists():
            shutil.rmtree(forward_dir)

        # 5. Remove from Registry
        del registry["branches"][name]
        
        # Also remove from brood's branch list if applicable
        for brood_name, brood_data in registry.get("broods", {}).items():
            if name in brood_data.get("branches", []):
                brood_data["branches"].remove(name)
        
        print(f"✅ Pruned branch '{name}'. Registry updated.")

    elif item_type == "brood":
        # 1. Validate Brood
        if name not in registry.get("broods", {}):
            print(f"Error: Brood '{name}' not found in registry.")
            return
        
        brood_data = registry["broods"][name]
        active_branches = brood_data.get("branches", [])
        
        if active_branches and not force:
            print(f"Error: Brood '{name}' has active branches: {', '.join(active_branches)}")
            print("Use --force to prune anyway (this will orphan the branches in the registry).")
            return

        forward_dir = cicadas / "forward" / "broods" / name
        incubator_dir = cicadas / "incubator" / name

        # 2. Restore to Incubator
        if not no_restore and forward_dir.exists():
            print(f"♻️  Restoring brood docs to incubator: {incubator_dir}...")
            incubator_dir.mkdir(parents=True, exist_ok=True)
            for item in forward_dir.iterdir():
                if item.name.startswith("."): continue
                shutil.move(str(item), str(incubator_dir / item.name))
        
        # 3. Cleanup Forward Dir
        if forward_dir.exists():
            shutil.rmtree(forward_dir)

        # 4. Remove from Registry
        del registry["broods"][name]
        print(f"✅ Pruned brood '{name}'. Registry updated.")

    save_json(registry_path, registry)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prune (delete/rollback) a branch or brood.")
    parser.add_argument("name", help="Name of the branch or brood to prune")
    parser.add_argument("--type", choices=["branch", "brood"], required=True, help="Type of item to prune")
    parser.add_argument("--no-restore", action="store_true", help="Do not move docs back to incubator (permanent delete)")
    parser.add_argument("--force", action="store_true", help="Force prune brood even if it has active branches")
    
    args = parser.parse_args()
    prune(args.name, args.type, args.no_restore, args.force)
