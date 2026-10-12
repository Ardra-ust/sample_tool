# Test Results Log — {{DATE}}

> Structured log per rule 17. Normalized from runner output — real counts only, no fabrication.

| Field | Value |
|-------|-------|
| **Log ID** | TRL-{{YYYYMMDD}} |
| **Timestamp (UTC)** | {{timestamp}} |
| **Environment** | local / CI / staging |
| **Branch / commit** | {{branch}} / {{sha}} |
| **Agent** | test-agent (mode log) |
| **Parent command** | {{command}} |

## Suite summary

| Suite | Command | Total | Pass | Fail | Skip | Duration | Coverage % | Verdict |
|-------|---------|-------|------|------|------|----------|------------|---------|
| API unit | backend unit-test command (per techstack.md, e.g. `pytest` (or `mvn test` for a Java stack)) | | | | | | | |
| API IT | | | | | | | | |
| UI unit | `npm test` | | | | | | | |
| E2E | `npm run test:e2e` | | | | | | N/A | |

## Failure index

| Suite | Test name | TC ref | Error (first line) | Flaky |
|-------|-----------|--------|-------------------|-------|
| | | | | yes/no |

## Evidence paths

| Artifact type | Path |
|---------------|------|
| Raw backend test-runner log | |
| Backend coverage report | |
| E2E HTML report | |
| Normalized summary | `artifacts/test-results-{{date}}.md` |

## Traceability check

| TC ID | rule_ids | Executed | Result |
|-------|----------|----------|--------|
| | | yes/no | |

**Output path:** `artifacts/test-results-log-{{date}}.md` (companion to `test-results-template.md`)
