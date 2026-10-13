"""Refresh status repository: the single status row and the atomic refresh lock.

Implements BR-015 (atomic lock, one refresh at a time), BR-016 (stale-lock clearance)
and NFR-004. The table name comes from REFRESH_STATUS_TABLE and is checked as a plain
identifier before it is placed in SQL. Values always travel as bound parameters.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")

STALE_MESSAGE: str = "Worker likely died; stale lock cleared."  # BR-016


class RefreshStatusRepository:
    """Reads and writes the one status row (FR-040, FR-043)."""

    def __init__(self, engine: Engine, table: str, row_id: int) -> None:
        if not _IDENTIFIER.match(table):
            raise ValueError("REFRESH_STATUS_TABLE must be a plain table name")
        self._engine = engine
        self._table = table
        self._row_id = row_id

    def try_acquire(self, now: datetime) -> bool:
        """Take the lock in one conditional UPDATE (running 0 -> 1).

        Returns True only for the caller whose UPDATE changed the row. Two concurrent
        callers cannot both get True (BR-015).
        """
        statement = text(
            f"UPDATE {self._table} "
            "SET running = 1, started_at = :now, finished_at = NULL, "
            "    message = NULL, trace = NULL, updated_at = :now "
            "WHERE id = :row_id AND running = 0"
        )
        with self._engine.begin() as connection:
            result = connection.execute(statement, {"now": now, "row_id": self._row_id})
            return result.rowcount == 1

    def clear_stale(self, now: datetime, cutoff: datetime) -> bool:
        """Clear a lock held since before cutoff (BR-016). Returns True when a lock was cleared."""
        statement = text(
            f"UPDATE {self._table} "
            "SET running = 0, finished_at = :now, message = :message, updated_at = :now "
            "WHERE id = :row_id AND running = 1 AND started_at < :cutoff"
        )
        with self._engine.begin() as connection:
            result = connection.execute(
                statement,
                {"now": now, "message": STALE_MESSAGE, "row_id": self._row_id, "cutoff": cutoff},
            )
            return result.rowcount == 1

    def finish(self, now: datetime, message: str | None, trace: str | None = None) -> None:
        """Clear the running flag and record the end time, message and any trace (FR-040)."""
        statement = text(
            f"UPDATE {self._table} "
            "SET running = 0, finished_at = :now, message = :message, trace = :trace, "
            "    updated_at = :now "
            "WHERE id = :row_id"
        )
        with self._engine.begin() as connection:
            connection.execute(
                statement,
                {"now": now, "message": message, "trace": trace, "row_id": self._row_id},
            )

    def read(self) -> dict[str, Any] | None:
        """Return the status row as a dict, or None when the row is missing."""
        statement = text(
            f"SELECT running, started_at, finished_at, message, trace, last_run_type "
            f"FROM {self._table} WHERE id = :row_id"
        )
        with self._engine.connect() as connection:
            row = connection.execute(statement, {"row_id": self._row_id}).mappings().first()
        return dict(row) if row is not None else None
