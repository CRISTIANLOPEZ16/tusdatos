import pytest
from app.domain.entities.event_status import EventStatus
from app.domain.errors.session import SessionConflictError


def test_registration_closes_exactly_at_session_start(make_session):
    session = make_session()
    with pytest.raises(SessionConflictError):
        session.ensure_can_register(
            registered_count=0,
            already_registered=False,
            event_status=EventStatus.ACTIVE,
            now=session.starts_at
        )
