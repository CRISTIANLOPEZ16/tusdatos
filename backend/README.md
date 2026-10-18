# Backend

API con Python 3.12, FastAPI, SQLAlchemy y PostgreSQL.
Arquitectura hexagonal: dominio, aplicación e infraestructura.

## Funcionalidades

- Registro de usuarios, contraseñas con Argon2 y autenticación con JWT.
- Creación, consulta, actualización y eliminación de eventos y sesiones.
- Listados con búsqueda por nombre, paginación y visibilidad según estado.
- Inscripciones a sesiones y consulta de eventos creados e inscritos del usuario.
- Ponentes compartidos por nombre y validación de conflictos de horario.

Los cupos pertenecen a cada sesión. Las respuestas muestran capacidad total,
inscritos y cupos disponibles. La inscripción exige un evento activo y debe
realizarse antes del inicio; el bloqueo en PostgreSQL evita sobrepasar el cupo
cuando llegan solicitudes simultáneas. Solo el creador gestiona su evento
y sus sesiones.

## Desarrollo local

Configura `.env` y `.env.test` como indica el [README principal](../README.md).
PostgreSQL debe estar disponible en el host y puerto configurados.
Puedes iniciarlo desde la raíz del proyecto:

```bash
docker compose --env-file backend/.env up -d --wait db
```

Desde `backend`:

```bash
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

Documentación: http://localhost:8000/docs.

## Datos de ejemplo

```bash
SEED_PASSWORD='DemoPassword123!' poetry run python -m scripts.seed
```

El seed lee `scripts/event_data.json` y agrega registros faltantes.
Incluye eventos, sesiones y ponentes. Crea el usuario `demo@example.com`
con la contraseña indicada en su primera ejecución.

## Pruebas realizadas

```bash
poetry run pytest -q --tb=short
```

Última verificación: **41 casos aprobados**. La suite incluye:

- Unitarias: límites de horarios, permisos y cambios de capacidad.
- Componentes HTTP: rutas protegidas, JWT inválidos y validación de entradas.
- Integración con PostgreSQL real: registro/login, migraciones, visibilidad,
  ocupación, restricciones de eliminación y competencia por el último cupo.

Configura `.env.test` con una base local dedicada cuyo nombre termine en
`_test`. La suite aplica sus migraciones; PostgreSQL debe estar activo.

La ejecución conjunta con frontend y base de datos está en el
[README principal](../README.md). Docker aplica migraciones y ejecuta el seed
antes de iniciar la API.
