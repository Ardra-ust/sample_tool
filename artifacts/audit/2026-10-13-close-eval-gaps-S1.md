# Audit — /close-eval-gaps — S1

**Date:** 2026-10-13
**Command:** /close-eval-gaps (scope: EV-028, EV-029 only)
**Task:** S1 eval fix loop
**Agent:** orchestrator-agent; checks run inline (no `tc-completeness-validator`, `tc-step-quality-validator`, or `test-agent` subagent type is available in this session)
**Iteration:** 1 of 3. Validate passed after one fix per item; no further iterations.

## What

Closed the two `auto_fix: true` items left open by `/run-eval`:

- **EV-028** — run the completeness and step-quality validators on `docs/test-cases.md`. Result: one completeness defect found (TC-021 body `rule_ids` missed FR-025). Fixed. Re-check: 0 completeness findings, 0 quality findings.
- **EV-029** — `docs/test-matrix.md` still showed `designed` and dash for all 51 cases. Updated status and last_result from a fresh test run: 27 passed, 23 failed, 1 skipped.

## Why

`/run-eval` (2026-10-13) queued both items as `auto_fix: true`. The spec says to close them before the eval run completes.

## How

1. Read the two validator specs and the denylist and taxonomy templates. Implemented their checks in a script over `docs/test-cases.md` and `docs/test-matrix.md`.
2. Ran the script. Found one mismatch: TC-021 body listed `FR-024` only. The index, matrix, and coverage file list FR-024 and FR-025. Edited the body to `FR-024, FR-025`.
3. Re-ran the suite with per-test output (`pytest -rA`). Totals: 49 passed, 23 failed, 1 skipped. Matched the earlier run. The one `ERROR` line is a logged exception from the TC-041 server test, not a test error.
4. Mapped each test name to its case IDs and wrote status and last_result into the matrix. A skipped test was matched on its reason text. TC-045b is recorded as skipped.
5. Updated the fix queue, ledger rows (AR-TCG-completeness and AR-run-tests-vs-matrix), fix log, and eval summary.

## Validation

| Check | Result |
|-------|--------|
| Index rows = case bodies (51 = 51) | Pass |
| Index rule_ids = case body rule_ids | Pass after TC-021 fix |
| Matrix rule_ids = index rule_ids | Pass |
| Every BRD rule (FR, BR, NFR) cited by a case | Pass |
| Denylist phrases in steps or expected | 0 hits |
| Each non-blocked case has ≥2 steps | Pass |
| Summary is not Verify/Reject only | Pass |
| source_path present for non-blocked cases | Pass |
| Matrix statuses match a fresh test run | Pass (51 of 51) |
| Test run totals | 49 passed, 23 failed, 1 skipped (same as /run-tests) |

## Open Items

| ID | Item | Owner |
|----|------|-------|
| OI-CL-1 | Checks were run inline. The validator subagents have not run as agents; a formal run would confirm the result. | quality-agent |
| OI-CL-2 | Negative-required check per taxonomy cannot be fully applied: the BRD has no Type column (DQ-E3 open). Constraint error-code specificity also not checked for the same reason. | Owner |
| OI-CL-3 | TC-045b steps are owner procedure, not a pure block statement. Judged acceptable under block documentation; not changed. | quality-agent |
| OI-CL-4 | 27 needs_human items from `/run-eval` remain open (product stages, parity baseline, L1-04, SAST tool choice). Not in this scope. | Owner / backend-agent |
| OI-CL-5 | Harness progress row not written. Only harness-updater can write it, and it isn't available here. | Orchestrator |

## Artifacts

- `docs/test-cases.md` (TC-021 rule_ids)
- `docs/test-matrix.md` (status, script_path, last_result for 51 cases; header line)
- `evals/product/results/2026-10-13-fix-queue.json` (EV-028, EV-029 closed)
- `evals/product/results/2026-10-13-completeness-ledger.md` (two rows updated)
- `evals/product/results/2026-10-13-fix-log.md` (applied fixes)
- `evals/product/results/2026-10-13-incremental.md` (deviation line updated)

## Next command

✅ /close-eval-gaps complete for EV-028 and EV-029 (both closed). The eval verdict stays FAIL: 27 needs_human items are open, including the P0 product failures.
**Next command:** /review-changes can run on the ledger, but it will show the open P0 failures. Decide on the human items first.
