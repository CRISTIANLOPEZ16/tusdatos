from typing import Protocol

from app.application.dto.event import (
    EventData, EventDetails, EventSummary, ListedEvents,
)
from app.domain.entities.event_status import EventStatus
from app.domain.errors.event import EventError


class InvalidEventQueryError(EventError):
    pass


class CreateEventUseCase(Protocol):
    async def create_event(
        self,
        data: EventData,
        creator_id: int,
    ) -> EventSummary:
        ...


class ListEventUseCase(Protocol):
    async def list_events_available(
        self,
        *,
        page: int,
        items_per_page: int,
        name: str | None = None,
    ) -> ListedEvents:
        ...


class ListEventUserUseCase(Protocol):
    async def list_all_me_events(
        self,
        *,
        user_id: int,
        page: int,
        items_per_page: int,
        name: str | None = None,
    ) -> ListedEvents:
        ...


class GetEventUseCase(Protocol):
    async def get_event_by_event_id(self, event_id: int) -> EventDetails: ...


class UpdateEventUseCase(Protocol):
    async def update_event(self, event_id: int, data: EventData,
                           user_id: int) -> EventSummary: ...


class DeleteEventUseCase(Protocol):
    async def delete_event(self, event_id: int, user_id: int) -> None: ...


class ListRegisteredEventsUseCase(Protocol):
    async def list_registered_events(self, user_id: int, *, page: int,
                                     items_per_page: int,
                                     name: str | None = None,
                                     statuses: list[EventStatus] | None = None,
                                     ) -> ListedEvents: ...
