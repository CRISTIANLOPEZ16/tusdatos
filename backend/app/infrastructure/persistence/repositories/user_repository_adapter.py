from sqlalchemy import select

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.ports.user_repository_port import (
    EmailAlreadyExistsError,
)
from app.domain.entities.user import User
from app.infrastructure.persistence.models.user import User as UserModel


class UserRepositoryAdapter:
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, user: User) -> User:
        row = UserModel(
            email=user.email,
            password_hash=user.password_hash,
            created_at=user.created_at,
        )
        self.session.add(row)
        try:
            await self.session.flush()
        except IntegrityError as exc:
            original = exc.orig
            if (
                getattr(original, "sqlstate", None) == "23505"
                and getattr(
                    getattr(original, "diag", None),
                    "constraint_name",
                    None,
                ) == "users_email_key"
            ):
                raise EmailAlreadyExistsError from exc
            raise
        return User(
            user_id=row.user_id,
            email=row.email,
            password_hash=row.password_hash,
            created_at=row.created_at,
        )


    
    async def get_by_email(self, email:str)->User|None:
        statement = select(UserModel).where(UserModel.email == email)
        row = await self.session.scalar(statement)
        if row is None:
            return None
        return User(
            user_id=row.user_id,
            email=row.email,
            password_hash=row.password_hash,
            created_at=row.created_at
        )