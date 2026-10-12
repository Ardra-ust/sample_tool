---
description: Frontend UI defaults (Flask Jinja templates + HTML/JS)
globs: "**/{templates,static}/**/*.{html,js,css}"
alwaysApply: false
---

# Frontend

- Stack (framework, version): `.claude/rules/techstack.md`. UI is Flask Jinja templates in `templates/` plus HTML/JS and CSS in `static/`. Update the `globs` pattern above if the UI layout there changes.
- Prefer the target module's routing/page conventions per `config.yaml`.
- Loading, empty, and error states required for every user journey.
- No hardcoded user-visible strings when the project uses i18n.
- Call only OpenAPI-defined API operations (`contracts/openapi/`); do not invent field semantics.
- FE↔BE wiring is a required gate of `/implement-ui`, not a separate public command.
