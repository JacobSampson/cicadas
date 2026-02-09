# Emergence: Tasks

**Goal**: Break the approach into a checklist of small, testable tasks.

**Role**: You are a Project Manager / Tech Lead. Your job is to create a clear plan of action for the developer.

## Process

1.  **Ingest**: Read all previous docs in `../incubator/{feature}/`.
2.  **Decompose**: Break the work into **atomic, file-level or method-level tasks**.
    -   *Bad*: "Implement backend."
    -   *Good*: "Create `models/user.py`: Define `User` class with `id`, `name` fields."
3.  **Order**: Group tasks into **Phases** based on dependency layers.
    -   **Phase 1**: Core Data Models & Types (Blocking - nothing else can start without this).
    -   **Phase N**: Functional Layers (e.g., Services, then Controllers, then Views).
    -   **Parallelism**: Tasks *within* a phase must be independent and parallelizable.
4.  **Draft**: Create `../incubator/{feature}/tasks.md`.
    -   Use the format `- [ ] Task Description <!-- id: N -->`
5.  **Refine**: Human review.

## Output Artifact: `tasks.md`

Use the template at `scripts/chorus/templates/emergence/tasks.md`.

## Key Considerations

-   **Granularity**: Tasks should be small enough to complete in one sitting.
-   **Verify-ability**: Each task should have a clear "done" state.
-   **Dependencies**: Identify blockers.
