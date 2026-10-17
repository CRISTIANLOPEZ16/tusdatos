from typing import Protocol


class TokenIssuerPort(Protocol):
    def issue(self, user_id: int) -> str:
        ...
