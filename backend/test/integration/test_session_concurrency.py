import asyncio

import pytest
from sqlalchemy import func, select

from app.application.services.session_service import SessionService
from app.domain.errors.session import SessionConflictError
from app.infrastructure.persistence.models import Registration
from app.infrastructure.persistence.repositories import (
    event_repository_adapter as event_repo,
    session_repository_adapter as session_repo,
    user_repository_adapter as user_repo,
)

pytestmark = pytest.mark.anyio


def service(db):
    return SessionService(
        session_repo.SessionRepositoryAdapter(db),
        event_repo.EventRepositoryAdapter(db),
        user_repo.UserRepositoryAdapter(db), db,
    )


async def test_only_one_user_gets_last_seat(committed_scenario):
    factory, users, events, session_id, _, _ = committed_scenario
    barrier = asyncio.Barrier(2)

    async def register(user_id):
        async with factory() as db:
            await barrier.wait()
            try:
                await service(db).register_to_session(
                    events[0], session_id, user_id,
                )
                return 'registered'
            except SessionConflictError as exc:
                assert str(exc) == 'La sesión no tiene cupos disponibles'
                return 'full'

    outcomes = await asyncio.wait_for(
        asyncio.gather(register(users[1]), register(users[2])), timeout=10,
    )
    assert sorted(outcomes) == ['full', 'registered']
    async with factory() as db:
        count = await db.scalar(
            select(func.count()).select_from(Registration).where(
                Registration.session_id == session_id,
            ),
        )
        assert count == 1
