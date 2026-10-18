import pytest
pytestmark = pytest.mark.anyio


@pytest.mark.parametrize(
    'method,path',
    [
        ('POST', '/events'),
        ('PUT', '/events/10'),
        ('DELETE', '/events/10'),
        ('POST', '/events/10/sessions'),
        ('PUT', '/events/10/sessions/20'),
        ('DELETE', '/events/10/sessions/20'),
        ('POST', '/events/10/sessions/20/registrations'),
        ('GET', '/users/me/events'),
        ('GET', '/users/me/registered-events'),
        ('GET', '/users/me/sessions')
    ]
)
async def test_mutations_and_private_lists_require_token(client, method, path):
    response = await client.request(method, path)
    assert response.status_code == 401
    assert response.headers['www-authenticate'] == 'Bearer'
