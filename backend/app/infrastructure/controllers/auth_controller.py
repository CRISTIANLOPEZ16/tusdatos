from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException

from app.application.ports.login_use_case import (
    InvalidCredentialsError,
    LoginUseCase,
)
from app.infrastructure.config.dependencies import get_login
from app.infrastructure.schemas.auth import (
    LoginRequest,
    TokenResponse,
)
from app.infrastructure.controllers.http_errors import ERROR_RESPONSES
from app.infrastructure.schemas.user_schema import ErrorResponse


router = APIRouter(prefix='/auth', tags=['Authentication'])


@router.post(
    '/login',
    response_model=TokenResponse,
    summary='Iniciar sesión',
    description=(
        "Endpoint público. Verifica las credenciales enviadas como JSON y "
        "devuelve un JWT cuya duración depende de la configuración del "
        "servidor. Para probar rutas protegidas, copia access_token, pulsa "
        "Authorize y pega solo el token, sin anteponer Bearer. Fuera de "
        "Swagger envía Authorization: Bearer <token>."
    ),
    response_description="Token de acceso para una cuenta válida",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Correo o contraseña incorrecto",
            "headers": ERROR_RESPONSES[401]["headers"],
            "content": {"application/json": {"example": {
                "detail": "Correo o contraseña incorrecto",
            }}},
        },
        422: ERROR_RESPONSES[422],
    },
)
async def login(
    body: LoginRequest,
    use_case: Annotated[LoginUseCase, Depends(get_login)],
) -> TokenResponse:
    try:
        token = await use_case.execute(body.email, body.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=401,
            detail='Correo o contraseña incorrecto',
            headers={"WWW-Authenticate": "Bearer"}
        ) from exc

    return TokenResponse(access_token=token)
