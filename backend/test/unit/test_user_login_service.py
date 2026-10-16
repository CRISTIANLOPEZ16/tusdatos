from unittest.mock import create_autospec

import pytest

from app.application.ports.login_use_case import InvalidCredentialsError
from app.application.ports.password_hasher_port import PasswordHasherPort
from app.application.ports.token_issuer_port import TokenIssuerPort
from app.application.services.login_service import LoginService
from app.domain.entities.user import User
from app.domain.ports.user_repository_port import UserRepositoryPort

pytestmark = pytest.mark.anyio


@pytest.fixture
def repository():
    return create_autospec(
        UserRepositoryPort, instance=True, spec_set=True,
    )


@pytest.fixture
def verifier():
    return create_autospec(
        PasswordHasherPort, instance=True, spec_set=True,
    )


@pytest.fixture
def tokens():
    return create_autospec(
        TokenIssuerPort, instance=True, spec_set=True,
    )


@pytest.fixture
def service(repository, verifier, tokens):
    return LoginService(
        repository=repository,
        password_verifier=verifier,
        token=tokens,
    )


async def test_valid_credentials_issue_token_for_persisted_user(
    service, repository, verifier, tokens,
):
    repository.get_by_email.return_value = User(
        user_id=7,
        email="user@example.com",
        password_hash="stored-hash",
    )
    verifier.verify_password.return_value = True
    tokens.issue.return_value = "issued-token"

    result = await service.execute(
        " USER@example.com ", "ExamplePassword123!",
    )

    assert result == "issued-token"
    repository.get_by_email.assert_awaited_once_with("user@example.com")
    verifier.verify_password.assert_awaited_once_with(
        "ExamplePassword123!", "stored-hash",
    )
    tokens.issue.assert_called_once_with(7)


@pytest.mark.parametrize("exists", [True, False])
async def test_invalid_credentials_never_issue_token(
    service, repository, verifier, tokens, exists,
):
    repository.get_by_email.return_value = (
        User(
            user_id=7,
            email="user@example.com",
            password_hash="stored-hash",
        )
        if exists else None
    )
    verifier.verify_password.return_value = False

    with pytest.raises(InvalidCredentialsError):
        await service.execute(
            "user@example.com", "incorrect-password",
        )

    verifier.verify_password.assert_awaited_once_with(
        "incorrect-password",
        "stored-hash" if exists else None,
    )
    tokens.issue.assert_not_called()


async def test_invalid_email_does_not_query_repository(
    service, repository, verifier, tokens,
):
    with pytest.raises(InvalidCredentialsError):
        await service.execute("invalid-email", "ExamplePassword123!")

    repository.get_by_email.assert_not_awaited()
    verifier.verify_password.assert_not_awaited()
    tokens.issue.assert_not_called()