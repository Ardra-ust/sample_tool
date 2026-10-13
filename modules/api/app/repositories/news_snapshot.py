"""Snapshot repository: reads the latest snapshot row (FR-023, FR-034).

Each refresh adds one row to the snapshot table and rows are never deleted (DQ-016). The read takes
the highest id. The table name is checked as a plain identifier before it is placed in SQL.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.db import check_identifier


class NewsSnapshotRepository:
    """Reads the most recent snapshot row."""

    def __init__(self, engine: Engine, table: str) -> None:
        check_identifier(table, "snapshot table name")
        self._engine = engine
        self._table = table

    def latest(self) -> dict[str, Any] | None:
        """Return {"news": <JSON text>, "updated_at": <datetime>} for the newest row, or None."""
        statement = text(f"SELECT news, updated_at FROM {self._table} ORDER BY id DESC LIMIT 1")
        with self._engine.connect() as connection:
            row = connection.execute(statement).mappings().first()
        return dict(row) if row is not None else None
