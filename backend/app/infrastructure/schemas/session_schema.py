from datetime import datetime
from typing import Annotated

from pydantic import (
    AwareDatetime, BaseModel, ConfigDict, Field, StringConstraints,
)


SESSION_REQUEST_EXAMPLE = {
    "title": "Arquitectura hexagonal con Python",
    "starts_at": "2027-11-01T10:00:00-05:00",
    "ends_at": "2027-11-01T11:00:00-05:00",
    "capacity": 30,
    "speaker_names": ["Ana Pérez", "Carlos López"],
}
SESSION_RESPONSE_EXAMPLE = {
    "session_id": 1,
    "event_id": 1,
    **SESSION_REQUEST_EXAMPLE,
    "registered_count": 12,
    "available_capacity": 18,
}

SpeakerName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=150),
]


class SessionWriteRequest(BaseModel):
    """Campos editables de una sesión. PUT requiere el cuerpo completo."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [SESSION_REQUEST_EXAMPLE]},
    )
    title: str = Field(
        min_length=1, max_length=150,
        description="Título; no puede quedar vacío al normalizar.",
    )
    starts_at: AwareDatetime = Field(
        description=(
            "Inicio con zona horaria, dentro del horario del evento. "
            "Ejemplo ISO 8601: 2027-11-01T10:00:00-05:00."
        ),
    )
    ends_at: AwareDatetime = Field(
        description=(
            'Final con zona horaria, posterior al inicio y dentro del '
            'evento.'
        ),
    )
    capacity: int = Field(
        ge=1, le=2_147_483_647, strict=True,
        description=(
            "Aforo total, como entero positivo. Al actualizar, no puede ser "
            "menor que el número de inscritos. No representa los cupos libres."
        ),
    )
    speaker_names: tuple[SpeakerName, ...] = Field(
        default=(),
        description=(
            "Nombres de ponentes, entre 1 y 150 caracteres cada uno. Se "
            "compactan espacios y se comparan sin distinguir mayúsculas; no "
            "pueden repetirse en la sesión. Los nombres nuevos se crean y los "
            "existentes se reutilizan entre usuarios. Omitir o enviar [] deja "
            "la sesión sin ponentes, también al actualizar."
        ),
    )


class SessionResponse(BaseModel):
    """Sesión con aforo, ocupación y disponibilidad al consultar."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [SESSION_RESPONSE_EXAMPLE]},
    )

    session_id: int = Field(description="ID de la sesión.", examples=[1])
    event_id: int = Field(
        description='ID del evento al que pertenece.',
        examples=[1],
    )
    title: str = Field(description="Título de la sesión.")
    starts_at: datetime = Field(description="Inicio con zona horaria.")
    ends_at: datetime = Field(description="Final con zona horaria.")
    capacity: int = Field(description="Aforo total configurado de la sesión.")
    registered_count: int = Field(
        ge=0, description="Número actual de inscripciones de esta sesión.",
        json_schema_extra={"readOnly": True},
    )
    available_capacity: int = Field(
        ge=0,
        description=(
            "Cupos libres al consultar: capacity menos registered_count. "
            "Es informativo; la inscripción vuelve a comprobar el cupo y "
            "las condiciones de acceso. No se acepta al crear o actualizar."
        ),
        json_schema_extra={"readOnly": True},
    )
    speaker_names: list[str] = Field(
        description=(
            'Nombres normalizados; se conserva la primera escritura '
            'registrada.'
        ),
    )


class ListSessionResponse(BaseModel):
    """Página de sesiones con su disponibilidad actual."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [{
            "items": [SESSION_RESPONSE_EXAMPLE], "total": 1,
            "page": 1, "items_per_page": 10,
        }]},
    )

    items: list[SessionResponse] = Field(
        description="Sesiones de esta página; [] si no hay resultados.",
    )
    total: int = Field(
        ge=0,
        description=(
            'Total de sesiones que cumplen el filtro, antes de '
            'paginar.'
        ),
    )
    page: int = Field(ge=1, description="Página solicitada, comenzando en 1.")
    items_per_page: int = Field(
        ge=1, le=100,
        description='Tamaño solicitado de página.',
    )


class SessionRegistrationResponse(BaseModel):
    """Confirmación de la inscripción del usuario autenticado."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [{
            "event_id": 1, "session_id": 1, "user_id": 2,
        }]},
    )

    event_id: int = Field(description="Evento al que pertenece la sesión.")
    session_id: int = Field(
        description='Sesión en la que se confirmó la inscripción.',
    )
    user_id: int = Field(
        description='Usuario inscrito, obtenido del JWT y no del cuerpo.',
    )
