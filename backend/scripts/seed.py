import asyncio
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.domain.entities.event_status import EventStatus
from app.infrastructure.persistence.database import engine, session_factory
from app.infrastructure.persistence.models import Event, Session, User
from app.infrastructure.security.password_hasher_adapter import (
    PasswordHasherAdapter,
)

from pathlib import Path

from pydantic import TypeAdapter
from sqlalchemy import func

from app.infrastructure.schemas.event_schema import EventWriteRequest


async def seed() -> None:
    try:
        
        async with session_factory.begin() as db:
            user = await db.scalar(
                select(User).where(User.email == "demo@example.com")
            )
            data_path = Path(__file__).with_name("event_data.json")
            events = TypeAdapter(list[EventWriteRequest]).validate_json(
                data_path.read_text(encoding="utf-8")
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

            for data in events:
                name = data.name.strip()
                address = data.address.strip()

                if data.ends_at <= data.starts_at:
                    raise ValueError(
                        f"El evento '{name}' debe finalizar después de su inicio"
                    )

                event = await db.scalar(
                    select(Event).where(
                        Event.created_by == user.user_id,
                        func.lower(func.btrim(Event.name)) == name.lower(),
                        func.lower(func.btrim(Event.address)) == address.lower(),
                        Event.starts_at == data.starts_at,
                        Event.ends_at == data.ends_at,
                    )
                )

                if event is None:
                    event = Event(
                        **(data.model_dump() | {"name": name, "address": address}),
                        created_by=user.user_id,
                    )
                    db.add(event)
                    await db.flush()

                session = await db.scalar(
                    select(Session).where(
                        Session.event_id == event.event_id,
                        Session.title == "[Demo] Arquitectura hexagonal",
                    )
                )

                if session is None:
                    db.add(Session(
                        event_id=event.event_id,
                        title="[Demo] Arquitectura hexagonal",
                        starts_at=event.starts_at,
                        ends_at=min(
                            event.starts_at + timedelta(hours=1),
                            event.ends_at,
                        ),
                        capacity=30,
                    ))

        print("Seed completado.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())