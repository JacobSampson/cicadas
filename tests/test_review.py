# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import io
import json
import subprocess
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import review
from base import CicadasTest


class TestParseVerdict(unittest.TestCase):
    """Unit tests for parse_verdict — no filesystem needed."""

    def test_parse_pass(self):
        text = "some text\n**Verdict: PASS**\nmore text"
        self.assertEqual(review.parse_verdict(text), "PASS")

    def test_parse_pass_with_notes(self):
        text = "**Verdict: PASS WITH NOTES**\n*Advisory findings: 2.*"
        self.assertEqual(review.parse_verdict(text), "PASS WITH NOTES")

    def test_parse_block(self):
        text = "---\n**Verdict: BLOCK**\n*Blocking findings: 1.*"
        self.assertEqual(review.parse_verdict(text), "BLOCK")

    def test_parse_none_when_absent(self):
        self.assertIsNone(review.parse_verdict("No verdict here."))

    def test_parse_none_on_empty(self):
        self.assertIsNone(review.parse_verdict(""))

    def test_pass_with_notes_not_confused_with_pass(self):
        """PASS WITH NOTES must not match as plain PASS."""
        text = "**Verdict: PASS WITH NOTES**"
        self.assertEqual(review.parse_verdict(text), "PASS WITH NOTES")


class TestCheckReview(CicadasTest):
    def _write_registry(self, initiative: str, branch: str) -> None:
        reg = {
            "schema_version": "2.0",
            "initiatives": {initiative: {"intent": "test"}},
            "branches": {branch: {"intent": "test", "modules": [], "initiative": initiative}},
        }
        (self.cicadas_dir / "registry.json").write_text(json.dumps(reg))

    def _write_review(self, initiative: str, verdict: str, advisory: int = 0, blocking: int = 0) -> Path:
        active_dir = self.cicadas_dir / "active" / initiative
        active_dir.mkdir(parents=True, exist_ok=True)
        content = (
            f"## Code Review: tweak/{initiative}\n\n"
            f"### ✅ Verified\n\n- All checks passed.\n\n---\n\n"
            f"**Verdict: {verdict}**\n"
            f"*Blocking findings: {blocking}. Advisory findings: {advisory}.*\n"
        )
        path = active_dir / "review.md"
        path.write_text(content)
        return path

    def test_no_git_returns_2(self):
        """Without a git repo, check_review returns 2."""
        code = review.check_review()
        self.assertEqual(code, 2)

    def test_no_review_md_returns_2(self):
        """With a registered branch but no review.md, returns 2."""
        self.init_git()
        subprocess.run(["git", "checkout", "-b", "tweak/myfix"], cwd=self.root, check=True, capture_output=True)
        self._write_registry("myfix", "tweak/myfix")
        (self.cicadas_dir / "active" / "myfix").mkdir(parents=True, exist_ok=True)

        f = io.StringIO()
        with redirect_stdout(f):
            code = review.check_review()
        self.assertEqual(code, 2)
        self.assertIn("No review.md found", f.getvalue())

    def test_pass_verdict_returns_0(self):
        self.init_git()
        subprocess.run(["git", "checkout", "-b", "tweak/myfix"], cwd=self.root, check=True, capture_output=True)
        self._write_registry("myfix", "tweak/myfix")
        self._write_review("myfix", "PASS")

        f = io.StringIO()
        with redirect_stdout(f):
            code = review.check_review()
        self.assertEqual(code, 0)
        self.assertIn("PASS", f.getvalue())

    def test_pass_with_notes_returns_0(self):
        self.init_git()
        subprocess.run(["git", "checkout", "-b", "tweak/myfix"], cwd=self.root, check=True, capture_output=True)
        self._write_registry("myfix", "tweak/myfix")
        self._write_review("myfix", "PASS WITH NOTES", advisory=2)

        f = io.StringIO()
        with redirect_stdout(f):
            code = review.check_review()
        self.assertEqual(code, 0)
        self.assertIn("PASS WITH NOTES", f.getvalue())

    def test_block_verdict_returns_1(self):
        self.init_git()
        subprocess.run(["git", "checkout", "-b", "tweak/myfix"], cwd=self.root, check=True, capture_output=True)
        self._write_registry("myfix", "tweak/myfix")
        self._write_review("myfix", "BLOCK", blocking=1)

        f = io.StringIO()
        with redirect_stdout(f):
            code = review.check_review()
        self.assertEqual(code, 1)
        self.assertIn("BLOCK", f.getvalue())

    def test_explicit_initiative_bypasses_branch_detection(self):
        """Passing --initiative directly works even without a registered branch."""
        self._write_review("direct-init", "PASS")

        f = io.StringIO()
        with redirect_stdout(f):
            code = review.check_review(initiative="direct-init")
        self.assertEqual(code, 0)

    def test_unregistered_branch_returns_2(self):
        self.init_git()
        subprocess.run(["git", "checkout", "-b", "tweak/unknown"], cwd=self.root, check=True, capture_output=True)
        # registry has no entry for this branch
        f = io.StringIO()
        with redirect_stdout(f):
            code = review.check_review()
        self.assertEqual(code, 2)
        self.assertIn("not registered", f.getvalue())


if __name__ == "__main__":
    unittest.main()
