from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum as SQLAlchemyEnum,
    Index,
    Text,
    column,
    func,
)
from sqlmodel import Field, Relationship, SQLModel

from app.domain.entities.event_status import EventStatus


if TYPE_CHECKING:
    from app.infrastructure.persistence.models.session import Session


class Event(SQLModel, table=True):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint(
            "ends_at > starts_at",
            name="ck_events_dates",
        ),
        Index(
            "ix_events_name_trgm",
            func.lower(column("name")).label("name_lower"),
            postgresql_using="gin",
            postgresql_ops={"name_lower": "gin_trgm_ops"},
        ),
        Index(
            "uq_events_identity",
            "created_by",
            func.lower(func.btrim(column("name"))).label("normalized_name"),
            func.lower(func.btrim(column("address"))).label(
                "normalized_address"
            ),
            "starts_at",
            "ends_at",
            unique=True,
        ),
    )

    event_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=3, max_length=150)
    description: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    address: str = Field(min_length=5, max_length=150)
    starts_at: datetime = Field(sa_type=DateTime(timezone=True))
    ends_at: datetime = Field(sa_type=DateTime(timezone=True))
    status: EventStatus = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                EventStatus,
                name="event_status",
                values_callable=lambda enum: [member.value for member in enum],
                validate_strings=True,
            ),
            nullable=False,
        ),
    )
    created_by: int = Field(foreign_key="users.user_id")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )

    sessions: list["Session"] = Relationship(
        back_populates="event",
        sa_relationship_kwargs={
            "lazy": "raise",
            "order_by": "Session.starts_at, Session.session_id",
        },
    )
