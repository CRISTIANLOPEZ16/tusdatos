# Frontend

Interfaz con React, TypeScript, Vite y Material UI para consultar y gestionar
eventos, sesiones e inscripciones.

## Funcionalidades

- Listado público con búsqueda, paginación y detalle de eventos y sesiones.
- Registro, inicio/cierre de sesión y acceso a vistas privadas mediante JWT.
- Dashboard con eventos creados y sesiones inscritas del usuario.
- Formularios para gestionar eventos y sesiones, e inscripción con cupos disponibles.

El código separa dominio, aplicación, adaptadores HTTP y presentación.
React Query gestiona las consultas y Zod valida las respuestas de la API.

## Estructura

| Carpeta | Responsabilidad |
|---|---|
| `src/app` | Rutas, proveedores y conexión de dependencias. |
| `src/domain` | Tipos de eventos, sesiones, usuarios y errores. |
| `src/application` | Contratos para autenticación, registro, eventos y sesiones. |
| `src/infrastructure` | Peticiones HTTP, validación de respuestas y almacenamiento de sesión. |
| `src/presentation` | Páginas, componentes, hooks y estilos, organizados por funcionalidad. |
| `tests` | Pruebas unitarias, de componentes e integración HTTP. |

En `presentation`, `events` contiene el listado, detalle y formulario de eventos;
`sessions`, las tarjetas y el formulario de sesiones; `auth`, login, registro y
protección de rutas; `profile`, el dashboard. `shared` reúne componentes comunes
y `styles` define el tema de MUI.

Los formularios de eventos y sesiones se abren en diálogos mediante
`ManagementDialogs`; solo el creador puede editar el evento o agregar sesiones.

## Rutas

Definidas en `src/app/router.tsx` con React Router.

| Ruta | Vista |
|---|---|
| `/` | Redirige a `/eventos`. |
| `/eventos` y `/eventos/page/:page` | Listado público y paginación. |
| `/eventos/buscar/:name` y `/eventos/buscar/:name/page/:page` | Búsqueda por nombre y paginación. |
| `/eventos/:eventId` | Detalle del evento y sus sesiones. |
| `/login` | Inicio de sesión. |
| `/registro` | Registro de usuario. |
| `/my-dashboard` | Dashboard; requiere sesión (`RequireAuth`). |
| Cualquier otra | Página no encontrada (`NotFoundPage`). |

La sesión se conserva en `sessionStorage`. Al expirar o recibir un `401` en una
petición autenticada, se cierra la sesión y se redirige a `/eventos`.

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
