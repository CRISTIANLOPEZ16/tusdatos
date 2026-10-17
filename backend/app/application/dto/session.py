from dataclasses import dataclass
from datetime import datetime

from app.domain.entities.session import Session


@dataclass(frozen=True)
class SessionData:
    title: str
    starts_at: datetime
    ends_at: datetime
    capacity: int
    speaker_names: tuple[str, ...] = ()


@dataclass(frozen=True)
class SessionDetails:
    session_id: int
    event_id: int
    title: str
    starts_at: datetime
    ends_at: datetime
    capacity: int
    registered_count: int
    available_capacity: int
    speaker_names: tuple[str, ...]

    @classmethod
    def from_session(cls, session: Session) -> "SessionDetails":
        if session.session_id is None:
            raise RuntimeError("La sesión persistida no tiene ID")
        return cls(
            session_id=session.session_id,
            event_id=session.event_id,
            title=session.title,
            starts_at=session.starts_at,
            ends_at=session.ends_at,
            capacity=session.capacity,
            registered_count=session.registered_count,
            available_capacity=session.available_capacity,
            speaker_names=session.speaker_names,
        )


@dataclass(frozen=True)
class ListedSessions:
    items: list[SessionDetails]
    total: int
    page: int
    items_per_page: int


@dataclass(frozen=True)
class SessionRegistration:
    event_id: int
    session_id: int
    user_id: int
