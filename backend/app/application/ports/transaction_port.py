from typing import Protocol


class TransactionPort(Protocol):
    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...
