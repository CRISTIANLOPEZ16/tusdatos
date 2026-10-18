from datetime import datetime

from app.domain.entities.event_status import EventStatus
from app.domain.errors.event import InvalidEventError
from app.domain.errors.session import InvalidSessionError, SessionConflictError


def validate_schedule(starts_at: datetime, ends_at: datetime) -> None:
    if starts_at.utcoffset() is None or ends_at.utcoffset() is None:
        raise InvalidEventError("Las fechas deben incluir zona horaria")
    if ends_at <= starts_at:
        raise InvalidEventError(
            'La fecha final debe ser posterior a la inicial'
        )


class Session:
    def __init__(self, *, event_id: int, title: str, starts_at: datetime,
                 ends_at: datetime, capacity: int,
                 session_id: int | None = None,
                 speaker_names: tuple[str, ...] = (),
                 registered_count: int = 0) -> None:
        title = title.strip()
        if not title or len(title) > 150:
            raise InvalidSessionError(
                'El título debe tener entre 1 y 150 caracteres'
            )
        if event_id < 1 or (session_id is not None and session_id < 1):
            raise InvalidSessionError(
                'Los identificadores deben ser positivos'
            )
        validate_schedule(starts_at, ends_at)
        if type(capacity) is not int or not 1 <= capacity <= 2_147_483_647:
            raise InvalidSessionError(
                'La capacidad debe ser un entero positivo'
            )
        names = []
        for name in speaker_names:
            if not isinstance(name, str):
                raise InvalidSessionError(
                    "El nombre del ponente debe ser texto"
                )
            name = " ".join(name.split())
            if not 1 <= len(name) <= 150:
                raise InvalidSessionError(
                    "El nombre del ponente debe tener entre 1 y 150 caracteres"
                )
            names.append(name)
        if len({name.casefold() for name in names}) != len(names):
            raise InvalidSessionError("Los ponentes no pueden repetirse")
        self.session_id = session_id
        self.event_id = event_id
        self.title = title
        self.starts_at = starts_at
        self.ends_at = ends_at
        self.capacity = capacity
        if type(registered_count) is not int or registered_count < 0:
            raise InvalidSessionError(
                "El número de inscritos debe ser un entero no negativo"
            )
        self.registered_count = registered_count
        self.ensure_capacity_for(registered_count)
        self.speaker_names = tuple(sorted(names, key=str.casefold))

    @property
    def available_capacity(self) -> int:
        return self.capacity - self.registered_count

    def ensure_fits(self, starts_at: datetime, ends_at: datetime) -> None:
        if self.starts_at < starts_at or self.ends_at > ends_at:
            raise SessionConflictError(
                'La sesión debe quedar dentro del evento'
            )

    def ensure_capacity_for(self, registered_count: int) -> None:
        if self.capacity < registered_count:
            raise SessionConflictError(
                'La capacidad es menor que las inscripciones'
            )

    def ensure_can_delete(self, registered_count: int) -> None:
        if registered_count:
            raise SessionConflictError(
                'No se puede eliminar una sesión con inscritos'
            )

    def ensure_can_register(self, *, registered_count: int,
                            already_registered: bool,
                            event_status: EventStatus, now: datetime) -> None:
        if already_registered:
            raise SessionConflictError(
                'El usuario ya está inscrito en la sesión'
            )
        if event_status != EventStatus.ACTIVE or now >= self.starts_at:
            raise SessionConflictError("La sesión no admite inscripciones")
        if registered_count >= self.capacity:
            raise SessionConflictError("La sesión no tiene cupos disponibles")

    def ensure_speakers_available(self, *, overlap: bool) -> None:
        if overlap:
            raise SessionConflictError(
                'Un ponente tiene otra sesión en ese horario'
            )
