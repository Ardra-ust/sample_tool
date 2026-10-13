#!/usr/bin/env bash
# Start the Flask API for local test/e2e runs. The Flask app also serves the Jinja UI
# (modules/ui/templates, modules/ui/static) from the same process, so there is no separate UI server.
# Stack per .claude/rules/techstack.md; backend and UI both live under modules/api.
set -euo pipefail

API_ROOT="${API_MODULE_ROOT:-modules/api}"
API_PORT="${API_PORT:-5000}"
API_APP_MODULE="${API_APP_MODULE:-app.main:app}"
PID_FILE="${PID_FILE:-artifacts/local-stack.pids}"

mkdir -p artifacts
: > "$PID_FILE"

if [[ ! -d "$API_ROOT" ]]; then
  echo "ERROR: Set API_MODULE_ROOT to the implemented module path (default modules/api)." >&2
  exit 1
fi

echo "Starting Flask API (and Jinja UI) in $API_ROOT on port $API_PORT ..."
(
  cd "$API_ROOT"
  if [[ -f pyproject.toml || -f requirements.txt ]]; then
    flask --app "$API_APP_MODULE" run --host 0.0.0.0 --port "$API_PORT" --reload &
  else
    echo "ERROR: No pyproject.toml or requirements.txt under $API_ROOT." >&2
    exit 1
  fi
  echo $! >> "$PID_FILE"
)

echo "UI is served by the Flask app at http://localhost:$API_PORT/ (no separate UI process)."
echo "Stack starting. Run scripts/verify-stack-health.sh before /run-tests E2E."
