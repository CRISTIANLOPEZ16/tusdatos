from dataclasses import asdict, dataclass
from datetime import datetime

from app.application.dto.session import SessionDetails
from app.domain.entities.event import Event
from app.domain.entities.event_status import EventStatus


@dataclass(frozen=True)
class EventData:
    name: str
    description: str | None
    address: str
    starts_at: datetime
    ends_at: datetime
    status: EventStatus


@dataclass(frozen=True)
class EventSummary:
    event_id: int
    name: str
    description: str | None
    address: str
    starts_at: datetime
    ends_at: datetime
    status: EventStatus
    created_by: int
    created_at: datetime

    @classmethod
    def from_event(cls, event: Event) -> "EventSummary":
        if event.event_id is None:
            raise RuntimeError("El evento persistido no tiene ID")

        return cls(
            event_id=event.event_id,
            name=event.name,
            description=event.description,
            address=event.address,
            starts_at=event.starts_at,
            ends_at=event.ends_at,
            status=event.status,
            created_by=event.created_by,
            created_at=event.created_at,
        )


@dataclass(frozen=True)
class EventDetails(EventSummary):
    sessions: list[SessionDetails]

    @classmethod
    def from_event(cls, event: Event) -> "EventDetails":
        summary = EventSummary.from_event(event)

        return cls(
            **asdict(summary),
            sessions=[
                SessionDetails.from_session(session)
                for session in event.sessions
            ],
        )


@dataclass(frozen=True)
class ListedEvents:
    items: list[EventSummary]
    total: int
    page: int
    items_per_page: int
