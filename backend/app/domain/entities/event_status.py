from enum import StrEnum

from app.domain.errors.event import InvalidEventError


class EventStatus(StrEnum):
    DRAFT = "borrador"
    ACTIVE = "activo"
    CANCELLED = "cancelado"
    FINISHED = "finalizado"
    ARCHIVED = "archivado"

    @classmethod
    def from_name(cls, name: str) -> "EventStatus":
        try:
            return cls(name.strip().casefold())
        except ValueError as exc:
            raise InvalidEventError(
                "Estado equivocado"
            ) from exc
