#!/usr/bin/env bash
# Start API + UI for local test/e2e runs. Requires modules built per config.yaml.
# This script can't read .claude/rules/techstack.md (it's a shell script, not prose Claude
# interprets), so instead of hardcoding one stack's boot command it detects common backend
# project markers and picks the matching command. Add a branch here only if your backend
# toolchain isn't one of the ones already covered.
set -euo pipefail

API_ROOT="${API_MODULE_ROOT:-modules/api}"
UI_ROOT="${UI_MODULE_ROOT:-modules/ui}"
API_PORT="${API_PORT:-8080}"
UI_PORT="${UI_PORT:-3000}"
PID_FILE="${PID_FILE:-artifacts/local-stack.pids}"

mkdir -p artifacts
: > "$PID_FILE"

if [[ ! -d "$API_ROOT" || ! -d "$UI_ROOT" ]]; then
  echo "ERROR: Set API_MODULE_ROOT and UI_MODULE_ROOT to implemented module paths." >&2
  exit 1
fi

echo "Starting API in $API_ROOT on port $API_PORT ..."
(
  cd "$API_ROOT"
  if [[ -f pom.xml ]]; then
    SPRING_PROFILES_ACTIVE="${SPRING_PROFILES_ACTIVE:-local}" \
      mvn -q spring-boot:run -Dspring-boot.run.arguments="--server.port=$API_PORT" &
  elif [[ -f pyproject.toml || -f requirements.txt ]]; then
    flask --app "${API_APP_MODULE:-app.main:app}" run --host 0.0.0.0 --port "$API_PORT" --reload &
  elif [[ -f build.gradle || -f build.gradle.kts ]]; then
    ./gradlew bootRun --args="--server.port=$API_PORT" &
  elif [[ -f go.mod ]]; then
    PORT="$API_PORT" go run . &
  elif [[ -f package.json ]]; then
    PORT="$API_PORT" npm run dev &
  else
    echo "ERROR: No recognized backend project file (pom.xml, pyproject.toml/requirements.txt, build.gradle*, go.mod, package.json) under $API_ROOT." >&2
    echo "Add a boot branch here for your backend toolchain (see .claude/rules/techstack.md)." >&2
    exit 1
  fi
  echo $! >> "$PID_FILE"
)

echo "Starting UI in $UI_ROOT on port $UI_PORT ..."
(
  cd "$UI_ROOT"
  if [[ -f package.json ]]; then
    PORT="$UI_PORT" npm run dev &
    echo $! >> "$PID_FILE"
  else
    # Jinja templates are served by the Flask API process; no separate UI server to start.
    echo "UI in $UI_ROOT is served by the Flask app (no package.json); skipping separate UI process."
  fi
)

echo "Stack starting. Run scripts/verify-stack-health.sh before /run-tests E2E."
