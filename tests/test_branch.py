# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import subprocess
import unittest

import branch
from base import CicadasTest


class TestBranch(CicadasTest):
    def setUp(self):
        super().setUp()
        self.init_git()
        # Mocking and real git operations are mixed here.
        # utils.get_default_branch() will return 'master' or 'main' depending on git init.
        from utils import get_default_branch

        self.default_branch = get_default_branch()

    def test_create_feature_branch(self):
        # Register an initiative first
        init_name = "test-init"
        with open(self.cicadas_dir / "registry.json", "r+") as f:
            reg = json.load(f)
            reg["initiatives"][init_name] = {"intent": "test"}
            f.seek(0)
            json.dump(reg, f)
            f.truncate()

        branch_name = "feat/my-feature"
        branch.create_branch(branch_name, "feat intent", "src/foo.py", initiative=init_name)

        # Verify git branch
        curr = subprocess.check_output(["git", "branch", "--show-current"], cwd=self.root).decode().strip()
        self.assertEqual(curr, branch_name)

        # Verify registry
        with open(self.cicadas_dir / "registry.json") as f:
            reg = json.load(f)
        self.assertIn(branch_name, reg["branches"])
        self.assertEqual(reg["branches"][branch_name]["initiative"], init_name)

    def test_create_fix_branch_from_root(self):
        branch_name = "fix/my-bug"
        branch.create_branch(branch_name, "bug intent", "src/bar.py")

        # Should branch from master/main
        curr = subprocess.check_output(["git", "branch", "--show-current"], cwd=self.root).decode().strip()
        self.assertEqual(curr, branch_name)

        # Verify parent was master/main
        branch_hash = subprocess.check_output(["git", "rev-parse", branch_name], cwd=self.root).decode().strip()
        default_hash = subprocess.check_output(["git", "rev-parse", self.default_branch], cwd=self.root).decode().strip()
        self.assertEqual(branch_hash, default_hash)

    def test_tweak_branch_active_dir_uses_initiative_name(self):
        """Active dir for a tweak branch should be active/{initiative}, not active/tweak/{name}."""
        init_name = "my-tweak"
        with open(self.cicadas_dir / "registry.json", "r+") as f:
            reg = json.load(f)
            reg["initiatives"][init_name] = {"intent": "test tweak"}
            f.seek(0)
            json.dump(reg, f)
            f.truncate()

        branch.create_branch("tweak/my-tweak", "tweak intent", "", initiative=init_name)

        # Active dir must be active/my-tweak, NOT active/tweak/my-tweak
        self.assertTrue((self.cicadas_dir / "active" / init_name).exists())
        self.assertFalse((self.cicadas_dir / "active" / "tweak").exists())

    def test_fix_branch_active_dir_uses_initiative_name(self):
        """Active dir for a fix branch should be active/{initiative}, not active/fix/{name}."""
        init_name = "my-fix"
        with open(self.cicadas_dir / "registry.json", "r+") as f:
            reg = json.load(f)
            reg["initiatives"][init_name] = {"intent": "test fix"}
            f.seek(0)
            json.dump(reg, f)
            f.truncate()

        branch.create_branch("fix/my-fix", "fix intent", "", initiative=init_name)

        self.assertTrue((self.cicadas_dir / "active" / init_name).exists())
        self.assertFalse((self.cicadas_dir / "active" / "fix").exists())

    def test_conflict_detection(self):
        # Register existing branch with same module
        with open(self.cicadas_dir / "registry.json", "r+") as f:
            reg = json.load(f)
            reg["branches"]["feat/old"] = {"modules": ["src/shared.py"], "intent": "old"}
            f.seek(0)
            json.dump(reg, f)
            f.truncate()

        # Capture output
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            branch.create_branch("feat/new", "new intent", "src/shared.py")

        output = f.getvalue()
        self.assertIn("WARNING: Module overlaps detected", output)
        self.assertIn("feat/old", output)


if __name__ == "__main__":
    unittest.main()
