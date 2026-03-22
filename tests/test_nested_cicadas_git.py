# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from utils import is_cicadas_nested_git_repo, record_nested_cicadas_changes, skip_nested_cicadas_git_commit


class TestNestedCicadasGit(unittest.TestCase):
    def test_is_nested_false_without_git(self):
        d = Path(tempfile.mkdtemp())
        try:
            cicadas = d / ".cicadas"
            cicadas.mkdir()
            self.assertFalse(is_cicadas_nested_git_repo(cicadas))
        finally:
            shutil.rmtree(d)

    def test_is_nested_true_with_git_dir(self):
        d = Path(tempfile.mkdtemp())
        try:
            cicadas = d / ".cicadas"
            cicadas.mkdir()
            subprocess.run(["git", "init", "-b", "main"], cwd=cicadas, check=True, capture_output=True)
            self.assertTrue(is_cicadas_nested_git_repo(cicadas))
        finally:
            shutil.rmtree(d)

    def test_record_nested_creates_commit_and_stages_parent(self):
        root = Path(tempfile.mkdtemp())
        try:
            cicadas = root / ".cicadas"
            cicadas.mkdir(parents=True)
            (cicadas / "registry.json").write_text("{}")

            subprocess.run(["git", "init", "-b", "main"], cwd=cicadas, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "nested@test"], cwd=cicadas, check=True)
            subprocess.run(["git", "config", "user.name", "Nested"], cwd=cicadas, check=True)
            subprocess.run(["git", "add", "registry.json"], cwd=cicadas, check=True)
            subprocess.run(["git", "commit", "-m", "init nested"], cwd=cicadas, check=True)

            subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "root@test"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Root"], cwd=root, check=True)
            (root / "README.md").write_text("p")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "init root"], cwd=root, check=True)

            reg = {"initiatives": {}, "branches": {"feat/x": {"intent": "t"}}}
            (cicadas / "registry.json").write_text(json.dumps(reg))

            os.environ.pop("CICADAS_SKIP_NESTED_GIT_COMMIT", None)
            did = record_nested_cicadas_changes(root, cicadas, ["registry.json"], "cicadas: test branch")
            self.assertTrue(did)

            log = subprocess.check_output(["git", "-C", str(cicadas), "log", "-1", "--format=%s"], text=True).strip()
            self.assertEqual(log, "cicadas: test branch")

            st = subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True)
            self.assertIn(".cicadas", st)
        finally:
            shutil.rmtree(root)

    def test_skip_env_disables_commit(self):
        root = Path(tempfile.mkdtemp())
        try:
            cicadas = root / ".cicadas"
            cicadas.mkdir(parents=True)
            (cicadas / "registry.json").write_text("{}")
            subprocess.run(["git", "init", "-b", "main"], cwd=cicadas, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "nested@test"], cwd=cicadas, check=True)
            subprocess.run(["git", "config", "user.name", "Nested"], cwd=cicadas, check=True)
            subprocess.run(["git", "add", "registry.json"], cwd=cicadas, check=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=cicadas, check=True)

            (cicadas / "registry.json").write_text('{"a": 1}')
            os.environ["CICADAS_SKIP_NESTED_GIT_COMMIT"] = "1"
            try:
                self.assertTrue(skip_nested_cicadas_git_commit())
                did = record_nested_cicadas_changes(root, cicadas, ["registry.json"], "should not run")
                self.assertFalse(did)
                log = subprocess.check_output(["git", "-C", str(cicadas), "log", "-1", "--format=%s"], text=True).strip()
                self.assertEqual(log, "init")
            finally:
                os.environ.pop("CICADAS_SKIP_NESTED_GIT_COMMIT", None)
        finally:
            shutil.rmtree(root)


if __name__ == "__main__":
    unittest.main()
