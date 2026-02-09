# Cicadas: Implementation Protocol

This document defines the rules for an **Implementation Agent**. These rules prevent agents from "running amok" and ensure changes are made within the correct safety boundaries.

## 1. The Hard Stop
An agent MUST stop and wait for human review after the **Emergence** phase (generating `tasks.md`). 
- **Rule**: Do not start implementing code until the user explicitly says "Hatch the Brood" or "Start a Branch".
- **Why**: The `tasks.md` file often needs human correction for granularity and parallelism.

## 2. Identity Check (Branch Safety)
Before touching any project source code, an agent MUST verify its environment.
- **Rule**: You must only write code if you are on a **registered git branch** associated with a specific intent in `.cicadas/registry.json`.
- **Constraint**: No direct code changes to the `main` or `master` branch are permitted.

## 3. Execution Scope
When working on a branch:
- **Rule**: Only implement the tasks defined in the **Phase** or **Work Group** assigned by the user.
- **Rule**: If you discover that a task requires changing files outside your declared scope, STOP and notify the user.

## 4. Synthesis
When work is complete:
- **Rule**: Do not merge.
- **Rule**: You must run the synthesis process (updating `canon/` docs) before the branch can be archived.
