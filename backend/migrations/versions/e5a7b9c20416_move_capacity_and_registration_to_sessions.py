"""Move capacity and registrations to sessions.

Revision ID: e5a7b9c20416
Revises: d47b8c209a31
"""
from alembic import op
import sqlalchemy as sa

revision = "e5a7b9c20416"
down_revision = "d47b8c209a31"
branch_labels = None
depends_on = None


def _require_empty_registrations() -> None:
    # Una inscripción al evento no identifica la sesión elegida por el usuario.
    count = op.get_bind().scalar(sa.text("SELECT count(*) FROM registrations"))
    if count:
        raise RuntimeError(
            "Hay inscripciones existentes. Define y migra explícitamente su "
            "sesión de destino antes de cambiar registrations; no se borrarán "
            "ni se asignarán automáticamente."
        )


def upgrade() -> None:
    op.execute("LOCK TABLE registrations IN ACCESS EXCLUSIVE MODE")
    _require_empty_registrations()
    op.drop_constraint("registrations_event_id_fkey", "registrations",
                       type_="foreignkey")
    op.drop_constraint("registrations_pkey", "registrations", type_="primary")
    op.drop_column("registrations", "event_id")
    op.add_column("registrations", sa.Column(
        "session_id", sa.Integer(), nullable=False,
    ))
    op.create_primary_key("registrations_pkey", "registrations",
                          ["session_id", "user_id"])
    op.create_foreign_key("registrations_session_id_fkey", "registrations",
                          "sessions", ["session_id"], ["session_id"])
    op.drop_constraint("ck_events_capacity", "events", type_="check")
    op.drop_column("events", "capacity")


def downgrade() -> None:
    op.execute("LOCK TABLE registrations IN ACCESS EXCLUSIVE MODE")
    _require_empty_registrations()
    op.drop_constraint("registrations_session_id_fkey", "registrations",
                       type_="foreignkey")
    op.drop_constraint("registrations_pkey", "registrations", type_="primary")
    op.drop_column("registrations", "session_id")
    op.add_column("registrations", sa.Column(
        "event_id", sa.Integer(), nullable=False,
    ))
    op.create_primary_key("registrations_pkey", "registrations",
                          ["event_id", "user_id"])
    op.create_foreign_key("registrations_event_id_fkey", "registrations",
                          "events", ["event_id"], ["event_id"])
    op.add_column("events", sa.Column(
        "capacity", sa.Integer(), nullable=True,
    ))
    # El valor anterior se perdió: restauramos un mínimo válido.
    op.execute("""
        UPDATE events SET capacity = COALESCE(
            (SELECT max(capacity) FROM sessions
             WHERE sessions.event_id = events.event_id), 1
        )
    """)
    op.alter_column("events", "capacity", nullable=False)
    op.create_check_constraint("ck_events_capacity", "events", "capacity > 0")
