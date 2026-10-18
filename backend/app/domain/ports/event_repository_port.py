from typing import Protocol

from app.domain.entities.event import Event
from app.domain.entities.event_status import EventStatus


class EventRepositoryPort(Protocol):
    async def get_by_id(
        self,
        event_id: int,
        *,
        include_sessions: bool = False,
        for_update: bool = False,
    ) -> Event | None:
        ...

    async def list_events(
        self,
        *,
        limit: int,
        offset: int,
        name: str | None,
        registered_user_id: int | None = None,
        statuses: list[EventStatus] | None = None,
        user_id: int | None = None,
    ) -> tuple[list[Event], int]:
        ...

    async def add(self, event: Event) -> Event:
        ...

    async def update(self, event: Event) -> Event:
        ...

    async def delete(self, event_id: int) -> None:
        ...

    async def exists_duplicate(self, event: Event) -> bool:
        ...
