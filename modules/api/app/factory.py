"""Application factory for the AI News Agent (Flask, Python 3.11+).

The Flask app lives in modules/api. Jinja templates and static files live in
modules/ui/templates and modules/ui/static, so both folders are passed explicitly.
Settings come from .env through app.config (FR-042).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Flask

from app.config import Settings, load_settings
from app.db import make_engine
from app.repositories.news_snapshot import NewsSnapshotRepository
from app.repositories.refresh_status import RefreshStatusRepository
from app.routes.health import health_bp
from app.routes.news import build_news_blueprint
from app.routes.pages import pages_bp
from app.routes.refresh import build_refresh_blueprint
from app.services.news import NewsService
from app.services.refresh import RefreshService

# This file is modules/api/app/factory.py: parents[0] is app/, parents[1] is modules/api/,
# parents[2] is modules/. The UI root is therefore modules/ui.
UI_ROOT: Path = Path(__file__).resolve().parents[2] / "ui"
SNAPSHOT_TABLE: str = "new_data"  # BRD §7


def create_app(
    settings: Settings | None = None,
    service: RefreshService | None = None,
    status_repository: Any | None = None,
    snapshot_repository: Any | None = None,
) -> Flask:
    """Build the Flask app. Tests pass fakes or their own settings; the default reads .env.

    Building an engine does not connect to MySQL, so importing the app has no side effects.
    """
    app = Flask(
        "app",
        template_folder=str(UI_ROOT / "templates"),
        static_folder=str(UI_ROOT / "static"),
    )
    if settings is None:
        settings = load_settings()
    if status_repository is None or snapshot_repository is None:
        engine = make_engine(settings)
        if status_repository is None:
            status_repository = RefreshStatusRepository(
                engine,
                settings.refresh_status_table,
                settings.refresh_status_row_id,
            )
        if snapshot_repository is None:
            snapshot_repository = NewsSnapshotRepository(engine, SNAPSHOT_TABLE)
    if service is None:
        service = RefreshService(status_repository, settings)

    app.register_blueprint(pages_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(build_refresh_blueprint(service, status_repository.read))
    app.register_blueprint(build_news_blueprint(NewsService(snapshot_repository)))
    return app
