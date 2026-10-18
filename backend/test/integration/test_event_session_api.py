from datetime import timedelta

import pytest
from sqlalchemy import select

from app.infrastructure.persistence.models import Registration, Speaker

pytestmark = pytest.mark.anyio


async def test_duplicate_and_full_registration_leave_one_row(
    scenario, db_session,
):
    s = scenario
    path = f'/events/{s["event_id"]}/sessions/{s["session_id"]}/registrations'
    for index, status in [(1, 201), (1, 409), (2, 409)]:
        response = await s['client'].post(path, headers=s['headers'][index])
        assert response.status_code == status
    registrations = (await db_session.scalars(
        select(Registration).where(
            Registration.session_id == s['session_id'],
        ),
    )).all()
    assert len(registrations) == 1
    assert registrations[0].user_id == s['users'][1].user_id


async def test_session_of_another_event_cannot_be_registered(scenario):
    s = scenario
    other = await s['client'].post(
        '/events', json=s['event_body'], headers=s['headers'][1],
    )
    assert other.status_code == 201
    event_id = other.json()['event_id']
    response = await s['client'].post(
        f'/events/{event_id}/sessions/{s["session_id"]}/registrations',
        headers=s['headers'][1],
    )
    assert response.status_code == 404


async def test_speaker_overlap_is_rejected_and_adjacent_session_allowed(
    scenario,
):
    s = scenario
    path = f'/events/{s["event_id"]}/sessions'
    overlap = await s['client'].post(
        path, json=s['session_body'], headers=s['headers'][0],
    )
    assert overlap.status_code == 409
    body = s['session_body'] | {
        'starts_at': s['session_body']['ends_at'],
        'ends_at': (s['start'] + timedelta(hours=3)).isoformat(),
    }
    adjacent = await s['client'].post(
        path, json=body, headers=s['headers'][0],
    )
    assert adjacent.status_code == 201


async def test_delete_empty_session_preserves_speaker(scenario, db_session):
    s = scenario
    response = await s['client'].delete(
        f'/events/{s["event_id"]}/sessions/{s["session_id"]}',
        headers=s['headers'][0],
    )
    assert response.status_code == 204
    assert response.content == b''
    assert await db_session.get(Speaker, s['speaker_id']) is not None


async def test_two_sessions_produce_one_registered_event(scenario):
    s = scenario
    path = f'/events/{s["event_id"]}/sessions'
    second = await s['client'].post(
        path, json=s['session_body'] | {'speaker_names': []},
        headers=s['headers'][0],
    )
    assert second.status_code == 201
    for session_id in (s['session_id'], second.json()['session_id']):
        response = await s['client'].post(
            f'{path}/{session_id}/registrations', headers=s['headers'][1],
        )
        assert response.status_code == 201
    mine = await s['client'].get(
        '/users/me/registered-events', headers=s['headers'][1],
        params={'name': s['event_body']['name'], 'items_per_page': 1},
    )
    assert mine.status_code == 200
    assert mine.json()['total'] == 1
    event_ids = [item['event_id'] for item in mine.json()['items']]
    assert event_ids == [s['event_id']]
    assert 'sessions' not in mine.json()['items'][0]
    for index, expected_ids in [(0, [s['event_id']]), (1, [])]:
        created = await s['client'].get(
            '/users/me/events', headers=s['headers'][index],
            params={'name': s['event_body']['name']},
        )
        assert created.status_code == 200
        assert created.json()['total'] == len(expected_ids)
        assert [
            item['event_id'] for item in created.json()['items']
        ] == expected_ids
    for personal_path in ('/users/me/registered-events', '/users/me/sessions'):
        other = await s['client'].get(personal_path, headers=s['headers'][2],)
        assert other.status_code == 200
        assert other.json()['total'] == 0
        assert other.json()['items'] == []


async def test_registered_session_and_parent_event_cannot_be_deleted(scenario):
    s = scenario
    path = f'/events/{s["event_id"]}/sessions/{s["session_id"]}'
    registration = await s['client'].post(
        path + '/registrations', headers=s['headers'][1],
    )
    assert registration.status_code == 201
    session_delete = await s['client'].delete(path, headers=s['headers'][0])
    assert session_delete.status_code == 409
    event_delete = await s['client'].delete(
        f'/events/{s["event_id"]}', headers=s['headers'][0],
    )
    assert event_delete.status_code == 409
