from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException

from app.application.ports.login_use_case import InvalidCredentialsError, LoginUseCase
from app.infrastructure.config.dependencies import get_login
from app.infrastructure.schemas.auth import LoginRequest, TokenResponse
from app.infrastructure.schemas.user_schema import ErrorResponse


router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post(
    '/login',
    response_model=TokenResponse,
    summary='Iniciar sesion',
    description=(
        "Verifica correo y contraseña y devuelve un JWT válido durante "
        "30 minutos con la configuración predeterminada. Envía el token "
        "en Authorization: Bearer <token> para acceder a rutas protegidas."
    ),
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Correo o contraseña incorrecto",
        },
    }
)
async def login(
    body: LoginRequest,
    use_case:Annotated[LoginUseCase, Depends(get_login)]
)->TokenResponse:
    try:
        token= await use_case.execute(body.email, body.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=401,
            detail='Correo o contraseña incorrecto',
            headers={"WWW-Authenticate": "Bearer"}
        ) from exc
        
    return TokenResponse(access_token=token)



