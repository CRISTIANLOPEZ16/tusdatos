from app.domain.entities.user import User
from app.infrastructure.persistence.models.user import User as UserModel
from app.infrastructure.persistence.repositories import user_repository_adapter

from sqlalchemy import select
from uuid import uuid4
import pytest


pytestmark =pytest.mark.anyio

async def test_outer_rollback_removes_session_committed_inser(database_engine, database_connection, sessions_factory):
    email = f"isolation-{uuid4().hex}@example.com"
    async with sessions_factory() as session:
        repository = user_repository_adapter.UserRepositoryAdapter(session)
        await repository.add(User(email=email, password_hash='isolation-tes-hash'))
        await session.commit()
    transaction = database_connection.get_transaction()
    assert transaction is not None
    await transaction.rollback()

    async with database_engine.connect() as observer :
        result = await observer.execute(select(UserModel.user_id).where(UserModel.email == email))
        assert result.scalar_one_or_none() is None

    