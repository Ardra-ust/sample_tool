"""Latest-snapshot route (FR-034). Contract operation getNews. No-cache headers (NFR-002)."""

from __future__ import annotations

from flask import Blueprint, Response, jsonify

from app.services.news import NewsService, NewsSnapshotError


def build_news_blueprint(service: NewsService) -> Blueprint:
    """Create the news Blueprint around one NewsService."""
    news_bp: Blueprint = Blueprint("news", __name__)

    @news_bp.get("/api/news")
    def get_news() -> Response | tuple[str, int]:
        try:
            body = service.latest_snapshot()
        except NewsSnapshotError:
            return "", 500  # no stack trace or stored content returned to the client
        response = jsonify(body)
        response.headers["Cache-Control"] = "no-cache"
        return response

    return news_bp
