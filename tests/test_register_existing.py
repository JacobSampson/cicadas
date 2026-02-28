# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import unittest

import register_existing
from base import CicadasTest


class TestRegisterExisting(CicadasTest):
    def test_register_basic(self):
        branch = "feat/existing"
        intent = "existing intent"

        register_existing.register_existing(self.root, branch, intent)

        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)

        self.assertIn(branch, registry["branches"])
        self.assertEqual(registry["branches"][branch]["intent"], intent)
        self.assertEqual(registry["branches"][branch]["modules"], [])

    def test_register_with_initiative_and_modules(self):
        # First register an initiative
        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        registry["initiatives"]["test-init"] = {"intent": "test", "created_at": "...", "signals": []}
        with open(self.cicadas_dir / "registry.json", "w") as f:
            json.dump(registry, f)

        branch = "feat/complex"
        intent = "complex intent"
        initiative = "test-init"
        modules = "mod1, mod2"

        register_existing.register_existing(self.root, branch, intent, initiative, modules)

        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)

        self.assertIn(branch, registry["branches"])
        self.assertEqual(registry["branches"][branch]["initiative"], initiative)
        self.assertEqual(set(registry["branches"][branch]["modules"]), {"mod1", "mod2"})

    def test_register_duplicate(self):
        branch = "feat/dup"
        register_existing.register_existing(self.root, branch, "intent 1")

        # Should not error, just print message (according to code)
        register_existing.register_existing(self.root, branch, "intent 2")

        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        self.assertEqual(registry["branches"][branch]["intent"], "intent 1")

    def test_register_invalid_initiative(self):
        # Warning only
        register_existing.register_existing(self.root, "feat/bad-init", "intent", initiative="non-existent")

        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        self.assertIn("feat/bad-init", registry["branches"])
        self.assertNotIn("initiative", registry["branches"]["feat/bad-init"])

    def test_register_registry_missing(self):
        (self.cicadas_dir / "registry.json").unlink()
        with self.assertRaises(SystemExit) as cm:
            register_existing.register_existing(self.root, "feat/no-reg", "intent")
        self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
