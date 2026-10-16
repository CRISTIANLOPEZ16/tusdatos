from pathlib import Path

import pytest

from app.infrastructure.config.settings import Settings


@pytest.fixture(scope="session")
def anyio_backend():
    return 'asyncio'

@pytest.fixture(scope='session', autouse=True)
def test_enviroment():
    env_file= Path(__file__).resolve().parents[1] / '.env.test'
    if not env_file.is_file():
        pytest.fail(f"Missing configuration: {env_file}", pytrace=False)
    settings = Settings(_env_file=env_file)
    if not settings.DB_NAME.endswith("_test"):
        pytest.fail('Test requiere a dedicated *_test database')
    with pytest.MonkeyPatch.context()as patch:
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

