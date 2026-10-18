import pytest
pytestmark = pytest.mark.anyio


@pytest.mark.parametrize('view', ['event', 'sessions', 'session', 'mine'])
async def test_session_read_views_show_occupancy_after_registration(
    scenario,
    view
):
    s = scenario
    path = f"/events/{s['event_id']}/sessions/{s['session_id']}"
    before = await s['client'].get(path)
    assert before.status_code == 200
    assert before.json()['registered_count'] == 0
    assert before.json()['available_capacity'] == 1
    registration = await s[
        'client'
    ].post(path + '/registrations', headers=s['headers'][1])
    assert registration.status_code == 201
    paths = {
        'event': f"/events/{s['event_id']}",
        'sessions': f"/events/{s['event_id']}/sessions",
        'session': path,
        'mine': '/users/me/sessions'
    }
    response = await s['client'].get(paths[view], headers=s['headers'][1])
    assert response.status_code == 200
    body = response.json()
    if view == 'event':
        rows = body['sessions']
    elif view == 'session':
        rows = [body]
    else:
        rows = body['items']
    row = next((row for row in rows if row['session_id'] == s['session_id']))
    assert (
        row['capacity'],
        row['registered_count'],
        row['available_capacity']
    ) == (1, 1, 0)
