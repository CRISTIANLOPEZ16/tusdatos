from email_validator import EmailNotValidError, validate_email

from app.application.dto.user import RegisteredUser
from app.application.ports.register_user_use_case import (
    InvalidRegistrationError,
)
from app.application.ports.password_hasher_port import (
    PasswordHasherPort,
)
from app.application.ports.transaction_port import TransactionPort
from app.domain.entities.user import User
from app.domain.ports.user_repository_port import UserRepositoryPort


class RegisterUserService:
    def __init__(
        self,
        repository: UserRepositoryPort,
        transaction: TransactionPort,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self.repository = repository
        self.transaction = transaction
        self.password_hasher = password_hasher

    async def execute(self, email: str, password: str) -> RegisteredUser:
        try:
            email = validate_email(
                email.strip(), check_deliverability=False,
            ).normalized.lower()
        except EmailNotValidError as exc:
            raise InvalidRegistrationError("Invalid email address") from exc
        if len(password) < 8:
            raise InvalidRegistrationError(
                "Password must contain at least 8 characters",
            )
        password_hash = await self.password_hasher.hash(password)
        user = User(email=email, password_hash=password_hash)
        try:
            registered = await self.repository.add(user)
            if registered.user_id is None:
                raise RuntimeError("Repository returned a user without an ID")
            result = RegisteredUser(
                user_id=registered.user_id,
                email=registered.email,
                created_at=registered.created_at,
            )
            await self.transaction.commit()
        except Exception:
            await self.transaction.rollback()
            raise
        return result
