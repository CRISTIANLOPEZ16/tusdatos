from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

@pytest.fixture(scope="session")
def database_url(test_enviroment):
    return test_enviroment.database_url

@pytest.fixture(scope="session")
def alembic_config():
    backend = Path(__file__).resolve().parents[2]
    return Config(str(backend/ 'alembic.ini'))


@pytest.fixture(scope="session")
def migrated_database(database_url, alembic_config):
    command.upgrade(alembic_config, 'head')
    return database_url

@pytest.fixture(scope='session')
async def database_engine(migrated_database, anyio_backend):
    engine= create_async_engine(migrated_database)
    try:
        yield engine
    finally:
        await engine.dispose()

@pytest.fixture
async def database_connection(database_engine):
    async with database_engine.connect() as connection :
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
        join_transaction_mode = "create_savepoint"
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
        base_url="http://test"
    ) as client:
        yield client
