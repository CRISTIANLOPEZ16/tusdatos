from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.event import Event
from app.domain.entities.event_status import EventStatus
from app.domain.errors.event import EventConflictError
from app.infrastructure.persistence.models.event import Event as EventModel
from app.infrastructure.persistence.models.registration import Registration
from app.infrastructure.persistence.models.session import (
    Session as SessionModel,
)
from app.infrastructure.persistence.repositories import (
    session_repository_adapter,
)


class EventRepositoryAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _query():
        return select(EventModel).execution_options(populate_existing=True)

    @staticmethod
    def _to_domain(
        row: EventModel,
        *,
        include_sessions: bool = False,
    ) -> Event:
        sessions = None
        if include_sessions:
            sessions = tuple(
                session_repository_adapter.SessionRepositoryAdapter.to_domain(
                    session,
                )
                for session in row.sessions
            )

        return Event(
            event_id=row.event_id,
            name=row.name,
            description=row.description,
            address=row.address,
            starts_at=row.starts_at,
            ends_at=row.ends_at,
            status=row.status,
            created_by=row.created_by,
            created_at=row.created_at,
            sessions=sessions,
        )

    @staticmethod
    def _values(event: Event) -> dict:
        return {
            "name": event.name,
            "description": event.description,
            "address": event.address,
            "starts_at": event.starts_at,
            "ends_at": event.ends_at,
            "status": event.status,
            "created_by": event.created_by,
            "created_at": event.created_at,
        }

    async def get_by_id(
        self,
        event_id: int,
        *,
        include_sessions: bool = False,
        for_update: bool = False,
    ) -> Event | None:
        query = self._query().where(EventModel.event_id == event_id)
        if include_sessions:
            query = query.options(
                selectinload(EventModel.sessions).selectinload(
                    SessionModel.speakers
                )
            )
        if for_update:
            query = query.with_for_update(of=EventModel)

        row = await self.session.scalar(query)
        if row is None:
            return None
        return self._to_domain(row, include_sessions=include_sessions)

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
        query = self._query()

        if name is not None:
            query = query.where(
                func.lower(EventModel.name).icontains(name, autoescape=True)
            )

        if user_id is not None:
            query = query.where(EventModel.created_by == user_id)

        if statuses is not None:
            query = query.where(EventModel.status.in_(statuses))

        if registered_user_id is not None:
            registered_ids = select(SessionModel.event_id).join(
                Registration
            ).where(
                Registration.user_id == registered_user_id
            )
            query = query.where(EventModel.event_id.in_(registered_ids))

        count_result = await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        rows = await self.session.scalars(
            query.order_by(EventModel.event_id).limit(limit).offset(offset)
        )
        return [self._to_domain(row) for row in rows], total

    async def add(self, event: Event) -> Event:
        row = EventModel(**self._values(event))
        self.session.add(row)
        await self._flush()

        if row.event_id is None:
            raise RuntimeError("El evento persistido no tiene ID")

        saved = await self.get_by_id(row.event_id)
        if saved is None:
            raise RuntimeError("No se pudo recuperar el evento creado")
        return saved

    async def _flush(self) -> None:
        try:
            await self.session.flush()
        except IntegrityError as exc:
            original = exc.orig
            sqlstate = getattr(original, "sqlstate", None)
            constraint = getattr(
                getattr(original, "diag", None),
                "constraint_name",
                None,
            )
            if sqlstate == "23503":
                raise EventConflictError(
                    'Un registro relacionado ya no existe'
                ) from exc

            if sqlstate == "23505" and constraint == "uq_events_identity":
                raise EventConflictError(
                    'Ya existe un evento con el mismo nombre, dirección y '
                    'horario para el mismo usuario'
                ) from exc
            raise

    async def exists_duplicate(self, event: Event) -> bool:
        query = select(EventModel.event_id).where(
            func.lower(func.btrim(EventModel.name))
            == func.lower(func.btrim(event.name)),
            func.lower(func.btrim(EventModel.address))
            == func.lower(func.btrim(event.address)),
            EventModel.starts_at == event.starts_at,
            EventModel.ends_at == event.ends_at,
            EventModel.created_by == event.created_by
        )

        if event.event_id is not None:
            query = query.where(
                EventModel.event_id != event.event_id
            )

        return await self.session.scalar(select(query.exists()))

    async def update(self, event: Event) -> Event:
        row = await self.session.get(EventModel, event.event_id)
        if row is None:
            raise RuntimeError("El evento bloqueado ya no existe")
        for key, value in self._values(event).items():
            setattr(row, key, value)
        await self._flush()
        return self._to_domain(row)

    async def delete(self, event_id: int) -> None:
        await self.session.execute(
            delete(EventModel).where(EventModel.event_id == event_id)
        )
        await self._flush()
