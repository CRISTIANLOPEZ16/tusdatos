from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from app.infrastructure.config.dependencies import get_token_adapter
from app.infrastructure.security.jwt_token_adapter import JWTTokenAdapter

bearer = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer),
    ],
    tokens: Annotated[JWTTokenAdapter, Depends(get_token_adapter)],
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