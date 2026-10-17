"""Prevent duplicate events for the same creator.

Revision ID: d47b8c209a31
Revises: c8d4e6f901ab
"""

from alembic import op
import sqlalchemy as sa


revision = "d47b8c209a31"
down_revision = "c8d4e6f901ab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    duplicate_ids = op.get_bind().execute(
        sa.text("""
            SELECT array_agg(event_id ORDER BY event_id)
            FROM events
            GROUP BY
                created_by,
                lower(btrim(name)),
                lower(btrim(address)),
                starts_at,
                ends_at
            HAVING count(*) > 1
            LIMIT 1
        """)
    ).scalar()

    if duplicate_ids is not None:
        raise RuntimeError(
            "Existen eventos duplicados para el mismo creador. "
            f"Corrige primero estos IDs: {duplicate_ids}"
        )

    op.create_index(
        "uq_events_identity",
        "events",
        [
            "created_by",
            sa.text("lower(btrim(name))"),
            sa.text("lower(btrim(address))"),
            "starts_at",
            "ends_at",
        ],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_events_identity", table_name="events")
