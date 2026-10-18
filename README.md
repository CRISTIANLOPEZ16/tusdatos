# Mis Eventos

Aplicación para gestionar eventos, sesiones e inscripciones.
Frontend con React y TypeScript, backend con FastAPI y PostgreSQL 17.

## Ejecutar con Docker

Requiere Docker y Docker Compose. Desde la raíz:

```bash
cp -n backend/.env.example backend/.env
cp -n backend/.env.example backend/.env.test
```

Configura las credenciales de PostgreSQL en ambos archivos. En `.env.test`,
usa un `DB_NAME` terminado en `_test`, con el mismo usuario y contraseña.
En `.env`, define `SEED_PASSWORD` (mínimo 8 caracteres) y una clave
`JWT_SECRET_KEY` aleatoria de al menos 64 caracteres.

```bash
docker compose --env-file backend/.env up --build -d --wait
```

- Frontend: http://localhost:3000
- Swagger: http://localhost:8000/docs

El arranque aplica las migraciones y carga los eventos, sesiones y ponentes
de `backend/scripts/event_data.json`. Usuario demo: `demo@example.com`;
contraseña: `SEED_PASSWORD` de su primera creación.

Para detener los servicios conservando los datos:

```bash
docker compose --env-file backend/.env down
```

Desarrollo y pruebas: [backend](backend/README.md) · [frontend](frontend/README.md).
