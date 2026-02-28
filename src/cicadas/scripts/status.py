# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

from utils import get_project_root, load_json


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


if __name__ == "__main__":
    show_status()
