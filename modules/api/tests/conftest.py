"""Shared fixtures for the S1 test package (docs/test-cases.md).

The database is an in-memory SQLite copy of the two tables. It runs the same SQL the repositories use
against MySQL. The browser and the Flask server run locally. No test calls the network or an LLM.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from app.config import Settings


def make_engine(snapshot_rows: list[dict[str, Any]] | None = None, status_running: int = 0) -> Engine:
    """Create the two tables and seed one status row (Ready) and optional snapshot rows."""
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE refresh_status (id INTEGER PRIMARY KEY, running INTEGER NOT NULL DEFAULT 0, "
            "started_at DATETIME, finished_at DATETIME, message TEXT, trace TEXT, last_run_type TEXT, "
            "updated_at DATETIME)"
        ))
        conn.execute(text(
            "INSERT INTO refresh_status (id, running, message, updated_at) VALUES (1, :running, 'Ready', CURRENT_TIMESTAMP)"
        ), {"running": status_running})
        conn.execute(text(
            "CREATE TABLE new_data (id INTEGER PRIMARY KEY AUTOINCREMENT, news TEXT NOT NULL, "
            "updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        ))
        for index, rows in enumerate(snapshot_rows or []):
            conn.execute(text("INSERT INTO new_data (news, updated_at) VALUES (:news, :at)"), {
                "news": json.dumps(rows, ensure_ascii=False),
                "at": datetime(2026, 10, 13, 9, 30 + index, 0),
            })
    return engine


@pytest.fixture
def settings() -> Settings:
    return Settings(refresh_stale_minutes=70)


@pytest.fixture
def clock_time() -> datetime:
    return datetime(2026, 10, 13, 12, 0, 0)
