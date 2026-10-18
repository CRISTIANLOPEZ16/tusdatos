"""Identify shared speakers by normalized name.

Revision ID: f6b8c0d31527
Revises: e5a7b9c20416
"""
from collections import defaultdict

from alembic import op
import sqlalchemy as sa

revision = "f6b8c0d31527"
down_revision = "e5a7b9c20416"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    op.execute(
        "LOCK TABLE sessions, session_speakers, speakers "
        "IN ACCESS EXCLUSIVE MODE"
    )
    groups = defaultdict(list)
    for speaker_id, name in bind.execute(sa.text(
        "SELECT speaker_id, name FROM speakers ORDER BY speaker_id"
    )):
        name = " ".join(name.split())
        if not 1 <= len(name) <= 150:
            raise RuntimeError(
                f"Corrige el nombre del ponente {speaker_id} antes de migrar"
            )
        groups[name.casefold()].append((speaker_id, name))

    overlap_query = sa.text("""
        SELECT a.session_id, b.session_id
        FROM session_speakers a
        JOIN session_speakers b ON a.session_id < b.session_id
        JOIN sessions sa ON sa.session_id = a.session_id
        JOIN sessions sb ON sb.session_id = b.session_id
        WHERE a.speaker_id IN :ids AND b.speaker_id IN :ids
          AND sa.starts_at < sb.ends_at AND sa.ends_at > sb.starts_at
        LIMIT 1
    """).bindparams(sa.bindparam("ids", expanding=True))
    for entries in groups.values():
        if len(entries) > 1:
            ids = [speaker_id for speaker_id, _ in entries]
            overlap = bind.execute(overlap_query, {"ids": ids}).first()
            if overlap is not None:
                raise RuntimeError(
                    f"Los ponentes {ids} tienen sesiones superpuestas "
                    f"{tuple(overlap)}; corrige los horarios antes de unirlos"
                )

    op.add_column("speakers", sa.Column(
        "normalized_name", sa.String(), nullable=True,
    ))
    for key, entries in groups.items():
        canonical_id, name = entries[0]
        if len(entries) > 1:
            duplicate_ids = [speaker_id for speaker_id, _ in entries[1:]]
            bind.execute(sa.text("""
                INSERT INTO session_speakers (session_id, speaker_id)
                SELECT DISTINCT session_id, :canonical_id
                FROM session_speakers WHERE speaker_id IN :ids
                ON CONFLICT DO NOTHING
            """).bindparams(sa.bindparam("ids", expanding=True)), {
                "ids": duplicate_ids, "canonical_id": canonical_id,
            })
            bind.execute(sa.text("""
                DELETE FROM session_speakers WHERE speaker_id IN :ids
            """).bindparams(sa.bindparam("ids", expanding=True)), {
                "ids": duplicate_ids,
            })
            bind.execute(sa.text("""
                DELETE FROM speakers WHERE speaker_id IN :ids
            """).bindparams(sa.bindparam("ids", expanding=True)), {
                "ids": duplicate_ids,
            })
        bind.execute(sa.text("""
            UPDATE speakers SET name = :name, normalized_name = :key
            WHERE speaker_id = :speaker_id
        """), {"name": name, "key": key, "speaker_id": canonical_id})
    op.alter_column("speakers", "normalized_name", nullable=False)
    op.create_unique_constraint(
        "uq_speakers_normalized_name", "speakers", ["normalized_name"],
    )


def downgrade() -> None:
    # Los duplicados unidos no pueden reconstruirse automáticamente.
    op.drop_constraint(
        "uq_speakers_normalized_name", "speakers", type_="unique",
    )
    op.drop_column("speakers", "normalized_name")
