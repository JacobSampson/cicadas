# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "src" / "cicadas" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from wiki_nav import (  # noqa: E402
    annotate_all_markdown,
    detect_wiki_web_base,
    discover_markdown_docs,
    ensure_wiki_metadata_comment,
    refresh_wiki_navigation,
    wiki_link_target,
)


class TestWikiNav(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.cicadas = self.test_dir / ".cicadas"
        (self.cicadas / "canon").mkdir(parents=True)
        (self.cicadas / "active" / "my-init").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_wiki_link_target_strips_md(self):
        self.assertEqual(wiki_link_target("canon/summary.md"), "canon/summary")

    def test_discover_and_refresh_writes_nav_files(self):
        (self.cicadas / "canon" / "summary.md").write_text("# Canon Summary\n\nBody.\n", encoding="utf-8")
        (self.cicadas / "active" / "my-init" / "prd.md").write_text("# PRD\n\n", encoding="utf-8")

        docs = discover_markdown_docs(self.cicadas)
        rels = {d["rel"] for d in docs}
        self.assertIn("canon/summary.md", rels)
        self.assertIn("active/my-init/prd.md", rels)

        h, s = refresh_wiki_navigation(self.cicadas)
        self.assertTrue(h)
        self.assertTrue(s)

        home = (self.cicadas / "Home.md").read_text(encoding="utf-8")
        self.assertIn("Cicadas state", home)
        self.assertIn("[Canon Summary](canon/summary)", home)
        self.assertIn("## Archive", home)

        side = (self.cicadas / "_Sidebar.md").read_text(encoding="utf-8")
        self.assertIn("[Home](Home)", side)
        self.assertIn("Canon", side)

    def test_annotate_idempotent(self):
        p = self.cicadas / "canon" / "summary.md"
        p.write_text("# T\n\n", encoding="utf-8")
        self.assertTrue(ensure_wiki_metadata_comment(self.cicadas, p))
        text = p.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("<!-- cicadas-wiki"))
        self.assertFalse(ensure_wiki_metadata_comment(self.cicadas, p))
        self.assertEqual(annotate_all_markdown(self.cicadas), 0)

    def test_skips_reserved_wiki_filenames(self):
        (self.cicadas / "Home.md").write_text("# H\n", encoding="utf-8")
        (self.cicadas / "_Sidebar.md").write_text("# S\n", encoding="utf-8")
        docs = discover_markdown_docs(self.cicadas)
        rels = {d["rel"] for d in docs}
        self.assertNotIn("Home.md", rels)
        self.assertNotIn("_Sidebar.md", rels)

    def test_title_prefers_h1_over_bogus_h2(self):
        p = self.cicadas / "canon" / "sample-prd.md"
        p.write_text(
            "---\n## next_section: 'Executive Summary'\n\n# PRD: Real Title\n\n",
            encoding="utf-8",
        )
        rec = discover_markdown_docs(self.cicadas)
        titles = {r["rel"]: r["title"] for r in rec}
        self.assertEqual(titles.get("canon/sample-prd.md"), "PRD: Real Title")

    def test_detect_wiki_web_base_from_config(self):
        (self.cicadas / "config.json").write_text(
            json.dumps({"wiki_web_base": "https://github.com/acme/foo/wiki"}),
            encoding="utf-8",
        )
        self.assertEqual(detect_wiki_web_base(self.cicadas), "https://github.com/acme/foo/wiki")

    def test_detect_wiki_web_base_from_git_remote(self):
        subprocess.run(["git", "init", "-b", "main"], cwd=self.cicadas, check=True, capture_output=True)
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/OwNnEr/My-Repo.wiki.git"],
            cwd=self.cicadas,
            check=True,
            capture_output=True,
        )
        self.assertEqual(detect_wiki_web_base(self.cicadas), "https://github.com/OwNnEr/My-Repo/wiki")

    def test_absolute_links_when_wiki_base_configured(self):
        (self.cicadas / "config.json").write_text(
            json.dumps({"wiki_web_base": "https://github.com/o/r/wiki"}),
            encoding="utf-8",
        )
        (self.cicadas / "canon" / "summary.md").write_text("# S\n", encoding="utf-8")
        refresh_wiki_navigation(self.cicadas)
        home = (self.cicadas / "Home.md").read_text(encoding="utf-8")
        self.assertIn("[S](https://github.com/o/r/wiki/canon/summary)", home)
        side = (self.cicadas / "_Sidebar.md").read_text(encoding="utf-8")
        self.assertIn("[Home](https://github.com/o/r/wiki)", side)
        self.assertIn("](https://github.com/o/r/wiki/Home#archive)", side)


if __name__ == "__main__":
    unittest.main()
