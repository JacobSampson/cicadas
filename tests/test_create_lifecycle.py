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

    def test_create_lifecycle_in_active(self):
        (self.cicadas_dir / "active" / "active-init").mkdir(parents=True)
        create_lifecycle.create_lifecycle("active-init", dest="active")

        path = self.cicadas_dir / "active" / "active-init" / "lifecycle.json"
        self.assertTrue(path.exists())
        data = json.loads(path.read_text())
        self.assertEqual(data["initiative"], "active-init")


if __name__ == "__main__":
    unittest.main()
