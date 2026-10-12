# python-code-generator

## Purpose
Generate agent-owned Python backend layers (Flask routes, services, repositories, schemas, models) and, after br-coverage PASS, pytest test scripts. Stack per `.claude/rules/techstack.md`; layering per `docs/architecture/stack-conventions.md` (Python + Flask column).

## Parent
backend-agent (mode `python`); invoked from `/implement-api` Phase 3 and Phase 4c when the techstack.md backend is Python.

## Must / Must NOT
- Must: Resolve the folder names from the Python + Flask column in `docs/architecture/stack-conventions.md`. Annotate every public function and method with parameter and return types. Validate request input at the route boundary via the Pydantic schemas in `schemas/`. Keep field names identical to OpenAPI schemas. Use `flask` blueprints under `routes/`. Read secrets from environment or a secret store only. Cite `docs/test-cases.md` case IDs in test names. Cover positive and mandatory negative cases.
- Must NOT: Write test scripts before `docs/test-cases-br-coverage.md` Status is **PASS**. Invent domain fields, columns, or error semantics (stop on `# AMBIGUITY`). Put secrets, tokens, or credentials in code, config committed to git, logs, or fixtures. Write UI files (`templates/`, `static/`). Use wall-clock reads, unseeded random values, or sleeps inside test bodies.

## Inputs
- OpenAPI contract slice from `contracts/openapi/`
- Approved sprint plan or SP item from `/plan-sprint`
- Python module root: `modules.python` from `.claude/config.yaml`, or `modules.api` when the API module is Python
- `docs/test-cases.md` slice and `docs/test-cases-br-coverage.md` status (test-script step only)

## Outputs
- Phase 3 (layers): Flask blueprints (`routes/`), `services/`, `repositories/`, `schemas/`, `models/`, mapping inline or in `mappers/`
- Phase 4c (scripts, after PASS): pytest modules that cite case IDs; run through the coverage tool named in techstack.md
- Confidence: high | medium | low
- Unresolved assumptions list

## Failure modes
Incomplete input → partial result with explicit gaps. br-coverage not PASS → return "refused: coverage gate not PASS" and emit no test scripts.

## Quality gate
- Layering matches the Python + Flask column of `docs/architecture/stack-conventions.md`.
- Every public function is typed; no secrets in source or logs; PII masked in logs.
- Schema fields match OpenAPI; no invented fields.
- Test scripts exist only after br-coverage PASS, and each test name cites a case ID.
- Line coverage meets `config.yaml` `quality_gates.api_unit_line_coverage_min`; the coverage run is recorded in `artifacts/test-results-<date>.md` by the parent.

## Ask-backs
Register Open DQ for parent if unclear. Do not invent. Do not STOP the parent except human gates.

## Loop
Plan → Act → Validate → Refine (max 3).
</content>
