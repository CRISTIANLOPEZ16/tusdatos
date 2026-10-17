from datetime import datetime

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.domain.entities.event_status import EventStatus
from app.infrastructure.schemas.pagination import PaginationParams
from app.infrastructure.schemas.session_schema import (
    SESSION_RESPONSE_EXAMPLE, SessionResponse,
)
from app.infrastructure.schemas.user_schema import ValidationIssue


EVENT_REQUEST_EXAMPLE = {
    "name": "Encuentro Python Medellín",
    "description": "Charlas y talleres de desarrollo de software.",
    "address": "Calle 10 # 20-30, Medellín",
    "starts_at": "2027-11-01T09:00:00-05:00",
    "ends_at": "2027-11-01T18:00:00-05:00",
    "status": "activo",
}
EVENT_RESPONSE_EXAMPLE = {
    "event_id": 1, **EVENT_REQUEST_EXAMPLE,
    "created_by": 1, "created_at": "2027-10-01T12:00:00Z",
}


class EventValidationErrorResponse(BaseModel):
    """Mensaje de negocio o lista de errores de validación de la entrada."""

    detail: str | list[ValidationIssue] = Field(
        description=(
            'Texto de validación del servicio o errores por campo de '
            'la petición.'
        ),
    )


class ListEventParams(PaginationParams):
    """Filtros públicos: paginación y búsqueda opcional por nombre."""

    name: str | None = Field(
        default=None, min_length=1, max_length=150,
        description=(
            "Nombre completo o parcial, sin distinguir mayúsculas. Si se "
            "omite, no filtra por nombre. Los caracteres % y _ son literales."
        ),
        examples=["Python"],
    )


class EventSummaryResponse(BaseModel):
    """Resumen del evento, sin sesiones ni capacidad global."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [EVENT_RESPONSE_EXAMPLE]},
    )

    event_id: int = Field(description="ID del evento.", examples=[1])
    name: str = Field(description="Nombre del evento.")
    description: str | None = Field(description="Descripción; puede ser null.")
    address: str = Field(description="Dirección del evento.")
    starts_at: datetime = Field(description="Inicio con zona horaria.")
    ends_at: datetime = Field(description="Final con zona horaria.")
    status: EventStatus = Field(description="Estado actual del evento.")
    created_by: int = Field(
        description='ID del creador, asignado desde su JWT.',
    )
    created_at: datetime = Field(
        description='Fecha de creación asignada por el servidor.',
    )


class ListEventResponse(BaseModel):
    """Página de resúmenes con el total anterior a la paginación."""

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "items": [EVENT_RESPONSE_EXAMPLE], "total": 1,
        "page": 1, "items_per_page": 10,
    }]})

    items: list[EventSummaryResponse] = Field(
        description='Eventos de esta página; puede estar vacío.',
    )
    total: int = Field(
        ge=0,
        description='Eventos que cumplen todos los filtros, antes de paginar.',
    )
    page: int = Field(ge=1, description="Página solicitada, comenzando en 1.")
    items_per_page: int = Field(
        ge=1, le=100,
        description='Tamaño solicitado de página.',
    )


class EventWriteRequest(BaseModel):
    """Datos editables del evento. Los campos desconocidos se rechazan."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [EVENT_REQUEST_EXAMPLE]},
    )

    name: str = Field(
        min_length=3, max_length=150,
        description=(
            'Nombre de entre 3 y 150 caracteres después de quitar '
            'espacios exteriores.'
        ),
    )
    description: str | None = Field(
        default=None,
        description=(
            'Descripción opcional; omitir o enviar null para dejarla '
            'vacía.'
        ),
    )
    address: str = Field(
        min_length=5, max_length=150,
        description=(
            'Dirección de entre 5 y 150 caracteres después de quitar '
            'espacios exteriores.'
        ),
    )
    starts_at: AwareDatetime = Field(
        description=(
            'Inicio con zona horaria; ejemplo ISO 8601: '
            '2027-11-01T09:00:00-05:00.'
        ),
    )
    ends_at: AwareDatetime = Field(
        description=(
            'Final con zona horaria, estrictamente posterior al '
            'inicio.'
        ),
    )
    status: EventStatus = Field(
        description=(
            "Estado: borrador, activo, cancelado, finalizado o archivado. "
            "Solo activo permite inscripciones a sus sesiones."
        ),
    )


class EventDetailsResponse(EventSummaryResponse):
    """Detalle del evento con sus sesiones y disponibilidad al consultar."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [{
            **EVENT_RESPONSE_EXAMPLE, "sessions": [SESSION_RESPONSE_EXAMPLE],
        }]},
    )

    sessions: list[SessionResponse] = Field(
        description=(
            'Sesiones ordenadas por inicio e ID; [] si el evento no '
            'tiene sesiones.'
        ),
    )
