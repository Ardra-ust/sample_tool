# Agent Audit — /implement-api — SP-02 (refresh start, lock, worker, stale lock)

> Aligns with `docs/harness/progress.md`. No secrets, credentials, or PHI/PII.

| Field | Value |
|-------|-------|
| **Date** | 2026-10-13 |
| **Command / Agent** | /implement-api (backend-agent; api-agent gate 2; run inline) |
| **Sprint item** | SP-02 (plan: `artifacts/sprints/S1-plan.md`, Approved by Ardra Arun, 2026-10-13) |
| **Requirements** | FR-035, FR-036, FR-039, FR-040; BR-015, BR-016; NFR-004; AC-002, AC-004, AC-005 |
| **Iteration** | 1 of 3. Behaviour checked; no refine needed. |
| **Outcome** | **Partial.** Code and contract verify done. Saved tests not written: test-case gates missing. Not Done. |

## What
- `app/repositories/refresh_status.py`: the status row; atomic lock by a conditional UPDATE (BR-015); stale clear for locks held over the limit (BR-016); finish writes (FR-040). Table name checked as an identifier; values bound as parameters.
- `app/services/refresh.py`: start order (clear stale, take lock, start worker); failure path (FR-036); WebJob or subprocess (FR-039); worker entry logic; redaction of configured secrets in traces (NFR-006).
- `app/routes/refresh.py`: `POST /api/refresh` (200 `started` or `running`; 500 with empty body on failure).
- `app/routes/health.py` (moved from `main.py`, same behaviour); `app/factory.py` (`create_app`); `app/main.py` now calls the factory.
- `app/db.py`: MySQL engine from settings (no connection at import).
- `refresh_worker.py` (modules/api): subprocess entry point.
- `artifacts/test-results-2026-10-13-sp02.md`: real results of the throwaway checks.
- This audit file.
- Not written: saved tests, `docs/test-cases*.md`, `docs/test-matrix.md`, the test package.

## Why
- SP-02 is the refresh start, lock, worker, and stale-lock item of the approved sprint plan.

## How
- Checks ran as a throwaway script, outside the repo. The database was an in-memory SQLite copy of the status table, so the conditional-update SQL ran unchanged. Network, LLM and subprocess calls were replaced with fakes.
- Contract verify: `POST /api/refresh` against `contracts/openapi/ai-news-agent-v1.yaml`. Spec validated; the response shapes match.
- Existing pytest suite: 16 passed.
- Rules: 02 (secrets from settings, redacted in traces); 03 (layering: route, service, repository); 05 (contract); 14 (no DDL added here; the migration is SP-01's); 22 (no invented copy: the start message is NULL; the stale message comes from BR-016; the failure and completion texts are plain status text, listed under Choices made).

### Choices made (for review)
- `last_run_type` is left NULL because OQ-API-2 is open.
- The 500 body is empty because OQ-API-1 is open.
- The WebJob request timeout is 30 seconds (`WEBJOB_TIMEOUT_SECONDS`). The sources give no value.
- Status message texts: "Refresh could not be started." (failure), "Refresh completed." and "Refresh failed." (worker). The BRD asks for a failure record and a completion message but gives no wording. Owner to confirm wording.
- The worker's pipeline is a stub that raises `NotImplementedError` until SP-04 to SP-08 are built. Every worker run therefore records a failure until then. This is intended.

## Conventions compliance (stack-conventions.md, Python + Flask)
- Layering: `routes/` (Blueprint), `services/` (orchestration), `repositories/` (SQL). `schemas/` and `models/` not needed for this slice.
- OpenAPI alignment: `POST /api/refresh` matches the contract.
- No secrets in code: database and integration settings come from `.env` through `app/config.py` (python-dotenv).

## Validation
| Check | Result |
|-------|--------|
| Plan Approved | PASS |
| Second start returns running (AC-002) | PASS |
| Stale lock cleared at 70 minutes, not at 69 (AC-005) | PASS |
| Completed run clears flag, sets finished_at and message (AC-004) | PASS |
| Failure records, releases lock, returns 500 (FR-036) | PASS |
| Contract verify | PASS |
| Existing tests | 16 passed |
| Saved tests written | NO (gates) |
| test-cases docs and br-coverage PASS | FAIL (missing) |
| Test package approved | FAIL (missing) |

## Open items
- **Secrets path:** the arguments asked for `modules/api/.env`. `.env` is at the repo root and `app/config.py` reads it there (SP-01). Confirm which location you want. Moving the file or the path in `config.py` is a change to SP-01.
- **Test gates:** `/expand-test-coverage` must write the test-case package; a human must approve it; br-coverage must PASS. Only then can saved SP-02 tests (mocked network and LLM) be written.
- **Status wording:** owner to confirm the three message texts.
- **OQ-API-1, OQ-API-2:** error body and `last_run_type` values (contract open questions).
- **Pipeline:** SP-04 to SP-08 supply the real worker pipeline.

## Next command
`/implement-api` for SP-03 (read routes: `GET /api/news`, `GET /api/refresh/status`), per the plan order. Test gates remain open.

**Output path:** `artifacts/audit/2026-10-13-implement-api-SP-02.md`
