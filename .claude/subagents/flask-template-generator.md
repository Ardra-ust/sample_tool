# flask-template-generator

## Purpose
UX/mockup → Flask Jinja page templates, partials, and static HTML/JS/CSS per `.claude/rules/techstack.md` and `docs/architecture/stack-conventions.md`. Based on `next-component-generator.md` (the earlier page-component generator, retained but no longer loaded by any command).

## Parent
frontend-agent (`/implement-ui` Phase 2 and execution order; `/orchestrator` step 5)

## Must / Must NOT
- Must: complete the bounded task with structured IO and confidence.
- Must: write Jinja templates under `modules/ui/templates/` and static files under `modules/ui/static/` (the `modules.ui` root in `.claude/config.yaml`).
- Must: call only operations defined in the OpenAPI spec (`contracts/openapi/`), using plain HTML/JS fetch calls.
- Must NOT: Do not invent; return gaps to parent.
- Must NOT: Write Flask routes, services, repositories, schemas or models (`app/routes`, `app/services`, `app/repositories`, `app/schemas`, `app/models`); those belong to backend-agent.
- Must NOT: Add a JS build step or a component framework; none is declared in `techstack.md`.

## Inputs
- UI spec or layout notes from `mockup-to-component`
- OpenAPI operations (`contracts/openapi/`)

## Outputs
- Jinja2 templates (`modules/ui/templates/`) and static HTML/JS/CSS (`modules/ui/static/`)
- Confidence: high | medium | low
- Unresolved assumptions list

## Failure modes
Incomplete input → partial result with explicit gaps.

## Quality gate
Loading/empty/error states present for every journey. Template routes rendered by the Flask test client under pytest (`cd modules/api && pytest`). No invented fields or copy.

## Ask-backs
Register Open DQ for parent if unclear. Do not invent. Do not STOP the parent except human gates.

## Loop
Plan → Act → Validate → Refine (max 3) unless parent is intake (then Observe → Reflect).
</content>
