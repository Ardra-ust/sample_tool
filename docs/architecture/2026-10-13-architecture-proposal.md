# Architecture Proposal — ai-news-agent

> From `/propose-architecture`. Status **Accepted** by Ardra Arun on 2026-10-13 (human architecture review).

| Field | Value |
|-------|-------|
| **Proposal ID** | AP-2026-10-13 |
| **Date** | 2026-10-13 |
| **Author** | documentation-agent (mode `architecture`), run inline by the orchestrator |
| **Sources** | BRD `artifacts/brd/ai-news-agent-BRD-draft.md` (Draft; FR/BR/NFR/AC cited below); questionnaire log `artifacts/architecture/2026-10-13-questionnaire-log.md`; `.claude/rules/techstack.md`; `.claude/config.yaml`; `docs/architecture/stack-conventions.md` |
| **Status** | Accepted — Ardra Arun, 2026-10-13 |

## Executive summary

- **Recommended pattern:** a single Flask web service (JSON API and Jinja-rendered pages) plus one refresh worker process that the web service starts as a subprocess. Not microservices, and no separate backend-for-frontend. The BRD §4.1 architecture line says the same ("single Flask web service plus a separate refresh worker").
- **One-line rationale:** the BRD requires the pipeline to run outside the request (FR-039) and the UI to be server-rendered Jinja with plain JS (BRD §4.1, §10). A single web service with one worker satisfies both without adding deployable components. (Driver: BRD §4.1, FR-039, FR-041.)

## Drivers

| ID | Driver | Source | Locator |
|----|--------|--------|---------|
| FR-039 | Refresh pipeline runs in a worker subprocess, outside the request | BRD §5 | notes §9 |
| FR-041 | Starting the web server does not fetch news; the UI shows the stored snapshot | BRD §5 | notes §9 |
| FR-034–FR-037 | Latest-snapshot, refresh start, status and health routes | BRD §5 | notes §8 |
| FR-026–FR-033 | Server-rendered news grid, sort, filters, refresh button with polling | BRD §5 | notes §10 |
| FR-042, NFR-001 | Secrets and connection settings from `.env`, never hardcoded | BRD §5, §10 | notes §11 |
| BR-015, BR-016 | Atomic refresh lock; stale-lock clearance after 70 minutes | BRD §6 | DQ-018 answer |
| FR-045 | Fixed twelve-stage pipeline order | BRD §5 | notes §5 "order matters" |
| NFR-002, NFR-003 | No-cache headers on status and snapshot endpoints; IST timestamps | BRD §10 | notes §4, §8 |
| NFR-006, NFR-009 | Mask secrets and PII in logs; strip HTML from feed text | BRD §10 | DQ-014 answer |
| NFR-008 | Backend line coverage ≥ 70% | BRD §10 | DQ-010 answer; `config.yaml` |

## Context map

| Context | Relationship | Neighbor | Integration style | Contract ref |
|---------|--------------|----------|-------------------|--------------|
| News API and UI (Flask) | upstream of the browser | Browser (Viewer, Refresh user) | sync HTTP: HTML pages and JSON routes | `contracts/openapi/ai-news-agent-v1.yaml` (JSON routes); templates in `modules/ui` |
| Refresh worker | downstream of the web service | Web service | local subprocess; coordination through the status record | BRD §7 (status fields), §8 (lock behaviour) |
| News sources | upstream of the worker | RSS feeds (42), Google News RSS (25 searches), SearchAPI.io, Tavily | sync HTTP pulls | BRD §8 |
| LLM and embeddings | upstream of the worker | Azure OpenAI (one resource, chat and embeddings) | sync HTTP | BRD DQ-001 answer |
| Data store | shared | MySQL, database `news_app` | SQL over a connection from `.env` | BRD §7 |
| Azure WebJob (optional) | alternative trigger for the worker | Azure | HTTP call, only when `AZURE_WEBJOB_TRIGGER_URL` is set | BRD FR-039 (DQ-012 answer) |

## Logical topology

> Diagram: `artifacts/diagrams/2026-10-13-logical-topology.mmd`

| Component | Role | Notes |
|-----------|------|-------|
| Flask web service (`modules/api`, package `app`) | Routes, services, repositories, JSON API, page rendering, refresh start | Templates and static from `modules/ui` (`template_folder` and `static_folder`) |
| Jinja templates and static files (`modules/ui`) | Page layout, sort and filter controls, polling script | Served by the web service; no separate UI server |
| Refresh worker (`refresh_worker.py`) | Runs the twelve pipeline stages (FR-045) and writes the snapshot and status | Started as a subprocess by the web service; or triggered by the optional WebJob |
| MySQL (`news_app`) | Snapshot rows and the single status record | Connection from `.env` |
| Azure OpenAI | Chat and embeddings | Single resource (DQ-001 answer) |
| External news sources | RSS, Google News RSS, SearchAPI.io, Tavily | Failures logged and skipped (DQ-018 answer) |

### Options considered

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| A. Run the pipeline inside the refresh request | Simplest; no process management | Long-running request; conflicts with FR-039 and notes §9 | Rejected |
| B. Web service starts a worker subprocess; atomic status-record lock (chosen) | Matches FR-039 and the BRD §4.1 architecture line; keeps the request short; simple to run locally on port 5000 | No supervisor by design: the worker finishes and clears its own flag; stale-lock rule covers a dead worker (DQ-A4 answer) | **Chosen** |
| C. Azure WebJob as the only trigger | Managed scheduling | Requires Azure hosting, which is out of scope for this build (DQ-A2 answer); not the default | Rejected as default; kept as the optional path in FR-039 |
| D. Separate services for UI, API and pipeline | Independent scaling | Adds deployables for a single-team tool; not required by any driver | Rejected |

## Cloud and deployment

| Concern | Choice | Source / ASSUMPTION |
|---------|--------|---------------------|
| Cloud / on-prem | **Local only for this build** (DQ-A2 answer): Flask on port 5000 with local MySQL, started with `scripts/run-local-stack.sh`. Cloud target not decided; out of scope for this sprint. | DQ-A2 answer; open item |
| Regions / DR | Not applicable for a local build | DQ-A2 answer |
| Environments | Local run on port 5000 (BRD §8, notes §8). Other environments not stated. | notes §8 |
| Compute | One web process; one worker process per refresh | FR-039 |
| Identity / secrets | Secrets by name only, read from `.env` (`MYSQL_*`, `TAVILY_API_KEY`, `SEARCHAPI_IO_KEY`, Azure OpenAI settings, optional WebJob settings). No values in any artefact. | FR-042, NFR-001 |

## Tech stack

| Layer | Technology | Maps to config binding |
|-------|------------|------------------------|
| API | Python 3.11+ with Flask | `modules.api` = `modules/api` |
| UI | Flask Jinja templates + HTML/JS | `modules.ui` = `modules/ui` |
| Contract | REST/JSON; OpenAPI 3.1 | `modules.openapi` = `contracts/openapi/ai-news-agent-v1.yaml` |
| Data | MySQL (`news_app`); ORM and migrations per techstack.md (SQLAlchemy 2.x and Alembic) — **confirm** | `local_stack` and `.env` settings |
| Messaging | None. The worker is started as a subprocess; no queue. | — |
| Infra | None for this build (DQ-A2 answer). `modules.infra` is not used. No infra, Terraform, deployment or CI/CD slice in the sprint. | DQ-A2 answer |

## Client / server model

| Concern | Decision | Cite |
|---------|----------|------|
| UI rendering | Server-side rendering (Jinja) with a small amount of plain JS for sort, filter and status polling | BRD §10; FR-030 |
| API exposure | Same-origin JSON routes used by the page script; no separate browser-direct API | BRD §8 |
| Auth flow | **None for this build** (DQ-A1 answer), for parity with the existing app. The UI and all routes, including `POST /api/refresh`, are open to anyone who can reach the server. No login slice. | DQ-A1 answer; see Known risks |
| Session / token handling | Not applicable: no sessions and no tokens in this build. The JWT bearer default in techstack.md is not used for this build. | DQ-A1 answer |

## Integration patterns

| System | Direction | Protocol | Notes |
|--------|-----------|----------|-------|
| RSS feeds (42) | inbound | HTTP RSS | BRD FR-001–003 |
| Google News RSS (25) | inbound | HTTP RSS; wrapper links decoded | BRD FR-004–006 |
| SearchAPI.io | inbound | HTTP GET, REST/JSON | BRD FR-007 |
| Tavily | inbound | Tavily search API | BRD FR-008–009 |
| Azure OpenAI (chat and embeddings) | outbound | HTTP, REST/JSON | BRD DQ-001 answer; chat model is whatever `AZURE_OPENAI_CHAT_DEPLOYMENT` is set to (DQ-A3, resolved) |
| MySQL | in and out | SQL connection | BRD §7 |
| Azure WebJob (optional) | outbound | HTTP call | Only when `AZURE_WEBJOB_TRIGGER_URL` is set (BRD FR-039) |

## Security and data

| Trust boundary | Controls | Data classification |
|----------------|----------|---------------------|
| Browser ↔ Flask web service | Output encoding through Jinja; no-cache headers on status and snapshot routes (NFR-002); no user input is stored (none in BRD). Authentication: **none for this build** (DQ-A1 answer; known risk below). | Public news content; status records Internal (DQ-A5 answer). |
| Web service ↔ worker (local subprocess) | Coordinated only through the atomic status record; no shared secrets beyond `.env` | Internal status only |
| Worker ↔ external sources and Azure OpenAI | Keys from `.env`; HTML stripped from feed text (NFR-009); failures logged and skipped | Public news content |
| Worker ↔ MySQL | Credentials from `.env` (NFR-001); masking in logs (NFR-006) | Public news content plus status |

## NFR targets

| NFR | Target | Verification | Source |
|-----|--------|--------------|--------|
| Backend line coverage | ≥ 70% | Coverage report from the API test run | BRD NFR-008, AC-021 |
| Stale-lock clearance | 70 minutes | Test with a stale status record | BRD BR-016, AC-005 |
| Refresh duration | Baseline: average of 3 reference runs, recorded by the owner. Tolerance: at most 1.5× the baseline. Open until the baseline is recorded. | Measured refresh duration (DQ-004, DQ-019) | BRD DQ-004 answer |
| Duplicate-removal thresholds | Embedding 0.75 / 0.82; title 0.92 | Pair test on saved snapshots | BRD AC-020 |
| Pipeline order | Twelve stages in FR-045 order | Stubbed test (AC-022) | BRD FR-045, AC-022 |
| Availability and latency | None required | — | BRD DQ-015 answer |

## ADR index

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Flask single web service with Jinja UI from `modules/ui` | Accepted (Ardra Arun, 2026-10-13) |
| ADR-002 | Refresh worker as subprocess with an atomic status-record lock | Accepted (Ardra Arun, 2026-10-13) |
| ADR-003 | Azure OpenAI and MySQL as the only external dependencies for data and LLM work | Accepted (Ardra Arun, 2026-10-13) |

Files: `docs/architecture/adr-001-flask-web-service-and-ui-layout.md`, `docs/architecture/adr-002-refresh-worker-and-lock.md`, `docs/architecture/adr-003-azure-openai-and-mysql.md`.

## Options considered (summary)

See the table under Logical topology. Recommended: option B for the worker, the single Flask web service for the application, and the module layout in `config.yaml`.

## Known risks

| ID | Risk | Owner | Mitigation / condition |
|----|------|-------|------------------------|
| RISK-A1 | **No authentication.** The UI and all routes, including `POST /api/refresh` (which starts a pipeline run and calls paid LLM and search APIs), are open to anyone who can reach the server. Accepted for this build for parity with the existing app (DQ-A1 answer). | Owner (to be named) | **Add authentication before the tool is exposed beyond a trusted network.** Until then, keep it on a trusted network only. |

### Planning constraints (from owner answers)

- The sprint plan must **not** include a login, JWT or session slice.
- The sprint plan must **not** include infra, Terraform, deployment or CI/CD slices. `modules.infra` is not used.
- The optional Azure WebJob trigger is kept exactly as FR-039 states: it is used only when `AZURE_WEBJOB_TRIGGER_URL` is set in `.env`; otherwise the worker runs as a subprocess.
- The LLM client sends only request parameters that the configured deployment supports. The tool must not send `temperature` or `max_tokens` settings that the deployment rejects. A unit test must confirm that the client builds a valid request.
- The first real refresh must not run until the Azure OpenAI approval gate (DQ-A5) is recorded.

## Open gaps

| DQ ID | Gap | Owner | Blocking |
|-------|-----|-------|----------|
| DQ-A1 | **ANSWERED** (BRD DQ-020): no authentication for this build (parity with the existing app). Recorded as RISK-A1: add authentication before wider exposure. | Owner (to be named) | no |
| DQ-A2 | **ANSWERED** (BRD DQ-021): local only (Flask on port 5000, local MySQL, `scripts/run-local-stack.sh`). Cloud target not decided; out of scope for this sprint. | Owner (to be named) | no |
| DQ-A3 | **RESOLVED** (Blocking = no). The chat model is whatever `AZURE_OPENAI_CHAT_DEPLOYMENT` names. The owner sets that value in `.env` and `.env.example`. No model name is written in the BRD, this proposal or the ADRs. The client must send only parameters the deployment supports (see Planning constraints). | Owner | no |
| DQ-A4 | **ANSWERED:** if the web process restarts while a worker runs, the worker finishes and clears its own running flag. If the worker dies, the 70-minute stale-lock rule (BR-016) clears the flag. No supervisor is added. | Owner (to be named) | no |
| DQ-A5 | **ANSWERED, with an approval gate.** News content is Public; status records are Internal. Article text sent to Azure OpenAI is public news with no personal data. **Approved:** the Azure OpenAI resource for this use was approved by Ardra Arun on 2026-10-13. The gate is cleared, so the first real refresh is no longer blocked by DQ-A5. | Owner | no |
| DQ-A6 | **ANSWERED:** SQLAlchemy 2.x and Alembic, per techstack.md. Alembic creates the `new_data` and `refresh_status` tables if they are missing. | Owner (to be named) | no |

## Assumptions

- ASSUMPTION-ARCH-001: a single web process and a single worker run at a time, since BR-015 allows one refresh at a time. Source: BRD BR-015. Pending approval.
- ASSUMPTION-ARCH-002: the optional WebJob path is not used unless the environment variable is set. Source: BRD FR-039 (DQ-012 answer). Pending approval.

Assumptions are pending approval and do not make the proposal Ready (rule 22).

## Implementation bindings (proposal only; not written to `config.yaml`)

Suggested bindings for downstream use, unchanged from the current config except where noted:

```yaml
modules:
  api: "modules/api"
  ui: "modules/ui"
  openapi: "contracts/openapi/ai-news-agent-v1.yaml"
local_stack:
  api_health_url: "http://localhost:5000/health"
  ui_health_url: "http://localhost:5000/"
```

These match the current `.claude/config.yaml`. No change is proposed.

## Approval

| Reviewer | Date | Status |
|----------|------|--------|
| Ardra Arun | 2026-10-13 | Accepted |

**Output path:** `docs/architecture/2026-10-13-architecture-proposal.md`
