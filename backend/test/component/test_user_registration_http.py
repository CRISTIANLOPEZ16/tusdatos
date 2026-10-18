from httpx import AsyncClient
import pytest
pytestmark = pytest.mark.anyio


@pytest.mark.parametrize(
    'payload,field',
    [
        ({'email': 'invalid', 'password': 'password123'}, 'email'),
        ({'email': 'user@example.com', 'password': 'short'}, 'password'),
        ({'email': 'user@example.com'}, 'password'),
        ({'password': 'password123'}, 'email')
    ]
)
async def test_invalid_input_returns_422_without_invoking_use_case(
    client: AsyncClient,
    registration_use_case,
    payload,
    field
):
    response = await client.post('/users/register', json=payload)
    assert response.status_code == 422
    errors = response.json()['detail']
    assert any((error['loc'][-1] == field for error in errors))
    registration_use_case.execute.assert_not_awaited()
