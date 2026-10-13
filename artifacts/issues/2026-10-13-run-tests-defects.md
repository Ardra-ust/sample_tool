# Defect analysis — /run-tests — S1 (23 failures)

> From `/run-tests` Phase 4. Each failure group has a summary, likely root cause, confidence and suggested resolution. No secrets.

## Group 1 — Pipeline stages not built (22 failures plus 1 sub-test)

| Field | Value |
|-------|-------|
| **Failures** | `test_stage_not_built` for TC-001 to TC-007, TC-009, TC-012 to TC-022, TC-032, TC-045, TC-046; and `test_tc050_stage9_and_stage10_parameters` |
| **Summary** | Each test imports the module that will hold a pipeline stage. The module does not exist, so the import fails. |
| **Likely root cause** | The stages belong to SP-04 (sources, NFR-009), SP-05 (noise and dedupe), SP-06 (stages 9 and 10), SP-07 (embedding and DB dedupe) and SP-08 (freshness, sort, save). Only SP-02 and SP-03 and the stage 3 and 5 relevance logic are built. The failures are expected. |
| **Confidence** | High. Every error is `ModuleNotFoundError` for a module listed in the sprint plan as not yet built. |
| **Suggested resolution** | Build SP-04 to SP-08 in the order of the sprint plan. Each module named in the failing test should be created under the path it names. Do not change the tests to pass before the stage exists. |
| **Owner** | backend-agent (per `artifacts/sprints/S1-plan.md`) |
| **Auto-fix** | No. The failure is a missing feature, not a defect in an existing test. Route to the sprint backlog. |

## Group 2 — Feature not in any sprint item (TC-032, FR-043)

| Field | Value |
|-------|-------|
| **Failure** | `test_stage_not_built[TC-032]` |
| **Summary** | The status-file fallback (FR-043) has no sprint item. The plan does not list it. |
| **Likely root cause** | Gap in the sprint plan. FR-043 is in the BRD but was not allocated. |
| **Confidence** | High |
| **Suggested resolution** | Add FR-043 fallback to a sprint item (SP-03 is the closest, since it reads status) or to a later sprint. Owner decides. |
| **Owner** | Owner (name needed) |
| **Auto-fix** | No. Needs a planning decision. |

## Group 3 — Parity check not built (TC-045, NFR-005)

| Field | Value |
|-------|-------|
| **Failure** | `test_stage_not_built[TC-045]` |
| **Summary** | The parity check that reports passed, failed or "not evaluated" against `evals/product/baseline.md` does not exist. |
| **Likely root cause** | Not in any sprint item. The baseline is owner-supplied (DQ-019), so the check depends on it. |
| **Confidence** | High |
| **Suggested resolution** | Build the parity check once the baseline exists. Until then the check must report "not evaluated" (AC-023). |
| **Owner** | backend-agent, after owner records the baseline |
| **Auto-fix** | No. Blocked on owner input. |

## Group 4 — Skipped, not a failure (TC-045b)

| Field | Value |
|-------|-------|
| **Case** | TC-045b |
| **Reason** | blocked: owner must record `evals/product/baseline.md` (DQ-019). |
| **Action** | Owner records the three-run averages. The skip is recorded as blocked, not as passed. |

## Self-heal (Phase 5)

No locator failures occurred. All seven UI cases passed. Self-heal not run; no `artifacts/issues/*-locator-heal.md` written.

## E2E defect analysis

No E2E failures. The UI cases passed in Microsoft Edge (see the results file for the deviation from the `npx playwright` command in config).
