from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """Credenciales de una cuenta previamente registrada."""

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "email": "organizador@example.com", "password": "ExamplePassword123!",
    }]})

    email: EmailStr = Field(
        description="Correo registrado; el login lo normaliza a minúsculas.",
        examples=["organizador@example.com"],
    )
    password: str = Field(
        min_length=1, description="Contraseña de la cuenta registrada.",
        json_schema_extra={"writeOnly": True, "format": "password"},
    )


class TokenResponse(BaseModel):
    """Token para acceder a las rutas protegidas; no contiene la contraseña."""

    access_token: str = Field(
        description="JWT. En Authorize pega este valor sin anteponer Bearer.",
    )
    token_type: Literal["bearer"] = Field(
        default="bearer", description="Esquema de autenticación del token.",
    )


class AuthenticatedUserResponse(BaseModel):
    user_id: int
