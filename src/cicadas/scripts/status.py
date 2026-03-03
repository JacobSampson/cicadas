# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import subprocess

from utils import get_default_branch, get_project_root, load_json


def _is_merged_into(root, source_ref, target_ref):
    """Return True if source is merged into target (source's tip is ancestor of target's tip)."""
    try:
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", source_ref, target_ref],
            cwd=root,
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _ref_exists(root, ref):
    """Return True if ref or branch name exists."""
    try:
        subprocess.run(["git", "rev-parse", "--verify", ref], cwd=root, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def _lifecycle_merge_status(root, cicadas, registry, initiative_name, default_branch):
    """For one initiative with active lifecycle, return (merged_pairs, next_step_name)."""
    active_dir = cicadas / "active" / initiative_name
    lifecycle_path = active_dir / "lifecycle.json"
    if not lifecycle_path.exists():
        return [], None
    lifecycle = load_json(lifecycle_path)
    steps = lifecycle.get("steps", [])
    if not steps:
        return [], None

    initiative_branch = f"initiative/{initiative_name}"
    branches = registry.get("branches", {})
    feat_branches = [n for n, i in branches.items() if i.get("initiative") == initiative_name and not (n.startswith("fix/") or n.startswith("tweak/"))]

    merged = []
    # Check each feature -> initiative (use refs/heads/ for local)
    for fb in feat_branches:
        if _ref_exists(root, fb) and _ref_exists(root, initiative_branch):
            if _is_merged_into(root, fb, initiative_branch):
                merged.append((fb, initiative_branch))
    # Check initiative -> default
    if _ref_exists(root, initiative_branch) and _ref_exists(root, default_branch):
        if _is_merged_into(root, initiative_branch, default_branch):
            merged.append((initiative_branch, default_branch))

    # Next step: if initiative merged to default -> "Complete initiative" (already done) or first step name; else if all features merged to initiative -> "Complete initiative"; else "Complete each feature" or last step name
    next_step = None
    if _ref_exists(root, initiative_branch) and _is_merged_into(root, initiative_branch, default_branch):
        next_step = "Initiative complete (merge to default done)."
    elif feat_branches and all(_ref_exists(root, fb) and _is_merged_into(root, fb, initiative_branch) for fb in feat_branches):
        next_step = next((s.get("name") for s in steps if s.get("id") == "complete_initiative"), steps[-1].get("name") if steps else None)
    else:
        next_step = next((s.get("name") for s in steps if s.get("id") == "complete_feature"), "Complete each feature")

    return merged, next_step


def show_status():
    root = get_project_root()
    cicadas = root / ".cicadas"
    registry = load_json(cicadas / "registry.json")

    print(f"Project: {root.name}\n")

    initiatives = registry.get("initiatives", {})
    print(f"Active Initiatives ({len(initiatives)}):")
    for name, info in initiatives.items():
        signals = info.get("signals", [])
        print(f"  - {name}: {info['intent']}")
        if signals:
            print(f"    Signals ({len(signals)}):")
            for s in signals[-3:]:  # Show last 3
                print(f"      [{s['timestamp']}] ({s.get('from_branch', '?')}): {s['message']}")

    branches = registry.get("branches", {})
    features = {n: i for n, i in branches.items() if not (n.startswith("fix/") or n.startswith("tweak/"))}
    fixes = {n: i for n, i in branches.items() if n.startswith("fix/")}
    tweaks = {n: i for n, i in branches.items() if n.startswith("tweak/")}

    if features:
        print(f"\nActive Feature Branches ({len(features)}):")
        for name, info in features.items():
            initiative = info.get("initiative", "standalone")
            print(f"  - {name}: {info['intent']} (Initiative: {initiative}, Modules: {', '.join(info.get('modules', []))})")

    if fixes:
        print(f"\nActive Bugs ({len(fixes)}):")
        for name, info in fixes.items():
            print(f"  - {name}: {info['intent']} (Modules: {', '.join(info.get('modules', []))})")

    if tweaks:
        print(f"\nActive Tweaks ({len(tweaks)}):")
        for name, info in tweaks.items():
            print(f"  - {name}: {info['intent']} (Modules: {', '.join(info.get('modules', []))})")

    # Lifecycle and merge status (git-based; optional)
    try:
        default_branch = get_default_branch()
        for init_name in initiatives:
            merged_pairs, next_step = _lifecycle_merge_status(root, cicadas, registry, init_name, default_branch)
            if merged_pairs or next_step:
                print(f"\nLifecycle ({init_name}):")
                for src, tgt in merged_pairs:
                    print(f"  Merged: {src} → {tgt}")
                if next_step:
                    print(f"  Next: {next_step}")
    except Exception:
        pass


if __name__ == "__main__":
    show_status()
