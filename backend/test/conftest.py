import pytest
from app.application.dto.session import SessionData
from app.application.ports.transaction_port import TransactionPort
from app.application.services.session_service import SessionService
from app.domain.entities.event import Event
from app.domain.entities.event_status import EventStatus
from app.domain.entities.session import Session
from app.domain.ports.event_repository_port import EventRepositoryPort
from app.domain.ports.session_repository_port import SessionRepositoryPort
from app.domain.ports.user_repository_port import UserRepositoryPort
from app.infrastructure.config.settings import Settings
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import create_autospec


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope='session', autouse=True)
def test_enviroment():
    env_file = Path(__file__).resolve().parents[1] / '.env.test'
    if not env_file.is_file():
        pytest.fail(f'Missing configuration: {env_file}', pytrace=False)
    settings = Settings(_env_file=env_file)
    if not settings.DB_NAME.endswith('_test'):
        pytest.fail('Test requiere a dedicated *_test database')
    if settings.DB_HOST not in {'localhost', '127.0.0.1', '::1'}:
        pytest.fail('Las pruebas requieren PostgreSQL local')
    with pytest.MonkeyPatch.context() as patch:
        for name, value in settings.model_dump().items():
            patch.setenv(name, str(value))
        yield settings


@pytest.fixture
async def app(test_enviroment):
    from app.main import app as application
    previous = application.dependency_overrides.copy()
    try:
        async with application.router.lifespan_context(application):
            yield application
    finally:
        application.dependency_overrides.clear()
        application.dependency_overrides.update(previous)


@pytest.fixture
def instant():
    return datetime.now(timezone.utc)


@pytest.fixture
def make_event(instant):

    def build(**changes):
        values = dict(
            event_id=10,
            name='Python Medellín',
            description=None,
            address='Calle 10 # 20',
            starts_at=instant + timedelta(days=2),
            ends_at=instant + timedelta(days=2, hours=8),
            status=EventStatus.ACTIVE,
            created_by=9,
            sessions=()
        )
        return Event(**values | changes)
    return build


@pytest.fixture
def make_session(make_event):

    def build(**changes):
        event = make_event()
        values = dict(
            session_id=20,
            event_id=event.event_id,
            title='Arquitectura',
            starts_at=event.starts_at + timedelta(hours=1),
            ends_at=event.starts_at + timedelta(hours=2),
            capacity=2
        )
        return Session(**values | changes)
    return build


@pytest.fixture
def session_data(make_session):
    session = make_session()
    return SessionData(
        title=session.title,
        starts_at=session.starts_at,
        ends_at=session.ends_at,
        capacity=session.capacity
    )


@pytest.fixture
def session_context(make_event, make_session):
    repository = create_autospec(
        SessionRepositoryPort,
        instance=True,
        spec_set=True
    )
    events = create_autospec(EventRepositoryPort, instance=True, spec_set=True)
    users = create_autospec(UserRepositoryPort, instance=True, spec_set=True)
    transaction = create_autospec(
        TransactionPort,
        instance=True,
        spec_set=True
    )
    users.get_by_id.return_value = object()
    events.get_by_id.return_value = make_event()
    repository.get_by_id.return_value = make_session()
    return (
        SessionService(repository, events, users, transaction),
        repository,
        events,
        users,
        transaction
    )
