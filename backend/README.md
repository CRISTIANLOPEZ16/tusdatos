# Backend

Ejecuta los comandos de Poetry desde `backend/`:

```bash
poetry install --with dev --no-root
cp .env.example .env
```

Configura `DB_USER`, `DB_PASSWORD` y `DB_NAME` en `backend/.env`. Compose usa
estos valores tanto para el backend como para PostgreSQL; no necesitas un
archivo `.env` en la raíz. Las conexiones locales usan `DB_HOST=localhost` y
`DB_PORT`. Compose publica PostgreSQL en ese puerto y configura la conexión
del contenedor del backend con `DB_HOST=db` y `DB_PORT=5432`, el puerto interno
de PostgreSQL.

Las variables de inicialización de PostgreSQL solo se aplican cuando el volumen
de datos está vacío. Cambiarlas no renombra una base de datos existente ni
actualiza sus usuarios.

Inicia PostgreSQL desde la raíz del repositorio:

```bash
docker compose --env-file backend/.env up -d db
```

Incluye también `--env-file backend/.env` en los siguientes comandos de Compose.
Desde `backend/`, aplica las migraciones existentes. No generes otra migración
inicial al instalar el proyecto:

```bash
poetry run alembic upgrade head
poetry run alembic check
```

La aplicación usa Psycopg mediante el motor asíncrono de SQLAlchemy y
`AsyncSession`. Utiliza `get_session` como dependencia de FastAPI, espera las
operaciones de base de datos con `await` y confirma la transacción explícitamente
en el caso de uso. Cada petición obtiene su propia sesión. Al cerrar la
aplicación, su gestor de ciclo de vida libera el motor mediante
`await engine.dispose()`.

Alembic usa la misma configuración y los mismos modelos con un motor síncrono
de Psycopg. No importa el motor asíncrono de la aplicación.

Para ejecutar el backend localmente:

```bash
poetry run uvicorn app.main:app --reload
```

## Arquitectura

Se mantienen tres capas: dominio, aplicación e infraestructura. El contrato
`domain/ports/user_repository_port.py` trabaja con entidades de dominio;
`infrastructure/persistence/repositories` lo implementa con SQLModel.
Los controladores están en `infrastructure/controllers`, los esquemas HTTP en
`infrastructure/schemas` y el hashing en `infrastructure/security`.
La conexión de implementaciones está en `infrastructure/config/dependencies.py`.

El servicio valida sus entradas también fuera de HTTP, normaliza el correo,
coordina los puertos y controla commit/rollback. Las contraseñas se procesan
con Argon2 y no se incluyen en respuestas. El repositorio no realiza login.

Consulta [la arquitectura](../docs/backend-architecture.md) y
[las guías de pruebas](../docs/TESTING_GUIDELINES_backend.md).
Login, eventos, sesiones e inscripciones a eventos siguen pendientes.

## Pruebas locales

Todos los comandos se ejecutan desde `backend/` con Poetry; no requieren
levantar el backend en Docker.

```bash
poetry run flake8 app test migrations
poetry run python -m pytest test/unit -q
poetry run python -m pytest --cov=app --cov-report=term-missing --cov-report=xml
```

Sin `TEST_DATABASE_URL`, se omiten las pruebas que necesitan PostgreSQL.
Las pruebas HTTP con el caso de uso simulado y las de Argon2 sí se ejecutan.
`coverage.xml` contiene el reporte de cobertura; las pruebas omitidas no
constituyen verificación de persistencia.

Para ejecutar también persistencia y el flujo HTTP con los adaptadores reales,
crea una base local exclusiva cuyo nombre termine en `_test`. Puede estar en
el PostgreSQL que ya ejecutas en Docker. Configura su URL y ejecuta:

```bash
export TEST_DATABASE_URL='postgresql+psycopg://usuario:clave@localhost:5432/mis_eventos_test'
poetry run python -m pytest --cov=app --cov-report=term-missing --cov-report=xml
```

Las fixtures rechazan hosts remotos, otros drivers y nombres sin `_test`.
Aplican las migraciones y vacían `users` y las tablas dependientes antes y
después de cada prueba de base de datos. Usa exclusivamente una base desechable;
no ejecutes estas pruebas en paralelo contra la misma base.

La migración `a7c9e2f40115` limita `events.name` a 150 caracteres para coincidir
con el modelo. Revisa nombres existentes más largos antes de aplicarla; no
se truncan automáticamente. Este refactor no aplica migraciones a tu base de
desarrollo.

## Documentación de la API

Con el backend iniciado en el puerto 8000:

- Swagger UI: <http://localhost:8000/docs>. Permite consultar y probar rutas.
- OpenAPI JSON: <http://localhost:8000/openapi.json>.
- ReDoc: <http://localhost:8000/redoc>.

FastAPI genera la especificación desde las rutas y los esquemas Pydantic.
No se requiere una dependencia adicional para OpenAPI. Las interfaces de
Swagger UI y ReDoc cargan sus recursos desde una CDN y requieren acceso a ella.

### Registro de usuarios — `POST /users/register`

Ruta pública, sin token. Recibe `application/json` con `email` válido y
`password` de al menos ocho caracteres. El correo se normaliza a minúsculas;
la contraseña se almacena con Argon2. No inicia sesión ni genera un JWT.

```bash
curl -X POST http://localhost:8000/users/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"ExamplePassword123!"}'
```

Respuesta `201 Created` (el ID y la fecha son ilustrativos):

```json
{
  "user_id": 1,
  "email": "user@example.com",
  "created_at": "2026-01-01T00:00:00Z"
}
```

| Código | Significado | Cuerpo |
| --- | --- | --- |
| `201` | Usuario creado | ID, correo y fecha; sin contraseña ni hash |
| `409` | Correo ya registrado | `{"detail":"Email already registered"}` |
| `422` | Campos ausentes, correo inválido o contraseña corta | `detail` contiene una lista de errores de entrada o un mensaje del caso de uso |

Swagger incluye ejemplos para respuestas exitosas y ambos formatos de error.
Solo se documentan los endpoints implementados.
