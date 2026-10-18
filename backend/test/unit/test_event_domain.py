import pytest
from app.domain.errors.session import SessionConflictError


def test_event_cannot_shrink_around_existing_sessions(
    make_event,
    make_session
):
    session = make_session()
    with pytest.raises(SessionConflictError):
        make_event(ends_at=session.starts_at, sessions=(session,))
