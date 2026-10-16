from app.domain.entities.user import User
from app.domain.ports.user_repository_port import (
    EmailAlreadyExistsError,
)
from app.infrastructure.persistence.repositories import (
    user_repository_adapter as user_repository_adapter,
)
from app.infrastructure.persistence.models.user import User as UserModel
from uuid import uuid4
from datetime import datetime, timezone

import pytest

pytestmark = pytest.mark.anyio


@pytest.fixture
def user():
    return User(
        email=f'user-{uuid4().hex}@example.com', password_hash='test-hash',
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

async def test_added_user_can_be_loaded_after_session_commit(sessions_factory, user):
    async with sessions_factory() as session:
        repository = user_repository_adapter.UserRepositoryAdapter(session=session)
        saved = await repository.add(user)
        await session.commit()

    async with sessions_factory() as session:
        repository = user_repository_adapter.UserRepositoryAdapter(session=session)
        loaded = await repository.get_by_email(user.email)

    assert loaded is not None
    assert loaded.user_id == saved.user_id
    assert loaded.user_id is not None
    assert loaded.email == saved.email
    assert loaded.password_hash == saved.password_hash
    assert loaded.created_at == saved.created_at

async def test_unkown_email_return_none(db_session):
    repository = user_repository_adapter.UserRepositoryAdapter(db_session)
    loaded = await repository.get_by_email(
        f"missing-{uuid4().hex}@example.com"
    )
    assert loaded is None

async def test_session_rollback_discards_insert(db_session, user):
    repository = user_repository_adapter.UserRepositoryAdapter(db_session)
    await repository.add(user)
    await db_session.rollback()
    assert await repository.get_by_email(user.email) is None

async def test_duplicate_email_raise_contract_error_and_session_recovers(db_session, user):
    repository = user_repository_adapter.UserRepositoryAdapter(db_session)
    await repository.add(user)
    await db_session.commit()
    with pytest.raises(EmailAlreadyExistsError):
        await repository.add(user)
    await db_session.rollback()
    loaded = await repository.get_by_email(user.email)
    assert loaded is not None
    assert loaded.email == user.email