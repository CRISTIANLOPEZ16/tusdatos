from dataclasses import asdict

from app.application.dto.event import (
    EventData,
    EventDetails,
    EventSummary,
    ListedEvents,
)
from app.application.ports.event_use_cases import InvalidEventQueryError
from app.application.ports.transaction_port import TransactionPort
from app.domain.entities.event import Event
from app.domain.entities.event_status import EventStatus
from app.domain.errors.event import EventNotFoundError
from app.domain.errors.user import UserNotFoundError
from app.domain.ports.event_repository_port import EventRepositoryPort
from app.domain.ports.user_repository_port import UserRepositoryPort


class EventService:
    def __init__(
        self,
        repository: EventRepositoryPort,
        users: UserRepositoryPort,
        transaction: TransactionPort,
    ) -> None:
        self.repository = repository
        self.users = users
        self.transaction = transaction

    async def _require_user(self, user_id: int) -> None:
        if await self.users.get_by_id(user_id) is None:
            raise UserNotFoundError(
                "El usuario autenticado ya no existe"
            )

    async def _list(
        self, *, page: int, items_per_page: int, name: str | None,
        registered_user_id: int | None = None,
        statuses: list[EventStatus] | None = None,
        user_id: int | None = None,
    ) -> ListedEvents:
        if page < 1:
            raise InvalidEventQueryError(
                'La página debe ser mayor o igual a 1'
            )

        if not 1 <= items_per_page <= 100:
            raise InvalidEventQueryError(
                'La cantidad por página debe estar entre 1 y 100'
            )

        if name is not None and not 1 <= len(name) <= 150:
            raise InvalidEventQueryError(
                'La búsqueda debe contener entre 1 y 150 caracteres'
            )

        events, total = await self.repository.list_events(
            limit=items_per_page,
            offset=(page - 1) * items_per_page,
            name=name,
            registered_user_id=registered_user_id,
            statuses=statuses,
            user_id=user_id,
        )

        return ListedEvents(
            items=[EventSummary.from_event(event) for event in events],
            total=total,
            page=page,
            items_per_page=items_per_page,
        )

    async def list_events_available(
        self,
        *,
        page: int,
        items_per_page: int,
        name: str | None = None,
    ) -> ListedEvents:
        statuses = [
            EventStatus.ACTIVE, EventStatus.CANCELLED, EventStatus.FINISHED,
        ]
        return await self._list(
            page=page,
            items_per_page=items_per_page,
            name=name,
            statuses=statuses,
        )

    async def list_all_me_events(
        self,
        *,
        user_id: int,
        page: int,
        items_per_page: int,
        name: str | None = None,
    ) -> ListedEvents:
        await self._require_user(user_id)
        return await self._list(
            page=page,
            items_per_page=items_per_page,
            name=name,
            user_id=user_id,
        )

    async def create_event(
        self,
        data: EventData,
        creator_id: int,
    ) -> EventSummary:
        try:
            await self._require_user(creator_id)

            event = Event(
                **asdict(data),
                created_by=creator_id,
            )
            already_exists = await self.repository.exists_duplicate(event)
            event.ensure_not_duplicate(already_exists)

            saved = await self.repository.add(event)
            result = EventSummary.from_event(saved)

            await self.transaction.commit()
            return result
        except Exception:
            await self.transaction.rollback()
            raise

    async def _get_event(self, event_id: int, *, for_update: bool = False,
                         include_sessions: bool = False) -> Event:
        event = await self.repository.get_by_id(
            event_id, for_update=for_update, include_sessions=include_sessions,
        )
        if event is None:
            raise EventNotFoundError("El evento no existe")
        return event

    async def get_event_by_event_id(self, event_id: int) -> EventDetails:
        event = await self._get_event(event_id, include_sessions=True)
        return EventDetails.from_event(event)

    async def update_event(self, event_id: int, data: EventData,
                           user_id: int) -> EventSummary:
        try:
            await self._require_user(user_id)
            current = await self._get_event(
                event_id, for_update=True, include_sessions=True,
            )
            current.ensure_owned_by(user_id)
            event = Event(**asdict(data), event_id=event_id,
                          created_by=current.created_by,
                          created_at=current.created_at,
                          sessions=current.sessions)
            event.ensure_not_duplicate(
                await self.repository.exists_duplicate(event)
            )
            saved = await self.repository.update(event)
            result = EventSummary.from_event(saved)
            await self.transaction.commit()
            return result
        except Exception:
            await self.transaction.rollback()
            raise

    async def delete_event(self, event_id: int, user_id: int) -> None:
        try:
            await self._require_user(user_id)
            event = await self._get_event(
                event_id, for_update=True, include_sessions=True,
            )
            event.ensure_owned_by(user_id)
            event.ensure_can_delete()
            await self.repository.delete(event_id)
            await self.transaction.commit()
        except Exception:
            await self.transaction.rollback()
            raise

    async def list_registered_events(self, user_id: int, *, page: int,
                                     items_per_page: int,
                                     name: str | None = None,
                                     statuses: list[EventStatus] | None = None,
                                     ) -> ListedEvents:
        await self._require_user(user_id)
        return await self._list(page=page, items_per_page=items_per_page,
                                name=name, registered_user_id=user_id,
                                statuses=statuses)
