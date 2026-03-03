# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import io
import json
import unittest
from contextlib import redirect_stdout

import archive
import status
from base import CicadasTest


class TestArchiveStatus(CicadasTest):
    def test_archive_branch(self):
        name = "feat-to-archive"
        # Setup branch in registry and active spec
        with open(self.cicadas_dir / "registry.json", "r+") as f:
            reg = json.load(f)
            reg["branches"][name] = {"intent": "test"}
            f.seek(0)
            json.dump(reg, f)
            f.truncate()

        active_dir = self.cicadas_dir / "active" / name
        active_dir.mkdir(parents=True)
        (active_dir / "spec.md").write_text("# Spec")

        # Run archive
        archive.archive(name, type_="branch")

        # Verify removed from registry
        with open(self.cicadas_dir / "registry.json") as f:
            reg = json.load(f)
        self.assertNotIn(name, reg["branches"])

        # Verify moved to archive
        # Archive dir contains ts-name
        arch_roots = [r.name for r in (self.cicadas_dir / "archive").iterdir()]
        self.assertTrue(any(name in r for r in arch_roots))

        # Verify active dir removed
        self.assertFalse(active_dir.exists())

    def test_archive_includes_lifecycle_json(self):
        """When active contains lifecycle.json, archive moves it with the rest of active."""
        name = "init-with-lifecycle"
        with open(self.cicadas_dir / "registry.json", "r+") as f:
            reg = json.load(f)
            reg["initiatives"][name] = {"intent": "test"}
            f.seek(0)
            json.dump(reg, f)
            f.truncate()

        active_dir = self.cicadas_dir / "active" / name
        active_dir.mkdir(parents=True)
        (active_dir / "prd.md").write_text("# PRD")
        (active_dir / "lifecycle.json").write_text('{"initiative": "init-with-lifecycle", "steps": []}')

        archive.archive(name, type_="initiative")

        arch_dirs = list((self.cicadas_dir / "archive").iterdir())
        self.assertEqual(len(arch_dirs), 1)
        husk = arch_dirs[0]
        self.assertTrue((husk / "lifecycle.json").exists())
        self.assertEqual((husk / "lifecycle.json").read_text(), '{"initiative": "init-with-lifecycle", "steps": []}')

    def test_archive_significance_check(self):
        name = "fix/my-bug"
        with open(self.cicadas_dir / "registry.json", "r+") as f:
            reg = json.load(f)
            reg["branches"][name] = {"intent": "bug"}
            f.seek(0)
            json.dump(reg, f)
            f.truncate()

        # Significance check alert only prints if active dir exists
        (self.cicadas_dir / "active" / name).mkdir(parents=True)

        f = io.StringIO()
        with redirect_stdout(f):
            archive.archive(name, type_="branch")

        output = f.getvalue()
        self.assertIn("!!! LIGHTWEIGHT PATH SIGNIFICANCE CHECK !!!", output)

    def test_archive_initiative_deregisters_associated_branches(self):
        """Archiving an initiative must also remove its linked branches from the registry."""
        init_name = "my-initiative"
        with open(self.cicadas_dir / "registry.json", "r+") as f:
            reg = json.load(f)
            reg["initiatives"][init_name] = {"intent": "test initiative"}
            reg["branches"]["feat/part-1"] = {"intent": "part 1", "initiative": init_name}
            reg["branches"]["tweak/side-fix"] = {"intent": "side fix", "initiative": init_name}
            reg["branches"]["feat/other"] = {"intent": "unrelated", "initiative": "other-initiative"}
            f.seek(0)
            json.dump(reg, f)
            f.truncate()

        (self.cicadas_dir / "active" / init_name).mkdir(parents=True)

        archive.archive(init_name, type_="initiative")

        with open(self.cicadas_dir / "registry.json") as f:
            reg = json.load(f)

        # Initiative and its branches deregistered
        self.assertNotIn(init_name, reg["initiatives"])
        self.assertNotIn("feat/part-1", reg["branches"])
        self.assertNotIn("tweak/side-fix", reg["branches"])
        # Unrelated branch untouched
        self.assertIn("feat/other", reg["branches"])

    def test_status_categorization(self):
        with open(self.cicadas_dir / "registry.json", "r+") as f:
            reg = json.load(f)
            reg["branches"]["feat/f1"] = {"intent": "feat", "modules": []}
            reg["branches"]["fix/b1"] = {"intent": "bug", "modules": []}
            reg["branches"]["tweak/t1"] = {"intent": "tweak", "modules": []}
            f.seek(0)
            json.dump(reg, f)
            f.truncate()

        f = io.StringIO()
        with redirect_stdout(f):
            status.show_status()

        output = f.getvalue()
        self.assertIn("Active Feature Branches (1):", output)
        self.assertIn("Active Bugs (1):", output)
        self.assertIn("Active Tweaks (1):", output)
        self.assertIn("feat/f1", output)
        self.assertIn("fix/b1", output)
        self.assertIn("tweak/t1", output)


if __name__ == "__main__":
    unittest.main()
