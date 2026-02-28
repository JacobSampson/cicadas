# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import subprocess
import unittest

import check
from base import CicadasTest


class TestCheck(CicadasTest):
    def test_check_not_registered(self):
        # Current branch unknown/not registered
        check.check_conflicts()
        # Should just print info

    def test_check_conflicts_and_signals(self):
        self.init_git()
        name = "feat/test"
        subprocess.run(["git", "checkout", "-b", name], cwd=self.root, check=True)

        # Register branch with modules
        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        registry["branches"][name] = {"modules": ["mod1"], "initiative": "init1"}
        # Register overlapping branch
        registry["branches"]["feat/other"] = {"modules": ["mod1"]}
        # Register initiative with signal
        registry["initiatives"]["init1"] = {"signals": [{"timestamp": "2026-01-01", "from_branch": "other", "message": "hello"}]}
        with open(self.cicadas_dir / "registry.json", "w") as f:
            json.dump(registry, f)

        check.check_conflicts()
        # Should print conflict warning and signal

    def test_check_git_log(self):
        self.init_git()
        # Create a new commit on master to trigger the log check
        (self.root / "new.txt").write_text("new")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "new commit"], cwd=self.root, check=True)

        # Checkout a feature branch from an OLDER commit
        subprocess.run(["git", "checkout", "HEAD~1", "-b", "feat/old"], cwd=self.root, check=True, stderr=subprocess.PIPE)

        # Register it
        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        registry["branches"]["feat/old"] = {"modules": []}
        with open(self.cicadas_dir / "registry.json", "w") as f:
            json.dump(registry, f)

        check.check_conflicts()
        # Should print new commits message


if __name__ == "__main__":
    unittest.main()
