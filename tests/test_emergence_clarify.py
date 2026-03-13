# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

"""Regression guard: Clarify subagent must document Intake and file paths (loom.md, requirements.md)."""

import unittest
from pathlib import Path


def _clarify_md_path() -> Path:
    """Path to emergence/clarify.md from repo root (parent of tests/)."""
    root = Path(__file__).resolve().parent.parent
    return root / "src" / "cicadas" / "emergence" / "clarify.md"


class TestEmergenceClarifyIntake(unittest.TestCase):
    def test_clarify_documents_intake_step(self):
        path = _clarify_md_path()
        self.assertTrue(path.exists(), f"clarify.md not found at {path}")
        content = path.read_text()
        self.assertIn("Intake", content, "clarify.md must document the Intake step (Q/D/L choice)")

    def test_clarify_documents_loom_md_path(self):
        path = _clarify_md_path()
        content = path.read_text()
        self.assertIn("loom.md", content, "clarify.md must document drafts/{initiative}/loom.md for Loom transcript")

    def test_clarify_documents_requirements_md_path(self):
        path = _clarify_md_path()
        content = path.read_text()
        self.assertIn("requirements.md", content, "clarify.md must document requirements.md for Doc intake")
