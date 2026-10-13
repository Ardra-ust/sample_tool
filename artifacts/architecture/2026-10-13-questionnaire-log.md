# Tech-stack questionnaire — ai-news-agent (2026-10-13)

> `/propose-architecture`. Logged Q&A. No secrets, credentials or PII in this log.

| Field | Value |
|-------|-------|
| **Date** | 2026-10-13 |
| **Operator** | Stated in the command arguments (role not named) |
| **Module / context** | `ai-news-agent` / `news-intelligence` |
| **Sources** | `artifacts/brd/ai-news-agent-BRD-draft.md` (Draft); `.claude/rules/techstack.md`; `.claude/config.yaml` |

| # | Question | Recommended (techstack.md default) | Your choice | Source if pre-filled |
|---|----------|------------------------------------|-------------|----------------------|
| 1 | Backend framework? | Python 3.11+ + Flask | Python 3.11+ + Flask | Operator (command arguments) |
| 2 | UI framework? | Flask Jinja templates + HTML/JS | Jinja templates + HTML/JS | Operator (command arguments) |
| 3 | API style? | REST + OpenAPI 3.1 (`contracts/openapi/`) | REST/JSON; OpenAPI spec as source of truth (no answer given; recommended default kept) | BRD §4.1, §8; `config.yaml` `modules.openapi` |
| 4 | Persistence? | MySQL + SQLAlchemy/Alembic | MySQL (database `news_app`). ORM and migration tool not stated; recommended default kept, confirm | Operator (MySQL); techstack.md (ORM) |
| 5 | UI data fetching? | Typed fetch client from OpenAPI | Not stated. The UI is server-rendered and polls `/api/refresh/status`. A typed client generator is not used with plain HTML/JS. Confirm | BRD §10; techstack.md (no JS framework) |
| 6 | Test layers? | pytest + Playwright | pytest and coverage.py for the API (≥70% line coverage); Flask test client for template and route tests; Playwright for E2E | Operator and BRD NFR-008; `config.yaml` `evals.test_commands` |
| 7 | Module layout? | `modules/api` (backend) + `modules/ui` (templates and static) | `modules/api` holds the Flask app; `modules/ui` holds `templates/` and `static/`. Matches `config.yaml` | `config.yaml` `modules.*`; techstack.md (module layout) |
| 8 | Auth pattern (high level)? | JWT bearer (detail deferred) | **None for this build** (owner answer to DQ-A1). Parity with the existing app; all routes including `POST /api/refresh` are open. Known risk RISK-A1: add authentication before wider exposure. | BRD §2, §8; owner answer |
| 9 | Cloud target (azure / aws / gcp / on-prem / hybrid)? | Not in techstack.md | **Local only for this build** (owner answer to DQ-A2): Flask on port 5000, local MySQL, `scripts/run-local-stack.sh`. Cloud target not decided; out of scope for this sprint. Azure WebJob stays optional per FR-039. | Owner answer to DQ-A2; BRD FR-039 |
| 10 | Compliance tags (e.g. SOC2, PCI)? | None | **None stated.** Not assumed. | — |
| 11 | Existing ADRs? | — | None found under `docs/architecture/` apart from `stack-conventions.md`. | Repo listing |

## Operator answers recorded as given

- Stack: Python 3.11+ Flask, MySQL, Jinja templates + HTML/JS.
- Do not recommend Java or Next.js.

## Gaps left open (Open DQ, see the proposal)

- DQ-A1: RESOLVED. No authentication for this build; known risk RISK-A1 (add authentication before wider exposure).
- DQ-A2: RESOLVED for this build (local only). Open item: cloud target not decided; out of scope for this sprint.
- DQ-A3: model name for the Azure chat deployment (BRD DQ-001 notes say `gpt-4o` per the owner answer; notes §12 say `gpt-5.2-chat`).
- DQ-A4: worker supervision when the web process restarts while a refresh subprocess is running.
