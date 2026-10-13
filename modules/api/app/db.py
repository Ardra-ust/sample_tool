"""Database engine for the MySQL database (FR-044; DQ-A6).

Connection settings come from the Settings object, which is read from .env (FR-042).
create_engine does not connect, so building the engine has no side effects.
"""

from __future__ import annotations

import re

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine

from app.config import Settings

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")


def check_identifier(name: str, label: str) -> None:
    """Refuse anything but a plain table name before it is placed in SQL."""
    if not _IDENTIFIER.match(name):
        raise ValueError(f"{label} must be a plain table name")


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
