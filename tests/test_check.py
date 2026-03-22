# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import subprocess
import unittest

import check
import utils
from base import CicadasTest


class TestCheck(CicadasTest):
    def test_check_not_registered(self):
        check.check_conflicts()  # Should not raise

    def test_check_conflicts_and_signals(self):
        self.init_git()
        name = "feat/test"
        subprocess.run(["git", "checkout", "-b", name], cwd=self.root, check=True)

        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        registry["branches"][name] = {"modules": ["mod1"], "initiative": "init1"}
        registry["branches"]["feat/other"] = {"modules": ["mod1"]}
        registry["initiatives"]["init1"] = {"signals": [{"timestamp": "2026-01-01", "from_branch": "other", "message": "hello"}]}
        with open(self.cicadas_dir / "registry.json", "w") as f:
            json.dump(registry, f)

        check.check_conflicts()  # Should print conflict + signal without raising

    def test_check_git_log(self):
        self.init_git()
        (self.root / "new.txt").write_text("new")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "new commit"], cwd=self.root, check=True)
        subprocess.run(["git", "checkout", "HEAD~1", "-b", "feat/old"], cwd=self.root, check=True, stderr=subprocess.PIPE)

        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        registry["branches"]["feat/old"] = {"modules": []}
        with open(self.cicadas_dir / "registry.json", "w") as f:
            json.dump(registry, f)

        check.check_conflicts()  # Should print new commits message


class TestCheckInitiativeScoped(CicadasTest):
    """Tests for the new initiative-scoped pre-execution mode."""

    def _setup_initiative(self, branches: dict) -> None:
        """Register an initiative and branches in the registry."""
        reg = utils.load_json(self.cicadas_dir / "registry.json")
        reg["initiatives"]["my-init"] = {"intent": "test", "signals": []}
        for name, info in branches.items():
            reg["branches"][name] = {**info, "initiative": "my-init"}
        utils.save_json(self.cicadas_dir / "registry.json", reg)

    def test_no_conflict_returns_false(self):
        self._setup_initiative({
            "feat/a": {"modules": ["src/api"], "intent": "a"},
            "feat/b": {"modules": ["src/ui"], "intent": "b"},
        })
        result = check.check_conflicts(initiative_name="my-init")
        self.assertFalse(result)

    def test_conflict_returns_true(self):
        self._setup_initiative({
            "feat/a": {"modules": ["src/shared"], "intent": "a"},
            "feat/b": {"modules": ["src/shared"], "intent": "b"},
        })
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            result = check.check_conflicts(initiative_name="my-init")
        self.assertTrue(result)
        self.assertIn("[WARN]", buf.getvalue())
        self.assertIn("src/shared", buf.getvalue())

    def test_empty_initiative_no_conflict(self):
        reg = utils.load_json(self.cicadas_dir / "registry.json")
        reg["initiatives"]["empty-init"] = {"intent": "empty", "signals": []}
        utils.save_json(self.cicadas_dir / "registry.json", reg)
        result = check.check_conflicts(initiative_name="empty-init")
        self.assertFalse(result)


class TestCheckStaleWorktree(CicadasTest):
    """Stale-worktree detection — path recorded but directory gone."""

    def test_stale_worktree_flagged(self):
        reg = utils.load_json(self.cicadas_dir / "registry.json")
        reg["branches"]["feat/gone"] = {
            "modules": [],
            "intent": "gone",
            "worktree_path": "/nonexistent/path/that/does/not/exist",
        }
        utils.save_json(self.cicadas_dir / "registry.json", reg)

        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            check.check_conflicts()
        self.assertIn("[WARN]", buf.getvalue())
        self.assertIn("Stale worktree", buf.getvalue())

    def test_no_stale_worktree_when_path_absent(self):
        """Registry branch without worktree_path should not trigger stale warning."""
        reg = utils.load_json(self.cicadas_dir / "registry.json")
        reg["branches"]["feat/normal"] = {"modules": [], "intent": "normal"}
        utils.save_json(self.cicadas_dir / "registry.json", reg)

        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            check.check_conflicts()
        self.assertNotIn("Stale worktree", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
