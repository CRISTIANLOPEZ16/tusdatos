import asyncio
import pytest
from app.application.dto.session import SessionData
from app.application.services.session_service import SessionService
from app.domain.errors.session import SessionConflictError
from app.infrastructure.persistence.models import (
    Registration,
    Session,
    SessionSpeaker,
    Speaker,
)
from app.infrastructure.persistence.repositories import (
    event_repository_adapter as event_repo,
    session_repository_adapter as session_repo,
    user_repository_adapter as user_repo,
)
from datetime import timedelta
from sqlalchemy import func, select
pytestmark = pytest.mark.anyio


def service(db):
    return SessionService(
        session_repo.SessionRepositoryAdapter(db),
        event_repo.EventRepositoryAdapter(db),
        user_repo.UserRepositoryAdapter(db),
        db
    )


async def test_new_speaker_is_unique_under_concurrent_creators(
    committed_scenario
):
    factory, users, events, _, marker, start = committed_scenario
    name = 'Nueva ' + marker
    barrier = asyncio.Barrier(2)

    async def create(index):
        async with factory() as db:
            data = SessionData(
                title='Nombre compartido',
                capacity=1,
                starts_at=start + timedelta(hours=4 + index),
                ends_at=start + timedelta(hours=5 + index),
                speaker_names=(name if index == 0 else name.upper(),)
            )
            await barrier.wait()
            return await service(
                db
            ).create_session(events[index], data, users[index])
    results = await asyncio.wait_for(
        asyncio.gather(create(0), create(1)),
        timeout=10
    )
    async with factory() as db:
        speaker_id = await db.scalar(
            select(
                Speaker.speaker_id
            ).where(Speaker.normalized_name == name.casefold())
        )
        assert speaker_id is not None
        count = await db.scalar(
            select(func.count()).select_from(Speaker).where(
                Speaker.normalized_name == name.casefold(),
            ),
        )
        assert count == 1
        session_ids = [result.session_id for result in results]
        ids = (await db.scalars(
            select(SessionSpeaker.speaker_id).where(
                SessionSpeaker.session_id.in_(session_ids),
            ),
        )).all()
        assert ids == [speaker_id, speaker_id]


async def test_capacity_reduction_and_registration_preserve_capacity(
    committed_scenario
):
    factory, users, events, session_id, _, start = committed_scenario
    async with factory() as db:
        row = await db.get(Session, session_id)
        row.capacity = 2
        db.add(Registration(session_id=session_id, user_id=users[1]))
        await db.commit()
    data = SessionData(
        title='Último cupo',
        capacity=1,
        starts_at=start + timedelta(hours=1),
        ends_at=start + timedelta(hours=2)
    )
    barrier = asyncio.Barrier(2)

    async def change(register):
        async with factory() as db:
            await barrier.wait()
            try:
                if register:
                    await service(
                        db
                    ).register_to_session(events[0], session_id, users[2])
                else:
                    await service(
                        db
                    ).update_session(events[0], session_id, data, users[0])
                return 'ok'
            except SessionConflictError:
                return 'conflict'
    outcomes = await asyncio.wait_for(
        asyncio.gather(change(True), change(False)),
        timeout=10
    )
    assert sorted(outcomes) == ['conflict', 'ok']
    async with factory() as db:
        capacity = await db.scalar(
            select(Session.capacity).where(Session.session_id == session_id)
        )
        count = await db.scalar(
            select(func.count()).select_from(Registration).where(
                Registration.session_id == session_id,
            ),
        )
        assert count <= capacity
