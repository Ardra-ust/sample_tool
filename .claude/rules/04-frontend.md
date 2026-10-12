---
description: Frontend UI defaults
globs: "**/*.{ts,tsx,js,jsx}"
alwaysApply: false
---

# Frontend

- Stack (framework, version): `.claude/rules/techstack.md`. Update the `globs` pattern above if the frontend language there changes.
- Prefer the target module's routing/page conventions per `config.yaml`.
- Loading, empty, and error states required for every user journey.
- No hardcoded user-visible strings when the project uses i18n.
- Typed API client from OpenAPI; do not invent field semantics.
- FE↔BE wiring is a required gate of `/implement-ui`, not a separate public command.
