# Project Overview: Cicadas

This repository contains the official implementation of the **Cicadas Method**—a sustainable, spec-driven development methodology designed for high-velocity engineering.

## 🔄 Dogfooding
Cicadas is both the **product** and the **process**. We use the Cicadas methodology (partitions, initiative branches, and Reflect operations) to evolve and maintain this orchestrator. Every change to this codebase follows the same rigorous spec-to-code-to-canon flow it enables for others.

## 📂 Project Structure

### Source & Code
- **[src/](src/)**: The main source directory.
  - **[src/cicadas/](src/cicadas/)**: Contains the core logic of the orchestrator, including lifecycle scripts (kickoff, branch, status, create_lifecycle, open_pr), emergence subagent instructions, and spec templates.
- **[tests/](tests/)**: A comprehensive suite of unit and integration tests ensuring the reliability of the CLI scripts and orchestration logic.

### Agent & Methodology Memory
- **[.agents/](.agents/)**: Stores agentic configuration, including custom skills (like the `cicadas` skill itself) and automated workflows that guide the AI's behavior.
- **[.cicadas/](.cicadas/)**: The "Institutional Memory" of the project. This directory tracks active initiatives, holds the authoritative **Canon** (reverse-engineered from code), and maintains the registry of partitions and signals.

## 📖 Further Reading
- **Root [README.md](README.md)**: High-level introduction, philosophy, and quick-start guide.
- **[src/cicadas/README.md](src/cicadas/README.md)**: Detailed technical breakdown of the orchestrator's architecture, directory structure, and operational formulas.

---
_Copyright 2026 Cicadas Contributors_
_SPDX-License-Identifier: Apache-2.0_
