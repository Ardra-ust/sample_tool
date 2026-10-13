"""Refresh start route (FR-035, FR-036). Contract operation startRefresh.

The 500 response has an empty body: the sources do not define an error body (contract open question OQ-API-1).
No stack trace or secret is returned to the client.
"""

from __future__ import annotations

from flask import Blueprint, Response, jsonify

from app.services.refresh import RefreshService, RefreshStartError


def build_refresh_blueprint(service: RefreshService) -> Blueprint:
    """Create the refresh Blueprint around one RefreshService."""
    refresh_bp: Blueprint = Blueprint("refresh", __name__)

    @refresh_bp.post("/api/refresh")
    def start_refresh() -> Response | tuple[str, int]:
        try:
            status = service.start()
        except RefreshStartError:
            return "", 500
        return jsonify({"status": status}), 200

    return refresh_bp
