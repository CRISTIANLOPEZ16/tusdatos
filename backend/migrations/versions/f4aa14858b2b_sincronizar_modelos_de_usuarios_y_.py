"""Sincronizar modelos de usuarios y eventos

Revision ID: f4aa14858b2b
Revises: d510c7cedc74
Create Date: 2026-10-15 12:40:46.512266

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = 'f4aa14858b2b'
down_revision: Union[str, Sequence[str], None] = '228a5d21d3e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'events', 'description', existing_type=sa.VARCHAR(),
        type_=sa.Text(), existing_nullable=True,
    )
    op.drop_column('users', 'name')
    op.drop_column('users', 'last_name')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('users', sa.Column(
        'last_name', sa.VARCHAR(), autoincrement=False, nullable=True,
    ))
    op.add_column('users', sa.Column(
        'name', sa.VARCHAR(), autoincrement=False, nullable=True,
    ))
    op.alter_column(
        'events', 'description', existing_type=sa.Text(),
        type_=sa.VARCHAR(), existing_nullable=True,
    )
