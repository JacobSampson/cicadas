# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import shutil
import subprocess
import sys

from utils import get_default_branch, get_project_root, load_json, save_json

LIGHTWEIGHT_PREFIXES = ("tweak/", "fix/")


def prompt_choice(question, choices):
    """Prompt the user with lettered choices; return the chosen key."""
    labels = "/".join(f"[{k}]{v}" for k, v in choices.items())
    while True:
        answer = input(f"{question} {labels}: ").strip().upper()
        if answer in choices:
            return answer
        print(f"  Please enter one of: {', '.join(choices.keys())}")


def handle_docs(initiative_name, cicadas):
    """Prompt whether to move active specs to drafts or delete them."""
    active = cicadas / "active" / initiative_name
    if not active.exists():
        return
    choice = prompt_choice(
        f"Active specs exist for '{initiative_name}'.",
        {"D": "Move to drafts", "X": "Delete"},
    )
    if choice == "D":
        drafts = cicadas / "drafts" / initiative_name
        drafts.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(active), str(drafts))
        print(f"  Specs moved to drafts/{initiative_name}")
    else:
        shutil.rmtree(str(active))
        print(f"  Specs deleted for '{initiative_name}'")


def delete_branch(branch_name, root):
    """Checkout default branch then force-delete the given branch."""
    default = get_default_branch()
    try:
        subprocess.run(["git", "checkout", default], check=True, cwd=root, capture_output=True)
        subprocess.run(["git", "branch", "-D", branch_name], check=True, cwd=root)
        print(f"  Deleted branch: {branch_name}")
    except subprocess.CalledProcessError:
        print(f"  Warning: Could not delete git branch '{branch_name}'")


def abort_lightweight(branch_name, initiative_name, root, cicadas, registry):
    """Abort a tweak/ or fix/ branch plus its paired initiative."""
    print(f"\nAborting {branch_name}...")

    # Remove the tweak/fix branch
    delete_branch(branch_name, root)
    registry.setdefault("branches", {}).pop(branch_name, None)

    # Remove the paired initiative branch
    initiative_branch = f"initiative/{initiative_name}"
    delete_branch(initiative_branch, root)
    registry.setdefault("initiatives", {}).pop(initiative_name, None)

    save_json(cicadas / "registry.json", registry)
    handle_docs(initiative_name, cicadas)
    print(f"\nAborted: {branch_name}")


def abort_feature(branch_name, initiative_name, root, cicadas, registry):
    """Abort a feat/ branch, with optional escalation to abort the whole initiative."""
    choice = prompt_choice(
        f"Aborting feature '{branch_name}'.",
        {"F": "Abort this feature only", "I": "Abort the entire initiative"},
    )

    print(f"\nAborting {branch_name}...")
    delete_branch(branch_name, root)
    registry.setdefault("branches", {}).pop(branch_name, None)
    save_json(cicadas / "registry.json", registry)

    if choice == "I":
        print(f"\nAlso aborting initiative '{initiative_name}'...")
        initiative_branch = f"initiative/{initiative_name}"
        delete_branch(initiative_branch, root)
        registry.setdefault("initiatives", {}).pop(initiative_name, None)
        save_json(cicadas / "registry.json", registry)
        handle_docs(initiative_name, cicadas)
        print(f"\nAborted: {branch_name} + initiative/{initiative_name}")
    else:
        # Specs live under the initiative name, not the feature branch name
        handle_docs(initiative_name, cicadas)
        print(f"\nAborted: {branch_name}")


def main():
    root = get_project_root()
    cicadas = root / ".cicadas"

    # Detect current branch
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            check=True, cwd=root, capture_output=True, text=True,
        )
        branch_name = result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Error: Could not determine current git branch.")
        sys.exit(1)

    registry = load_json(cicadas / "registry.json")

    if any(branch_name.startswith(p) for p in LIGHTWEIGHT_PREFIXES):
        prefix = next(p for p in LIGHTWEIGHT_PREFIXES if branch_name.startswith(p))
        # initiative name is stored in the branch registry entry
        branch_meta = registry.get("branches", {}).get(branch_name, {})
        initiative_name = branch_meta.get("initiative") or branch_name[len(prefix):]
        abort_lightweight(branch_name, initiative_name, root, cicadas, registry)

    elif branch_name.startswith("feat/"):
        branch_meta = registry.get("branches", {}).get(branch_name, {})
        initiative_name = branch_meta.get("initiative") or branch_name[len("feat/"):]
        abort_feature(branch_name, initiative_name, root, cicadas, registry)

    elif branch_name.startswith("initiative/"):
        initiative_name = branch_name[len("initiative/"):]
        print(f"\nAborting initiative '{initiative_name}'...")
        delete_branch(branch_name, root)
        registry.setdefault("initiatives", {}).pop(initiative_name, None)
        save_json(cicadas / "registry.json", registry)
        handle_docs(initiative_name, cicadas)
        print(f"\nAborted: {branch_name}")

    else:
        print(f"Nothing to abort from branch '{branch_name}'.")
        print("Abort is available from: tweak/, fix/, feat/, or initiative/ branches.")
        sys.exit(0)


if __name__ == "__main__":
    main()
