import asyncio
import os
from pathlib import Path

from pydantic import Field, TypeAdapter
from sqlalchemy import func, select

from app.domain.entities.event import Event as EventEntity
from app.domain.entities.session import Session as SessionEntity
from app.infrastructure.persistence.database import engine, session_factory
from app.infrastructure.persistence.models import Event, Session, User
from app.infrastructure.persistence.repositories import (
    session_repository_adapter,
)
from app.infrastructure.schemas.event_schema import EventWriteRequest
from app.infrastructure.schemas.session_schema import SessionWriteRequest
from app.infrastructure.security.password_hasher_adapter import (
    PasswordHasherAdapter,
)


class SeedEvent(EventWriteRequest):
    sessions: list[SessionWriteRequest] = Field(default_factory=list)


async def seed() -> None:
    try:
        data_path = Path(__file__).with_name("event_data.json")
        events = TypeAdapter(list[SeedEvent]).validate_json(
            data_path.read_text(encoding="utf-8")
        )

        async with session_factory.begin() as db:
            user = await db.scalar(
                select(User).where(User.email == "demo@example.com")
            )
            if user is None:
                password = os.environ["SEED_PASSWORD"]
                if len(password) < 8:
                    raise ValueError(
                        "SEED_PASSWORD requiere al menos 8 caracteres"
                    )
                user = User(
                    email="demo@example.com",
                    password_hash=await PasswordHasherAdapter().hash(password),
                )
                db.add(user)
                await db.flush()

            if user.user_id is None:
                raise RuntimeError("El usuario persistido no tiene ID")

            repository = session_repository_adapter.SessionRepositoryAdapter(
                db,
            )
            for data in events:
                values = data.model_dump(exclude={"sessions"})
                validated_event = EventEntity(
                    **values, created_by=user.user_id,
                )
                event = await db.scalar(select(Event).where(
                    Event.created_by == user.user_id,
                    func.lower(func.btrim(Event.name))
                    == validated_event.name.lower(),
                    func.lower(func.btrim(Event.address))
                    == validated_event.address.lower(),
                    Event.starts_at == validated_event.starts_at,
                    Event.ends_at == validated_event.ends_at,
                ))

                if event is None:
                    event = Event(
                        **(values | {
                            "name": validated_event.name,
                            "address": validated_event.address,
                        }),
                        created_by=user.user_id,
                    )
                    db.add(event)
                    await db.flush()

                if event.event_id is None:
                    raise RuntimeError("El evento persistido no tiene ID")

                for session_data in data.sessions:
                    session = SessionEntity(
                        event_id=event.event_id, **session_data.model_dump(),
                    )
                    session.ensure_fits(event.starts_at, event.ends_at)
                    existing_id = await db.scalar(select(
                        Session.session_id,
                    ).where(
                        Session.event_id == event.event_id,
                        Session.title == session.title,
                        Session.starts_at == session.starts_at,
                        Session.ends_at == session.ends_at,
                    ))
                    if existing_id is not None:
                        continue

                    await repository.lock_speakers(session.speaker_names)
                    session.ensure_speakers_available(
                        overlap=await repository.has_speaker_overlap(session),
                    )
                    await repository.add(session)

        print("Seed completado.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
