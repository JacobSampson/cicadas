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
            reg["branches"]["skill/s1"] = {"intent": "skill", "modules": []}
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
        self.assertIn("Active Skills (1):", output)
        self.assertIn("feat/f1", output)
        self.assertIn("fix/b1", output)
        self.assertIn("tweak/t1", output)
        self.assertIn("skill/s1", output)

    def test_skill_branch_not_counted_as_feature(self):
        """skill/ branches must not appear in the Active Feature Branches section."""
        with open(self.cicadas_dir / "registry.json", "r+") as f:
            reg = json.load(f)
            reg["branches"]["skill/my-tool"] = {"intent": "build tool skill", "modules": []}
            f.seek(0)
            json.dump(reg, f)
            f.truncate()

        f = io.StringIO()
        with redirect_stdout(f):
            status.show_status()

        output = f.getvalue()
        self.assertIn("Active Skills (1):", output)
        self.assertNotIn("Active Feature Branches (1):", output)

    def test_archive_skill_initiative(self):
        """Archiving a skill-prefixed initiative works correctly."""
        init_name = "skill-pdf"
        with open(self.cicadas_dir / "registry.json", "r+") as f:
            reg = json.load(f)
            reg["initiatives"][init_name] = {"intent": "pdf skill"}
            reg["branches"]["skill/pdf"] = {"intent": "pdf skill branch", "initiative": init_name}
            f.seek(0)
            json.dump(reg, f)
            f.truncate()

        (self.cicadas_dir / "active" / init_name).mkdir(parents=True)
        (self.cicadas_dir / "active" / init_name / "SKILL.md").write_text("# Skill")

        archive.archive(init_name, type_="initiative")

        with open(self.cicadas_dir / "registry.json") as f:
            reg = json.load(f)
        self.assertNotIn(init_name, reg["initiatives"])
        self.assertNotIn("skill/pdf", reg["branches"])

        arch_dirs = [d.name for d in (self.cicadas_dir / "archive").iterdir()]
        self.assertTrue(any(init_name in d for d in arch_dirs))

    def test_status_lifecycle_section_when_lifecycle_exists(self):
        """When an initiative has active lifecycle.json, status prints a Lifecycle section with Next step."""
        init_name = "with-lifecycle"
        with open(self.cicadas_dir / "registry.json", "r+") as f:
            reg = json.load(f)
            reg["initiatives"][init_name] = {"intent": "test initiative"}
            reg["branches"]["feat/part1"] = {"intent": "part 1", "initiative": init_name, "modules": []}
            f.seek(0)
            json.dump(reg, f)
            f.truncate()

        (self.cicadas_dir / "active" / init_name).mkdir(parents=True)
        (self.cicadas_dir / "active" / init_name / "lifecycle.json").write_text(
            '{"initiative": "with-lifecycle", "steps": [{"id": "complete_feature", "name": "Complete each feature"}]}'
        )

        f = io.StringIO()
        with redirect_stdout(f):
            status.show_status()

        output = f.getvalue()
        self.assertIn("Lifecycle (with-lifecycle):", output)
        self.assertIn("Next:", output)


class TestArchiveWorktree(CicadasTest):
    """Worktree teardown tests for archive.py."""

    def setUp(self):
        super().setUp()
        self.init_git()
        import subprocess
        subprocess.run(["git", "checkout", "-b", "feat/wt-branch"], cwd=self.root, check=True, capture_output=True)
        import utils
        from utils import worktree_path
        self.wt_dir = worktree_path(self.root, "feat/wt-branch")
        subprocess.run(["git", "checkout", "master"], cwd=self.root, capture_output=True)
        # Create the worktree
        utils.create_worktree(self.root, "feat/wt-branch", self.wt_dir)
        # Register in registry
        reg = utils.load_json(self.cicadas_dir / "registry.json")
        reg["branches"]["feat/wt-branch"] = {"intent": "test", "worktree_path": str(self.wt_dir)}
        utils.save_json(self.cicadas_dir / "registry.json", reg)

    def tearDown(self):
        import subprocess
        if self.wt_dir.exists():
            subprocess.run(["git", "worktree", "remove", "--force", str(self.wt_dir)], cwd=self.root, capture_output=True)
        super().tearDown()

    def test_archive_cleans_worktree(self):
        import utils
        archive.archive("feat/wt-branch", type_="branch")
        # Worktree should be removed
        self.assertFalse(self.wt_dir.exists())
        # worktree_path should be absent from registry (branch deregistered)
        reg = utils.load_json(self.cicadas_dir / "registry.json")
        self.assertNotIn("feat/wt-branch", reg["branches"])

    def test_archive_dirty_worktree_exits_without_force(self):
        import sys
        (self.wt_dir / "dirty.txt").write_text("uncommitted")
        with self.assertRaises(SystemExit) as cm:
            archive.archive("feat/wt-branch", type_="branch", force=False)
        self.assertEqual(cm.exception.code, 1)
        # Worktree should still exist
        self.assertTrue(self.wt_dir.exists())

    def test_archive_dirty_worktree_force_removes(self):
        (self.wt_dir / "dirty.txt").write_text("uncommitted")
        archive.archive("feat/wt-branch", type_="branch", force=True)
        self.assertFalse(self.wt_dir.exists())

    def test_archive_missing_worktree_dir_warns_and_continues(self):
        """If worktree dir was already deleted, archive should still proceed and clear registry."""
        import shutil, utils
        shutil.rmtree(self.wt_dir)
        # Prune the worktree from git's list
        import subprocess
        subprocess.run(["git", "worktree", "prune"], cwd=self.root, capture_output=True)
        f = io.StringIO()
        with redirect_stdout(f):
            archive.archive("feat/wt-branch", type_="branch")
        reg = utils.load_json(self.cicadas_dir / "registry.json")
        self.assertNotIn("feat/wt-branch", reg["branches"])


class TestStatusWorktrees(CicadasTest):
    """Worktrees section in status.py output."""

    def test_no_worktrees_section_when_none(self):
        """If no branches have worktree_path, the Worktrees section must not appear."""
        import utils
        reg = utils.load_json(self.cicadas_dir / "registry.json")
        reg["branches"]["feat/normal"] = {"intent": "normal", "modules": []}
        utils.save_json(self.cicadas_dir / "registry.json", reg)
        f = io.StringIO()
        with redirect_stdout(f):
            status.show_status()
        self.assertNotIn("Worktrees", f.getvalue())

    def test_worktrees_section_shows_missing(self):
        """A branch with a nonexistent worktree_path is shown as [MISSING]."""
        import utils
        reg = utils.load_json(self.cicadas_dir / "registry.json")
        reg["branches"]["feat/gone"] = {"intent": "gone", "modules": [], "worktree_path": "/nonexistent/wt/path"}
        utils.save_json(self.cicadas_dir / "registry.json", reg)
        f = io.StringIO()
        with redirect_stdout(f):
            status.show_status()
        out = f.getvalue()
        self.assertIn("Worktrees", out)
        self.assertIn("[MISSING]", out)
        self.assertIn("feat/gone", out)

    def test_worktrees_section_shows_clean(self):
        """A branch with a real clean worktree shows [clean] and HEAD."""
        self.init_git()
        import subprocess
        import utils
        subprocess.run(["git", "checkout", "-b", "feat/wt-clean"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "checkout", "master"], cwd=self.root, capture_output=True)
        wt = utils.worktree_path(self.root, "feat/wt-clean")
        utils.create_worktree(self.root, "feat/wt-clean", wt)
        reg = utils.load_json(self.cicadas_dir / "registry.json")
        reg["branches"]["feat/wt-clean"] = {"intent": "clean", "modules": [], "worktree_path": str(wt)}
        utils.save_json(self.cicadas_dir / "registry.json", reg)
        f = io.StringIO()
        with redirect_stdout(f):
            status.show_status()
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=self.root, capture_output=True)
        out = f.getvalue()
        self.assertIn("[clean]", out)
        self.assertIn("feat/wt-clean", out)


if __name__ == "__main__":
    unittest.main()
