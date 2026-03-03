# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import unittest

import kickoff
from base import CicadasTest


class TestKickoff(CicadasTest):
    def test_kickoff_basic(self):
        # Setup draft
        name = "test-init"
        draft_dir = self.cicadas_dir / "drafts" / name
        draft_dir.mkdir(parents=True)
        (draft_dir / "prd.md").write_text("# Test PRD")

        # Initialize git for kickoff to work
        self.init_git()

        # Run kickoff
        kickoff.kickoff(name, "test intent")

        # Verify active spec
        active_spec = self.cicadas_dir / "active" / name / "prd.md"
        self.assertTrue(active_spec.exists())
        self.assertEqual(active_spec.read_text(), "# Test PRD")

        # Verify drafts removed
        self.assertFalse(draft_dir.exists())

        # Verify registry
        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        self.assertIn(name, registry["initiatives"])
        self.assertEqual(registry["initiatives"][name]["intent"], "test intent")

        # Verify git branch
        import subprocess

        branches = subprocess.check_output(["git", "branch"], cwd=self.root).decode()
        self.assertIn(f"initiative/{name}", branches)

    def test_kickoff_no_drafts(self):
        self.init_git()
        name = "empty-init"
        kickoff.kickoff(name, "no drafts")

        active_dir = self.cicadas_dir / "active" / name
        self.assertTrue(active_dir.exists())

        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        self.assertIn(name, registry["initiatives"])
        self.assertEqual(registry["initiatives"][name]["signals"], [])

    def test_kickoff_promotes_lifecycle_json(self):
        """When drafts contain lifecycle.json, kickoff promotes it to active."""
        name = "with-lifecycle"
        draft_dir = self.cicadas_dir / "drafts" / name
        draft_dir.mkdir(parents=True)
        (draft_dir / "prd.md").write_text("# Test PRD")
        lifecycle_content = '{"initiative": "with-lifecycle", "pr_boundaries": {"specs": false}, "steps": []}'
        (draft_dir / "lifecycle.json").write_text(lifecycle_content)

        self.init_git()
        kickoff.kickoff(name, "test intent")

        active_lifecycle = self.cicadas_dir / "active" / name / "lifecycle.json"
        self.assertTrue(active_lifecycle.exists())
        self.assertEqual(active_lifecycle.read_text(), lifecycle_content)
        self.assertFalse(draft_dir.exists())

    def test_kickoff_existing(self):
        self.init_git()
        name = "exists"
        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        registry["initiatives"][name] = {"intent": "old"}
        with open(self.cicadas_dir / "registry.json", "w") as f:
            json.dump(registry, f)

        # Should just print that it already exists
        kickoff.kickoff(name, "new")

        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        self.assertEqual(registry["initiatives"][name]["intent"], "old")


if __name__ == "__main__":
    unittest.main()
