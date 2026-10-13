"""Alembic environment for the AI News Agent (MySQL, database news_app).

Connection settings come from the repo-root .env through python-dotenv. Secrets are
never written to this file. Migrations are additive and forward-only (techstack.md).
"""

import os
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# This file is modules/api/alembic/env.py, so parents[3] is the repo root.
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

config = context.config

# Tables are created by explicit, hand-reviewed migrations, not by model metadata.
target_metadata = None


def database_url() -> URL:
    """Build the MySQL URL from environment variables (no hardcoded credentials)."""
    return URL.create(
        "mysql+mysqlconnector",
        username=os.environ.get("MYSQL_USER", ""),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        host=os.environ.get("MYSQL_HOST", ""),
        database=os.environ.get("MYSQL_DATABASE") or "news_app",
    )


def run_migrations_offline() -> None:
    """Emit SQL without connecting (used for review: alembic upgrade head --sql)."""
    context.configure(
        url=database_url(),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply migrations to the database named in .env."""
    engine = create_engine(database_url())
    with engine.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
