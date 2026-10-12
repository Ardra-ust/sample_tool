---
description: Template-owned backend unit test generation
globs:
  - "**/*Test.java"
  - "**/*IT.java"
  - "**/test_*.py"
  - "**/*_test.py"
  - "**/agent-owned backend unit tests**"
  - "**/docs/test-cases.md"
alwaysApply: false
---

# Test Generation

Backend unit/IT test framework: `.claude/rules/techstack.md`. Globs and examples below cover both the current default (Python/pytest) and the legacy (Java/JUnit) stack — trim/update them if the backend language changes again.

- Agents extract variables; `agent-owned backend unit tests` own backend test structure via the template registry.
- Stop on `# AMBIGUITY` — do not invent test structure.
- Registry files own harness (framework-appropriate slice/mocking/container-test setup), standard CRUD methods, and the traceability header. Forbidden: unseeded sleeps, unseeded random values, wall-clock reads, and random-UUID generation inside test bodies (e.g. `time.sleep()`, `random.random()`, `datetime.now()`, `uuid.uuid4()` in the Python default; `Thread.sleep()`, `new Random()`, `LocalDateTime.now()`, `UUID.randomUUID()` for a Java stack).
- Agent-owned extras are sibling `*RegressionTest` / `*SecurityTest` classes (or `AGENT-OWNED TEST` blocks) whose IDs exist in `docs/test-cases.md` and `agent_driven_scenarios`.
- Persist/reuse `artifacts/templates/<resource>-vars.yaml`. `stack-conventions.md compliance --check test` must PASS before DoD.
- `/implement-api` writes slice test cases + BR coverage, then scripts, then runs tests (ASSUMPTION-PCC-002 — not blocked by expand PASS). `/expand-test-coverage` expands remaining FR/BR **design** only. Gap scripts for remaining FR/BR run on `/run-tests` after package **Approved**. There is no public `/generate-backend-unit-api-tests` command.
