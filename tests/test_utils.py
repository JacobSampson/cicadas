# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import os
import unittest

import utils
from base import CicadasTest


class TestUtils(CicadasTest):
    def test_get_project_root(self):
        # Should find the root with .cicadas
        self.assertEqual(utils.get_project_root().resolve(), self.root.resolve())

        # Move to a subfolder, should still find root
        sub = self.root / "src" / "foo"
        sub.mkdir(parents=True)
        os.chdir(sub)
        self.assertEqual(utils.get_project_root().resolve(), self.root.resolve())

    def test_load_save_json(self):
        path = self.root / "test.json"
        data = {"foo": "bar", "baz": 123}
        utils.save_json(path, data)

        loaded = utils.load_json(path)
        self.assertEqual(loaded, data)

        # Test non-existent file
        self.assertEqual(utils.load_json(self.root / "missing.json"), {})

    def test_get_default_branch(self):
        self.init_git()
        # Default for git init is usually master or main
        # We'll check what it actually is
        import subprocess

        expected = subprocess.check_output(["git", "branch", "--show-current"], cwd=self.root).decode().strip()

        self.assertEqual(utils.get_default_branch(), expected)


if __name__ == "__main__":
    unittest.main()
