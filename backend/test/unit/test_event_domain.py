import pytest
from app.domain.errors.event import (
    EventConflictError,
    EventForbiddenError,
    InvalidEventError,
)
from app.domain.errors.session import SessionConflictError


@pytest.mark.parametrize(
    'changes',
    [{'name': '  '}, {'address': 'x'}, {'created_by': 0}, {'status': 'activo'}]
)
def test_invalid_event_is_rejected(make_event, changes):
    with pytest.raises(InvalidEventError):
        make_event(**changes)


def test_only_creator_can_modify_event(make_event):
    event = make_event()
    event.ensure_owned_by(9)
    with pytest.raises(EventForbiddenError):
        event.ensure_owned_by(11)


def test_event_rejects_duplicate_identity(make_event):
    with pytest.raises(EventConflictError):
        make_event().ensure_not_duplicate(True)


def test_event_cannot_shrink_around_existing_sessions(
    make_event,
    make_session
):
    session = make_session()
    with pytest.raises(SessionConflictError):
        make_event(ends_at=session.starts_at, sessions=(session,))


def test_event_rejects_session_from_another_event(make_event, make_session):
    with pytest.raises(InvalidEventError):
        make_event(sessions=(make_session(event_id=99),))


def test_event_deletion_requires_no_sessions(make_event, make_session):
    make_event().ensure_can_delete()
    with pytest.raises(EventConflictError):
        make_event(sessions=(make_session(),)).ensure_can_delete()
