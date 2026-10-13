# Test Results — SP-02 (refresh start, lock, worker, stale lock)

> From `/implement-api`. Real counts only. Partial: the test-case gates are not met, so no saved test scripts were written (see Gaps).

| Field | Value |
|-------|-------|
| **Run ID** | TR-20260513-SP02 |
| **Timestamp (local)** | 2026-10-13 |
| **Environment** | local, Windows, Python 3.13.2; SQLite in-memory copy of the status table; all network, LLM and subprocess calls replaced with fakes |
| **Command** | /implement-api (SP-02) |
| **Agent** | backend-agent (contract verify by api-agent, run inline) |

## Summary

| Check (requirement) | Result |
|---------------------|--------|
| Second start returns `running`; no second worker launch (BR-015, AC-002) | Pass |
| Lock held 69 min is not cleared; 72 min is cleared and start proceeds (BR-016, AC-005) | Pass |
| Stale clear writes the BR-016 message "Worker likely died; stale lock cleared." (BR-016) | Pass |
| Completed run clears running, sets finished_at and message "Refresh completed." (FR-040, AC-004) | Pass |
| Failed start records the failure, releases the lock, and raises for HTTP 500 (FR-036) | Pass |
| Failure trace has the configured secret redacted (NFR-006) | Pass |
| `POST /api/refresh` returns 200 `{"status":"started"}` then `{"status":"running"}` | Pass |
| `POST /api/refresh` failure returns 500 with an empty body | Pass |
| WebJob used only when `AZURE_WEBJOB_TRIGGER_URL` is set; no subprocess then (FR-039) | Pass |
| Worker success exits 0 and clears the flag (FR-040) | Pass |
| Worker with the unimplemented pipeline exits 1, clears the flag, trace names SP-04 (FR-040) | Pass |
| Invalid `REFRESH_STATUS_TABLE` value rejected | Pass |
| Existing pytest suite (SP-01 config tests) | 16 passed, 0 failed |

Checks were run as a throwaway script. Nothing was saved as a test.

## Contract verify (api-agent gate 2)

| Check | Result |
|-------|--------|
| `POST /api/refresh` responses are 200 and 500 | Pass |
| 200 body is `application/json` `RefreshStartResponse` (status `started` or `running`) | Pass |
| 500 body | Empty; the contract leaves the error body open (OQ-API-1) |
| Spec validates under OpenAPI 3.1 | Pass |

## Gaps

| Gap | Effect |
|-----|--------|
| `docs/test-cases.md`, `docs/test-matrix.md`, `docs/test-cases-br-coverage.md` missing | No case IDs; saved test scripts are refused |
| `docs/quality/test-package-review.md` missing | `/run-tests` cannot start |
| Worker pipeline stages not built (SP-04 to SP-08) | Every real worker run ends with "Refresh failed." until the pipeline exists |
| `.env` is at the repo root; the item asked for `modules/api/.env` | Settings still read the repo-root file (see audit) |
| Route `/api/refresh/status` (SP-03) not built | Status is written to the database but not yet served |

## Artifacts

| Type | Path |
|------|------|
| Lock and repository | `modules/api/app/repositories/refresh_status.py` |
| Start and worker logic | `modules/api/app/services/refresh.py` |
| Route | `modules/api/app/routes/refresh.py` |
| Worker entry point | `modules/api/refresh_worker.py` |
| Contract | `contracts/openapi/ai-news-agent-v1.yaml` |
