from datetime import datetime, timedelta, timezone
import jwt
import pytest
from app.application.ports.token_verifier_port import InvalidTokenError
from app.infrastructure.security.jwt_token_adapter import JWTTokenAdapter


@pytest.fixture
def secret():
    return 'test-signing-key-' + 'a' * 64


@pytest.fixture
def tokens(secret):
    return JWTTokenAdapter(secret=secret, expire_minutes=30, algorithm='HS256')


def test_token_identifies_user(tokens):
    assert tokens.get_user_id(tokens.issue(7)) == 7


@pytest.mark.parametrize(
    'subject',
    ['0', '-1', 'abc', '', '٧', '1.0', 7, None, '9' * 5000]
)
def test_invalid_subject_is_rejected(tokens, secret, subject):
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {'sub': subject, 'iat': now, 'exp': now + timedelta(minutes=1)},
        secret,
        algorithm='HS256'
    )
    with pytest.raises(InvalidTokenError):
        tokens.get_user_id(token)
