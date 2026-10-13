"""Refresh routes: start (FR-035, FR-036) and status (FR-037). Contract operations startRefresh and getRefreshStatus.

The 500 response has an empty body: the sources do not define an error body (contract open question OQ-API-1).
No stack trace or secret is returned to the client. Status responses send no-cache headers (NFR-002).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from flask import Blueprint, Response, jsonify

from app.services.news import format_time
from app.services.refresh import RefreshService, RefreshStartError


def status_body(row: dict[str, Any] | None) -> dict[str, Any]:
    """Shape the status row for the contract (RefreshStatus). No trace is returned."""
    if row is None:
        return {"running": False, "started_at": None, "finished_at": None, "message": None, "last_run_type": None}
    return {
        "running": bool(row.get("running")),
        "started_at": format_time(row.get("started_at")),
        "finished_at": format_time(row.get("finished_at")),
        "message": row.get("message"),
        "last_run_type": row.get("last_run_type"),
    }


def build_refresh_blueprint(
    service: RefreshService,
    read_status: Callable[[], dict[str, Any] | None],
) -> Blueprint:
    """Create the refresh Blueprint around one RefreshService and one status reader."""
    refresh_bp: Blueprint = Blueprint("refresh", __name__)

    @refresh_bp.post("/api/refresh")
    def start_refresh() -> Response | tuple[str, int]:
        try:
            status = service.start()
        except RefreshStartError:
            return "", 500
        return jsonify({"status": status}), 200

    @refresh_bp.get("/api/refresh/status")
    def refresh_status() -> Response:
        response = jsonify(status_body(read_status()))
        response.headers["Cache-Control"] = "no-cache"
        return response

    return refresh_bp
