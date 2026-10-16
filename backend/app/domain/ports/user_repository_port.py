from typing import Protocol

from app.domain.entities.user import User

class EmailAlreadyExistsError(Exception):
    """The email is already associated with a user."""



class UserRepositoryPort(Protocol):
    async def add(self, user: User) -> User:
        """Persist the user and return its state with an assigned ID."""
        ...
    async def get_by_email(self, email:str)-> User|None:
        ...
        