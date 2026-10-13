# Agent Audit — /implement-api (SP-03) then /implement-ui (SP-09, SP-10)

> Aligns with `docs/harness/progress.md`. No secrets, credentials, or PHI/PII.

| Field | Value |
|-------|-------|
| **Date** | 2026-10-13 |
| **Command / Agent** | /implement-api for SP-03 (backend-agent; api-agent gate 2); /implement-ui for SP-09 and SP-10 (frontend-agent; flask-template-generator; run inline) |
| **Plan** | `artifacts/sprints/S1-plan.md`, Approved (Ardra Arun, 2026-10-13) |
| **Iteration** | 1 of 3 for each command. Browser check failed once (favicon 404), fixed; re-checked. |
| **Outcome** | SP-03 and SP-09/SP-10 **built and checked**. Not Done: saved test scripts and the test-case gates are still missing. |

## What
**SP-03 (API read routes):**
- `GET /api/news`: latest snapshot as `{count, results, fetched_at}`; empty gives `count` 0 and `results` []; no-cache header; 500 with empty body if the stored snapshot is not a JSON array. `app/repositories/news_snapshot.py`, `app/services/news.py`, `app/routes/news.py`.
- `GET /api/refresh/status`: `{running, started_at, finished_at, message, last_run_type}`; no-cache header; trace not returned. In `app/routes/refresh.py`.
- `app/db.py`: `check_identifier` for table names. `app/factory.py`: wires both new routes; `new_data` is the snapshot table.

**SP-09 and SP-10 (news grid):**
- `modules/ui/templates/index.html`: title "Latest Tech News" (FR-032), updated line, sort (FR-027), domain filter (FR-028), deal-type chips with counts and Clear filter (FR-029), Refresh News (FR-030), grid, "No news found" (FR-031), footer "Copyright 2025 UST" (DQ-009), empty icon link to avoid a favicon 404.
- `modules/ui/static/css/news.css`: layout and deal colours from BRD §6.3.
- `modules/ui/static/js/news.js`: wiring to `getNews`, `startRefresh`, `getRefreshStatus`; text inserted with `textContent` only; only http and https links are used as hrefs; "See more..." shown only on summaries that overflow; refresh shows "Refreshing news - this may take a while..." (BRD §10), polls until `running` is false, then reloads (FR-030, AC-016); load failure shows "No news loaded, check your connection" (owner copy).
- `app/routes/pages.py`: `GET /` renders the index. No business logic in the route.

## Why
- SP-03 is the read path the grid needs. SP-09 and SP-10 are the grid and its filters and refresh. The plan order (API before UI) was followed.

## How
- SQL checked against an in-memory SQLite copy of both tables (real repository SQL). Network, LLM and subprocess calls faked.
- Browser check: Flask served on localhost with fake data; Microsoft Edge via Playwright; checks run as a throwaway script, not saved.
- Contract: the three paths used by the page are contract operations (`/api/news`, `/api/refresh`, `/api/refresh/status`).

## Validation
| Check | Result | Evidence |
|-------|--------|----------|
| Plan Approved | PASS | Plan header |
| SP-03 empty snapshot (AC-012) | PASS | `count` 0, `results` [] |
| SP-03 snapshot shape and time format | PASS | count, fetched_at `YYYY-MM-DD HH:MM:SS` |
| SP-03 bad stored snapshot → 500, no body | PASS | Returns empty body |
| SP-03 status shape; no-cache on both routes | PASS | Headers checked |
| Page title, footer, updated line (FR-032, DQ-009, FR-034) | PASS | Browser |
| Six deal chips with counts; filter; Clear filter (AC-014) | PASS | Browser |
| Domain filter (AC-013) | PASS | Browser: Retail shows 1 of 4 |
| Sort by date and priority (FR-027) | PASS | Browser |
| "See more..." only where cut (owner answer) | PASS | Browser |
| `javascript:` link not used as href; HTML shown as text | PASS | Browser |
| No Insight UI (FR-033, AC-020) | PASS | Browser |
| Empty state "No news found" (AC-015, FR-031) | PASS | Browser |
| Load failure copy | PASS | Browser |
| Refresh message, disabled button, poll, reload (AC-016, FR-030) | PASS | Browser |
| No console errors on load | PASS (after favicon fix) | Browser |
| Existing pytest suite | 16 passed | pytest |
| Saved test scripts (UI and SP-03) | NO | Gates missing |

## Not built, on purpose
- **Blue marker for IT-services-aligned news:** not built. The rule for "aligned" is undefined and may be the out-of-scope UST alignment feature (BRD §2, FR-033). Owner must define it.
- **Logo:** not built. `[Logo]` placeholder kept (owner: proceed without). No logo file in the repo.
- **Loading state:** an indicator bar with no text. The owner has not supplied loading wording (UD-04).
- **Refresh start failure copy:** no copy for a failed start (contract gives none; open item UD-06). The button is re-enabled and the notice cleared.
- **Priority number on cards:** not shown; owner has not confirmed it.

## Conventions and scope
- Python Flask: `routes/` (Blueprints), `services/`, `repositories/`, `factory.py`; `templates/` and `static/` under `modules/ui` (stack-conventions.md).
- FE↔BE wiring gate: the three contract operations are used; response shapes follow the spec.
- Scope: UI files written only under `modules/ui`; backend files under `modules/api`.

## Open items
- **Test gates (blocking the DoD):** `docs/test-cases.md`, `docs/test-matrix.md`, `docs/test-cases-br-coverage.md` (PASS), `docs/quality/test-package-review.md` (approved). Saved UI and SP-03 tests cannot be written until these exist.
- **Owner:** blue-marker "aligned" rule and scope confirmation; logo file and permission; loading wording (UD-04); refresh-start failure copy (UD-06); status message wording (SP-02); OQ-API-1 (500 error body) and OQ-API-2 (`last_run_type`).
- **Pipeline:** SP-04 to SP-08 build the data the grid shows. Until then the grid shows "No news found" with an empty snapshot.
- **Secrets path:** `.env` is at the repo root (SP-01 decision); the request asked for `modules/api/.env`.

## Next command
`/expand-test-coverage` (test-case package for SP-02, SP-03, SP-09, SP-10). Then approval by Ardra Arun before `/run-tests`.

**Output path:** `artifacts/audit/2026-10-13-implement-ui-SP-09-SP-10.md`
