# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path


def get_project_root():
    """Detect .cicadas folder or .git folder to find root."""
    curr = Path.cwd()
    for parent in [curr] + list(curr.parents):
        if (parent / ".cicadas").exists() or (parent / ".git").exists():
            return parent
    return curr


def get_default_branch():
    """Detect the default branch (main, master, etc.) from git."""
    import subprocess

    root = get_project_root()
    try:
        # Check symbolic-ref for the remote HEAD
        res = subprocess.check_output(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], cwd=root, stderr=subprocess.DEVNULL).decode().strip()
        return res.split("/")[-1]
    except Exception:
        # Fallback 1: check if 'main' exists locally
        try:
            subprocess.check_call(["git", "show-ref", "--verify", "--quiet", "refs/heads/main"], cwd=root)
            return "main"
        except Exception:
            # Fallback 2: return 'master'
            return "master"


def load_json(path):
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert Path objects to strings for JSON serialization
    def path_serializer(obj):
        if isinstance(obj, Path):
            return str(obj)
        raise TypeError(f"Type {type(obj)} not serializable")

    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=path_serializer)
