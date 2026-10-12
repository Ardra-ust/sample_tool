# Stack conventions

Stack names/versions (backend, frontend, persistence, testing, etc.): `.claude/rules/techstack.md`. This file covers folder layering and conventions **within** that stack, not the stack choice itself.

This starter kit uses **agent-owned** code generation. There is no template render pipeline.

## Backend (`modules/api`)

Layer **roles** are fixed; the folder **name** per role depends on whichever backend framework `.claude/rules/techstack.md` currently names. Agents resolve the row matching that framework below — they do not hardcode a folder name for a different stack, and they do not invent a row for an unlisted framework (register Open DQ instead; a human adds the row).

| Layer role | Python + FastAPI (techstack.md current default) | Java + Spring | Node.js + Express/TypeScript | Go + Gin/Echo | C# + ASP.NET Core |
|---|---|---|---|---|---|
| Routing / boundary — REST endpoints, validation, response envelope | `routers/` | `controller/` | `routes/` (route wiring) + `controllers/` (handlers) | `handler/` (Go convention: singular package names) | `Controllers/` |
| Business logic — transactions, orchestration | `services/` | `service/` | `services/` | `service/` | `Services/` |
| Data access — persistence layer | `repositories/` | `repository/` | `repositories/` | `repository/` | `Repositories/` |
| Request/response schema (DTO layer) | `schemas/` (Pydantic models) | `dto/` | `dto/` (e.g. Zod/class-validator schemas) | `dto/` (request/response structs) | `DTOs/` |
| Domain / persistence model | `models/` (SQLAlchemy entities) | `entity/` | `models/` (ORM models, e.g. Prisma/TypeORM) | `model/` (Go convention: singular) | `Models/` (or `Entities/`) |
| DTO ↔ domain mapping | inline in `services/`, or `mappers/` if the slice needs a dedicated layer | `mapper/` | inline in `services/`, or `mappers/` | inline in `service/` | `Mappings/` (e.g. AutoMapper profiles) |
| Versioned schema migrations | `alembic/versions/` (migration tool per techstack.md) | `db/migration/` | `migrations/` (e.g. Prisma/Knex/TypeORM) | `migrations/` (e.g. golang-migrate/goose) | `Migrations/` (EF Core) |

Only the frameworks listed above resolve automatically. Naming case follows each ecosystem's own convention (Go: lowercase singular; C#: PascalCase; the rest: lowercase plural) — agents must not flatten that to one casing style across stacks.

- OpenAPI is source of truth for API shape (`contracts/openapi/`).
- Schema-layer field names must match OpenAPI schemas.
- No secrets in code or logs.
- Adding a new backend framework: add a column here (folder names for that framework) in the same edit that changes the row in `.claude/rules/techstack.md` — the table doesn't populate itself for a framework it has never seen.

## Frontend (`modules/ui`)

```
app/ → routed pages
components/ → presentational + container components
lib/api/ → typed client from OpenAPI
```

- Wiring gate: every UI action traces to OpenAPI operation + story AC.
- Use typed fetch client; no invented API fields.

## Tests

- Backend unit/integration test framework per `.claude/rules/techstack.md`; cite `docs/test-cases.md` case IDs in test names.
- Frontend unit and E2E test frameworks per `.claude/rules/techstack.md`.
- br-coverage-validator PASS before test scripts.

## Audit note

Record stack-conventions compliance (layering, OpenAPI alignment, cited case IDs) in the implement audit.
