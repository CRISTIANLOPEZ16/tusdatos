# Backend

API con Python 3.12, FastAPI, SQLAlchemy y PostgreSQL.
Arquitectura hexagonal: dominio, aplicación e infraestructura.

## Desarrollo local

Configura `.env` y `.env.test` como indica el [README principal](../README.md).
PostgreSQL debe estar disponible en el host y puerto configurados.
Desde `backend`:

```bash
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

Documentación: http://localhost:8000/docs.

## Datos de ejemplo y pruebas

```bash
SEED_PASSWORD='DemoPassword123!' poetry run python -m scripts.seed
poetry run pytest
```

El seed lee `scripts/event_data.json` y agrega registros faltantes.
Las integraciones requieren PostgreSQL local y una base dedicada cuyo
nombre termine en `_test`.

Los cupos pertenecen a cada sesión. Las inscripciones requieren un JWT,
un evento activo y cupos disponibles antes del inicio de la sesión.
