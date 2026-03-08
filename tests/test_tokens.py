# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import unittest
from pathlib import Path

from base import CicadasTest
from tokens import VALID_SOURCES, append_entry, init_log, load_log


class TestInitLog(CicadasTest):
    def test_creates_file_with_empty_entries(self):
        log = self.root / "tokens.json"
        init_log(log)
        self.assertTrue(log.exists())
        data = json.loads(log.read_text())
        self.assertEqual(data, {"entries": []})

    def test_does_not_overwrite_existing_file(self):
        log = self.root / "tokens.json"
        log.write_text(json.dumps({"entries": [{"phase": "existing"}]}))
        init_log(log)
        data = json.loads(log.read_text())
        self.assertEqual(len(data["entries"]), 1)

    def test_creates_parent_dirs(self):
        log = self.root / "nested" / "dir" / "tokens.json"
        init_log(log)
        self.assertTrue(log.exists())


class TestLoadLog(CicadasTest):
    def test_returns_empty_list_when_file_absent(self):
        log = self.root / "nonexistent.json"
        self.assertEqual(load_log(log), [])

    def test_returns_empty_list_on_invalid_json(self):
        log = self.root / "tokens.json"
        log.write_text("not valid json {{{")
        self.assertEqual(load_log(log), [])

    def test_returns_empty_list_when_entries_key_missing(self):
        log = self.root / "tokens.json"
        log.write_text(json.dumps({"other": "data"}))
        self.assertEqual(load_log(log), [])

    def test_returns_entries(self):
        log = self.root / "tokens.json"
        log.write_text(json.dumps({"entries": [{"phase": "lifecycle"}]}))
        entries = load_log(log)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["phase"], "lifecycle")


class TestAppendEntry(CicadasTest):
    def _log(self) -> Path:
        return self.root / "tokens.json"

    def test_creates_file_on_first_write(self):
        append_entry(self._log(), initiative="test", phase="lifecycle", source="unavailable")
        self.assertTrue(self._log().exists())

    def test_entry_has_required_fields(self):
        append_entry(self._log(), initiative="test", phase="lifecycle", source="unavailable")
        entries = load_log(self._log())
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual(e["initiative"], "test")
        self.assertEqual(e["phase"], "lifecycle")
        self.assertEqual(e["source"], "unavailable")
        self.assertIn("timestamp", e)

    def test_multiple_appends_grow_list(self):
        for i in range(3):
            append_entry(self._log(), initiative="test", phase=f"phase-{i}", source="unavailable")
        self.assertEqual(len(load_log(self._log())), 3)

    def test_optional_fields_default_to_none(self):
        append_entry(self._log(), initiative="test", phase="lifecycle", source="unavailable")
        e = load_log(self._log())[0]
        self.assertIsNone(e["subphase"])
        self.assertIsNone(e["input_tokens"])
        self.assertIsNone(e["output_tokens"])
        self.assertIsNone(e["cached_tokens"])
        self.assertIsNone(e["model"])
        self.assertIsNone(e["notes"])

    def test_optional_fields_stored_when_provided(self):
        append_entry(
            self._log(),
            initiative="test",
            phase="emergence",
            source="agent-reported",
            subphase="clarify",
            input_tokens=1200,
            output_tokens=400,
            cached_tokens=800,
            model="claude-sonnet-4-6",
            notes="two rounds",
        )
        e = load_log(self._log())[0]
        self.assertEqual(e["subphase"], "clarify")
        self.assertEqual(e["input_tokens"], 1200)
        self.assertEqual(e["output_tokens"], 400)
        self.assertEqual(e["cached_tokens"], 800)
        self.assertEqual(e["model"], "claude-sonnet-4-6")
        self.assertEqual(e["notes"], "two rounds")

    def test_raises_on_invalid_source(self):
        with self.assertRaises(ValueError):
            append_entry(self._log(), initiative="test", phase="lifecycle", source="bad-source")

    def test_raises_on_empty_initiative(self):
        with self.assertRaises(ValueError):
            append_entry(self._log(), initiative="", phase="lifecycle", source="unavailable")

    def test_raises_on_empty_phase(self):
        with self.assertRaises(ValueError):
            append_entry(self._log(), initiative="test", phase="", source="unavailable")

    def test_all_valid_sources_accepted(self):
        for source in VALID_SOURCES:
            log = self.root / f"tokens-{source}.json"
            append_entry(log, initiative="test", phase="lifecycle", source=source)
            self.assertEqual(load_log(log)[0]["source"], source)

    def test_timestamp_is_iso8601_utc(self):
        append_entry(self._log(), initiative="test", phase="lifecycle", source="unavailable")
        ts = load_log(self._log())[0]["timestamp"]
        # Must end with Z and contain T
        self.assertTrue(ts.endswith("Z"))
        self.assertIn("T", ts)

    def test_creates_parent_dirs(self):
        log = self.root / "nested" / "tokens.json"
        append_entry(log, initiative="test", phase="lifecycle", source="unavailable")
        self.assertTrue(log.exists())


if __name__ == "__main__":
    unittest.main()
