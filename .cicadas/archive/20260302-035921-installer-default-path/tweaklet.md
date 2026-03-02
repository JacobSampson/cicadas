
# Tweaklet: installer-default-path

## Intent
Change the installer's default skill destination from `src/cicadas` to `.cicadas-skill/cicadas`,
keeping the Cicadas skill out of the project's source tree and in a convention-friendly hidden directory.

## Proposed Change

### 1. `install.sh`
- Line 11: `INSTALL_DIR="src/cicadas"` → `INSTALL_DIR=".cicadas-skill/cicadas"`

### 2. `HOW-TO.md`
- Update the "Download and extract" step description default path
- Update the `--dir` flag default value in the options table
- Update the symlink example (`../../src/cicadas` → `../../.cicadas-skill/cicadas`)

### 3. `README.md`
- Update the one-liner install description: "downloads Cicadas into `src/cicadas/`" → `.cicadas-skill/cicadas/`

Note: The Quick Command Reference table in `README.md` (`src/cicadas/scripts/...`) is left as-is —
it reflects this repo's own dogfooding layout, not a user install path.

## Tasks
- [ ] Update `install.sh` default `INSTALL_DIR` <!-- id: 10 -->
- [ ] Update `HOW-TO.md` default path references <!-- id: 11 -->
- [ ] Update `README.md` install description line <!-- id: 12 -->
- [x] Significance Check: Yes — canon/tech-overview.md line 53 references `src/cicadas/` as the default install path. Update after merge on master. <!-- id: 13 -->

---
_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
