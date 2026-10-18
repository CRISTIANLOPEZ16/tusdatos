# Frontend

Interfaz con React, TypeScript, Vite y Material UI para consultar y gestionar
eventos, sesiones e inscripciones.

## Desarrollo local

Requiere Node.js 24 y el backend en `http://127.0.0.1:8000`.
Desde `frontend`:

```bash
npm ci
npm run dev
```

Abre http://localhost:5173. Vite redirige `/api` al backend.

## Pruebas y build

```bash
npm test
npm run lint
npm run build
```

Para ejecutar los tres servicios con Docker, consulta el
[README principal](../README.md).
