import pytest

from app.application.ports.register_user_use_case import (
    InvalidRegistrationError,
)
from app.domain.ports.user_repository_port import (
    EmailAlreadyExistsError,
)

pytestmark = pytest.mark.anyio


async def test_registration_returns_201_without_sensitive_fields(client):
    payload = {'email': 'user@example.com', 'password': 'password123'}

    response = await client.post('/users/register', json=payload)

    assert response.status_code == 201
    assert response.json() == {
        'user_id': 1, 'email': 'user@example.com',
        'created_at': '2026-01-01T00:00:00Z',
    }
    assert 'password' not in response.json()
    assert 'password_hash' not in response.json()


async def test_registration_returns_409_when_email_exists(
    client, registration_use_case,
):
    registration_use_case.execute.side_effect = EmailAlreadyExistsError()

    response = await client.post('/users/register', json={
        'email': 'user@example.com', 'password': 'password123',
    })

    assert response.status_code == 409
    assert response.json() == {'detail': 'Email already registered'}


@pytest.mark.parametrize('payload,field', [
    ({'email': 'invalid', 'password': 'password123'}, 'email'),
    ({'email': 'user@example.com', 'password': 'short'}, 'password'),
    ({'email': 'user@example.com'}, 'password'),
    ({'password': 'password123'}, 'email'),
])
async def test_invalid_input_returns_422_without_invoking_use_case(
    client, registration_use_case, payload, field,
):
    response = await client.post('/users/register', json=payload)

    assert response.status_code == 422
    errors = response.json()['detail']
    assert any(error['loc'][-1] == field for error in errors)
    registration_use_case.execute.assert_not_awaited()


async def test_application_validation_error_returns_422(
    client, registration_use_case,
):
    registration_use_case.execute.side_effect = InvalidRegistrationError(
        'Invalid registration input',
    )

    response = await client.post('/users/register', json={
        'email': 'user@example.com', 'password': 'password123',
    })

    assert response.status_code == 422
    assert response.json() == {'detail': 'Invalid registration input'}


async def test_openapi_describes_registration_contract(client):
    response = await client.get('/openapi.json')

    assert response.status_code == 200
    spec = response.json()
    operation = spec['paths']['/users/register']['post']
    assert {'201', '409', '422'} <= operation['responses'].keys()
    assert operation['requestBody']['required']
    schemas = spec['components']['schemas']
    request = schemas['UserCreateRequest']
    assert set(request['required']) == {'email', 'password'}
    password = request['properties']['password']
    assert password['minLength'] == 8
    assert password['writeOnly'] is True
    assert 'password' not in schemas['UserResponse']['properties']
    assert 'password_hash' not in schemas['UserResponse']['properties']
    assert len(
        schemas['RegistrationValidationErrorResponse']['properties']
        ['detail']['anyOf']
    ) == 2


@pytest.mark.parametrize('path', ['/docs', '/redoc'])
async def test_documentation_pages_are_available(client, path):
    response = await client.get(path)

    assert response.status_code == 200
    assert '/openapi.json' in response.text
