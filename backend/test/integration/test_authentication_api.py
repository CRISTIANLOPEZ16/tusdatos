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
    return f"user-{uuid4().hex}@example.com"


async def test_registration_stores_hash_and_rejects_normalized_duplicate(
    api_client, db_session, email,
):
    response = await api_client.post("/users/register", json={
        "email": email.upper(),
        "password": "ExamplePassword123!",
    })
    duplicate = await api_client.post("/users/register", json={
        "email": email,
        "password": "ExamplePassword123!",
    })

    assert response.status_code == 201
    assert response.json()["email"] == email
    assert "password" not in response.json()
    assert "password_hash" not in response.json()
    assert duplicate.status_code == 409

    rows = (
        await db_session.scalars(
            select(User).where(User.email == email),
        )
    ).all()

    assert len(rows) == 1
    assert rows[0].user_id == response.json()["user_id"]
    assert await PasswordHasherAdapter().verify_password(
        "ExamplePassword123!",
        rows[0].password_hash,
    )


async def test_registered_user_can_login_and_receive_valid_token(
    api_client, email,
):
    registration = await api_client.post("/users/register", json={
        "email": email,
        "password": "ExamplePassword123!",
    })
    assert registration.status_code == 201

    response = await api_client.post("/auth/login", json={
        "email": email.upper(),
        "password": "ExamplePassword123!",
    })

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert "password" not in body
    assert "password_hash" not in body

    settings = Settings()
    tokens = JWTTokenAdapter(
        secret=settings.JWT_SECRET_KEY,
        expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        algorith=settings.ALGORITHM,
    )
    assert tokens.get_user_id(body["access_token"]) == (
        registration.json()["user_id"]
    )


async def test_unknown_user_and_wrong_password_receive_same_error(
    api_client, email,
):
    registration = await api_client.post("/users/register", json={
        "email": email,
        "password": "ExamplePassword123!",
    })
    assert registration.status_code == 201

    wrong_password = await api_client.post("/auth/login", json={
        "email": email,
        "password": "incorrect-password",
    })
    unknown_user = await api_client.post("/auth/login", json={
        "email": f"missing-{uuid4().hex}@example.com",
        "password": "incorrect-password",
    })

    assert wrong_password.status_code == 401
    assert unknown_user.status_code == 401
    assert unknown_user.json() == wrong_password.json()
    assert unknown_user.headers["www-authenticate"] == "Bearer"
    assert "access_token" not in unknown_user.json()


async def test_invalid_registration_does_not_create_user(
    api_client, db_session, email,
):
    response = await api_client.post("/users/register", json={
        "email": email,
        "password": "short",
    })

    assert response.status_code == 422
    stored_id = await db_session.scalar(
        select(User.user_id).where(User.email == email),
    )
    assert stored_id is None