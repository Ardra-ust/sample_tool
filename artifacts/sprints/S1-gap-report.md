# Gap Report — Sprint S1 (AI News Agent)

> Internal gap step of `/plan-sprint` (not a public command). Status: **Proposed — Pending Approval** with the plan. No secrets or PII in this report.

| Field | Value |
|-------|-------|
| **Sprint** | S1 |
| **Goal** | Build the full AI News Agent |
| **Duration** | 2 weeks (proposed dates 2026-10-13 to 2026-10-26; owner to confirm) |
| **BRD** | `artifacts/brd/ai-news-agent-BRD-draft.md`, status **Accepted** (Ardra Arun, 2026-10-13); decisions row in `docs/harness/decisions.md` |
| **Architecture** | `docs/architecture/2026-10-13-architecture-proposal.md` (Proposed); ADR-001 to ADR-003 (Proposed) |
| **Date** | 2026-10-13 |

## What exists in the repo today

| Area | State |
|------|-------|
| Flask app | `modules/api/app/main.py` with `GET /health` and the template and static folders pointed at `modules/ui`. No other routes, services, repositories or pipeline code. |
| Dependencies | `modules/api/requirements.txt` lists only `Flask`, `pytest`, `pytest-cov`. |
| UI | `modules/ui/templates/` and `modules/ui/static/` contain only `.gitkeep`. |
| API contract | `contracts/openapi/ai-news-agent-v1.yaml` does not exist. |
| Database | No migrations and no `new_data` or `refresh_status` tables. |
| Worker | `refresh_worker.py` does not exist. |
| Config | `.env.example` does not exist. `.env` exists, is untracked and is not ignored by git (not read here). |
| Tests | No test directory. |
| Baseline | `evals/product/baseline.md` does not exist. |
| Harness | `docs/harness/progress.md` is untracked; `decisions.md` has the BRD acceptance row. |

## Gaps

Critical gaps must have an owner (DoD). Owners are roles; personal names are not in the sources, so each is "(name needed)".

| ID | Severity | Gap | Owner | Blocks | Action |
|----|----------|-----|-------|--------|--------|
| G-01 | critical | LLM prompt text and expected output format for the title re-check (BRD FR-012), relevance gate (FR-014), deal tagging (FR-020) and domain, priority and summary (FR-021). The BRD defines the behaviour, not the prompts. | Product owner (name needed) | SP-06 | Owner supplies the prompts and output schemas. Not invented here. |
| G-02 | critical | Location and format of the 42 RSS feeds and 25 Google News query strings. The BRD fixes the content but not where it lives in the code. | Dev lead (name needed) | SP-04 | Decide: code constant or a versioned config file. |
| G-03 | critical | Location of the consumer-noise block and allow word lists, and the relevance-gate force-keep list (FR-011, FR-014). | Dev lead (name needed) | SP-05, SP-06 | Decide the location. Lists come from BRD §5 and FR-014 only. |
| G-04 | critical | Dependencies not declared. `requirements.txt` has Flask, pytest and pytest-cov only. The pipeline needs a MySQL driver, SQLAlchemy and Alembic (DQ-A6), feed parsing, dotenv, the Google News decoder, HTML stripping (NFR-009), numpy and dateutil (FR-013, FR-016 and FR-019), and the Azure OpenAI and Tavily clients. Versions are not pinned in any source. | Dev lead (name needed) | SP-01 | Add the packages, pin versions, and record the choices. Groq is excluded by the owner. |
| G-05 | critical | OpenAPI spec `contracts/openapi/ai-news-agent-v1.yaml` does not exist. The api-agent gates require it before routes are implemented. | api-agent, with dev lead | SP-02, SP-03 | api-agent writes the spec from BRD §5 and §8, then verifies it. |
| G-06 | high | `.env.example` is missing (FR-042), so the required variable names are undocumented. | Dev lead (name needed) | SP-01 | Create with empty values, with no secrets. |
| G-07 | high | Migrations for `new_data` and `refresh_status` are not written (DQ-A6: Alembic creates the tables if missing). | data-agent, with backend-agent | SP-01 | Write an additive Alembic migration. No DDL in the plan text. |
| G-08 | high | `.env` is untracked and not ignored by git. It holds credentials. | Dev lead (name needed) | Any commit | Add `.env` to ignore rules before any commit. The file is not read or changed by this plan. |
| G-09 | high | Playwright and Node are not set up. `config.yaml` points E2E at `npx playwright test` in `modules/api`, but there is no Playwright configuration. | Dev lead (name needed) | SP-10 (E2E), SP-11 | Set up the E2E configuration in the sprint. |
| G-10 | high | The owner has not recorded the baseline. `evals/product/baseline.md` is missing, so the parity check (AC-023) cannot pass. | Owner (name needed) | Parity check only; does not block the build | Owner runs the existing app 3 times on one day and records the averages. Until then `/run-eval` reports "not evaluated". |
| G-11 | critical for first refresh | Approval of the Azure OpenAI resource for this use is not recorded (DQ-A5). | Approver (name and date needed) | First real refresh only; does not block the build | Record the approver and date. Until then the first real refresh must not run. |
| G-12 | medium | The request parameters the chat deployment supports are not verified. `AZURE_OPENAI_CHAT_DEPLOYMENT` is owner-set (DQ-A3), and the ADR requires a test that the client sends only supported parameters. | Dev lead (name needed) | SP-06 test | Verify the supported parameters against the deployment. |
| G-13 | medium | Storage of the 400-article cap and the 500-article dedupe cap in code is clear, but the pipeline order (FR-045) needs a test that does not depend on the live LLM. | Dev lead (name needed) | SP-08 | Stub sources and LLM calls (AC-022). |
| G-14 | low | `evals.rule_source` in `config.yaml` is blank. It does not block the build. | Dev lead (name needed) | `/run-eval` input | Set it to the BRD path when `/run-eval` is planned. |
| G-15 | low | `local_stack.ui_health_url` is `http://localhost:5000/`, which needs a root route. The app has no root route yet. | Dev lead (name needed) | SP-03 or SP-09 | Add the root page route in the UI slice, or set the URL explicitly. |

## G-01 closed (LLM prompts and output formats)

**Status: CLOSED.** The prompts in `artifacts/intake/supporting/llm-prompts-workflow.md` were reviewed and confirmed by the owner, Ardra Arun, on 2026-10-13.

Three deliberate points were recorded at closure:

- **(a)** The Stage 10 example had a trailing comma after `"priority": 4`, which made it invalid JSON. The comma was removed in the intake copy. No other prompt text was changed. The Stage 10 template folder `modules/api/app/prompts/` does not exist yet, so no template copy was changed.
- **(b)** The Stage 3 instruction to give extra weight to deal titles is overridden by the DQ-006 title safety net (RISK-002). The safety net blocks restoring any title containing "deal", so deal titles are never restored at Stage 3 even though the prompt asks the model to prefer them. This is the owner's decision.
- **(c)** "UST" stays in the Stage 5 relevance-gate prompt, as a peer name, per DQ-008. It is recorded as known substring behaviour, not a UST feature.

G-01 no longer blocks SP-06. The prompt text still has to be stored as templates under `modules/api/app/prompts/` when SP-06 is built.

## Closed or accepted (no action in S1)

| Item | Status |
|------|--------|
| Stale-lock limit (70 minutes, not the notes' 20) | Owner decision (DQ-018). |
| Authentication | None for this build. Known risk RISK-A1 and NFR-010 are recorded. |
| Cloud and hosting | Local only. Cloud target out of scope (DQ-021). No infra, CI/CD or Terraform in the plan. |
| Azure WebJob | Optional, per FR-039 only. |
| Chat model | Owner sets `AZURE_OPENAI_CHAT_DEPLOYMENT` (DQ-A3). No model name in the docs. |
| Snapshot retention | Never delete rows (DQ-016). |
| Footer text | "Copyright 2025 UST" (DQ-009). |
| Feed list fixes | Keep all 42 feeds as listed, correct "Financial Times" (DQ-011). |

## Critical gaps and owners

Every critical gap has an owner role. Names are required from the team before the sprint starts (G-01 to G-04, G-02 and G-03 block build slices; G-11 blocks only the first real refresh).

## Validation

| Check | Result |
|-------|--------|
| BRD Accepted | Pass |
| Every planned SP maps to FR/BR | See plan (traceability table) |
| Critical gaps owned | Owners assigned as roles; names needed |
| Proposed — Pending Approval | Yes |
