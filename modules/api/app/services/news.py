"""News read service: the latest-snapshot response (FR-034; contract operation getNews).

Times are formatted as YYYY-MM-DD HH:MM:SS (NFR-003). The stored news value is a JSON array of articles;
it is returned as stored. The article shape is the one the pipeline writes (FR-024; built in SP-04 to SP-08).
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Protocol

TIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"


class SnapshotSource(Protocol):
    """The part of the snapshot repository the service uses."""

    def latest(self) -> dict[str, Any] | None: ...


class NewsSnapshotError(ValueError):
    """Raised when the stored snapshot is not a JSON array. The route returns HTTP 500 with no body."""


def format_time(value: Any) -> str | None:
    """Format a stored time for the API; None stays None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime(TIME_FORMAT)
    return str(value)


class NewsService:
    """Builds the response for GET /api/news."""

    def __init__(self, source: SnapshotSource) -> None:
        self._source = source

    def latest_snapshot(self) -> dict[str, Any]:
        """Return {count, results, fetched_at}. With no snapshot: count 0 and an empty list (FR-034)."""
        row = self._source.latest()
        if row is None:
            return {"count": 0, "results": [], "fetched_at": None}
        results = json.loads(row["news"])
        if not isinstance(results, list):
            raise NewsSnapshotError("stored snapshot is not a JSON array")
        return {
            "count": len(results),
            "results": results,
            "fetched_at": format_time(row.get("updated_at")),
        }
