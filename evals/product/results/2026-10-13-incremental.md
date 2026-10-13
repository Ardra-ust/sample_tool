# Eval results — 2026-10-13 — incremental

**Verdict: FAIL** (confidence: medium). Ledger complete: 88 rows.

| Measure | Count |
|---|---|
| Rules in scope (BRD) | 76 |
| Rules pass | 34 |
| Rules fail | 42 |
| Rules not run | 0 |
| Always-on families present | 5 of 5 |
| Fix-queue items | 29 |
| auto_fix open | 2 |
| needs_human | 27 |

## Always-on families

| Family | Verdict | Note |
|---|---|---|
| L1-04-input-validation | catalog_gap | No mandatory negative case for invalid input. Adding cases changes the Approved test package; route via /expand-test-coverage. See EV-025. |
| L1-05-error-handling | pass | Positive: TC-040 empty state. Negative: TC-026 HTTP 500, TC-041 load failure. Open: OQ-API-1 (500 body wording) unresolved. |
| L1-08-security-anti-pattern | not_run | No SAST or security anti-pattern tool configured. Tool choice is a human decision. See EV-026. |
| L1-09-secret-handling | pass | Positive: TC-031 settings from .env. Negative: TC-043 secrets masked in logs; TC-026 redaction test. |
| L4-03-gate-blocks-security | not_run | No security gate in build or CI. Enable only; tool choice is a human decision. See EV-027. |

## Gate

Not green. 23 product cases fail (stages not built), and three always-on families are MISSING or not run. Not a product pass.

## Deviations

- Case folders (prompt.md + GRADING.md) not created; rows point at docs/test-matrix.md IDs. Pointer folders can be generated on request.
- Severities for BR-001..008 and NFRs are assumed (ASSUMPTION-EVAL-001).
- /close-eval-gaps run for EV-028 and EV-029: both closed (see fix-log). The other 27 items are needs_human and remain open.

## Inputs

- artifacts/test-results-2026-10-13-run-tests.md
- docs/test-matrix.md, docs/test-cases-br-coverage.md, artifacts/issues/2026-10-13-run-tests-defects.md
