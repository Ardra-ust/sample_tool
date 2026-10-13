# Sprint Plan — Sprint S1 (AI News Agent)

> From `/plan-sprint`. Status: **Approved** by Ardra Arun on 2026-10-13 (human approval). Agents did not approve this plan.

| Field | Value |
|-------|-------|
| **Sprint** | S1 |
| **Dates** | 2026-10-13 – 2026-10-26 (2 weeks; proposed, owner to confirm) |
| **Goal** | Build the full AI News Agent |
| **BRD ref** | `artifacts/brd/ai-news-agent-BRD-draft.md`, status **Accepted** (Ardra Arun, 2026-10-13); recorded in `docs/harness/decisions.md` |
| **Status** | Approved — Ardra Arun, 2026-10-13 |
| **Planner** | planner-agent (mode sprint), run inline by orchestrator-agent |
| **Gap report** | `artifacts/sprints/S1-gap-report.md` |

## Goals

1. Working pipeline: fetch from all four source types, filter, dedupe, classify, store one snapshot per refresh, in the FR-045 order.
2. Working UI: news grid, sort, domain and deal-type filters, manual refresh with polling.
3. Working routes: `GET /api/news`, `POST /api/refresh`, `GET /api/refresh/status`, `GET /health`, with the worker subprocess and the optional WebJob path (FR-039).
4. Quality gates: backend line coverage ≥ 70%, and the parity check reported correctly (AC-023).

## Scope limits (from owner decisions; not to be planned)

- No login, JWT or session slice (DQ-020; RISK-A1).
- No infra, Terraform, deployment or CI/CD slice (DQ-021). `modules.infra` is not used.
- Local only: Flask on port 5000, local MySQL, `scripts/run-local-stack.sh`.
- The Azure WebJob is used only when `AZURE_WEBJOB_TRIGGER_URL` is set (FR-039).
- No real refresh runs until the Azure OpenAI approval is recorded (DQ-A5 gate).
- Snapshot rows are never deleted (DQ-016).

## Sprint backlog

Size: S, M, L (relative; no points are assigned because no capacity figures were given).

| SP ID | Title | Size | FR/BR/AC refs | Execute command(s) | Depends on | Owner agent |
|-------|-------|------|---------------|--------------------|------------|-------------|
| SP-01 | Foundation: configuration, dependencies, migrations, env template | M | FR-040 (config), FR-042, FR-043, FR-044, NFR-001 | /implement-api | G-04, G-06, G-07, G-08 | backend-agent, data-agent |
| SP-02 | Refresh start, lock, worker subprocess, status writes, stale lock, WebJob option | L | FR-035, FR-036, FR-039, FR-040, BR-015, BR-016, NFR-004, AC-002, AC-004, AC-005 | /implement-api | SP-01, G-05 | backend-agent |
| SP-03 | Read routes and health: `/api/news`, `/api/refresh/status`, `/health`, app boot, no-cache and IST | S | FR-034, FR-037, FR-038, FR-041, NFR-002, NFR-003, AC-001, AC-003, AC-012 | /implement-api | SP-01, G-05 | backend-agent |
| SP-04 | Source fetchers: RSS, Google News, SearchAPI.io, Tavily; per-source skip; article fields; HTML strip | L | FR-001–FR-010, FR-024, FR-025, NFR-009, AC-017 | /implement-api | SP-01, G-02 | backend-agent |
| SP-05 | Consumer-noise filter and link/title dedupe (max 500) | S | FR-011, FR-013, BR-014 (prerequisite for FR-012) | /implement-api | SP-04, G-03 | backend-agent |
| SP-06 | LLM stages: title re-check, relevance gate, deal tagging, domain/priority/summary, boosts, is_deal_news | L | FR-012, FR-014, FR-015, FR-020, FR-021, BR-001–BR-010, BR-014, BR-017, AC-006, AC-007, AC-008, AC-019 | /implement-api | SP-05, G-01, G-03, G-12 | backend-agent |
| SP-07 | Embedding near-duplicate removal, title pass, database comparison and merge | M | FR-016, FR-017, FR-018, BR-011, AC-020 | /implement-api | SP-05, SP-06 | backend-agent |
| SP-08 | Freshness, sort, save, FR-045 pipeline order, no empty snapshot | M | FR-019, FR-022, FR-023, FR-045, BR-012, BR-013, BR-018, AC-009, AC-010, AC-011, AC-018, AC-022 | /implement-api | SP-06, SP-07 | backend-agent |
| SP-09 | UI grid and index route: cards, page title, footer, no Insight UI, empty state | M | FR-026, FR-031, FR-032, FR-033, NFR-007 (empty and error states), G-15 | /implement-ui | SP-03 | frontend-agent |
| SP-10 | UI sort, domain and deal-type filters, refresh button with polling | M | FR-027, FR-028, FR-029, FR-030, NFR-007, AC-013, AC-014, AC-015, AC-016 | /implement-ui | SP-02, SP-03, SP-09 | frontend-agent |
| SP-11 | Quality gates: coverage ≥ 70%, log masking, parity check reporting, E2E setup | M | NFR-005, NFR-006, NFR-008, AC-021, AC-023 | /implement-api, /implement-ui | SP-08, SP-10, G-09, G-10 | backend-agent, frontend-agent |

Requirement NFR-010 (no authentication) has no SP. It is a recorded risk (RISK-A1), not a build task.

## Execute spine (locked)

Remaining steps after this plan is approved:

```text
/implement-api (SP-01 to SP-08, SP-11 backend) → /implement-ui (SP-09, SP-10, SP-11 UI)
  → /expand-test-coverage → [human: test-package Approved] → /run-tests → /run-eval
  → /close-eval-gaps (loop until fix queue clear) → /review-changes → /application-summary
```

`/run-eval` cannot report the parity check as passed until `evals/product/baseline.md` has all values (G-10). Without them it reports "not evaluated" (AC-023).

## Execution order

1. SP-01 (foundation) first; everything depends on it.
2. SP-02 and SP-03 in parallel once SP-01 and the OpenAPI spec (G-05) are in place.
3. SP-04, then SP-05, then SP-06 (LLM stages, blocked by G-01).
4. SP-07, then SP-08.
5. SP-09 after SP-03; SP-10 after SP-02 and SP-09.
6. SP-11 last.

## Technical dependencies

| Dependency | Type | Status | Blocker for |
|------------|------|--------|-------------|
| G-01: LLM prompts and output formats | Business content | Pending owner | SP-06 |
| G-02: feed list and query-string location | Design decision | Pending dev lead | SP-04 |
| G-03: noise and force-keep word lists location | Design decision | Pending dev lead | SP-05, SP-06 |
| G-04: dependency list and pinned versions | Build | Pending dev lead | SP-01 |
| G-05: OpenAPI spec `ai-news-agent-v1.yaml` | API contract | Pending api-agent | SP-02, SP-03 |
| G-06: `.env.example` | Config | Pending | SP-01 |
| G-07: migrations for `new_data` and `refresh_status` | Data | Pending | SP-01 |
| G-08: `.env` ignored by git | Repo hygiene | Pending | any commit |
| G-09: Playwright configuration | Test setup | Pending | SP-11 |
| G-10: baseline values in `evals/product/baseline.md` | Measurement | Pending owner | parity check (AC-023) only |
| G-11: Azure OpenAI approval recorded | Compliance gate | Pending approver | first real refresh only |
| G-12: supported request parameters for the chat deployment | Verification | Pending dev lead | SP-06 test |

## Traceability (forward)

| FR/BR/AC | Requirement summary | Design artifact | API (operationId) | UI (route/component) | Test case(s) | Status |
|----------|---------------------|-----------------|-------------------|----------------------|--------------|--------|
| FR-001–FR-010 | Source fetching and failure skip | BRD §5; notes §3 | — | — | TC to be written in `/expand-test-coverage` | Not started (SP-04) |
| FR-011, FR-013 | Noise filter; link/title dedupe | BRD §5 | — | — | TC pending | Not started (SP-05) |
| FR-012, FR-014, FR-015, FR-020, FR-021 | LLM stages | BRD §5; G-01 | — | — | TC pending | Blocked (SP-06, G-01) |
| FR-016–FR-018 | Embedding dedupe and DB comparison | BRD §5 | — | — | TC pending | Not started (SP-07) |
| FR-019, FR-022, FR-023, FR-045 | Freshness, sort, save, stage order | BRD §5 | — | — | TC pending (AC-022) | Not started (SP-08) |
| FR-024, FR-025 | Article fields and dates | BRD §5 | — | — | TC pending | Not started (SP-04) |
| FR-026–FR-033 | UI grid, sort, filters, refresh, empty state, footer | BRD §5, §10 | — | templates in `modules/ui` | TC pending | Not started (SP-09, SP-10) |
| FR-034, FR-037, FR-038 | Read routes and health | BRD §5, §8 | G-05 | — | TC pending | Not started (SP-03) |
| FR-035, FR-036, FR-039, FR-040 | Refresh start, failure, worker, status | BRD §5, §9 | G-05 | — | TC pending | Not started (SP-02) |
| FR-041 | App start does not fetch | BRD §5 | — | — | TC pending | Not started (SP-03) |
| FR-042–FR-044 | Config, DB status, MySQL storage | BRD §5, §7 | — | — | TC pending | Not started (SP-01) |
| BR-001–BR-010 | Domains, deal types, priority, boosts | BRD §6 | — | — | TC pending | Not started (SP-06, SP-08) |
| BR-011 | Dedup thresholds 0.75, 0.84, 0.82; title 0.92 | BRD §6 | — | — | TC pending (AC-020) | Not started (SP-07) |
| BR-012, BR-013, BR-018 | 15-day cut-off, 400/500 caps, sort | BRD §6 | — | — | TC pending | Not started (SP-08) |
| BR-014, BR-017 | Forbidden restore words; relevance drop rules | BRD §6 | — | — | TC pending | Not started (SP-05, SP-06) |
| BR-015, BR-016 | Atomic lock; 70-minute stale lock | BRD §6 | — | — | TC pending (AC-002, AC-005) | Not started (SP-02) |
| NFR-001 | Secrets from `.env` | BRD §10 | — | — | TC pending | Not started (SP-01) |
| NFR-002, NFR-003 | No-cache headers; IST | BRD §10 | — | — | TC pending | Not started (SP-03) |
| NFR-004 | Atomic lock and stale clearance | BRD §10 | — | — | TC pending | Not started (SP-02) |
| NFR-005 | Parity check (baseline) | BRD §10, DQ-019 | — | — | AC-023 | Not started (SP-11, G-10) |
| NFR-006 | Log masking | BRD §10 | — | — | TC pending | Not started (SP-11) |
| NFR-007 | Loading, empty and error UI states | BRD §10 | — | templates | TC pending | Not started (SP-09, SP-10) |
| NFR-008 | Backend line coverage ≥ 70% | BRD §10 | — | — | AC-021 | Not started (SP-11) |
| NFR-009 | Strip HTML from feed text | BRD §10 | — | — | TC pending | Not started (SP-04) |
| AC-001–AC-023 | Acceptance criteria | BRD §15 | — | — | `/expand-test-coverage` | Mapped above |

Coverage check: every FR-001–FR-045, BR-001–BR-018, and AC-001–AC-023 appears in at least one row. NFR-010 is a recorded risk, not a task.

## Risks

| Risk | Mitigation |
|------|------------|
| Two-week scope is large for eleven items with L sizes. No capacity figures were given. | Order by dependency; SP-06 and SP-04 are the critical path. Owner to confirm capacity before approval. |
| LLM prompts not supplied (G-01) block SP-06 and the LLM stages | Owner supplies prompts before SP-06 starts. Until then SP-06 is blocked, and SP-07 and SP-08 can be stubbed. |
| Supported chat request parameters unverified (G-12) | Verify against the deployment before SP-06 merges; the test in ADR-003 must pass. |
| Live provider calls in CI | Stubs only in unit tests (AC-022). |
| First real refresh runs before DQ-A5 approval | Gate recorded in this plan; the run is blocked until the approver and date are entered. |
| Parity check reported as passed without a baseline | `/run-eval` reports "not evaluated" when `evals/product/baseline.md` is missing or blank (AC-023). |
| `.env` committed by mistake (G-08) | Add ignore rules in SP-01 before any commit. |

## Human gate

| Approver | Date | Decision |
|----------|------|----------|
| Ardra Arun | 2026-10-13 | Approved |

The BRD gate was cleared on 2026-10-13 (Ardra Arun). This plan was approved by the same person on 2026-10-13. `/implement-api` still waits on the SP-01 critical gaps (G-04, G-06, G-07, G-08).

**Output path:** `artifacts/sprints/S1-plan.md`

**Next command after Approved:** `/implement-api` (command spine).
