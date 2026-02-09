You are an expert technical writer and software architect. Your task is to update the Canonical Documentation (Canon) for the project based on the latest changes.

**Inputs:**
1.  **Current Canon Code**: The source code of the project, including the changes in the current branch.
2.  **Forward Docs**: Documentation from the `forward/` directory for this brood or branch describing the recent changes (PRDs, specs, tasks). 
3.  **Existing Canon**: The current state of the documentation in `canon/`.

**Task:**
Review the changes and update the following files in the `canon/` directory. Create them if they don't exist, using the templates provided.

1.  **`product-overview.md`**: Update goals, personas, metrics, and feature lists if the business logic or scope has changed.
2.  **`ux-overview.md`**: Update design principles, new UI patterns, or user flows if the frontend/UX has changed.
3.  **`tech-overview.md`**: Update the architecture, component list, API specs, data models, and sequence diagrams to reflect the codebase state.
4.  **`modules/{module_name}.md`**: Update or create specific module documentation for any modified code modules.

**Guidelines:**
-   **Be Specific**: accurate technical details are more important than high-level fluff.
-   **Be Comprehensive**: Do not delete existing information unless it is obsolete. *Expand* the documentation.
-   **Use Mermiad**: Use mermaid diagrams for complex flows.
-   **Follow Templates**: Adhere to the structure of the provided templates.

**Output:**
1.  **Synthesis Plan**: Create a bulleted list of the files you intend to modify and a brief summary of the changes for each.
2.  **File Content**: Provide the full markdown content for each file.
