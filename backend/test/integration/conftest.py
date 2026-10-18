import pytest
from alembic import command
from alembic.config import Config
from app.domain.entities.event_status import EventStatus
from app.infrastructure.config.dependencies import get_token_adapter
from app.infrastructure.persistence.models import (
    Event,
    Registration,
    Session,
    Speaker,
    User,
)
from datetime import datetime, timedelta, timezone
from httpx import ASGITransport, AsyncClient
from pathlib import Path
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from uuid import uuid4


@pytest.fixture(scope='session')
def database_url(test_enviroment):
    return test_enviroment.database_url


@pytest.fixture(scope='session')
def alembic_config():
    backend = Path(__file__).resolve().parents[2]
    return Config(str(backend / 'alembic.ini'))


@pytest.fixture(scope='session')
def migrated_database(database_url, alembic_config):
    command.upgrade(alembic_config, 'head')
    return database_url


@pytest.fixture(scope='session')
async def database_engine(migrated_database, anyio_backend):
    engine = create_async_engine(migrated_database)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def database_connection(database_engine):
    async with database_engine.connect() as connection:
        transaction = await connection.begin()
        try:
            yield connection
        finally:
            if transaction.is_active:
                await transaction.rollback()


@pytest.fixture
def sessions_factory(database_connection):
    return async_sessionmaker(
        bind=database_connection,
        expire_on_commit=False,
        join_transaction_mode='create_savepoint'
    )


@pytest.fixture
async def db_session(sessions_factory):
    async with sessions_factory() as session:
        yield session


@pytest.fixture
async def api_client(app, sessions_factory):
    from app.infrastructure.persistence.database import get_session

    async def override_session():
        async with sessions_factory() as session:
            yield session
    app.dependency_overrides[get_session] = override_session
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    ) as client:
        yield client


@pytest.fixture
async def scenario(api_client, db_session):
    marker = uuid4().hex
    users = [
        User(
            email=f'{marker}-{i}@example.com',
            password_hash='unused'
        ) for i in range(3)
    ]
    speaker = Speaker(
        name='Ponente ' + marker,
        normalized_name='ponente ' + marker
    )
    db_session.add_all([*users, speaker])
    await db_session.flush()
    await db_session.commit()
    headers = [
        {
            'Authorization': 'Bearer ' + get_token_adapter().issue(u.user_id)
        } for u in users
    ]
    start = datetime.now(timezone.utc) + timedelta(days=2)
    event_body = dict(
        name='Evento ' + marker,
        description=None,
        address='Calle 123',
        starts_at=start.isoformat(),
        ends_at=(start + timedelta(hours=8)).isoformat(),
        status='activo'
    )
    event = await api_client.post(
        '/events',
        json=event_body,
        headers=headers[0]
    )
    assert event.status_code == 201
    eid = event.json()['event_id']
    body = dict(
        title='Sesión',
        starts_at=(start + timedelta(hours=1)).isoformat(),
        ends_at=(start + timedelta(hours=2)).isoformat(),
        capacity=1,
        speaker_names=[speaker.name]
    )
    session = await api_client.post(
        f'/events/{eid}/sessions',
        json=body,
        headers=headers[0]
    )
    assert session.status_code == 201
    return dict(
        marker=marker,
        client=api_client,
        event_id=eid,
        session_id=session.json()['session_id'],
        headers=headers,
        users=users,
        session_body=body,
        event_body=event_body,
        speaker_id=speaker.speaker_id,
        start=start
    )


@pytest.fixture
async def committed_scenario(database_engine, database_url):
    assert database_url.database.endswith('_test')
    assert database_url.host in {'localhost', '127.0.0.1', '::1'}
    factory = async_sessionmaker(database_engine, expire_on_commit=False)
    marker = uuid4().hex
    user_ids = []
    try:
        async with factory() as db:
            users = [
                User(email=f'{marker}-{i}@example.com', password_hash='unused')
                for i in range(3)
            ]
            db.add_all(users)
            await db.flush()
            user_ids = [user.user_id for user in users]
            start = datetime.now(timezone.utc) + timedelta(days=2)
            event = Event(
                name=marker, description=None, address='Calle 123',
                starts_at=start, ends_at=start + timedelta(hours=8),
                status=EventStatus.ACTIVE, created_by=user_ids[0],
            )
            db.add(event)
            await db.flush()
            session = Session(
                event_id=event.event_id, title='Último cupo',
                starts_at=start + timedelta(hours=1),
                ends_at=start + timedelta(hours=2), capacity=1,
            )
            db.add(session)
            await db.flush()
            await db.commit()
            yield factory, user_ids, event.event_id, session.session_id
    finally:
        async with factory() as db:
            event_ids = select(Event.event_id).where(
                Event.created_by.in_(user_ids),
            )
            session_ids = select(Session.session_id).where(
                Session.event_id.in_(event_ids),
            )
            await db.execute(delete(Registration).where(
                Registration.session_id.in_(session_ids),
            ))
            await db.execute(delete(Session).where(
                Session.event_id.in_(event_ids),
            ))
            await db.execute(delete(Event).where(
                Event.created_by.in_(user_ids),
            ))
            await db.execute(delete(User).where(User.user_id.in_(user_ids)))
            await db.commit()


@pytest.fixture
async def visibility_events(scenario, db_session):
    prefix = 'Visibilidad ' + scenario['marker']
    events = [
        Event(
            name=f'{prefix} {status.value}',
            description=None,
            address='Calle 123',
            starts_at=scenario['start'],
            ends_at=scenario['start'] + timedelta(hours=8),
            status=status,
            created_by=scenario['users'][0].user_id
        ) for status in EventStatus
    ]
    db_session.add_all(events)
    await db_session.flush()
    await db_session.commit()
    return {'prefix': prefix, 'events': events}
