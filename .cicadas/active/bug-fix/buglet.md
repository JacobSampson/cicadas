# Buglet: No Cicadas copyright in generated artifacts

## Problem Description
Cicadas writes its own copyright line ("Copyright 2026 Cicadas Contributors", SPDX-License-Identifier) into every generated spec, code, or other artifact when those texts are present on the original templates. User projects should not have Cicadas copyright embedded in their generated deliverables.

## Reproduction Steps
1. Run any script or flow that generates specs from templates (e.g. init, kickoff, or copying from `templates/`).
2. Inspect the generated file (e.g. `.cicadas/active/.../prd.md` or a file created from a template).
3. Observe the Cicadas copyright footer in the output.

## Proposed Fix
Remove the Cicadas copyright footer from all templates and from any script that appends or injects it into generated output. Generated artifacts (specs, canon, etc.) should either have no copyright block or be left for the project to add their own.

## Tasks
- [ ] Reproduce bug with a test case <!-- id: 0 -->
- [ ] Remove copyright from templates and generated output <!-- id: 1 -->
- [ ] Verify fix with the test case <!-- id: 2 -->
- [ ] Significance Check: Does this warrant a Canon update? <!-- id: 3 -->
