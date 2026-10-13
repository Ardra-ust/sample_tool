"""Application factory for the AI News Agent (Flask, Python 3.11+).

The Flask app lives in modules/api. Jinja templates and static files live in
modules/ui/templates and modules/ui/static, so both folders are passed explicitly.
Settings come from .env through app.config (FR-042).
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask

from app.config import Settings, load_settings
from app.db import make_engine
from app.repositories.refresh_status import RefreshStatusRepository
from app.routes.health import health_bp
from app.routes.refresh import build_refresh_blueprint
from app.services.refresh import RefreshService

# This file is modules/api/app/factory.py: parents[0] is app/, parents[1] is modules/api/,
# parents[2] is modules/. The UI root is therefore modules/ui.
UI_ROOT: Path = Path(__file__).resolve().parents[2] / "ui"


def create_app(settings: Settings | None = None, service: RefreshService | None = None) -> Flask:
    """Build the Flask app. Tests pass their own settings or service; the default reads .env.

    Building the engine does not connect to MySQL, so importing the app has no side effects.
    """
    app = Flask(
        "app",
        template_folder=str(UI_ROOT / "templates"),
        static_folder=str(UI_ROOT / "static"),
    )
    if service is None:
        settings = settings if settings is not None else load_settings()
        repository = RefreshStatusRepository(
            make_engine(settings),
            settings.refresh_status_table,
            settings.refresh_status_row_id,
        )
        service = RefreshService(repository, settings)

    app.register_blueprint(health_bp)
    app.register_blueprint(build_refresh_blueprint(service))
    return app
