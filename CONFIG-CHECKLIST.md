# config.yaml checklist

Copy `.claude/config.yaml.example` → `.claude/config.yaml` and fill before running commands. "Recommended default" values below match the default stack in `.claude/rules/techstack.md` — substitute your own if you changed the stack.

| Key | Your value | Recommended default |
|-----|------------|------------------|
| `project.name` | | *(required — no placeholders)* |
| `project.domain` | | bounded context name |
| `modules.api` | | `modules/api` |
| `modules.ui` | | `modules/ui` (Jinja templates and static files; the Flask app in `modules/api` serves them) |
| `modules.openapi` | | `contracts/openapi/<service>-v1.yaml` |
| `evals.rule_source` | | path to Accepted BRD after `/generate-brd` |
| `evals.test_commands.api` | | `cd modules/api && pytest --cov` |
| `evals.test_commands.ui` | | `cd modules/api && pytest` (Flask template/route tests) |
| `evals.test_commands.e2e` | | `cd modules/api && npx playwright test` |
| `local_stack.api_health_url` | | `http://localhost:5000/health` |
| `local_stack.ui_health_url` | | `http://localhost:5000/` (Flask serves the Jinja UI) |
| `pipeline.eval_fix_command` | | `close-eval-gaps` |
| `local_stack.start_script` | | `scripts/run-local-stack.sh` |
| `quality_gates.api_unit_line_coverage_min` | | `0.70` |

**Hard stop:** orchestrator refuses product code while placeholders remain (rule 01).
