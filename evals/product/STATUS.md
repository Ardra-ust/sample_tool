# Product eval status

Fill per consuming app. Status legend: `EXISTS` (pointer to product test), `NEW` (no case yet), `IMPROVED`, `MISSING` (family empty or rule has no row — FAIL, not green), `WAIVED` (human, with reason; never P0/P1).

Always-on safety families must not stay `NEW`/`MISSING` after `/run-eval` unless queued as `catalog_gap`.

| Type | Status | Notes |
|------|--------|-------|
| L1-01-pure-function-correctness | NEW | add project cases |
| L1-02-edge-case-coverage | NEW | |
| L1-03-rest-endpoint-correctness | NEW | |
| L1-04-input-validation | MISSING | no negative invalid-input case; see EV-025 |
| L1-05-error-handling | EXISTS | TC-026, TC-040, TC-041; pass |
| L1-06-test-generation-inclusion | NEW | |
| L1-07-style-conventions | NEW | |
| L1-08-security-anti-pattern | MISSING | no SAST tool; see fix-queue |
| L1-09-secret-handling | EXISTS | TC-031, TC-043, TC-026; pass |
| L1-10-requirement-completeness | IMPROVED | 34 pass, 42 fail, 0 not run of 76 BRD rules (pointers to matrix IDs) |
| L1-13-prompt-ab-harness | NEW | optional |
| L4-01-pipeline-happy-path | NEW | |
| L4-02-gate-blocks-low-coverage | NEW | Backend coverage check enabled |
| L4-03-gate-blocks-security | MISSING | no security gate; see fix-queue |
| L4-04-gate-blocks-forbidden-paths | NEW | CODEOWNERS |
| LX-01-judge-human-agreement | NEW | |
| LX-02-anchor-ambiguity | NEW | |
| LX-03-judge-prompt-versioning | NEW | |
