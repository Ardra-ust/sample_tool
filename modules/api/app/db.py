"""Database engine for the MySQL database (FR-044; DQ-A6).

Connection settings come from the Settings object, which is read from .env (FR-042).
create_engine does not connect, so building the engine has no side effects.
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine

from app.config import Settings


def database_url(settings: Settings) -> URL:
    """Build the MySQL URL from settings. No credentials are written in code."""
    return URL.create(
        "mysql+mysqlconnector",
        username=settings.mysql_user,
        password=settings.mysql_password,
        host=settings.mysql_host,
        database=settings.mysql_database,
    )


def make_engine(settings: Settings) -> Engine:
    """Create the SQLAlchemy engine. Connections are opened only when used."""
    return create_engine(database_url(settings), pool_pre_ping=True)
