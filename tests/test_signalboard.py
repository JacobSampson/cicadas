# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import runpy
import subprocess
import sys
import unittest
from unittest.mock import patch

import signalboard as signal_mod
from base import CicadasTest


class TestSignal(CicadasTest):
    def test_send_signal_no_initiative_unregistered_branch(self):
        self.init_git()
        # On master branch which is not registered for signal broadcasting
        signal_mod.send_signal("test message", initiative=None)
        # Should print error

    def test_send_signal_auto_detect_success(self):
        self.init_git()
        name = "feat/test"
        subprocess.run(["git", "checkout", "-b", name], cwd=self.root, check=True)

        # Register branch and initiative
        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        registry["branches"][name] = {"initiative": "init1"}
        registry["initiatives"]["init1"] = {"signals": []}
        with open(self.cicadas_dir / "registry.json", "w") as f:
            json.dump(registry, f)

        signal_mod.send_signal("auto detected signal")

        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        self.assertEqual(len(registry["initiatives"]["init1"]["signals"]), 1)

    def test_signal_cli(self):
        self.init_git()
        # Setup registry
        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        registry["initiatives"]["init-cli"] = {"signals": []}
        with open(self.cicadas_dir / "registry.json", "w") as f:
            json.dump(registry, f)

        test_args = ["signalboard.py", "cli signal", "--initiative", "init-cli"]
        with patch.object(sys, "argv", test_args):
            runpy.run_module("signalboard", run_name="__main__")

        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        self.assertEqual(registry["initiatives"]["init-cli"]["signals"][0]["message"], "cli signal")


if __name__ == "__main__":
    unittest.main()
