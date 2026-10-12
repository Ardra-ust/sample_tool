---
name: e2e-testing
description: Start verified local stack, run the E2E test framework against the live UI, route failures to owning agents. Use on /run-tests and /close-eval-gaps UI fixes.
---

# E2E Testing

E2E framework: `.claude/rules/techstack.md`.

## Prerequisites

Application **must** be running before E2E:

```bash
bash scripts/run-local-stack.sh
bash scripts/verify-stack-health.sh
```

If health check fails → **environment FAIL**; owning agent: **backend-agent** (API) or **frontend-agent** (UI).

## Run

From config `evals.test_commands.e2e`, default stack example:

```bash
cd <ui-module-root>
npm run test:e2e
```

Use a stable/headless browser channel when browser download is blocked. Default `--workers=1` (or the E2E framework's equivalent single-worker flag).

## Authoring (e2e-codegen)

1. Every spec cites TC / AC / FR/BR from approved package.
2. Generate `e2e/fixtures`, `e2e/data`, page objects when missing.
3. Mirror API auth headers from IT tests — no invented journeys.

## On failure

| Failure type | Owning agent |
|--------------|--------------|
| Locator / UI regression | frontend-agent |
| API 4xx/5xx / wrong payload | backend-agent or api-agent |
| Environment / stack down | backend-agent + frontend-agent |

e2e-defect-analyzer → `artifacts/issues/<date>-e2e-failure.md`. e2e-self-healer → suggestion only (human applies).

## Subagents

`e2e-codegen`, `ui-test-runner`, `e2e-scenario-writer`, `e2e-defect-analyzer`, `e2e-self-healer`
