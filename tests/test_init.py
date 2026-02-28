# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import unittest

import init
from base import CicadasTest
from utils import load_json


class TestInit(CicadasTest):
    def test_init_cicadas(self):
        # CicadasTest.setUp already creates some of this, but let's test the script's logic
        # We'll use a fresh sub-directory for this specific test
        new_root = self.root / "new_project"
        new_root.mkdir()

        init.init_cicadas(new_root)

        cicadas_dir = new_root / ".cicadas"
        self.assertTrue(cicadas_dir.exists())
        self.assertTrue((cicadas_dir / "canon/modules").exists())
        self.assertTrue((cicadas_dir / "active").exists())
        self.assertTrue((cicadas_dir / "drafts").exists())
        self.assertTrue((cicadas_dir / "archive").exists())

        registry = load_json(cicadas_dir / "registry.json")
        self.assertEqual(registry["schema_version"], "2.0")

        index = load_json(cicadas_dir / "index.json")
        self.assertEqual(index["schema_version"], "2.0")

        config = load_json(cicadas_dir / "config.json")
        self.assertEqual(config["project_name"], "new_project")


if __name__ == "__main__":
    unittest.main()
