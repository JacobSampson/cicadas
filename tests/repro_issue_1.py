
import unittest
import shutil
import tempfile
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts directory to path to allow importing modules
sys.path.append(str(Path(__file__).parent.parent / "scripts/chorus/scripts"))

# Mock utils before importing archive
sys.modules["utils"] = MagicMock()
from archive import archive_item

class TestArchiveRegistryUpdate(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.cicadas_dir = self.test_dir / ".cicadas"
        self.cicadas_dir.mkdir()
        (self.cicadas_dir / "forward").mkdir()
        (self.cicadas_dir / "archive").mkdir()
        
        # Create dummy registry
        self.registry_data = {
            "branches": {
                "feature-branch": {"intent": "test intent"}
            },
            "broods": {
                "test-brood": {
                }
            }
        }
        with open(self.cicadas_dir / "registry.json", "w") as f:
            json.dump(self.registry_data, f)
            
        # Create dummy branch directory
        (self.cicadas_dir / "forward" / "feature-branch").mkdir()
        (self.cicadas_dir / "forward" / "feature-branch" / "test.md").touch()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("archive.get_project_root")
    @patch("archive.load_json")
    @patch("archive.save_json")
    def test_archive_removes_from_brood(self, mock_save, mock_load, mock_root):
        mock_root.return_value = self.test_dir
        
        # Setup load_json side effect to return our registry data
        # We need to return a copy so modifications in the function don't affect our reference immediately
        def load_side_effect(path):
            if path.name == "registry.json":
                return self.registry_data.copy()
            return {}
        mock_load.side_effect = load_side_effect

        # Run archive_item
        archive_item("feature-branch")

        # Verify save_json was called with updated registry
        args, _ = mock_save.call_args
        saved_registry = args[1]
        
        # Assertions
        self.assertNotIn("feature-branch", saved_registry["branches"], "Branch should be removed from top-level branches")
        self.assertNotIn("branches", saved_registry["broods"]["test-brood"], "Brood should not have a 'branches' key")

if __name__ == "__main__":
    unittest.main()
