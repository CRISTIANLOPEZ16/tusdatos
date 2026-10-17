from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.session import Session
from app.domain.errors.session import SessionConflictError
from app.infrastructure.persistence.models.registration import Registration
from app.infrastructure.persistence.models.session import (
    Session as SessionModel,
)
from app.infrastructure.persistence.models.session_speaker import (
    SessionSpeaker,
)
from app.infrastructure.persistence.models.speaker import Speaker


class SessionRepositoryAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def to_domain(row: SessionModel) -> Session:
        return Session(
            session_id=row.session_id, event_id=row.event_id, title=row.title,
            starts_at=row.starts_at, ends_at=row.ends_at,
            capacity=row.capacity,
            registered_count=row.registered_count,
            speaker_names=tuple(speaker.name for speaker in row.speakers),
        )

    @staticmethod
    def _query():
        return select(SessionModel).options(
            selectinload(SessionModel.speakers)
        ).execution_options(populate_existing=True)

    @staticmethod
    def _values(session: Session) -> dict:
        return {"event_id": session.event_id, "title": session.title,
                "starts_at": session.starts_at, "ends_at": session.ends_at,
                "capacity": session.capacity}

    async def get_by_id(self, event_id: int, session_id: int, *,
                        for_update: bool = False) -> Session | None:
        query = self._query().where(
            SessionModel.event_id == event_id,
            SessionModel.session_id == session_id,
        )
        if for_update:
            query = query.with_for_update(of=SessionModel)
        row = await self.session.scalar(query)
        return None if row is None else self.to_domain(row)

    async def list_sessions(self, *, event_id: int | None, limit: int,
                            offset: int, registered_user_id: int | None = None
                            ) -> tuple[list[Session], int]:
        query = self._query()
        if event_id is not None:
            query = query.where(SessionModel.event_id == event_id)
        if registered_user_id is not None:
            registered = select(Registration.session_id).where(
                Registration.user_id == registered_user_id
            )
            query = query.where(SessionModel.session_id.in_(registered))
        total = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        )
        rows = await self.session.scalars(query.order_by(
            SessionModel.starts_at, SessionModel.session_id
        ).limit(limit).offset(offset))
        return [self.to_domain(row) for row in rows], total

    async def _flush(self) -> None:
        try:
            await self.session.flush()
        except IntegrityError as exc:
            sqlstate = getattr(exc.orig, "sqlstate", None)
            constraint = getattr(
                getattr(exc.orig, "diag", None), "constraint_name", None,
            )
            if sqlstate == "23505" and constraint == "registrations_pkey":
                raise SessionConflictError("La inscripción ya existe") from exc
            if sqlstate == "23503":
                raise SessionConflictError(
                    "Un registro relacionado no existe"
                ) from exc
            raise

    async def _save_speakers(self, session: Session) -> None:
        await self.session.execute(delete(SessionSpeaker).where(
            SessionSpeaker.session_id == session.session_id
        ))
        query = select(Speaker.speaker_id).where(Speaker.normalized_name.in_(
            [name.casefold() for name in session.speaker_names]
        ))
        speaker_ids = (await self.session.scalars(query)).all()
        if len(speaker_ids) != len(session.speaker_names):
            raise RuntimeError(
                "Los ponentes deben resolverse antes de guardar"
            )
        self.session.add_all([
            SessionSpeaker(
                session_id=session.session_id, speaker_id=speaker_id,
            )
            for speaker_id in speaker_ids
        ])
        await self._flush()

    async def add(self, session: Session) -> Session:
        row = SessionModel(**self._values(session))
        self.session.add(row)
        await self._flush()
        session.session_id = row.session_id
        await self._save_speakers(session)
        return await self.get_by_id(session.event_id, row.session_id)

    async def update(self, session: Session) -> Session:
        row = await self.session.get(SessionModel, session.session_id)
        if row is None:
            raise RuntimeError("La sesión bloqueada ya no existe")
        for key, value in self._values(session).items():
            setattr(row, key, value)
        await self._flush()
        await self._save_speakers(session)
        return await self.get_by_id(session.event_id, session.session_id)

    async def delete(self, session_id: int) -> None:
        await self.session.execute(delete(SessionSpeaker).where(
            SessionSpeaker.session_id == session_id
        ))
        await self.session.execute(delete(SessionModel).where(
            SessionModel.session_id == session_id
        ))
        await self._flush()

    async def count_registrations(self, session_id: int) -> int:
        return await self.session.scalar(select(func.count()).select_from(
            Registration
        ).where(Registration.session_id == session_id))

    async def is_registered(self, session_id: int, user_id: int) -> bool:
        query = select(Registration).where(
            Registration.session_id == session_id,
            Registration.user_id == user_id,
        )
        return await self.session.scalar(select(query.exists()))

    async def register(self, session_id: int, user_id: int) -> None:
        self.session.add(Registration(
            session_id=session_id, user_id=user_id,
        ))
        await self._flush()

    async def lock_speakers(self, speaker_names: tuple[str, ...]) -> None:
        names = {name.casefold(): name for name in speaker_names}
        # Crear y bloquear en el mismo orden también protege nombres nuevos.
        for key in sorted(names):
            await self.session.execute(insert(Speaker).values(
                name=names[key], normalized_name=key,
            ).on_conflict_do_nothing(
                constraint="uq_speakers_normalized_name",
            ))
            await self.session.scalar(select(Speaker.speaker_id).where(
                Speaker.normalized_name == key
            ).with_for_update())

    async def has_speaker_overlap(self, session: Session) -> bool:
        query = select(SessionModel.session_id).join(SessionSpeaker).join(
            Speaker
        ).where(
            Speaker.normalized_name.in_(
                [name.casefold() for name in session.speaker_names]
            ),
            SessionModel.starts_at < session.ends_at,
            SessionModel.ends_at > session.starts_at,
        )
        if session.session_id is not None:
            query = query.where(SessionModel.session_id != session.session_id)
        return await self.session.scalar(select(query.exists()))
