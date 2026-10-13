# Agent Audit — /expand-test-coverage — S1 (refused)

> Aligns with `docs/harness/progress.md`. No secrets, credentials, or PHI/PII.

| Field | Value |
|-------|-------|
| **Date** | 2026-10-13 |
| **Command / Agent** | /expand-test-coverage (quality-agent, test-agent; not run) |
| **Iteration** | 0. Stopped before Phase 1. |
| **Outcome** | **REFUSED.** Required inputs not met. No test cases, matrix, coverage gate or package written. |

## Why it stopped
1. **No accepted BRD.** The command requires an Accepted BRD or story pack. The BRD `artifacts/brd/ai-news-agent-BRD-draft.md` is at v0.2, status **Draft — Pending Domain Review**, because v0.2 adds the LLM stage specification (§17, FR-046 to FR-048) and needs re-acceptance. v0.1 was accepted by Ardra Arun on 2026-10-13.
2. **`evals.rule_source` is blank.** `.claude/config.yaml` line 66 is `rule_source: ""`. The command refuses when it is missing.

## Checks
| Check | Result | Evidence |
|-------|--------|----------|
| BRD Accepted (or story pack) | FAIL | BRD header and status row: Draft v0.2 |
| `evals.rule_source` set | FAIL | `.claude/config.yaml` line 66 |
| Untrusted intake scan | Not run | No untrusted inputs supplied; trusted artifacts only |
| `docs/test-cases.md` | Not written | Refused before Phase 1 |

## Open items (for the human)
- **DQ-E1:** accept BRD v0.2 (Ardra Arun or a named approver). Until then the BRD is not Accepted.
- **DQ-E2:** set `evals.rule_source` to the accepted BRD path (`artifacts/brd/ai-news-agent-BRD-draft.md`). This is a config change and needs approval before it is made.
- Both must be done before the command can run. No test case has been invented.

## Next command
`/expand-test-coverage` once DQ-E1 and DQ-E2 are closed.

**Output path:** `artifacts/audit/2026-10-13-expand-test-coverage-S1-refused.md`
