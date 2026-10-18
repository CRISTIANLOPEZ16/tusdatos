import pytest
from app.infrastructure.security.password_hasher_adapter import (
    PasswordHasherAdapter,
)


@pytest.mark.anyio
async def test_verification_accepts_correct_password_and_rejects_wrong_one():
    hasher = PasswordHasherAdapter()
    hashed = await hasher.hash('password123')
    assert await hasher.verify_password('password123', hashed)
    assert not await hasher.verify_password('wrong-password', hashed)
