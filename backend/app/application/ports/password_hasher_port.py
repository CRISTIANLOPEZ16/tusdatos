from typing import Protocol


class PasswordHasherPort(Protocol):
    async def hash(self, password: str) -> str:
        ...

    async def verify_password(self, password:str, password_hash:str | None )->bool:
        ...