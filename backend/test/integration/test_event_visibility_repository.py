import pytest
pytestmark = pytest.mark.anyio


async def test_public_event_list_hides_draft_and_archived(
    visibility_events,
    api_client
):
    response = await api_client.get(
        '/events',
        params={'name': visibility_events['prefix']}
    )
    assert response.status_code == 200
    assert response.json()['total'] == 3
    assert {
        row['status'] for row in response.json()['items']
    } == {'activo', 'cancelado', 'finalizado'}
