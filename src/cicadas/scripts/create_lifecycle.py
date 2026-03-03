# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

"""
Create or update lifecycle.json for an initiative (drafts or active).
Loads default template and sets pr_boundaries from CLI flags.
Defaults: specs=no, initiatives=yes, features=yes, tasks=no.
"""

import argparse
import json
from pathlib import Path

from utils import get_project_root, load_json, save_json


def _templates_dir():
    """Directory containing lifecycle-default.json (sibling of scripts/)."""
    script_dir = Path(__file__).resolve().parent
    return script_dir.parent / "templates"


def create_lifecycle(initiative_name, dest="drafts", pr_specs=False, pr_initiatives=True, pr_features=True, pr_tasks=False):
    root = get_project_root()
    cicadas = root / ".cicadas"
    templates = _templates_dir()
    default_path = templates / "lifecycle-default.json"

    if not default_path.exists():
        # Fallback: minimal default
        data = {
            "pr_boundaries": {"specs": False, "initiatives": True, "features": True, "tasks": False},
            "steps": [
                {"id": "kickoff_initiative", "name": "Kickoff initiative", "description": "Promote drafts to active, create initiative branch"},
                {"id": "kickoff_features", "name": "Kickoff feature branches", "description": "For each partition, run branch.py"},
                {"id": "feature_work", "name": "Feature work (per feature)", "description": "Task branches → implement → test → reflect → commit → push → PR (if enabled) → merge to feature", "opens_pr": True},
                {"id": "complete_feature", "name": "Complete each feature", "description": "Update index, push, open PR to initiative (if enabled), merge", "opens_pr": True},
                {"id": "complete_initiative", "name": "Complete initiative", "description": "Open PR to main (if enabled), merge, synthesize canon, archive", "opens_pr": True},
            ],
        }
    else:
        with open(default_path) as f:
            data = json.load(f)

    data["initiative"] = initiative_name
    data["pr_boundaries"] = {
        "specs": pr_specs,
        "initiatives": pr_initiatives,
        "features": pr_features,
        "tasks": pr_tasks,
    }

    if dest == "active":
        out_dir = cicadas / "active" / initiative_name
    else:
        out_dir = cicadas / "drafts" / initiative_name

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "lifecycle.json"
    save_json(out_path, data)
    print(f"Wrote {out_path}")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create lifecycle.json for an initiative (drafts or active)")
    parser.add_argument("name", help="Initiative name")
    parser.add_argument("--active", action="store_true", help="Write to active/{name}/ instead of drafts/{name}/")
    parser.add_argument("--pr-specs", action="store_true", help="Open PR at specs boundary (default: no)")
    parser.add_argument("--pr-initiatives", action="store_true", default=True, help="Open PR at initiative→main (default: yes)")
    parser.add_argument("--no-pr-initiatives", action="store_false", dest="pr_initiatives", help="Do not open PR at initiative→main")
    parser.add_argument("--pr-features", action="store_true", default=True, help="Open PR at feature→initiative (default: yes)")
    parser.add_argument("--no-pr-features", action="store_false", dest="pr_features", help="Do not open PR at feature→initiative")
    parser.add_argument("--pr-tasks", action="store_true", help="Open PR at task→feature (default: no)")
    args = parser.parse_args()

    dest = "active" if args.active else "drafts"
    create_lifecycle(
        args.name,
        dest=dest,
        pr_specs=args.pr_specs,
        pr_initiatives=args.pr_initiatives,
        pr_features=args.pr_features,
        pr_tasks=args.pr_tasks,
    )
