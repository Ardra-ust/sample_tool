"""Health route (FR-038). Contract operation getHealth: text/plain, body OK."""

from __future__ import annotations

from flask import Blueprint, Response

health_bp: Blueprint = Blueprint("health", __name__)


@health_bp.get("/health")
def health() -> Response:
    """Health check used by scripts/verify-stack-health.sh."""
    return Response("OK", status=200, mimetype="text/plain")
