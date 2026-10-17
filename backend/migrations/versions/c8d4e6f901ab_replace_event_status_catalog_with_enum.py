"""Replace the event status catalog with a PostgreSQL enum.

Revision ID: c8d4e6f901ab
Revises: 0ec36b17e8b9
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "c8d4e6f901ab"
down_revision = "0ec36b17e8b9"
branch_labels = None
depends_on = None

STATUSES = ("borrador", "activo", "cancelado", "finalizado", "archivado")


def upgrade() -> None:
    op.execute("LOCK TABLE events, status IN ACCESS EXCLUSIVE MODE")
    event_status = postgresql.ENUM(
        *STATUSES, name="event_status", create_type=False,
    )
    event_status.create(op.get_bind())
    op.add_column(
        "events", sa.Column("status", event_status, nullable=True),
    )

    # Invalid legacy names abort the transaction before any catalog is removed.
    op.execute("""
        UPDATE events AS e
        SET status = lower(btrim(s.name))::event_status
        FROM status AS s
        WHERE e.status_id = s.status_id
    """)
    op.alter_column(
        "events", "status", existing_type=event_status, nullable=False,
    )
    op.drop_constraint(
        "events_status_id_fkey", "events", type_="foreignkey",
    )
    op.drop_column("events", "status_id")
    op.drop_table("status")


def downgrade() -> None:
    """Restore a catalog without its former IDs or descriptions."""
    op.execute("LOCK TABLE events IN ACCESS EXCLUSIVE MODE")
    catalog = op.create_table(
        "status",
        sa.Column("status_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("description", sa.String(), nullable=True),
    )
    op.bulk_insert(catalog, [{"name": value} for value in STATUSES])
    op.add_column(
        "events", sa.Column("status_id", sa.Integer(), nullable=True),
    )
    op.execute("""
        UPDATE events AS e
        SET status_id = s.status_id
        FROM status AS s
        WHERE s.name = e.status::text
    """)
    op.alter_column(
        "events", "status_id", existing_type=sa.Integer(), nullable=False,
    )
    op.create_foreign_key(
        "events_status_id_fkey", "events", "status",
        ["status_id"], ["status_id"],
    )
    op.drop_column("events", "status")
    postgresql.ENUM(*STATUSES, name="event_status").drop(op.get_bind())
