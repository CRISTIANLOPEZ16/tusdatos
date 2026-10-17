from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


class Registration(SQLModel, table=True):
    __tablename__ = "registrations"

    session_id: int = Field(
        foreign_key="sessions.session_id", primary_key=True,
    )
    user_id: int = Field(
        foreign_key="users.user_id", primary_key=True, index=True,
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
