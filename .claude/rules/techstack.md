---
description: Single source of truth for the project's tech stack (frontend, backend, persistence, API, testing, infra)
alwaysApply: true
---

# Tech Stack

This file is the **single source of truth** for tech stack choices. Every other rule, agent, subagent, skill, command, or template must **reference this file** (e.g. "per `.claude/rules/techstack.md`") instead of restating a framework name or version. To change the stack, edit only this file and update `docs/architecture/stack-conventions.md` if layering/folder conventions must change to match.

| Layer | Choice | Notes |
|---|---|---|
| Backend language/framework | Python 3.11+ + FastAPI | Agent-owned generation, no template render pipeline. *(Framework not specified by name — FastAPI assumed for native OpenAPI generation; swap this row if you meant Flask/Django.)* |
| Backend ORM / migration tool | SQLAlchemy 2.x + Alembic | Additive/forward-only migrations only |
| Backend mapper | Pydantic v2 models | Request/response schemas double as the DTO layer |
| Backend unit/integration test framework | pytest | |
| Backend coverage tool | coverage.py (`pytest-cov`) | Gate thresholds live in `.claude/config.yaml` `quality_gates.*` |
| Backend build tool / commands | pip + uvicorn (`pytest`, `pytest --cov`, `uvicorn app.main:app --reload`) | See `.claude/config.yaml` `evals.test_commands.api` |
| Backend health endpoint | `GET /health` (explicit route — not automatic like Spring Actuator) | Must be implemented in the app for `scripts/verify-stack-health.sh` |
| Frontend framework | React 18+ (Vite) + TypeScript | *(Framework not specified beyond "React" — Vite + TypeScript assumed as the default build tool/language; swap this row if you meant plain JS or a different bundler.)* Typed API client generated from OpenAPI |
| Frontend unit test framework | Vitest + React Testing Library | |
| Frontend lint / audit tools | ESLint, `npm audit`, TypeScript compiler | |
| E2E test framework | Playwright | See `.claude/config.yaml` `evals.test_commands.e2e` |
| Frontend build tool / commands | npm + Vite (`npm run dev`, `npm test`, `npm run test:e2e`) | See `.claude/config.yaml` `evals.test_commands.ui` |
| API style | REST + OpenAPI 3.1 | FastAPI generates this natively; treat the generated spec as source of truth for API shape (`contracts/openapi/`) |
| Persistence / database | SQLite (file-based) | Single-file DB; no separate DB server to boot for local/dev/test |
| Module layout | `modules/api` + `modules/ui` monorepo | Roots configurable via `.claude/config.yaml` `modules.*` |
| Auth pattern | JWT bearer (detail deferred to architecture proposal) | |

Every other rule, agent, subagent, skill, command, and template must describe these roles **generically** ("backend framework", "ORM", "coverage tool", "E2E test framework", ...) and cite this file for the concrete name — never restate "Python", "FastAPI", "React", "Vite", "pytest", "Vitest", "Playwright", "SQLAlchemy", "Alembic", "Pydantic", "coverage.py", "SQLite", or "npm" as a hardcoded fact elsewhere. The one exception is a runnable example command (e.g. in `.claude/config.yaml` or a skill's "Run" section): it may show the current default command as an *example*, labeled as following this file, since a command must name a real tool to be runnable — but the prose describing *why*/*what* stays generic.

## Overrides

- Per-project overrides live in `.claude/config.yaml` (`modules.*`, `evals.test_commands.*`, `local_stack.*`), not in this file. This file states **what** the stack is; `config.yaml` states **where** its modules/scripts live.
- Changing a stack choice (e.g. swapping Spring Boot for another backend framework, or Postgres for another datastore) means updating the row here, then checking `docs/architecture/stack-conventions.md` for folder-layering/convention changes and `.claude/config.yaml` `evals.test_commands` for the corresponding build/test commands.
- Do not hardcode a stack choice into product code, factory contracts, or a new rule/agent/skill file — cite this file instead.
