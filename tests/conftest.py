# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path

# Ensure scripts and tests dirs are importable before any test module is collected.
TESTS_DIR = Path(__file__).parent
SCRIPTS_DIR = TESTS_DIR.parent / "src" / "cicadas" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(TESTS_DIR))
