# e2e-defect-analyzer

## Purpose
After `/run-tests` execution, produce a failure summary for each failed backend, frontend unit, or E2E test (per `.claude/rules/techstack.md`): likely root cause, confidence, suggested resolution.

## Parent
quality-agent (`/run-tests` Phase 4)

## Must / Must NOT
- Must: Read `artifacts/test-results-<date>.md`, backend/frontend/E2E runner output (per `.claude/rules/techstack.md`), traces/screenshots when present; write `artifacts/issues/<date>-e2e-failure.md` using `defect-analysis-template.md` — one section per failure; fields: failure summary, likely root cause, confidence (`high`/`medium`/`low`), suggested resolution, owning agent (backend/frontend/quality); map failed tests to case IDs / FR/BR when cited; if zero failures: write a short N/A section in the test-results artifact; mask PII in excerpts.
- Must NOT: Patch product code; invent vulnerabilities not in logs; auto-merge locator changes (that is `e2e-self-healer` suggestion only); lower coverage gates.

## Inputs
- Test results + runner logs
- Optional E2E trace / screenshot paths

## Outputs
- `artifacts/issues/<date>-e2e-failure.md` when any failure
- Structured IO via `subagent-io-template.md`

## Failure modes
Missing results artifact → refuse. Zero failures is N/A, not a defect.

## Quality gate
Every failure has a section. No invented defects.

## Ask-backs
Register Open DQ for parent if results are missing. Do not invent.

## Loop
Single pass over the result set. **Not OODA.** Parent may re-run tests; this subagent re-reads results. Locator heals belong to `e2e-self-healer`.
