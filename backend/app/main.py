from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.persistence.database import engine
from app.infrastructure.controllers.user_controller import router as users_router
from app.infrastructure.controllers.auth_controller import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(
    title="Mis Eventos API",
    description=(
        "API de Mis Eventos. Actualmente permite registrar usuarios. "
        "Login, eventos, sesiones e inscripciones siguen pendientes. "
        "Los cuerpos de las peticiones y respuestas usan JSON."
    ),
    openapi_tags=[{
        "name": "Users", "description": "Registro público de usuarios.",
    }],
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(users_router)
app.include_router(auth_router)