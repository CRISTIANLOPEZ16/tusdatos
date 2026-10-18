from app.application.dto.session import ListedSessions
from app.application.ports.session_use_cases import (
    ListRegisteredSessionsUseCase,
)
from app.infrastructure.config.dependencies import get_session_service
from datetime import datetime, timedelta, timezone
from unittest.mock import create_autospec
import jwt
import pytest
from app.application.ports.login_use_case import LoginUseCase
from app.infrastructure.config.dependencies import get_login, get_token_adapter
pytestmark = pytest.mark.anyio


async def test_login_token_grants_access_to_identity(client, app):
    tokens = get_token_adapter()
    login = create_autospec(LoginUseCase, instance=True, spec_set=True)
    login.execute.return_value = tokens.issue(7)
    app.dependency_overrides[get_login] = lambda: login
    response = await client.post(
        '/auth/login',
        json={'email': 'user@example.com', 'password': 'ExamplePassword123!'}
    )
    assert response.status_code == 200
    sessions = create_autospec(
        ListRegisteredSessionsUseCase,
        instance=True,
        spec_set=True
    )
    sessions.list_registered_sessions.return_value = ListedSessions(
        [],
        0,
        1,
        10
    )
    app.dependency_overrides[get_session_service] = lambda: sessions
    identity = await client.get(
        '/users/me/sessions',
        headers={'Authorization': f"Bearer {response.json()['access_token']}"}
    )
    assert identity.status_code == 200
    assert identity.json(
    ) == {'items': [], 'total': 0, 'page': 1, 'items_per_page': 10}
    sessions.list_registered_sessions.assert_awaited_once_with(
        7,
        page=1,
        items_per_page=10
    )


@pytest.mark.parametrize(
    'authorization',
    [None, 'Basic credentials', 'Bearer', 'Bearer malformed']
)
async def test_missing_or_malformed_credentials_are_rejected(
    client,
    authorization
):
    headers = {
        'Authorization': authorization
    } if authorization is not None else {}
    response = await client.get('/users/me/sessions', headers=headers)
    assert response.status_code == 401
    assert response.headers['www-authenticate'] == 'Bearer'
    assert response.json() == {'detail': 'Invalid or expired token'}


@pytest.mark.parametrize(
    'failure',
    ['expired', 'signature', 'subject', 'missing_exp', 'algorithm']
)
async def test_invalid_jwt_cannot_access_protected_route(client, failure):
    tokens = get_token_adapter()
    now = datetime.now(timezone.utc)
    claims = {
        'sub': '7',
        'iat': now - timedelta(minutes=2),
        'exp': now + timedelta(minutes=1)
    }
    secret = tokens.secret
    algorithm = tokens.algorithm
    if failure == 'expired':
        claims['exp'] = now - timedelta(minutes=1)
    elif failure == 'signature':
        secret = 'different-test-key-' + 'x' * 64
    elif failure == 'subject':
        claims['sub'] = '0'
    elif failure == 'missing_exp':
        del claims['exp']
    elif failure == 'algorithm':
        algorithm = 'HS512'
    token = jwt.encode(claims, secret, algorithm=algorithm)
    response = await client.get(
        '/users/me/sessions',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 401
    assert response.headers['www-authenticate'] == 'Bearer'
    assert response.json() == {'detail': 'Invalid or expired token'}
