---
name: backend-coverage
description: Run the backend coverage toolchain for the API module, interpret line/branch gaps, and recommend unit tests. Use when improving API coverage or reporting metrics.
---

# Backend Coverage

## Run
Use the backend coverage tool named in `.claude/rules/techstack.md` (see `config.yaml` `modules.api`). Default stack example:

```bash
cd <api-module-root>
pytest --cov=app --cov-report=xml --cov-branch
```

Parse the tool's report (e.g. `coverage.xml`) for LINE / BRANCH counters.

## Priority for branch gaps
1. Validation / domain rules (one test per branch)
2. Application services
3. Parsers / calculators / adapters

## Gates
`.claude/config.yaml` → `quality_gates.api_unit_line_coverage_min` and `api_unit_branch_coverage_target`. Do not lower them.

Run after unit/IT tests; use with live stack when IT probes run (skill: `quality`).

## Subagent
`.claude/subagents/coverage-analyzer.md`
