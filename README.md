# Cicadas

A methodology and toolset for sustainable, skill-agnostic Spec-Driven Development (SDD).

Cicadas reverses the traditional relationship between code and documentation. Instead of fighting to keep specifications in sync with code, **Cicadas treats forward-looking docs (PRDs, plans) as disposable inputs** that drive implementation and then expire. Authoritative system documentation is then **reverse-engineered from the code itself** into canonical snapshots.

## The Methodology

1.  **Forward Docs**: You write a PRD and Implementation Plan to drive a specific change.
2.  **Implementation**: You (and your AI agents) write the code.
3.  **Synthesis**: Before merging, you synthesize a new "Cicadas Snapshot" from the code and the intent in your forward docs.
4.  **Husking**: The forward docs are archived ("husked") and never maintained again.
5.  **Canonical Truth**: The `canon/` directory always reflects the current reality of the code.

For a full explanation, see [Cicadas Method (General)](docs/cicadas-method-general.md).

## Project Structure

This repository contains both the definition of the methodology and the **Chorus** reference implementation (CLI tools).

```text
.
├── docs/                       # Methodology documentation
│   ├── cicadas-method.md       # Original concept
│   └── cicadas-method-general.md # Skill-agnostic manual
├── scripts/
│   └── chorus/                 # The Chorus orchestration toolset
│       ├── scripts/            # Python CLI tools (branch, check, archive, etc.)
│       ├── templates/          # Markdown templates for snapshots and docs
│       └── CHORUS.md           # The Agent Manual (Entry point for AI)
└── .cicadas/                   # This project's own Cicadas artifacts
    ├── canon/                  # Canonical snapshots of this repo
    ├── index.json              # Artifact ledger
    └── registry.json           # Active branch registry
```

## Getting Started

To use the Cicadas method on this project (or to bootstrap it on another), see the **[Chorus Agent Manual](scripts/chorus/CHORUS.md)**.

### Quick Command Reference

All tools are located in `scripts/chorus/scripts/`.

- **Start a task**: `python scripts/chorus/scripts/branch.py my-feature --intent "..."`
- **Check status**: `python scripts/chorus/scripts/status.py`
- **Verify work**: `python scripts/chorus/scripts/check.py`
- **Finish task**: `python scripts/chorus/scripts/archive.py my-feature`
