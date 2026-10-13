# Harness Decisions (append-only)

| Date | Decision | Owner | Notes |
|------|----------|-------|-------|
| | | | |
| 2026-10-13 | BRD `ai-news-agent` (artifacts/brd/ai-news-agent-BRD-draft.md) ACCEPTED by human reviewer. | Ardra Arun | Human acceptance; no waiver used. Status Accepted in the BRD header. /plan-sprint may run once a sprint ID, goal and duration are supplied. Open gates not closed by this row: DQ-A5 Azure OpenAI approval (must be recorded before the first real refresh); evals/product/baseline.md values (DQ-003, DQ-004, DQ-019, non-blocking). |
| 2026-10-13 | Sprint plan S1 (`artifacts/sprints/S1-plan.md`, with gap report `artifacts/sprints/S1-gap-report.md`) APPROVED by human approver. | Ardra Arun | Human approval of the plan. Agents did not approve it. Plan status is Approved in its header and approval table. Before /implement-api runs, these must be closed: SP-01 critical gaps G-04 (dependencies), G-06 (.env.example), G-07 (migrations), G-08 (.env ignored by git). Also owner input still open: G-01 LLM prompts (blocks SP-06), G-02 feed list location (SP-04), G-03 word-list location (SP-05, SP-06), G-05 OpenAPI spec (SP-02, SP-03). Not closed by this row: G-10 baseline values (parity check only), G-11 DQ-A5 Azure approval (first real refresh only). |

Do not overwrite prior rows. Supersede with a new row.

Common waivers: BRD Accepted, plan Approved, test-package Approved, intake PII redaction.
