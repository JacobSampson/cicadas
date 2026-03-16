# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import unittest

import create_lifecycle
from base import CicadasTest


class TestCreateLifecycle(CicadasTest):
    def test_create_lifecycle_in_drafts_defaults(self):
        create_lifecycle.create_lifecycle("my-init", dest="drafts")

        path = self.cicadas_dir / "drafts" / "my-init" / "lifecycle.json"
        self.assertTrue(path.exists())
        data = json.loads(path.read_text())
        self.assertEqual(data["initiative"], "my-init")
        self.assertFalse(data["pr_boundaries"]["specs"])
        self.assertTrue(data["pr_boundaries"]["initiatives"])
        self.assertTrue(data["pr_boundaries"]["features"])
        self.assertFalse(data["pr_boundaries"]["tasks"])
        self.assertIsInstance(data["steps"], list)
        self.assertGreater(len(data["steps"]), 0)

    def test_create_lifecycle_overrides(self):
        create_lifecycle.create_lifecycle(
            "other",
            dest="drafts",
            pr_specs=True,
            pr_initiatives=False,
            pr_features=False,
            pr_tasks=True,
        )

        path = self.cicadas_dir / "drafts" / "other" / "lifecycle.json"
        data = json.loads(path.read_text())
        self.assertTrue(data["pr_boundaries"]["specs"])
        self.assertFalse(data["pr_boundaries"]["initiatives"])
        self.assertFalse(data["pr_boundaries"]["features"])
        self.assertTrue(data["pr_boundaries"]["tasks"])

    def test_create_lifecycle_overwrites_existing(self):
        """Calling create_lifecycle twice should overwrite — not corrupt — the file."""
        create_lifecycle.create_lifecycle("my-init", dest="drafts")
        create_lifecycle.create_lifecycle("my-init", dest="drafts", pr_specs=True)

        path = self.cicadas_dir / "drafts" / "my-init" / "lifecycle.json"
        data = json.loads(path.read_text())
        self.assertTrue(data["pr_boundaries"]["specs"])

    def test_create_lifecycle_step_ids_present(self):
        """Steps array must contain at least complete_feature and complete_initiative IDs."""
        create_lifecycle.create_lifecycle("my-init", dest="drafts")
        path = self.cicadas_dir / "drafts" / "my-init" / "lifecycle.json"
        data = json.loads(path.read_text())
        step_ids = [s.get("id") for s in data["steps"]]
        self.assertIn("complete_feature", step_ids)
        self.assertIn("complete_initiative", step_ids)

    def test_create_lifecycle_creates_parent_dir_if_missing(self):
        """create_lifecycle should create the initiative directory if it doesn't exist."""
        path = self.cicadas_dir / "drafts" / "brand-new" / "lifecycle.json"
        self.assertFalse(path.exists())
        create_lifecycle.create_lifecycle("brand-new", dest="drafts")
        self.assertTrue(path.exists())

    def test_create_lifecycle_in_active(self):
        (self.cicadas_dir / "active" / "active-init").mkdir(parents=True)
        create_lifecycle.create_lifecycle("active-init", dest="active")

        path = self.cicadas_dir / "active" / "active-init" / "lifecycle.json"
        self.assertTrue(path.exists())
        data = json.loads(path.read_text())
        self.assertEqual(data["initiative"], "active-init")


if __name__ == "__main__":
    unittest.main()
