# Test Results — /run-tests — S1 (approved package)

> From `/run-tests`. Real counts from the run. Package: `docs/quality/test-package-review.md` (Approved, Ardra Arun, 2026-10-13). Coverage gate: `docs/test-cases-br-coverage.md` (PASS, 100%).

| Field | Value |
|-------|-------|
| **Run ID** | TR-20261013-S1-run-tests |
| **Timestamp** | 2026-10-13 (local) |
| **Environment** | Windows, Python 3.13.2, pytest 9.1.1, pytest-cov 7.1.0, SQLAlchemy 2.0.44 (SQLite in-memory copy of the tables for the backend cases), Microsoft Edge with Python Playwright (UI cases). No network and no LLM calls. |
| **Commands** | `cd modules/api && python -m pytest -q --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml` (backend and UI cases together); UI only: `python -m pytest tests/test_ui_cases.py` |
| **Branch** | fill-config-ai-news-agent (uncommitted working tree) |
| **Agent** | backend-agent and frontend-agent (scripts written inline) |

## Summary

| Suite (execution_layer) | Total | Pass | Fail | Skip | Verdict |
|-------------------------|-------|------|------|------|---------|
| Backend unit / IT / integration (api, IT, integration) | 66 | 42 | 23 | 1 | Fail (stages not built) |
| UI (uat, Playwright) | 7 | 7 | 0 | 0 | Pass |
| **Total** | **73** | **49** | **23** | **1** | — |

Cases with no failure: TC-008, TC-010, TC-011, TC-023 to TC-031, TC-033, TC-034, TC-043, TC-044, TC-047, TC-048, TC-049, TC-035 to TC-041. (TC-050 is partly covered: the stage 3 and 5 parameters pass, the stage 9 and 10 parameters fail; see Failures.)

## Failures (23)

| Case(s) | Test | Error | Root cause (see defect file) |
|---------|------|-------|-------------------------------|
| TC-001, TC-002 | `test_stage_not_built[TC-001/002]` | ModuleNotFoundError: app.pipeline.fetch_rss | SP-04 not built |
| TC-003 | `test_stage_not_built[TC-003]` | ModuleNotFoundError: app.pipeline.fetch_google_news | SP-04 not built |
| TC-004 | `test_stage_not_built[TC-004]` | ModuleNotFoundError: app.pipeline.fetch_searchapi | SP-04 not built |
| TC-005 | `test_stage_not_built[TC-005]` | ModuleNotFoundError: app.pipeline.fetch_tavily | SP-04 not built |
| TC-006 | `test_stage_not_built[TC-006]` | ModuleNotFoundError: app.pipeline.fetch_all | SP-04 not built |
| TC-007 | `test_stage_not_built[TC-007]` | ModuleNotFoundError: app.services.noise | SP-05 not built |
| TC-009, TC-012, TC-013 | `test_stage_not_built[...]` | ModuleNotFoundError: app.services.dedupe | SP-05 / SP-07 not built |
| TC-014 | `test_stage_not_built[TC-014]` | ModuleNotFoundError: app.services.freshness | SP-08 not built |
| TC-015 | `test_stage_not_built[TC-015]` | ModuleNotFoundError: app.services.deal_tagging | SP-06 (stage 9) not built |
| TC-016 | `test_stage_not_built[TC-016]` | ModuleNotFoundError: app.services.classify | SP-06 (stage 10) not built |
| TC-017 | `test_stage_not_built[TC-017]` | ModuleNotFoundError: app.services.priority | SP-06 not built |
| TC-018 | `test_stage_not_built[TC-018]` | ModuleNotFoundError: app.services.sort | SP-08 not built |
| TC-019 | `test_stage_not_built[TC-019]` | ModuleNotFoundError: app.services.snapshot | SP-08 not built |
| TC-020 | `test_stage_not_built[TC-020]` | ModuleNotFoundError: app.pipeline.runner | SP-08 not built |
| TC-021 | `test_stage_not_built[TC-021]` | ModuleNotFoundError: app.services.article | SP-04 / SP-08 not built |
| TC-022 | `test_stage_not_built[TC-022]` | ModuleNotFoundError: app.services.dates | SP-04 not built |
| TC-032 | `test_stage_not_built[TC-032]` | ModuleNotFoundError: app.services.status_fallback | Not in any SP; FR-043 needs a backlog item |
| TC-045 | `test_stage_not_built[TC-045]` | ModuleNotFoundError: app.evals.parity | Parity check not built |
| TC-046 | `test_stage_not_built[TC-046]` | ModuleNotFoundError: app.services.text_clean | SP-04 (NFR-009) not built |
| TC-050 (stages 9 and 10) | `test_tc050_stage9_and_stage10_parameters` | ModuleNotFoundError: app.services.deal_tagging / classify | SP-06 not built |

## Skipped (1)

| Case | Test | Reason |
|------|------|--------|
| TC-045b | `test_tc045b_parity_baseline_recorded` | blocked: owner must record `evals/product/baseline.md` (DQ-019). Recorded as skipped, not passed. |

## Coverage (Phase 3, `pytest --cov=app`)

| Module | Line % | Floor 70% |
|--------|--------|-----------|
| app/config.py | 100% | Met |
| app/llm/prompts.py | 100% | Met |
| app/llm/stages.py | 89% | Met |
| app/repositories/news_snapshot.py | 100% | Met |
| app/repositories/refresh_status.py | 97% | Met |
| app/routes/refresh.py | 96% | Met |
| app/routes/news.py | 93% | Met |
| app/routes/health.py | 100% | Met |
| app/routes/pages.py | 100% | Met |
| app/services/refresh.py | 93% | Met |
| app/services/news.py | 92% | Met |
| app/services/relevance.py | 94% | Met |
| app/factory.py | 79% | Met |
| app/db.py | 85% | Met |
| app/main.py | 0% (boot file only, 2 statements) | Not evaluated per module; excluded from the decision |
| **Total** | **93%** (405 statements, 28 missed) | **Met** (floor 0.70) |

## UI results (uat, 7 cases, all pass)

| Case | Result |
|------|--------|
| TC-035 index title, footer, no Insight controls | Pass |
| TC-036 sort options and date order | Pass |
| TC-037 domain filter: All and five domains | Pass |
| TC-038 deal chips with counts; Clear filter | Pass |
| TC-039 refresh message, polling, reload | Pass |
| TC-040 empty state "No news found" | Pass |
| TC-041 load failure message | Pass |

## Deviations from the package

- The config names `npx playwright test`. The UI cases run through Python Playwright with Microsoft Edge instead, because the Node Playwright package is not installed and the network blocks installing it. The cases and checks are unchanged.
- The UI run uses fake snapshot data. No real refresh was run, so the first real refresh is still gated by DQ-A5 (approval recorded).
- Two test-file defects found during the run were corrected before the final run: TC-048 used an edit that changed nothing, and TC-026 did not configure the secret for redaction. Both were test errors, not product changes.

## Artifacts

| Type | Path |
|------|------|
| Backend and UI tests | `modules/api/tests/test_backend_cases.py`, `modules/api/tests/test_ui_cases.py`, `modules/api/tests/conftest.py` |
| Coverage XML | `modules/api/coverage.xml` |
| Defect analysis | `artifacts/issues/2026-10-13-run-tests-defects.md` |
| Audit | `artifacts/audit/2026-10-13-run-tests-S1.md` |
