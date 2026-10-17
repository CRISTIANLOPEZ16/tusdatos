from typing import Annotated

from fastapi import Depends, Path, Request
from fastapi.responses import JSONResponse

from app.application.ports.event_use_cases import InvalidEventQueryError
from app.domain.errors.event import (
    EventConflictError, EventForbiddenError, EventNotFoundError,
    InvalidEventError,
)
from app.domain.errors.session import (
    InvalidSessionError, SessionConflictError, SessionNotFoundError,
)
from app.domain.errors.user import UserNotFoundError
from app.infrastructure.schemas.event_schema import (
    EventValidationErrorResponse,
)
from app.infrastructure.schemas.user_schema import ErrorResponse
from app.infrastructure.security.authentication import get_current_user_id


ResourceId = Annotated[int, Path(
    ge=1, le=2_147_483_647,
    description="Identificador positivo del recurso indicado en la ruta.",
    examples=[1],
)]
CurrentUserId = Annotated[int, Depends(get_current_user_id)]

ERROR_RESPONSES = {
    401: {
        "model": ErrorResponse,
        "description": (
            "Token ausente, inválido o expirado, o usuario que ya no existe."
        ),
        "headers": {"WWW-Authenticate": {
            "description": "Esquema de autenticación requerido.",
            "schema": {"type": "string", "example": "Bearer"},
        }},
        "content": {"application/json": {"examples": {
            "token": {"value": {"detail": "Invalid or expired token"}},
            "user": {"value": {
                "detail": "El usuario autenticado ya no existe",
            }},
        }}},
    },
    403: {
        "model": ErrorResponse,
        "description": "El usuario autenticado no es el creador del evento.",
        "content": {"application/json": {"example": {
            "detail": "Solo el creador puede modificar el evento",
        }}},
    },
    404: {
        "model": ErrorResponse,
        "description": (
            "El evento no existe o la sesión no pertenece al evento indicado."
        ),
        "content": {"application/json": {"examples": {
            "event": {"value": {"detail": "El evento no existe"}},
            "session": {"value": {
                "detail": "La sesión no pertenece al evento o no existe",
            }},
        }}},
    },
    409: {
        "model": ErrorResponse,
        "description": (
            "Conflicto con las reglas de negocio descritas en la operación. "
            "detail indica la condición que impide completarla."
        ),
    },
    422: {
        "model": EventValidationErrorResponse,
        "description": (
            "Entrada inválida: campos, fechas, identificadores o paginación. "
            "detail es un mensaje de negocio o una lista de errores."
        ),
        "content": {"application/json": {"examples": {
            "field": {"value": {"detail": [{
                "loc": ["query", "page"],
                "msg": "Input should be greater than or equal to 1",
                "type": "greater_than_equal",
            }]}},
            "business": {"value": {
                "detail": "La fecha final debe ser posterior a la inicial",
            }},
        }}},
    },
}
ERROR_CODES = {
    InvalidEventError: 422, InvalidEventQueryError: 422,
    InvalidSessionError: 422, EventNotFoundError: 404,
    SessionNotFoundError: 404, EventForbiddenError: 403,
    EventConflictError: 409, SessionConflictError: 409,
    UserNotFoundError: 401,
}


async def event_error_handler(
    request: Request, exc: Exception,
) -> JSONResponse:
    status = ERROR_CODES.get(type(exc), 500)
    return JSONResponse(
        status_code=status,
        content={"detail": str(exc) if status != 500 else "Error interno"},
        headers={"WWW-Authenticate": "Bearer"} if status == 401 else None,
    )
