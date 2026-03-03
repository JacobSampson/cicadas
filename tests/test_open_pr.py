# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import io
import unittest
from contextlib import redirect_stdout

import open_pr
from base import CicadasTest


class TestOpenPr(CicadasTest):
    def test_open_pr_not_git_prints_message(self):
        """Without git repo, open_pr prints message and returns 1."""
        f = io.StringIO()
        with redirect_stdout(f):
            code = open_pr.open_pr(base_branch="main")
        self.assertEqual(code, 1)
        self.assertIn("Not a git repository", f.getvalue())

    def test_bitbucket_pr_url_parsing(self):
        """_bitbucket_pr_url builds URL from HTTPS and SSH remote formats."""
        url = open_pr._bitbucket_pr_url("https://bitbucket.org/ws/proj", "feat/foo", "main")
        self.assertEqual(url, "https://bitbucket.org/ws/proj/pull-requests/new?source=feat/foo&dest=main")
        url = open_pr._bitbucket_pr_url("git@bitbucket.org:ws/proj.git", "feat/bar", "master")
        self.assertEqual(url, "https://bitbucket.org/ws/proj/pull-requests/new?source=feat/bar&dest=master")

    def test_bitbucket_pr_url_non_bitbucket_returns_none(self):
        """_bitbucket_pr_url returns None for non-Bitbucket remotes."""
        self.assertIsNone(open_pr._bitbucket_pr_url("https://github.com/u/r", "feat/x", "main"))
        self.assertIsNone(open_pr._bitbucket_pr_url("", "feat/x", "main"))


if __name__ == "__main__":
    unittest.main()
