# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import unittest

import synthesize
from base import CicadasTest


class TestSynthesize(CicadasTest):
    def setUp(self):
        super().setUp()
        # Initialize git so get_project_root() works without mocks
        self.init_git()
        # Note: synthesize.py uses Path(__file__) to find templates,
        # which will resolve to the actual src directory.
        # This is fine for "real" tests as long as the templates exist.

    def test_gather_context_basic(self):
        # Create a branch and some files
        name = "feat/test"
        (self.cicadas_dir / "active" / name).mkdir(parents=True)
        (self.cicadas_dir / "active" / name / "prd.md").write_text("Active PRD")

        # Add to registry
        with open(self.cicadas_dir / "registry.json") as f:
            registry = json.load(f)
        registry["branches"][name] = {"modules": ["my_mod"]}
        with open(self.cicadas_dir / "registry.json", "w") as f:
            json.dump(registry, f)

        # Create code file
        # synthesize.py looks in src/mod/ or mod/
        mod_dir = self.root / "src" / "my_mod"
        mod_dir.mkdir(parents=True)
        (mod_dir / "logic.py").write_text("print('hello')")

        # Create canon
        (self.cicadas_dir / "canon/modules").mkdir(parents=True, exist_ok=True)
        (self.cicadas_dir / "canon/overview.md").write_text("Canon Overview")

        # We need to ensure we are in the root so get_project_root works
        context = synthesize.gather_context(name)

        self.assertIn("prd.md", context["active_docs"])
        self.assertEqual(context["active_docs"]["prd.md"], "Active PRD")
        self.assertIn("src/my_mod/logic.py", context["code_context"])
        self.assertIn("overview.md", context["canon_docs"])

    def test_generate_prompt(self):
        context = {
            "canon_docs": {"overview.md": "Canon"},
            "active_docs": {"prd.md": "Active"},
            "code_context": {"src/main.py": "print(1)"},
            "index": {"entries": []},
        }
        prompt = synthesize.generate_prompt(context)
        # Check for real template content identifiers instead of mocked one
        self.assertIn("### Step 1: Determine Mode", prompt)
        self.assertIn("Canon", prompt)
        self.assertIn("Active", prompt)
        self.assertIn("print(1)", prompt)

    def test_apply_response(self):
        # Create a temp response file
        response = """
File: canon/new_doc.md
```markdown
Updated content
```
"""
        response_file = self.root / "response.txt"
        response_file.write_text(response)

        synthesize.apply_response(response)  # Can call directly with text

        target = self.cicadas_dir / "canon/new_doc.md"
        self.assertTrue(target.exists())
        self.assertEqual(target.read_text().strip(), "Updated content")


if __name__ == "__main__":
    unittest.main()
