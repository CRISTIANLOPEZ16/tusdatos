from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.application.ports.event_use_cases import ListRegisteredEventsUseCase
from app.application.ports.register_user_use_case import (
    InvalidRegistrationError,
    RegisterUserUseCase,
)
from app.application.ports.session_use_cases import (
    ListRegisteredSessionsUseCase,
)
from app.domain.ports.user_repository_port import (
    EmailAlreadyExistsError,
)
from app.infrastructure.config.dependencies import (
    get_event_service, get_session_service,
)
from app.infrastructure.config.dependencies import get_register_user
from app.infrastructure.controllers.http_errors import (
    CurrentUserId, ERROR_RESPONSES,
)
from app.infrastructure.schemas.event_schema import (
    ListEventParams, ListEventResponse,
)
from app.infrastructure.schemas.pagination import PaginationParams
from app.infrastructure.schemas.session_schema import ListSessionResponse
from app.infrastructure.schemas.user_schema import (
    ErrorResponse,
    RegistrationValidationErrorResponse,
    UserCreateRequest,
    UserResponse,
)


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Registrar un usuario",
    description=(
        "Crea una cuenta sin requerir autenticación. El correo se normaliza "
        "a minúsculas y debe ser único. La contraseña requiere al menos "
        "8 caracteres y se almacena como hash Argon2. La respuesta no "
        "incluye la contraseña ni su hash. Este endpoint no inicia sesión "
        "ni devuelve un token."
    ),
    response_description="Usuario registrado correctamente",
    responses={
        201: {
            "content": {"application/json": {"example": {
                "user_id": 1,
                "email": "user@example.com",
                "created_at": "2026-01-01T00:00:00Z",
            }}},
        },
        409: {
            "model": ErrorResponse,
            "description": "El correo ya está registrado",
            "content": {"application/json": {"example": {
                "detail": "Email already registered",
            }}},
        },
        422: {
            "model": RegistrationValidationErrorResponse,
            "description": "Campos ausentes o entrada inválida",
            "content": {"application/json": {"examples": {
                "request": {"summary": "Campo obligatorio ausente", "value": {
                    "detail": [{
                        "loc": ["body", "password"],
                        "msg": "Field required", "type": "missing",
                        "input": {"email": "user@example.com"},
                    }],
                }},
                "application": {"summary": "Validación del caso de uso",
                                "value": {"detail": "Invalid email address"}},
            }}},
        },
    },
)
async def register_user(
    body: UserCreateRequest,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_user)],
) -> UserResponse:
    try:
        user = await use_case.execute(
            email=str(body.email),
            password=body.password,
        )
    except InvalidRegistrationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except EmailAlreadyExistsError as exc:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        ) from exc

    return UserResponse(**asdict(user))


@router.get(
    "/me/events", response_model=ListEventResponse,
    summary='Listar mis eventos por inscripción',
    description=(
        'Requiere Bearer JWT. Devuelve los eventos en los que el usuario '
        'tiene al menos una sesión inscrita, sin repetir eventos. No es un '
        'listado de eventos creados por el usuario. Permite paginación y '
        'búsqueda por nombre; no aplica el filtro de estados del listado '
        'público. Devuelve resúmenes sin sesiones, ordenados por ID. '
    ),
    response_description='Página de eventos con sesiones inscritas',
    responses={401: ERROR_RESPONSES[401], 422: ERROR_RESPONSES[422]},
)
async def list_my_events(
    user_id: CurrentUserId, params: Annotated[ListEventParams, Query()],
    use_case: Annotated[
        ListRegisteredEventsUseCase, Depends(get_event_service),
    ],
) -> ListEventResponse:
    result = await use_case.list_registered_events(
        user_id, **params.model_dump(),
    )
    return ListEventResponse(**asdict(result))


@router.get(
    "/me/sessions", response_model=ListSessionResponse,
    summary='Listar mis sesiones inscritas',
    description=(
        'Requiere Bearer JWT. Devuelve las sesiones inscritas del usuario, '
        'ordenadas por inicio e ID y con paginación. registered_count '
        'representa todos los inscritos de cada sesión, no solo al usuario '
        'autenticado. available_capacity muestra los cupos libres al '
        'consultar. '
    ),
    response_description='Página de sesiones inscritas con disponibilidad',
    responses={401: ERROR_RESPONSES[401], 422: ERROR_RESPONSES[422]},
)
async def list_my_sessions(
    user_id: CurrentUserId, params: Annotated[PaginationParams, Query()],
    use_case: Annotated[
        ListRegisteredSessionsUseCase, Depends(get_session_service),
    ],
) -> ListSessionResponse:
    return ListSessionResponse.model_validate(
        await use_case.list_registered_sessions(user_id, **params.model_dump())
    )
