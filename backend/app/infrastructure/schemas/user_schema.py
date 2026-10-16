from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    """Datos necesarios para registrar un usuario."""

    email: EmailStr = Field(
        description="Correo del usuario; se guarda en minúsculas",
        examples=["user@example.com"],
    )
    password: str = Field(
        min_length=8, description="Contraseña de al menos 8 caracteres",
        examples=["ExamplePassword123!"],
        json_schema_extra={"writeOnly": True, "format": "password"},
    )


class UserResponse(BaseModel):
    """Datos públicos del usuario registrado."""

    user_id: int = Field(
        description="Identificador del usuario", examples=[1],
    )
    email: EmailStr = Field(
        description="Correo normalizado del usuario",
        examples=["user@example.com"],
    )
    created_at: datetime = Field(
        description="Fecha de creación con zona horaria",
        examples=["2026-01-01T00:00:00Z"],
    )


class ErrorResponse(BaseModel):
    detail: str = Field(description="Descripción del error")


class ValidationIssue(BaseModel):
    loc: list[str | int]
    msg: str
    type: str


class RegistrationValidationErrorResponse(BaseModel):
    detail: str | list[ValidationIssue] = Field(
        description="Mensaje de aplicación o lista de errores de entrada",
    )
