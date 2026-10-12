# /run-tests

## Invocation

`/run-tests` — generate and run executable tests from an **Approved** expand package.

## Objective

Generate executable tests from an **Approved** expand package, run them, persist results, then complete defect analysis (and self-heal suggestions on locator failures). Order: backend unit/IT → frontend unit → E2E (test frameworks per `.claude/rules/techstack.md`). Backend registry tests via `backend-test-generator` + `docs/architecture/stack-conventions.md` PASS.

## Use Agents

- orchestrator-agent
- quality-agent
- backend-agent
- frontend-agent
- test-agent (generate mode — scripts + execute only)

## Delegate to Subagents

- backend-test-generator (backend registry files)
- e2e-codegen
- api-test-runner
- ui-test-runner
- coverage-analyzer
- e2e-defect-analyzer
- e2e-self-healer
- audit-trail-writer

## Enforce Rules

00, 02, 07, 09, 10, 11, 17, 22, 23 (test-generation)

## Use Templates

`test-results-template.md`, `audit-trail-template.md`, `plan-act-validate-refine-loop.md`, `ooda-self-heal-loop.md` (Phase 5 inner), `e2e-spec-template.md`, `page-object-template.md`, `defect-analysis-template.md`, `self-heal-suggestion-template.md`, `agent-owned backend unit tests`

## Use Skills

`.claude/skills/quality/SKILL.md`, `.claude/skills/br-coverage/SKILL.md`, `.claude/skills/backend-coverage/SKILL.md`, `.claude/skills/e2e-testing/SKILL.md`

## Runtime Inputs

### Required

- `docs/test-cases-br-coverage.md` Status **PASS** (br-coverage-validator only)
- `docs/quality/test-package-review.md` **Approval = Approved** (human). Agents Must NOT self-approve.
- `docs/test-cases.md` + `docs/test-matrix.md`

## Command-Specific Hardening

Refuse if Approval is missing, **Pending Approval**, or stamped by an agent. Dated waiver in `docs/harness/decisions.md` is the only override. Do not disable the backend coverage tool or edit its build-file coverage floors. E2E specs must cite case IDs / AC / FR/BR. Self-heal **suggests** locator diffs via OODA (`ooda-self-heal-loop.md`); do not auto-merge. Applying a heal requires an explicit human request. No secrets in fixtures. `e2e-codegen` must generate `e2e/fixtures` + `e2e/data` when missing — do not no-op Phase 1 because a smoke spec already exists. Default E2E `--workers=1` (or the framework's equivalent single-worker flag). Backend registry tests must PASS `docs/architecture/stack-conventions.md`; agent-owned extras cite `docs/test-cases.md` IDs. If API is down for E2E: record **environment FAIL** in test-results; do not skip session journeys as pass.

## Execution Policy

Plan → Act → Validate → Refine (max 3 ceiling). Iteration 1 Validate pass → stop. Refine only from findings. Escalate with owners after iteration 3.

## Execution flow

| Phase | Role | Artifact |
|-------|------|----------|
| 0 Gate | Orchestrator | Confirm PASS + Approved |
| 0b Stack | quality-agent | `scripts/run-local-stack.sh` + `scripts/verify-stack-health.sh` — API + UI must be healthy before E2E |
| 1 Scripts | backend-agent / frontend-agent / backend-test-generator / e2e-codegen, routed by `execution_layer` | backend unit/IT, frontend unit, e2e specs/pages/fixtures/data |
| 2 Execute | api-test-runner then ui-test-runner (frontend unit then E2E) | `artifacts/test-results-<date>.md` + script paths |
| 3 Line coverage | coverage-analyzer | backend coverage tool / frontend unit-test coverage evidence in results |
| 4 Defect | e2e-defect-analyzer | `artifacts/issues/<date>-e2e-failure.md` per failure (or N/A if none) |
| 5 Self-heal | e2e-self-healer OODA inner loop (locator failures only) | `artifacts/issues/<date>-locator-heal.md` — suggestion only; never auto-merge |

**Layer routing (Phase 1):**

| Matrix / case `execution_layer` | Gap `Automated = NONE` routes to |
|---------------------------------|----------------------------------|
| `api`, `IT` | backend-agent (unit / IT) + backend-test-generator |
| `uat` | frontend-agent (unit) and/or e2e-codegen (E2E journey) |
| `integration` | backend-agent + frontend-agent + e2e-codegen |
| `blocked` | Skip (not a gap); optional unit test only |

Do not invent journeys or AC not in the approved package (rule 22).

## Decision logic

- If package not Approved → **refuse**; next action is human approval of `docs/quality/test-package-review.md`.
- If coverage not PASS → **refuse**; return to `/expand-test-coverage`.
- If requirements unclear → **ask user**; do not invent.

## Clarification Protocol

After resolve-before-ask, register Open DQ when the package file is missing. Do not invent approval. STOP for the human gate. Still refuse when Approval is not Approved.

## Artifact persistence

- Generated tests under `modules.api` / `modules.ui` (from `config.yaml`) including e2e specs/pages/fixtures/data
- `artifacts/test-results-<date>.md`
- `artifacts/issues/<date>-e2e-failure.md` (when failures)
- `artifacts/issues/<date>-locator-heal.md` (when locator failures)
- `artifacts/audit/<date>-run-tests-<task>.md`

## Definition of Done

- [ ] Preconditions PASS + Approved verified
- [ ] Backend unit/IT tests generated for api/IT gaps and executed
- [ ] Frontend unit tests generated for uat UI-unit gaps and executed
- [ ] E2E specs + POM + fixtures + test data generated for in-scope E2E; every spec cites TC/AC/FR/BR
- [ ] `docs/architecture/stack-conventions.md` PASS when backend registry tests changed
- [ ] Execution order backend unit/IT → frontend unit → E2E honored
- [ ] Test results artifact lists commands, pass/fail/skip, and script paths
- [ ] Backend coverage tool % for API and frontend unit-test coverage for UI helpers when those layers ran
- [ ] Defect analysis written for each failure (summary, likely root cause, confidence, suggested resolution)
- [ ] Locator failures have a self-heal **suggestion** (not merged)
- [ ] No secrets/PII in fixtures or data
- [ ] Audit written; harness updated (phase-changing)

## Next command

```
✅ /run-tests complete.
**Next command:** /run-eval
```
