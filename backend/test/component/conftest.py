from unittest.mock import create_autospec
import pytest
from httpx import ASGITransport, AsyncClient
from app.application.ports.register_user_use_case import RegisterUserUseCase


@pytest.fixture
def registration_use_case():
    return create_autospec(
        RegisterUserUseCase,
        instance=True,
        spec_set=True
    )


@pytest.fixture
async def client(app, registration_use_case):
    from app.infrastructure.config.dependencies import get_register_user
    app.dependency_overrides[get_register_user] = lambda: registration_use_case
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    ) as client:
        yield client
