from typing import Protocol


class InvalidTokenError(ValueError):
    """The token cannot identify an authenticated user."""


class TokenVerifierPort(Protocol):
    def get_user_id(self, token: str) -> int:
        ...
