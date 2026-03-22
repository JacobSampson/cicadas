# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import unittest
from pathlib import Path

import validate_skill
from base import CicadasTest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_skill_dir(cicadas: Path, slug: str, subdir: str = "active") -> Path:
    """Create .cicadas/{subdir}/skill-{slug}/ and return the path."""
    d = cicadas / subdir / f"skill-{slug}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_skill_md(skill_dir: Path, *, name: str, description: str = "A valid description.") -> None:
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# Body\n"
    )


# ---------------------------------------------------------------------------
# Spike / regex correctness
# ---------------------------------------------------------------------------

class TestFrontmatterParsing(unittest.TestCase):
    """Task 1: validate multi-line YAML description handling."""

    def _parse(self, text: str) -> dict | None:
        return validate_skill._extract_frontmatter(text)

    def test_single_line_description(self):
        text = "---\nname: my-skill\ndescription: A short description.\n---\n\n# Body\n"
        fields = self._parse(text)
        self.assertIsNotNone(fields)
        self.assertEqual(fields["description"], "A short description.")

    def test_folded_scalar_description(self):
        """YAML folded scalar (>) should be captured and joined."""
        text = (
            "---\n"
            "name: my-skill\n"
            "description: >\n"
            "  This is a longer description that\n"
            "  spans multiple lines for readability.\n"
            "---\n\n# Body\n"
        )
        fields = self._parse(text)
        self.assertIsNotNone(fields)
        desc = fields.get("description", "")
        self.assertIn("longer description", desc)
        self.assertIn("readability", desc)

    def test_block_scalar_description(self):
        """YAML block scalar (|) should be captured."""
        text = (
            "---\n"
            "name: my-skill\n"
            "description: |\n"
            "  First line.\n"
            "  Second line.\n"
            "---\n\n# Body\n"
        )
        fields = self._parse(text)
        self.assertIsNotNone(fields)
        desc = fields.get("description", "")
        self.assertIn("First line", desc)
        self.assertIn("Second line", desc)

    def test_quoted_description(self):
        text = '---\nname: my-skill\ndescription: "Use when the user asks about X."\n---\n\n'
        fields = self._parse(text)
        self.assertEqual(fields["description"], "Use when the user asks about X.")

    def test_no_frontmatter_returns_none(self):
        text = "# Just markdown\nNo frontmatter here.\n"
        self.assertIsNone(self._parse(text))

    def test_missing_closing_delimiter_returns_none(self):
        text = "---\nname: my-skill\ndescription: desc\n"
        self.assertIsNone(self._parse(text))


# ---------------------------------------------------------------------------
# Error cases (one per [ERR] output type)
# ---------------------------------------------------------------------------

class TestValidateSkillErrors(CicadasTest):

    def _errors(self, slug: str) -> list[str]:
        return validate_skill.validate(slug, cicadas_dir=self.cicadas_dir)

    def test_missing_skill_md(self):
        _make_skill_dir(self.cicadas_dir, "no-md")
        errors = self._errors("no-md")
        self.assertTrue(any("SKILL.md not found" in e for e in errors))

    def test_missing_frontmatter(self):
        d = _make_skill_dir(self.cicadas_dir, "no-front")
        (d / "SKILL.md").write_text("# No frontmatter here\n")
        errors = self._errors("no-front")
        self.assertTrue(any("frontmatter" in e for e in errors))

    def test_name_missing(self):
        d = _make_skill_dir(self.cicadas_dir, "no-name")
        (d / "SKILL.md").write_text("---\ndescription: Something.\n---\n\n# Body\n")
        errors = self._errors("no-name")
        self.assertTrue(any("'name' field missing" in e for e in errors))

    def test_name_too_long(self):
        slug = "a" * 65
        d = _make_skill_dir(self.cicadas_dir, slug)
        _write_skill_md(d, name=slug)
        errors = self._errors(slug)
        self.assertTrue(any("exceeds 64 characters" in e for e in errors))

    def test_name_bad_charset_uppercase(self):
        d = _make_skill_dir(self.cicadas_dir, "bad-Charset")
        (d / "SKILL.md").write_text("---\nname: bad-Charset\ndescription: desc\n---\n\n")
        errors = validate_skill.validate(str(d), cicadas_dir=self.cicadas_dir)
        self.assertTrue(any("invalid characters" in e for e in errors))

    def test_name_starts_with_hyphen(self):
        slug = "-starts-bad"
        d = _make_skill_dir(self.cicadas_dir, slug)
        (d / "SKILL.md").write_text(f"---\nname: {slug}\ndescription: desc\n---\n\n")
        errors = validate_skill.validate(str(d), cicadas_dir=self.cicadas_dir)
        self.assertTrue(any("starts or ends with a hyphen" in e for e in errors))

    def test_name_ends_with_hyphen(self):
        slug = "ends-bad-"
        d = _make_skill_dir(self.cicadas_dir, slug)
        (d / "SKILL.md").write_text(f"---\nname: {slug}\ndescription: desc\n---\n\n")
        errors = validate_skill.validate(str(d), cicadas_dir=self.cicadas_dir)
        self.assertTrue(any("starts or ends with a hyphen" in e for e in errors))

    def test_name_consecutive_hyphens(self):
        slug = "double--hyphen"
        d = _make_skill_dir(self.cicadas_dir, slug)
        (d / "SKILL.md").write_text(f"---\nname: {slug}\ndescription: desc\n---\n\n")
        errors = validate_skill.validate(str(d), cicadas_dir=self.cicadas_dir)
        self.assertTrue(any("consecutive hyphens" in e for e in errors))

    def test_name_dir_mismatch(self):
        d = _make_skill_dir(self.cicadas_dir, "my-skill")
        (d / "SKILL.md").write_text("---\nname: other-name\ndescription: desc\n---\n\n")
        errors = self._errors("my-skill")
        self.assertTrue(any("does not match directory name" in e for e in errors))

    def test_description_missing(self):
        d = _make_skill_dir(self.cicadas_dir, "no-desc")
        (d / "SKILL.md").write_text("---\nname: no-desc\n---\n\n# Body\n")
        errors = self._errors("no-desc")
        self.assertTrue(any("'description' field missing" in e for e in errors))

    def test_description_empty(self):
        d = _make_skill_dir(self.cicadas_dir, "empty-desc")
        (d / "SKILL.md").write_text("---\nname: empty-desc\ndescription: \n---\n\n")
        errors = self._errors("empty-desc")
        self.assertTrue(any("empty" in e for e in errors))

    def test_description_too_long(self):
        d = _make_skill_dir(self.cicadas_dir, "long-desc")
        long_desc = "x" * 1025
        (d / "SKILL.md").write_text(f"---\nname: long-desc\ndescription: {long_desc}\n---\n\n")
        errors = self._errors("long-desc")
        self.assertTrue(any("exceeds 1024 characters" in e for e in errors))


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

class TestValidateSkillOK(CicadasTest):

    def test_valid_skill_no_errors(self):
        d = _make_skill_dir(self.cicadas_dir, "good-skill")
        _write_skill_md(d, name="good-skill")
        errors = validate_skill.validate("good-skill", cicadas_dir=self.cicadas_dir)
        self.assertEqual(errors, [])

    def test_valid_skill_explicit_path(self):
        d = _make_skill_dir(self.cicadas_dir, "path-skill")
        _write_skill_md(d, name="path-skill")
        errors = validate_skill.validate(str(d), cicadas_dir=self.cicadas_dir)
        self.assertEqual(errors, [])

    def test_valid_skill_long_description_at_limit(self):
        d = _make_skill_dir(self.cicadas_dir, "max-desc")
        desc = "a" * 1024
        (d / "SKILL.md").write_text(f"---\nname: max-desc\ndescription: {desc}\n---\n\n")
        errors = validate_skill.validate("max-desc", cicadas_dir=self.cicadas_dir)
        self.assertEqual(errors, [])


# ---------------------------------------------------------------------------
# Slug resolution
# ---------------------------------------------------------------------------

class TestSlugResolution(CicadasTest):

    def test_active_preferred_over_drafts(self):
        """When skill exists in both active/ and drafts/, active/ is used."""
        # Create valid skill in active
        active = _make_skill_dir(self.cicadas_dir, "shared", "active")
        _write_skill_md(active, name="shared")
        # Create invalid skill in drafts (missing name)
        drafts = _make_skill_dir(self.cicadas_dir, "shared", "drafts")
        (drafts / "SKILL.md").write_text("---\ndescription: something\n---\n\n")

        errors = validate_skill.validate("shared", cicadas_dir=self.cicadas_dir)
        # Should use active/ (valid) → no errors
        self.assertEqual(errors, [])

    def test_falls_back_to_drafts_when_no_active(self):
        d = _make_skill_dir(self.cicadas_dir, "draft-only", "drafts")
        _write_skill_md(d, name="draft-only")
        errors = validate_skill.validate("draft-only", cicadas_dir=self.cicadas_dir)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
