from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.register_user_use_case import (
    RegisterUserUseCase,
)
from app.application.services.register_user_service import RegisterUserService
from app.infrastructure.security.password_hasher_adapter import (
    PasswordHasherAdapter
)
from app.infrastructure.persistence.repositories import (
    user_repository_adapter,
)
from app.infrastructure.persistence.database import get_session
from app.infrastructure.security.jwt_token_adapter import JWTTokenAdapter
from app.application.ports.login_use_case import LoginUseCase
from app.infrastructure.config.settings import Settings
from app.application.services.login_service import LoginService


password_hasher = PasswordHasherAdapter()


def get_register_user(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RegisterUserUseCase:
    return RegisterUserService(
        repository=user_repository_adapter.UserRepositoryAdapter(session),
        transaction=session,
        password_hasher=password_hasher,
    )

def get_token_adapter() -> JWTTokenAdapter:
    settings = Settings()
    return JWTTokenAdapter(
        secret=settings.JWT_SECRET_KEY,
        expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        algorith=settings.ALGORITHM
    )

def get_login(
        session: Annotated[AsyncSession, Depends(get_session)],
        tokens: Annotated[JWTTokenAdapter, Depends(get_token_adapter)]
)->LoginUseCase:
    return LoginService(
        repository=user_repository_adapter.UserRepositoryAdapter(session),
        password_verifier=password_hasher,
        token=tokens
    )