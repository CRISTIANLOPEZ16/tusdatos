from uuid import uuid4
import pytest
from sqlalchemy import select
from app.infrastructure.config.settings import Settings
from app.infrastructure.persistence.models.user import User
from app.infrastructure.security.jwt_token_adapter import JWTTokenAdapter
from app.infrastructure.security.password_hasher_adapter import (
    PasswordHasherAdapter,
)
pytestmark = pytest.mark.anyio


@pytest.fixture
def email():
    return f'user-{uuid4().hex}@example.com'


async def test_registration_stores_hash_and_rejects_normalized_duplicate(
    api_client,
    db_session,
    email
):
    response = await api_client.post(
        '/users/register',
        json={'email': email.upper(), 'password': 'ExamplePassword123!'}
    )
    duplicate = await api_client.post(
        '/users/register',
        json={'email': email, 'password': 'ExamplePassword123!'}
    )
    assert response.status_code == 201
    assert response.json()['email'] == email
    assert 'password' not in response.json()
    assert 'password_hash' not in response.json()
    assert duplicate.status_code == 409
    rows = (
        await db_session.scalars(select(User).where(User.email == email))
    ).all()
    assert len(rows) == 1
    assert rows[0].user_id == response.json()['user_id']
    assert await PasswordHasherAdapter(
    ).verify_password('ExamplePassword123!', rows[0].password_hash)


async def test_registered_user_can_login_and_receive_valid_token(
    api_client,
    email
):
    registration = await api_client.post(
        '/users/register',
        json={'email': email, 'password': 'ExamplePassword123!'}
    )
    assert registration.status_code == 201
    response = await api_client.post(
        '/auth/login',
        json={'email': email.upper(), 'password': 'ExamplePassword123!'}
    )
    assert response.status_code == 200
    body = response.json()
    assert body['token_type'] == 'bearer'
    assert 'password' not in body
    assert 'password_hash' not in body
    settings = Settings()
    tokens = JWTTokenAdapter(
        secret=settings.JWT_SECRET_KEY,
        expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        algorithm=settings.ALGORITHM
    )
    assert tokens.get_user_id(
        body['access_token']
    ) == registration.json()['user_id']
    identity = await api_client.get(
        '/users/me/sessions',
        headers={'Authorization': f"Bearer {body['access_token']}"}
    )
    assert identity.status_code == 200
    assert identity.json(
    ) == {'items': [], 'total': 0, 'page': 1, 'items_per_page': 10}
