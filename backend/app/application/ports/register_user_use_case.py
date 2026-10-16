from typing import Protocol

from app.application.dto.user import RegisteredUser


class InvalidRegistrationError(ValueError):
    """Registration input violates the application's contract."""


class RegisterUserUseCase(Protocol):
    async def execute(self, email: str, password: str) -> RegisteredUser:
        ...
