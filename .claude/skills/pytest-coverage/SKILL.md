---
name: pytest-coverage
description: Run pytest with coverage.py for the Python API module, interpret line and branch gaps, and recommend unit tests. Pytest/coverage twin of the Java coverage skill; use when the backend is Python.
---

# Pytest Coverage

Tool names per `.claude/rules/techstack.md` (pytest + coverage.py via pytest-cov). Pairs with `backend-coverage`; use this one when the backend row is Python.

## Run

Example following `.claude/rules/techstack.md`, run from the Python module root in `.claude/config.yaml`:

```bash
cd <python-module-root>
pytest --cov=app --cov-branch --cov-report=xml --cov-report=term-missing
```

Parse `coverage.xml` (Cobertura format). The root `<coverage>` element carries `line-rate` and `branch-rate`; per-class `<line>` elements with `branch="true"` and `condition-coverage` show which branches are missed.

## Priority for branch gaps
1. Validation / domain rules (one test per branch)
2. Services
3. Parsers / calculators / adapters

## Gates
`.claude/config.yaml` → `quality_gates.api_unit_line_coverage_min` and `api_unit_branch_coverage_target`. Do not lower them. Record the numbers and the command in `artifacts/test-results-<date>.md`; do not estimate them.

## Subagent
`.claude/subagents/coverage-analyzer.md` parses the report and ranks risky gaps.
