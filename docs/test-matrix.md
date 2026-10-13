# Test Matrix — ai-news-agent (S1, BRD v0.2)

> Index only. Case bodies are in `docs/test-cases.md`. Coverage is scored in `docs/test-cases-br-coverage.md` by br-coverage-validator. Scripts exist under `modules/api/tests/`; status and last_result are from the 2026-10-13 `/run-tests` run.

| Field | Value |
|-------|-------|
| **Scope** | S1 backend slice (SP-01 to SP-03, SP-02, SP-09/10) and the LLM relevance stages; BRD v0.2 |
| **Cases file** | `docs/test-cases.md` |
| **Coverage file** | `docs/test-cases-br-coverage.md` |
| **Last updated** | 2026-10-13 |

## Matrix

| case_id | title | rule_ids (FR/BR/NFR) | AC | layer | type (+/-) | status | script_path | last_result |
|---------|-------|----------------------|----|-------|------------|--------|-------------|-------------|
| TC-001 | RSS feeds: per-feed entry limits | FR-001, FR-010 | — | integration | positive | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-002 | RSS: English only; summary cut lengths | FR-002, FR-003 | — | integration | positive, negative | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-003 | Google News: query form, entry limits, boost, decoded links | FR-004, FR-005, FR-006, BR-009 | — | integration | positive | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-004 | SearchAPI.io request parameters | FR-007 | — | integration | positive | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-005 | Tavily: one search, valid date, link and English filter | FR-008, FR-009 | — | integration | positive, negative | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-006 | One failing source is skipped; run continues | FR-010 | AC-017 | integration | negative | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-007 | Consumer-noise filter: block and allow words | FR-011 | — | IT | positive, negative | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-008 | Stage 3 title re-check and never-restore words | FR-012, BR-014 | — | integration | positive, negative | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-009 | De-duplication by link then title; cap of 500 | FR-013 | — | integration | positive, negative | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-010 | Stage 5 relevance gate: keep, drop, force-keep | FR-014, BR-017 | — | integration | positive, negative | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-011 | Relevance gate failure keeps the batch | FR-015 | — | integration | negative | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-012 | Embedding near-duplicate removal and title pass | FR-016, BR-011 | AC-020 | IT | positive, negative | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-013 | Database comparison: 0.84 drop, merge, 0.82 pass; DB failure | FR-017, FR-018, BR-011 | — | integration | positive, negative | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-014 | Freshness: 15-day cut, invalid date, cap of 400 | FR-019, BR-012, BR-013 | AC-001, AC-010, AC-011 | IT | positive, negative | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-015 | Deal-type tagging: six types, main-subject rule, failure | FR-020, BR-004, BR-005, BR-006 | — | integration | positive, negative | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-016 | Domain, priority and summary: classification, Unknown fallback, priority cap | FR-021, BR-001, BR-002, BR-003, BR-007, BR-008, BR-010 | AC-006 | integration | positive, negative | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-017 | Priority boosts: Google News +1, deal +1, cap 5 | BR-009, BR-010 | AC-007, AC-008 | IT | positive, negative | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-018 | Sort: priority high to low, then newest published | FR-022, BR-018 | AC-009 | IT | positive | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-019 | Save one snapshot per refresh; nothing fetched saves nothing | FR-023 | AC-018 | integration | positive, negative | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-020 | Pipeline stage order and no overlap | FR-045 | AC-022 | integration | positive | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-021 | Article fields; is_deal_news and published_at | FR-024, FR-025 | AC-019 | IT | positive | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-022 | Relative dates to absolute IST; summary fragments removed | FR-025, NFR-003 | — | IT | positive | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-023 | GET /api/news: shape, empty snapshot, no-cache | FR-034, NFR-002, AC-012 | AC-012 | api | positive | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-024 | GET /health returns OK | FR-038 | AC-003 | api | positive | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-025 | POST /api/refresh: started, then running (one refresh at a time) | FR-035, BR-015 | AC-002 | api | positive, negative | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-026 | Refresh start failure: HTTP 500 and failure recorded | FR-036 | — | api | negative | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-026a | Stale lock: cleared after 70 minutes, not before | BR-016, NFR-004 | AC-005 | IT | positive, negative | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-027 | GET /api/refresh/status: shape and no-cache | FR-037, NFR-002 | — | api | positive | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-028 | Worker start: subprocess by default; WebJob only when URL is set | FR-039 | — | integration | positive | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-029 | Worker finish: running flag cleared; message or trace written | FR-040 | AC-004 | integration | positive, negative | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-030 | Starting the app does not fetch news | FR-041 | — | api | positive | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-031 | Settings read from .env; no hardcoded secret | FR-042, NFR-001 | — | IT | positive | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-032 | Status file fallback when the database is unavailable (development only) | FR-043 | — | IT | positive | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-033 | Status row created with "Ready" when missing | FR-044 | — | integration | positive | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-034 | Snapshots and status stored in database news_app | FR-044, FR-023 | — | integration | positive | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-035 | Index page: title, footer, no Insight controls | FR-026, FR-032, FR-033 | — | uat | positive, negative | passed | modules/api/tests/test_ui_cases.py | 2026-10-13 run-tests: pass |
| TC-036 | Sort control: two options | FR-027 | — | uat | positive | passed | modules/api/tests/test_ui_cases.py | 2026-10-13 run-tests: pass |
| TC-037 | Domain filter: All and five domains | FR-028 | AC-013 | uat | positive, negative | passed | modules/api/tests/test_ui_cases.py | 2026-10-13 run-tests: pass |
| TC-038 | Deal-type filter: six chips with counts; Clear filter | FR-029 | AC-014 | uat | positive | passed | modules/api/tests/test_ui_cases.py | 2026-10-13 run-tests: pass |
| TC-039 | Refresh button: message, polling, reload | FR-030 | AC-016 | uat | positive | passed | modules/api/tests/test_ui_cases.py | 2026-10-13 run-tests: pass |
| TC-040 | Empty state "No news found" | FR-031 | AC-015 | uat | positive | passed | modules/api/tests/test_ui_cases.py | 2026-10-13 run-tests: pass |
| TC-041 | Load failure shows the connection message | NFR-007 | — | uat | negative | passed | modules/api/tests/test_ui_cases.py | 2026-10-13 run-tests: pass |
| TC-043 | Secrets masked in traces and logs | NFR-006 | — | IT | negative | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-044 | Backend line coverage gate at 70% | NFR-008 | AC-021 | IT | positive, negative | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-045 | Parity check: reported only against a complete baseline | NFR-005 | AC-023 | IT | positive, negative | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-045b | Parity baseline values recorded by the owner | NFR-005 | AC-023 | blocked | positive | skipped | — | 2026-10-13 run-tests: skip |
| TC-046 | HTML stripped from feed summaries | NFR-009 | — | IT | positive, negative | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |
| TC-047 | No authentication in this build (recorded risk) | NFR-010, FR-035 | — | api | positive | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-048 | Prompts stored verbatim as templates | FR-046 | AC-024 | IT | positive, negative | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-049 | Relevance judged for an IT services company (stages 3 and 5) | FR-048 | — | IT | positive | passed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: pass |
| TC-050 | LLM calls use supported parameters per stage | FR-047 | — | IT | positive, negative | failed | modules/api/tests/test_backend_cases.py | 2026-10-13 run-tests: fail |

## Status definitions

| Status | Meaning |
|--------|---------|
| designed | In test-cases.md; no script yet |
| scripted | Automation exists |
| pass / fail | Last run result |

## Roll-up

| Layer | Designed | Scripted | Pass |
|-------|----------|----------|------|
| api | 7 | 0 | 0 |
| IT | 17 | 0 | 0 |
| integration | 19 | 0 | 0 |
| uat | 7 | 0 | 0 |
| blocked | 1 | 0 | 0 |
| **Total** | 51 | 0 | 0 |

**Output path:** `docs/test-matrix.md`
