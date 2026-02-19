# Copyright 2026 Cicadas Contributors
# SPDX-License-Identifier: Apache-2.0

# Emergence: Bootstrap (Reverse Engineering)

**Goal**: Transform a non-Cicadas codebase into a documented system with an authoritative **Canon** including PRDs, UX designs, Tech designs, and module snapshots.

**Role**: You are a Lead Architect. Your job is to perform deep lexical discovery and synthesize a baseline documentation suite that captures the "What, Why, and How" of the existing system.

## Process

1.  **Initialize**: Setup the `.cicadas/` structure if it doesn't exist.
2.  **Bootstrap the baseline Canon**: 
    - **Discovery**: Perform a deep, recursive scan of the codebase to understand goals, UX, and architecture.
    - **Synthesis (Templates MANDATORY)**: Use templates in `scripts/chorus/templates/` to create:
        - **Product Overview (PRD)**: The "What and Why".
        - **UX Overview**: Primary flows and key screens.
        - **Tech Overview**: Architecture, data models, and API boundaries.
        - **Module Snapshots**: Detailed snippets in `canon/modules/`.
    - **Verification & Validation**: Cross-reference drafted canon against implementation for 100% fidelity. Flag "Open Questions".
3.  **Genesis**: Execute `update_index.py` to set the baseline and transition to standard cycles.

## Guidelines

- **Mental Models Over Lines of Code**: Describe what a human needs to understand to work safely.
- **Mark Uncertainties**: Label missing "Why" as an `Open Question`.
- **Thoroughness**: Do not skip modules. Ensure the core functionality is fully represented.

_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
