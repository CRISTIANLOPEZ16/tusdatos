from datetime import datetime, timezone
from unittest.mock import create_autospec

import pytest

from app.application.ports.register_user_use_case import (
    InvalidRegistrationError,
)
from app.application.services.register_user_service import RegisterUserService
from app.domain.entities.user import User
from app.application.ports.password_hasher_port import (
    PasswordHasherPort,
)
from app.application.ports.transaction_port import TransactionPort
from app.domain.ports.user_repository_port import (
    EmailAlreadyExistsError,
    UserRepositoryPort,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def repository():
    return create_autospec(UserRepositoryPort, instance=True, spec_set=True)


@pytest.fixture
def transaction():
    return create_autospec(TransactionPort, instance=True, spec_set=True)


@pytest.fixture
def hasher():
    mock = create_autospec(PasswordHasherPort, instance=True, spec_set=True)
    mock.hash.return_value = 'hashed-password'
    return mock


@pytest.fixture
def registered_user():
    return User(
        user_id=1, email='user@example.com', password_hash='hashed-password',
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def service(repository, transaction, hasher, registered_user):
    repository.add.return_value = registered_user
    return RegisterUserService(repository, transaction, hasher)


async def test_registration_returns_public_user_and_commits(
    service, transaction, registered_user,
):
    result = await service.execute('user@example.com', 'password123')

    assert result.user_id == registered_user.user_id
    assert result.email == registered_user.email
    assert result.created_at == registered_user.created_at
    assert not hasattr(result, 'password_hash')
    transaction.commit.assert_awaited_once()
    transaction.rollback.assert_not_awaited()


async def test_registration_persists_normalized_email_and_hashed_password(
    service, repository, hasher,
):
    await service.execute(' USER@example.com ', 'password123')

    hasher.hash.assert_awaited_once_with('password123')
    repository.add.assert_awaited_once()
    persisted = repository.add.await_args.args[0]
    assert persisted.email == 'user@example.com'
    assert persisted.password_hash == 'hashed-password'
    assert persisted.password_hash != 'password123'


@pytest.mark.parametrize('error', [EmailAlreadyExistsError(), OSError('db')])
async def test_persistence_failure_rolls_back_and_propagates(
    service, repository, transaction, error,
):
    repository.add.side_effect = error

    with pytest.raises(type(error)) as raised:
        await service.execute('user@example.com', 'password123')

    assert raised.value is error
    transaction.rollback.assert_awaited_once()
    transaction.commit.assert_not_awaited()


async def test_commit_failure_requests_rollback(service, transaction):
    transaction.commit.side_effect = OSError('commit failed')

    with pytest.raises(OSError, match='commit failed'):
        await service.execute('user@example.com', 'password123')

    transaction.rollback.assert_awaited_once()


async def test_hash_failure_does_not_write(
    service, hasher, repository, transaction,
):
    hasher.hash.side_effect = RuntimeError('hash failed')

    with pytest.raises(RuntimeError, match='hash failed'):
        await service.execute('user@example.com', 'password123')

    repository.add.assert_not_awaited()
    transaction.commit.assert_not_awaited()
    transaction.rollback.assert_not_awaited()


async def test_repository_without_assigned_id_causes_rollback(
    service, repository, transaction,
):
    repository.add.return_value = User(
        email='user@example.com', password_hash='hashed-password',
    )

    with pytest.raises(RuntimeError, match='without an ID'):
        await service.execute('user@example.com', 'password123')

    transaction.rollback.assert_awaited_once()
    transaction.commit.assert_not_awaited()


@pytest.mark.parametrize('email,password', [
    ('invalid', 'password123'),
    ('', 'password123'),
    ('user@example.com', 'short'),
])
async def test_invalid_input_does_not_hash_or_write(
    service, repository, transaction, hasher, email, password,
):
    with pytest.raises(InvalidRegistrationError):
        await service.execute(email, password)

    hasher.hash.assert_not_awaited()
    repository.add.assert_not_awaited()
    transaction.commit.assert_not_awaited()
    transaction.rollback.assert_not_awaited()
