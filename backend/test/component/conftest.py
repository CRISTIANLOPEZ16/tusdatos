from datetime import datetime, timezone
from unittest.mock import create_autospec
import pytest
from httpx import ASGITransport, AsyncClient
from app.application.dto.user import RegisteredUser
from app.application.ports.register_user_use_case import RegisterUserUseCase


@pytest.fixture
def registration_use_case():
    use_case = create_autospec(
        RegisterUserUseCase,
        instance=True,
        spec_set=True
    )
    use_case.execute.return_value = RegisteredUser(
        user_id=1,
        email='user@example.com',
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    return use_case


@pytest.fixture
async def client(app, registration_use_case):
    from app.infrastructure.config.dependencies import get_register_user
    app.dependency_overrides[get_register_user] = lambda: registration_use_case
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    ) as client:
        yield client
