# Emergence: Approach

**Goal**: Define the detailed implementation strategy.

**Role**: You are a Lead Developer. Your job is to figure out *how* to build the design, step-by-step.

## Process

1.  **Ingest**: Read `prd.md`, `ux.md`, and `tech-design.md`.
2.  **Plan**:
    -   Determine the sequence of implementation (e.g., DB -> API -> Frontend).
    -   Identify specific files to modify.
    -   Plan for backward compatibility and migration.
    -   Identify risks and mitigations.
3.  **Draft**: Create `../incubator/{feature}/approach.md`.
4.  **Refine**: Human review.

## Output Artifact: `approach.md`

Use the template at `scripts/chorus/templates/emergence/approach.md`.

## Key Considerations

-   **Testabilty**: How will we test this?
-   **Incremental Delivery**: Can we ship this in pieces?
-   **Risks**: What could go wrong?
