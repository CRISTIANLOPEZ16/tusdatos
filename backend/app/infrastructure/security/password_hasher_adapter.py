from asyncio import to_thread

from pwdlib import PasswordHash


class PasswordHasherAdapter:
    def __init__(self) -> None:
        self._hasher = PasswordHash.recommended()
        self._dummy_hash = self._hasher.hash('by_default_password')

    async def hash(self, password: str) -> str:
        return await to_thread(self._hasher.hash, password)

    async def verify_password(self, password: str, password_hash: str) -> bool:
        matches= await to_thread(
            self._hasher.verify,
            password,
            password_hash if password_hash is not None else self._dummy_hash
        )
        return password_hash is not None and matches
