from app.domain.errors.event import EventError


class InvalidSessionError(EventError):
    pass


class SessionNotFoundError(EventError):
    pass


class SessionConflictError(EventError):
    pass
