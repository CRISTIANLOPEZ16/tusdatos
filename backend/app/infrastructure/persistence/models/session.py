from datetime import datetime
from typing import ClassVar, TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, func, select
from sqlalchemy.orm import column_property
from sqlmodel import Field, Relationship, SQLModel

from app.infrastructure.persistence.models.registration import Registration
from app.infrastructure.persistence.models.session_speaker import (
    SessionSpeaker,
)


if TYPE_CHECKING:
    from app.infrastructure.persistence.models.event import Event
    from app.infrastructure.persistence.models.speaker import Speaker


class Session(SQLModel, table=True):
    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_sessions_capacity"),
        CheckConstraint(
            "ends_at > starts_at",
            name="ck_sessions_dates",
        ),
    )

    session_id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(
        foreign_key="events.event_id",
        index=True,
    )
    title: str
    starts_at: datetime = Field(sa_type=DateTime(timezone=True))
    ends_at: datetime = Field(sa_type=DateTime(timezone=True))
    capacity: int
    registered_count: ClassVar[int]

    event: "Event" = Relationship(
        back_populates="sessions",
        sa_relationship_kwargs={"lazy": "raise"},
    )

    speakers: list["Speaker"] = Relationship(
        link_model=SessionSpeaker,
        sa_relationship_kwargs={"lazy": "raise"},
    )


# SQLModel debe mapear session_id antes de registrar esta expresión.
Session.__mapper__.add_property(
    "registered_count",
    column_property(
        select(func.count(Registration.user_id))
        .where(Registration.session_id == Session.session_id)
        .correlate_except(Registration)
        .scalar_subquery()
    ),
)
