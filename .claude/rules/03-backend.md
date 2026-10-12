---
description: Backend implementation defaults (agent-owned)
globs: modules/api/**/*
---

# Backend

- Stack (language, framework, version): `.claude/rules/techstack.md`. Layering/folder conventions: `docs/architecture/stack-conventions.md`.
- **Agent-owned implement:** no framework master-templates or render-check pipeline in kit DoD.
- Layering: routing/boundary → business logic → data-access, per the folder names `docs/architecture/stack-conventions.md` gives for the current techstack.md backend framework; centralized error envelope; validation on inputs.
- Persist OpenAPI/schema-layer alignment via api-agent contract sync during `/implement-api`.
- Unit tests required; coverage floor from `config.yaml` `quality_gates.api_unit_line_coverage_min`.
- No secrets in source; mask PII in logs.
