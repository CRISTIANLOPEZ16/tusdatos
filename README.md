# Mis Eventos

Aplicación con frontend React/Vite, API FastAPI y PostgreSQL 17.

## Ejecutar con Docker

Requiere Docker con Docker Compose.

1. Copia `backend/.env.example` a `backend/.env` y, si no existe, a
   `backend/.env.test`:

   ```bash
   cp -n backend/.env.example backend/.env
   cp -n backend/.env.example backend/.env.test
   ```

2. En `.env.test`, configura `DB_NAME` con un nombre terminado en `_test`,
   por ejemplo `events_db_test`. Conserva el mismo `DB_USER` y `DB_PASSWORD`
   de `.env`: Compose crea también esa base para las pruebas locales.
   En `.env`, define `SEED_PASSWORD` con al menos 8 caracteres y reemplaza
   el ejemplo de `JWT_SECRET_KEY` por una clave aleatoria de al menos
   64 caracteres. Puedes generarla con:

   ```bash
   python3 -c 'import secrets; print(secrets.token_hex(32))'
   ```

3. Desde la raíz del repositorio:

   ```bash
   docker compose --env-file backend/.env up --build -d --wait
   ```

- Frontend: http://localhost:3000
- API y Swagger: http://localhost:8000/docs
- PostgreSQL: `localhost`, puerto `DB_PORT` de `.env` (5432 por defecto).

El backend espera a PostgreSQL, aplica las migraciones y ejecuta
`scripts.seed` antes de iniciar la API. El seed lee
`backend/scripts/event_data.json`, crea los registros que falten y conserva
los existentes. El usuario de demostración es `demo@example.com`, con la
contraseña `SEED_PASSWORD` cuando se crea por primera vez; repetir el seed
no cambia su contraseña.

Nginx sirve el frontend y redirige `/api/` al backend por la red de Compose.
Las rutas del frontend admiten recarga directa sin devolver 404. El proxy
de Vite se sigue usando al desarrollar con `npm run dev`.

Para cambiar los puertos publicados, define `FRONTEND_PORT`, `BACKEND_PORT`
o `DB_PORT` al ejecutar Compose. Dentro de los contenedores, PostgreSQL
mantiene el puerto 5432 y la API el 8000.

## Logs y parada

```bash
docker compose --env-file backend/.env logs -f backend frontend
docker compose --env-file backend/.env down
```

La base de datos se conserva en el volumen `postgres_data` al detener los
contenedores. No uses `down -v` si quieres conservar sus datos.
