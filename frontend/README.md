# Frontend

Interfaz con React, TypeScript, Vite y Material UI para consultar y gestionar
eventos, sesiones e inscripciones.

## Funcionalidades

- Listado público con búsqueda, paginación y detalle de eventos y sesiones.
- Registro, inicio/cierre de sesión y acceso a vistas privadas mediante JWT.
- Dashboard con eventos creados, eventos inscritos y sesiones del usuario.
- Formularios para gestionar eventos y sesiones, e inscripción con cupos disponibles.

El código separa dominio, aplicación, adaptadores HTTP y presentación.
React Query gestiona las consultas y Zod valida las respuestas de la API.

## Desarrollo local

Requiere Node.js 24 y el backend en `http://127.0.0.1:8000`.
Desde `frontend`:

```bash
npm ci
npm run dev
```

Abre http://localhost:5173. Vite redirige `/api` al backend.

## Pruebas realizadas

```bash
npm test
npm run lint
npm run build
```

Última verificación: **16 pruebas aprobadas en 5 archivos**, lint sin errores
y compilación de producción correcta. Se comprobaron:

- Lectura y caducidad del JWT, restauración de sesión y protección del dashboard.
- Login, logout, credenciales incorrectas y respuestas privadas `401`.
- Búsqueda, paginación y orden del listado de eventos.
- Parámetros HTTP, contratos de respuesta y presentación de errores.

Las pruebas usan Vitest y Testing Library con solicitudes HTTP simuladas.
El build comprueba TypeScript y genera los archivos estáticos en `dist`.

Para ejecutar los tres servicios con Docker, consulta el
[README principal](../README.md). En ese entorno, Nginx sirve la aplicación
en http://localhost:3000 y redirige `/api` al contenedor del backend.
