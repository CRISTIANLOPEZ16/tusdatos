from datetime import datetime, timezone

from app.domain.entities.event_status import EventStatus
from app.domain.entities.session import Session, validate_schedule
from app.domain.errors.event import (
    EventConflictError,
    EventForbiddenError,
    InvalidEventError,
)


class Event:
    def __init__(
        self,
        *,
        name: str,
        description: str | None,
        address: str,
        starts_at: datetime,
        ends_at: datetime,
        status: EventStatus,
        created_by: int,
        event_id: int | None = None,
        created_at: datetime | None = None,
        sessions: tuple[Session, ...] | None = None,
    ) -> None:
        name = name.strip()
        address = address.strip()

        if not 3 <= len(name) <= 150:
            raise InvalidEventError(
                'El nombre debe contener entre 3 y 150 caracteres'
            )

        if not 5 <= len(address) <= 150:
            raise InvalidEventError(
                'La dirección debe contener entre 5 y 150 caracteres'
            )

        if created_by < 1:
            raise InvalidEventError("El creador debe tener un ID positivo")

        if not isinstance(status, EventStatus):
            raise InvalidEventError("El estado no está permitido")

        validate_schedule(starts_at, ends_at)

        self.event_id = event_id
        self.name = name
        self.description = description
        self.address = address
        self.starts_at = starts_at
        self.ends_at = ends_at
        self.status = status
        self.created_by = created_by
        self.created_at = (
            created_at
            if created_at is not None
            else datetime.now(timezone.utc)
        )
        self._sessions = sessions

        if sessions is not None:
            for session in sessions:
                if session.event_id != event_id:
                    raise InvalidEventError(
                        "La sesión no pertenece a este evento"
                    )

                session.ensure_fits(
                    starts_at,
                    ends_at,
                )

    @property
    def sessions(self) -> tuple[Session, ...]:
        if self._sessions is None:
            raise RuntimeError(
                'Las sesiones deben cargarse para esta operación'
            )

        return self._sessions

    def ensure_owned_by(self, user_id: int) -> None:
        if self.created_by != user_id:
            raise EventForbiddenError(
                'Solo el creador puede modificar el evento'
            )

    def ensure_can_delete(self) -> None:
        if self.sessions:
            raise EventConflictError(
                'Debes eliminar las sesiones antes de eliminar el evento'
            )

    def ensure_not_duplicate(self, already_exists: bool) -> None:
        if already_exists:
            raise EventConflictError(
                "Ya existe un evento con el mismo nombre, "
                "dirección y horario"
            )
