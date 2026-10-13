"""Create new_data and refresh_status; seed the status row with "Ready".

Revision ID: 0001
Revises:
Create Date: 2026-10-13

Additive only. The downgrade is refused: migrations are forward-only (techstack.md),
and dropping tables would destroy snapshot rows, which are never deleted (DQ-016).
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "new_data",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("news", mysql.LONGTEXT(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "refresh_status",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("running", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("last_run_type", sa.String(length=64), nullable=True),
        sa.Column("trace", mysql.LONGTEXT(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # FR-044: the status row is created with a "Ready" message when missing.
    op.execute(
        sa.text(
            "INSERT INTO refresh_status (id, running, message, updated_at) "
            "VALUES (1, 0, 'Ready', CURRENT_TIMESTAMP)"
        )
    )


def downgrade() -> None:
    raise NotImplementedError(
        "0001 downgrade is refused: migrations are forward-only and the tables hold "
        "snapshot rows that are never deleted (DQ-016). Requires a human decision."
    )
