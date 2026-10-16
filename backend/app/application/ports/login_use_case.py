from typing import Protocol

class InvalidCredentialsError(Exception):
    """El correo o la contraseña no son correctos """

class LoginUseCase(Protocol):
    async def execute(self, email:str, password:str)->str:
        ...