# Tech-stack questionnaire — {{SESSION_ID}}

> `/propose-architecture`. Log Q&A to `artifacts/architecture/<date>-questionnaire-log.md`. "Recommended" column mirrors the kit default in `.claude/rules/techstack.md` — keep both in sync if the default stack changes.

| Field | Value |
|-------|-------|
| **Date** | {{YYYY-MM-DD}} |
| **Operator** | {{name or role}} |

| # | Question | Recommended (recommended default) | Your choice | Source if pre-filled |
|---|----------|------------------------------|-------------|----------------------|
| 1 | Backend framework? | Python 3.11+ + FastAPI | | |
| 2 | UI framework? | React 18+ (Vite) + TypeScript | | |
| 3 | API style? | REST + OpenAPI 3.1 | | |
| 4 | Persistence? | SQLite + SQLAlchemy/Alembic | | |
| 5 | UI data fetching? | Typed fetch client from OpenAPI | | |
| 6 | Test layers? | pytest + Vitest + Playwright | | |
| 7 | Module layout? | `modules/api` + `modules/ui` monorepo | | |
| 8 | Auth pattern (high level)? | JWT bearer (detail deferred) | | |

## Suggested config.yaml bindings (proposal only)

```yaml
modules:
 api: modules/api
 ui: modules/ui
 openapi: contracts/openapi/{{service}}-v1.yaml
```
