from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime
from sqlmodel import Field, SQLModel


class Session(SQLModel, table=True):
    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_sessions_capacity"),
        CheckConstraint("ends_at > starts_at", name="ck_sessions_dates"),
    )

    session_id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="events.event_id", index=True)
    title: str
    starts_at: datetime = Field(sa_type=DateTime(timezone=True))
    ends_at: datetime = Field(sa_type=DateTime(timezone=True))
    capacity: int
