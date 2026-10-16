from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Text, Column
from sqlmodel import Field, SQLModel


class Event(SQLModel, table=True):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_events_capacity"),
        CheckConstraint("ends_at > starts_at", name="ck_events_dates"),
    )

    event_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=3, max_length=150)
    description: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True),
    )
    starts_at: datetime = Field(sa_type=DateTime(timezone=True))
    ends_at: datetime = Field(sa_type=DateTime(timezone=True))
    capacity: int
    status_id: int = Field(foreign_key="status.status_id")
    created_by: int = Field(foreign_key="users.user_id")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
