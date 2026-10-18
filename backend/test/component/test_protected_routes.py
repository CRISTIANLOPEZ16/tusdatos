from datetime import datetime, timedelta, timezone
import jwt
import pytest
from app.infrastructure.config.dependencies import get_token_adapter
pytestmark = pytest.mark.anyio


@pytest.mark.parametrize(
    'authorization',
    ['Basic credentials', 'Bearer', 'Bearer malformed']
)
async def test_missing_or_malformed_credentials_are_rejected(
    client,
    authorization
):
    headers = {'Authorization': authorization}
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
