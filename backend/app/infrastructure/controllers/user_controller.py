from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.domain.ports.user_repository_port import (
    EmailAlreadyExistsError,
)
from app.application.ports.register_user_use_case import (
    InvalidRegistrationError,
    RegisterUserUseCase,
)
from app.infrastructure.config.dependencies import get_register_user
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
