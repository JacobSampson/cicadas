# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

# Import signalboard.py using importlib to avoid conflict with builtin 'signal' module (though renamed, it's safer)
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path

import prune
import update_index
from base import CicadasTest

SCRIPTS_DIR = Path(__file__).parent.parent / "src" / "cicadas" / "scripts"
spec = importlib.util.spec_from_file_location("cicadas_signal", SCRIPTS_DIR / "signalboard.py")
cicadas_signal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cicadas_signal)


class TestOrchestration(CicadasTest):
    def setUp(self):
        super().setUp()
        self.init_git()

    def test_update_index(self):
        update_index.update_index("feat/test", "test summary", decisions="d1", modules="m1,m2")
        with open(self.cicadas_dir / "index.json") as f:
            index = json.load(f)
        self.assertEqual(len(index["entries"]), 1)
        self.assertEqual(index["entries"][0]["branch"], "feat/test")
        self.assertEqual(index["entries"][0]["modules"], ["m1", "m2"])

    def test_prune_branch(self):
        self.init_git()
        name = "feat/to-prune"
        # Setup branch
        subprocess.run(["git", "checkout", "-b", name], cwd=self.root, check=True)
        with open(self.cicadas_dir / "registry.json", "r+") as f:
            reg = json.load(f)
            reg["branches"][name] = {"intent": "test"}
            f.seek(0)
            json.dump(reg, f)
            f.truncate()

        active_dir = self.cicadas_dir / "active" / name
        active_dir.mkdir(parents=True)
        (active_dir / "draft-spec.md").write_text("# Spec")

        # Run prune
        prune.prune(name, type_="branch")

        # Verify git branch deleted
        branches = subprocess.check_output(["git", "branch"], cwd=self.root).decode()
        self.assertNotIn(name, branches)

        # Verify restored to drafts
        self.assertTrue((self.cicadas_dir / "drafts" / name / "draft-spec.md").exists())

        # Verify removed from registry
        with open(self.cicadas_dir / "registry.json") as f:
            reg = json.load(f)
        self.assertNotIn(name, reg["branches"])

    def test_signal_basic(self):
        # Register an initiative
        init_name = "test-init"
        with open(self.cicadas_dir / "registry.json", "r+") as f:
            reg = json.load(f)
            reg["initiatives"][init_name] = {"intent": "test", "signals": []}
            f.seek(0)
            json.dump(reg, f)
            f.truncate()

        cicadas_signal.send_signal("test message", initiative=init_name)

        with open(self.cicadas_dir / "registry.json") as f:
            reg = json.load(f)
        signals = reg["initiatives"][init_name]["signals"]
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["message"], "test message")


if __name__ == "__main__":
    unittest.main()
