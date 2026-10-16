"""Align the event name length with the persistence model.

Revision ID: a7c9e2f40115
Revises: f4aa14858b2b
"""
from alembic import op
import sqlalchemy as sa

revision = 'a7c9e2f40115'
down_revision = 'f4aa14858b2b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'events', 'name', existing_type=sa.String(),
        type_=sa.String(150), existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'events', 'name', existing_type=sa.String(150),
        type_=sa.String(), existing_nullable=False,
    )
