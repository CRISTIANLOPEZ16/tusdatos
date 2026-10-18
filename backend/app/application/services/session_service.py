from dataclasses import asdict
from datetime import datetime, timezone

from app.application.dto.session import (
    ListedSessions, SessionData, SessionDetails, SessionRegistration,
)
from app.application.ports.transaction_port import TransactionPort
from app.domain.entities.session import Session
from app.domain.errors.event import EventNotFoundError
from app.domain.errors.session import InvalidSessionError, SessionNotFoundError
from app.domain.errors.user import UserNotFoundError
from app.domain.ports.event_repository_port import EventRepositoryPort
from app.domain.ports.session_repository_port import SessionRepositoryPort
from app.domain.ports.user_repository_port import UserRepositoryPort


class SessionService:
    def __init__(self, repository: SessionRepositoryPort,
                 events: EventRepositoryPort, users: UserRepositoryPort,
                 transaction: TransactionPort) -> None:
        self.repository = repository
        self.events = events
        self.users = users
        self.transaction = transaction

    async def _require_user(self, user_id: int) -> None:
        if await self.users.get_by_id(user_id) is None:
            raise UserNotFoundError("El usuario autenticado ya no existe")

    async def _get_event(self, event_id: int, *, for_update: bool = False):
        event = await self.events.get_by_id(event_id, for_update=for_update)
        if event is None:
            raise EventNotFoundError("El evento no existe")
        return event

    async def _get_session(self, event_id: int, session_id: int, *,
                           for_update: bool = False) -> Session:
        session = await self.repository.get_by_id(
            event_id, session_id, for_update=for_update,
        )
        if session is None:
            raise SessionNotFoundError(
                'La sesión no pertenece al evento o no existe'
            )
        return session

    async def _list(self, *, event_id: int | None, page: int,
                    items_per_page: int,
                    registered_user_id: int | None = None) -> ListedSessions:
        if page < 1 or not 1 <= items_per_page <= 100:
            raise InvalidSessionError("Paginación inválida")
        sessions, total = await self.repository.list_sessions(
            event_id=event_id, limit=items_per_page,
            offset=(page - 1) * items_per_page,
            registered_user_id=registered_user_id,
        )
        return ListedSessions(
            [SessionDetails.from_session(session) for session in sessions],
            total, page, items_per_page,
        )

    async def list_sessions(self, event_id: int, *, page: int,
                            items_per_page: int) -> ListedSessions:
        await self._get_event(event_id)
        return await self._list(event_id=event_id, page=page,
                                items_per_page=items_per_page)

    async def list_registered_sessions(self, user_id: int, *, page: int,
                                       items_per_page: int) -> ListedSessions:
        await self._require_user(user_id)
        return await self._list(event_id=None, page=page,
                                items_per_page=items_per_page,
                                registered_user_id=user_id)

    async def get_session(self, event_id: int,
                          session_id: int) -> SessionDetails:
        await self._get_event(event_id)
        return SessionDetails.from_session(
            await self._get_session(event_id, session_id)
        )

    async def _validate_speakers(
        self, session: Session, *, previous_names: tuple[str, ...] = (),
    ) -> None:
        await self.repository.lock_speakers(
            previous_names + session.speaker_names
        )
        session.ensure_speakers_available(
            overlap=await self.repository.has_speaker_overlap(session),
        )

    async def create_session(self, event_id: int, data: SessionData,
                             user_id: int) -> SessionDetails:
        try:
            await self._require_user(user_id)
            event = await self._get_event(event_id, for_update=True)
            event.ensure_owned_by(user_id)
            session = Session(event_id=event_id, **asdict(data))
            session.ensure_fits(event.starts_at, event.ends_at)
            await self._validate_speakers(session)
            saved = await self.repository.add(session)
            result = SessionDetails.from_session(saved)
            await self.transaction.commit()
            return result
        except Exception:
            await self.transaction.rollback()
            raise

    async def update_session(self, event_id: int, session_id: int,
                             data: SessionData, user_id: int
                             ) -> SessionDetails:
        try:
            await self._require_user(user_id)
            event = await self._get_event(event_id, for_update=True)
            event.ensure_owned_by(user_id)
            current = await self._get_session(
                event_id, session_id, for_update=True,
            )
            session = Session(event_id=event_id, session_id=session_id,
                              **asdict(data))
            session.ensure_fits(event.starts_at, event.ends_at)
            session.ensure_capacity_for(
                await self.repository.count_registrations(session_id)
            )
            await self._validate_speakers(
                session, previous_names=current.speaker_names,
            )
            saved = await self.repository.update(session)
            result = SessionDetails.from_session(saved)
            await self.transaction.commit()
            return result
        except Exception:
            await self.transaction.rollback()
            raise

    async def delete_session(self, event_id: int, session_id: int,
                             user_id: int) -> None:
        try:
            await self._require_user(user_id)
            event = await self._get_event(event_id, for_update=True)
            event.ensure_owned_by(user_id)
            session = await self._get_session(
                event_id, session_id, for_update=True,
            )
            session.ensure_can_delete(
                await self.repository.count_registrations(session_id)
            )
            await self.repository.lock_speakers(session.speaker_names)
            await self.repository.delete(session_id)
            await self.transaction.commit()
        except Exception:
            await self.transaction.rollback()
            raise

    async def register_to_session(self, event_id: int, session_id: int,
                                  user_id: int) -> SessionRegistration:
        try:
            await self._require_user(user_id)
            event = await self._get_event(event_id, for_update=True)
            session = await self._get_session(
                event_id, session_id, for_update=True,
            )
            session.ensure_can_register(
                registered_count=await self.repository.count_registrations(
                    session_id,
                ),
                already_registered=await self.repository.is_registered(
                    session_id, user_id,
                ),
                event_status=event.status, now=datetime.now(timezone.utc),
            )
            await self.repository.register(session_id, user_id)
            await self.transaction.commit()
            return SessionRegistration(event_id, session_id, user_id)
        except Exception:
            await self.transaction.rollback()
            raise
