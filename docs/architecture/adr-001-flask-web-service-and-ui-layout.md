# ADR-001 — Flask single web service with Jinja UI from `modules/ui`

> Architecture Decision Record. Status **Accepted** by Ardra Arun on 2026-10-13 (human architecture review).

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-001 |
| **Status** | Accepted — Ardra Arun, 2026-10-13 |
| **Date** | 2026-10-13 |
| **Deciders** | (to be named) |
| **Consulted** | Operator (stack statement in the command arguments) |
| **Command / trigger** | `/propose-architecture` |
| **Supersedes** | N/A |
| **Superseded by** | N/A |

## Context

- **Problem statement:** Which web framework serves the JSON routes and the pages, and where do the templates live?
- **Business / technical drivers:** BRD §4.1 (Flask, Jinja templates, plain HTML/JS, single web service); FR-026–FR-037 (pages and JSON routes); FR-041 (web start does not fetch news).
- **Current state:** Repository has `modules/api` and `modules/ui` configured in `.claude/config.yaml`. The Flask app package exists in `modules/api/app`, and its `template_folder` and `static_folder` point at `modules/ui`.
- **Constraints:** Stack is Python 3.11+ with Flask (operator). No Java or Next.js (operator). Module roots are fixed by `config.yaml`.
- **Assumptions:** ASSUMPTION-ARCH-001 (one web process at a time).

## Decision

- **Chosen option:** One Flask service (`modules/api`, package `app`) that serves the JSON routes in BRD §8 and renders pages from Jinja templates in `modules/ui/templates`. Static files come from `modules/ui/static`. The UI is not a separate application.
- **Alternatives considered:**

| Option | Pros | Cons | Rejected because |
|--------|------|------|------------------|
| A. Flask serves JSON and Jinja pages from one process (chosen) | One deployable for the web tier; matches operator stack; no build step for the UI | Page logic and JSON share one process | — |
| B. Flask JSON API with a separate client-side SPA | Independent UI deployment | Needs a JS framework and build step; the BRD requires server-rendered Jinja (§4.1) | Conflicts with the stated stack |
| C. Separate UI server | Independent UI scaling | Adds a deployable with no driver | No driver in BRD |

- **Rationale:** Option A is the only option that matches the operator's stack and the BRD §4.1 architecture line without adding deployables.

## Consequences

### Positive

- One web process to run locally on port 5000 (BRD §8).
- No JavaScript build chain is needed. Plain JS handles sort, filter and polling.

### Negative / trade-offs

- Page and JSON code share a process; any heavy work must stay in the worker (see ADR-002).

### Neutral

- Template and static folders live outside the Flask package, so the app sets `template_folder` and `static_folder` explicitly.

## Implementation notes

| Area | Impact | Owner | Target |
|------|--------|-------|--------|
| API / contracts | JSON routes listed in BRD §8; OpenAPI spec is the source of truth | api-agent / backend-agent | `/implement-api` |
| UI | Templates and static under `modules/ui`; backend-agent may write them for a backend slice (scope.yaml) | frontend-agent | `/implement-ui` |
| Data / migrations | Not covered by this ADR (see ADR-003) | — | — |
| Infra / CI | None for this build (DQ-A2 answer): local only, `scripts/run-local-stack.sh` | — | — |
| Tests | pytest for API and route tests; Flask test client for templates; Playwright for E2E | test-agent | `/expand-test-coverage` |
| Documentation | `docs/architecture/stack-conventions.md` already describes this layout | documentation-agent | — |

## Compliance and security

- **AuthN/Z impact:** None for this build (DQ-A1 answer). All routes are open. Known risk RISK-A1: add authentication before wider exposure.
- **Data classification impact:** Public news content; status records Internal (DQ-A5 answer).
- **Audit logging impact:** Log masking applies (NFR-006).

## Validation

| Check | Result | Evidence |
|-------|--------|----------|
| Aligns with BRD/NFR | Yes | BRD §4.1, FR-026–FR-037, FR-041 |
| Reviewed by architect/SME | Pending | — |
| Rollback path documented | Yes | Serve the same routes from one process; no data migration involved |

## References

| Ref | Locator |
|-----|---------|
| BRD | `artifacts/brd/ai-news-agent-BRD-draft.md` §4.1, §8, §10 |
| Related ADR | ADR-002, ADR-003 |
| Proposal | `docs/architecture/2026-10-13-architecture-proposal.md` |
