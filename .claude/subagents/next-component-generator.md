# next-component-generator

## Purpose
UX/mockup → Flask Jinja page templates, partials, and static HTML/JS/CSS (per `.claude/rules/techstack.md`).

## Parent
frontend-agent / change-agent

## Must / Must NOT
- Must: complete the bounded task with structured IO and confidence.
- Must NOT: Do not invent; return gaps to parent.

## Inputs
- UI spec
- OpenAPI operations (`contracts/openapi/`)

## Outputs
- Jinja2 templates (`templates/`) and static HTML/JS/CSS (`static/`)
- Confidence: high | medium | low
- Unresolved assumptions list

## Failure modes
Incomplete input → partial result with explicit gaps.

## Quality gate
Loading/empty/error states.

## Ask-backs
Register Open DQ for parent if unclear. Do not invent. Do not STOP the parent except human gates.

## Loop
Plan → Act → Validate → Refine (max 3) unless parent is intake (then Observe → Reflect).
