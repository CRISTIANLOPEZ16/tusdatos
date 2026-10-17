from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.domain.errors.event import EventError
from app.domain.errors.user import UserNotFoundError
from app.infrastructure.controllers.auth_controller import (
    router as auth_router,
)
from app.infrastructure.controllers.event_controller import (
    router as event_router,
)
from app.infrastructure.controllers.http_errors import event_error_handler
from app.infrastructure.controllers.session_controller import (
    router as session_router,
)
from app.infrastructure.controllers.user_controller import (
    router as users_router,
)
from app.infrastructure.persistence.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(
    title="Mis Eventos API",
    description=(
        "API para gestionar eventos, sesiones e inscripciones.\n\n"
        "### Autenticación\n"
        "1. Crea una cuenta en `POST /users/register`.\n"
        "2. Obtén un token en `POST /auth/login` enviando JSON.\n"
        "3. Pulsa **Authorize** y pega `access_token` sin el prefijo Bearer. "
        "Las peticiones usarán `Authorization: Bearer <token>`.\n\n"
        "### Permisos\n"
        "Las consultas de eventos y sesiones son públicas. Crear un evento "
        "requiere autenticación; modificarlo o gestionar sus sesiones exige "
        "ser su creador. Cualquier usuario autenticado puede inscribirse a "
        "una sesión que admita inscripciones y tenga cupos.\n\n"
        "### Fechas, paginación y cupos\n"
        "Envía fechas ISO 8601 con zona horaria. Los listados usan `page` "
        "(desde 1) e `items_per_page` (1 a 100). `total` se calcula antes "
        "de paginar. El aforo pertenece a cada sesión: `capacity` es el "
        "total configurado, `registered_count` los inscritos y "
        "`available_capacity` los cupos libres al consultar.\n\n"
        "### Errores\n"
        "Las respuestas de error contienen `detail`: texto para errores "
        "de negocio o una lista para errores de validación por campo. "
        "Los endpoints DELETE correctos devuelven 204 sin cuerpo."
    ),
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Inicio de sesión y obtención de un Bearer JWT.",
        },
        {
            "name": "Users",
            "description": (
                "Registro público y consultas autenticadas de las "
                "inscripciones del usuario actual."
            ),
        },
        {
            "name": "Events",
            "description": (
                "Consultas públicas y gestión de eventos por su creador. "
                "El detalle incluye sesiones; el listado solo resúmenes."
            ),
        },
        {
            "name": "Sessions",
            "description": (
                "Sesiones de cada evento, ponentes por nombre, aforo e "
                "inscripciones del usuario autenticado."
            ),
        },
    ],
    version="0.1.0",
    lifespan=lifespan,
)
app.add_exception_handler(EventError, event_error_handler)
app.add_exception_handler(UserNotFoundError, event_error_handler)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(event_router)
app.include_router(session_router)
