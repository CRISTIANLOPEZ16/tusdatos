from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.ports.token_verifier_port import (
    InvalidTokenError,
    TokenVerifierPort,
)
from app.infrastructure.config.dependencies import get_token_adapter

bearer = HTTPBearer(
    auto_error=False,
    description=(
        "Obtén access_token en POST /auth/login y pega solo su valor. "
        "Un token ausente, inválido o expirado produce 401."
    ),
)


def get_current_user_id(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer),
    ],
    tokens: Annotated[TokenVerifierPort, Depends(get_token_adapter)],
) -> int:
    unauthorized = HTTPException(
        status_code=401,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    try:
        return tokens.get_user_id(credentials.credentials)
    except InvalidTokenError as exc:
        raise unauthorized from exc
