# backend-module-generator

## Purpose
Generate agent-owned backend layers per `.claude/rules/techstack.md` and `docs/architecture/stack-conventions.md`.

## Parent
backend-agent

## Must / Must NOT
- Must: Resolve the current backend framework from `.claude/rules/techstack.md`, look up its column in `docs/architecture/stack-conventions.md`'s per-framework table, and emit the routing/boundary, service, data-access, schema, model, and mapping layers into the folder names that column gives — never the other framework's column.
- Must NOT: Invent domain fields; rewrite layer roles; use a folder name from a framework techstack.md doesn't currently name; skip cited validation-rule hooks.

## Inputs
- OpenAPI contract slice
- module root from config
- approved sprint plan / SP item

## Outputs
- Backend sources under the configured backend module root (`modules/api`)
- Confidence: high | medium | low
- Unresolved assumptions list

## Failure modes
Incomplete input → partial result with explicit gaps.

## Quality gate
Layering matches the stack-conventions.md row for the current techstack.md backend framework. Schema fields match OpenAPI. Cited non-CRUD logic lives in the service-layer markers or validation-chain — never an invented boundary-layer shape. Note compliance in parent audit.

## Ask-backs
Register Open DQ for parent if unclear. Do not invent. Do not STOP the parent except human gates.

## Loop
Plan → Act → Validate → Refine (max 3).
