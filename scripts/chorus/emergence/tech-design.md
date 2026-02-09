# Emergence: Technical Design

**Goal**: Define the system architecture and data models.

**Role**: You are a Software Architect. Your job is to design a robust, scalable technical solution that meets the PRD and UX requirements.

## Process

1.  **Ingest**: Read `../incubator/{feature}/prd.md` and `ux.md`.
2.  **Analyze**:
    -   Review existing system snapshots in `.cicadas/canon/`.
    -   Identify necessary data model changes (schema, migrations).
    -   Identify necessary API changes (endpoints, contracts).
    -   Identify new or modified components.
3.  **Draft**: Create `../incubator/{feature}/tech-design.md`.
    -   Include Mermaid diagrams for complex flows.
4.  **Refine**: Human review.

## Output Artifact: `tech-design.md`

Use the template at `scripts/chorus/templates/emergence/tech-design.md`.

## Key Considerations

-   **Separation of Concerns**: Keep business logic separate from UI.
-   **Security**: Validate all inputs.
-   **Performance**: Consider database indexes and caching.
-   **Scalability**: Will this work with 10x data?
