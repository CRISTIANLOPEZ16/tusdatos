import pytest
from app.application.ports.session_use_cases import GetSessionUseCase
from app.domain.errors.session import SessionNotFoundError
from app.infrastructure.config.dependencies import get_session_service
from unittest.mock import create_autospec
pytestmark = pytest.mark.anyio


async def test_session_not_found_maps_to_404(client, app):
    use_case = create_autospec(GetSessionUseCase, instance=True, spec_set=True)
    use_case.get_session.side_effect = SessionNotFoundError('No existe')
    app.dependency_overrides[get_session_service] = lambda: use_case
    response = await client.get('/events/10/sessions/20')
    assert response.status_code == 404
    assert response.json() == {'detail': 'No existe'}


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
