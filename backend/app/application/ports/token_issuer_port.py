from typing import Protocol

class InvalidTokenError(ValueError):
    """Input token is invalid"""


class TokenIssuerPort(Protocol):
    def issue(self, user_id:int)->str:
        ...
    def get_user_id(self, token:str)->int|None:
        ...