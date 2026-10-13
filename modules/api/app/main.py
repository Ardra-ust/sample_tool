"""Flask entry point for the AI News Agent.

The Flask app lives in modules/api. Its Jinja templates and static files live in
modules/ui/templates and modules/ui/static, so both folders are passed explicitly.
Boot with: flask --app app.main:app run --reload (from modules/api).
"""

from pathlib import Path

from flask import Flask

# This file is modules/api/app/main.py: parents[0] is app/, parents[1] is modules/api/,
# parents[2] is modules/. The UI root is therefore modules/ui.
UI_ROOT = Path(__file__).resolve().parents[2] / "ui"

app = Flask(
    __name__,
    template_folder=str(UI_ROOT / "templates"),
    static_folder=str(UI_ROOT / "static"),
)


@app.get("/health")
def health() -> tuple[str, int]:
    """Health check used by scripts/verify-stack-health.sh."""
    return "OK", 200
