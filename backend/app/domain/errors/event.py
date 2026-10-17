class EventError(Exception):
    pass


class InvalidEventError(EventError):
    pass


class EventNotFoundError(EventError):
    pass


class EventConflictError(EventError):
    pass


class EventForbiddenError(EventError):
    pass
